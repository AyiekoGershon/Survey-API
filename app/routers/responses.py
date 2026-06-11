from fastapi import APIRouter, HTTPException, UploadFile, Request, status
from fastapi.responses import Response, FileResponse
from typing import Optional, Any, Dict, List, Union
from datetime import datetime
from app.database import get_db_connection
from app.services.xml_service import dict_to_xml
from app.services.supabase_storage import upload_file as supabase_upload
import os

UPLOAD_DIR = os.path.join("app", "uploads", "files")
os.makedirs(UPLOAD_DIR, exist_ok=True)

router = APIRouter()


def _is_file_upload(value: object) -> bool:
    """Check if a form value is a file upload (supports both FastAPI and Starlette UploadFile)"""
    return isinstance(value, UploadFile) or (hasattr(value, 'filename') and hasattr(value, 'read'))


@router.post("/surveys/{survey_id}/responses", response_class=Response, status_code=status.HTTP_201_CREATED)
async def submit_response(survey_id: int, request: Request) -> Response:
    """Submit a survey response with optional file uploads"""
    form = await request.form()
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Verify survey exists
        cursor.execute("SELECT id FROM surveys WHERE id = %s AND is_active = TRUE", (survey_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Survey not found")

        # Extract email
        email = form.get("email_address", "")
        if not email:
            raise HTTPException(status_code=400, detail="Email address is required")

        # Get all questions for this survey (to map names to IDs and types)
        cursor.execute(
            "SELECT id, name, type FROM questions WHERE survey_id = %s",
            (survey_id,)
        )
        questions = cursor.fetchall()
        question_map: Dict[str, Dict[str, Any]] = {q[1]: {"id": q[0], "type": q[2]} for q in questions}

        if not question_map:
            raise HTTPException(status_code=400, detail="No questions found for this survey")

        # Create response record
        cursor.execute(
            "INSERT INTO responses (survey_id, user_email) VALUES (%s, %s)",
            (survey_id, email)
        )
        conn.commit()
        response_id = cursor.lastrowid
        if response_id is None:
            raise HTTPException(status_code=500, detail="Failed to create response record")

        # Process form fields
        has_any_answer = False

        # Use multi_items() to handle duplicate field names (including multiple file uploads)
        for key, value in form.multi_items():
            if key == "email_address":
                continue

            # Skip if we don't know this question
            question_info = question_map.get(key)
            if not question_info:
                continue

            q_id = question_info["id"]
            q_type = question_info["type"]

            # Handle file uploads
            if isinstance(value, UploadFile):
                if value.filename:
                    # Upload file to Supabase Storage
                    storage_path = await supabase_upload(value, response_id)

                    # Store as certificate (not as answer_text)
                    cursor.execute(
                        """INSERT INTO certificates (response_id, filename, file_path)
                           VALUES (%s, %s, %s)""",
                        (response_id, value.filename, storage_path)
                    )
                    has_any_answer = True

            else:
                # Handle text answer
                value_str = str(value).strip() if value else ""
                if value_str:
                    cursor.execute(
                        """INSERT INTO answer_texts (response_id, question_id, value)
                           VALUES (%s, %s, %s)""",
                        (response_id, q_id, value_str)
                    )
                    has_any_answer = True

        if not has_any_answer:
            conn.rollback()
            raise HTTPException(status_code=400, detail="No answers provided")

        conn.commit()

        # Build XML response
        response_xml = {
            "question_response": {
                "response_id": str(response_id),
                "email_address": email,
                "date_responded": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "message": "Response submitted successfully"
            }
        }

        return Response(content=dict_to_xml(response_xml), media_type="application/xml", status_code=status.HTTP_201_CREATED)

    except HTTPException:
        raise
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Error submitting response: {str(e)}")
    finally:
        cursor.close()
        conn.close()


@router.get("/surveys/{survey_id}/responses", response_class=Response)
async def get_responses(
    survey_id: int,
    page: int = 1,
    pageSize: int = 10,
    email: Optional[str] = None
) -> Response:
    """Get paginated survey responses with optional email filter"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        # Verify survey exists
        cursor.execute("SELECT id FROM surveys WHERE id = %s", (survey_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Survey not found")

        offset = (page - 1) * pageSize

        # Build query with filters
        query = "SELECT * FROM responses WHERE survey_id = %s"
        count_query = "SELECT COUNT(*) as total FROM responses WHERE survey_id = %s"
        params: List[Any] = [survey_id]

        if email:
            query += " AND user_email LIKE %s"
            count_query += " AND user_email LIKE %s"
            params.append(f"%{email}%")

        # Get total count
        cursor.execute(count_query, params)
        total_row = cursor.fetchone()
        total = total_row["total"] if total_row else 0

        # Get paginated responses
        query += " ORDER BY submitted_at DESC LIMIT %s OFFSET %s"
        cursor.execute(query, params + [pageSize, offset])
        responses = cursor.fetchall()

        # Build XML response
        root_attrs: Dict[str, str] = {
            "@total": str(total),
            "@page": str(page),
            "@page_size": str(pageSize)
        }
        responses_dict: Dict[str, Any] = {"question_responses": root_attrs}
        response_entries: Dict[str, Any] = {}

        for idx, resp in enumerate(responses):
            # Get text answers for this response
            cursor.execute(
                """SELECT q.name, a.value FROM answer_texts a
                   JOIN questions q ON a.question_id = q.id
                   WHERE a.response_id = %s""",
                (resp["id"],)
            )
            answers = cursor.fetchall()

            # Get certificates (uploaded files)
            cursor.execute(
                "SELECT id, filename FROM certificates WHERE response_id = %s",
                (resp["id"],)
            )
            certs = cursor.fetchall()

            response_entry: Dict[str, Any] = {
                "response_id": str(resp["id"]),
                "email_address": resp["user_email"],
                "date_responded": resp["submitted_at"].strftime("%Y-%m-%d %H:%M:%S") if resp["submitted_at"] else ""
            }

            # Add text answers
            for ans in answers:
                response_entry[ans["name"]] = ans["value"]

            # Add certificates with download links
            if certs:
                cert_list = []
                for cert in certs:
                    cert_list.append({
                        "@id": str(cert["id"]),
                        "@filename": cert["filename"],
                        "#text": cert["filename"]
                    })
                # Wrap in a certificates element
                response_entry["certificates"] = {"certificate": cert_list if len(cert_list) > 1 else cert_list[0]}

            response_entries[f"response_{idx+1}"] = response_entry

        responses_dict["question_responses"].update(response_entries)  # type: ignore[arg-type]

        return Response(content=dict_to_xml(responses_dict), media_type="application/xml")

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        cursor.close()
        conn.close()

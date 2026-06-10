from fastapi import APIRouter, HTTPException, status, Form
from fastapi.responses import Response
from typing import Optional
import json
from app.database import get_db_connection
from app.services.xml_service import dict_to_xml

router = APIRouter()

@router.post("/surveys/{survey_id}/questions", response_class=Response, status_code=status.HTTP_201_CREATED)
async def create_question(
    survey_id: int,
    name: str = Form(...),
    type: str = Form(...),
    text: str = Form(...),
    required: str = Form("no"),
    description: str = Form(""),
    options: Optional[str] = Form(None),  # JSON string of options
    file_properties: Optional[str] = Form(None)  # JSON string of file properties
):
    """Create a new question for a survey"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Verify survey exists and is active
        cursor.execute(
            "SELECT id FROM surveys WHERE id = %s AND is_active = TRUE",
            (survey_id,)
        )
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Survey not found")
        
        # Get max sort order
        cursor.execute(
            "SELECT COALESCE(MAX(sort_order), -1) + 1 as next_order FROM questions WHERE survey_id = %s",
            (survey_id,)
        )
        result = cursor.fetchone()
        sort_order = result[0] if result else 0
        
        # Insert question
        required_bool = required.lower() == "yes"
        cursor.execute(
            """INSERT INTO questions (survey_id, name, type, text, description, required, sort_order)
               VALUES (%s, %s, %s, %s, %s, %s, %s)""",
            (survey_id, name, type, text, description, required_bool, sort_order)
        )
        question_id = cursor.lastrowid
        
        # Handle options for choice questions
        if type in ["single_choice", "multiple_choice"] and options:
            options_list = json.loads(options)
            for idx, opt in enumerate(options_list):
                cursor.execute(
                    """INSERT INTO options (question_id, option_value, option_label, sort_order)
                       VALUES (%s, %s, %s, %s)""",
                    (question_id, opt["value"], opt["label"], idx)
                )
        
        # Handle file properties
        if type == "file" and file_properties:
            props = json.loads(file_properties)
            cursor.execute(
                "UPDATE questions SET file_properties = %s WHERE id = %s",
                (json.dumps(props), question_id)
            )
        
        conn.commit()
        
        # Build XML response
        question_data = {
            "question": {
                "@id": str(question_id),
                "@name": name,
                "@type": type,
                "@required": required,
                "text": text,
                "description": description
            }
        }
        
        if type in ["single_choice", "multiple_choice"] and options:
            options_dict = {"options": {"@multiple": "yes" if type == "multiple_choice" else "no"}}
            for opt in json.loads(options):
                options_dict["options"][f"option_{opt['value']}"] = {
                    "@value": opt["value"],
                    "#text": opt["label"]
                }
            question_data["question"].update(options_dict)
        
        return Response(content=dict_to_xml(question_data), media_type="application/xml", status_code=status.HTTP_201_CREATED)
        
    except HTTPException:
        raise
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        cursor.close()
        conn.close()

@router.get("/surveys/{survey_id}/questions", response_class=Response)
async def get_survey_questions(survey_id: int):
    """Get all questions for a survey"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        # Verify survey exists
        cursor.execute("SELECT id FROM surveys WHERE id = %s", (survey_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Survey not found")
        
        # Get questions
        cursor.execute(
            """SELECT id, name, type, text, description, required, sort_order, file_properties
               FROM questions WHERE survey_id = %s ORDER BY sort_order""",
            (survey_id,)
        )
        questions = cursor.fetchall()
        
        # Build XML response
        questions_dict = {"questions": {}}
        
        for q in questions:
            question_data = {
                "@id": str(q["id"]),
                "@name": q["name"],
                "@type": q["type"],
                "@required": "yes" if q["required"] else "no",
                "text": q["text"],
                "description": q["description"] or ""
            }
            
            # Add options for choice questions
            if q["type"] in ["single_choice", "multiple_choice"]:
                cursor.execute(
                    """SELECT option_value, option_label FROM options
                       WHERE question_id = %s ORDER BY sort_order""",
                    (q["id"],)
                )
                options = cursor.fetchall()
                
                options_dict = {"options": {"@multiple": "yes" if q["type"] == "multiple_choice" else "no"}}
                for opt in options:
                    options_dict["options"][f"option_{opt['option_value']}"] = {
                        "@value": opt["option_value"],
                        "#text": opt["option_label"]
                    }
                question_data.update(options_dict)
            
            # Add file properties (handle both string and pre-parsed dict from PostgreSQL JSON column)
            if q["type"] == "file" and q["file_properties"]:
                props = q["file_properties"]
                if isinstance(props, str):
                    props = json.loads(props)
                question_data["file_properties"] = {
                    "@format": props.get("format", ".pdf"),
                    "@max_file_size": str(props.get("max_size_mb", 1)),
                    "@max_file_size_unit": "mb",
                    "@multiple": "yes" if props.get("multiple", True) else "no"
                }
            
            questions_dict["questions"][f"question_{q['id']}"] = question_data
        
        return Response(content=dict_to_xml(questions_dict), media_type="application/xml")
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        cursor.close()
        conn.close()

@router.put("/questions/{question_id}", response_class=Response)
async def update_question(
    question_id: int,
    text: Optional[str] = None,
    description: Optional[str] = None,
    required: Optional[bool] = None,
    sort_order: Optional[int] = None
):
    """Update a question"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        updates = []
        params = []
        
        if text is not None:
            updates.append("text = %s")
            params.append(text)
        if description is not None:
            updates.append("description = %s")
            params.append(description)
        if required is not None:
            updates.append("required = %s")
            params.append(required)
        if sort_order is not None:
            updates.append("sort_order = %s")
            params.append(sort_order)
        
        if not updates:
            raise HTTPException(status_code=400, detail="No fields to update")
        
        params.append(question_id)
        query = f"UPDATE questions SET {', '.join(updates)} WHERE id = %s"
        cursor.execute(query, params)
        conn.commit()
        
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Question not found")
        
        return Response(content=dict_to_xml({"message": "Question updated successfully"}), media_type="application/xml")
    except HTTPException:
        raise
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        cursor.close()
        conn.close()

@router.delete("/questions/{question_id}", response_class=Response)
async def delete_question(question_id: int):
    """Delete a question"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # First delete related options (cascade should handle, but explicit for safety)
        cursor.execute("DELETE FROM options WHERE question_id = %s", (question_id,))
        # Then delete the question
        cursor.execute("DELETE FROM questions WHERE id = %s", (question_id,))
        conn.commit()
        
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Question not found")
        
        return Response(content=dict_to_xml({"message": "Question deleted successfully"}), media_type="application/xml")
    except HTTPException:
        raise
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        cursor.close()
        conn.close()
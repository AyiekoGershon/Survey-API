from fastapi import APIRouter, HTTPException, status, Request
from fastapi.responses import Response
from typing import Optional
from app.database import get_db_connection
from app.services.xml_service import dict_to_xml

router = APIRouter()

@router.post("/surveys", response_class=Response, status_code=status.HTTP_201_CREATED)
async def create_survey(request: Request):
    """Create a new survey (supports both query params and form data)"""
    # Try to get data from form body first, then query params
    form = await request.form()
    name = form.get("name", "") or request.query_params.get("name", "")
    description = form.get("description", "") or request.query_params.get("description", "")
    
    if not name:
        raise HTTPException(status_code=400, detail="Survey name is required")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            "INSERT INTO surveys (name, description) VALUES (%s, %s)",
            (name, description)
        )
        conn.commit()
        survey_id = cursor.lastrowid
        
        # Build XML response
        xml_data = {
            "survey": {
                "@id": str(survey_id),
                "name": name,
                "description": description
            }
        }
        
        return Response(content=dict_to_xml(xml_data), media_type="application/xml", status_code=status.HTTP_201_CREATED)
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        cursor.close()
        conn.close()

@router.get("/surveys", response_class=Response)
async def get_surveys(active_only: bool = True):
    """Get all surveys"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        if active_only:
            cursor.execute(
                "SELECT id, name, description, created_at, updated_at, is_active FROM surveys WHERE is_active = TRUE ORDER BY created_at DESC"
            )
        else:
            cursor.execute(
                "SELECT id, name, description, created_at, updated_at, is_active FROM surveys ORDER BY created_at DESC"
            )
        
        surveys = cursor.fetchall()
        
        # Build XML response
        surveys_dict = {"surveys": {}}
        for survey in surveys:
            survey_data = {
                "@id": str(survey["id"]),
                "name": survey["name"],
                "description": survey["description"],
                "created_at": survey["created_at"].strftime("%Y-%m-%d %H:%M:%S") if survey["created_at"] else "",
                "is_active": "true" if survey["is_active"] else "false"
            }
            surveys_dict["surveys"][f"survey_{survey['id']}"] = survey_data
        
        return Response(content=dict_to_xml(surveys_dict), media_type="application/xml")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        cursor.close()
        conn.close()

@router.get("/surveys/{survey_id}", response_class=Response)
async def get_survey(survey_id: int):
    """Get a specific survey by ID"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        cursor.execute(
            "SELECT id, name, description, created_at, updated_at, is_active FROM surveys WHERE id = %s",
            (survey_id,)
        )
        survey = cursor.fetchone()
        
        if not survey:
            raise HTTPException(status_code=404, detail="Survey not found")
        
        survey_data = {
            "survey": {
                "@id": str(survey["id"]),
                "name": survey["name"],
                "description": survey["description"],
                "created_at": survey["created_at"].strftime("%Y-%m-%d %H:%M:%S") if survey["created_at"] else "",
                "is_active": "true" if survey["is_active"] else "false"
            }
        }
        
        return Response(content=dict_to_xml(survey_data), media_type="application/xml")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        cursor.close()
        conn.close()

@router.put("/surveys/{survey_id}", response_class=Response)
async def update_survey(survey_id: int, request: Request):
    """Update a survey (supports both query params and form data)"""
    form = await request.form()
    name = form.get("name") or request.query_params.get("name")
    description = form.get("description") or request.query_params.get("description")
    is_active_str = form.get("is_active") or request.query_params.get("is_active")
    is_active = None
    if is_active_str is not None:
        is_active = is_active_str.lower() in ("true", "1", "yes")
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Build dynamic update query
        updates = []
        params = []
        
        if name is not None:
            updates.append("name = %s")
            params.append(name)
        if description is not None:
            updates.append("description = %s")
            params.append(description)
        if is_active is not None:
            updates.append("is_active = %s")
            params.append(is_active)
        
        if not updates:
            raise HTTPException(status_code=400, detail="No fields to update")
        
        updates.append("updated_at = NOW()")
        params.append(survey_id)
        
        query = f"UPDATE surveys SET {', '.join(updates)} WHERE id = %s"
        cursor.execute(query, params)
        conn.commit()
        
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Survey not found")
        
        return Response(content=dict_to_xml({"message": "Survey updated successfully"}), media_type="application/xml")
    except HTTPException:
        raise
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        cursor.close()
        conn.close()

@router.delete("/surveys/{survey_id}", response_class=Response)
async def delete_survey(survey_id: int, soft_delete: bool = True):
    """Delete a survey (soft delete by default)"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        if soft_delete:
            cursor.execute(
                "UPDATE surveys SET is_active = FALSE, updated_at = NOW() WHERE id = %s",
                (survey_id,)
            )
        else:
            # Hard delete - will cascade to questions, options, responses, answers, certificates
            cursor.execute("DELETE FROM surveys WHERE id = %s", (survey_id,))
        
        conn.commit()
        
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Survey not found")
        
        return Response(content=dict_to_xml({"message": "Survey deleted successfully"}), media_type="application/xml")
    except HTTPException:
        raise
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        cursor.close()
        conn.close()
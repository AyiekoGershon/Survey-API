from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse, Response
from app.database import get_db_connection
from app.services.xml_service import dict_to_xml
import os

router = APIRouter()

@router.get("/certificates/{certificate_id}")
async def download_certificate(certificate_id: int):
    """Download a certificate by its ID"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        cursor.execute(
            "SELECT filename, file_path FROM certificates WHERE id = %s",
            (certificate_id,)
        )
        certificate = cursor.fetchone()
        
        if not certificate:
            raise HTTPException(status_code=404, detail="Certificate not found")
        
        # Check if file exists
        if not os.path.exists(certificate["file_path"]):
            raise HTTPException(status_code=404, detail="Certificate file not found on server")
        
        return FileResponse(
            path=certificate["file_path"],
            filename=certificate["filename"],
            media_type="application/pdf"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error downloading certificate: {str(e)}")
    finally:
        cursor.close()
        conn.close()

@router.get("/responses/{response_id}/certificates", response_class=Response)
async def get_response_certificates(response_id: int):
    """Get all certificates for a response"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        cursor.execute(
            "SELECT id, filename, uploaded_at FROM certificates WHERE response_id = %s",
            (response_id,)
        )
        certificates = cursor.fetchall()
        
        return Response(content=dict_to_xml({"certificates": certificates}), media_type="application/xml")
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        cursor.close()
        conn.close()
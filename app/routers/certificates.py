from fastapi import APIRouter, HTTPException
from fastapi.responses import Response
from app.database import get_db_connection
from app.services.xml_service import dict_to_xml
from app.services.supabase_storage import download_file, file_exists
import io

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

        # Check if file exists in Supabase Storage
        if not file_exists(certificate["file_path"]):
            raise HTTPException(status_code=404, detail="Certificate file not found in storage")

        # Download file content from Supabase Storage
        file_content = download_file(certificate["file_path"])

        # Determine media type based on file extension
        filename = certificate["filename"]
        if filename.lower().endswith(".pdf"):
            media_type = "application/pdf"
        elif filename.lower().endswith((".png", ".jpg", ".jpeg", ".gif", ".webp")):
            media_type = f"image/{filename.rsplit('.', 1)[1].lower()}"
        else:
            media_type = "application/octet-stream"

        return Response(
            content=file_content,
            media_type=media_type,
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"'
            }
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

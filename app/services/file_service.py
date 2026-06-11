"""File service for handling file uploads."""
from fastapi import UploadFile
from app.services.supabase_storage import upload_file as supabase_upload, download_file


async def save_uploaded_file(file: UploadFile, response_id: int) -> str:
    """
    Save an uploaded file to Supabase Storage bucket.
    
    Args:
        file: UploadFile object from FastAPI
        response_id: ID of the response to organize files
        
    Returns:
        Storage path to the saved file (e.g., "certificates/123/filename.pdf")
    """
    # Upload to Supabase Storage
    storage_path = await supabase_upload(file, response_id)
    return storage_path


def get_file_data(storage_path: str) -> bytes:
    """
    Get file content from Supabase Storage.
    
    Args:
        storage_path: Path within the storage bucket
        
    Returns:
        File content as bytes
    """
    return download_file(storage_path)

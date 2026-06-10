"""File service for handling file uploads."""
import os
import shutil
from pathlib import Path
from fastapi import UploadFile


UPLOAD_DIR = "app/uploads"


def save_uploaded_file(file: UploadFile, response_id: int) -> str:
    """
    Save an uploaded file to the uploads directory.
    
    Args:
        file: UploadFile object from FastAPI
        response_id: ID of the response to organize files
        
    Returns:
        Path to the saved file
    """
    # Create uploads directory if it doesn't exist
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    
    # Create subdirectory for response ID
    response_dir = os.path.join(UPLOAD_DIR, str(response_id))
    os.makedirs(response_dir, exist_ok=True)
    
    # Save file
    file_path = os.path.join(response_dir, file.filename)
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    return file_path

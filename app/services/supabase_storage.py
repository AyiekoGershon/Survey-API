"""Supabase Storage service for handling file uploads and downloads."""
import os
from typing import Optional
from fastapi import UploadFile
from supabase import create_client, Client


# Supabase configuration from environment variables
# For backend operations, use the service_role key (bypasses RLS).
# If SERVICE_KEY is not set, falls back to ANON_KEY.
SUPABASE_URL = os.getenv("SUPABASE_URL", "https://yieipunlunexjrflrwau.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_ANON_KEY", "")
STORAGE_BUCKET = os.getenv("STORAGE_BUCKET", "survey-files")

# Initialize Supabase client
_supabase_client: Optional[Client] = None


def get_supabase_client() -> Client:
    """Get or create the Supabase client singleton."""
    global _supabase_client
    if _supabase_client is None:
        _supabase_client = create_client(SUPABASE_URL, SUPABASE_KEY)
    return _supabase_client



def get_storage_path(response_id: int, filename: str) -> str:
    """
    Get the storage path for a certificate file.

    Args:
        response_id: ID of the response to organize files
        filename: Original filename

    Returns:
        Path within the storage bucket
    """
    return f"certificates/{response_id}/{filename}"


async def upload_file(file: UploadFile, response_id: int) -> str:
    """
    Upload a file to Supabase Storage bucket.

    Args:
        file: UploadFile object from FastAPI
        response_id: ID of the response to organize files

    Returns:
        The storage path of the uploaded file (e.g., "certificates/123/filename.pdf")
    """
    supabase = get_supabase_client()

    # Read file content
    content = await file.read()

    # Determine storage path (use filename, defaulting if None)
    filename = file.filename or f"file_{response_id}"
    storage_path = get_storage_path(response_id, filename)

    # Upload to Supabase Storage
    supabase.storage.from_(STORAGE_BUCKET).upload(
        path=storage_path,
        file=content,
        file_options={"content-type": file.content_type or "application/octet-stream"}
    )

    return storage_path


def upload_file_sync(file_data: bytes, response_id: int, filename: str, content_type: Optional[str] = None) -> str:
    """
    Upload file bytes to Supabase Storage bucket (synchronous version).

    Args:
        file_data: File content as bytes
        response_id: ID of the response to organize files
        filename: Original filename
        content_type: MIME type of the file

    Returns:
        The storage path of the uploaded file
    """
    supabase = get_supabase_client()

    storage_path = get_storage_path(response_id, filename)

    options = {}
    if content_type:
        options["content-type"] = content_type

    supabase.storage.from_(STORAGE_BUCKET).upload(
        path=storage_path,
        file=file_data,
        file_options=options
    )

    return storage_path


def download_file(storage_path: str) -> bytes:
    """
    Download a file from Supabase Storage.

    Args:
        storage_path: Path within the storage bucket (e.g., "certificates/123/filename.pdf")

    Returns:
        File content as bytes
    """
    supabase = get_supabase_client()

    result = supabase.storage.from_(STORAGE_BUCKET).download(path=storage_path)

    return result


def get_public_url(storage_path: str) -> str:
    """
    Get the public URL for a file in Supabase Storage.

    Args:
        storage_path: Path within the storage bucket

    Returns:
        Public URL to access the file
    """
    supabase = get_supabase_client()

    return supabase.storage.from_(STORAGE_BUCKET).get_public_url(path=storage_path)


def file_exists(storage_path: str) -> bool:
    """
    Check if a file exists in Supabase Storage.

    Args:
        storage_path: Path within the storage bucket

    Returns:
        True if the file exists, False otherwise
    """
    supabase = get_supabase_client()

    try:
        # Try to get file info - will raise exception if not found
        supabase.storage.from_(STORAGE_BUCKET).info(path=storage_path)
        return True
    except Exception:
        return False


def delete_file(storage_path: str) -> None:
    """
    Delete a file from Supabase Storage.

    Args:
        storage_path: Path within the storage bucket
    """
    supabase = get_supabase_client()

    supabase.storage.from_(STORAGE_BUCKET).remove(paths=[storage_path])


def get_file_info(storage_path: str) -> dict:
    """
    Get information about a file in Supabase Storage.

    Args:
        storage_path: Path within the storage bucket

    Returns:
        Dictionary with file metadata
    """
    supabase = get_supabase_client()

    try:
        info = supabase.storage.from_(STORAGE_BUCKET).info(path=storage_path)
        return info
    except Exception as e:
        raise FileNotFoundError(f"File not found in storage: {storage_path}") from e

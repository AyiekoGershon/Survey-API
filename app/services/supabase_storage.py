"""Supabase Storage service for handling file uploads and downloads.
Supports both Supabase Storage API and S3-compatible storage (e.g., Cloudflare R2, MinIO)."""
import os
from typing import Optional, Any
from fastapi import UploadFile
from supabase import create_client, Client
import boto3
from botocore.config import Config
import mimetypes


# Supabase/S3 configuration from environment variables
SUPABASE_URL = os.getenv("SUPABASE_URL", "https://yieipunlunexjrflrwau.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_ANON_KEY", "")
STORAGE_BUCKET = os.getenv("STORAGE_BUCKET", "survey-files")

# S3-compatible storage configuration (optional, falls back to Supabase Storage API)
S3_ACCESS_KEY = os.getenv("SUPABASE_ACCESS_KEY_ID", "")
S3_SECRET_KEY = os.getenv("SUPABASE_SECRETE_ACCESS_KEY", "")
S3_ENDPOINT = os.getenv("S3_ENDPOINT", "https://yieipunlunexjrflrwau.supabase.co/storage/v1/s3")
S3_REGION = os.getenv("S3_REGION", "us-east-1")

# Use S3 if credentials are provided
USE_S3 = bool(S3_ACCESS_KEY and S3_SECRET_KEY)

# Initialize clients
_supabase_client: Optional[Client] = None
_s3_client: Any = None


def get_supabase_client() -> Client:
    """Get or create the Supabase client singleton."""
    global _supabase_client
    if _supabase_client is None:
        _supabase_client = create_client(SUPABASE_URL, SUPABASE_KEY)
    return _supabase_client


def get_s3_client() -> Any:
    """Get or create the S3-compatible client singleton."""
    global _s3_client
    if _s3_client is None and USE_S3:
        _s3_client = boto3.client(
            's3',
            endpoint_url=S3_ENDPOINT,
            aws_access_key_id=S3_ACCESS_KEY,
            aws_secret_access_key=S3_SECRET_KEY,
            region_name=S3_REGION,
            config=Config(signature_version='s3v4'),
        )
    return _s3_client



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
    Upload a file to storage (Supabase Storage or S3-compatible).

    Args:
        file: UploadFile object from FastAPI
        response_id: ID of the response to organize files

    Returns:
        The storage path of the uploaded file (e.g., "certificates/123/filename.pdf")
    """
    # Read file content
    content = await file.read()

    # Determine storage path (use filename, defaulting if None)
    filename = file.filename or f"file_{response_id}"
    storage_path = get_storage_path(response_id, filename)
    content_type = file.content_type or mimetypes.guess_type(filename)[0] or "application/octet-stream"

    if USE_S3:
        s3_client = get_s3_client()
        s3_client.put_object(
            Bucket=STORAGE_BUCKET,
            Key=storage_path,
            Body=content,
            ContentType=content_type,
        )
    else:
        supabase = get_supabase_client()
        _upload_to_supabase(supabase, storage_path, content, content_type)

    return storage_path


def _upload_to_supabase(supabase: Client, storage_path: str, content: bytes, content_type: str) -> None:
    """Upload file to Supabase Storage API."""
    try:
        supabase.storage.from_(STORAGE_BUCKET).upload(
            path=storage_path,
            file=content,
            file_options={"content-type": content_type}
        )
    except Exception as e:
        # If file already exists, try updating it
        if "already exists" in str(e).lower():
            supabase.storage.from_(STORAGE_BUCKET).update(
                path=storage_path,
                file=content,
                file_options={"content-type": content_type}
            )
        else:
            raise


def upload_file_sync(file_data: bytes, response_id: int, filename: str, content_type: Optional[str] = None) -> str:
    """
    Upload file bytes to storage (synchronous version).

    Args:
        file_data: File content as bytes
        response_id: ID of the response to organize files
        filename: Original filename
        content_type: MIME type of the file

    Returns:
        The storage path of the uploaded file
    """
    storage_path = get_storage_path(response_id, filename)

    if not content_type:
        content_type = mimetypes.guess_type(filename)[0] or "application/octet-stream"

    if USE_S3:
        s3_client = get_s3_client()
        s3_client.put_object(
            Bucket=STORAGE_BUCKET,
            Key=storage_path,
            Body=file_data,
            ContentType=content_type,
        )
    else:
        supabase = get_supabase_client()
        _upload_to_supabase(supabase, storage_path, file_data, content_type)

    return storage_path


def download_file(storage_path: str) -> bytes:
    """
    Download a file from storage.

    Args:
        storage_path: Path within the storage bucket

    Returns:
        File content as bytes
    """
    if USE_S3:
        s3_client = get_s3_client()
        response = s3_client.get_object(Bucket=STORAGE_BUCKET, Key=storage_path)
        return response['Body'].read()
    else:
        supabase = get_supabase_client()
        result = supabase.storage.from_(STORAGE_BUCKET).download(path=storage_path)
        return result


def get_public_url(storage_path: str) -> str:
    """
    Get the public URL for a file.

    Args:
        storage_path: Path within the storage bucket

    Returns:
        Public URL to access the file
    """
    if USE_S3:
        s3_client = get_s3_client()
        url = s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': STORAGE_BUCKET, 'Key': storage_path},
            ExpiresIn=3600  # 1 hour expiry
        )
        return url
    else:
        # Use Supabase Storage API
        supabase = get_supabase_client()
        return supabase.storage.from_(STORAGE_BUCKET).get_public_url(path=storage_path)


def file_exists(storage_path: str) -> bool:
    """
    Check if a file exists in storage.

    Args:
        storage_path: Path within the storage bucket

    Returns:
        True if the file exists, False otherwise
    """
    try:
        if USE_S3:
            s3_client = get_s3_client()
            s3_client.head_object(Bucket=STORAGE_BUCKET, Key=storage_path)
            return True
        else:
            supabase = get_supabase_client()
            supabase.storage.from_(STORAGE_BUCKET).info(path=storage_path)
            return True
    except Exception:
        return False


def delete_file(storage_path: str) -> None:
    """
    Delete a file from storage.

    Args:
        storage_path: Path within the storage bucket
    """
    if USE_S3:
        s3_client = get_s3_client()
        s3_client.delete_object(Bucket=STORAGE_BUCKET, Key=storage_path)
    else:
        supabase = get_supabase_client()
        supabase.storage.from_(STORAGE_BUCKET).remove(paths=[storage_path])


def get_file_info(storage_path: str) -> dict:
    """
    Get information about a file in storage.

    Args:
        storage_path: Path within the storage bucket

    Returns:
        Dictionary with file metadata
    """
    try:
        if USE_S3:
            s3_client = get_s3_client()
            response = s3_client.head_object(Bucket=STORAGE_BUCKET, Key=storage_path)
            return {
                'size': response.get('ContentLength', 0),
                'content_type': response.get('ContentType', ''),
                'last_modified': str(response.get('LastModified', '')),
                'etag': response.get('ETag', ''),
            }
        else:
            # Use Supabase Storage API
            supabase = get_supabase_client()
            info = supabase.storage.from_(STORAGE_BUCKET).info(path=storage_path)
            return info
    except Exception as e:
        raise FileNotFoundError(f"File not found in storage: {storage_path}") from e

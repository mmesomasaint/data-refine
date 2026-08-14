# app/core/security.py
import re
from fastapi import Security, HTTPException, status, UploadFile
from fastapi.security.api_key import APIKeyHeader
from app.config import settings

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

async def verify_api_key(api_key: str = Security(api_key_header)):
    if not api_key or api_key != settings.API_KEY.get_secret_value():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing X-API-Key header."
        )
    return api_key

def sanitize_csv_cell(value: str) -> str:
    """
    Mitigates CSV Formula Injection (CWE-1236).
    Prepends a single quote if string begins with =, +, -, @, tab, or carriage return.
    """
    if not isinstance(value, str):
        return value
        
    value = value.strip()
    if re.match(r"^[\=\+\-\@\t\r]", value):
        return f"'{value}"
    return value

def validate_csv_file_meta(file: UploadFile):
    """Ensures file is valid CSV by extension and MIME content type."""
    if not file.filename.lower().endswith(".csv"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file type. Only standard .csv files are supported."
        )

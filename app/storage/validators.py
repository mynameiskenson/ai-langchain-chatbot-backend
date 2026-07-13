from fastapi import UploadFile
from app.core.exceptions import ValidationException

ALLOWED_TYPES = ["application/pdf"]
MAX_FILE_SIZE = 10 * 1024 * 1024


async def validate_upload(file: UploadFile) -> UploadFile:
    """FastAPI dependency — validates file type and size at the HTTP boundary.
    Raises ValidationException (returns ApiResponse error) on failure.
    Resets the file stream so the service can read it normally.
    """
    if file.content_type not in ALLOWED_TYPES:
        raise ValidationException("Invalid file type. Only PDF files are allowed.")

    chunk_size = 1024 * 1024
    total = 0
    file.file.seek(0)
    while True:
        chunk = file.file.read(chunk_size)
        if not chunk:
            break
        total += len(chunk)
        if total > MAX_FILE_SIZE:
            file.file.seek(0)
            raise ValidationException("File size exceeds the maximum limit of 10 MB.")

    file.file.seek(0)
    return file
from fastapi import UploadFile
from app.core.exceptions import ValidationException

ALLOWED_TYPES = [
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/msword",
]
MAX_FILE_SIZE = 10 * 1024 * 1024


async def validate_upload(file: UploadFile) -> UploadFile:
    """Validate uploaded file type and size; raise `ValidationException` on failure."""
    if file.content_type not in ALLOWED_TYPES:
        raise ValidationException(f"Invalid file type for {file.filename}. Only PDF/DOCX files are allowed.")

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
            raise ValidationException(f"File size for {file.filename} exceeds the maximum limit of 10 MB.")

    file.file.seek(0)
    return file
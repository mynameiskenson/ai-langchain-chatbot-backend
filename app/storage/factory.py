from pathlib import Path

from app.core.config import settings

from app.storage.local import LocalStorage

def get_storage():
    provider = settings.storage.PROVIDER.lower()

    if provider == "local":
        base_path = Path(settings.storage.LOCAL_UPLOAD_PATH)
        return LocalStorage(base_path)
    else:
        raise ValueError(f"Unsupported storage provider: {provider}")
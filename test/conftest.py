import pytest

from app.database.session import AsyncSessionLocal

@pytest.fixture
async def db_session():
    """Create a new database session for a test."""
    async with AsyncSessionLocal() as session:
        yield session
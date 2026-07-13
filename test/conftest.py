import pytest
from sqlalchemy.ext.asyncio import AsyncSession

# =========================
# Database Session Fixture
# Uses a SAVEPOINT (nested transaction) so tests can commit
# without persisting changes — outer transaction is rolled back.
# =========================
from app.database.session import AsyncSessionLocal, engine


@pytest.fixture
async def db_session():
    """Create a new database session for a test using a nested transaction.

    This allows repository code to call `commit()` during tests while
    the outer transaction is rolled back at the end of the test so no
    data persists.
    """
    # Create a connection and begin a top-level transaction
    async with engine.connect() as conn:
        trans = await conn.begin()
        # Bind a session to the connection and start a nested transaction
        async with AsyncSession(bind=conn, expire_on_commit=False) as session:
            await session.begin_nested()
            try:
                yield session
            finally:
                try:
                    # Rollback any nested transaction to clean up after the test
                    await session.rollback()
                except Exception:
                    # If the nested transaction is already rolled back, ignore the error
                    pass
        # rollback the outer transaction so nothing persists
        await trans.rollback()

# =========================
# Repository Fixtures
# =========================
from app.modules.document.repository import DocumentRepository

@pytest.fixture
async def test_document_repository(db_session: AsyncSession):
    """Create a new instance of DocumentRepository for testing."""
    return DocumentRepository(db_session)

from app.modules.document.repository import DocumentChunkRepository

@pytest.fixture
async def test_document_chunk_repository(db_session: AsyncSession):
    """Create a new instance of DocumentChunkRepository for testing."""
    return DocumentChunkRepository(db_session)

# Unit of Work fixture
from app.uow.sqlalchemy import SQLAlchemyUnitOfWork


@pytest.fixture
async def test_uow(db_session: AsyncSession):
    """Provide a SQLAlchemyUnitOfWork bound to the test session."""
    return SQLAlchemyUnitOfWork(db_session)
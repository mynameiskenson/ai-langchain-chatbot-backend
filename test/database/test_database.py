import pytest
from sqlalchemy import text


@pytest.mark.asyncio
async def test_database_connection(db_session):
    # Perform a simple query to check database connectivity
    result = await db_session.execute(text("SELECT 1"))
    value = result.scalar_one()
    assert value == 1, "Database connection test failed"
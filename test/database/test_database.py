from sqlalchemy import text

def test_database_connection(db_session):
    # Perform a simple query to check database connectivity
    result = db_session.execute(text('SELECT 1')).scalar()
    assert result == 1, "Database connection test failed"
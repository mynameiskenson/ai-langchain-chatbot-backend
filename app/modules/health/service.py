from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

class HealthService:
    def __init__(self):
        pass

    def check_health(self):
        # Implement the logic to check the health of the service
        return {"status": "healthy"}
    
    async def check_database_health(self, db: AsyncSession):
        try:
            # Perform a simple query to check database connectivity
            await db.execute(text('SELECT 1'))
            return {"status": "healthy", "database": "connected"}
        except Exception as e:
            return {"status": "unhealthy", "database": f"disconnected - {e}"}
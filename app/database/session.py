from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from app.core.config import settings

# Create the SQLAlchemy async engine
engine = create_async_engine(
    settings.database.database_url,
    echo=settings.app.DEBUG,
    pool_pre_ping=True,
)

# Create a configured AsyncSession maker
AsyncSessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False)
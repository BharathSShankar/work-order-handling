from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# Use SQLite's async dialect
DATABASE_URL = "sqlite+aiosqlite:///./my_database.db"

# Create async engine for SQLite
engine = create_async_engine(DATABASE_URL, echo=True, future=True)

# Create session factory for async sessions
AsyncSessionLocal = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

# Base class for models
Base = declarative_base()

# Dependency to get async DB session
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

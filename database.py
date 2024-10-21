from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from contextlib import asynccontextmanager

# Use SQLite's async dialect
DATABASE_URL = "sqlite+aiosqlite:///./my_database.db"

# Create async engine for SQLite
engine = create_async_engine(DATABASE_URL, echo=True, future=True)

# Create session factory for async sessions
AsyncSessionLocal = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

# Base class for models
Base = declarative_base()

# Dependency to get async DB session using an async context manager
@asynccontextmanager
async def get_db():
    session = AsyncSessionLocal()
    try:
        yield session
        await session.commit()
    except Exception as e:
        await session.rollback()
        raise e
    finally:
        await session.close()

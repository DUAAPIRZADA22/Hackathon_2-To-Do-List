"""
Database Session Management for Todo AI Chatbot (Phase III)

Implements async engine and session management with connection pooling.
Uses SQLAlchemy 2.0 async patterns with psycopg (PostgreSQL) driver.

Configuration:
- Engine: Async PostgreSQL with connection pooling
- Session: Async session with auto-commit disabled
- Pool size: 20 connections, max overflow 40
"""

import os
from typing import AsyncGenerator
from pathlib import Path

# Load environment variables from .env file before any other imports
# This ensures DATABASE_URL is available when the module is loaded
from dotenv import load_dotenv

# Try to find .env file in the backend directory or parent directories
env_path = Path(__file__).parent.parent.parent / ".env"
if env_path.exists():
    load_dotenv(env_path)
else:
    # Fallback to loading from current directory
    load_dotenv()

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import NullPool


# =====================================================
# Database Engine Configuration
# =====================================================

def get_database_url() -> str:
    """
    Get database URL from environment variable.

    Returns:
        Async-compatible database URL (psycopg for HF compatibility)

    Example:
        postgresql+psycopg://user:password@host:port/database
    """
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise ValueError(
            "DATABASE_URL environment variable not set. "
            "Please set it in your .env file."
        )

    # Convert postgresql:// or postgresql+asyncpg:// to postgresql+psycopg://
    # Use psycopg for async operations (Hugging Face compatible)
    if database_url.startswith("postgresql://"):
        database_url = database_url.replace("postgresql://", "postgresql+psycopg://", 1)
    elif database_url.startswith("postgresql+asyncpg://"):
        database_url = database_url.replace("postgresql+asyncpg://", "postgresql+psycopg://", 1)

    return database_url


# Create async engine with connection pooling
engine = create_async_engine(
    get_database_url(),
    echo=False,  # Set to True for SQL query logging in development
    pool_size=20,  # Connection pool size
    max_overflow=40,  # Additional connections when pool is full
    pool_pre_ping=True,  # Verify connections before using
    pool_recycle=3600,  # Recycle connections after 1 hour
)

# Create async session factory
async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,  # Prevent expired object issues
    autocommit=False,
    autoflush=False,
)


# =====================================================
# Session Management
# =====================================================

async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency that provides a database session.

    Usage in FastAPI:
        @app.get("/tasks")
        async def list_tasks(session: AsyncSession = Depends(get_session)):
            ...

    Yields:
        AsyncSession: SQLAlchemy async session

    Example:
        async for session in get_session():
            result = await session.execute(select(Task))
    """
    async with async_session_maker() as session:
        try:
            yield session
            # Try to commit, but handle any errors gracefully
            try:
                await session.commit()
            except Exception as commit_error:
                # If commit fails, just rollback silently
                try:
                    await session.rollback()
                except Exception:
                    pass  # Ignore rollback errors
        except Exception:
            # Rollback on exception during request handling
            try:
                await session.rollback()
            except Exception:
                pass  # Ignore rollback errors
            # Re-raise the original exception so FastAPI can handle it
            raise
        finally:
            # Always close the session
            try:
                await session.close()
            except Exception:
                pass  # Ignore close errors


# =====================================================
# Database Initialization
# =====================================================

async def init_db() -> None:
    """
    Initialize database connection and create tables.

    This should be called on application startup.
    Uses SQLAlchemy Core create_all() for table creation.

    Note:
        In production, use Alembic migrations instead of create_all().
        This is intended for development and testing only.
    """
    from sqlmodel import SQLModel

    # Import all models to ensure they're registered with SQLModel
    try:
        from backend.src.db.models import Task, Conversation, Message
        # Also import User model from Phase I/II to satisfy foreign key constraints
        from backend.src.models.user import User
    except ImportError:
        from src.db.models import Task, Conversation, Message
        # Also import User model from Phase I/II to satisfy foreign key constraints
        from src.models.user import User

    async with engine.begin() as conn:
        # Create all tables (will not overwrite existing tables)
        await conn.run_sync(SQLModel.metadata.create_all)


async def close_db() -> None:
    """
    Close database connections.

    This should be called on application shutdown.
    """
    await engine.dispose()


# =====================================================
# Health Check
# =====================================================

async def check_db_connection() -> bool:
    """
    Check if database connection is alive.

    Returns:
        True if connection successful, False otherwise
    """
    try:
        from sqlalchemy import text
        async with engine.begin() as conn:
            # Simple query to test connection
            await conn.execute(text("SELECT 1"))
        return True
    except Exception as e:
        print(f"Database connection check failed: {e}")
        return False


# =====================================================
# Development Helpers
# =====================================================

async def drop_all_tables() -> None:
    """
    Drop all database tables.

    WARNING: This will delete all data!
    Only use in development/testing environments.
    """
    from sqlmodel import SQLModel

    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)


async def reset_db() -> None:
    """
    Reset database: drop all tables and recreate.

    WARNING: This will delete all data!
    Only use in development/testing environments.
    """
    await drop_all_tables()
    await init_db()

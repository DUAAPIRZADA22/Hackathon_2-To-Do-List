"""
Database configuration and session management
"""

import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker, Session
from typing import Callable

from src.core.config import settings

logger = logging.getLogger(__name__)

# Convert async URL to sync URL for Phase I/II synchronous engine
# Phase III uses psycopg, Phase I/II uses sync psycopg
database_url_sync = settings.DATABASE_URL
print(f"[DEBUG] Original DATABASE_URL: {database_url_sync}")

if database_url_sync.startswith("postgresql+asyncpg://"):
    # Replace asyncpg driver with postgresql+psycopg for sync operations
    database_url_sync = database_url_sync.replace("postgresql+asyncpg://", "postgresql+psycopg://", 1)
    print(f"[DEBUG] Converted to sync URL: {database_url_sync}")
elif database_url_sync.startswith("postgresql://"):
    # Convert plain postgresql:// to postgresql+psycopg://
    database_url_sync = database_url_sync.replace("postgresql://", "postgresql+psycopg://", 1)
    print(f"[DEBUG] Converted to sync URL: {database_url_sync}")

# Create database engine with sync-compatible URL
engine = create_engine(
    database_url_sync,
    pool_pre_ping=True,
    pool_recycle=300,
)
print(f"[DEBUG] Phase I/II database engine created with driver: {engine.driver}")

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base class for models (SQLAlchemy 2.0 style)
class Base(DeclarativeBase):
    pass


def get_db():
    """
    Dependency function to get database session.

    For sync endpoints, this returns the session directly.
    For async endpoints, use Phase III's get_session instead.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

"""Database configuration using SQLAlchemy V2"""

from sqlalchemy import create_engine, event
from sqlalchemy.orm import DeclarativeBase, Session
from contextlib import contextmanager
from typing import Generator
import os
from pathlib import Path

from app.core.config import settings
from app.core.logging import app_logger

# Ensure data directory exists
data_dir = Path("data")
data_dir.mkdir(exist_ok=True)

# Create engine with proper configuration
engine = create_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    pool_pre_ping=True,
    pool_recycle=300,
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {}
)

class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models."""
    pass

def create_tables():
    """Create all database tables."""
    try:
        Base.metadata.create_all(bind=engine)
        app_logger.info("Database tables created successfully")
    except Exception as e:
        app_logger.error(f"Error creating database tables: {e}")
        raise

@contextmanager
def get_db_session() -> Generator[Session, None, None]:
    """Database session context manager."""
    session = Session(engine)
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        app_logger.error(f"Database session error: {e}")
        raise
    finally:
        session.close()

def get_db() -> Generator[Session, None, None]:
    """Database session dependency for FastAPI."""
    with get_db_session() as session:
        yield session

# Enable foreign key constraints for SQLite
@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    """Enable foreign key constraints for SQLite."""
    if "sqlite" in settings.DATABASE_URL:
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

def init_database():
    """Initialize the database with tables."""
    try:
        create_tables()
        app_logger.info("Database initialized successfully")
    except Exception as e:
        app_logger.error(f"Failed to initialize database: {e}")
        raise
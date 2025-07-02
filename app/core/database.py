from typing import Generator, Optional
from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase, Session

from app.core.config import settings
from app.core.logging import app_logger

class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models."""
    pass

engine = None
SessionLocal = None

def setup_database() -> None:
    """Initialize database connection and create tables if enabled."""
    global engine, SessionLocal

    if not settings.ENABLE_DATABASE:
        app_logger.info("Database is disabled by configuration.")
        return

    if not settings.DATABASE_URL:
        app_logger.warning("Database URL not configured, but ENABLE_DATABASE is True.")
        return

    try:
        engine = create_engine(
            settings.DATABASE_URL,
            pool_pre_ping=True,
            pool_recycle=3600,
            echo=settings.DEBUG,
        )
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        app_logger.info(f"Database connection established: {settings.DATABASE_URL.split('@')[-1].split('/')[-1]}")
        create_tables()
    except Exception as e:
        app_logger.error(f"Failed to connect to database: {e}")
        raise

def get_db() -> Generator[Session, None, None]:
    """Dependency for FastAPI to get a database session."""
    if not SessionLocal:
        raise RuntimeError("Database not initialized or enabled.")
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@contextmanager
def get_db_context() -> Generator[Session, None, None]:
    """Context manager for database sessions."""
    if not SessionLocal:
        raise RuntimeError("Database not initialized or enabled.")
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_tables() -> None:
    """Create all tables defined in SQLAlchemy models."""
    if not engine:
        app_logger.warning("Database engine not initialized.")
        return
    Base.metadata.create_all(bind=engine)
    app_logger.info("Database tables created successfully.")
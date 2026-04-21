"""
Database setup and configuration for SQLModel.
This file handles database connection and session management.
"""

from sqlmodel import SQLModel, create_engine, Session
from typing import Generator
from app.config import get_settings


# Get settings
settings = get_settings()

# Create database engine
# echo=True logs all SQL statements (useful for debugging)
engine = create_engine(
    settings.database_url,
    echo=settings.debug,
    connect_args={"check_same_thread": False} if "sqlite" in settings.database_url else {}
)


def create_db_and_tables():
    """
    Create all database tables based on SQLModel models.
    Run this on application startup.
    """
    SQLModel.metadata.create_all(engine)


def get_session() -> Generator[Session, None, None]:
    """
    Dependency function to get database session.
    Yields a session for each request and ensures cleanup.
    """
    with Session(engine) as session:
        yield session

"""SQLite database setup using SQLModel."""

from __future__ import annotations

import logging
from pathlib import Path

from sqlmodel import Session, SQLModel, create_engine

from app.config import settings

logger = logging.getLogger(__name__)

# Ensure data directory exists
Path(settings.data_dir).mkdir(parents=True, exist_ok=True)

# Create engine — SQLite with check_same_thread=False for async usage
engine = create_engine(
    settings.database_url,
    echo=False,
    connect_args={"check_same_thread": False},
)


def init_db() -> None:
    """Create all database tables."""
    SQLModel.metadata.create_all(engine)
    logger.info("Database initialized at %s", settings.database_url)


def get_session() -> Session:
    """Get a database session."""
    return Session(engine)

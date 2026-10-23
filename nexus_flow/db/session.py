"""SQLAlchemy database session and engine setup."""

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from nexus_flow.core.config import get_settings

settings = get_settings()

# Connect args specific to SQLite for multithreaded web server
connect_args = {}
if settings.database_url.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(
    settings.database_url,
    connect_args=connect_args,
    echo=False,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    """Dependency for yielding request-scoped database sessions."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Initializes all database tables registered on Base."""
    from nexus_flow.db import models  # Ensure all models are imported
    Base.metadata.create_all(bind=engine)

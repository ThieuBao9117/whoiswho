"""
Database Configuration - CSB Connection (SQLite for Development)

CSB has its OWN database, separate from HRM.
- Uses SQLite for easy development (no PostgreSQL required)
- Can be switched to PostgreSQL for production
- Employee data can be imported from CSV
"""
from sqlalchemy import create_engine
from sqlalchemy.pool import NullPool
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings

# CSB Database Engine - completely separate from HRM
engine = create_engine(
    settings.CSB_DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in settings.CSB_DATABASE_URL else {},
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """FastAPI dependency for database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    Initialize CSB database - create all tables.
    Called on first run or when setting up new instance.
    """
    # Import all models so Base.metadata knows about them
    from app.models import csb_models  # noqa: F401

    Base.metadata.create_all(bind=engine)
    print("✅ CSB Database initialized successfully")

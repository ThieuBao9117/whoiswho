"""
Database Configuration - WHO Is WHO (SQLite for Development)

CSB has its OWN database, separate from HRM.
- Uses SQLite for easy development (no PostgreSQL required)
- Can be switched to PostgreSQL for production
- Employee data can be imported from CSV
"""
from sqlalchemy import create_engine, event, text
from sqlalchemy.pool import QueuePool
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings

_is_sqlite = "sqlite" in settings.CSB_DATABASE_URL

# CSB Database Engine - completely separate from HRM
engine = create_engine(
    settings.CSB_DATABASE_URL,
    connect_args={"check_same_thread": False} if _is_sqlite else {
        "connect_timeout": 10,   # PostgreSQL connection timeout (seconds)
        "options": "-c statement_timeout=15000",  # 15s max per query
    },
    pool_pre_ping=True,          # Test connection before use (detect stale)
    pool_size=5,                 # Max persistent connections
    max_overflow=10,             # Extra connections when pool exhausted
    pool_timeout=10,             # Wait max 10s for available connection
    pool_recycle=1800,           # Recycle connections every 30 min
) if not _is_sqlite else create_engine(
    settings.CSB_DATABASE_URL,
    connect_args={"check_same_thread": False},
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

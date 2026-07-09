"""
Database Configuration - WHO Is WHO (SQLite for Development)

CSB has its OWN database, separate from HRM.
- Uses SQLite for easy development (no PostgreSQL required)
- Can be switched to PostgreSQL for production
- Employee data can be imported from CSV
"""
from sqlalchemy import create_engine, text
from sqlalchemy.pool import NullPool
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings

_is_sqlite = "sqlite" in settings.CSB_DATABASE_URL

# CSB Database Engine - completely separate from HRM
# Dung NullPool: moi request tao connection moi, khong giu connection idle
# Tranh stale connection deadlock sau khi PostgreSQL dong idle connection
if _is_sqlite:
    engine = create_engine(
        settings.CSB_DATABASE_URL,
        connect_args={"check_same_thread": False},
    )
else:
    engine = create_engine(
        settings.CSB_DATABASE_URL,
        poolclass=NullPool,              # Khong pool - moi request = connection moi
        connect_args={
            "connect_timeout": 10,       # Fail nhanh neu PostgreSQL khong tra loi
            "options": "-c statement_timeout=30000",  # 30s max per query
        },
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """FastAPI dependency for database session.
    NullPool: moi request tao fresh connection, tu dong close sau request.
    """
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

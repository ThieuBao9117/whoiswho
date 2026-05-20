"""
HRM Database Engine - Read-Only Connection
==========================================
Đây là engine KẾT NỐI trực tiếp vào HRM database (Source of Truth).
- CHỈ ĐỌC — không tạo/migrate bảng nào
- Tách biệt hoàn toàn với CSB engine
- Ánh xạ trực tiếp các bảng Django HRM hiện có

HRM DB: postgresql+psycopg://postgres:123456@localhost:5433/hrm
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings

# ─── HRM Engine (read-only, không pooling để dev đơn giản) ───────────────────
HRM_DATABASE_URL = settings.CSB_DATABASE_URL  # đọc từ .env (CSB_DATABASE_URL tránh xung đột với system DATABASE_URL)

hrm_engine = create_engine(
    HRM_DATABASE_URL,
    pool_pre_ping=True,          # tự kiểm tra kết nối còn sống không
    pool_size=5,
    max_overflow=10,
    echo=False,                  # bật True khi debug SQL
)

HrmSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=hrm_engine,
)

# Base riêng cho HRM models — KHÔNG dùng create_all()
HrmBase = declarative_base()


def get_hrm_db():
    """FastAPI dependency — session đọc HRM database"""
    db = HrmSessionLocal()
    try:
        yield db
    finally:
        db.close()

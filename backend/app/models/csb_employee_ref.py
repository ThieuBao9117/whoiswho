"""
CSB Employee Reference - Independent from HRM DB

Bảng này lưu tham chiếu nhân viên từ HRM sang CSB.
KHÔNG có FK trực tiếp sang auth_user hay hr_employee.

Đồng bộ qua API từ HRM → CSB:
- Khi nhân viên mới vào HRM
- Khi thay đổi phòng ban/chức vụ
- Khi nghỉ việc (status = 'Inactive')

Database: SQLite (development) / PostgreSQL (production)
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Index
from datetime import datetime
from app.core.database import Base
import uuid


class CSBEmployeeRef(Base):
    """
    Local employee reference synced from HRM.

    Design principles:
    - No foreign keys to HRM tables
    - Uses hrm_employee_id to track source record
    - Synced periodically via API
    - Read-only from CSB perspective (edit trong HRM)
    - Works with both SQLite and PostgreSQL
    """
    __tablename__ = "csb_employee_refs"
    
    # Integer primary key for SQLite compatibility
    id = Column(Integer, primary_key=True, autoincrement=True)

    # Tham chiếu đến nguồn HRM
    hrm_employee_id = Column(Integer, nullable=True, index=True)
    hrm_user_id = Column(Integer, nullable=True)  # auth_user.id từ HRM

    # Thông tin nhân viên (copy từ HRM)
    emp_code = Column(String(32), unique=True, index=True, nullable=False)
    username = Column(String(150), unique=True, index=True, nullable=False)
    full_name = Column(String(120), index=True, nullable=False)
    email = Column(String(254), nullable=True)

    entity = Column(String(120), index=True, nullable=True)      # Công ty / Chi nhánh
    division = Column(String(120), index=True, nullable=True)    # Khối
    department = Column(String(120), index=True, nullable=True)  # Phòng ban
    team = Column(String(120), index=True, nullable=True)        # Nhóm
    part = Column(String(120), index=True, nullable=True)        # Tổ
    position = Column(String(120), nullable=True)                # Chức danh (chi tiết hơn role)
    role = Column(String(120), nullable=True)                    # Vai trò hệ thống

    status = Column(String(32), default="Active", index=True)
    join_date = Column(DateTime, nullable=True)

    photo = Column(String(100), nullable=True)

    # Metadata
    is_active = Column(Boolean, default=True, index=True)
    last_synced_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<CSBEmployeeRef(emp_code={self.emp_code}, name={self.full_name})>"

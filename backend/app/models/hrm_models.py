"""
HRM Read-Only Models
=====================
Ánh xạ (reflect) các bảng Django HRM hiện có.
- KHÔNG tạo migration, KHÔNG thay đổi schema
- Chỉ đọc dữ liệu từ HRM database
- Dựa trên schema thực tế: hr_employee (55 col), auth_user
"""
from sqlalchemy import (
    Column, Integer, BigInteger, String, Boolean,
    Date, DateTime, Text, Numeric, ForeignKey
)
from sqlalchemy.orm import relationship
from app.core.hrm_database import HrmBase


class HrmAuthUser(HrmBase):
    """
    Ánh xạ bảng auth_user của Django HRM.
    """
    __tablename__ = "auth_user"

    id = Column(Integer, primary_key=True, index=True)
    password = Column(String(128))
    last_login = Column(DateTime, nullable=True)
    is_superuser = Column(Boolean, default=False)
    username = Column(String(150), unique=True, index=True)
    first_name = Column(String(150), nullable=True)
    last_name = Column(String(150), nullable=True)
    email = Column(String(254), nullable=True)
    is_staff = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    date_joined = Column(DateTime)

    # Liên kết ngược đến employee
    employee = relationship("HrmEmployee", back_populates="user", uselist=False)


class HrmEmployee(HrmBase):
    """
    Ánh xạ bảng hr_employee của HRM Django.
    55 columns — cập nhật theo schema thực tế.
    """
    __tablename__ = "hr_employee"

    # ── Định danh ───────────────────────────────────────────────
    id = Column(BigInteger, primary_key=True, index=True)
    emp_code = Column(String(32), unique=True, index=True)
    full_name = Column(String(120), index=True)
    user_id = Column(Integer, ForeignKey("auth_user.id"), nullable=True)

    # ── Tổ chức ──────────────────────────────────────────────────
    department = Column(String(120), index=True, nullable=True)
    part = Column(String(120), index=True, nullable=True)
    role = Column(String(120), nullable=True)
    level = Column(String(120), nullable=True)
    manager = Column(String(120), nullable=True)
    manager_emp_id = Column(BigInteger, nullable=True)
    is_trainer = Column(Boolean, default=False)

    # ── Trạng thái ───────────────────────────────────────────────
    status = Column(String(32), default="Active", index=True)
    is_resigned = Column(Boolean, default=False)
    resigned_date = Column(Date, nullable=True)
    resigned_reason = Column(Text, nullable=True)

    # ── Ngày tháng quan trọng ────────────────────────────────────
    join_date = Column(Date, nullable=True)
    dob = Column(Date, nullable=True)
    probation_time = Column(String(120), nullable=True)

    # ── Liên lạc ─────────────────────────────────────────────────
    email = Column(String(254), nullable=True)
    phone_number = Column(String(32), nullable=True)
    relative_phone = Column(String(32), nullable=True)
    address = Column(Text, nullable=True)
    temporary_address = Column(Text, nullable=True)

    # ── Cá nhân ──────────────────────────────────────────────────
    gender = Column(String(16), nullable=True)
    place_of_birth = Column(String(255), nullable=True)
    nationality = Column(String(120), nullable=True)
    ethnicity = Column(String(120), nullable=True)
    religion = Column(String(120), nullable=True)
    marriage = Column(String(32), nullable=True)
    health_type = Column(String(120), nullable=True)

    # ── Giấy tờ tùy thân ─────────────────────────────────────────
    cccd = Column(String(32), nullable=True)
    cccd_date_issued = Column(Date, nullable=True)
    cccd_place_issued = Column(String(255), nullable=True)
    cmnd_number = Column(String(32), nullable=True)
    cmnd_date_issued = Column(Date, nullable=True)
    cmnd_place_issued = Column(String(255), nullable=True)
    tax_code = Column(String(32), nullable=True)
    insurance_book = Column(String(32), nullable=True)

    # ── Học vấn / Kinh nghiệm ────────────────────────────────────
    degree = Column(String(120), nullable=True)
    education = Column(String(120), nullable=True)
    certifications = Column(Text, nullable=True)
    exp_work = Column(Text, nullable=True)
    contact_family = Column(Text, nullable=True)

    # ── Hợp đồng ─────────────────────────────────────────────────
    contract_1 = Column(String(120), nullable=True)
    contract_2 = Column(String(120), nullable=True)
    contract_3 = Column(String(120), nullable=True)
    contract_start_date = Column(Date, nullable=True)

    # ── Lương / Phụ cấp ──────────────────────────────────────────
    contract_salary = Column(Numeric, nullable=True)
    diligent_allowance = Column(Numeric, nullable=True)
    diligent_shift_allowance = Column(Numeric, nullable=True)
    leader_allowance = Column(Numeric, nullable=True)
    ot_meal_unit_amount = Column(Numeric, nullable=True)
    bhxh_employee_default = Column(Numeric, nullable=True)
    union_fee_default = Column(Numeric, nullable=True)

    # ── Media ─────────────────────────────────────────────────────
    photo = Column(String(100), nullable=True)

    # ── Quan hệ ────────────────────────────────────────────────────
    user = relationship("HrmAuthUser", back_populates="employee")

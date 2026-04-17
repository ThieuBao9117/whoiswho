from sqlalchemy import Column, Integer, String, Boolean, Date, DateTime, ForeignKey, Text, Numeric
from sqlalchemy.orm import relationship
from app.core.database import Base

class AuthUser(Base):
    """
    Mapping to Django's built-in auth_user table
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
    
    # Relationship to Employee
    employee_profile = relationship("Employee", back_populates="user", uselist=False)

class Employee(Base):
    """
    Mapping to HRM's hr_employee table.
    We'll assume the table name is "hr_employee" based on standard Django convention 
    for an app named "hr" and model "Employee".
    """
    __tablename__ = "hr_employee"
    
    id = Column(Integer, primary_key=True, index=True)
    emp_code = Column(String(32), unique=True, index=True)
    full_name = Column(String(120), index=True)
    
    department = Column(String(120), index=True, nullable=True)
    part = Column(String(120), index=True, nullable=True)
    role = Column(String(120), nullable=True)
    
    status = Column(String(32), default="Active", index=True)
    join_date = Column(Date, nullable=True)
    
    # Auth link
    user_id = Column(Integer, ForeignKey("auth_user.id"), nullable=True)
    user = relationship("AuthUser", back_populates="employee_profile")
    
    # You can add other fields from hr/models.py if needed here,
    # but for ConnectReward, we mainly need the identity, department, role, and join_date.
    photo = Column(String(100), nullable=True) # ImageField is typically a varchar path

    # Relationship to ConnectReward specific models can be defined in crw_models via back_populates

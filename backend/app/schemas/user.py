from pydantic import BaseModel
from typing import Optional, List
from datetime import date, datetime
from uuid import UUID


class UserLogin(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class EmployeeBase(BaseModel):
    """Employee profile from CSB local reference (synced from HRM)"""
    id: UUID
    hrm_employee_id: int
    emp_code: str
    full_name: str
    username: str
    email: Optional[str] = None
    department: Optional[str] = None
    part: Optional[str] = None
    role: Optional[str] = None
    status: Optional[str] = None
    join_date: Optional[datetime] = None
    photo: Optional[str] = None
    is_active: bool
    last_synced_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class UserMe(BaseModel):
    """Current authenticated user - from CSB employee reference"""
    id: UUID
    hrm_employee_id: int
    emp_code: str
    username: str
    full_name: str
    email: Optional[str] = None
    department: Optional[str] = None
    part: Optional[str] = None
    role: Optional[str] = None
    photo: Optional[str] = None
    status: str
    is_active: bool

    class Config:
        from_attributes = True

from pydantic import BaseModel
from typing import Optional, List
from datetime import date

class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class EmployeeBase(BaseModel):
    id: int
    emp_code: str
    full_name: str
    department: Optional[str] = None
    role: Optional[str] = None
    status: Optional[str] = None
    join_date: Optional[date] = None

class EmployeeOut(EmployeeBase):
    pass
    
    class Config:
        from_attributes = True

class UserMe(BaseModel):
    id: int
    username: str
    is_staff: bool
    employee_profile: Optional[EmployeeBase] = None
    
    class Config:
        from_attributes = True

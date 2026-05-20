from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from uuid import UUID
from app.models.crw_models import ConnectionStatus


class EmployeeOut(BaseModel):
    id: UUID
    emp_code: str
    full_name: str
    department: Optional[str] = None
    part: Optional[str] = None
    role: Optional[str] = None
    status: Optional[str] = None

    class Config:
        from_attributes = True

class ConnectionCreate(BaseModel):
    connector_id: int

class ConnectionOut(BaseModel):
    id: int
    new_hire_id: int
    connector_id: int
    status: ConnectionStatus
    created_at: datetime
    responded_at: Optional[datetime] = None
    
    new_hire: Optional[EmployeeOut] = None
    connector: Optional[EmployeeOut] = None
    
    class Config:
        from_attributes = True

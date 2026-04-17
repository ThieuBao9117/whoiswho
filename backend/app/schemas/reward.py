from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.models.crw_models import TargetType, RewardStatus
from app.schemas.user import EmployeeOut

class TargetBase(BaseModel):
    target_type: TargetType
    tl_required: int
    staff_required: int
    operator_required: int
    reward_amount: float
    is_active: bool = True

class TargetCreate(TargetBase):
    pass

class TargetOut(TargetBase):
    id: int
    
    class Config:
        from_attributes = True

class RewardOut(BaseModel):
    id: int
    employee_id: int
    target_id: int
    achieved_date: datetime
    status: RewardStatus
    notes: Optional[str] = None
    
    employee: Optional[EmployeeOut] = None
    target: Optional[TargetOut] = None
    
    class Config:
        from_attributes = True

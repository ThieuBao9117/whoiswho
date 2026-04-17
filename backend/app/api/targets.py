from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from app.core.database import get_db
from app.models.crw_models import CRWTarget, TargetType
from app.schemas.user import EmployeeOut # Reusing for simplicity or define new
from pydantic import BaseModel

router = APIRouter()

class TargetCreate(BaseModel):
    period_str: str
    operator_required: int
    leader_required: int
    pl_required: int
    tm_required: int
    gd_required: int
    reward_amount: float

@router.get("/", response_model=List[TargetCreate])
def get_targets(db: Session = Depends(get_db)):
    return db.query(CRWTarget).all()

@router.post("/")
def create_or_update_target(data: TargetCreate, db: Session = Depends(get_db)):
    target = db.query(CRWTarget).filter(CRWTarget.period_str == data.period_str).first()
    if not target:
        target = CRWTarget(period_str=data.period_str)
        db.add(target)
    
    target.operator_required = data.operator_required
    target.leader_required = data.leader_required
    target.pl_required = data.pl_required
    target.tm_required = data.tm_required
    target.gd_required = data.gd_required
    target.reward_amount = data.reward_amount
    
    db.commit()
    return {"status": "success"}

@router.get("/{period_str}")
def get_target_by_period(period_str: str, db: Session = Depends(get_db)):
    target = db.query(CRWTarget).filter(CRWTarget.period_str == period_str).first()
    if not target:
        # Return default
        return {
            "period_str": period_str,
            "operator_required": 5,
            "leader_required": 2,
            "pl_required": 1,
            "tm_required": 1,
            "gd_required": 0,
            "reward_amount": 500000.0
        }
    return target

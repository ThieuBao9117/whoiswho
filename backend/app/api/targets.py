"""
Targets API - Manage connection targets

Uses SQLAlchemy ORM for SQLite/PostgreSQL compatibility.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime
from pydantic import BaseModel

from app.core.database import get_db
from app.models.crw_models import CRWTarget

router = APIRouter(tags=["Targets"])

class TargetUpdate(BaseModel):
    period_str: str
    target_type: str = "MONTH"
    operator_required: int = 5
    leader_required: int = 2
    pl_required: int = 1
    tm_required: int = 1
    gd_required: int = 0
    reward_amount: float = 200000
    is_active: bool = True


@router.get("/")
def get_target(period: Optional[str] = None, db: Session = Depends(get_db)):
    """Get current target configuration"""
    if period:
        target = db.query(CRWTarget).filter(CRWTarget.period_str == period).first()
    else:
        target = db.query(CRWTarget).filter(
            CRWTarget.is_active == True
        ).order_by(CRWTarget.period_str.desc()).first()

    if not target:
        # Return default target
        return {
            "period_str": datetime.now().strftime("%Y-%m"),
            "target_type": "MONTH",
            "operator_required": 5,
            "leader_required": 2,
            "pl_required": 1,
            "tm_required": 1,
            "gd_required": 0,
            "reward_amount": 200000,
            "is_active": True
        }

    return {
        "id": target.id,
        "target_type": target.target_type.value if hasattr(target.target_type, 'value') else target.target_type,
        "period_str": target.period_str,
        "operator_required": target.operator_required,
        "leader_required": target.leader_required,
        "pl_required": target.pl_required,
        "tm_required": target.tm_required,
        "gd_required": target.gd_required,
        "reward_amount": target.reward_amount,
        "is_active": target.is_active
    }

@router.get("/{period}")
def get_target_by_period(period: str, db: Session = Depends(get_db)):
    """Get target configuration by period"""
    target = db.query(CRWTarget).filter(CRWTarget.period_str == period).first()
    
    if not target:
        return {
            "period_str": period,
            "target_type": "MONTH",
            "operator_required": 5,
            "leader_required": 2,
            "pl_required": 1,
            "tm_required": 1,
            "gd_required": 0,
            "reward_amount": 200000,
            "is_active": True
        }

    return {
        "id": target.id,
        "target_type": target.target_type.value if hasattr(target.target_type, 'value') else target.target_type,
        "period_str": target.period_str,
        "operator_required": target.operator_required,
        "leader_required": target.leader_required,
        "pl_required": target.pl_required,
        "tm_required": target.tm_required,
        "gd_required": target.gd_required,
        "reward_amount": target.reward_amount,
        "is_active": target.is_active
    }

@router.post("/")
def save_target(data: TargetUpdate, db: Session = Depends(get_db)):
    """Save target configuration"""
    target = db.query(CRWTarget).filter(CRWTarget.period_str == data.period_str).first()
    
    if target:
        target.target_type = data.target_type
        target.operator_required = data.operator_required
        target.leader_required = data.leader_required
        target.pl_required = data.pl_required
        target.tm_required = data.tm_required
        target.gd_required = data.gd_required
        target.reward_amount = data.reward_amount
        target.is_active = data.is_active
    else:
        target = CRWTarget(**data.dict())
        db.add(target)
    
    db.commit()
    db.refresh(target)
    return {"status": "success", "id": target.id}

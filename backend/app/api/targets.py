"""
Targets API - Manage connection targets

Uses SQLAlchemy ORM for SQLite/PostgreSQL compatibility.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime

from app.core.database import get_db
from app.models.crw_models import CRWTarget

router = APIRouter(tags=["Targets"])


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
            "reward_amount": 500000,
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

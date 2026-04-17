from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Dict
from datetime import datetime

from app.core.database import get_db
from app.models.hrm_models import Employee
from app.models.crw_models import CRWConnection, ConnectionStatus, CRWReward

router = APIRouter()

@router.get("/stats/{month}")
def get_admin_stats(month: str, db: Session=Depends(get_db)):
    # Basic stats for the dashboard cards
    total_employees = db.query(Employee).count()
    
    # connections count for month
    total_connections = db.query(CRWConnection).filter(
        CRWConnection.created_at.like(f"{month}%")
    ).count()
    
    # Rewards count
    # Note: In a real app, you'd check CRWReward table
    completed_kpi = db.query(CRWReward).filter(
        CRWReward.status == "APPROVED"
    ).count()
    
    # Dummy projected amount for MVP 
    projected_reward = completed_kpi * 500000 
    
    return {
        "total_employees": total_employees,
        "completed_kpi": completed_kpi,
        "projected_reward": projected_reward,
        "total_connections": total_connections
    }

@router.get("/report/{month}")
def get_monthly_report(month: str, db: Session=Depends(get_db)):
    # ... existing code ...
    return report

@router.get("/leaderboard")
def get_leaderboard(db: Session=Depends(get_db)):
    # Get top 20 connectors by accepted count
    top_connectors = db.query(
        Employee,
        func.count(CRWConnection.id).label("score")
    ).join(CRWConnection, CRWConnection.connector_id == Employee.id)\
     .filter(CRWConnection.status == ConnectionStatus.ACCEPTED)\
     .group_by(Employee.id)\
     .order_by(func.count(CRWConnection.id).desc())\
     .limit(20).all()
    
    return [
        {
            "id": c.Employee.emp_code,
            "name": c.Employee.full_name,
            "dept": c.Employee.department,
            "score": c.score,
            "avatar": c.Employee.photo or f"https://i.pravatar.cc/150?u={c.Employee.emp_code}",
            "isTop": idx == 0
        } for idx, c in enumerate(top_connectors)
    ]

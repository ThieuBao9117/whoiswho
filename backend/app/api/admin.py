"""
Admin API - Leaderboard, stats, reports

Uses SQLAlchemy ORM for SQLite/PostgreSQL compatibility.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, case
from typing import List, Optional
from datetime import datetime

from app.core.database import get_db
from app.models.csb_employee_ref import CSBEmployeeRef
from app.models.crw_models import CRWConnection
from app.services.game_logic import get_leaderboard_data, calculate_user_game_state

router = APIRouter(tags=["Admin"])


@router.get("/leaderboard")
def leaderboard(
    month: Optional[int] = Query(None, description="Month of the leaderboard (1-12)"),
    year: Optional[int] = Query(None, description="Year of the leaderboard"),
    limit: Optional[int] = Query(50, description="Max number of entries to return"),
    db: Session = Depends(get_db)
):
    """
    Get connection leaderboard sorted by completion speed for a specific month.
    
    - month/year default to current month/year if not provided.
    - Only includes employees who completed their target (has_won=True) with win_time in that month.
    - Results include: rank, name, dept, role_label, days_to_complete, win_date.
    """
    now = datetime.utcnow()
    target_month = month or now.month
    target_year = year or now.year

    data = get_leaderboard_data(db, limit=limit, target_month=target_month, target_year=target_year)

    return {
        "month": target_month,
        "year": target_year,
        "total": len(data),
        "entries": data,
    }


@router.get("/stats/{period}")
def get_stats(period: str, db: Session = Depends(get_db)):
    """Get stats for a period"""
    total_employees = db.query(CSBEmployeeRef).filter(
        CSBEmployeeRef.is_active == True
    ).count()

    total_connections = db.query(CRWConnection).filter(
        CRWConnection.status == "ACCEPTED"
    ).count()

    return {
        "total_employees": total_employees,
        "total_connections": total_connections,
        "period": period
    }


@router.get("/report")
def get_report(db: Session = Depends(get_db)):
    """Get connection report for all employees"""
    employees = db.query(CSBEmployeeRef).filter(
        CSBEmployeeRef.is_active == True
    ).all()

    result = []
    for emp in employees:
        state = calculate_user_game_state(db, emp)

        result.append({
            "emp_code": emp.emp_code,
            "full_name": emp.full_name,
            "department": emp.department or "N/A",
            "role": emp.role or "N/A",
            "is_operator": state.get("is_operator", False),
            "count": f"{state['current_connections']}/{state['target_connections']}",
            "reward": 500000 if state['has_won'] else 0,
            "has_won": state['has_won'],
            "is_expired": state['is_expired'],
            "days_remaining": state['days_remaining'],
            "days_to_complete": state.get("days_to_complete"),
        })

    # Sort by count descending
    result.sort(key=lambda x: int(x["count"].split("/")[0]), reverse=True)
    return result

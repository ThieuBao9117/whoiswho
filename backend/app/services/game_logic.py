from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.csb_employee_ref import CSBEmployeeRef
from app.models.crw_models import CRWConnection, ConnectionStatus, CRWTarget, TargetType


def get_target_for_employee(db: Session, emp: CSBEmployeeRef) -> int:
    """
    Get the required connection target for an employee.
    Looks up CRWTarget for the current active monthly target.
    Falls back to 9 if no target is configured.
    """
    role = (emp.role or "").lower()
    is_operator = "operator" in role or "công nhân" in role

    # Try to find active monthly target
    target = db.query(CRWTarget).filter(
        CRWTarget.is_active == True,
        CRWTarget.target_type == TargetType.MONTH
    ).order_by(CRWTarget.id.desc()).first()

    if not target:
        return 9  # fallback default

    if is_operator:
        return target.operator_required or 5
    
    role_lower = role
    if "leader" in role_lower and "part" in role_lower:
        return target.pl_required or 1
    if "leader" in role_lower or "trưởng ca" in role_lower:
        return target.leader_required or 2
    if "manager" in role_lower or "team manager" in role_lower:
        return target.tm_required or 1
    if "gd" in role_lower or "giám đốc" in role_lower:
        return target.gd_required or 0

    # Default staff: sum of all requirements
    total = (
        (target.operator_required or 5) +
        (target.leader_required or 2) +
        (target.pl_required or 1) +
        (target.tm_required or 1)
    )
    return total


def calculate_user_game_state(db: Session, emp: CSBEmployeeRef) -> Dict[str, Any]:
    """
    Calculate the gamification state for an employee.
    Rules:
    - Operator (Công nhân): 30 days from join_date.
    - Office staff (NV văn phòng): 60 days from join_date.
    - Target: dynamic from CRWTarget table, defaults to role-based sum.
    """
    if not emp.join_date:
        join_date = emp.created_at or datetime.utcnow()
    else:
        join_date = emp.join_date

    # 1. Calculate duration based on role
    role = (emp.role or "").lower()
    is_operator = "operator" in role or "công nhân" in role

    duration_days = 30 if is_operator else 60
    deadline = join_date + timedelta(days=duration_days)

    now = datetime.utcnow()
    days_remaining = (deadline - now).days
    is_expired = now > deadline

    # 2. Get accepted connections
    connections = db.query(CRWConnection).filter(
        CRWConnection.status == ConnectionStatus.ACCEPTED,
        ((CRWConnection.connector_id == emp.id) | (CRWConnection.new_hire_id == emp.id))
    ).order_by(CRWConnection.responded_at.asc()).all()

    current_count = len(connections)

    # Dynamic target
    target_count = get_target_for_employee(db, emp)

    has_won = target_count > 0 and current_count >= target_count

    # 3. Calculate completion time if won
    completion_time_seconds = None
    win_time = None
    days_to_complete = None

    if has_won and target_count > 0:
        # The connection that hit the target (Nth connection)
        winning_connection = connections[target_count - 1]
        win_time = winning_connection.responded_at or winning_connection.created_at

        # Check if the user won BEFORE their deadline
        if win_time and win_time <= deadline:
            completion_time_seconds = (win_time - join_date).total_seconds()
            days_to_complete = int(completion_time_seconds // 86400)
        else:
            # They hit the target AFTER the deadline, so they didn't actually win
            has_won = False
            win_time = None
            days_to_complete = None

    # Prevent playing if already won OR expired (but only if target > 0)
    can_play = not has_won and not is_expired and target_count > 0

    return {
        "join_date": join_date.isoformat(),
        "deadline": deadline.isoformat(),
        "days_remaining": max(0, days_remaining),
        "is_expired": is_expired,
        "current_connections": current_count,
        "target_connections": target_count,
        "has_won": has_won,
        "win_time": win_time,
        "completion_time_seconds": completion_time_seconds,
        "days_to_complete": days_to_complete,
        "can_play": can_play,
        "role": emp.role or "",
        "is_operator": is_operator,
    }


def get_leaderboard_data(
    db: Session,
    limit: int = 50,
    target_month: int = None,
    target_year: int = None
) -> List[Dict[str, Any]]:
    """
    Get leaderboard for a specific month, ranked by fastest completion (days).
    Optimized to use O(1) queries instead of O(N).
    """
    if target_year is None:
        target_year = datetime.utcnow().year
    if target_month is None:
        target_month = datetime.utcnow().month

    target = db.query(CRWTarget).filter(
        CRWTarget.is_active == True,
        CRWTarget.target_type == TargetType.MONTH
    ).order_by(CRWTarget.id.desc()).first()

    # Pre-fetch all accepted connections
    from collections import defaultdict
    connections_by_user = defaultdict(list)
    
    all_accepted = db.query(CRWConnection).filter(
        CRWConnection.status == ConnectionStatus.ACCEPTED
    ).order_by(CRWConnection.responded_at.asc()).all()
    
    for conn in all_accepted:
        connections_by_user[conn.connector_id].append(conn)
        connections_by_user[conn.new_hire_id].append(conn)

    # We only need to check employees who have connections
    employee_ids_with_conns = list(connections_by_user.keys())
    if not employee_ids_with_conns:
        return []

    employees = db.query(CSBEmployeeRef).filter(
        CSBEmployeeRef.id.in_(employee_ids_with_conns),
        CSBEmployeeRef.is_active == True
    ).all()

    winners = []

    for emp in employees:
        role = (emp.role or "").lower()
        is_operator = "operator" in role or "công nhân" in role
        
        # Calculate target_count inline
        if not target:
            target_count = 9
        elif is_operator:
            target_count = target.operator_required or 5
        else:
            if "leader" in role and "part" in role:
                target_count = target.pl_required or 1
            elif "leader" in role or "trưởng ca" in role:
                target_count = target.leader_required or 2
            elif "manager" in role or "team manager" in role:
                target_count = target.tm_required or 1
            elif "gd" in role or "giám đốc" in role:
                target_count = target.gd_required or 0
            else:
                target_count = (target.operator_required or 5) + (target.leader_required or 2) + (target.pl_required or 1) + (target.tm_required or 1)
                
        conns = connections_by_user.get(emp.id, [])
        current_count = len(conns)
        
        has_won = target_count > 0 and current_count >= target_count
        
        if not has_won:
            continue
            
        join_date = emp.join_date if emp.join_date else (emp.created_at or datetime.utcnow())
        duration_days = 30 if is_operator else 60
        deadline = join_date + timedelta(days=duration_days)
        
        winning_connection = conns[target_count - 1]
        win_time = winning_connection.responded_at or winning_connection.created_at
        
        # Check if the user won BEFORE their deadline
        if not win_time or win_time > deadline:
            continue
            
        # Check if win time is in target month/year
        if win_time.year != target_year or win_time.month != target_month:
            continue
            
        completion_time_seconds = (win_time - join_date).total_seconds()
        days = int(completion_time_seconds // 86400)
        hours = int((completion_time_seconds % 86400) // 3600)

        time_str = f"{days} ngày"
        if hours > 0 or days == 0:
            time_str += f" {hours} giờ"

        role_label = "Operator" if is_operator else "Staff"

        winners.append({
            "id": emp.id,
            "emp_code": emp.emp_code,
            "name": emp.full_name,
            "dept": emp.department or "N/A",
            "role": emp.role or "Staff",
            "role_label": role_label,
            "is_operator": is_operator,
            "score": time_str,
            "completion_time": time_str,
            "days_to_complete": days,
            "raw_seconds": completion_time_seconds,
            "win_date": win_time.strftime("%d/%m/%Y"),
            "avatar": emp.photo or f"https://i.pravatar.cc/150?u={emp.emp_code}",
        })

    # Sort by fastest completion time
    winners.sort(key=lambda x: x["raw_seconds"])

    # Add ranking and isTop flag
    for idx, w in enumerate(winners):
        w["rank"] = idx + 1
        w["isTop"] = idx == 0

    return winners[:limit]

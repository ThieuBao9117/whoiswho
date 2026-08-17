from datetime import datetime, timedelta, timezone
from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.csb_employee_ref import CSBEmployeeRef
from app.models.crw_models import CRWConnection, ConnectionStatus, CRWTarget, TargetType

# Chỉ tính nhân viên onboard từ tháng 4/2026 trở đi
# Nhân viên join trước ngày này không được tính trong bảng xếp hạng
PROGRAM_START_DATE = datetime(2026, 4, 1, tzinfo=timezone.utc)


def get_target_for_employee(db: Session, emp: CSBEmployeeRef) -> int:
    """
    Get the required connection target for an employee based on fixed rules:
    - Operator / Công nhân: 10
    - Team Leader / Trưởng ca: 20  (KHÔNG bao gồm Part Leader)
    - Officer / Others (bao gồm Part Leader): 30
    """
    role = (emp.role or "").lower()

    if "operator" in role or "công nhân" in role:
        return 10
    # Chỉ team leader và trưởng ca mới là 20, KHÔNG phải part leader
    if "team leader" in role or "trưởng ca" in role:
        return 20

    return 30


def calculate_user_game_state(db: Session, emp: CSBEmployeeRef) -> Dict[str, Any]:
    """
    Calculate the gamification state for an employee.
    Rules:
    - Operator (Công nhân): 30 days from join_date.
    - Office staff (NV văn phòng): 60 days from join_date.
    - Target: dynamic from CRWTarget table, defaults to role-based sum.
    """
    if not emp.join_date:
        join_date = emp.created_at or datetime.now(timezone.utc)
    else:
        join_date = emp.join_date
        # Normalize to timezone-aware if naive (e.g. legacy data)
        if join_date.tzinfo is None:
            join_date = join_date.replace(tzinfo=timezone.utc)

    # 1. Calculate duration based on role
    role = (emp.role or "").lower()
    is_operator = "operator" in role or "công nhân" in role

    duration_days = 30 if is_operator else 60
    deadline = join_date + timedelta(days=duration_days)

    now = datetime.now(timezone.utc)
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

    # Cho phép kết nối thêm ngay cả khi đã đạt chỉ tiêu (has_won).
    # Chỉ khóa khi hết hạn (is_expired) và chưa đạt mục tiêu.
    can_play = not is_expired and target_count > 0

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
    Only includes employees who completed their target (has_won=True)
    with win_time in that exact month.
    Optimized to use O(1) queries instead of O(N).
    """
    if target_year is None:
        target_year = datetime.now(timezone.utc).year
    if target_month is None:
        target_month = datetime.now(timezone.utc).month

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
        # Chỉ tính NV onboard từ tháng 4/2026 trở đi
        emp_join = emp.join_date if emp.join_date else (emp.created_at or datetime.now(timezone.utc))
        if emp_join.tzinfo is None:
            emp_join = emp_join.replace(tzinfo=timezone.utc)
        if emp_join < PROGRAM_START_DATE:
            continue

        role = (emp.role or "").lower()
        is_operator = "operator" in role or "công nhân" in role

        # Calculate target_count inline
        # Chỉ team leader và trưởng ca mới là 20, KHÔNG phải part leader
        if is_operator:
            target_count = 10
        elif "team leader" in role or "trưởng ca" in role:
            target_count = 20
        else:
            target_count = 30

        conns = connections_by_user.get(emp.id, [])
        current_count = len(conns)

        has_won = target_count > 0 and current_count >= target_count

        if not has_won:
            continue

        join_date = emp.join_date if emp.join_date else (emp.created_at or datetime.now(timezone.utc))
        # Normalize to timezone-aware if naive
        if join_date.tzinfo is None:
            join_date = join_date.replace(tzinfo=timezone.utc)
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
            "dept": (emp.part or emp.department) or "N/A",
            "role": emp.role or "Staff",
            "role_label": role_label,
            "is_operator": is_operator,
            "score": time_str,
            "completion_time": time_str,
            "raw_count": len(conns),
            "days_to_complete": days,
            "raw_seconds": completion_time_seconds,
            "win_date": win_time.strftime("%d/%m/%Y"),
            "avatar": (f"http://hrm.csbrg.com{emp.photo}" if emp.photo and emp.photo.startswith('/') else emp.photo) or f"https://ui-avatars.com/api/?name={emp.full_name or emp.emp_code}&background=random&color=fff&size=200&bold=true",
        })

    # Sort by fastest completion time
    winners.sort(key=lambda x: x["raw_seconds"])

    # Add ranking and isTop flag
    for idx, w in enumerate(winners):
        w["rank"] = idx + 1
        w["isTop"] = idx == 0

    return winners[:limit]


def get_live_ranking_data(
    db: Session,
    limit: int = 50,
    target_month: int = None,
    target_year: int = None
) -> List[Dict[str, Any]]:
    """
    Get live ranking for a specific month.
    - Carries over connections for in-progress users (still within their deadline).
    - Excludes users who won BEFORE this month (already counted in past months).
    - Excludes users whose deadline has passed and have NOT won (they can no longer win).
    """
    if target_year is None:
        target_year = datetime.now(timezone.utc).year
    if target_month is None:
        target_month = datetime.now(timezone.utc).month

    # Calculate start and end of target month without dateutil
    target_start = datetime(target_year, target_month, 1, tzinfo=timezone.utc)
    if target_month == 12:
        target_end = datetime(target_year + 1, 1, 1, tzinfo=timezone.utc)
    else:
        target_end = datetime(target_year, target_month + 1, 1, tzinfo=timezone.utc)

    # Get all accepted connections up to the end of target month
    connections = db.query(CRWConnection).filter(
        CRWConnection.status == ConnectionStatus.ACCEPTED,
        CRWConnection.responded_at < target_end
    ).order_by(CRWConnection.responded_at.asc()).all()

    from collections import defaultdict
    connections_by_user = defaultdict(list)
    for conn in connections:
        connections_by_user[conn.connector_id].append(conn)
        connections_by_user[conn.new_hire_id].append(conn)

    employee_ids = list(connections_by_user.keys())
    if not employee_ids:
        return []

    employees = db.query(CSBEmployeeRef).filter(
        CSBEmployeeRef.id.in_(employee_ids),
        CSBEmployeeRef.is_active == True
    ).all()

    now = datetime.now(timezone.utc)
    winners = []
    for emp in employees:
        emp_join = emp.join_date if emp.join_date else (emp.created_at or now)
        if emp_join.tzinfo is None:
            emp_join = emp_join.replace(tzinfo=timezone.utc)
        if emp_join < PROGRAM_START_DATE:
            continue

        role = (emp.role or "").lower()
        is_operator = "operator" in role or "công nhân" in role

        # Chỉ team leader và trưởng ca mới là 20, KHÔNG phải part leader
        target_count = 10 if is_operator else (20 if "team leader" in role or "trưởng ca" in role else 30)

        conns = connections_by_user.get(emp.id, [])

        # Filter connections that are valid (responded before their personal deadline)
        duration_days = 30 if is_operator else 60
        deadline = emp_join + timedelta(days=duration_days)
        is_expired = now > deadline

        valid_conns = []
        for c in conns:
            ct = (c.responded_at or c.created_at)
            if ct.tzinfo is None:
                ct = ct.replace(tzinfo=timezone.utc)
            if ct <= deadline:
                valid_conns.append(c)

        current_count = len(valid_conns)
        has_won = target_count > 0 and current_count >= target_count

        win_time = None
        win_date = None
        if has_won:
            win_time = valid_conns[target_count - 1].responded_at or valid_conns[target_count - 1].created_at
            if win_time.tzinfo is None:
                win_time = win_time.replace(tzinfo=timezone.utc)

            # Exclude: won before the start of the target month (already shown in past month)
            if win_time < target_start:
                continue

            win_date = win_time.strftime("%d/%m/%Y")

        # Exclude: deadline passed and still haven't won — they can no longer complete
        if is_expired and not has_won:
            continue

        # Exclude: no valid connections at all
        if current_count == 0:
            continue

        role_label = "Operator" if is_operator else "Staff"

        winners.append({
            "id": emp.id,
            "emp_code": emp.emp_code,
            "name": emp.full_name,
            "dept": (emp.part or emp.department) or "N/A",
            "role": emp.role or "Staff",
            "role_label": role_label,
            "is_operator": is_operator,
            "score": f"{current_count} kết nối",
            "completion_time": f"{current_count} kết nối",
            "raw_count": current_count,
            "target_connections": target_count,
            "has_won": has_won,
            "is_expired": is_expired,
            "win_date": win_date,
            "avatar": (f"http://hrm.csbrg.com{emp.photo}" if emp.photo and emp.photo.startswith('/') else emp.photo) or f"https://ui-avatars.com/api/?name={emp.full_name or emp.emp_code}&background=random&color=fff&size=200&bold=true",
        })

    winners.sort(key=lambda x: x["raw_count"], reverse=True)

    # Add ranking and isTop flag
    for idx, w in enumerate(winners):
        w["rank"] = idx + 1
        w["isTop"] = idx == 0

    return winners[:limit]

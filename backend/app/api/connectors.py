"""
Connectors API - Search for employees to be connectors
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.core.database import get_db
from app.api.auth import get_current_user
from app.models.csb_employee_ref import CSBEmployeeRef
from app.models.crw_models import CRWConnection, ConnectionStatus

router = APIRouter()


@router.get("/filters")
def get_filter_options(
    current_user: CSBEmployeeRef = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Return distinct values for all filterable fields"""
    def distinct_vals(col):
        rows = db.query(col).filter(
            CSBEmployeeRef.is_active == True,
            col.isnot(None),
            col != ''
        ).distinct().order_by(col).all()
        return [r[0] for r in rows]

    return {
        "entities":    distinct_vals(CSBEmployeeRef.entity),
        "divisions":   distinct_vals(CSBEmployeeRef.division),
        "departments": distinct_vals(CSBEmployeeRef.department),
        "teams":       distinct_vals(CSBEmployeeRef.team),
        "parts":       distinct_vals(CSBEmployeeRef.part),
        "positions":   distinct_vals(CSBEmployeeRef.position),
        "roles":       distinct_vals(CSBEmployeeRef.role),
    }


@router.get("/search")
def search_connectors(
    name:       str = Query(None),
    entity:     str = Query(None),
    division:   str = Query(None),
    department: str = Query(None),
    team:       str = Query(None),
    part:       str = Query(None),
    position:   str = Query(None),
    role:       str = Query(None),
    current_user: CSBEmployeeRef = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Search employees with full org-hierarchy filters, returns connection status"""
    query = db.query(CSBEmployeeRef).filter(
        CSBEmployeeRef.is_active == True,
        CSBEmployeeRef.id != current_user.id
    )

    if name:       query = query.filter(CSBEmployeeRef.full_name.ilike(f"%{name}%"))
    if entity:     query = query.filter(CSBEmployeeRef.entity.ilike(f"%{entity}%"))
    if division:   query = query.filter(CSBEmployeeRef.division.ilike(f"%{division}%"))
    if department: query = query.filter(CSBEmployeeRef.department.ilike(f"%{department}%"))
    if team:       query = query.filter(CSBEmployeeRef.team.ilike(f"%{team}%"))
    if part:       query = query.filter(CSBEmployeeRef.part.ilike(f"%{part}%"))
    if position:   query = query.filter(CSBEmployeeRef.position.ilike(f"%{position}%"))
    if role:       query = query.filter(CSBEmployeeRef.role.ilike(f"%{role}%"))

    employees = query.order_by(CSBEmployeeRef.full_name).limit(100).all()

    # Build connection status map for current user
    # Check both: where user sent invites (new_hire) and received invites (connector)
    sent = db.query(CRWConnection).filter(
        CRWConnection.new_hire_id == current_user.id
    ).all()
    received = db.query(CRWConnection).filter(
        CRWConnection.connector_id == current_user.id
    ).all()
    
    # Merge both into status map (received takes precedence if exists)
    status_map = {}
    for c in sent:
        status_map[c.connector_id] = c.status
    for c in received:
        # If there's already a status, prefer the most recent one (likely ACCEPTED)
        if c.connector_id not in status_map or c.status == ConnectionStatus.ACCEPTED:
            status_map[c.connector_id] = c.status

    result = []
    for emp in employees:
        raw_status = status_map.get(emp.id)
        conn_status = raw_status.value if hasattr(raw_status, 'value') else (raw_status or "none")
        result.append({
            "id":           emp.id,
            "emp_code":     emp.emp_code,
            "full_name":    emp.full_name,
            "entity":       emp.entity,
            "division":     emp.division,
            "department":   emp.department,
            "team":         emp.team,
            "part":         emp.part,
            "position":     emp.position,
            "role":         emp.role,
            "photo":        emp.photo,
            "conn_status":  conn_status,  # none | PENDING | ACCEPTED | REJECTED
        })

    return result


@router.get("/{emp_id}")
def get_connector(
    emp_id: int,
    current_user: CSBEmployeeRef = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get specific employee by ID"""
    employee = db.query(CSBEmployeeRef).filter(CSBEmployeeRef.id == emp_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    return {
        "id":         employee.id,
        "emp_code":   employee.emp_code,
        "full_name":  employee.full_name,
        "entity":     employee.entity,
        "division":   employee.division,
        "department": employee.department,
        "team":       employee.team,
        "part":       employee.part,
        "position":   employee.position,
        "role":       employee.role,
        "photo":      employee.photo,
    }

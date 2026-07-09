"""
Connections API - Manage connection invites

Uses SQLAlchemy ORM for SQLite/PostgreSQL compatibility.
"""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Query
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
import json

from app.core.database import get_db
from app.api.auth import get_current_user
from app.models.csb_employee_ref import CSBEmployeeRef
from app.models.crw_models import CRWConnection, ConnectionStatus
from app.services.synology_chat import send_connection_request, send_congratulations_message
from app.services.game_logic import calculate_user_game_state, get_leaderboard_data

router = APIRouter()


@router.post("/invite")
def send_invite(
    data: dict,
    background_tasks: BackgroundTasks,
    current_user: CSBEmployeeRef = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Send a connection invite to another employee"""
    connector_id = data.get("connector_id")
    if not connector_id:
        raise HTTPException(status_code=400, detail="Missing connector_id")

    # Check if user is allowed to play
    game_state = calculate_user_game_state(db, current_user)
    if not game_state["can_play"]:
        if game_state["has_won"]:
            raise HTTPException(status_code=403, detail="You have already won the game!")
        else:
            raise HTTPException(status_code=403, detail="Your mission has expired!")

    # Check if connector exists
    from sqlalchemy import func, cast, String
    connector = db.query(CSBEmployeeRef).filter(
        (cast(CSBEmployeeRef.id, String) == str(connector_id)) | 
        (func.lower(CSBEmployeeRef.emp_code) == func.lower(str(connector_id))) |
        (func.lower(CSBEmployeeRef.username) == func.lower(str(connector_id)))
    ).first()
    
    if not connector:
        raise HTTPException(status_code=404, detail="Connector not found")

    # Check existing connection
    existing = db.query(CRWConnection).filter(
        CRWConnection.new_hire_id == current_user.id,
        CRWConnection.connector_id == connector.id
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="Connection invite already exists")

    # Create connection
    new_connection = CRWConnection(
        new_hire_id=current_user.id,
        connector_id=connector.id,
        status=ConnectionStatus.PENDING,
        created_at=datetime.utcnow()
    )
    db.add(new_connection)
    
    try:
        db.commit()
        db.refresh(new_connection)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

    # Send Synology Chat notification in background
    background_tasks.add_task(
        send_connection_request,
        connection_id=str(new_connection.id),
        sender_name=current_user.full_name,
        sender_emp_code=current_user.emp_code,
        receiver_name=connector.full_name,
        receiver_emp_code=connector.emp_code
    )

    return {
        "id": new_connection.id,
        "status": "PENDING",
        "connector_id": connector.id,
        "new_hire_id": current_user.id
    }


@router.get("/my")
def my_sent_invites(
    current_user: CSBEmployeeRef = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List connections initiated by current user"""
    connections = db.query(CRWConnection).join(
        CSBEmployeeRef, CRWConnection.connector_id == CSBEmployeeRef.id
    ).filter(
        CRWConnection.new_hire_id == current_user.id
    ).order_by(CRWConnection.created_at.desc()).all()

    result = []
    for conn in connections:
        connector = db.query(CSBEmployeeRef).filter(CSBEmployeeRef.id == conn.connector_id).first()
        result.append({
            "id": conn.id,
            "status": conn.status.value if hasattr(conn.status, 'value') else conn.status,
            "created_at": conn.created_at.isoformat() if conn.created_at else None,
            "responded_at": conn.responded_at.isoformat() if conn.responded_at else None,
            "connector": {
                "full_name": connector.full_name if connector else "Unknown",
                "emp_code": connector.emp_code if connector else "Unknown",
                "department": connector.department if connector else "Unknown",
                "role": connector.role if connector else "Unknown",
            }
        })

    return result


@router.get("/incoming")
def incoming_invites(
    current_user: CSBEmployeeRef = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List pending invites for current user"""
    connections = db.query(CRWConnection).join(
        CSBEmployeeRef, CRWConnection.new_hire_id == CSBEmployeeRef.id
    ).filter(
        CRWConnection.connector_id == current_user.id,
        CRWConnection.status == "PENDING"
    ).order_by(CRWConnection.created_at.desc()).all()

    result = []
    for conn in connections:
        new_hire = db.query(CSBEmployeeRef).filter(CSBEmployeeRef.id == conn.new_hire_id).first()
        result.append({
            "id": conn.id,
            "created_at": conn.created_at.isoformat() if conn.created_at else None,
            "new_hire": {
                "full_name": new_hire.full_name if new_hire else "Unknown",
                "emp_code": new_hire.emp_code if new_hire else "Unknown",
                "department": new_hire.department if new_hire else "Unknown"
            }
        })

    return result


@router.get("/received")
def received_connections(
    month: str = Query(None),
    current_user: CSBEmployeeRef = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """All accepted connections received by current user (as connector), optionally filtered by month"""
    from sqlalchemy import extract

    query = db.query(CRWConnection).filter(
        CRWConnection.connector_id == current_user.id,
        CRWConnection.status == ConnectionStatus.ACCEPTED
    )

    if month:
        try:
            year, mon = month.split('-')
            query = query.filter(
                extract('year', CRWConnection.responded_at) == int(year),
                extract('month', CRWConnection.responded_at) == int(mon)
            )
        except Exception:
            pass

    connections = query.order_by(CRWConnection.responded_at.desc()).all()

    result = []
    for conn in connections:
        new_hire = db.query(CSBEmployeeRef).filter(CSBEmployeeRef.id == conn.new_hire_id).first()
        result.append({
            "id": conn.id,
            "status": conn.status.value if hasattr(conn.status, 'value') else conn.status,
            "created_at": conn.created_at.isoformat() if conn.created_at else None,
            "responded_at": conn.responded_at.isoformat() if conn.responded_at else None,
            "new_hire": {
                "id": new_hire.id if new_hire else None,
                "full_name": new_hire.full_name if new_hire else "Unknown",
                "emp_code": new_hire.emp_code if new_hire else "Unknown",
                "department": new_hire.department if new_hire else "Unknown",
                "part": new_hire.part if new_hire else None,
                "role": new_hire.role if new_hire else "Unknown",
                "photo": new_hire.photo if new_hire else None,
            }
        })

    return result


@router.put("/{conn_id}")
def update_invite_status(
    conn_id: str,
    background_tasks: BackgroundTasks,
    accept: bool = Query(True),
    current_user: CSBEmployeeRef = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Accept or reject a connection invite. If acceptance completes new_hire's target, fires congratulations."""
    connection = db.query(CRWConnection).filter(CRWConnection.id == conn_id).first()

    if not connection:
        raise HTTPException(status_code=404, detail="Not found")

    if connection.connector_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    # Check game state BEFORE accepting to detect if they are winning for the first time
    new_hire = db.query(CSBEmployeeRef).filter(CSBEmployeeRef.id == connection.new_hire_id).first()
    state_before = calculate_user_game_state(db, new_hire) if new_hire else None
    already_won_before = state_before["has_won"] if state_before else True

    new_status = ConnectionStatus.ACCEPTED if accept else ConnectionStatus.REJECTED
    connection.status = new_status
    connection.responded_at = datetime.utcnow()

    db.commit()

    # Check if accepting this connection caused new_hire to win for the first time
    just_won = False
    rank = None
    days_to_complete = None

    if accept and new_hire and not already_won_before:
        state_after = calculate_user_game_state(db, new_hire)
        if state_after["has_won"]:
            just_won = True
            days_to_complete = state_after.get("days_to_complete")
            role_label = "Operator" if state_after.get("is_operator") else "Staff"

            # Get current leaderboard to determine rank
            now = datetime.utcnow()
            leaderboard = get_leaderboard_data(db, target_month=now.month, target_year=now.year)
            for entry in leaderboard:
                if entry["id"] == new_hire.id:
                    rank = entry["rank"]
                    break

            # Send congratulations via Synology Chat in background
            background_tasks.add_task(
                send_congratulations_message,
                emp_name=new_hire.full_name,
                emp_code=new_hire.emp_code,
                days_to_complete=days_to_complete or 0,
                rank=rank or 1,
                target_month=now.month,
                target_year=now.year,
                role_label=role_label,
            )

    return {
        "status": "success",
        "connection_id": conn_id,
        "new_status": new_status,
        "just_won": just_won,
        "rank": rank,
        "days_to_complete": days_to_complete,
    }


@router.get("/all")
def all_connections(
    current_user: CSBEmployeeRef = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all connections (both as new_hire and as connector) for current user"""
    result = []
    
    # Connections where user is the new_hire (user sent invites)
    sent_conns = db.query(CRWConnection).filter(
        CRWConnection.new_hire_id == current_user.id
    ).order_by(CRWConnection.created_at.desc()).all()
    
    for conn in sent_conns:
        connector = db.query(CSBEmployeeRef).filter(CSBEmployeeRef.id == conn.connector_id).first()
        result.append({
            "id": conn.id,
            "status": conn.status.value if hasattr(conn.status, 'value') else conn.status,
            "created_at": conn.created_at.isoformat() if conn.created_at else None,
            "responded_at": conn.responded_at.isoformat() if conn.responded_at else None,
            "direction": "sent",
            "other_user": {
                "id": connector.id if connector else None,
                "full_name": connector.full_name if connector else "Unknown",
                "emp_code": connector.emp_code if connector else "Unknown",
                "department": (connector.part or connector.department) if connector else None,
                "role": connector.role if connector else None,
                "photo": connector.photo if connector else None,
            }
        })
    
    # Connections where user is the connector (user received invites)
    received_conns = db.query(CRWConnection).filter(
        CRWConnection.connector_id == current_user.id
    ).order_by(CRWConnection.created_at.desc()).all()
    
    for conn in received_conns:
        # Skip if already added (both accepted)
        if any(c['id'] == conn.id for c in result):
            continue
        new_hire = db.query(CSBEmployeeRef).filter(CSBEmployeeRef.id == conn.new_hire_id).first()
        result.append({
            "id": conn.id,
            "status": conn.status.value if hasattr(conn.status, 'value') else conn.status,
            "created_at": conn.created_at.isoformat() if conn.created_at else None,
            "responded_at": conn.responded_at.isoformat() if conn.responded_at else None,
            "direction": "received",
            "other_user": {
                "id": new_hire.id if new_hire else None,
                "full_name": new_hire.full_name if new_hire else "Unknown",
                "emp_code": new_hire.emp_code if new_hire else "Unknown",
                "department": (new_hire.part or new_hire.department) if new_hire else None,
                "role": new_hire.role if new_hire else None,
                "photo": new_hire.photo if new_hire else None,
            }
        })
    
    return result

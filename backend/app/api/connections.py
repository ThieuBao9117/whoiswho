from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from app.core.database import get_db
from app.models.hrm_models import AuthUser, Employee
from app.models.crw_models import CRWConnection, ConnectionStatus
from app.schemas.connection import ConnectionOut, ConnectionCreate
from app.api.auth import get_current_user
from app.services.synology_chat import send_connection_request

router = APIRouter()

@router.post("/invite", response_model=ConnectionOut)
def send_invite(
    data: ConnectionCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_user)
):
    if not current_user.employee_profile:
        raise HTTPException(status_code=400, detail="User has no employee profile")
    
    # Check existing
    existing = db.query(CRWConnection).filter(
        CRWConnection.new_hire_id == current_user.employee_profile.id,
        CRWConnection.connector_id == data.connector_id
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="Connection invite already exists")
        
    conn = CRWConnection(
        new_hire_id=current_user.employee_profile.id,
        connector_id=data.connector_id,
        status=ConnectionStatus.PENDING
    )
    db.add(conn)
    db.commit()
    db.refresh(conn)
    
    # Get connector data for webhook
    connector = db.query(Employee).filter(Employee.id == data.connector_id).first()
    if connector:
        background_tasks.add_task(
            send_connection_request,
            connection_id=conn.id,
            sender_name=current_user.employee_profile.full_name,
            sender_emp_code=current_user.employee_profile.emp_code,
            receiver_name=connector.full_name,
            receiver_emp_code=connector.emp_code
        )
        
    return conn

@router.get("/my", response_model=List[ConnectionOut])
def my_sent_invites(
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_user)
):
    if not current_user.employee_profile:
        return []
    return db.query(CRWConnection).filter(
        CRWConnection.new_hire_id == current_user.employee_profile.id
    ).all()

@router.get("/incoming", response_model=List[ConnectionOut])
def incoming_invites(
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_user)
):
    if not current_user.employee_profile:
        return []
    return db.query(CRWConnection).filter(
        CRWConnection.connector_id == current_user.employee_profile.id,
        CRWConnection.status == ConnectionStatus.PENDING
    ).all()

@router.put("/{conn_id}")
def update_invite_status(
    conn_id: int,
    accept: bool,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_user)
):
    conn = db.query(CRWConnection).filter(CRWConnection.id == conn_id).first()
    if not conn:
        raise HTTPException(status_code=404, detail="Not found")
        
    if not current_user.employee_profile or current_user.employee_profile.id != conn.connector_id:
        raise HTTPException(status_code=403, detail="Not authorized")
        
    conn.status = ConnectionStatus.ACCEPTED if accept else ConnectionStatus.REJECTED
    conn.responded_at = datetime.utcnow()
    db.commit()
    db.refresh(conn)
    
    # If accepted, we should theoretically check rewards here using a service
    
    return {"status": "success", "connection_id": conn.id}

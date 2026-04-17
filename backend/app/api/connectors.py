from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.models.hrm_models import Employee, AuthUser
from app.schemas.user import EmployeeOut
from app.api.auth import get_current_user

router = APIRouter()

@router.get("/search", response_model=List[EmployeeOut])
def search_connectors(
    department: str = Query(None),
    role: str = Query(None),
    name: str = Query(None),
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_user)
):
    query = db.query(Employee)
    
    # Do not show self in search
    if current_user.employee_profile:
        query = query.filter(Employee.id != current_user.employee_profile.id)
        
    if department:
        query = query.filter(Employee.department == department)
    if role:
        query = query.filter(Employee.role == role)
    if name:
        query = query.filter(Employee.full_name.ilike(f"%{name}%"))
        
    return query.limit(50).all()

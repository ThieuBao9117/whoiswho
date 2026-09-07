"""
Authentication API - WHO Is WHO

CSB uses JWT tokens from HRM (shared SECRET_KEY).
Two auth flows:
1. SSO Login: User comes from HRM with JWT token
2. Direct Login: (fallback for development) - uses SQLAlchemy ORM
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from datetime import timedelta
from typing import Optional

from app.core.database import get_db
from app.core.security import create_access_token, verify_password
from app.core.config import settings
from app.models.csb_employee_ref import CSBEmployeeRef
from app.schemas.user import Token, UserMe
from jose import JWTError, jwt
from app.services.game_logic import calculate_user_game_state

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")


def is_admin_user(user: CSBEmployeeRef) -> bool:
    """Return whether a synced WHO employee may access admin screens."""
    username = (user.username or "").strip().lower()
    department = (user.department or "").strip().casefold()
    role = (user.role or "").strip().casefold()
    status_value = (user.status or "").strip().casefold()

    # Keep the existing development/admin account behavior.
    if "admin" in username:
        return True

    return (
        bool(user.is_active)
        and status_value == "active"
        and role != "driver"
        and department in {"hr", "hr & ehs"}
    )


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """
    Validate JWT token and return CSB employee.
    Uses SQLAlchemy ORM
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    from sqlalchemy import func
    user = db.query(CSBEmployeeRef).filter(func.lower(CSBEmployeeRef.username) == func.lower(username)).first()
    if user is None:
        raise credentials_exception

    return user


@router.post("/sso-login", response_model=Token)
def sso_login(token: str, db: Session = Depends(get_db)):
    """
    SSO Login - User comes from HRM with JWT token.
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")

        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")

        from sqlalchemy import func
        user = db.query(CSBEmployeeRef).filter(
            (func.lower(CSBEmployeeRef.username) == func.lower(username)) | 
            (func.lower(CSBEmployeeRef.emp_code) == func.lower(username))
        ).first()
        if not user:
            raise HTTPException(status_code=404, detail=f"User '{username}' not found. Please sync from HRM.")
        if not user.is_active:
            raise HTTPException(status_code=403, detail="Account is inactive.")

        access_token = create_access_token(
            data={"sub": username, "emp_code": user.emp_code, "source": "sso"},
            expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        return {"access_token": access_token, "token_type": "bearer"}

    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")


@router.post("/login")
async def direct_login(request: Request, db: Session = Depends(get_db)):
    """
    Direct Login - Fallback for development.
    Accepts both JSON and form data:
      - JSON: {"username": "demo", "password": "any"}
      - Form: username=demo&password=any
    Uses SQLAlchemy ORM.
    """
    content_type = request.headers.get("content-type", "")
    username = ""
    password = ""

    if "application/json" in content_type:
        import json
        body = await request.body()
        try:
            data = json.loads(body)
            username = data.get("username", "").strip()
            password = data.get("password", "").strip()
        except:
            username = ""
    elif "application/x-www-form-urlencoded" in content_type or "multipart/form-data" in content_type:
        form = await request.form()
        username = form.get("username", "").strip()
        password = form.get("password", "").strip()
    else:
        # Try JSON first, fallback to form
        try:
            import json
            body = await request.body()
            data = json.loads(body)
            username = data.get("username", "").strip()
            password = data.get("password", "").strip()
        except:
            username = ""

    if not username:
        raise HTTPException(status_code=400, detail="Missing username")

    # Kiểm tra password - fixed password for all users
    FIXED_PASSWORD = "csb6301!"
    if password != FIXED_PASSWORD:
        raise HTTPException(status_code=401, detail="Incorrect password")

    from sqlalchemy import func
    user = db.query(CSBEmployeeRef).filter(
        (func.lower(CSBEmployeeRef.username) == func.lower(username)) | 
        (func.lower(CSBEmployeeRef.emp_code) == func.lower(username))
    ).first()

    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="User not found or inactive")

    access_token = create_access_token(
        data={"sub": user.username, "emp_code": user.emp_code, "source": "direct"},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    return {
        "access_token": access_token, 
        "token_type": "bearer", 
        "user": {
            "username": user.username, 
            "name": user.full_name, 
            "emp_code": user.emp_code
        }
    }


@router.get("/me")
def read_users_me(current_user: CSBEmployeeRef = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get current authenticated user profile - format for frontend"""
    game_state = calculate_user_game_state(db, current_user)
    
    return {
        "username": current_user.username,
        "is_staff": is_admin_user(current_user),
        "game_state": game_state,
        "employee_profile": {
            "id": str(current_user.id) if hasattr(current_user, 'id') else current_user.emp_code,
            "emp_code": current_user.emp_code,
            "full_name": current_user.full_name,
            "department": current_user.department,
            "part": current_user.part,
            "role": current_user.role,
            "status": current_user.status,
            "is_active": current_user.is_active,
            "join_date": current_user.join_date.isoformat() if current_user.join_date else None,
            "photo": current_user.photo,
        }
    }


@router.get("/users/list")
def list_users(db: Session = Depends(get_db)):
    """List all active users (for testing)"""
    users = db.query(CSBEmployeeRef).filter(CSBEmployeeRef.is_active == True).order_by(CSBEmployeeRef.full_name).all()
    return [
        {
            "id": str(user.id),
            "username": user.username, 
            "emp_code": user.emp_code, 
            "full_name": user.full_name, 
            "department": user.department, 
            "role": user.role
        }
        for user in users
    ]

"""
Sync API - Receive employee data from HRM System

Endpoints:
- POST /api/sync/employees       - Sync single employee
- POST /api/sync/employees/batch - Bulk sync (initial / scheduled)
- GET  /api/sync/status          - Check last sync status
- DELETE /api/sync/reset         - Xóa sạch bảng (cần header X-Confirm: reset)

Database: SQLite (dev) / PostgreSQL (prod)
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel
import uuid

from app.core.database import get_db
from app.models.csb_employee_ref import CSBEmployeeRef

router = APIRouter(prefix="/api/sync", tags=["sync"])


class EmployeeSyncPayload(BaseModel):
    """Payload từ HRM gửi sang"""
    hrm_employee_id: int
    hrm_user_id: Optional[int] = None
    emp_code: str
    username: str
    full_name: str
    email: Optional[str] = None
    entity: Optional[str] = None
    division: Optional[str] = None
    department: Optional[str] = None
    team: Optional[str] = None
    part: Optional[str] = None
    position: Optional[str] = None
    role: Optional[str] = None
    status: str = "Active"
    join_date: Optional[datetime] = None
    photo: Optional[str] = None


class SyncResponse(BaseModel):
    success: bool
    synced_count: int = 0
    created_count: int = 0
    updated_count: int = 0
    errors: List[str] = []
    last_sync_at: Optional[datetime] = None


@router.post("/employees", response_model=SyncResponse)
def sync_employee(
    payload: EmployeeSyncPayload,
    db: Session = Depends(get_db)
):
    """
    Sync một nhân viên từ HRM → CSB.
    
    HRM gọi endpoint này khi:
    - Nhân viên mới được tạo
    - Thông tin nhân viên thay đổi (dept, role, status)
    - Nhân viên nghỉ việc (status = 'Inactive')
    """
    try:
        # 1. Lookup logic: try hrm_employee_id first, then fallback to emp_code
        existing = db.query(CSBEmployeeRef).filter(
            CSBEmployeeRef.hrm_employee_id == payload.hrm_employee_id
        ).first()

        if not existing:
            existing = db.query(CSBEmployeeRef).filter(
                CSBEmployeeRef.emp_code == payload.emp_code
            ).first()

        if existing:
            # --- Conflict resolution ---
            # If we found a record, check if there are OTHER records that would conflict with our new data
            # (e.g. another row having the same emp_code that we are about to set)
            
            # Check for conflicting emp_code
            dupe_code = db.query(CSBEmployeeRef).filter(
                CSBEmployeeRef.emp_code == payload.emp_code,
                CSBEmployeeRef.id != existing.id
            ).first()
            if dupe_code:
                db.delete(dupe_code)
            
            # Check for conflicting username
            dupe_user = db.query(CSBEmployeeRef).filter(
                CSBEmployeeRef.username == payload.username,
                CSBEmployeeRef.id != existing.id
            ).first()
            if dupe_user:
                db.delete(dupe_user)
            
            # Flush to clear unique constraints before update
            db.flush()

            # UPDATE - Cập nhật thông tin từ HRM
            existing.hrm_employee_id = payload.hrm_employee_id
            existing.hrm_user_id = payload.hrm_user_id
            existing.emp_code = payload.emp_code
            existing.username = payload.username
            existing.full_name = payload.full_name
            existing.email = payload.email
            existing.entity = payload.entity
            existing.division = payload.division
            existing.department = payload.department
            existing.team = payload.team
            existing.part = payload.part
            existing.position = payload.position
            existing.role = payload.role
            existing.status = payload.status
            existing.join_date = payload.join_date
            existing.photo = payload.photo
            existing.last_synced_at = datetime.utcnow()
            existing.updated_at = datetime.utcnow()

            if payload.status == "Inactive":
                existing.is_active = False
            else:
                existing.is_active = True

            db.commit()
            db.refresh(existing)

            return SyncResponse(
                success=True,
                updated_count=1,
                last_sync_at=existing.last_synced_at
            )
        else:
            # CREATE - Nhân viên mới hoàn toàn
            # Vẫn cần kiểm tra xem emp_code/username có bị trùng ở đâu đó không (trường hợp hiếm)
            dupe = db.query(CSBEmployeeRef).filter(
                (CSBEmployeeRef.emp_code == payload.emp_code) | 
                (CSBEmployeeRef.username == payload.username)
            ).first()
            if dupe:
                # Nếu trùng, biến nó thành existing luôn
                existing = dupe
                
                # Clear other conflicts if any
                other_dupe = db.query(CSBEmployeeRef).filter(
                    (CSBEmployeeRef.emp_code == payload.emp_code) | 
                    (CSBEmployeeRef.username == payload.username),
                    CSBEmployeeRef.id != existing.id
                ).first()
                if other_dupe:
                    db.delete(other_dupe)
                
                db.flush()
                
                # Lặp lại logic update
                existing.hrm_employee_id = payload.hrm_employee_id
                existing.hrm_user_id = payload.hrm_user_id
                existing.emp_code = payload.emp_code
                existing.username = payload.username
                existing.full_name = payload.full_name
                existing.email = payload.email
                existing.entity = payload.entity
                existing.division = payload.division
                existing.department = payload.department
                existing.team = payload.team
                existing.part = payload.part
                existing.position = payload.position
                existing.role = payload.role
                existing.status = payload.status
                existing.join_date = payload.join_date
                existing.photo = payload.photo
                existing.last_synced_at = datetime.utcnow()
                existing.updated_at = datetime.utcnow()
                existing.is_active = (payload.status != "Inactive")
                
                db.commit()
                db.refresh(existing)
                return SyncResponse(success=True, updated_count=1, last_sync_at=existing.last_synced_at)

            new_employee = CSBEmployeeRef(
                hrm_employee_id=payload.hrm_employee_id,
                hrm_user_id=payload.hrm_user_id,
                emp_code=payload.emp_code,
                username=payload.username,
                full_name=payload.full_name,
                email=payload.email,
                entity=payload.entity,
                division=payload.division,
                department=payload.department,
                team=payload.team,
                part=payload.part,
                position=payload.position,
                role=payload.role,
                status=payload.status,
                join_date=payload.join_date,
                photo=payload.photo,
                last_synced_at=datetime.utcnow()
            )
            if payload.status == "Inactive":
                new_employee.is_active = False

            db.add(new_employee)
            db.commit()
            db.refresh(new_employee)

            return SyncResponse(
                success=True,
                created_count=1,
                last_sync_at=new_employee.last_synced_at
            )

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Sync failed: {str(e)}"
        )


@router.post("/employees/batch", response_model=SyncResponse)
def batch_sync_employees(
    payloads: List[EmployeeSyncPayload],
    db: Session = Depends(get_db)
):
    """
    Sync hàng loạt nhân viên từ HRM → CSB.

    Dùng cho:
    - Initial sync (lần đầu triển khai)
    - Scheduled sync (đồng bộ định kỳ)

    Strategy:
    - Tìm record theo hrm_employee_id TRƯỚC, fallback tìm theo emp_code
      để tránh INSERT trùng khi DB đã có dữ liệu cũ.
    - db.flush() từng record để bắt lỗi UNIQUE sớm; rollback savepoint
      cho record đó rồi tiếp tục các record còn lại.
    """
    created = 0
    updated = 0
    errors = []

    for payload in payloads:
        try:
            # --- Lookup: ưu tiên hrm_employee_id, fallback emp_code ---
            existing = None
            if payload.hrm_employee_id:
                existing = db.query(CSBEmployeeRef).filter(
                    CSBEmployeeRef.hrm_employee_id == payload.hrm_employee_id
                ).first()

            if existing is None:
                existing = db.query(CSBEmployeeRef).filter(
                    CSBEmployeeRef.emp_code == payload.emp_code
                ).first()

            if existing:
                # --- Xóa các bản ghi trùng emp_code / username (khác id) ---
                dupes_by_code = db.query(CSBEmployeeRef).filter(
                    CSBEmployeeRef.emp_code == payload.emp_code,
                    CSBEmployeeRef.id != existing.id
                ).all()
                for d in dupes_by_code:
                    db.delete(d)

                dupes_by_user = db.query(CSBEmployeeRef).filter(
                    CSBEmployeeRef.username == payload.username,
                    CSBEmployeeRef.id != existing.id
                ).all()
                for d in dupes_by_user:
                    db.delete(d)

                # UPDATE
                existing.hrm_employee_id = payload.hrm_employee_id
                existing.hrm_user_id     = payload.hrm_user_id
                existing.emp_code        = payload.emp_code
                existing.username        = payload.username
                existing.full_name       = payload.full_name
                existing.email           = payload.email
                existing.entity          = payload.entity
                existing.division        = payload.division
                existing.department      = payload.department
                existing.team            = payload.team
                existing.part            = payload.part
                existing.position        = payload.position
                existing.role            = payload.role
                existing.status          = payload.status
                existing.join_date       = payload.join_date
                existing.photo           = payload.photo
                existing.last_synced_at  = datetime.utcnow()
                existing.updated_at      = datetime.utcnow()
                existing.is_active       = (payload.status != "Inactive")
                updated += 1
            else:
                # Kiểm tra xem emp_code / username đã tồn tại chưa (trường hợp hrm_employee_id thay đổi)
                dupe = db.query(CSBEmployeeRef).filter(
                    CSBEmployeeRef.emp_code == payload.emp_code
                ).first()
                if dupe is None:
                    dupe = db.query(CSBEmployeeRef).filter(
                        CSBEmployeeRef.username == payload.username
                    ).first()

                if dupe:
                    # Cập nhật row đã có thay vì INSERT mới
                    dupe.hrm_employee_id = payload.hrm_employee_id
                    dupe.hrm_user_id     = payload.hrm_user_id
                    dupe.emp_code        = payload.emp_code
                    dupe.username        = payload.username
                    dupe.full_name       = payload.full_name
                    dupe.email           = payload.email
                    dupe.entity          = payload.entity
                    dupe.division        = payload.division
                    dupe.department      = payload.department
                    dupe.team            = payload.team
                    dupe.part            = payload.part
                    dupe.position        = payload.position
                    dupe.role            = payload.role
                    dupe.status          = payload.status
                    dupe.join_date       = payload.join_date
                    dupe.photo           = payload.photo
                    dupe.last_synced_at  = datetime.utcnow()
                    dupe.updated_at      = datetime.utcnow()
                    dupe.is_active       = (payload.status != "Inactive")
                    updated += 1
                else:
                    # CREATE mới hoàn toàn
                    new_employee = CSBEmployeeRef(
                        hrm_employee_id = payload.hrm_employee_id,
                        hrm_user_id     = payload.hrm_user_id,
                        emp_code        = payload.emp_code,
                        username        = payload.username,
                        full_name       = payload.full_name,
                        email           = payload.email,
                        entity          = payload.entity,
                        division        = payload.division,
                        department      = payload.department,
                        team            = payload.team,
                        part            = payload.part,
                        position        = payload.position,
                        role            = payload.role,
                        status          = payload.status,
                        join_date       = payload.join_date,
                        photo           = payload.photo,
                        last_synced_at  = datetime.utcnow()
                    )
                    db.add(new_employee)
                    created += 1

            # Flush từng record — bắt UNIQUE conflict trước khi commit
            try:
                db.flush()
            except Exception as flush_err:
                db.rollback()
                errors.append(f"SKIP emp_code={payload.emp_code}: {flush_err}")
                if existing:
                    updated -= 1
                else:
                    created -= 1
                continue

        except Exception as e:
            errors.append(
                f"ERROR hrm_id={payload.hrm_employee_id} "
                f"emp_code={payload.emp_code}: {e}"
            )

    # Commit tất cả bản ghi đã flush thành công
    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Batch commit failed: {str(e)}"
        )

    return SyncResponse(
        success=len(errors) == 0,
        synced_count=created + updated,
        created_count=created,
        updated_count=updated,
        errors=errors,
        last_sync_at=datetime.utcnow()
    )


@router.get("/status")
def get_sync_status(db: Session = Depends(get_db)):
    """Kiểm tra trạng thái sync mới nhất"""
    last_sync = db.query(CSBEmployeeRef).filter(
        CSBEmployeeRef.last_synced_at.isnot(None)
    ).order_by(CSBEmployeeRef.last_synced_at.desc()).first()

    total_employees = db.query(CSBEmployeeRef).count()
    active_employees = db.query(CSBEmployeeRef).filter(
        CSBEmployeeRef.is_active == True
    ).count()

    return {
        "total_employees_in_csb": total_employees,
        "active_employees": active_employees,
        "last_sync_at": last_sync.last_synced_at.isoformat() if last_sync else None,
        "database": "csb_db (SQLite dev / PostgreSQL prod)"
    }


@router.delete("/reset")
def reset_employee_refs(
    confirm: str = "",
    db: Session = Depends(get_db)
):
    """
    Xóa sạch toàn bộ bảng csb_employee_refs.

    Dùng khi DB có dữ liệu duplicate cần sync lại từ đầu.
    Yêu cầu query param: ?confirm=reset
    Ví dụ: DELETE /api/sync/reset?confirm=reset
    """
    if confirm != "reset":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Thieu xac nhan. Them query param: ?confirm=reset"
        )
    try:
        deleted = db.query(CSBEmployeeRef).delete(synchronize_session=False)
        db.commit()
        return {
            "success": True,
            "deleted_rows": deleted,
            "message": f"Da xoa {deleted} records. San sang sync lai tu HRM."
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Reset that bai: {str(e)}"
        )

"""
Admin API - Leaderboard, stats, reports

Uses SQLAlchemy ORM for SQLite/PostgreSQL compatibility.
"""
from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import func, case
from typing import List, Optional
from datetime import datetime
import subprocess
import os
import io
import openpyxl
from fastapi.responses import StreamingResponse
from openpyxl.styles import Font, Alignment, PatternFill
from app.models.crw_models import ConnectionStatus

from app.core.database import get_db
from app.models.csb_employee_ref import CSBEmployeeRef
from app.models.crw_models import CRWConnection
from app.services.game_logic import get_leaderboard_data, get_live_ranking_data, calculate_user_game_state

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

    # Determine if this is a final ranking or live ranking
    is_final = False
    if target_year < now.year:
        is_final = True
    elif target_year == now.year and target_month < now.month:
        is_final = True
    elif target_year == now.year and target_month == now.month and now.day >= 30:
        is_final = True

    if is_final:
        data = get_leaderboard_data(db, limit=limit, target_month=target_month, target_year=target_year)
    else:
        data = get_live_ranking_data(db, limit=limit, target_month=target_month, target_year=target_year)

    return {
        "month": target_month,
        "year": target_year,
        "is_final": is_final,
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


@router.post("/trigger-sync")
def trigger_sync():
    """Trigger background sync from HRM"""
    script_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "sync_from_hrm_full.py")
    python_exe = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "venv", "Scripts", "python.exe")
    
    try:
        subprocess.Popen([python_exe, script_path])
        return {"status": "success", "message": "Đang chạy tiến trình đồng bộ ngầm."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/report")
@router.get("/report/{period}")
def get_report(period: str = None, db: Session = Depends(get_db)):
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
            "department": (emp.part or emp.department) or "N/A",
            "role": emp.role or "N/A",
            "is_operator": state.get("is_operator", False),
            "count": f"{state['current_connections']}/{state['target_connections']}",
            "reward": 200000 if state['has_won'] else 0,
            "has_won": state['has_won'],
            "is_expired": state['is_expired'],
            "days_remaining": state['days_remaining'],
            "days_to_complete": state.get("days_to_complete"),
        })

    # Sort by count descending
    result.sort(key=lambda x: int(x["count"].split("/")[0]), reverse=True)
    return result


@router.get("/report/{emp_code}/history")
def get_employee_history(emp_code: str, db: Session = Depends(get_db)):
    """Get detailed connection history for a specific employee code"""
    emp = db.query(CSBEmployeeRef).filter(CSBEmployeeRef.emp_code == emp_code).first()
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")

    state = calculate_user_game_state(db, emp)

    # Get all connections involving this user
    connections = db.query(CRWConnection).filter(
        (CRWConnection.connector_id == emp.id) | (CRWConnection.new_hire_id == emp.id)
    ).order_by(CRWConnection.created_at.desc()).all()

    history = []
    for c in connections:
        # Determine the other person
        other_id = c.connector_id if c.new_hire_id == emp.id else c.new_hire_id
        other_emp = db.query(CSBEmployeeRef).filter(CSBEmployeeRef.id == other_id).first()
        
        # Determine direction
        direction = "sent" if c.new_hire_id == emp.id else "received"

        history.append({
            "connection_id": c.id,
            "direction": direction,
            "status": c.status.value if hasattr(c.status, 'value') else c.status,
            "created_at": c.created_at.isoformat() if c.created_at else None,
            "responded_at": c.responded_at.isoformat() if c.responded_at else None,
            "other_person": {
                "emp_code": other_emp.emp_code if other_emp else "Unknown",
                "full_name": other_emp.full_name if other_emp else "Unknown",
                "department": (other_emp.part or other_emp.department) if other_emp else "N/A",
                "photo": other_emp.photo if other_emp else None
            }
        })

    return {
        "employee": {
            "emp_code": emp.emp_code,
            "full_name": emp.full_name,
            "department": emp.part or emp.department,
            "role": emp.role,
        },
        "progress": {
            "current": state['current_connections'],
            "target": state['target_connections'],
            "has_won": state['has_won'],
            "is_expired": state['is_expired'],
            "days_remaining": state['days_remaining'],
            "join_date": state['join_date']
        },
        "history": history
    }




@router.get("/report/{period}/export")
def export_report_excel(period: str, db: Session = Depends(get_db)):
    """Export connection details for winners of a specific month"""
    try:
        year_str, month_str = period.split("-")
        target_year = int(year_str)
        target_month = int(month_str)
    except:
        raise HTTPException(status_code=400, detail="Invalid period format, expected YYYY-MM")

    winners = get_leaderboard_data(db, limit=1000, target_month=target_month, target_year=target_year)

    wb = openpyxl.Workbook()
    default_sheet = wb.active
    wb.remove(default_sheet)

    header_fill = PatternFill(start_color="4F81BD", end_color="4F81BD", fill_type="solid")
    header_font = Font(color="FFFFFF", bold=True)
    winner_fill = PatternFill(start_color="E2EFDA", end_color="E2EFDA", fill_type="solid")

    has_data = False

    def get_dept(emp):
        if not emp: return "N/A"
        return (emp.part or emp.department) or "N/A"

    from sqlalchemy import or_

    sheet_title = f"Tháng {target_month}-{target_year}"
    ws = wb.create_sheet(title=sheet_title)
    ws.append([f"DANH SÁCH CHIẾN THẮNG THÁNG {target_month}/{target_year}"])
    ws.append([])

    for winner in winners:
        has_data = True
        emp_id = winner["id"]
        emp = db.query(CSBEmployeeRef).filter(CSBEmployeeRef.id == emp_id).first()
        if not emp: continue

        ws.append([
            f"Người thắng: {winner['name']} ({winner['emp_code']})", 
            f"Phòng ban: {winner['dept']}", 
            f"Tổng số lượng kết nối: {winner['raw_count']} người",
            f"Thời gian hoàn thành KPI: {winner['score']}"
        ])
        for cell in ws._cells.values():
            if cell.row == ws.max_row:
                cell.fill = winner_fill
                cell.font = Font(bold=True)

        ws.append(["STT", "Người được kết nối", "Mã NV", "Phòng ban / Tổ", "Chức vụ", "Thời gian kết nối thành công"])
        for cell in ws._cells.values():
            if cell.row == ws.max_row:
                cell.fill = header_fill
                cell.font = header_font
                cell.alignment = Alignment(horizontal="center")

        conns = db.query(CRWConnection).filter(
            or_(CRWConnection.connector_id == emp_id, CRWConnection.new_hire_id == emp_id),
            CRWConnection.status == ConnectionStatus.ACCEPTED
        ).all()
        conns.sort(key=lambda x: x.responded_at or x.created_at)

        for idx, conn in enumerate(conns, 1):
            if conn.connector_id == emp_id:
                target = conn.new_hire
            else:
                target = conn.connector
                
            t_name = target.full_name if target else "Unknown"
            t_code = target.emp_code if target else "Unknown"
            t_dept = get_dept(target)
            t_role = target.role if target else "N/A"
            c_time = (conn.responded_at or conn.created_at)
            c_time_str = c_time.strftime("%Y-%m-%d %H:%M:%S") if c_time else "N/A"
            
            ws.append([idx, t_name, t_code, t_dept, t_role, c_time_str])

        ws.append([])
        ws.append([])

    for col in ws.columns:
        max_length = 0
        column = col[0].column_letter
        for cell in col:
            try:
                if len(str(cell.value)) > max_length:
                    max_length = len(cell.value)
            except:
                pass
        ws.column_dimensions[column].width = min(max_length + 2, 50)

    if not has_data:
        ws.append([f"Chưa có người chiến thắng nào trong tháng {target_month}/{target_year}."])

    # Save to BytesIO
    output = io.BytesIO()
    wb.save(output)
    output.seek(0)
    
    headers = {
        'Content-Disposition': f'attachment; filename="Chi_Tiet_Nguoi_Thang_Cuoc_{period}.xlsx"',
        'Access-Control-Expose-Headers': 'Content-Disposition'
    }
    
    return StreamingResponse(output, headers=headers, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

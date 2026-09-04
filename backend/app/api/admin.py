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
            "is_expired": state['is_expired'],
            "days_remaining": state['days_remaining'],
            "join_date": state['join_date']
        },
        "history": history
    }


@router.get("/report/{period}/export")
def export_report_excel(period: str, db: Session = Depends(get_db)):
    """Export connection details for winners of a specific month - 3-sheet beautiful report"""
    try:
        year_str, month_str = period.split("-")
        target_year = int(year_str)
        target_month = int(month_str)
    except:
        raise HTTPException(status_code=400, detail="Invalid period format, expected YYYY-MM")

    from sqlalchemy import or_
    from openpyxl.utils import get_column_letter
    from openpyxl.styles import Border, Side
    from datetime import timezone, timedelta
    from app.services.game_logic import PROGRAM_START_DATE
    from collections import defaultdict

    # ── Color palette ──
    C_HEADER_BG = "1E3A5F"
    C_TITLE_BG  = "2563EB"
    C_ROW_ALT   = "F0F4FF"
    C_KPI_OK    = "D1FAE5"
    C_KPI_FAIL  = "FEE2E2"
    C_RANK1     = "FFD700"
    C_RANK2     = "E2E8F0"
    C_RANK3     = "FED7AA"
    C_BORDER    = "CBD5E1"

    def mfill(hex_c):
        return PatternFill(start_color=hex_c, end_color=hex_c, fill_type="solid")

    def tb():
        s = Side(style='thin', color=C_BORDER)
        return Border(left=s, right=s, top=s, bottom=s)

    def sc(cell, fill=None, font=None, align=None, border=None):
        if fill:   cell.fill = fill
        if font:   cell.font = font
        if align:  cell.alignment = align
        if border: cell.border = border

    now = datetime.utcnow().replace(tzinfo=timezone.utc)
    target_start = datetime(target_year, target_month, 1, tzinfo=timezone.utc)
    next_m = target_month + 1 if target_month < 12 else 1
    next_y = target_year if target_month < 12 else target_year + 1
    target_end = datetime(next_y, next_m, 1, tzinfo=timezone.utc)

    all_accepted = db.query(CRWConnection).filter(
        CRWConnection.status == ConnectionStatus.ACCEPTED,
        CRWConnection.responded_at < target_end
    ).order_by(CRWConnection.responded_at.asc()).all()

    conns_by_emp = defaultdict(list)
    for c in all_accepted:
        conns_by_emp[c.connector_id].append(c)
        conns_by_emp[c.new_hire_id].append(c)

    all_emps = db.query(CSBEmployeeRef).filter(CSBEmployeeRef.is_active == True).all()

    def get_role_info(emp):
        role = (emp.role or "").lower()
        username = (emp.username or "").upper()
        # Driver (lái xe) chỉ cần 10 kết nối trong 30 ngày, giống Operator
        if username.startswith("DRV_") or "driver" in role:
            return 10, 30, "Driver"
        if "operator" in role or "công nhân" in role or "cong nhan" in role:
            return 10, 30, "Operator"
        if "team leader" in role or "trưởng ca" in role:
            return 20, 60, "Team Leader"
        return 30, 60, "Staff/Officer"

    all_kpi = []
    month_winners = []

    for emp in all_emps:
        j = emp.join_date
        if not j: continue
        if j.tzinfo is None: j = j.replace(tzinfo=timezone.utc)
        if j < PROGRAM_START_DATE: continue

        target_count, duration, role_label = get_role_info(emp)
        deadline = j + timedelta(days=duration)
        is_expired = now > deadline

        conns = conns_by_emp.get(emp.id, [])
        valid = []
        for c in conns:
            ct = c.responded_at or c.created_at
            if ct is None: continue
            if ct.tzinfo is None: ct = ct.replace(tzinfo=timezone.utc)
            if ct <= deadline:
                valid.append((c, ct))
        valid.sort(key=lambda x: x[1])

        current_count = len(valid)
        has_won = current_count >= target_count
        win_time = None
        won_in_month = False
        days_done = None

        if has_won:
            _, win_time = valid[target_count - 1]
            if win_time.tzinfo is None: win_time = win_time.replace(tzinfo=timezone.utc)
            days_done = int((win_time - j).total_seconds() // 86400)
            if target_start <= win_time < target_end:
                won_in_month = True

        dept = emp.part or emp.department or "N/A"
        rec = {
            "emp": emp, "dept": dept, "role_label": role_label,
            "target_count": target_count, "duration": duration,
            "join_date": j, "deadline": deadline,
            "current_count": current_count, "has_won": has_won,
            "won_in_month": won_in_month, "win_time": win_time,
            "days_done": days_done, "is_expired": is_expired,
            "valid_conns": valid, "rank": 0,
        }
        all_kpi.append(rec)
        if won_in_month:
            month_winners.append(rec)

    month_winners.sort(key=lambda x: x["days_done"])
    for i, w in enumerate(month_winners):
        w["rank"] = i + 1

    sorted_all = sorted(all_kpi, key=lambda x: (
        0 if x["won_in_month"] else (1 if not x["is_expired"] and not x["has_won"] else 2),
        x["rank"] if x["rank"] > 0 else 999,
        -x["current_count"]
    ))

    wb = openpyxl.Workbook()
    default_sheet = wb.active
    wb.remove(default_sheet)

    # ══════════════════════════════════════════════════════
    # SHEET 1: TỔNG HỢP
    # ══════════════════════════════════════════════════════
    ws1 = wb.create_sheet(title=f"Tong hop T{target_month}-{target_year}")
    ws1.freeze_panes = "A5"

    ws1.merge_cells("A1:M1")
    c = ws1["A1"]
    c.value = f"BÁO CÁO KPI KẾT NỐI WHO IS WHO — THÁNG {target_month}/{target_year}"
    sc(c, mfill(C_TITLE_BG), Font(name="Calibri", size=15, bold=True, color="FFFFFF"),
       Alignment(horizontal="center", vertical="center"))
    ws1.row_dimensions[1].height = 34

    ws1.merge_cells("A2:M2")
    ws1["A2"].value = f"Xuất ngày: {datetime.now().strftime('%d/%m/%Y %H:%M')}   |   Người đạt KPI: {len(month_winners)}   |   Tổng thưởng: {len(month_winners)*200000:,} VNĐ"
    sc(ws1["A2"], mfill("DBEAFE"), Font(name="Calibri", size=10, italic=True, color="1E40AF"),
       Alignment(horizontal="center", vertical="center"))
    ws1.row_dimensions[2].height = 18

    ws1.merge_cells("A3:M3")
    ws1.row_dimensions[3].height = 6

    HDRS1 = ["#","Xếp hạng","Mã NV","Họ và tên","Bộ phận / Tổ","Chức vụ","Ngày vào","Deadline","KPI cần","Đã đạt","Ngày HT","Số ngày","Thưởng (VNĐ)"]
    WDTHS1 = [4, 10, 12, 22, 20, 14, 12, 12, 9, 8, 14, 9, 14]
    for ci, (h, w) in enumerate(zip(HDRS1, WDTHS1), 1):
        cell = ws1.cell(row=4, column=ci, value=h)
        sc(cell, mfill(C_HEADER_BG),
           Font(name="Calibri", size=9, bold=True, color="FFFFFF"),
           Alignment(horizontal="center", vertical="center", wrap_text=True), tb())
        ws1.column_dimensions[get_column_letter(ci)].width = w
    ws1.row_dimensions[4].height = 28

    for stt, emp_r in enumerate(sorted_all, 1):
        rn = stt + 4
        rank = emp_r["rank"]
        emp = emp_r["emp"]
        if emp_r["won_in_month"]:
            bg = C_RANK1 if rank==1 else (C_RANK2 if rank==2 else (C_RANK3 if rank==3 else C_KPI_OK))
            status_text = f"✅ ĐẠT KPI (#{rank})"; reward = 200000
        elif emp_r["has_won"]:
            bg = "E0F2FE"; status_text = "✅ Đạt (tháng khác)"; reward = 0
        elif emp_r["is_expired"]:
            bg = C_KPI_FAIL; status_text = "❌ Hết hạn"; reward = 0
        else:
            bg = C_ROW_ALT if rn%2==0 else "FFFFFF"
            days_l = max(0,(emp_r["deadline"]-now).days)
            status_text = f"⏳ {days_l} ngày còn"; reward = 0

        vals1 = [
            stt,
            f"#{rank}" if emp_r["won_in_month"] else "-",
            emp.emp_code, emp.full_name, emp_r["dept"], emp_r["role_label"],
            emp_r["join_date"].strftime("%d/%m/%Y"),
            emp_r["deadline"].strftime("%d/%m/%Y"),
            emp_r["target_count"], emp_r["current_count"],
            emp_r["win_time"].strftime("%d/%m/%Y") if emp_r["win_time"] else "-",
            emp_r["days_done"] if emp_r["days_done"] is not None else "-",
            reward
        ]
        fill1 = mfill(bg)
        for ci, val in enumerate(vals1, 1):
            cell = ws1.cell(row=rn, column=ci, value=val)
            sc(cell, fill1,
               Font(name="Calibri", size=9, bold=(ci in (4,10)),
                    color="065F46" if emp_r["won_in_month"] else "1E293B"),
               Alignment(horizontal="center" if ci in (1,2,7,8,9,10,11,12,13) else "left",
                         vertical="center"), tb())
        ws1.cell(row=rn, column=13).number_format = '#,##0'
        ws1.row_dimensions[rn].height = 18

    last_r = len(sorted_all) + 5
    ws1.merge_cells(f"A{last_r}:L{last_r}")
    ws1[f"A{last_r}"].value = f"TỔNG CỘNG: {len(month_winners)} người đạt KPI tháng {target_month}/{target_year}"
    sc(ws1[f"A{last_r}"], mfill(C_TITLE_BG),
       Font(name="Calibri", size=10, bold=True, color="FFFFFF"),
       Alignment(horizontal="center", vertical="center"), tb())
    tc = ws1.cell(row=last_r, column=13, value=len(month_winners)*200000)
    tc.number_format = '#,##0'
    sc(tc, mfill(C_TITLE_BG),
       Font(name="Calibri", size=10, bold=True, color="FFD700"),
       Alignment(horizontal="center", vertical="center"), tb())
    ws1.row_dimensions[last_r].height = 22

    # ══════════════════════════════════════════════════════
    # SHEET 2: CHI TIẾT KẾT NỐI TỪNG NGƯỜI ĐẠT KPI
    # ══════════════════════════════════════════════════════
    ws2 = wb.create_sheet(title=f"Chi tiet T{target_month}-{target_year}")
    ws2.freeze_panes = "A3"

    ws2.merge_cells("A1:I1")
    ws2["A1"].value = f"CHI TIẾT KẾT NỐI — NGƯỜI ĐẠT KPI THÁNG {target_month}/{target_year}"
    sc(ws2["A1"], mfill("1D4ED8"),
       Font(name="Calibri", size=14, bold=True, color="FFFFFF"),
       Alignment(horizontal="center", vertical="center"))
    ws2.row_dimensions[1].height = 32

    DET_WIDTHS2 = [5,6,25,12,22,18,12,22,20]
    for ci, w in enumerate(DET_WIDTHS2, 1):
        ws2.column_dimensions[get_column_letter(ci)].width = w

    det_row = 3
    for winner in month_winners:
        rank = winner["rank"]
        medal = "🥇" if rank==1 else ("🥈" if rank==2 else ("🥉" if rank==3 else f"#{rank}"))
        emp = winner["emp"]

        ws2.merge_cells(f"A{det_row}:I{det_row}")
        c = ws2[f"A{det_row}"]
        c.value = f"{medal}  {emp.full_name} ({emp.emp_code}) — Xếp hạng #{rank}"
        rank_bg = C_RANK1 if rank==1 else (C_RANK2 if rank==2 else (C_RANK3 if rank==3 else "D1FAE5"))
        sc(c, mfill(rank_bg),
           Font(name="Calibri", size=12, bold=True, color="1E3A8A"),
           Alignment(horizontal="left", vertical="center", indent=1))
        ws2.row_dimensions[det_row].height = 26
        det_row += 1

        for cells_range, val in [
            (f"A{det_row}:C{det_row}", f"📂 {winner['dept']}   |   👤 {winner['role_label']}"),
            (f"D{det_row}:F{det_row}", f"📅 Ngày vào: {winner['join_date'].strftime('%d/%m/%Y')}   Deadline: {winner['deadline'].strftime('%d/%m/%Y')}"),
            (f"G{det_row}:I{det_row}", f"🏆 HT: {winner['win_time'].strftime('%d/%m/%Y')} ({winner['days_done']} ngày)   Thưởng: 200,000 VNĐ"),
        ]:
            ws2.merge_cells(cells_range)
            start_cell = cells_range.split(":")[0]
            ws2[start_cell].value = val
            sc(ws2[start_cell], mfill("EFF6FF"),
               Font(name="Calibri", size=9, color="1E3A8A"),
               Alignment(horizontal="left", vertical="center", indent=1))
        ws2.row_dimensions[det_row].height = 18
        det_row += 1

        ws2.merge_cells(f"A{det_row}:I{det_row}")
        ws2[f"A{det_row}"].value = f"   KPI mục tiêu: {winner['target_count']} kết nối trong {winner['duration']} ngày   ✅ Đã đạt: {winner['current_count']} kết nối"
        sc(ws2[f"A{det_row}"], mfill("DCFCE7"),
           Font(name="Calibri", size=9, bold=True, color="065F46"),
           Alignment(horizontal="left", vertical="center", indent=1))
        ws2.row_dimensions[det_row].height = 16
        det_row += 1

        HDRS2 = ["STT","Chiều","Mã NV","Họ và tên","Bộ phận / Tổ","Chức vụ","Ngày kết nối","Trong KPI?","Ghi chú"]
        for ci, h in enumerate(HDRS2, 1):
            cell = ws2.cell(row=det_row, column=ci, value=h)
            sc(cell, mfill(C_HEADER_BG),
               Font(name="Calibri", size=8, bold=True, color="FFFFFF"),
               Alignment(horizontal="center", vertical="center"), tb())
        ws2.row_dimensions[det_row].height = 20
        det_row += 1

        for stt, (conn_obj, ct) in enumerate(winner["valid_conns"], 1):
            is_connector = (conn_obj.connector_id == emp.id)
            if is_connector:
                other = db.query(CSBEmployeeRef).filter(CSBEmployeeRef.id == conn_obj.new_hire_id).first()
                direction = "← Nhận"
            else:
                other = db.query(CSBEmployeeRef).filter(CSBEmployeeRef.id == conn_obj.connector_id).first()
                direction = "→ Gửi"

            o_name = other.full_name if other else "Unknown"
            o_code = other.emp_code if other else "N/A"
            o_dept = (other.part or other.department or "N/A") if other else "N/A"
            o_role = (other.role or "N/A") if other else "N/A"

            in_kpi = stt <= winner["target_count"]
            is_win = stt == winner["target_count"]
            date_str = ct.strftime("%d/%m/%Y %H:%M") if ct else "N/A"
            kpi_mark = f"✅ #{stt}" if in_kpi else "➕"
            note = f"⭐ KẾT NỐI THỨ {stt} — HOÀN THÀNH KPI!" if is_win else ("Tính vào KPI" if in_kpi else "Thêm ngoài KPI")

            row_bg = "FEFCE8" if is_win else ("ECFDF5" if in_kpi else "F8FAFC")
            vals2 = [stt, direction, o_code, o_name, o_dept, o_role, date_str, kpi_mark, note]
            for ci, val in enumerate(vals2, 1):
                cell = ws2.cell(row=det_row, column=ci, value=val)
                sc(cell, mfill(row_bg),
                   Font(name="Calibri", size=8, bold=is_win,
                        color="92400E" if is_win else "1E293B"),
                   Alignment(horizontal="center" if ci in (1,2,7,8) else "left", vertical="center"),
                   tb())
            ws2.row_dimensions[det_row].height = 15
            det_row += 1

        det_row += 2  # spacer between people

    if not month_winners:
        ws2.merge_cells("A3:I3")
        ws2["A3"].value = f"Chưa có người đạt KPI trong tháng {target_month}/{target_year}."
        ws2["A3"].font = Font(name="Calibri", size=11, italic=True, color="6B7280")
        ws2["A3"].alignment = Alignment(horizontal="center", vertical="center")

    # ══════════════════════════════════════════════════════
    # SHEET 3: CHI TIÊU TẤT CẢ NHÂN VIÊN
    # ══════════════════════════════════════════════════════
    ws3 = wb.create_sheet(title=f"Chi tieu T{target_month}-{target_year}")
    ws3.freeze_panes = "A3"

    ws3.merge_cells("A1:M1")
    ws3["A1"].value = f"CHI TIÊU KẾT NỐI — TẤT CẢ NHÂN VIÊN THÁNG {target_month}/{target_year}"
    sc(ws3["A1"], mfill("7C3AED"),
       Font(name="Calibri", size=13, bold=True, color="FFFFFF"),
       Alignment(horizontal="center", vertical="center"))
    ws3.row_dimensions[1].height = 30

    HDRS3 = ["STT","Mã NV","Họ và tên","Bộ phận","Chức vụ","KPI cần","Đã đạt","Ngày vào","Deadline","Ngày HT","Số ngày","Trạng thái","Thưởng"]
    W3 = [4,12,22,18,14,9,8,12,12,12,8,18,12]
    for ci,(h,w) in enumerate(zip(HDRS3,W3),1):
        cell = ws3.cell(row=2, column=ci, value=h)
        sc(cell, mfill("4C1D95"),
           Font(name="Calibri", size=9, bold=True, color="FFFFFF"),
           Alignment(horizontal="center", vertical="center"), tb())
        ws3.column_dimensions[get_column_letter(ci)].width = w
    ws3.row_dimensions[2].height = 22

    for stt, emp_r in enumerate(sorted_all, 1):
        rn = stt + 2
        rank = emp_r["rank"]
        emp = emp_r["emp"]
        if emp_r["won_in_month"]:
            bg = "D1FAE5"; status = f"✅ ĐẠT (#{rank})"; reward = 200000
        elif emp_r["has_won"]:
            bg = "E0F2FE"; status = "✅ Đạt (tháng khác)"; reward = 0
        elif emp_r["is_expired"]:
            bg = "FEE2E2"; status = "❌ Hết hạn"; reward = 0
        else:
            days_l = max(0,(emp_r["deadline"]-now).days)
            bg = "FFFBEB" if rn%2==0 else "FFFFFF"
            status = f"⏳ {days_l} ngày còn"; reward = 0

        vals3 = [
            stt, emp.emp_code, emp.full_name, emp_r["dept"], emp_r["role_label"],
            emp_r["target_count"], emp_r["current_count"],
            emp_r["join_date"].strftime("%d/%m/%Y"),
            emp_r["deadline"].strftime("%d/%m/%Y"),
            emp_r["win_time"].strftime("%d/%m/%Y") if emp_r["win_time"] else "-",
            emp_r["days_done"] if emp_r["days_done"] is not None else "-",
            status, reward
        ]
        fill3 = mfill(bg)
        for ci, val in enumerate(vals3, 1):
            cell = ws3.cell(row=rn, column=ci, value=val)
            sc(cell, fill3,
               Font(name="Calibri", size=9, bold=(ci==3),
                    color="065F46" if emp_r["won_in_month"] else "1E293B"),
               Alignment(horizontal="center" if ci in (1,6,7,8,9,10,11,13) else "left",
                         vertical="center"), tb())
        ws3.cell(row=rn, column=13).number_format = '#,##0'
        ws3.row_dimensions[rn].height = 16

    output = io.BytesIO()
    wb.save(output)
    output.seek(0)

    headers = {
        'Content-Disposition': f'attachment; filename="Bao_cao_KPI_T{target_month}_{target_year}.xlsx"',
        'Access-Control-Expose-Headers': 'Content-Disposition'
    }

    return StreamingResponse(output, headers=headers,
                             media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")


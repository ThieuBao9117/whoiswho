# -*- coding: utf-8 -*-
"""
Xuat bao cao KPI thang 7/2026 - format dep, 2 sheet:
  Sheet 1: TONG HOP - danh sach tat ca nguoi dat KPI
  Sheet 2: CHI TIET - ket noi tung nguoi dat KPI
"""
import os, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
load_dotenv()

import openpyxl
from openpyxl.styles import (
    Font, Alignment, PatternFill, Border, Side, GradientFill
)
from openpyxl.utils import get_column_letter
from openpyxl.drawing.image import Image as XLImage
from sqlalchemy import create_engine, or_, text
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timezone, timedelta
from collections import defaultdict

DATABASE_URL = os.getenv("CSB_DATABASE_URL", "")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()

MONTH = 7
YEAR = 2026
PROGRAM_START = datetime(2026, 4, 1, tzinfo=timezone.utc)

# ─── Color Palette ───────────────────────────────────────────────
C_HEADER_BG   = "1E3A5F"   # dark navy
C_HEADER_FG   = "FFFFFF"
C_TITLE_BG    = "2563EB"   # blue
C_TITLE_FG    = "FFFFFF"
C_WINNER_BG   = "FFF3CD"   # light yellow
C_WINNER_BOLD = "92400E"
C_ROW_ALT     = "F0F4FF"   # light blue alt
C_KPI_OK      = "D1FAE5"   # green
C_KPI_FAIL    = "FEE2E2"   # red
C_BORDER      = "CBD5E1"
C_RANK1       = "FFD700"   # gold
C_RANK2       = "E2E8F0"   # silver
C_RANK3       = "FED7AA"   # bronze
C_DETAIL_HDR  = "1D4ED8"   # blue header for detail sheet
C_PERSON_BG   = "EFF6FF"   # light blue for person header

def thin_border():
    s = Side(style='thin', color=C_BORDER)
    return Border(left=s, right=s, top=s, bottom=s)

def make_fill(hex_color):
    return PatternFill(start_color=hex_color, end_color=hex_color, fill_type="solid")

def hdr_font(size=11, bold=True, color=C_HEADER_FG, italic=False):
    return Font(name="Calibri", size=size, bold=bold, color=color, italic=italic)

def style_cell(cell, fill=None, font=None, align=None, border=None):
    if fill:  cell.fill  = fill
    if font:  cell.font  = font
    if align: cell.alignment = align
    if border:cell.border = border

def auto_col_width(ws, min_w=8, max_w=50):
    for col in ws.columns:
        max_len = 0
        col_letter = get_column_letter(col[0].column_index if hasattr(col[0],'column_index') else col[0].column)
        for cell in col:
            try:
                v = str(cell.value or "")
                max_len = max(max_len, len(v))
            except: pass
        ws.column_dimensions[col_letter].width = min(max(max_len + 2, min_w), max_w)

# ─── Load data ───────────────────────────────────────────────────
print("Loading data from DB...")

# All accepted connections up to end of month
target_start = datetime(YEAR, MONTH, 1, tzinfo=timezone.utc)
target_end   = datetime(YEAR, MONTH+1, 1, tzinfo=timezone.utc)

conn_rows = db.execute(text("""
    SELECT c.id, c.connector_id, c.new_hire_id, c.status, c.created_at, c.responded_at,
           nh.full_name as nh_name, nh.emp_code as nh_code,
           nh.department as nh_dept, nh.part as nh_part, nh.role as nh_role,
           cn.full_name as cn_name, cn.emp_code as cn_code,
           cn.department as cn_dept, cn.part as cn_part, cn.role as cn_role
    FROM crw_connections c
    LEFT JOIN csb_employee_refs nh ON nh.id = c.new_hire_id
    LEFT JOIN csb_employee_refs cn ON cn.id = c.connector_id
    WHERE c.status = 'ACCEPTED'
      AND c.responded_at < :tend
    ORDER BY c.responded_at ASC
"""), {"tend": target_end}).fetchall()

emp_rows = db.execute(text("""
    SELECT id, emp_code, full_name, role, join_date, department, part, is_active
    FROM csb_employee_refs WHERE is_active = true
""")).fetchall()

emp_by_id = {str(r.id): r for r in emp_rows}

# Group connections per employee
conns_by_emp = defaultdict(list)
for c in conn_rows:
    conns_by_emp[str(c.connector_id)].append(c)
    conns_by_emp[str(c.new_hire_id)].append(c)

# Evaluate KPI for each employee
def get_role_info(role_str):
    role = (role_str or "").lower()
    is_op = "operator" in role or "công nhân" in role or "cong nhan" in role
    is_tl = "team leader" in role or "trưởng ca" in role or "truong ca" in role
    if is_op:
        return 10, 30, "Operator"
    elif is_tl:
        return 20, 60, "Team Leader"
    else:
        return 30, 60, "Staff/Officer"

now = datetime(2026, 7, 29, 10, 20, 0, tzinfo=timezone.utc)
winners = []
all_employees_kpi = []

for emp in emp_rows:
    eid = str(emp.id)
    join_date = emp.join_date
    if not join_date:
        continue
    if hasattr(join_date, 'tzinfo') and join_date.tzinfo is None:
        join_date = join_date.replace(tzinfo=timezone.utc)
    if join_date < PROGRAM_START:
        continue

    target_count, duration, role_label = get_role_info(emp.role)
    deadline = join_date + timedelta(days=duration)
    is_expired = now > deadline

    conns = conns_by_emp.get(eid, [])
    # Only connections before deadline
    valid_conns = []
    for c in conns:
        ct = c.responded_at or c.created_at
        if ct and hasattr(ct, 'tzinfo') and ct.tzinfo is None:
            ct = ct.replace(tzinfo=timezone.utc)
        if ct and ct <= deadline:
            valid_conns.append((c, ct))
    valid_conns.sort(key=lambda x: x[1])

    current_count = len(valid_conns)
    has_won = current_count >= target_count

    win_time = None
    won_in_month = False
    days_to_complete = None

    if has_won:
        _, win_time = valid_conns[target_count - 1]
        days_to_complete = int((win_time - join_date).total_seconds() // 86400)
        if target_start <= win_time < target_end:
            won_in_month = True

    dept = emp.part or emp.department or "N/A"
    all_employees_kpi.append({
        "id": eid,
        "emp_code": emp.emp_code,
        "full_name": emp.full_name,
        "dept": dept,
        "role": emp.role or "N/A",
        "role_label": role_label,
        "join_date": join_date,
        "deadline": deadline,
        "target_count": target_count,
        "current_count": current_count,
        "has_won": has_won,
        "won_in_month": won_in_month,
        "win_time": win_time,
        "days_to_complete": days_to_complete,
        "is_expired": is_expired,
        "valid_conns": valid_conns,
    })
    if won_in_month:
        winners.append(all_employees_kpi[-1])

winners.sort(key=lambda x: x["days_to_complete"])
for i, w in enumerate(winners):
    w["rank"] = i + 1

print(f"Found {len(winners)} winner(s) in {MONTH}/{YEAR}")

# ─── Build Workbook ───────────────────────────────────────────────
wb = openpyxl.Workbook()

# ══════════════════════════════════════════════════════════════════
# SHEET 1: TỔNG HỢP KPI
# ══════════════════════════════════════════════════════════════════
ws1 = wb.active
ws1.title = f"Tong hop T{MONTH}-{YEAR}"

# Freeze panes
ws1.freeze_panes = "A5"

# ── Row 1: Big Title ──
ws1.merge_cells("A1:J1")
c = ws1["A1"]
c.value = f"BÁO CÁO KPI KẾT NỐI WHO IS WHO — THÁNG {MONTH}/{YEAR}"
style_cell(c,
    fill=make_fill(C_TITLE_BG),
    font=Font(name="Calibri", size=16, bold=True, color=C_TITLE_FG),
    align=Alignment(horizontal="center", vertical="center")
)
ws1.row_dimensions[1].height = 36

# ── Row 2: Sub info ──
ws1.merge_cells("A2:J2")
c = ws1["A2"]
c.value = f"Xuất ngày: {now.strftime('%d/%m/%Y %H:%M')}   |   Chương trình từ: 01/04/2026"
style_cell(c,
    fill=make_fill("DBEAFE"),
    font=Font(name="Calibri", size=10, italic=True, color="1E40AF"),
    align=Alignment(horizontal="center", vertical="center")
)
ws1.row_dimensions[2].height = 20

# ── Row 3: Summary stats ──
ws1.merge_cells("A3:B3")
ws1["A3"].value = f"Tổng người đạt KPI: {len(winners)}"
ws1["A3"].font = Font(name="Calibri", size=11, bold=True, color="065F46")
ws1["A3"].fill = make_fill("D1FAE5")
ws1["A3"].alignment = Alignment(horizontal="center", vertical="center")

ws1.merge_cells("C3:D3")
ws1["C3"].value = f"Tổng tham gia: {len(all_employees_kpi)}"
ws1["C3"].font = Font(name="Calibri", size=11, bold=True, color="1E3A8A")
ws1["C3"].fill = make_fill("DBEAFE")
ws1["C3"].alignment = Alignment(horizontal="center", vertical="center")

ws1.merge_cells("E3:F3")
ws1["E3"].value = f"Tổng thưởng: {len(winners) * 200000:,} VNĐ"
ws1["E3"].font = Font(name="Calibri", size=11, bold=True, color="92400E")
ws1["E3"].fill = make_fill("FEF3C7")
ws1["E3"].alignment = Alignment(horizontal="center", vertical="center")

ws1.row_dimensions[3].height = 26

# ── Row 4: Table Headers ──
HEADERS = ["#", "Xếp hạng", "Mã NV", "Họ và tên", "Bộ phận / Tổ", "Chức vụ", 
           "Ngày vào", "KPI (kết nối)", "Đã đạt", "Ngày hoàn thành", "Số ngày HT", "Thưởng (VNĐ)", "Trạng thái"]
COL_WIDTHS = [4, 10, 12, 22, 20, 16, 13, 13, 8, 18, 10, 14, 12]

for col_idx, (h, w) in enumerate(zip(HEADERS, COL_WIDTHS), 1):
    cell = ws1.cell(row=4, column=col_idx, value=h)
    style_cell(cell,
        fill=make_fill(C_HEADER_BG),
        font=Font(name="Calibri", size=10, bold=True, color=C_HEADER_FG),
        align=Alignment(horizontal="center", vertical="center", wrap_text=True),
        border=thin_border()
    )
    ws1.column_dimensions[get_column_letter(col_idx)].width = w
ws1.row_dimensions[4].height = 32

# ── Data rows ──
# All employees sorted: winners first (by rank), then in-progress, then expired
sorted_all = sorted(all_employees_kpi, key=lambda x: (
    0 if x["won_in_month"] else (1 if not x["is_expired"] and not x["has_won"] else 2),
    x.get("rank", 999),
    -x["current_count"]
))

row_num = 5
rank_counter = 1
for emp in sorted_all:
    r = row_num
    
    # Pick fill color
    if emp["won_in_month"]:
        rank = emp.get("rank", 0)
        if rank == 1:    bg = C_RANK1
        elif rank == 2:  bg = C_RANK2
        elif rank == 3:  bg = C_RANK3
        else:            bg = C_KPI_OK
        status_text = f"✅ ĐẠT KPI (#{rank})"
    elif emp["has_won"] and not emp["won_in_month"]:
        bg = "E0F2FE"
        status_text = "✅ Đạt (tháng khác)"
    elif emp["is_expired"] and not emp["has_won"]:
        bg = C_KPI_FAIL
        status_text = "❌ Hết hạn"
    else:
        bg = C_ROW_ALT if row_num % 2 == 0 else "FFFFFF"
        days_left = max(0, (emp["deadline"] - now).days)
        status_text = f"⏳ Đang làm ({days_left} ngày còn)"

    fill = make_fill(bg)
    font_data = Font(name="Calibri", size=10, color="1E293B")
    font_bold = Font(name="Calibri", size=10, bold=True, color="1E293B")

    vals = [
        row_num - 4,  # STT
        f"#{emp['rank']}" if emp["won_in_month"] else "-",  # Rank
        emp["emp_code"],
        emp["full_name"],
        emp["dept"],
        emp["role_label"],
        emp["join_date"].strftime("%d/%m/%Y") if emp["join_date"] else "",
        emp["target_count"],
        emp["current_count"],
        emp["win_time"].strftime("%d/%m/%Y") if emp["win_time"] else "-",
        emp["days_to_complete"] if emp["days_to_complete"] is not None else "-",
        200000 if emp["won_in_month"] else 0,
        status_text,
    ]
    
    for col_idx, val in enumerate(vals, 1):
        cell = ws1.cell(row=r, column=col_idx, value=val)
        style_cell(cell, fill=fill,
            font=font_bold if col_idx in (4, 9, 13) else font_data,
            align=Alignment(horizontal="center" if col_idx in (1,2,7,8,9,10,11,12) else "left", vertical="center"),
            border=thin_border()
        )
    
    # Format currency cell
    ws1.cell(row=r, column=12).number_format = '#,##0'
    ws1.row_dimensions[r].height = 20
    row_num += 1

# ── Add totals row ──
ws1.merge_cells(f"A{row_num}:K{row_num}")
ws1[f"A{row_num}"].value = f"TỔNG CỘNG: {len(winners)} người đạt KPI"
style_cell(ws1[f"A{row_num}"],
    fill=make_fill(C_TITLE_BG),
    font=Font(name="Calibri", size=11, bold=True, color="FFFFFF"),
    align=Alignment(horizontal="center", vertical="center"),
    border=thin_border()
)
total_cell = ws1.cell(row=row_num, column=12, value=len(winners) * 200000)
total_cell.number_format = '#,##0'
style_cell(total_cell,
    fill=make_fill(C_TITLE_BG),
    font=Font(name="Calibri", size=11, bold=True, color="FFD700"),
    align=Alignment(horizontal="center", vertical="center"),
    border=thin_border()
)
ws1.row_dimensions[row_num].height = 26

print("Sheet 1 (Tong hop) done.")

# ══════════════════════════════════════════════════════════════════
# SHEET 2: CHI TIẾT KẾT NỐI TỪNG NGƯỜI ĐẠT KPI
# ══════════════════════════════════════════════════════════════════
ws2 = wb.create_sheet(title=f"Chi tiet T{MONTH}-{YEAR}")
ws2.freeze_panes = "A3"

# Title row
ws2.merge_cells("A1:I1")
c = ws2["A1"]
c.value = f"CHI TIẾT KẾT NỐI — NGƯỜI ĐẠT KPI THÁNG {MONTH}/{YEAR}"
style_cell(c,
    fill=make_fill(C_DETAIL_HDR),
    font=Font(name="Calibri", size=15, bold=True, color="FFFFFF"),
    align=Alignment(horizontal="center", vertical="center")
)
ws2.row_dimensions[1].height = 34

# Set column widths for detail sheet
DET_COLS = ["A","B","C","D","E","F","G","H","I"]
DET_WIDTHS = [5, 6, 25, 12, 22, 18, 12, 22, 20]
for col, w in zip(DET_COLS, DET_WIDTHS):
    ws2.column_dimensions[col].width = w

detail_row = 3

for winner in winners:
    rank = winner["rank"]
    rank_medal = "🥇" if rank == 1 else ("🥈" if rank == 2 else ("🥉" if rank == 3 else f"#{rank}"))

    # ── Person header block ──
    ws2.merge_cells(f"A{detail_row}:I{detail_row}")
    cell = ws2[f"A{detail_row}"]
    cell.value = f"{rank_medal}  {winner['full_name']} ({winner['emp_code']}) — Xếp hạng #{rank}"
    rank_bg = C_RANK1 if rank==1 else (C_RANK2 if rank==2 else (C_RANK3 if rank==3 else "D1FAE5"))
    style_cell(cell,
        fill=make_fill(rank_bg),
        font=Font(name="Calibri", size=13, bold=True, color="1E3A8A"),
        align=Alignment(horizontal="left", vertical="center", indent=1),
    )
    ws2.row_dimensions[detail_row].height = 28
    detail_row += 1

    # ── Info sub-row ──
    info_cells = [
        (f"A{detail_row}", f"B{detail_row}", "Bộ phận:"),
        (None, None, None),
        (f"C{detail_row}", f"D{detail_row}", winner["dept"]),
        (None, None, None),
    ]
    ws2.merge_cells(f"A{detail_row}:B{detail_row}")
    ws2.merge_cells(f"C{detail_row}:D{detail_row}")
    ws2.merge_cells(f"E{detail_row}:F{detail_row}")
    ws2.merge_cells(f"G{detail_row}:I{detail_row}")

    ws2[f"A{detail_row}"].value = f"📂 Bộ phận: {winner['dept']}"
    ws2[f"C{detail_row}"].value = f"👤 Chức vụ: {winner['role_label']}"
    ws2[f"E{detail_row}"].value = f"📅 Ngày vào: {winner['join_date'].strftime('%d/%m/%Y')}"
    ws2[f"G{detail_row}"].value = f"🏆 Hoàn thành: {winner['win_time'].strftime('%d/%m/%Y')} ({winner['days_to_complete']} ngày)"

    for col_letter in ["A","C","E","G"]:
        c = ws2[f"{col_letter}{detail_row}"]
        style_cell(c,
            fill=make_fill(C_PERSON_BG),
            font=Font(name="Calibri", size=10, bold=False, color="1E3A8A"),
            align=Alignment(horizontal="left", vertical="center", indent=1)
        )
    ws2.row_dimensions[detail_row].height = 20
    detail_row += 1

    # KPI progress row
    ws2.merge_cells(f"A{detail_row}:D{detail_row}")
    ws2.merge_cells(f"E{detail_row}:I{detail_row}")
    ws2[f"A{detail_row}"].value = f"   KPI mục tiêu: {winner['target_count']} kết nối trong {60 if winner['role_label'] != 'Operator' else 30} ngày"
    ws2[f"E{detail_row}"].value = f"   ✅ Đã đạt: {winner['current_count']} kết nối  |  Thưởng: 200,000 VNĐ"
    for col_letter in ["A","E"]:
        c = ws2[f"{col_letter}{detail_row}"]
        style_cell(c,
            fill=make_fill("DCFCE7"),
            font=Font(name="Calibri", size=10, bold=True, color="065F46"),
            align=Alignment(horizontal="left", vertical="center", indent=1)
        )
    ws2.row_dimensions[detail_row].height = 18
    detail_row += 1

    # ── Connection table header ──
    conn_headers = ["STT", "KẾT NỐI", "Mã NV", "Họ và tên", "Bộ phận / Tổ", "Chức vụ", "Ngày kết nối", "Có trong KPI?", "Ghi chú"]
    for col_idx, h in enumerate(conn_headers, 1):
        cell = ws2.cell(row=detail_row, column=col_idx, value=h)
        style_cell(cell,
            fill=make_fill(C_HEADER_BG),
            font=Font(name="Calibri", size=9, bold=True, color="FFFFFF"),
            align=Alignment(horizontal="center", vertical="center"),
            border=thin_border()
        )
    ws2.row_dimensions[detail_row].height = 22
    detail_row += 1

    # ── Connection rows ──
    target_count = winner["target_count"]
    for stt, (conn_obj, ct) in enumerate(winner["valid_conns"], 1):
        c_eid = str(conn_obj.connector_id)
        eid   = winner["id"]
        
        # Determine the "other person"
        if c_eid == eid:
            # This person is the connector -> other is new_hire
            other_name = conn_obj.nh_name
            other_code = conn_obj.nh_code
            other_dept = conn_obj.nh_part or conn_obj.nh_dept or "N/A"
            other_role = conn_obj.nh_role or "N/A"
            direction = "← Nhận"
        else:
            # This person is new_hire -> other is connector
            other_name = conn_obj.cn_name
            other_code = conn_obj.cn_code
            other_dept = conn_obj.cn_part or conn_obj.cn_dept or "N/A"
            other_role = conn_obj.cn_role or "N/A"
            direction = "→ Gửi"

        in_kpi = stt <= target_count
        date_str = ct.strftime("%d/%m/%Y %H:%M") if ct else "N/A"
        note = f"KẾT NỐI #{stt} — đạt KPI!" if stt == target_count else ("Trong KPI" if in_kpi else "Ngoài KPI")
        
        row_bg = "ECFDF5" if in_kpi else "F8FAFC"
        kpi_text = f"✅ #{stt}" if in_kpi else "➕ Thêm"

        vals2 = [stt, direction, other_code, other_name, other_dept, other_role, date_str, kpi_text, note]
        for col_idx, val in enumerate(vals2, 1):
            cell = ws2.cell(row=detail_row, column=col_idx, value=val)
            is_win_row = (stt == target_count)
            style_cell(cell,
                fill=make_fill("FEFCE8" if is_win_row else row_bg),
                font=Font(name="Calibri", size=9,
                         bold=is_win_row,
                         color="92400E" if is_win_row else "1E293B"),
                align=Alignment(horizontal="center" if col_idx in (1,2,7,8) else "left",
                               vertical="center"),
                border=thin_border()
            )
        if stt == target_count:
            ws2.row_dimensions[detail_row].height = 16
        else:
            ws2.row_dimensions[detail_row].height = 15
        detail_row += 1

    # ── Spacer rows between people ──
    for _ in range(2):
        ws2.row_dimensions[detail_row].height = 6
        detail_row += 1

print("Sheet 2 (Chi tiet) done.")

# ══════════════════════════════════════════════════════════════════
# SHEET 3: CHI TIEU TUNG NGUOI (all participants)
# ══════════════════════════════════════════════════════════════════
ws3 = wb.create_sheet(title=f"Chi tieu T{MONTH}-{YEAR}")

ws3.merge_cells("A1:H1")
ws3["A1"].value = f"CHI TIÊU KẾT NỐI — TẤT CẢ NHÂN VIÊN THAM GIA THÁNG {MONTH}/{YEAR}"
style_cell(ws3["A1"],
    fill=make_fill("7C3AED"),
    font=Font(name="Calibri", size=14, bold=True, color="FFFFFF"),
    align=Alignment(horizontal="center", vertical="center")
)
ws3.row_dimensions[1].height = 32

hdr3 = ["STT","Mã NV","Họ và tên","Bộ phận","Chức vụ","KPI (kết nối)","Đã đạt","Ngày vào","Deadline","Ngày HT","Số ngày","Trạng thái","Thưởng"]
for ci, h in enumerate(hdr3, 1):
    c = ws3.cell(row=2, column=ci, value=h)
    style_cell(c,
        fill=make_fill("4C1D95"),
        font=Font(name="Calibri", size=9, bold=True, color="FFFFFF"),
        align=Alignment(horizontal="center", vertical="center"),
        border=thin_border()
    )
ws3.row_dimensions[2].height = 22

COL3_W = [4,12,22,18,14,10,8,12,12,12,8,18,12]
for ci, w in enumerate(COL3_W, 1):
    ws3.column_dimensions[get_column_letter(ci)].width = w

for stt, emp in enumerate(sorted_all, 1):
    r = stt + 2
    if emp["won_in_month"]:
        bg = "D1FAE5"
        status = f"✅ ĐẠT (#{emp['rank']})"
        reward = 200000
    elif emp["has_won"] and not emp["won_in_month"]:
        bg = "E0F2FE"
        status = "✅ Đạt (tháng khác)"
        reward = 0
    elif emp["is_expired"]:
        bg = "FEE2E2"
        status = "❌ Hết hạn"
        reward = 0
    else:
        bg = "FFFBEB" if stt % 2 == 0 else "FFFFFF"
        days_l = max(0,(emp["deadline"]-now).days)
        status = f"⏳ {days_l} ngày còn"
        reward = 0

    vals3 = [
        stt, emp["emp_code"], emp["full_name"], emp["dept"], emp["role_label"],
        emp["target_count"], emp["current_count"],
        emp["join_date"].strftime("%d/%m/%Y"),
        emp["deadline"].strftime("%d/%m/%Y"),
        emp["win_time"].strftime("%d/%m/%Y") if emp["win_time"] else "-",
        emp["days_to_complete"] if emp["days_to_complete"] is not None else "-",
        status, reward
    ]
    fill3 = make_fill(bg)
    for ci, val in enumerate(vals3, 1):
        cell = ws3.cell(row=r, column=ci, value=val)
        style_cell(cell,
            fill=fill3,
            font=Font(name="Calibri", size=9, bold=(ci in (3,7)),
                     color="065F46" if emp["won_in_month"] else "1E293B"),
            align=Alignment(horizontal="center" if ci in (1,6,7,8,9,10,11,13) else "left",
                           vertical="center"),
            border=thin_border()
        )
    ws3.cell(row=r, column=13).number_format = '#,##0'
    ws3.row_dimensions[r].height = 18

ws3.freeze_panes = "A3"
print("Sheet 3 (Chi tieu) done.")

# Save
output_path = os.path.join(os.path.dirname(__file__), f"Bao_cao_KPI_T{MONTH}_{YEAR}.xlsx")
wb.save(output_path)
db.close()
print(f"\n✅ Saved: {output_path}")

# -*- coding: utf-8 -*-
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

"""
Kiem tra KPI thang 7/2026 cho Top 3:
- Vu Van Phi (41 ket noi)
- Pham Viet Dat (39 ket noi)
- Nguyen Duc Quynh (31 ket noi)

Logic KPI:
- Operator / Cong nhan: can 10 ket noi trong 30 ngay
- Team Leader / Truong ca: can 20 ket noi trong 60 ngay
- Officer / Others (bao gom Part Leader): can 30 ket noi trong 60 ngay
"""
import os
import sys

# Đường dẫn đến backend để import modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
load_dotenv()

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timezone, timedelta

DATABASE_URL = os.getenv("CSB_DATABASE_URL", "")
if not DATABASE_URL:
    print("❌ Không tìm thấy CSB_DATABASE_URL trong .env")
    sys.exit(1)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()

# Danh sách Top 3 cần check (theo ảnh)
TOP3_NAMES = ["Vũ Văn Phi", "Phạm Viết Đạt", "Nguyễn Đức Quỳnh"]
MONTH = 7
YEAR = 2026

print("=" * 70)
print(f"   KIỂM TRA KPI THÁNG {MONTH}/{YEAR} - TOP 3")
print("=" * 70)

# Query tất cả employee refs
employees_query = text("""
    SELECT id, emp_code, full_name, role, join_date, department, part, is_active
    FROM csb_employee_refs
    WHERE is_active = true
    ORDER BY full_name
""")

employees = db.execute(employees_query).fetchall()

# Map tên -> employee
emp_map = {}
for e in employees:
    for name in TOP3_NAMES:
        if name.lower() in (e.full_name or "").lower() or (e.full_name or "").lower() in name.lower():
            emp_map[name] = e

# Nếu không tìm thấy chính xác, thử fuzzy
if len(emp_map) < 3:
    for e in employees:
        fname = (e.full_name or "").strip()
        for name in TOP3_NAMES:
            # So sánh theo từng từ
            name_words = set(name.lower().split())
            fname_words = set(fname.lower().split())
            if len(name_words & fname_words) >= 2 and name not in emp_map:
                emp_map[name] = e

print(f"\n📋 Tìm thấy {len(emp_map)}/3 người trong DB:\n")

for name in TOP3_NAMES:
    if name in emp_map:
        e = emp_map[name]
        print(f"  ✅ {name} -> {e.emp_code} | Role: {e.role} | Join: {e.join_date}")
    else:
        print(f"  ❌ {name} -> Không tìm thấy trong DB")

print()

# Kiểm tra từng người
for name in TOP3_NAMES:
    if name not in emp_map:
        continue
    
    emp = emp_map[name]
    emp_id = emp.id
    role = (emp.role or "").lower()
    
    # Xác định KPI target và deadline
    is_operator = "operator" in role or "công nhân" in role
    is_team_leader = "team leader" in role or "trưởng ca" in role
    
    if is_operator:
        target_count = 10
        duration_days = 30
        role_label = "Operator"
    elif is_team_leader:
        target_count = 20
        duration_days = 60
        role_label = "Team Leader"
    else:
        target_count = 30
        duration_days = 60
        role_label = "Staff/Officer"
    
    # Lấy join_date
    join_date = emp.join_date
    if join_date is None:
        print(f"\n⚠️  {name}: không có join_date!")
        continue
    
    if hasattr(join_date, 'tzinfo') and join_date.tzinfo is None:
        join_date = join_date.replace(tzinfo=timezone.utc)
    
    deadline = join_date + timedelta(days=duration_days)
    
    # Target month boundaries
    target_start = datetime(YEAR, MONTH, 1, tzinfo=timezone.utc)
    target_end = datetime(YEAR, MONTH + 1, 1, tzinfo=timezone.utc)
    now = datetime(2026, 7, 29, 10, 16, 0, tzinfo=timezone.utc)  # thời điểm hiện tại
    
    # Query accepted connections (trong deadline)
    conn_query = text("""
        SELECT id, connector_id, new_hire_id, status, created_at, responded_at
        FROM crw_connections
        WHERE status = 'ACCEPTED'
          AND (connector_id = :eid OR new_hire_id = :eid)
        ORDER BY responded_at ASC
    """)
    conns = db.execute(conn_query, {"eid": str(emp_id)}).fetchall()
    
    # Lọc connections trong deadline
    valid_conns = []
    for c in conns:
        ct = c.responded_at or c.created_at
        if ct is None:
            continue
        if hasattr(ct, 'tzinfo') and ct.tzinfo is None:
            ct = ct.replace(tzinfo=timezone.utc)
        if ct <= deadline:
            valid_conns.append((c, ct))
    
    total_conns = len(valid_conns)
    
    # Kiểm tra có đạt KPI không
    has_won = total_conns >= target_count
    
    win_time = None
    days_to_complete = None
    won_in_july = False
    
    if has_won:
        winning_conn, win_time = valid_conns[target_count - 1]
        days_to_complete = int((win_time - join_date).total_seconds() // 86400)
        
        # Kiểm tra xem win trong tháng 7 không
        if target_start <= win_time < target_end:
            won_in_july = True
    
    # Connections trong tháng 7
    july_conns = [(c, ct) for c, ct in valid_conns if target_start <= ct < target_end]
    
    print("-" * 70)
    print(f"👤 {name}")
    print(f"   Mã NV     : {emp.emp_code}")
    print(f"   Vai trò   : {emp.role} ({role_label})")
    print(f"   Bộ phận   : {emp.part or emp.department or 'N/A'}")
    print(f"   Ngày vào  : {join_date.strftime('%d/%m/%Y')}")
    print(f"   Deadline  : {deadline.strftime('%d/%m/%Y')} ({duration_days} ngày)")
    print(f"   KPI target: {target_count} kết nối")
    print(f"   Đã kết nối: {total_conns} kết nối (trong deadline)")
    print(f"   Kết nối T7: {len(july_conns)} kết nối trong tháng 7")
    
    if has_won:
        print(f"   ✅ ĐẠT KPI! Hoàn thành ngày {win_time.strftime('%d/%m/%Y')} ({days_to_complete} ngày)")
        if won_in_july:
            print(f"   🏆 CHIẾN THẮNG THÁNG 7!")
        else:
            print(f"   ℹ️  Đã chiến thắng từ tháng trước (win_time: {win_time.strftime('%d/%m/%Y')})")
    else:
        print(f"   ❌ CHƯA ĐẠT KPI (còn thiếu {target_count - total_conns} kết nối)")
        is_expired = now > deadline
        if is_expired:
            print(f"   ⏰ ĐÃ HẾT HẠN - không thể đạt KPI nữa")
        else:
            days_left = (deadline - now).days
            print(f"   ⏳ Còn {days_left} ngày để hoàn thành")

print("\n" + "=" * 70)
print("   CHÚ THÍCH KPI:")
print("   - Operator/Công nhân: cần 10 kết nối trong 30 ngày từ ngày vào")
print("   - Team Leader/Trưởng ca: cần 20 kết nối trong 60 ngày từ ngày vào")
print("   - Staff/Officer/Part Leader: cần 30 kết nối trong 60 ngày từ ngày vào")
print("=" * 70)

# In thêm số lượng kết nối tháng 7 theo ngày (chỉ cho Top 3)
print("\n📅 CHI TIẾT KẾT NỐI THÁNG 7/2026:\n")
for name in TOP3_NAMES:
    if name not in emp_map:
        continue
    emp = emp_map[name]
    
    conn_query2 = text("""
        SELECT c.id, c.connector_id, c.new_hire_id, c.responded_at,
               nh.full_name as new_hire_name, nh.role as new_hire_role,
               cn.full_name as connector_name, cn.role as connector_role
        FROM crw_connections c
        LEFT JOIN csb_employee_refs nh ON nh.id = c.new_hire_id
        LEFT JOIN csb_employee_refs cn ON cn.id = c.connector_id
        WHERE c.status = 'ACCEPTED'
          AND (c.connector_id = :eid OR c.new_hire_id = :eid)
          AND c.responded_at >= :start AND c.responded_at < :end
        ORDER BY c.responded_at ASC
    """)
    
    july_start = datetime(YEAR, MONTH, 1)
    july_end = datetime(YEAR, MONTH + 1, 1)
    
    rows = db.execute(conn_query2, {
        "eid": str(emp.id),
        "start": july_start,
        "end": july_end
    }).fetchall()
    
    print(f"  {name} - {len(rows)} kết nối trong tháng 7:")
    for r in rows[:5]:  # Hiển thị 5 kết nối đầu
        other = r.new_hire_name if str(r.connector_id) == str(emp.id) else r.connector_name
        direction = "→" if str(r.connector_id) == str(emp.id) else "←"
        date_str = r.responded_at.strftime('%d/%m') if r.responded_at else "N/A"
        print(f"     {date_str} {direction} {other}")
    if len(rows) > 5:
        print(f"     ... và {len(rows) - 5} kết nối khác")
    print()

db.close()
print("✅ Hoàn tất kiểm tra!")

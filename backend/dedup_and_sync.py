"""
dedup_and_sync.py
-----------------
Xóa các bản ghi trùng emp_code / username trong bảng csb_employee_refs
(giữ lại bản ghi có hrm_employee_id khác NULL hoặc id nhỏ nhất),
sau đó in thống kê để kiểm tra.

Chạy: python dedup_and_sync.py
"""

import sqlite3
import os

# Đường dẫn tới DB SQLite của CSB backend
DB_PATH = os.path.join(os.path.dirname(__file__), "csb_connection.db")

if not os.path.exists(DB_PATH):
    # Thử csb.db trong thư mục app
    DB_PATH = os.path.join(os.path.dirname(__file__), "app", "csb.db")

print(f"[DB] Connecting: {DB_PATH}")
conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

# ── 1. Thống kê trước khi dọn ──────────────────────────────────────────────
cur.execute("SELECT COUNT(*) FROM csb_employee_refs")
total_before = cur.fetchone()[0]

cur.execute("""
    SELECT emp_code, COUNT(*) as cnt
    FROM csb_employee_refs
    GROUP BY emp_code
    HAVING cnt > 1
    ORDER BY cnt DESC
""")
dup_codes = cur.fetchall()

cur.execute("""
    SELECT username, COUNT(*) as cnt
    FROM csb_employee_refs
    GROUP BY username
    HAVING cnt > 1
    ORDER BY cnt DESC
""")
dup_users = cur.fetchall()

print(f"\n[BEFORE] Total rows   : {total_before}")
print(f"[BEFORE] Dup emp_codes: {len(dup_codes)}")
print(f"[BEFORE] Dup usernames: {len(dup_users)}")

# ── 2. Xóa duplicate emp_code (giữ row có hrm_employee_id IS NOT NULL, hoặc id nhỏ nhất) ──
deleted_code = 0
for (emp_code, cnt) in dup_codes:
    cur.execute("""
        SELECT id, hrm_employee_id FROM csb_employee_refs
        WHERE emp_code = ?
        ORDER BY
            CASE WHEN hrm_employee_id IS NOT NULL THEN 0 ELSE 1 END,
            id ASC
    """, (emp_code,))
    rows = cur.fetchall()
    keep_id = rows[0][0]
    delete_ids = [r[0] for r in rows[1:]]
    if delete_ids:
        cur.executemany(
            "DELETE FROM csb_employee_refs WHERE id = ?",
            [(i,) for i in delete_ids]
        )
        deleted_code += len(delete_ids)
        print(f"  [DEDUP emp_code] {emp_code}: keep id={keep_id}, deleted {delete_ids}")

conn.commit()

# ── 3. Xóa duplicate username (sau khi đã dedup emp_code) ──────────────────
cur.execute("""
    SELECT username, COUNT(*) as cnt
    FROM csb_employee_refs
    GROUP BY username
    HAVING cnt > 1
    ORDER BY cnt DESC
""")
dup_users2 = cur.fetchall()

deleted_user = 0
for (username, cnt) in dup_users2:
    cur.execute("""
        SELECT id, hrm_employee_id FROM csb_employee_refs
        WHERE username = ?
        ORDER BY
            CASE WHEN hrm_employee_id IS NOT NULL THEN 0 ELSE 1 END,
            id ASC
    """, (username,))
    rows = cur.fetchall()
    keep_id = rows[0][0]
    delete_ids = [r[0] for r in rows[1:]]
    if delete_ids:
        cur.executemany(
            "DELETE FROM csb_employee_refs WHERE id = ?",
            [(i,) for i in delete_ids]
        )
        deleted_user += len(delete_ids)
        print(f"  [DEDUP username] {username}: keep id={keep_id}, deleted {delete_ids}")

conn.commit()

# ── 4. Thống kê sau khi dọn ────────────────────────────────────────────────
cur.execute("SELECT COUNT(*) FROM csb_employee_refs")
total_after = cur.fetchone()[0]

print(f"\n[AFTER]  Total rows     : {total_after}")
print(f"[AFTER]  Deleted (code) : {deleted_code}")
print(f"[AFTER]  Deleted (user) : {deleted_user}")
print(f"[AFTER]  Total deleted  : {deleted_code + deleted_user}")
print("\n[OK] Dedup hoan tat. Hay chay lai: py manage.py sync_to_csb")

conn.close()

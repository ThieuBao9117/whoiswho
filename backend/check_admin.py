import sqlite3

db_path = "csb_connection.db"
conn = sqlite3.connect(db_path)
cur = conn.cursor()

# List tables
cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cur.fetchall()
print("=== ALL TABLES ===")
for t in tables:
    print(f"  - {t[0]}")

# Check csb_employee_refs for admin
print("\n=== csb_employee_refs (looking for admin) ===")
try:
    cur.execute("SELECT id, emp_code, username, full_name, department, role, status, is_active FROM csb_employee_refs WHERE username LIKE '%admin%' OR emp_code LIKE '%ADM%'")
    rows = cur.fetchall()
    if rows:
        for r in rows:
            print(f"  id={r[0]}, emp_code={r[1]}, username={r[2]}, full_name={r[3]}, dept={r[4]}, role={r[5]}, status={r[6]}, is_active={r[7]}")
    else:
        print("  *** NO ADMIN USER FOUND! ***")
except Exception as e:
    print(f"  Error: {e}")

# Show all users
print("\n=== ALL USERS IN csb_employee_refs ===")
try:
    cur.execute("SELECT id, emp_code, username, full_name, is_active FROM csb_employee_refs ORDER BY id LIMIT 20")
    rows = cur.fetchall()
    print(f"  Total shown: {len(rows)}")
    for r in rows:
        print(f"  id={r[0]}, emp_code={r[1]}, username={r[2]}, name={r[3]}, active={r[4]}")
except Exception as e:
    print(f"  Error: {e}")

# Count total
print("\n=== TOTAL COUNT ===")
try:
    cur.execute("SELECT COUNT(*) FROM csb_employee_refs")
    print(f"  Total records: {cur.fetchone()[0]}")
    cur.execute("SELECT COUNT(*) FROM csb_employee_refs WHERE is_active = 1")
    print(f"  Active records: {cur.fetchone()[0]}")
except Exception as e:
    print(f"  Error: {e}")

conn.close()

"""
Direct SQLite sync — fetches users from HRM API and inserts into csb_connection.db
"""
import urllib.request
import json
import sqlite3
from datetime import datetime

HRM_URL = "http://localhost:8080/accounts/api/user-list/"
API_KEY = "hrm-csb-api-2026-CHANGE_ME"
DB_FILE = "csb_connection.db"


def fetch_all():
    users, next_url, page = [], f"{HRM_URL}?api_key={API_KEY}", 1
    while next_url:
        print(f"  Page {page}...", end=" ", flush=True)
        with urllib.request.urlopen(next_url, timeout=30) as r:
            data = json.loads(r.read())
        users.extend(data.get("results", []))
        print(len(data.get("results", [])))
        next_url, page = data.get("next"), page + 1
    return users


def sync(users):
    conn = sqlite3.connect(DB_FILE)
    now = datetime.utcnow().isoformat()
    created = updated = skipped = 0

    for u in users:
        username = (u.get("username") or "").strip()
        emp_code = (u.get("emp_code") or username).strip()
        full_name = (u.get("full_name") or username).strip()
        if not username or not emp_code:
            skipped += 1
            continue

        status = "Active" if u.get("is_active", True) else "Inactive"
        is_active = 1 if u.get("is_active", True) else 0
        hrm_id = u.get("id", 0)

        row = conn.execute(
            "SELECT id FROM csb_employee_refs WHERE username=? OR emp_code=?",
            (username, emp_code)
        ).fetchone()

        if row:
            conn.execute(
                """UPDATE csb_employee_refs
                   SET full_name=?, email=?, department=?, role=?,
                       status=?, is_active=?, last_synced_at=?, hrm_employee_id=?, hrm_user_id=?
                   WHERE id=?""",
                (full_name, u.get("email") or None, u.get("department"), u.get("role"),
                 status, is_active, now, hrm_id, hrm_id, row[0])
            )
            updated += 1
        else:
            conn.execute(
                """INSERT INTO csb_employee_refs
                   (hrm_employee_id, hrm_user_id, emp_code, username, full_name,
                    email, department, role, status, is_active, last_synced_at, created_at, updated_at)
                   VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (hrm_id, hrm_id, emp_code, username, full_name,
                 u.get("email") or None, u.get("department"), u.get("role"),
                 status, is_active, now, now, now)
            )
            created += 1

    conn.commit()
    conn.close()
    return created, updated, skipped


if __name__ == "__main__":
    print("=== Fetching from HRM ===")
    users = fetch_all()
    print(f"Total: {len(users)}\n=== Syncing to DB ===")
    created, updated, skipped = sync(users)
    print(f"\nCreated: {created} | Updated: {updated} | Skipped: {skipped}")
    print("\nLogin tại http://localhost:5173:")
    print("  Username: admin")
    print("  Password: csb6301!")

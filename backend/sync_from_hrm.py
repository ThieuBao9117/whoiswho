"""
Sync users from HRM API (localhost:8081) into CSB backend (localhost:8000)
Run: python sync_from_hrm.py
"""
import urllib.request
import urllib.parse
import json

HRM_URL = "http://localhost:8080/accounts/api/user-list/"
API_KEY = "hrm-csb-api-2026-CHANGE_ME"
CSB_BATCH_URL = "http://localhost:8000/api/sync/employees/batch"


def fetch_all_users():
    all_users = []
    next_url = f"{HRM_URL}?api_key={API_KEY}"
    page = 1
    while next_url:
        print(f"  Fetching page {page}...", end=" ")
        with urllib.request.urlopen(next_url, timeout=30) as resp:
            data = json.loads(resp.read())
        results = data.get("results", [])
        all_users.extend(results)
        print(f"{len(results)} users")
        next_url = data.get("next")
        page += 1
    return all_users


def build_payload(user, index):
    return {
        "hrm_employee_id": user.get("id", index),
        "hrm_user_id": user.get("id"),
        "emp_code": user.get("emp_code") or user.get("username", ""),
        "username": user.get("username", ""),
        "full_name": user.get("full_name") or user.get("username", ""),
        "email": user.get("email") or None,
        "department": user.get("department") or None,
        "role": user.get("role") or None,
        "status": "Active" if user.get("is_active", True) else "Inactive",
    }


def batch_sync(payloads, batch_size=100):
    total_created = 0
    total_updated = 0
    for i in range(0, len(payloads), batch_size):
        batch = payloads[i:i + batch_size]
        body = json.dumps(batch).encode("utf-8")
        req = urllib.request.Request(
            CSB_BATCH_URL,
            data=body,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=60) as resp:
            result = json.loads(resp.read())
        total_created += result.get("created_count", 0)
        total_updated += result.get("updated_count", 0)
        print(f"  Batch {i//batch_size + 1}: created={result.get('created_count',0)}, updated={result.get('updated_count',0)}")
        if result.get("errors"):
            for err in result["errors"][:3]:
                print(f"    ERROR: {err}")
    return total_created, total_updated


if __name__ == "__main__":
    print("=== Fetching users from HRM ===")
    users = fetch_all_users()
    print(f"Total users fetched: {len(users)}")

    print("\n=== Syncing to CSB backend ===")
    payloads = [build_payload(u, i) for i, u in enumerate(users) if u.get("username")]
    created, updated = batch_sync(payloads)

    print(f"\n=== Done! Created: {created}, Updated: {updated} ===")
    print("\nNow login at http://localhost:5173 with:")
    print("  Username: admin  (or any username from HRM)")
    print("  Password: csb6301!")

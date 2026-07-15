"""
sync_from_hrm_full.py - Dong bo nhan vien tu HRM sang WHO Is WHO

Cach chay:
    venv/Scripts/python.exe sync_from_hrm_full.py

Tuy chon:
    venv/Scripts/python.exe sync_from_hrm_full.py --dry-run   (chi xem, khong ghi)
    venv/Scripts/python.exe sync_from_hrm_full.py --all       (ca active lan inactive)
"""

import requests
import sys
import os
from datetime import datetime

# Fix Windows terminal encoding for Vietnamese characters
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

# ─────────────────────────────────────────────
# CẤU HÌNH - chỉnh sửa nếu cần
# ─────────────────────────────────────────────
HRM_BASE   = "http://50.50.50.4"
HRM_USER   = "mi_mtri"
HRM_PASS   = "@Dmin123#$"

CSB_BASE   = "http://localhost:7000"   # Backend CSB đang chạy local

BATCH_SIZE = 50  # Số nhân viên gửi mỗi lần (tránh timeout)
TIMEOUT    = 30  # Giây

# ─────────────────────────────────────────────
# BƯỚC 1: Đăng nhập HRM - lấy JWT token
# ─────────────────────────────────────────────

def get_hrm_token():
    print(f"[1/4] Dang nhap HRM: {HRM_BASE}/accounts/api/login/")
    try:
        resp = requests.post(
            f"{HRM_BASE}/accounts/api/login/",
            json={"username": HRM_USER, "password": HRM_PASS},
            timeout=TIMEOUT
        )
        resp.raise_for_status()
        token = resp.json().get("access")
        if not token:
            print(f"    LOI: Khong lay duoc access token. Response: {resp.text[:200]}")
            sys.exit(1)
        print(f"    OK - Da lay duoc JWT token")
        return token
    except requests.exceptions.ConnectionError:
        print(f"    LOI: Khong ket noi duoc toi {HRM_BASE}")
        print(f"    -> Kiem tra HRM co dang chay khong, hoac doi dia chi IP")
        sys.exit(1)
    except requests.exceptions.HTTPError as e:
        print(f"    LOI HTTP: {e}")
        sys.exit(1)


# ─────────────────────────────────────────────
# BƯỚC 2: Pull danh sách nhân viên từ HRM
# ─────────────────────────────────────────────

def fetch_employees_from_hrm(token, include_inactive=False):
    print(f"[2/4] Pull danh sach nhan vien tu HRM...")
    headers = {"Authorization": f"Bearer {token}"}

    all_employees = []
    page = 1

    while True:
        params = {
            "page": page,
            "page_size": 200,
        }
        # Nếu không lấy tất cả, chỉ lấy Active
        if not include_inactive:
            params["status"] = "Active"

        try:
            resp = requests.get(
                f"{HRM_BASE}/accounts/api/employees/",
                params=params,
                headers=headers,
                timeout=TIMEOUT
            )
            resp.raise_for_status()
        except requests.exceptions.HTTPError as e:
            print(f"    LOI HTTP trang {page}: {e}")
            break

        data = resp.json()

        # Hỗ trợ cả dạng có phân trang lẫn không
        if isinstance(data, list):
            results = data
            has_next = False
        elif isinstance(data, dict):
            results = data.get("results", [])
            has_next = bool(data.get("next"))
        else:
            results = []
            has_next = False

        all_employees.extend(results)
        print(f"    Trang {page}: {len(results)} nhan vien (tong: {len(all_employees)})")

        if not has_next or len(results) == 0:
            break
        page += 1

    print(f"    OK - Tong cong: {len(all_employees)} nhan vien tu HRM")
    return all_employees


# ─────────────────────────────────────────────
# BƯỚC 3: Chuyển đổi format HRM → CSB payload
# ─────────────────────────────────────────────

def map_employee_to_csb(emp):
    """
    Map fields từ HRM Employee API sang CSB EmployeeSyncPayload
    """
    # Xác định trạng thái
    if emp.get("is_resigned") or emp.get("status", "Active") == "Inactive":
        status = "Inactive"
    else:
        status = emp.get("status", "Active")

    # Parse join_date
    join_date = None
    raw_date = emp.get("join_date")
    if raw_date:
        try:
            join_date = datetime.strptime(raw_date, "%Y-%m-%d").isoformat()
        except (ValueError, TypeError):
            join_date = None

    # Photo URL - giữ nguyên nếu là full URL hợp lệ, sửa nếu bị lỗi localhost từ Django
    photo = emp.get("photo")
    if photo:
        if photo.startswith("http://127.0.0.1") or photo.startswith("http://localhost"):
            from urllib.parse import urlparse
            parsed = urlparse(photo)
            photo = f"{HRM_BASE}{parsed.path}"
        elif not photo.startswith("http"):
            photo = f"{HRM_BASE}{photo}"

    return {
        "hrm_employee_id": emp.get("hrm_employee_id") or emp.get("id"),
        "hrm_user_id":     emp.get("user_id") or emp.get("hrm_user_id"),
        "emp_code":        emp.get("emp_code", "").strip(),
        "username":        emp.get("username", "").strip(),
        "full_name":       emp.get("full_name", "").strip(),
        "email":           emp.get("email"),
        "entity":          emp.get("entity"),
        "division":        emp.get("division"),
        "department":      emp.get("department"),
        "team":            emp.get("team"),
        "part":            emp.get("part"),
        "position":        emp.get("position") or emp.get("role"),
        "role":            emp.get("role"),
        "status":          status,
        "join_date":       join_date,
        "photo":           photo,
    }


# ─────────────────────────────────────────────
# BƯỚC 4: Gửi batch sync lên CSB
# ─────────────────────────────────────────────

def sync_to_csb(employees, dry_run=False):
    print(f"[3/4] Chuan bi sync {len(employees)} nhan vien vao CSB...")

    # Lọc bỏ những record thiếu emp_code hoặc username
    valid = []
    skipped = []
    for emp in employees:
        mapped = map_employee_to_csb(emp)
        if not mapped["emp_code"] or not mapped["username"]:
            skipped.append(emp.get("full_name", "?"))
            continue
        valid.append(mapped)

    if skipped:
        print(f"    BO QUA {len(skipped)} nhan vien thieu emp_code/username")
        for name in skipped[:5]:
            safe_name = name.encode('ascii', errors='replace').decode('ascii')
            print(f"      - {safe_name}")

    print(f"    Se sync: {len(valid)} nhan vien")

    if dry_run:
        print("\n    [DRY RUN] Chi hien thi, khong ghi vao CSB:")
        for emp in valid[:10]:
            print(f"      {emp['emp_code']:12} | {emp['username']:20} | {emp['full_name']} | {emp['status']}")
        if len(valid) > 10:
            print(f"      ... va {len(valid) - 10} nhan vien khac")
        return {"success": True, "synced": len(valid), "dry_run": True}

    # Chia batch
    total_created = 0
    total_updated = 0
    total_errors = []

    for i in range(0, len(valid), BATCH_SIZE):
        batch = valid[i : i + BATCH_SIZE]
        batch_num = i // BATCH_SIZE + 1
        total_batches = (len(valid) + BATCH_SIZE - 1) // BATCH_SIZE

        print(f"    Batch {batch_num}/{total_batches}: {len(batch)} nhan vien...", end=" ")

        try:
            resp = requests.post(
                f"{CSB_BASE}/api/sync/employees/batch",
                json=batch,
                timeout=TIMEOUT
            )
            resp.raise_for_status()
            result = resp.json()

            total_created += result.get("created_count", 0)
            total_updated += result.get("updated_count", 0)
            errors = result.get("errors", [])
            if errors:
                total_errors.extend(errors[:3])  # Giới hạn log
            print(f"OK (moi:{result.get('created_count',0)} cap-nhat:{result.get('updated_count',0)})")

        except requests.exceptions.HTTPError as e:
            msg = f"Batch {batch_num} loi HTTP: {e}"
            print(f"LOI - {msg}")
            total_errors.append(msg)
        except requests.exceptions.ConnectionError:
            msg = "Khong ket noi duoc CSB backend (localhost:7000)"
            print(f"LOI - {msg}")
            total_errors.append(msg)
            break

    return {
        "success": len(total_errors) == 0,
        "created": total_created,
        "updated": total_updated,
        "errors": total_errors,
    }


# ─────────────────────────────────────────────
# BƯỚC 5: Kiểm tra kết quả
# ─────────────────────────────────────────────

def verify_csb_sync():
    print("[4/4] Kiem tra ket qua trong CSB...")
    try:
        resp = requests.get(f"{CSB_BASE}/api/sync/status", timeout=10)
        data = resp.json()
        print(f"    Tong nhan vien CSB:  {data.get('total_employees_in_csb', 0)}")
        print(f"    Nhan vien active:    {data.get('active_employees', 0)}")
        print(f"    Lan sync gan nhat:   {data.get('last_sync_at', 'N/A')}")
    except Exception as e:
        print(f"    Khong kiem tra duoc: {e}")


# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────

if __name__ == "__main__":
    dry_run = "--dry-run" in sys.argv
    include_inactive = "--all" in sys.argv

    print("=" * 55)
    print("  SYNC NHAN VIEN: HRM -> WHO Is WHO")
    print(f"  HRM: {HRM_BASE}")
    print(f"  CSB: {CSB_BASE}")
    print(f"  Mode: {'DRY RUN (khong ghi)' if dry_run else 'LIVE'}")
    print(f"  Bao gom: {'Tat ca (ca nghi viec)' if include_inactive else 'Chi Active'}")
    print("=" * 55)

    # 1. Login HRM
    token = get_hrm_token()

    # 2. Pull employees
    employees = fetch_employees_from_hrm(token, include_inactive=include_inactive)

    if not employees:
        print("\nKhong co nhan vien nao de sync. Ket thuc.")
        sys.exit(0)

    # 3. Sync to CSB
    result = sync_to_csb(employees, dry_run=dry_run)

    # 4. Verify
    if not dry_run:
        verify_csb_sync()

    # Summary
    print("\n" + "=" * 55)
    if result.get("dry_run"):
        print(f"  [DRY RUN] Se sync {result['synced']} nhan vien")
    else:
        print(f"  Tao moi:       {result.get('created', 0)}")
        print(f"  Cap nhat:      {result.get('updated', 0)}")
        if result.get("errors"):
            print(f"  Loi:           {len(result['errors'])}")
            for err in result["errors"][:5]:
                print(f"    - {err}")
        status = "THANH CONG" if result["success"] else "CO LOI"
        print(f"  Ket qua:       {status}")
    print("=" * 55)

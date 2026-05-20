"""
Test kết nối HRM database qua ORM models
"""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0, ".")

from app.core.hrm_database import HrmSessionLocal
from app.models.hrm_models import HrmEmployee, HrmAuthUser

db = HrmSessionLocal()

try:
    # Test đếm nhân viên
    total = db.query(HrmEmployee).count()
    print(f"OK Total employees: {total}")

    # Test query 5 nhân viên đầu
    employees = db.query(HrmEmployee).limit(5).all()
    print(f"\nSample employees (5):")
    for emp in employees:
        print(f"  [{emp.emp_code}] {emp.full_name} | {emp.department} / {emp.part} | {emp.status}")

    # Test đếm users
    total_users = db.query(HrmAuthUser).count()
    print(f"\nOK Total auth_users: {total_users}")

    # Test join employee + user
    result = (
        db.query(HrmEmployee, HrmAuthUser)
        .join(HrmAuthUser, HrmEmployee.user_id == HrmAuthUser.id, isouter=True)
        .limit(3).all()
    )
    print(f"\nEmployee + User join (3):")
    for emp, user in result:
        username = user.username if user else "N/A"
        print(f"  {emp.full_name} -> username: {username}")

    print("\n=== HRM DB Integration: SUCCESS ===")

except Exception as e:
    print(f"FAIL: {e}")
    import traceback
    traceback.print_exc()
finally:
    db.close()

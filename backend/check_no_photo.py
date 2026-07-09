import sys; sys.path.insert(0, r'C:\WHO\csbwhoiswho\backend')
from app.core.database import SessionLocal
from app.models.csb_employee_ref import CSBEmployeeRef

db = SessionLocal()
all_emps = db.query(CSBEmployeeRef).filter(CSBEmployeeRef.is_active == True).order_by(CSBEmployeeRef.department, CSBEmployeeRef.full_name).all()

no_photo = [e for e in all_emps if not e.photo or e.photo.strip() == '']
has_photo = len(all_emps) - len(no_photo)

print(f"Tong active: {len(all_emps)} | Co anh: {has_photo} | Khong co anh: {len(no_photo)}")
print()
print(f"{'EMP_CODE':<12} | {'HO_TEN':<28} | {'PHONG_BAN':<20} | ROLE")
print('-' * 90)
for e in no_photo:
    emp_code = (e.emp_code or '')[:12]
    name     = (e.full_name or '')[:28]
    dept     = (e.department or 'N/A')[:20]
    role     = (e.role or '')
    print(f"{emp_code:<12} | {name:<28} | {dept:<20} | {role}")

db.close()
print()
print(f"==> {len(no_photo)} nguoi chua co anh dai dien")

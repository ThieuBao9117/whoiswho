from app.core.database import SessionLocal
from app.models.csb_employee_ref import CSBEmployeeRef

db = SessionLocal()
users = db.query(CSBEmployeeRef).all()
print([u.username for u in users])
db.close()
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.models.csb_employee_ref import CSBEmployeeRef
from app.api.auth import read_users_me

engine = create_engine('postgresql+psycopg://postgres:%40Dmin123%23$@localhost:5432/csb_db')
Session = sessionmaker(bind=engine)
db = Session()

user = db.query(CSBEmployeeRef).filter(CSBEmployeeRef.emp_code == 'V0260311').first()
if user:
    res = read_users_me(user, db)
    print("UserMe Response Photo:", res.get("employee_profile", {}).get("photo"))
else:
    print("User not found in DB")

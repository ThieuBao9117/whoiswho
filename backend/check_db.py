import sys
import codecs
sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())

from sqlalchemy import create_engine, text

engine = create_engine('postgresql+psycopg://postgres:%40Dmin123%23$@localhost:5432/csb_db')
with engine.connect() as conn:
    print("--- BVLam ---")
    res1 = conn.execute(text("SELECT id, emp_code, full_name, photo FROM csb_employee_refs WHERE username='ASSEM_BVLam'")).fetchone()
    if res1:
        print(f"ID: {res1.id}, Code: {res1.emp_code}, Name: {res1.full_name}, Photo: {res1.photo}")
    else:
        print("Not found")
    
    print("--- Users without photo ---")
    res2 = conn.execute(text("SELECT COUNT(*) FROM csb_employee_refs WHERE photo IS NULL")).scalar()
    print(f"Count: {res2}")

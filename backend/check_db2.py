import sys, codecs
sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())
from sqlalchemy import create_engine, text

engine = create_engine('postgresql+psycopg://postgres:%40Dmin123%23$@localhost:5432/csb_db')
with engine.connect() as conn:
    res = conn.execute(text("SELECT emp_code, full_name FROM csb_employee_refs WHERE full_name LIKE '%Lâm%' OR full_name LIKE '%Hoàng%' ORDER BY emp_code DESC LIMIT 10")).fetchall()
    for r in res:
        print(f"Code: {r.emp_code}, Name: {r.full_name}")

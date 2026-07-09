import sys
sys.stdout.reconfigure(encoding='utf-8')
from sqlalchemy import create_engine, text
engine = create_engine('postgresql+psycopg://postgres:%40Dmin123%23$@localhost:5432/csb_db')
with engine.connect() as conn:
    res = conn.execute(text("SELECT * FROM csb_employee_refs WHERE emp_code='V0230301'")).mappings().fetchone()
    print(dict(res))

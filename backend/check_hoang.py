from sqlalchemy import create_engine, text

engine = create_engine('postgresql+psycopg://postgres:%40Dmin123%23$@localhost:5432/csb_db')
with engine.connect() as conn:
    print("--- Searching for MI_MHHoang in CSB ---")
    res1 = conn.execute(text("SELECT id, username, emp_code, is_active FROM csb_employee_refs WHERE username='MI_MHHoang'")).fetchone()
    print("Result:", res1)
    
    print("--- Searching for any user like '%Hoang%' ---")
    res2 = conn.execute(text("SELECT username, emp_code FROM csb_employee_refs WHERE full_name ILIKE '%Hoang%'")).fetchall()
    for row in res2:
        print(row)

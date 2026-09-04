import sys
import codecs
sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())

from sqlalchemy import create_engine, text

engine = create_engine('postgresql+psycopg://postgres:%40Dmin123%23$@localhost:5432/csb_db')
with engine.connect() as conn:
    # Check table structure first
    cols = conn.execute(text("""
        SELECT column_name FROM information_schema.columns 
        WHERE table_name = 'csb_employee_refs' ORDER BY ordinal_position
    """)).fetchall()
    print("Columns:", [c[0] for c in cols])
    
    # Query drivers
    res = conn.execute(text("""
        SELECT username, emp_code, full_name, department, role, position
        FROM csb_employee_refs 
        WHERE LOWER(role) LIKE '%driver%' 
           OR LOWER(position) LIKE '%driver%'
        ORDER BY full_name
    """)).fetchall()
    
    print(f"\n=== DRIVER ({len(res)} nguoi) ===")
    for r in res:
        print(f"  username={r[0]} | emp_code={r[1]} | ten={r[2]} | dept={r[3]} | role={r[4]} | position={r[5]}")

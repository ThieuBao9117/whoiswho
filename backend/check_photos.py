import sys
sys.stdout.reconfigure(encoding='utf-8')
from sqlalchemy import create_engine, text

engine = create_engine('postgresql+psycopg://postgres:%40Dmin123%23$@localhost:5432/csb_db')
with engine.connect() as conn:
    total = conn.execute(text('SELECT COUNT(*) FROM csb_employee_refs WHERE is_active=true')).scalar()
    with_photo = conn.execute(text("SELECT COUNT(*) FROM csb_employee_refs WHERE is_active=true AND photo IS NOT NULL AND photo != ''")).scalar()
    no_photo = total - with_photo
    print(f'Tong nhan vien active: {total}')
    print(f'Co hinh (photo): {with_photo}')
    print(f'Chua co hinh: {no_photo}')

    # Phan tich loai URL
    hrm_url = conn.execute(text("SELECT COUNT(*) FROM csb_employee_refs WHERE photo LIKE 'http%'")).scalar()
    game_url = conn.execute(text("SELECT COUNT(*) FROM csb_employee_refs WHERE photo LIKE '/game/avatars/%'")).scalar()
    other_url = with_photo - hrm_url - game_url
    print(f'\n--- Phan tich URL photo ---')
    print(f'  URL HRM (http://...): {hrm_url}')
    print(f'  URL game (/game/avatars/...): {game_url}')
    print(f'  URL khac: {other_url}')

    # Sample URL HRM
    rows = conn.execute(text("SELECT emp_code, photo FROM csb_employee_refs WHERE photo LIKE 'http%' LIMIT 3")).fetchall()
    print(f'\n--- Sample URL HRM ---')
    for r in rows:
        print(f'  {r[0]}: {r[1]}')

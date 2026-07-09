from sqlalchemy import create_engine, text

engine = create_engine('postgresql+psycopg://postgres:%40Dmin123%23$@localhost:5432/csb_db')
with engine.begin() as conn:
    conn.execute(text("UPDATE csb_employee_refs SET photo = REPLACE(photo, '/game/avatars/', '/game/assets/avatars/') WHERE photo IS NOT NULL"))
    print("Updated DB photo paths to /game/assets/avatars/")

from sqlalchemy import create_engine, text

url = "postgresql+psycopg://postgres:%40Dmin123%23$@localhost:5432/csb_db"
engine = create_engine(url, connect_args={"connect_timeout": 3})

try:
    with engine.connect() as conn:
        row = conn.execute(text("SELECT current_database(), version()")).fetchone()
        print(f"OK DB: {row[0]}")
        print(f"OK VER: {row[1][:60]}")
except Exception as e:
    print(f"FAIL: {e}")
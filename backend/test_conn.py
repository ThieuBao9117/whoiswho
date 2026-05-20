from sqlalchemy import create_engine, text

url = "postgresql+psycopg://postgres:123456@localhost:5433/hrm"
engine = create_engine(url, connect_args={"connect_timeout": 5})

try:
    with engine.connect() as conn:
        row = conn.execute(text("SELECT current_database(), version()")).fetchone()
        print(f"OK DB: {row[0]}")
        print(f"OK VER: {row[1][:60]}")
        tables = conn.execute(text(
            "SELECT tablename FROM pg_tables WHERE schemaname='public' ORDER BY tablename LIMIT 15"
        )).fetchall()
        print(f"\nTables found: {len(tables)}")
        for t in tables:
            print(f"  - {t[0]}")
except Exception as e:
    print(f"FAIL: {e}")

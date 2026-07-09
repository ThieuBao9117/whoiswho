from sqlalchemy import create_engine, text

engine = create_engine('postgresql+psycopg://postgres:%40Dmin123%23$@localhost:5432/postgres')
try:
    with engine.connect() as conn:
        conn.execute(text("COMMIT"))
        query = "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = 'csb_db' AND pid != pg_backend_pid()"
        result = conn.execute(text(query)).fetchall()
        print(f"Successfully terminated {len(result)} other connections to 'csb_db'.")
except Exception as e:
    print(f"Error terminating connections: {e}")

from sqlalchemy import create_engine, text

engine = create_engine(
    "postgresql+psycopg://postgres:123456@localhost:5433/hrm",
    connect_args={"connect_timeout": 5}
)

with engine.connect() as conn:
    tables = conn.execute(text(
        "SELECT tablename FROM pg_tables WHERE schemaname='public' ORDER BY tablename"
    )).fetchall()
    print("ALL HRM TABLES:")
    for t in tables:
        print(f"  {t[0]}")

    # Check hr_employee columns
    cols = conn.execute(text(
        "SELECT column_name, data_type FROM information_schema.columns "
        "WHERE table_name='hr_employee' ORDER BY ordinal_position"
    )).fetchall()
    print(f"\nhr_employee columns ({len(cols)}):")
    for c in cols:
        print(f"  {c[0]} ({c[1]})")

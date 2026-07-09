"""
Quick fix: Alter photo column from VARCHAR(100) to VARCHAR(500)
Run: venv/Scripts/python.exe fix_photo_column.py
"""
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os

load_dotenv()
db_url = os.getenv("CSB_DATABASE_URL")
print(f"Connecting to: {db_url[:40]}...")

engine = create_engine(db_url)
try:
    with engine.connect() as conn:
        conn.execute(text("ALTER TABLE csb_employee_refs ALTER COLUMN photo TYPE VARCHAR(500)"))
        conn.commit()
        print("OK - photo column expanded to VARCHAR(500)")
        
        # Also update Alembic version table so migration 003 is marked as done
        conn.execute(text("INSERT INTO alembic_version (version_num) VALUES ('003_expand_photo_column') ON CONFLICT DO NOTHING"))
        conn.commit()
        print("OK - Alembic version updated to 003_expand_photo_column")
except Exception as e:
    print(f"Error: {e}")

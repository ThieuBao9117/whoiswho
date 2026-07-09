from alembic.config import Config
from alembic import command
import os
import sys
from dotenv import load_dotenv

# Load environmental variables from .env
load_dotenv()

# Map CSB_DATABASE_URL to ALEMBIC_DATABASE_URL
csb_db_url = os.getenv("CSB_DATABASE_URL")
if csb_db_url:
    os.environ["ALEMBIC_DATABASE_URL"] = csb_db_url
    print("Setting ALEMBIC_DATABASE_URL from CSB_DATABASE_URL...")
else:
    print("WARNING: CSB_DATABASE_URL not found in environment!")

print("Current directory:", os.getcwd())
try:
    alembic_cfg = Config("alembic.ini")
    print("Upgrading database to head...")
    command.upgrade(alembic_cfg, "head")
    print("Database migration successfully completed!")
except Exception as e:
    print(f"Error during migration: {e}")
    import traceback
    traceback.print_exc()

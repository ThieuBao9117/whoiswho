"""
Import users from CSV into CSB database
Usage: python import_users.py
"""
import csv
import sys
import os
from datetime import datetime

# Add the app directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__))))

from sqlalchemy.orm import Session
from app.core.database import SessionLocal, engine, Base
from app.models.csb_models import CSBEmployeeRef


def import_users_from_csv(csv_file):
    """Import users from CSV file"""
    # Initialize database first - create tables
    from app.core.database import init_db
    init_db()
    
    db: Session = SessionLocal()
    
    try:
        with open(csv_file, 'r', encoding='utf-8-sig') as f:  # utf-8-sig handles BOM
            reader = csv.DictReader(f)
            
            count = 0
            for row in reader:
                username = row.get('username', '').strip()
                emp_code = row.get('emp_code', '').strip()
                full_name = row.get('full_name', '').strip()
                department = row.get('department', '').strip()
                role = row.get('role', '').strip()
                
                if not username or not emp_code:
                    continue
                
                # Check if user already exists
                existing = db.query(CSBEmployeeRef).filter(
                    (CSBEmployeeRef.username == username) | 
                    (CSBEmployeeRef.emp_code == emp_code)
                ).first()
                
                if existing:
                    print(f"Skipping {username} - already exists")
                    continue
                
                # Generate hrm_employee_id from row count
                hrm_employee_id = count + 10000
                
                # Create new user
                user = CSBEmployeeRef(
                    hrm_employee_id=hrm_employee_id,
                    hrm_user_id=None,
                    username=username,
                    emp_code=emp_code,
                    full_name=full_name if full_name else username,
                    department=department if department else 'General',
                    role=role if role else 'Employee',
                    status='Active',
                    is_active=True,
                    last_synced_at=datetime.utcnow()
                )
                db.add(user)
                count += 1
                if count <= 5:  # Print first 5 for debugging
                    print(f"Added: {username} - {full_name} ({department})")
            
            db.commit()
            print(f"\n✅ Successfully imported {count} users!")
            
    except Exception as e:
        db.rollback()
        print(f"❌ Error importing users: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    csv_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), "users_export.csv")
    
    if not os.path.exists(csv_file):
        print(f"❌ CSV file not found: {csv_file}")
        sys.exit(1)
    
    print(f"📥 Importing users from {csv_file}...")
    import_users_from_csv(csv_file)

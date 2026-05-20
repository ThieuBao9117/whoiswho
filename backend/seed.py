import sys
import os
from datetime import datetime

# Add the app directory to sys.path so we can import from app
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__))))

from sqlalchemy.orm import Session
from app.core.database import SessionLocal, engine, Base
from app.core.security import get_password_hash
from app.models.hrm_models import AuthUser, Employee
from app.models.crw_models import CRWTarget

def seed_data():
    # Make sure tables exist
    Base.metadata.create_all(bind=engine)
    
    db: Session = SessionLocal()
    
    try:
        # 1. Create ADMIN user
        admin_user = db.query(AuthUser).filter(AuthUser.username == "admin").first()
        if not admin_user:
            admin_user = AuthUser(
                username="admin",
                password=get_password_hash("admin123"),
                is_staff=True,
                is_superuser=True,
                date_joined=datetime.now(),
                is_active=True
            )
            db.add(admin_user)
            db.flush() # Get ID
            
            # Add Admin Employee Profile
            admin_emp = Employee(
                user_id=admin_user.id,
                emp_code="ADM-001",
                full_name="Quản Trị Viên (HR)",
                department="HR Dept",
                role="HR Admin",
                join_date=datetime.now().date()
            )
            db.add(admin_emp)
            print("Admin user created: admin / admin123")
        
        # 2. Create Regular USER (New Hire)
        test_user = db.query(AuthUser).filter(AuthUser.username == "user").first()
        if not test_user:
            test_user = AuthUser(
                username="user",
                password=get_password_hash("user123"),
                is_staff=False,
                is_superuser=False,
                date_joined=datetime.now(),
                is_active=True
            )
            db.add(test_user)
            db.flush()
            
            # Add User Employee Profile
            user_emp = Employee(
                user_id=test_user.id,
                emp_code="EMP-2026-001",
                full_name="Minh Trần",
                department="Sản xuất",
                role="Operator",
                join_date=datetime.now().date()
            )
            db.add(user_emp)
            print("Regular user created: user / user123")

        # 3. Create Mentors/Connectors (to search)
        mentors = [
            ("MNT-001", "Nguyễn Văn A", "Leader", "Sản xuất"),
            ("MNT-002", "Lê Văn B", "Part Leader", "Kỹ thuật"),
            ("MNT-003", "Trần Thị C", "Team Manager", "Sản xuất"),
            ("MNT-004", "Phạm Văn D", "GD", "Giám Đốc"),
        ]
        
        for code, name, role, dept in mentors:
            if not db.query(Employee).filter(Employee.emp_code == code).first():
                emp = Employee(
                    emp_code=code,
                    full_name=name,
                    role=role,
                    department=dept,
                    join_date=datetime(2025, 1, 1).date()
                )
                db.add(emp)
        
        # 4. Initial Target for Month
        period = datetime.now().strftime("%Y-%m")
        if not db.query(CRWTarget).filter(CRWTarget.period_str == period).first():
            target = CRWTarget(
                period_str=period,
                operator_required=5,
                leader_required=2,
                pl_required=1,
                tm_required=1,
                gd_required=0,
                reward_amount=500000.0
            )
            db.add(target)

        db.commit()
        print("Seeding completed successfully!")
        
    except Exception as e:
        db.rollback()
        print(f"Error seeding data: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_data()

from sqlalchemy import text
from app.core.database import SessionLocal

def delete_test_who():
    db = SessionLocal()
    try:
        # Check users
        result = db.execute(text("SELECT id, username FROM csb_employee_refs WHERE username = 'test_who'"))
        users = result.fetchall()
        
        test_user_ids = [str(u.id) for u in users]
        
        if test_user_ids:
            for uid in test_user_ids:
                print(f"Deleting test_who with id {uid}...")
                db.execute(text(f"DELETE FROM csb_audit_logs WHERE record_id = '{uid}' OR changed_by_ref_id = '{uid}'"))
                db.execute(text(f"DELETE FROM crw_connections WHERE new_hire_id = '{uid}' OR connector_id = '{uid}'"))
                db.execute(text(f"DELETE FROM crw_rewards WHERE employee_id = '{uid}' OR approved_by_ref_id = '{uid}'"))
                db.execute(text(f"DELETE FROM csb_employee_refs WHERE id = '{uid}'"))
            db.commit()
            print("Successfully deleted test_who.")
        else:
            print("test_who not found.")
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == '__main__':
    delete_test_who()

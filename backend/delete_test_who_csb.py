import asyncio
from sqlalchemy import text
from app.core.database import SessionLocal

async def delete_test_who():
    db = SessionLocal()
    try:
        # Check users
        result = await db.execute(text("SELECT id, username, full_name, emp_code FROM csb_employee_refs WHERE username ILIKE '%test%' OR username ILIKE '%who%' OR full_name ILIKE '%Test Who%'"))
        users = result.fetchall()
        for u in users:
            print(f"Found user: {u.username} (ID: {u.id}, Name: {u.full_name}, Code: {u.emp_code})")
            
        test_user_ids = [str(u.id) for u in users if 'test' in u.username.lower() or 'who' in u.username.lower()]
        
        if test_user_ids:
            for uid in test_user_ids:
                print(f"Deleting data for {uid}...")
                await db.execute(text(f"DELETE FROM crw_connections WHERE new_hire_id = '{uid}' OR connector_id = '{uid}'"))
                await db.execute(text(f"DELETE FROM crw_rewards WHERE employee_id = '{uid}' OR approved_by_ref_id = '{uid}'"))
                await db.execute(text(f"DELETE FROM csb_employee_refs WHERE id = '{uid}'"))
            await db.commit()
            print("Successfully deleted test user(s) from CSB DB.")
        else:
            print("No test user found to delete.")
    except Exception as e:
        print(f"Error: {e}")
        await db.rollback()
    finally:
        await db.close()

if __name__ == '__main__':
    asyncio.run(delete_test_who())

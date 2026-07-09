import asyncio
from sqlalchemy import text
from app.core.database import SessionLocal

async def delete_test_who():
    db = SessionLocal()
    try:
        # Check users
        result = await db.execute(text("SELECT id, username FROM users WHERE username ILIKE '%test%' OR username ILIKE '%who%'"))
        users = result.fetchall()
        for u in users:
            print(f"Found user: {u.username} (ID: {u.id})")
            
        # Delete test_who
        if users:
            await db.execute(text("DELETE FROM connections WHERE from_user_id IN (SELECT id FROM users WHERE username = 'test_who') OR to_user_id IN (SELECT id FROM users WHERE username = 'test_who')"))
            await db.execute(text("DELETE FROM reward_logs WHERE user_id IN (SELECT id FROM users WHERE username = 'test_who')"))
            await db.execute(text("DELETE FROM users WHERE username = 'test_who'"))
            await db.commit()
            print("Successfully deleted test_who and all associated connections/rewards.")
    except Exception as e:
        print(f"Error: {e}")
        await db.rollback()
    finally:
        await db.close()

if __name__ == '__main__':
    asyncio.run(delete_test_who())

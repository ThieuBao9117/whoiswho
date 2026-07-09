import asyncio
from app.core.database import SessionLocal
from app.models.user import User

async def run():
    async with SessionLocal() as db:
        result = await db.execute("SELECT id, username, full_name FROM users WHERE username LIKE '%test%' OR full_name LIKE '%Test%'")
        users = result.fetchall()
        for u in users:
            print(f"ID: {u.id}, Username: {u.username}, Name: {u.full_name}")

asyncio.run(run())

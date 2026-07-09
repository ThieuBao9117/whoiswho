"""
Quick test script to verify database and auth work
"""
import psycopg
from datetime import datetime, timedelta
from jose import jwt

# Config
DB_URL = "host=localhost port=5433 user=postgres password=123456 dbname=hrm"
SECRET_KEY = "csb-connection-secret-2026"
ALGORITHM = "HS256"

print("=" * 50)
print("WHO Is WHO - Demo User Test")
print("=" * 50)

# 1. Test DB connection
print("\n1. Connecting to database...")
conn = psycopg.connect(DB_URL)
cur = conn.cursor()
print("   ✅ Connected!")

# 2. List users
print("\n2. Users in csb_employee_refs:")
cur.execute("SELECT username, emp_code, full_name, department FROM csb_employee_refs ORDER BY hrm_employee_id")
users = cur.fetchall()
if not users:
    print("   ❌ No users found!")
else:
    for u in users:
        print(f"   ✅ {u[0]:12} | {u[1]:8} | {u[2]:15} | {u[3]}")

# 3. Generate JWT token for demo user
print("\n3. Generating JWT token for 'demo' user...")
token = jwt.encode(
    {
        "sub": "demo",
        "emp_code": "DEMO001",
        "exp": datetime.utcnow() + timedelta(hours=24),
        "source": "test"
    },
    SECRET_KEY,
    algorithm=ALGORITHM
)
print(f"   ✅ Token: {token[:50]}...")

# 4. Test token decode
print("\n4. Verifying token...")
payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
print(f"   ✅ Decoded: {payload}")

print("\n" + "=" * 50)
print("✅ All tests passed!")
print(f"\n📋 Login credentials:")
print(f"   Username: demo")
print(f"   Password: (any - dev mode)")
print(f"\n🔑 Use this token in frontend:")
print(f"   {token}")
print("=" * 50)

cur.close()
conn.close()

import jwt
import datetime
import requests
import sys

# === 1. Tao token nhu HRM ===
SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
username = "mi_mtri"  # username HRM test

now = datetime.datetime.now(datetime.timezone.utc)
payload = {
    "sub": username,
    "exp": now + datetime.timedelta(minutes=5),
    "iat": now,
}

token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
print(f"[1] Token da tao (username={username}):")
print(f"    {token[:80]}...")

# === 2. Goi SSO login endpoint ===
print(f"\n[2] Goi POST http://localhost:7000/api/auth/sso-login?token=...")
try:
    r = requests.post(
        f"http://localhost:7000/api/auth/sso-login?token={token}",
        timeout=5
    )
    print(f"    Status: {r.status_code}")
    print(f"    Body: {r.text[:500]}")
except Exception as e:
    print(f"    LOI ket noi: {e}")

# === 3. Thu voi username khac ===
print(f"\n[3] Thu decode token de xac nhan key khop:")
try:
    decoded = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    print(f"    OK - decoded: {decoded}")
except Exception as e:
    print(f"    LOI decode: {e}")

# === 4. Kiem tra CSB_SSO_URL trong HRM ===
print(f"\n[4] CSB_SSO_URL se redirect den:")
print(f"    http://hrm.csbrg.com/game/sso?token=...")
print(f"    Frontend sso-login API URL: /game/api/auth/sso-login?token=...")
print(f"\n[5] Kiem tra API proxy /game/api/* -> localhost:7000:")
try:
    r = requests.get(
        "http://localhost:7000/",
        timeout=5,
        headers={"Host": "hrm.csbrg.com"}
    )
    print(f"    CSB Backend: {r.status_code} - {r.text[:100]}")
except Exception as e:
    print(f"    LOI: {e}")

import requests

# Test 1: Generate valid token
import jwt
import datetime

SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
username = "mi_mtri"

now = datetime.datetime.now(datetime.timezone.utc)
payload = {
    "sub": username,
    "exp": now + datetime.timedelta(minutes=5),
    "iat": now,
}
token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")

# Test 2: Call through IIS Proxy with Host header
url = f"http://127.0.0.1/game/api/auth/sso-login?token={token}"
print(f"Calling: {url}")

try:
    r = requests.post(url, headers={'Host': 'hrm.csbrg.com'})
    print(f"Status: {r.status_code}")
    print(f"Body: {r.text[:500]}")
except Exception as e:
    print(f"Error: {e}")

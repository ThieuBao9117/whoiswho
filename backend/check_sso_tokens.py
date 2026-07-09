import base64, json
from dotenv import load_dotenv
load_dotenv()

# Decode tokens from actual SSO log
tokens = [
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJtaV9tdHJpIiwiZXhwIjoxNzc5MjYzMTA2LCJpYXQiOjE3NzkyNjI4MDZ9.01yvBH0CBm3rvlwb6lA2Ve7BvceqTewIXdKUqP--xIY",
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJBU1NFTV9CVkxhbSIsImV4cCI6MTc3OTI1NzQ4NiwiaWF0IjoxNzc5MjU3MTg2fQ.apZm8lZLl_uZWVwD3yVXJnLNAAzuW7DQPEYv8E7P7ug",
]

print("=== Token usernames ===")
for token in tokens:
    payload_b64 = token.split('.')[1]
    payload_b64 += '=' * (4 - len(payload_b64) % 4)
    payload = json.loads(base64.b64decode(payload_b64))
    print(f"  sub = {payload['sub']}")

import sys; sys.path.insert(0, '.')
from app.core.config import settings
print(f"\nBackend SECRET_KEY: {settings.SECRET_KEY}")

from jose import jwt as jose_jwt
print("\n=== Token signature validation ===")
for token in tokens:
    try:
        decoded = jose_jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"], options={"verify_exp": False})
        print(f"  VALID - sub={decoded['sub']}")
    except Exception as e:
        print(f"  INVALID - {e}")

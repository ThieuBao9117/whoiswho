import requests

# Test SSO login
token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0IiwiZXhwIjoxNzc5Mjg4MjU2LCJpYXQiOjE3NzkyODQ5NTZ9.GwPQ5wPgMFO5jCNP-5v6h8H9W7wH6yK1qG7X8Y9Z0A"

try:
    r = requests.post(f"http://localhost:7000/api/auth/sso-login?token={token}")
    print(f"Status: {r.status_code}")
    print(f"Response: {r.text}")
except Exception as e:
    print(f"Error: {e}")
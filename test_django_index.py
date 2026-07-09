import requests

try:
    r = requests.get('http://localhost:8000/accounts/login/')
    print(f"Status: {r.status_code}")
    print(f"Length: {len(r.text)}")
except Exception as e:
    print(e)

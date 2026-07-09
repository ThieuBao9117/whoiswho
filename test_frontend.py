import requests

try:
    r = requests.get('http://127.0.0.1/game/', headers={'Host': 'hrm.csbrg.com'}, timeout=5)
    print(f"Frontend Status: {r.status_code}")
    print(f"Frontend Body Snippet: {r.text[:200]}")
except Exception as e:
    print(e)

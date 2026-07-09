import requests

try:
    # Disable redirect to capture Location header
    r = requests.get('http://localhost:8000/go-to-csb/', allow_redirects=False)
    print(f"Status: {r.status_code}")
    print(f"Location: {r.headers.get('Location', 'None')}")
except Exception as e:
    print(e)

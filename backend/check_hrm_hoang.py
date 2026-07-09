import requests
import json
import codecs
import sys
sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())

HRM_BASE   = "http://hrm.csbrg.com"
HRM_USER   = "mi_mtri"
HRM_PASS   = "@Dmin123#$"

# Login
resp = requests.post(f"{HRM_BASE}/accounts/api/login/", json={"username": HRM_USER, "password": HRM_PASS})
token = resp.json().get("access")
headers = {"Authorization": f"Bearer {token}"}

# Query employee
resp = requests.get(f"{HRM_BASE}/accounts/api/employees/", params={"search": "Hoang"}, headers=headers)
print(json.dumps(resp.json(), ensure_ascii=False))

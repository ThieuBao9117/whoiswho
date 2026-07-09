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

# Query employee by username MI_MHHoang
resp = requests.get(f"{HRM_BASE}/accounts/api/employees/", params={"username": "MI_MHHoang"}, headers=headers)
print("Searching for MI_MHHoang:", json.dumps(resp.json(), ensure_ascii=False))

# Let's also check MI_MHHoang by full name search
resp = requests.get(f"{HRM_BASE}/accounts/api/employees/", params={"search": "MI_MHHoang"}, headers=headers)
print("Searching for MI_MHHoang by search param:", json.dumps(resp.json(), ensure_ascii=False))

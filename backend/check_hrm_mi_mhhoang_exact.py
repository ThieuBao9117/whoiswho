import requests

HRM_BASE   = "http://hrm.csbrg.com"
HRM_USER   = "mi_mtri"
HRM_PASS   = "@Dmin123#$"

# Login
resp = requests.post(f"{HRM_BASE}/accounts/api/login/", json={"username": HRM_USER, "password": HRM_PASS})
token = resp.json().get("access")
headers = {"Authorization": f"Bearer {token}"}

# Query employee by username MI_MHHoang
resp = requests.get(f"{HRM_BASE}/accounts/api/employees/", params={"username": "MI_MHHoang"}, headers=headers)
data = resp.json()
if isinstance(data, dict) and "results" in data:
    data = data["results"]

found = [e for e in data if e.get("username") == "MI_MHHoang"]
if found:
    print("Found MI_MHHoang:", found[0])
else:
    print("Not found MI_MHHoang in HRM!")
    print("Total records returned by HRM for username=MI_MHHoang:", len(data))

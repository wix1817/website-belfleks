import requests
import json

PB_URL = "http://127.0.0.1:8090"
ADMIN_EMAIL = "admin@bflex.by"
ADMIN_PASS = "AdminPassword123!"

res = requests.post(f"{PB_URL}/api/collections/_superusers/auth-with-password", json={
    "identity": ADMIN_EMAIL,
    "password": ADMIN_PASS
})
token = res.json()["token"]

res = requests.get(f"{PB_URL}/api/collections/categories", headers={"Authorization": f"Bearer {token}"})
print(json.dumps(res.json(), indent=2))

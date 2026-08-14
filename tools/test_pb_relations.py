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
headers = {"Authorization": f"Bearer {token}"}

test_coll = {
    "name": "test_relations",
    "type": "base",
    "fields": [
        {"name": "rel", "type": "relation", "collectionId": "pbc_3912384153", "maxSelect": 1},
        {"name": "file", "type": "file", "maxSelect": 1, "mimeTypes": ["image/jpeg"]}
    ]
}

res = requests.post(f"{PB_URL}/api/collections", json=test_coll, headers=headers)
print("Status:", res.status_code)
if res.status_code >= 400:
    print(res.text)
else:
    print(json.dumps(res.json(), indent=2))

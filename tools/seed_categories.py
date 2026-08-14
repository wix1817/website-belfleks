import requests

PB_URL = "http://127.0.0.1:8090"
ADMIN_EMAIL = "admin@bflex.by"
ADMIN_PASS = "AdminPassword123!"

def login():
    res = requests.post(f"{PB_URL}/api/collections/_superusers/auth-with-password", json={
        "identity": ADMIN_EMAIL,
        "password": ADMIN_PASS
    })
    return res.json()["token"]

def main():
    token = login()
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    categories = [
        {"name": "Промышленные рукава", "slug": "promyshlennye-rukava", "sort_order": 10},
        {"name": "Рукава высокого давления", "slug": "rukava-vysokogo-davleniya", "sort_order": 20},
        {"name": "Воздуховоды", "slug": "vozduhovody", "sort_order": 30},
        {"name": "Композитные рукава", "slug": "kompozitnye-rukava", "sort_order": 40},
        {"name": "Соединения", "slug": "soedineniya", "sort_order": 50},
        {"name": "Зажимы", "slug": "zazhimy", "sort_order": 60},
        {"name": "Аксессуары", "slug": "aksessuary", "sort_order": 70},
    ]

    prom_rukava_id = None

    for cat in categories:
        res = requests.post(f"{PB_URL}/api/collections/categories/records", headers=headers, json={
            "name": cat["name"],
            "slug": cat["slug"],
            "sort_order": cat["sort_order"],
            "is_active": True
        })
        if res.status_code == 200:
            print(f"Created category {cat['name']}")
            if cat["name"] == "Промышленные рукава":
                prom_rukava_id = res.json()["id"]
        else:
            print(f"Error creating {cat['name']}: {res.text}")

    if prom_rukava_id:
        subcats = [
            {"name": "Вода", "slug": "voda", "sort_order": 1},
            {"name": "Воздух", "slug": "vozduh", "sort_order": 2},
            {"name": "Пар", "slug": "par", "sort_order": 3},
            {"name": "Химстойкие", "slug": "himstoykie", "sort_order": 4},
            {"name": "Абразивостойкие", "slug": "abrazivostoykie", "sort_order": 5},
            {"name": "Пищевые", "slug": "pischevye", "sort_order": 6},
        ]
        
        for sub in subcats:
            res = requests.post(f"{PB_URL}/api/collections/categories/records", headers=headers, json={
                "name": sub["name"],
                "slug": sub["slug"],
                "parent": prom_rukava_id,
                "sort_order": sub["sort_order"],
                "is_active": True
            })
            if res.status_code == 200:
                print(f"Created subcategory {sub['name']}")
            else:
                print(f"Error creating subcat {sub['name']}: {res.text}")

    print("Category seed done.")

if __name__ == '__main__':
    main()

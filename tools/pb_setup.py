import requests
import json
import time

PB_URL = "http://127.0.0.1:8090"
ADMIN_EMAIL = "admin@bflex.by"
ADMIN_PASS = "AdminPassword123!"

def login():
    try:
        res = requests.post(f"{PB_URL}/api/collections/_superusers/auth-with-password", json={
            "identity": ADMIN_EMAIL,
            "password": ADMIN_PASS
        })
        res.raise_for_status()
        return res.json()["token"]
    except requests.exceptions.RequestException as e:
        print("Initial login failed, trying to create first admin...")
        # If no admin exists, we need to create one. PocketBase allows creating the first admin without auth
        # Actually, in v0.23, first admin is created during startup if we pass --admin="email:pass" or via UI.
        # But assuming admin exists because Docker container is running and I might have created it manually, or the user did.
        # Wait, if I delete pb_data, the admin is deleted!
        # How to create the first admin in PB 0.23 via API?
        # POST /api/admins -> wait, admins are now in `_superusers` collection in v0.23!
        # POST /api/collections/_superusers/records
        # Let's try that if login fails.
        res = requests.post(f"{PB_URL}/api/collections/_superusers/records", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASS,
            "passwordConfirm": ADMIN_PASS
        })
        if res.status_code >= 400:
            print("Failed to create superuser:", res.text)
        res.raise_for_status()
        
        # Now login again
        res = requests.post(f"{PB_URL}/api/collections/_superusers/auth-with-password", json={
            "identity": ADMIN_EMAIL,
            "password": ADMIN_PASS
        })
        res.raise_for_status()
        return res.json()["token"]

def create_collection(token, data):
    headers = {"Authorization": f"Bearer {token}"}
    res = requests.get(f"{PB_URL}/api/collections/{data['name']}", headers=headers)
    if res.status_code == 200:
        print(f"Collection {data['name']} already exists. Updating...")
        # PocketBase API requires ID to update
        col_id = res.json()["id"]
        res = requests.patch(f"{PB_URL}/api/collections/{col_id}", json=data, headers=headers)
    else:
        print(f"Creating collection {data['name']}...")
        res = requests.post(f"{PB_URL}/api/collections", json=data, headers=headers)
    
    if res.status_code >= 400:
        print(f"Error for {data['name']}:", res.text)
    res.raise_for_status()
    return res.json()

def main():
    # Wait for PocketBase to start
    for _ in range(10):
        try:
            requests.get(f"{PB_URL}/api/health")
            break
        except:
            time.sleep(1)
            
    token = login()
    print("Logged in successfully.")
    
    # 1. Categories
    categories = {
        "name": "categories",
        "type": "base",
        "system": False,
        "fields": [
            {"name": "name", "type": "text", "required": True},
            {"name": "slug", "type": "text", "required": True},
            {"name": "description", "type": "editor"},
            {"name": "image", "type": "file", "maxSelect": 1, "mimeTypes": ["image/jpeg", "image/png", "image/svg+xml", "image/webp"]},
            {"name": "sort_order", "type": "number"},
            {"name": "meta_title", "type": "text"},
            {"name": "meta_description", "type": "text"},
            {"name": "is_active", "type": "bool"}
        ],
        "listRule": "",
        "viewRule": ""
    }
    cat_res = create_collection(token, categories)
    
    # Update categories to add parent relation
    categories["fields"].append({
        "name": "parent", "type": "relation", "collectionId": cat_res["id"], "maxSelect": 1
    })
    create_collection(token, categories)

    # 2. Products
    products = {
        "name": "products",
        "type": "base",
        "system": False,
        "fields": [
            {"name": "name", "type": "text", "required": True},
            {"name": "slug", "type": "text", "required": True},
            {"name": "category", "type": "relation", "collectionId": cat_res["id"], "maxSelect": 1},
            {"name": "tags", "type": "json"}, # Array of strings
            {"name": "description", "type": "editor"},
            {"name": "short_description", "type": "text"},
            {"name": "images", "type": "file", "maxSelect": 10, "mimeTypes": ["image/jpeg", "image/png", "image/webp"]},
            {"name": "specifications", "type": "json"},
            {"name": "diameter_table", "type": "json"},
            {"name": "applications", "type": "json"},
            {"name": "features", "type": "json"},
            {"name": "pdf_brochure", "type": "file", "maxSelect": 1, "mimeTypes": ["application/pdf"]},
            {"name": "meta_title", "type": "text"},
            {"name": "meta_description", "type": "text"},
            {"name": "faq", "type": "json"},
            {"name": "is_active", "type": "bool"},
            {"name": "is_featured", "type": "bool"},
            {"name": "sort_order", "type": "number"}
        ],
        "listRule": "",
        "viewRule": ""
    }
    prod_res = create_collection(token, products)
    
    # Update products with self-relations
    products["fields"].extend([
        {"name": "upsell", "type": "relation", "collectionId": prod_res["id"], "maxSelect": 10},
        {"name": "crossell", "type": "relation", "collectionId": prod_res["id"], "maxSelect": 10}
    ])
    create_collection(token, products)

    # 3. Documents
    documents = {
        "name": "documents",
        "type": "base",
        "system": False,
        "fields": [
            {"name": "title", "type": "text", "required": True},
            {"name": "file", "type": "file", "required": True, "maxSelect": 1, "mimeTypes": ["application/pdf"]},
            {"name": "category", "type": "select", "maxSelect": 1, "values": ["Сертификат", "Техническая документация", "Прайс", "Презентация"]},
            {"name": "description", "type": "text"},
            {"name": "date", "type": "date"}
        ],
        "listRule": "",
        "viewRule": ""
    }
    create_collection(token, documents)

    # 4. Chemical Resistance
    chem = {
        "name": "chemical_resistance",
        "type": "base",
        "system": False,
        "fields": [
            {"name": "chemical", "type": "text", "required": True},
            {"name": "resistance_data", "type": "json"},
            {"name": "notes", "type": "text"}
        ],
        "listRule": "",
        "viewRule": ""
    }
    create_collection(token, chem)

    # 5. Pages
    pages = {
        "name": "pages",
        "type": "base",
        "system": False,
        "fields": [
            {"name": "title", "type": "text", "required": True},
            {"name": "slug", "type": "text", "required": True},
            {"name": "content", "type": "editor"},
            {"name": "meta_title", "type": "text"},
            {"name": "meta_description", "type": "text"},
            {"name": "hero_title", "type": "text"},
            {"name": "hero_subtitle", "type": "text"},
            {"name": "is_active", "type": "bool"}
        ],
        "listRule": "",
        "viewRule": ""
    }
    create_collection(token, pages)

    # 6. News
    news = {
        "name": "news",
        "type": "base",
        "system": False,
        "fields": [
            {"name": "title", "type": "text", "required": True},
            {"name": "slug", "type": "text", "required": True},
            {"name": "excerpt", "type": "text"},
            {"name": "content", "type": "editor"},
            {"name": "image", "type": "file", "maxSelect": 1, "mimeTypes": ["image/jpeg", "image/png", "image/webp"]},
            {"name": "published_date", "type": "date"},
            {"name": "meta_title", "type": "text"},
            {"name": "meta_description", "type": "text"},
            {"name": "is_published", "type": "bool"}
        ],
        "listRule": "",
        "viewRule": ""
    }
    create_collection(token, news)

    # 7. Contacts
    contacts = {
        "name": "contacts",
        "type": "base",
        "system": False,
        "fields": [
            {"name": "name", "type": "text"},
            {"name": "company", "type": "text"},
            {"name": "phone", "type": "text"},
            {"name": "email", "type": "email"},
            {"name": "message", "type": "text"},
            {"name": "product", "type": "relation", "collectionId": prod_res["id"], "maxSelect": 1},
            {"name": "source", "type": "text"}
        ],
        "listRule": "",
        "createRule": ""
    }
    create_collection(token, contacts)

    # 8. Site Settings
    site_settings = {
        "name": "site_settings",
        "type": "base",
        "system": False,
        "fields": [
            {"name": "site_name", "type": "text"},
            {"name": "site_description", "type": "text"},
            {"name": "phone_main", "type": "text"},
            {"name": "phone_secondary", "type": "text"},
            {"name": "email", "type": "email"},
            {"name": "address", "type": "text"},
            {"name": "working_hours", "type": "text"},
            {"name": "telegram_link", "type": "url"},
            {"name": "viber_link", "type": "url"},
            {"name": "crm_embed_code", "type": "text"},
            {"name": "analytics_code", "type": "text"},
            {"name": "footer_text", "type": "editor"},
            {"name": "logo_square", "type": "file", "maxSelect": 1, "mimeTypes": ["image/svg+xml"]},
            {"name": "logo_full", "type": "file", "maxSelect": 1, "mimeTypes": ["image/svg+xml"]},
            {"name": "favicon", "type": "file", "maxSelect": 1, "mimeTypes": ["image/svg+xml", "image/x-icon", "image/png"]}
        ],
        "listRule": "",
        "viewRule": ""
    }
    create_collection(token, site_settings)

    # 9. Manufacturers
    manufacturers = {
        "name": "manufacturers",
        "type": "base",
        "system": False,
        "fields": [
            {"name": "name", "type": "text", "required": True},
            {"name": "logo", "type": "file", "maxSelect": 1, "mimeTypes": ["image/jpeg", "image/png", "image/svg+xml", "image/webp"]},
            {"name": "sort_order", "type": "number"},
            {"name": "is_active", "type": "bool"}
        ],
        "listRule": "",
        "viewRule": ""
    }
    create_collection(token, manufacturers)
    
    print("All collections created successfully!")

if __name__ == "__main__":
    main()

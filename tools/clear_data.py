import requests

# Delete products
print("Deleting products...")
res = requests.get('http://127.0.0.1:8090/api/collections/products/records?perPage=500').json()
for r in res.get('items', []):
    requests.delete(f'http://127.0.0.1:8090/api/collections/products/records/{r["id"]}')
    
# Delete categories
print("Deleting categories...")
res = requests.get('http://127.0.0.1:8090/api/collections/categories/records?perPage=500').json()
for r in res.get('items', []):
    requests.delete(f'http://127.0.0.1:8090/api/collections/categories/records/{r["id"]}')

print("Done")

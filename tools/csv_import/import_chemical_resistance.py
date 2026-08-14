import csv
import requests
import sys

PB_URL = "http://127.0.0.1:8090"
ADMIN_EMAIL = "admin@bflex.by"
ADMIN_PASS = "AdminPassword123!"

def login():
    res = requests.post(f"{PB_URL}/api/collections/_superusers/auth-with-password", json={
        "identity": ADMIN_EMAIL,
        "password": ADMIN_PASS
    })
    res.raise_for_status()
    return res.json()["token"]

def main():
    if len(sys.argv) < 2:
        print("Usage: python import_chemical_resistance.py <path_to_csv>")
        sys.exit(1)
        
    csv_path = sys.argv[1]
    
    token = login()
    headers = {"Authorization": f"Bearer {token}"}
    
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        header_row = next(reader)
        materials = header_row[1:]
        
        count = 0
        for row in reader:
            if not row or not row[0].strip():
                continue
            chemical = row[0].strip()
            resistance_data = {}
            for i, material in enumerate(materials):
                val = row[i+1] if i+1 < len(row) else ""
                val = val.strip()
                if val:
                    resistance_data[material.strip()] = val
                    
            data = {
                "chemical": chemical,
                "resistance_data": resistance_data,
                "notes": ""
            }
            
            res = requests.post(f"{PB_URL}/api/collections/chemical_resistance/records", json=data, headers=headers)
            if res.status_code >= 400:
                print(f"Failed to insert {chemical}: {res.text}")
            else:
                count += 1
                
        print(f"Successfully inserted {count} records.")

if __name__ == '__main__':
    main()

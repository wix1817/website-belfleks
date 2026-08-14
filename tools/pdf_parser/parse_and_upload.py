import os
import fitz # PyMuPDF
import pdfplumber
import requests
import json
import re

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

def clean_text(text):
    return re.sub(r'\s+', ' ', text).strip()

def parse_pdf(filepath):
    data = {
        "name": "",
        "tags": [],
        "description": "",
        "specifications": {},
        "diameter_table": [],
        "images": []
    }
    
    with pdfplumber.open(filepath) as pdf:
        # Extract images from PyMuPDF
        doc = fitz.open(filepath)
        page = doc[0]
        # In actual implementation, we would extract images and save them.
        
        # Extract text with layout
        text = pdf.pages[0].extract_text(layout=True)
        lines = text.split("\n")
        
        # Remove header and footer
        content_lines = []
        for line in lines:
            # Skip footer
            if "доступны иные размеры" in line.lower() or "р/с by02" in line.lower():
                break
            # Skip header
            if "г. гродно" in line.lower() or "www.belfleks.by" in line.lower() or "тел." in line.lower():
                continue
            content_lines.append(line)
            
        # Parse sections
        title_lines = []
        desc_lines = []
        tags = []
        specs_lines = []
        
        state = "title"
        for line in content_lines:
            line_stripped = line.strip()
            if not line_stripped:
                continue
                
            if state == "title":
                if "Устойчивость" in line or ("," in line and not line_stripped.endswith(":")):
                    tags.extend([t.strip() for t in line_stripped.split(",") if t.strip()])
                    state = "desc"
                elif "Технические" in line and "характеристики" in line:
                    state = "specs"
                else:
                    if len(line_stripped) > 5:
                        title_lines.append(line_stripped)
            elif state == "desc":
                if "Технические" in line and "характеристики" in line:
                    state = "specs"
                else:
                    desc_lines.append(line_stripped)
            elif state == "specs":
                if "Внутр. Ø" in line or "Наружн. Ø" in line:
                    state = "table"
                    break # Rest is table handled by pdfplumber table extraction
                else:
                    specs_lines.append(line)
                    
        # Parse title and tags
        data["name"] = clean_text(" ".join(title_lines))
        # Sometimes tags are inside title if no comma
        if not tags and title_lines:
            # Try to infer tags if any
            pass
            
        data["tags"] = tags
        data["description"] = clean_text(" ".join(desc_lines))
        
        # Parse specs (column layout)
        # Using re.split(r' {3,}', line) to separate columns
        col_keys = []
        col_values = []
        active_col_indices = []
        
        for line in specs_lines:
            parts = [p.strip() for p in re.split(r' {4,}', line.strip()) if p.strip()]
            if not parts:
                continue
            is_key_row = all(p.endswith(":") for p in parts)
            if is_key_row:
                active_col_indices = []
                for p in parts:
                    col_keys.append(p.replace(":", ""))
                    col_values.append([])
                    active_col_indices.append(len(col_keys) - 1)
            else:
                parts_spaced = [p.strip() for p in re.split(r' {4,}', line) if p.strip()]
                for i, p in enumerate(parts_spaced):
                    if i < len(active_col_indices):
                        col_idx = active_col_indices[i]
                        col_values[col_idx].append(p)
                        
        for i, key in enumerate(col_keys):
            if i < len(col_values):
                data["specifications"][key] = clean_text(" ".join(col_values[i]))
                
        # Parse table directly from layout text
        table_lines = []
        in_table = False
        for line in content_lines:
            if "Внутр. Ø" in line or "Наружн. Ø" in line:
                in_table = True
            
            if in_table:
                if line.strip():
                    table_lines.append(line.strip())
                    
        if table_lines:
            # We have header lines and data lines
            # Typically 2 lines of header. Data lines start with numbers.
            data_started = False
            headers = ["Внутр. Ø (мм)", "Наружн. Ø (мм)", "Рабочее давление (бар)", "Разрывное давление (бар)", "Радиус изгиба (мм)", "Длина бухты (м)", "Вес (кг/м)"]
            
            for line in table_lines:
                # Is data line? usually starts with digits
                if re.match(r'^\d', line):
                    data_started = True
                    # Split by 2+ spaces
                    parts = [p.strip() for p in re.split(r' {2,}', line) if p.strip()]
                    row_data = {}
                    for i, p in enumerate(parts):
                        if i < len(headers):
                            row_data[headers[i]] = p
                    if row_data:
                        data["diameter_table"].append(row_data)
                            
    return data

def generate_html_table(diameter_table):
    if not diameter_table:
        return ""
        
    headers = list(diameter_table[0].keys())
    
    html = '<div class="overflow-x-auto my-6">\n'
    html += '  <table class="w-full text-sm text-left text-gray-500 border border-gray-200">\n'
    html += '    <thead class="text-xs text-gray-700 uppercase bg-gray-50">\n'
    html += '      <tr>\n'
    for h in headers:
        html += f'        <th scope="col" class="px-4 py-3 border-b">{h}</th>\n'
    html += '      </tr>\n'
    html += '    </thead>\n'
    html += '    <tbody>\n'
    
    for row in diameter_table:
        html += '      <tr class="bg-white border-b hover:bg-gray-50">\n'
        for h in headers:
            val = row.get(h, "")
            html += f'        <td class="px-4 py-2 border-r">{val}</td>\n'
        html += '      </tr>\n'
        
    html += '    </tbody>\n'
    html += '  </table>\n'
    html += '</div>'
    return html

def process_and_upload_all(pdf_dir, token):
    headers = {"Authorization": f"Bearer {token}"}
    
    # Get or create category
    cats_res = requests.get(f"{PB_URL}/api/collections/categories/records", headers=headers)
    cats_res.raise_for_status()
    cats_data = cats_res.json()
    
    cat_id = None
    for c in cats_data.get("items", []):
        if c.get("name") == "Промышленные рукава":
            cat_id = c["id"]
            break
            
    if not cat_id:
        cat_res = requests.post(f"{PB_URL}/api/collections/categories/records", json={
            "name": "Промышленные рукава",
            "slug": "industrial-hoses",
            "is_active": True
        }, headers=headers)
        cat_res.raise_for_status()
        cat_id = cat_res.json()["id"]

    for filename in os.listdir(pdf_dir):
        if not filename.lower().endswith('.pdf'):
            continue
            
        filepath = os.path.join(pdf_dir, filename)
        print(f"Processing {filename}...")
        try:
            data = parse_pdf(filepath)
            
            # Description should only be text description
            md_desc = f"<p>{data['description']}</p>"
                
            # Extract Image
            image_path = None
            doc = fitz.open(filepath)
            for page in doc:
                image_list = page.get_images(full=True)
                if image_list:
                    xref = image_list[0][0]
                    base_image = doc.extract_image(xref)
                    image_bytes = base_image["image"]
                    image_ext = base_image["ext"]
                    image_path = os.path.join(pdf_dir, f"temp_image.{image_ext}")
                    with open(image_path, "wb") as f:
                        f.write(image_bytes)
                    break
                    
            # Upload to PB
            upload_data = {
                "name": data["name"] or filename.replace('.pdf', ''),
                "slug": clean_text(data["name"] or filename.replace('.pdf', '')).lower().replace(' ', '-').replace('/', '-').replace(',', ''),
                "category": cat_id,
                "description": md_desc,
                "specifications": json.dumps(data["specifications"]),
                "diameter_table": json.dumps(data["diameter_table"]),
                "tags": json.dumps(data["tags"]),
                "is_active": True
            }
            
            files = {}
            f_img = None
            if image_path and os.path.exists(image_path):
                f_img = open(image_path, "rb")
                files["images"] = (f"image.{image_ext}", f_img, f"image/{image_ext}")
                
            res = requests.post(
                f"{PB_URL}/api/collections/products/records",
                headers={"Authorization": headers["Authorization"]}, 
                data=upload_data,
                files=files if files else None
            )
            
            if res.status_code not in (200, 201):
                print(f"Failed to upload {filename}: {res.text}")
            else:
                print(f"Successfully uploaded {data['name']}")
                
            if f_img:
                f_img.close()
            if image_path and os.path.exists(image_path):
                os.remove(image_path)
                
        except Exception as e:
            print(f"Error processing {filename}: {e}")

def main():
    token = login()
    pdf_dir = "agent/pdf"
    process_and_upload_all(pdf_dir, token)

if __name__ == '__main__':
    main()

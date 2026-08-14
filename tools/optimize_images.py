import os
from PIL import Image

src_dir = 'agent/img'
dest_dir = 'astro/public/img'

if not os.path.exists(dest_dir):
    os.makedirs(dest_dir)

for filename in os.listdir(src_dir):
    src_path = os.path.join(src_dir, filename)
    if os.path.isfile(src_path):
        try:
            with Image.open(src_path) as img:
                # Convert to RGB if RGBA/P to avoid WebP errors for some modes
                if img.mode in ("RGBA", "P"):
                    img = img.convert("RGB")
                    
                # Resize if width > 1920 (to save space)
                max_width = 1920
                if img.width > max_width:
                    ratio = max_width / img.width
                    new_height = int(img.height * ratio)
                    img = img.resize((max_width, new_height), Image.Resampling.LANCZOS)
                
                name, _ = os.path.splitext(filename)
                dest_path = os.path.join(dest_dir, f"{name}.webp")
                
                img.save(dest_path, "WEBP", quality=85)
                print(f"Optimized: {filename} -> {name}.webp")
        except Exception as e:
            print(f"Failed to process {filename}: {e}")

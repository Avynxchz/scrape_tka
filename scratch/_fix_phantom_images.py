import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TARGET_FILES = [
    os.path.join(ROOT, "data", "bahasa_indonesia_lanjut_paket_2_learning.json"),
    os.path.join(ROOT, "exports", "bahasa_indonesia_lanjut_paket_2_learning.json")
]
IMG_DIR = os.path.join(ROOT, "data", "bahasa_indonesia_lanjut", "paket_2", "images")

for file_path in TARGET_FILES:
    if not os.path.exists(file_path):
        continue
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    removed_count = 0
    for q in data.get("soal", []):
        for field in ["stimulus", "pertanyaan"]:
            obj = q.get(field, {})
            if "images" in obj:
                valid_images = []
                for img in obj["images"]:
                    fn = img.get("filename", "")
                    disk_path = os.path.join(IMG_DIR, fn)
                    if os.path.isfile(disk_path) and os.path.getsize(disk_path) > 0:
                        valid_images.append(img)
                    else:
                        print(f"Removing phantom image from Q{q['nomor']} {field}: {fn}")
                        removed_count += 1
                        # Also clean from HTML if present
                        if "html" in obj and fn:
                            # remove img tag with this fn
                            pattern = rf'<img[^>]*{re.escape(fn)}[^>]*>'
                            obj["html"] = re.sub(pattern, "", obj["html"])
                obj["images"] = valid_images

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"Successfully cleaned {removed_count} phantom images from {os.path.basename(file_path)}")

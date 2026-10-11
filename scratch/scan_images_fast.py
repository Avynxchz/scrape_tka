import os
import json
import glob
import re
import sys

print("Building disk image index...")
disk_images = {}
for root, dirs, files in os.walk("data"):
    for f in files:
        if f.lower().endswith(('.png', '.jpg', '.jpeg', '.svg', '.webp')):
            disk_images.setdefault(f.lower(), []).append(os.path.join(root, f))

print(f"Indexed {len(disk_images)} unique image files on disk.")

json_files = glob.glob("data/*_learning.json")
print(f"Checking {len(json_files)} primary learning JSON files...")

missing = []
total_refs = 0

for jf in json_files:
    fname = os.path.basename(jf)
    try:
        with open(jf, "r", encoding="utf-8") as f:
            data = json.load(f)
        for q in data.get("soal", []):
            q_num = q.get("nomor", "?")
            # extract image filenames
            content_str = json.dumps(q)
            # Find image filenames like \d+_[a-f0-9]+\.png or similar
            matches = set(re.findall(r'([a-zA-Z0-9_\-]+\.(?:png|jpg|jpeg|svg|webp))', content_str, re.IGNORECASE))
            for img in matches:
                total_refs += 1
                img_lower = img.lower()
                if img_lower not in disk_images:
                    missing.append({"json": fname, "q": q_num, "img": img})
    except Exception as e:
        print(f"Error {jf}: {e}")

print(f"\nScan completed:")
print(f"Total image references checked: {total_refs}")
print(f"Total missing: {len(missing)}")

with open("scratch/missing_images_report.json", "w", encoding="utf-8") as out:
    json.dump(missing, out, indent=2)

if missing:
    print("\nMissing images summary (by JSON file):")
    by_file = {}
    for m in missing:
        by_file.setdefault(m["json"], []).append(f"Q{m['q']}: {m['img']}")
    for k, v in by_file.items():
        print(f"  {k} ({len(v)} missing): {', '.join(v[:5])}")
else:
    print("ALL image references in learning JSON files exist on disk!")

import os, json, re, glob
from PIL import Image

DATA_DIR = "data"
SUBJECTS = [
    "kimia", "biologi", "fisika", "matematika", "matematika_lanjut",
    "ekonomi", "geografi", "sosiologi", "antropologi", "sejarah",
    "ppkn", "kewirausahaan", "bahasa_indonesia", "bahasa_indonesia_lanjut",
    "bahasa_inggris", "bahasa_inggris_lanjut", "bahasa_arab",
    "bahasa_jerman", "bahasa_prancis", "bahasa_jepang", "bahasa_korea", "bahasa_mandarin"
]

results = {
    "cross_subject_images": [],
    "flat_math_notations": [],
    "images_missing_transcripts": [],
    "extreme_size_images": []
}

# 1. Check all subjects and packages
for sub in SUBJECTS:
    for pkg in [1, 2]:
        fn = f"{sub}_paket_{pkg}_learning.json"
        fp = os.path.join(DATA_DIR, fn)
        if not os.path.exists(fp):
            continue
        try:
            with open(fp, "r", encoding="utf-8") as f:
                d = json.load(f)
        except Exception as e:
            print(f"Error loading {fp}: {e}")
            continue

        qs = d.get("soal", d) if isinstance(d, dict) else d

        # Load sidecar transcriptions
        sidecar_fp = os.path.join(DATA_DIR, f"{sub}_paket_{pkg}_sidecar_transcriptions.json")
        sidecars = {}
        if os.path.exists(sidecar_fp):
            try:
                with open(sidecar_fp, "r", encoding="utf-8") as sf:
                    sidecars = json.load(sf)
            except Exception:
                pass

        pkg_img_dir = os.path.join(DATA_DIR, sub, f"paket_{pkg}", "images")

        for q in qs:
            qnum = q.get("nomor")
            
            # (a) Check images
            all_imgs = []
            for part in [q.get("stimulus"), q.get("pertanyaan")]:
                if part and part.get("images"):
                    for im in part["images"]:
                        all_imgs.append(im.get("filename") or im.get("rel_path", ""))
                # Also check HTML src
                if part and part.get("html"):
                    for m in re.finditer(r'src=["\']([^"\']+\.(?:png|jpe?g|webp|gif))["\']', part["html"], re.I):
                        fname = m.group(1).split("/")[-1].split("?")[0]
                        all_imgs.append(fname)
            for opt in q.get("pilihan_jawaban", []):
                if opt.get("image"):
                    im = opt["image"]
                    all_imgs.append(im.get("filename") or im.get("rel_path", ""))
                if opt.get("html"):
                    for m in re.finditer(r'src=["\']([^"\']+\.(?:png|jpe?g|webp|gif))["\']', opt["html"], re.I):
                        fname = m.group(1).split("/")[-1].split("?")[0]
                        all_imgs.append(fname)

            # Check if each image exists in package folder or if it's from another subject
            for img_name in set(all_imgs):
                if not img_name:
                    continue
                clean_name = os.path.basename(img_name)
                local_path = os.path.join(pkg_img_dir, clean_name)
                
                # Check cross subject: does it exist locally or only in another subject?
                if not os.path.exists(local_path):
                    # Find where it is
                    found_in = []
                    for other_sub in SUBJECTS:
                        for other_pkg in [1, 2]:
                            other_p = os.path.join(DATA_DIR, other_sub, f"paket_{other_pkg}", "images", clean_name)
                            if os.path.exists(other_p):
                                found_in.append(f"{other_sub}_p{other_pkg}")
                    results["cross_subject_images"].append({
                        "subject": sub, "paket": pkg, "nomor": qnum,
                        "image": clean_name, "found_in": found_in
                    })
                else:
                    # (d) Check image sizes
                    try:
                        with Image.open(local_path) as im:
                            w, h = im.size
                            if w > 900 or h > 700:
                                results["extreme_size_images"].append({
                                    "subject": sub, "paket": pkg, "nomor": qnum,
                                    "image": clean_name, "size": (w, h), "type": "too_large"
                                })
                    except Exception:
                        pass

                # (c) Check AI tutor transcript
                if clean_name not in sidecars and not any(k.endswith(clean_name) for k in sidecars):
                    # Check if it has description inside canonical or q
                    results["images_missing_transcripts"].append({
                        "subject": sub, "paket": pkg, "nomor": qnum, "image": clean_name
                    })

            # (b) Check flat math notations in text & options
            texts_to_check = []
            if q.get("stimulus", {}).get("text"):
                texts_to_check.append(("stimulus", q["stimulus"]["text"]))
            if q.get("pertanyaan", {}).get("text"):
                texts_to_check.append(("pertanyaan", q["pertanyaan"]["text"]))
            for opt in q.get("pilihan_jawaban", []):
                if opt.get("text"):
                    texts_to_check.append((f"opt_{opt.get('key')}", opt["text"]))

            flat_patterns = [
                (r'\b10\s+([2-9]|\d{2})\b', '10 with flat exponent (e.g. 10 24)'),
                (r'\b10\s*[-–]\s*([1-9]|\d{2})\b', '10 with flat negative exponent (e.g. 10 -6)'),
                (r'\b110\s*[-–]\s*6\b', '110 -6 typo for 1x10^-6'),
                (r'\b\d+\s*oC\b', 'oC degree symbol (e.g. 40 oC)'),
                (r'\bsp\s+[23]\b', 'sp 2 or sp 3 flat orbital notation'),
                (r'\brad\.\s*s\s*[-–]\s*2\b', 'rad.s-2 flat unit'),
                (r'\bm\.\s*s\s*[-–]\s*[12]\b', 'm.s-1 flat unit'),
                (r'\bkg\.\s*m\s*[-–]\s*3\b', 'kg.m-3 flat unit')
            ]

            for loc, txt in texts_to_check:
                for pat, label in flat_patterns:
                    matches = re.findall(pat, txt, re.I)
                    if matches:
                        results["flat_math_notations"].append({
                            "subject": sub, "paket": pkg, "nomor": qnum,
                            "location": loc, "label": label, "matches": matches[:3],
                            "snippet": txt[:80]
                        })

# Save results
out_json = "scratch/audit_scan_results.json"
with open(out_json, "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2)

print(f"Scan complete!")
print(f"Cross-subject missing images: {len(results['cross_subject_images'])}")
print(f"Flat math notations: {len(results['flat_math_notations'])}")
print(f"Images missing transcripts: {len(results['images_missing_transcripts'])}")
print(f"Extreme size images: {len(results['extreme_size_images'])}")

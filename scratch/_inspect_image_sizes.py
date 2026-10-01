import glob
import os
from PIL import Image

for pkg in [1, 2]:
    img_dir = f"data/matematika_lanjut/paket_{pkg}/images"
    imgs = sorted(glob.glob(f"{img_dir}/*.*"))
    print(f"\n=== MTK LANJUT PAKET {pkg} IMAGES ({len(imgs)} files) ===")
    for p in imgs:
        try:
            with Image.open(p) as im:
                w, h = im.size
                fn = os.path.basename(p)
                # flag very small or very large
                flag = ""
                if h < 30 or w < 30:
                    flag = "🔍 SANGAT KECIL"
                elif h > 400 or w > 600:
                    flag = "🐘 SANGAT BESAR"
                elif h > 200:
                    flag = "MEDIUM-LARGE"
                print(f"{fn}: {w}x{h} px {flag}")
        except Exception as e:
            print(f"Error {p}: {e}")

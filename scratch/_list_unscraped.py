import sys, os
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, os.path.abspath("."))
import json
from pipeline.subject_catalog import MASTER_CATALOG, get_full_catalog

cat = get_full_catalog()
print(f"Total in MASTER_CATALOG: {len(MASTER_CATALOG)}")

live = [k for k, v in cat['subjects'].items() if v['status'] == 'live']
unscraped = [k for k, v in cat['subjects'].items() if v['status'] != 'live']

print(f"\n🟢 Live Packages ({len(live)}):")
for l in sorted(live):
    print(f"  • {l}")

print(f"\n⏳ Remaining Unscraped Packages ({len(unscraped)}):")
for u in sorted(unscraped):
    item = MASTER_CATALOG[u]
    print(f"  • {u:35s} | Jenis: {item.get('jenis')} | Val: {item.get('val'):4s} | Kat: {item.get('kategori', '')} | Name: {item.get('name')}")

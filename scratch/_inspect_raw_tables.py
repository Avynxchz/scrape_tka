import sys
import re
from bs4 import BeautifulSoup

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

with open("data/raw_html/matematika_lanjut_paket_1.html", encoding="utf-8") as f:
    soup1 = BeautifulSoup(f.read(), "html.parser")

with open("data/raw_html/matematika_lanjut_paket_2.html", encoding="utf-8") as f:
    soup2 = BeautifulSoup(f.read(), "html.parser")

print("=== PAKET 1 EXAM ROOM HTML INSPECTION ===")
for i, table in enumerate(soup1.find_all("table")):
    print(f"\n--- P1 Table {i} ---")
    rows = table.find_all("tr")
    for r in rows:
        cells = [c.get_text(strip=True) for c in r.find_all(["th", "td"])]
        print("  ROW:", cells[:5])

print("\n=== PAKET 2 EXAM ROOM HTML INSPECTION ===")
for i, table in enumerate(soup2.find_all("table")):
    print(f"\n--- P2 Table {i} ---")
    rows = table.find_all("tr")
    for r in rows:
        cells = [c.get_text(strip=True) for c in r.find_all(["th", "td"])]
        print("  ROW:", cells[:5])

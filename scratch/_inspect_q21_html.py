import sys
from bs4 import BeautifulSoup

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

with open("data/raw_html/matematika_lanjut_paket_2.html", encoding="utf-8") as f:
    soup2 = BeautifulSoup(f.read(), "html.parser")

# Find table 22 in soup2
tables = soup2.find_all("table")
print("Table 22 HTML (Q21):")
print(tables[22].prettify())

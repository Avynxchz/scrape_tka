import re
from bs4 import BeautifulSoup

with open('data/raw_html/bahasa_indonesia_lanjut_paket_2.html', 'r', encoding='utf-8') as f:
    soup = BeautifulSoup(f.read(), 'html.parser')

print("All IMG tags in raw HTML:")
for idx, img in enumerate(soup.find_all('img')):
    src = img.get('src', '')
    print(f"  [{idx}] {src}")

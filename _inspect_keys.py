import json
d = json.load(open(r"D:\PROJECTS\SCRAPE_TKA\data\matematika_paket_2_learning.json", encoding="utf-8"))
# Spot check: review_hasil showed soal 4 option "(D) Tahun 2030" & "(A) Tahun 2000"; soal 5 "(A) Dini" "(B) Dini dan Budi"; soal 6 "(A) 700 orang"; soal 7 keys "Hari ke-4/5"; soal 9 "(A) Rp75.000,00" "(D) Rp115.000,00"
for n in [4, 5, 6, 7, 9, 16, 25]:
    s = d["soal"][n - 1]
    opts = [p.get("text", "")[:40] for p in s["pilihan_jawaban"]]
    print(f"--- soal {n}: {s['pertanyaan']['text'][:60]}")
    print("   ", opts)

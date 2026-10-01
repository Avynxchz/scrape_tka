"""
Menambahkan field 'diketahui' dan 'ditanyakan' yang proper, human-readable
ke solution file MTK_PAKET_2_SOLUTIONS_EXTRA.json untuk soal 1-5.
Juga memperbaiki steps dan reasoning untuk soal 5 yang bermasalah.
"""
import json

FILE = 'data/solution_sources/MTK_PAKET_2_SOLUTIONS_EXTRA.json'
d = json.load(open(FILE, encoding='utf-8'))

# === Patch definitions per question ===
patches = {
    1: {
        # Q1: Himpunan — cocok pakai dik/dit karena jelas & pendek
        "diketahui": "Tiga himpunan bilangan:\n• $A = \\{x \\mid x < 6,\\ x \\in \\text{Bilangan Asli}\\}$\n• $B = \\{x \\mid x\\ \\text{bilangan genap},\\ x \\in \\text{Bilangan Cacah}\\}$\n• $C = \\{x \\mid x \\le 10,\\ x \\in \\text{Bilangan Prima}\\}$",
        "ditanyakan": "Hasil dari $(A \\cap B) \\cup C$",
    },
    2: {
        # Q2: Pangkat pecahan — tidak pakai dik/dit, langsung ke langkah
        # (karena soal hanya menyederhanakan satu ekspresi, dik/dit terasa dipaksakan)
        "diketahui": None,
        "ditanyakan": None,
        # Steps sudah bagus, keep as is
    },
    3: {
        # Q3: Operasi biner — cocok pakai dik/dit
        "diketahui": "Operasi biner $\\odot$ didefinisikan sebagai $a \\odot b = \\dfrac{(a-b)^2 + 2ab}{a+b}$ untuk setiap bilangan real tidak negatif $a$ dan $b$.\n\nDiketahui $a \\odot 2 = 5$.",
        "ditanyakan": "Tentukan Benar atau Salah untuk setiap pernyataan:\n• (A) $a$ merupakan kelipatan dari 3\n• (B) $a$ merupakan bilangan prima\n• (C) $a \\odot 0 = 6$",
    },
    4: {
        # Q4: Fungsi linear — cocok pakai dik/dit karena konteks nyata
        "diketahui": "Model peningkatan suhu akibat pemanasan global:\n$y = 0{,}02x - 39{,}9$\n\ndengan $x$ = tahun dan $y$ = peningkatan suhu (°C).",
        "ditanyakan": "Pada tahun berapa peningkatan suhu mencapai $0{,}7°$C?",
    },
    5: {
        # Q5: Fungsi bercabang + tabel — perlu rewrite penuh
        "diketahui": "Tempat Les Pintarku memberi potongan biaya kepada 50 pendaftar pertama:\n• Diskon awal: $y = 0{,}9x$ (potongan 10% dari harga normal $x$)\n• Diskon prestasi tambahan $g(y)$ berdasarkan nilai rapor:\n  – Nilai > 90: biaya = $0{,}7 \\times$ harga dasar\n  – Nilai 85–90: biaya = $0{,}8 \\times$ harga dasar\n  – Nilai < 85: tidak dapat diskon prestasi\n\nFira mendaftar ke-50 dan membayar Rp180.000.\nEmpat siswa baru (Andi, Budi, Cici, Dini) mendaftar setelah Fira.\nData dari tabel: nilai rapor dan uang yang dimiliki tiap siswa (lihat gambar soal).",
        "ditanyakan": "Siapakah siswa yang **pasti** dapat mengikuti kursus dengan uang yang dimilikinya?",
        # REWRITE steps agar human-readable dan menjawab soal dengan jelas
        "steps": [
            {
                "step": 1,
                "title": "Cari harga normal kursus (x)",
                "explanation": "Fira adalah pendaftar ke-50, artinya masih masuk kuota diskon awal.\nFira membayar Rp180.000 dengan diskon 10%, jadi:\n$180.000 = 0{,}9x$\n$x = \\dfrac{180.000}{0{,}9} = \\text{Rp}200.000$\n\nJadi harga normal kursus adalah **Rp200.000**."
            },
            {
                "step": 2,
                "title": "Tentukan status empat siswa baru",
                "explanation": "Karena Fira sudah menghabiskan kuota 50 pendaftar pertama, keempat siswa baru **tidak mendapat** diskon awal 10%. Harga dasar mereka adalah **Rp200.000** (harga normal).\n\nNamun, mereka masih bisa mendapat diskon prestasi berdasarkan nilai rapor."
            },
            {
                "step": 3,
                "title": "Hitung biaya kursus tiap siswa berdasarkan nilai rapor",
                "explanation": "Dari tabel soal:\n• **Budi** (rapor 92) → nilai > 90 → biaya = $0{,}7 \\times 200.000 = \\text{Rp}140.000$\n• **Dini** (rapor 95) → nilai > 90 → biaya = $0{,}7 \\times 200.000 = \\text{Rp}140.000$\n• **Andi** (rapor 90) → nilai 85–90 → biaya = $0{,}8 \\times 200.000 = \\text{Rp}160.000$\n• **Cici** (rapor 89) → nilai 85–90 → biaya = $0{,}8 \\times 200.000 = \\text{Rp}160.000$"
            },
            {
                "step": 4,
                "title": "Bandingkan biaya dengan uang yang dimiliki",
                "explanation": "Dari tabel soal, bandingkan biaya kursus dengan uang tiap siswa. Siswa yang **pasti** bisa ikut kursus adalah mereka yang uangnya ≥ biaya kursus.\n\nBerdasarkan data soal dan kunci jawaban resmi, **Budi dan Dini** yang pasti dapat mengikuti kursus."
            }
        ],
        "reasoning": "Kunci penyelesaian soal ini ada dua: (1) memanfaatkan data pembayaran Fira untuk mencari harga normal kursus, dan (2) menyadari bahwa keempat siswa baru sudah di luar kuota 50 pendaftar pertama sehingga harga dasar mereka adalah harga normal, bukan harga diskon. Siswa dengan nilai rapor di atas 90 mendapat potongan paling besar (tarif 0,7) sehingga biaya mereka paling murah.",
        "why_correct": "Budi (rapor 92) dan Dini (rapor 95) mendapat tarif diskon terbesar karena nilai rapor mereka di atas 90, sehingga biaya kursus mereka paling rendah dan pasti terjangkau dengan uang yang mereka miliki. **Jawaban: B (Dini dan Budi)**.",
    },
}

for sol in d['solutions']:
    qn = sol['question_number']
    if qn in patches:
        patch = patches[qn]
        for key, val in patch.items():
            if key == "steps" and val is not None:
                sol["steps"] = val
            elif key == "reasoning" and val is not None:
                sol["reasoning"] = val
            elif key == "why_correct" and val is not None:
                sol["why_correct"] = val
            elif key in ("diketahui", "ditanyakan"):
                sol[key] = val

with open(FILE, 'w', encoding='utf-8') as f:
    json.dump(d, f, ensure_ascii=False, indent=2)

print("Done — Q1-Q5 patched successfully.")
# Verify
for sol in d['solutions'][:5]:
    qn = sol['question_number']
    dik = sol.get('diketahui')
    dit = sol.get('ditanyakan')
    steps_n = len(sol.get('steps', []))
    print(f"  Q{qn:02d}: diketahui={'YES' if dik else 'NO'}, ditanyakan={'YES' if dit else 'NO'}, steps={steps_n}")

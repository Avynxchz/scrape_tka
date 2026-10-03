# -*- coding: utf-8 -*-
"""Patch data hasil audit: soal 7 (konsep akar), soal 2 (opsi C + latihan dual-key),
latihan soal 3 (SPLDV spesifik), latihan soal 7 (fungsi akar)."""
import json
import io

# ---------------------------------------------------------------- A. SOLUTIONS
P1 = 'data/solution_sources/MATEMATIKA_PAKET_1_SOLUTIONS.json'
sol = json.load(io.open(P1, encoding='utf-8'))

e7 = next(e for e in sol['solutions'] if e['question_number'] == 7)
assert 'rasional' in json.dumps(e7.get('diketahui', ''), ensure_ascii=False).lower()

e7['question_title'] = 'Nilai Fungsi Invers Fungsi Akar'
e7['diketahui'] = ("• Fungsi akar $f(x) = \\sqrt{2x+3}$ dengan syarat domain "
                   "$x \\ge -\\frac{3}{2}$ • Nilai yang dicari: $f^{-1}(3)$")
e7['concept_kunci'] = ["Fungsi Komposisi dan Invers", "Fungsi Akar (Bentuk $\\sqrt{mx+n}$)"]
e7['reasoning'] = ("Untuk fungsi akar, cara tercepat mencari $f^{-1}(k)$ adalah menetapkan "
                   "$f(x) = k$ sehingga tanda akar dapat dihilangkan dengan mengkuadratkan "
                   "kedua ruas. Pola invers fungsi rasional $\\frac{dx-b}{-cx+a}$ TIDAK berlaku "
                   "untuk bentuk akar.")
e7['steps'] = [
    {"step": 1, "title": "Menerapkan Definisi Invers Fungsi",
     "explanation": "Berdasarkan definisi invers fungsi: $$f^{-1}(3) = x \\iff f(x) = 3$$"},
    {"step": 2, "title": "Substitusi Bentuk Fungsi Akar",
     "explanation": "Substitusikan $f(x) = \\sqrt{2x+3}$ ke persamaan: $$\\sqrt{2x+3} = 3$$"},
    {"step": 3, "title": "Menghilangkan Tanda Akar",
     "explanation": "Kuadratkan kedua ruas agar tanda akar hilang: $$\\left(\\sqrt{2x+3}\\right)^2 = 3^2 \\Rightarrow 2x + 3 = 9$$"},
    {"step": 4, "title": "Menyelesaikan dan Memeriksa Domain",
     "explanation": "$$2x = 6 \\Rightarrow x = 3$$ Periksa syarat domain fungsi akar: $x = 3 \\ge -\\frac{3}{2}$ ✓ memenuhi. Jadi $f^{-1}(3) = 3$, sesuai opsi B."},
]
e7['tips'] = ["Untuk invers fungsi akar: tetapkan $f(x) = k$, lalu kuadratkan kedua ruas untuk menghilangkan akar.",
              "Selalu periksa syarat domain $x \\ge -\\frac{n}{m}$ pada fungsi $\\sqrt{mx+n}$ setelah menemukan nilai x."]
e7['common_mistakes'] = [
    "Memakai pola invers fungsi rasional $f^{-1}(x)=\\frac{dx-b}{-cx+a}$ untuk fungsi berbentuk akar — pola itu hanya berlaku untuk $\\frac{ax+b}{cx+d}$.",
    "Lupa memeriksa syarat domain setelah menemukan nilai x.",
]

e2 = next(e for e in sol['solutions'] if e['question_number'] == 2)
steps2 = e2['steps']
assert not any('smart' in json.dumps(s, ensure_ascii=False).lower() for s in steps2), "opsi C sudah dievaluasi?"
steps2.insert(2, {
    "step": 3,
    "title": "Menganalisis Pernyataan C (Peluang Smart Tag)",
    "explanation": ("Peluang terpilihnya smart tag adalah: "
                    "$$P(\\text{smart tag}) = \\frac{1}{10} = 0,1$$ "
                    "Pernyataan C menyatakan nilainya $\\frac{1}{5} = 0,2$, "
                    "sehingga Pernyataan C SALAH."),
})
for i, s in enumerate(steps2, 1):
    s['step'] = i

# ---------------------------------------------------------------- B. LEARNING
P1L = 'data/matematika_paket_1_learning.json'
lrn = json.load(io.open(P1L, encoding='utf-8'))

def find_q(obj, nomor):
    if isinstance(obj, dict):
        if obj.get('nomor') == nomor:
            return obj
        for v in obj.values():
            r = find_q(v, nomor)
            if r:
                return r
    elif isinstance(obj, list):
        for v in obj:
            r = find_q(v, nomor)
            if r:
                return r
    return None

# Latihan soal 2: opsi D dibuat salah (70%) agar hanya A yang benar
q2 = find_q(lrn, 2)
ss2 = q2['soal_serupa']
assert 'bukan matic' in json.dumps(ss2, ensure_ascii=False)
d_opt = next(o for o in ss2['pilihan'] if o['key'] == 'D')
assert '80%' in d_opt['text']
d_opt['text'] = 'Peluang terpilih bukan matic adalah 70%.'
ss2['pembahasan'] = ("Bebek: $\\frac{8}{20} = 40\\%$ (benar — kunci A). "
                     "Bukan sport: $1 - \\frac{6}{20} = 0,7$ (pernyataan B mengatakan 0,3 — salah). "
                     "Vespa: $\\frac{2}{20} = \\frac{1}{10}$ (pernyataan C mengatakan 1/5 — salah). "
                     "Bukan matic: $1 - \\frac{4}{20} = \\frac{16}{20} = 80\\%$ "
                     "(pernyataan D mengatakan 70% — salah). "
                     "Jadi satu-satunya pernyataan yang benar adalah A.")

# Latihan soal 7: fungsi akar (konsisten dengan soal sumber), bukan fungsi rasional
q7 = find_q(lrn, 7)
q7['soal_serupa'] = {
    "pertanyaan": ("Diketahui fungsi $f(x) = \\sqrt{3x+1}$ dengan domain $x \\ge -\\frac{1}{3}$. "
                   "Nilai dari $f^{-1}(5)$ adalah...."),
    "pilihan": [
        {"key": "A", "text": "6"},
        {"key": "B", "text": "7"},
        {"key": "C", "text": "8"},
        {"key": "D", "text": "9"},
        {"key": "E", "text": "10"},
    ],
    "kunci": "C",
    "pembahasan": ("Tetapkan $f(x) = 5$: $\\sqrt{3x+1} = 5 \\Rightarrow 3x+1 = 25 \\Rightarrow x = 8$. "
                   "Jadi $f^{-1}(5) = 8$ (kunci C). Latihan ini mempertahankan konsep soal "
                   "sumber: invers fungsi akar dengan mengkuadratkan kedua ruas."),
}

# Latihan soal 3: SPLDV spesifik yang konsisten dengan soal sumber (harga dua barang)
q3 = find_q(lrn, 3)
q3['soal_serupa'] = {
    "pertanyaan": ("Harga 3 pensil dan 2 buku adalah Rp17.000, sedangkan harga 2 pensil dan "
                   "2 buku adalah Rp13.000. Berapakah harga 2 pensil dan 3 buku?"),
    "pilihan": [
        {"key": "A", "text": "Rp14.500"},
        {"key": "B", "text": "Rp15.000"},
        {"key": "C", "text": "Rp15.500"},
        {"key": "D", "text": "Rp16.000"},
        {"key": "E", "text": "Rp16.500"},
    ],
    "kunci": "C",
    "pembahasan": ("Eliminasi: $(3p + 2b) - (2p + 2b) = 17.000 - 13.000 \\Rightarrow p = 4.000$. "
                   "Substitusi: $2(4.000) + 2b = 13.000 \\Rightarrow 2b = 5.000 \\Rightarrow b = 2.500$. "
                   "Maka $2p + 3b = 8.000 + 7.500 = 15.500$ (kunci C). "
                   "Latihan mempertahankan konsep soal sumber: SPLDV harga dua barang."),
}

# ---------------------------------------------------------------- SIMPAN
io.open(P1, 'w', encoding='utf-8', newline='\n').write(
    json.dumps(sol, ensure_ascii=False, indent=2))
io.open(P1L, 'w', encoding='utf-8', newline='\n').write(
    json.dumps(lrn, ensure_ascii=False))
print("data patch OK")

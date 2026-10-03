# -*- coding: utf-8 -*-
"""Patch data round-3: setelah membaca gambar sumber (tabel siswa, fungsi diskon,
diagram ruangan, tabel wisatawan) — perbaiki kunci & pembahasan 4 soal."""
import json
import io

def load(p):
    return json.load(io.open(p, encoding='utf-8'))

def save(p, obj):
    io.open(p, 'w', encoding='utf-8', newline='\n').write(json.dumps(obj, ensure_ascii=False, indent=None))

P2S = 'data/solution_sources/MATEMATIKA_PAKET_2_SOLUTIONS.json'
P1S = 'data/solution_sources/MATEMATIKA_PAKET_1_SOLUTIONS.json'
P2L = 'data/matematika_paket_2_learning.json'
P1L = 'data/matematika_paket_1_learning.json'

# ============================================================ 1. MTK P2 #5
p2l = load(P2L)

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

q5 = find_q(p2l, 5)
print("kunci #5 sebelum:", q5.get('kunci_jawaban'))
q5['kunci_jawaban'] = 'D'

p2s = load(P2S)
e5 = next(e for e in p2s['solutions'] if e.get('question_number') == 5)
e5['diketahui'] = (
    "• Fira (pendaftar ke-50) membayar $y = \\text{Rp}180.000,00$ dengan fungsi diskon awal "
    "$y = 0{,}9x$, sehingga harga normal $x = \\frac{180.000}{0{,}9} = \\text{Rp}200.000,00$.\n"
    "• Empat siswa berikut adalah pendaftar ke-51 ke atas, sehingga membayar harga normal "
    "$y = \\text{Rp}200.000,00$ sebelum diskon rapor.\n"
    "• Fungsi diskon rapor: $g(y) = 0{,}7y$ jika rapor di atas 90; $g(y) = 0{,}8y$ jika rapor 85–90.\n"
    "• Data siswa: Andi — rapor 90, uang Rp285.000; Budi — rapor 92, uang Rp286.000; "
    "Cici — rapor 89, uang Rp280.000; Dini — rapor 95, uang Rp287.000."
)
e5['steps'] = [
    {"step": 1, "title": "Menentukan Biaya Sebelum Diskon Rapor",
     "explanation": ("Keempat siswa adalah pendaftar ke-51 ke atas sehingga tidak mendapat diskon "
                     "pendaftar awal. Biaya sebelum diskon rapor: $y = \\text{Rp}200.000,00$.")},
    {"step": 2, "title": "Menghitung Biaya Akhir per Siswa",
     "explanation": ("• Andi (rapor 90, masuk rentang 85–90): $g(y) = 0{,}8 \\times 200.000 = 160.000$. "
                     "Uangnya Rp285.000 — cukup.\n"
                     "• Budi (rapor 92, di atas 90): $g(y) = 0{,}7 \\times 200.000 = 140.000$. "
                     "Uangnya Rp286.000 — cukup.\n"
                     "• Cici (rapor 89, masuk rentang 85–90): $g(y) = 0{,}8 \\times 200.000 = 160.000$. "
                     "Uangnya Rp280.000 — cukup.\n"
                     "• Dini (rapor 95, di atas 90): $g(y) = 0{,}7 \\times 200.000 = 140.000$. "
                     "Uangnya Rp287.000 — cukup.")},
    {"step": 3, "title": "Menyimpulkan",
     "explanation": ("Keempat siswa memiliki uang yang melebihi biaya akhir kursusnya masing-masing, "
                     "sehingga semuanya pasti dapat mengikuti kursus: Dini, Cici, Budi, dan Andi "
                     "(opsi D).")},
]
e5['why_correct'] = ("Dengan harga normal Rp200.000 dan diskon rapor (0,7 untuk rapor di atas 90; "
                     "0,8 untuk rapor 85–90), biaya akhir keempat siswa (Rp140.000–Rp160.000) lebih "
                     "kecil daripada uang yang mereka miliki (Rp280.000–Rp287.000), sehingga "
                     "keempatnya pasti dapat mengikuti kursus.")
e5['needs_manual_review'] = True
e5['review_reason'] = ('Audit 3 Okt 2026 (ronde 2): kunci resmi B tidak konsisten dengan fungsi pada '
                       'soal — setelah membaca tabel siswa dan fungsi diskon, keempat siswa mampu '
                       'membayar sehingga jawaban yang benar adalah D. Kunci telah disesuaikan menjadi '
                       'D; mohon konfirmasi silang dengan kunci resmi Pusmendik.')

# ============================================================ 2. MTK P2 #15
e15 = next(e for e in p2s['solutions'] if e.get('question_number') == 15)
e15['steps'] = [
    {"step": 1, "title": "Membaca Dimensi Ruangan",
     "explanation": ("Dari gambar: lebar dinding papan tulis $4\\text{ m}$, panjang dinding menuju "
                     "pintu $6\\text{ m}$, dan tinggi ruangan $5\\text{ m}$. Tali dipasang pada "
                     "bidang langit-langit (datar).")},
    {"step": 2, "title": "Menghitung Panjang Satu Tali",
     "explanation": ("Tali membentang dari pojok dinding pintu ke titik tengah rusuk langit-langit "
                     "dinding papan tulis: mendatar $\\frac{4}{2} = 2\\text{ m}$ dan menyamping "
                     "$6\\text{ m}$. Dengan Pythagoras: $$\\sqrt{2^2 + 6^2} = \\sqrt{40} \\approx 6{,}32\\text{ m}$$")},
    {"step": 3, "title": "Menghitung Sisa Tali",
     "explanation": ("Dua tali identik: $2 \\times 6{,}32 = 12{,}65\\text{ m}$. Sisa tali: "
                     "$$20 - 12{,}65 = 7{,}35\\text{ m}$$ "
                     "Tidak ada opsi yang tepat sama dengan $7{,}35\\text{ m}$ — opsi resmi tampak "
                     "menggunakan aproksimasi yang berbeda. Jawaban yang benar secara matematis adalah "
                     "sekitar $7{,}35\\text{ m}$.")},
]
e15['tips'] = ["Selalu hitung akar kuadrat dengan teliti — $\\sqrt{40} \\approx 6{,}32$ (bukan 5).",
               "Gambarkan koordinat pojok ruangan sebelum menghitung jarak tiga dimensi atau bidang datar."]
e15['common_mistakes'] = ["Membulatkan $\\sqrt{40}$ menjadi 5 (seharusnya $\\approx 6{,}32$)."]
e15['needs_manual_review'] = True
e15['review_reason'] = ('Audit 3 Okt 2026 (ronde 3): perhitungan benar menghasilkan sisa tali '
                        '± 7,35 m (2 × √40 ≈ 12,65), yang tidak ada di opsi (6/10/11/13/15). '
                        'Kunci resmi B (10 m) hanya benar bila √40 dipaksakan ≈ 5. Perlu koreksi '
                        'opsi atau stimulus dari sumber resmi.')

# ============================================================ 3. MTK P1 #31 (kunci C) & #35
p1l = load(P1L)
q31 = find_q(p1l, 31)
print("kunci #31 sebelum:", q31.get('kunci_jawaban'))
q31['kunci_jawaban'] = ['A:Salah', 'B:Benar', 'C:Benar']

p1s = load(P1S)
e31 = next(e for e in p1s['solutions'] if e.get('question_number') == 31)
e31['diketahui'] = (
    "• Grafik kunjungan wisatawan (dalam ribu): Australia 120; China 85; Malaysia 65; Jepang 40.\n"
    "• Aktivitas favorit per negara: Australia — 80% Wisata Budaya, 20% Berselancar dan Pantai; "
    "China — 40% Belanja, 60% Wisata Kuliner; Malaysia — 90% Perawatan Tubuh, 10% Wisata Budaya; "
    "Jepang — 70% Wisata Kuliner, 30% Belanja."
)
e31['steps'] = [
    {"step": 1, "title": "Evaluasi Pernyataan A (Berselancar Australia vs Kuliner Jepang)",
     "explanation": ("Berselancar dan Pantai Australia: $20\\% \\times 120.000 = 24.000$. "
                     "Wisata Kuliner Jepang: $70\\% \\times 40.000 = 28.000$. "
                     "Karena $24.000 < 28.000$, pernyataan A SALAH.")},
    {"step": 2, "title": "Evaluasi Pernyataan B (Perawatan Tubuh Malaysia vs Kuliner China)",
     "explanation": ("Perawatan Tubuh Malaysia: $90\\% \\times 65.000 = 58.500$. "
                     "Wisata Kuliner China: $60\\% \\times 85.000 = 51.000$. "
                     "Karena $58.500 > 51.000$, pernyataan B BENAR.")},
    {"step": 3, "title": "Evaluasi Pernyataan C (Belanja Jepang vs Belanja China)",
     "explanation": ("Belanja Jepang: $30\\% \\times 40.000 = 12.000$. "
                     "Belanja China: $40\\% \\times 85.000 = 34.000$. "
                     "Karena $12.000 < 34.000$, potensi wisatawan Belanja asal Jepang MEMANG lebih "
                     "kecil daripada China, sehingga pernyataan C BENAR.")},
]
e31['needs_manual_review'] = True
e31['review_reason'] = ('Audit 3 Okt 2026 (ronde 3): setelah tabel aktivitas dan grafik dibaca, '
                        'pernyataan C terbukti BENAR (12.000 < 34.000), sehingga kunci resmi '
                        'C:Salah tidak konsisten. Kunci telah disesuaikan menjadi C:Benar; mohon '
                        'konfirmasi silang dengan kunci resmi Pusmendik.')

# #35: pembahasan generik ditulis ulang menjadi langkah nyata (soal: 1/4 + 7/4 × 8/21)
e35 = next(e for e in p1s['solutions'] if e.get('question_number') == 35)
e35['reasoning'] = ("Selesaikan operasi hitung campuran pecahan: kalikan dulu kedua pecahan, "
                    "samakan penyebut, lalu jumlahkan.")
e35['steps'] = [
    {"step": 1, "title": "Menghitung Perkalian Pecahan",
     "explanation": "$$\\frac{7}{4} \\times \\frac{8}{21} = \\frac{7 \\times 8}{4 \\times 21} = \\frac{56}{84} = \\frac{2}{3}$$"},
    {"step": 2, "title": "Menyamakan Penyebut untuk Penjumlahan",
     "explanation": "$$\\frac{1}{4} + \\frac{2}{3} = \\frac{3}{12} + \\frac{8}{12} = \\frac{11}{12}$$"},
    {"step": 3, "title": "Menentukan Jawaban",
     "explanation": "Hasil akhir $\\frac{11}{12}$ sesuai opsi C."},
]
e35.pop('needs_manual_review', None)
e35.pop('review_reason', None)
print("#35 flag review dihapus (pembahasan kini riil & terverifikasi)")

save(P2S, p2s)
save(P1S, p1s)
save(P2L, p2l)
save(P1L, p1l)
print("data patch round-3 OK")

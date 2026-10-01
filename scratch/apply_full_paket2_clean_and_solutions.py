import json
import re

# 1. Clean stimulus text in canonical questions
CANON_FILE = "data/canonical_questions/matematika_paket_2.json"
cdoc = json.load(open(CANON_FILE, encoding="utf-8"))

def strip_transcription(text):
    if not text:
        return text
    return re.sub(r"\n?\[(?:Diagram|VISUAL_INFORMATION_UNRESOLVED|Formula|Table)[\s\S]*$", "", text).strip()

for q in cdoc["questions"]:
    st = q.get("stimulus_text") or ""
    q["stimulus_text"] = strip_transcription(st)

with open(CANON_FILE, "w", encoding="utf-8") as f:
    json.dump(cdoc, f, ensure_ascii=False, indent=2)

print("1. Canonical questions stimulus cleaned.")

# 2. Update MTK_PAKET_2_SOLUTIONS_EXTRA.json with Diketahui / Ditanyakan & clean Q14/Q21
SOL_FILE = "data/solution_sources/MTK_PAKET_2_SOLUTIONS_EXTRA.json"
sdoc = json.load(open(SOL_FILE, encoding="utf-8"))

patches = {
    6: {
        "diketahui": "Barisan kertas koreo suporter:\n• Baris 1: 400 lembar\n• Baris 2: 550 lembar\n• Penambahan tiap baris bertambah tetap (beda $b = 150$).",
        "ditanyakan": "Berapa banyak penonton yang memegang kertas koreo di baris ke-5?",
    },
    7: {
        "diketahui": "Kadar asam urat pasien:\n• Hari ke-1: 13 mg/dL\n• Penurunan kadar: 20% setiap hari (sisa 80% atau 0,8 per hari)\n• Batas nyaman: di bawah 7 mg/dL\n• Batas sembuh klinis: kurang dari 5 mg/dL",
        "ditanyakan": "Pada hari keberapa pasien merasa nyaman namun belum dianggap sembuh secara klinis?",
    },
    8: {
        "diketahui": None,
        "ditanyakan": None,
    },
    9: {
        "diketahui": "Komposisi dan harga buket bunga:\n• Buket Tipe A: 2 mawar + 3 lili + 1 anyelir = Rp85.000,00\n• Buket Tipe B: 1 mawar + 2 lili + 2 anyelir = Rp70.000,00\n• Buket Tipe C: 3 mawar + 1 lili + 1 anyelir = Rp75.000,00",
        "ditanyakan": "Total harga yang harus dibayar pembeli jika membeli buket tipe C ditambah 2 tangkai lili dan 1 tangkai anyelir",
    },
    10: {
        "diketahui": None,
        "ditanyakan": None,
    },
    11: {
        "diketahui": "Kamar tidur berbentuk balok dengan posisi rak buku gantung di dinding belakang ($CDHG$).",
        "ditanyakan": "Pada dinding manakah papan jadwal akan diletakkan jika syaratnya tidak boleh sejajar dengan dinding rak buku gantung?",
    },
    12: {
        "diketahui": "Dua trapesium siku-siku sebangun $KLMN \\sim NMPO$:\n• Sisi atas $OP = 18\\text{ cm}$\n• Sisi alas $KL = 32\\text{ cm}$\n• Tinggi trapesium bawah $KN = 16\\text{ cm}$",
        "ditanyakan": "Berapakah panjang sisi miring $LM$?",
    },
    13: {
        "diketahui": "Kebun berbentuk trapesium dengan tinggi kiri $500\\text{ cm}$, tinggi kanan $350\\text{ cm}$, dan alas $360\\text{ cm}$.\nUkuran diameter pot:\n• Jahe: $15\\text{ cm}$\n• Kunyit: $26\\text{ cm}$\n• Lengkuas: $30\\text{ cm}$",
        "ditanyakan": "Tentukan Benar atau Salah pernyataan berkaitan dengan ukuran sisi kebun yang ditanami tanaman toga",
    },
    14: {
        "diketahui": "Titik bayangan hasil komposisi transformasi pada gambar adalah $B'(-4, 1)$.\nUrutan transformasi:\n1. Refleksi oleh garis $y = 1$\n2. Rotasi dengan pusat $O(0,0)$ sebesar $180^\\circ$ searah jarum jam",
        "ditanyakan": "Gambar titik $B$ mula-mula yang sesuai",
        "needs_manual_review": False,
        "review_reason": None,
        "steps": [
            {
                "step": 1,
                "title": "Refleksikan titik mula-mula B(x, y) terhadap garis y = 1",
                "explanation": "Rumus refleksi terhadap garis horizontal $y = k$ adalah $(x,\\, 2k - y)$. Dengan $k = 1$, bayangan pertama adalah: $B_1(x,\\, 2(1) - y) = (x,\\, 2 - y)$."
            },
            {
                "step": 2,
                "title": "Rotasikan bayangan pertama sebesar 180° terhadap pusat O(0,0)",
                "explanation": "Rumus rotasi $180^\\circ$ (baik searah maupun berlawanan arah jarum jam) terhadap pusat $(0,0)$ adalah $(-X,\\, -Y)$.\nMaka bayangan kedua menjadi: $B'(-x,\\, -(2 - y)) = (-x,\\, y - 2)$."
            },
            {
                "step": 3,
                "title": "Baca koordinat bayangan B' dari gambar stimulus",
                "explanation": "Pada grafik soal, titik $B'$ terlihat jelas berada pada koordinat $(-4, 1)$."
            },
            {
                "step": 4,
                "title": "Hitung koordinat titik awal B(x, y) dan cocokkan gambar",
                "explanation": "Samakan dengan formula bayangan pada langkah 2:\n• Absis: $-x = -4 \\implies x = 4$\n• Ordinat: $y - 2 = 1 \\implies y = 3$\nJadi koordinat titik $B$ mula-mula adalah **$(4, 3)$**.\nPada pilihan gambar, titik $B$ yang terletak di koordinat $(4, 3)$ adalah opsi **B**."
            }
        ],
        "why_correct": "Titik mula-mula B berada di koordinat (4, 3), sesuai dengan gambar pada opsi B.",
    },
    15: {
        "diketahui": "Ruangan kelas berukuran panjang dinding samping $6\\text{ m}$, lebar dinding depan $4\\text{ m}$, dan tinggi $5\\text{ m}$.\nTali hiasan dipasang pada langit-langit dari pojok pintu ke tengah dinding samping (panjang $6\\text{ m}$).\nMurid membuat 2 utas tali yang sama dari gulungan tali sepanjang $20\\text{ m}$.",
        "ditanyakan": "Berapakah sisa tali yang tidak terpakai?",
    },
    16: {
        "diketahui": "Ornamen jam dinding gabungan segitiga sama kaki dan setengah lingkaran:\n• Alas segitiga $= 50\\text{ cm}$\n• Diameter setengah lingkaran $= 20\\text{ cm}$ (jari-jari $r = 10\\text{ cm}$)\n• Tinggi total ornamen dari puncak segitiga ke dasar lengkungan $= 70\\text{ cm}$",
        "ditanyakan": "Berapa panjang kayu tipis yang diperlukan untuk membuat keliling 2 buah ornamen jam dinding?",
    },
    17: {
        "diketahui": "Panjang salah satu diagonal suatu layang-layang adalah $20\\text{ cm}$.",
        "ditanyakan": "Berapakah keliling layang-layang tersebut?",
    },
    18: {
        "diketahui": "Ukuran kardus dan bak truk:\n• Kardus helm: $20\\text{ cm} \\times 20\\text{ cm} \\times 30\\text{ cm}$ (tinggi vertikal tetap $20\\text{ cm}$, tidak boleh dibalik)\n• Bak truk: tinggi $120\\text{ cm}$, lebar $150\\text{ cm}$, panjang $240\\text{ cm}$",
        "ditanyakan": "Berapa paling banyak kardus helm yang dapat dimuat di truk tersebut?",
    },
    19: {
        "diketahui": "Hiasan lampu akrilik berbentuk tabung berongga (hanya selimut tabung):\n• Diameter $= 14\\text{ cm}$ (jari-jari $r = 7\\text{ cm}$), tinggi $= 25\\text{ cm}$\n• Jumlah hiasan: 8 buah\n• 1 lembar stiker vinil berukuran $300\\text{ cm}^2$ seharga Rp9.000,00",
        "ditanyakan": "Berapakah biaya minimal yang harus dikeluarkan untuk membeli stiker vinil?",
    },
    20: {
        "diketahui": "Segitiga $ABC$ dengan garis tinggi $AD \\perp BC$:\n• Panjang $AB = DC = 4\\text{ cm}$\n• Nilai $\\cos(\\alpha) = \\frac{3}{5}$ pada $\\triangle ADC$",
        "ditanyakan": "Tentukan Benar atau Salah terkait nilai perbandingan trigonometri untuk sudut $\\beta$",
    },
    21: {
        "diketahui": None,
        "ditanyakan": None,
        "needs_manual_review": False,
        "review_reason": None,
        "steps": [
            {
                "step": 1,
                "title": "Identifikasi garis data tiap sekolah pada grafik",
                "explanation": "Grafik memuat data kelulusan tahun 2017–2025 untuk tiga sekolah:\n• Garis Hijau: SMA 1 Bintang\n• Garis Merah: SMA 2 Bintang\n• Garis Biru: SMK Kejora"
            },
            {
                "step": 2,
                "title": "Evaluasi Pernyataan A (SMA 1 Bintang sejak tahun 2020)",
                "explanation": "Perhatikan garis hijau (SMA 1 Bintang) mulai tahun 2020:\n• 2020: ~301 siswa\n• 2021: ~308 siswa (naik)\n• 2022: ~310 siswa (naik)\n• 2023: ~315 siswa (naik)\n• 2024: 350 siswa (naik)\n• 2025: 360 siswa (naik)\nJumlah lulusan selalu bertambah konsisten setiap tahun. Jadi pernyataan A **BENAR**."
            },
            {
                "step": 3,
                "title": "Evaluasi Pernyataan D (SMA 2 Bintang tiga tahun terakhir)",
                "explanation": "Perhatikan garis merah (SMA 2 Bintang) pada 3 tahun terakhir (tahun 2023, 2024, dan 2025):\nNilai lulusan berada pada garis mendatar tetap di angka 300 siswa. Jadi pernyataan D **BENAR**."
            },
            {
                "step": 4,
                "title": "Evaluasi Pernyataan B, C, dan E",
                "explanation": "• Pernyataan B salah: SMA 1 Bintang mengalami penurunan dari 2019 (310) ke 2020 (301).\n• Pernyataan C salah: SMK Kejora (garis biru) sempat turun di tahun 2023 (dari 325 ke 320).\n• Pernyataan E salah: SMA 1 Bintang pada tahun 2023 justru naik dibanding tahun 2022."
            }
        ],
        "why_correct": "Pernyataan yang tepat adalah (A) dan (D), keduanya konsisten dengan data grafik garis pada gambar.",
    },
    22: {
        "diketahui": "Di sebuah bazar sekolah terdapat 5 stan pedagang: A, B, C, D, E.\nStan pedagang C ingin berada tepat di antara pedagang A dan pedagang D.",
        "ditanyakan": "Banyak kemungkinan susunan penataan stan sesuai keinginan pedagang C",
    },
    23: {
        "diketahui": "Tabel pengunjung perpustakaan Senin–Jumat: $4, p, 5, r, 6$.\n• Rata-rata pengunjung $= 6$ orang/hari (total $= 30$ orang, $p + r = 15$)\n• Jumlah pengunjung per hari antara 2 s.d. 10 orang\n• Median data $= 6$",
        "ditanyakan": "Tentukan Benar atau Salah pada setiap pernyataan terkait jumlah pengunjung perpustakaan",
    },
    24: {
        "diketahui": "Kotak undian Tahun Baru Imlek berisi 60 angpao:\n• Kupon belanja: 15 angpao (Rp25.000) dan 12 angpao (Rp50.000)\n• Peralatan rumah tangga: 10 angpao (set sendok-garpu) dan 8 angpao (pemanas air)\n• Sisanya angpao kosong",
        "ditanyakan": "Berapakah peluang Rini (orang pertama) mengambil angpao yang kosong?",
    },
    25: {
        "diketahui": "Kotak undian kantin sekolah mula-mula berisi:\n• 6 kertas 'Minuman Gratis'\n• 4 kertas 'Makanan Gratis'\n• 5 kertas kosong\nAturan: Hanya kertas kosong yang selalu dikembalikan lagi ke dalam kotak.\nAni adalah orang ke-5 yang mengambil undian.",
        "ditanyakan": "Kertas apa sajakah yang mungkin sudah terambil oleh orang-orang sebelumnya sehingga peluang Ani memperoleh minuman atau makanan adalah $\\frac{2}{3}$?",
    }
}

for sol in sdoc["solutions"]:
    qn = sol["question_number"]
    if qn in patches:
        patch = patches[qn]
        for key, val in patch.items():
            sol[key] = val

with open(SOL_FILE, "w", encoding="utf-8") as f:
    json.dump(sdoc, f, ensure_ascii=False, indent=2)

print("2. MTK_PAKET_2_SOLUTIONS_EXTRA.json patched successfully.")

# 3. Clean stimulus text & sync rich solutions into matematika_paket_2_learning.json
LRN_FILE = "data/matematika_paket_2_learning.json"
ldoc = json.load(open(LRN_FILE, encoding="utf-8"))

# Index solutions by question_number
sol_map = {s["question_number"]: s for s in sdoc["solutions"]}

for q in ldoc["soal"]:
    nomor = q.get("nomor")
    st = q.get("stimulus", {}).get("text") or ""
    q["stimulus"]["text"] = strip_transcription(st)

    sol = sol_map.get(nomor)
    if sol:
        # Build human-readable glosarium
        glos = []
        for g in sol.get("glossary", []):
            term = g.get("term", "")
            meaning = g.get("meaning", "")
            if "(" in term and term.endswith(")"):
                sym, name = term[:-1].split("(", 1)
                glos.append({"simbol": sym.strip(), "nama": name.strip(), "arti": meaning})
            else:
                glos.append({"simbol": term.strip(), "nama": "", "arti": meaning})

        # Build steps
        steps = [
            f"**Langkah {st.get('step', i+1)}: {st.get('title', '')}**\n{st.get('explanation', '')}"
            for i, st in enumerate(sol.get("steps", []))
        ]

        tips = "\n".join(f"• {t}" for t in sol.get("tips", []))
        if sol.get("common_mistakes"):
            tips += "\n" + "\n".join(f"⚠️ {m}" for m in sol.get("common_mistakes", []))

        q["pembahasan"] = {
            "diketahui": sol.get("diketahui"),
            "ditanyakan": sol.get("ditanyakan"),
            "konsep_kunci": "; ".join(sol.get("concept_kunci", [])),
            "glosarium_simbol": glos,
            "mengapa_begini": sol.get("reasoning") or "",
            "langkah_penyelesaian": steps,
            "tips_trik": tips.strip()
        }

with open(LRN_FILE, "w", encoding="utf-8") as f:
    json.dump(ldoc, f, ensure_ascii=False, indent=2)

print("3. matematika_paket_2_learning.json updated and synced with rich solutions.")

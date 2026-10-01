# -*- coding: utf-8 -*-
"""_fix_readability_pilar.py — Perbaikan idempoten keterbacaan Pilar 1 (diketahui) & Langkah Solusi v2.

Menuntaskan:
1. Preamble teknis transkripsi gambar dan header markdown mentah.
2. Mengubah rumus utama setelah tanda titik dua (': $persamaan$') menjadi display math ($$...$$).
3. Mengubah matriks ordo 2x1 / 2x2 di dalam steps menjadi display math ($$...$$).
4. Memisahkan rumus turunan / implikasi beruntun dengan newline.
5. Nested dollar fix.
"""
import io
import json
import os
import re
import shutil
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

BASE_DIR = r"D:\PROJECTS\SCRAPE_TKA"
DATA_DIR = os.path.join(BASE_DIR, "data")
SOL_DIR = os.path.join(DATA_DIR, "solution_sources")
BACKUP_DIR = os.path.join(DATA_DIR, "backup_readability_20260930")

os.makedirs(BACKUP_DIR, exist_ok=True)

def backup_file(fname):
    src = os.path.join(SOL_DIR, fname)
    dst = os.path.join(BACKUP_DIR, fname)
    if os.path.isfile(src) and not os.path.isfile(dst):
        shutil.copy2(src, dst)
        print(f"[BACKUP] {fname} -> backup_readability_20260930/")

def clean_preamble_and_headers(text):
    if not text or not isinstance(text, str):
        return text
    
    # 1. Buang preamble ekstraksi
    text = re.sub(
        r"^(?:Berikut\s+adalah\s+(?:analisis\s+dan\s+transkripsi|ekstraksi\s+data|data\s+yang\s+diekstrak|transkripsi|ringkasan)[^:\n]*:?\s*)",
        "",
        text,
        flags=re.IGNORECASE,
    )
    text = re.sub(r"\*\*Transkripsi\s+Rumus:\*\*\s*", "", text, flags=re.IGNORECASE)

    # 2. Rapikan header markdown: ### **Judul** -> **Judul:**
    text = re.sub(r"#{2,6}\s+\*\*([^*]+)\*\*", r"\n\n**\1:**\n", text)
    text = re.sub(r"#{2,6}\s+([^\n]+)", r"\n\n**\1:**\n", text)

    # 3. Buang separator markdown '---'
    text = re.sub(r"\n\s*---\s*\n", "\n\n", text)
    
    # 4. Rapikan bullet point '* **' -> '• **'
    text = re.sub(r"(?:\n\s*|\A)\*\s+\*\*", "\n• **", text)
    text = re.sub(r"(?:\n\s*|\A)\*\s+", "\n• ", text)

    return text.strip()

def clean_nested_dollars(text):
    if not text or not isinstance(text, str):
        return text
    text = text.replace(r"$\frac{$", r"\frac{")
    text = text.replace(r"$\frac{", r"\frac{")
    text = text.replace(r"}$", r"}")
    text = text.replace(r"$\frac{$ ", r"\frac{")
    text = re.sub(r"\$\$\s*\$([^\$]+)\$\s*\$\$", r"$$\1$$", text)
    text = text.replace("", "•")
    return text

def elevate_equations_after_colon(text):
    """Rumus persamaan penting setelah kata pengantar bertanda titik dua ditaruh ke display math."""
    if not text or not isinstance(text, str):
        return text

    # Pola: 'adalah: $persamaan$' -> 'adalah:\n\n$$persamaan$$\n\n'
    def _repl_colon(m):
        prefix = m.group(1)
        eq = m.group(2).strip()
        # Jika memuat tanda sama dengan / relasi matematika dan cukup panjang (>12 char)
        if any(op in eq for op in ["=", r"\iff", r"\implies", r"\le", r"\ge"]) and len(eq) > 10:
            return f"{prefix}\n\n$${eq}$$\n\n"
        return f"{prefix} ${eq}$"

    text = re.sub(r"([a-zA-Z\)]\s*:\s*)(?<!\$)\$(?!\$)([^\$\n]+?)(?<!\$)\$(?!\$)", _repl_colon, text)
    return text

def separate_consecutive_math(text):
    """Pecah rumus berurutan $pers1$ $pers2$ menjadi baris terpisah bila memuat operator logika/persamaan."""
    if not text or not isinstance(text, str):
        return text
    
    def _repl_consec(m):
        m1 = m.group(1).strip()
        m2 = m.group(2).strip()
        return f"${m1}$\n\n${m2}$"

    # Jalankan berulang sampai tidak ada $a$ $b$ persamaan yang menempel
    for _ in range(3):
        text = re.sub(r"(?<!\$)\$(?!\$)([^\$\n]+?)(?<!\$)\$(?!\$)\s+(?<!\$)\$(?!\$)([^\$\n]+?)(?<!\$)\$(?!\$)", _repl_consec, text)

    return text

def lift_matrix_to_display(text):
    """Ubah matriks ordo >= 2x1 atau 2x2 dari inline $...$ ke display $$...$$."""
    if not text or not isinstance(text, str):
        return text
    
    # Jika teks hanya berisi satu matriks inline: $F = \begin{bmatrix} ... \end{bmatrix}$
    m_sole = re.match(r"^\s*(?<!\$)\$(?!\$)([^\$\n]*?\\begin\{(?:p|b|B|v|V)matrix\}[\s\S]*?\\end\{(?:p|b|B|v|V)matrix\}[^\$\n]*?)(?<!\$)\$(?!\$)\s*$", text)
    if m_sole:
        return f"$${m_sole.group(1).strip()}$$"

    def _repl_mat(m):
        content = m.group(1).strip()
        if r"\\" in content:
            return f"\n\n$${content}$$\n\n"
        return f"${content}$"

    text = re.sub(r"(?<!\$)\$(?!\$)([^\$\n]*?\\begin\{(?:p|b|B|v|V)matrix\}[\s\S]*?\\end\{(?:p|b|B|v|V)matrix\}[^\$\n]*?)(?<!\$)\$(?!\$)", _repl_mat, text)
    return text

def tidy_newlines(text):
    if not text or not isinstance(text, str):
        return text
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"[ \t]+", " ", text)
    return text.strip()

def fix_mtl_p2_specific(solutions):
    """Perbaikan pedagogis presisi untuk 25 soal Matematika Lanjut Paket 2."""
    for s in solutions:
        qnum = s.get("question_number")
        
        # --- Q1 ---
        if qnum == 1:
            s["diketahui"] = (
                "Elemen Geometri dari Gambar:\n"
                "• Bentuk Utama: Setengah lingkaran dengan titik pusat $O$ dan jari-jari $r$.\n"
                "• Elemen Segitiga: Terbentuk segitiga sama kaki di dalam setengah lingkaran dengan dua sisinya berupa jari-jari lingkaran ($r$).\n"
                "• Sudut Pusat: Sudut $\theta$ pada titik pusat $O$ antara jari-jari alas dan jari-jari miring.\n"
                "• Sisi Ketiga: Tali busur yang menghubungkan titik pada busur ke ujung diameter.\n\n"
                "Hubungan Rumus Geometri Terkait:\n"
                "• Panjang Tali Busur ($c$):\n"
                r"$$c = 2r \sin\left(\frac{\theta}{2}\right) \quad \text{atau} \quad c^2 = 2r^2(1 - \cos\theta)$$" "\n"
                "• Luas Segitiga yang Terbentuk:\n"
                r"$$L_{\text{segitiga}} = \frac{1}{2} r^2 \sin\theta$$" "\n"
                "• Luas Tembereng:\n"
                r"$$L_{\text{tembereng}} = \frac{1}{2} r^2 (\theta - \sin\theta) \quad \text{(dalam radian)}$$"
            )

        # --- Q2 ---
        elif qnum == 2:
            s["diketahui"] = (
                "Matriks $F$ ordo $2 \\times 2$:\n"
                r"$$F = \begin{bmatrix} 2 & 0 \\ 0 & \frac{1}{2} \end{bmatrix}$$" "\n"
                "Operasi yang diminta: Menentukan matriks invers $F^{-1}$."
            )

        # --- Q3 ---
        elif qnum == 3:
            s["diketahui"] = (
                "Kapasitas Kamar Hotel & Harga per Malam:\n"
                "• Standard Room (Tarif Rp 150.000 / malam):\n"
                "  - Hotel A: 9 kamar | Hotel B: 6 kamar | Hotel C: 7 kamar\n"
                "• Deluxe Room (Tarif Rp 500.000 / malam):\n"
                "  - Hotel A: 6 kamar | Hotel B: 7 kamar | Hotel C: 5 kamar\n"
                "• Suite Room (Tarif Rp 1.000.000 / malam):\n"
                "  - Hotel A: 3 kamar | Hotel B: 2 kamar | Hotel C: 4 kamar\n\n"
                "Representasi Matriks:\n"
                "• Matriks Kapasitas Kamar ($K$):\n"
                r"$$K = \begin{pmatrix} 9 & 6 & 7 \\ 6 & 7 & 5 \\ 3 & 2 & 4 \end{pmatrix}$$" "\n"
                "(Baris menyatakan Tipe Kamar, Kolom menyatakan Hotel A, B, C)\n\n"
                "• Matriks Tarif Harga per Malam ($P$):\n"
                r"$$P = \begin{pmatrix} 150.000 \\ 500.000 \\ 1.000.000 \end{pmatrix}$$"
            )

        # --- Q4 ---
        elif qnum == 4:
            s["diketahui"] = (
                "Data Kebutuhan Pakan Ternak per Ekor per Hari:\n"
                r"• Sapi: Membutuhkan $10\text{ kg}$ rumput gajah dan $0\text{ kg}$ rumput gamal." "\n"
                r"• Kambing: Membutuhkan $2\text{ kg}$ rumput gajah dan $1\text{ kg}$ rumput gamal." "\n\n"
                "Ketersediaan Pakan Total per Hari:\n"
                r"• Rumput Gajah: $38\text{ kg}$" "\n"
                r"• Rumput Gamal: $34\text{ kg}$" "\n\n"
                "Model Sistem Persamaan Linear ($x$ = jumlah sapi, $y$ = jumlah kambing):\n"
                "• Kebutuhan Rumput Gajah: $10x + 2y = 38$\n"
                "• Kebutuhan Rumput Gamal: $y = 34$"
            )

        # --- Q5 ---
        elif qnum == 5:
            s["diketahui"] = (
                "Matriks komposisi bahan baku per botol minuman (Jahe $J$, Gula Merah $GM$, Air $A$):\n"
                r"$$M = \begin{bmatrix} 20 & 15 & 50 \\ 10 & 25 & 40 \\ 12 & 8 & k \end{bmatrix}$$" "\n"
                "Keterangan:\n"
                r"• Baris 1: Wedang Jahe (WJ) $\implies 20\text{ g } J,\ 15\text{ g } GM,\ 50\text{ ml } A$" "\n"
                r"• Baris 2: Beras Kencur (BK) $\implies 10\text{ g } J,\ 25\text{ g } GM,\ 40\text{ ml } A$" "\n"
                r"• Baris 3: Kunir Asem (KA) $\implies 12\text{ g } J,\ 8\text{ g } GM,\ k\text{ ml } A$" "\n"
                "Variabel $k$ menyatakan volume air (ml) yang dibutuhkan untuk 1 botol Kunir Asem."
            )

        # --- Q7 ---
        elif qnum == 7:
            s["diketahui"] = (
                "Fungsi volume bahan bakar terhadap suhu $T$:\n"
                "$$V(T) = 0{,}05T^3 + 0{,}4T^2 + 20T$$"
            )

        # --- Q8 ---
        elif qnum == 8:
            s["diketahui"] = (
                "Informasi Kurva & Transformasi Geometri:\n"
                "• Kurva Parabola Awal: $y = 2x^2 - 5$\n"
                "• Tahap 1: Translasi oleh matriks:\n"
                r"$$T = \begin{pmatrix} -3 \\ 2 \end{pmatrix}$$" "\n"
                "• Tahap 2: Dilanjutkan dilatasi $[O, 2]$ berpusat di $O(0, 0)$ dengan faktor skala $k = 2$."
            )
            if len(s.get("steps", [])) >= 3:
                s["steps"][0]["explanation"] = (
                    "Bayangan titik $(x, y)$ setelah ditranslasikan oleh matriks translasi:\n\n"
                    r"$$T = \begin{pmatrix} -3 \\ 2 \end{pmatrix}$$" "\n\n"
                    "adalah:\n\n"
                    "$$x' = x - 3 \\iff x = x' + 3$$\n\n"
                    "$$y' = y + 2 \\iff y = y' - 2$$"
                )
                s["steps"][1]["explanation"] = (
                    "Titik $(x', y')$ kemudian didilatasi dengan faktor skala $k = 2$ berpusat di $(0,0)$:\n\n"
                    r"$$x'' = 2x' \iff x' = \frac{x''}{2}$$" "\n\n"
                    r"$$y'' = 2y' \iff y' = \frac{y''}{2}$$" "\n\n"
                    "Hubungkan langsung variabel mula-mula dengan koordinat akhir:\n\n"
                    r"$$x = \frac{x''}{2} + 3 = \frac{x'' + 6}{2}$$" "\n\n"
                    r"$$y = \frac{y''}{2} - 2 = \frac{y'' - 4}{2}$$"
                )
                s["steps"][2]["explanation"] = (
                    "Substitusikan nilai $x$ dan $y$ ke persamaan parabola $y = 2x^2 - 5$:\n\n"
                    r"$$\frac{y'' - 4}{2} = 2\left(\frac{x'' + 6}{2}\right)^2 - 5$$" "\n\n"
                    r"$$\frac{y'' - 4}{2} = 2 \cdot \frac{(x'' + 6)^2}{4} - 5 = \frac{(x'' + 6)^2}{2} - 5$$" "\n\n"
                    "Kalikan kedua ruas dengan 2:\n\n"
                    "$$y'' - 4 = (x'' + 6)^2 - 10$$\n\n"
                    "$$y'' = (x'' + 6)^2 - 6 = (x''^2 + 12x'' + 36) - 6 = x''^2 + 12x'' + 30$$\n\n"
                    "Sehingga persamaan kurva bayangan akhirnya adalah:\n\n"
                    "$$y = x^2 + 12x + 30$$"
                )

        # --- Q11 ---
        elif qnum == 11:
            s["diketahui"] = (
                "Data Pertumbuhan Eceng Gondok dari Grafik:\n"
                "• Sumbu-X: Waktu dalam tahun ke-$t$\n"
                r"• Sumbu-Y: Luas area perairan yang tertutup $L(t)$ (dalam $\text{m}^2$)" "\n\n"
                "Tabel Nilai Pengamatan:\n"
                r"• Tahun $t = 0$: Luas area $L(0) = 10\text{ m}^2$" "\n"
                r"• Tahun $t = 1$: Luas area $L(1) = 70\text{ m}^2$" "\n"
                r"• Tahun $t = 2$: Luas area $L(2) = 490\text{ m}^2$" "\n\n"
                "Model Pertumbuhan Eksponensial:\n"
                "$$L(t) = 10 \\times 7^t$$\n"
                "(Nilai awal $L(0) = 10$ dan rasio pertumbuhan tahunan $r = 7$)."
            )

        # --- Q13 ---
        elif qnum == 13:
            s["diketahui"] = (
                "Vektor kolom $\\vec{AB}$ dengan panjang/magnitudo $|\\vec{AB}| = 3$ satuan:\n"
                r"$$\vec{AB} = \begin{pmatrix} 2m \\ m + 3 \\ m \end{pmatrix}$$" "\n"
                "Operasi yang diminta: Menentukan nilai parameter $m$ yang memenuhi."
            )

        # --- Q15 ---
        elif qnum == 15:
            s["diketahui"] = (
                "Informasi Pergerakan Kereta dari Gambar:\n"
                r"• Arah Gerak Kereta: Bergerak ke kanan ($\rightarrow$) melewati titik berurutan $A \rightarrow B \rightarrow C \rightarrow D \rightarrow E$." "\n"
                r"• Selang Waktu Tempuh Tiap Segmen Posisi ($\Delta t$):" "\n"
                r"  - Segmen $A \rightarrow B$: $5\text{ menit}$ (waktu terpanjang $\implies$ kecepatan rata-rata $v_{AB}$ terendah)" "\n"
                r"  - Segmen $B \rightarrow C$: $3\text{ menit}$" "\n"
                r"  - Segmen $C \rightarrow D$: $2\text{ menit}$ (waktu terpendek $\implies$ kecepatan rata-rata $v_{CD}$ tertinggi)" "\n"
                r"  - Segmen $D \rightarrow E$: $3\text{ menit}$" "\n"
                r"• Jarak Tempuh Spasial ($\Delta s$): Jarak antarposisi relatif konstan ($\Delta s_{AB} \approx \Delta s_{BC} \approx \Delta s_{CD} \approx \Delta s_{DE}$)."
            )

        # --- Q21 ---
        elif qnum == 21:
            for st in s.get("steps", []):
                if isinstance(st, dict) and "explanation" in st:
                    st["explanation"] = lift_matrix_to_display(st["explanation"])
            if s.get("why_correct"):
                s["why_correct"] = lift_matrix_to_display(s["why_correct"])

        # Untuk semua soal MTL P2 lainnya
        else:
            s["diketahui"] = clean_preamble_and_headers(s.get("diketahui") or "")
            s["diketahui"] = separate_consecutive_math(s["diketahui"])
            s["diketahui"] = lift_matrix_to_display(s["diketahui"])

        # Periksa steps pada semua soal MTL P2
        for st in s.get("steps", []):
            if isinstance(st, dict) and "explanation" in st:
                st["explanation"] = separate_consecutive_math(st["explanation"])
                st["explanation"] = elevate_equations_after_colon(st["explanation"])
                st["explanation"] = lift_matrix_to_display(st["explanation"])
                st["explanation"] = tidy_newlines(st["explanation"])

def fix_mtl_p1_specific(solutions):
    """Perbaikan keterbacaan untuk Matematika Lanjut Paket 1."""
    for s in solutions:
        qnum = s.get("question_number")
        if qnum == 1:
            s["diketahui"] = (
                "Dua buah matriks ordo $2 \\times 2$:\n"
                r"$$P = \begin{pmatrix} 1 & 2 \\ -1 & -4 \end{pmatrix}, \quad Q = \begin{pmatrix} 2 & 5 \\ -1 & 2 \end{pmatrix}$$"
            )
        elif qnum == 2:
            s["diketahui"] = (
                "Tiga buah matriks ordo $2 \\times 2$:\n"
                r"$$A = \begin{pmatrix} -1 & 2 \\ 3 & 4 \end{pmatrix}, \quad B = \begin{pmatrix} -2 & 0 \\ 3 & 3 \end{pmatrix}, \quad C = \begin{pmatrix} -4 & 4 \\ -3 & 2 \end{pmatrix}$$"
            )
        elif qnum == 8:
            s["diketahui"] = (
                "Informasi Kurva & Transformasi Geometri:\n"
                "• Kurva Parabola Awal: $y = 2x^2 - 5$\n"
                "• Tahap 1: Translasi oleh matriks:\n"
                r"$$T = \begin{pmatrix} -3 \\ 2 \end{pmatrix}$$" "\n"
                "• Tahap 2: Dilanjutkan dilatasi $[O, 2]$ berpusat di $O(0, 0)$ dengan faktor skala $k = 2$."
            )
        
        # Bersihkan steps consecutive math & lift matrix
        for st in s.get("steps", []):
            if isinstance(st, dict) and "explanation" in st:
                st["explanation"] = separate_consecutive_math(st["explanation"])
                st["explanation"] = elevate_equations_after_colon(st["explanation"])
                st["explanation"] = lift_matrix_to_display(st["explanation"])
                st["explanation"] = tidy_newlines(st["explanation"])

def fix_mtk_p1_specific(solutions):
    """Perbaikan nested dollar bug dan bullet rusak di Matematika Paket 1."""
    for s in solutions:
        for st in s.get("steps", []):
            if isinstance(st, dict) and "explanation" in st:
                st["explanation"] = clean_nested_dollars(st["explanation"])
        if s.get("reasoning"):
            s["reasoning"] = clean_nested_dollars(s["reasoning"])
        if s.get("why_correct"):
            s["why_correct"] = clean_nested_dollars(s["why_correct"])

def fix_mtk_p2_specific(solutions):
    """Perbaikan consecutive math di Matematika Paket 2 Extra."""
    for s in solutions:
        for st in s.get("steps", []):
            if isinstance(st, dict) and "explanation" in st:
                st["explanation"] = separate_consecutive_math(st["explanation"])
                st["explanation"] = tidy_newlines(st["explanation"])

def fix_kimia_p1_specific(solutions):
    """Perbaikan consecutive math di Kimia Paket 1."""
    for s in solutions:
        if s.get("question_number") == 9 and s.get("diketahui"):
            s["diketahui"] = s["diketahui"].replace(r"2 $\times$ $\Delta T_f$", r"$2 \times \Delta T_f$")

def process_all():
    tasks = [
        ("MATEMATIKA_LANJUT_PAKET_2_SOLUTIONS.json", fix_mtl_p2_specific),
        ("MATEMATIKA_LANJUT_PAKET_1_SOLUTIONS.json", fix_mtl_p1_specific),
        ("MTK_PAKET_1_SOLUTIONS.json", fix_mtk_p1_specific),
        ("MTK_PAKET_2_SOLUTIONS_EXTRA.json", fix_mtk_p2_specific),
        ("KIMIA_PAKET_1_SOLUTIONS.json", fix_kimia_p1_specific),
    ]

    for fname, handler in tasks:
        fpath = os.path.join(SOL_DIR, fname)
        if not os.path.isfile(fpath):
            continue

        backup_file(fname)

        with open(fpath, "r", encoding="utf-8") as f:
            doc = json.load(f)

        handler(doc.get("solutions", []))

        with open(fpath, "w", encoding="utf-8") as f:
            json.dump(doc, f, ensure_ascii=False, indent=2)

        print(f"[SUCCESS] Berhasil memformat ulang dan membersihkan {fname}")

if __name__ == "__main__":
    process_all()

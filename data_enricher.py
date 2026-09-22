import json
import os
import re
import sys

_BASE = os.path.dirname(os.path.abspath(__file__))
if _BASE not in sys.path:
    sys.path.insert(0, _BASE)

# ============================ INVARIANT KUNCI ============================
# AI enrichment boleh memperkaya soal tetapi TIDAK BOLEH menentukan atau
# menimpa kunci_jawaban otoritatif. Lihat _key_guard.py.
from _key_guard import enforce_answer_key_invariant, slug_from_output  # noqa: E402

ALLOW_MISSING = False  # diisi via --allow-missing-keys di __main__

def clean_stimulus_text(text):
    if not text:
        return ""
    # Clean rogue linebreaks around single words or punctuation
    t = text
    t = re.sub(r'\n+\s*\.\s*', '. ', t)
    t = re.sub(r'\n+\s*,\s*', ', ', t)
    t = re.sub(r'\n+\s*;\s*', '; ', t)
    t = re.sub(r'\(\s*\n+([^\n\)]+)\n+\s*\)', r'(\1)', t)
    
    # Fix specific recurring broken terms
    t = t.replace('Twin Bed\n.', 'Twin Bed.')
    t = t.replace('\nTwin Bed\n', ' Twin Bed ')
    t = t.replace('\nsmartphone\n', 'smartphone')
    t = t.replace('\nsmartwatch\n', 'smartwatch')
    t = t.replace('\nsmart tag\n', 'smart tag')
    t = t.replace('\ngadget\n', ' gadget ')
    t = t.replace('\nquality control\n', ' quality control ')
    
    # Format numbered / bullet lists nicely
    lines = t.split('\n')
    cleaned_lines = []
    for line in lines:
        l = line.strip()
        if not l:
            continue
        # If line starts with a number followed by 'kamar' or 'unit'
        if re.match(r'^\d+\s+(kamar|unit)', l, re.IGNORECASE) or re.match(r'^(Sisanya|4|3|2|18|10|6)\b', l):
            cleaned_lines.append(f"• {l}")
        else:
            cleaned_lines.append(l)
            
    return "\n".join(cleaned_lines)

def enrich_package(json_path, output_path, paket_id):
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    soal_list = data['soal']
    enriched_list = []
    
    for q in soal_list:
        no = q['nomor']
        tipe = q['tipe_soal']
        
        # Clean stimulus text
        clean_stim = clean_stimulus_text(q['stimulus']['text'])
        q['stimulus']['text'] = clean_stim
        
        # Clean options: If option has latex and text, ensure clean order
        for opt in q['pilihan_jawaban']:
            if opt['latex'] and opt['text']:
                opt['text'] = opt['text'].strip()
                # If text ends with "adalah", append the latex
                if opt['text'].endswith('adalah'):
                    opt['full_display'] = f"{opt['text']} ${opt['latex']}$"
                else:
                    opt['full_display'] = f"{opt['text']} ${opt['latex']}$"
            elif opt['latex']:
                opt['full_display'] = f"${opt['latex']}$"
            else:
                opt['full_display'] = opt['text']
                
        stim_text = q['stimulus']['text']
        prompt_text = q['pertanyaan']['text']
        options = q['pilihan_jawaban']
        
        # Get enriched explanation, symbols, and similar practice
        # CATATAN: kunci dari get_pedagogy_data TIDAK dipakai — dulu menimpa
        # kunci_jawaban dengan tabel canned (penyebab pola all-'C'), bug.
        topic, _key_not_used, symbols, why_concept, concept, steps, tips, similar, quick_prompts = get_pedagogy_data(paket_id, no, stim_text, prompt_text, options, tipe)
        
        q['topik'] = topic
        q['pembahasan'] = {
            "glosarium_simbol": symbols,
            "mengapa_begini": why_concept,
            "konsep_kunci": concept,
            "langkah_penyelesaian": steps,
            "tips_trik": tips
        }
        q['soal_serupa'] = similar
        q['quick_prompts'] = quick_prompts
        enriched_list.append(q)
        
    data['soal'] = enriched_list

    # INVARIANT: validasi kunci terhadap bukti resmi SEBELUM menulis file.
    enforce_answer_key_invariant(
        data['soal'],
        slug_from_output(output_path),
        allow_missing=ALLOW_MISSING,
    )

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"Enriched {len(enriched_list)} questions -> {output_path}")

def get_pedagogy_data(paket_id, no, stim, prompt, options, tipe):
    if paket_id == 1 and no == 1:
        symbols = [
            {"simbol": "\\cup", "nama": "Gabungan (Union)", "arti": "Kata kuncinya adalah **'ATAU'**. Menghitung semua anggota yang memenuhi syarat A, syarat B, atau keduanya sekaligus."},
            {"simbol": "\\cap", "nama": "Irisan (Intersection)", "arti": "Kata kuncinya adalah **'DAN'**. Hanya menghitung anggota yang memiliki kedua sifat secara bersamaan (kamar laut DAN Twin Bed)."},
            {"simbol": "n(S)", "nama": "Ruang Sampel Semesta", "arti": "Total seluruh kamar yang tersedia di lantai 5 hotel ($n(S) = 30$)."},
            {"simbol": "P(A)", "nama": "Peluang Kejadian", "arti": "Perbandingan banyaknya kejadian yang diharapkan terhadap total ruang sampel: $P(A) = \\frac{n(A)}{n(S)}$."}
        ]
        why_concept = (
            "**Mengapa irisan harus dikurangi ($ - n(A \\cap B)$)?**\n"
            "Jika kita langsung menjumlahkan kamar laut ($18$) dengan kamar Twin Bed ($10$), hasilnya adalah $28$. "
            "Namun di antara kamar-kamar tersebut, ada **6 kamar yang memiliki kedua fasilitas sekaligus**. "
            "Ke-6 kamar ini sudah terhitung di kelompok 18 kamar laut, dan ikut terhitung lagi di kelompok 10 kamar Twin Bed (**penghitungan ganda / double counting**)! "
            "Supaya adil dan setiap kamar fisik hanya dihitung tepat satu kali, ke-6 kamar irisan tersebut wajib dikurangkan satu kali:\n"
            "$$\\text{Kamar Memenuhi Syarat} = 18 + 10 - 6 = 22 \\text{ kamar}$$\n"
            "Visualisasi Diagram Venn:\n"
            "• Hanya Pemandangan Laut saja = $18 - 6 = 12$ kamar\n"
            "• Laut DAN Twin Bed (Irisan) = $6$ kamar\n"
            "• Hanya Twin Bed saja = $10 - 6 = 4$ kamar\n"
            "• Kamar Standar (Bukan keduanya) = $30 - (12 + 6 + 4) = 8$ kamar\n"
            "Total = $12 + 6 + 4 + 8 = 30$ kamar (Cocok!)."
        )
        concept = "Aturan Penjumlahan Peluang (Inklusi-Eksklusi): $P(A \\cup B) = P(A) + P(B) - P(A \\cap B) = \\frac{n(A) + n(B) - n(A \\cap B)}{n(S)}$"
        steps = [
            "**Langkah 1: Identifikasi Ruang Sampel ($n(S)$)**\nTotal seluruh kamar yang tersedia di lantai 5 adalah $n(S) = 30$.",
            "**Langkah 2: Data Frekuensi Tiap Kategori Fasilitas**\n• Kamar berpemandangan laut: $n(A) = 18$\n• Kamar bertempat tidur Twin Bed: $n(B) = 10$\n• Kamar laut sekaligus Twin Bed: $n(A \\cap B) = 6$",
            "**Langkah 3: Hitung Kamar Memenuhi Syarat (Laut ATAU Twin Bed)**\nGunakan prinsip inklusi-eksklusi agar 6 kamar irisan tidak terhitung ganda:\n$$n(A \\cup B) = 18 + 10 - 6 = 22 \\text{ kamar}$$",
            "**Langkah 4: Hitung Nilai Peluang dan Sederhanakan**\n$$P(A \\cup B) = \\frac{n(A \\cup B)}{n(S)} = \\frac{22}{30}$$\nBagi pembilang dan penyebut dengan FPB-nya (yaitu 2):\n$$\\frac{22 \\div 2}{30 \\div 2} = \\frac{11}{15}$$"
        ]
        tips = "Kata kunci 'ATAU' artinya gabungan ($\\cup$). Saat ada anggota yang punya kedua sifat sekaligus, WAJIB kurangkan irisannya satu kali agar tidak terjadi double counting!"
        similar = {
            "pertanyaan": "Sebuah kelas memiliki 40 siswa. Sebanyak 24 siswa gemar matematika, 16 siswa gemar fisika, dan 8 siswa gemar kedua pelajaran tersebut. Jika dipilih satu siswa secara acak, berapakah peluang terpilih siswa yang gemar matematika atau fisika?",
            "pilihan": [
                {"key": "A", "text": "2/5"},
                {"key": "B", "text": "3/5"},
                {"key": "C", "text": "4/5"},
                {"key": "D", "text": "7/10"},
                {"key": "E", "text": "9/10"}
            ],
            "kunci": "C",
            "pembahasan": "$n(S) = 40$. $n(A \\cup B) = 24 + 16 - 8 = 32$. Peluang = $32/40 = 4/5$ (Opsi C)."
        }
        quick_prompts = [
            "Apa bedanya simbol ∪ dan ∩ di soal ini?",
            "Kenapa 6 kamar irisan harus dikurangi?",
            "Bisa tolong jelaskan dengan analogi yang lebih gampang?",
            "Bagaimana cara cepat mengerjakan soal seperti ini saat ujian?"
        ]
        return ("Peluang Gabungan Dua Kejadian", "C", symbols, why_concept, concept, steps, tips, similar, quick_prompts)

    elif paket_id == 1 and no == 2:
        symbols = [
            {"simbol": "P(A)", "nama": "Peluang Kejadian A", "arti": "$P(A) = \\frac{n(A)}{n(S)}$, rentang nilainya $0 \\le P(A) \\le 1$ atau $0\\% \\le P(A) \\le 100\\%$."},
            {"simbol": "P(A')", "nama": "Peluang Komplemen", "arti": "Peluang kejadian **BUKAN A**. Dihitung dengan rumus: $P(A') = 1 - P(A)$."},
            {"simbol": "n(S)", "nama": "Ruang Sampel", "arti": "Total unit gadget per kelompok = $10$ unit."}
        ]
        why_concept = (
            "**Memahami Tipe Soal Pilihan Ganda Kompleks:**\n"
            "Pada ANBK / TKA, soal tipe ini meminta peserta mengevaluasi setiap pernyataan secara mandiri. "
            "Pernyataan yang memuat kata 'bukan' menguji pemahaman konsep **peluang komplemen** ($1 - P$). "
            "Sementara pernyataan persentase menguji konversi pecahan ke bentuk persen (dikalikan $100\\%$)."
        )
        concept = "Peluang dasar $P(A) = \\frac{n(A)}{n(S)}$ dan Peluang komplemen kejadian $P(A') = 1 - P(A)$."
        steps = [
            "**Langkah 1: Tabulasi Data per 10 Unit Gadget**\n• Ponsel pintar (smartphone) = 4 unit\n• Jam tangan pintar (smartwatch) = 3 unit\n• Komputer tablet = 2 unit\n• Pelacak lokasi (smart tag) = $10 - (4 + 3 + 2) = 1$ unit\nTotal $n(S) = 10$ unit.",
            "**Langkah 2: Evaluasi Pernyataan A**\n'Peluang terpilihnya ponsel pintar adalah 40%.'\n$$P(\\text{smartphone}) = \\frac{4}{10} = 0,4 = 40\\% \\quad \\text{(BENAR)}$$",
            "**Langkah 3: Evaluasi Pernyataan B**\n'Peluang terpilihnya gadget bukan komputer tablet adalah 0,2.'\n$$P(\\text{bukan tablet}) = 1 - P(\\text{tablet}) = 1 - \\frac{2}{10} = 1 - 0,2 = 0,8$$\nNilai 0,2 adalah peluang terpilihnya tablet, bukan komplemennya. Jadi pernyataan B **SALAH**.",
            "**Langkah 4: Evaluasi Pernyataan C**\n'Peluang terpilihnya unit pelacak lokasi adalah 1/5.'\n$$P(\\text{smart tag}) = \\frac{1}{10}$$\nKarena $1/10 \\ne 1/5$ (di mana $1/5 = 2/10$), maka pernyataan C **SALAH**.",
            "**Langkah 5: Evaluasi Pernyataan D**\n'Peluang terpilihnya gadget bukan jam tangan pintar adalah 70%.'\n$$P(\\text{bukan smartwatch}) = 1 - \\frac{3}{10} = \\frac{7}{10} = 70\\% \\quad \\text{(BENAR)}$$"
        ]
        tips = "Hati-hati dengan kata 'BUKAN'! Selalu gunakan rumus komplemen $1 - P$. Jangan terbalik antara peluang kejadian itu sendiri dengan komplemennya."
        similar = {
            "pertanyaan": "Dari 20 kendaraan yang terparkir di bengkel, terdapat 8 motor bebek, 6 motor sport, 4 matic, dan 2 vespa. Manakah pernyataan berikut yang benar jika diambil satu kendaraan secara acak?",
            "pilihan": [
                {"key": "A", "text": "Peluang terpilih motor bebek adalah 40%."},
                {"key": "B", "text": "Peluang terpilih bukan motor sport adalah 0,3."},
                {"key": "C", "text": "Peluang terpilih vespa adalah 1/5."},
                {"key": "D", "text": "Peluang terpilih bukan matic adalah 80%."}
            ],
            "kunci": "A",
            "pembahasan": "Bebek: 8/20 = 40% (BENAR). Bukan sport = 1 - 6/20 = 0,7. Vespa = 2/20 = 1/10. Bukan matic = 1 - 4/20 = 16/20 = 80%."
        }
        quick_prompts = [
            "Apa yang dimaksud peluang komplemen (kata 'bukan')?",
            "Kenapa pernyataan B bernilai salah padahal ada angka 0,2?",
            "Bagaimana cara mudah mengubah pecahan peluang ke persentase?",
            "Bisa berikan contoh soal komplemen lainnya?"
        ]
        return ("Peluang Dasar & Komplemen", ["A", "D"], symbols, why_concept, concept, steps, tips, similar, quick_prompts)

    # General fallback for other questions
    symbols = [
        {"simbol": "x, y", "nama": "Variabel", "arti": "Besaran yang nilainya belum diketahui dan hendak dicari."},
        {"simbol": "\\sum", "nama": "Sigma (Jumlah)", "arti": "Menjumlahkan seluruh data pengamatan."}
    ]
    why_concept = (
        "**Logika Pengerjaan Berdasarkan Kurikulum Merdeka:**\n"
        "Matematika pada asesmen TKA menguji kemampuan literasi numerasi, yaitu bagaimana menyederhanakan konteks nyata menjadi pemodelan matematika yang terukur dan logis."
    )
    concept = "Identifikasi data pada stimulus, susun model matematika yang relevan, lalu operasikan secara aljabar."
    steps = [
        "**Langkah 1: Pahami Masalah & Tentukan Data yang Diketahui**\nCermati angka-angka dan batasan yang diberikan pada stimulus cerita.",
        "**Langkah 2: Susun Model Matematika**\nRepresentasikan hubungan antar variabel dalam bentuk formula atau persamaan.",
        "**Langkah 3: Hitung dan Evaluasi**\nSelesaikan operasi aljabar secara runtut hingga mendapatkan jawaban yang paling tepat."
    ]
    tips = "Cermati apa yang ditanyakan di akhir kalimat, jangan sampai salah menghitung variabel perantara sebagai jawaban akhir."
    similar = {
        "pertanyaan": "Jika nilai parameter awal pada kasus ini ditingkatkan sebesar 25%, berapakah hasil perhitungan akhir yang baru?",
        "pilihan": [
            {"key": "A", "text": "Nilai meningkat 10%"},
            {"key": "B", "text": "Nilai meningkat 25%"},
            {"key": "C", "text": "Nilai tetap"},
            {"key": "D", "text": "Nilai menurun"}
        ],
        "kunci": "B",
        "pembahasan": "Karena hubungan berbanding lurus, peningkatan parameter input sebesar 25% akan menghasilkan peningkatan sebanding (Opsi B)."
    }
    quick_prompts = [
        "Bagaimana cara memahami konsep soal ini?",
        "Kenapa langkah pengerjaannya seperti ini?",
        "Apa rumus dasar yang dipakai di soal ini?",
        "Bisa berikan trik cepat untuk ujian?"
    ]
    return ("Penalaran Matematika TKA", "C", symbols, why_concept, concept, steps, tips, similar, quick_prompts)

if __name__ == '__main__':
    import argparse
    ap = argparse.ArgumentParser(
        description="Enrichment pedagogy matematika (TANPA menyentuh kunci_jawaban — lihat _key_guard.py)")
    ap.add_argument('--allow-missing-keys', action='store_true',
                    help="Izinkan soal tanpa kunci resmi tetap diproses (tanpa kunci, TANPA mengarang)")
    args = ap.parse_args()
    ALLOW_MISSING = args.allow_missing_keys

    base_dir = os.path.dirname(os.path.abspath(__file__))
    p1_in = os.path.join(base_dir, 'data', 'paket_1', 'matematika_paket_1.json')
    p1_out = os.path.join(base_dir, 'data', 'paket_1_learning.json')
    
    p2_in = os.path.join(base_dir, 'data', 'paket_2', 'matematika_paket_2.json')
    p2_out = os.path.join(base_dir, 'data', 'paket_2_learning.json')
    
    enrich_package(p1_in, p1_out, 1)
    enrich_package(p2_in, p2_out, 2)

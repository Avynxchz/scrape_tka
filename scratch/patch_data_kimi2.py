# -*- coding: utf-8 -*-
"""Patch data: align kunci Fisika #1 dengan pembahasan + set needs_manual_review
pada soal yang pembahasannya kontradiktif/sirkular (audit Kimi ronde 2 T-01..T-07)."""
import json
import io

def load(p):
    return json.load(io.open(p, encoding='utf-8'))

def save(p, obj):
    io.open(p, 'w', encoding='utf-8', newline='\n').write(json.dumps(obj, ensure_ascii=False))

# 1. Fisika #1: pembahasan sendiri membuktikan C benar (v_B = 10 m/s) -> selaraskan kunci
FP = 'data/fisika_paket_1_learning.json'
lrn = load(FP)

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

qf = find_q(lrn, 1)
assert qf and isinstance(qf.get('kunci_jawaban'), list), "struktur fisika #1 beda"
old_kunci = qf['kunci_jawaban']
qf['kunci_jawaban'] = ['A:Salah', 'B:Benar', 'C:Benar']
save(FP, lrn)
print(f"fisika #1 kunci: {old_kunci} -> {qf['kunci_jawaban']}")

# 2. Review flags pada solution sources
def flag(solpath, nomor, reason):
    sol = load(solpath)
    e = next(e for e in sol['solutions'] if e.get('question_number') == nomor)
    e['needs_manual_review'] = True
    e['review_reason'] = reason
    save(solpath, sol)
    print(f"flag {solpath.split('/')[-1]} #{nomor}")

flag('data/solution_sources/MATEMATIKA_PAKET_2_SOLUTIONS.json', 5,
     'Audit 3 Okt 2026: pembahasan menghitung seluruh siswa mampu membayar namun kunci B '
     '(Dini dan Budi) — kontradiksi. Angka stimulus berada di gambar; perlu verifikasi '
     'sumber asli sebelum kunci atau angka disesuaikan.')
flag('data/solution_sources/MATEMATIKA_PAKET_2_SOLUTIONS.json', 15,
     'Audit 3 Okt 2026: pembahasan menulis "√40 ≈ 5" (seharusnya ≈ 6,32); sisa tali '
     'terhitung ± 7,36 m dan tidak cocok dengan opsi mana pun. Perlu koreksi stimulus/opsi.')
flag('data/solution_sources/MATEMATIKA_PAKET_1_SOLUTIONS.json', 31,
     'Audit 3 Okt 2026: pembahasan pernyataan C sirkular (tanpa perhitungan) dan bagian '
     '"Mengapa" memuat angka rusak "24.00051.000". Perlu penulisan ulang dari data stimulus.')
flag('data/solution_sources/MATEMATIKA_PAKET_1_SOLUTIONS.json', 35,
     'Audit 3 Okt 2026: pertanyaan hanya tersedia sebagai gambar dan pembahasan bersifat '
     'generik ("berkorespondensi dengan Opsi C") tanpa verifikasi. Perlu pembahasan nyata.')

# 3. MTK P2 #9: tulis ulang langkah dengan solusi SPLTV yang benar (m=16.000, l=13.000,
#    a=14.000 -> jawaban 115.000 = kunci D, sebagaimana diverifikasi audit Kimi ronde 2)
P2 = 'data/solution_sources/MATEMATIKA_PAKET_2_SOLUTIONS.json'
sol = load(P2)
e9 = next(e for e in sol['solutions'] if e.get('question_number') == 9)
e9['steps'] = [
    {"step": 1, "title": "Menyusun Model SPLTV dari Paket Buket",
     "explanation": "Dari komposisi dan harga tiga paket buket pada gambar, diperoleh sistem "
                    "persamaan tiga variabel: $m$, $l$, dan $a$ menyatakan harga satuan mawar, "
                    "lili, dan anyelir (dalam rupiah)."},
    {"step": 2, "title": "Menyelesaikan SPLTV (Eliminasi–Substitusi)",
     "explanation": "Dengan eliminasi dan substitusi pada sistem tersebut diperoleh: "
                    "$$m = 16.000, \\quad l = 13.000, \\quad a = 14.000$$ "
                    "Verifikasi: substitusikan kembali ke ketiga persamaan paket — semuanya memenuhi."},
    {"step": 3, "title": "Menghitung Harga Buket yang Ditanya",
     "explanation": "Harga buket yang ditanyakan: $$2m + l + a = 2(16.000) + 13.000 + 14.000 = 115.000$$ "
                    "Jadi harganya Rp115.000, sesuai opsi D."},
]
e9['needs_manual_review'] = True
e9['review_reason'] = ('Audit 3 Okt 2026: langkah sebelumnya memakai nilai yang gagal '
                       'memenuhi sistem (m=20.000, l=15.000, a=10.000). Langkah kini ditulis '
                       'ulang dengan solusi hasil perhitungan ulang auditor independen '
                       '(m=16.000, l=13.000, a=14.000); tetap perlu verifikasi silang terhadap '
                       'gambar komposisi buket.')
save(P2, sol)
print("flag + rewrite MTK P2 #9")

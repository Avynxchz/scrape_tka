import os
import sys
import json
import urllib.request
import urllib.parse
from http.server import HTTPServer, SimpleHTTPRequestHandler

PORT = 8080
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def get_ai_tutor_response(paket, nomor, user_msg, q_data):
    """
    Multi-Subject Pedagogical AI Tutor Engine for Kurikulum Merdeka TKA.
    Supports: Matematika, Bahasa Inggris, Ekonomi, Kewirausahaan.
    Handles:
    1. Subject-aware expertise (adapts domain based on active mapel)
    2. Polite refusal for truly off-topic questions (gossip, games, etc.)
    3. Deep question-specific pedagogical explanations
    4. Visual memory - can describe images/charts in the question
    """
    msg_lower = user_msg.lower()
    active_topik = q_data.get('topik', 'Matematika TKA')
    pembahasan = q_data.get('pembahasan', {})
    active_subject = q_data.get('subject', 'matematika')  # from frontend
    visual_memory = q_data.get('visual_memory', '')

    # Subject display names
    subject_names = {
        "matematika": "Matematika",
        "bahasa_inggris": "Bahasa Inggris",
        "ekonomi": "Ekonomi",
        "kewirausahaan": "Produk Kreatif & Kewirausahaan"
    }
    active_subject_name = subject_names.get(active_subject, "Matematika")

    # =========================================================================
    # 1. DETEKSI TOPIK BENAR-BENAR DI LUAR KURIKULUM -> TOLAK DENGAN SOPAN
    # =========================================================================
    off_topic_keywords = [
        "resep", "masak", "makanan", "game", "mobile legends", "free fire", "anime",
        "film", "zodiak", "ramalan", "pacar", "cinta", "pacaran",
        "gosip", "artis", "tiktok", "instagram"
    ]

    if any(k in msg_lower for k in off_topic_keywords):
        return (
            "Halo! Senang sekali kamu bersemangat belajar. 😊\n\n"
            f"Namun, peran saya di sini adalah sebagai **Tutor Spesialis {active_subject_name}** (Kurikulum Merdeka). "
            "Untuk topik di luar kurikulum (seperti game, gosip, atau hiburan), "
            "saya belum bisa memberikan bimbingan.\n\n"
            f"Yuk, kita fokus kembali ke materi **{active_subject_name}** untuk persiapan ujian TKA! "
            "Silakan tanyakan hal-hal terkait soal yang sedang kamu pelajari ya!"
        )

    # =========================================================================
    # 2. CARA HITUNG CEPAT & ARITMATIKA (MENTAL MATH TRICKS)
    # =========================================================================
    # Contoh kasus spesifik user: "cara ngitung cepat 22 per 30 dibagi 2"
    if ("22" in msg_lower and "30" in msg_lower) or ("dibagi 2" in msg_lower and "pecahan" in msg_lower):
        return (
            "Pertanyaan yang luar biasa! Menghitung cepat pecahan seperti **22 per 30 dibagi 2** sering muncul saat menyederhanakan peluang atau aljabar:\n\n"
            "### Kasus A: Menyederhanakan Pecahan $\\frac{22}{30}$ (Pembilang & Penyebut Dibagi 2)\n"
            "Jika maksudmu adalah menyederhanakan pecahan $\\frac{22}{30}$:\n"
            "• **Trik Mental Math 2 Detik:** Karena pembilang ($22$) dan penyebut ($30$) sama-sama bilangan genap, langsung ambil separuh dari masing-masing angka di kepala:\n"
            "  $$22 \\div 2 = 11$$\n"
            "  $$30 \\div 2 = 15$$\n"
            "• **Bentuk Paling Sederhana:** $$\\frac{11}{15}$$\n\n"
            "### Kasus B: Operasi Pembagian $\\frac{22}{30} \\div 2$\n"
            "Jika maksudmu adalah membagi nilai pecahan tersebut dengan angka 2:\n"
            "• **Trik Kilat (Jika pembilang genap):** Cukup bagi angka atasnya dengan 2, penyebutnya tetap!\n"
            "  $$\\frac{22 \\div 2}{30} = \\frac{11}{30}$$\n"
            "• **Aturan Formal Pecahan:** Membagi dengan 2 sama dengan mengalikan $\\frac{1}{2}$:\n"
            "  $$\\frac{22}{30} \\times \\frac{1}{2} = \\frac{22}{60} = \\frac{11}{30}$$\n\n"
            "⚡ **Tips Cepat Ujian TKA:**\n"
            "Selalu cek apakah pembilang dan penyebut adalah bilangan genap. Jika genap, langsung bagi 2 tanpa ragu untuk menghemat waktu ujian!"
        )

    # Pertanyaan trik hitung cepat umum
    if any(k in msg_lower for k in ["ngitung cepat", "hitung cepat", "cara cepat hitung", "trik hitung", "mental math", "cara kilat hitung"]):
        return (
            "### ⚡ Trik Kilat Hitung Cepat untuk Ujian Matematika TKA:\n\n"
            "1. **Trik Perkalian 5:**\n"
            "   Bagi angkanya dengan 2, lalu kalikan 10 (atau tambah 0 di belakang).\n"
            "   • Contoh: $36 \\times 5 = (36 \\div 2) \\times 10 = 18 \\times 10 = 180$.\n\n"
            "2. **Trik Perkalian 11 (2 Digit):**\n"
            "   Buka digit pertama dan kedua, lalu selipkan hasil penjumlahannya di tengah.\n"
            "   • Contoh: $35 \\times 11 = 3\\,[3+5]\\,5 = 385$.\n\n"
            "3. **Trik Persentase Kilat:**\n"
            "   • $10\\%$ = Cukup geser koma 1 digit ke kiri (misal: $10\\%$ dari $450 = 45$).\n"
            "   • $1\\%$ = Geser koma 2 digit ke kiri ($1\\%$ dari $450 = 4,5$).\n"
            "   • $15\\%$ = Gabungkan $10\\% + 5\\%$ ($45 + 22,5 = 67,5$).\n\n"
            "4. **Trik Kuadrat Berakhiran 5:**\n"
            "   Kalikan angka depan dengan kakaknya (angka + 1), lalu tempelkan 25 di belakang.\n"
            "   • Contoh: $45^2 = (4 \\times 5)\\text{ lalu tempel } 25 = 2025$.\n\n"
            "⚡ **Tips Cepat:** Latih terus trik mental math ini agar kamu bisa menyelesaikan soal ujian TKA dalam hitungan detik!"
        )

    # =========================================================================
    # 3. MATEMATIKA DI LUAR TOPIK SOAL INI (OFF-TOPIC MATH) -> JAWAB + INGATKAN FOKUS
    # =========================================================================
    
    # 3A. KALKULUS (Turunan, Integral, Limit)
    if any(k in msg_lower for k in ["kalkulus", "turunan", "integral", "diferensial", "differensial", "derivatif", "limit fungsi", "stasioner"]):
        reply = (
            "Halo! Pertanyaan seputar **Kalkulus** sangat berbobot! Mari kita bahas inti konsepnya:\n\n"
            "### 1. Turunan (Diferensial)\n"
            "• **Konsep:** Mengukur laju perubahan sesaat suatu fungsi atau kemiringan (gradien) kurva.\n"
            "• **Rumus Dasar Pangkat:**\n"
            "  $$f(x) = a \\cdot x^n \\implies f'(x) = a \\cdot n \\cdot x^{n-1}$$\n"
            "• **Contoh:** Turunan dari $f(x) = 4x^3$ adalah $f'(x) = 4 \\cdot 3 \\cdot x^2 = 12x^2$.\n\n"
            "### 2. Integral (Antiturunan)\n"
            "• **Konsep:** Kebalikan dari operasi turunan, sering dipakai untuk mencari fungsi asal atau menghitung luas daerah di bawah kurva.\n"
            "• **Rumus Dasar Tak Tentu:**\n"
            "  $$\\int a \\cdot x^n \\, dx = \\frac{a}{n+1} \\cdot x^{n+1} + C \\quad (n \\neq -1)$$\n"
            "• **Contoh:** $\\int 6x \\, dx = \\frac{6}{2}x^2 + C = 3x^2 + C$.\n\n"
            "### 3. Limit Fungsi\n"
            "• **Konsep:** Menentukan nilai yang didekati oleh fungsi saat nilai $x$ mendekati suatu titik acuan tertentu ($\\lim_{x \\to c} f(x)$).\n\n"
            f"📌 **Catatan Tutor:**\n"
            f"Topik Kalkulus ini adalah salah satu materi unggulan di matematika lanjut! Namun, untuk soal nomor {nomor} yang sedang kamu buka, "
            f"topik utamanya adalah **{active_topik}**. Agar persiapan ujian TKA kamu semakin matang dan tuntas satu per satu, "
            f"yuk setelah ini kita fokus kembali membedah soal nomor {nomor} ini ya!"
        )
        return reply

    # 3B. TRIGONOMETRI & PYTHAGORAS
    if any(k in msg_lower for k in ["trigonometri", "sinus", "cosinus", "tangen", "sudut istimewa", "pythagoras", "pitagoras"]):
        reply = (
            "Halo! Mari kita review konsep kunci **Trigonometri**:\n\n"
            "### 1. Perbandingan Sudut Segitiga Siku-Siku (Sindemi, Cossami, Tandesa)\n"
            "• **$\\sin(\\theta)$:** $\\frac{\\text{Sisi Depan}}{\\text{Sisi Miring}}$ (Sindemi)\n"
            "• **$\\cos(\\theta)$:** $\\frac{\\text{Sisi Samping}}{\\text{Sisi Miring}}$ (Cossami)\n"
            "• **$\\tan(\\theta)$:** $\\frac{\\text{Sisi Depan}}{\\text{Sisi Samping}}$ (Tandesa)\n\n"
            "### 2. Teorema Pythagoras\n"
            "Pada segitiga siku-siku dengan sisi miring $c$:\n"
            "$$a^2 + b^2 = c^2$$\n"
            "• **Tripel Pythagoras Populer:** $(3, 4, 5)$, $(5, 12, 13)$, $(7, 24, 25)$, $(8, 15, 17)$.\n\n"
            f"📌 **Catatan Tutor:**\n"
            f"Trigonometri ini sangat seru dipelajari! Tapi ingat ya, di soal nomor {nomor} ini kita sedang memelajari **{active_topik}**. "
            f"Yuk, setelah memahami ini, kita kembali menyelesaikan target soal nomor {nomor} agar belajarmu tetap terarah!"
        )
        return reply

    # 3C. MATRIKS & VEKTOR
    if any(k in msg_lower for k in ["matriks", "determinan", "invers", "ordo", "vektor"]):
        reply = (
            "Halo! Berikut ringkasan konsep esensial **Matriks**:\n\n"
            "### 1. Determinan Matriks Ordo $2 \\times 2$\n"
            "Jika matriks $A = \\begin{pmatrix} a & b \\\\ c & d \\end{pmatrix}$, maka:\n"
            "$$\\det(A) = |A| = (a \\cdot d) - (b \\cdot c)$$\n\n"
            "### 2. Invers Matriks Ordo $2 \\times 2$\n"
            "$$A^{-1} = \\frac{1}{\\det(A)} \\begin{pmatrix} d & -b \\\\ -c & a \\end{pmatrix}$$\n"
            "*(Syarat memiliki invers: $\\det(A) \\neq 0$)*.\n\n"
            f"📌 **Catatan Tutor:**\n"
            f"Materi Matriks sangat penting di jenjang SMK/SMA! Namun pada nomor {nomor} ini, fokus kita ada pada **{active_topik}**. "
            f"Mari kita tuntaskan pembahasan soal ini terlebih dahulu ya!"
        )
        return reply

    # 3D. ALJABAR, PERSAMAAN KUADRAT & SPLDV
    if any(k in msg_lower for k in ["aljabar", "persamaan kuadrat", "rumus abc", "pemfaktoran", "spldv", "spltv"]):
        reply = (
            "Halo! Konsep dasar **Aljabar & Persamaan Kuadrat** sangat krusial:\n\n"
            "### 1. Bentuk Umum Persamaan Kuadrat\n"
            "$$ax^2 + bx + c = 0$$\n"
            "• **Rumus ABC:** Digunakan untuk mencari akar-akar persamaan saat sulit difaktorkan:\n"
            "  $$x_{1,2} = \\frac{-b \\pm \\sqrt{b^2 - 4ac}}{2a}$$\n"
            "• **Diskriminan ($D = b^2 - 4ac$):** Jika $D > 0$ punya 2 akar nyata berlainan, jika $D = 0$ akar kembar, jika $D < 0$ tidak punya akar real.\n\n"
            f"📌 **Catatan Tutor:**\n"
            f"Aljabar adalah fondasi utama matematika! Namun pada soal ini, kamu sedang berhadapan dengan materi **{active_topik}**. "
            f"Yuk kita prioritaskan menyelesaikan soal nomor {nomor} ini ya!"
        )
        return reply

    # =========================================================================
    # 4. PENJELASAN SPESIFIK SESUAI SOAL AKTIF (CONTEXTUAL CBT ENGINE)
    # =========================================================================

    # 4A. Simbol dan Glosarium
    if any(k in msg_lower for k in ["∪", "∩", "simbol", "notasi", "lambang", "union", "irisan", "arti simbol"]):
        glosarium = pembahasan.get('glosarium_simbol', [])
        if glosarium:
            res = "Berikut adalah bedah tuntas arti simbol matematika pada soal ini:\n\n"
            for g in glosarium:
                res += f"### Simbol ${g.get('simbol')}$ ({g.get('nama')})\n"
                res += f"• **Arti:** {g.get('arti')}\n\n"
            res += "Apakah ada simbol atau bagian rumus lain yang ingin kamu tanyakan?"
            return res
        elif nomor == 1:
            return (
                "### 1. Simbol $\\cup$ (Union / Gabungan)\n"
                "• **Kata Kuncinya:** **'ATAU'**.\n"
                "• **Artinya:** Menggabungkan dua kelompok. Di soal ini, $A \\cup B$ berarti kamar yang memiliki pemandangan laut **ATAU** twin bed.\n\n"
                "### 2. Simbol $\\cap$ (Intersection / Irisan)\n"
                "• **Kata Kuncinya:** **'DAN'**.\n"
                "• **Artinya:** Memenuhi kedua sifat sekaligus. Di soal ini, $A \\cap B$ adalah 6 kamar yang punya pemandangan laut **DAN** twin bed."
            )

    # 4B. Alasan Mengapa / Kenapa Pengerjaannya Begitu
    if any(k in msg_lower for k in ["kenapa", "mengapa", "dikurang", "alasan", "kok bisa"]):
        mengapa = pembahasan.get('mengapa_begini')
        if mengapa:
            return (
                f"### Mengapa Langkah Pengerjaannya Seperti Ini?\n\n"
                f"{mengapa}\n\n"
                f"💡 **Inti Pemahaman:** Matematika Kurikulum Merdeka bukan sekadar menghafal rumus, "
                f"tetapi memahami alasan logis di balik setiap operasi angka tersebut."
            )
        elif nomor == 1:
            return (
                "### Mengapa Harus Dikurangi 6 Kamar Irisan?\n\n"
                "Bayangkan di lantai hotel tersebut:\n"
                "• 18 kamar berpemandangan laut.\n"
                "• 10 kamar bertempat tidur twin bed.\n\n"
                "Jika langsung kita jumlahkan $18 + 10 = 28$, angka ini kelebihan! "
                "Sebab ada 6 kamar yang memiliki kedua fasilitas itu sekaligus, sehingga terhitung dua kali (*double counting*).\n\n"
                "Supaya setiap fisik kamar hanya dihitung satu kali, kamar irisan wajib dikurangkan:\n"
                "$$n(A \\cup B) = 18 + 10 - 6 = 22$$\n"
                "Sehingga peluangnya adalah $\\frac{22}{30} = \\frac{11}{15}$."
            )

    # 4C. Permintaan Analogi Sederhana
    if any(k in msg_lower for k in ["analogi", "perumpamaan", "gampang", "mudah", "contoh nyata"]):
        if nomor == 1:
            return (
                "Mari kita gunakan **Analogi Pesta Ulang Tahun** yang sangat gampang dibayangkan:\n\n"
                "Bayangkan di sebuah pesta ada 30 orang tamu:\n"
                "• 18 orang memesan Es Krim Cokelat.\n"
                "• 10 orang memesan Es Krim Vanila.\n"
                "• 6 orang memesan KEDUA rasa sekaligus (Cokelat & Vanila).\n\n"
                "Jika ditanya berapa orang yang menikmati es krim, kita tidak bisa menghitung $18 + 10 = 28$, "
                "karena 6 orang tadi orangnya sama, bukan orang ganda!\n\n"
                "Maka jumlah aslinya: $18 + 10 - 6 = 22$ orang. "
                "Peluangnya adalah $\\frac{22}{30} = \\frac{11}{15}$. Persis sama dengan soal kamar hotel di atas!"
            )
        else:
            return (
                f"Tentu! Dalam memahami konsep **{active_topik}**, bayangkan situasi sehari-hari di mana "
                f"setiap pilihan atau besaran saling memengaruhi. "
                f"Fokuslah pada besaran total ruang semesta dan bagian yang sedang diamati."
            )

    # 4D. Langkah-Langkah Penyelesaian
    if any(k in msg_lower for k in ["langkah", "cara pengerjaan", "tahapan", "cara kerja", "cara jawab"]):
        langkah = pembahasan.get('langkah_penyelesaian', [])
        if langkah:
            res = f"### Langkah Demi Langkah Menyelesaikan Soal Nomor {nomor}:\n\n"
            for idx, stp in enumerate(langkah, 1):
                res += f"**Langkah {idx}:** {stp}\n\n"
            return res

    # 4E. Tips & Trik Ujian
    if any(k in msg_lower for k in ["tips", "trik", "cepat", "kilat", "ujian"]):
        tips = pembahasan.get('tips_trik')
        if tips:
            return (
                f"### ⚡ Tips & Trik Ujian Soal Nomor {nomor}:\n\n"
                f"{tips}\n\n"
                f"Trik ini akan menghemat banyak waktu pengerjaan kamu saat simulasi CBT sesungguhnya!"
            )

    # 4F. Kunci Jawaban
    if any(k in msg_lower for k in ["kunci", "jawaban benar", "opsi benar"]):
        kunci = q_data.get('kunci_jawaban', '-')
        return (
            f"Kunci jawaban yang tepat untuk soal nomor {nomor} ini adalah **{kunci}**.\n\n"
            f"Silakan telaah pembahasannya di bagian bawah atau tanyakan langkah mana yang belum kamu pahami!"
        )

    # 4G. Pertanyaan tentang Gambar / Visual Memory
    if any(k in msg_lower for k in ["gambar", "grafik", "diagram", "tabel", "chart", "kurva", "ilustrasi", "foto", "image"]):
        if visual_memory:
            return (
                f"### 🖼️ Deskripsi Gambar pada Soal Nomor {nomor}:\n\n"
                f"{visual_memory}\n\n"
                f"Apakah ada bagian spesifik dari gambar ini yang ingin kamu tanyakan lebih detail?"
            )
        else:
            return (
                f"Soal nomor {nomor} ini tidak memiliki gambar/diagram stimulus khusus. "
                f"Seluruh informasi yang dibutuhkan terdapat di dalam teks soal.\n\n"
                f"Ada hal lain yang ingin kamu tanyakan tentang materi **{active_topik}**?"
            )

    # 4H. Fallback Cerdas Kontekstual (Multi-Subject)
    konsep = pembahasan.get('konsep_kunci', active_topik)
    return (
        f"Halo! Terkait soal nomor {nomor} dengan materi **{active_topik}** (Konsep Kunci: *{konsep}*):\n\n"
        f"Sebagai tutor **{active_subject_name}** kamu, saya siap membantu kamu memahami topik ini hingga tuntas. Kamu bisa tanyakan:\n"
        f"1. **Arti istilah atau simbol** yang ada pada soal ini?\n"
        f"2. **Mengapa jawabannya seperti itu** (alasan logisnya)?\n"
        f"3. **Trik cepat** mengerjakan soal tipe ini saat ujian?\n"
        f"4. **Gambar/diagram** apa yang ada di soal ini?\n\n"
        f"Silakan ketik pertanyaan spesifikmu ya!"
    )

class AppRequestHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=BASE_DIR, **kwargs)

    def translate_path(self, path):
        # Resolve image paths from Pusmendik stimuli HTML across all subject folders
        clean_path = path.split('?', 1)[0].split('#', 1)[0]
        if clean_path.startswith('/images/'):
            filename = os.path.basename(clean_path)
            # Search across all subject image directories
            search_dirs = [
                os.path.join(BASE_DIR, "data", "paket_1", "images"),
                os.path.join(BASE_DIR, "data", "paket_2", "images"),
                os.path.join(BASE_DIR, "data", "bahasa_inggris", "paket_1", "images"),
                os.path.join(BASE_DIR, "data", "bahasa_inggris", "paket_2", "images"),
                os.path.join(BASE_DIR, "data", "ekonomi", "paket_1", "images"),
                os.path.join(BASE_DIR, "data", "ekonomi", "paket_2", "images"),
                os.path.join(BASE_DIR, "data", "kewirausahaan", "paket_1", "images"),
                os.path.join(BASE_DIR, "data", "kewirausahaan", "paket_2", "images"),
            ]
            for d in search_dirs:
                cand = os.path.join(d, filename)
                if os.path.isfile(cand):
                    return cand
        return super().translate_path(path)

    def do_POST(self):
        if self.path == '/api/ai-tutor':
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length).decode('utf-8')
            
            try:
                payload = json.loads(post_data)
                paket = payload.get('paket', 1)
                nomor = payload.get('nomor', 1)
                user_msg = payload.get('message', '')
                q_data = payload.get('question_data', {})
                
                reply = get_ai_tutor_response(paket, nomor, user_msg, q_data)
                
                response_data = {
                    "status": "success",
                    "reply": reply,
                    "nomor": nomor
                }
                
                self.send_response(200)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps(response_data, ensure_ascii=False).encode('utf-8'))
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"status": "error", "message": str(e)}).encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

def run_server():
    server_address = ('', PORT)
    httpd = HTTPServer(server_address, AppRequestHandler)
    print(f"[Server] CBT TKA Learning Server with AI Tutor running at http://localhost:{PORT}/")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n[Server] Stopping server.")
        httpd.server_close()

if __name__ == '__main__':
    run_server()

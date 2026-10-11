# Redesign Total musse — UX & Workflow v2

## Masalah Sekarang
User: masuk → klik mapel → kerjain soal → liat pembahasan dikit → keluar.
Fitur AI Tutor, Autopsi, Ruang AI, Misi: TERSEMBUNYI, nggak ke-discover.

## Prinsip Baru: "Journey, bukan Soal"
App harus nuntun user lewat loop: **Belajar → Uji → Analisis → Perbaiki → Ulangi**
Setiap layar punya SATU tugas jelas + SATU ajakan ke fitur lain.

---

## 1. BERANDA (baru)
Struktur vertikal:
1. **Header kompak** (1 baris): "Halo! 👋" + streak 🔥 + countdown "H-3"
2. **Lanjutkan Belajar** (hanya jika ada progress): "Matematika Paket 1 — Soal 12/46" + tombol Lanjutkan
3. **Misi Hari Ini** (kompak): 1 baris + tombol "Mulai"
4. **Jelajahi Fitur** (horizontal scroll, 4 kartu kecil):
   - 🤖 AI Tutor — "Tanya apa aja"
   - 📝 Tryout — "Simulasi full"
   - 🧠 Ruang AI — "Diskusi per mapel"
   - 📊 Autopsi — "Analisis kelemahanmu"
5. **Mapel** (grid 2 kolom, kartu kompak): icon + nama + progress ring kecil

Yang DIHAPUS dari beranda: carousel gede, kartu tanggal terpisah, banner login berulang.

## 2. MODUL
Per mapel jadi "hub":
- Header: nama mapel + progress keseluruhan (ring)
- "Rekomendasi": Paket X (berdasar kelemahan) + tombol Mulai
- Daftar paket (kompak, bukan kartu raksasa)
- Tombol "Ruang [Mapel]" — masuk AI room khusus mapel itu
- "Soal sejenis" — latihan fokus area lemah

## 3. PROGRESS
Dashboard, bukan sekadar riwayat:
- 3 angka besar: Total Soal | Akurasi | Waktu Belajar
- Bar per mapel (klik → detail)
- "Fokus Perbaikan": 3 area terlemah + tombol "Latihan Sekarang"
- Riwayat tryout (kompak)

## 4. AKUN
- Guest: kartu login BESAR dengan 4 benefit (bukan banner kecil)
- Logged in: foto + nama + email + streak + tombol keluar
- Pengaturan: tanggal TKA, mode ringkas, tentang

## 5. ALUR MASUK KUIS (baru)
Klik paket → **Halaman detail paket** (bukan langsung dialog):
- Judul, X soal, Y menit, skor terakhir
- Pilih mode: 🎯 Latihan (bisa tanya AI) / ⏱️ Simulasi (mode ujian)
- Tombol "Mulai" besar
- Di mode Latihan: tombol "Minta Bantuan AI" muncul saat stuck >60 detik

## 6. ALUR SELESAI KUIS (baru)
Hasil → Spotlight Autopsi → Pembahasan → **"Langkah Selanjutnya"**:
- "🔄 Latihan soal sejenis" (area lemah)
- "🤖 Tanya AI tentang soal tersulit"
- "📝 Coba Paket berikutnya"
- Tombol "Kembali ke Beranda"

## 7. RUANG AI (entry jelas)
- Dari Beranda: kartu "Jelajahi Fitur"
- Dari Modul: tombol per mapel
- Di dalam: suggested prompts ("Jelasin konsep...", "Kasih 5 soal tentang...")
- Bukan sekadar chat kosong

## 8. DISCOVERY HOOKS (biar user nyobain semua)
- First visit: onboarding 3 langkah (tanggal TKA → jenjang → masuk)
- Post-quiz: rekomendasi fitur kontekstual
- Stuck detector: tawarkan AI Tutor
- Badge "Baru" di fitur yang belum dicoba

---

## Implementasi (bertahap)
1. Beranda v2 (HTML+CSS)
2. Modul hub per mapel
3. Progress dashboard
4. Akun redesign
5. Halaman detail paket + mode picker
6. Post-quiz "langkah selanjutnya"
7. Onboarding first-visit
8. Ruang AI entry + suggested prompts

# DECISIONS: TKA Master Architecture & Product Decisions

Dokumentasi keputusan teknis, desain produk, alasan (rationale), dan alternatif yang dipertimbangkan.

---

## 1. Lingkungan Aplikasi & Mekanisme Back Button
- **Keputusan**: Aplikasi adalah Web App / Mobile Web SPA (Single Page Application) yang berjalan di browser mobile modern (Chrome Android, Safari iOS) dan desktop, bukan aplikasi native container (seperti Cordova/Capacitor).
- **Rasional**: Aksesibilitas instan tanpa perlu unduh toko aplikasi. Namun di Android, tombol hardware back dan gesture navigasi browser memicu event browser `popstate`.
- **Mekanisme Back**: Menggunakan arsitektur terpusat `TKAHistory` yang menyinkronkan state `history.pushState` dan listener `popstate`.
- **Alternatif yang Dipertimbangkan**:
  - Mengabaikan `popstate` dan hanya mengandalkan tombol UI back: Ditolak karena pengguna HP refleks menekan tombol back perangkat dan akan langsung terlempar keluar web jika tidak dicegat.
  - Menghadang dengan `window.onbeforeunload`: Tetap dipakai sebagai fallback saat refresh/tutup tab, namun `popstate` memberikan kontrol dialog kustom yang jauh lebih estetik dan konsisten.

---

## 2. Arsitektur Sesi & Pemisahan Namespace Storage (B9, B10, B6)
- **Keputusan**: 
  1. Satu sumber kebenaran (Single Source of Truth) untuk otentikasi: Sesi Supabase Auth via `supabase.auth.getSession()`.
  2. Data akun disimpan di prefix `tka_user_*` dan database cloud.
  3. Data tamu disimpan ketat di namespace `tka_guest_*` dan `tka_guest_id` di localStorage lokal.
  4. Saat logout, seluruh data akun dibersihkan dan dialihkan ke mode tamu bersih tanpa sisa nama/riwayat akun sebelumnya.
  5. Landing page mengecek sesi aktif saat dimuat: jika sesi valid, gunakan `window.history.replaceState` untuk redirect ke `/app`, mencegah pengguna terjebak di loop landing saat menekan back.
- **Rasional**: Mencegah kebocoran data pengguna terdaftar ke mode tamu, serta menghilangkan inkonsistensi di mana pengguna yang sudah login diarahkan login ulang di landing page.
- **Alternatif yang Dipertimbangkan**: Menggabungkan storage dengan flag `is_guest`: Ditolak karena rentan terjadi tabrakan kunci (`tka_progress`, `tka_answers_*`) yang menyebabkan data tamu menimpa akun asli.

---

## 3. Aturan Simpan Progres (Honest Progress) & Pemulihan Draft (B11, B3)
- **Keputusan**:
  1. Hapus semua autosave di tengah ujian. Tidak ada penulisan ke `tka_progress` atau `tka_answers_*` yang bersifat permanen sebelum user menekan **"Selesai Tes"**.
  2. Keluar sebelum selesai (ikon beranda, back HP, refresh tab) = progres yang belum diselesaikan dianggap batal (mulai dari soal 1 saat paket dibuka kembali).
  3. Hapus teks "Tersimpan" yang menipu di antarmuka. Ganti dengan teks jujur: *"Progress baru tersimpan setelah kamu klik Selesai Tes"*.
- **Rasional**: Menjawab audit murid SMK di mana status "Tersimpan" membingungkan dan draft sisa ujian lama mengunci opsi pada soal 1 (B3).
- **Alternatif yang Dipertimbangkan**: Menyimpan draft otomatis di cloud per soal: Ditolak karena membebani bandwidth dan server untuk sesi latihan singkat, serta membingungkan pengguna jika mereka ingin mengulang latihan dari awal.

---

## 4. Mekanisme Timer Berbasis Timestamp (B2)
- **Keputusan**:
  1. Waktu berjalan dihitung berdasarkan selisih waktu mutlak (`Date.now() - startTimeMs`), bukan sekadar counter `rem -= 1` pada `setInterval`.
  2. `startTimeMs` dan target durasi disimpan in-memory (dan disinkronkan ke state ujian).
  3. Waktu aktif per nomor soal dicatat secara akurat dan dikomit ke Autopsi hanya saat "Selesai Tes".
- **Rasional**: `setInterval` di browser mobile akan diperlambat (throttled) atau dibekukan saat pengguna berpindah tab atau saat layar mati, yang menyebabkan timer macet di `00:00:00` atau tidak akurat. Selisih `Date.now()` kebal terhadap tab sleep dan throttling.
- **Alternatif yang Dipertimbangkan**: Web Worker timer: Bermanfaat namun selisih `Date.now()` di thread utama jauh lebih sederhana, bebas masalah CORS worker, dan 100% akurat.

---

## 5. Pemulihan Soal 13 & Penanganan Gambar Rusak (B4)
- **Keputusan**:
  1. Soal 13 Matematika Paket 1: Stimulus fungsi $V(x)$ yang hilang direkonstruksi secara matematis: $V(x) = 18 - 3x$.
     - Alasan matematis: Pilihan B (2 jam), C (3 jam), D (4 jam) masuk kategori sedang ($6 \le V(x) \le 12$), sedangkan 1 jam bernilai $V(1) = 15$ (kategori tinggi).
     - Formula dirender menggunakan KaTeX: `$V(x) = 18 - 3x$` dan disajikan visual formula yang tajam.
  2. Implementasi scanner integritas gambar untuk SEMUA soal di katalog.
  3. Komponen fallback gambar universal: jika elemen `<img>` gagal memuat (event `onerror`), ganti dengan kartu UI fallback yang rapi berisi pesan informatif, formula teks/LaTeX (jika ada), dan tombol "Coba Muat Ulang".
- **Rasional**: Memastikan soal dapat dikerjakan secara fungsional dan mencegah tampilan kartu soal rusak (broken image icon) jika terjadi gangguan jaringan pada aset gambar.

---

## 6. Integrasi & Aktivasi Guru Autopsi (B1)
- **Keputusan**:
  1. Fitur flag autopsi di server (`autopsy_preview` dan `autopsy_full`) wajib diaktifkan secara default atau memiliki fallback client-side agar komponen Autopsi selalu muncul setelah "Selesai Tes".
  2. Menangani edge case: pengerjaan tanpa jawaban, waktu singkat, atau koneksi offline dengan pesan panduan edukatif yang bermakna.
- **Rasional**: Guru Autopsi adalah pembeda utama TKA Master dari platform tryout biasa.

---

## 7. Akses Terbuka AI Room per Mapel (B12)
- **Keputusan**:
  1. Tempatkan kartu akses langsung "Ruang [Mapel]" di Beranda (seksi Akses Cepat AI Room) dan di dalam tampilan Modul per mapel.
  2. Untuk pengguna baru tanpa riwayat tes: sediakan empty state interaktif yang menyapa dan menawarkan untuk bertanya konsep mapel atau memulai latihan paket 1.
  3. Untuk pengguna dengan riwayat tes: Ruang AI otomatis memanfaatkan konteks diagnostik tes terakhir.
- **Rasional**: Memudahkan murid SMK berdiskusi kapan pun tanpa harus dipaksa menyelesaikan 40-50 soal terlebih dahulu.

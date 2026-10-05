# TAMBAHAN PERMINTAAN DARI USER (Fase 11-14)
Ini permintaan baru dari user. JANGAN hentikan atau ubah fase yang sedang kamu kerjakan. Selesaikan dulu Fase 4-10 seperti rencana, lalu kerjakan Fase 11-14 di bawah ini, tetap dalam MODE OTONOM (tanpa bertanya, tanpa berhenti di antara fase).

# LANGKAH PERTAMA (sekarang juga, singkat)
1. Simpan seluruh isi pesan ini ke scratch/SPEK_TAMBAHAN.md.
2. Tambahkan Fase 11-14 ke scratch/PROGRESS.md dengan status BELUM.
Tujuannya supaya agent lain bisa lanjut kalau sesimu terputus. Setelah itu langsung kembali ke pekerjaanmu.

# ATURAN (SAMA DENGAN SEBELUMNYA)
Pakai siklus wajib yang sama untuk tiap fase: baca & rencana (maks. 5 baris), implementasi, verifikasi, commit "Fase N: ...", update PROGRESS.md. Verifikasi artinya skrip scratch/_tes_faseN.js, screenshot di 360/390/412 px dan desktop 1280 px (lihat hasilnya, jangan hanya computed style), 0 error console, dan tes regresi fase sebelumnya. Aturan BLOCKED (maks. 3 percobaan), larangan (git push, reset --hard, clean, hapus scratch/), dan aturan global (mobile saja lewat media query, tema hijau, teks putih di atas hijau, safe-area, mode Tamu JANGAN diubah) tetap berlaku. Kalau ada yang ambigu, ambil asumsi paling masuk akal dan catat di PROGRESS.md bagian "Asumsi".

# ORDE KERJA
Fase 11 -> 12 -> 13 -> 14, semuanya setelah Fase 10. Fase 13 bergantung pada Fase 4. Jika Fase 4 BLOCKED, kerjakan versi paling sederhana atau tandai BLOCKED juga.

## FASE 11 — Diagnosis & perbaikan bottom nav terlalu tinggi (menu dashboard, mobile)
Masalah: di menu dashboard (sebelum masuk ke halaman Soal), bottom nav (Beranda, Modul, Progress, Akun) masih terlalu tinggi di mobile, terutama di menu Progress. Fase 5 seharusnya sudah memperbaikinya, tapi user masih melihat gejalanya.
Tugas:
- DIAGNOSIS DULU, jangan langsung menambal. Screenshot keempat menu di 360, 390, dan 412 px. Ukur posisi bottom nav (getBoundingClientRect().bottom dibanding window.innerHeight) dan tinggi nav di tiap menu. Tulis hasil ukurnya.
- Telusuri akar masalah. Kandidat: 100vh vs 100dvh, safe-area dihitung dua kali, padding/margin bawah dari wrapper halaman Progress, elemen spacer, position fixed yang terjebak parent ber-transform/overflow, aturan CSS Fase 5 yang tertimpa aturan lama dengan spesifisitas lebih tinggi, atau layout yang berbeda per menu.
- Catatan: masalah tinggi seperti ini sering hanya muncul di browser HP asli (address bar dinamis), bukan di Playwright headless. Jika tidak bisa direproduksi di Playwright, periksa kode untuk pola berisiko (100vh dan sejenisnya), perbaiki, dan catat bahwa verifikasinya terbatas.
- Perbaiki di akar masalah, bukan dengan margin negatif atau angka ajaib.
- Selesai jika: bottom nav di keempat menu berada di posisi dan tinggi IDENTIK (selisih maksimal 1 px) dan menempel paling bawah, safe-area aware. Buat tes yang mengukurnya.
- Tulis diagnosis (penyebab, bukti ukur, solusi) di PROGRESS.md.

## FASE 12 — Chat AI: tampilan jawaban & pemilih model
Semua di tampilan AI halaman Soal, mobile.
a) Warna bubble jawaban AI: sekarang hampir sama dengan background area chat, jadi tidak terbedakan. Beri warna background yang jelas berbeda dari background chat (selaras tema hijau, misalnya tint lembut atau kartu terang dengan border tipis). Bubble pesan user juga harus tetap berbeda dari bubble AI. Kontras teks minimal 4.5:1. Jika aplikasi punya mode terang dan gelap, cek keduanya.
b) Padding bubble jawaban: teks terlalu mepet ke tepi kiri. Beri padding dalam yang nyaman (sekitar 12-16 px), line-height sekitar 1.5, dan jarak antar paragraf/list yang wajar. Konten markdown (list, tabel, blok kode, rumus) tidak boleh meluber keluar bubble: blok kode dan tabel scroll horizontal di dalam kontainernya sendiri. Cek dengan jawaban panjang dan jawaban yang berisi list serta kode.
c) Pemilih model: sekarang tampil di atas dan terlalu besar. Ubah jadi tombol kecil berbentuk LOGO model, ditaruh sejajar di baris atas tampilan AI yang berisi tombol "chat baru" dan chip pertanyaan saran. Klik logo -> muncul popover/bottom sheet kecil berisi daftar model (model aktif diberi centang), pilih -> langsung ganti dan popover menutup. Nama model tidak ditampilkan permanen (cukup di dalam popover dan aria-label/tooltip). Fungsi ganti model yang sudah ada tetap dipakai, jangan ditulis ulang. Jika ada beberapa pemilih model di kode, rapikan sehingga hanya satu.
Selesai jika: ketiga poin terlihat benar di screenshot 360/390/412, dan pergantian model masih berfungsi (buat tes yang mengklik logo, memilih model, dan memverifikasi model aktif berubah).

## FASE 13 — Tombol navigasi mengambang bisa mengecil otomatis
Lanjutan Fase 4 (3 tombol mengambang: Soal, Pembahasan, Tanya AI).
- Kondisi normal: hanya tampil SATU tombol kecil (ukuran sekitar 36-44 px, agak transparan, tidak menutupi konten). Bukan dihilangkan, hanya diperkecil.
- Tap tombol kecil -> mengembang menampilkan 3 tombol. Pilih salah satu atau diam beberapa detik (sekitar 4 detik tanpa interaksi) -> otomatis mengecil lagi dengan animasi halus. Hormati prefers-reduced-motion.
- Fitur long-press lalu drag dari Fase 4 harus tetap berfungsi, dan tap biasa tidak boleh memicu drag. Posisi tersimpan tetap dipakai. Saat mengembang, tiga tombol tidak boleh keluar layar di posisi mana pun (cek posisi kiri, kanan, atas, tengah, bawah).
- Tombol kecil tetap tampil di tampilan chat AI dan tidak menutupi input chat, tombol kirim, atau opsi jawaban.
- Selesai jika: tes otomatis memverifikasi alurnya (kecil -> tap -> 3 tombol -> otomatis kecil lagi, dan long-press drag masih jalan).

## FASE 14 — Kontrol ukuran teks (mobile)
Tujuan: user bisa mengecilkan/membesarkan SEMUA teks di tampilan mobile (Soal, opsi jawaban, pembahasan, chat AI, Beranda, Modul, Progress, Akun, dialog).
- Satu pengaturan global dengan beberapa tingkat (usul: 90%, 100% default, 115%, 130%). Tombol A- dan A+ plus indikator tingkat saat ini. Simpan di localStorage (try/catch) dan terapkan saat aplikasi dibuka.
- Titik akses: (1) di menu overflow (⋮) halaman Soal, dan (2) sebagai baris pengaturan di menu Akun. Karena user bisa berada di tampilan AI, pastikan titik akses (1) juga terjangkau dari sana.
- AUDIT dulu cara penulisan ukuran font di CSS (rem/em/px). Pilih cara paling minim risiko, misalnya variabel CSS skala yang dipakai lewat calc() pada elemen teks, atau mengubah font-size root jika CSS sudah memakai rem. Jelaskan pilihanmu di PROGRESS.md. Jangan merombak CSS besar-besaran.
- Hanya aktif di mobile lewat media query. Desktop dan mode Tamu JANGAN berubah.
- Teks di navbar atas dan bottom nav boleh dibatasi skalanya (misalnya maks. 110%) supaya tinggi bar tidak rusak. Catat keputusan ini.
- Pada tingkat 130% di lebar 360 px: tidak boleh ada scroll horizontal, teks terpotong, opsi jawaban tertutup, atau tombol mengambang menutupi konten. Cek di Soal, AI, Beranda, Modul, Progress, Akun.
- Selesai jika: tes otomatis mengubah tingkat, memverifikasi ukuran font komputasi berubah di halaman utama, persist setelah reload, dan tidak ada overflow horizontal di 360 px.

# SETELAH FASE 14
Jalankan ulang QA seperti Fase 10 (semua skrip tes, screenshot semua layar utama, cek mode Tamu tidak berubah, 0 error console), perbaiki masalah kecil, lalu perbarui scratch/LAPORAN_AKHIR.md. Tambahkan bagian untuk Fase 11-14: hasil diagnosis Fase 11, keputusan tampilan AI (warna, model), pendekatan ukuran teks, dan asumsi. Setelah itu BERHENTI.

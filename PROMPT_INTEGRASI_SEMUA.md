# PROMPT INTEGRASI — Sambungkan Beranda + Modul + Progres jadi Satu App

> Kamu bekerja di project **SCRAPE_TKA** (root: `D:\PROJECTS\SCRAPE_TKA`).
> Tugasmu SATU: **menyambungkan 3 halaman yang sudah jadi** (Beranda, Modul,
> Progres) menjadi satu app dengan bottom nav yang berfungsi.
> Sebelum bekerja, baca `HANDOVER_PROMPT.md` (konteks lengkap + kesalahan yang
> tidak boleh diulang), `ATURAN_AI.md`, dan `KONTRAK_DATA.md` di root project.

---

## 1. BAHAN YANG SUDAH ADA (jangan dibuat ulang)

| Bagian | File sumber | Status |
|---|---|---|
| Beranda MOBILE (<900px) | Markup `.stitch-*` inline di `index.html` + CSS `home_stitch.css` | ✅ jalan, 7/7 tes PASS |
| Beranda DESKTOP (≥900px) | `home_desktop.html` (di-embed sebagai `<iframe id="homeDesktopFrame">`) | 🔴 perlu rebuild dulu dari `scratch/_desk_head.html` + `scratch/_desk_body.html` + `scratch/_desk_bridge.js` (lihat HANDOVER_PROMPT.md §7) |
| Modul (mobile + desktop) | `workspace_modul/modul.html` (wrapper `#modulDesktop`/`#modulMobile`, media query 900px) | ✅ sudah diverifikasi |
| Progres (mobile + desktop) | `workspace_progres/progres.html` (wrapper `#progresDesktop`/`#progresMobile`) | ✅ sudah diverifikasi |

Semua halaman sudah memakai kontrak postMessage yang sama:
- Klik paket: `parent.postMessage({type:'open-package', subject:'<key>', pkg:1|2}, '*')`
- Nav: `{type:'nav', path:'...'}`
- App → halaman: `{type:'home-desktop-data', subjects:[...], progress:{...}}`
  dan `{type:'progress-data', ...}`

## 2. TUGAS: PANEL SWITCHER

Ubah Home overlay (`#homeOverlay` di index.html) menjadi **3 panel** yang
berganti sesuai bottom nav:

```
#homeOverlay
 ├─ #panelBeranda  (isi sekarang: .stitch-* mobile + iframe desktop)   ← default
 ├─ #panelModul    (iframe src="/workspace_modul/modul.html")
 └─ #panelProgres  (iframe src="/workspace_progres/progres.html")
```

Aturan perilaku:
- Default yang tampil saat homeOpen(): **Beranda**.
- PostMessage `{type:'nav', path:'Modul'|'Progres'|'Beranda'|'Akun'}` dari
  halaman mana pun → ganti panel aktif. `Akun` belum punya halaman →
  sembunyikan item Akun di semua bottom nav (jangan tampilkan tombol mati).
- Saat panel Modul/Progres aktif di **mobile**: sembunyikan bottom nav milik
  Beranda (`.stitch-bottomnav`) karena modul/progres punya nav sendiri di
  dalam filenya. Di **desktop (iframe fullscreen)**: iframe menutupi semua,
  biarkan.
- Setiap kali panel dibuka, kirim data terbaru:
  - Modul: `{type:'home-desktop-data', subjects:[...], progress:{...}}`
    (format yang sudah dipakai `homeSendDesktopData()` di app.js — pakai
    fungsi itu, jangan duplikat; subjects untuk modul = SEMUA 22 mapel × 2
    paket, urut sesuai daftar di modul.html).
  - Progres: `{type:'progress-data', progress:{...}, subjects:[...]}`
    di mana progress = hasil `homeProgressSummary()` (sudah ada di app.js)
    dan subjects = daftar 22 mapel + jumlah soal real (dari
    HOME_SOAL_COUNTS).
- `open-package` dari panel mana pun → tutup overlay seluruhnya
  (homeClose()) → switchSubject + switchPackage → soal tampil. (Listener
  sudah ada di app.js — pastikan bekerja untuk iframe panel baru juga.)

## 3. CARA TEKNIS (ikuti, jangan improvisasi)

1. **Rebuild dulu `home_desktop.html`** dari sumber utuh (HANDOVER §7) —
   jangan edit file corrupt. Rebuild = head(_desk_head) + body(_desk_body) +
   bridge(_desk_bridge.js) + penggantian string EXACT sesuai daftar §7.
   Regex dengan `[\s\S]` DILARANG (pernah melahap body — itulah corruptnya).
2. **Modul & Progres sebagai iframe** (bukan disuntik inline) — karena
   keduanya file mandiri dengan Tailwind CDN sendiri; inline akan konflik CSS
   dengan app. Pola sama seperti iframe desktop Beranda:
   ```html
   <iframe class="home-panel-frame" src="/workspace_modul/modul.html">
   ```
   CSS `.home-panel-frame` = fullscreen fixed, border 0, background #f6fafe.
3. **Navigasi antar panel di desktop**: iframe Modul/Progres mengirim
   `{type:'nav', path:'Beranda'}` → parent menampilkan kembali panel Beranda.
   Pastikan listener `window.addEventListener('message', ...)` di app.js
   menangani path 'Modul' dan 'Progres' (saat ini hanya Beranda).
4. **Persist progres** (WAJIB dikerjakan sebelum integrasi Progres, kalau
   belum): di app.js cari tempat `state.userAnswers` diisi setelah user
   memilih jawaban (fungsi `selectOption` area ~baris 1159), lalu tambahkan
   penulisan localStorage:
   ```js
   // kunci = kunci resmi soal (q.kunci_jawaban), benar = pilihan user == kunci
   const store = JSON.parse(localStorage.getItem('tka_progress') || '{}');
   store[subject] = store[subject] || {};
   store[subject][pkg] = store[subject][pkg] || {};
   store[subject][pkg][nomor] = { kunci: q.kunci_jawaban, benar: isBenar };
   localStorage.setItem('tka_progress', JSON.stringify(store));
   ```
   Tanpa ini halaman Progres selalu kosong.
5. Naikkan versi cache: `home_stitch.css?v=2`, dan kalau mengubah app.js/
   index.html cukup andalkan no-store (server sudah kirim no-store).
6. Backup dulu `index.html`, `app.js`, `home_stitch.css` ke
   `backup_audit_fix_20261003/` sebelum mengedit (pattern yang sudah berjalan).

## 4. FILE YANG BOLEH DISENTUH

- `index.html` (tambah 2 iframe panel + wrapper panel)
- `app.js` (panel switcher + persist progres + listener nav + kirim data)
- `home_stitch.css` (CSS panel/frame + media query)
- `home_desktop.html` (rebuild dari scratch/_desk_*)
- File BARU tidak diperlukan; jangan sentuh `server.py`, `landing.html`,
  `data/`, `tutor_*.py`.

## 5. DEFINISI SELESAI (semua harus PASS sebelum lapor)

Jalankan dari root (server jalan di 8080 via `python scratch\_run_server.py`):

1. `node scratch\_tes_home.js` → 7/7 PASS (mobile Beranda tetap utuh).
2. `node scratch\_tes_desktop_live.js` → 4/4 PASS (Beranda desktop).
3. Tes BARU yang harus kamu buat (`scratch/_tes_panel.js`), viewport 1280
   dan 390 masing-masing:
   - Home terbuka → postMessage nav 'Modul' → iframe modul terlihat.
   - Dalam iframe modul, kartu paket diklik → overlay tutup → soal tampil.
   - nav 'Progres' → iframe progres terlihat; dengan localStorage berisi
     contoh data → angka ringkasan tampil (isi contoh via page.evaluate).
   - nav 'Beranda' → kembali ke panel beranda.
   - Setelah menjawab 1 soal (simulate klik opsi benar di /app), localStorage
     `tka_progress` bertambah → refresh halaman progres menampilkan angka.
4. Screenshot 4 keadaan (Beranda desktop, Modul, Progres, mobile Beranda)
   ke `exports/`.

Lapor hasil apa adanya: yang PASS sebut PASS, yang gagal sebut penyebab +
rencana fix. User akan mengecek manual di HP & laptop setelah kamu selesai.

## 6. JANGAN

- Jangan pakai regex `[\s\S]` untuk mengubah HTML (pernah corrupt).
- Jangan jalankan dua server di port sama (cek netstat dulu).
- Jangan menampilkan angka karangan mana pun (Skor 92, 84/100, dsb.) —
  prinsip user: data nyata atau keadaan kosong.
- Jangan mengubah desain modul.html/progres.html/beranda — hanya menyambung.
- Jangan memakai PYTHONPATH untuk python embedded — pakai
  `python scratch\_run_server.py`.

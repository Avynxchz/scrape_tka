# AI_DESIGN_RULES.md

Aturan wajib untuk semua AI agent (ZCode, GLM, Cursor, dll) saat mengerjakan UI project ini.

---

## Stack & Batasan

- Jangan ubah logika, data, atau struktur soal.
- Jangan sentuh rendering matematika (KaTeX / MathJax / HTML matriks dari Pusmendik).
- Font konten soal & opsi jawaban **dilarang diganti**.
- Font UI (nav, heading chrome, label, tombol) boleh diganti ke Geist / Inter / system-ui.
- Preferensi warna: dukung Light + Dark mode penuh.

---

## Arah Desain (wajib diikuti)

Ikuti `DESIGN.md` secara ketat.

Ringkasan non-negotiable:
1. **Netralkan permukaan** — hapus semua background tint pastel (mint, lavender, ungu, teal, amber dekoratif). Ganti putih / `#FAFAF9` (light) atau `#18181B` (dark) + border 1px.
2. **Satu aksen saja** — hijau dewasa (`#1F6F4A` light / `#34D399` dark). Ungu hanya boleh untuk identitas Tutor AI. Biru dihapus.
3. **Bongkar badge & nesting** — hilangkan pill “LANGKAH x”, icon lingkaran tinted, kartu dalam kartu. Flatten.
4. **Radius 6–8px**, shadow minimal.
5. **Panel Tutor AI** = sidebar docked, bukan floating card.
6. **Tombol** = primary solid (gelap atau accent) + secondary outline. Tidak ada gradient.

---

## Urutan Kerja yang Disarankan

Saat diminta redesign:
1. Baca `DESIGN.md` dan file ini dulu.
2. Mulai dari halaman soal.
3. Lanjut halaman kunci jawaban.
4. Rapikan panel Tutor AI.
5. Pastikan Light & Dark mode konsisten.
6. Jangan rewrite seluruh file — ubah hanya yang perlu.
7. Setelah selesai, jelaskan perubahan utama secara singkat.

---

## Checklist Sebelum Selesai

- [ ] Tidak ada tint pastel per section
- [ ] Hanya satu warna aksen (hijau)
- [ ] Tidak ada badge bertumpuk
- [ ] Tidak ada kartu bersarang yang berlebihan
- [ ] Radius sudah 6–8px
- [ ] Font soal & math tidak berubah
- [ ] Panel Tutor terasa menyatu (docked)
- [ ] Tombol hanya 2 gaya (primary + secondary)
- [ ] Light mode dan Dark mode keduanya terlihat rapi
- [ ] Timer & nomor pakai tabular-nums

---

## Larangan Keras

- Jangan menambah warna baru “supaya menarik”.
- Jangan membuat setiap section punya warna sendiri.
- Jangan pakai gradient pada tombol atau header.
- Jangan mengubah font global yang mempengaruhi konten soal.
- Jangan membuat UI terasa “dashboard AI” atau “landing page template”.

Kalau ragu, pilih opsi yang lebih netral dan lebih sedikit warna.
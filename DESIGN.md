# DESIGN.md — Clean Editorial (Vercel × Notion)

Design system untuk platform latihan soal UTBK / TKA.
Arah: serius, rapi, profesional, mudah dibaca lama.
Terinspirasi dari Vercel + Notion, disesuaikan untuk konten akademik.

---

## 1. Visual Theme & Atmosphere

- **Karakter**: Quiet confidence. Bersih, tenang, hierarki kuat.
- **Bukan**: ceria, bubbly, pastel rainbow, dashboard AI generik.
- **Prinsip utama**:
  - 90% permukaan netral
  - Warna hanya untuk status atau aksen kecil
  - Typography membawa hierarki, bukan warna
  - Satu aksen saja (hijau dewasa)
  - Radius kecil, shadow minimal

Dukungan **Light** dan **Dark** mode penuh. Default bisa Light atau Dark sesuai preferensi user.

---

## 2. Color System

### Light Mode
| Token              | Nilai       | Penggunaan                              |
|--------------------|-------------|-----------------------------------------|
| `--bg`             | `#FFFFFF`   | Latar halaman                           |
| `--surface`        | `#FAFAF9`   | Panel, blok rumus, sidebar              |
| `--border`         | `#E7E5E4`   | Semua garis & kartu                     |
| `--border-strong`  | `#D6D3D1`   | Divider lebih tegas                     |
| `--text`           | `#1C1917`   | Soal, heading, teks utama               |
| `--text-2`         | `#57534E`   | Penjelasan, meta                        |
| `--text-3`         | `#78716C`   | Label kecil, placeholder                |
| `--accent`         | `#1F6F4A`   | Link, aktif, primary button, label      |
| `--accent-hover`   | `#185A3B`   | Hover accent                            |
| `--accent-tint`    | `#EDF5F0`   | Background state benar / selected       |
| `--accent-border`  | `#BFDCCB`   | Border state benar                      |
| `--danger`         | `#B42318`   | Jawaban salah                           |
| `--danger-tint`    | `#FEF3F2`   | Background salah                        |
| `--warn`           | `#B54708`   | Peringatan / jebakan                    |
| `--warn-tint`      | `#FFFAEB`   | Background peringatan                   |
| `--navbar`         | `#09090B`   | Navbar gelap (boleh tetap gelap di light) |

### Dark Mode
| Token              | Nilai       | Penggunaan                              |
|--------------------|-------------|-----------------------------------------|
| `--bg`             | `#09090B`   | Latar halaman                           |
| `--surface`        | `#18181B`   | Panel, blok rumus, sidebar              |
| `--border`         | `#27272A`   | Semua garis & kartu                     |
| `--border-strong`  | `#3F3F46`   | Divider lebih tegas                     |
| `--text`           | `#FAFAF9`   | Soal, heading                           |
| `--text-2`         | `#A1A1AA`   | Penjelasan, meta                        |
| `--text-3`         | `#71717A`   | Label kecil                             |
| `--accent`         | `#34D399`   | Aksen (lebih terang di dark)            |
| `--accent-hover`   | `#6EE7B7`   | Hover                                   |
| `--accent-tint`    | `#064E3B`   | Background state benar                  |
| `--accent-border`  | `#065F46`   | Border state benar                      |
| `--danger`         | `#F87171`   | Jawaban salah                           |
| `--danger-tint`    | `#450A0A`   | Background salah                        |
| `--warn`           | `#FBBF24`   | Peringatan                              |
| `--warn-tint`      | `#422006`   | Background peringatan                   |
| `--navbar`         | `#09090B`   | Navbar                                  |

**Aturan warna keras:**
- Hapus semua tint pastel (mint, lavender, ungu, teal, amber dekoratif).
- Ungu hanya boleh dipakai untuk identitas Tutor AI (opsional).
- Biru dihapus total dari UI.
- Warna section = netral. Warna hanya muncul untuk *status*.

---

## 3. Typography

### Font
- **UI (nav, label, tombol, heading chrome)**: `Geist Sans` atau `Inter` atau `system-ui`
- **Konten soal & opsi jawaban**: Biarkan font yang sekarang (jangan diganti). Math dirender KaTeX/MathJax — jangan disentuh.
- **Mono (timer, nomor soal, kode)**: `Geist Mono` / `ui-monospace` + `font-variant-numeric: tabular-nums`

### Scale (disarankan)
| Element              | Size     | Weight | Tracking     |
|----------------------|----------|--------|--------------|
| Page title           | 20–24px  | 600    | -0.02em      |
| Section heading      | 16–18px  | 600    | -0.01em      |
| Soal body            | 16px     | 400    | normal       |
| Opsi jawaban         | 15–16px  | 400    | normal       |
| Label / eyebrow      | 11–12px  | 500    | 0.04em uppercase |
| Meta / helper        | 13px     | 400    | normal       |

---

## 4. Spacing & Layout

- Gunakan **8-point grid**.
- Section spacing vertikal: 24–40px.
- Padding kartu: 16–24px.
- Max-width konten pembahasan: ~720px (supaya enak dibaca).
- Panel Tutor AI: 320–380px, bisa collapse.

---

## 5. Radius & Elevation

- Radius default: **6px** (tombol, input, chip kecil)
- Radius kartu: **8px**
- Jangan pakai 12–16px lagi.
- Shadow: hampir tidak ada. Kalau perlu, pakai shadow sangat lembut atau cukup border.
- Hindari kartu bersarang (card in card). Flatten dengan divider.

---

## 6. Components Rules

### Opsi Jawaban
- Default: border netral
- Hover: background subtle
- Selected: border + tint accent
- Setelah dicek: hijau (benar) / merah (salah) + icon, bukan warna saja

### Tombol
- Primary: solid gelap (`#18181B` light / putih dark) **atau** accent solid — pilih satu, jangan campur
- Secondary: outline netral
- Tidak ada gradient
- Tidak ada dua CTA berwarna bertumpuk

### Badge / Pill / Label
- Minimal. Label kecil abu-abu uppercase tracking lebar lebih disukai.
- Hindari badge di dalam badge.
- Nomor langkah: `01`, `02` tipografi biasa, bukan pill berwarna.

### Panel Tutor AI
- Sidebar docked (tinggi penuh), bukan floating card ber-shadow.
- Background `--surface`, dipisah border-left 1px.
- Header sederhana: "Tutor AI" + status.
- Chat gaya dokumen (label kecil + teks), bukan bubble navy.
- Input pinned di bawah.

### Halaman Kunci Jawaban
- Hero cukup jawaban besar + status "Terverifikasi".
- Section: Jawaban → Langkah → Tips / Jebakan.
- Glosarium & penjelasan tambahan: accordion tertutup default.
- Timeline langkah netral (garis vertikal abu-abu).

---

## 7. Do's and Don'ts

**Do**
- Netral + satu aksen
- Hierarki lewat size & weight
- Flat surface + border tipis
- Collapsible panel Tutor
- Tabular nums untuk timer & nomor

**Don't**
- Rainbow section (satu section satu warna pastel)
- Triple emphasis (tint + border + icon berwarna sekaligus)
- Badge bertumpuk
- Gradient button
- Radius besar + shadow tebal
- Mengubah font konten soal / math
- Card di dalam card

---

## 8. Mode Preference

Sediakan toggle Light / Dark di UI (navbar atau settings).
Simpan preferensi di localStorage.
Default bisa Dark (karena user prefer hitam) atau mengikuti system preference.
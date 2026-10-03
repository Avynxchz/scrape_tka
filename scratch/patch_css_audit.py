# -*- coding: utf-8 -*-
"""Patch style.css: f00c escape, header shrink, dsb. (fix hasil audit 4 model)."""
import io

PATH = 'style.css'
BS = chr(92)  # backslash
src = io.open(PATH, encoding='utf-8').read()

# 1. f00c: escape CSS dobel -> tunggal (ikon centang Font Awesome muncul lagi)
old = '  content: "' + BS + BS + 'f00c";'
new = '  content: "' + BS + 'f00c";'
assert old in src, "f00c dobel tidak ditemukan"
src = src.replace(old, new)

# 2. Header shrink (audit Manus P1-01: overflow 1280px)
old_hdr = """.header-container {
  max-width: 1180px;
  margin: 0 auto;
  padding: 0 16px;
  height: 64px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
}"""
new_hdr = """.header-container {
  max-width: 1180px;
  margin: 0 auto;
  padding: 0 16px;
  height: 64px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

/* Audit Manus P1-01: cegah overflow header di 1280px — elemen tengah boleh menyusut */
.header-center-controls {
  min-width: 0;
}

.subject-select-wrap {
  min-width: 0;
}

.subject-select {
  max-width: 340px;
}

@media (max-width: 1360px) {
  .brand-subtitle {
    display: none;
  }
}"""
assert old_hdr in src, "header block tidak cocok"
src = src.replace(old_hdr, new_hdr, 1)

# 3. Focus-visible untuk opsi (aksesibilitas keyboard)
old_foc = """.option-item:hover {
  border-color: var(--border-strong);
  background: var(--surface);
}"""
new_foc = """.option-item:hover {
  border-color: var(--border-strong);
  background: var(--surface);
}

.option-item:focus-visible {
  outline: 2px solid var(--accent);
  outline-offset: 2px;
}

/* Audit Kimi P1: zoom gambar opsi kini tombol terpisah dari aksi memilih */
.opt-zoom-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  margin-left: 6px;
  vertical-align: middle;
  border: 1px solid var(--border);
  background: var(--bg-card);
  border-radius: 6px;
  color: var(--text-3);
  font-size: 11px;
  cursor: zoom-in;
  transition: border-color 0.15s ease, color 0.15s ease;
}

.opt-zoom-btn:hover {
  border-color: var(--border-strong);
  color: var(--text);
}"""
assert old_foc in src, "hover option block tidak cocok"
src = src.replace(old_foc, new_foc, 1)

# 4. Timer habis: pill berubah status
old_timer = """.timer-pill {
  display: flex;
  align-items: center;
  gap: 7px;
  background: var(--navbar-surface);
  border: 1px solid var(--navbar-border);
  color: var(--navbar-text);
  padding: 6px 12px;
  border-radius: var(--radius-sm);
  font-family: var(--font-mono);
  font-size: 12px;
  font-weight: 500;
  letter-spacing: 0.02em;
  font-variant-numeric: tabular-nums;
}"""
new_timer = old_timer + """

.timer-pill.timer-habis {
  border-color: var(--danger-border);
  color: var(--danger);
}"""
assert old_timer in src, "timer-pill block tidak cocok"
src = src.replace(old_timer, new_timer, 1)

# 5. Touch targets (audit Kimi P1-8): kirim chat 40px, model select 36px, chip & tombol kecil
old_send = """.btn-send-chat {
  width: 32px;
  height: 32px;"""
new_send = """.btn-send-chat {
  width: 40px;
  height: 40px;"""
assert old_send in src
src = src.replace(old_send, new_send, 1)

old_sel = """.ai-model-select {
  flex: 1;
  padding: 4px 8px;
  font-size: 11.5px;"""
new_sel = """.ai-model-select {
  flex: 1;
  min-height: 36px;
  padding: 4px 8px;
  font-size: 12px;"""
assert old_sel in src
src = src.replace(old_sel, new_sel, 1)

old_chip = """.chip-btn {
  background: transparent;
  color: var(--text-2);
  border: 1px solid var(--border);
  padding: 5px 10px;"""
new_chip = """.chip-btn {
  background: transparent;
  color: var(--text-2);
  border: 1px solid var(--border);
  min-height: 34px;
  padding: 6px 12px;"""
assert old_chip in src
src = src.replace(old_chip, new_chip, 1)

old_nc = """.btn-new-chat-tutor {
  display: inline-flex;
  align-items: center;
  gap: 3px;
  font-size: 10px;
  font-weight: 500;
  padding: 1px 6px;"""
new_nc = """.btn-new-chat-tutor {
  display: inline-flex;
  align-items: center;
  gap: 3px;
  font-size: 10px;
  font-weight: 500;
  min-height: 26px;
  padding: 4px 8px;"""
assert old_nc in src
src = src.replace(old_nc, new_nc, 1)

old_rq = """.btn-refresh-quota {
  display: inline-flex;
  align-items: center;
  gap: 3px;
  font-size: 10px;
  font-weight: 500;
  padding: 1px 6px;"""
new_rq = """.btn-refresh-quota {
  display: inline-flex;
  align-items: center;
  gap: 3px;
  font-size: 10px;
  font-weight: 500;
  min-height: 26px;
  padding: 4px 8px;"""
assert old_rq in src
src = src.replace(old_rq, new_rq, 1)

# 6. Grid daftar soal: 4 kolom di layar kecil (audit Qwen P2-3)
old_grid = """  .soal-grid {
    grid-template-columns: repeat(5, 1fr);
  }
}"""
new_grid = """  .soal-grid {
    grid-template-columns: repeat(4, 1fr);
  }
}

@media (max-width: 480px) {
  .soal-grid {
    grid-template-columns: repeat(4, 1fr);
    gap: 10px;
  }
}"""
# catatan: blok lama ada dua (768 restore); ganti kemunculan TERAKHIR (blok 768 fase 2)
idx = src.rfind(old_grid)
assert idx != -1, "soal-grid 5 kolom tidak ditemukan"
src = src[:idx] + new_grid + src[idx + len(old_grid):]

# 7. Status ganda: jawab + ragu tampil bersamaan (audit Kimi P2-12)
old_dual = """.grid-item.ragu {
  background: var(--warn-tint);
  color: var(--warn);
  border-color: var(--warn-border);
}"""
new_dual = old_dual + """

.grid-item.answered.ragu {
  background: var(--accent-tint);
  color: var(--accent);
  border-color: var(--accent-border);
  position: relative;
}

.grid-item.answered.ragu::after,
.grid-item.ragu.current::after {
  content: "";
  position: absolute;
  top: 4px;
  right: 4px;
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--warn);
}"""
assert old_dual in src
src = src.replace(old_dual, new_dual, 1)

# 8. Lightbox -> tema terang konsisten (audit Kimi P2-14)
old_lb1 = """.lightbox-content {
  position: relative;
  max-width: 95vw;
  max-height: 94vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  background: rgba(30, 41, 59, 0.95);
  border: 1px solid rgba(255, 255, 255, 0.12);"""
new_lb1 = """.lightbox-content {
  position: relative;
  max-width: 95vw;
  max-height: 94vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  background: var(--bg-card);
  border: 1px solid var(--border);"""
assert old_lb1 in src
src = src.replace(old_lb1, new_lb1, 1)

old_lb2 = """.lightbox-btn {
  background: rgba(255, 255, 255, 0.12);
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: #f8fafc;"""
new_lb2 = """.lightbox-btn {
  background: var(--surface-2);
  border: 1px solid var(--border);
  color: var(--text);"""
assert old_lb2 in src
src = src.replace(old_lb2, new_lb2, 1)

old_lb3 = """.lightbox-close {
  background: rgba(239, 68, 68, 0.2);
  border: 1px solid rgba(239, 68, 68, 0.4);
  color: #fca5a5;"""
new_lb3 = """.lightbox-close {
  background: var(--wrong-tint);
  border: 1px solid var(--wrong-border);
  color: var(--wrong);"""
assert old_lb3 in src
src = src.replace(old_lb3, new_lb3, 1)

old_lb4 = """.lightbox-close:hover {
  background: rgba(239, 68, 68, 0.85);
  color: #ffffff;
}"""
new_lb4 = """.lightbox-close:hover {
  background: var(--wrong);
  color: #ffffff;
}"""
assert old_lb4 in src
src = src.replace(old_lb4, new_lb4, 1)

old_lb5 = """.lightbox-caption {
  margin-top: 10px;
  font-size: 13px;
  color: #cbd5e1;"""
new_lb5 = """.lightbox-caption {
  margin-top: 10px;
  font-size: 13px;
  color: var(--text-2);"""
assert old_lb5 in src
src = src.replace(old_lb5, new_lb5, 1)

# 9. Select mapel tidak meluap dari panel menu mobile (audit Kimi P2-13)
old_msel = """  .header-center-controls .subject-select {
    background: var(--bg-card);
    color: var(--text);
    border-color: var(--border);
    font-size: 16px;
  }"""
new_msel = """  .header-center-controls .subject-select {
    background: var(--bg-card);
    color: var(--text);
    border-color: var(--border);
    font-size: 16px;
    width: 100%;
    max-width: 100%;
    box-sizing: border-box;
  }"""
assert old_msel in src
src = src.replace(old_msel, new_msel, 1)

# 10. X button tutor sheet (audit Qwen P1-2)
old_x = """.ai-header-badge {
  color: var(--text-3);
  font-size: 14px;
}"""
new_x = old_x + """

/* Tombol tutup eksplisit bottom sheet — hanya tampil di mobile */
.btn-close-sheet {
  display: none;
  background: transparent;
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  color: var(--text-2);
  width: 34px;
  height: 34px;
  font-size: 15px;
  cursor: pointer;
  flex-shrink: 0;
}

.btn-close-sheet:hover {
  border-color: var(--border-strong);
  color: var(--text);
}"""
assert old_x in src
src = src.replace(old_x, new_x, 1)

old_xmob = """  .tutor-sheet-handle {
    display: flex;
    justify-content: center;
    align-items: center;
    padding: 10px 0 4px;
    cursor: grab;
    touch-action: none;
    flex-shrink: 0;
    background: var(--surface);
    border-bottom: 1px solid var(--border);
  }"""
new_xmob = old_xmob + """

  .btn-close-sheet {
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .ai-header-badge {
    display: none;
  }"""
assert old_xmob in src
src = src.replace(old_xmob, new_xmob, 1)

# 11. Select mapel di menu mobile: padding lebih legas (touch target)
old_ptab = """.pkg-tab {
  background: transparent;
  border: none;
  padding: 5px 14px;"""
new_ptab = """.pkg-tab {
  background: transparent;
  border: none;
  padding: 7px 14px;
  min-height: 34px;"""
assert old_ptab in src
src = src.replace(old_ptab, new_ptab, 1)

io.open(PATH, 'w', encoding='utf-8', newline='\n').write(src)
print("style.css patch OK")

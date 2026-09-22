# Canonical Question Transcription — Schema v1.0

Lapisan teks kanonis untuk AI — terpisah dari representasi UI (`*_learning.json`)
dan dari raw scrape. **Tidak pernah menulis kembali data otoritatif** (raw,
learning, `data/kunci/` tetap utuh; `validate_data.py` tetap jadi gerbang).

## Regenerasi (deterministik, idempoten)

```bash
python build_canonical_questions.py                 # bangun ulang semua paket
python _vision_packet.py build [slug ...]           # packet review vision per paket
python _vision_packet.py ingest <slug> hasil.json   # tulis side-car + rebuild
python -m pytest tests/test_canonical_extraction.py # tes perilaku ekstraksi
```

## Pipeline

```
Raw scrape (HTML resmi)                    data/kunci/ (bukti resmi)
  ├── stimulus/pertanyaan html + img ─┐            │
  │   + atribut data-latex resmi      │            │
  └── pilihan_jawaban (text/latex/img)│            │
                                      ▼            ▼
                        build_canonical_questions.py (join + cross-check)
                                      │
              data/canonical_questions/<slug>.json ──► Claude / AI Tutor
                                      ▲
        _vision/<slug>.json (side-car, opsional; hasil pass Claude Web)
```

## Prioritas representasi (satu aturan, konsisten)

1. **`data-latex` resmi** dari atribut `<img>` situs — sumber semantik tertinggi.
2. **Transkripsi vision side-car** (`_vision/<slug>.json`) — hanya bila tidak ada
   `data-latex`; harus faktual per elemen.
3. **Penanda eksplisit** `[VISUAL_INFORMATION_UNRESOLVED: ...]` + entri
   `visual_context.unresolved` — bila keduanya tidak ada. **Tidak pernah menebak.**

## Struktur `<slug>.json`

```jsonc
{
  "schema_version": "1.0",
  "slug": "matematika_paket_2",
  "subject": "Matematika",
  "package": 2,
  "total_questions": 25,
  "source": {
    "raw_scrape": "data/paket_2/matematika_paket_2.json",
    "official_key_evidence": "data/kunci/matematika_paket_2_kunci.json",
    "official_key_scraped_at": "...",
    "learning_reference": "data/matematika_paket_2_learning.json",
    "extraction": "deterministic structured extraction (data-latex + source text); no OCR"
  },
  "questions": [
    {
      "id": "mtk_p2_q02",
      "slug": "...", "subject": "...", "package": 2, "question_number": 2,
      "source_id": "soal-no-2",
      "type": "PG | PGK | BS | LABEL",
      "stimulus_text": "teks stimulus verbatim, formula inline sbg $...$, visual sbg penanda/deskripsi",
      "stimulus_images": [{ "filename", "rel_path", "remote_url", "role", "data_latex?" }],
      "question_text": "idem, untuk blok pertanyaan",
      "question_images": [...],

      // PG / PGK:
      "options": { "A": "teks kanonis opsi", ... },
      // BS / LABEL (pernyataan A/B/C):
      "statements": [
        { "key": "A", "text"?, "latex"?, "image"?, "display": "teks gabungan" }
      ],

      "visual_context": {
        "description": "ringkasan status visual",
        "formulas":  [{ "latex", "image", "location", "source": "official data-latex | vision transcription" }],
        "tables":    [{ "image", "location", "description"?, "source"? }],
        "graphs":    [ ... idem ... ],
        "diagrams":  [ ... idem ... ],
        "unresolved":[{ "kind", "element", "reason" }]
      },
      "source_images": [{ "filename", "rel_path", "remote_url", "role", "represented_by"? }],
      "official_answer": {
        // PG:   { "format": "single",        "correct": ["C"] }
        // PGK:  { "format": "multiple",      "correct": ["A","D"] }
        // BS:   { "format": "per_statement", "statements": { "A":"Benar", ... } }
        // LABEL:{ "format": "per_statement", "statements": { "A":"Similarity", ... } }
      },
      "answer_source": "official_review_scrape (data/kunci/, review_hasil Pusmendik)",
      "unresolved_count": 0,
      "transcription_status": "ai_ready | manual_review"
    }
  ]
}
```

### Field `represented_by` (source_images)

Gambar yang terwakili semantik oleh representasi lain (mis. opsi sudah punya
`latex` eksplisit sehingga gambarnya redundan secara informasi) ditandai
`"represented_by": "option latex" | "statement latex"` — referensi file tetap
utuh untuk UI.

## Gerbang AI-ready

`transcription_status == "ai_ready"` ⟺ `unresolved_count == 0`, yaitu semua
informasi yang diperlukan untuk memahami dan mengerjakan soal ada dalam teks
(`data-latex` resmi, teks verbatim, atau transkripsi vision). Soal dengan
elemen belum terwakili berstatus `manual_review` — referensi gambar tetap
disimpan, penanda tetap eksplisit, **tidak ada tebakan**.

## Side-car vision (`_vision/<slug>.json`)

- Bentuk: `{ "<filename>.png": { "latex": str|null, "description": str|null } }`.
- Dihasilkan dari packet review `_review/<slug>/` (notes.json + images/):
  transkripsi **faktual per elemen** oleh Claude Web — bukan penyelesaian soal,
  bukan penalaran pendidikan.
- `ingest` memvalidasi: hanya filename yang memang unresolved, ada latex/desc,
  file sumber ada. Side-car **ditambahkan** (merge), tidak pernah menimpa.
- Builder membaca side-car secara opsional → build tetap deterministik dan
  regenerable tanpa side-car (kembali ke penanda eksplisit).

## Invariant yang dijaga (lihat tests/)

- Jumlah soal per paket == raw (46/25/20/25/20/29/10/30 = 205).
- Distribusi tipe == learning/evidence (PG 117, PGK 61, BS 22, LABEL 5; 259 item dinilai).
- `official_answer` identik dengan bukti `data/kunci/` dan learning (cross-check raise).
- Semua `source_images` ada di disk; setiap referensi terwakili (latex/deskripsi/
  penanda) — tidak ada gambar "diam".
- `unresolved_count == 0` ⟺ `ai_ready`.

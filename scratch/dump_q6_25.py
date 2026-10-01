import json

data = json.load(open("data/matematika_paket_2_learning.json", encoding="utf-8"))["soal"]

with open("scratch/dump_out.txt", "w", encoding="utf-8") as out:
    for i in range(5, len(data)):
        q = data[i]
        out.write(f"\n==================== SOAL {q.get('nomor', i+1)} ====================\n")
        out.write(f"ID: {q.get('id')}\n")
        out.write(f"TIPE: {q.get('tipe_soal')}\n")
        out.write(f"TOPIK: {q.get('topik')}\n")
        out.write(f"STIMULUS_TEXT: {q.get('stimulus', {}).get('text')}\n")
        out.write(f"PERTANYAAN: {q.get('pertanyaan')}\n")
        out.write(f"PILIHAN: {json.dumps(q.get('pilihan_jawaban'), ensure_ascii=False, indent=2)}\n")
        out.write(f"KUNCI: {json.dumps(q.get('kunci_jawaban'), ensure_ascii=False)}\n")
        out.write(f"VISUAL_MEMORY: {json.dumps(q.get('visual_memory'), ensure_ascii=False, indent=2)}\n")
        out.write(f"PEMBAHASAN_EXISTING: {json.dumps(q.get('pembahasan'), ensure_ascii=False, indent=2)}\n")

print("Dumped 6-25 successfully!")

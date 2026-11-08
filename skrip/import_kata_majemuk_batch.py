"""
import_kata_majemuk_batch.py
==============================
Validasi hasil klasifikasi AI eksternal (NDJSON) lalu gabung dengan aman
ke kata_majemuk_pola.json. TIDAK PERNAH minta copy-paste manual ke file
data -- semua lewat json.dump terprogram (menghindari insiden JSON rusak
seperti yang pernah terjadi di nuance_pairs.json).

Cara pakai:
    python import_kata_majemuk_batch.py balasan_ai.txt
    python import_kata_majemuk_batch.py balasan_ai.txt --dry-run

Validasi yang dilakukan per baris:
- Baris harus JSON valid
- Harus ada field: word, pola, keterangan_id
- pola harus salah satu dari 6 nilai valid
- word harus ada di kata_majemuk_candidates_2char_ALL.json (cegah halusinasi AI)
- word tidak boleh sudah diklasifikasi sebelumnya (no-duplicate)
- word tidak boleh dobel DALAM batch yang sama

Baris yang gagal validasi di-skip dan dilaporkan, TIDAK menghentikan
keseluruhan proses (baris valid lainnya tetap masuk).
"""

import json
import os
import sys

CANDIDATES_PATH = "kata_majemuk_candidates_2char_ALL.json"
OUTPUT_PATH = "kata_majemuk_pola.json"

VALID_POLA = {"联合式", "偏正式", "动宾式", "主谓式", "补充式", "lainnya"}


def load_json(path, default):
    if not os.path.exists(path):
        return default
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def atomic_write_json(path, data):
    """Tulis JSON dengan aman: tulis ke file temp dulu, baru rename.
    Kalau proses gagal di tengah jalan, file asli tidak ikut rusak."""
    tmp_path = path + ".tmp"
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    os.replace(tmp_path, path)


def main():
    if len(sys.argv) < 2:
        print("Cara pakai: python import_kata_majemuk_batch.py <file_balasan_ai.txt> [--dry-run]")
        sys.exit(1)

    input_path = sys.argv[1]
    dry_run = "--dry-run" in sys.argv

    if not os.path.exists(input_path):
        print(f"[ERROR] File tidak ditemukan: {input_path}")
        sys.exit(1)

    candidates = load_json(CANDIDATES_PATH, [])
    valid_words = set(c["word"] for c in candidates)
    if not valid_words:
        print(f"[ERROR] {CANDIDATES_PATH} tidak ditemukan/kosong -- tidak bisa validasi existence.")
        sys.exit(1)

    existing = load_json(OUTPUT_PATH, [])
    already_done = set(item["word"] for item in existing)

    accepted = []
    rejected = []
    seen_in_batch = set()

    with open(input_path, "r", encoding="utf-8") as f:
        raw_lines = [ln.strip() for ln in f if ln.strip()]

    for i, line in enumerate(raw_lines, 1):
        # jaga-jaga kalau AI tetap kasih code fence markdown
        if line.startswith("```"):
            continue

        try:
            obj = json.loads(line)
        except json.JSONDecodeError as e:
            rejected.append((i, line, f"JSON tidak valid: {e}"))
            continue

        word = obj.get("word", "").strip()
        pola = obj.get("pola", "").strip()
        keterangan = obj.get("keterangan_id", "").strip()

        if not word or not pola:
            rejected.append((i, line, "field 'word' atau 'pola' kosong/hilang"))
            continue

        if pola not in VALID_POLA:
            rejected.append((i, line, f"pola tidak valid: '{pola}'"))
            continue

        if word not in valid_words:
            rejected.append((i, line, f"kata '{word}' tidak ada di daftar kandidat (kemungkinan halusinasi AI)"))
            continue

        if word in already_done:
            rejected.append((i, line, f"kata '{word}' sudah pernah diklasifikasi sebelumnya, di-skip"))
            continue

        if word in seen_in_batch:
            rejected.append((i, line, f"kata '{word}' dobel di dalam batch ini, di-skip (baris pertama dipakai)"))
            continue

        seen_in_batch.add(word)
        accepted.append({
            "word": word,
            "pola": pola,
            "keterangan_id": keterangan,
        })

    print(f"Total baris dibaca : {len(raw_lines)}")
    print(f"Diterima           : {len(accepted)}")
    print(f"Ditolak            : {len(rejected)}")

    if rejected:
        print("\n--- Detail baris ditolak ---")
        for i, line, reason in rejected:
            preview = line if len(line) <= 60 else line[:60] + "..."
            print(f"  baris {i}: {reason}")
            print(f"    isi: {preview}")

    if not accepted:
        print("\nTidak ada data valid untuk digabung. Berhenti.")
        return

    if dry_run:
        print(f"\n[DRY RUN] {len(accepted)} kata AKAN digabung ke {OUTPUT_PATH} (belum benar-benar ditulis).")
        print("Jalankan tanpa --dry-run untuk benar-benar menyimpan.")
        return

    merged = existing + accepted
    atomic_write_json(OUTPUT_PATH, merged)
    print(f"\n✅ {len(accepted)} kata baru digabung ke {OUTPUT_PATH}.")
    print(f"   Total sekarang: {len(merged)} kata terklasifikasi.")


if __name__ == "__main__":
    main()

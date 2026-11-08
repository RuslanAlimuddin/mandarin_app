"""
revert_batch.py
==================
Batalkan koreksi yang SUDAH diterapkan dari 1 file balasan AI (format
{"word":..., "pola_lama":..., "pola_baru":..., ...}), kembalikan tiap
kata ke pola_lama-nya. Dipakai kalau 1 batch verifikasi ternyata banyak
salah dan sudah kadung di-apply tanpa --dry-run.

Cara pakai:
    python revert_batch.py balasan40.txt --dry-run
    python revert_batch.py balasan40.txt

Cara kerja: baca ulang file balasan yang sama, ambil pasangan
(word, pola_lama), lalu tulis ulang ke kata_majemuk_pola.json dengan
pola_lama itu -- hanya untuk kata yang field pola_lama-nya terisi.
"""

import json
import os
import sys

CLASSIFIED_PATH = "kata_majemuk_pola.json"


def load_json(path, default):
    if not os.path.exists(path):
        return default
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def atomic_write_json(path, data):
    tmp_path = path + ".tmp"
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    os.replace(tmp_path, path)


def main():
    if len(sys.argv) < 2:
        print("Cara pakai: python revert_batch.py <file_balasan_ai.txt> [--dry-run]")
        sys.exit(1)

    input_path = sys.argv[1]
    dry_run = "--dry-run" in sys.argv

    if not os.path.exists(input_path):
        print(f"[ERROR] File tidak ditemukan: {input_path}")
        sys.exit(1)

    classified = load_json(CLASSIFIED_PATH, [])
    if not classified:
        print(f"[ERROR] {CLASSIFIED_PATH} tidak ditemukan/kosong.")
        sys.exit(1)

    index = {item["word"]: item for item in classified}

    with open(input_path, "r", encoding="utf-8") as f:
        raw_lines = [ln.strip() for ln in f if ln.strip()]

    reverted = []
    skipped = []

    for i, line in enumerate(raw_lines, 1):
        if line.startswith("```"):
            continue
        try:
            obj = json.loads(line)
        except json.JSONDecodeError:
            skipped.append((i, "JSON tidak valid"))
            continue

        word = obj.get("word", "").strip()
        pola_lama = obj.get("pola_lama", "").strip() if obj.get("pola_lama") else None

        if not word or not pola_lama:
            skipped.append((i, f"'{word}': tidak ada field pola_lama, di-skip"))
            continue

        if word not in index:
            skipped.append((i, f"'{word}': tidak ditemukan di {CLASSIFIED_PATH}"))
            continue

        current_pola = index[word]["pola"]
        if current_pola == pola_lama:
            skipped.append((i, f"'{word}': pola saat ini sudah = pola_lama, tidak perlu revert"))
            continue

        reverted.append((word, current_pola, pola_lama))

    print(f"Total baris dibaca : {len(raw_lines)}")
    print(f"Akan di-revert     : {len(reverted)}")
    print(f"Di-skip            : {len(skipped)}")

    if skipped:
        print("\n--- Detail di-skip ---")
        for i, reason in skipped[:20]:
            print(f"  baris {i}: {reason}")
        if len(skipped) > 20:
            print(f"  ... dan {len(skipped) - 20} lainnya")

    if not reverted:
        print("\nTidak ada yang perlu di-revert.")
        return

    print("\n--- Akan dikembalikan ke pola lama ---")
    for word, current, old in reverted[:15]:
        print(f"  {word}: {current}  ->  {old}")
    if len(reverted) > 15:
        print(f"  ... dan {len(reverted) - 15} lainnya")

    if dry_run:
        print(f"\n[DRY RUN] {len(reverted)} kata AKAN dikembalikan ke pola lama (belum ditulis).")
        return

    for word, current, old in reverted:
        index[word]["pola"] = old

    atomic_write_json(CLASSIFIED_PATH, classified)
    print(f"\n✅ {len(reverted)} kata dikembalikan ke pola lamanya di {CLASSIFIED_PATH}.")


if __name__ == "__main__":
    main()

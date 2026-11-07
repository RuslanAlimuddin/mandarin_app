# -*- coding: utf-8 -*-
"""
merge_graded_readers_hsk9.py
Gabungkan graded_readers_hsk9_batch.json (3 bacaan baru, ratakan HSK9)
ke dalam data/graded_readers.json utama.

Cara pakai (dari folder C:\\mandarin_app):
    python merge_graded_readers_hsk9.py

Langkah yang dilakukan:
  1. Backup data/graded_readers.json -> data/graded_readers_backup_sebelum_merge_hsk9.json
  2. Cek bentrok id (harusnya tidak ada, sudah divalidasi Claude sebelumnya)
  3. Gabungkan 3 bacaan baru ke passages existing
  4. Tulis ulang data/graded_readers.json
  5. Cetak ringkasan + instruksi verifikasi lanjutan
"""
import json
import os
import shutil

MAIN_FILE   = os.path.join("data", "graded_readers.json")
BATCH_FILE  = "graded_readers_hsk9_batch.json"
BACKUP_FILE = os.path.join("data", "graded_readers_backup_sebelum_merge_hsk9.json")

def main():
    if not os.path.isfile(MAIN_FILE):
        print(f"❌ Tidak ketemu {MAIN_FILE}. Jalankan skrip ini dari folder C:\\mandarin_app.")
        return
    if not os.path.isfile(BATCH_FILE):
        print(f"❌ Tidak ketemu {BATCH_FILE}. Taruh file itu sejajar dengan skrip ini dulu.")
        return

    with open(MAIN_FILE, encoding="utf-8") as f:
        main_data = json.load(f)
    existing_passages = main_data["passages"] if isinstance(main_data, dict) else main_data

    with open(BATCH_FILE, encoding="utf-8") as f:
        batch = json.load(f)

    existing_ids = set(p.get("id") for p in existing_passages)
    conflicts = [p["id"] for p in batch if p["id"] in existing_ids]
    if conflicts:
        print(f"❌ Ada bentrok id, batal merge: {conflicts}")
        return

    # 1. Backup
    shutil.copy(MAIN_FILE, BACKUP_FILE)
    print(f"✓ Backup dibuat: {BACKUP_FILE}")

    # 2. Gabungkan
    existing_passages.extend(batch)
    if isinstance(main_data, dict):
        main_data["passages"] = existing_passages
        output = main_data
    else:
        output = existing_passages

    # 3. Tulis ulang
    with open(MAIN_FILE, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"✓ {len(batch)} bacaan baru digabung ke {MAIN_FILE}")
    print(f"✓ Total bacaan sekarang: {len(existing_passages)}")
    print()
    print("Langkah berikutnya:")
    print("  1. Jalankan: python verify_coverage.py data\\graded_readers.json")
    print("  2. Buka graded-reader.html, cek 3 bacaan baru tema Kesehatan / Pendidikan Tinggi / Lingkungan Hidup di level HSK9")
    print("  3. Kalau semua OK, boleh hapus graded_readers_hsk9_batch.json dan backup file ini")

if __name__ == "__main__":
    main()

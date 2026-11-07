"""
Merge 4 file staging bacaan baru (batch 1-4) ke data/graded_readers.json.

Cara pakai (dari folder C:\\mandarin_app):
    python merge_graded_readers.py

Skrip ini akan:
1. Baca data/graded_readers.json yang sudah ada (69 bacaan)
2. Baca 4 file staging: graded_readers_tema6.json s/d tema9.json (masing-masing 8 bacaan)
3. Cek tidak ada bentrok ID
4. Gabungkan semua, simpan balik ke data/graded_readers.json
5. Backup file lama otomatis ke data/graded_readers_backup_sebelum_merge.json
"""
import json
import os
import shutil

DATA_DIR = 'data'
EXISTING_FILE = os.path.join(DATA_DIR, 'graded_readers.json')
STAGING_FILES = [
    'graded_readers_tema6.json',
    'graded_readers_tema7.json',
    'graded_readers_tema8.json',
    'graded_readers_tema9.json',
]
BACKUP_FILE = os.path.join(DATA_DIR, 'graded_readers_backup_sebelum_merge.json')

def main():
    if not os.path.exists(EXISTING_FILE):
        print(f"TIDAK KETEMU: {EXISTING_FILE}")
        print("Pastikan skrip ini dijalankan dari folder C:\\mandarin_app")
        return

    with open(EXISTING_FILE, encoding='utf-8') as f:
        existing_data = json.load(f)
    existing_passages = existing_data['passages']
    print(f"Bacaan yang sudah ada: {len(existing_passages)}")

    new_passages = []
    for fn in STAGING_FILES:
        if not os.path.exists(fn):
            print(f"PERINGATAN: {fn} tidak ditemukan di folder ini, dilewati.")
            print(f"  (Pastikan file staging ini sudah رسلان taruh di folder yang sama dengan skrip ini)")
            continue
        with open(fn, encoding='utf-8') as f:
            batch = json.load(f)
        new_passages.extend(batch)
        print(f"  + {fn}: {len(batch)} bacaan")

    if not new_passages:
        print("Tidak ada bacaan baru yang berhasil dibaca. Berhenti.")
        return

    # Cek bentrok ID
    existing_ids = set(p['id'] for p in existing_passages)
    new_ids = [p['id'] for p in new_passages]
    dupes_within_new = set(x for x in new_ids if new_ids.count(x) > 1)
    dupes_with_existing = existing_ids & set(new_ids)

    if dupes_within_new:
        print(f"GAGAL: ada ID bentrok di antara file staging: {dupes_within_new}")
        return
    if dupes_with_existing:
        print(f"GAGAL: ada ID bentrok dengan bacaan yang sudah ada: {dupes_with_existing}")
        return

    print(f"Total bacaan baru: {len(new_passages)}")
    print(f"Total setelah digabung: {len(existing_passages) + len(new_passages)}")

    # Backup file lama
    shutil.copy(EXISTING_FILE, BACKUP_FILE)
    print(f"Backup disimpan ke: {BACKUP_FILE}")

    # Gabung dan simpan
    combined = {'passages': existing_passages + new_passages}
    with open(EXISTING_FILE, 'w', encoding='utf-8') as f:
        json.dump(combined, f, ensure_ascii=False, indent=2)

    print(f"SELESAI. {EXISTING_FILE} sekarang berisi {len(combined['passages'])} bacaan.")
    print("Jalankan verify_coverage.py sekali lagi ke file final untuk memastikan semua aman:")
    print(f"  python verify_coverage.py {EXISTING_FILE}")

if __name__ == '__main__':
    main()

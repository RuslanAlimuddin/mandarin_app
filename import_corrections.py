"""
import_corrections.py
========================
Terapkan koreksi (hasil dari salah satu dari 3 alur recheck) ke
kata_majemuk_pola.json dengan AMAN -- update in-place per kata, bukan
tambah entri baru. Selalu tampilkan diff (lama -> baru) sebelum & sesudah
diterapkan.

Dipakai untuk SEMUA jenis koreksi (keterangan_id, reklasifikasi
subjek-predikat, verifikasi dongbin/buchong) -- formatnya fleksibel:
tiap baris NDJSON boleh berisi salah satu atau kedua field ini:
    pola_baru           (kalau ada -> update field 'pola')
    keterangan_id_baru  (kalau ada -> update field 'keterangan_id')
    (field 'keterangan_id' polos juga diterima sbg alias keterangan_id_baru)

Field 'word' WAJIB ada di semua baris.

Cara pakai:
    python import_corrections.py balasan.txt --dry-run
    python import_corrections.py balasan.txt
"""

import json
import os
import sys

CLASSIFIED_PATH = "kata_majemuk_pola.json"
VALID_POLA = {"联合式", "偏正式", "动宾式", "主谓式", "补充式", "lainnya"}


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
        print("Cara pakai: python import_corrections.py <file_balasan_ai.txt> [--dry-run]")
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

    if not raw_lines:
        print("File balasan kosong -- tidak ada koreksi (mungkin memang tidak ada yang perlu dikoreksi). Selesai.")
        return

    applied = []
    rejected = []

    for i, line in enumerate(raw_lines, 1):
        if line.startswith("```"):
            continue

        try:
            obj = json.loads(line)
        except json.JSONDecodeError as e:
            rejected.append((i, line, f"JSON tidak valid: {e}"))
            continue

        word = obj.get("word", "").strip()
        if not word:
            rejected.append((i, line, "field 'word' kosong/hilang"))
            continue

        if word not in index:
            rejected.append((i, line, f"kata '{word}' tidak ditemukan di {CLASSIFIED_PATH}"))
            continue

        pola_baru = obj.get("pola_baru", "").strip() if obj.get("pola_baru") else None
        keterangan_baru = (
            obj.get("keterangan_id_baru", "").strip() if obj.get("keterangan_id_baru")
            else (obj.get("keterangan_id", "").strip() if obj.get("keterangan_id") else None)
        )

        if not pola_baru and not keterangan_baru:
            rejected.append((i, line, "tidak ada 'pola_baru' maupun 'keterangan_id_baru' untuk diterapkan"))
            continue

        if pola_baru and pola_baru not in VALID_POLA:
            rejected.append((i, line, f"pola_baru tidak valid: '{pola_baru}'"))
            continue

        old_item = index[word]
        diff = {"word": word}
        if pola_baru and pola_baru != old_item["pola"]:
            diff["pola_lama"] = old_item["pola"]
            diff["pola_baru"] = pola_baru
        if keterangan_baru and keterangan_baru != old_item.get("keterangan_id", ""):
            diff["keterangan_lama"] = old_item.get("keterangan_id", "")
            diff["keterangan_baru"] = keterangan_baru

        if len(diff) == 1:
            # tidak ada perubahan riil (koreksi identik dgn data lama)
            rejected.append((i, line, f"kata '{word}': tidak ada perubahan riil dari data saat ini, di-skip"))
            continue

        applied.append((old_item, pola_baru, keterangan_baru, diff))

    print(f"Total baris dibaca: {len(raw_lines)}")
    print(f"Akan diterapkan   : {len(applied)}")
    print(f"Ditolak           : {len(rejected)}")

    if rejected:
        print("\n--- Detail baris ditolak ---")
        for i, line, reason in rejected:
            preview = line if len(line) <= 60 else line[:60] + "..."
            print(f"  baris {i}: {reason}")
            print(f"    isi: {preview}")

    if not applied:
        print("\nTidak ada koreksi valid untuk diterapkan.")
        return

    print("\n--- Diff yang akan diterapkan ---")
    for old_item, pola_baru, keterangan_baru, diff in applied:
        print(f"\n  {diff['word']}:")
        if "pola_baru" in diff:
            print(f"    pola       : {diff['pola_lama']}  ->  {diff['pola_baru']}")
        if "keterangan_baru" in diff:
            print(f"    keterangan : {diff['keterangan_lama']}")
            print(f"                 ->  {diff['keterangan_baru']}")

    if dry_run:
        print(f"\n[DRY RUN] {len(applied)} koreksi AKAN diterapkan (belum benar-benar ditulis).")
        print("Jalankan tanpa --dry-run untuk benar-benar menyimpan.")
        return

    for old_item, pola_baru, keterangan_baru, diff in applied:
        if pola_baru:
            old_item["pola"] = pola_baru
        if keterangan_baru:
            old_item["keterangan_id"] = keterangan_baru

    atomic_write_json(CLASSIFIED_PATH, classified)
    print(f"\n✅ {len(applied)} koreksi diterapkan ke {CLASSIFIED_PATH}.")


if __name__ == "__main__":
    main()

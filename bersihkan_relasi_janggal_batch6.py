"""
bersihkan_relasi_janggal_batch6.py
====================================
Membersihkan relasi sinonim/antonim salah hasil review manual Claude atas
6 cycle Tier B (sesi lanjutan setelah BLUEPRINT v33, ~600 kata lagi).
Sesi ini pertama kali pakai cek_dan_bersihkan_hasil_tier_b.py sbg penyaring
awal sebelum review manual Claude -- jauh lebih cepat, tapi tetap ada
review manual krn heuristik-nya banyak false positive (lihat catatan
single-char di flagged_relations_batch6.json).

DESAIN (sama dgn batch4/5):
  - HANYA memproses pasangan eksplisit dari flagged_relations_batch6.json.
  - TIDAK ADA pattern-matching/regex.
  - Default = DRY RUN, harus --apply eksplisit.
  - high_confidence diproses default; suspicious_padding_single_char_caution
    dan borderline_review_needed perlu opt-in eksplisit.

Cara pakai:
  python bersihkan_relasi_janggal_batch6.py                     # dry-run, high_confidence saja
  python bersihkan_relasi_janggal_batch6.py --include-borderline
  python bersihkan_relasi_janggal_batch6.py --apply [flags di atas]

  CATATAN: suspicious_padding_single_char_caution TIDAK punya flag opt-in
  krn isinya justru daftar FALSE POSITIVE terkonfirmasi (kata baku yg
  SALAH ke-flag) -- disimpan sbg referensi contoh kasus, BUKAN utk dihapus.
  Skrip ini tidak akan pernah memproses kategori itu.

File yg dibutuhkan di folder yg sama:
  - data/app_words.json
  - flagged_relations_batch6.json
"""

import json
import sys
import argparse
import subprocess
from pathlib import Path

APP_WORDS_PATH = Path("data/app_words.json")
FLAGGED_PATH = Path("flagged_relations_batch6.json")

OLD_FIELD = {"synonyms": "synonyms", "antonyms": "antonyms"}
DETAIL_FIELD = {"synonyms": "synonyms_detail", "antonyms": "antonyms_detail"}


def load_json(path):
    if not path.exists():
        print(f"ERROR: file tidak ditemukan: {path}")
        sys.exit(1)
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def find_word_entry(app_words, word):
    for entry in app_words:
        if entry.get("simplified") == word:
            return entry
    return None


def remove_from_old_field(entry, related, rel_type):
    field = OLD_FIELD[rel_type]
    lst = entry.get(field)
    if isinstance(lst, list) and related in lst:
        lst.remove(related)
        return True
    return False


def remove_from_detail_field(entry, related, rel_type):
    field = DETAIL_FIELD[rel_type]
    lst = entry.get(field)
    if isinstance(lst, list):
        new_lst = []
        removed = False
        for item in lst:
            item_word = item.get("word") if isinstance(item, dict) else item
            if item_word == related and not removed:
                removed = True
                continue
            new_lst.append(item)
        if removed:
            entry[field] = new_lst
            return True
    return False


def process_pair(app_words, word, related, rel_type, apply_changes, report):
    entry = find_word_entry(app_words, word)
    if entry is None:
        report.append((word, related, rel_type, "SKIP - kata tidak ditemukan di app_words.json"))
        return

    if apply_changes:
        removed_old = remove_from_old_field(entry, related, rel_type)
        removed_detail = remove_from_detail_field(entry, related, rel_type)
    else:
        field = OLD_FIELD[rel_type]
        removed_old = related in (entry.get(field) or [])
        detail_field = DETAIL_FIELD[rel_type]
        detail_list = entry.get(detail_field) or []
        removed_detail = any(
            (item.get("word") if isinstance(item, dict) else item) == related
            for item in detail_list
        )

    if not removed_old and not removed_detail:
        report.append((word, related, rel_type, "SKIP - relasi tidak ditemukan (mungkin sudah bersih)"))
        return

    status = "AKAN DIHAPUS" if not apply_changes else "DIHAPUS"
    detail_note = "field lama" + (" + detail" if removed_detail else "") if removed_old else "hanya field detail"
    report.append((word, related, rel_type, f"{status} ({detail_note})"))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="Eksekusi beneran (default: dry-run)")
    parser.add_argument("--include-borderline", action="store_true",
                         help="Ikut proses daftar borderline_review_needed (default: skip)")
    args = parser.parse_args()

    flagged = load_json(FLAGGED_PATH)
    pairs = list(flagged.get("high_confidence", []))
    categories_used = ["high_confidence"]
    if args.include_borderline:
        pairs += list(flagged.get("borderline_review_needed", []))
        categories_used.append("borderline_review_needed")

    print("=" * 70)
    print(f"BERSIHKAN RELASI JANGGAL - BATCH 6 {'(APPLY)' if args.apply else '(DRY RUN)'}")
    print(f"Kategori diproses: {', '.join(categories_used)}")
    print(f"Total pasangan: {len(pairs)}")
    print("(suspicious_padding_single_char_caution TIDAK diproses -- itu daftar false-positive, bukan utk dihapus)")
    print("=" * 70)

    app_words = load_json(APP_WORDS_PATH)

    if args.apply:
        # NOTE: checkpoint.py didesain sbg CLI ("python checkpoint.py save"),
        # BUKAN modul yg diimpor -- tidak ada fungsi save() di level modul
        # (itu penyebab AttributeError sebelumnya: 'module checkpoint has no
        # attribute save'). Panggil via subprocess, persis spt dipakai dari
        # command line, supaya snapshot ZIP lengkapnya (semua *.py + data/)
        # benar-benar dibuat sebelum menulis perubahan.
        checkpoint_script = Path("checkpoint.py")
        checkpoint_ok = False
        if checkpoint_script.exists():
            result = subprocess.run(
                [sys.executable, str(checkpoint_script), "save",
                 "--note", "sebelum bersihkan_relasi_janggal_batch6 --apply"],
                capture_output=True, text=True
            )
            print(result.stdout)
            if result.returncode == 0:
                checkpoint_ok = True
            else:
                print(result.stderr)
        if not checkpoint_ok:
            print("PERINGATAN: checkpoint.py tidak ditemukan/gagal dijalankan "
                  "-- pastikan رسلان sudah backup app_words.json manual sebelum lanjut!\n")
            confirm = input("Lanjutkan tanpa checkpoint otomatis? (ketik 'ya' untuk lanjut): ")
            if confirm.strip().lower() != "ya":
                print("Dibatalkan.")
                sys.exit(0)

    report = []
    for item in pairs:
        word, related, rel_type = item["word"], item["related"], item["relation_type"]
        process_pair(app_words, word, related, rel_type, args.apply, report)
        process_pair(app_words, related, word, rel_type, args.apply, report)

    for word, related, rel_type, status in report:
        print(f"  {word} <-> {related} [{rel_type}]: {status}")

    n_removed = sum(1 for r in report if "DIHAPUS" in r[3] and "SKIP" not in r[3])
    n_skipped = sum(1 for r in report if "SKIP" in r[3])
    print("\n" + "-" * 70)
    print(f"Ringkasan: {n_removed} entri {'dihapus' if args.apply else 'akan dihapus'}, "
          f"{n_skipped} dilewati (tidak ditemukan)")

    if args.apply:
        save_json(APP_WORDS_PATH, app_words)
        print(f"\napp_words.json sudah ditulis ulang.")
    else:
        print("\nIni baru DRY RUN -- tidak ada file yang ditulis. "
              "Jalankan ulang dgn --apply kalau hasilnya sudah sesuai.")


if __name__ == "__main__":
    main()

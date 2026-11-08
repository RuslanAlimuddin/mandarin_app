"""
bersihkan_relasi_janggal_sesi_v35.py
=====================================
Sama desainnya dgn bersihkan_relasi_janggal_batch4/5/6.py -- baca
exclude_list_sesi_v35.json (134 pasangan hasil review manual Claude
sepanjang sesi setelah BLUEPRINT v34), lalu buang pasangan tsb dari
synonyms/antonyms DAN synonyms_detail/antonyms_detail di app_words.json.

Cara pakai:
    python bersihkan_relasi_janggal_sesi_v35.py
        -> dry-run, cuma cetak apa yg AKAN dibuang, TIDAK ubah file

    python bersihkan_relasi_janggal_sesi_v35.py --apply
        -> beneran menulis perubahan ke data/app_words.json
           (bikin backup .bak dulu sebelum menulis)

File input default: exclude_list_sesi_v35.json (folder yg sama)
Target: data/app_words.json
"""

import json
import sys
import argparse
import shutil
from pathlib import Path

EXCLUDE_LIST_PATH = Path("exclude_list_sesi_v35.json")
APP_WORDS_PATH = Path("data") / "app_words.json"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true",
                         help="Tulis perubahan beneran (default: dry-run saja)")
    parser.add_argument("--exclude-list", type=str, default=None,
                         help="Path custom ke file exclude list")
    parser.add_argument("--words-file", type=str, default=None,
                         help="Path custom ke app_words.json")
    args = parser.parse_args()

    exclude_path = Path(args.exclude_list) if args.exclude_list else EXCLUDE_LIST_PATH
    words_path = Path(args.words_file) if args.words_file else APP_WORDS_PATH

    if not exclude_path.exists():
        print(f"ERROR: file tidak ditemukan: {exclude_path}")
        sys.exit(1)
    if not words_path.exists():
        print(f"ERROR: file tidak ditemukan: {words_path}")
        sys.exit(1)

    with open(exclude_path, encoding="utf-8") as f:
        exclude_list = json.load(f)

    # bikin lookup: main_word -> set(candidate yg harus dibuang)
    to_remove = {}
    for item in exclude_list:
        to_remove.setdefault(item["main_word"], set()).add(item["candidate"])

    with open(words_path, encoding="utf-8") as f:
        words = json.load(f)

    print("=" * 70)
    print(f"BERSIHKAN RELASI JANGGAL -- SESI v35 ({len(exclude_list)} pasangan target)")
    print("=" * 70)

    removed_log = []
    words_touched = 0

    for entry in words:
        simp = entry.get("simplified", "")
        candidates = to_remove.get(simp)
        if not candidates:
            continue

        touched_this_word = False

        # field lama (list of string)
        for field in ("synonyms", "antonyms"):
            old_list = entry.get(field) or []
            new_list = [w for w in old_list if w not in candidates]
            if len(new_list) != len(old_list):
                removed = set(old_list) - set(new_list)
                for r in removed:
                    removed_log.append((simp, field, r))
                entry[field] = new_list
                touched_this_word = True

        # field detail (list of dict {"word": ...})
        for field in ("synonyms_detail", "antonyms_detail"):
            old_list = entry.get(field) or []
            new_list = [d for d in old_list if d.get("word") not in candidates]
            if len(new_list) != len(old_list):
                removed = {d.get("word") for d in old_list} - {d.get("word") for d in new_list}
                for r in removed:
                    removed_log.append((simp, field, r))
                entry[field] = new_list
                touched_this_word = True

        if touched_this_word:
            words_touched += 1

    print(f"\n{len(removed_log)} relasi ditemukan & akan dibuang, dari {words_touched} kata:\n")
    for simp, field, cand in removed_log:
        print(f"  {simp} -> {cand}  [{field}]")

    matched_pairs = {(simp, cand) for simp, field, cand in removed_log}
    unmatched = [
        (mw, c) for mw, cands in to_remove.items() for c in cands
        if (mw, c) not in matched_pairs
    ]
    if unmatched:
        print(f"\n[PERINGATAN] {len(unmatched)} pasangan di exclude-list TIDAK ditemukan "
              f"di app_words.json (mungkin sudah dibuang manual sebelumnya, atau kata/relasinya "
              f"beda dari yg tercatat):")
        for mw, c in unmatched:
            print(f"  {mw} -> {c}")

    if not args.apply:
        print("\nIni baru dry-run. Jalankan ulang dgn --apply utk menulis perubahan beneran.")
        return

    backup_path = words_path.with_suffix(words_path.suffix + ".bak")
    shutil.copy(words_path, backup_path)
    print(f"\nBackup ditulis ke: {backup_path}")

    with open(words_path, "w", encoding="utf-8") as f:
        json.dump(words, f, ensure_ascii=False, indent=2)
    print(f"Perubahan diterapkan ke: {words_path}")


if __name__ == "__main__":
    main()

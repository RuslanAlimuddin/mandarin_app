"""
bersihkan_relasi_janggal_batch4.py
====================================
Membersihkan relasi sinonim/antonim yang salah (hipernim/hiponim, wrong-sense,
atau self-admitted beda makna) hasil review manual Claude atas ~900 kata Tier B
(pilot v3 + 8 cycle reguler, sesi BLUEPRINT v31->v32).

DESAIN AMAN (pelajaran dari insiden batch3 v1):
  - HANYA memproses pasangan (word, related, relation_type) yang eksplisit
    tercantum di flagged_relations_batch4.json.
  - TIDAK ADA pattern-matching / regex terhadap note_id atau field lain.
    Kalau suatu hari mau menambah heuristik pattern-matching lagi, itu
    HARUS report-only (seperti batch3 v2), tidak boleh langsung menghapus.
  - Default = DRY RUN. Harus pakai --apply eksplisit untuk menulis perubahan.
  - Default HANYA memproses daftar "high_confidence". Pasangan di
    "borderline_review_needed" TIDAK disentuh kecuali --include-borderline.
  - Backup via checkpoint.py (kalau modul itu ada di folder yang sama)
    dipanggil otomatis sebelum --apply menulis apa pun.

Cara pakai:
  python bersihkan_relasi_janggal_batch4.py                     # dry-run, high-confidence saja
  python bersihkan_relasi_janggal_batch4.py --include-borderline # dry-run, termasuk borderline
  python bersihkan_relasi_janggal_batch4.py --apply              # eksekusi beneran, high-confidence saja
  python bersihkan_relasi_janggal_batch4.py --apply --include-borderline

File yang dibutuhkan di folder yang sama:
  - app_words.json
  - flagged_relations_batch4.json
"""

import json
import sys
import argparse
import subprocess
from pathlib import Path

APP_WORDS_PATH = Path("data/app_words.json")
FLAGGED_PATH = Path("flagged_relations_batch4.json")

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
    """app_words.json diasumsikan list of dict dengan key 'simplified'.
    Sesuaikan kalau struktur lokal beda."""
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
        before = len(lst)
        # item detail biasanya dict {"word": ..., "note_id": ...} tapi
        # beberapa hasil AI berupa string polos (lihat catatan v3.2
        # normalize_relation_items() di BLUEPRINT v31) -- tangani dua-duanya
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

    removed_old = removed_detail = False
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
    if args.include_borderline:
        pairs += list(flagged.get("borderline_review_needed", []))

    print("=" * 70)
    print(f"BERSIHKAN RELASI JANGGAL - BATCH 4 {'(APPLY)' if args.apply else '(DRY RUN)'}")
    print(f"Total pasangan diproses: {len(pairs)}"
          f" ({'termasuk borderline' if args.include_borderline else 'high-confidence saja'})")
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
                 "--note", "sebelum bersihkan_relasi_janggal_batch4 --apply"],
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
    # simetris: proses arah word->related, DAN cek arah balik related->word
    # (kalau relasi itu resiprokal di data, dua-duanya perlu dibersihkan)
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

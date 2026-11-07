"""
bersihkan_relasi_janggal_batch3.py — v2 (setelah insiden over-deletion)
=========================================================================
RIWAYAT: versi pertama skrip ini (jalan pertama kali) menghapus 1.800
relasi -- JAUH melebihi ~150 pasangan yang sudah diverifikasi manual sesi
lalu. Setelah dicek, mayoritas yang terhapus adalah PATTERN MATCHING
"false positive": trigger seperti "更" (substring dari "更广"/"更宽"),
kata "偏" sendirian, dan frasa umum Indonesia ("tidak selalu", "khusus
untuk", "jarang") ternyata muncul di RIBUAN note_id yang sehat/valid --
bukan cuma di kasus janggal. رسلان sudah restore dari backup
(data\\app_words.json.bak).

PERUBAHAN DESAIN v2 (supaya insiden ini tidak terulang):

  1. PATTERN MATCHING sekarang HANYA REPORT, TIDAK PERNAH auto-hapus --
     bahkan dengan --apply. Ini murni alat bantu رسلان untuk MENEMUKAN
     kandidat baru yang perlu di-review manual (spt yang رسلان lakukan
     manual sepanjang sesi pilot kemarin, satu per satu di chat).
  2. Trigger phrase dipersempit drastis -- hanya frasa yang SANGAT
     eksplisit mengaku "ini bukan relasi yang tepat" (bukan sekadar
     kata "umum/luas" yang muncul di deskripsi nuansa normal).
  3. Yang BENAR-BENAR dihapus dengan --apply HANYA pasangan di
     flagged_relations_batch3.json -- daftar ~150 pasangan yang sudah
     رسلان + Claude verifikasi manual satu-satu sepanjang sesi pilot,
     BUKAN hasil pattern matching otomatis.

Alur kerja yang disarankan ke depan:
  a. Jalankan skrip ini (dry-run) -- lihat 2 laporan terpisah:
     "AKAN DIHAPUS" (dari daftar eksplisit) dan "KANDIDAT UNTUK DI-REVIEW"
     (dari pattern matching, TIDAK dihapus otomatis).
  b. رسلان baca daftar "KANDIDAT UNTUK DI-REVIEW" manual, pilih yang
     benar-benar janggal.
  c. Kandidat yang dikonfirmasi janggal ditambahkan ke
     flagged_relations_batch3.json (atau file batch baru), BARU di-apply.

Cara pakai:
    python bersihkan_relasi_janggal_batch3.py                 # dry-run, 2 laporan
    python bersihkan_relasi_janggal_batch3.py --apply          # hapus HANYA daftar eksplisit
    python bersihkan_relasi_janggal_batch3.py --apply --backup # + simpan .bak dulu
"""

import json
import re
import sys
import shutil
from pathlib import Path

APP_WORDS_PATH = Path("data") / "app_words.json"
FLAGGED_PAIRS_PATH = Path("flagged_relations_batch3.json")

FIELD_SIMPLIFIED = "simplified"
FIELD_SYN_OLD = "synonyms"
FIELD_ANT_OLD = "antonyms"
FIELD_SYN_DETAIL = "synonyms_detail"
FIELD_ANT_DETAIL = "antonyms_detail"

# ======================================================================
# Trigger frasa v2 -- DIPERSEMPIT DRASTIS. Hanya frasa yang eksplisit
# mengaku "ini bukan relasi yang tepat/lazim", bukan sekadar penjelasan
# nuansa umum/luas yang wajar ada di deskripsi sinonim normal.
#
# SENGAJA DIBUANG dari v1 krn terbukti generik & bikin false positive
# masif: "lebih umum", "lebih luas", "cakupan lebih luas", "tidak
# khusus", "tidak selalu", "belum tentu", "bukan selalu", "lebih
# sempit", "lebih spesifik", "khusus untuk", "khusus konteks", "jarang",
# "范围更广", "范围更宽", "更广", "更宽", "更宽泛", "偏".
# ======================================================================
TRIGGER_PHRASES = [
    "bukan sinonim",
    "tidak sepenuhnya sepadan",
    "tidak sepadan",
    "tidak lazim",
    "tidak disarankan",
    "sebaiknya hindari",
    "sebaiknya gunakan",
    "dipaksakan",
    "bukan istilah",
    "hanya cocok untuk",
    "hanya dalam konteks",
    "hanya di konteks",
    # Mandarin -- versi eksplisit saja, bukan "更广"/"更宽"/"偏" generik
    "不完全等同",
    "不选定",
    "不作为同义词",
    "不等同于",
]
_TRIGGER_RE = re.compile("|".join(re.escape(p) for p in TRIGGER_PHRASES), re.IGNORECASE)


def load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def load_flagged_pairs():
    if not FLAGGED_PAIRS_PATH.exists():
        print(f"[peringatan] {FLAGGED_PAIRS_PATH} tidak ditemukan.")
        return set()
    pairs = load_json(FLAGGED_PAIRS_PATH)
    return {(p["word"], p["target"]) for p in pairs}


def iter_entries(data):
    if isinstance(data, list):
        for entry in data:
            yield entry.get(FIELD_SIMPLIFIED), entry
    elif isinstance(data, dict):
        for key, entry in data.items():
            yield entry.get(FIELD_SIMPLIFIED, key), entry
    else:
        raise TypeError("Struktur app_words.json tidak dikenali.")


def scan_entry(word, entry, flagged_pairs, to_delete_report, review_report):
    """Satu kali scan per entri: pisahkan hasil jadi dua kelompok --
    to_delete_report (dari daftar eksplisit, akan benar2 dihapus kalau
    --apply) dan review_report (dari pattern matching, HANYA laporan,
    TIDAK PERNAH dihapus otomatis)."""
    for detail_field in (FIELD_SYN_DETAIL, FIELD_ANT_DETAIL):
        items = entry.get(detail_field)
        if not items:
            continue

        seen_words = set()
        for it in items:
            if not isinstance(it, dict):
                continue
            w = it.get("word")
            note = it.get("note_id", "")

            if w in seen_words:
                to_delete_report.append((word, detail_field, w, "duplikat dalam array"))
                continue
            seen_words.add(w)

            if (word, w) in flagged_pairs:
                to_delete_report.append((word, detail_field, w, "daftar eksplisit"))
            elif note and _TRIGGER_RE.search(note):
                review_report.append((word, detail_field, w, note))


def apply_deletions(data, to_delete_report):
    """Hapus HANYA item yang masuk to_delete_report (daftar eksplisit +
    duplikat) -- tidak pernah dari review_report."""
    to_delete_set = {(w, f, t) for w, f, t, _ in to_delete_report}
    total = 0
    for word, entry in iter_entries(data):
        if word is None:
            continue
        for detail_field, old_field in (
            (FIELD_SYN_DETAIL, FIELD_SYN_OLD),
            (FIELD_ANT_DETAIL, FIELD_ANT_OLD),
        ):
            items = entry.get(detail_field)
            if not items:
                continue
            seen = set()
            new_items = []
            removed_words = []
            for it in items:
                if not isinstance(it, dict):
                    continue
                w = it.get("word")
                key = (word, detail_field, w)
                is_dup = w in seen
                seen.add(w)
                if key in to_delete_set or is_dup:
                    removed_words.append(w)
                    total += 1
                    continue
                new_items.append(it)
            if removed_words:
                entry[detail_field] = new_items
                if old_field in entry and isinstance(entry[old_field], list):
                    entry[old_field] = [x for x in entry[old_field] if x not in removed_words]
    return total


def main():
    apply_changes = "--apply" in sys.argv
    do_backup = "--backup" in sys.argv

    if not APP_WORDS_PATH.exists():
        print(f"ERROR: {APP_WORDS_PATH} tidak ditemukan. Jalankan dari C:\\mandarin_app\\.")
        return

    flagged_pairs = load_flagged_pairs()
    data = load_json(APP_WORDS_PATH)

    to_delete_report = []
    review_report = []

    for word, entry in iter_entries(data):
        if word is None:
            continue
        scan_entry(word, entry, flagged_pairs, to_delete_report, review_report)

    print("=" * 70)
    print(f"AKAN DIHAPUS (daftar eksplisit + duplikat): {len(to_delete_report)}")
    print("=" * 70)
    for word, field_name, target, reason in to_delete_report:
        print(f"  {word} -- {field_name} -- {target}  [{reason}]")

    print("\n" + "=" * 70)
    print(f"KANDIDAT UNTUK DI-REVIEW MANUAL (TIDAK dihapus otomatis): {len(review_report)}")
    print("=" * 70)
    print("(Pattern matching hanya alat bantu menemukan kandidat -- baca note_id")
    print(" di bawah, cek manual, baru tambahkan ke flagged_relations_batch3.json")
    print(" kalau memang janggal. TIDAK pernah dihapus otomatis oleh --apply.)\n")
    for word, field_name, target, note in review_report:
        print(f"  {word} -- {field_name} -- {target}  note: \"{note}\"")

    if not apply_changes:
        print(f"\n[DRY RUN] Tidak ada file yang diubah.")
        print(f"Jalankan --apply --backup untuk benar2 menghapus {len(to_delete_report)} item di atas")
        print("(daftar eksplisit saja -- kandidat review TIDAK akan ikut terhapus).")
        return

    if do_backup:
        backup_path = APP_WORDS_PATH.with_suffix(".json.bak")
        shutil.copy(APP_WORDS_PATH, backup_path)
        print(f"\nBackup disimpan ke {backup_path}")

    total_deleted = apply_deletions(data, to_delete_report)
    save_json(APP_WORDS_PATH, data)
    print(f"\n{APP_WORDS_PATH} sudah ditimpa dengan {total_deleted} relasi terhapus (HANYA dari daftar eksplisit + duplikat).")
    print("Jangan lupa jalankan checkpoint.py save setelah ini.")


if __name__ == "__main__":
    main()

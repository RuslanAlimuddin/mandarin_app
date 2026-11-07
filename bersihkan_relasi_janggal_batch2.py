"""
bersihkan_relasi_janggal_batch2.py — READ-ONLY kecuali dijalankan tanpa --dry-run.

Batch kedua pembersihan relasi sinonim/antonim yang keliru, ditemukan lewat
review manual selama proses apply Tier B (E.0.2b lanjutan) SETELAH batch
pertama (lihat bersihkan_relasi_janggal.py, 16 relasi, sudah dijalankan).

Cara pakai:
    cd C:\\mandarin_app
    python bersihkan_relasi_janggal_batch2.py --dry-run
    python bersihkan_relasi_janggal_batch2.py
"""

import json
import os
import sys
import shutil
from datetime import datetime

PATH_WORDS = os.path.join("data", "app_words.json")
DRY_RUN = "--dry-run" in sys.argv

DAFTAR_HAPUS = [
    ("瓜", "synonyms", "果", "hipernim (果=buah scr umum) & kurang tepat kategori (瓜 sering dianggap sayur, bkn buah)"),
    ("瓜", "synonyms", "果实", "hipernim (果实=hasil tanaman scr umum), bukan sinonim"),
    ("证书", "synonyms", "文凭", "hiponim (文凭=jenis spesifik utk pendidikan), bukan sinonim"),
    ("证书", "synonyms", "执照", "hiponim (执照=jenis spesifik utk izin profesi), bukan sinonim"),
    ("法规", "synonyms", "法律", "hipernim (法规 adalah BAGIAN dari 法律), bukan sinonim"),
    ("面子", "synonyms", "表面", "面子 sehari-hari berarti 'harga diri/gengsi', bukan 'permukaan' harfiah"),
    ("面子", "synonyms", "外面", "面子 sehari-hari berarti 'harga diri/gengsi', bukan 'permukaan' harfiah"),
    ("面子", "antonyms", "里面", "面子 sehari-hari berarti 'harga diri/gengsi', bukan 'permukaan' harfiah"),
]


def remove_from_plain(arr, target):
    if not arr:
        return arr, False
    if target in arr:
        return [x for x in arr if x != target], True
    return arr, False


def remove_from_detail(arr, target):
    if not arr:
        return arr, False
    new_arr = [x for x in arr if x.get("word") != target]
    return new_arr, len(new_arr) != len(arr)


def main():
    with open(PATH_WORDS, "r", encoding="utf-8") as f:
        words = json.load(f)

    words_by_key = {w.get("simplified"): w for w in words}

    print("=" * 70)
    print(f"PEMBERSIHAN BATCH 2 -- {len(DAFTAR_HAPUS)} RELASI JANGGAL")
    print("=" * 70)

    berhasil = []
    tidak_ditemukan = []

    for main_word, field, target, alasan in DAFTAR_HAPUS:
        w = words_by_key.get(main_word)
        if not w:
            tidak_ditemukan.append((main_word, field, target, "kata utama tidak ditemukan di app_words.json"))
            continue

        detail_field = field + "_detail"
        found_plain = found_detail = False

        if field in w:
            new_plain, found_plain = remove_from_plain(w[field], target)
            if found_plain:
                w[field] = new_plain

        if detail_field in w:
            new_detail, found_detail = remove_from_detail(w[detail_field], target)
            if found_detail:
                w[detail_field] = new_detail

        if found_plain or found_detail:
            berhasil.append((main_word, field, target, alasan))
            print(f"  [HAPUS] {main_word} -- {field}: {target}")
            print(f"          alasan: {alasan}")
        else:
            tidak_ditemukan.append((main_word, field, target, "relasi tidak ditemukan (mungkin sudah dihapus/belum di-apply)"))

    print(f"\nBerhasil dihapus: {len(berhasil)}/{len(DAFTAR_HAPUS)}")
    if tidak_ditemukan:
        print(f"\nTIDAK ditemukan (dilewati, cek manual kalau perlu): {len(tidak_ditemukan)}")
        for main_word, field, target, alasan in tidak_ditemukan:
            print(f"  - {main_word} / {field} / {target}: {alasan}")

    if DRY_RUN:
        print("\n[DRY RUN] Tidak ada file yang ditulis. Jalankan tanpa --dry-run untuk apply.")
        return

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = PATH_WORDS + f".bak_before_bersihkan_relasi_janggal_batch2_{ts}"
    shutil.copy2(PATH_WORDS, backup_path)
    print(f"\nBackup dibuat: {backup_path}")

    with open(PATH_WORDS, "w", encoding="utf-8") as f:
        json.dump(words, f, ensure_ascii=False, indent=2)

    print(f"\n[SELESAI] {len(berhasil)} relasi janggal dihapus dari app_words.json.")
    print("Jangan lupa: jalankan checkpoint.py save setelah ini.")


if __name__ == "__main__":
    main()

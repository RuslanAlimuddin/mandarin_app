"""
bersihkan_relasi_janggal.py — READ-ONLY kecuali dijalankan tanpa --dry-run.

Menghapus relasi sinonim/antonim yang keliru, ditemukan lewat review manual
selama proses apply Tier B (E.0.2b lanjutan). Menghapus dari SEMUA field
terkait: synonyms/antonyms (array string) DAN synonyms_detail/antonyms_detail
(array object dgn pinyin+note_id).

Cara pakai:
    cd C:\\mandarin_app
    python bersihkan_relasi_janggal.py --dry-run
    python bersihkan_relasi_janggal.py
"""

import json
import os
import sys
import shutil
from datetime import datetime

PATH_WORDS = os.path.join("data", "app_words.json")
DRY_RUN = "--dry-run" in sys.argv

# (kata utama, field, kata yang harus dihapus dari field itu, alasan singkat)
DAFTAR_HAPUS = [
    ("当", "synonyms", "咚", "咚 cuma onomatope bunyi, tidak nyambung makna dgn 当"),
    ("铁", "synonyms", "金属", "hipernim (besi ADALAH jenis logam), bukan sinonim"),
    ("冰雪", "synonyms", "雪冰", "bukan kata Mandarin lazim, kemungkinan halusinasi (pembalikan karakter)"),
    ("瓜", "synonyms", "甜瓜", "hipernim (甜瓜 adalah JENIS 瓜), bukan sinonim"),
    ("瓜", "synonyms", "南瓜", "hipernim (南瓜 adalah JENIS 瓜), bukan sinonim"),
    ("细节", "synonyms", "详节", "bukan kata Mandarin lazim, kemungkinan halusinasi"),
    ("竟然", "antonyms", "当然", "当然 = penegasan, bukan lawan makna 'tak disangka'"),
    ("胶带", "synonyms", "透明胶带", "hiponim (透明胶带 adalah JENIS 胶带), bukan sinonim"),
    ("入门", "synonyms", "入口", "入门 lebih sering berarti 'dasar/pemula', bukan 'pintu masuk' harfiah"),
    ("入门", "antonyms", "出口", "入门 lebih sering berarti 'dasar/pemula', bukan 'pintu masuk' harfiah"),
    ("研究生", "synonyms", "硕士生", "hiponim (硕士生 adalah JENIS 研究生), bukan sinonim"),
    ("研究生", "synonyms", "博士生", "hiponim (博士生 adalah JENIS 研究生), bukan sinonim"),
    ("迷信", "synonyms", "愚信", "bukan kata Mandarin lazim, kemungkinan halusinasi"),
    ("大于", "antonyms", "等于", "salah logika -- lawan 'lebih besar dari' itu 'kurang dari', bukan 'sama dengan'"),
    ("被动", "synonyms", "被逼", "被逼='terpaksa' -- konsep berdekatan tapi tidak identik dgn 'pasif'"),
    ("受灾", "synonyms", "遇难", "遇难='tewas dlm kecelakaan/bencana' -- jauh lebih parah & beda makna dari 'terdampak'"),
]


def remove_from_plain(arr, target):
    """Hapus target dari array string. Return (array_baru, ditemukan?)."""
    if not arr:
        return arr, False
    if target in arr:
        return [x for x in arr if x != target], True
    return arr, False


def remove_from_detail(arr, target):
    """Hapus target dari array object {'word': ...}. Return (array_baru, ditemukan?)."""
    if not arr:
        return arr, False
    new_arr = [x for x in arr if x.get("word") != target]
    return new_arr, len(new_arr) != len(arr)


def main():
    with open(PATH_WORDS, "r", encoding="utf-8") as f:
        words = json.load(f)

    words_by_key = {w.get("simplified"): w for w in words}

    print("=" * 70)
    print(f"PEMBERSIHAN {len(DAFTAR_HAPUS)} RELASI JANGGAL")
    print("=" * 70)

    berhasil = []
    tidak_ditemukan = []

    for main_word, field, target, alasan in DAFTAR_HAPUS:
        w = words_by_key.get(main_word)
        if not w:
            tidak_ditemukan.append((main_word, field, target, "kata utama tidak ditemukan di app_words.json"))
            continue

        plain_field = field  # "synonyms" / "antonyms"
        detail_field = field[:-1] + "_detail" if field.endswith("s") else field + "_detail"
        # field sudah "synonyms"/"antonyms" -> detail = "synonyms_detail"/"antonyms_detail"
        detail_field = field + "_detail"

        found_plain = found_detail = False

        if plain_field in w:
            new_plain, found_plain = remove_from_plain(w[plain_field], target)
            if found_plain:
                w[plain_field] = new_plain

        if detail_field in w:
            new_detail, found_detail = remove_from_detail(w[detail_field], target)
            if found_detail:
                w[detail_field] = new_detail

        if found_plain or found_detail:
            berhasil.append((main_word, field, target, alasan))
            print(f"  [HAPUS] {main_word} -- {field}: {target}")
            print(f"          alasan: {alasan}")
        else:
            tidak_ditemukan.append((main_word, field, target, "relasi tidak ditemukan (mungkin sudah dihapus sebelumnya)"))

    print(f"\nBerhasil dihapus: {len(berhasil)}/{len(DAFTAR_HAPUS)}")
    if tidak_ditemukan:
        print(f"\nTIDAK ditemukan (dilewati, cek manual kalau perlu): {len(tidak_ditemukan)}")
        for main_word, field, target, alasan in tidak_ditemukan:
            print(f"  - {main_word} / {field} / {target}: {alasan}")

    if DRY_RUN:
        print("\n[DRY RUN] Tidak ada file yang ditulis. Jalankan tanpa --dry-run untuk apply.")
        return

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = PATH_WORDS + f".bak_before_bersihkan_relasi_janggal_{ts}"
    shutil.copy2(PATH_WORDS, backup_path)
    print(f"\nBackup dibuat: {backup_path}")

    with open(PATH_WORDS, "w", encoding="utf-8") as f:
        json.dump(words, f, ensure_ascii=False, indent=2)

    print(f"\n[SELESAI] {len(berhasil)} relasi janggal dihapus dari app_words.json.")
    print("Jangan lupa: jalankan checkpoint.py save setelah ini.")


if __name__ == "__main__":
    main()

"""
scope_kata_majemuk_full.py
============================
Lanjutan dari scope_kata_majemuk.py -- kali ini cakupan PENUH:
- Semua kata 2-karakter, di SEMUA level HSK (termasuk HSK 7-9 dan yang
  tanpa HSK sama sekali).
- Laporan (bukan daftar untuk diklasifikasi) kata 3+ karakter, karena
  skema 5-pola (联合式/偏正式/动宾式/主谓式/补充式) dirancang untuk
  struktur 2-karakter -- kata 3+ karakter perlu skema/pendekatan
  terpisah yang belum dirancang.

READ-ONLY, tidak mengubah app_words.json sama sekali.

Cara pakai:
    python scope_kata_majemuk_full.py

Output:
- Laporan tabel di layar (breakdown per panjang kata x HSK).
- kata_majemuk_candidates_2char_ALL.json  -> semua kata 2-karakter,
  semua level HSK termasuk null kalau tidak ada HSK. INI daftar
  kandidat lengkap untuk klasifikasi pola (belum diklasifikasi).
- kata_majemuk_3plus_INFO_ONLY.json -> daftar kata 3+ karakter, HANYA
  untuk referensi/diskusi skema masa depan, BUKAN untuk diklasifikasi
  dengan skema 5-pola yang sekarang.
"""

import json
import os
import sys
from collections import Counter, defaultdict

DATA_PATH = os.path.join("data", "app_words.json")
OUT_2CHAR = "kata_majemuk_candidates_2char_ALL.json"
OUT_3PLUS = "kata_majemuk_3plus_INFO_ONLY.json"


def load_words():
    if not os.path.exists(DATA_PATH):
        print(f"[ERROR] Tidak ketemu {DATA_PATH}")
        print("        Jalankan script ini dari folder C:\\mandarin_app\\")
        sys.exit(1)
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        raw = json.load(f)
    if isinstance(raw, list):
        return raw
    if isinstance(raw, dict):
        for key in ("words", "data", "entries", "items"):
            if key in raw and isinstance(raw[key], list):
                return raw[key]
        print("[ERROR] Struktur dict tidak dikenali. Key:", list(raw.keys()))
        sys.exit(1)
    print("[ERROR] Struktur app_words.json tidak dikenali.")
    sys.exit(1)


def hsk_to_num(hsk_raw):
    if hsk_raw is None:
        return None
    digits = "".join(ch for ch in str(hsk_raw) if ch.isdigit())
    return int(digits) if digits else None


def main():
    words = load_words()
    total = len(words)
    print(f"Total entri di app_words.json: {total}\n")

    # field sudah kita ketahui dari run sebelumnya, tapi tetap dideteksi
    # ulang secara defensif kalau-kalau strukturnya beda di masa depan.
    sample = words[0]
    hanzi_key = "simplified" if "simplified" in sample else None
    hsk_key = "hsk" if "hsk" in sample else None
    pinyin_key = "pinyin" if "pinyin" in sample else None
    if not hanzi_key:
        for k in sample.keys():
            if k.lower() in ("word", "hanzi", "char", "chars"):
                hanzi_key = k
    if not hanzi_key:
        print("[STOP] Field hanzi tidak terdeteksi. Field tersedia:", list(sample.keys()))
        sys.exit(1)

    # breakdown: panjang kata -> {hsk_num_or_'none': jumlah}
    breakdown = defaultdict(Counter)
    length_dist = Counter()

    words_2char = []
    words_3plus = []

    for entry in words:
        hanzi = entry.get(hanzi_key, "") or ""
        length = len(hanzi)
        length_dist[length] += 1

        if length < 2:
            continue  # 1 karakter: tidak relevan untuk pola majemuk sama sekali

        hsk_raw = entry.get(hsk_key) if hsk_key else None
        hsk_num = hsk_to_num(hsk_raw)
        bucket_label = str(hsk_num) if hsk_num is not None else "tanpa_hsk"
        breakdown[length][bucket_label] += 1

        record = {
            "word": hanzi,
            "pinyin": entry.get(pinyin_key, "") if pinyin_key else "",
            "hsk": hsk_num,  # null kalau tidak ada
        }

        if length == 2:
            words_2char.append(record)
        else:
            record["length"] = length
            words_3plus.append(record)

    # --- laporan ---
    print("=== Distribusi panjang kata (semua entri) ===")
    for length in sorted(length_dist):
        label = f"{length} karakter"
        print(f"  {label:14s}: {length_dist[length]}")

    print("\n=== Breakdown kata 2-karakter per HSK (SEMUA level, termasuk 7-9 & tanpa HSK) ===")
    total_2char = 0
    for lvl_label in sorted(breakdown[2].keys(), key=lambda x: (x == "tanpa_hsk", x)):
        cnt = breakdown[2][lvl_label]
        total_2char += cnt
        print(f"  HSK {lvl_label:10s}: {cnt}")
    print(f"  TOTAL kata 2-karakter (semua HSK + tanpa HSK): {total_2char}")

    print("\n=== Breakdown kata 3+ karakter per panjang (info saja, skema pola belum ada) ===")
    total_3plus = 0
    for length in sorted(k for k in breakdown.keys() if k >= 3):
        cnt = sum(breakdown[length].values())
        total_3plus += cnt
        print(f"  {length} karakter: {cnt}")
    print(f"  TOTAL kata 3+ karakter: {total_3plus}")

    # --- simpan file ---
    with open(OUT_2CHAR, "w", encoding="utf-8") as f:
        json.dump(words_2char, f, ensure_ascii=False, indent=2)
    print(f"\nDisimpan: {OUT_2CHAR}  ({len(words_2char)} kata -- INI daftar kandidat klasifikasi pola)")

    with open(OUT_3PLUS, "w", encoding="utf-8") as f:
        json.dump(words_3plus, f, ensure_ascii=False, indent=2)
    print(f"Disimpan: {OUT_3PLUS}  ({len(words_3plus)} kata -- REFERENSI SAJA, bukan untuk diklasifikasi sekarang)")

    print("\nContoh 5 kata 2-karakter dari HSK 7 (buat gambaran isi luar HSK 1-6):")
    hsk7_samples = [w for w in words_2char if w["hsk"] == 7][:5]
    for w in hsk7_samples:
        print(f"  {w['word']} ({w['pinyin']})")

    print("\nContoh 5 kata 2-karakter TANPA HSK sama sekali:")
    none_samples = [w for w in words_2char if w["hsk"] is None][:5]
    for w in none_samples:
        print(f"  {w['word']} ({w['pinyin']})")


if __name__ == "__main__":
    main()

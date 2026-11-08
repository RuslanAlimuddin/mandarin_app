"""
scope_kata_majemuk.py
======================
Script scoping (READ-ONLY, tidak mengubah data apa pun) untuk fitur baru
"Pola Pembentukan Kata Majemuk".

Tujuan: hitung berapa banyak kata 2-karakter di app_words.json yang HSK 1-6,
supaya kita tahu skala sebelum merancang prompt+skema klasifikasi.

Cara pakai:
    python scope_kata_majemuk.py

Tidak butuh argumen. Aman dijalankan berkali-kali, tidak menulis apa pun
kecuali file laporan `kata_majemuk_candidates.json` (daftar kandidat mentah,
belum diklasifikasi) di folder yang sama dengan script ini.
"""

import json
import os
import sys
from collections import Counter

DATA_PATH = os.path.join("data", "app_words.json")
OUTPUT_PATH = "kata_majemuk_candidates.json"


def load_words():
    if not os.path.exists(DATA_PATH):
        print(f"[ERROR] Tidak ketemu {DATA_PATH}")
        print("        Jalankan script ini dari folder C:\\mandarin_app\\ (folder induk 'data').")
        sys.exit(1)
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        raw = json.load(f)
    # app_words.json bisa berupa list langsung, atau dict dengan key seperti "words"/"data"
    if isinstance(raw, list):
        return raw
    if isinstance(raw, dict):
        for key in ("words", "data", "entries", "items"):
            if key in raw and isinstance(raw[key], list):
                return raw[key]
        # fallback: kalau dict tapi tidak ketemu key yang jelas, kasih tahu strukturnya
        print("[WARN] app_words.json berupa dict tapi key list tidak dikenali.")
        print("       Key yang ada:", list(raw.keys()))
        sys.exit(1)
    print("[ERROR] Struktur app_words.json tidak dikenali.")
    sys.exit(1)


def detect_fields(sample):
    """Coba tebak nama field hanzi/pinyin/hsk dari 1 entri sampel."""
    hanzi_key = None
    hsk_key = None
    pinyin_key = None
    for k in sample.keys():
        lk = k.lower()
        if hanzi_key is None and lk in ("word", "hanzi", "simplified", "char", "chars"):
            hanzi_key = k
        if hsk_key is None and "hsk" in lk:
            hsk_key = k
        if pinyin_key is None and "pinyin" in lk:
            pinyin_key = k
    return hanzi_key, hsk_key, pinyin_key


def main():
    words = load_words()
    print(f"Total entri di app_words.json: {len(words)}")

    if not words:
        print("[ERROR] File kosong.")
        sys.exit(1)

    sample = words[0]
    print("\nContoh 1 entri (buat cek struktur field):")
    print(json.dumps(sample, ensure_ascii=False, indent=2)[:500])

    hanzi_key, hsk_key, pinyin_key = detect_fields(sample)
    print(f"\nField terdeteksi -> hanzi: {hanzi_key!r}, hsk: {hsk_key!r}, pinyin: {pinyin_key!r}")

    if not hanzi_key:
        print("\n[STOP] Tidak bisa deteksi field hanzi otomatis.")
        print("       Field yang ada di 1 entri:", list(sample.keys()))
        print("       Kirim output ini ke Claude supaya script bisa disesuaikan.")
        sys.exit(1)

    hsk_distribution = Counter()
    candidates = []
    skipped_no_hsk = 0

    for entry in words:
        hanzi = entry.get(hanzi_key, "")
        if len(hanzi) != 2:
            continue  # hanya kata 2-karakter

        hsk_raw = entry.get(hsk_key) if hsk_key else None
        # normalisasi HSK jadi angka kalau bisa (bisa berupa "HSK3", 3, "3", dst.)
        hsk_num = None
        if hsk_raw is not None:
            digits = "".join(ch for ch in str(hsk_raw) if ch.isdigit())
            if digits:
                hsk_num = int(digits)

        if hsk_num is None:
            skipped_no_hsk += 1
            continue

        hsk_distribution[hsk_num] += 1

        if 1 <= hsk_num <= 6:
            candidates.append({
                "word": hanzi,
                "pinyin": entry.get(pinyin_key, "") if pinyin_key else "",
                "hsk": hsk_num,
            })

    print("\n--- Distribusi HSK untuk semua kata 2-karakter ---")
    for lvl in sorted(hsk_distribution):
        print(f"  HSK {lvl}: {hsk_distribution[lvl]} kata")
    if skipped_no_hsk:
        print(f"  (tanpa HSK / tidak terbaca: {skipped_no_hsk} kata, di-skip)")

    print(f"\n=== TOTAL kandidat 2-karakter HSK 1-6: {len(candidates)} ===")

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(candidates, f, ensure_ascii=False, indent=2)
    print(f"\nDaftar kandidat mentah disimpan ke: {OUTPUT_PATH}")
    print("(Ini BELUM diklasifikasi pola-nya -- ini cuma daftar mentah untuk cek skala dulu.)")

    print("\nContoh 10 kandidat pertama:")
    for c in candidates[:10]:
        print(f"  {c['word']} ({c['pinyin']}) - HSK {c['hsk']}")


if __name__ == "__main__":
    main()

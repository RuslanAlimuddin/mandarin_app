"""
intip_app_words.py — cek struktur & sampel acak app_words.json
=================================================================
Tujuan: memberi gambaran valid isi app_words.json (struktur field,
statistik kelengkapan data) tanpa perlu membuka file raksasa itu
manual di editor. Aman -- read-only, tidak mengubah apa pun.

Cara pakai (dari C:\\mandarin_app>):
    python intip_app_words.py                  # 5 sampel acak, default
    python intip_app_words.py --n 10            # 10 sampel acak
    python intip_app_words.py --cari 海藻        # cari & tampilkan kata spesifik
    python intip_app_words.py --seed 42          # sampel acak yg reproducible
"""

import argparse
import json
import random
from pathlib import Path

PATH_WORDS = Path("data") / "app_words.json"


def load_words():
    if not PATH_WORDS.exists():
        print(f"ERROR: {PATH_WORDS} tidak ditemukan.")
        print("Jalankan skrip ini dari folder C:\\mandarin_app\\ (bukan dari dalam data\\).")
        raise SystemExit(1)
    with open(PATH_WORDS, "r", encoding="utf-8") as f:
        return json.load(f)


def describe_structure(words):
    print("=" * 70)
    print("STRUKTUR FILE")
    print("=" * 70)
    print(f"Tipe data top-level : {type(words).__name__}")
    if isinstance(words, dict):
        print(f"Jumlah key           : {len(words)}")
        sample_key = next(iter(words))
        print(f"Contoh key           : {sample_key!r}")
        first_entry = words[sample_key]
    elif isinstance(words, list):
        print(f"Jumlah entri          : {len(words)}")
        first_entry = words[0] if words else {}
    else:
        print("Struktur tidak dikenali (bukan list atau dict).")
        return
    print(f"Field pada entri pertama: {sorted(first_entry.keys()) if isinstance(first_entry, dict) else '(bukan dict)'}")


def field_stats(words):
    """Hitung berapa % entri yang punya tiap field kunci -- membantu lihat
    field mana yang sering kosong/tidak ada sama sekali."""
    entries = list(words.values()) if isinstance(words, dict) else words
    total = len(entries)
    if total == 0:
        return

    fields_to_check = [
        "simplified", "pinyin", "synonyms", "antonyms",
        "synonyms_detail", "antonyms_detail", "_tb_empty_streak",
    ]
    print("\n" + "=" * 70)
    print(f"STATISTIK KELENGKAPAN FIELD (dari {total} entri)")
    print("=" * 70)
    for field in fields_to_check:
        count_present = sum(1 for e in entries if isinstance(e, dict) and e.get(field))
        pct = count_present / total * 100
        print(f"  {field:20s}: {count_present:6d}/{total} ({pct:5.1f}%) terisi/tidak-kosong")


def print_sample(words, n, seed=None, search=None):
    entries = list(words.values()) if isinstance(words, dict) else words

    if search:
        matches = [e for e in entries if isinstance(e, dict) and e.get("simplified") == search]
        print("\n" + "=" * 70)
        print(f"HASIL PENCARIAN: '{search}'")
        print("=" * 70)
        if not matches:
            print("  Tidak ditemukan.")
        for m in matches:
            print(json.dumps(m, ensure_ascii=False, indent=2))
        return

    if seed is not None:
        random.seed(seed)
    n = min(n, len(entries))
    sample = random.sample(entries, n)

    print("\n" + "=" * 70)
    print(f"SAMPEL ACAK ({n} entri)")
    print("=" * 70)
    for e in sample:
        print(json.dumps(e, ensure_ascii=False, indent=2))
        print("-" * 40)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=5, help="jumlah sampel acak (default 5)")
    ap.add_argument("--seed", type=int, default=None, help="seed random, biar hasil bisa diulang")
    ap.add_argument("--cari", type=str, default=None, help="cari kata tertentu (persis, field 'simplified')")
    args = ap.parse_args()

    words = load_words()
    describe_structure(words)
    field_stats(words)
    print_sample(words, args.n, seed=args.seed, search=args.cari)


if __name__ == "__main__":
    main()

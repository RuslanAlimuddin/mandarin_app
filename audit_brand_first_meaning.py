#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
audit_brand_first_meaning.py

AUDIT READ-ONLY (tidak mengubah file apa pun).

Latar belakang: kasus 老板 ("Robam" nama merek jadi arti pertama, padahal
seharusnya "pemilik toko") lolos dari audit_app_words_readings.py sesi lalu.
Dugaan: audit sistemik sebelumnya efektif menangkap pola "singkatan dari
<negara/kota>" dan penanda marga/varian/sastra, tapi TIDAK secara khusus
mencari "nama merek dagang" sebagai arti pertama, apalagi di kata majemuk
2+ karakter (bukan cuma karakter tunggal).

Pendekatan: scan SELURUH app_words.json, cari entri yang arti PERTAMA di
meanings_id mengandung sinyal nama merek/brand/proper-noun asing:
  - Ada huruf kapital di tengah kata (pola umum utk nama merek/brand Latin
    yg disisipkan ke teks Indonesia, mis. "Robam", "Hyundai", "Volkswagen")
  - Frasa "merek dagang", "merek", "perusahaan", "aplikasi", "produsen"
Lalu bandingkan dgn arti KEDUA dst -- kalau ada arti umum/generik di posisi
belakang, ini kandidat kuat utk pola bug yang sama dgn 老板/现代/大众/加/头条
yang sudah kita temukan & benerin di kata TUNGGAL. Fokus laporan ini ke
kata MAJEMUK (2+ karakter) karena kata tunggal kemungkinan sudah tercakup
audit_app_words_readings.py sesi lalu.

Penggunaan:
    python audit_brand_first_meaning.py
    python audit_brand_first_meaning.py --path data/app_words.json
    python audit_brand_first_meaning.py --include-single-char
"""
import json
import re
import argparse
from pathlib import Path

DATA_PATH = Path("data/app_words.json")

BRAND_KEYWORDS = ["merek dagang", "merek", "perusahaan", "aplikasi", "produsen", "singkatan dari"]
# Regex: huruf kapital yang muncul TIDAK di awal string (indikasi nama
# proper-noun/brand disisipkan di tengah kalimat Indonesia)
CAP_MIDWORD_RE = re.compile(r"(?<!^)(?<=[a-z\u00e0-\u017f])[A-Z][a-zA-Z]*")


def load_json(path: Path):
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def iter_entries(data):
    if isinstance(data, dict):
        for k, v in data.items():
            yield k, v
    else:
        for e in data:
            yield e.get("id") or e.get("simplified"), e


def looks_like_brand(text: str) -> bool:
    if not text:
        return False
    lowered = text.lower()
    if any(kw in lowered for kw in BRAND_KEYWORDS):
        return True
    if CAP_MIDWORD_RE.search(text):
        return True
    return False


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--path", default=str(DATA_PATH))
    ap.add_argument("--include-single-char", action="store_true",
                     help="Ikut tampilkan kata 1 karakter (default: hanya kata majemuk 2+)")
    args = ap.parse_args()

    path = Path(args.path)
    if not path.exists():
        print(f"File tidak ditemukan: {path}")
        return

    data = load_json(path)

    print("=== AUDIT: kemungkinan nama merek/proper-noun di arti PERTAMA ===\n")
    hits = 0
    for word, e in iter_entries(data):
        if not word:
            continue
        if not args.include_single_char and len(word) < 2:
            continue
        meanings = e.get("meanings_id") or []
        if not meanings:
            continue
        first = meanings[0]
        if looks_like_brand(first):
            hits += 1
            print(f"--- {word} ({e.get('pinyin')}) ---")
            print(f"  arti pertama (dicurigai): {first}")
            if len(meanings) > 1:
                print(f"  arti lain               : {meanings[1:4]}")
            print()

    print(f"Total kandidat ditemukan: {hits}\n")
    print("--- CATATAN ---")
    print("Ini audit READ-ONLY. Tidak ada file yang diubah.")
    print("False positive mungkin terjadi (mis. nama tempat yang memang arti")
    print("utamanya adalah nama tempat itu sendiri). Perlu sample-check manual")
    print("sebelum ada keputusan reorder/fix, sama seperti kata majemuk yg")
    print("sudah kita tangani (现代/大众/大学/头条/美德) sesi sebelumnya.")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
extract_3_words.py

Ekstrak entri LENGKAP untuk 3 kata terakhir yang perlu data penuh sebelum
ditulis perbaikannya: 号, 看, 说

Tidak mengubah app_words.json apa pun -- murni membaca & menulis file baru.

Penggunaan (dari C:\\mandarin_app>):
    python extract_3_words.py

Hasil tersimpan di: 3_words_extract.json
"""
import json
from pathlib import Path

DATA_PATH = Path("data/app_words.json")
OUTPUT_PATH = Path("3_words_extract.json")

WORDS = ["号", "看", "说"]


def main():
    if not DATA_PATH.exists():
        print(f"File tidak ditemukan: {DATA_PATH}")
        print("Pastikan menjalankan script ini dari C:\\mandarin_app>")
        return

    with DATA_PATH.open(encoding="utf-8") as f:
        data = json.load(f)

    if isinstance(data, dict):
        entries = {w: data[w] for w in WORDS if w in data}
        found = list(entries.keys())
        result = entries
    else:
        entries = [e for e in data if e.get("id") in WORDS or e.get("simplified") in WORDS]
        found = [e.get("id") or e.get("simplified") for e in entries]
        result = entries

    with OUTPUT_PATH.open("w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    missing = [w for w in WORDS if w not in found]
    print(f"Ditemukan {len(found)} dari {len(WORDS)} kata.")
    if missing:
        print(f"Tidak ditemukan: {', '.join(missing)}")
    print(f"Tersimpan di: {OUTPUT_PATH.resolve()}")
    print("\nSekarang upload file ini ke chat.")


if __name__ == "__main__":
    main()

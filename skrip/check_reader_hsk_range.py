"""
check_reader_hsk_range.py
---------------------------
Cek rentang level HSK yang tercakup di graded_readers.json, plus breakdown
per level dan per tipe (bacaan vs percakapan). READ-ONLY.
"""

import json
from pathlib import Path
from collections import Counter

GRADED_READERS = Path("data") / "graded_readers.json"


def flatten_readers(data):
    results = []
    if isinstance(data, dict):
        if "glossary" in data:
            results.append(data)
        else:
            for v in data.values():
                results.extend(flatten_readers(v))
    elif isinstance(data, list):
        for item in data:
            results.extend(flatten_readers(item))
    return results


def main():
    if not GRADED_READERS.exists():
        print(f"[!] File tidak ditemukan: {GRADED_READERS}")
        return

    with open(GRADED_READERS, "r", encoding="utf-8") as f:
        data = json.load(f)

    readers = flatten_readers(data)
    print(f"[info] Total entri graded reader: {len(readers)}\n")

    hsk_counter = Counter()
    type_counter = Counter()
    hsk_by_type = Counter()

    for r in readers:
        hsk = r.get("hsk") or r.get("level") or r.get("hsk_level") or "?"
        tipe = r.get("type") or r.get("jenis") or "?"
        hsk_counter[str(hsk)] += 1
        type_counter[str(tipe)] += 1
        hsk_by_type[(str(tipe), str(hsk))] += 1

    print("=== Breakdown per level HSK ===")
    for hsk, count in sorted(hsk_counter.items()):
        print(f"  HSK {hsk}: {count} entri")

    print("\n=== Breakdown per tipe konten ===")
    for tipe, count in sorted(type_counter.items()):
        print(f"  {tipe}: {count} entri")

    print("\n=== Breakdown tipe x level ===")
    for (tipe, hsk), count in sorted(hsk_by_type.items()):
        print(f"  {tipe} / HSK {hsk}: {count} entri")

    numeric_levels = [int(h) for h in hsk_counter if h.isdigit()]
    if numeric_levels:
        print(f"\n=== KESIMPULAN: rentang level = HSK {min(numeric_levels)}–{max(numeric_levels)} ===")
    else:
        print("\n[!] Tidak ada field level numerik terdeteksi -- field mungkin bernama beda.")
        print("    Kirim 1 contoh entri lengkap (bukan glossary-nya, tapi objek reader-nya sendiri)")
        print("    supaya saya bisa sesuaikan nama field yang dicari.")


if __name__ == "__main__":
    main()

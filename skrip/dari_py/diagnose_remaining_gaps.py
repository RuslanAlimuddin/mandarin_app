# -*- coding: utf-8 -*-
"""
diagnose_remaining_gaps.py
────────────────────────────
Diagnosis SISA entri yang masih "_missing_fields" setelah Tahap 2.
Untuk tiap kategori, tampilkan:
  1. Rekap: field apa yang paling sering hilang (radical/radical_number/
     stroke_count/bopomofo)
  2. SEMUA entri yang bermasalah, lengkap dengan simplified+pinyin+field
     yang hilang -- supaya pola kegagalan bopomofo (kalau ada) ketahuan
     persis dari bentuk pinyin-nya.

TIDAK mengubah apa pun. Baca saja dari staging/*_enriched.json.

CARA PAKAI:
    cd C:\\mandarin_app
    python diagnose_remaining_gaps.py
"""

import json
from pathlib import Path
from collections import Counter

STAGING_DIR = Path("staging")
CATEGORY_FILES = ["kata_seru", "onomatope", "sapaan_keluarga", "sapaan_sosial", "partikel_modal"]


def out(lines, s=""):
    print(s)
    lines.append(s)


def main():
    lines = []
    out(lines, "DIAGNOSIS SISA GAP — TAHAP 2")
    out(lines, "=" * 70)

    field_counter_total = Counter()

    for cat in CATEGORY_FILES:
        path = STAGING_DIR / f"{cat}_enriched.json"
        out(lines, f"\n{'─'*70}")
        out(lines, f"[{cat}]")
        if not path.exists():
            out(lines, f"  ⚠ {path} tidak ditemukan, dilewati.")
            continue

        with open(path, "r", encoding="utf-8") as f:
            entries = json.load(f)

        problem_entries = [e for e in entries if "_missing_fields" in e]
        out(lines, f"  Total bermasalah: {len(problem_entries)}")

        field_counter = Counter()
        for e in problem_entries:
            for f in e["_missing_fields"]:
                field_counter[f] += 1
                field_counter_total[f] += 1

        out(lines, f"  Rekap field yang hilang: {dict(field_counter)}")

        if problem_entries:
            out(lines, f"\n  Daftar lengkap:")
            for e in problem_entries:
                simp = e.get("simplified", "")
                pinyin = e.get("pinyin", "")
                missing = e.get("_missing_fields", [])
                out(lines, f"    {simp:<8} pinyin={pinyin!r:<20} hilang={missing}")

    out(lines, f"\n{'=' * 70}")
    out(lines, f"REKAP TOTAL SEMUA KATEGORI")
    out(lines, f"  {dict(field_counter_total)}")

    Path("diagnose_remaining_gaps_report.txt").write_text("\n".join(lines), encoding="utf-8")
    print(f"\n✓ Laporan disimpan ke diagnose_remaining_gaps_report.txt")


if __name__ == "__main__":
    main()

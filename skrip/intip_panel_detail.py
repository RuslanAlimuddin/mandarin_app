"""
intip_panel_detail.py — READ-ONLY, tidak mengubah file apapun.

Tujuan: cari di mana struktur HTML panel detail kamus didefinisikan
(elemen dengan id seperti d-hanzi, d-pinyin, d-meanings-id, detail-content,
dst -- yang dipakai oleh renderDetail() di kamus-detail.js lewat $('...')),
supaya kita tahu file mana yang perlu disentuh untuk menambah blok
"Contoh Kalimat" (E.0.1).

Cara pakai:
    cd C:\\mandarin_app
    python intip_panel_detail.py

Aman dijalankan berkali-kali, tidak menulis/menghapus apapun.
"""

import os
import re

ROOT = os.getcwd()  # jalankan dari C:\mandarin_app

# ID elemen yang dipakai renderDetail() via $('...') -- lihat kamus-detail.js
TARGET_IDS = [
    "detail-empty-state", "detail-content", "detail-actions",
    "d-hanzi", "d-traditional", "d-pinyin", "d-bopomofo", "d-pos",
    "d-meanings-id", "d-meanings-en",
    "d-section-mnemonic", "d-section-components", "d-components",
    "d-section-theme", "d-section-synonym", "d-section-antonym",
    "detail-meaning-item", "detail-meaning-num", "detail-pos-tag",
    "rel-word-chip",
]

# Field data yang belum pernah dirender (E.0.1) -- kalau kebetulan sudah
# disebut di HTML/JS manapun, itu petunjuk penting juga.
TARGET_FIELDS = [
    "contoh_kalimat_cn", "contoh_kalimat_pinyin", "contoh_kalimat_id",
]

EXTS = (".html", ".css", ".js")
SKIP_DIRS = {".git", "node_modules", "__pycache__"}

def scan():
    hits = {}  # keyword -> list of (filepath, lineno, line_text)
    for keyword in TARGET_IDS + TARGET_FIELDS:
        hits[keyword] = []

    for dirpath, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for fname in filenames:
            if not fname.lower().endswith(EXTS):
                continue
            fpath = os.path.join(dirpath, fname)
            try:
                with open(fpath, "r", encoding="utf-8", errors="ignore") as f:
                    lines = f.readlines()
            except Exception as e:
                print(f"[SKIP] {fpath}: {e}")
                continue
            for lineno, line in enumerate(lines, start=1):
                for keyword in TARGET_IDS + TARGET_FIELDS:
                    if keyword in line:
                        rel = os.path.relpath(fpath, ROOT)
                        hits[keyword].append((rel, lineno, line.strip()))

    return hits


def main():
    hits = scan()

    print("=" * 70)
    print("HASIL INTIP -- lokasi elemen panel detail kamus")
    print("=" * 70)

    found_files = set()
    for keyword in TARGET_IDS:
        occ = hits[keyword]
        if not occ:
            print(f"\n[!] '{keyword}' -- TIDAK DITEMUKAN di file manapun (.html/.css/.js)")
            continue
        print(f"\n[{keyword}]  ({len(occ)} kemunculan)")
        for rel, lineno, text in occ[:5]:  # cukup 5 contoh pertama per keyword
            found_files.add(rel)
            print(f"  {rel}:{lineno}  |  {text[:120]}")
        if len(occ) > 5:
            print(f"  ... +{len(occ) - 5} lainnya")

    print("\n" + "=" * 70)
    print("Field 'contoh_kalimat_*' (E.0.1) -- sudah disebut di kode?")
    print("=" * 70)
    any_field_hit = False
    for keyword in TARGET_FIELDS:
        occ = hits[keyword]
        if occ:
            any_field_hit = True
            print(f"\n[{keyword}]  ({len(occ)} kemunculan)")
            for rel, lineno, text in occ:
                print(f"  {rel}:{lineno}  |  {text[:120]}")
    if not any_field_hit:
        print("\n(tidak ditemukan sama sekali -- konsisten dgn BLUEPRINT: field")
        print(" ada di data tapi belum pernah dirender di kode manapun)")

    print("\n" + "=" * 70)
    print(f"RINGKASAN: file yang menyebut elemen panel detail ({len(found_files)}):")
    print("=" * 70)
    for f in sorted(found_files):
        print(f"  - {f}")


if __name__ == "__main__":
    main()

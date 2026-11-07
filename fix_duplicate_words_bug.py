#!/usr/bin/env python3
"""
fix_duplicate_words_bug.py — Mandarin Interaktif: perbaiki bug 'words' duplikat
=============================================================================
Menangani 5 pasangan yang field "words"-nya salah ketik (kata pertama
ke-duplikat, mis. ["对面","对面"]) -- bug lama dari data sumber, ditemukan
lewat audit_quality.py.

Cara pakai (dari folder C:\\mandarin_app\\):
    python fix_duplicate_words_bug.py
    python fix_duplicate_words_bug.py --dry-run

Untuk tiap pasangan yang words-nya duplikat:
  - Kalau comparison-nya punya 2+ kata BERBEDA (datanya sebenarnya lengkap,
    cuma field "words" yang typo) -> "words" diperbaiki mengikuti comparison.
  - Kalau comparison cuma punya 1 kata unik (datanya memang rusak, tidak ada
    info kata kedua sama sekali) -> pasangan itu DIHAPUS dari nuance_pairs.json.
"""
import json
import sys
import argparse
from pathlib import Path


def load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--nuance", default="data/nuance_pairs.json")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    nuance_path = Path(args.nuance)
    if not nuance_path.exists():
        print(f"[GAGAL] {nuance_path} tidak ditemukan.")
        sys.exit(1)

    data = load_json(nuance_path)
    pairs = data.get("pairs", [])

    fixed = []
    removed = []
    kept = []

    for p in pairs:
        words = p.get("words", [])
        if len(words) == len(set(words)):
            kept.append(p)
            continue

        comp_words = []
        for c in p.get("comparison", []):
            w = c.get("word")
            if w and w not in comp_words:
                comp_words.append(w)

        if len(comp_words) >= 2:
            old_words = p["words"]
            p["words"] = comp_words
            fixed.append((p.get("id"), old_words, comp_words))
            kept.append(p)
        else:
            removed.append((p.get("id"), words))

    print(f"Total pasangan semula: {len(pairs)}")
    print(f"\nDIPERBAIKI ({len(fixed)}):")
    for pid, old, new in fixed:
        print(f"  [{pid}] {old} -> {new}")

    print(f"\nDIHAPUS -- data rusak permanen, cuma 1 kata yang ada infonya ({len(removed)}):")
    for pid, words in removed:
        print(f"  [{pid}] {words}")

    print(f"\nTotal pasangan setelah perbaikan: {len(kept)}")

    if args.dry_run:
        print("\n[DRY RUN] Tidak disimpan.")
        return

    data["pairs"] = kept
    save_json(nuance_path, data)
    print(f"\n[OK] Tersimpan ke {nuance_path}.")


if __name__ == "__main__":
    main()

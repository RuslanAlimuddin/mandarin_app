#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
cek_karakter.py — Mandarin Interaktif
Diagnostik READ-ONLY: bongkar SEMUA representasi sebuah karakter/kata di
app_words.json & cidict_index.json, termasuk cek perbedaan unicode
tersembunyi (NFC/NFD/whitespace) yg bisa bikin duplikat "tidak terdeteksi"
oleh pembandingan string biasa.

CARA PAKAI:
  python cek_karakter.py 土
  python cek_karakter.py 土 吃 打        <- bisa banyak karakter sekaligus
  python cek_karakter.py                <- default cek 土 kalau tanpa argumen
"""
import json
import os
import sys
import unicodedata

DATA_DIR = "data"


def load_json_safe(path):
    if not os.path.exists(path):
        return None
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"(gagal parse {path}: {e})")
        return None


def codepoint_dump(s):
    """Tampilkan tiap karakter dlm string sbg codepoint + nama unicode --
    supaya kelihatan kalau ada karakter 'kembar' yg sebenarnya beda
    (mis. varian compatibility, atau whitespace nyempil)."""
    parts = []
    for ch in s:
        try:
            name = unicodedata.name(ch)
        except ValueError:
            name = "?"
        parts.append(f"U+{ord(ch):04X}({name})")
    return " ".join(parts)


def dump_matches(data, label, target, field_names=("simplified", "traditional", "id")):
    if data is None:
        print(f"   [{label}] (file tidak dimuat, dilewati)")
        return

    target_nfc = unicodedata.normalize("NFC", target)
    target_nfd = unicodedata.normalize("NFD", target)

    exact_matches = []
    normalized_only_matches = []  # match SETELAH normalisasi, tapi TIDAK match sebelum -- ini yg "hilang" dari deteksi biasa
    for idx, w in enumerate(data):
        raw_vals = {fn: w.get(fn) for fn in field_names if w.get(fn) is not None}
        hit_raw = any(v == target for v in raw_vals.values())
        hit_norm = any(
            unicodedata.normalize("NFC", str(v)) == target_nfc or
            unicodedata.normalize("NFD", str(v)) == target_nfd
            for v in raw_vals.values()
        )
        if hit_raw:
            exact_matches.append((idx, w))
        elif hit_norm:
            normalized_only_matches.append((idx, w))

    print(f"\n   [{label}] exact-string match: {len(exact_matches)} entri")
    for idx, w in exact_matches:
        simp = w.get("simplified", "")
        print(f"      #{idx}  id={w.get('id')!r}  simplified={simp!r}")
        print(f"           codepoints simplified: {codepoint_dump(simp)}")
        print(f"           pinyin={w.get('pinyin')!r}")
        print(f"           meanings_id={w.get('meanings_id')}")
        print(f"           pos_id={w.get('pos_id')}")

    if normalized_only_matches:
        print(f"\n   ⚠️  [{label}] Ditemukan {len(normalized_only_matches)} entri yg BARU match "
              f"SETELAH normalisasi unicode (artinya representasi string aslinya BEDA "
              f"walau kelihatan sama di layar!):")
        for idx, w in normalized_only_matches:
            simp = w.get("simplified", "")
            print(f"      #{idx}  id={w.get('id')!r}  simplified={simp!r}")
            print(f"           codepoints simplified: {codepoint_dump(simp)}")
            print(f"           pinyin={w.get('pinyin')!r}")
            print(f"           meanings_id={w.get('meanings_id')}")


def main():
    targets = sys.argv[1:] or ["土"]

    app_words = load_json_safe(os.path.join(DATA_DIR, "app_words.json"))
    cidict = load_json_safe(os.path.join(DATA_DIR, "cidict_index.json"))

    for target in targets:
        print(f"\n{'='*70}\nKARAKTER/KATA: {target}   "
              f"(codepoints query: {codepoint_dump(target)})\n{'='*70}")
        dump_matches(app_words, "app_words.json", target)
        dump_matches(cidict, "cidict_index.json", target)


if __name__ == "__main__":
    main()

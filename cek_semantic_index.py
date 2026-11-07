#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
cek_semantic_index.py — Mandarin Interaktif
Diagnostik READ-ONLY (harusnya benar-benar TERAKHIR): cek seberapa
lengkap data/cidict_semantic_index.json -- apakah field `context` &
`examples` per makna SUDAH terisi (utk semua/sebagian entri), atau
semuanya masih kosong ("unknown"/[]).

Fokus khusus ke kata-kata polisemi umum yg sudah kita bahas (吃/了/着/
那/从/里/为/个/是/土/打/上/下) -- ini yg menentukan apakah Tier 3 bisa
"lanjutkan yg sudah ada" atau harus "mulai dari nol".

TIDAK mengubah file apa pun.

CARA PAKAI:
  python cek_semantic_index.py
  -> upload semantic_index_report.json yg dihasilkan
"""
import json
import os
import random

random.seed(42)
DATA_DIR = "data"
OUT_PATH = "semantic_index_report.json"
FOCUS_WORDS = ["吃", "了", "着", "那", "从", "里", "为", "个", "是",
               "土", "打", "上", "下", "错", "麻", "保"]


def main():
    path = os.path.join(DATA_DIR, "cidict_semantic_index.json")
    if not os.path.exists(path):
        print(f"[GAGAL] tidak ditemukan: {path}")
        return
    with open(path, encoding="utf-8") as f:
        data = json.load(f)

    total_entries = len(data)
    total_meanings = 0
    filled_context = 0     # context != "unknown" dan tidak kosong
    filled_examples = 0    # examples list tidak kosong
    unknown_context = 0
    empty_examples = 0

    for char, entry in data.items():
        meanings = entry.get("meanings", [])
        for m in meanings:
            total_meanings += 1
            ctx = m.get("context")
            ex = m.get("examples")
            if ctx and ctx != "unknown":
                filled_context += 1
            else:
                unknown_context += 1
            if ex and len(ex) > 0:
                filled_examples += 1
            else:
                empty_examples += 1

    print(f"{'='*70}\nRINGKASAN KELENGKAPAN cidict_semantic_index.json\n{'='*70}")
    print(f"Total kata/entri     : {total_entries:,}")
    print(f"Total makna (meanings): {total_meanings:,}")
    print(f"\ncontext terisi (bukan 'unknown')  : {filled_context:,} ({filled_context/total_meanings*100:.2f}%)")
    print(f"context masih 'unknown'/kosong    : {unknown_context:,} ({unknown_context/total_meanings*100:.2f}%)")
    print(f"\nexamples terisi (>=1 contoh)      : {filled_examples:,} ({filled_examples/total_meanings*100:.2f}%)")
    print(f"examples masih kosong []          : {empty_examples:,} ({empty_examples/total_meanings*100:.2f}%)")

    print(f"\n{'='*70}\nCEK KHUSUS KATA POLISEMI UMUM (fokus rencana Tier 3)\n{'='*70}")
    focus_results = {}
    for w in FOCUS_WORDS:
        entry = data.get(w)
        print(f"\n--- {w} ---")
        if not entry:
            print("   (tidak ada di cidict_semantic_index.json)")
            focus_results[w] = None
            continue
        print(json.dumps(entry, ensure_ascii=False, indent=3))
        focus_results[w] = entry

    # Sampel acak TAMBAHAN (bukan cuma alfabetis awal) utk cek representatif
    print(f"\n{'='*70}\nSampel ACAK 10 entri (cek independen dari kata fokus di atas)\n{'='*70}")
    random_keys = random.sample(list(data.keys()), min(10, len(data)))
    random_sample = {}
    for k in random_keys:
        print(f"\n--- {k} ---")
        print(json.dumps(data[k], ensure_ascii=False, indent=3)[:500])
        random_sample[k] = data[k]

    report = {
        "total_entries": total_entries,
        "total_meanings": total_meanings,
        "filled_context": filled_context,
        "unknown_context": unknown_context,
        "filled_examples": filled_examples,
        "empty_examples": empty_examples,
        "focus_words_detail": focus_results,
        "random_sample": random_sample,
    }
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    print(f"\n{'='*70}\nSelesai. Disimpan ke: {OUT_PATH}")
    print("Upload file itu ke sesi Claude berikutnya utk finalisasi rencana Tier 3.")
    print(f"{'='*70}")


if __name__ == "__main__":
    main()

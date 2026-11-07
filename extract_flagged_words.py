# -*- coding: utf-8 -*-
"""
extract_flagged_words.py — SEKALI PAKAI, verifikasi temuan audit_polysemy_batch.py
Tidak mengubah data apa pun. Jalankan dari C:\\mandarin_app:

    python extract_flagged_words.py

Menulis: flagged_words_detail.json
Isinya: entri LENGKAP dari app_words.json (kalau ada) dan SEMUA kandidat
cidict_index.json, untuk kata-kata yang ditandai audit_polysemy_batch.py,
supaya bisa dipastikan manual apakah field pinyin-nya memang salah.
"""
import json
from pathlib import Path
from collections import defaultdict

DATA_DIR = Path("data")

WORDS_TO_CHECK = ['别', '那', '过', '与', '化', '强', '号']


def load(path):
    with open(path, encoding='utf-8') as f:
        return json.load(f)


app_words = load(DATA_DIR / "app_words.json")
cidict = load(DATA_DIR / "cidict_index.json")

grouped_cidict = defaultdict(list)
for w in cidict:
    s = w.get('simplified')
    if s:
        grouped_cidict[s].append(w)

app_words_by_simplified = {}
for w in app_words:
    s = w.get('simplified')
    if s:
        app_words_by_simplified[s] = w

out = {}
for word in WORDS_TO_CHECK:
    out[word] = {
        'app_words_entry': app_words_by_simplified.get(word, 'TIDAK ADA di app_words.json'),
        'cidict_candidates': grouped_cidict.get(word, []),
    }

with open("flagged_words_detail.json", "w", encoding='utf-8') as f:
    json.dump(out, f, ensure_ascii=False, indent=1)

print("Selesai. File 'flagged_words_detail.json' dibuat di folder ini.")

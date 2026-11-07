# -*- coding: utf-8 -*-
"""
sample_dict_structure.py — SEKALI PAKAI, hanya untuk intip struktur data.
Tidak mengubah file apa pun. Jalankan dari C:\\mandarin_app:

    python sample_dict_structure.py

Akan menulis 1 file: dict_structure_sample.json
Isinya: beberapa entri contoh dari cidict_index.json (termasuk yang
multi-pinyin) dan app_words.json, buat Claude pastikan skema fieldnya
sebelum bikin audit_polysemy_batch.py.
"""
import json
import random
from pathlib import Path
from collections import defaultdict

DATA_DIR = Path("data")

def load(path):
    with open(path, encoding='utf-8') as f:
        return json.load(f)

out = {}

# ── cidict_index.json ──
cidict = load(DATA_DIR / "cidict_index.json")
out['cidict_total_entries'] = len(cidict)
out['cidict_first_3_raw'] = cidict[:3]

grouped = defaultdict(list)
for w in cidict:
    s = w.get('simplified')
    if s:
        grouped[s].append(w)

multi_pinyin = {}
for s, entries in grouped.items():
    pys = set((e.get('pinyin') or '').strip() for e in entries)
    if len(pys) > 1:
        multi_pinyin[s] = entries

out['cidict_total_hanzi_with_multiple_pinyin_variants'] = len(multi_pinyin)

sample_keys = random.sample(list(multi_pinyin.keys()), min(15, len(multi_pinyin)))
out['cidict_multi_pinyin_samples'] = {k: multi_pinyin[k] for k in sample_keys}

# beberapa yang sudah ada di COMMON_READING_OVERRIDE, untuk pembanding
known = ['都', '和', '要', '得', '中', '着']
out['cidict_known_override_examples'] = {k: grouped.get(k, 'TIDAK DITEMUKAN') for k in known}

# ── app_words.json ──
app_words = load(DATA_DIR / "app_words.json")
out['app_words_total_entries'] = len(app_words)
out['app_words_first_3_raw'] = app_words[:3]
out['app_words_random_5_raw'] = random.sample(app_words, min(5, len(app_words)))

# cek apakah field 'themes' ada, dan field lain2 apa saja muncul
all_keys = set()
for w in app_words[:200]:
    all_keys.update(w.keys())
out['app_words_observed_field_names_sample200'] = sorted(all_keys)

with open("dict_structure_sample.json", "w", encoding='utf-8') as f:
    json.dump(out, f, ensure_ascii=False, indent=1)

print("Selesai. File 'dict_structure_sample.json' dibuat di folder ini.")
print(f"Total cidict: {len(cidict)} entri, {len(multi_pinyin)} hanzi punya >1 varian pinyin.")
print(f"Total app_words: {len(app_words)} entri.")

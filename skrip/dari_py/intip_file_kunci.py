#!/usr/bin/env python3
# intip_file_kunci.py
# Jalankan: python intip_file_kunci.py
# Output  : C:\mandarin_app\data\LAPORAN_INTIP.txt

import json, os

KAMUS_DIR = r"C:\mandarin_kamus"
OUTPUT    = r"C:\mandarin_app\data\LAPORAN_INTIP.txt"

lines = []
def log(s=""):
    print(s)
    lines.append(str(s))

def separator(title):
    log("\n" + "═"*60)
    log(f"  {title}")
    log("═"*60)

def load_json(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f), None
    except Exception as e:
        return None, str(e)

def intip(rel_path, n_samples=3, n_keys=5):
    full = os.path.join(KAMUS_DIR, rel_path)
    separator(rel_path)
    d, err = load_json(full)
    if err:
        log(f"  ✗ ERROR: {err}")
        return

    if isinstance(d, list):
        log(f"  Tipe : list × {len(d):,} item")
        for i, item in enumerate(d[:n_samples]):
            log(f"\n  Item[{i}]:")
            if isinstance(item, dict):
                for k, v in item.items():
                    log(f"    {k:<30} : {str(v)[:100]}")
            else:
                log(f"    {str(item)[:150]}")

    elif isinstance(d, dict):
        keys = list(d.keys())
        log(f"  Tipe : dict × {len(d):,} keys")
        log(f"  Contoh keys: {keys[:10]}")
        for k in keys[:n_keys]:
            v = d[k]
            log(f"\n  Key '{k}':")
            if isinstance(v, dict):
                for kk, vv in v.items():
                    log(f"    {kk:<30} : {str(vv)[:100]}")
            elif isinstance(v, list):
                log(f"    list × {len(v)} → {str(v[:3])[:150]}")
            else:
                log(f"    {str(v)[:150]}")

# ── File yang perlu diintip ──────────────────────────────────

intip(r"database\semantic_hanzi_v3_id.json",  n_samples=2, n_keys=3)
intip(r"output\synonym_antonym.json",          n_samples=3, n_keys=5)
intip(r"database\cidict_semantic_index.json",  n_samples=2, n_keys=3)
intip(r"database\cidict_index.json",           n_samples=2, n_keys=3)
intip(r"output\cidict_full.json",              n_samples=2, n_keys=3)
intip(r"indexes\index_radical.json",           n_samples=2, n_keys=3)
intip(r"indexes\index_pinyin.json",            n_samples=2, n_keys=3)
intip(r"indexes\index_stroke.json",            n_samples=2, n_keys=3)
intip(r"database\master_hanzi_v2.json",        n_samples=2, n_keys=3)

# ── Cek apakah cidict_full punya field lengkap ───────────────
separator("CEK FIELD cidict_full.json vs cidict_index.json (data/)")

for rel in [r"output\cidict_full.json", r"database\cidict_index.json"]:
    full = os.path.join(KAMUS_DIR, rel)
    d, err = load_json(full)
    if err:
        log(f"  {rel}: ERROR {err}")
        continue
    if isinstance(d, list) and d:
        sample = d[0]
        log(f"\n  [{rel}] — list × {len(d):,}")
        if isinstance(sample, dict):
            log(f"  Fields: {list(sample.keys())}")
    elif isinstance(d, dict):
        keys = list(d.keys())
        log(f"\n  [{rel}] — dict × {len(d):,}")
        first_val = d[keys[0]]
        if isinstance(first_val, dict):
            log(f"  Fields dalam value: {list(first_val.keys())}")
        else:
            log(f"  Value sample: {str(first_val)[:100]}")

# Simpan
os.makedirs(os.path.dirname(OUTPUT), exist_ok=True)
with open(OUTPUT, "w", encoding="utf-8") as f:
    f.write("\n".join(lines))

print(f"\n✅ Selesai! Buka: {OUTPUT}")

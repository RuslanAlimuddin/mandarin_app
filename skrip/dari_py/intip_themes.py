#!/usr/bin/env python3
# intip_themes.py
# Jalankan: python intip_themes.py
# Output  : C:\mandarin_app\data\LAPORAN_THEMES.txt

import json, os

KAMUS_DIR  = r"C:\mandarin_kamus"
OUT_REPORT = r"C:\mandarin_app\data\LAPORAN_THEMES.txt"

lines = []
def log(s=""):
    print(s)
    lines.append(str(s))

def sep(title=""):
    log("\n" + "═"*60)
    log(f"  {title}")
    log("═"*60)

def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

# ── 1. Intip output\themes.json ──────────────────────────────
sep("output\\themes.json — struktur")
path = os.path.join(KAMUS_DIR, "output", "themes.json")
d = load_json(path)
log(f"  Tipe root : {type(d).__name__}")

if isinstance(d, dict):
    keys = list(d.keys())
    log(f"  Jumlah keys : {len(keys)}")
    log(f"  Contoh keys (20): {keys[:20]}")
    log()
    # Intip 3 key pertama
    for k in keys[:3]:
        v = d[k]
        log(f"  Key '{k}':")
        if isinstance(v, dict):
            for kk, vv in v.items():
                log(f"    {kk:<25} : {str(vv)[:120]}")
        elif isinstance(v, list):
            log(f"    list × {len(v)}")
            for item in v[:3]:
                log(f"    {str(item)[:120]}")
        else:
            log(f"    {str(v)[:120]}")
        log()

elif isinstance(d, list):
    log(f"  Jumlah item : {len(d)}")
    for item in d[:3]:
        log(f"\n  Item:")
        if isinstance(item, dict):
            for k, v in item.items():
                log(f"    {k:<25} : {str(v)[:120]}")
        else:
            log(f"  {str(item)[:120]}")

# ── 2. Intip database\flashcard_deck_engine.json (186 MB) ────
# Hanya baca sebagian kecil saja agar cepat
sep("database\\flashcard_deck_engine.json — 10 baris pertama saja")
path2 = os.path.join(KAMUS_DIR, "database", "flashcard_deck_engine.json")
try:
    with open(path2, "r", encoding="utf-8") as f:
        # Baca hanya 2000 karakter pertama
        head = f.read(3000)
    log(f"  2000 karakter pertama:")
    log(head)
except Exception as e:
    log(f"  ERROR: {e}")

# ── 3. Intip database\learning_experience_index.json (125 MB) ─
sep("database\\learning_experience_index.json — 3000 karakter pertama")
path3 = os.path.join(KAMUS_DIR, "database", "learning_experience_index.json")
try:
    with open(path3, "r", encoding="utf-8") as f:
        head = f.read(3000)
    log(head)
except Exception as e:
    log(f"  ERROR: {e}")

# Simpan
with open(OUT_REPORT, "w", encoding="utf-8") as f:
    f.write("\n".join(lines))
print(f"\n✅ Selesai! Buka: {OUT_REPORT}")

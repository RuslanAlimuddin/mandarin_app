"""
peek_ext_themes.py
Jalankan: python peek_ext_themes.py
Tujuan  : tampilkan struktur lengkap beberapa tema ext_ untuk tahu
          field apa saja yang tersedia (khususnya apakah ada label_zh).
"""

import json, pathlib

THEME_FILE = pathlib.Path(r"C:\mandarin_app\data\index_theme.json")

with open(THEME_FILE, encoding="utf-8") as f:
    data = json.load(f)

ext_keys = [k for k in data if k.startswith("ext_")]
print(f"Total tema ext_: {len(ext_keys)}")
print("=" * 70)

# Tampilkan 5 entry ext_ — tanpa field 'words' agar tidak banjir teks
print("5 ENTRY ext_ (tanpa field 'words'):\n")
for k in ext_keys[:5]:
    v = data[k]
    ringkas = {fk: fv for fk, fv in v.items() if fk != "words"}
    print(f"Key: '{k}'")
    print(json.dumps(ringkas, ensure_ascii=False, indent=4))
    print()

# Hitung berapa ext_ yang punya label_zh
punya_zh = sum(1 for k in ext_keys if data[k].get("label_zh"))
print(f"ext_ yang punya label_zh : {punya_zh} / {len(ext_keys)}")

# Semua label_en yang ada (untuk referensi manual jika perlu)
print("\n" + "=" * 70)
print("DAFTAR SEMUA TEMA ext_ (key → label_en → label_zh jika ada):")
print("-" * 70)
for k in ext_keys:
    v     = data[k]
    len_  = v.get("label_en", "")
    lzh   = v.get("label_zh", "—")
    count = v.get("count", len(v.get("words", [])))
    print(f"  {k:<45} | {len_:<35} | {lzh} ({count})")

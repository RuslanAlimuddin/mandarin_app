"""
generate_phonetic_index.py
Jalankan: python generate_phonetic_index.py
Output  : C:\mandarin_app\data\index_phonetic.json

Membaca field `components` dari app_words.json (array karakter),
lalu membangun index terbalik:
  { "komponen": ["word_id_1", "word_id_2", ...], ... }

Hanya komponen yang muncul pada ≥2 kata yang dimasukkan
(komponen tunggal / unik tidak berguna sebagai filter deck).
"""

import json, pathlib, collections

SRC  = pathlib.Path(r"C:\mandarin_app\data\app_words.json")
DEST = pathlib.Path(r"C:\mandarin_app\data\index_phonetic.json")
MIN_WORDS = 2          # komponen harus muncul di ≥ N kata

# ── Load ───────────────────────────────────────────────────────
with open(SRC, encoding="utf-8") as f:
    words = json.load(f)

if isinstance(words, dict):
    words = list(words.values())

print(f"Memuat {len(words):,} kata dari {SRC.name}")

# ── Bangun index terbalik ──────────────────────────────────────
index = collections.defaultdict(list)

for w in words:
    word_id    = w.get("id") or w.get("simplified", "")
    components = w.get("components", [])

    if not isinstance(components, list):
        continue

    for comp in components:
        if comp and isinstance(comp, str):
            index[comp].append(word_id)

# ── Filter: hanya komponen yang ada di ≥ MIN_WORDS kata ────────
filtered = {
    comp: ids
    for comp, ids in index.items()
    if len(ids) >= MIN_WORDS
}

# ── Urutkan: komponen dengan kata terbanyak duluan ─────────────
sorted_index = dict(
    sorted(filtered.items(), key=lambda x: -len(x[1]))
)

# ── Simpan ─────────────────────────────────────────────────────
with open(DEST, "w", encoding="utf-8") as f:
    json.dump(sorted_index, f, ensure_ascii=False, indent=2)

# ── Laporan ────────────────────────────────────────────────────
print(f"\nHasil:")
print(f"  Total komponen unik (sebelum filter) : {len(index):,}")
print(f"  Komponen dimasukkan (≥{MIN_WORDS} kata)       : {len(sorted_index):,}")
print(f"\n10 komponen terbanyak:")
for comp, ids in list(sorted_index.items())[:10]:
    print(f"  '{comp}'  →  {len(ids):,} kata")

print(f"\n✓ Disimpan ke: {DEST}")

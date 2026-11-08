"""
peek_words.py
Jalankan: python peek_words.py
Tujuan  : tampilkan field-field yang kemungkinan berisi info komponen/fonetik
          dari app_words.json, beserta 3 contoh nilainya.
"""

import json, pathlib, collections

DATA_FILE = r"C:\mandarin_app\data\app_words.json"

with open(DATA_FILE, encoding="utf-8") as f:
    words = json.load(f)

# Normalkan: bisa list langsung atau dict {id: {...}}
if isinstance(words, dict):
    words = list(words.values())

print(f"Total kata: {len(words)}\n")
print("=" * 60)

# Kumpulkan semua field yang ada di seluruh data
field_counter = collections.Counter()
for w in words:
    for k in w.keys():
        field_counter[k] += 1

print("SEMUA FIELD (nama : jumlah kata yang punya field itu):")
print("-" * 60)
for field, count in sorted(field_counter.items(), key=lambda x: -x[1]):
    print(f"  {field:<30} {count:>7,}")

# Kata kunci yang mungkin terkait fonetik/komponen
KANDIDAT = [
    "components", "component", "phonetic", "phonetic_component",
    "radicals", "radical", "parts", "decomposition",
    "semantic", "structure", "strokes", "char_components",
]

print("\n" + "=" * 60)
print("FIELD KANDIDAT FONETIK — 3 contoh nilai:")
print("-" * 60)

found_any = False
for key in KANDIDAT:
    samples = [w[key] for w in words if key in w and w[key]][:3]
    if samples:
        found_any = True
        print(f"\n  Field: '{key}'")
        for i, s in enumerate(samples, 1):
            print(f"    Contoh {i}: {json.dumps(s, ensure_ascii=False)}")

if not found_any:
    print("\n  Tidak ada field kandidat standar ditemukan.")
    print("  Coba lihat daftar semua field di atas dan cari yang relevan.\n")
    # Tampilkan 1 entry lengkap sebagai referensi
    print("  Contoh 1 entry lengkap (kata pertama yang punya banyak field):")
    richest = max(words, key=lambda w: len(w))
    print(json.dumps(richest, ensure_ascii=False, indent=4))

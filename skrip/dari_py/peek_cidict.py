"""
peek_cidict.py
Jalankan: python peek_cidict.py
Tujuan  : tampilkan struktur cidict_index.json untuk tahu
          field mana yang bisa dipakai sebagai terjemahan label tema.
"""

import json, pathlib

DATA_FILE = r"C:\mandarin_app\data\cidict_index.json"

with open(DATA_FILE, encoding="utf-8") as f:
    data = json.load(f)

print(f"Tipe root: {type(data).__name__}")
print("=" * 60)

# Jika root adalah list
if isinstance(data, list):
    print(f"Jumlah entry: {len(data)}")
    print(f"\nContoh entry [0]:")
    print(json.dumps(data[0], ensure_ascii=False, indent=4))
    if len(data) > 1:
        print(f"\nContoh entry [1]:")
        print(json.dumps(data[1], ensure_ascii=False, indent=4))

# Jika root adalah dict
elif isinstance(data, dict):
    keys = list(data.keys())
    print(f"Jumlah key: {len(keys)}")
    print(f"\n5 key pertama: {keys[:5]}")
    print(f"\nContoh entry key '{keys[0]}':")
    val = data[keys[0]]
    print(json.dumps(val, ensure_ascii=False, indent=4))
    print(f"\nContoh entry key '{keys[1]}':")
    val2 = data[keys[1]]
    print(json.dumps(val2, ensure_ascii=False, indent=4))

    # Cek apakah value-nya punya field yang mengandung kata Indonesia
    print("\n" + "=" * 60)
    print("Field-field di dalam value (dari 20 entry pertama):")
    import collections
    fc = collections.Counter()
    for k in keys[:20]:
        v = data[k]
        if isinstance(v, dict):
            for f in v.keys():
                fc[f] += 1
    for f, c in sorted(fc.items(), key=lambda x: -x[1]):
        print(f"  {f:<30} {c:>4}")

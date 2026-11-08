"""
peek_theme.py
Jalankan: python peek_theme.py
Tujuan  : tampilkan struktur index_theme.json agar bisa dirancang
          skrip terjemahan yang tepat.
"""

import json, pathlib

THEME_FILE  = pathlib.Path(r"C:\mandarin_app\data\index_theme.json")

with open(THEME_FILE, encoding="utf-8") as f:
    data = json.load(f)

print(f"Tipe root : {type(data).__name__}")
print(f"Jumlah key: {len(data)}")
print("=" * 70)

keys = list(data.keys())

# Tampilkan 5 entry pertama
print("5 ENTRY PERTAMA (lengkap):")
print("-" * 70)
for k in keys[:5]:
    print(f"\nKey: '{k}'")
    print(json.dumps(data[k], ensure_ascii=False, indent=4))

print("\n" + "=" * 70)

# Cek: berapa yang label_id-nya masih kosong atau sama dengan label_en
kosong   = 0
sama_en  = 0
sudah_id = 0

for k, v in data.items():
    if not isinstance(v, dict):
        continue
    lid = v.get("label_id", "")
    len_ = v.get("label_en", "")
    if not lid:
        kosong += 1
    elif lid.lower() == len_.lower():
        sama_en += 1
    else:
        sudah_id += 1

print(f"STATUS label_id:")
print(f"  Sudah berbahasa Indonesia : {sudah_id}")
print(f"  Sama persis dengan label_en : {sama_en}")
print(f"  Kosong                    : {kosong}")

print("\n" + "=" * 70)
print("5 ENTRY dengan label_id KOSONG atau SAMA DENGAN label_en:")
print("-" * 70)
count = 0
for k, v in data.items():
    if not isinstance(v, dict):
        continue
    lid = v.get("label_id", "")
    len_ = v.get("label_en", "")
    if not lid or lid.lower() == len_.lower():
        print(f"  key='{k}'  label_en='{len_}'  label_id='{lid}'")
        count += 1
        if count >= 5:
            break

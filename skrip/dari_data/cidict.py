import os, json

files = ["cidict_index.json", "cidict_semantic_index.json", "cidict_full.json", "cidict_ts.u8"]

for fname in files:
    path = os.path.join("C:\\mandarin_app\\data", fname)
    if not os.path.isfile(path):
        print(f"=== {fname} === TIDAK DITEMUKAN")
        continue
    size = os.path.getsize(path)
    print(f"=== {fname} ===")
    print(f"Ukuran: {size:,} bytes ({size/1024/1024:.2f} MB)")
    with open(path, encoding="utf-8", errors="replace") as f:
        content = f.read(2000)  # 2000 karakter pertama
        print("--- 2000 karakter pertama ---")
        print(content)
    print()
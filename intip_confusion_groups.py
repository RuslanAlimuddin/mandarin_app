"""
intip_confusion_groups.py — READ-ONLY.

Cek struktur PERSIS confusion_groups.json (53 grup karakter mirip bentuk)
sebelum bangun fitur "Karakter Mirip" (E.0.3) -- jangan tebak skema.

Cara pakai:
    cd C:\\mandarin_app
    python intip_confusion_groups.py
"""

import json
import os

PATH = os.path.join("data", "confusion_groups.json")


def main():
    with open(PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    print(f"Tipe top-level: {type(data).__name__}")
    if isinstance(data, list):
        print(f"Jumlah grup: {len(data)}")
        entries = data
    elif isinstance(data, dict):
        print(f"Jumlah key: {len(data)}")
        print(f"Contoh key: {list(data.keys())[:5]}")
        entries = list(data.values())
    else:
        entries = []

    print("\n=== 3 CONTOH GRUP LENGKAP ===")
    for e in entries[:3]:
        print(json.dumps(e, ensure_ascii=False, indent=2))
        print("---")

    print("\n=== SEMUA FIELD yg muncul di tiap grup ===")
    all_fields = set()
    for e in entries:
        if isinstance(e, dict):
            all_fields.update(e.keys())
    print(sorted(all_fields))

    # cek field karakter -- list of string biasa atau list of object?
    print("\n=== Tipe field 'karakter/chars/characters' (nama field bisa beda) ===")
    for e in entries[:2]:
        if isinstance(e, dict):
            for k, v in e.items():
                print(f"  {k}: {type(v).__name__} = {json.dumps(v, ensure_ascii=False)[:200]}")

    # cek apakah semua karakter di dalam grup ADA di app_words.json
    words_path = os.path.join("data", "app_words.json")
    with open(words_path, "r", encoding="utf-8") as f:
        words = json.load(f)
    words_set = set(w.get("simplified") for w in words)

    print("\n=== Cek semua karakter di confusion_groups.json ADA di app_words.json? ===")
    missing = []
    total_chars = 0
    for e in entries:
        if not isinstance(e, dict):
            continue
        for key, val in e.items():
            if isinstance(val, list):
                for item in val:
                    if isinstance(item, str) and len(item) <= 2:
                        total_chars += 1
                        if item not in words_set:
                            missing.append(item)
    print(f"Total kemunculan karakter (kasar, semua field list bertipe string pendek): {total_chars}")
    print(f"Tidak ditemukan di app_words.json: {len(missing)}  {missing[:20]}")


if __name__ == "__main__":
    main()

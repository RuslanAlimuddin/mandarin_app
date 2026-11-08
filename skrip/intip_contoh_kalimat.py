"""
intip_contoh_kalimat.py — READ-ONLY, tidak mengubah file apapun.

Tujuan: cek struktur PERSIS field contoh_kalimat_cn / contoh_kalimat_pinyin /
contoh_kalimat_id di data/app_words.json sebelum menulis kode render (E.0.1).
Jangan tebak -- BLUEPRINT v28 D.2 cuma bilang field ini "ADA" (257 entri),
belum pernah dicek tipe & bentuknya (array of string sejajar? array of
object? satu string panjang?).

Cara pakai:
    cd C:\\mandarin_app
    python intip_contoh_kalimat.py
"""

import json
import os

PATH = os.path.join("data", "app_words.json")

FIELDS = ["contoh_kalimat_cn", "contoh_kalimat_pinyin", "contoh_kalimat_id"]


def describe(value):
    t = type(value).__name__
    if isinstance(value, list):
        return f"list[len={len(value)}]  item_types={sorted(set(type(x).__name__ for x in value))}"
    if isinstance(value, str):
        return f"str[len={len(value)}]"
    return t


def main():
    with open(PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    print(f"Total entri: {len(data)}")

    # Cari semua entri yang punya minimal 1 dari 3 field ini
    hits = [w for w in data if any(f in w and w[f] for f in FIELDS)]
    print(f"Entri dengan minimal 1 field contoh_kalimat_* terisi: {len(hits)}")

    # Cek konsistensi panjang antar field (utk pastikan sejajar / tidak)
    mismatch = 0
    for w in hits:
        lens = {}
        for f in FIELDS:
            v = w.get(f)
            if isinstance(v, list):
                lens[f] = len(v)
        if len(set(lens.values())) > 1:
            mismatch += 1

    print(f"Entri dgn panjang array TIDAK sama antar field cn/pinyin/id: {mismatch}")

    print("\n" + "=" * 70)
    print("5 CONTOH ENTRI LENGKAP (field terkait + simplified utk konteks)")
    print("=" * 70)
    for w in hits[:5]:
        print(f"\n--- {w.get('simplified')} ({w.get('id')}) ---")
        for f in FIELDS:
            if f in w:
                print(f"  {f}: {describe(w[f])}")
                print(f"    isi: {json.dumps(w[f], ensure_ascii=False)[:300]}")
            else:
                print(f"  {f}: (field tidak ada di entri ini)")

    print("\n" + "=" * 70)
    print("SEMUA VARIAN TIPE yang muncul per field (di seluruh 11.983 entri)")
    print("=" * 70)
    for f in FIELDS:
        types_seen = set()
        list_item_types = set()
        max_len = 0
        for w in data:
            if f in w:
                v = w[f]
                types_seen.add(type(v).__name__)
                if isinstance(v, list):
                    max_len = max(max_len, len(v))
                    for item in v:
                        list_item_types.add(type(item).__name__)
                        if isinstance(item, dict):
                            list_item_types.add("dict_keys:" + ",".join(sorted(item.keys())))
        print(f"\n[{f}]")
        print(f"  tipe field yg muncul: {types_seen}")
        print(f"  kalau list -> tipe item: {list_item_types}, max panjang: {max_len}")


if __name__ == "__main__":
    main()

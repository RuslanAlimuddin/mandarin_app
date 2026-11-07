"""
intip_unicode_karakter_mirip.py — READ-ONLY.

Bandingkan Unicode codepoint PERSIS antara karakter di
confusion_groups.json vs app_words.json. Karakter yg visual mirip
(己/已/巳, dst) kadang punya codepoint BEDA walau kelihatan identik di
layar (CJK Unified Ideographs vs CJK Compatibility Ideographs, dst) --
ini bisa bikin pencocokan string gagal walau "kelihatan" sama.

Cara pakai:
    cd C:\\mandarin_app
    python intip_unicode_karakter_mirip.py
"""

import json
import os

PATH_CONFUSION = os.path.join("data", "confusion_groups.json")
PATH_WORDS = os.path.join("data", "app_words.json")


def codepoints(s):
    return ' '.join(f"U+{ord(c):04X}" for c in s)


def main():
    with open(PATH_CONFUSION, "r", encoding="utf-8") as f:
        confusion = json.load(f)
    with open(PATH_WORDS, "r", encoding="utf-8") as f:
        words = json.load(f)

    # Index semua simplified yg ada di app_words.json -> list of (index, id, simplified)
    simplified_index = {}
    for i, w in enumerate(words):
        s = w.get("simplified")
        if s:
            simplified_index.setdefault(s, []).append((i, w.get("id"), s))

    print("=" * 70)
    print("CEK SEMUA KARAKTER DI confusion_groups.json vs app_words.json")
    print("(bandingkan exact string match DAN codepoint Unicode)")
    print("=" * 70)

    for g in confusion["groups"]:
        chars = [g["character"]] + g.get("confusable_with", [])
        print(f"\n--- Grup id={g['id']}: {''.join(chars)} ---")
        for c in chars:
            cp = codepoints(c)
            hits = simplified_index.get(c)
            if hits:
                print(f"  {c!r} [{cp}]  -> DITEMUKAN di app_words.json ({len(hits)}x), contoh id={hits[0][1]}")
            else:
                print(f"  {c!r} [{cp}]  -> TIDAK DITEMUKAN exact match di app_words.json!")
                # cari kandidat mirip (semua entri app_words yg secara VISUAL
                # sama tapi codepoint beda) -- bandingkan via normalisasi kasar
                close = [k for k in simplified_index.keys() if len(k) == 1 and k != c]
                # cari yg unicode name category sama (KASAR: cek apakah selisih
                # codepoint kecil, indikasi varian kompatibilitas)
                for k in close:
                    if abs(ord(k) - ord(c)) < 200 and ord(c) > 0x3400:
                        # bukan bukti pasti, cuma petunjuk kasar
                        pass

    print("\n" + "=" * 70)
    print("RINGKASAN: seluruh karakter TIDAK DITEMUKAN (exact match gagal)")
    print("=" * 70)
    not_found = []
    for g in confusion["groups"]:
        chars = [g["character"]] + g.get("confusable_with", [])
        for c in chars:
            if c not in simplified_index:
                not_found.append((g["id"], c, codepoints(c)))

    if not_found:
        for gid, c, cp in not_found:
            print(f"  grup {gid}: {c!r} [{cp}]")
    else:
        print("  (semua ketemu -- kalau begini berarti masalahnya BUKAN di sini, cek tempat lain)")


if __name__ == "__main__":
    main()

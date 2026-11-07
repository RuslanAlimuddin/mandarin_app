"""
diagnosa_tier_a.py — READ-ONLY, tidak mengubah apapun.

Tujuan: memverifikasi APAKAH benar semua 40 kandidat Tier A (kata yang
punya synonyms/antonyms tapi belum punya synonyms_detail/antonyms_detail)
memang overlap dengan nuance_pairs.json -- atau ada isu pencocokan string
yang membuat exclude ini keliru.

Cara pakai:
    cd C:\\mandarin_app
    python diagnosa_tier_a.py
"""

import json
import os

PATH_WORDS = os.path.join("data", "app_words.json")
PATH_NUANCE = os.path.join("data", "nuance_pairs.json")


def load_nuance_words():
    with open(PATH_NUANCE, "r", encoding="utf-8") as f:
        nuance_raw = json.load(f)
    words_in_nuance = set()
    for p in nuance_raw.get("pairs", []):
        for w in p.get("words", []):
            words_in_nuance.add(w)
        for c in p.get("comparison", []):
            if c.get("word"):
                words_in_nuance.add(c["word"])
    return words_in_nuance


def main():
    with open(PATH_WORDS, "r", encoding="utf-8") as f:
        words = json.load(f)

    words_in_nuance = load_nuance_words()

    tier_a_all = [w for w in words if (w.get("synonyms") or w.get("antonyms"))
                  and not (w.get("synonyms_detail") or w.get("antonyms_detail"))]

    print(f"Total kandidat Tier A (sebelum exclude): {len(tier_a_all)}\n")
    print(f"{'Kata':<10} {'Simplified repr':<20} {'Ada di nuance?':<16} {'Match persis?'}")
    print("-" * 70)

    tidak_overlap = []
    for w in tier_a_all:
        simp = w.get("simplified")
        in_nuance = simp in words_in_nuance
        # Cek juga versi stripped, untuk deteksi whitespace tersembunyi
        stripped_match = simp.strip() in words_in_nuance if simp else False
        print(f"{simp!r:<10} {repr(simp):<20} {str(in_nuance):<16} {stripped_match}")
        if not in_nuance:
            tidak_overlap.append(simp)

    print(f"\n=== HASIL ===")
    print(f"Dari {len(tier_a_all)} kandidat, yang TIDAK overlap nuance: {len(tidak_overlap)}")
    if tidak_overlap:
        print("Kata-kata ini SEHARUSNYA lolos ke Tier A tapi tidak -- ada bug:")
        for w in tidak_overlap:
            print(f"  - {w}")
    else:
        print("Semua 40 kandidat memang overlap dengan nuance_pairs.json.")
        print("=> Exclude ini BENAR sesuai desain, BUKAN bug.")
        print("=> Tier A sudah habis/tuntas untuk saat ini.")


if __name__ == "__main__":
    main()

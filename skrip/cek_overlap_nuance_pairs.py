"""
cek_overlap_nuance_pairs.py — READ-ONLY, tidak mengubah apapun.

Cek overlap PENUH antara:
  - Tier A (60 kata, sudah ada synonyms/antonyms tapi belum ada note_id)
  - Tier B pilot (100 kata top kandidat, dari kandidat_tier_b_top150_v2.json)
terhadap kata-kata yang SUDAH ADA di data/nuance_pairs.json (1.291 pasangan,
2.579 kata unik).

Kalau overlap besar, artinya banyak kandidat kita SUDAH punya perbandingan
linguistik MENDALAM di nuance_pairs.json -- generate note_id/relasi baru yg
lebih dangkal untuk kata itu jadi kurang prioritas (bukan tidak berguna,
tapi nilai tambahnya lebih kecil drpd kata yg belum tersentuh sama sekali).

Cara pakai (jalankan SETELAH kandidat_tier_b_top150_v2.json ada, dari sesi
scan_kandidat_sinonim_antonim_v2.py sebelumnya):
    cd C:\\mandarin_app
    python cek_overlap_nuance_pairs.py
"""

import json
import os

PATH_WORDS = os.path.join("data", "app_words.json")
PATH_NUANCE = os.path.join("data", "nuance_pairs.json")
PATH_TIER_B = "kandidat_tier_b_top150_v2.json"


def main():
    with open(PATH_WORDS, "r", encoding="utf-8") as f:
        words = json.load(f)
    with open(PATH_NUANCE, "r", encoding="utf-8") as f:
        nuance_raw = json.load(f)

    nuance_pairs = nuance_raw.get("pairs", [])
    words_in_nuance = set()
    for p in nuance_pairs:
        for w in p.get("words", []):
            words_in_nuance.add(w)
        for c in p.get("comparison", []):
            if c.get("word"):
                words_in_nuance.add(c["word"])

    print(f"Total kata unik di nuance_pairs.json: {len(words_in_nuance)}")

    # ── Tier A: rekonstruksi 60 kata dari app_words.json (kriteria sama spt scan sblmnya) ──
    tier_a = [w for w in words if (w.get("synonyms") or w.get("antonyms"))
              and not (w.get("synonyms_detail") or w.get("antonyms_detail"))]
    tier_a_words = [w.get("simplified") for w in tier_a]

    overlap_a = [w for w in tier_a_words if w in words_in_nuance]
    print(f"\n=== TIER A ({len(tier_a_words)} kata) ===")
    print(f"Overlap dgn nuance_pairs.json: {len(overlap_a)}/{len(tier_a_words)}  ({100*len(overlap_a)/len(tier_a_words):.0f}%)")
    print(f"Kata yg overlap: {overlap_a}")
    not_overlap_a = [w for w in tier_a_words if w not in words_in_nuance]
    print(f"Kata yg TIDAK overlap (murni kandidat Tier A): {not_overlap_a}")

    # ── Tier B pilot: baca dari file hasil scan sebelumnya ──
    if os.path.exists(PATH_TIER_B):
        with open(PATH_TIER_B, "r", encoding="utf-8") as f:
            tier_b_data = json.load(f)
        tier_b_words = [w.get("simplified") for w in tier_b_data]

        overlap_b = [w for w in tier_b_words if w in words_in_nuance]
        print(f"\n=== TIER B PILOT ({len(tier_b_words)} kata) ===")
        print(f"Overlap dgn nuance_pairs.json: {len(overlap_b)}/{len(tier_b_words)}  ({100*len(overlap_b)/len(tier_b_words):.0f}%)")
        print(f"Kata yg overlap: {overlap_b}")
    else:
        print(f"\n[!] {PATH_TIER_B} tidak ditemukan -- jalankan scan_kandidat_sinonim_antonim_v2.py dulu")


if __name__ == "__main__":
    main()

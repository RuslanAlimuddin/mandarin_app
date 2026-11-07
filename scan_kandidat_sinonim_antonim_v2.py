"""
scan_kandidat_sinonim_antonim_v2.py — READ-ONLY.

Perbaikan dari v1 (setelah lihat hasil top-20 kotor):
  1. frequency == 1000000 diperlakukan sbg SENTINEL/tidak ada data asli
     -- kata dgn freq ini didorong ke BAWAH prioritas, bukan ke atas.
  2. Buang kata yg meanings_id-nya mengandung "varian" / "bentuk erhua" /
     "KP:" (pola polusi metadata yg sama spt di BLUEPRINT D.2) -- ini
     bukan makna asli, jadi kata itu bukan kandidat sinonim/antonim yg baik.
  3. pos_id kosong ([]) TETAP masuk tapi ditandai & didorong ke bawah
     (bukan otomatis dianggap kata konten spt v1).

Cara pakai:
    cd C:\\mandarin_app
    python scan_kandidat_sinonim_antonim_v2.py
"""

import json
import os
from collections import Counter

PATH_WORDS = os.path.join("data", "app_words.json")

SKIP_POS_ID_KEYWORDS = [
    "partikel", "kata bantu", "kata seru", "konjungsi", "preposisi",
    "kata ganti", "angka", "kata ukur", "onomatope",
]

# Pola polusi metadata (mirip D.2) yg menandakan meanings_id BUKAN arti asli
POLLUTED_MEANING_MARKERS = ["varian", "bentuk erhua", "kp:", "lihat juga"]

FREQ_SENTINEL = 1000000


def get_pos_id_str(w):
    raw = w.get("pos_id")
    if isinstance(raw, list):
        return " ".join(str(x) for x in raw).lower()
    return (raw or "").lower()


def has_polluted_meaning(w):
    meanings = w.get("meanings_id")
    if not meanings:
        return False
    if isinstance(meanings, str):
        meanings = [meanings]
    for m in meanings:
        m_low = (m or "").lower()
        if any(marker in m_low for marker in POLLUTED_MEANING_MARKERS):
            return True
    return False


def is_content_word(w):
    pos_id = get_pos_id_str(w)
    if any(kw in pos_id for kw in SKIP_POS_ID_KEYWORDS):
        return False
    return True


def main():
    with open(PATH_WORDS, "r", encoding="utf-8") as f:
        words = json.load(f)

    print(f"Total entri: {len(words)}")

    # ── TINGKAT A (sama spt v1, tidak berubah) ──
    tier_a = [w for w in words if (w.get("synonyms") or w.get("antonyms"))
              and not (w.get("synonyms_detail") or w.get("antonyms_detail"))]
    print(f"\n=== TINGKAT A (tidak berubah): {len(tier_a)} kata ===")

    # ── TINGKAT B v2 ──
    tier_b_clean = []      # pos_id jelas + meanings bersih -> prioritas utama
    tier_b_unclassified = []  # pos_id kosong tapi meanings bersih -> prioritas ke-2
    excluded_polluted = 0
    excluded_non_content = 0

    for w in words:
        has_syn = bool(w.get("synonyms"))
        has_ant = bool(w.get("antonyms"))
        hsk = w.get("hsk")
        if has_syn or has_ant or not hsk:
            continue

        if has_polluted_meaning(w):
            excluded_polluted += 1
            continue

        pos_id = get_pos_id_str(w)
        if not is_content_word(w):
            excluded_non_content += 1
            continue

        if pos_id.strip():
            tier_b_clean.append(w)
        else:
            tier_b_unclassified.append(w)

    def freq_sort_val(w):
        freq = w.get("frequency")
        try:
            freq = float(freq)
        except (TypeError, ValueError):
            return 0  # tidak ada data -> paling bawah
        if freq == FREQ_SENTINEL:
            return 0  # sentinel -> paling bawah, BUKAN paling atas
        return -freq  # freq asli -> makin tinggi makin diprioritaskan

    def hsk_val(w):
        try:
            return int(w.get("hsk"))
        except (TypeError, ValueError):
            return 99

    tier_b_clean.sort(key=lambda w: (hsk_val(w), freq_sort_val(w)))
    tier_b_unclassified.sort(key=lambda w: (hsk_val(w), freq_sort_val(w)))

    print(f"\n=== TINGKAT B v2 (setelah filter erhua/KP/varian + freq sentinel) ===")
    print(f"Dikecualikan krn meanings_id polusi (varian/erhua/KP:): {excluded_polluted}")
    print(f"Dikecualikan krn pos_id jelas non-konten (partikel dkk): {excluded_non_content}")
    print(f"Kandidat BERSIH, pos_id jelas (prioritas utama): {len(tier_b_clean)}")
    print(f"Kandidat pos_id BELUM terklasifikasi (prioritas ke-2): {len(tier_b_unclassified)}")

    hsk_counts = Counter(w.get("hsk") for w in tier_b_clean)
    print(f"Breakdown HSK (kandidat bersih): {dict(sorted(hsk_counts.items(), key=lambda x: str(x[0])))}")

    print("\nContoh 25 kata prioritas teratas (kandidat BERSIH):")
    for w in tier_b_clean[:25]:
        freq = w.get("frequency")
        freq_tag = " [SENTINEL]" if freq == FREQ_SENTINEL else ""
        print(f"  {w.get('simplified')} ({w.get('pinyin')})  hsk={w.get('hsk')}  freq={freq}{freq_tag}  pos_id={w.get('pos_id')}  arti={w.get('meanings_id')}")

    # Simpan top 150 kandidat bersih
    top_b = tier_b_clean[:150]
    out_path = "kandidat_tier_b_top150_v2.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(
            [
                {
                    "simplified": w.get("simplified"),
                    "pinyin": w.get("pinyin"),
                    "hsk": w.get("hsk"),
                    "frequency": w.get("frequency"),
                    "pos_id": w.get("pos_id"),
                    "meanings_id": w.get("meanings_id"),
                }
                for w in top_b
            ],
            f, ensure_ascii=False, indent=2
        )
    print(f"\nDaftar top 150 kandidat BERSIH disimpan ke: {out_path}")


if __name__ == "__main__":
    main()

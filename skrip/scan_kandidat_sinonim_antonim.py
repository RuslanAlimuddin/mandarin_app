"""
scan_kandidat_sinonim_antonim.py — READ-ONLY, tidak mengubah file apapun.

Tujuan (E.0.2b): petakan kandidat perluasan cakupan sinonim/antonim,
dipecah 2 tingkat:

  TINGKAT A (termurah/prioritas): kata yang field synonyms/antonyms
  (array-of-string, LAMA) SUDAH terisi, tapi BELUM punya
  synonyms_detail/antonyms_detail (note_id/pinyin) -- krn tidak
  termasuk 134 kata hasil merge synonym_antonym.json (E.0.2). AI cuma
  perlu nulis catatan nuansa utk pasangan yg RELASINYA SUDAH PASTI
  BENAR (sudah ada di data lama) -- risiko rendah, tidak perlu
  menentukan pasangan baru dari nol.

  TINGKAT B (lebih mahal): kata dgn HSK level (1-9), part-of-speech
  konten (kata kerja/sifat/benda -- bukan partikel/kata tugas), YANG
  field synonyms MAUPUN antonyms-nya KOSONG TOTAL. AI perlu menentukan
  pasangan relasi dari nol -- risiko lebih tinggi, urutkan by frequency
  desc spy yg paling sering dipakai duluan.

Cara pakai:
    cd C:\\mandarin_app
    python scan_kandidat_sinonim_antonim.py
"""

import json
import os

PATH_WORDS = os.path.join("data", "app_words.json")

# POS yang masuk akal punya sinonim/antonim (kata konten). Kode pos mentah
# blm diterjemahkan semua (lihat BLUEPRINT E.2), jadi kita filter longgar:
# skip yg jelas2 bukan kata konten kalau ketauan dari pos_id kalau ada.
SKIP_POS_ID_KEYWORDS = [
    "partikel", "kata bantu", "kata seru", "konjungsi", "preposisi",
    "kata ganti", "angka", "kata ukur", "onomatope",
]


def is_content_word(w):
    pos_id_raw = w.get("pos_id")
    if isinstance(pos_id_raw, list):
        pos_id = " ".join(str(x) for x in pos_id_raw).lower()
    else:
        pos_id = (pos_id_raw or "").lower()
    if any(kw in pos_id for kw in SKIP_POS_ID_KEYWORDS):
        return False
    return True


def main():
    with open(PATH_WORDS, "r", encoding="utf-8") as f:
        words = json.load(f)

    print(f"Total entri: {len(words)}")

    # ── TINGKAT A ──
    tier_a = []
    for w in words:
        has_old = bool(w.get("synonyms")) or bool(w.get("antonyms"))
        has_detail = bool(w.get("synonyms_detail")) or bool(w.get("antonyms_detail"))
        if has_old and not has_detail:
            tier_a.append(w)

    print(f"\n=== TINGKAT A: sudah ada relasi, belum ada note_id/pinyin ===")
    print(f"Jumlah kata: {len(tier_a)}")
    print("Contoh 15 kata pertama:")
    for w in tier_a[:15]:
        print(f"  {w.get('simplified')} (hsk={w.get('hsk')})  synonyms={w.get('synonyms')}  antonyms={w.get('antonyms')}")

    # ── TINGKAT B ──
    tier_b = []
    for w in words:
        has_syn = bool(w.get("synonyms"))
        has_ant = bool(w.get("antonyms"))
        hsk = w.get("hsk")
        if not has_syn and not has_ant and hsk and is_content_word(w):
            tier_b.append(w)

    # urutkan by frequency desc (kalau ada), fallback by hsk asc
    def sort_key(w):
        freq = w.get("frequency")
        try:
            freq_val = -float(freq) if freq is not None else 0
        except (TypeError, ValueError):
            freq_val = 0
        try:
            hsk_val = int(w.get("hsk"))
        except (TypeError, ValueError):
            hsk_val = 99
        return (hsk_val, freq_val)

    tier_b.sort(key=sort_key)

    print(f"\n=== TINGKAT B: HSK 1-9, kata konten, relasi KOSONG TOTAL ===")
    print(f"Jumlah kata: {len(tier_b)}")

    # breakdown per level HSK
    from collections import Counter
    hsk_counts = Counter(w.get("hsk") for w in tier_b)
    print(f"Breakdown per level HSK: {dict(sorted(hsk_counts.items(), key=lambda x: str(x[0])))}")

    print("\nContoh 20 kata prioritas teratas (HSK rendah + frequency tinggi dulu):")
    for w in tier_b[:20]:
        print(f"  {w.get('simplified')} ({w.get('pinyin')})  hsk={w.get('hsk')}  freq={w.get('frequency')}  pos_id={w.get('pos_id')}  arti={w.get('meanings_id')}")

    # Simpan daftar lengkap tier_b (top 150) ke file terpisah biar gampang dibaca
    top_b = tier_b[:150]
    out_path = "kandidat_tier_b_top150.json"
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
    print(f"\nDaftar top 150 kandidat Tingkat B disimpan ke: {out_path}")
    print("(dipakai script berikutnya utk generate prompt AI)")


if __name__ == "__main__":
    main()

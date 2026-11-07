"""
hitung_sisa_tier_b.py — READ-ONLY, tidak mengubah apapun.

Menjawab dua pertanyaan:
  1. Berapa kata TERSISA di pool Tier B (yang genuinely belum pernah
     berhasil dapat synonyms/antonyms)?
  2. Dari sisa itu, berapa yang KEMUNGKINAN BESAR permanen kosong
     (numeralia, partikel gramatikal, nama diri unik) -- supaya bisa
     di-exclude dari pool ke depannya, biar tiap cycle 100-kata tidak
     kebuang percuma untuk kata yang sudah pasti tidak akan dapat relasi.

Cara pakai:
    cd C:\\mandarin_app
    python hitung_sisa_tier_b.py
"""

import json
import os

PATH_WORDS = os.path.join("data", "app_words.json")
PATH_NUANCE = os.path.join("data", "nuance_pairs.json")

SKIP_POS_ID_KEYWORDS = [
    "partikel", "kata bantu", "kata seru", "konjungsi", "preposisi",
    "kata ganti", "angka", "kata ukur", "onomatope",
]
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
    return not any(kw in pos_id for kw in SKIP_POS_ID_KEYWORDS)


def load_nuance_words():
    with open(PATH_NUANCE, "r", encoding="utf-8") as f:
        nuance_raw = json.load(f)
    s = set()
    for p in nuance_raw.get("pairs", []):
        for w in p.get("words", []):
            s.add(w)
        for c in p.get("comparison", []):
            if c.get("word"):
                s.add(c["word"])
    return s


def is_pure_number(simplified):
    """Deteksi kasar: kata angka Mandarin murni (satuan/puluhan/ratusan dasar)."""
    NUMERAL_CHARS = set("零一二三四五六七八九十百千万亿两")
    return len(simplified) <= 2 and all(c in NUMERAL_CHARS for c in simplified)


def main():
    with open(PATH_WORDS, "r", encoding="utf-8") as f:
        words = json.load(f)
    words_in_nuance = load_nuance_words()

    # Pool Tier B identik dgn logika generate_prompt_sinonim_antonim_v3.py
    pool = []
    for w in words:
        has_syn = bool(w.get("synonyms"))
        has_ant = bool(w.get("antonyms"))
        hsk = w.get("hsk")
        if has_syn or has_ant or not hsk:
            continue
        if has_polluted_meaning(w):
            continue
        if not is_content_word(w):
            continue
        if w.get("simplified") in words_in_nuance:
            continue
        if get_pos_id_str(w).strip():
            pool.append(w)

    print(f"Total sisa pool Tier B (belum pernah dapat relasi): {len(pool)} kata")

    # Perkiraan konservatif berapa banyak yg genuinely tidak akan pernah dapat relasi
    kemungkinan_permanen_kosong = []
    for w in pool:
        simp = w.get("simplified", "")
        if is_pure_number(simp):
            kemungkinan_permanen_kosong.append(simp)
        elif len(simp) == 1 and get_pos_id_str(w).strip() == "":
            kemungkinan_permanen_kosong.append(simp)

    print(f"Kandidat 'kemungkinan permanen kosong' (angka murni dll): {len(kemungkinan_permanen_kosong)} kata")
    if kemungkinan_permanen_kosong:
        preview = kemungkinan_permanen_kosong[:30]
        print("Contoh:", ", ".join(preview))

    sisa_realistis = len(pool) - len(kemungkinan_permanen_kosong)
    print(f"\nSisa pool yang REALISTIS bisa dapat relasi: ~{sisa_realistis} kata")

    # Estimasi jumlah cycle, pakai rata2 fill-rate historis ~45% (dari observasi batch2 terakhir)
    for asumsi_persen, label in [(0.70, "optimis, spt batch2 awal"), (0.45, "rata-rata historis"), (0.25, "pesimis, spt batch2 terakhir")]:
        estimasi_kata_terisi_per_cycle = 100 * asumsi_persen
        if estimasi_kata_terisi_per_cycle > 0:
            estimasi_cycle = sisa_realistis / estimasi_kata_terisi_per_cycle
            print(f"  Estimasi cycle tersisa ({label}, ~{int(asumsi_persen*100)}% fill-rate): ~{estimasi_cycle:.0f} cycle lagi")


if __name__ == "__main__":
    main()

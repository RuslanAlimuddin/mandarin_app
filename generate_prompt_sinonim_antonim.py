"""
generate_prompt_sinonim_antonim.py — READ-ONLY (cuma baca app_words.json,
tidak mengubah apapun). Output: 4 file teks/JSON siap dipakai.

Cara pakai:
    cd C:\\mandarin_app
    python generate_prompt_sinonim_antonim.py

Hasil:
    prompt_tier_a.txt        <- copy-paste ISI FILE INI ke AI eksternal
    prompt_tier_b_pilot.txt  <- copy-paste ISI FILE INI ke AI eksternal
    (2 file ini sudah termasuk instruksi + data kata, siap pakai apa adanya)

Setelah dapat jawaban AI (harus JSON), simpan sbg:
    hasil_tier_a.json
    hasil_tier_b_pilot.json
lalu kasih ke Claude utk diaudit sebelum di-apply ke app_words.json.
"""

import json
import os
from collections import Counter

PATH_WORDS = os.path.join("data", "app_words.json")

SKIP_POS_ID_KEYWORDS = [
    "partikel", "kata bantu", "kata seru", "konjungsi", "preposisi",
    "kata ganti", "angka", "kata ukur", "onomatope",
]
POLLUTED_MEANING_MARKERS = ["varian", "bentuk erhua", "kp:", "lihat juga"]
FREQ_SENTINEL = 1000000
TIER_B_PILOT_SIZE = 100


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


def freq_sort_val(w):
    freq = w.get("frequency")
    try:
        freq = float(freq)
    except (TypeError, ValueError):
        return 0
    if freq == FREQ_SENTINEL:
        return 0
    return -freq


def hsk_val(w):
    try:
        return int(w.get("hsk"))
    except (TypeError, ValueError):
        return 99


def main():
    with open(PATH_WORDS, "r", encoding="utf-8") as f:
        words = json.load(f)

    # ── TINGKAT A ──
    tier_a = [w for w in words if (w.get("synonyms") or w.get("antonyms"))
              and not (w.get("synonyms_detail") or w.get("antonyms_detail"))]

    tier_a_data = [
        {
            "simplified": w.get("simplified"),
            "pinyin": w.get("pinyin"),
            "meaning_id": (w.get("meanings_id") or [""])[0] if isinstance(w.get("meanings_id"), list) else w.get("meanings_id"),
            "synonyms": w.get("synonyms") or [],
            "antonyms": w.get("antonyms") or [],
        }
        for w in tier_a
    ]

    prompt_a = f"""Kamu adalah ahli bahasa Mandarin-Indonesia. Tugasmu: untuk SETIAP kata di
bawah, dan untuk SETIAP kata di dalam daftar "synonyms" dan "antonyms"-nya
(daftar ini SUDAH DIPASTIKAN BENAR relasinya, JANGAN diubah/ditambah/dikurangi
kata-nya), tambahkan:
  1. "pinyin" -- pinyin bertona kata tsb
  2. "note_id" -- catatan SINGKAT (maks ~8 kata) dalam Bahasa Indonesia yang
     menjelaskan NUANSA kata itu dibanding kata utama. Untuk sinonim, jelaskan
     bedanya (register formal/informal, tingkat intensitas, konteks pemakaian).
     Untuk antonim, cukup terjemahan singkat kata itu sendiri.

Contoh gaya note_id yang diinginkan (dari data yang sudah ada):
  - 看 -> 望 (sinonim): "menatap jauh ke depan"
  - 看 -> 瞧 (sinonim): "melihat (informal/percakapan)"
  - 哭 -> 笑 (antonim): "tertawa, tersenyum"
  - 早 -> 晚 (antonim): "malam, terlambat"

ATURAN KETAT:
  - JANGAN mengubah, menambah, atau menghapus kata apapun dari daftar
    synonyms/antonyms yang diberikan -- HANYA tambahkan pinyin+note_id.
  - Output HARUS berupa JSON array valid, TIDAK ADA teks lain di luar JSON
    (tanpa ```json code fence, tanpa penjelasan sebelum/sesudah).
  - Format setiap item HARUS PERSIS seperti skema di bawah.

Skema output (array of object, satu object per kata utama):
[
  {{
    "simplified": "<kata utama, SAMA PERSIS spt input>",
    "synonyms": [ {{"word": "<kata>", "pinyin": "<pinyin>", "note_id": "<catatan>"}}, ... ],
    "antonyms": [ {{"word": "<kata>", "pinyin": "<pinyin>", "note_id": "<catatan>"}}, ... ]
  }},
  ...
]

DATA (60 kata, proses SEMUA):
{json.dumps(tier_a_data, ensure_ascii=False, indent=2)}
"""

    with open("prompt_tier_a.txt", "w", encoding="utf-8") as f:
        f.write(prompt_a)

    # ── TINGKAT B PILOT ──
    tier_b_clean = []
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
        if get_pos_id_str(w).strip():
            tier_b_clean.append(w)

    tier_b_clean.sort(key=lambda w: (hsk_val(w), freq_sort_val(w)))
    pilot = tier_b_clean[:TIER_B_PILOT_SIZE]

    tier_b_data = [
        {
            "simplified": w.get("simplified"),
            "pinyin": w.get("pinyin"),
            "hsk": w.get("hsk"),
            "pos_id": w.get("pos_id"),
            "meaning_id": (w.get("meanings_id") or [""])[0] if isinstance(w.get("meanings_id"), list) else w.get("meanings_id"),
        }
        for w in pilot
    ]

    prompt_b = f"""Kamu adalah ahli bahasa Mandarin-Indonesia yang menyusun kamus pembelajar.
Tugasmu: untuk SETIAP kata di bawah, tentukan sinonim (2-5 kata) dan antonim
(0-5 kata) yang PALING UMUM & NATURAL dipakai penutur asli -- BUKAN terjemahan
literal, tapi kata Mandarin lain yang benar-benar sering dipertukarkan/
dipertentangkan dalam percakapan sehari-hari atau tulisan standar.

ATURAN PALING PENTING -- JANGAN MEMAKSAKAN:
  - Kalau sebuah kata memang TIDAK PUNYA sinonim yang natural (mis. kata benda
    sangat spesifik seperti nama tempat/benda unik), biarkan array "synonyms"
    KOSONG []. JANGAN dipaksakan cari kata yang mirip tapi sebenarnya beda arti.
  - Sama utk "antonyms" -- banyak kata benda TIDAK PUNYA lawan kata alami
    (mis. "米饭"/nasi tidak punya antonim). Kalau begitu, biarkan array KOSONG.
  - LEBIH BAIK array kosong daripada pasangan yang dipaksakan/salah.
  - Kata ARAH (前边/后边/上边/下边/东边/西边/南边/北边/里边/外边) biasanya
    punya antonim yang SANGAT JELAS (arah berlawanan) -- pastikan itu terisi.

Untuk setiap kata di synonyms/antonyms yang kamu tentukan, sertakan juga:
  - "pinyin": pinyin bertona
  - "note_id": catatan SINGKAT (maks ~8 kata) dlm Bahasa Indonesia. Utk
    sinonim jelaskan bedanya (formal/informal, intensitas, konteks). Utk
    antonim cukup terjemahan singkat.

Output HARUS JSON array valid, TIDAK ADA teks lain di luar JSON (tanpa
```json code fence, tanpa penjelasan sebelum/sesudah).

Skema output:
[
  {{
    "simplified": "<kata utama, SAMA PERSIS spt input>",
    "synonyms": [ {{"word": "<kata>", "pinyin": "<pinyin>", "note_id": "<catatan>"}}, ... ],
    "antonyms": [ {{"word": "<kata>", "pinyin": "<pinyin>", "note_id": "<catatan>"}}, ... ]
  }},
  ...
]

DATA (100 kata, proses SEMUA -- kalau suatu kata memang tidak punya
sinonim/antonim natural, tetap sertakan object-nya dgn array kosong,
JANGAN dilewati/dihilangkan dari output):
{json.dumps(tier_b_data, ensure_ascii=False, indent=2)}
"""

    with open("prompt_tier_b_pilot.txt", "w", encoding="utf-8") as f:
        f.write(prompt_b)

    print(f"Tingkat A: {len(tier_a_data)} kata -> prompt_tier_a.txt")
    print(f"Tingkat B pilot: {len(tier_b_data)} kata -> prompt_tier_b_pilot.txt")
    print("\nLangkah selanjutnya:")
    print("1. Buka prompt_tier_a.txt, copy SEMUA isinya, tempel ke AI eksternal (mis. ChatGPT/Gemini).")
    print("   Simpan jawabannya (JSON) sbg hasil_tier_a.json")
    print("2. Ulangi utk prompt_tier_b_pilot.txt -> hasil_tier_b_pilot.json")
    print("3. Kasih kedua file hasil ke Claude utk diaudit sebelum apply.")


if __name__ == "__main__":
    main()

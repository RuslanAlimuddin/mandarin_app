"""
generate_prompt_sinonim_antonim_v3.py — READ-ONLY (tidak mengubah apapun).

v3.1: tambahan pengecualian kata yang sudah gagal dapat relasi berulang kali
(lihat TIER_B_EMPTY_THRESHOLD) -- supaya kata spt angka/partikel yang memang
tidak akan pernah dapat sinonim/antonim tidak terus membebani tiap batch
100-kata. Counter "_tb_empty_streak" diisi oleh apply_hasil_sinonim_antonim.py
tiap kali AI mengembalikan array kosong utk kata itu.

Final version: gabungan filter kualitas v2 (buang varian erhua/KP/freq
sentinel) + EXCLUDE kata yang sudah overlap dgn nuance_pairs.json (1.291
pasangan, 2.579 kata unik) -- supaya kuota generate AI eksternal fokus ke
kata yg BENAR-BENAR belum tersentuh di kedua sistem (bukan buang usaha
utk kata yg sudah dibahas mendalam di "Beda dengan Kata Mirip").

Cara pakai:
    cd C:\\mandarin_app
    python generate_prompt_sinonim_antonim_v3.py

Hasil:
    prompt_tier_a_v3.txt        <- copy-paste ke AI eksternal
    prompt_tier_b_pilot_v3.txt  <- copy-paste ke AI eksternal
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
TIER_B_PILOT_SIZE = 100

# Kata yg sudah gagal dapat relasi (synonyms+antonyms sama2 kosong dari AI)
# sebanyak ini kali berturut-turut, dikecualikan permanen dari pool Tier B.
TIER_B_EMPTY_THRESHOLD = 3

# Karakter yg menyusun angka Mandarin murni -- kata yg TERDIRI SELURUHNYA dari
# karakter ini (mis. 九, 七, 千万, 三十) dikecualikan proaktif dari pool Tier B,
# karena angka murni tidak akan pernah punya sinonim/antonim natural, dan AI
# kadang berhalusinasi (mis. mengira "8" antonim dari "9") alih-alih
# mengembalikan array kosong -- jadi tidak bisa diandalkan pada mekanisme
# _tb_empty_streak (itu cuma mendeteksi kosong, bukan mendeteksi salah).
NUMERAL_CHARS = set("零一二三四五六七八九十百千万亿两")


def is_pure_number(simplified):
    if not simplified:
        return False
    return all(c in NUMERAL_CHARS for c in simplified)


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
    print(f"Kata unik di nuance_pairs.json (dikecualikan dari batch): {len(words_in_nuance)}")

    # ── TINGKAT A (exclude overlap) ──
    tier_a_all = [w for w in words if (w.get("synonyms") or w.get("antonyms"))
                  and not (w.get("synonyms_detail") or w.get("antonyms_detail"))]
    tier_a = [w for w in tier_a_all if w.get("simplified") not in words_in_nuance]

    print(f"Tier A: {len(tier_a_all)} kandidat awal -> {len(tier_a)} setelah exclude overlap nuance")

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

DATA ({len(tier_a_data)} kata, proses SEMUA):
{json.dumps(tier_a_data, ensure_ascii=False, indent=2)}
"""

    with open("prompt_tier_a_v3.txt", "w", encoding="utf-8") as f:
        f.write(prompt_a)

    # ── TINGKAT B PILOT (exclude overlap + exclude sudah gagal berulang) ──
    tier_b_clean = []
    excluded_by_streak = 0
    excluded_numeral = 0
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
            continue  # exclude overlap
        if is_pure_number(w.get("simplified")):
            excluded_numeral += 1
            continue  # angka murni, kecualikan proaktif (lihat komentar di atas)
        if w.get("_tb_empty_streak", 0) >= TIER_B_EMPTY_THRESHOLD:
            excluded_by_streak += 1
            continue  # sudah gagal dapat relasi berulang kali, skip permanen
        if get_pos_id_str(w).strip():
            tier_b_clean.append(w)

    tier_b_clean.sort(key=lambda w: (hsk_val(w), freq_sort_val(w)))
    pilot = tier_b_clean[:TIER_B_PILOT_SIZE]

    print(f"Tier B: {len(tier_b_clean)} kandidat bersih setelah exclude overlap nuance + exclude angka murni + exclude gagal-berulang (total, semua level)")
    print(f"Tier B: {excluded_numeral} kata dikecualikan krn angka murni")
    print(f"Tier B: {excluded_by_streak} kata dikecualikan permanen krn sudah gagal >= {TIER_B_EMPTY_THRESHOLD}x berturut-turut")
    print(f"Tier B pilot diambil: {len(pilot)} kata")

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
  - JANGAN mengusulkan kata yang maknanya lebih SEMPIT/SPESIFIK (hiponim) atau
    lebih LUAS/UMUM (hipernim) dari kata utama sebagai sinonim -- mis. "瓜"
    (melon/labu secara umum) BUKAN sinonim dari "甜瓜"/"南瓜" (jenis2 spesifik
    dari 瓜). Sinonim harus level makna yang SAMA, bukan relasi jenis-kategori.
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

DATA ({len(tier_b_data)} kata, proses SEMUA -- kalau suatu kata memang tidak
punya sinonim/antonim natural, tetap sertakan object-nya dgn array kosong,
JANGAN dilewati/dihilangkan dari output):
{json.dumps(tier_b_data, ensure_ascii=False, indent=2)}
"""

    with open("prompt_tier_b_pilot_v3.txt", "w", encoding="utf-8") as f:
        f.write(prompt_b)

    print(f"\nTingkat A final: {len(tier_a_data)} kata -> prompt_tier_a_v3.txt")
    print(f"Tingkat B pilot final: {len(tier_b_data)} kata -> prompt_tier_b_pilot_v3.txt")


if __name__ == "__main__":
    main()

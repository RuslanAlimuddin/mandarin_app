# extract_phonetic.py
# Mengekstrak komponen fonetik (声符) untuk semua karakter di app_words.json
# menggunakan paket `hanzipy` (data linguistik nyata, bukan tebakan heuristik).
#
# CARA PAKAI:
#   1. pip install hanzipy --break-system-packages
#   2. Taruh script ini di folder C:\mandarin_app\ (sejajar dengan folder data\)
#   3. Jalankan: python extract_phonetic.py
#   4. Hasil: data\index_phonetic.json
#
# Format output (mirip index_radical.json):
#   { "马": ["妈","骂","码","蚂", ...], "青": ["清","请","情", ...], ... }
# artinya: kata-kata di app_words.json yang punya komponen fonetik tsb.

import json
import logging
import os
import re
import sys

# Matikan SEMUA log debug/info bawaan hanzipy supaya output bersih
logging.disable(logging.INFO)
logging.basicConfig(level=logging.WARNING)

try:
    from hanzipy.dictionary import HanziDictionary
except ImportError:
    print("[ERROR] Paket 'hanzipy' belum terinstall.")
    print("        Jalankan dulu: pip install hanzipy --break-system-packages")
    sys.exit(1)

DATA_DIR   = 'data'
INPUT_FILE = os.path.join(DATA_DIR, 'app_words.json')
OUTPUT_FILE = os.path.join(DATA_DIR, 'index_phonetic.json')


def strip_tone_number(syll):
    """'ma3' -> 'ma', 'Ma3' -> 'ma' (untuk normalisasi perbandingan)."""
    if not syll:
        return ''
    return re.sub(r'\d+$', '', syll).lower().replace('u:', 'v')


STRONG_MATCH = {1, 2}

# Goresan dasar / radikal sangat umum yang TIDAK bermakna sebagai komponen fonetik
# meski lolos cek regularity (terlalu generik untuk jadi dasar pengelompokan game)
BASIC_STROKES = {
    '一', '丨', '丶', '丿', '乙', '亅', '二', '十', '人', '入', '八', '儿',
    '冂', '冖', '凵', '刀', '力', '勹', '匕', '匚', '匸', '又',
}


def get_phonetic_components(dictionary, char):
    """
    Ambil komponen fonetik VALID untuk satu karakter.

    PENTING — skala 'regularity' di hanzipy itu KEBALIKAN dari intuisi (angka lebih
    kecil = match lebih kuat), berdasarkan source code hanzipy/dictionary.py:
        1 = Match Persis (termasuk nada)   <- terbaik, mis. ma1 vs ma1
        2 = Match Suku Kata (tanpa nada)    <- masih kuat, mis. ma1 vs ma3
        3 = Mirip di Konsonan Awal saja     <- lemah
        4 = Mirip di Vokal Akhir saja       <- sangat lemah, banyak noise (mis. semua
                                               kata berakhiran 'i' nyangkut ke karakter
                                               manapun yang juga berakhir 'i')
        0 = Tidak ada hubungan sama sekali
        None = tidak ada data pinyin pembanding

    Kita HANYA ambil regularity 1 atau 2 (match suku kata kuat) supaya hasil grup
    fonetik benar-benar bermakna seperti contoh 马 -> 妈/骂/码/蚂, bukan noise seperti
    一/丨/十 yang sebelumnya nyangkut ke ratusan kata tak terkait.

    Mengembalikan set komponen (bisa kosong jika tidak ada).
    """
    components = set()
    try:
        result = dictionary.determine_phonetic_regularity(char)
    except Exception:
        return components

    if not result:
        return components

    # result: { "ma1": {"component":[...], "phonetic_pinyin":[...], "regularity":[...]}, ... }
    for pron_key, info in result.items():
        comps = info.get('component', [])
        regs  = info.get('regularity', [])
        for comp, reg in zip(comps, regs):
            if not comp or comp == 'No glyph available':
                continue
            if comp == char:
                continue  # lewati diri sendiri
            if comp in BASIC_STROKES:
                continue  # pengaman tambahan: goresan dasar bukan fonetik bermakna
            if reg in STRONG_MATCH:
                components.add(comp)

    return components


def main():
    if not os.path.exists(INPUT_FILE):
        print(f"[ERROR] File tidak ditemukan: {INPUT_FILE}")
        print("        Jalankan script ini dari folder C:\\mandarin_app\\")
        sys.exit(1)

    print("[INFO] Memuat app_words.json ...")
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        words = json.load(f)
    print(f"[INFO] {len(words)} entri kata dimuat.")

    print("[INFO] Menginisialisasi hanzipy dictionary (mungkin perlu beberapa detik) ...")
    dictionary = HanziDictionary()

    # index_phonetic: { komponen_fonetik: set(word_id, ...) }
    index_phonetic = {}

    # Cache supaya karakter yang sama tidak dianalisis berkali-kali
    char_cache = {}

    total = len(words)
    processed_chars = 0
    matched_words = 0

    for i, w in enumerate(words):
        if (i + 1) % 1000 == 0:
            print(f"[INFO] Diproses {i + 1}/{total} kata ...")

        word_id    = w.get('id') or w.get('simplified', '')
        simplified = w.get('simplified', word_id)
        if not simplified:
            continue

        word_components = set()

        # Untuk kata 1 karakter: analisis langsung
        # Untuk kata >1 karakter: analisis tiap karakter penyusunnya
        for ch in simplified:
            if not ('\u4e00' <= ch <= '\u9fff'):
                continue  # bukan hanzi (misal tanda baca), lewati

            if ch not in char_cache:
                char_cache[ch] = get_phonetic_components(dictionary, ch)
                processed_chars += 1

            word_components |= char_cache[ch]

        if word_components:
            matched_words += 1
            for comp in word_components:
                index_phonetic.setdefault(comp, [])
                if word_id not in index_phonetic[comp]:
                    index_phonetic[comp].append(word_id)

    # Urutkan tiap grup berdasarkan jumlah kata terbanyak dulu (untuk konsistensi tampilan)
    index_phonetic_sorted = dict(
        sorted(index_phonetic.items(), key=lambda kv: -len(kv[1]))
    )

    os.makedirs(DATA_DIR, exist_ok=True)
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(index_phonetic_sorted, f, ensure_ascii=False, indent=2)

    print()
    print(f"[SELESAI] {OUTPUT_FILE} berhasil dibuat.")
    print(f"          Karakter unik dianalisis : {processed_chars}")
    print(f"          Kata dengan match fonetik : {matched_words} / {total}")
    print(f"          Jumlah grup komponen fonetik: {len(index_phonetic_sorted)}")
    print()
    print("[CATATAN] Data ini berbasis hanzipy (cjk-decomp), cukup akurat tapi bukan")
    print("          sempurna 100% — disarankan spot-check beberapa grup besar")
    print("          (lihat 10-20 grup teratas) sebelum dipakai di aplikasi.")

    # Tampilkan 10 grup terbesar sebagai sample untuk verifikasi cepat
    print()
    print("=== SAMPLE 10 GRUP FONETIK TERBESAR ===")
    for comp, ids in list(index_phonetic_sorted.items())[:10]:
        sample = ids[:8]
        more = f" (+{len(ids)-8} lagi)" if len(ids) > 8 else ""
        print(f"  {comp}: {', '.join(sample)}{more}")


if __name__ == '__main__':
    main()

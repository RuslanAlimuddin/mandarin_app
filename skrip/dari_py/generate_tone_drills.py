"""
generate_tone_drills.py
═══════════════════════════════════════════════════════════════
Generate data/tone_drills.json dari data/app_words.json untuk
Modul Latihan Tone (Mandarin Interaktif, Tier 3).

Menghasilkan 2 kumpulan soal:
  1. "singles" -- kata 1 karakter yang nadanya jelas (1-4, bukan netral),
     dipakai untuk mode "Pilih Nada" (dengar audio -> pilih tombol 1/2/3/4).
  2. "groups"  -- SEMUA kata (1 karakter maupun lebih) dikelompokkan
     berdasarkan pinyin TANPA tanda nada (mis. "xǐhuan" & "xíhuan"
     sama-sama jadi "xihuan"). Kelompok dengan >=2 kata berbeda dipakai
     untuk mode "Pilih Hanzi" (dengar audio -> pilih hanzi yang benar
     dari beberapa pilihan mirip/minimal-pair).

Jalankan dari folder root proyek (C:\\mandarin_app):
    python generate_tone_drills.py

Output: data/tone_drills.json
═══════════════════════════════════════════════════════════════
"""

import json
import sys
from collections import defaultdict

INPUT_PATH  = 'data/app_words.json'
OUTPUT_PATH = 'data/tone_drills.json'

VALID_HSK_LEVELS = [1, 2, 3, 4, 5, 6, 7]

# Tanda diakritik -> nomor nada
TONE_MAP = {
    'ā': 1, 'ē': 1, 'ī': 1, 'ō': 1, 'ū': 1, 'ǖ': 1,
    'á': 2, 'é': 2, 'í': 2, 'ó': 2, 'ú': 2, 'ǘ': 2,
    'ǎ': 3, 'ě': 3, 'ǐ': 3, 'ǒ': 3, 'ǔ': 3, 'ǚ': 3,
    'à': 4, 'è': 4, 'ì': 4, 'ò': 4, 'ù': 4, 'ǜ': 4,
}

# Tanda diakritik -> huruf polos (untuk bikin pinyin tanpa nada)
TONELESS_MAP = {
    'ā': 'a', 'á': 'a', 'ǎ': 'a', 'à': 'a',
    'ē': 'e', 'é': 'e', 'ě': 'e', 'è': 'e',
    'ī': 'i', 'í': 'i', 'ǐ': 'i', 'ì': 'i',
    'ō': 'o', 'ó': 'o', 'ǒ': 'o', 'ò': 'o',
    'ū': 'u', 'ú': 'u', 'ǔ': 'u', 'ù': 'u',
    'ǖ': 'ü', 'ǘ': 'ü', 'ǚ': 'ü', 'ǜ': 'ü',
}


def as_hsk_int(val):
    """Normalisasi field hsk yang bisa berupa int, string angka, string 'HSK1',
       float, atau None -> int atau None."""
    if val is None or isinstance(val, bool):
        return None
    if isinstance(val, int):
        return val
    if isinstance(val, float):
        return int(val)
    if isinstance(val, str):
        digits = ''.join(ch for ch in val if ch.isdigit())
        return int(digits) if digits else None
    return None


def toneless_pinyin(py):
    """'xǐhuan' -> 'xihuan' (lowercase, tanda nada dibuang)."""
    return ''.join(TONELESS_MAP.get(ch, ch) for ch in py).lower()


def single_syllable_tone(py):
    """Cari tanda nada PERTAMA di string; None kalau tidak ada (netral).
       Untuk kata 1 karakter ini setara dengan nada satu-satunya suku kata."""
    for ch in py:
        if ch in TONE_MAP:
            return TONE_MAP[ch]
    return None


def primary_meaning(word):
    """Ambil arti pertama yang berguna dari meanings_id (skip catatan varian)."""
    meanings = word.get('meanings_id') or []
    if isinstance(meanings, str):
        meanings = [meanings]
    if not meanings:
        return ''
    for m in meanings:
        low = m.lower()
        if not (low.startswith('varian dari') or low.startswith('varian lama dari')):
            prefix = '(bentuk terikat)'
            return m[len(prefix):].strip() if low.startswith(prefix) else m
    return meanings[0]


def load_words():
    try:
        with open(INPUT_PATH, encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"✗ Tidak ditemukan: {INPUT_PATH}")
        print("  Jalankan skrip ini dari folder root proyek (C:\\mandarin_app).")
        sys.exit(1)


def make_entry(word):
    return {
        'cn':  word.get('simplified', ''),
        'py':  word.get('pinyin', ''),
        'id':  primary_meaning(word),
        'hsk': as_hsk_int(word.get('hsk')),
    }


def main():
    words = load_words()
    print(f"Total kata dimuat: {len(words)}")

    # ── 1. SINGLES: kata 1 karakter dengan nada 1-4 yang jelas ──────
    singles = []
    for w in words:
        cn = w.get('simplified', '')
        py = w.get('pinyin', '')
        if not cn or not py or len(cn) != 1:
            continue
        hsk = as_hsk_int(w.get('hsk'))
        if hsk not in VALID_HSK_LEVELS:
            continue
        tone = single_syllable_tone(py)
        if tone is None:
            continue  # nada netral -- tidak dipakai di mode "Pilih Nada"
        entry = make_entry(w)
        entry['tone'] = tone
        entry['base'] = toneless_pinyin(py)
        singles.append(entry)

    # ── 2. GROUPS: semua kata dikelompokkan per pinyin tanpa nada ───
    by_base = defaultdict(list)
    seen_cn_per_base = defaultdict(set)
    for w in words:
        cn = w.get('simplified', '')
        py = w.get('pinyin', '')
        if not cn or not py:
            continue
        hsk = as_hsk_int(w.get('hsk'))
        if hsk not in VALID_HSK_LEVELS:
            continue
        base = toneless_pinyin(py)
        if cn in seen_cn_per_base[base]:
            continue  # hindari duplikat hanzi yang sama persis di grup yang sama
        seen_cn_per_base[base].add(cn)
        by_base[base].append(make_entry(w))

    # Hanya simpan grup yang punya >=2 hanzi BERBEDA (baru bisa jadi pilihan ganda)
    groups = {base: entries for base, entries in by_base.items() if len(entries) >= 2}

    output = {'singles': singles, 'groups': groups}

    with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"\n✓ Selesai. Output: {OUTPUT_PATH}")
    print(f"  Soal 'Pilih Nada'  (singles): {len(singles)} kata")
    print(f"  Soal 'Pilih Hanzi' (groups) : {len(groups)} kelompok, "
          f"{sum(len(v) for v in groups.values())} kata total")

    # Ringkasan distribusi nada di singles (sanity check)
    tone_dist = defaultdict(int)
    for e in singles:
        tone_dist[e['tone']] += 1
    print(f"  Distribusi nada: " + ', '.join(f"T{t}:{tone_dist[t]}" for t in sorted(tone_dist)))


if __name__ == '__main__':
    main()

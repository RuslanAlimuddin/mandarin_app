# -*- coding: utf-8 -*-
"""
enrich_leksikon_khusus.py
────────────────────────────
TAHAP 2: mengisi field struktural (radical, radical_number, stroke_count,
structure, components, char_type, bopomofo) untuk 470 entri baru di
staging/*.json (kata_seru, onomatope, sapaan_keluarga, sapaan_sosial,
partikel_modal) yang sebelumnya masih null.

STRATEGI 2 LAPIS:
  LAPIS 1 (utama, paling akurat): bangun tabel lookup PER KARAKTER dari
    entri 1-karakter yang SUDAH ADA di app_words.json (11.726 entri).
    Karena field struktural sifatnya per-karakter (bukan per-kata), dan
    hampir semua karakter di 470 entri baru ini karakter umum yang sudah
    pasti ada di kamus, lapis ini akan menutup mayoritas kasus.

  LAPIS 2 (fallback, untuk karakter langka yang TIDAK ketemu di Lapis 1):
    hitung dari data/dictionary.txt (radikal + decomposition mentah) +
    data/hanzi_writer_data.json (jumlah goresan dari panjang array
    "strokes") + kangxi_radical_map.json (nomor radikal, dengan tabel
    padanan varian glyph -> bentuk kanonis Kangxi).

ATURAN AGREGASI UNTUK KATA MULTI-KARAKTER (disalin persis dari
build_app_words.py yang sudah terverifikasi jalan di app_words.json asli):
  - stroke_count = SUM stroke_count tiap karakter
  - structure    = structure karakter PERTAMA (fallback 'single')
  - components   = UNION (dedup, urutan dipertahankan) dari components
                   tiap karakter
  - char_type    = 'compound' kalau kata >1 karakter
  - radical, radical_number = dari karakter PERTAMA
  - bopomofo     = bopomofo tiap karakter disambung spasi

TIDAK mengubah app_words.json. Output ditulis ke staging/*_enriched.json
plus laporan cakupan (berapa % terselesaikan Lapis 1 vs Lapis 2 vs masih
kosong -> perlu isi manual).

CARA PAKAI:
    cd C:\\mandarin_app
    python enrich_leksikon_khusus.py

PRASYARAT:
  - staging/kata_seru.json, onomatope.json, sapaan_keluarga.json,
    sapaan_sosial.json, partikel_modal.json (hasil Tahap 1 / audit)
    sudah ada di folder staging/ (sejajar folder ini)
  - kangxi_radical_map.json ditaruh di folder yang sama dengan script
    ini (copy dari C:\\mandarin_kamus\\database\\kangxi_radical_map.json)
"""

import json
import os
from pathlib import Path
from collections import defaultdict

DATA_DIR       = Path("data")
APP_WORDS_PATH = DATA_DIR / "app_words.json"
DICT_TXT_PATH  = DATA_DIR / "dictionary.txt"
WRITER_PATH    = DATA_DIR / "hanzi_writer_data.json"
KANGXI_PATH    = Path("kangxi_radical_map.json")   # taruh di folder script ini
STROKE_SUPPLEMENT_PATH = Path("stroke_supplement_58chars.json")  # taruh di folder script ini juga

STAGING_DIR    = Path("staging")
CATEGORY_FILES = ["kata_seru", "onomatope", "sapaan_keluarga", "sapaan_sosial", "partikel_modal"]

REPORT_PATH = Path("laporan_enrichment_leksikon.txt")

# Padanan varian glyph radikal (bentuk yang sering muncul di data anda,
# termasuk bentuk sederhana/varian posisi) -> bentuk KANONIS Kangxi yang
# dipakai kangxi_radical_map.json. Daftar ini TIDAK lengkap 100% (214
# radikal semua punya varian), tapi mencakup varian paling umum yang
# kemungkinan besar muncul di karakter leksikon khusus kita.
VARIANT_TO_KANGXI = {
    "⺼": "肉",                      # 月="daging" (tapi 月 asli="bulan" -- lihat AMBIGUOUS_RADICALS)
    "讠": "言", "钅": "金", "氵": "水", "扌": "手", "忄": "心",
    "辶": "辵", "艹": "艸", "礻": "示", "衤": "衣", "纟": "糸",
    "饣": "食", "刂": "刀", "冫": "水", "犭": "犬", "灬": "火",
    "亻": "人",                      # BARU: dipakai di 侄/你/他/们 dst.
    "⺮": "竹",                      # BARU: dipakai di 算/笑/筷 dst.
    "罒": "网",                      # BARU: dipakai di 罢/罗/署 dst.
    "⺶": "羊", "⺷": "羊",           # BARU: varian atas 养/美 dst.
}
# CATATAN PENTING: 月 dan 阝 itu AMBIGU -- 月 bisa radikal 74 (bulan, asli)
# ATAU varian radikal 130 (daging/肉); 阝 bisa radikal 170 (阜, di KIRI,
# spt 阿/陀/防) ATAU radikal 163 (邑, di KANAN, spt 阁/那/部) -- posisinya
# tidak bisa dipastikan cuma dari field "radical" dictionary.txt tanpa
# analisis lebih lanjut. Kita TIDAK menebak untuk kasus ini -- radical_number
# dibiarkan None + ditandai isi manual, lebih aman daripada salah 50/50.
AMBIGUOUS_RADICALS = {"月", "阝"}


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


# ══════════════════════════════════════════════════════════════════
# KONVERSI PINYIN (DIAKRITIK) -> BOPOMOFO — deterministik, tidak butuh
# lookup karakter sama sekali. Dipakai LANGSUNG dari field "pinyin"
# yang sudah ada di tiap entri (bukan dari tier1/tier2 per-karakter).
# ══════════════════════════════════════════════════════════════════
_TONE_REVERSE = {}
_TONE_TABLE = {
    'a': 'āáǎà', 'e': 'ēéěè', 'i': 'īíǐì',
    'o': 'ōóǒò', 'u': 'ūúǔù', 'ü': 'ǖǘǚǜ',
}
for base, marks in _TONE_TABLE.items():
    for tone_idx, ch in enumerate(marks, start=1):
        _TONE_REVERSE[ch] = (base, tone_idx)

_INITIALS = ['zh', 'ch', 'sh', 'b', 'p', 'm', 'f', 'd', 't', 'n', 'l',
             'g', 'k', 'h', 'j', 'q', 'x', 'r', 'z', 'c', 's', 'y', 'w']
_INITIAL_BOPOMOFO = {
    'zh': 'ㄓ', 'ch': 'ㄔ', 'sh': 'ㄕ', 'r': 'ㄖ', 'z': 'ㄗ', 'c': 'ㄘ', 's': 'ㄙ',
    'b': 'ㄅ', 'p': 'ㄆ', 'm': 'ㄇ', 'f': 'ㄈ', 'd': 'ㄉ', 't': 'ㄊ', 'n': 'ㄋ',
    'l': 'ㄌ', 'g': 'ㄍ', 'k': 'ㄎ', 'h': 'ㄏ', 'j': 'ㄐ', 'q': 'ㄑ', 'x': 'ㄒ',
}
_BUZZ_INITIALS = {'zh', 'ch', 'sh', 'r', 'z', 'c', 's'}  # final "i" tak ditulis

_FINAL_BOPOMOFO = {
    'a': 'ㄚ', 'o': 'ㄛ', 'e': 'ㄜ', 'ê': 'ㄝ', 'ai': 'ㄞ', 'ei': 'ㄟ',
    'ao': 'ㄠ', 'ou': 'ㄡ', 'an': 'ㄢ', 'en': 'ㄣ', 'ang': 'ㄤ', 'eng': 'ㄥ',
    'ong': 'ㄨㄥ', 'er': 'ㄦ',
    'i': 'ㄧ', 'ia': 'ㄧㄚ', 'ie': 'ㄧㄝ', 'iao': 'ㄧㄠ', 'iu': 'ㄧㄡ', 'iou': 'ㄧㄡ',
    'ian': 'ㄧㄢ', 'in': 'ㄧㄣ', 'iang': 'ㄧㄤ', 'ing': 'ㄧㄥ', 'iong': 'ㄩㄥ',
    'u': 'ㄨ', 'ua': 'ㄨㄚ', 'uo': 'ㄨㄛ', 'uai': 'ㄨㄞ', 'ui': 'ㄨㄟ', 'uei': 'ㄨㄟ',
    'uan': 'ㄨㄢ', 'un': 'ㄨㄣ', 'uen': 'ㄨㄣ', 'uang': 'ㄨㄤ', 'ueng': 'ㄨㄥ',
}
_FINAL_BOPOMOFO_V = {  # final dengan ü (dipakai setelah j/q/x/y DAN n/l -- 女nǚ/绿lǜ dst.)
    'u': 'ㄩ', 'ue': 'ㄩㄝ', 've': 'ㄩㄝ', 'uan': 'ㄩㄢ', 'un': 'ㄩㄣ',
    'ü': 'ㄩ', 'üe': 'ㄩㄝ',
}
_V_INITIALS = {'j', 'q', 'x', 'y', 'n', 'l'}  # inisial yang bisa diikuti ü
_STANDALONE_Y = {  # syllable diawali y (tanpa initial konsonan biasa)
    'yi': 'ㄧ', 'ya': 'ㄧㄚ', 'ye': 'ㄧㄝ', 'yao': 'ㄧㄠ', 'you': 'ㄧㄡ',
    'yan': 'ㄧㄢ', 'yin': 'ㄧㄣ', 'yang': 'ㄧㄤ', 'ying': 'ㄧㄥ', 'yong': 'ㄩㄥ',
    'yu': 'ㄩ', 'yue': 'ㄩㄝ', 'yuan': 'ㄩㄢ', 'yun': 'ㄩㄣ', 'yo': 'ㄧㄛ',
}
_STANDALONE_W = {
    'wu': 'ㄨ', 'wa': 'ㄨㄚ', 'wo': 'ㄨㄛ', 'wai': 'ㄨㄞ', 'wei': 'ㄨㄟ',
    'wan': 'ㄨㄢ', 'wen': 'ㄨㄣ', 'wang': 'ㄨㄤ', 'weng': 'ㄨㄥ',
}
_TONE_MARK = {1: '', 2: 'ˊ', 3: 'ˇ', 4: 'ˋ', 5: '˙'}


def _strip_tone(syl_raw):
    """'āi' -> ('ai', 1). Kalau tak ada diakritik -> nada netral (5)."""
    tone = 5
    plain = []
    for ch in syl_raw:
        if ch in _TONE_REVERSE:
            base, t = _TONE_REVERSE[ch]
            plain.append(base)
            tone = t
        else:
            plain.append(ch)
    return ''.join(plain), tone


def syllable_to_bopomofo(syl_raw):
    """Konversi 1 suku kata pinyin (dengan diakritik, boleh ada angka nada
    seperti fallback) ke Bopomofo. Return None kalau polanya tak dikenali
    (lebih baik None -> ditandai manual, daripada salah)."""
    syl_raw = syl_raw.strip()
    if not syl_raw:
        return None
    # dukung juga input angka nada di akhir (mis. 'ai1') sebagai fallback
    if syl_raw[-1].isdigit():
        tone = int(syl_raw[-1])
        plain = syl_raw[:-1].replace('v', 'ü')
    else:
        plain, tone = _strip_tone(syl_raw)
        plain = plain.replace('v', 'ü')

    plain = plain.lower()

    # standalone y-/w- syllables (tanpa initial konsonan)
    if plain in _STANDALONE_Y:
        return _STANDALONE_Y[plain] + _TONE_MARK.get(tone, '')
    if plain in _STANDALONE_W:
        return _STANDALONE_W[plain] + _TONE_MARK.get(tone, '')

    # cari initial (urutan terpanjang dulu supaya zh/ch/sh kepilih sebelum z/c/s/h)
    initial = ''
    for cand in _INITIALS:
        if plain.startswith(cand) and cand not in ('y', 'w'):
            initial = cand
            break

    final = plain[len(initial):]

    # kasus buzz-i (zhi/chi/shi/ri/zi/ci/si) -- final 'i' tak ditulis di bopomofo
    if initial in _BUZZ_INITIALS and final == 'i':
        return (_INITIAL_BOPOMOFO.get(initial, '') or '') + _TONE_MARK.get(tone, '')

    # kasus ü setelah j/q/x/y/n/l (ditulis 'u' di pinyin tapi berarti ü,
    # ATAU sudah literal 'ü' kalau berasal dari v->ü replace di awal)
    if initial in _V_INITIALS and final in _FINAL_BOPOMOFO_V:
        fb = _FINAL_BOPOMOFO_V[final]
    else:
        fb = _FINAL_BOPOMOFO.get(final)

    if fb is None or (not initial and plain not in _STANDALONE_Y and plain not in _STANDALONE_W):
        # final tak dikenal / tak ada initial & bukan standalone y/w yang dikenal
        if fb is None:
            return None

    ib = _INITIAL_BOPOMOFO.get(initial, '')
    return ib + fb + _TONE_MARK.get(tone, '')


def _is_valid_syllable(syl):
    """Cek validitas TANPA menghitung ulang bopomofo (dipakai saat
    segmentasi -- string kosong/bare 'i'/'u'/'ü' tanpa y/w di depan
    BUKAN suku kata pinyin yang sah, jadi ditolak eksplisit supaya
    segmentasi tidak salah potong)."""
    if not syl:
        return False
    plain, _ = _strip_tone(syl.lower().replace('v', 'ü'))
    if plain in ('i', 'u', 'ü'):
        return False  # pinyin asli selalu 'yi'/'wu'/'yu', bukan huruf lepas
    return syllable_to_bopomofo(syl) is not None


def _segment_concat(s, n, max_syl_len=6, _cache=None):
    """Backtracking: coba pecah string pinyin TANPA spasi jadi persis
    n suku kata yang semuanya valid. Dicoba dari potongan TERPANJANG
    dulu (maximal munch) supaya tidak salah potong suku kata panjang
    jadi 2 suku kata pendek yang kebetulan sama-sama 'valid'."""
    if _cache is None:
        _cache = {}
    key = (s, n)
    if key in _cache:
        return _cache[key]
    if n == 1:
        result = [s] if _is_valid_syllable(s) else None
        _cache[key] = result
        return result
    upper = min(len(s) - (n - 1), max_syl_len)  # sisakan >=1 char per suku kata sisanya
    for i in range(upper, 0, -1):
        head, tail = s[:i], s[i:]
        if _is_valid_syllable(head):
            rest = _segment_concat(tail, n - 1, max_syl_len, _cache)
            if rest is not None:
                result = [head] + rest
                _cache[key] = result
                return result
    _cache[key] = None
    return None


def pinyin_to_bopomofo(pinyin_full, n_syllables=None):
    """Konversi string pinyin ke bopomofo. Coba dulu pemisahan SPASI
    (kasus normal). Kalau gagal DAN n_syllables diketahui (= jumlah
    karakter hanzi kata itu), coba segmentasi otomatis dari string
    yang digabung tanpa spasi."""
    if not pinyin_full:
        return None
    # tanda kutip (') dipakai standar pinyin sebagai pemisah suku kata
    # sebelum suku kata berawalan vokal (mis. nǚ'ér, gān'érzi) -- perlakukan
    # sama seperti spasi
    pinyin_full = pinyin_full.replace("'", " ").replace("\u2019", " ")
    syllables = pinyin_full.strip().split()

    # kasus normal: sudah terpisah spasi, jumlah suku kata cocok jumlah hanzi
    if len(syllables) > 1 or (n_syllables in (None, 1)):
        results = []
        ok = True
        for syl in syllables:
            bpm = syllable_to_bopomofo(syl)
            if bpm is None:
                ok = False
                break
            results.append(bpm)
        if ok and results:
            return ' '.join(results)

    # fallback: pinyin digabung tanpa spasi -- segmentasi otomatis
    if n_syllables and n_syllables > 1:
        concat = pinyin_full.strip().replace(' ', '')
        segments = _segment_concat(concat, n_syllables)
        if segments:
            bpms = [syllable_to_bopomofo(s) for s in segments]
            if all(bpms):
                return ' '.join(bpms)

    return None


def out(lines, s=""):
    print(s)
    lines.append(s)


# ══════════════════════════════════════════════════════════════════
# LAPIS 1: bangun lookup per-karakter dari app_words.json yang sudah ada
# ══════════════════════════════════════════════════════════════════
def build_tier1_lookup(app_words):
    lookup = {}
    for w in app_words:
        simp = w.get("simplified") or w.get("id") or ""
        if len(simp) != 1:
            continue
        # kalau karakter ini sudah pernah masuk lookup, jangan ditimpa
        # (entri pertama yang ketemu dipakai -- biasanya entri HSK asli
        # lebih bisa dipercaya daripada entri hsk:null/cidict fallback)
        if simp in lookup:
            continue
        lookup[simp] = {
            "radical":        w.get("radical"),
            "radical_number": w.get("radical_number"),
            "stroke_count":   w.get("stroke_count"),
            "structure":      w.get("structure"),
            "components":     w.get("components") or [simp],
            "char_type":      w.get("char_type"),
            "bopomofo":       w.get("bopomofo"),
        }
    return lookup


# ══════════════════════════════════════════════════════════════════
# LAPIS 2: fallback dari dictionary.txt + hanzi_writer_data.json + kangxi
# ══════════════════════════════════════════════════════════════════
def parse_decomposition(decomp):
    """Ambil simbol IDC pertama (penentu structure) + sisa karakter
    (components), dari string seperti '⿰女子' atau '⿱⿱爫冖友'."""
    IDC_MAP = {
        "⿰": "left-right", "⿱": "top-bottom", "⿲": "left-mid-right",
        "⿳": "top-mid-bottom", "⿴": "enclosed-full", "⿵": "enclosed-top",
        "⿶": "enclosed-bottom", "⿷": "enclosed-left", "⿸": "enclosed-topleft",
        "⿹": "enclosed-topright", "⿺": "enclosed-botleft", "⿻": "overlapping",
    }
    if not decomp or decomp == "？" or decomp[0] not in IDC_MAP:
        return "single", []
    structure = IDC_MAP[decomp[0]]
    # sisa string setelah simbol IDC pertama = komponen (buang IDC lain
    # yang mungkin muncul untuk dekomposisi bersarang, ambil karakter non-IDC saja)
    components = [c for c in decomp[1:] if c not in IDC_MAP and c != "？"]
    return structure, components


def build_tier2_sources():
    dict_lookup = {}
    if DICT_TXT_PATH.exists():
        with open(DICT_TXT_PATH, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    obj = json.loads(line)
                except Exception:
                    continue
                ch = obj.get("character")
                if ch:
                    dict_lookup[ch] = obj

    writer_lookup = {}
    if WRITER_PATH.exists():
        writer_lookup = load_json(WRITER_PATH)

    # Lapis 2b: suplemen goresan untuk karakter yang tidak ada di
    # hanzi_writer_data.json lokal (3.034 karakter) -- diambil LANGSUNG
    # dari graphics.txt milik proyek Make Me a Hanzi (sumber resmi yang
    # sama dengan dictionary.txt anda), khusus untuk 58 karakter yang
    # sebelumnya bolong. Kalau file ini tidak ada, dilewati saja (tidak error).
    stroke_supplement = {}
    if STROKE_SUPPLEMENT_PATH.exists():
        stroke_supplement = load_json(STROKE_SUPPLEMENT_PATH)

    kangxi_num_to_char = {}
    kangxi_char_to_num = {}
    if KANGXI_PATH.exists():
        kangxi_num_to_char = load_json(KANGXI_PATH)
        kangxi_char_to_num = {v: int(k) for k, v in kangxi_num_to_char.items()}

    return dict_lookup, writer_lookup, kangxi_char_to_num, stroke_supplement


def resolve_radical_number(radical_raw, kangxi_char_to_num):
    if not radical_raw:
        return None
    if radical_raw in AMBIGUOUS_RADICALS:
        return None  # sengaja tidak ditebak -- lihat catatan AMBIGUOUS_RADICALS
    # coba langsung
    if radical_raw in kangxi_char_to_num:
        return kangxi_char_to_num[radical_raw]
    # coba lewat tabel padanan varian
    canonical = VARIANT_TO_KANGXI.get(radical_raw)
    if canonical and canonical in kangxi_char_to_num:
        return kangxi_char_to_num[canonical]
    return None


def tier2_char_info(char, dict_lookup, writer_lookup, kangxi_char_to_num, stroke_supplement=None):
    """Bangun info 1 karakter dari sumber Lapis 2. Return dict parsial --
    field yang tidak berhasil didapat akan None (biar ketahuan di laporan)."""
    stroke_supplement = stroke_supplement or {}
    info = {
        "radical": None, "radical_number": None, "stroke_count": None,
        "structure": None, "components": None, "char_type": None,
        "bopomofo": None,  # bopomofo TIDAK dicoba di Lapis 2 (perlu
                            # konversi pinyin->zhuyin yang berisiko salah;
                            # dibiarkan None, ditandai isi manual)
    }
    d = dict_lookup.get(char)
    if d:
        info["radical"] = d.get("radical")
        info["radical_number"] = resolve_radical_number(d.get("radical"), kangxi_char_to_num)
        structure, components = parse_decomposition(d.get("decomposition", ""))
        info["structure"] = structure
        info["components"] = components if components else [char]
        info["char_type"] = "compound" if structure != "single" else "single"

    w = writer_lookup.get(char)
    if w and isinstance(w, dict) and "strokes" in w:
        info["stroke_count"] = len(w["strokes"])
    elif char in stroke_supplement:
        # Lapis 2b: fallback ke suplemen dari graphics.txt (Make Me a Hanzi)
        info["stroke_count"] = stroke_supplement[char]

    return info


# ══════════════════════════════════════════════════════════════════
# ENRICHMENT 1 ENTRI (multi-karakter, ikuti aturan build_app_words.py)
# ══════════════════════════════════════════════════════════════════
def enrich_entry(entry, tier1, dict_lookup, writer_lookup, kangxi_char_to_num, stats, stroke_supplement=None):
    simp = entry.get("simplified", "")
    if not simp:
        return entry

    char_infos = []
    for ch in simp:
        if ch in tier1:
            char_infos.append(tier1[ch])
            stats["char_from_tier1"] += 1
        else:
            info = tier2_char_info(ch, dict_lookup, writer_lookup, kangxi_char_to_num, stroke_supplement)
            char_infos.append(info)
            stats["char_from_tier2"] += 1
            if info["stroke_count"] is None or info["radical"] is None:
                stats["chars_incomplete"].add(ch)

    first = char_infos[0]

    # stroke_count = SUM (kalau ada char yang None, total jadi None -- lebih
    # baik jujur "tidak lengkap" daripada angka yang salah)
    strokes = [c["stroke_count"] for c in char_infos]
    stroke_count = sum(strokes) if all(s is not None for s in strokes) else None

    # structure = dari karakter pertama
    structure = first["structure"] or "single"

    # components = union dedup dari semua karakter
    components = []
    for c in char_infos:
        for comp in (c["components"] or []):
            if comp not in components:
                components.append(comp)

    # char_type
    char_type = "compound" if len(simp) > 1 else (first["char_type"] or "single")

    # radical / radical_number dari karakter pertama
    radical = first["radical"]
    radical_number = first["radical_number"]

    # bopomofo = dihitung LANGSUNG dari field "pinyin" milik entri sendiri
    # (deterministik, tidak butuh lookup per-karakter sama sekali).
    # Fallback ke sambungan bopomofo per-karakter HANYA kalau field
    # "pinyin" entri kosong (seharusnya jarang terjadi).
    bopomofo = pinyin_to_bopomofo(entry.get("pinyin", ""), n_syllables=len(simp))
    if bopomofo is None:
        bopomofos = [c["bopomofo"] for c in char_infos]
        bopomofo = " ".join(bopomofos) if all(b for b in bopomofos) else None
        if bopomofo is not None:
            stats["bopomofo_from_char_fallback"] += 1
    else:
        stats["bopomofo_from_pinyin"] += 1

    entry["radical"] = radical
    entry["radical_number"] = radical_number
    entry["stroke_count"] = stroke_count
    entry["structure"] = structure
    entry["components"] = components if components else [simp]
    entry["char_type"] = char_type
    entry["bopomofo"] = bopomofo

    # tandai kalau ada field yang masih kosong -> perlu isi manual
    missing = [k for k in ["radical", "radical_number", "stroke_count", "bopomofo"] if entry.get(k) is None]
    if missing:
        entry["_missing_fields"] = missing
        stats["entries_incomplete"] += 1
    else:
        stats["entries_complete"] += 1

    return entry


def self_test_bopomofo(report):
    """Validasi cepat fungsi pinyin_to_bopomofo terhadap 2 contoh yang
    SUDAH DIKETAHUI BENAR dari app_words.json anda sendiri (好, 无法).
    Kalau salah satu gagal, laporan akan bilang jelas -- JANGAN lanjut
    percaya hasil bopomofo di file lain kalau self-test ini gagal."""
    out(report, "SELF-TEST konversi pinyin -> bopomofo (validasi terhadap data yang sudah pasti benar):")
    tests = [
        ("hǎo", "ㄏㄠˇ", "好", 1),
        ("wú fǎ", "ㄨˊ ㄈㄚˇ", "无法", 2),
        ("wàizǔmǔ", "ㄨㄞˋ ㄗㄨˇ ㄇㄨˇ", "外祖母 (tanpa spasi)", 3),
        ("nǚ", "ㄋㄩˇ", "女 (uji n+ü)", 1),
        ("lǜshī", "ㄌㄩˋ ㄕ", "律师 (uji l+ü, tanpa spasi)", 2),
        ("nǚ'ér", "ㄋㄩˇ ㄦˊ", "女儿 (uji tanda kutip pemisah)", 2),
    ]
    all_ok = True
    for pinyin, expected, word, n in tests:
        got = pinyin_to_bopomofo(pinyin, n_syllables=n)
        ok = (got == expected)
        all_ok = all_ok and ok
        mark = "✓" if ok else "✗ GAGAL"
        out(report, f"  {mark}  {word} ({pinyin}) -> dihasilkan: {got!r}  (harusnya: {expected!r})")
    if not all_ok:
        out(report, "  ⚠ SELF-TEST GAGAL -- ada bug di fungsi konversi. STOP, jangan pakai hasil")
        out(report, "    bopomofo di file *_enriched.json sebelum ini diperbaiki. Laporkan ke Claude.")
    out(report, "")
    return all_ok


def main():
    report = []
    out(report, "ENRICHMENT LEKSIKON KHUSUS — TAHAP 2")
    out(report, "=" * 70)

    if not self_test_bopomofo(report):
        Path(REPORT_PATH).write_text("\n".join(report), encoding="utf-8")
        return

    if not APP_WORDS_PATH.exists():
        out(report, f"✗ {APP_WORDS_PATH} tidak ditemukan. Jalankan dari folder C:\\mandarin_app.")
        Path(REPORT_PATH).write_text("\n".join(report), encoding="utf-8")
        return

    out(report, f"Memuat {APP_WORDS_PATH} ...")
    app_words = load_json(APP_WORDS_PATH)
    out(report, f"  ✓ {len(app_words):,} entri dimuat")

    tier1 = build_tier1_lookup(app_words)
    out(report, f"  ✓ Lapis 1 (lookup karakter dari app_words.json): {len(tier1):,} karakter unik")

    dict_lookup, writer_lookup, kangxi_char_to_num, stroke_supplement = build_tier2_sources()
    out(report, f"  ✓ Lapis 2 siap -- dictionary.txt: {len(dict_lookup):,} karakter | "
                f"hanzi_writer_data.json: {len(writer_lookup):,} karakter | "
                f"kangxi map: {len(kangxi_char_to_num):,} radikal | "
                f"suplemen goresan: {len(stroke_supplement):,} karakter")
    if not KANGXI_PATH.exists():
        out(report, f"  ⚠ {KANGXI_PATH} tidak ditemukan di folder ini -- radical_number Lapis 2 "
                    f"tidak akan bisa diisi. Copy file itu dari C:\\mandarin_kamus\\database\\ dulu.")
    if not STROKE_SUPPLEMENT_PATH.exists():
        out(report, f"  ⚠ {STROKE_SUPPLEMENT_PATH} tidak ditemukan -- 58 karakter langka masih akan")
        out(report, f"    gagal di stroke_count. Copy file itu ke folder ini dulu.")

    STAGING_DIR.mkdir(exist_ok=True)

    grand_stats = defaultdict(int)
    grand_stats["chars_incomplete"] = set()

    for cat in CATEGORY_FILES:
        in_path = STAGING_DIR / f"{cat}.json"
        out(report, f"\n{'─'*70}")
        out(report, f"[{cat}]")
        if not in_path.exists():
            out(report, f"  ⚠ {in_path} tidak ditemukan, dilewati.")
            continue

        entries = load_json(in_path)
        stats = {
            "char_from_tier1": 0, "char_from_tier2": 0,
            "entries_complete": 0, "entries_incomplete": 0,
            "chars_incomplete": set(),
            "bopomofo_from_pinyin": 0, "bopomofo_from_char_fallback": 0,
        }

        for e in entries:
            enrich_entry(e, tier1, dict_lookup, writer_lookup, kangxi_char_to_num, stats, stroke_supplement)

        out_path = STAGING_DIR / f"{cat}_enriched.json"
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(entries, f, ensure_ascii=False, indent=1)

        total = len(entries)
        out(report, f"  Total entri: {total}")
        out(report, f"  Lengkap (semua field struktural terisi): {stats['entries_complete']} "
                    f"({stats['entries_complete']/total*100:.0f}%)")
        out(report, f"  Belum lengkap (perlu isi manual):        {stats['entries_incomplete']}")
        out(report, f"  Bopomofo dihitung dari pinyin entri:     {stats['bopomofo_from_pinyin']}/{total}")
        if stats["chars_incomplete"]:
            out(report, f"  Karakter yang bermasalah di Lapis 2:     "
                        f"{', '.join(sorted(stats['chars_incomplete']))}")
        out(report, f"  -> disimpan ke {out_path}")

        for k in ["char_from_tier1", "char_from_tier2", "entries_complete", "entries_incomplete"]:
            grand_stats[k] += stats[k]
        grand_stats["chars_incomplete"] |= stats["chars_incomplete"]

    out(report, f"\n{'='*70}")
    out(report, "RINGKASAN TOTAL")
    out(report, f"  Karakter diselesaikan via Lapis 1 (app_words.json): {grand_stats['char_from_tier1']:,}")
    out(report, f"  Karakter diselesaikan via Lapis 2 (dictionary.txt dkk): {grand_stats['char_from_tier2']:,}")
    out(report, f"  Entri lengkap total   : {grand_stats['entries_complete']:,}")
    out(report, f"  Entri belum lengkap   : {grand_stats['entries_incomplete']:,}")
    if grand_stats["chars_incomplete"]:
        out(report, f"\n  SEMUA karakter yang masih bermasalah (butuh isi manual):")
        out(report, f"    {', '.join(sorted(grand_stats['chars_incomplete']))}")

    Path(REPORT_PATH).write_text("\n".join(report), encoding="utf-8")
    print(f"\n✓ Laporan lengkap disimpan ke {REPORT_PATH.resolve()}")
    print("  File *_enriched.json di staging/ SIAP untuk tahap sample-check")
    print("  sebelum digabung ke app_words.json (belum di-apply otomatis).")


if __name__ == "__main__":
    main()

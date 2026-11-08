"""
generate_wordbuilder_pools.py
═══════════════════════════════════════════════════════════════
Generate data/wb_pools.json dari data/app_words.json untuk
Word Builder (Mandarin Interaktif).

Setiap pool berisi list kata flat, masing-masing kata ditandai
field "hsk" -- filter per-level (checkbox HSK1..7) dilakukan di
sisi client (JS), bukan di sini. Skrip ini hanya membatasi
JUMLAH kata per level per pool (MAX_PER_LEVEL) supaya dropdown
tidak kebanjiran opsi, dan mengurutkan tiap level berdasarkan
frequency (semakin kecil angka = semakin sering dipakai).

Jalankan dari folder root proyek (C:\\mandarin_app):
    python generate_wordbuilder_pools.py

Output: data/wb_pools.json
═══════════════════════════════════════════════════════════════
"""

import json
import sys
from collections import defaultdict

INPUT_PATH     = 'data/app_words.json'
OUTPUT_PATH    = 'data/wb_pools.json'
OVERRIDES_PATH = 'wb_overrides.json'

MAX_PER_LEVEL = 15          # cap kata per level HSK per pool
VALID_HSK_LEVELS = [1, 2, 3, 4, 5, 6, 7]   # HSKNone dibuang


def as_list(val):
    """Normalisasi field yang bisa berupa None, string tunggal, atau list."""
    if val is None:
        return []
    if isinstance(val, list):
        return val
    return [val]


def as_hsk_int(val):
    """Normalisasi field hsk yang bisa berupa int, string angka, string 'HSK1',
       float, atau None -> int atau None."""
    if val is None:
        return None
    if isinstance(val, bool):
        return None
    if isinstance(val, int):
        return val
    if isinstance(val, float):
        return int(val)
    if isinstance(val, str):
        digits = ''.join(ch for ch in val if ch.isdigit())
        return int(digits) if digits else None
    return None


def load_words():
    try:
        with open(INPUT_PATH, encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"✗ Tidak ditemukan: {INPUT_PATH}")
        print("  Jalankan skrip ini dari folder root proyek (C:\\mandarin_app).")
        sys.exit(1)


def load_overrides():
    try:
        with open(OVERRIDES_PATH, encoding='utf-8') as f:
            data = json.load(f)
            return data.get('corrections', {}), set(data.get('drops', []))
    except FileNotFoundError:
        print(f"⚠ {OVERRIDES_PATH} tidak ditemukan -- lanjut TANPA koreksi manual.")
        print("  (entri dengan bacaan marga/langka mungkin masih ada di hasil)")
        return {}, set()


def apply_overrides(pool_name, entries, corrections, drops):
    """Terapkan koreksi py/id dan buang entri yang ditandai drop, untuk 1 pool."""
    result = []
    for e in entries:
        key = f"{pool_name}:{e['cn']}"
        if key in drops:
            continue
        if key in corrections:
            fix = corrections[key]
            e = dict(e)  # jangan mutate original
            e['py'] = fix['py']
            e['id'] = fix['id']
        result.append(e)
    return result


def is_proper_noun_pinyin(py):
    """True kalau pinyin diawali huruf kapital (indikasi bacaan marga/nama)."""
    return bool(py) and py[0].isupper()


def primary_meaning(word):
    """Ambil arti yang paling berguna dari meanings_id, bukan sekadar index [0].

    Dua masalah kualitas data yang ditangani di sini:
    1. Sebagian entri meanings_id[0] berupa catatan kamus "varian dari X[pinyin]"
       (self-referential, tidak berguna untuk pemula) -> dilewati, cari gloss
       berikutnya yang bukan catatan varian.
    2. Sebagian gloss diawali "(bentuk terikat) " (bound-form note) -> prefix
       ini dibuang, sisanya tetap dipakai (biasanya sudah berupa arti yang jelas).
    """
    meanings = word.get('meanings_id') or []
    if isinstance(meanings, str):
        meanings = [meanings]
    if not meanings:
        return ''

    def is_variant_note(m):
        low = m.lower()
        return low.startswith('varian dari') or low.startswith('varian lama dari')

    def strip_bound_form(m):
        prefix = '(bentuk terikat)'
        if m.lower().startswith(prefix):
            return m[len(prefix):].strip()
        return m

    # Cari gloss pertama yang BUKAN catatan varian
    for m in meanings:
        if not is_variant_note(m):
            return strip_bound_form(m)

    # Semua gloss adalah catatan varian (buntu) -> pakai yang pertama apa adanya
    return meanings[0]


def make_entry(word):
    return {
        'cn':  word.get('simplified', ''),
        'py':  word.get('pinyin', ''),
        'id':  primary_meaning(word),
        'hsk': as_hsk_int(word.get('hsk')),
        'freq': word.get('frequency') if word.get('frequency') is not None else 999999,
    }


def cap_per_level(entries):
    """Kelompokkan per level HSK, urutkan by frequency, cap MAX_PER_LEVEL,
       lalu gabung kembali jadi satu list flat."""
    by_level = defaultdict(list)
    for e in entries:
        hsk = e['hsk']
        if hsk not in VALID_HSK_LEVELS:
            continue  # buang kata tanpa level HSK yang valid
        by_level[hsk].append(e)

    result = []
    for lvl in VALID_HSK_LEVELS:
        pool = sorted(by_level[lvl], key=lambda e: e['freq'])[:MAX_PER_LEVEL]
        result.extend(pool)
    return result


def strip_internal_fields(entries):
    """Buang field 'freq' (hanya dipakai internal utk sorting), rapikan hsk."""
    out = []
    for e in entries:
        out.append({'cn': e['cn'], 'py': e['py'], 'id': e['id'], 'hsk': e['hsk']})
    return out


def finalize_pool(pool_name, raw_words, corrections, drops, cap=MAX_PER_LEVEL, allow_proper_cn=None):
    """
    Pipeline lengkap 1 pool: buat entry -> cap per level (atau tidak) ->
    terapkan koreksi/drop manual -> buang sisa entri berpinyin kapital
    yang belum tercover override (indikasi bacaan marga/nama yang lolos).
    """
    allow_proper_cn = allow_proper_cn or set()

    entries = [make_entry(w) for w in raw_words]
    if cap is not None:
        entries = cap_per_level(entries)
    else:
        entries = [e for e in entries if e['hsk'] in VALID_HSK_LEVELS]
        entries.sort(key=lambda e: e['freq'])
    entries = strip_internal_fields(entries)

    entries = apply_overrides(pool_name, entries, corrections, drops)

    # Safety net: buang sisa entri kapital yang TIDAK ada di corrections/drops
    # (berarti belum sempat ditinjau manual) -- kecuali cn-nya di-allow (mis. 中国).
    cleaned = []
    dropped_unreviewed = []
    for e in entries:
        if is_proper_noun_pinyin(e['py']) and e['cn'] not in allow_proper_cn:
            dropped_unreviewed.append(e)
            continue
        cleaned.append(e)

    if dropped_unreviewed:
        print(f"  [auto-drop] {pool_name}: {len(dropped_unreviewed)} entri kapital belum "
              f"di-review dibuang -> {[e['cn'] for e in dropped_unreviewed]}")

    return cleaned


def main():
    words = load_words()
    print(f"Total kata dimuat: {len(words)}")
    corrections, drops = load_overrides()
    print(f"Override dimuat: {len(corrections)} koreksi, {len(drops)} drop manual\n")

    used_ids = set()  # cegah kata yang sama dobel-masuk ke pool lain (kecuali identitas/subyek yg boleh overlap)

    def id_of(w):
        return w.get('id') or w.get('simplified')

    # ── SATUAN (量词 / classifier) ──────────────────────────────
    satuan_raw = [w for w in words if 'q' in as_list(w.get('pos'))]
    satuan = finalize_pool('satuan', satuan_raw, corrections, drops)
    for w in satuan_raw:
        used_ids.add(id_of(w))

    # ── ANGKA (kata bilangan) — tidak dibatasi cap, datanya sedikit ──
    angka_raw = [w for w in words if 'm' in as_list(w.get('pos'))]
    angka = finalize_pool('angka', angka_raw, corrections, drops, cap=None)
    for w in angka_raw:
        used_ids.add(id_of(w))

    # ── WAKTU (kata waktu) ────────────────────────────────────────
    waktu_raw = [
        w for w in words
        if 't' in as_list(w.get('pos'))
        or any(t in ('waktu', 'hari_tanggal') for t in as_list(w.get('themes')))
    ]
    waktu = finalize_pool('waktu', waktu_raw, corrections, drops)
    for w in waktu_raw:
        used_ids.add(id_of(w))

    # ── TEMPAT (kata tempat / lokasi) ─────────────────────────────
    # allow_proper: nama negara/wilayah SAH punya pinyin kapital (mis. 中国 Zhōngguó)
    tempat_raw = [
        w for w in words
        if 'f' in as_list(w.get('pos'))
        or 'arah_lokasi' in as_list(w.get('themes'))
        or 'negara_budaya' in as_list(w.get('themes'))
    ]
    tempat_allow_proper = {
        w.get('simplified') for w in tempat_raw
        if 'negara_budaya' in as_list(w.get('themes'))
    }
    tempat = finalize_pool('tempat', tempat_raw, corrections, drops, allow_proper_cn=tempat_allow_proper)
    for w in tempat_raw:
        used_ids.add(id_of(w))

    # ── IDENTITAS (profesi, fokus lebih sempit) ────────────────────
    identitas_raw = [
        w for w in words
        if ('n' in as_list(w.get('pos')) or 'vn' in as_list(w.get('pos')))
        and 'pekerjaan' in as_list(w.get('themes'))
    ]
    identitas = finalize_pool('identitas', identitas_raw, corrections, drops)
    # catatan: id kata identitas TIDAK ditambahkan ke used_ids -- boleh
    # muncul juga di 'subyek' (orang) karena dua pool ini memang dekat maknanya

    # ── SUBYEK (pronomina + kata orang: keluarga/pekerjaan) ────────
    subyek_raw = [
        w for w in words
        if 'r' in as_list(w.get('pos'))
        or (
            ('n' in as_list(w.get('pos')) or 'vn' in as_list(w.get('pos')))
            and any(t in ('keluarga', 'pekerjaan') for t in as_list(w.get('themes')))
        )
    ]
    subyek = finalize_pool('subyek', subyek_raw, corrections, drops)
    for w in subyek_raw:
        used_ids.add(id_of(w))

    # ── KATA_KERJA ───────────────────────────────────────────────
    kerja_raw = [
        w for w in words
        if 'v' in as_list(w.get('pos')) or 'vn' in as_list(w.get('pos'))
    ]
    kata_kerja = finalize_pool('kata_kerja', kerja_raw, corrections, drops)
    for w in kerja_raw:
        used_ids.add(id_of(w))

    # ── KATA_SIFAT ───────────────────────────────────────────────
    sifat_raw = [w for w in words if 'a' in as_list(w.get('pos'))]
    kata_sifat = finalize_pool('kata_sifat', sifat_raw, corrections, drops)
    for w in sifat_raw:
        used_ids.add(id_of(w))

    # ── OBJEK_UMUM (kata benda umum, exclude yg sudah dipakai pool lain) ──
    objek_raw = [
        w for w in words
        if 'n' in as_list(w.get('pos'))
        and id_of(w) not in used_ids
    ]
    objek_umum = finalize_pool('objek_umum', objek_raw, corrections, drops)

    pools = {
        'subyek':     subyek,
        'kata_kerja': kata_kerja,
        'objek_umum': objek_umum,
        'kata_sifat': kata_sifat,
        'tempat':     tempat,
        'waktu':      waktu,
        'angka':      angka,
        'satuan':     satuan,
        'identitas':  identitas,
    }

    with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
        json.dump(pools, f, ensure_ascii=False, indent=2)

    print(f"\n✓ Selesai. Output: {OUTPUT_PATH}\n")
    print("Ringkasan jumlah kata per pool:")
    for name, entries in pools.items():
        by_level = defaultdict(int)
        for e in entries:
            by_level[e['hsk']] += 1
        level_str = ', '.join(f"HSK{lv}:{by_level[lv]}" for lv in VALID_HSK_LEVELS if by_level[lv])
        print(f"  {name:12s}: total {len(entries):4d}  ({level_str})")


if __name__ == '__main__':
    main()

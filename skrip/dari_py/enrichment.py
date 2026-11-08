#!/usr/bin/env python3
# enrichment.py
# Jalankan: python enrichment.py
# Dari folder mana saja — path sudah hardcode di bawah

import json, os, re, unicodedata
from collections import defaultdict

# ── PATH ────────────────────────────────────────────────────
DATA_DIR      = r"C:\mandarin_app\data"
KAMUS_DIR     = r"C:\mandarin_kamus"

IN_APP_WORDS  = os.path.join(DATA_DIR,  "app_words.json")
IN_SYN_ANT    = os.path.join(KAMUS_DIR, "output", "synonym_antonym.json")
IN_CIDICT     = os.path.join(KAMUS_DIR, "output", "cidict_full.json")

OUT_APP_WORDS = os.path.join(DATA_DIR,  "app_words.json")          # overwrite
OUT_APP_BAK   = os.path.join(DATA_DIR,  "app_words_backup.json")   # backup dulu
OUT_CIDICT    = os.path.join(DATA_DIR,  "cidict_index.json")       # ganti format
OUT_IDX_RAD   = os.path.join(DATA_DIR,  "index_radical.json")      # baru
OUT_IDX_STR   = os.path.join(DATA_DIR,  "index_stroke.json")       # baru
OUT_IDX_THEME = os.path.join(DATA_DIR,  "index_theme.json")        # baru
OUT_REPORT    = os.path.join(DATA_DIR,  "LAPORAN_ENRICHMENT.txt")

lines = []
def log(s=""):
    print(s)
    lines.append(str(s))

def sep(title=""):
    log("\n" + "═"*60)
    if title: log(f"  {title}"); log("═"*60)

def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def save_json(path, obj, indent=None):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=indent)

# ════════════════════════════════════════════════════════════
# KONVERTER PINYIN ANGKA → DIAKRITIK
# ════════════════════════════════════════════════════════════

TONE_MAP = {
    'a': ['ā','á','ǎ','à','a'],
    'e': ['ē','é','ě','è','e'],
    'i': ['ī','í','ǐ','ì','i'],
    'o': ['ō','ó','ǒ','ò','o'],
    'u': ['ū','ú','ǔ','ù','u'],
    'ü': ['ǖ','ǘ','ǚ','ǜ','ü'],
    'v': ['ǖ','ǘ','ǚ','ǜ','ü'],  # v sering dipakai sebagai ü
}

def convert_syllable(syl):
    """Konversi satu suku kata pinyin angka ke diakritik. Contoh: 'ma1' → 'mā'"""
    syl = syl.strip().lower()
    if not syl:
        return syl

    # Ekstrak angka nada di akhir
    tone = 5  # nada netral default
    if syl and syl[-1].isdigit():
        tone = int(syl[-1])
        syl  = syl[:-1]

    if tone == 5 or tone == 0:
        # Nada netral: tidak ada tanda, ganti v → ü saja
        return syl.replace('v', 'ü').replace('u:', 'ü')

    # Aturan penempatan tanda nada:
    # 1. Jika ada 'a' atau 'e', taruh di sana
    # 2. Jika ada 'ou', taruh di 'o'
    # 3. Taruh di vokal terakhir

    syl = syl.replace('v', 'ü').replace('u:', 'ü')

    def place(s, vowel, t):
        idx = s.find(vowel)
        if idx == -1:
            return s, False
        replacement = TONE_MAP[vowel][t - 1] if vowel in TONE_MAP else vowel
        return s[:idx] + replacement + s[idx+1:], True

    for priority in ['a', 'e']:
        result, ok = place(syl, priority, tone)
        if ok:
            return result

    if 'ou' in syl:
        result, ok = place(syl, 'o', tone)
        if ok:
            return result

    # Vokal terakhir
    for i in range(len(syl)-1, -1, -1):
        if syl[i] in TONE_MAP:
            replacement = TONE_MAP[syl[i]][tone - 1]
            return syl[:i] + replacement + syl[i+1:]

    return syl

def pinyin_numeric_to_diacritic(pinyin_raw):
    """Konversi string pinyin angka multi-suku ke diakritik. 'ni3 hao3' → 'nǐ hǎo'"""
    if not pinyin_raw:
        return ''
    syllables = pinyin_raw.strip().split()
    return ' '.join(convert_syllable(s) for s in syllables)

# ════════════════════════════════════════════════════════════
# LANGKAH 1: BACKUP app_words.json
# ════════════════════════════════════════════════════════════
sep("LANGKAH 1: Backup app_words.json")

log(f"  Membaca {IN_APP_WORDS} ...")
app_words = load_json(IN_APP_WORDS)
log(f"  ✓ {len(app_words):,} kata dimuat")

log(f"  Menyimpan backup ke {OUT_APP_BAK} ...")
save_json(OUT_APP_BAK, app_words)
log(f"  ✓ Backup selesai")

# ════════════════════════════════════════════════════════════
# LANGKAH 2: MERGE SYNONYMS & ANTONYMS
# ════════════════════════════════════════════════════════════
sep("LANGKAH 2: Merge synonyms & antonyms")

log(f"  Membaca {IN_SYN_ANT} ...")
syn_ant = load_json(IN_SYN_ANT)

# Buat lookup: kata → list sinonim (hanya kata hanzi-nya)
syn_lookup = {}
for word, data in syn_ant.get('synonyms', {}).items():
    syns = [s['word'] for s in data.get('synonyms', []) if s.get('word')]
    if syns:
        syn_lookup[word] = syns

ant_lookup = {}
for word, data in syn_ant.get('antonyms', {}).items():
    ants = [a['word'] for a in data.get('antonyms', []) if a.get('word')]
    if ants:
        ant_lookup[word] = ants

log(f"  Sinonim tersedia : {len(syn_lookup):,} kata")
log(f"  Antonim tersedia : {len(ant_lookup):,} kata")

# Merge ke app_words
merged_syn = 0
merged_ant = 0
for w in app_words:
    key = w.get('simplified') or w.get('id', '')
    if key in syn_lookup:
        w['synonyms'] = syn_lookup[key]
        merged_syn += 1
    elif not w.get('synonyms'):
        w['synonyms'] = []

    if key in ant_lookup:
        w['antonyms'] = ant_lookup[key]
        merged_ant += 1
    elif not w.get('antonyms'):
        w['antonyms'] = []

log(f"  ✓ Kata mendapat sinonim : {merged_syn:,}")
log(f"  ✓ Kata mendapat antonim : {merged_ant:,}")

# ════════════════════════════════════════════════════════════
# LANGKAH 3: SIMPAN app_words.json YANG SUDAH DIPERKAYA
# ════════════════════════════════════════════════════════════
sep("LANGKAH 3: Simpan app_words.json")

log(f"  Menyimpan ke {OUT_APP_WORDS} ...")
save_json(OUT_APP_WORDS, app_words)
log(f"  ✓ app_words.json disimpan ({len(app_words):,} kata)")

# ════════════════════════════════════════════════════════════
# LANGKAH 4: KONVERSI cidict_full.json → cidict_index.json
# Format baru: array of objects dengan fields:
#   id, simplified, pinyin, pinyin_numeric, meanings_id
# ════════════════════════════════════════════════════════════
sep("LANGKAH 4: Konversi cidict_full.json → cidict_index.json")

log(f"  Membaca {IN_CIDICT} ...")
cidict_full = load_json(IN_CIDICT)
log(f"  ✓ {len(cidict_full):,} entri cidict dimuat")

# Buat set kata HSK untuk menandai mana yang sudah ada
hsk_set = set()
for w in app_words:
    hsk_set.add(w.get('simplified', ''))
    hsk_set.add(w.get('traditional', ''))
hsk_set.discard('')

log(f"  Set kata HSK : {len(hsk_set):,} entri")
log(f"  Mengkonversi pinyin_raw → diakritik ...")

cidict_new = []
skipped    = 0
converted  = 0

for item in cidict_full:
    simp = item.get('simplified', '') or ''
    trad = item.get('traditional', '') or ''
    pinyin_raw  = item.get('pinyin_raw', '') or ''
    meanings_id = item.get('meanings_id', []) or []

    if not simp:
        skipped += 1
        continue

    # Konversi pinyin
    pinyin_diac = pinyin_numeric_to_diacritic(pinyin_raw)
    # Simpan juga versi numeric (hapus spasi di tengah tiap suku kata)
    pinyin_num  = pinyin_raw.strip()

    entry = {
        'id':            simp,
        'simplified':    simp,
        'traditional':   trad if trad != simp else simp,
        'pinyin':        pinyin_diac,
        'pinyin_numeric': pinyin_num,
        'meanings_id':   meanings_id,
        'in_hsk':        simp in hsk_set or trad in hsk_set,
    }
    cidict_new.append(entry)
    converted += 1

log(f"  ✓ Konversi selesai: {converted:,} entri, {skipped:,} dilewati")

# Verifikasi sampel konversi pinyin
log(f"\n  Sampel konversi pinyin (5 entri):")
for item in cidict_new[:5]:
    log(f"    {item['simplified']:<8} {item.get('pinyin_numeric',''):<20} → {item['pinyin']}")

log(f"\n  Menyimpan ke {OUT_CIDICT} ...")
save_json(OUT_CIDICT, cidict_new)

size_mb = os.path.getsize(OUT_CIDICT) / 1024 / 1024
log(f"  ✓ cidict_index.json disimpan ({converted:,} entri, {size_mb:.1f} MB)")

# ════════════════════════════════════════════════════════════
# LANGKAH 5: BUAT INDEX RADIKAL (hanya kata HSK)
# Format: { "氵": ["水", "海", "河", ...], ... }
# ════════════════════════════════════════════════════════════
sep("LANGKAH 5: Buat index_radical.json (HSK only)")

idx_radical = defaultdict(list)
for w in app_words:
    rad  = w.get('radical', '')
    simp = w.get('simplified', '')
    if rad and simp:
        idx_radical[rad].append(simp)

# Sort tiap list berdasarkan frekuensi (field frequency, ascending = lebih umum)
freq_map = {w.get('simplified',''): w.get('frequency', 99999) for w in app_words}

for rad in idx_radical:
    idx_radical[rad].sort(key=lambda x: freq_map.get(x, 99999))

log(f"  Jumlah radikal : {len(idx_radical)}")
log(f"  Top 10 radikal terbanyak:")
sorted_rad = sorted(idx_radical.items(), key=lambda x: -len(x[1]))
for rad, words in sorted_rad[:10]:
    log(f"    {rad}  {len(words):>4} kata  contoh: {words[:5]}")

save_json(OUT_IDX_RAD, dict(idx_radical))
log(f"  ✓ index_radical.json disimpan")

# ════════════════════════════════════════════════════════════
# LANGKAH 6: BUAT INDEX GORESAN (hanya kata HSK)
# Format: { "8": ["的", "为", ...], "12": [...], ... }
# ════════════════════════════════════════════════════════════
sep("LANGKAH 6: Buat index_stroke.json (HSK only)")

idx_stroke = defaultdict(list)
for w in app_words:
    stroke = w.get('stroke_count')
    simp   = w.get('simplified', '')
    if stroke is not None and simp:
        idx_stroke[str(stroke)].append(simp)

for s in idx_stroke:
    idx_stroke[s].sort(key=lambda x: freq_map.get(x, 99999))

log(f"  Jumlah goresan unik : {len(idx_stroke)}")
log(f"  Range  : {min(int(k) for k in idx_stroke)} – {max(int(k) for k in idx_stroke)}")
sorted_str = sorted(idx_stroke.items(), key=lambda x: int(x[0]))
log(f"  Distribusi (5 goresan pertama):")
for s, words in sorted_str[:5]:
    log(f"    {s:>3} goresan  {len(words):>4} kata  contoh: {words[:5]}")

save_json(OUT_IDX_STR, dict(idx_stroke))
log(f"  ✓ index_stroke.json disimpan")

# ════════════════════════════════════════════════════════════
# LANGKAH 7: BUAT INDEX TEMA (hanya kata HSK)
# Format: { "warna": ["红","橙","黄",...], ... }
# ════════════════════════════════════════════════════════════
sep("LANGKAH 7: Buat index_theme.json (HSK only)")

idx_theme = defaultdict(list)
for w in app_words:
    themes = w.get('themes', []) or []
    simp   = w.get('simplified', '')
    if not simp:
        continue
    if isinstance(themes, list):
        for t in themes:
            if t:
                idx_theme[t].append(simp)
    elif themes:
        idx_theme[str(themes)].append(simp)

for t in idx_theme:
    idx_theme[t].sort(key=lambda x: freq_map.get(x, 99999))

log(f"  Jumlah tema : {len(idx_theme)}")
log(f"  Daftar tema:")
for tema, words in sorted(idx_theme.items(), key=lambda x: -len(x[1])):
    log(f"    {tema:<30} {len(words):>5} kata  contoh: {words[:4]}")

save_json(OUT_IDX_THEME, dict(idx_theme))
log(f"  ✓ index_theme.json disimpan")

# ════════════════════════════════════════════════════════════
# RINGKASAN
# ════════════════════════════════════════════════════════════
sep("RINGKASAN")

files = [OUT_APP_WORDS, OUT_CIDICT, OUT_IDX_RAD, OUT_IDX_STR, OUT_IDX_THEME]
for f in files:
    if os.path.exists(f):
        sz = os.path.getsize(f) / 1024 / 1024
        log(f"  ✓ {os.path.basename(f):<30} {sz:.1f} MB")

log(f"""
  Langkah selanjutnya:
  1. Salin file-file di atas ke folder C:\\mandarin_app\\data\\
  2. app_words.json   — sudah di-overwrite (backup: app_words_backup.json)
  3. cidict_index.json — format baru (array, bukan dict)
  4. index_radical.json, index_stroke.json, index_theme.json — file baru
""")

# Simpan laporan
with open(OUT_REPORT, "w", encoding="utf-8") as f:
    f.write("\n".join(lines))

log(f"  Laporan: {OUT_REPORT}")
print("\n✅ Enrichment selesai!")

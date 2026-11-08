# -*- coding: utf-8 -*-
"""
complete_theme_json.py — Mandarin Interaktif
===============================================
Lengkapi file JSON tema MENTAH (hasil AI lain, format {theme, words:[{hanzi,
pinyin,translation}]}) jadi entri app_words.json LENGKAP (radikal, goresan,
struktur, komponen, bopomofo, traditional), lalu gabungkan ke app_words.json
+ index_theme.json lokal رسلان. 100% OFFLINE -- semua data referensi dibaca
dari file lokal di C:\\mandarin_app\\data\\.

CARA PAKAI:
  1. Taruh skrip ini di C:\\mandarin_app (sejajar dgn folder data/).
  2. Simpan JSON mentah dari AI lain, mis. sebagai raw_keluarga.json:
       {
         "theme": "Keluarga",
         "words": [
           {"hanzi": "爸爸", "pinyin": "bà ba", "translation": "ayah"},
           ...
         ]
       }
  3. Jalankan:
       python complete_theme_json.py raw_keluarga.json
  4. Skrip akan:
       - Cek tiap kata: sudah ada di app_words.json? -> tinggal ditag tema baru
       - Belum ada? -> bangun entri lengkap (radikal/goresan/struktur/bopomofo
         dihitung dari data/dictionary.txt + data/hanzi_writer_data.json,
         arti Indonesia dari data/cidict_index.json kalau ketemu, kalau
         tidak pakai field "translation" dari JSON mentah)
       - app_words.json & index_theme.json di C:\\mandarin_app\\data\\
         DITULIS LANGSUNG (in-place). Backup otomatis dibuat dulu
         (app_words.json.bak_TIMESTAMP) sebelum menulis.
       - Laporan lengkap dicetak ke layar + disimpan sbg
         complete_theme_json_report_TIMESTAMP.txt

Aman dijalankan berkali-kali untuk tema berbeda -- kata yang sudah ada
tidak akan diduplikasi, cuma ditambah tag tema barunya.
"""
import json
import re
import sys
import shutil
import unicodedata
from pathlib import Path
from datetime import datetime

# ── Konfigurasi path (sesuaikan kalau struktur folder رسلان beda) ──
DATA_DIR = Path("data")
APP_WORDS_PATH   = DATA_DIR / "app_words.json"
INDEX_THEME_PATH = DATA_DIR / "index_theme.json"
CIDICT_PATH      = DATA_DIR / "cidict_index.json"
MMH_DICT_PATH    = DATA_DIR / "dictionary.txt"           # format Make Me a Hanzi
STROKES_PATH     = DATA_DIR / "hanzi_writer_data.json"   # {char: {"strokes":[...]}}


# ═══════════════════════════════════════════════════════════════
# BAGIAN 1 — Konverter pinyin (divalidasi thd 1000 sampel data resmi,
# akurasi 99.7%, sesi Claude sebelumnya). Jangan diubah tanpa validasi ulang.
# ═══════════════════════════════════════════════════════════════

TONE_MARKS = {
    'ā':('a',1),'á':('a',2),'ǎ':('a',3),'à':('a',4),
    'ē':('e',1),'é':('e',2),'ě':('e',3),'è':('e',4),
    'ī':('i',1),'í':('i',2),'ǐ':('i',3),'ì':('i',4),
    'ō':('o',1),'ó':('o',2),'ǒ':('o',3),'ò':('o',4),
    'ū':('u',1),'ú':('u',2),'ǔ':('u',3),'ù':('u',4),
    'ǖ':('v',1),'ǘ':('v',2),'ǚ':('v',3),'ǜ':('v',4),
    'ü':('v',0),'ń':('n',2),'ň':('n',3),'ǹ':('n',4),
}

def syllable_to_numeric(syl):
    tone = 5
    out = []
    for ch in syl:
        low = ch.lower()
        if low in TONE_MARKS:
            base, t = TONE_MARKS[low]
            if t != 0:
                tone = t
            out.append(base.upper() if ch.isupper() else base)
        else:
            out.append(ch)
    return ''.join(out) + (str(tone) if any(c.isalpha() for c in syl) else '')

def pinyin_to_numeric(pinyin_diacritic):
    tokens = re.split(r'(\s+)', pinyin_diacritic.strip())
    return ''.join(syllable_to_numeric(t) if t.strip() else t for t in tokens)

INITIALS = ['zh','ch','sh','b','p','m','f','d','t','n','l','g','k','h','j','q','x','r','z','c','s']
INITIAL_MAP = {
    'b':'ㄅ','p':'ㄆ','m':'ㄇ','f':'ㄈ','d':'ㄉ','t':'ㄊ','n':'ㄋ','l':'ㄌ',
    'g':'ㄍ','k':'ㄎ','h':'ㄏ','j':'ㄐ','q':'ㄑ','x':'ㄒ',
    'zh':'ㄓ','ch':'ㄔ','sh':'ㄕ','r':'ㄖ','z':'ㄗ','c':'ㄘ','s':'ㄙ',
}
FINAL_MAP = {
    'a':'ㄚ','o':'ㄛ','e':'ㄜ','ê':'ㄝ','ai':'ㄞ','ei':'ㄟ','ao':'ㄠ','ou':'ㄡ',
    'an':'ㄢ','en':'ㄣ','ang':'ㄤ','eng':'ㄥ','er':'ㄦ',
    'i':'ㄧ','ia':'ㄧㄚ','ie':'ㄧㄝ','iao':'ㄧㄠ','iu':'ㄧㄡ','iou':'ㄧㄡ',
    'ian':'ㄧㄢ','in':'ㄧㄣ','iang':'ㄧㄤ','ing':'ㄧㄥ','iong':'ㄩㄥ',
    'u':'ㄨ','ua':'ㄨㄚ','uo':'ㄨㄛ','uai':'ㄨㄞ','ui':'ㄨㄟ','uei':'ㄨㄟ',
    'uan':'ㄨㄢ','un':'ㄨㄣ','uen':'ㄨㄣ','uang':'ㄨㄤ','ueng':'ㄨㄥ',
    'v':'ㄩ','ve':'ㄩㄝ','van':'ㄩㄢ','vn':'ㄩㄣ',
    'ong':'ㄨㄥ',
}
TONE_CHAR = {1:'', 2:'ˊ', 3:'ˇ', 4:'ˋ', 5:'˙'}
BUZZ_INITIALS = {'zh','ch','sh','r','z','c','s'}

def syllable_numeric_to_bopomofo(syl):
    m = re.match(r'^([a-zA-Z]+)([1-5]?)$', syl)
    if not m:
        return syl
    body, tone = m.group(1).lower(), m.group(2)
    tone = int(tone) if tone else 5

    if body == 'r':
        return 'ㄦ' + TONE_CHAR.get(tone, '')

    initial = ''
    for cand in sorted(INITIALS, key=len, reverse=True):
        if body.startswith(cand):
            initial = cand
            break
    final = body[len(initial):]

    if initial in BUZZ_INITIALS and final == 'i':
        final = ''

    if not initial:
        if body == 'yi':
            final = 'i'
        elif body == 'yin':
            final = 'in'
        elif body == 'ying':
            final = 'ing'
        elif body == 'wu':
            final = 'u'
        elif body == 'yu':
            final = 'v'
        elif body.startswith('yu'):
            final = 'v' + body[2:]
        elif body.startswith('y'):
            final = 'i' + body[1:]
        elif body.startswith('w'):
            final = 'u' + body[1:]
        else:
            final = body

    if initial in ('j', 'q', 'x'):
        JQX_U_TO_V = {'u': 'v', 'ue': 've', 'uan': 'van', 'un': 'vn'}
        final = JQX_U_TO_V.get(final, final)

    bopomofo_initial = INITIAL_MAP.get(initial, '')
    bopomofo_final = FINAL_MAP.get(final, final if final else '')
    tone_mark = TONE_CHAR.get(tone, '')
    return bopomofo_initial + bopomofo_final + tone_mark

def pinyin_to_bopomofo(pinyin_diacritic):
    numeric = pinyin_to_numeric(pinyin_diacritic)
    tokens = numeric.split(' ')
    return ' '.join(syllable_numeric_to_bopomofo(t) for t in tokens if t)


# ═══════════════════════════════════════════════════════════════
# BAGIAN 2 — Load semua data referensi lokal
# ═══════════════════════════════════════════════════════════════

STRUCT_MAP = {
    '⿰': 'left-right', '⿱': 'top-bottom', '⿲': 'left-middle-right',
    '⿳': 'top-middle-bottom', '⿴': 'enclosed-full', '⿵': 'enclosed-top',
    '⿶': 'enclosed-bottom', '⿷': 'enclosed-left', '⿸': 'enclosed-topleft',
    '⿹': 'enclosed-topright', '⿺': 'enclosed-botleft', '⿻': 'overlaid',
}

def load_json(path, required=True):
    if not path.exists():
        if required:
            print(f"‼ FATAL: file wajib tidak ditemukan: {path}")
            sys.exit(1)
        return None
    with open(path, encoding='utf-8') as f:
        return json.load(f)

def load_mmh_dict(path):
    d = {}
    if not path.exists():
        print(f"⚠ {path} tidak ditemukan -- radikal/struktur/komponen akan kosong utk kata baru")
        return d
    with open(path, encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            obj = json.loads(line)
            d[obj['character']] = obj
    return d

def load_strokes(path):
    """Terima 2 format: {char: {"strokes":[...]}} ATAU list of {"character":...,"strokes":[...]}"""
    if not path.exists():
        print(f"⚠ {path} tidak ditemukan -- stroke_count akan 0 utk kata baru")
        return {}
    with open(path, encoding='utf-8') as f:
        raw = json.load(f)
    out = {}
    if isinstance(raw, dict):
        for k, v in raw.items():
            strokes = v.get('strokes') if isinstance(v, dict) else v
            out[k] = len(strokes) if strokes else 0
    elif isinstance(raw, list):
        for item in raw:
            c = item.get('character')
            strokes = item.get('strokes')
            if c:
                out[c] = len(strokes) if strokes else 0
    return out


def char_info(ch, mmh_dict, strokes_map):
    d = mmh_dict.get(ch, {})
    decomp = d.get('decomposition', '')
    structure = STRUCT_MAP.get(decomp[0]) if decomp and decomp[0] in STRUCT_MAP else 'single'
    components = [c for c in decomp if c not in STRUCT_MAP and c != '？'] if decomp else []
    return {
        'radical': d.get('radical', ch),
        'stroke_count': strokes_map.get(ch, 0),
        'structure': structure,
        'components': components,
    }

def word_derived_fields(hanzi, mmh_dict, strokes_map):
    infos = [char_info(c, mmh_dict, strokes_map) for c in hanzi]
    radical = infos[0]['radical'] if infos else ''
    stroke_count = sum(i['stroke_count'] for i in infos)
    structure = infos[0]['structure'] if infos else 'single'
    components = []
    for i in infos:
        components.extend(i['components'])
    return radical, stroke_count, structure, components


def slugify_theme(label):
    s = label.strip().lower()
    s = re.sub(r'[^a-z0-9\s_-]', '', s)
    s = re.sub(r'[\s-]+', '_', s)
    return 'custom_' + s.strip('_')


# ═══════════════════════════════════════════════════════════════
# BAGIAN 3 — Proses utama
# ═══════════════════════════════════════════════════════════════

def main():
    if len(sys.argv) < 2:
        print("Cara pakai: python complete_theme_json.py <file_json_mentah.json>")
        sys.exit(1)

    raw_path = Path(sys.argv[1])
    if not raw_path.exists():
        print(f"‼ File tidak ditemukan: {raw_path}")
        sys.exit(1)

    raw = load_json(raw_path)
    theme_label = raw.get('theme', '').strip()
    raw_words = raw.get('words', [])
    if not theme_label or not raw_words:
        print("‼ JSON mentah harus punya field 'theme' (nama) dan 'words' (list berisi minimal 1 kata)")
        sys.exit(1)

    print(f"Tema: {theme_label}  ({len(raw_words)} kata di file mentah)")

    app_words   = load_json(APP_WORDS_PATH)
    index_theme = load_json(INDEX_THEME_PATH)
    cidict      = load_json(CIDICT_PATH, required=False) or []
    mmh_dict    = load_mmh_dict(MMH_DICT_PATH)
    strokes_map = load_strokes(STROKES_PATH)

    by_id_app    = {w.get('id') or w.get('simplified'): w for w in app_words}
    by_s_cidict  = {}
    for w in cidict:
        by_s_cidict.setdefault(w['simplified'], w)

    # ── cari/bikin key tema ──
    theme_key = None
    for k, v in index_theme.items():
        if v.get('label_id', '').strip().lower() == theme_label.lower():
            theme_key = k
            break
    if not theme_key:
        theme_key = slugify_theme(theme_label)
        if theme_key in index_theme:
            print(f"  (key tema '{theme_key}' sudah ada tapi label beda -- tetap dipakai/digabung)")
        else:
            index_theme[theme_key] = {'label_id': theme_label, 'label_zh': '', 'words': [], 'count': 0}
    print(f"Key tema: {theme_key}")

    new_entries = []
    already_tagged = []
    newly_tagged   = []
    built_new      = []
    skipped        = []

    for item in raw_words:
        hanzi = (item.get('hanzi') or '').strip()
        if not hanzi:
            skipped.append(item)
            continue

        # kasus 1: kata SUDAH ada di app_words.json -> tinggal tag temanya
        if hanzi in by_id_app:
            w = by_id_app[hanzi]
            themes = w.get('themes') or []
            if theme_key not in themes:
                themes.append(theme_key)
                w['themes'] = themes
                newly_tagged.append(hanzi)
            else:
                already_tagged.append(hanzi)
            continue

        # kasus 2: kata BARU -> bangun entri lengkap
        pinyin_raw = (item.get('pinyin') or '').strip()
        translation = (item.get('translation') or '').strip()

        cidict_hit = by_s_cidict.get(hanzi)
        if cidict_hit:
            pinyin = cidict_hit['pinyin']
            pinyin_numeric = cidict_hit.get('pinyin_numeric') or pinyin_to_numeric(pinyin)
            traditional = cidict_hit.get('traditional', hanzi)
            meaning_id = cidict_hit['meanings_id'][0] if cidict_hit.get('meanings_id') else (translation or '(arti belum ada)')
            source_note = 'cidict_index.json (lokal) -- arti resmi dipakai, bukan translation dari AI'
        else:
            pinyin = pinyin_raw or ' '.join(c for c in hanzi)
            pinyin_numeric = pinyin_to_numeric(pinyin)
            traditional = hanzi  # asumsi -- TIDAK divalidasi, lihat _source_note
            meaning_id = translation or '(arti belum ada -- lengkapi manual)'
            source_note = f'Tidak ketemu di cidict_index.json -- pinyin & arti dari AI ("{theme_label}" import), traditional diasumsikan sama dgn simplified (BELUM divalidasi)'

        bopomofo = pinyin_to_bopomofo(pinyin)
        radical, stroke_count, structure, components = word_derived_fields(hanzi, mmh_dict, strokes_map)

        entry = {
            'id': hanzi, 'simplified': hanzi, 'traditional': traditional,
            'pinyin': pinyin, 'pinyin_numeric': pinyin_numeric, 'bopomofo': bopomofo,
            'hsk': None, 'hsk2': None, 'frequency': None,
            'pos': ['n'], 'pos_id': ['kata benda'],
            'meanings_id': [meaning_id], 'meanings_en': [],
            'radical': radical, 'radical_number': None, 'stroke_count': stroke_count,
            'structure': structure, 'components': components,
            'char_type': 'compound' if len(hanzi) > 1 else 'simple',
            'themes': [theme_key],
            'synonyms': [], 'antonyms': [],
            '_source_note': source_note,
        }
        new_entries.append(entry)
        by_id_app[hanzi] = entry
        built_new.append(hanzi)

    # ── tulis balik (dgn backup dulu) ──
    if new_entries or newly_tagged:
        ts = datetime.now().strftime('%Y%m%d_%H%M%S')
        if APP_WORDS_PATH.exists():
            backup_path = APP_WORDS_PATH.with_suffix(f'.json.bak_{ts}')
            shutil.copy2(APP_WORDS_PATH, backup_path)
            print(f"\nBackup dibuat: {backup_path}")

        app_words.extend(new_entries)
        json.dump(app_words, open(APP_WORDS_PATH, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

        all_theme_words = set(index_theme[theme_key]['words'])
        for h in built_new + newly_tagged:
            all_theme_words.add(h)
        index_theme[theme_key]['words'] = sorted(all_theme_words)
        index_theme[theme_key]['count'] = len(all_theme_words)
        json.dump(index_theme, open(INDEX_THEME_PATH, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

    # ── laporan ──
    report = []
    report.append(f"=== LAPORAN complete_theme_json.py -- {datetime.now()} ===")
    report.append(f"Tema: {theme_label} (key: {theme_key})")
    report.append(f"Total kata di file mentah: {len(raw_words)}")
    report.append(f"  Kata baru dibangun & ditambah ke app_words.json: {len(built_new)}")
    report.append(f"  Kata sudah ada, baru ditag tema ini: {len(newly_tagged)}")
    report.append(f"  Kata sudah ada & sudah tertag tema ini sebelumnya: {len(already_tagged)}")
    report.append(f"  Dilewati (hanzi kosong): {len(skipped)}")
    report.append(f"Jumlah kartu tema '{theme_label}' sekarang: {index_theme[theme_key]['count']}")
    report.append("")
    report.append("--- Kata baru dari cidict_index.json (arti resmi, kualitas tinggi) ---")
    for e in new_entries:
        if 'arti resmi dipakai' in e['_source_note']:
            report.append(f"  {e['simplified']} | {e['pinyin']} | {e['meanings_id'][0]}")
    report.append("")
    report.append("--- Kata baru TANPA cidict (dari AI, PERLU DICEK MANUAL traditional & arti) ---")
    for e in new_entries:
        if 'arti resmi dipakai' not in e['_source_note']:
            report.append(f"  {e['simplified']} | {e['pinyin']} | {e['meanings_id'][0]}")
    if skipped:
        report.append("")
        report.append("--- Item dilewati (hanzi kosong/format salah) ---")
        for s in skipped:
            report.append(f"  {s}")

    report_text = "\n".join(report)
    print("\n" + report_text)

    report_path = Path(f"complete_theme_json_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
    report_path.write_text(report_text, encoding='utf-8')
    print(f"\nLaporan disimpan: {report_path}")
    print("\nSELESAI. app_words.json & index_theme.json sudah diperbarui langsung.")
    print("Cek kata2 di bagian 'TANPA cidict' di atas -- itu paling perlu diverifikasi manual.")


if __name__ == "__main__":
    main()

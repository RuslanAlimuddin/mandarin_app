# -*- coding: utf-8 -*-
"""
complete_reading_json.py — Mandarin Interaktif
===============================================
Lengkapi file JSON bacaan/percakapan MENTAH (hasil AI lain) jadi entri siap
pakai di data/graded_readers.json — glosarium (pinyin + arti) diisi OTOMATIS
lewat tokenisasi greedy longest-match terhadap app_words.json (prioritas)
dan cidict_index.json (fallback), PERSIS pola yang sudah terbukti dipakai di
complete_theme_json.py. 100% OFFLINE.

Mendukung 2 jenis konten (auto-terdeteksi dari isi file mentah):
  - "bacaan"     -> field wajib: text (paragraf biasa)
  - "percakapan" -> field wajib: turns (array {speaker, cn, translation})

CARA PAKAI:
  1. Taruh skrip ini di C:\\mandarin_app (sejajar dgn folder data/).
  2. Simpan JSON mentah dari AI lain, mis. sebagai raw_bandara.json.
     Boleh 1 objek, atau list berisi beberapa objek sekaligus.

     Contoh BACAAN mentah:
       {
         "type": "bacaan",
         "level": 3,
         "tema": "Di Bandara",
         "title": "Di Bandara",
         "text": "我在机场等飞机。飞机晚点了,我有点儿着急。",
         "translation": "Saya menunggu pesawat di bandara. Pesawatnya
                          terlambat, saya agak khawatir."
       }
       (field "text"/"translation" boleh AI isi bebas, TIDAK perlu kasih
        glossary -- skrip ini yang akan bangun glossary otomatis)

     Contoh PERCAKAPAN mentah:
       {
         "type": "percakapan",
         "level": 2,
         "tema": "Perkenalan Diri",
         "title": "Berkenalan di Kelas",
         "related_theme": "keluarga",
         "turns": [
           {"speaker": "A", "cn": "你好,我叫王明。", "translation": "Halo, nama saya Wang Ming."},
           {"speaker": "B", "cn": "你好王明,我是林娜。", "translation": "Halo Wang Ming, saya Lin Na."}
         ]
       }
       ("related_theme" opsional -- key ke index_theme.json kalau mau
        dikait ke tema kosakata terkait, mis. "restoran" -> "makanan_minuman")

  PENTING UNTUK PERCAKAPAN -- field "names" (SANGAT disarankan diisi):
     Nama tokoh dialog (mis. 王明, 林娜) BUKAN kata kamus biasa. Kalau
     dibiarkan, sistem akan coba cari di kamus dan bisa dapat 2 hasil salah:
       (a) kebetulan cocok kata/nama lain di kamus (mis. "王明" bisa kena
           arti tokoh sejarah lain yang kebetulan sama namanya di CC-CEDICT)
       (b) tidak ketemu sama sekali -> kepecah jadi karakter lepas, masing2
           dapat arti generiknya sendiri (mis. 林 = "marga Lin", 娜 =
           "(fonetik na)") -- SALAH TOTAL untuk pembaca, tapi tidak akan
           kelihatan sbg error karena tiap karakter "berhasil" ketemu.
     Solusi: selalu sertakan field "names" di root objek, isi SEMUA nama
     tokoh yang dipakai di "turns":
       "names": [
         {"hanzi": "王明", "pinyin": "Wáng Míng", "translation": "Wang Ming (nama orang)"},
         {"hanzi": "林娜", "pinyin": "Lín Nà", "translation": "Lin Na (nama orang)"}
       ]
     Field ini prioritas PALING TINGGI saat tokenisasi (di atas app_words.json
     & cidict_index.json), jadi dijamin dipakai persis sesuai yang diisi di
     sini, bukan hasil tebakan kamus. Berlaku juga untuk bacaan (field
     "names" opsional yang sama, kalau bacaan pakai nama tokoh).

  3. Jalankan:
       python complete_reading_json.py raw_bandara.json

  4. Skrip akan:
       - Tokenisasi tiap teks (greedy longest-match, maxlen 8) terhadap
         app_words.json dulu, kalau tidak ketemu baru cidict_index.json.
       - Kata/karakter yang TETAP tidak ketemu di keduanya ditandai
         "PERLU DICEK MANUAL" di laporan (py/arti dikosongkan, bukan ditebak).
       - ID unik dibangun otomatis dari tema/judul + level, dicek supaya
         TIDAK bentrok dengan entri yang sudah ada di graded_readers.json.
       - data/graded_readers.json DITULIS LANGSUNG (in-place). Backup
         otomatis dibuat dulu (graded_readers.json.bak_TIMESTAMP).
       - Laporan lengkap dicetak ke layar + disimpan sbg
         complete_reading_json_report_TIMESTAMP.txt

Aman dijalankan berkali-kali untuk bacaan/percakapan berbeda.
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
APP_WORDS_PATH     = DATA_DIR / "app_words.json"
CIDICT_PATH        = DATA_DIR / "cidict_index.json"
GRADED_READER_PATH = DATA_DIR / "graded_readers.json"

MAXLEN = 8  # panjang maksimum kata yang dicoba dicocokkan saat tokenisasi
PUNCT = set('，。！？、；：""''（）《》…—·,.!?;:()[]"\' \n\t“”0123456789')

# Karakter super-umum yang di cidict_index.json punya BANYAK entri (marga,
# bacaan sastra/klasik, bacaan modern) -- tanpa ini, sistem bisa asal ambil
# entri pertama yang urutannya kebetulan bukan bacaan modern yang wajar.
# Isi tabel ini kalau nanti ketemu kasus baru serupa (cek laporan hasil run,
# atau laporan رسلان kalau ada arti yang kelihatan aneh/tidak nyambung).
COMMON_READING_OVERRIDE = {
    '都': 'dōu', '和': 'hé', '要': 'yào', '更': 'gèng', '得': 'de',
    '中': 'zhōng', '着': 'zhe', '数': 'shù', '还': 'hái', '只': 'zhǐ',
    '长': 'cháng', '行': 'xíng', '分': 'fēn', '少': 'shǎo', '倒': 'dào',
    '重': 'zhòng', '难': 'nán', '当': 'dāng', '校': 'xiào', '传': 'chuán',
    '曾': 'céng', '系': 'xì', '为': 'wéi', '会': 'huì', '没': 'méi',
}
# Kalau ada >1 kandidat dan tidak ada di tabel override di atas, hindari
# entri yang meaning-nya jelas-jelas marga/nama/varian/bacaan sastra kuno --
# biasanya bukan bacaan yang dimaksud dalam teks bacaan/percakapan biasa.
DEPRIORITIZE_MARKERS = ('marga ', 'varian', '(sastra)', 'nama keluarga', '(bentuk terikat)')


# ═══════════════════════════════════════════════════════════════
# BAGIAN 1 — Load data referensi lokal
# ═══════════════════════════════════════════════════════════════

def load_json(path, required=True):
    if not path.exists():
        if required:
            print(f"‼ FATAL: file wajib tidak ditemukan: {path}")
            sys.exit(1)
        return None
    with open(path, encoding='utf-8') as f:
        return json.load(f)


def pick_best_cidict_entry(candidates, hanzi):
    """candidates = list of raw cidict entries (dict) utk 1 simplified yang sama.
    Pilih 1 yang paling masuk akal jadi bacaan/arti default."""
    if len(candidates) == 1:
        return candidates[0]

    override_py = COMMON_READING_OVERRIDE.get(hanzi)
    if override_py:
        for c in candidates:
            if c.get('pinyin', '').strip().lower() == override_py.lower():
                return c

    # hindari entri yg meaning-nya keliatan marga/varian/sastra kuno
    non_rare = []
    for c in candidates:
        meanings = c.get('meanings_id') or []
        first = (meanings[0] if meanings else '').lower()
        if not any(marker in first for marker in DEPRIORITIZE_MARKERS):
            non_rare.append(c)
    if non_rare:
        return non_rare[0]

    return candidates[0]  # semua kandidat "rare" -- pasrah pakai yg pertama


def build_lookup(app_words, cidict):
    """Gabungkan app_words.json (prioritas) + cidict_index.json (fallback)
    jadi satu dict {simplified: {py, id, source}} buat tokenisasi & glosarium.
    Untuk kata yg di cidict_index.json py entri lebih dari 1 (marga, bacaan
    sastra, dll), pakai pick_best_cidict_entry() supaya tidak asal ambil
    entri pertama yg kebetulan bukan bacaan yang wajar dipakai."""
    grouped = {}
    for w in cidict:
        s = w.get('simplified')
        if not s:
            continue
        grouped.setdefault(s, []).append(w)

    lookup = {}
    for s, candidates in grouped.items():
        best = pick_best_cidict_entry(candidates, s)
        meanings = best.get('meanings_id') or []
        lookup[s] = {
            'py': best.get('pinyin', ''),
            'id': meanings[0] if meanings else '',
            'source': 'cidict_index.json',
        }
    # app_words.json ditimpa di atas cidict -- prioritas lebih tinggi
    # (kata yang sudah dikurasi رسلان sendiri di app dianggap lebih akurat)
    for w in app_words:
        s = w.get('simplified')
        if not s:
            continue
        meanings = w.get('meanings_id') or []
        lookup[s] = {
            'py': w.get('pinyin', ''),
            'id': meanings[0] if meanings else '',
            'source': 'app_words.json',
        }

    # PASS TERAKHIR: tabel COMMON_READING_OVERRIDE menang MUTLAK di atas
    # app_words.json maupun cidict -- soalnya app_words.json sendiri kadang
    # field "pinyin"-nya kebetulan bacaan langka (mis. "都" tersimpan sbg
    # bacaan marga "Dū", padahal yg dimaksud hampir selalu "dōu"=semua).
    for hanzi, target_py in COMMON_READING_OVERRIDE.items():
        candidates = grouped.get(hanzi)
        if not candidates:
            continue
        matching = [c for c in candidates if c.get('pinyin', '').strip().lower() == target_py.lower()]
        if not matching:
            continue
        non_rare = [c for c in matching if not any(
            marker in ((c.get('meanings_id') or [''])[0]).lower() for marker in DEPRIORITIZE_MARKERS
        )]
        best = non_rare[0] if non_rare else matching[0]
        meanings = best.get('meanings_id') or []
        lookup[hanzi] = {
            'py': best.get('pinyin', ''),
            'id': meanings[0] if meanings else '',
            'source': 'COMMON_READING_OVERRIDE',
        }

    return lookup


# ═══════════════════════════════════════════════════════════════
# BAGIAN 2 — Tokenisasi greedy longest-match (sama gaya dgn
# verify_coverage.py & tokenizePassage() di graded-reader.html)
# ═══════════════════════════════════════════════════════════════

def tokenize_and_gloss(text, lookup, maxlen=MAXLEN):
    """Kembalikan (tokens, glossary_entries_ordered, unresolved_list).
    tokens: list dict {type:'word'|'punct', cn, py, id, source}
    glossary_entries_ordered: list unik {cn,py,id} sesuai urutan kemunculan
    unresolved: list kata/karakter yang TIDAK ketemu di lookup manapun"""
    tokens = []
    seen_gloss = {}
    unresolved = []
    i = 0
    n = len(text)
    while i < n:
        ch = text[i]
        if ch in PUNCT:
            tokens.append({'type': 'punct', 'cn': ch})
            i += 1
            continue
        matched_word = None
        matched_len = 0
        for L in range(min(maxlen, n - i), 0, -1):
            cand = text[i:i + L]
            if cand in lookup:
                matched_word = cand
                matched_len = L
                break
        if matched_word:
            info = lookup[matched_word]
            tokens.append({'type': 'word', 'cn': matched_word, 'py': info['py'], 'id': info['id'], 'source': info['source']})
            if matched_word not in seen_gloss:
                seen_gloss[matched_word] = {'cn': matched_word, 'py': info['py'], 'id': info['id']}
            i += matched_len
        else:
            single = text[i]
            tokens.append({'type': 'word', 'cn': single, 'py': '', 'id': '', 'source': None})
            if single not in seen_gloss:
                seen_gloss[single] = {'cn': single, 'py': '', 'id': ''}
                unresolved.append(single)
            i += 1
    return tokens, list(seen_gloss.values()), unresolved


def normalize_level(raw_level):
    """Terima level dalam bentuk apa pun yang wajar: 1 (int), "1", "HSK 1",
    "HSK1", "hsk 1" -- selalu kembalikan integer bersih. Ini penting karena
    AI generator kadang menulis level sebagai teks, bukan angka murni."""
    if isinstance(raw_level, int):
        return raw_level
    if isinstance(raw_level, float):
        return int(raw_level)
    s = str(raw_level)
    m = re.search(r'\d+', s)
    if not m:
        raise ValueError(f'level "{raw_level}" tidak mengandung angka yang bisa dibaca')
    return int(m.group())


def slugify(label):
    s = unicodedata.normalize('NFKD', label).strip().lower()
    s = re.sub(r'[^a-z0-9\s_-]', '', s)
    s = re.sub(r'[\s-]+', '_', s)
    return s.strip('_') or 'tanpa_judul'


def make_unique_id(base, existing_ids, used_this_batch):
    candidate = base
    n = 2
    while candidate in existing_ids or candidate in used_this_batch:
        candidate = f"{base}_{n}"
        n += 1
    used_this_batch.add(candidate)
    return candidate


# ═══════════════════════════════════════════════════════════════
# BAGIAN 3 — Proses 1 item mentah -> entri siap pakai
# ═══════════════════════════════════════════════════════════════

def apply_names_override(item, lookup):
    """Field opsional "names": [{"hanzi":"王明","translation":"Wang Ming (nama orang)"}]
    dipakai buat nama tokoh/tempat yang TIDAK boleh diambil dari kamus umum
    (nama orang sering kebetulan cocok kata kamus dgn arti lain sama sekali,
    atau tidak ada di kamus sama sekali dan malah kepecah jadi karakter
    lepas). Override ini prioritas PALING TINGGI, dicek sebelum app_words/cidict."""
    names = item.get('names') or []
    if not names:
        return lookup
    local = dict(lookup)  # jangan ubah lookup global, cuma untuk item ini
    for n in names:
        hanzi = (n.get('hanzi') or '').strip()
        if not hanzi:
            continue
        local[hanzi] = {'py': n.get('pinyin', ''), 'id': n.get('translation', '(nama)'), 'source': 'names (manual)'}
    return local


def process_bacaan(item, lookup, existing_ids, used_ids, report):
    level = normalize_level(item['level'])
    tema = (item.get('tema') or '').strip()
    title = (item.get('title') or tema or 'Tanpa Judul').strip()
    text = item['text']
    translation = item.get('translation', '')
    lookup = apply_names_override(item, lookup)

    tokens, glossary, unresolved = tokenize_and_gloss(text, lookup)

    base = slugify(tema or title) + f"_hsk{level}"
    new_id = make_unique_id(base, existing_ids, used_ids)

    entry = {
        'id': new_id,
        'level': level,
        'type': 'bacaan',
        'title': title,
        'text': text,
        'translation': translation,
        'glossary': glossary,
    }
    if tema:
        entry['tema'] = tema
    if item.get('related_theme'):
        entry['related_theme'] = item['related_theme']

    report.append(f"[BACAAN] {new_id} — \"{title}\" (HSK{level}, tema: {tema or '-'})")
    report.append(f"    {len(glossary)} kata di glossary, {len(unresolved)} PERLU DICEK MANUAL")
    if unresolved:
        report.append(f"    -> {', '.join(unresolved)}")
    return entry


def process_percakapan(item, lookup, existing_ids, used_ids, report):
    level = normalize_level(item['level'])
    tema = (item.get('tema') or '').strip()
    title = (item.get('title') or tema or 'Tanpa Judul').strip()
    raw_turns = item['turns']
    lookup = apply_names_override(item, lookup)

    all_glossary = {}
    all_unresolved = []
    out_turns = []
    translation_lines = []

    for t in raw_turns:
        speaker = t.get('speaker', '?')
        cn = t['cn']
        line_translation = t.get('translation', '')
        tokens, glossary, unresolved = tokenize_and_gloss(cn, lookup)

        # pinyin satu baris = gabungan pinyin tiap token kata (utk toggle pinyin per baris)
        py_parts = [tok['py'] for tok in tokens if tok['type'] == 'word' and tok['py']]
        line_py = ' '.join(py_parts)

        out_turns.append({
            'speaker': speaker,
            'cn': cn,
            'py': line_py,
            'translation': line_translation,
        })
        translation_lines.append(f"{speaker}: {line_translation}")

        for g in glossary:
            if g['cn'] not in all_glossary:
                all_glossary[g['cn']] = g
        for u in unresolved:
            if u not in all_unresolved:
                all_unresolved.append(u)

    base = slugify(tema or title) + f"_hsk{level}"
    new_id = make_unique_id(base, existing_ids, used_ids)

    entry = {
        'id': new_id,
        'level': level,
        'type': 'percakapan',
        'title': title,
        'turns': out_turns,
        'translation': '\n'.join(translation_lines),
        'glossary': list(all_glossary.values()),
    }
    if tema:
        entry['tema'] = tema
    if item.get('related_theme'):
        entry['related_theme'] = item['related_theme']

    report.append(f"[PERCAKAPAN] {new_id} — \"{title}\" (HSK{level}, tema: {tema or '-'}, {len(out_turns)} baris)")
    report.append(f"    {len(all_glossary)} kata di glossary, {len(all_unresolved)} PERLU DICEK MANUAL")
    if all_unresolved:
        report.append(f"    -> {', '.join(all_unresolved)}")
    return entry


# ═══════════════════════════════════════════════════════════════
# BAGIAN 4 — Main
# ═══════════════════════════════════════════════════════════════

def main():
    if len(sys.argv) < 2:
        print("Cara pakai: python complete_reading_json.py <file_json_mentah.json>")
        sys.exit(1)

    raw_path = Path(sys.argv[1])
    if not raw_path.exists():
        print(f"‼ File tidak ditemukan: {raw_path}")
        sys.exit(1)

    raw = load_json(raw_path)
    items = raw if isinstance(raw, list) else [raw]

    print(f"Membaca {len(items)} item mentah dari {raw_path}")

    app_words = load_json(APP_WORDS_PATH)
    cidict = load_json(CIDICT_PATH, required=False) or []
    lookup = build_lookup(app_words, cidict)
    print(f"Lookup gabungan: {len(lookup)} kata (app_words.json + cidict_index.json)")

    gr_data = load_json(GRADED_READER_PATH)
    existing_passages = gr_data['passages'] if isinstance(gr_data, dict) else gr_data
    existing_ids = set(p['id'] for p in existing_passages)
    print(f"Bacaan/percakapan yang sudah ada: {len(existing_passages)}")

    used_ids = set()
    report = []
    report.append(f"=== LAPORAN complete_reading_json.py — {datetime.now()} ===")
    report.append(f"File sumber: {raw_path}")
    report.append("")

    new_entries = []
    skipped = []

    for idx, item in enumerate(items):
        if 'level' not in item:
            skipped.append((idx, 'field "level" wajib ada'))
            continue
        try:
            normalize_level(item['level'])
        except ValueError as e:
            skipped.append((idx, str(e)))
            continue
        detected_type = item.get('type')
        if not detected_type:
            detected_type = 'percakapan' if 'turns' in item else 'bacaan'

        try:
            if detected_type == 'percakapan':
                if 'turns' not in item or not item['turns']:
                    skipped.append((idx, 'type percakapan tapi field "turns" kosong/tidak ada'))
                    continue
                entry = process_percakapan(item, lookup, existing_ids, used_ids, report)
            else:
                if 'text' not in item or not item['text']:
                    skipped.append((idx, 'type bacaan tapi field "text" kosong/tidak ada'))
                    continue
                entry = process_bacaan(item, lookup, existing_ids, used_ids, report)
        except KeyError as e:
            skipped.append((idx, f'field wajib hilang: {e}'))
            continue

        new_entries.append(entry)
        report.append("")

    if skipped:
        report.append("--- Item DILEWATI (format tidak lengkap) ---")
        for idx, reason in skipped:
            report.append(f"  Item #{idx}: {reason}")
        report.append("")

    if not new_entries:
        print("\nTidak ada entri baru yang berhasil diproses. Tidak ada yang ditulis.")
        print("\n".join(report))
        sys.exit(0)

    # ── tulis balik (dgn backup dulu) ──
    ts = datetime.now().strftime('%Y%m%d_%H%M%S')
    if GRADED_READER_PATH.exists():
        backup_path = GRADED_READER_PATH.with_suffix(f'.json.bak_{ts}')
        shutil.copy2(GRADED_READER_PATH, backup_path)
        print(f"\nBackup dibuat: {backup_path}")

    combined_passages = existing_passages + new_entries
    combined = {'passages': combined_passages}
    with open(GRADED_READER_PATH, 'w', encoding='utf-8') as f:
        json.dump(combined, f, ensure_ascii=False, indent=1)

    report.append(f"Total item mentah: {len(items)}")
    report.append(f"  Berhasil ditambahkan: {len(new_entries)}")
    report.append(f"  Dilewati: {len(skipped)}")
    report.append(f"Total bacaan/percakapan sekarang di {GRADED_READER_PATH}: {len(combined_passages)}")

    report_text = "\n".join(report)
    print("\n" + report_text)

    report_path = Path(f"complete_reading_json_report_{ts}.txt")
    report_path.write_text(report_text, encoding='utf-8')
    print(f"\nLaporan disimpan: {report_path}")
    print("\nSELESAI. data/graded_readers.json sudah diperbarui langsung.")
    print("Cek kata yang ditandai 'PERLU DICEK MANUAL' di laporan -- itu paling perlu diverifikasi manual.")
    print("\nSaran: jalankan verify_coverage.py ke file final untuk memastikan semua aman:")
    print(f"  python verify_coverage.py {GRADED_READER_PATH}")


if __name__ == "__main__":
    main()

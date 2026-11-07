# -*- coding: utf-8 -*-
"""build_remaining_themes.py -- Nama Negara Utama, Bentuk & Bangun, sisa Olahraga Bola"""
import json

# reuse fungsi bopomofo/struktur dari skrip sebelumnya
exec(open('build_theme_entries.py').read().split("# ── 5. Terjemahan")[0])

cidict = json.load(open('cidict_index.json', encoding='utf-8'))
by_s_cidict2 = {w['simplified']: w for w in cidict}
app_words = json.load(open('app_words.json', encoding='utf-8'))
index_theme = json.load(open('index_theme.json', encoding='utf-8'))

CANDS = {
 'ext_names_of_the_main_countries': ['美国','日本','韩国','法国','德国','英国','泰国','俄罗斯','印度','越南','加拿大','澳大利亚','新加坡','马来西亚','意大利','西班牙'],
 'ext_shapes': ['正方形','长方形','三角形','菱形','梯形'],
 'ext_ball_games': ['曲棍球','保龄球'],
}

existing_ids = {w.get('id') or w.get('simplified') for w in app_words}

new_entries = []
for theme_key, cands in CANDS.items():
    for hanzi in cands:
        if hanzi in existing_ids:
            print('lewati (sudah ada):', hanzi)
            continue
        w = by_s_cidict2.get(hanzi)
        if not w:
            print('!! tidak ketemu di cidict:', hanzi)
            continue

        pinyin = w['pinyin']
        pinyin_numeric = w.get('pinyin_numeric') or pinyin_to_numeric(pinyin)
        bopomofo = pinyin_to_bopomofo(pinyin)
        radical, stroke_count, structure, components = word_derived_fields(hanzi)

        entry = {
            'id': hanzi, 'simplified': hanzi, 'traditional': w.get('traditional', hanzi),
            'pinyin': pinyin, 'pinyin_numeric': pinyin_numeric, 'bopomofo': bopomofo,
            'hsk': None, 'hsk2': None, 'frequency': None,
            'pos': ['n'], 'pos_id': ['kata benda'],
            'meanings_id': w['meanings_id'][:1],
            'meanings_en': [],
            'radical': radical, 'radical_number': None, 'stroke_count': stroke_count,
            'structure': structure, 'components': components,
            'char_type': 'compound' if len(hanzi) > 1 else 'simple',
            'themes': [theme_key],
            'synonyms': [], 'antonyms': [],
            '_source_note': 'CC-CEDICT (cidict_index.json)',
        }
        new_entries.append(entry)
        existing_ids.add(hanzi)

print(f'\nEntri baru: {len(new_entries)}')
app_words.extend(new_entries)
json.dump(app_words, open('app_words.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

for entry in new_entries:
    for theme_key in entry['themes']:
        if entry['simplified'] not in index_theme[theme_key]['words']:
            index_theme[theme_key]['words'].append(entry['simplified'])
        index_theme[theme_key]['count'] = len(index_theme[theme_key]['words'])
json.dump(index_theme, open('index_theme.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

print('app_words.json total:', len(app_words))
for k in CANDS:
    print(' ', index_theme[k]['label_id'], '->', index_theme[k]['count'], 'kartu')

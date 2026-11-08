#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
inspect_themes.py — inspeksi themes_extracted_v2.json TANPA perlu upload
seluruh file 8MB. Menghasilkan laporan ringkas + sampel ACAK per tema
supaya Claude bisa menilai kualitas data secara representatif.

Cara pakai:
    python inspect_themes.py themes_extracted_v2.json

Hasil: laporan_tema_sample.json di folder yang sama -- upload file itu
ke chat Claude.
"""
import json
import random
import sys
import os

SAMPLE_PER_THEME = 12     # berapa kata contoh diambil ACAK per tema
POLYPHONE_CHECK = {
    # kata umum yang rawan salah baca kalau di-generate otomatis tanpa
    # konteks (dari catatan BLUEPRINT) -- kalau muncul di data, kita cek
    # pinyin yang tercatat supaya Claude bisa lihat apa perlu dikoreksi manual
    '还': 'hái (bukan huán, kecuali makna "mengembalikan")',
    '都': 'dōu (bukan dū, kecuali nama kota "Chengdu" dll)',
    '了': 'le / liǎo tergantung konteks',
    '得': 'de / děi / dé tergantung konteks',
    '地': 'de (partikel) / dì (tanah) tergantung konteks',
    '长': 'cháng (panjang) / zhǎng (tumbuh/pemimpin) tergantung konteks',
    '重': 'zhòng (berat) / chóng (lagi/ulang) tergantung konteks',
    '教': 'jiāo (mengajar) / jiào (agama/pengajaran) tergantung konteks',
    '差': 'chà (kurang) / chā (selisih) / chāi (tugas) tergantung konteks',
    '为': 'wéi / wèi tergantung konteks',
    '好': 'hǎo (baik) / hào (suka) tergantung konteks',
    '发': 'fā (mengirim/tumbuh) / fà (rambut) tergantung konteks',
    '中': 'zhōng (tengah) / zhòng (kena/pas) tergantung konteks',
}


def main():
    if len(sys.argv) != 2:
        print('Pemakaian: python inspect_themes.py themes_extracted_v2.json')
        sys.exit(1)
    path = sys.argv[1]
    if not os.path.isfile(path):
        print(f'File tidak ditemukan: {path}')
        sys.exit(1)

    print('Membaca file (mungkin makan waktu beberapa detik untuk file besar)...')
    with open(path, encoding='utf-8') as f:
        data = json.load(f)

    report = {'source_file': path, 'themes': {}}

    if isinstance(data, dict):
        theme_keys = list(data.keys())
    elif isinstance(data, list):
        # kalau ternyata array datar dengan field 'theme'/'tema', kelompokkan
        grouped = {}
        for item in data:
            key = item.get('theme') or item.get('tema') or '(tanpa_tema)'
            grouped.setdefault(key, []).append(item)
        data = grouped
        theme_keys = list(data.keys())
    else:
        print('Struktur data tidak dikenali (bukan object atau array).')
        sys.exit(1)

    print(f'Ditemukan {len(theme_keys)} tema.')

    polyphone_hits = []

    for key in theme_keys:
        entries = data[key]
        raw_preview = json.dumps(entries, ensure_ascii=False)[:400]

        entries_list = []
        if isinstance(entries, list):
            entries_list = entries
        elif isinstance(entries, dict):
            # coba cari field yang isinya LIST OF WORDS di dalam dict tema ini
            # (skema umum: {"words":[...]}, {"vocab":[...]}, {"items":[...]}, dst)
            list_field = None
            for cand_key in ('words', 'vocab', 'vocabulary', 'items', 'entries', 'data', 'kata'):
                if cand_key in entries and isinstance(entries[cand_key], list):
                    list_field = cand_key
                    break
            if list_field is None:
                # fallback: cari field list TERPANJANG apa pun namanya
                list_fields = [(k, v) for k, v in entries.items() if isinstance(v, list)]
                if list_fields:
                    list_field = max(list_fields, key=lambda kv: len(kv[1]))[0]
            if list_field:
                entries_list = entries[list_field]
            else:
                # tidak ketemu list sama sekali -- anggap tiap key:value di dict
                # ini sendiri adalah 1 kata (skema {kata: detail})
                entries_list = [{'word': k, **(v if isinstance(v, dict) else {'value': v})}
                                 for k, v in entries.items()]

        total = len(entries_list)
        sample_n = min(SAMPLE_PER_THEME, total)
        sample = random.sample(entries_list, sample_n) if total else []

        # cek kata polifon rawan di tema ini
        for item in entries_list:
            word = item.get('word') or item.get('simplified') or item.get('cn') or ''
            if word in POLYPHONE_CHECK:
                pinyin_val = item.get('pinyin') or item.get('py') or ''
                polyphone_hits.append({
                    'theme': key, 'word': word,
                    'pinyin_in_data': pinyin_val,
                    'catatan_seharusnya': POLYPHONE_CHECK[word],
                })

        report['themes'][key] = {
            'total_kata': total,
            'sampel_acak': sample,
            'raw_preview_400char': raw_preview,
        }

    report['polyphone_check'] = polyphone_hits
    report['catatan'] = (
        'sampel_acak diambil RANDOM tiap tema (bukan urutan awal file) supaya '
        'representatif. polyphone_check menunjukkan entri kata umum-rawan-salah-baca '
        'yang ketemu di data beserta pinyin yang tercatat -- cek manual apa sudah benar.'
    )

    out_path = os.path.join(os.path.dirname(os.path.abspath(path)), 'laporan_tema_sample.json')
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=1)

    print(f'Selesai. Laporan disimpan di: {out_path}')
    print(f'Total tema: {len(theme_keys)}, total polyphone hits: {len(polyphone_hits)}')
    print('Upload laporan_tema_sample.json itu ke chat Claude.')


if __name__ == '__main__':
    main()

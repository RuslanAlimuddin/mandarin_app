# merge_themes.py
# Mencocokkan kata hasil scrape (themes_external_raw.json) dengan entri yang sudah ada
# di app_words.json, lalu menggabungkannya ke index_theme.json sebagai tema baru.
#
# CARA PAKAI:
#   1. Taruh themes_external_raw.json di folder C:\mandarin_app\ (sejajar app_words.json)
#   2. Jalankan: python merge_themes.py
#   3. Hasil:
#        - data\index_theme.json     (DIPERBARUI — tema lama + tema baru digabung)
#        - data\index_theme_backup.json (backup index_theme.json SEBELUM diubah)
#        - unmatched_theme_words.json   (laporan kata yang TIDAK ditemukan di app_words.json,
#                                         untuk dicek manual / opsional ditambahkan nanti)
#
# CATATAN PENTING:
#   Kata dari scrape yang TIDAK ada di app_words.json (kosakata di luar cakupan HSK 1-9
#   yang sudah رسلان punya) TIDAK akan otomatis ditambahkan ke app_words.json — karena
#   itu butuh data lengkap (radical, stroke_count, components, dst.) yang tidak tersedia
#   dari hasil scrape ini. Kata-kata itu hanya akan dilaporkan di unmatched_theme_words.json
#   supaya رسلان bisa putuskan apakah ingin ditambahkan manual nanti.

import json
import os
import shutil
import sys

DATA_DIR = 'data'
APP_WORDS_FILE     = os.path.join(DATA_DIR, 'app_words.json')
INDEX_THEME_FILE   = os.path.join(DATA_DIR, 'index_theme.json')
INDEX_THEME_BACKUP = os.path.join(DATA_DIR, 'index_theme_backup.json')
EXTERNAL_THEMES_FILE = 'themes_external_raw.json'
UNMATCHED_REPORT_FILE = 'unmatched_theme_words.json'

# Tema yang sudah ada manual sebelumnya (untuk dihindari tabrakan key)
# Jika rsalan ingin tema baru menimpa tema lama dengan nama sama, ubah PREFER_EXTERNAL=True
PREFIX_NEW_THEMES = 'ext_'   # prefix supaya tema hasil scrape tidak tabrakan nama
                              # dengan tema manual yang sudah ada (mis. "warna" vs "ext_colors")


def main():
    for f in [APP_WORDS_FILE, EXTERNAL_THEMES_FILE]:
        if not os.path.exists(f):
            print(f"[ERROR] File tidak ditemukan: {f}")
            sys.exit(1)

    print("[INFO] Memuat app_words.json ...")
    with open(APP_WORDS_FILE, 'r', encoding='utf-8') as f:
        app_words = json.load(f)

    # Index pencarian cepat: simplified -> id
    simplified_to_id = {}
    for w in app_words:
        simp = w.get('simplified') or w.get('id', '')
        word_id = w.get('id') or simp
        if simp:
            simplified_to_id[simp] = word_id

    print(f"[INFO] {len(app_words)} kata HSK dimuat, {len(simplified_to_id)} entri simplified unik.")

    print("[INFO] Memuat themes_external_raw.json ...")
    with open(EXTERNAL_THEMES_FILE, 'r', encoding='utf-8') as f:
        external_themes = json.load(f)

    # Muat index_theme.json yang sudah ada (kalau ada), backup dulu
    existing_themes = {}
    if os.path.exists(INDEX_THEME_FILE):
        with open(INDEX_THEME_FILE, 'r', encoding='utf-8') as f:
            existing_themes = json.load(f)
        shutil.copy(INDEX_THEME_FILE, INDEX_THEME_BACKUP)
        print(f"[INFO] index_theme.json lama di-backup ke {INDEX_THEME_BACKUP}")
    else:
        print("[INFO] index_theme.json belum ada, akan dibuat baru.")

    unmatched_report = {}
    total_matched = 0
    total_unmatched = 0
    themes_added = 0

    for slug, theme_data in external_themes.items():
        matched_ids = []
        unmatched_words = []

        for entry in theme_data.get('words', []):
            hanzi = entry.get('hanzi', '')
            word_id = simplified_to_id.get(hanzi)
            if word_id:
                if word_id not in matched_ids:
                    matched_ids.append(word_id)
                total_matched += 1
            else:
                unmatched_words.append(entry)
                total_unmatched += 1

        if not matched_ids:
            # Tema ini tidak punya kata yang match sama sekali, lewati
            if unmatched_words:
                unmatched_report[slug] = unmatched_words
            continue

        new_key = PREFIX_NEW_THEMES + slug
        existing_themes[new_key] = {
            'label_id': theme_data.get('label_en', slug),  # label_en dipakai sementara,
                                                              # rsalan bisa terjemahkan manual nanti
            'label_en': theme_data.get('label_en', slug),
            'words': matched_ids,
            'count': len(matched_ids),
            'source': theme_data.get('attribution', 'AllSet Learning Vocabulary Wiki'),
        }
        themes_added += 1

        if unmatched_words:
            unmatched_report[slug] = unmatched_words

    # Simpan index_theme.json gabungan
    with open(INDEX_THEME_FILE, 'w', encoding='utf-8') as f:
        json.dump(existing_themes, f, ensure_ascii=False, indent=2)

    # Simpan laporan kata yang tidak ketemu
    with open(UNMATCHED_REPORT_FILE, 'w', encoding='utf-8') as f:
        json.dump(unmatched_report, f, ensure_ascii=False, indent=2)

    print()
    print(f"[SELESAI] {INDEX_THEME_FILE} berhasil diperbarui.")
    print(f"          Tema baru ditambahkan      : {themes_added}")
    print(f"          Total tema sekarang        : {len(existing_themes)}")
    print(f"          Kata berhasil dicocokkan   : {total_matched}")
    print(f"          Kata TIDAK ditemukan       : {total_unmatched}  (lihat {UNMATCHED_REPORT_FILE})")
    print()
    print("[CATATAN] Tema baru diberi prefix 'ext_' (mis. 'ext_colors') supaya tidak")
    print("          tabrakan dengan tema manual yang sudah ada. رسلان bisa rename")
    print("          key atau terjemahkan label_id ke Bahasa Indonesia secara manual")
    print("          di index_theme.json kapan saja.")
    print()
    print("=== SAMPLE 5 TEMA BARU TERBESAR ===")
    new_only = {k: v for k, v in existing_themes.items() if k.startswith(PREFIX_NEW_THEMES)}
    for k, v in sorted(new_only.items(), key=lambda kv: -kv[1]['count'])[:5]:
        print(f"  {k}: {v['count']} kata cocok — \"{v['label_en']}\"")


if __name__ == '__main__':
    main()

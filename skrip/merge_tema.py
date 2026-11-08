# -*- coding: utf-8 -*-
"""
merge_tema.py — Mandarin Interaktif
======================================
Gabungkan tema SUMBER ke tema TUJUAN (dipakai setelah لihat laporan dari
audit_tema_overlap.py, atau kapan saja رسلان putuskan 2 tema memang sama).

WAJIB update 2 file sekaligus supaya konsisten:
  1. data/index_theme.json  -- gabung "words", jumlahkan "count", hapus key sumber
  2. data/app_words.json    -- tiap kata yg tag "themes"-nya berisi key sumber,
                                diganti jadi key tujuan (dedup kalau sudah ada keduanya)

CARA PAKAI (dari folder C:\\mandarin_app):
    python merge_tema.py <key_sumber> <key_tujuan>

    Contoh:
        python merge_tema.py ext_numeral angka
        (semua kata di "ext_numeral" akan pindah masuk "angka",
         lalu key "ext_numeral" dihapus dari index_theme.json)

    Tambahkan --dry-run buat lihat dulu apa yang AKAN terjadi tanpa
    benar-benar menulis apa pun:
        python merge_tema.py ext_numeral angka --dry-run

    Tambahkan --keep-source kalau mau tema sumber TETAP ada di
    index_theme.json (cuma kata-katanya digabung/disalin ke tujuan,
    tema sumber tidak dihapus):
        python merge_tema.py ext_numeral angka --keep-source

Backup otomatis dibuat untuk KEDUA file sebelum ditulis.
"""
import json
import sys
import shutil
import argparse
from pathlib import Path
from datetime import datetime

DATA_DIR = Path("data")
INDEX_THEME_PATH = DATA_DIR / "index_theme.json"
APP_WORDS_PATH = DATA_DIR / "app_words.json"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('source', help='key tema SUMBER (akan digabung lalu dihapus, kecuali --keep-source)')
    ap.add_argument('target', help='key tema TUJUAN (akan menampung gabungan kata)')
    ap.add_argument('--dry-run', action='store_true', help='cuma tampilkan apa yang akan terjadi, tidak menulis apa pun')
    ap.add_argument('--keep-source', action='store_true', help='jangan hapus tema sumber dari index_theme.json setelah digabung')
    args = ap.parse_args()

    if not INDEX_THEME_PATH.exists() or not APP_WORDS_PATH.exists():
        print("‼ FATAL: data/index_theme.json atau data/app_words.json tidak ditemukan.")
        print("   Jalankan skrip ini dari folder C:\\mandarin_app")
        sys.exit(1)

    with open(INDEX_THEME_PATH, encoding='utf-8') as f:
        themes = json.load(f)
    with open(APP_WORDS_PATH, encoding='utf-8') as f:
        words = json.load(f)

    if args.source not in themes:
        print(f'‼ FATAL: key sumber "{args.source}" tidak ada di index_theme.json')
        sys.exit(1)
    if args.target not in themes:
        print(f'‼ FATAL: key tujuan "{args.target}" tidak ada di index_theme.json')
        sys.exit(1)
    if args.source == args.target:
        print('‼ FATAL: sumber dan tujuan tidak boleh sama')
        sys.exit(1)

    src = themes[args.source]
    tgt = themes[args.target]

    src_words = set(src.get('words', []))
    tgt_words = set(tgt.get('words', []))
    merged_words = sorted(tgt_words | src_words)
    newly_added = sorted(src_words - tgt_words)

    print(f'Tema SUMBER : "{src.get("label_id")}" ({args.source}) -- {len(src_words)} kata')
    print(f'Tema TUJUAN : "{tgt.get("label_id")}" ({args.target}) -- {len(tgt_words)} kata')
    print(f'Setelah digabung -> {len(merged_words)} kata ({len(newly_added)} kata baru masuk ke tujuan)')
    if newly_added:
        print(f'  Kata yang baru masuk: {"、".join(newly_added[:15])}' + (' ...' if len(newly_added) > 15 else ''))

    # cari kata2 di app_words.json yang tag themes-nya menyebut key sumber
    affected_words = [w for w in words if args.source in (w.get('themes') or [])]
    print(f'\n{len(affected_words)} entri di app_words.json bertag "{args.source}" akan diupdate jadi "{args.target}"')

    if args.dry_run:
        print('\n[--dry-run] TIDAK ADA YANG DITULIS. Jalankan tanpa --dry-run untuk benar-benar eksekusi.')
        return

    # ── backup dulu ──
    ts = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_theme = INDEX_THEME_PATH.with_suffix(f'.json.bak_{ts}')
    backup_words = APP_WORDS_PATH.with_suffix(f'.json.bak_{ts}')
    shutil.copy2(INDEX_THEME_PATH, backup_theme)
    shutil.copy2(APP_WORDS_PATH, backup_words)
    print(f'\nBackup dibuat:\n  {backup_theme}\n  {backup_words}')

    # ── update index_theme.json ──
    tgt['words'] = merged_words
    tgt['count'] = len(merged_words)
    if not args.keep_source:
        del themes[args.source]
        print(f'Key "{args.source}" dihapus dari index_theme.json (kata-katanya sudah pindah ke "{args.target}")')
    else:
        print(f'Key "{args.source}" TETAP ada (--keep-source dipakai)')

    with open(INDEX_THEME_PATH, 'w', encoding='utf-8') as f:
        json.dump(themes, f, ensure_ascii=False, indent=2)

    # ── update app_words.json ──
    updated_count = 0
    for w in words:
        th = w.get('themes')
        if th and args.source in th:
            new_th = [t for t in th if t != args.source]
            if args.target not in new_th:
                new_th.append(args.target)
            w['themes'] = new_th
            updated_count += 1

    with open(APP_WORDS_PATH, 'w', encoding='utf-8') as f:
        json.dump(words, f, ensure_ascii=False, indent=1)

    print(f'\n{updated_count} entri app_words.json diupdate tag temanya.')
    print(f'index_theme.json: "{args.target}" sekarang {len(merged_words)} kata.')
    print('\nSELESAI. Ingat: F12 -> Application -> Storage -> Clear site data -> refresh')
    print('di browser supaya perubahan kelihatan (cache browser, bukan bug).')


if __name__ == "__main__":
    main()

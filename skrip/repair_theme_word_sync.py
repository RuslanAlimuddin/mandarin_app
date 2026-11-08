# -*- coding: utf-8 -*-
"""
repair_theme_word_sync.py — Mandarin Interaktif
===================================================
PERBAIKAN SEKALI-JALAN (bukan alat yang dipakai rutin). Menyamakan
index_theme.json <-> app_words.json yang sudah kadung tidak sinkron --
kemungkinan besar sisa impor tema generasi awal SEBELUM complete_theme_json.py
dibuat (script itu sendiri sudah benar, tidak menghasilkan masalah baru).

MASALAH YANG DIPERBAIKI:
  index_theme.json bilang kata X ada di tema Y (lewat field "words" di tema Y),
  tapi kata X sendiri di app_words.json field "themes"-nya TIDAK menyebut Y.
  Akibatnya: deck Flashcard utk tema Y bisa kosong (buildDeckQueue() baca
  w.themes per kata, bukan index_theme.json), walau Kamus/sidebar kelihatan
  tema itu "ada isinya" (karena baca index_theme.json langsung).

APA YANG DILAKUKAN SKRIP INI:
  Untuk tiap tema Y di index_theme.json, tiap kata X di "words"-nya:
    kalau kata X ADA di app_words.json TAPI field "themes"-nya belum
    menyebut Y -> tambahkan Y ke situ.
  TIDAK menghapus tag apa pun, TIDAK mengubah index_theme.json sama sekali
  -- cuma menambah tag yang KURANG di app_words.json. Searah, aman.

  Kata yang disebut di index_theme.json tapi TIDAK ADA SAMA SEKALI di
  app_words.json (harusnya jarang/tidak ada) akan dilaporkan terpisah,
  TIDAK bisa diperbaiki otomatis (butuh dicek manual -- mungkin salah ketik
  hanzi, atau memang belum pernah masuk app_words.json).

CARA PAKAI (dari folder C:\\mandarin_app):
    python repair_theme_word_sync.py --dry-run    <- lihat dulu apa yang AKAN berubah
    python repair_theme_word_sync.py               <- eksekusi beneran (backup otomatis)
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
    ap.add_argument('--dry-run', action='store_true', help='cuma tampilkan apa yang akan berubah, tidak menulis apa pun')
    args = ap.parse_args()

    if not INDEX_THEME_PATH.exists() or not APP_WORDS_PATH.exists():
        print("‼ FATAL: data/index_theme.json atau data/app_words.json tidak ditemukan.")
        print("   Jalankan skrip ini dari folder C:\\mandarin_app")
        sys.exit(1)

    with open(INDEX_THEME_PATH, encoding='utf-8') as f:
        themes = json.load(f)
    with open(APP_WORDS_PATH, encoding='utf-8') as f:
        words = json.load(f)

    word_by_simplified = {w['simplified']: w for w in words}

    to_fix = []       # (word_obj, hanzi, theme_key) -- akan ditambah tag-nya
    not_found = []     # (hanzi, theme_key) -- kata tidak ada sama sekali di app_words.json

    for theme_key, info in themes.items():
        for hanzi in info.get('words', []):
            w = word_by_simplified.get(hanzi)
            if w is None:
                not_found.append((hanzi, theme_key))
                continue
            current = set(w.get('themes') or [])
            if theme_key not in current:
                to_fix.append((w, hanzi, theme_key))

    # ringkasan per tema, biar رسلان bisa lihat tema mana yang paling parah
    per_theme_count = {}
    for _, _, tk in to_fix:
        per_theme_count[tk] = per_theme_count.get(tk, 0) + 1

    print(f"Memuat {len(themes)} tema, {len(words)} kata")
    print(f"\nTotal tag yang KURANG dan akan ditambahkan: {len(to_fix)}")
    print(f"Jumlah tema yang terpengaruh: {len(per_theme_count)}")
    if not_found:
        print(f"\n⚠ {len(not_found)} referensi kata di index_theme.json TIDAK KETEMU sama sekali di app_words.json")
        print("   (ini TIDAK diperbaiki otomatis -- perlu dicek manual, mungkin typo hanzi)")
        sample = not_found[:15]
        for hanzi, tk in sample:
            print(f'     "{hanzi}" (disebut di tema "{tk}")')
        if len(not_found) > 15:
            print(f'     ... (+{len(not_found) - 15} lagi, lihat laporan lengkap di file .txt)')

    print("\nTema paling banyak butuh perbaikan:")
    for tk, cnt in sorted(per_theme_count.items(), key=lambda x: -x[1])[:15]:
        label = themes[tk].get('label_id', tk)
        print(f'  {cnt:4d} kata  -- "{label}" ({tk})')

    if args.dry_run:
        print("\n[--dry-run] TIDAK ADA YANG DITULIS. Jalankan tanpa --dry-run untuk benar-benar eksekusi.")
        return

    if not to_fix:
        print("\nTidak ada yang perlu diperbaiki. Database sudah sinkron. 👍")
        return

    # ── backup dulu ──
    ts = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_words = APP_WORDS_PATH.with_suffix(f'.json.bak_{ts}')
    shutil.copy2(APP_WORDS_PATH, backup_words)
    print(f"\nBackup dibuat: {backup_words}")

    for w, hanzi, theme_key in to_fix:
        current = w.get('themes') or []
        current.append(theme_key)
        w['themes'] = current

    with open(APP_WORDS_PATH, 'w', encoding='utf-8') as f:
        json.dump(words, f, ensure_ascii=False, indent=1)

    ts_report = datetime.now().strftime('%Y%m%d_%H%M%S')
    report_lines = [f"=== LAPORAN repair_theme_word_sync.py — {datetime.now()} ==="]
    report_lines.append(f"{len(to_fix)} tag ditambahkan ke app_words.json\n")
    for tk, cnt in sorted(per_theme_count.items(), key=lambda x: -x[1]):
        label = themes[tk].get('label_id', tk)
        report_lines.append(f'{cnt:4d} kata -- "{label}" ({tk})')
    if not_found:
        report_lines.append(f"\n{len(not_found)} referensi kata TIDAK ketemu di app_words.json (cek manual):")
        for hanzi, tk in not_found:
            report_lines.append(f'  "{hanzi}" (tema: {tk})')
    report_path = Path(f"repair_theme_word_sync_report_{ts_report}.txt")
    report_path.write_text("\n".join(report_lines), encoding='utf-8')

    print(f"\nSELESAI. {len(to_fix)} tag berhasil ditambahkan ke {APP_WORDS_PATH}")
    print(f"Laporan lengkap: {report_path}")
    print("\nIngat: F12 -> Application -> Storage -> Clear site data -> refresh")
    print("di browser supaya perubahan kelihatan (cache browser, bukan bug).")
    print("\nSetelah ini, coba lagi deck 'Warna (Ext)' di Flashcard -- harusnya sudah ada kartunya.")


if __name__ == "__main__":
    main()

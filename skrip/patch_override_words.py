# -*- coding: utf-8 -*-
"""
patch_override_words.py — Mandarin Interaktif
=================================================
KOREKSI DARURAT: fix_app_words_readings.py (dijalankan sebelumnya) punya bug
-- utk kata yang SUDAH ada di tabel COMMON_READING_OVERRIDE (~25 karakter:
都,和,要,更,得,中,着,数,还,只,长,行,分,少,倒,重,难,当,校,传,曾,系,为,会,没),
jalur perbaikan "SEDANG" tidak menghormati tabel itu -- bisa salah pilih
bacaan/arti kalau ada kandidat lain yg KEBETULAN senada tapi beda arti
(cth nyata: "都" kepilih "dū=ibu kota" padahal seharusnya "dōu=semua" sesuai
COMMON_READING_OVERRIDE).

Script ini cek ULANG SEMUA kata di COMMON_READING_OVERRIDE (regardless posisi
sebelumnya sudah "kelihatan benar" atau tidak -- karena bug-nya bikin kata yg
salah pun jadi TIDAK KELIHATAN mencurigakan lagi utk audit biasa), lalu paksa
selaras dengan pick_best_cidict_entry() -- fungsi yang SAMA yang dipakai
complete_reading_json.py sendiri dan SUDAH menghormati tabel override.

CARA PAKAI (dari C:\\mandarin_app):
    python patch_override_words.py --dry-run     # WAJIB dicoba dulu
    python patch_override_words.py                # eksekusi, backup otomatis

Cuma 25 kata yang diperiksa -- laporannya singkat, gampang dibaca satu-satu.
"""
import sys
import json
import shutil
from pathlib import Path
from datetime import datetime
from collections import defaultdict

import complete_reading_json as crj


def load_all():
    app_words = crj.load_json(crj.APP_WORDS_PATH)
    cidict = crj.load_json(crj.CIDICT_PATH, required=False) or []
    grouped = defaultdict(list)
    for w in cidict:
        s = w.get('simplified')
        if s:
            grouped[s].append(w)
    app_words_by_simplified = {w.get('simplified'): w for w in app_words if w.get('simplified')}
    return app_words, app_words_by_simplified, grouped


def pick_override_target(candidates, target_py):
    """Cari kandidat yg pinyin-nya cocok persis dgn target override, TAPI
    tetap utamakan yg tidak langka (hindari kasus spt "中": override 'zhōng'
    kebetulan cocok teks dgn entri "(bentuk terikat) Tiongkok" yg langka DAN
    entri "di dalam" yg umum -- keduanya sama2 berbunyi zhōng)."""
    matches = [c for c in candidates
               if (c.get('pinyin') or '').strip().lower() == target_py.lower()]
    if not matches:
        return None
    non_rare = []
    for c in matches:
        meanings = c.get('meanings_id') or []
        first = (meanings[0] if meanings else '').lower()
        if not any(marker in first for marker in crj.DEPRIORITIZE_MARKERS):
            non_rare.append(c)
    return non_rare[0] if non_rare else matches[0]


def reorder_meanings(old_meanings, target_meanings):
    target_set = set(target_meanings)
    matched = [m for m in old_meanings if m in target_set]
    rest = [m for m in old_meanings if m not in target_set]
    return matched + rest, len(matched)


def main():
    dry_run = '--dry-run' in sys.argv

    app_words, by_simplified, grouped = load_all()
    print(f"Total kata di COMMON_READING_OVERRIDE: {len(crj.COMMON_READING_OVERRIDE)}")
    print(f"Mode: {'DRY-RUN (tidak menulis apa pun)' if dry_run else 'EKSEKUSI (akan menulis file)'}")
    print()

    fixes = []
    already_ok = []
    not_in_app_words = []
    manual_needed = []

    for hanzi, target_py in crj.COMMON_READING_OVERRIDE.items():
        entry = by_simplified.get(hanzi)
        if not entry:
            not_in_app_words.append(hanzi)
            continue

        candidates = grouped.get(hanzi)
        if not candidates:
            continue

        best = pick_override_target(candidates, target_py)
        if not best:
            manual_needed.append({
                'hanzi': hanzi, 'current_py': entry.get('pinyin', ''), 'correct_py': target_py,
                'target_meaning': '(TIDAK ADA kandidat cidict dgn bacaan ini -- cek manual)',
            })
            continue
        correct_py = best.get('pinyin', '')
        target_meanings = best.get('meanings_id') or []

        current_py = (entry.get('pinyin') or '').strip()
        old_meanings = entry.get('meanings_id') or []

        new_meanings, matched_count = reorder_meanings(old_meanings, target_meanings)

        py_changed = (current_py != correct_py)
        order_changed = (new_meanings != old_meanings)

        if matched_count == 0 and (py_changed or order_changed):
            manual_needed.append({
                'hanzi': hanzi, 'current_py': current_py, 'correct_py': correct_py,
                'target_meaning': target_meanings[0] if target_meanings else '',
            })
            continue

        if not py_changed and not order_changed:
            already_ok.append(hanzi)
            continue

        fixes.append({
            'hanzi': hanzi, 'old_py': current_py, 'new_py': correct_py,
            'new_numeric': best.get('pinyin_numeric', entry.get('pinyin_numeric', '')),
            'old_meaning0': old_meanings[0] if old_meanings else '',
            'new_meaning0': new_meanings[0] if new_meanings else '',
            'new_meanings': new_meanings, 'py_changed': py_changed,
            'entry': entry,
        })

    print(f"Sudah benar (tidak perlu diubah): {len(already_ok)} -> {', '.join(already_ok)}")
    print(f"Tidak ada di app_words.json: {len(not_in_app_words)} -> {', '.join(not_in_app_words) or '-'}")
    print(f"PERLU DIPERBAIKI: {len(fixes)}")
    print()
    for f in fixes:
        line = f"  \"{f['hanzi']}\": "
        if f['py_changed']:
            line += f"pinyin {f['old_py']} -> {f['new_py']}; "
        line += f"arti utama \"{f['old_meaning0']}\" -> \"{f['new_meaning0']}\""
        print(line)

    if manual_needed:
        print()
        print("PERLU DICEK MANUAL (dilewati, teks arti tidak ketemu persis):")
        for m in manual_needed:
            print(f"  \"{m['hanzi']}\": target py={m['correct_py']}, target arti=\"{m['target_meaning']}\"")

    ts = datetime.now().strftime('%Y%m%d_%H%M%S')
    if dry_run:
        print("\nDRY-RUN selesai. TIDAK ADA file data yang diubah.")
        return

    if not fixes:
        print("\nTidak ada perubahan untuk ditulis.")
        return

    backup_path = crj.APP_WORDS_PATH.with_suffix(f'.json.bak_override_{ts}')
    shutil.copy2(crj.APP_WORDS_PATH, backup_path)
    print(f"\nBackup dibuat: {backup_path}")

    for f in fixes:
        if f['py_changed']:
            f['entry']['pinyin'] = f['new_py']
            f['entry']['pinyin_numeric'] = f['new_numeric']
        f['entry']['meanings_id'] = f['new_meanings']

    with open(crj.APP_WORDS_PATH, 'w', encoding='utf-8') as fp:
        json.dump(app_words, fp, ensure_ascii=False, indent=1)

    print(f"SELESAI. {len(fixes)} entri dikoreksi ulang selaras COMMON_READING_OVERRIDE.")


if __name__ == "__main__":
    main()

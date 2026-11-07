# -*- coding: utf-8 -*-
"""
audit_app_words_readings.py — Mandarin Interaktif
====================================================
Laporan READ-ONLY (tidak mengubah data apa pun) — audit SISTEMATIS ke SELURUH
app_words.json, cari kata yang polanya mirip kasus historis "都"/"那"/"过" dkk:
field "pinyin" (atau meanings_id[0], arti default) kemungkinan kepilih dari
bacaan langka (marga/varian/sastra) padahal ADA alternatif bacaan yang lebih
umum tersedia di cidict_index.json untuk hanzi/kata yang sama.

Dua sinyal "mencurigakan" yang dipakai (independen, salah satu cukup):
  1. Huruf pertama field "pinyin" KAPITAL (konvensi dataset ini utk marga).
  2. meanings_id[0] (arti default) mengandung penanda kata seperti "marga ",
     "varian", "(sastra)", "nama keluarga", "(bentuk terikat)" -- sama persis
     DEPRIORITIZE_MARKERS yg dipakai complete_reading_json.py.

Kalau salah satu sinyal itu nyala, DAN cidict_index.json ternyata punya
kandidat bacaan lain yang TIDAK langka untuk hanzi/kata yang sama, baru
ditandai (skip kalau tidak ada pembanding -- berarti memang tidak ada
alternatif yg lebih baik, kemungkinan besar bukan bug).

Dipisah 2 tingkat keparahan:
  🔴 TINGGI  -- alternatif tak-langka itu NADA-nya BEDA dari yg tersimpan
                sekarang -> nada/pinyin kemungkinan salah total.
  🟠 SEDANG  -- alternatif tak-langka itu NADA-nya SAMA dgn yg tersimpan
                sekarang -> nada kemungkinan sudah benar, cuma arti
                default (meanings_id[0]) yg salah pilih.

Diurutkan per bucket berdasarkan field "frequency" (makin kecil = makin
sering dipakai = makin penting diprioritaskan diperbaiki).

CARA PAKAI (dari C:\\mandarin_app):
    python audit_app_words_readings.py                 # semua entri
    python audit_app_words_readings.py --hsk-only       # cuma yg ada tag HSK

Output: dicetak ke layar + disimpan sbg
  audit_app_words_readings_report_TIMESTAMP.txt
Tidak ada file data yang ditulis/diubah.
"""
import sys
import json
from pathlib import Path
from datetime import datetime
from collections import defaultdict

import complete_reading_json as crj  # reuse DEPRIORITIZE_MARKERS, load_json, path config

DATA_DIR = crj.DATA_DIR


def load_all():
    app_words = crj.load_json(crj.APP_WORDS_PATH)
    cidict = crj.load_json(crj.CIDICT_PATH, required=False) or []
    grouped = defaultdict(list)
    for w in cidict:
        s = w.get('simplified')
        if s:
            grouped[s].append(w)
    return app_words, grouped


def is_rare_reading(cidict_entry):
    meanings = cidict_entry.get('meanings_id') or []
    first = (meanings[0] if meanings else '').lower()
    return any(marker in first for marker in crj.DEPRIORITIZE_MARKERS)


def looks_suspicious(entry):
    py = (entry.get('pinyin') or '').strip()
    if py[:1].isupper():
        return True, f'pinyin diawali huruf kapital ("{py}")'
    meanings = entry.get('meanings_id') or []
    first = (meanings[0] if meanings else '')
    if any(marker in first.lower() for marker in crj.DEPRIORITIZE_MARKERS):
        return True, f'arti default terlihat langka: "{first}"'
    return False, None


def audit_word(entry, grouped):
    word = entry.get('simplified', '')
    py = (entry.get('pinyin') or '').strip()
    suspicious, reason = looks_suspicious(entry)
    if not suspicious:
        return None

    candidates = grouped.get(word)
    if not candidates or len(candidates) <= 1:
        return None  # tidak ada pembanding -> tidak actionable

    non_rare = [c for c in candidates if not is_rare_reading(c)]
    if not non_rare:
        return None  # semua kandidat sama2 "langka" -> mungkin memang begitu adanya

    same_tone_alt = [c for c in non_rare if (c.get('pinyin') or '').strip().lower() == py.lower()]
    diff_tone_alt = [c for c in non_rare if (c.get('pinyin') or '').strip().lower() != py.lower()]

    # Kalau ADA alternatif tak-langka dgn nada yg SAMA persis spt yg tersimpan
    # sekarang -> nada itu sendiri sebenarnya valid/umum, cuma arti default
    # (meanings_id[0]) yg salah pilih -> SEDANG. Baru kalau tidak ada satupun
    # alternatif tak-langka yg nadanya sama -> nada itu sendiri patut dicurigai -> TINGGI.
    if same_tone_alt:
        severity = 'sedang'
        alts = same_tone_alt
    else:
        severity = 'tinggi'
        alts = diff_tone_alt

    alt_desc = "; ".join(
        f"{c.get('pinyin', '?')} ({(c.get('meanings_id') or ['-'])[0]})" for c in alts
    )
    meanings = entry.get('meanings_id') or []
    return {
        'severity': severity,
        'word': word,
        'current_py': py,
        'current_meaning': meanings[0] if meanings else '',
        'reason': reason,
        'alternatives': alt_desc,
        'hsk': entry.get('hsk'),
        'frequency': entry.get('frequency'),
    }


def format_item(it):
    freq = it['frequency'] if it['frequency'] is not None else '?'
    hsk = it['hsk'] if it['hsk'] else '-'
    lines = [
        f"  - \"{it['word']}\" (tersimpan: {it['current_py']} -- \"{it['current_meaning']}\") "
        f"[HSK{hsk}, freq={freq}]",
        f"      alasan dicurigai: {it['reason']}",
        f"      alternatif tak-langka: {it['alternatives']}",
    ]
    return "\n".join(lines)


def main():
    hsk_only = '--hsk-only' in sys.argv

    app_words, grouped = load_all()
    print(f"Total app_words.json: {len(app_words)} entri")
    if hsk_only:
        print("Mode: hanya entri yang punya tag HSK")

    findings = {'tinggi': [], 'sedang': []}
    for entry in app_words:
        if hsk_only and not entry.get('hsk'):
            continue
        result = audit_word(entry, grouped)
        if result:
            findings[result['severity']].append(result)

    for key in findings:
        findings[key].sort(key=lambda it: (it['frequency'] is None, it['frequency'] or 0))

    report_lines = [f"=== LAPORAN audit_app_words_readings.py — {datetime.now()} ==="]
    report_lines.append(f"Total entri app_words.json diperiksa: {len(app_words)}"
                         + (" (mode --hsk-only)" if hsk_only else ""))
    report_lines.append(f"Ditemukan TINGGI (nada kemungkinan salah total): {len(findings['tinggi'])}")
    report_lines.append(f"Ditemukan SEDANG (nada ok, arti default kemungkinan salah): {len(findings['sedang'])}")
    report_lines.append("")

    report_lines.append("═══ 🔴 PRIORITAS TINGGI — nada/pinyin kemungkinan salah total ═══")
    report_lines.append("(diurutkan dari kata paling sering dipakai)")
    report_lines.append("")
    for it in findings['tinggi']:
        report_lines.append(format_item(it))
    report_lines.append("")

    report_lines.append("═══ 🟠 PRIORITAS SEDANG — nada kemungkinan ok, arti default kemungkinan salah urutan ═══")
    report_lines.append("(diurutkan dari kata paling sering dipakai)")
    report_lines.append("")
    for it in findings['sedang']:
        report_lines.append(format_item(it))
    report_lines.append("")

    report_text = "\n".join(report_lines)
    print(report_text)

    ts = datetime.now().strftime('%Y%m%d_%H%M%S')
    out_path = Path(f"audit_app_words_readings_report_{ts}.txt")
    out_path.write_text(report_text, encoding='utf-8')
    print(f"\nLaporan disimpan: {out_path}")
    print("\nTidak ada file data yang diubah -- ini murni laporan buat review manual.")


if __name__ == "__main__":
    main()

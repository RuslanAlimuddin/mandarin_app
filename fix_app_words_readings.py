# -*- coding: utf-8 -*-
"""
fix_app_words_readings.py — Mandarin Interaktif
==================================================
Perbaiki app_words.json berdasarkan temuan audit_app_words_readings.py:
kata yang bacaan/arti default-nya kepilih dari entri langka (marga/varian/
sastra) padahal ADA alternatif yang lebih umum di cidict_index.json.

APA YANG DIUBAH per kategori:
  🔴 TINGGI (nada kemungkinan salah total):
     - field "pinyin" & "pinyin_numeric" DIGANTI ke bacaan yang benar
       (dipilih pakai pick_best_cidict_entry() -- fungsi yg SAMA persis
       dipakai complete_reading_json.py, jadi konsisten dgn override yg
       sudah ada di COMMON_READING_OVERRIDE kalau relevan).
     - "meanings_id": arti yang cocok dgn bacaan baru dipindah ke DEPAN
       (TIDAK dihapus apa pun, cuma reorder).

  🟠 SEDANG (nada sudah benar, arti default yg salah urutan):
     - "pinyin" & "pinyin_numeric" TIDAK diubah.
     - "meanings_id": arti yang lebih umum (nada sama) dipindah ke DEPAN.

CATATAN PENTING -- KETERBATASAN YANG DISENGAJA:
  - "meanings_en" TIDAK ikut di-reorder. cidict_index.json cuma punya
    meanings_id (tidak ada versi Inggris), dan meanings_id vs meanings_en
    di app_words.json TERNYATA TIDAK selalu selaras index-nya (ada beberapa
    kata yg meanings_id-nya 1 entri lebih banyak dari meanings_en) --
    reorder otomatis di sini berisiko salah pasang. Kalau رسلان perlu
    meanings_en ikut rapi, itu perlu ditangani terpisah (manual atau
    pendekatan lain), BUKAN oleh script ini.
  - "bopomofo" TIDAK ikut diperbarui utk entri TINGGI (cidict_index.json
    tidak punya field bopomofo utk didapatkan ulang). Kemungkinan jadi
    tidak sinkron dgn pinyin baru -- kalau bopomofo dipakai di UI, cek
    manual utk entri TINGGI yg diproses.
  - Kalau teks arti pengganti TIDAK ketemu persis di dalam meanings_id
    entri yg ada (harusnya jarang terjadi), entri itu DILEWATI (tidak
    diubah) dan dicatat di laporan sbg "PERLU DICEK MANUAL" -- supaya
    tidak asal tebak.

CARA PAKAI (dari C:\\mandarin_app):
    python fix_app_words_readings.py --dry-run     # WAJIB dicoba dulu,
                                                      lihat laporan, TIDAK
                                                      menulis apa pun
    python fix_app_words_readings.py                # eksekusi beneran,
                                                      backup otomatis dibuat
                                                      dulu

Bisa juga dibatasi ke kata tertentu saja (misal buat mulai dari 26 TINGGI
dulu sebelum menyentuh yang SEDANG):
    python fix_app_words_readings.py --dry-run --severity tinggi
    python fix_app_words_readings.py --severity tinggi
"""
import sys
import json
import shutil
from pathlib import Path
from datetime import datetime
from collections import defaultdict

import complete_reading_json as crj
import audit_app_words_readings as audit


def load_all():
    app_words = crj.load_json(crj.APP_WORDS_PATH)
    cidict = crj.load_json(crj.CIDICT_PATH, required=False) or []
    grouped = defaultdict(list)
    for w in cidict:
        s = w.get('simplified')
        if s:
            grouped[s].append(w)
    return app_words, grouped


def reorder_meanings(old_meanings, target_meanings):
    """Pindahkan item di old_meanings yg teksnya cocok persis dgn salah satu
    item di target_meanings ke DEPAN, sisanya tetap di urutan asal.
    Return (new_meanings, matched_count)."""
    target_set = set(target_meanings)
    matched = [m for m in old_meanings if m in target_set]
    rest = [m for m in old_meanings if m not in target_set]
    return matched + rest, len(matched)


def compute_fix(entry, grouped):
    """Return dict rencana perubahan, atau None kalau tidak perlu/tidak bisa diubah."""
    result = audit.audit_word(entry, grouped)
    if not result:
        return None

    word = result['word']
    severity = result['severity']
    candidates = grouped.get(word) or []
    py_now = (entry.get('pinyin') or '').strip()
    old_meanings = entry.get('meanings_id') or []

    # PENTING: kalau kata ini ADA di COMMON_READING_OVERRIDE, tabel itu MUTLAK
    # menang -- jangan biarkan heuristik "nada sama" (jalur sedang) memilih
    # kandidat lain yg kebetulan senada tapi BUKAN yg dimaksud override
    # (bug historis: "都" pernah kepilih "dū=ibu kota" krn senada dgn "Dū",
    # padahal override minta "dōu"=semua, beda nada sama sekali).
    override_py = crj.COMMON_READING_OVERRIDE.get(word)
    if override_py:
        matches = [c for c in candidates
                   if (c.get('pinyin') or '').strip().lower() == override_py.lower()]
        non_rare_matches = [c for c in matches if not audit.is_rare_reading(c)]
        best = (non_rare_matches[0] if non_rare_matches else
                (matches[0] if matches else None))
        if not best:
            return {'status': 'perlu_manual', 'word': word, 'severity': severity,
                    'reason': f'tidak ketemu kandidat cidict utk override "{override_py}"'}
        new_py = best.get('pinyin', '')
        new_numeric = best.get('pinyin_numeric', '')
        target_meanings = best.get('meanings_id') or []
    elif severity == 'tinggi':
        best = crj.pick_best_cidict_entry(candidates, word)
        new_py = best.get('pinyin', '')
        new_numeric = best.get('pinyin_numeric', '')
        target_meanings = best.get('meanings_id') or []
    else:  # sedang -- nada tidak berubah, cuma reorder arti
        non_rare_same_tone = [
            c for c in candidates
            if not audit.is_rare_reading(c) and (c.get('pinyin') or '').strip().lower() == py_now.lower()
        ]
        if not non_rare_same_tone:
            return None  # jaga-jaga, seharusnya tidak terjadi
        best = non_rare_same_tone[0]
        # normalisasi huruf kapital di depan (indikasi marga) -> huruf kecil,
        # karena arti utama yg baru sudah bukan marga lagi
        new_py = py_now[:1].lower() + py_now[1:] if py_now[:1].isupper() else py_now
        new_numeric = entry.get('pinyin_numeric', '')
        target_meanings = best.get('meanings_id') or []

    new_meanings, matched_count = reorder_meanings(old_meanings, target_meanings)
    if matched_count == 0:
        return {'status': 'perlu_manual', 'word': word, 'severity': severity,
                'reason': 'arti pengganti tidak ketemu persis di meanings_id yang ada'}

    changed_py = (new_py != py_now)  # sensitif kapitalisasi -- normalisasi huruf kecil dianggap perubahan juga
    changed_order = (new_meanings != old_meanings)
    if not changed_py and not changed_order:
        return None  # sudah benar, tidak ada yg perlu diubah

    return {
        'status': 'fix', 'word': word, 'severity': severity,
        'old_py': py_now, 'new_py': new_py,
        'new_numeric': new_numeric,
        'old_meanings0': old_meanings[0] if old_meanings else '',
        'new_meanings0': new_meanings[0] if new_meanings else '',
        'new_meanings': new_meanings,
        'changed_py': changed_py,
    }


def main():
    args = sys.argv[1:]
    dry_run = '--dry-run' in args
    severity_filter = None
    if '--severity' in args:
        severity_filter = args[args.index('--severity') + 1].lower()

    app_words, grouped = load_all()
    print(f"Total app_words.json: {len(app_words)} entri")
    print(f"Mode: {'DRY-RUN (tidak menulis apa pun)' if dry_run else 'EKSEKUSI (akan menulis file)'}")
    if severity_filter:
        print(f"Filter tingkat keparahan: {severity_filter}")

    fixes = []
    manual_needed = []

    for entry in app_words:
        plan = compute_fix(entry, grouped)
        if not plan:
            continue
        if severity_filter and plan['severity'] != severity_filter:
            continue
        if plan['status'] == 'perlu_manual':
            manual_needed.append(plan)
        else:
            fixes.append((entry, plan))

    report_lines = [f"=== LAPORAN fix_app_words_readings.py — {datetime.now()} ==="]
    report_lines.append(f"Mode: {'DRY-RUN' if dry_run else 'EKSEKUSI'}"
                         + (f" (filter: {severity_filter})" if severity_filter else ""))
    report_lines.append(f"Total entri akan diperbaiki: {len(fixes)}")
    report_lines.append(f"Total entri PERLU DICEK MANUAL (dilewati): {len(manual_needed)}")
    report_lines.append("")

    report_lines.append("--- PERUBAHAN ---")
    for entry, plan in fixes:
        tag = '🔴' if plan['severity'] == 'tinggi' else '🟠'
        line = f"{tag} \"{plan['word']}\": "
        if plan['changed_py']:
            line += f"pinyin {plan['old_py']} -> {plan['new_py']}; "
        line += f"arti utama \"{plan['old_meanings0']}\" -> \"{plan['new_meanings0']}\""
        report_lines.append(line)

    if manual_needed:
        report_lines.append("")
        report_lines.append("--- PERLU DICEK MANUAL (dilewati, tidak diubah) ---")
        for plan in manual_needed:
            report_lines.append(f"  \"{plan['word']}\" ({plan['severity']}): {plan['reason']}")

    report_text = "\n".join(report_lines)
    print(report_text)

    ts = datetime.now().strftime('%Y%m%d_%H%M%S')
    report_path = Path(f"fix_app_words_readings_report_{ts}.txt")
    report_path.write_text(report_text, encoding='utf-8')
    print(f"\nLaporan disimpan: {report_path}")

    if dry_run:
        print("\nDRY-RUN selesai. TIDAK ADA file data yang diubah.")
        print("Kalau hasilnya sudah sesuai, jalankan lagi TANPA --dry-run untuk eksekusi beneran.")
        return

    if not fixes:
        print("\nTidak ada perubahan untuk ditulis.")
        return

    # ── tulis balik (dgn backup dulu) ──
    backup_path = crj.APP_WORDS_PATH.with_suffix(f'.json.bak_{ts}')
    shutil.copy2(crj.APP_WORDS_PATH, backup_path)
    print(f"Backup dibuat: {backup_path}")

    for entry, plan in fixes:
        if plan['changed_py']:
            entry['pinyin'] = plan['new_py']
            entry['pinyin_numeric'] = plan['new_numeric']
        entry['meanings_id'] = plan['new_meanings']

    with open(crj.APP_WORDS_PATH, 'w', encoding='utf-8') as f:
        json.dump(app_words, f, ensure_ascii=False, indent=1)

    print(f"\nSELESAI. {len(fixes)} entri di app_words.json sudah diperbarui.")
    print("Langkah berikutnya: jalankan repair_glossary.py untuk regenerasi ulang")
    print("glossary di entri graded_readers.json yang mungkin terdampak kata-kata ini.")


if __name__ == "__main__":
    main()

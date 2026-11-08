# -*- coding: utf-8 -*-
"""
repair_glossary.py — Mandarin Interaktif (v2 -- SCOPED)
============================================================
PERBAIKAN PENTING dari versi sebelumnya: versi lama mempercayai SELURUH
app_words.json sekarang sbg kebenaran mutlak, lalu sync SEMUA perbedaan ke
graded_readers.json. Ini BERBAHAYA -- ada kata (mis. "号","看","说","带")
yang app_words.json-nya punya masalah data SENDIRI, TIDAK TERKAIT dgn
audit_app_words_readings.py/fix_app_words_readings.py/patch_override_words.py
yg sudah kita jalankan. Sync membabi-buta akan menimpa glossary yg SUDAH
BENAR dgn versi yg lebih salah.

Versi ini SCOPED: cuma sync kata yang TERVERIFIKASI berubah (dibandingkan
file app_words.json SEBELUM proses perbaikan dimulai -- file backup). Kata
lain, walaupun beda dari lookup sekarang, TIDAK disentuh -- di luar cakupan
yang sudah kita validasi bersama.

CARA PAKAI (dari C:\\mandarin_app) -- WAJIB isi --baseline dgn path backup
app_words.json SEBELUM proses perbaikan dimulai (yg dibuat otomatis oleh
fix_app_words_readings.py saat eksekusi pertama, biasanya nama file mirip
"data\\app_words.json.bak_20260729_221158"):

    python repair_glossary.py --dry-run --baseline data\\app_words.json.bak_20260729_221158
    python repair_glossary.py --baseline data\\app_words.json.bak_20260729_221158

Output: laporan lengkap disimpan sbg repair_glossary_report_TIMESTAMP.txt,
termasuk daftar "MASIH TERLIHAT MENCURIGAKAN" -- kata yg kita perbaiki tapi
arti barunya SENDIRI masih terlihat kurang wajar (spt kasus "上" yg hasil
perbaikannya jadi "digunakan dalam 上聲" -- bukan perbaikan yg bagus juga).
Kata-kata itu TETAP disinkronkan (drpd dibiarkan versi lama yg juga salah),
TAPI ditandai supaya رسلان bisa cek & perbaiki manual di app_words.json
terpisah, lalu jalankan ulang script ini (aman, idempotent).
"""
import sys
import json
import shutil
from pathlib import Path
from datetime import datetime

import complete_reading_json as crj

# Penanda tambahan KHUSUS utk sanity-check pasca-perbaikan -- sengaja
# dibatasi cuma 1 pola baru (bukan expand besar2an) supaya tidak salah
# tandai kata2 yg justru sudah benar sbg nama tempat/singkatan (banyak
# di antara 430 perbaikan kemarin yg itu memang arti aslinya yg benar).
POST_FIX_SANITY_MARKERS = ('digunakan dalam', 'singkatan dari')


def load_all(baseline_path):
    old_app_words = crj.load_json(baseline_path)
    new_app_words = crj.load_json(crj.APP_WORDS_PATH)
    cidict = crj.load_json(crj.CIDICT_PATH, required=False) or []
    lookup_now = crj.build_lookup(new_app_words, cidict)

    old_by_word = {w['simplified']: w for w in old_app_words if w.get('simplified')}

    verified_changed = set()
    still_suspicious = []
    for w in new_app_words:
        word = w.get('simplified')
        if not word:
            continue
        old = old_by_word.get(word)
        if not old:
            continue  # kata baru yg tdk ada di baseline -> di luar cakupan, skip
        old_py = old.get('pinyin', '')
        new_py = w.get('pinyin', '')
        old_meanings = old.get('meanings_id') or []
        new_meanings = w.get('meanings_id') or []
        old_m0 = old_meanings[0] if old_meanings else ''
        new_m0 = new_meanings[0] if new_meanings else ''
        if old_py != new_py or old_m0 != new_m0:
            verified_changed.add(word)
            if any(marker in new_m0.lower() for marker in POST_FIX_SANITY_MARKERS):
                still_suspicious.append({'word': word, 'old_py': old_py, 'new_py': new_py,
                                          'old_m0': old_m0, 'new_m0': new_m0})

    gr_raw = crj.load_json(crj.GRADED_READER_PATH)
    is_dict_wrapped = isinstance(gr_raw, dict)
    passages = gr_raw['passages'] if is_dict_wrapped else gr_raw

    return gr_raw, passages, lookup_now, verified_changed, still_suspicious


def compute_entry_changes(entry, lookup_now, verified_changed):
    change_log = []
    new_glossary = []
    changed = False

    for item in entry.get('glossary', []):
        cn = item.get('cn', '')
        old_py = item.get('py', '')
        old_id = item.get('id', '')
        new_item = dict(item)

        if cn in verified_changed:
            now = lookup_now.get(cn)
            if now and (now.get('py', '') != old_py or now.get('id', '') != old_id):
                new_item['py'] = now.get('py', old_py)
                new_item['id'] = now.get('id', old_id)
                change_log.append({
                    'cn': cn, 'old_py': old_py, 'new_py': new_item['py'],
                    'old_id': old_id, 'new_id': new_item['id'],
                })
                changed = True
        # kata di luar verified_changed -- SENGAJA tidak disentuh sama sekali,
        # apa pun perbedaannya dgn lookup_now (di luar cakupan yg divalidasi)

        new_glossary.append(new_item)

    return changed, new_glossary, change_log


def main():
    dry_run = '--dry-run' in sys.argv
    if '--baseline' not in sys.argv:
        print("‼ WAJIB isi --baseline <path_file_backup_app_words.json_sebelum_perbaikan>")
        print("  Contoh: python repair_glossary.py --dry-run --baseline data\\app_words.json.bak_20260729_221158")
        sys.exit(1)
    baseline_path = Path(sys.argv[sys.argv.index('--baseline') + 1])
    if not baseline_path.exists():
        print(f"‼ File baseline tidak ditemukan: {baseline_path}")
        sys.exit(1)

    exclude_words = set()
    if '--exclude' in sys.argv:
        idx = sys.argv.index('--exclude') + 1
        while idx < len(sys.argv) and not sys.argv[idx].startswith('--'):
            exclude_words.add(sys.argv[idx])
            idx += 1
        print(f"Kata yg DIKECUALIKAN dari sync run ini: {', '.join(exclude_words)}")

    gr_raw, passages, lookup_now, verified_changed, still_suspicious = load_all(baseline_path)
    verified_changed -= exclude_words
    still_suspicious = [s for s in still_suspicious if s['word'] not in exclude_words]
    print(f"Baseline: {baseline_path}")
    print(f"Kata TERVERIFIKASI berubah (cakupan perbaikan kita): {len(verified_changed)}")
    print(f"Total entri graded_readers.json: {len(passages)}")
    print(f"Mode: {'DRY-RUN (tidak menulis apa pun)' if dry_run else 'EKSEKUSI (akan menulis file)'}")
    print()

    entries_changed = 0
    words_changed_total = 0
    report_lines = [f"=== LAPORAN repair_glossary.py (v2, scoped) — {datetime.now()} ==="]
    report_lines.append(f"Baseline: {baseline_path}")
    report_lines.append(f"Mode: {'DRY-RUN' if dry_run else 'EKSEKUSI'}")
    report_lines.append(f"Kata dlm cakupan (verified_changed): {len(verified_changed)}")
    report_lines.append(f"Total entri diperiksa: {len(passages)}")
    report_lines.append("")

    if still_suspicious:
        report_lines.append("⚠ MASIH TERLIHAT MENCURIGAKAN SETELAH DIPERBAIKI (tetap disinkronkan di bawah,")
        report_lines.append("  tapi disarankan رسلان cek manual di app_words.json terpisah):")
        for s in still_suspicious:
            report_lines.append(f"  - \"{s['word']}\": {s['old_py']!r}/{s['old_m0']!r} -> {s['new_py']!r}/{s['new_m0']!r}")
        report_lines.append("")

    for entry in passages:
        changed, new_glossary, change_log = compute_entry_changes(entry, lookup_now, verified_changed)
        if not changed:
            continue
        entries_changed += 1
        words_changed_total += len(change_log)
        header = f"=== {entry.get('id')} — \"{entry.get('title')}\" (HSK{entry.get('level')}, {entry.get('type', 'bacaan')}) ==="
        report_lines.append(header)
        for c in change_log:
            report_lines.append(
                f"  - \"{c['cn']}\": py {c['old_py']!r} -> {c['new_py']!r} | "
                f"arti {c['old_id']!r} -> {c['new_id']!r}"
            )
        report_lines.append("")
        if not dry_run:
            entry['glossary'] = new_glossary

    summary = (
        f"--- RINGKASAN ---\n"
        f"Entri diperiksa       : {len(passages)}\n"
        f"Entri berubah         : {entries_changed}\n"
        f"Total kata diperbarui : {words_changed_total}\n"
        f"Masih mencurigakan    : {len(still_suspicious)} (lihat daftar di atas)\n"
    )
    report_lines.append(summary)
    report_text = "\n".join(report_lines)
    print(report_text)

    ts = datetime.now().strftime('%Y%m%d_%H%M%S')
    report_path = Path(f"repair_glossary_report_{ts}.txt")
    report_path.write_text(report_text, encoding='utf-8')
    print(f"Laporan disimpan: {report_path}")

    if dry_run:
        print("\nDRY-RUN selesai. TIDAK ADA file data yang diubah.")
        return

    if entries_changed == 0:
        print("\nTidak ada perubahan untuk ditulis.")
        return

    backup_path = crj.GRADED_READER_PATH.with_suffix(f'.json.bak_{ts}')
    shutil.copy2(crj.GRADED_READER_PATH, backup_path)
    print(f"Backup dibuat: {backup_path}")

    with open(crj.GRADED_READER_PATH, 'w', encoding='utf-8') as f:
        json.dump(gr_raw, f, ensure_ascii=False, indent=1)

    print(f"\nSELESAI. {entries_changed} entri ({words_changed_total} kata) diperbarui di graded_readers.json.")


if __name__ == "__main__":
    main()

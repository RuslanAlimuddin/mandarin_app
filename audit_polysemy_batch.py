# -*- coding: utf-8 -*-
"""
audit_polysemy_batch.py — Mandarin Interaktif
================================================
Laporan READ-ONLY (tidak mengubah data apa pun) untuk bantu رسلان review
manual kata-kata yang BERISIKO salah bacaan/arti di entri graded_readers.json
yang belum pernah dicek satu-satu -- khususnya kata/karakter yang di
cidict_index.json punya >1 varian pinyin berbeda (marga/sastra/modern dll,
lihat COMMON_READING_OVERRIDE & pick_best_cidict_entry() di
complete_reading_json.py untuk konteks masalahnya).

Cara kerja: baca ulang field "glossary" yang SUDAH TERSIMPAN di tiap entri
(bukan re-tokenisasi dari nol -- supaya tidak salah tandai nama tokoh yang
field "names"-nya sudah tidak tersimpan di entri final), lalu:
  1. Kata yang di cidict_index.json cuma py 1 macam -> aman, dilewati.
  2. Kata yang sudah ada di COMMON_READING_OVERRIDE -> aman, dilewati.
  3. Sisanya dibandingkan dengan hasil build_lookup() versi SEKARANG:
     - cocok & sumber cidict fallback         -> [TINGGI] belum tervalidasi
     - cocok & sumber app_words.json tapi pola -> [SEDANG] pola spt kasus "都"
       mirip kasus historis (bacaan yg dipakai
       kelihatan langka/marga/sastra padahal
       ada alternatif umum)
     - TIDAK cocok dgn lookup sekarang         -> [INFO] kemungkinan override
                                                    nama tokoh (aman) ATAU
                                                    data referensi berubah

CARA PAKAI (dari C:\\mandarin_app, sejajar dgn complete_reading_json.py):
    python audit_polysemy_batch.py                     # audit SEMUA entri
    python audit_polysemy_batch.py --last 19            # 19 entri TERAKHIR
    python audit_polysemy_batch.py --ids id1 id2 id3    # entri tertentu

Output: laporan dicetak ke layar + disimpan sbg
  audit_polysemy_batch_report_TIMESTAMP.txt
Tidak ada file data yang ditulis/diubah.
"""
import sys
import re
from pathlib import Path
from datetime import datetime
from collections import defaultdict

import complete_reading_json as crj  # reuse persis: build_lookup, load_json, path config, dll.

SENTENCE_SPLIT_RE = re.compile(r'(?<=[。！？])')


def load_all():
    app_words = crj.load_json(crj.APP_WORDS_PATH)
    cidict = crj.load_json(crj.CIDICT_PATH, required=False) or []
    lookup_now = crj.build_lookup(app_words, cidict)

    grouped = defaultdict(list)
    for w in cidict:
        s = w.get('simplified')
        if s:
            grouped[s].append(w)

    gr_data = crj.load_json(crj.GRADED_READER_PATH)
    passages = gr_data['passages'] if isinstance(gr_data, dict) else gr_data
    return passages, grouped, lookup_now


def select_entries(passages, args):
    if args.ids:
        wanted = set(args.ids)
        selected = [p for p in passages if p.get('id') in wanted]
        missing = wanted - set(p.get('id') for p in selected)
        for m in missing:
            print(f"  (peringatan: id '{m}' tidak ditemukan di graded_readers.json)")
        return selected
    if args.last:
        return passages[-args.last:]
    return passages


def get_context_segments(entry):
    """List of (label, text) potongan teks asli entri, buat cari konteks kalimat."""
    if entry.get('type') == 'percakapan':
        return [(t.get('speaker', '?'), t.get('cn', '')) for t in entry.get('turns', [])]
    return [(None, entry.get('text', ''))]


def find_context_snippet(word, segments):
    """Cari 1 contoh kalimat (dipecah per tanda baca akhir) yang mengandung 'word'."""
    for label, seg in segments:
        if word not in seg:
            continue
        for sentence in SENTENCE_SPLIT_RE.split(seg):
            if word in sentence:
                prefix = f"{label}: " if label else ""
                return f"{prefix}{sentence.strip()}"
        prefix = f"{label}: " if label else ""
        return f"{prefix}{seg.strip()}"
    return None


def count_occurrences(word, segments):
    return sum(seg.count(word) for _, seg in segments)


def is_rare_reading(cidict_entry):
    meanings = cidict_entry.get('meanings_id') or []
    first = (meanings[0] if meanings else '').lower()
    return any(marker in first for marker in crj.DEPRIORITIZE_MARKERS)


def audit_entry(entry, grouped, lookup_now):
    """Kembalikan dict {'tinggi': [...], 'sedang': [...], 'info': [...]} berisi temuan."""
    findings = {'tinggi': [], 'sedang': [], 'info': []}
    segments = get_context_segments(entry)
    seen_words = set()

    for g in entry.get('glossary', []):
        word = g.get('cn', '')
        stored_py = (g.get('py') or '').strip()
        if not word or word in seen_words:
            continue
        seen_words.add(word)

        candidates = grouped.get(word)
        if not candidates:
            continue  # tidak ada di cidict sama sekali (murni app_words / nama) -> tidak relevan di sini
        distinct_pys = set((c.get('pinyin') or '').strip().lower() for c in candidates)
        if len(distinct_pys) <= 1:
            continue  # tidak ambigu
        if word in crj.COMMON_READING_OVERRIDE:
            continue  # sudah ditangani

        now = lookup_now.get(word)
        alt_desc = "; ".join(
            f"{c.get('pinyin', '?')} ({(c.get('meanings_id') or ['-'])[0]})"
            for c in candidates
        )
        occ = count_occurrences(word, segments)
        ctx = find_context_snippet(word, segments)
        item = {
            'word': word, 'stored_py': stored_py, 'occurrences': occ,
            'context': ctx, 'alternatives': alt_desc,
        }

        if now and stored_py.lower() == (now.get('py') or '').strip().lower():
            if now.get('source') == 'cidict_index.json':
                item['note'] = 'dipilih otomatis dari cidict (fallback), belum divalidasi manusia'
                findings['tinggi'].append(item)
            elif now.get('source') == 'app_words.json':
                chosen = next((c for c in candidates
                                if (c.get('pinyin') or '').strip().lower() == stored_py.lower()), None)
                has_non_rare_alt = any(
                    not is_rare_reading(c) and (c.get('pinyin') or '').strip().lower() != stored_py.lower()
                    for c in candidates
                )
                if chosen and is_rare_reading(chosen) and has_non_rare_alt:
                    item['note'] = 'bacaan di app_words.json terlihat langka/marga/sastra, ada alternatif umum -- pola spt kasus "都"'
                    findings['sedang'].append(item)
                # kalau app_words.json & bukan pola langka -> dianggap aman, tidak dilaporkan
        else:
            item['note'] = 'beda dari hasil lookup saat ini -- kemungkinan override nama tokoh (aman), atau data referensi berubah sejak entri dibuat'
            findings['info'].append(item)

    return findings


def format_entry_report(entry, findings):
    lines = []
    total = sum(len(v) for v in findings.values())
    if total == 0:
        return None
    header = f"=== {entry.get('id')} — \"{entry.get('title')}\" (HSK{entry.get('level')}, {entry.get('type', 'bacaan')}) ==="
    lines.append(header)

    def block(label, key, icon):
        items = findings[key]
        if not items:
            return
        lines.append(f"  {icon} {label}:")
        for it in items:
            lines.append(f"    - \"{it['word']}\" (dipakai: {it['stored_py'] or '-'}) — muncul {it['occurrences']}x")
            if it.get('note'):
                lines.append(f"        catatan: {it['note']}")
            if it.get('context'):
                lines.append(f"        konteks: {it['context']}")
            lines.append(f"        varian pinyin di cidict: {it['alternatives']}")

    block("PRIORITAS TINGGI (belum tervalidasi manusia)", 'tinggi', '🔴')
    block("PRIORITAS SEDANG (pola serupa kasus historis)", 'sedang', '🟠')
    block("INFO (kemungkinan aman, cuma catatan)", 'info', 'ℹ️ ')
    lines.append("")
    return "\n".join(lines)


def main():
    args = parse_args(sys.argv[1:])
    passages, grouped, lookup_now = load_all()
    print(f"Total entri di graded_readers.json: {len(passages)}")

    targets = select_entries(passages, args)
    print(f"Mengaudit {len(targets)} entri...\n")

    report_lines = [f"=== LAPORAN audit_polysemy_batch.py — {datetime.now()} ==="]
    report_lines.append(f"Entri diaudit: {len(targets)} dari total {len(passages)}")
    report_lines.append("")

    n_flagged_entries = 0
    n_flagged_words_total = 0

    for entry in targets:
        findings = audit_entry(entry, grouped, lookup_now)
        text = format_entry_report(entry, findings)
        if text:
            n_flagged_entries += 1
            n_flagged_words_total += sum(len(v) for v in findings.values())
            report_lines.append(text)

    summary = (
        f"\n--- RINGKASAN ---\n"
        f"Entri diaudit         : {len(targets)}\n"
        f"Entri dengan temuan   : {n_flagged_entries}\n"
        f"Total kata ditandai   : {n_flagged_words_total}\n"
        f"(Entri tanpa temuan berarti tidak ada kata multi-pinyin yang mencurigakan -- aman.)\n"
    )
    report_lines.append(summary)

    report_text = "\n".join(report_lines)
    print(report_text)

    ts = datetime.now().strftime('%Y%m%d_%H%M%S')
    out_path = Path(f"audit_polysemy_batch_report_{ts}.txt")
    out_path.write_text(report_text, encoding='utf-8')
    print(f"Laporan disimpan: {out_path}")


class Args:
    ids = None
    last = None


def parse_args(argv):
    a = Args()
    i = 0
    while i < len(argv):
        tok = argv[i]
        if tok == '--last':
            a.last = int(argv[i + 1])
            i += 2
        elif tok == '--ids':
            a.ids = argv[i + 1:]
            i = len(argv)
        else:
            print(f"Argumen tidak dikenal: {tok}")
            sys.exit(1)
    return a


if __name__ == "__main__":
    main()

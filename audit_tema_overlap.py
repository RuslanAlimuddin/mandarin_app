# -*- coding: utf-8 -*-
"""
audit_tema_overlap.py — Mandarin Interaktif
=============================================
Alat bantu KURASI (dijalankan sesekali, TIDAK dipakai aplikasi). Cari
pasangan tema di data/index_theme.json yang kemungkinan tumpang-tindih atau
duplikat konsep, mis. "warna" vs "warna (ext)", "Mata Uang" vs "Nama Mata
Uang". Cuma cetak LAPORAN -- tidak mengubah data apa pun.

Dua sinyal yang dicek per pasangan tema:
  1. OVERLAP KATA   -- rasio Jaccard (irisan kata / union kata)
  2. MIRIP NAMA     -- kemiripan string label_id (pakai difflib bawaan Python)

CARA PAKAI (dari folder C:\\mandarin_app):
    python audit_tema_overlap.py
    python audit_tema_overlap.py --overlap-min 0.10 --label-min 0.5

Kalau laporan menunjukkan ada pasangan yang memang perlu digabung, baru
pakai merge_tema.py buat eksekusinya (script ini SENGAJA tidak mengubah
apa pun -- murni observasi buat رسلان putuskan sendiri).
"""
import json
import sys
import argparse
from pathlib import Path
from difflib import SequenceMatcher
from datetime import datetime

DATA_DIR = Path("data")
INDEX_THEME_PATH = DATA_DIR / "index_theme.json"


def label_similarity(a, b):
    return SequenceMatcher(None, a.lower().strip(), b.lower().strip()).ratio()


def jaccard(set_a, set_b):
    if not set_a and not set_b:
        return 0.0
    inter = set_a & set_b
    union = set_a | set_b
    return len(inter) / len(union) if union else 0.0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--overlap-min', type=float, default=0.12,
                     help='Ambang rasio overlap kata (Jaccard) buat dianggap mencurigakan. Default 0.12')
    ap.add_argument('--label-min', type=float, default=0.5,
                     help='Ambang kemiripan nama tema buat dianggap mencurigakan. Default 0.5')
    ap.add_argument('--top', type=int, default=0,
                     help='Batasi tampilkan N pasangan teratas saja (0 = tampilkan semua yang lolos ambang)')
    args = ap.parse_args()

    if not INDEX_THEME_PATH.exists():
        print(f"‼ FATAL: {INDEX_THEME_PATH} tidak ditemukan. Jalankan skrip ini dari folder C:\\mandarin_app")
        sys.exit(1)

    with open(INDEX_THEME_PATH, encoding='utf-8') as f:
        themes = json.load(f)

    keys = list(themes.keys())
    print(f"Memuat {len(keys)} tema dari {INDEX_THEME_PATH}")
    print(f"Ambang: overlap kata >= {args.overlap_min:.0%}  ATAU  kemiripan nama >= {args.label_min:.0%}\n")

    word_sets = {k: set(themes[k].get('words', [])) for k in keys}
    labels = {k: themes[k].get('label_id', k) for k in keys}

    results = []
    n = len(keys)
    for i in range(n):
        for j in range(i + 1, n):
            k1, k2 = keys[i], keys[j]
            ov = jaccard(word_sets[k1], word_sets[k2])
            lab_sim = label_similarity(labels[k1], labels[k2])
            if ov >= args.overlap_min or lab_sim >= args.label_min:
                shared = sorted(word_sets[k1] & word_sets[k2])
                results.append({
                    'k1': k1, 'k2': k2,
                    'label1': labels[k1], 'label2': labels[k2],
                    'count1': len(word_sets[k1]), 'count2': len(word_sets[k2]),
                    'overlap_ratio': ov,
                    'label_sim': lab_sim,
                    'shared_count': len(shared),
                    'shared_sample': shared[:10],
                })

    # urutkan dari yang paling mencurigakan (kombinasi overlap kata + kemiripan nama)
    results.sort(key=lambda r: (r['overlap_ratio'] + r['label_sim']), reverse=True)

    if args.top:
        results = results[:args.top]

    if not results:
        print("Tidak ada pasangan tema yang mencurigakan pada ambang ini. 👍")
        print("(coba turunkan --overlap-min / --label-min kalau mau pencarian lebih longgar)")
        return

    lines = []
    lines.append(f"=== LAPORAN audit_tema_overlap.py — {datetime.now()} ===")
    lines.append(f"{len(results)} pasangan tema mencurigakan ditemukan dari {len(keys)} tema total\n")

    for idx, r in enumerate(results, 1):
        lines.append(f"[{idx}] \"{r['label1']}\" ({r['k1']}, {r['count1']} kata)  <->  \"{r['label2']}\" ({r['k2']}, {r['count2']} kata)")
        lines.append(f"     overlap kata: {r['overlap_ratio']:.0%} ({r['shared_count']} kata sama)   kemiripan nama: {r['label_sim']:.0%}")
        if r['shared_sample']:
            contoh = '、'.join(r['shared_sample'])
            lebih = f" ... (+{r['shared_count'] - len(r['shared_sample'])} lagi)" if r['shared_count'] > len(r['shared_sample']) else ''
            lines.append(f"     contoh kata sama: {contoh}{lebih}")
        lines.append(f"     -> kalau memang perlu digabung: python merge_tema.py {r['k1']} {r['k2']}")
        lines.append("")

    report = "\n".join(lines)
    print(report)

    ts = datetime.now().strftime('%Y%m%d_%H%M%S')
    out_path = Path(f"audit_tema_overlap_report_{ts}.txt")
    out_path.write_text(report, encoding='utf-8')
    print(f"Laporan disimpan: {out_path}")
    print("\nCatatan: skrip ini CUMA melaporkan, tidak mengubah data apa pun.")
    print("رسلان yang putuskan manual mana yang memang perlu digabung (lihat merge_tema.py).")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
cek_polusi_makna.py — Mandarin Interaktif
Diagnostik READ-ONLY: ukur seberapa banyak entri `meanings_id` di
app_words.json sebenarnya BUKAN makna asli, melainkan metadata yg
"bocor" ikut (KP: kata-penggolong, varian-dari, dst). Lalu hitung ULANG
distribusi polisemi SETELAH sampah ini dibuang -- supaya angka
"kandidat kata polisemi" jadi akurat, bukan digelembungkan sampah.

TIDAK mengubah app_words.json. Cuma menganalisis & melaporkan.

CARA PAKAI:
  python cek_polusi_makna.py
  -> baca ringkasan di terminal, lalu upload polusi_makna_report.json
     yg otomatis dibuat, ke sesi Claude berikutnya.
"""
import json
import os
import random
import re
from collections import Counter

random.seed(42)
DATA_DIR = "data"
OUT_PATH = "polusi_makna_report.json"
SAMPLE_N = 20

# Pola metadata yg BUKAN makna asli, hasil observasi manual dari sampel
# polisemi_report.json sesi sebelumnya. Ditulis longgar (bukan exact
# match) supaya menangkap variasi kecil, tapi cukup spesifik supaya
# tidak salah tangkap makna asli yg kebetulan mirip.
JUNK_PATTERNS = [
    (re.compile(r'^KP:'), 'KP: (kata penggolong bocor)'),
    (re.compile(r'^varian dari '), 'varian dari (cross-ref karakter)'),
    (re.compile(r'^Taiwan (pr\.|dibaca)'), 'Taiwan pr. (catatan bacaan region)'),
    (re.compile(r'^juga pr\.'), 'juga pr. (catatan bacaan alternatif)'),
    (re.compile(r'^lihat juga '), 'lihat juga (cross-ref)'),
    (re.compile(r'^old variant of '), 'old variant of (cross-ref arkais)'),
    (re.compile(r'^CL:'), 'CL: (classifier notation gaya lama)'),
]


def load_json_safe(path):
    if not os.path.exists(path):
        return None, f"(tidak ditemukan: {path})"
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f), None
    except Exception as e:
        return None, f"(gagal parse {path}: {e})"


def classify_item(item):
    """Return nama pola junk kalau item cocok salah satu JUNK_PATTERNS,
    None kalau ini kelihatan seperti makna asli."""
    if not isinstance(item, str):
        return None
    s = item.strip()
    for pattern, label in JUNK_PATTERNS:
        if pattern.search(s):
            return label
    return None


def main():
    app_words, err = load_json_safe(os.path.join(DATA_DIR, "app_words.json"))
    if app_words is None:
        print(f"[GAGAL] {err}")
        return

    total_entries = len(app_words)
    total_items = 0
    total_junk_items = 0
    junk_label_counts = Counter()
    entries_with_junk = 0
    entries_with_junk_samples = []

    # Distribusi BARU (setelah sampah dibuang) utk dibandingkan dgn
    # distribusi lama (mentah) dari polisemi_report.json sesi sebelumnya.
    clean_meaning_counts = Counter()
    clean_threshold_counts = {th: 0 for th in [1, 2, 3, 4, 5, 8]}

    for w in app_words:
        meanings = w.get("meanings_id")
        if not isinstance(meanings, list):
            continue
        total_items += len(meanings)

        clean_items = []
        found_junk_here = []
        for item in meanings:
            label = classify_item(item)
            if label:
                total_junk_items += 1
                junk_label_counts[label] += 1
                found_junk_here.append((item, label))
            else:
                clean_items.append(item)

        if found_junk_here:
            entries_with_junk += 1
            if len(entries_with_junk_samples) < SAMPLE_N:
                entries_with_junk_samples.append({
                    "hanzi": w.get("simplified") or w.get("id"),
                    "pinyin": w.get("pinyin"),
                    "meanings_id_asli": meanings,
                    "item_terdeteksi_junk": found_junk_here,
                    "meanings_id_setelah_bersih": clean_items,
                })

        n_clean = len(clean_items)
        bucket = n_clean if n_clean < 5 else ("5-7" if n_clean < 8 else "8+")
        clean_meaning_counts[bucket] += 1
        for th in clean_threshold_counts:
            if n_clean >= th:
                clean_threshold_counts[th] += 1

    print(f"{'='*70}\nRINGKASAN POLUSI METADATA DI meanings_id\n{'='*70}")
    print(f"Total entri app_words.json           : {total_entries:,}")
    print(f"Total ITEM di semua meanings_id       : {total_items:,}")
    print(f"Total ITEM yg terdeteksi SAMPAH        : {total_junk_items:,} "
          f"({total_junk_items/total_items*100:.1f}% dari semua item)")
    print(f"Jumlah ENTRI yg py >=1 item sampah      : {entries_with_junk:,} "
          f"({entries_with_junk/total_entries*100:.1f}% dari semua entri)")

    print("\nRincian per jenis pola sampah:")
    for label, cnt in junk_label_counts.most_common():
        print(f"   {label:45}: {cnt:,}")

    print(f"\n{'='*70}\nDISTRIBUSI POLISEMI SETELAH SAMPAH DIBUANG (bandingkan dgn laporan lama)\n{'='*70}")
    for k in sorted(clean_meaning_counts.keys(), key=lambda x: (isinstance(x, str), x)):
        pct = clean_meaning_counts[k] / total_entries * 100
        print(f"   {str(k):>4} makna bersih : {clean_meaning_counts[k]:>6,} entri ({pct:5.1f}%)")

    print("\nJumlah kata dgn >= N makna BERSIH (angka polisemi yg lebih akurat):")
    for th, cnt in clean_threshold_counts.items():
        print(f"   >= {th} makna bersih : {cnt:,} kata")

    print(f"\nSampel {len(entries_with_junk_samples)} entri yg kena sampah (utk verifikasi manual):")
    for s in entries_with_junk_samples[:10]:
        print(f"   {s['hanzi']} ({s['pinyin']}):")
        print(f"      asli  : {s['meanings_id_asli']}")
        print(f"      bersih: {s['meanings_id_setelah_bersih']}")

    report = {
        "total_entries": total_entries,
        "total_items": total_items,
        "total_junk_items": total_junk_items,
        "entries_with_junk": entries_with_junk,
        "junk_label_counts": dict(junk_label_counts),
        "distribusi_makna_bersih": {str(k): v for k, v in clean_meaning_counts.items()},
        "kandidat_per_threshold_bersih": clean_threshold_counts,
        "sampel_entri_terkena_sampah": entries_with_junk_samples,
    }
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    print(f"\n{'='*70}\nSelesai. Disimpan ke: {OUT_PATH}")
    print("Upload file itu ke sesi Claude berikutnya utk lanjut diskusi & rencana.")
    print(f"{'='*70}")


if __name__ == "__main__":
    main()

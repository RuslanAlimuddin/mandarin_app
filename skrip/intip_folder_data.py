#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
intip_folder_data.py — Mandarin Interaktif
Diagnostik READ-ONLY terakhir sebelum finalisasi rencana Tier 1/2/3
(struktur detail kata polisemi). Dua hal:

  A. List SEMUA file di folder data/ beserta ukurannya -- supaya kelihatan
     file apa saja yg ada, siapa tau ada dataset relevan yg terlupa
     (mis. dataset kata penggolong terpisah) yg belum tersambung ke app.
  B. Dump skema LENGKAP (semua field, apa adanya) dari beberapa entri
     sampel app_words.json -- termasuk 土 dan 吃 -- supaya kelihatan field
     apa saja yg SUDAH ada sebelum mengusulkan field baru.

TIDAK mengubah file apa pun.

CARA PAKAI:
  python intip_folder_data.py
  -> upload folder_data_report.json yg dihasilkan
"""
import json
import os

DATA_DIR = "data"
OUT_PATH = "folder_data_report.json"
SAMPLE_WORDS = ["土", "吃", "个", "了"]  # kata yg sudah kita bahas + 1 partikel umum


def list_data_folder():
    print(f"{'='*70}\nISI FOLDER {DATA_DIR}/\n{'='*70}")
    if not os.path.isdir(DATA_DIR):
        print(f"(folder {DATA_DIR} tidak ditemukan dari lokasi script dijalankan)")
        return []

    entries = []
    for name in sorted(os.listdir(DATA_DIR)):
        full = os.path.join(DATA_DIR, name)
        if os.path.isfile(full):
            size = os.path.getsize(full)
            size_str = f"{size/1024/1024:.2f} MB" if size > 1024*1024 else f"{size/1024:.1f} KB"
            print(f"   {name:45} {size_str:>12}")
            entries.append({"name": name, "size_bytes": size})
        elif os.path.isdir(full):
            print(f"   {name}/  (folder)")
            entries.append({"name": name, "is_dir": True})
    return entries


def dump_sample_entries():
    print(f"\n{'='*70}\nSKEMA LENGKAP (semua field apa adanya) — app_words.json\n{'='*70}")
    path = os.path.join(DATA_DIR, "app_words.json")
    if not os.path.exists(path):
        print(f"(tidak ditemukan: {path})")
        return {}, []

    with open(path, encoding="utf-8") as f:
        data = json.load(f)

    # Kumpulkan SEMUA nama field yg pernah muncul di seluruh dataset --
    # supaya kelihatan field langka yg mungkin cuma ada di sebagian entri.
    all_fields = set()
    for w in data:
        all_fields.update(w.keys())
    print(f"Total entri: {len(data):,}")
    print(f"Semua nama field yg pernah muncul di dataset ({len(all_fields)} field):")
    for f_ in sorted(all_fields):
        n_present = sum(1 for w in data if f_ in w and w[f_] not in (None, "", [], {}))
        print(f"   {f_:25} -> muncul (berisi) di {n_present:,} / {len(data):,} entri")

    samples = {}
    print(f"\nDump LENGKAP entri sampel:")
    for target in SAMPLE_WORDS:
        found = next((w for w in data if w.get("simplified") == target), None)
        print(f"\n   --- {target} ---")
        if found:
            print(json.dumps(found, ensure_ascii=False, indent=6))
            samples[target] = found
        else:
            print(f"   (tidak ditemukan entri simplified == {target!r})")
            samples[target] = None

    return {"all_fields": sorted(all_fields),
            "field_presence_count": {f_: sum(1 for w in data if f_ in w and w[f_] not in (None, "", [], {})) for f_ in all_fields}}, samples


def main():
    folder_listing = list_data_folder()
    field_info, samples = dump_sample_entries()

    report = {
        "folder_listing": folder_listing,
        "field_info": field_info,
        "sample_entries": samples,
    }
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    print(f"\n{'='*70}\nSelesai. Disimpan ke: {OUT_PATH}")
    print("Upload file itu ke sesi Claude berikutnya utk lanjut diskusi & rencana.")
    print(f"{'='*70}")


if __name__ == "__main__":
    main()

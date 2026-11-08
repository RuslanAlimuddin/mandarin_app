#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
cari_data_yatim.py — Mandarin Interaktif
Diagnostik READ-ONLY: pindai SEMUA file .html & .js di seluruh folder
proyek (mandarin_app/), cek nama tiap file di data/ disebut di mana
saja atau TIDAK PERNAH SAMA SEKALI. File yg tidak pernah disebut adalah
kandidat kuat "data sudah disiapkan tapi lupa disambungkan ke fitur" --
seperti kasus confusion_groups.json yg رسلان baru ingat.

TIDAK mengubah file apa pun. Dijalankan dari root C:\\mandarin_app\\.

CARA PAKAI:
  python cari_data_yatim.py
  -> upload data_yatim_report.json yg dihasilkan
"""
import json
import os

DATA_DIR = "data"
OUT_PATH = "data_yatim_report.json"

# Folder/pola yg dilewati saat scan kode -- backup zip checkpoint, venv, dll.
SKIP_DIR_NAMES = {"__pycache__", "node_modules", ".git", "checkpoints", "backup", "backups"}


def find_code_files(root="."):
    """Cari semua .html dan .js di seluruh project, KECUALI yg ada di
    dalam data/ itu sendiri (kita cuma mau kode aplikasi, bukan data)."""
    code_files = []
    for dirpath, dirnames, filenames in os.walk(root):
        # jangan turun ke folder data/ atau folder yg di-skip
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIR_NAMES and
                       os.path.normpath(os.path.join(dirpath, d)) != os.path.normpath(DATA_DIR)]
        for fn in filenames:
            if fn.endswith(".html") or fn.endswith(".js"):
                code_files.append(os.path.join(dirpath, fn))
    return code_files


def scan_references(code_files, data_filenames):
    """Untuk tiap nama file di data/, cek apakah string namanya muncul
    di SALAH SATU file kode. Simple substring search -- cukup akurat
    krn nama file biasanya unik & spesifik (mis. 'confusion_groups.json')."""
    references = {name: [] for name in data_filenames}

    for cf in code_files:
        try:
            with open(cf, encoding="utf-8", errors="ignore") as f:
                content = f.read()
        except Exception as e:
            print(f"   (gagal baca {cf}: {e})")
            continue

        for name in data_filenames:
            if name in content:
                references[name].append(cf)

    return references


def main():
    if not os.path.isdir(DATA_DIR):
        print(f"[GAGAL] Folder {DATA_DIR}/ tidak ditemukan. Jalankan script ini "
              f"dari root C:\\mandarin_app\\ (sejajar dgn folder data\\).")
        return

    data_filenames = sorted([
        f for f in os.listdir(DATA_DIR)
        if os.path.isfile(os.path.join(DATA_DIR, f)) and
        not f.startswith(".") and
        (f.endswith(".json") or f.endswith(".txt") or f.endswith(".u8"))
    ])
    print(f"Jumlah file data (.json/.txt/.u8) di {DATA_DIR}/: {len(data_filenames)}")

    code_files = find_code_files(".")
    print(f"Jumlah file kode (.html/.js) di seluruh proyek: {len(code_files)}")
    print("File kode yg dipindai:")
    for cf in sorted(code_files):
        print(f"   {cf}")

    references = scan_references(code_files, data_filenames)

    orphans = [name for name, refs in references.items() if not refs]
    referenced = [name for name, refs in references.items() if refs]

    print(f"\n{'='*70}\nFILE DATA YG TIDAK PERNAH DISEBUT DI KODE MANAPUN "
          f"({len(orphans)} file) -- KANDIDAT FITUR TERLUPA\n{'='*70}")
    for name in orphans:
        size = os.path.getsize(os.path.join(DATA_DIR, name))
        size_str = f"{size/1024/1024:.2f} MB" if size > 1024*1024 else f"{size/1024:.1f} KB"
        print(f"   {name:45} {size_str:>10}")

    print(f"\n{'='*70}\nFILE DATA YG SUDAH DIREFERENSIKAN ({len(referenced)} file)\n{'='*70}")
    for name in referenced:
        refs_short = [os.path.basename(r) for r in references[name]]
        print(f"   {name:45} -> dipakai di: {', '.join(refs_short)}")

    report = {
        "total_data_files": len(data_filenames),
        "total_code_files_scanned": len(code_files),
        "code_files_scanned": code_files,
        "orphan_files": orphans,
        "referenced_files": {name: references[name] for name in referenced},
    }
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    print(f"\n{'='*70}\nSelesai. Disimpan ke: {OUT_PATH}")
    print("Upload file itu ke sesi Claude berikutnya utk ditindaklanjuti.")
    print(f"{'='*70}")


if __name__ == "__main__":
    main()

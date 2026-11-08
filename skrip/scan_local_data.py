#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scan_local_data.py — Mandarin Interaktif
=========================================
Skrip PENGINTAI (read-only, TIDAK mengubah/menghapus apa pun) untuk memetakan
data yang رسلان sudah punya di C:\\mandarin_app dan C:\\mandarin_kamus, supaya
Claude tahu data apa saja yang tersedia LOKAL sebelum mencari ke sumber luar
(GitHub, dsb).

CARA PAKAI:
  1. Simpan file ini di mana saja (boleh di C:\\mandarin_app sendiri).
  2. Jalankan lewat Command Prompt / PowerShell:
       python scan_local_data.py
  3. Hasilnya otomatis tersimpan ke scan_report.txt di folder yang sama
     dengan skrip ini. Copy-paste ISI file itu ke chat Claude.

Skrip ini HANYA membaca file (tidak pernah menulis/menghapus/mengubah file
sumber). Kalau salah satu folder tidak ada di komputer رسلان, skrip otomatis
melewatinya tanpa error.
"""

import os
import sys
import json
import random
import csv
from pathlib import Path

# ── Folder yang mau diintip -- sesuaikan kalau lokasinya beda ──
TARGET_DIRS = [
    r"C:\mandarin_app",
    r"C:\mandarin_kamus",
]

# Ekstensi yang dianggap "data" dan akan diintip isinya (bukan cuma dilist namanya)
DATA_EXTENSIONS = {'.json', '.csv', '.tsv', '.txt'}

# Folder yang dilewati (biasanya bukan data, cuma bikin laporan penuh sampah)
SKIP_DIR_NAMES = {'.git', 'node_modules', '__pycache__', '.vscode', 'dist', 'build'}

# Berapa banyak sampel entri/baris acak yang diambil dari tiap file data
SAMPLE_SIZE = 3

# Ukuran file maksimum (bytes) yang masih dibaca penuh ke memori untuk sampling
# acak yang benar-benar acak. File yang lebih besar dari ini akan disampling
# dengan cara streaming baris (khusus txt/csv) atau cuma dilaporkan ukurannya
# (khusus json besar yang berisiko lambat/berat kalau di-load penuh).
MAX_FULL_READ_BYTES = 15 * 1024 * 1024  # 15 MB


def human_size(n):
    for unit in ['B', 'KB', 'MB', 'GB']:
        if n < 1024:
            return f"{n:.1f}{unit}"
        n /= 1024
    return f"{n:.1f}TB"


def try_read_text(path, max_bytes=None):
    """Baca file sebagai teks, coba beberapa encoding umum di Windows/Mandarin app."""
    encodings = ['utf-8', 'utf-8-sig', 'gbk', 'big5', 'latin-1']
    raw = path.read_bytes() if max_bytes is None else path.read_bytes()[:max_bytes]
    for enc in encodings:
        try:
            return raw.decode(enc)
        except (UnicodeDecodeError, LookupError):
            continue
    return raw.decode('utf-8', errors='replace')


def summarize_json(path, size):
    out = []
    try:
        if size > MAX_FULL_READ_BYTES:
            out.append(f"    [file JSON {human_size(size)} -- terlalu besar utk sampling acak penuh, cuma cek struktur luar]")
            text = try_read_text(path, max_bytes=4000)
            out.append("    awal file (mentah, 4000 byte pertama):")
            out.append("      " + text[:2000].replace("\n", "\n      "))
            return out

        text = try_read_text(path)
        data = json.loads(text)

        if isinstance(data, list):
            out.append(f"    Tipe: list, {len(data)} item")
            if data:
                sample_idx = random.sample(range(len(data)), min(SAMPLE_SIZE, len(data)))
                for i in sample_idx:
                    item = data[i]
                    s = json.dumps(item, ensure_ascii=False)
                    if len(s) > 500:
                        s = s[:500] + " ...(dipotong)"
                    out.append(f"    contoh[{i}]: {s}")

        elif isinstance(data, dict):
            keys = list(data.keys())
            out.append(f"    Tipe: dict/objek, {len(keys)} key")
            out.append(f"    daftar key (maks 40 ditampilkan): {keys[:40]}")
            sample_keys = random.sample(keys, min(SAMPLE_SIZE, len(keys))) if keys else []
            for k in sample_keys:
                v = data[k]
                s = json.dumps(v, ensure_ascii=False)
                if len(s) > 500:
                    s = s[:500] + " ...(dipotong)"
                out.append(f"    contoh['{k}']: {s}")
        else:
            out.append(f"    Tipe JSON tak terduga: {type(data).__name__}")

    except json.JSONDecodeError as e:
        out.append(f"    [Gagal parse sbg JSON: {e}. Mungkin JSON-Lines (1 objek per baris)? Coba intip baris mentah:]")
        try:
            text = try_read_text(path, max_bytes=4000)
            lines = [l for l in text.splitlines() if l.strip()][:3]
            for l in lines:
                out.append("    " + (l[:300] + ("..." if len(l) > 300 else "")))
        except Exception as e2:
            out.append(f"    [Gagal juga baca mentah: {e2}]")
    except Exception as e:
        out.append(f"    [Error baca file: {e}]")
    return out


def summarize_csv_tsv(path, size, delimiter=','):
    out = []
    try:
        text = try_read_text(path, max_bytes=min(size, MAX_FULL_READ_BYTES))
        reader = csv.reader(text.splitlines(), delimiter=delimiter)
        rows = list(reader)
        out.append(f"    Tipe: CSV/TSV, {len(rows)} baris (termasuk header kalau ada)")
        if rows:
            out.append(f"    header/baris-1: {rows[0]}")
            body = rows[1:] if len(rows) > 1 else []
            if body:
                sample_idx = random.sample(range(len(body)), min(SAMPLE_SIZE, len(body)))
                for i in sample_idx:
                    out.append(f"    contoh baris {i+2}: {body[i]}")
    except Exception as e:
        out.append(f"    [Error baca CSV/TSV: {e}]")
    return out


def summarize_txt(path, size):
    out = []
    try:
        text = try_read_text(path, max_bytes=min(size, MAX_FULL_READ_BYTES))
        lines = [l for l in text.splitlines() if l.strip()]
        out.append(f"    Tipe: teks polos, {len(lines)} baris non-kosong")
        if lines:
            sample_idx = random.sample(range(len(lines)), min(SAMPLE_SIZE, len(lines)))
            for i in sorted(sample_idx):
                l = lines[i]
                out.append(f"    contoh baris {i+1}: {l[:300]}{'...' if len(l) > 300 else ''}")
    except Exception as e:
        out.append(f"    [Error baca TXT: {e}]")
    return out


def scan_dir(root, report):
    root_path = Path(root)
    if not root_path.exists():
        report.append(f"\n{'='*70}")
        report.append(f"FOLDER TIDAK DITEMUKAN: {root}  (dilewati)")
        return

    report.append(f"\n{'='*70}")
    report.append(f"FOLDER: {root}")
    report.append('='*70)

    all_files = []
    for dirpath, dirnames, filenames in os.walk(root_path):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIR_NAMES and not d.startswith('.')]
        for fn in filenames:
            all_files.append(Path(dirpath) / fn)

    if not all_files:
        report.append("  (folder kosong atau tidak ada file terbaca)")
        return

    report.append(f"  Total file ditemukan: {len(all_files)}\n")

    # Daftar semua file dulu (ringkas: path relatif + ukuran)
    report.append("  --- Daftar semua file ---")
    for f in sorted(all_files):
        try:
            size = f.stat().st_size
        except OSError:
            size = 0
        rel = f.relative_to(root_path)
        report.append(f"    {rel}  ({human_size(size)})")

    # Lalu intip isi tiap file DATA (json/csv/tsv/txt)
    report.append("\n  --- Isi/sampel tiap file data ---")
    for f in sorted(all_files):
        if f.suffix.lower() not in DATA_EXTENSIONS:
            continue
        try:
            size = f.stat().st_size
        except OSError:
            size = 0
        rel = f.relative_to(root_path)
        report.append(f"\n  ▶ {rel}  ({human_size(size)})")

        if size == 0:
            report.append("    (file kosong)")
            continue

        ext = f.suffix.lower()
        if ext == '.json':
            report.extend(summarize_json(f, size))
        elif ext == '.csv':
            report.extend(summarize_csv_tsv(f, size, delimiter=','))
        elif ext == '.tsv':
            report.extend(summarize_csv_tsv(f, size, delimiter='\t'))
        elif ext == '.txt':
            report.extend(summarize_txt(f, size))


def main():
    report = []
    report.append("LAPORAN PENGINTAIAN DATA LOKAL -- Mandarin Interaktif")
    report.append("(read-only, tidak ada file yang diubah/dihapus)")

    for d in TARGET_DIRS:
        scan_dir(d, report)

    out_path = Path(__file__).resolve().parent / "scan_report.txt"
    out_path.write_text("\n".join(report), encoding="utf-8")

    print(f"Selesai. Laporan tersimpan di: {out_path}")
    print("Buka file itu, copy-paste seluruh isinya ke chat Claude.")


if __name__ == "__main__":
    main()

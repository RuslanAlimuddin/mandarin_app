#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scan_mandarin_app.py
Jalankan skrip ini di PC رسلان (butuh Python 3, tanpa library tambahan).
Hasilnya: file laporan_struktur.json di folder yang sama dengan skrip ini,
berisi daftar semua file di C:\\mandarin_app beserta info ringkas
(ukuran, dan untuk file .json/.html: struktur top-level / cuplikan).

Cara pakai:
    1. Simpan file ini di C:\\mandarin_app\\scan_mandarin_app.py
    2. Buka Command Prompt / PowerShell di folder itu
    3. Jalankan: python scan_mandarin_app.py
    4. Upload laporan_struktur.json yang dihasilkan ke chat Claude

Kalau رسلان mau scan folder lain (mis. C:\\hanyu_extract), ubah
variabel ROOT di bawah lalu jalankan lagi.
"""
import json
import os

ROOT = r"C:\mandarin_app"   # ganti kalau mau scan folder lain
OUTPUT = "laporan_struktur.json"
MAX_JSON_PREVIEW_CHARS = 800   # batasi cuplikan supaya laporan tidak raksasa
SKIP_DIRS = {".git", "node_modules", "__pycache__"}


def describe_json(path):
    """Kembalikan ringkasan struktur JSON: tipe, jumlah entri/keys, contoh."""
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        return {"error": f"gagal parse JSON: {e}"}

    info = {}
    if isinstance(data, dict):
        keys = list(data.keys())
        info["type"] = "object"
        info["top_level_key_count"] = len(keys)
        info["top_level_keys_sample"] = keys[:25]
        # kalau value dari key pertama adalah list, kasih tahu panjangnya
        if keys:
            v0 = data[keys[0]]
            if isinstance(v0, list):
                info["first_key_is_list_len"] = len(v0)
    elif isinstance(data, list):
        info["type"] = "array"
        info["length"] = len(data)
        if data and isinstance(data[0], dict):
            info["item_keys_sample"] = list(data[0].keys())
    else:
        info["type"] = type(data).__name__

    preview = json.dumps(data, ensure_ascii=False)[:MAX_JSON_PREVIEW_CHARS]
    info["preview"] = preview
    return info


def describe_file(path):
    size = os.path.getsize(path)
    entry = {"size_bytes": size}
    lower = path.lower()
    if lower.endswith(".json"):
        entry.update(describe_json(path))
    elif lower.endswith((".html", ".js", ".py", ".txt", ".css")):
        try:
            with open(path, encoding="utf-8", errors="replace") as f:
                content = f.read()
            entry["line_count"] = content.count("\n") + 1
            entry["preview"] = content[:500]
        except Exception as e:
            entry["error"] = str(e)
    return entry


def main():
    if not os.path.isdir(ROOT):
        print(f"Folder tidak ditemukan: {ROOT}")
        print("Edit variabel ROOT di bagian atas skrip ini, lalu jalankan lagi.")
        return

    report = {"root": ROOT, "files": {}}
    total = 0
    for dirpath, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for fname in filenames:
            full = os.path.join(dirpath, fname)
            rel = os.path.relpath(full, ROOT)
            try:
                report["files"][rel] = describe_file(full)
                total += 1
            except Exception as e:
                report["files"][rel] = {"error": str(e)}

    with open(OUTPUT, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=1)

    print(f"Selesai. {total} file dipindai.")
    print(f"Laporan disimpan di: {os.path.abspath(OUTPUT)}")
    print("Upload file itu ke chat Claude kalau perlu.")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
lacak_file_yatim.py — Mandarin Interaktif
Diagnostik READ-ONLY dua bagian:

  A. Cari SEMUA mention "cidict_semantic_index" dan "character_etymology_en"
     di seluruh file .md (BLUEPRINT versi lama) di folder Downloads --
     supaya ketahuan sesi mana & konteks apa file ini pernah dibahas.
  B. Intip struktur & sampel isi data/cidict_semantic_index.json dan
     data/character_etymology_en.json langsung -- kadang bentuk datanya
     sendiri sudah cukup buat nebak tujuannya tanpa perlu histori.

TIDAK mengubah file apa pun.

CARA PAKAI (dari folder C:\\mandarin_app\\):
  python lacak_file_yatim.py
  (defaultnya scan folder Downloads di user profile -- kalau BLUEPRINT
  disimpan di folder lain, jalankan: python lacak_file_yatim.py "D:\\path\\folder")
"""
import json
import os
import sys

DATA_DIR = "data"
OUT_PATH = "lacak_file_yatim_report.json"
KEYWORDS = ["cidict_semantic_index", "character_etymology_en", "confusion_groups"]
CONTEXT_CHARS = 200  # karakter konteks di kiri-kanan tiap match


def default_downloads_folder():
    home = os.path.expanduser("~")
    return os.path.join(home, "Downloads")


def search_blueprints(folder, keywords):
    print(f"{'='*70}\nMENCARI DI FOLDER: {folder}\n{'='*70}")
    if not os.path.isdir(folder):
        print(f"(folder tidak ditemukan: {folder})")
        return {}

    md_files = []
    for dirpath, dirnames, filenames in os.walk(folder):
        for fn in filenames:
            if fn.lower().endswith((".md", ".txt")):
                md_files.append(os.path.join(dirpath, fn))

    print(f"Jumlah file .md/.txt ditemukan: {len(md_files)}")

    results = {kw: [] for kw in keywords}
    for path in md_files:
        try:
            with open(path, encoding="utf-8", errors="ignore") as f:
                content = f.read()
        except Exception as e:
            print(f"   (gagal baca {path}: {e})")
            continue

        for kw in keywords:
            start = 0
            while True:
                idx = content.find(kw, start)
                if idx == -1:
                    break
                ctx_start = max(0, idx - CONTEXT_CHARS)
                ctx_end = min(len(content), idx + len(kw) + CONTEXT_CHARS)
                snippet = content[ctx_start:ctx_end].replace("\n", " ")
                results[kw].append({"file": path, "snippet": snippet})
                start = idx + len(kw)

    for kw in keywords:
        hits = results[kw]
        print(f"\n--- Kata kunci: {kw!r} -> {len(hits)} kemunculan ---")
        for h in hits[:5]:  # tampilkan max 5 per keyword di terminal, semua disimpan di JSON
            print(f"   [{os.path.basename(h['file'])}]")
            print(f"     ...{h['snippet']}...")
        if len(hits) > 5:
            print(f"   ...dan {len(hits)-5} kemunculan lain (lihat file JSON lengkap)")

    return results


def peek_json_file(path, label, sample_n=5):
    print(f"\n{'='*70}\n{label}\n{'='*70}")
    if not os.path.exists(path):
        print(f"(tidak ditemukan: {path})")
        return None
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        print(f"(gagal parse: {e})")
        return None

    result = {"type": type(data).__name__}
    if isinstance(data, list):
        print(f"Bentuk: LIST, {len(data):,} item")
        result["length"] = len(data)
        sample = data[:sample_n]
        print("Sampel item PERTAMA (bukan acak, supaya konsisten dgn urutan asli):")
        for item in sample:
            s = json.dumps(item, ensure_ascii=False)
            print("   " + (s[:400] + "...(terpotong)" if len(s) > 400 else s))
        result["first_items"] = sample
    elif isinstance(data, dict):
        keys = list(data.keys())
        print(f"Bentuk: DICT, {len(keys):,} key top-level")
        print(f"20 key pertama: {keys[:20]}")
        result["top_level_keys_count"] = len(keys)
        result["top_level_keys_sample"] = keys[:20]
        sample_keys = keys[:sample_n]
        result["sample"] = {}
        for k in sample_keys:
            v = data[k]
            s = json.dumps(v, ensure_ascii=False)
            print(f"   {k!r}: " + (s[:400] + "...(terpotong)" if len(s) > 400 else s))
            result["sample"][k] = v
    return result


def main():
    folder = sys.argv[1] if len(sys.argv) > 1 else default_downloads_folder()
    blueprint_results = search_blueprints(folder, KEYWORDS)

    data_results = {}
    data_results["cidict_semantic_index"] = peek_json_file(
        os.path.join(DATA_DIR, "cidict_semantic_index.json"),
        "data/cidict_semantic_index.json")
    data_results["character_etymology_en"] = peek_json_file(
        os.path.join(DATA_DIR, "character_etymology_en.json"),
        "data/character_etymology_en.json")
    # Pembanding: versi Indonesia yg SUDAH dipakai, buat dibandingkan skemanya
    data_results["char_etymology_id_pembanding"] = peek_json_file(
        os.path.join(DATA_DIR, "char_etymology_id.json"),
        "data/char_etymology_id.json (PEMBANDING, sudah aktif dipakai)")

    report = {
        "blueprint_search_folder": folder,
        "blueprint_mentions": blueprint_results,
        "data_file_peeks": data_results,
    }
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    print(f"\n{'='*70}\nSelesai. Disimpan ke: {OUT_PATH}")
    print("Upload file itu ke sesi Claude berikutnya.")
    print(f"{'='*70}")


if __name__ == "__main__":
    main()

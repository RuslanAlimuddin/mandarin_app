#!/usr/bin/env python3
"""
explorer.py
===========
Membaca app_words.json dan wb_pools.json, lalu menampilkan:
  1. Contoh 1-2 entry dari app_words.json (semua field, tipe data, dll)
  2. Struktur wb_pools.json dan mapping POS → pool name
  3. (Opsional) Mencari file .py yang kemungkinan generate wb_pools.json
"""

import json
import os
import sys
import glob
from pathlib import Path
from collections import OrderedDict


def separator(title: str, char: str = "=", width: int = 80):
    print(f"\n{char * width}")
    print(f" {title}".center(width))
    print(f"{char * width}\n")


def print_json_tree(data, prefix: str = "", depth: int = 0, max_depth: int = 4):
    """Print struktur JSON seperti tree, dengan tipe data."""
    if depth > max_depth:
        print(f"{prefix}...")
        return

    if isinstance(data, dict):
        for i, (k, v) in enumerate(data.items()):
            is_last = i == len(data) - 1
            connector = "└── " if is_last else "├── "
            type_hint = f" <{type(v).__name__}>"
            print(f"{prefix}{connector}{k!r}{type_hint}")
            ext = "    " if is_last else "│   "
            print_json_tree(v, prefix + ext, depth + 1, max_depth)
    elif isinstance(data, list):
        if len(data) == 0:
            print(f"{prefix}└── [] (empty)")
        else:
            # Tampilkan max 2 item saja sebagai contoh
            show = min(2, len(data))
            for i in range(show):
                is_last = (i == show - 1) and (show >= len(data))
                connector = "└── " if is_last else "├── "
                print(f"{prefix}{connector}[{i}]")
                ext = "    " if is_last else "│   "
                print_json_tree(data[i], prefix + ext, depth + 1, max_depth)
            if len(data) > show:
                print(f"{prefix}└── ... ({len(data) - show} more items)")
    else:
        # Scalar value
        val_str = repr(data)
        if len(val_str) > 80:
            val_str = val_str[:77] + "..."
        print(f"{prefix}└── {val_str}")


def analyze_app_words(filepath: str, num_samples: int = 2):
    """Tampilkan contoh entry dari app_words.json."""
    separator("1. CONTOH ENTRY DARI app_words.json")

    if not os.path.exists(filepath):
        print(f"  [ERROR] File tidak ditemukan: {filepath}")
        print("  Coba cari file serupa...")
        # Coba cari file yang mirip
        base_dir = os.path.dirname(filepath) or "."
        candidates = glob.glob(os.path.join(base_dir, "**/app_words*.json"), recursive=True)
        candidates += glob.glob(os.path.join(base_dir, "**/words*.json"), recursive=True)
        if candidates:
            print(f"  Ditemukan file alternatif:")
            for c in candidates[:5]:
                print(f"    - {c}")
        return None

    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    print(f"  File      : {filepath}")
    print(f"  Ukuran    : {os.path.getsize(filepath):,} bytes")
    print(f"  Tipe root : {type(data).__name__}")

    if isinstance(data, list):
        total = len(data)
        print(f"  Jumlah entry: {total}")
        if total == 0:
            print("  (kosong)")
            return data
        samples = data[:num_samples]
    elif isinstance(data, dict):
        keys = list(data.keys())
        print(f"  Jumlah key : {len(keys)}")
        print(f"  Keys       : {keys[:10]}{'...' if len(keys) > 10 else ''}")
        # Ambil 2 value pertama sebagai sample
        samples = [data[keys[0]]] if keys else []
        if len(keys) > 1:
            samples.append(data[keys[1]])
    else:
        print(f"  Struktur tidak terduga: {type(data)}")
        return data

    for i, sample in enumerate(samples):
        print(f"\n  --- Entry #{i + 1} ---")
        print_json_tree(sample, prefix="  ")

    # Analisis field yang ada di semua entry (kalau list)
    if isinstance(data, list) and len(data) > 0:
        print(f"\n  --- Analisis Semua Field ---")
        all_keys = set()
        key_types = {}  # key -> set of types
        key_examples = {}  # key -> first 2 unique values

        for entry in data:
            if isinstance(entry, dict):
                for k, v in entry.items():
                    all_keys.add(k)
                    t = type(v).__name__
                    key_types.setdefault(k, set()).add(t)
                    if k not in key_examples or len(key_examples[k]) < 2:
                        val_set = key_examples.setdefault(k, [])
                        val_repr = repr(v)
                        if len(val_repr) > 50:
                            val_repr = val_repr[:47] + "..."
                        if val_repr not in [x[1] for x in val_set]:
                            val_set.append((t, val_repr))

        print(f"  Total field unik: {len(all_keys)}")
        for k in sorted(all_keys):
            types = ", ".join(sorted(key_types.get(k, set())))
            examples = key_examples.get(k, [])
            ex_str = "; ".join(f"{t}: {v}" for t, v in examples)
            print(f"    {k:30s} | types: [{types:20s}] | contoh: {ex_str}")

        # Cari field yang kemungkinan POS
        pos_candidates = [k for k in all_keys if any(
            x in k.lower() for x in ["pos", "tag", "type", "kategori", "kelas", "category"]
        )]
        if pos_candidates:
            print(f"\n  Field yang kemungkinan POS: {pos_candidates}")
            for pk in pos_candidates:
                values = set()
                for entry in data:
                    if isinstance(entry, dict) and pk in entry:
                        v = entry[pk]
                        values.add(str(v))
                print(f"    {pk} -> nilai unik: {sorted(values)[:30]}")

    return data


def analyze_wb_pools(filepath: str):
    """Tampilkan struktur wb_pools.json dan mapping POS → pool."""
    separator("2. STRUKTUR & MAPPING DARI wb_pools.json")

    if not os.path.exists(filepath):
        print(f"  [ERROR] File tidak ditemukan: {filepath}")
        base_dir = os.path.dirname(filepath) or "."
        candidates = glob.glob(os.path.join(base_dir, "**/wb_pools*.json"), recursive=True)
        candidates += glob.glob(os.path.join(base_dir, "**/*pool*.json"), recursive=True)
        if candidates:
            print(f"  Ditemukan file alternatif:")
            for c in candidates[:5]:
                print(f"    - {c}")
        return None

    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    print(f"  File      : {filepath}")
    print(f"  Ukuran    : {os.path.getsize(filepath):,} bytes")
    print(f"  Tipe root : {type(data).__name__}")

    # Tree structure
    print(f"\n  --- Struktur Tree ---")
    print_json_tree(data, prefix="  ", max_depth=3)

    # Jika dict, tampilkan semua pool names
    if isinstance(data, dict):
        pool_names = list(data.keys())
        print(f"\n  --- Daftar Pool ({len(pool_names)}) ---")
        for name in pool_names:
            val = data[name]
            if isinstance(val, list):
                count = len(val)
                sample = val[0] if val else None
                sample_str = repr(sample)
                if len(sample_str) > 60:
                    sample_str = sample_str[:57] + "..."
                print(f"    {name:30s} -> {count} items, contoh: {sample_str}")
            elif isinstance(val, dict):
                count = len(val)
                sub_keys = list(val.keys())[:5]
                print(f"    {name:30s} -> {count} sub-keys: {sub_keys}")
            else:
                print(f"    {name:30s} -> {type(val).__name__}: {repr(val)[:60]}")

    return data


def find_generator_scripts(search_dir: str = "."):
    """Cari file .py yang kemungkinan generate wb_pools.json."""
    separator("3. PENCARIAN SCRIPT GENERATOR (opsional)")

    py_files = glob.glob(os.path.join(search_dir, "**/*.py"), recursive=True)

    if not py_files:
        print("  Tidak ada file .py ditemukan di direktori ini.")
        return

    print(f"  Ditemukan {len(py_files)} file .py. Mencari yang mereferensi 'wb_pools'...\n")

    hits = []
    for py_file in py_files:
        try:
            with open(py_file, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
            # Cari indikasi bahwa file ini generate wb_pools
            keywords = ["wb_pools", "pool", "generate_pool", "build_pool", "create_pool"]
            found_keywords = [kw for kw in keywords if kw.lower() in content.lower()]
            if found_keywords:
                hits.append((py_file, found_keywords))
        except Exception:
            continue

    if not hits:
        print("  Tidak ditemukan file .py yang mereferensi 'wb_pools' atau 'pool'.")
        print("  Menampilkan semua file .py yang ada:")
        for pf in py_files[:20]:
            print(f"    - {pf}")
        return

    for py_file, keywords in hits:
        print(f"  --- {py_file} ---")
        print(f"  Keywords ditemukan: {keywords}")
        print(f"  Ukuran: {os.path.getsize(py_file):,} bytes\n")

        # Tampilkan isi file (dengan highlight baris yang relevan)
        try:
            with open(py_file, "r", encoding="utf-8", errors="ignore") as f:
                lines = f.readlines()
            print(f"  Isi file ({len(lines)} baris):")
            print(f"  {'-' * 76}")
            for i, line in enumerate(lines, 1):
                # Highlight baris yang mengandung keyword
                is_relevant = any(kw.lower() in line.lower() for kw in keywords)
                marker = ">>>" if is_relevant else "   "
                # Truncate panjang baris
                display = line.rstrip("\n")
                if len(display) > 100:
                    display = display[:97] + "..."
                print(f"  {marker} {i:4d} | {display}")
            print(f"  {'-' * 76}\n")
        except Exception as e:
            print(f"  [ERROR] Gagal membaca: {e}\n")


def cross_reference(app_words_data, wb_pools_data):
    """Coba cross-reference antara app_words dan wb_pools."""
    separator("4. CROSS-REFERENCE: POS → Pool Mapping")

    if app_words_data is None or wb_pools_data is None:
        print("  Skip (salah satu atau kedua data tidak tersedia).")
        return

    # Kumpulkan semua kata dari wb_pools
    pool_words = {}  # word -> pool_name
    if isinstance(wb_pools_data, dict):
        for pool_name, words in wb_pools_data.items():
            if isinstance(words, list):
                for w in words:
                    if isinstance(w, str):
                        pool_words[w.lower()] = pool_name
                    elif isinstance(w, dict) and "word" in w:
                        pool_words[w["word"].lower()] = pool_name
                    elif isinstance(w, dict) and "text" in w:
                        pool_words[w["text"].lower()] = pool_name

    # Kumpulkan POS dari app_words
    word_pos = {}  # word -> pos
    if isinstance(app_words_data, list):
        # Coba temukan field kata dan field POS
        pos_field = None
        word_field = None

        for entry in app_words_data[:100]:
            if not isinstance(entry, dict):
                continue
            for k, v in entry.items():
                kl = k.lower()
                if kl in ("pos", "tag", "type", "kategori", "kelas", "category", "pos_tag"):
                    pos_field = k
                if kl in ("word", "text", "kata", "lemma", "form", "surface"):
                    if word_field is None:
                        word_field = k

        if pos_field and word_field:
            print(f"  Menggunakan field: word='{word_field}', pos='{pos_field}'\n")
            for entry in app_words_data:
                if isinstance(entry, dict) and word_field in entry and pos_field in entry:
                    word_pos[entry[word_field].lower()] = entry[pos_field]

    # Cross-reference
    pos_to_pools = {}  # pos -> set of pool names
    matched = 0
    for word, pos in word_pos.items():
        if word in pool_words:
            pool_name = pool_words[word]
            pos_to_pools.setdefault(pos, set()).add(pool_name)
            matched += 1

    if pos_to_pools:
        print(f"  Ditemukan {matched} kata yang cocok di kedua file.\n")
        print(f"  {'POS':20s} | Pool Names")
        print(f"  {'-' * 20}-+-{'-' * 50}")
        for pos in sorted(pos_to_pools.keys()):
            pools = ", ".join(sorted(pos_to_pools[pos]))
            print(f"  {pos:20s} | {pools}")
    else:
        print("  Tidak ditemukan kecocokan kata antara app_words dan wb_pools.")
        print("  Kemungkinan:")
        print("    - Field kata/POS tidak terdeteksi otomatis")
        print("    - Format kata berbeda (misalnya ada affix/inflection)")
        print("    - Kedua file memang tidak berhubungan langsung")


def main():
    # Direktori pencarian (bisa di-override via argumen)
    search_dir = sys.argv[1] if len(sys.argv) > 1 else "."

    app_words_path = os.path.join(search_dir, "app_words.json")
    wb_pools_path = os.path.join(search_dir, "wb_pools.json")

    print("=" * 80)
    print("  JSON EXPLORER: app_words.json & wb_pools.json")
    print(f"  Search dir: {os.path.abspath(search_dir)}")
    print("=" * 80)

    app_words_data = analyze_app_words(app_words_path, num_samples=2)
    wb_pools_data = analyze_wb_pools(wb_pools_path)
    find_generator_scripts(search_dir)
    cross_reference(app_words_data, wb_pools_data)

    separator("SELESAI")
    print("  Script ini bersifat eksploratif — ia membaca file yang ada")
    print("  dan menampilkannya dengan rapi. Tidak ada yang diubah.\n")


if __name__ == "__main__":
    main()
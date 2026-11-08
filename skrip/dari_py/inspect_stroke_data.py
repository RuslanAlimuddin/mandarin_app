#!/usr/bin/env python3
"""
inspect_stroke_data.py
═══════════════════════════════════════════════════════════════
Cek kelengkapan data untuk Modul Stroke Order:
  1. Field components/radical/structure/stroke di data/app_words.json
     -- ada berapa persen entry yang punya data lengkap, dan contoh isinya.
  2. Mencari file APAPUN di proyek yang kemungkinan berisi data jalur
     vektor stroke-order asli (bukan cuma metadata seperti components/
     radical/structure) -- misalnya dataset gaya Make Me a Hanzi /
     Hanzi Writer yang punya field seperti "strokes", "medians", "svg",
     dsb. Kalau ternyata ADA, modul bisa jauh lebih kaya (animasi
     goresan asli); kalau TIDAK ADA, kita pakai fallback "urutan
     komponen dari struktur" seperti yang sudah didiskusikan.

Jalankan dari folder root proyek (C:\\mandarin_app):
    python inspect_stroke_data.py

Script ini hanya MEMBACA dan MENAMPILKAN -- tidak mengubah apapun.
═══════════════════════════════════════════════════════════════
"""

import json
import os
import glob
from collections import defaultdict, Counter


def separator(title, char='=', width=78):
    print(f"\n{char * width}")
    print(f" {title}".center(width))
    print(f"{char * width}\n")


def inspect_app_words():
    separator("1. FIELD components / radical / structure / stroke DI app_words.json")

    path = 'data/app_words.json'
    if not os.path.exists(path):
        print(f"  [ERROR] Tidak ditemukan: {path}")
        return None

    with open(path, encoding='utf-8') as f:
        words = json.load(f)

    total = len(words)
    print(f"  Total kata: {total}")

    has_components = [w for w in words if w.get('components')]
    has_radical    = [w for w in words if w.get('radical')]
    has_structure  = [w for w in words if w.get('structure')]
    has_stroke     = [w for w in words if w.get('stroke') is not None]

    print(f"\n  Punya 'components' terisi : {len(has_components):5d}  ({100*len(has_components)/total:.1f}%)")
    print(f"  Punya 'radical' terisi    : {len(has_radical):5d}  ({100*len(has_radical)/total:.1f}%)")
    print(f"  Punya 'structure' terisi  : {len(has_structure):5d}  ({100*len(has_structure)/total:.1f}%)")
    print(f"  Punya 'stroke' terisi     : {len(has_stroke):5d}  ({100*len(has_stroke)/total:.1f}%)")

    # Distribusi nilai structure yang ada
    struct_counter = Counter(w['structure'] for w in has_structure)
    print(f"\n  Distribusi nilai 'structure' ({len(struct_counter)} tipe unik):")
    for val, count in struct_counter.most_common(15):
        print(f"    {val:20s} : {count}")

    # Berapa banyak karakter 1-hanzi yang punya components DAN structure
    # sekaligus (ini yang paling penting utk modul -- perlu KEDUANYA)
    single_char_words = [w for w in words if len(w.get('simplified', '')) == 1]
    single_complete = [
        w for w in single_char_words
        if w.get('components') and w.get('structure')
    ]
    print(f"\n  Kata 1-karakter total                     : {len(single_char_words)}")
    print(f"  Kata 1-karakter dgn components+structure  : {len(single_complete)} "
          f"({100*len(single_complete)/max(1,len(single_char_words)):.1f}%)")

    # Tampilkan 5 contoh entry lengkap
    print(f"\n  --- 5 contoh entry lengkap (components+structure+radical+stroke) ---")
    shown = 0
    for w in words:
        if w.get('components') and w.get('structure') and w.get('radical') and w.get('stroke') is not None:
            print(f"    {w.get('simplified')!r:6s} pinyin={w.get('pinyin')!r:10s} "
                  f"components={w.get('components')!r:20s} structure={w.get('structure')!r:15s} "
                  f"radical={w.get('radical')!r:6s} stroke={w.get('stroke')!r}")
            shown += 1
            if shown >= 5:
                break
    if shown == 0:
        print("    (tidak ditemukan entry yang lengkap ke-4 field sekaligus)")

    return words


def search_real_stroke_data(search_dir='.'):
    separator("2. MENCARI DATA STROKE-ORDER ASLI (jalur vektor per-goresan)")

    # Kata kunci nama file yang umum dipakai dataset stroke-order asli
    filename_hints = [
        '*stroke*order*', '*strokeorder*', '*hanzi*writer*',
        '*hanziwriter*', '*makemeahanzi*', '*make_me_a_hanzi*',
        '*graphics*.json', '*medians*',
    ]

    candidates = set()
    for hint in filename_hints:
        candidates.update(glob.glob(os.path.join(search_dir, '**', hint), recursive=True))

    # Field kunci yang menandakan data stroke asli (bukan cuma metadata)
    content_hints = ['strokes', 'medians', 'svg', 'path', 'stroke_paths', 'strokePaths']

    print("  Mencari berdasarkan nama file...")
    if candidates:
        print(f"  Ditemukan {len(candidates)} file dengan nama mencurigakan:")
        for c in sorted(candidates):
            print(f"    - {c}")
    else:
        print("  Tidak ada file dengan nama yang cocok.")

    # Scan semua .json di project untuk field yang mengindikasikan stroke path asli
    print("\n  Memindai isi semua file .json di proyek (mencari field seperti "
          "'strokes'/'medians'/'svg' yang mengindikasikan jalur vektor asli)...")
    json_files = glob.glob(os.path.join(search_dir, '**', '*.json'), recursive=True)
    hits = []
    for jf in json_files:
        try:
            with open(jf, encoding='utf-8') as f:
                sample = f.read(2000)  # cukup baca awal file saja, hemat waktu
            found = [h for h in content_hints if f'"{h}"' in sample]
            if found:
                hits.append((jf, found))
        except Exception:
            continue

    if hits:
        print(f"\n  Ditemukan {len(hits)} file .json yang MUNGKIN berisi data stroke asli:")
        for jf, found in hits:
            print(f"    - {jf}  (field: {found})")
        print("\n  ⚠ Kalau salah satu di atas memang berisi jalur vektor stroke order,")
        print("    kabari -- modul bisa dibuat jauh lebih kaya dari rencana awal.")
    else:
        print("\n  Tidak ditemukan file .json manapun yang mengindikasikan data stroke asli.")
        print("  Kesimpulan: rencana fallback (urutan komponen dari struktur) yang tepat dipakai.")


def main():
    words = inspect_app_words()
    search_real_stroke_data('.')
    separator("SELESAI")
    print("  Script ini bersifat eksploratif -- ia membaca file yang ada")
    print("  dan menampilkannya dengan rapi. Tidak ada yang diubah.\n")


if __name__ == '__main__':
    main()

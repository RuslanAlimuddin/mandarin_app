"""
combine_explanations.py
Gabungkan 7 file pattern_explanations_part*.json (folder root proyek)
menjadi satu data/pattern_explanations.json untuk dipakai wordbuilder.html.

Jalankan dari folder root proyek (C:\\mandarin_app):
    python combine_explanations.py
"""

import json
import os

PART_FILES = [
    'pattern_explanations_part1_dasar.json',
    'pattern_explanations_part2_deskripsi.json',
    'pattern_explanations_part3_waktu_aspek.json',
    'pattern_explanations_part4_tanya.json',
    'pattern_explanations_part5_majemuk_hubungan.json',
    'pattern_explanations_part6_majemuk_perbandingan.json',
    'pattern_explanations_part7_fungsi.json',
]

OUTPUT_PATH = 'data/pattern_explanations.json'

REQUIRED_FIELDS = [
    'penjelasan_dasar', 'perbandingan_indonesia', 'kapan_tidak_boleh',
    'kesalahan_umum', 'contoh_tambahan', 'pola_terkait',
]


def main():
    combined = {}
    missing_files = []

    for fname in PART_FILES:
        if not os.path.exists(fname):
            missing_files.append(fname)
            continue
        with open(fname, encoding='utf-8') as f:
            data = json.load(f)
        overlap = set(data.keys()) & set(combined.keys())
        if overlap:
            print(f"⚠ Peringatan: pola duplikat ditemukan di {fname}: {overlap}")
        combined.update(data)

    if missing_files:
        print("✗ File berikut tidak ditemukan (pastikan ada di folder yang sama):")
        for f in missing_files:
            print(f"   - {f}")
        print("\nProses dibatalkan.")
        return

    # Validasi tiap pola punya 6 field lengkap
    problems = []
    for key, val in combined.items():
        missing = [f for f in REQUIRED_FIELDS if f not in val]
        if missing:
            problems.append((key, missing))

    if problems:
        print("⚠ Beberapa pola tidak lengkap field-nya:")
        for key, missing in problems:
            print(f"   - {key}: kurang {missing}")

    os.makedirs('data', exist_ok=True)
    with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
        json.dump(combined, f, ensure_ascii=False, indent=2)

    print(f"✓ Selesai. {len(combined)} pola digabung ke '{OUTPUT_PATH}'.")


if __name__ == '__main__':
    main()

"""
gabung_wordbuilder.py
Gabungkan wordbuilder_PART_1..4.txt (folder parts/) -> wordbuilder.html (folder root).

Urutan penggabungan:
  PART_1 = <head> + CSS lokal
  PART_2 = <body> + HTML (navbar, sidebar, main area)
  PART_3 = <script> data pola (PATTERNS) + komentar WORD_POOLS
  PART_4 = <script> engine render, event handler, init

Jalankan dari folder root proyek (C:\\mandarin_app):
    python gabung_wordbuilder.py
"""

import os

PARTS_DIR = 'parts'
OUTPUT    = 'wordbuilder.html'

PART_FILES = [
    'wordbuilder_PART_1.txt',
    'wordbuilder_PART_2.txt',
    'wordbuilder_PART_3.txt',
    'wordbuilder_PART_4.txt',
]


def main():
    combined = []
    for fname in PART_FILES:
        path = os.path.join(PARTS_DIR, fname)
        if not os.path.exists(path):
            print(f"✗ Tidak ditemukan: {path}")
            return
        with open(path, encoding='utf-8') as f:
            combined.append(f.read())

    result = ''.join(combined)

    with open(OUTPUT, 'w', encoding='utf-8') as f:
        f.write(result)

    print(f"✓ Selesai. {OUTPUT} dibuat dari {len(PART_FILES)} file PART.")
    print(f"  Total ukuran: {len(result):,} karakter.")


if __name__ == '__main__':
    main()

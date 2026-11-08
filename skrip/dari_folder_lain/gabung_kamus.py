# gabung_kamus.py — gabungkan PART 1-6 menjadi kamus.html
import os

PARTS = [
    'kamus_PART_1.txt',
    'kamus_PART_2.txt',
    'kamus_PART_3.txt',
    'kamus_PART_4.txt',
    'kamus_PART_5.txt',
    'kamus_PART_6.txt',
]

OUTPUT = 'kamus.html'

with open(OUTPUT, 'w', encoding='utf-8') as out:
    for i, part in enumerate(PARTS):
        if not os.path.exists(part):
            print(f'[ERROR] File tidak ditemukan: {part}')
            exit(1)
        with open(part, 'r', encoding='utf-8') as f:
            content = f.read()
        if i > 0:
            out.write('\n')
        out.write(content)
        print(f'[OK] {part} ({len(content.splitlines())} baris)')

print(f'\n[SELESAI] {OUTPUT} berhasil dibuat.')

# gabung_flashcard.py — gabungkan PART 1-5 menjadi flashcard.html
import os

PARTS = [
    'flashcard_PART_1.txt',
    'flashcard_PART_2.txt',
    'flashcard_PART_3.txt',
    'flashcard_PART_4.txt',
    'flashcard_PART_5.txt',
]

OUTPUT = 'flashcard.html'

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

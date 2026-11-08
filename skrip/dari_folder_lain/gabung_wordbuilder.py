#!/usr/bin/env python3
# gabung_wordbuilder.py
# Jalankan di folder mandarin_app/
# python gabung_wordbuilder.py

parts = [
    'wordbuilder_PART_1.txt',
    'wordbuilder_PART_2.txt',
    'wordbuilder_PART_3.txt',
    'wordbuilder_PART_4.txt',
]

output_file = 'wordbuilder.html'

with open(output_file, 'w', encoding='utf-8') as out:
    for part in parts:
        try:
            with open(part, 'r', encoding='utf-8') as f:
                content = f.read()
                out.write(content)
                if not content.endswith('\n'):
                    out.write('\n')
            print(f'  ✓ {part}')
        except FileNotFoundError:
            print(f'  ✗ TIDAK DITEMUKAN: {part}')

print(f'\n✅ {output_file} berhasil dibuat!')
print(f'   Buka di browser: wordbuilder.html')

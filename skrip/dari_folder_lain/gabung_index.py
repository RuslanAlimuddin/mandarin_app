#!/usr/bin/env python3
# gabung_index.py
# python gabung_index.py

parts = ['index_PART_1.txt', 'index_PART_2.txt']
output_file = 'index.html'

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

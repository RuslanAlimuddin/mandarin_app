#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
split_to_parts.py — pecah file .html (flashcard.html / kamus.html, atau file
lain yang pakai konvensi PART yang sama) jadi PART_1..N.txt.

Konvensi yang dideteksi otomatis:
  - PART 1 = dari awal file s/d akhir tag </head> (inklusif)
  - PART 2 = dari <body> s/d SEBELUM <script> PART 3 pertama
  - PART 3, 4, 5, ... = tiap <script> yang komentar pembukanya berbunyi
    "<nama_file> — PART <n>: ..." (persis format yang sudah dipakai
    di flashcard.html/kamus.html)

Cara pakai:
    python split_to_parts.py flashcard.html
    python split_to_parts.py kamus.html

Hasil: flashcard_PART_1.txt, flashcard_PART_2.txt, dst -- di folder yang
sama dengan file sumbernya. PART file lama dengan nama sama akan DITIMPA
(pastikan sudah tidak ada revisi manual belum tersimpan di PART lama
sebelum menjalankan ini).

Skrip ini TIDAK mengubah isi apa pun -- murni memotong berdasarkan posisi
penanda, byte-per-byte. Kalau mau verifikasi hasilnya identik dengan
sumbernya, jalankan lagi gabung_flashcard.py / gabung_kamus.py dan
bandingkan (harus sama persis).
"""
import os
import re
import sys

PART_MARKER_RE = re.compile(
    r'<script>\s*\n\s*/\*.*?\n\s*[\w.\-]+\s*—\s*PART\s+(\d+)\s*:',
    re.DOTALL
)


def split_file(path):
    with open(path, 'rb') as f:
        raw = f.read()
    # deteksi & pertahankan gaya line-ending asli file
    text = raw.decode('utf-8')

    base = os.path.splitext(os.path.basename(path))[0]
    out_dir = os.path.dirname(os.path.abspath(path))

    # 1) cari akhir </head> (batas PART 1 / PART 2)
    head_match = re.search(r'</head>\s*\n?', text, re.IGNORECASE)
    if not head_match:
        print('[ERROR] Tidak ditemukan tag </head> -- file ini mungkin tidak'
              ' pakai konvensi PART yang sama. Cek manual.')
        return False
    part1_end = head_match.end()

    # 2) cari semua marker PART N (N >= 3) lewat komentar pembuka <script>
    markers = []
    for m in PART_MARKER_RE.finditer(text):
        n = int(m.group(1))
        markers.append((n, m.start()))  # posisi mulai dari '<script>'

    if not markers:
        print('[ERROR] Tidak ditemukan marker "— PART n:" sama sekali.'
              ' Cek manual apakah file ini memang pakai konvensi PART.')
        return False

    markers.sort(key=lambda t: t[1])  # urutkan berdasar posisi di file
    # validasi nomor urut PART berurutan & masuk akal
    expected = 3
    for n, _ in markers:
        if n != expected:
            print(f'[WARNING] Urutan PART tidak berurutan -- ketemu PART {n},'
                  f' harusnya PART {expected}. Lanjut tetap, tapi cek hasilnya.')
        expected = n + 1

    # 3) susun batas-batas potongan
    bounds = [0, part1_end]                      # awal PART1, akhir PART1(=awal PART2)
    bounds.append(markers[0][1])                 # akhir PART2 (=awal PART3)
    for i in range(1, len(markers)):
        bounds.append(markers[i][1])             # akhir PART(2+i) (=awal PART(3+i))
    bounds.append(len(text))                     # akhir PART terakhir

    total_parts = len(markers) + 2                # PART1 + PART2 + tiap marker
    if len(bounds) - 1 != total_parts:
        print(f'[ERROR] Jumlah potongan ({len(bounds)-1}) tidak cocok dengan'
              f' ekspektasi ({total_parts}). Batalkan, cek manual.')
        return False

    written = []
    for i in range(total_parts):
        chunk = text[bounds[i]:bounds[i + 1]]
        out_name = f'{base}_PART_{i + 1}.txt'
        out_path = os.path.join(out_dir, out_name)
        with open(out_path, 'w', encoding='utf-8', newline='') as f:
            f.write(chunk)
        written.append((out_name, len(chunk)))

    print(f'Selesai. {len(written)} PART file ditulis di: {out_dir}')
    for name, size in written:
        print(f'  {name}  ({size} karakter)')
    print('\nTimpa PART lama رسلان dengan file-file ini, lalu lanjut edit'
          ' via PART seperti biasa.')
    return True


def main():
    if len(sys.argv) != 2:
        print('Pemakaian: python split_to_parts.py <file.html>')
        sys.exit(1)
    path = sys.argv[1]
    if not os.path.isfile(path):
        print(f'File tidak ditemukan: {path}')
        sys.exit(1)
    ok = split_file(path)
    sys.exit(0 if ok else 1)


if __name__ == '__main__':
    main()

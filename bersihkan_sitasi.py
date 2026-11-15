#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
bersihkan_sitasi.py -- menghapus sisa penanda "[citation:n]" dari berkas data Tata Bahasa.

Latar belakang: penanda seperti [citation:1] adalah sisa dari alat penyusun data, bukan isi pelajaran.
Letaknya selalu di akhir isi kolom (fungsi, terjemahan, penjelasan, "Arti / Catatan"), kadang tepat
sebelum titik penutup. Skrip ini menghapus penanda itu beserta spasi di depannya, sehingga
"... standar [citation:1]." menjadi "... standar."

Cara pakai (jalankan dari folder C:\\mandarin_app):
  python bersihkan_sitasi.py            -> hanya MELIHAT (tidak mengubah apa pun)
  python bersihkan_sitasi.py --apply    -> menghapus (cadangan tiap berkas dibuat otomatis)

Yang diperiksa skrip: seluruh data\\*.json dan data\\pelajaran\\*.json. Berkas tanpa penanda tidak disentuh.
Setelah menulis, skrip memastikan: JSON masih valid, struktur isi sama persis, hanya penanda yang hilang,
dan tidak ada penanda tersisa. Bila ada yang tidak cocok, berkas dikembalikan dari cadangan.
Aman dijalankan ulang. Cadangan: <berkas>.bak_sitasi_<tanggal-jam>. Untuk membatalkan, salin kembali.
"""
import glob
import io
import json
import os
import re
import shutil
import sys
import time

TS = time.strftime('%Y%m%d_%H%M%S')
RUN = re.compile(r'(?:[ \t]*\[citation:\d+\])+')
ANY = re.compile(r'\[citation:\d+\]')


def strip_value(o):
    """terapkan penghapusan yang sama pada nilai yang sudah di-decode (untuk membandingkan struktur)"""
    if isinstance(o, str):
        return RUN.sub('', o)
    if isinstance(o, list):
        return [strip_value(x) for x in o]
    if isinstance(o, dict):
        return {k: strip_value(v) for k, v in o.items()}
    return o


def fail(msg):
    print('GAGAL: ' + msg)
    sys.exit(1)


def main():
    apply = '--apply' in sys.argv
    print('Mode: ' + ('HAPUS (--apply)' if apply else 'LIHAT-DULU (tidak mengubah apa pun)'))
    if not os.path.isdir('data'):
        fail('folder data tidak ditemukan (jalankan dari folder C:\\mandarin_app)')
    files = sorted(glob.glob(os.path.join('data', '*.json')) + glob.glob(os.path.join('data', 'pelajaran', '*.json')))
    todo = []
    for f in files:
        with io.open(f, encoding='utf-8', newline='') as fh:
            text = fh.read()
        n = len(ANY.findall(text))
        if n:
            todo.append((f, text, n))
    if not todo:
        print('Tidak ada penanda [citation:n] di berkas data mana pun. Tidak ada yang perlu dilakukan.')
        return
    total = 0
    for f, text, n in todo:
        total += n
        runs = RUN.findall(text)
        print('%-28s %4d penanda dalam %3d tempat' % (f.replace('\\', '/'), n, len(runs)))
        shown = 0
        for m in RUN.finditer(text):
            a = text[max(0, m.start() - 34):m.start()].replace('\n', ' ')
            b = text[m.end():m.end() + 6].replace('\n', ' ')
            print('      sebelum: ...%s%s%s' % (a, m.group(0).strip(), b))
            print('      sesudah: ...%s%s' % (a, b))
            shown += 1
            if shown >= 2:
                break
    print('Total: %d penanda di %d berkas' % (total, len(todo)))

    if not apply:
        print('\nBelum ada yang diubah. Jika sudah sesuai, jalankan:  python bersihkan_sitasi.py --apply')
        return

    for f, text, n in todo:
        new = RUN.sub('', text)
        try:
            before = json.loads(text)
            after = json.loads(new)
        except ValueError as e:
            fail('%s: hasil bukan JSON yang valid (%s); tidak ada yang ditulis untuk berkas ini' % (f, e))
        if strip_value(before) != after or ANY.search(new):
            fail('%s: pemeriksaan struktur gagal; tidak ada yang ditulis untuk berkas ini' % f)
        bak = f + '.bak_sitasi_' + TS
        shutil.copy2(f, bak)
        with io.open(f, 'w', encoding='utf-8', newline='') as fh:
            fh.write(new)
        with io.open(f, encoding='utf-8', newline='') as fh:
            chk = fh.read()
        if chk != new or ANY.search(chk):
            shutil.copy2(bak, f)
            fail('%s: pemeriksaan akhir gagal; dikembalikan dari cadangan' % f)
        print('OK  %s: %d penanda dihapus (cadangan: %s)' % (f.replace('\\', '/'), n, os.path.basename(bak)))
    print('SELESAI. Muat ulang Tata Bahasa (Ctrl+F5) dan buka satu poin di HSK 5 atau HSK 9 untuk memeriksa.')


if __name__ == '__main__':
    main()

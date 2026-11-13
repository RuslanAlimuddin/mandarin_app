#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pasang_afiks_kamus.py -- memasang menu "Awalan & Akhiran" ke kamus.html.

Yang dilakukan (hanya 2 penambahan kecil di kamus.html):
  1. item sidebar "Awalan & Akhiran" tepat di bawah "Akar Kosakata"
  2. satu baris <script src="kamus/kamus-afiks.js"> sebelum kamus-init.js

Cara pakai (jalankan dari folder C:\\mandarin_app):
  python pasang_afiks_kamus.py            -> hanya MELIHAT (tidak mengubah apa pun)
  python pasang_afiks_kamus.py --apply    -> memasang (cadangan dibuat otomatis)

Aman dijalankan ulang: bagian yang sudah terpasang dilewati.
Berkas lain tidak disentuh. Cadangan: kamus.html.bak_afiks_<tanggal-jam>
Cara membatalkan: salin kembali berkas cadangan itu menjadi kamus.html.
"""
import io
import json
import os
import shutil
import sys
import time

HTML = 'kamus.html'
JS = os.path.join('kamus', 'kamus-afiks.js')
DATA = os.path.join('data', 'afiks_kamus.json')

MARK_ITEM = 'data-filter="group-afiks"'
MARK_SCRIPT = 'kamus/kamus-afiks.js'
ANCHOR_AKAR = 'data-filter="group-akar"'
ANCHOR_SCRIPT = '<script src="kamus/kamus-init.js"></script>'


def fail(msg):
    print('GAGAL: ' + msg)
    sys.exit(1)


def main():
    apply = '--apply' in sys.argv
    print('Mode: ' + ('PASANG (--apply)' if apply else 'LIHAT-DULU (tidak mengubah apa pun)'))

    # 1. prasyarat
    for p in (HTML, JS, DATA):
        if not os.path.isfile(p):
            fail('berkas tidak ditemukan: %s (jalankan dari folder C:\\mandarin_app dan pastikan berkas sudah ditaruh)' % p)
    try:
        with io.open(DATA, encoding='utf-8') as f:
            d = json.load(f)
        if not isinstance(d, list) or len(d) != 60:
            fail('%s harus berupa daftar 60 entri (ditemukan: %s)' % (DATA, len(d) if isinstance(d, list) else type(d).__name__))
    except ValueError as e:
        fail('%s bukan JSON yang valid: %s' % (DATA, e))
    print('OK  data/afiks_kamus.json: 60 entri, JSON valid')
    print('OK  kamus/kamus-afiks.js ditemukan')

    with io.open(HTML, encoding='utf-8', newline='') as f:
        text = f.read()
    nl = '\r\n' if '\r\n' in text else '\n'
    new = text
    changes = []

    # 2. item sidebar (setelah item Akar Kosakata)
    if MARK_ITEM in new:
        print('--  item sidebar: sudah terpasang, dilewati')
    else:
        if new.count(ANCHOR_AKAR) != 1:
            fail('penanda item "Akar Kosakata" tidak ditemukan tepat 1 kali (ditemukan %d)' % new.count(ANCHOR_AKAR))
        i = new.index(ANCHOR_AKAR)
        j = new.index('</div>', i) + len('</div>')
        line_start = new.rfind('\n', 0, i) + 1
        indent = new[line_start:i]
        indent = indent if indent.strip() == '' else '        '
        block = (nl + indent + '<div class="sidebar-item" data-filter="group-afiks" onclick="openGroupPanel(\'afiks\')">' +
                 nl + indent + '  <span>🧩 Awalan &amp; Akhiran</span>' +
                 nl + indent + '  <span class="item-count" id="cnt-afiks">…</span>' +
                 nl + indent + '</div>')
        new = new[:j] + block + new[j:]
        changes.append('menambah item sidebar "🧩 Awalan & Akhiran" di bawah Akar Kosakata')

    # 3. baris script (sebelum kamus-init.js)
    if MARK_SCRIPT in new:
        print('--  baris script: sudah terpasang, dilewati')
    else:
        if new.count(ANCHOR_SCRIPT) != 1:
            fail('baris <script src="kamus/kamus-init.js"> tidak ditemukan tepat 1 kali (ditemukan %d)' % new.count(ANCHOR_SCRIPT))
        new = new.replace(ANCHOR_SCRIPT, '<script src="kamus/kamus-afiks.js"></script>' + nl + ANCHOR_SCRIPT)
        changes.append('menambah <script src="kamus/kamus-afiks.js"> sebelum kamus-init.js')

    if not changes:
        print('Tidak ada yang perlu diubah: semuanya sudah terpasang.')
        return
    print('Perubahan pada kamus.html:')
    for c in changes:
        print('  + ' + c)
    print('Ukuran: %d -> %d karakter (%+d)' % (len(text), len(new), len(new) - len(text)))

    if not apply:
        print('\nBelum ada yang diubah. Jika sudah sesuai, jalankan:  python pasang_afiks_kamus.py --apply')
        return

    # 4. cadangan lalu tulis
    bak = HTML + '.bak_afiks_' + time.strftime('%Y%m%d_%H%M%S')
    shutil.copy2(HTML, bak)
    print('Cadangan dibuat: ' + bak)
    with io.open(HTML, 'w', encoding='utf-8', newline='') as f:
        f.write(new)

    # 5. periksa hasilnya
    with io.open(HTML, encoding='utf-8', newline='') as f:
        chk = f.read()
    ok = (MARK_ITEM in chk and MARK_SCRIPT in chk and chk.index(MARK_SCRIPT) < chk.index(ANCHOR_SCRIPT))
    if not ok:
        shutil.copy2(bak, HTML)
        fail('pemeriksaan akhir gagal; kamus.html dikembalikan dari cadangan')
    print('SELESAI. Buka kamus.html (muat ulang dengan Ctrl+F5) dan cari "🧩 Awalan & Akhiran" di bawah Akar Kosakata.')


if __name__ == '__main__':
    main()

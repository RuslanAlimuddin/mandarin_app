#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
arsipkan_pilar3.py -- memindahkan pilar_3.json (yang ternyata salinan pelajaran Pilar 5) ke folder arsip.

Latar belakang: data\\pelajaran\\pilar_3.json isinya sama dengan pilar_5.json (Kata Kerja Modal),
padahal Pilar 3 adalah 量词. Akibatnya tombol "Pelajaran Lengkap" Pilar 3 menampilkan pelajaran yang salah.
Setelah berkas dipindahkan, tombol itu menampilkan pesan bawaan Peta Bahasa:
"Pelajaran lengkap untuk pilar ini belum dibuat." Berkas TIDAK dihapus: ia dipindah ke
data\\pelajaran\\arsip\\pilar_3_salinan_pilar5.json.

Cara pakai (jalankan dari folder C:\\mandarin_app):
  python arsipkan_pilar3.py            -> hanya MELIHAT (tidak mengubah apa pun)
  python arsipkan_pilar3.py --apply    -> memindahkan

Skrip hanya memindahkan bila isi pilar_3.json memang SAMA dengan pilar_5.json (agar tidak salah
memindahkan pelajaran 量词 yang kelak sudah benar). Aman dijalankan ulang.
Untuk membatalkan, pindahkan kembali berkas dari folder arsip ke data\\pelajaran\\pilar_3.json.
"""
import io
import json
import os
import shutil
import sys

P3 = os.path.join('data', 'pelajaran', 'pilar_3.json')
P5 = os.path.join('data', 'pelajaran', 'pilar_5.json')
ARS = os.path.join('data', 'pelajaran', 'arsip')
DEST = os.path.join(ARS, 'pilar_3_salinan_pilar5.json')


def fail(msg):
    print('GAGAL: ' + msg)
    sys.exit(1)


def main():
    apply = '--apply' in sys.argv
    print('Mode: ' + ('PINDAHKAN (--apply)' if apply else 'LIHAT-DULU (tidak mengubah apa pun)'))
    if not os.path.isdir(os.path.join('data', 'pelajaran')):
        fail('folder data\\pelajaran tidak ditemukan (jalankan dari folder C:\\mandarin_app)')
    if not os.path.isfile(P3):
        print('pilar_3.json sudah tidak ada di data\\pelajaran (mungkin sudah diarsipkan). Tidak ada yang perlu dilakukan.')
        return
    if not os.path.isfile(P5):
        fail('pilar_5.json tidak ditemukan; tidak bisa memastikan pilar_3.json adalah salinan')
    with io.open(P3, encoding='utf-8') as f:
        a = json.load(f)
    with io.open(P5, encoding='utf-8') as f:
        b = json.load(f)
    if a != b:
        fail('isi pilar_3.json TIDAK sama dengan pilar_5.json, jadi tidak dipindahkan (mungkin sudah diganti pelajaran yang benar)')
    print('OK  pilar_3.json isinya sama dengan pilar_5.json (judul: "%s", %d bagian)' % (a.get('judul', '?'), len(a.get('bagian', []))))
    print('  + akan dipindahkan ke %s' % DEST.replace('\\', '/'))
    if os.path.exists(DEST):
        fail('berkas tujuan sudah ada: ' + DEST)
    if not apply:
        print('\nBelum ada yang diubah. Jika sudah sesuai, jalankan:  python arsipkan_pilar3.py --apply')
        return
    os.makedirs(ARS, exist_ok=True)
    shutil.move(P3, DEST)
    if os.path.exists(P3) or not os.path.isfile(DEST):
        fail('pemindahan tidak berhasil sempurna; periksa folder data\\pelajaran')
    print('SELESAI. Buka peta-bahasa.html (Ctrl+F5) → kartu Pilar 3 → "Pelajaran Lengkap": kini tampil pesan "belum dibuat".')


if __name__ == '__main__':
    main()

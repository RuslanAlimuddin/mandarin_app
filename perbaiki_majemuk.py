#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
perbaiki_majemuk.py -- memperbaiki 7 kata (hasil pemeriksaan kata majemuk) sesuai tabel yang sudah disetujui:
  犹太节日  jiē -> jié (sisa kesalahan bacaan lama)      看得见 / 懒得  得 dé -> de (netral)
  延误  yán wu -> yán wù                                 欧洲 / 奥运会  tanda nada yang salah letak
  闺女  tanda ˙ yang nyasar dibuang
Berkas yang diubah: data\\app_words.json, data\\produktif_karakter.json (pinyin kata turunan),
data\\nuance_pairs.json (pinyin kata). Pinyin angka dan zhuyin dibuat ulang untuk 4 kata yang bacaannya berubah.

Cara pakai (jalankan dari folder C:\\mandarin_app):
  python perbaiki_majemuk.py            -> hanya MELIHAT (tidak mengubah apa pun)
  python perbaiki_majemuk.py --apply    -> menerapkan (cadangan dibuat otomatis)

Cadangan: data\\<berkas>.json.bak_majemuk_<tanggal-jam>. Untuk membatalkan, salin kembali ke nama aslinya.
Skrip menolak bekerja bila nilai lama di data tidak sama dengan yang tercatat (data sudah berubah). Aman dijalankan ulang.
"""
import io
import json
import os
import re
import shutil
import sys
import time
import unicodedata

TS = time.strftime('%Y%m%d_%H%M%S')
# (kata, pinyin_lama, pinyin_baru, angka_lama, angka_baru, zhuyin_lama, zhuyin_baru)
TABEL = [
    ('犹太节日', 'yóu tài jiē rì', 'yóu tài jié rì', 'you2 tai4 jie1 ri4', 'you2 tai4 jie2 ri4', 'ㄧㄡˊ ㄊㄞˋ ㄐㄧㄝ ㄖˋ', 'ㄧㄡˊ ㄊㄞˋ ㄐㄧㄝˊ ㄖˋ'),
    ('看得见', 'kàn dé jiàn', 'kàn de jiàn', 'kan4 de2 jian4', 'kan4 de5 jian4', 'ㄎㄢˋ ㄉㄜˊ ㄐㄧㄢˋ', 'ㄎㄢˋ ㄉㄜ˙ ㄐㄧㄢˋ'),
    ('懒得', 'lǎn dé', 'lǎn de', 'lan3 de2', 'lan3 de5', 'ㄌㄢˇ ㄉㄜˊ', 'ㄌㄢˇ ㄉㄜ˙'),
    ('延误', 'yán wu', 'yán wù', 'yan2 wu5', 'yan2 wu4', 'ㄧㄢˊ ㄨ˙', 'ㄧㄢˊ ㄨˋ'),
    ('欧洲', 'Oū zhōu', 'Ōu zhōu', 'Ou1 zhou1', 'Ou1 zhou1', 'ㄡ ㄓㄡ', 'ㄡ ㄓㄡ'),
    ('奥运会', 'Aò yùn huì', 'Ào yùn huì', 'Ao4 yun4 hui4', 'Ao4 yun4 hui4', 'ㄠˋ ㄩㄣˋ ㄏㄨㄟˋ', 'ㄠˋ ㄩㄣˋ ㄏㄨㄟˋ'),
    ('闺女', 'guī ˙nü', 'guī nü', 'gui1 nü5', 'gui1 nü5', 'ㄍㄨㄟ ㄋㄩ˙', 'ㄍㄨㄟ ㄋㄩ˙'),
]
# penulisan lama lain yang muncul di berkas turunan
ALT_OLD = {'闺女': ['guī ˙nu:']}


def fail(msg):
    print('GAGAL: ' + msg)
    sys.exit(1)


def fl(s):
    return re.sub(r"[\s'’·-]", '', unicodedata.normalize('NFC', (s or '').lower()))


def load(name):
    path = os.path.join('data', name + '.json')
    with io.open(path, encoding='utf-8', newline='') as f:
        raw = f.read()
    nl = '\r\n' if '\r\n' in raw else '\n'
    return json.loads(raw.replace('\r\n', '\n')), nl, raw


def dump(obj, nl):
    s = json.dumps(obj, ensure_ascii=False, indent=2, separators=(',', ': '))
    return s.replace('\n', nl) if nl != '\n' else s


def walk(o, fn):
    if isinstance(o, dict):
        fn(o)
        for v in o.values():
            walk(v, fn)
    elif isinstance(o, list):
        for v in o:
            walk(v, fn)


def main():
    apply = '--apply' in sys.argv
    print('Mode: ' + ('TERAPKAN (--apply)' if apply else 'LIHAT-DULU (tidak mengubah apa pun)'))
    names = ('app_words', 'produktif_karakter', 'nuance_pairs')
    for nm in names:
        if not os.path.isfile(os.path.join('data', nm + '.json')):
            fail('berkas tidak ditemukan: data\\%s.json (jalankan dari folder C:\\mandarin_app)' % nm)
    L = {nm: load(nm) for nm in names}
    words = L['app_words'][0]
    W = {w['simplified']: w for w in words}
    done, todo, bad = [], [], []
    for kata, py0, py1, n0, n1, z0, z1 in TABEL:
        e = W.get(kata)
        if e is None:
            fail('kata tidak ada di app_words.json: ' + kata)
        cur = (e['pinyin'], e.get('pinyin_numeric'), e.get('bopomofo'))
        if cur == (py1, n1, z1):
            done.append(kata)
        elif cur == (py0, n0, z0):
            todo.append((kata, py0, py1, n0, n1, z0, z1))
        else:
            bad.append((kata, cur))
    if bad:
        for k, c in bad:
            print('  tidak sesuai daftar: %s -> %s' % (k, c))
        fail('%d kata berbeda dari nilai yang tercatat; tidak ada yang diubah' % len(bad))
    print('Sudah benar: %d | akan diperbaiki: %d' % (len(done), len(todo)))
    for kata, py0, py1, n0, n1, z0, z1 in todo:
        e = W[kata]
        e['pinyin'], e['pinyin_numeric'], e['bopomofo'] = py1, n1, z1
        print('    %s | pinyin: %s -> %s%s%s' % (kata, py0, py1,
              (' | angka: %s -> %s' % (n0, n1)) if n0 != n1 else '', (' | zhuyin: %s -> %s' % (z0, z1)) if z0 != z1 else ''))
    new_py = {t[0]: t[2] for t in TABEL}
    old_set = {t[0]: {fl(t[1])} | {fl(a) for a in ALT_OLD.get(t[0], [])} for t in TABEL}
    cnt = {'produktif_karakter': 0, 'nuance_pairs': 0}
    for root, v in L['produktif_karakter'][0].items():
        for d in v.get('kata_turunan', []):
            k = d.get('kata')
            if k in new_py and fl(d.get('pinyin')) in old_set[k] and d['pinyin'] != new_py[k]:
                d['pinyin'] = new_py[k]
                cnt['produktif_karakter'] += 1

    def fn_nuance(d):
        k = d.get('word')
        if k in new_py and isinstance(d.get('pinyin'), str) and fl(d['pinyin']) in old_set[k] and d['pinyin'] != new_py[k]:
            d['pinyin'] = new_py[k]
            cnt['nuance_pairs'] += 1
    walk(L['nuance_pairs'][0], fn_nuance)
    print('produktif_karakter.json: %d baris diubah | nuance_pairs.json: %d baris diubah' % (cnt['produktif_karakter'], cnt['nuance_pairs']))
    if not todo and not any(cnt.values()):
        print('Tidak ada yang perlu diubah: semuanya sudah benar.')
        return
    if not apply:
        print('\nBelum ada yang diubah. Jika sudah sesuai, jalankan:  python perbaiki_majemuk.py --apply')
        return
    for nm in names:
        obj, nl, raw = L[nm]
        new_raw = dump(obj, nl)
        if new_raw == raw:
            print('--  %s.json: tidak berubah' % nm)
            continue
        path = os.path.join('data', nm + '.json')
        bak = path + '.bak_majemuk_' + TS
        shutil.copy2(path, bak)
        with io.open(path, 'w', encoding='utf-8', newline='') as f:
            f.write(new_raw)
        with io.open(path, encoding='utf-8', newline='') as f:
            chk = f.read()
        try:
            ok = (chk == new_raw) and json.loads(chk.replace('\r\n', '\n')) == obj
        except ValueError:
            ok = False
        if not ok:
            shutil.copy2(bak, path)
            fail('%s: pemeriksaan akhir gagal; dikembalikan dari cadangan' % path)
        print('OK  %s.json ditulis (cadangan: %s)' % (nm, os.path.basename(bak)))
    print('SELESAI. Muat ulang aplikasi dengan Ctrl+F5.')


if __name__ == '__main__':
    main()

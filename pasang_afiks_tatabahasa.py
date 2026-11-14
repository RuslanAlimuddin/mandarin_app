#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pasang_afiks_tatabahasa.py -- menambah 60 poin "Awalan & Akhiran" (AFX.01-AFX.60) ke tatabahasa.html.

Cara kerja: Awalan & Akhiran diperlakukan sebagai "level ke-10" yang datanya diambil dari
data/grammar_afiks.json, sehingga layar kategori, daftar poin, rincian, Daftar Isi, dan
pencarian yang sudah ada ikut bekerja. Yang berubah hanya tatabahasa.html (12 penggantian
teks kecil). Sembilan berkas level HSK tidak disentuh.

Yang ditambahkan untuk pengguna:
  1. kartu "Awalan & Akhiran" di layar awal (di bawah kartu HSK 1-9)
  2. 60 poin masuk topik "Prefix & Suffix (Imbuhan)" di Daftar Isi (penanda AFX)
  3. pencarian ikut menemukan poin AFX
  4. di rincian poin AFX: tingkat HSK terendah + tombol "Lihat di Kamus"; untuk 们, 子, 第
     ada tombol ke poin lama
  5. tautan langsung:  tatabahasa.html#point=AFX.01  (juga #point=hsk1-57 untuk poin lama)

Cara pakai (jalankan dari folder C:\\mandarin_app):
  python pasang_afiks_tatabahasa.py            -> hanya MELIHAT (tidak mengubah apa pun)
  python pasang_afiks_tatabahasa.py --apply    -> memasang (cadangan dibuat otomatis)

Aman dijalankan ulang. Cadangan: tatabahasa.html.bak_afiks_<tanggal-jam>
Cara membatalkan: salin kembali berkas cadangan itu menjadi tatabahasa.html.
"""
import io
import json
import os
import shutil
import sys
import time

HTML = 'tatabahasa.html'
DATA = os.path.join('data', 'grammar_afiks.json')
MARK = 'TB_AFX_LEVEL'

NAMES = ['A. Orang/pelaku', 'B. Sifat dan konsep abstrak', 'C. Jenis dan gaya', 'D. Bidang dan ilmu',
         'E. Tempat dan lembaga', 'F. Alat, barang, biaya', 'G. Pelengkap kata benda',
         'H. Penanda awal kata', 'I. Menolak/meniadakan', 'J. Tingkat dan keseluruhan']

HELPERS = r'''const TB_LEVELS = [1,2,3,4,5,6,7,8,9,10];
/* Level 10 = "Awalan & Akhiran" (60 poin AFX, data/grammar_afiks.json) */
const TB_AFX_LEVEL = 10;
function tbLvl(l) { return l === TB_AFX_LEVEL ? 'Awalan & Akhiran' : 'HSK ' + l; }
function tbLvlShort(l) { return l === TB_AFX_LEVEL ? 'AFX' : 'HSK' + l; }
/* poin lama di Tata Bahasa yang diperdalam oleh poin AFX */
const TB_AFX_LAMA = {
  'AFX.40': { id: 'hsk1-57', t: 'HSK 1 · poin 57 (—们 —边)' },
  'AFX.41': { id: 'hsk3-16.3', t: 'HSK 3 · poin 16.3 (—子)' },
  'AFX.45': { id: 'hsk1-56', t: 'HSK 1 · poin 56 (小— 第—)' }
};
/* buka satu poin lewat id-nya (AFX.nn atau hskN-xx), dipakai tautan #point=... dan tombol "poin lama" */
async function tbOpenPointById(id) {
  const m = /^hsk(\d+)-/.exec(id);
  const lvl = m ? parseInt(m[1], 10) : (/^AFX\./.test(id) ? TB_AFX_LEVEL : null);
  if (lvl === null) throw new Error('id poin tidak dikenal: ' + id);
  await loadLevelData(lvl);
  const data = TB_STATE.cache[lvl];
  for (let ci = 0; ci < data.categories.length; ci++) {
    if (data.categories[ci].points.some(p => p.id === id)) {
      TB_STATE.level = lvl; TB_STATE.catIndex = ci;
      goToDetailScreen(id);
      return;
    }
  }
  throw new Error('poin tidak ditemukan: ' + id);
}
/* tambahan di rincian poin AFX: tingkat HSK terendah + tombol ke Kamus (+ poin lama) */
function tbAfxExtra(point) {
  if (!point || !point.kamus_id) return '';
  let h = '';
  if (point.tingkat_hsk_terendah) {
    h += `<div class="tb-detail-fungsi"><strong>Tingkat HSK terendah:</strong> ${escHtml(point.tingkat_hsk_terendah)}</div>`;
  }
  const links = [`<a class="tb-back-btn" style="text-decoration:none" href="kamus.html#group=afiks:${encodeURIComponent(point.kamus_nama)}">📖 Lihat di Kamus: ${escHtml(point.kamus_nama)}</a>`];
  const lama = TB_AFX_LAMA[point.number];
  if (lama) links.push(`<button class="tb-back-btn" onclick="tbOpenPointById('${lama.id}')">↩ Poin lama: ${escHtml(lama.t)}</button>`);
  return h + `<div class="tb-detail-fungsi" style="display:flex;flex-wrap:wrap;gap:8px">${links.join('')}</div>`;
}'''

INIT_PT = r'''  const ptMatch = location.hash.match(/^#point=(.+)$/);
  if (ptMatch) {
    try { await tbOpenPointById(decodeURIComponent(ptMatch[1])); }
    catch (e) { console.error('Gagal membuka poin:', e); goToLevelScreen(); }
    return;
  }
'''

TOPIK_OLD = '  "准词缀 (Quasi-Affixes)": "Prefix & Suffix (Imbuhan)",'
TOPIK_NEW = TOPIK_OLD + '\n' + '\n'.join('  "%s": "Prefix & Suffix (Imbuhan)",' % n for n in NAMES)

FUNGSI_OLD = "<strong>Fungsi:</strong> ${escHtml(point.fungsi)}</div>` : ''}"

# (nama, teks lama, teks baru) -- setiap teks lama harus muncul TEPAT 1 kali
REPL = [
    ('daftar level + fungsi bantu', 'const TB_LEVELS = [1,2,3,4,5,6,7,8,9];', HELPERS),
    ('pemuat data level', "const res = await fetch(`data/grammar_hsk${level}.json`);",
     "const res = await fetch(level === TB_AFX_LEVEL ? 'data/grammar_afiks.json' : `data/grammar_hsk${level}.json`);"),
    ('remah roti', '>HSK ${TB_STATE.level}</span>', '>${tbLvl(TB_STATE.level)}</span>'),
    ('kartu level: tata letak', '<div class="tb-level-card" onclick="goToCategoryScreen(${lvl})">',
     '<div class="tb-level-card" onclick="goToCategoryScreen(${lvl})"${lvl === TB_AFX_LEVEL ? \' style="grid-column:1/-1"\' : \'\'}>'),
    ('kartu level: judul', '<div class="tb-level-num">HSK ${lvl}</div>',
     "<div class=\"tb-level-num\">${lvl === TB_AFX_LEVEL ? '🧩 Awalan & Akhiran' : 'HSK ' + lvl}</div>"),
    ('layar kategori: memuat', 'Memuat kategori HSK ${level}…', 'Memuat kategori ${tbLvl(level)}…'),
    ('layar kategori: gagal', 'Gagal memuat data HSK ${level}.<br>Pastikan <code>data/grammar_hsk${level}.json</code>',
     "Gagal memuat data ${tbLvl(level)}.<br>Pastikan <code>data/${level === TB_AFX_LEVEL ? 'grammar_afiks' : 'grammar_hsk' + level}.json</code>"),
    ('Daftar Isi: ringkasan', "${items.length} poin · HSK ${levelsSet.join(',')}",
     "${items.length} poin · ${levelsSet.map(tbLvlShort).join(', ')}"),
    ('Daftar Isi: penanda', '>HSK${it.level}</span>', '>${tbLvlShort(it.level)}</span>'),
    ('hasil pencarian: penanda', '>HSK${r.level}</span>', '>${tbLvlShort(r.level)}</span>'),
    ('topik Daftar Isi', TOPIK_OLD, TOPIK_NEW),
    ('rincian poin', FUNGSI_OLD, FUNGSI_OLD + '\n    ${tbAfxExtra(point)}'),
    ('tautan #point=', "  const hashMatch = location.hash.match(/^#search=(.+)$/);",
     INIT_PT + "  const hashMatch = location.hash.match(/^#search=(.+)$/);"),
]


def fail(msg):
    print('GAGAL: ' + msg)
    sys.exit(1)


def main():
    apply = '--apply' in sys.argv
    print('Mode: ' + ('PASANG (--apply)' if apply else 'LIHAT-DULU (tidak mengubah apa pun)'))
    for p in (HTML, DATA):
        if not os.path.isfile(p):
            fail('berkas tidak ditemukan: %s (jalankan dari folder C:\\mandarin_app)' % p)
    try:
        with io.open(DATA, encoding='utf-8') as f:
            g = json.load(f)
        pts = [p for c in g['categories'] for p in c['points']]
    except Exception as e:
        fail('%s tidak bisa dibaca: %s' % (DATA, e))
    names = [c['name'] for c in g['categories']]
    if len(pts) != 60 or names != NAMES:
        fail('%s harus berisi 60 poin dalam 10 kategori A-J (ditemukan %d poin; kategori: %s)' % (DATA, len(pts), names))
    print('OK  data/grammar_afiks.json: 60 poin, 10 kategori A-J')

    with io.open(HTML, encoding='utf-8', newline='') as f:
        text = f.read()
    if MARK in text:
        print('Sudah terpasang (penanda %s ditemukan). Tidak ada yang diubah.' % MARK)
        return
    nl = '\r\n' if '\r\n' in text else '\n'
    new = text
    for name, old, rep in REPL:
        n = new.count(old)
        if n != 1:
            fail('bagian "%s" tidak ditemukan tepat 1 kali (ditemukan %d). tatabahasa.html di sini berbeda dari yang saya periksa; tidak ada yang diubah.' % (name, n))
        if nl == '\r\n':
            rep = rep.replace('\r\n', '\n').replace('\n', '\r\n')
        new = new.replace(old, rep)
        print('  + ' + name)
    print('Ukuran: %d -> %d karakter (%+d)' % (len(text), len(new), len(new) - len(text)))

    if not apply:
        print('\nBelum ada yang diubah. Jika sudah sesuai, jalankan:  python pasang_afiks_tatabahasa.py --apply')
        return

    bak = HTML + '.bak_afiks_' + time.strftime('%Y%m%d_%H%M%S')
    shutil.copy2(HTML, bak)
    print('Cadangan dibuat: ' + bak)
    with io.open(HTML, 'w', encoding='utf-8', newline='') as f:
        f.write(new)
    with io.open(HTML, encoding='utf-8', newline='') as f:
        chk = f.read()
    if chk != new or chk.count(MARK) < 5:
        shutil.copy2(bak, HTML)
        fail('pemeriksaan akhir gagal; tatabahasa.html dikembalikan dari cadangan')
    print('SELESAI. Buka tatabahasa.html (muat ulang dengan Ctrl+F5): kartu "🧩 Awalan & Akhiran" ada di layar awal.')


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pasang_pilar12.py -- memasang Pilar 12 "Pembentukan Kata (构词法)" ke Peta Bahasa.

Dua pekerjaan:
  A. data/pelajaran/pilar_12.json  : memberi penanda tampilan pada tulisan Mandarin (Hanzi)
     dan pinyin di paragraf, daftar, dan tabel, supaya tampil sama seperti pilar lain.
     Isi teksnya TIDAK berubah (diperiksa otomatis: teks tanpa penanda sama persis).
  B. peta-bahasa.html : (1) entri Pilar 12 + 5 baris tautan, (2) baris Akar Kosakata dipindah
     dari Pilar 11 ke Pilar 12, (3) judul "Peta 12 Pilar", (4) tautan #pilar-N membuka kartu
     pilar itu dan Pelajaran Lengkap-nya, (5) kartu Pilar 12 terbuka otomatis.
Berkas lain tidak disentuh.

Cara pakai (jalankan dari folder C:\\mandarin_app):
  python pasang_pilar12.py            -> hanya MELIHAT (tidak mengubah apa pun)
  python pasang_pilar12.py --apply    -> memasang (cadangan dibuat otomatis)

Aman dijalankan ulang. Cadangan: peta-bahasa.html.bak_pilar12_<tanggal-jam> dan
data/pelajaran/pilar_12.json.bak_<tanggal-jam>. Untuk membatalkan, salin cadangannya kembali.
"""
import io
import json
import os
import re
import shutil
import sys
import time

HTML = 'peta-bahasa.html'
JSONP = os.path.join('data', 'pelajaran', 'pilar_12.json')
TS = time.strftime('%Y%m%d_%H%M%S')

TONE = 'āáǎàēéěèīíǐìōóǒòūúǔùǖǘǚǜü'
NEUTRAL = {'men', 'zi', 'tou', 'er', 'de', 'le', 'ne', 'ma', 'ba'}
HZ = r'[\u4e00-\u9fff]+'
PYW = r'[A-Za-z' + TONE + r']*[' + TONE + r'][A-Za-z' + TONE + r']*'
GENERIC = re.compile('(' + HZ + ')|(' + PYW + ')')
CELL = re.compile(r'^(\s*)(' + HZ + r')(\s*[—–-]?\s*)([A-Za-z' + TONE + r']+(?:\s*/\s*[A-Za-z' + TONE + r']+)*)(\s*)$')


def hz(s):
    return '<span class="hz">' + s + '</span>'


def py(s):
    return '<span class="py">' + s + '</span>'


def is_pinyin_seq(s):
    toks = [t for t in re.split(r'\s*/\s*|\s+', s) if t]
    if any(re.search('[' + TONE + ']', t) for t in toks):
        return all(re.fullmatch(r'[A-Za-z' + TONE + r']+', t) for t in toks)
    return all(t.lower() in NEUTRAL for t in toks)


def conv(t):
    """bungkus Hanzi dan pinyin dengan penanda gaya (idempotent)"""
    if not isinstance(t, str) or 'class="hz"' in t or 'class="py"' in t:
        return t
    m = CELL.match(t)
    if m and is_pinyin_seq(m.group(4)):
        return m.group(1) + hz(m.group(2)) + m.group(3) + py(m.group(4)) + m.group(5)
    return GENERIC.sub(lambda x: hz(x.group(1)) if x.group(1) else py(x.group(2)), t)


def strip_tags(t):
    return re.sub(r'<[^>]+>', '', t)


def convert_doc(doc):
    """kembalikan (dokumen baru, jumlah bidang diubah). Hanya bidang yang ditampilkan sebagai HTML mentah."""
    n = [0]

    def c(t):
        r = conv(t)
        if r != t:
            n[0] += 1
            assert strip_tags(r) == t, 'teks berubah: ' + t[:40]
        return r
    if doc.get('ringkasan'):
        doc['ringkasan'] = c(doc['ringkasan'])
    for b in doc.get('bagian', []):
        for x in b.get('isi', []):
            tp = x.get('tipe')
            if tp in ('paragraf', 'peringatan'):
                x['teks'] = c(x.get('teks', ''))
            elif tp == 'poin':
                x['daftar'] = [c(d) for d in x.get('daftar', [])]
            elif tp == 'tabel':
                x['baris'] = [[c(cell) for cell in row] for row in x.get('baris', [])]
    return doc, n[0]


PILAR12_ENTRY = r'''  {
    title: '12. Pembentukan Kata (构词法)',
    status: 'baru',
    desc: 'Cara kata Mandarin dibentuk: awalan & akhiran (60 entri), kata majemuk, dan akar kosakata. Pelajaran Lengkap berisi pengantar, cara membaca kartu, perbandingan akhiran pelaku, awalan penolak, dan peta 60 entri.',
    subtopics: [
      { name: 'Awalan & Akhiran — 60 entri di Kamus (kelompok A–J)', status: 'baru', link: 'kamus.html#opengroup=afiks', label: 'Buka di Kamus →' },
      { name: 'Poin Tata Bahasa AFX.01–AFX.60 (60 poin)', status: 'baru', link: 'tatabahasa.html#point=AFX.01', label: 'Buka Tata Bahasa →' },
      { name: 'Akar Kosakata (karakter dasar → kata turunan)', status: 'kuat', link: 'kamus.html#opengroup=akar', label: 'Buka di Kamus →' },
      { name: 'Pola Pembentukan Kata Majemuk — 8.867 kata, tampil di rincian kata dua karakter (contoh: 学习)', status: 'kuat', link: 'kamus.html#search=学习', label: 'Lihat contoh di Kamus →' },
      { name: 'Reduplikasi (AA, AABB, ABAB) — dibahas di Pilar 9', status: 'kuat', link: '#pilar-9', label: 'Ke Pilar 9 →' },
    ],
  },
'''

HANDLER = r'''if (firstNew) firstNew.classList.add('open');

/* Tautan langsung: peta-bahasa.html#pilar-N membuka kartu pilar N beserta Pelajaran Lengkap-nya */
function bukaPilarDariHash() {
  const m = location.hash.match(/^#pilar-(\d+)$/);
  if (!m) return;
  const card = document.getElementById('pilar-' + m[1]);
  if (!card) return;
  card.classList.add('open');
  const box = card.querySelector('.pelajaran-box');
  const toggle = card.querySelector('.pelajaran-toggle');
  if (toggle && box && !box.classList.contains('open')) toggle.click();
  card.scrollIntoView({ block: 'start' });
}
bukaPilarDariHash();
window.addEventListener('hashchange', bukaPilarDariHash);'''

AKAR_ROW = "\n      { name: 'Akar Kosakata (karakter dasar → kata turunan)', status: 'kuat', link: 'kamus.html#opengroup=akar', label: 'Buka di Kamus →' },"

# (nama, lama, baru) -- setiap teks lama harus muncul TEPAT 1 kali
REPL = [
    ('judul halaman', '<title>Peta 11 Pilar — Mandarin Interaktif</title>', '<title>Peta 12 Pilar — Mandarin Interaktif</title>'),
    ('judul utama', '<h1>🗺️ Peta 11 Pilar Bahasa Mandarin</h1>', '<h1>🗺️ Peta 12 Pilar Bahasa Mandarin</h1>'),
    ('Akar Kosakata keluar dari Pilar 11', AKAR_ROW, ''),
    ('entri Pilar 12', '  },\n];\n\nfunction el(', '  },\n' + PILAR12_ENTRY + '];\n\nfunction el('),
    ('id kartu pilar', "    const card = el('div', 'pillar-card');", "    const card = el('div', 'pillar-card');\n    card.id = 'pilar-' + (idx + 1);"),
    ('kartu terbuka otomatis', "const firstNew = document.querySelectorAll('.pillar-card')[9]; // Pilar 10 (index 9)",
     "const firstNew = document.querySelectorAll('.pillar-card')[11]; // Pilar 12 (index 11) — yang terbaru"),
    ('tautan #pilar-N', "if (firstNew) firstNew.classList.add('open');", HANDLER),
]


def fail(msg):
    print('GAGAL: ' + msg)
    sys.exit(1)


def main():
    apply = '--apply' in sys.argv
    print('Mode: ' + ('PASANG (--apply)' if apply else 'LIHAT-DULU (tidak mengubah apa pun)'))
    for p in (HTML, JSONP):
        if not os.path.isfile(p):
            fail('berkas tidak ditemukan: %s (jalankan dari folder C:\\mandarin_app)' % p)

    # ── A. pilar_12.json ──
    with io.open(JSONP, encoding='utf-8') as f:
        raw = f.read()
    try:
        doc = json.loads(raw)
    except ValueError as e:
        fail('%s bukan JSON yang valid: %s' % (JSONP, e))
    if doc.get('pilar') != 12 or len(doc.get('bagian', [])) != 6:
        fail('%s harus berisi Pilar 12 dengan 6 bagian (ditemukan: pilar=%s, bagian=%d)' % (JSONP, doc.get('pilar'), len(doc.get('bagian', []))))
    for bad in ('perlu dicek', '⚠️', 'Kamus Pembentukan Kata', 'Ruslan', '[citation'):
        if bad in raw:
            fail('%s masih versi lama (mengandung "%s"). Ambil versi "perbaikan akhir" dari repo.' % (JSONP, bad))
    if 'Awalan & Akhiran' not in raw:
        fail('%s tampaknya bukan versi perbaikan akhir (tidak ada "Awalan & Akhiran").' % JSONP)
    print('OK  data/pelajaran/pilar_12.json: Pilar 12, 6 bagian, versi perbaikan akhir')
    newdoc, nchg = convert_doc(doc)
    if nchg == 0:
        print('--  penanda tampilan: sudah ada, dilewati')
        new_json = None
    else:
        new_json = json.dumps(newdoc, ensure_ascii=False, indent=2) + '\n'
        print('  + penanda tampilan Hanzi/pinyin: %d bidang teks diberi penanda (%d span hz, %d span py); teks diperiksa tidak berubah'
              % (nchg, new_json.count('class=\\"hz\\"'), new_json.count('class=\\"py\\"')))

    # ── B. peta-bahasa.html ──
    with io.open(HTML, encoding='utf-8', newline='') as f:
        text = f.read()
    new = text
    if "title: '12. Pembentukan Kata" in new:
        print('--  peta-bahasa.html: Pilar 12 sudah terpasang, dilewati')
        new = None
    else:
        nl = '\r\n' if '\r\n' in new else '\n'
        for name, old, rep in REPL:
            if nl == '\r\n':
                old = old.replace('\r\n', '\n').replace('\n', '\r\n')
                rep = rep.replace('\r\n', '\n').replace('\n', '\r\n')
            n = new.count(old)
            if n != 1:
                fail('bagian "%s" tidak ditemukan tepat 1 kali (ditemukan %d). peta-bahasa.html di sini berbeda dari yang saya periksa; tidak ada yang diubah.' % (name, n))
            new = new.replace(old, rep)
            print('  + ' + name)
        print('Ukuran peta-bahasa.html: %d -> %d karakter (%+d)' % (len(text), len(new), len(new) - len(text)))

    if new is None and new_json is None:
        print('Tidak ada yang perlu diubah: semuanya sudah terpasang.')
        return
    if not apply:
        print('\nBelum ada yang diubah. Jika sudah sesuai, jalankan:  python pasang_pilar12.py --apply')
        return

    if new_json is not None:
        bak = JSONP + '.bak_' + TS
        shutil.copy2(JSONP, bak)
        print('Cadangan dibuat: ' + bak)
        with io.open(JSONP, 'w', encoding='utf-8', newline='') as f:
            f.write(new_json)
        with io.open(JSONP, encoding='utf-8') as f:
            chk = json.load(f)
        if chk.get('pilar') != 12 or len(chk['bagian']) != 6:
            shutil.copy2(bak, JSONP)
            fail('pemeriksaan akhir pilar_12.json gagal; dikembalikan dari cadangan')
    if new is not None:
        bak = HTML + '.bak_pilar12_' + TS
        shutil.copy2(HTML, bak)
        print('Cadangan dibuat: ' + bak)
        with io.open(HTML, 'w', encoding='utf-8', newline='') as f:
            f.write(new)
        with io.open(HTML, encoding='utf-8', newline='') as f:
            chk = f.read()
        if chk != new or "title: '12. Pembentukan Kata" not in chk:
            shutil.copy2(bak, HTML)
            fail('pemeriksaan akhir peta-bahasa.html gagal; dikembalikan dari cadangan')
    print('SELESAI. Buka peta-bahasa.html (muat ulang dengan Ctrl+F5): kartu "12. Pembentukan Kata" terbuka otomatis.')


if __name__ == '__main__':
    main()

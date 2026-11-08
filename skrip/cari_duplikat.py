"""
cari_duplikat.py
=================
Scan seluruh drive C:\ untuk menemukan SEMUA salinan file:
  - index_theme.json
  - flashcard.html
  - kamus.html

Untuk tiap index_theme.json yang ditemukan, skrip ini juga membaca isinya
dan menampilkan nilai "count" untuk key "ext_currency" -- supaya bisa
langsung dibandingkan mana yang datanya baru (25) dan mana yang lama (3),
tanpa perlu buka satu-satu secara manual.

CARA PAKAI:
  1. Buka Command Prompt biasa (tidak perlu run as admin).
  2. cd ke folder mana saja (boleh taruh skrip ini di C:\ langsung, atau di
     C:\mandarin_app -- tidak masalah, dia scan seluruh C:\ apa pun posisinya).
  3. Jalankan:  python cari_duplikat.py
  4. Tunggu -- proses scan seluruh drive C:\ bisa makan waktu beberapa menit
     tergantung ukuran & kecepatan disk. Ada tanda titik (....) berjalan
     supaya tahu skrip tidak macet.
  5. Salin SELURUH hasil output yang tercetak, tempel balik ke Claude.
"""

import os
import sys
import json
import time
from datetime import datetime

# Folder-folder besar bawaan Windows yang HAMPIR PASTI tidak relevan --
# di-skip supaya scan jauh lebih cepat dan tidak nyangkut di file sistem.
SKIP_DIRS = {
    'windows', 'program files', 'program files (x86)', 'programdata',
    '$recycle.bin', 'system volume information', 'appdata',
    'node_modules', '.git', 'msocache', 'perflogs',
}

TARGET_NAMES = {'index_theme.json', 'flashcard.html', 'kamus.html'}

ROOT = 'C:\\'

def should_skip_dir(dirname):
    return dirname.lower() in SKIP_DIRS

def human_size(n):
    for unit in ['B', 'KB', 'MB', 'GB']:
        if n < 1024:
            return f"{n:.1f}{unit}"
        n /= 1024
    return f"{n:.1f}TB"

def get_ext_currency_count(filepath):
    """Coba baca index_theme.json dan ambil count utk key ext_currency.
    Kalau gagal parse / key tidak ada, kembalikan None + alasan."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        entry = data.get('ext_currency')
        if entry is None:
            return None, 'key ext_currency tidak ada di file ini'
        return entry.get('count'), None
    except Exception as e:
        return None, f'gagal baca: {e}'

def main():
    print(f"Mulai scan {ROOT} pada {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("Ini bisa makan waktu beberapa menit -- mohon tunggu...\n")

    found = {name: [] for name in TARGET_NAMES}
    scanned_dirs = 0
    last_tick = time.time()

    for dirpath, dirnames, filenames in os.walk(ROOT, topdown=True):
        # Filter subfolder yang mau di-skip, MODIFY IN PLACE (cara resmi os.walk)
        dirnames[:] = [d for d in dirnames if not should_skip_dir(d)]

        scanned_dirs += 1
        if time.time() - last_tick > 2:
            print(".", end="", flush=True)
            last_tick = time.time()

        for fname in filenames:
            if fname.lower() in TARGET_NAMES:
                full = os.path.join(dirpath, fname)
                try:
                    stat = os.stat(full)
                    found[fname.lower()].append({
                        'path': full,
                        'mtime': stat.st_mtime,
                        'size': stat.st_size,
                    })
                except Exception:
                    pass

    print(f"\n\nScan selesai. Total folder diperiksa: {scanned_dirs}\n")
    print("=" * 78)

    for name in ['index_theme.json', 'flashcard.html', 'kamus.html']:
        entries = found[name]
        print(f"\n### {name} -- ditemukan {len(entries)} salinan ###")
        if not entries:
            print("  (tidak ditemukan di mana pun)")
            continue
        # Urutkan dari yang paling BARU diubah ke paling lama
        entries.sort(key=lambda e: e['mtime'], reverse=True)
        for e in entries:
            mtime_str = datetime.fromtimestamp(e['mtime']).strftime('%Y-%m-%d %H:%M:%S')
            line = f"  [{mtime_str}]  {human_size(e['size']):>8}  {e['path']}"
            if name == 'index_theme.json':
                count, err = get_ext_currency_count(e['path'])
                if err:
                    line += f"   -- ext_currency: {err}"
                else:
                    line += f"   -- ext_currency count = {count}"
            print(line)

    print("\n" + "=" * 78)
    print("SELESAI. Salin semua teks di atas (dari 'Mulai scan' sampai baris ini)")
    print("lalu tempel balik ke Claude.")

if __name__ == '__main__':
    if not sys.platform.startswith('win'):
        print("Skrip ini dibuat khusus untuk Windows (path C:\\). Jalankan di PC Windows رسلان.")
        sys.exit(1)
    main()

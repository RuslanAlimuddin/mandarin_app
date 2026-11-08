"""
cari_residu_sinonim_di_proyek.py — READ-ONLY, tidak mengubah apapun.

Scan SELURUH folder C:\\mandarin_app (semua subfolder, semua tipe file --
bukan cuma .html/.js/.json) untuk nama file yang menyebut sinonim/antonim/
synonym/antonym -- termasuk script Python lama, file JSON perantara, hasil
generate AI yang mungkin belum sempat di-apply, dsb. Ini beda dari
intip_pemakaian_synonym_field.py (yg cuma cari PEMAKAIAN KODE) -- ini
cari SEMUA FILE yg namanya nyerempet topik ini, apapun jenisnya.

Cara pakai:
    cd C:\\mandarin_app
    python cari_residu_sinonim_di_proyek.py
"""

import os
from datetime import datetime

ROOT = os.getcwd()
SKIP_DIRS = {".git", "node_modules", "__pycache__"}
KEYWORDS = ["sinonim", "antonim", "synonym", "antonym"]


def main():
    hits = []
    for dirpath, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for fname in filenames:
            fname_low = fname.lower()
            if any(kw in fname_low for kw in KEYWORDS):
                fpath = os.path.join(dirpath, fname)
                try:
                    size = os.path.getsize(fpath)
                    mtime = datetime.fromtimestamp(os.path.getmtime(fpath)).strftime("%Y-%m-%d %H:%M")
                except OSError:
                    size, mtime = -1, "?"
                rel = os.path.relpath(fpath, ROOT)
                hits.append((rel, size, mtime))

    hits.sort(key=lambda x: x[2])  # urut by tanggal modifikasi

    print(f"Total file yg namanya menyebut sinonim/antonim/synonym/antonym: {len(hits)}\n")
    print(f"{'Tanggal Modifikasi':<18} {'Ukuran':>10}  Path")
    print("-" * 80)
    for rel, size, mtime in hits:
        size_str = f"{size:,} B" if size >= 0 else "?"
        print(f"{mtime:<18} {size_str:>10}  {rel}")

    print("\n" + "=" * 70)
    print("Kalau ada file .json di antara ini SELAIN app_words.json/")
    print("synonym_antonym.json yang sudah kita tau -- itu kandidat kuat")
    print("hasil kerja lama yang mungkin belum ter-apply penuh. Tempel isi")
    print("file itu (atau upload) kalau ukurannya kecil/menengah.")


if __name__ == "__main__":
    main()

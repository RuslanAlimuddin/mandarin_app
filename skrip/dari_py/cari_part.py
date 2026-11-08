# -*- coding: utf-8 -*-
"""
cari_part.py
============
Script ini men-scan semua file PART (.txt / .html) di dalam sebuah folder
(termasuk subfolder-nya), lalu mencari baris-baris yang berkaitan dengan
migrasi Tier 0 (unifikasi $ / $$ / $w dan showToast).

CARA PAKAI:
1. Simpan file ini di mana saja, misalnya C:\mandarin_app\cari_part.py
2. Buka Command Prompt (cmd), lalu jalankan:
       python cari_part.py
3. Saat diminta, ketik path folder yang mau di-scan, misalnya:
       C:\mandarin_app
   (kalau folder kamus/flashcard/word ada di dalam C:\mandarin_app,
    tinggal masukkan path induknya saja - C:\mandarin_app - karena
    script ini scan semua subfolder juga)
4. Baca laporan yang muncul di layar. Laporan yang sama juga otomatis
   disimpan ke file "laporan_cari_part.txt" di folder yang sama dengan
   script ini, supaya bisa di-copy-paste atau dikirim balik ke Claude.
"""

import os

# Kata kunci yang dicari, dikelompokkan biar laporan lebih rapi.
KEYWORD_GROUPS = {
    "Definisi selector ($ / $$ / $w)": [
        "const $ =",
        "const $$ =",
        "const $w =",
        "function $(",
        "function $$(",
        "function $w(",
    ],
    "Pemakaian selector $$(...)": [
        "$$(",
    ],
    "Pemakaian selector $w(...)": [
        "$w(",
    ],
    "showToast": [
        "function showToast",
        "showToast(",
    ],
    "escHtml": [
        "function escHtml",
        "escHtml(",
    ],
    "[Tier1] Markup kamus - panel detail hanzi": [
        'id="d-hanzi"',
        'id="detail-content"',
        'id="detail-actions"',
        'id="d-pinyin"',
    ],
    "[Tier1] Markup flashcard - kartu depan/belakang": [
        'id="fc-front-hanzi"',
        'id="fc-back-hanzi"',
        'id="fc-card-inner"',
        'id="fc-card-wrap"',
    ],
    "[Tier1] Markup wordbuilder - hasil output": [
        'id="wb-out-chinese"',
        'id="wb-output-result"',
        'id="wb-copy-btn"',
    ],
}

VALID_EXTENSIONS = (".txt", ".html", ".htm")


def scan_file(filepath):
    """Kembalikan dict: {grup: [(nomor_baris, isi_baris), ...]}"""
    hasil = {grup: [] for grup in KEYWORD_GROUPS}
    try:
        with open(filepath, "r", encoding="utf-8", errors="replace") as f:
            for lineno, line in enumerate(f, start=1):
                for grup, keywords in KEYWORD_GROUPS.items():
                    for kw in keywords:
                        if kw in line:
                            hasil[grup].append((lineno, line.strip()))
                            break  # cukup 1 match per grup per baris
    except Exception as e:
        print(f"  [GAGAL BACA] {filepath}: {e}")
    return hasil


def main():
    print("=" * 60)
    print("  CARI PART - Tier 0 (selector & showToast)")
    print("=" * 60)
    folder = input(
        "\nMasukkan path folder yang mau di-scan\n"
        "(kosongkan lalu Enter untuk pakai default C:\\mandarin_app): "
    ).strip()
    if not folder:
        folder = r"C:\mandarin_app"

    if not os.path.isdir(folder):
        print(f"\n[ERROR] Folder tidak ditemukan: {folder}")
        input("\nTekan Enter untuk keluar...")
        return

    laporan_lines = []
    laporan_lines.append(f"Folder yang di-scan: {folder}\n")

    file_list = []
    for root, dirs, files in os.walk(folder):
        for fname in files:
            if fname.lower().endswith(VALID_EXTENSIONS):
                file_list.append(os.path.join(root, fname))

    file_list.sort()

    if not file_list:
        print(f"\nTidak ada file .txt/.html ditemukan di {folder}")
        input("\nTekan Enter untuk keluar...")
        return

    print(f"\nDitemukan {len(file_list)} file. Memindai...\n")

    # Ringkasan: PART mana saja yang punya minimal 1 match
    part_relevan = set()

    for filepath in file_list:
        hasil = scan_file(filepath)
        ada_match = any(len(v) > 0 for v in hasil.values())
        if not ada_match:
            continue

        part_relevan.add(filepath)
        rel = os.path.relpath(filepath, folder)
        header = f"\n--- {rel} ---"
        print(header)
        laporan_lines.append(header)

        for grup, matches in hasil.items():
            if not matches:
                continue
            sub = f"  [{grup}] {len(matches)} baris ditemukan:"
            print(sub)
            laporan_lines.append(sub)
            for lineno, isi in matches[:15]:  # batasi tampilan max 15/grup
                line_out = f"    baris {lineno}: {isi[:120]}"
                print(line_out)
                laporan_lines.append(line_out)
            if len(matches) > 15:
                more = f"    ...dan {len(matches) - 15} baris lainnya"
                print(more)
                laporan_lines.append(more)

    print("\n" + "=" * 60)
    print("RINGKASAN - PART yang perlu di-upload ke Claude:")
    print("=" * 60)
    laporan_lines.append("\n" + "=" * 60)
    laporan_lines.append("RINGKASAN - PART yang perlu di-upload ke Claude:")
    laporan_lines.append("=" * 60)

    if part_relevan:
        for fp in sorted(part_relevan):
            rel = os.path.relpath(fp, folder)
            print(f"  - {rel}")
            laporan_lines.append(f"  - {rel}")
    else:
        msg = "  (tidak ada PART yang cocok dengan kata kunci di atas)"
        print(msg)
        laporan_lines.append(msg)

    # Simpan laporan ke file
    laporan_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "laporan_cari_part.txt")
    try:
        with open(laporan_path, "w", encoding="utf-8") as f:
            f.write("\n".join(laporan_lines))
        print(f"\nLaporan lengkap disimpan di: {laporan_path}")
    except Exception as e:
        print(f"\n[WARNING] Gagal menyimpan laporan ke file: {e}")

    input("\nSelesai. Tekan Enter untuk keluar...")


if __name__ == "__main__":
    main()

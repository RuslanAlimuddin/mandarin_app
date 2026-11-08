# -*- coding: utf-8 -*-
"""
Ekstrak halaman "HSK 语法大纲" (silabus tata bahasa resmi HSK1-6) dari PDF
resmi yang sudah رسلان unduh, tanpa perlu proses seluruh 400 halaman.

Cara pakai:
    1. Unduh PDF resminya dari:
       https://hsk.cn-bj.ufileos.com/3.0/%E6%96%B0%E7%89%88HSK%E8%80%83%E8%AF%95%E5%A4%A7%E7%BA%B21219.pdf
       (buka link itu di browser, klik "save as" / unduh, simpan sebagai hsk_dagang.pdf)
    2. pip install pdfplumber --break-system-packages   (kalau belum ada)
    3. python extract_grammar_pages.py hsk_dagang.pdf

Hasil: hsk_grammar_1_6.txt (teks halaman 382-400 apa adanya) di folder yang
sama. Upload file itu ke chat Claude.

Catatan: nomor halaman 382 itu sesuai daftar isi yang tercetak DI DALAM PDF,
bukan selalu sama dengan nomor halaman PDF viewer (kadang ada selisih
beberapa halaman karena cover/halaman kosong di awal). Skrip ini otomatis
mencari teks "HSK 语法大纲" dan "HSK（一级）" persis di section itu untuk
memastikan potongannya benar, alih-alih pakai nomor halaman mentah.
"""
import sys
import re

try:
    import pdfplumber
except ImportError:
    print("Perlu install dulu: pip install pdfplumber --break-system-packages")
    sys.exit(1)


def main():
    if len(sys.argv) != 2:
        print("Pemakaian: python extract_grammar_pages.py <file.pdf>")
        sys.exit(1)
    path = sys.argv[1]

    print("Membuka PDF (mungkin agak lama untuk file besar)...")
    with pdfplumber.open(path) as pdf:
        total = len(pdf.pages)
        print(f"Total halaman PDF: {total}")

        # cari halaman yang mengandung header "HSK 语法大纲" DI BADAN TEKS
        # (bukan di daftar isi -- daftar isi biasanya di 5 halaman pertama,
        # jadi kita mulai cari dari halaman ke-10 dan seterusnya)
        start_idx = None
        for i in range(10, total):
            text = pdf.pages[i].extract_text() or ""
            if "HSK 语法大纲" in text or "HSK（一级）" in text and i > total * 0.7:
                start_idx = i
                break

        if start_idx is None:
            print("[PERINGATAN] Tidak ketemu otomatis section 语法大纲.")
            print("Silakan cek manual nomor halamannya di PDF reader, lalu")
            print("edit skrip ini (ganti start_idx/end_idx) dan jalankan lagi.")
            return

        # ambil dari situ sampai akhir dokumen (section grammar biasanya
        # bagian TERAKHIR sebelum lampiran, jadi ambil sampai habis saja,
        # lebih aman daripada menebak halaman akhir)
        end_idx = total

        print(f"Ditemukan section 语法大纲 mulai halaman PDF ke-{start_idx + 1}")
        print(f"Mengekstrak halaman {start_idx + 1} sampai {end_idx}...")

        out_lines = []
        for i in range(start_idx, end_idx):
            text = pdf.pages[i].extract_text() or ""
            out_lines.append(f"\n===== HALAMAN PDF {i + 1} =====\n")
            out_lines.append(text)

    out_path = "hsk_grammar_1_6.txt"
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(out_lines))

    print(f"Selesai. Disimpan: {out_path}")
    print("Upload file itu ke chat Claude.")


if __name__ == "__main__":
    main()

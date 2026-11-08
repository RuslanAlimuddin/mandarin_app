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
       (opsional, kalau hasil defaultnya meleset: python extract_grammar_pages.py hsk_dagang.pdf 380)
       -- angka kedua = nomor halaman PDF (1-indexed) tempat mulai section 语法大纲

Hasil: hsk_grammar_1_6.txt (teks halaman itu sampai akhir dokumen) di folder
yang sama. Upload file itu ke chat Claude.

Catatan: PDF resmi ini punya watermark "汉考国际" yang teksnya kadang
"menyisip" di tengah kata saat diekstrak, jadi pencarian teks otomatis untuk
section tidak selalu bisa diandalkan -- makanya skrip ini pakai nomor
halaman langsung (dihitung dari selisih offset cover/halaman kosong di
awal dokumen terhadap nomor halaman yang TERCETAK di PDF).
"""
import sys

try:
    import pdfplumber
except ImportError:
    print("Perlu install dulu: pip install pdfplumber --break-system-packages")
    sys.exit(1)


def main():
    if len(sys.argv) not in (2, 3):
        print("Pemakaian: python extract_grammar_pages.py <file.pdf> [nomor_halaman_mulai]")
        sys.exit(1)
    path = sys.argv[1]
    # default: 385 (hasil hitungan offset dari section 汉字大纲 yang ketemu
    # di halaman PDF 356 = halaman cetak 353, jadi offset +3; 语法大纲 di
    # halaman cetak 382 -> perkiraan halaman PDF 385)
    start_page_1indexed = int(sys.argv[2]) if len(sys.argv) == 3 else 385

    print("Membuka PDF (mungkin agak lama untuk file besar)...")
    with pdfplumber.open(path) as pdf:
        total = len(pdf.pages)
        print(f"Total halaman PDF: {total}")

        start_idx = start_page_1indexed - 1
        if start_idx < 0 or start_idx >= total:
            print(f"[ERROR] Nomor halaman {start_page_1indexed} di luar jangkauan (1-{total}).")
            sys.exit(1)

        end_idx = total
        print(f"Mengekstrak halaman PDF {start_page_1indexed} sampai {end_idx}...")

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

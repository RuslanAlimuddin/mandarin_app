"""
peek_random.py — Mengintip ACAK (bukan cuma item pertama)
============================================================
Supaya gambarannya representatif (bukan kebetulan dapat entri aneh
di urutan pertama karena data terurut A-Z / numerik dulu), script ini
mengambil sampel ACAK dari:
  - themes.json            (5 kata acak dari 3 tema acak)
  - master_final_hsk.json  (10 entri acak dari seluruh file)
  - hsk_new_words_v2.json  (10 entri acak dari hasil ekstraksi kemarin)
  - themes_extracted_v2.json (5 kata acak dari 2 tema acak)

Semua hasil ditulis ke peek_random_report.txt -- tidak mengubah file
apa pun.
============================================================
"""

import json
import os
import random

THEMES_PATH        = r"C:\mandarin_kamus\output\themes.json"
MASTER_HSK_PATH     = r"C:\hanyu_extract\output_final\master_final_hsk.json"
HSK_NEW_WORDS_PATH  = r"hsk_new_words_v2.json"
THEMES_EXTRACTED_PATH = r"themes_extracted_v2.json"

OUT_DIR = os.path.dirname(os.path.abspath(__file__))
random.seed()  # acak beneran tiap dijalankan


def section(report, title):
    report.write("\n" + "=" * 60 + "\n")
    report.write(title + "\n")
    report.write("=" * 60 + "\n")


def peek_themes_random(report):
    section(report, "THEMES.JSON -- sampel acak")
    if not os.path.isfile(THEMES_PATH):
        report.write("tidak ditemukan\n"); return
    with open(THEMES_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    temas = random.sample(list(data.keys()), min(3, len(data)))
    for tema in temas:
        val = data[tema]
        words = val.get("words", []) if isinstance(val, dict) else []
        report.write(f"\n--- tema: {tema} (word_count={val.get('word_count')}, jumlah words aktual={len(words)}) ---\n")
        sample = random.sample(words, min(5, len(words))) if words else []
        for w in sample:
            report.write(json.dumps(w, ensure_ascii=False) + "\n")


def peek_master_hsk_random(report):
    section(report, "MASTER_FINAL_HSK.JSON -- 10 entri acak dari 124.966")
    if not os.path.isfile(MASTER_HSK_PATH):
        report.write("tidak ditemukan\n"); return
    with open(MASTER_HSK_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    for entry in random.sample(data, min(10, len(data))):
        report.write(json.dumps(entry, ensure_ascii=False) + "\n\n")

    # Statistik cepat: berapa % yang hsk_level terisi vs null
    total = len(data)
    filled = sum(1 for e in data if e.get("hsk_level") not in (None, "", "null"))
    report.write(f"\nStatistik: {filled}/{total} entri ({filled/total*100:.1f}%) punya hsk_level terisi.\n")


def peek_extracted_random(report):
    section(report, "hsk_new_words_v2.json -- 10 entri acak dari hasil ekstraksi kemarin")
    if os.path.isfile(HSK_NEW_WORDS_PATH):
        with open(HSK_NEW_WORDS_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        for entry in random.sample(data, min(10, len(data))):
            report.write(json.dumps(entry, ensure_ascii=False) + "\n")
    else:
        report.write("tidak ditemukan (jalankan extract_v2.py dulu)\n")

    section(report, "themes_extracted_v2.json -- sampel acak dari hasil ekstraksi kemarin")
    if os.path.isfile(THEMES_EXTRACTED_PATH):
        with open(THEMES_EXTRACTED_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        temas = random.sample(list(data.keys()), min(2, len(data)))
        for tema in temas:
            val = data[tema]
            words = val.get("words", []) if isinstance(val, dict) else []
            report.write(f"\n--- tema: {tema} ---\n")
            for w in random.sample(words, min(5, len(words))) if words else []:
                report.write(json.dumps(w, ensure_ascii=False) + "\n")
    else:
        report.write("tidak ditemukan (jalankan extract_v2.py dulu)\n")


def main():
    report_path = os.path.join(OUT_DIR, "peek_random_report.txt")
    with open(report_path, "w", encoding="utf-8") as report:
        peek_themes_random(report)
        peek_master_hsk_random(report)
        peek_extracted_random(report)
    print(f"✓ Selesai. Upload file ini ke Claude: {report_path}")


if __name__ == "__main__":
    main()

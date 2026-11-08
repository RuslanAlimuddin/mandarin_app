# -*- coding: utf-8 -*-
"""
konversi_tabel_akar.py

Mengonversi produktif_karakter.json (hasil analisis_produktivitas.py) dari
format bersarang (nested) menjadi tabel Excel datar (flat) yang mudah dibaca
dan langsung siap di-print.

Kolom output:
    Akar Kosakata | Pinyin Akar | Arti Akar | Kata Turunan | Pinyin Turunan |
    Arti Turunan | HSK Turunan | 💡 Bantu Ingat | 📜 Asal-Usul | Radikal

Catatan:
- Kolom "Radikal" diambil dari app_words.json (field "radical" pada entri
  kata turunan tsb).
- Kolom "💡 Bantu Ingat" TIDAK berasal dari file terpisah -- setelah menelusuri
  kamus-detail.js, ternyata fitur ini di aplikasi dihasilkan SECARA ALGORITMIK:
  tiap karakter dalam kata didekomposisi, maknanya di-lookup (prioritas:
  char_etymology_id.json > app_words.json), lalu dirangkai jadi rantai
  "char (makna) + char (makna) -> arti kata". Skrip ini mereplikasi persis
  logika tryRenderMnemonic()/renderMnemonicBox() tsb di Python.
  - Tanpa --etimologi: pakai makna karakter tunggal dari app_words.json saja
    (mirip fallback sumber ke-2 di app).
  - Dengan --etimologi data/char_etymology_id.json: kualitas lebih baik,
    persis prioritas sumber ke-1 di app (gloss_id per karakter).
  Kata yang berhasil dirangkai minimal 2 karakter (sama seperti syarat di
  app: resolved.length >= 2), sisanya dikosongkan.
- Kolom "📜 Asal-Usul" HANYA terisi kalau --etimologi diberikan (field
  asal_usul_id di char_etymology_id.json, sama seperti catatan 📜 di kartu
  mnemonic pada detail panel Kamus). Format: "字 asal-usulnya; 字 asal-usulnya"
  untuk tiap karakter dalam kata yang punya catatan.

Cara pakai:
    python konversi_tabel_akar.py produktif_karakter.json app_words.json output.xlsx
    python konversi_tabel_akar.py produktif_karakter.json app_words.json output.xlsx --etimologi char_etymology_id.json
    python konversi_tabel_akar.py produktif_karakter.json app_words.json output.xlsx --min-turunan 5
    python konversi_tabel_akar.py produktif_karakter.json app_words.json output.xlsx --csv
"""

import argparse
import csv
import json
import sys

from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
from openpyxl.utils import get_column_letter


HEADERS = [
    "Akar Kosakata",
    "Pinyin Akar",
    "Arti Akar",
    "Kata Turunan",
    "Pinyin Turunan",
    "Arti Turunan",
    "HSK Turunan",
    "💡 Bantu Ingat",
    "📜 Asal-Usul",
    "Radikal",
]


def load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def build_radical_lookup(app_words):
    """kata (simplified) -> radical"""
    lookup = {}
    for w in app_words:
        simp = w.get("simplified")
        if simp and simp not in lookup:
            lookup[simp] = w.get("radical", "")
    return lookup


def build_char_meaning_index(app_words):
    """
    Replikasi buildCharMeaningIndex() di kamus-data.js:
    karakter tunggal -> meanings_id[0] (makna pertama = paling umum/singkat).
    """
    idx = {}
    for w in app_words:
        simp = w.get("simplified") or w.get("id") or ""
        meanings = w.get("meanings_id")
        if len(simp) == 1 and meanings:
            if simp not in idx:
                idx[simp] = meanings[0]
    return idx


def load_char_etymology(path):
    """
    Replikasi loadCharEtymology() -- opsional, sumber prioritas tertinggi.
    Struktur file: { "char": {"gloss_id": "...", "asal_usul_id": "..."}, ... }
    """
    if not path:
        return {}
    try:
        return load_json(path)
    except FileNotFoundError:
        print(f"[Peringatan] File etimologi '{path}' tidak ditemukan, pakai app_words.json saja untuk Bantu Ingat.")
        return {}


def get_char_meaning(char, char_etymology, char_meaning_index):
    """Replikasi getCharMeaning() -- prioritas: etimologi > app_words.json."""
    etym = char_etymology.get(char)
    if etym and etym.get("gloss_id"):
        return etym["gloss_id"]
    return char_meaning_index.get(char)


def build_mnemonic(kata, arti_kata, char_etymology, char_meaning_index):
    """
    Replikasi tryRenderMnemonic() + renderMnemonicBox(): dekomposisi kata
    jadi karakter, resolve makna tiap karakter, rangkai jadi rantai.
    Minimal 2 karakter berhasil di-resolve (sama seperti syarat di app),
    kalau tidak, dikembalikan string kosong.
    """
    resolved = []
    for ch in kata:
        m = get_char_meaning(ch, char_etymology, char_meaning_index)
        if m:
            resolved.append((ch, m))

    if len(resolved) < 2:
        return ""

    chain = " + ".join(f"{c} ({m})" for c, m in resolved)
    return f"{chain} → {arti_kata}"


def build_etymology_notes(kata, char_etymology):
    """
    Kolom '📜 Asal-Usul': rangkai catatan asal_usul_id tiap karakter dalam
    kata (kalau ada di char_etymology_id.json). Beda dari build_mnemonic()
    yang merangkai MAKNA -- ini merangkai CERITA/ASAL-USUL karakternya,
    persis catatan 📜 di kartu mnemonic pada detail panel Kamus.
    """
    if not char_etymology:
        return ""
    notes = []
    for ch in kata:
        etym = char_etymology.get(ch)
        if etym and etym.get("asal_usul_id"):
            notes.append(f"{ch} {etym['asal_usul_id']}")
    return "; ".join(notes)


def flatten_rows(akar_data, radical_lookup, char_etymology, char_meaning_index, min_turunan=1):
    """
    Menghasilkan list of tuples sesuai HEADERS, plus info grup untuk merge
    cell (jumlah baris tiap akar), diurutkan dari akar paling produktif.
    """
    rows = []
    group_sizes = []  # jumlah baris (kata turunan) per akar, urut sesuai rows

    items = sorted(akar_data.items(), key=lambda kv: kv[1].get("jumlah_turunan", 0), reverse=True)

    for akar, d in items:
        turunan_list = d.get("kata_turunan", [])
        if len(turunan_list) < min_turunan:
            continue

        group_sizes.append(len(turunan_list))
        for i, t in enumerate(turunan_list):
            kata = t.get("kata", "")
            arti_turunan = t.get("arti", "")
            radikal = radical_lookup.get(kata, "")
            bantu_ingat = build_mnemonic(kata, arti_turunan, char_etymology, char_meaning_index)
            asal_usul = build_etymology_notes(kata, char_etymology)

            rows.append((
                akar if i == 0 else "",           # akan di-merge, hanya perlu isi baris pertama
                d.get("pinyin", "") if i == 0 else "",
                d.get("arti", "") if i == 0 else "",
                kata,
                t.get("pinyin", ""),
                arti_turunan,
                t.get("hsk", ""),
                bantu_ingat,
                asal_usul,
                radikal,
            ))

    return rows, group_sizes


def write_xlsx(rows, group_sizes, out_path):
    wb = Workbook()
    ws = wb.active
    ws.title = "Akar Kosakata"

    header_font = Font(name="Arial", bold=True, color="FFFFFF", size=11)
    header_fill = PatternFill(start_color="4A4A4A", end_color="4A4A4A", fill_type="solid")
    body_font = Font(name="Arial", size=10.5)
    akar_font = Font(name="Arial", size=11, bold=True, color="9C7A1E")
    thin = Side(style="thin", color="D9D9D9")
    border = Border(left=thin, right=thin, top=thin, bottom=thin)
    center = Alignment(horizontal="center", vertical="center", wrap_text=True)
    left = Alignment(horizontal="left", vertical="center", wrap_text=True)

    ws.append(HEADERS)
    for col in range(1, len(HEADERS) + 1):
        c = ws.cell(row=1, column=col)
        c.font = header_font
        c.fill = header_fill
        c.alignment = center
        c.border = border
    ws.freeze_panes = "A2"

    r = 2
    for group_size in group_sizes:
        start_row = r
        for _ in range(group_size):
            row = rows[r - 2]
            for col, value in enumerate(row, start=1):
                c = ws.cell(row=r, column=col, value=value if value != "" else None)
                c.font = akar_font if col <= 3 else body_font
                c.alignment = center if col in (2, 3, 5, 6, 7, 10) else left
                c.border = border
            r += 1
        end_row = r - 1
        if end_row > start_row:
            for col in (1, 2, 3):
                ws.merge_cells(start_row=start_row, start_column=col, end_row=end_row, end_column=col)
                ws.cell(row=start_row, column=col).alignment = Alignment(
                    horizontal="center", vertical="center", wrap_text=True
                )

    widths = [16, 14, 22, 16, 16, 26, 10, 34, 34, 10]
    for i, w in enumerate(widths, start=1):
        ws.column_dimensions[get_column_letter(i)].width = w

    ws.print_title_rows = "1:1"
    ws.page_setup.orientation = "landscape"
    ws.page_setup.fitToWidth = 1
    ws.page_setup.fitToHeight = 0
    ws.sheet_properties.pageSetUpPr.fitToPage = True

    wb.save(out_path)


def write_csv(rows, group_sizes, out_path):
    # Untuk CSV, isi ulang kolom akar di tiap baris (CSV tidak punya merge cell)
    expanded = []
    idx = 0
    for group_size in group_sizes:
        akar, pinyin_akar, arti_akar = rows[idx][0], rows[idx][1], rows[idx][2]
        for i in range(group_size):
            row = list(rows[idx + i])
            row[0], row[1], row[2] = akar, pinyin_akar, arti_akar
            expanded.append(row)
        idx += group_size

    with open(out_path, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(HEADERS)
        writer.writerows(expanded)


def main():
    parser = argparse.ArgumentParser(description="Konversi produktif_karakter.json ke tabel Excel/CSV siap print.")
    parser.add_argument("produktif_json", help="Path ke produktif_karakter.json")
    parser.add_argument("app_words_json", help="Path ke app_words.json (untuk lookup radikal & makna karakter)")
    parser.add_argument("output", help="Path file output (.xlsx atau .csv)")
    parser.add_argument("--etimologi", default=None, help="Path opsional ke data/char_etymology_id.json (kualitas Bantu Ingat lebih baik)")
    parser.add_argument("--min-turunan", type=int, default=1, help="Hanya sertakan akar dengan minimal N kata turunan (default 1)")
    parser.add_argument("--csv", action="store_true", help="Paksa output berformat CSV walau nama file .xlsx")
    args = parser.parse_args()

    akar_data = load_json(args.produktif_json)
    app_words = load_json(args.app_words_json)
    radical_lookup = build_radical_lookup(app_words)
    char_meaning_index = build_char_meaning_index(app_words)
    char_etymology = load_char_etymology(args.etimologi)

    rows, group_sizes = flatten_rows(akar_data, radical_lookup, char_etymology, char_meaning_index, args.min_turunan)

    if args.csv or args.output.lower().endswith(".csv"):
        write_csv(rows, group_sizes, args.output)
    else:
        write_xlsx(rows, group_sizes, args.output)

    total_akar = len(group_sizes)
    total_kata = len(rows)
    terisi_bantu_ingat = sum(1 for r in rows if r[7])
    terisi_asal_usul = sum(1 for r in rows if r[8])
    print(f"Selesai. {total_akar} akar kosakata, {total_kata} kata turunan -> {args.output}")
    print(f"[Info] Kolom 'Bantu Ingat' terisi untuk {terisi_bantu_ingat}/{total_kata} kata turunan.")
    if args.etimologi:
        print(f"[Info] Kolom 'Asal-Usul' terisi untuk {terisi_asal_usul}/{total_kata} kata turunan.")
    else:
        print("[Info] Tanpa --etimologi, kualitas Bantu Ingat lebih terbatas dan kolom Asal-Usul kosong.")


if __name__ == "__main__":
    main()

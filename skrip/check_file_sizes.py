#!/usr/bin/env python3
"""
check_file_sizes.py — Mandarin Interaktif: cek ukuran & dampak load file data
=============================================================================
Cara pakai (dari folder C:\\mandarin_app\\):
    python check_file_sizes.py

Mengukur ukuran tiap file di data/ dan mensimulasikan waktu parse JSON-nya
di Python (proxi kasar untuk waktu JSON.parse() di browser -- angka
sebenarnya di browser biasanya lebih cepat, tapi urutan besar/kecilnya
representatif untuk melihat file mana yang jadi beban).
"""
import json
import time
from pathlib import Path

DATA_DIR = Path("data")

FILES_TO_CHECK = [
    "nuance_pairs.json",
    "app_words.json",
    "cidict_index.json",
    "graded_readers.json",
    "confusion_groups.json",
    "char_etymology_id.json",
    "index_radical.json",
    "index_stroke.json",
    "index_theme.json",
    "index_phonetic.json",
    "produktif_karakter.json",
    "hanzi_writer_data.json",
]


def human_size(n):
    for unit in ["B", "KB", "MB", "GB"]:
        if n < 1024:
            return f"{n:.1f} {unit}"
        n /= 1024
    return f"{n:.1f} TB"


def main():
    if not DATA_DIR.exists():
        print(f"[GAGAL] Folder {DATA_DIR} tidak ditemukan. Jalankan dari C:\\mandarin_app\\")
        return

    print(f"{'File':<28} {'Ukuran':>10} {'Waktu parse':>14} {'Catatan'}")
    print("-" * 80)

    total_size = 0
    results = []
    for fname in FILES_TO_CHECK:
        path = DATA_DIR / fname
        if not path.exists():
            results.append((fname, None, None, "tidak ada / belum dibuat"))
            continue
        size = path.stat().st_size
        total_size += size

        t0 = time.perf_counter()
        try:
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
            t1 = time.perf_counter()
            parse_time = t1 - t0
            if fname == "nuance_pairs.json" and isinstance(data, dict) and "pairs" in data:
                n_items = len(data["pairs"])
            else:
                n_items = len(data) if isinstance(data, (list, dict)) else None
            note = f"{n_items} entri" if n_items is not None else ""
        except Exception as e:
            parse_time = None
            note = f"GAGAL PARSE: {e}"

        results.append((fname, size, parse_time, note))

    for fname, size, ptime, note in results:
        size_str = human_size(size) if size is not None else "-"
        time_str = f"{ptime*1000:.0f} ms" if ptime is not None else "-"
        print(f"{fname:<28} {size_str:>10} {time_str:>14}   {note}")

    print("-" * 80)
    print(f"Total ukuran file di atas: {human_size(total_size)}")

    # Peringatan kalau nuance_pairs.json sudah termasuk besar
    nuance_size = next((s for f, s, t, n in results if f == "nuance_pairs.json" and s), 0)
    if nuance_size > 2 * 1024 * 1024:
        print(f"\n[PERHATIAN] nuance_pairs.json sudah {human_size(nuance_size)}.")
        print("            Ini di-fetch terpisah oleh kamus-nuance.js (bukan bagian")
        print("            dari load awal kamus.html), jadi TIDAK memperlambat")
        print("            waktu buka halaman pertama kali. Tapi kalau nanti dipakai")
        print("            juga di flashcard.html/wordbuilder.html, waktu fetch")
        print("            pertama kali di halaman itu perlu dicek juga.")

    print("\nKalau mau saya tinjau, kirim balik output tabel di atas (copy-paste teks CMD-nya).")


if __name__ == "__main__":
    main()

"""
peek_and_extract.py — Mengintip & mengekstrak 2 file besar
============================================================
Dua file ini terlalu besar untuk diupload mentah-mentah:
  - C:\\mandarin_kamus\\output\\themes.json           (~19 MB)
  - C:\\hanyu_extract\\output_final\\master_final_hsk.json (~75 MB)

Script ini TIDAK mengubah file aslinya. Ia membaca file-file itu,
lalu:
  1. Menampilkan struktur aslinya (biar Claude paham skemanya)
  2. Membuat versi yang JAUH lebih kecil & relevan untuk diupload:
       - themes_extracted.json      -> semua kata per tema, tapi
         cuma field penting (hanzi, pinyin, arti, hsk) - bukan
         field besar/berulang yang bikin filenya bengkak
       - hsk_new_words.json         -> HANYA kata di master_final_hsk
         yang BELUM ada di app_words.json (kosakata "baru" di luar
         cakupan kamus yang sekarang dipakai)

CARA PAKAI:
  1. Taruh file ini di folder yang sama dengan app_words.json ATAU
     edit variabel APP_WORDS_PATH di bawah supaya menunjuk ke lokasi
     app_words.json yang dipakai app (biasanya di dalam project
     mandarin_app, folder data/).
  2. Jalankan:  python peek_and_extract.py
  3. Hasilnya 3 file baru muncul di folder yang sama dengan script:
       - peek_report.txt        (ringkasan struktur, baca dulu ini)
       - themes_extracted.json  (untuk diupload ke Claude)
       - hsk_new_words.json     (untuk diupload ke Claude)
============================================================
"""

import json
import os

# ── SESUAIKAN PATH INI KALAU LOKASINYA BEDA ─────────────────────────
THEMES_PATH      = r"C:\mandarin_kamus\output\themes.json"
MASTER_HSK_PATH  = r"C:\hanyu_extract\output_final\master_final_hsk.json"
APP_WORDS_PATH   = r"app_words.json"   # kamus yang SUDAH dipakai app sekarang

OUT_DIR = os.path.dirname(os.path.abspath(__file__))


def human_size(path):
    if not os.path.isfile(path):
        return "TIDAK DITEMUKAN"
    n = os.path.getsize(path)
    for unit in ["B", "KB", "MB", "GB"]:
        if n < 1024:
            return f"{n:.1f}{unit}"
        n /= 1024
    return f"{n:.1f}TB"


def peek_themes(report):
    report.write("=" * 60 + "\n")
    report.write(f"THEMES.JSON  ({human_size(THEMES_PATH)})\n")
    report.write("=" * 60 + "\n")
    if not os.path.isfile(THEMES_PATH):
        report.write("File tidak ditemukan, dilewati.\n\n")
        return None

    with open(THEMES_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    report.write(f"Jumlah tema: {len(data)}\n")
    report.write(f"Daftar tema: {list(data.keys())}\n\n")

    first_theme = next(iter(data))
    first_val = data[first_theme]
    report.write(f"Contoh isi tema '{first_theme}':\n")
    report.write(f"  Tipe: {type(first_val).__name__}\n")
    if isinstance(first_val, list):
        report.write(f"  Jumlah item: {len(first_val)}\n")
        report.write(f"  Contoh item pertama:\n{json.dumps(first_val[0], ensure_ascii=False, indent=2)}\n")
    elif isinstance(first_val, dict):
        report.write(f"  Key: {list(first_val.keys())}\n")
    report.write("\n")
    return data


def extract_themes(data):
    """Simpan versi ringkas: cuma field penting per kata per tema."""
    if data is None:
        return
    KEEP_FIELD_CANDIDATES = ["simplified", "hanzi", "word", "pinyin", "meaning_id",
                              "meanings_id", "arti", "hsk", "hsk_level", "hsk3_level"]
    slim = {}
    for tema, items in data.items():
        if not isinstance(items, list):
            slim[tema] = items
            continue
        slim_items = []
        for it in items:
            if isinstance(it, dict):
                slim_items.append({k: it[k] for k in KEEP_FIELD_CANDIDATES if k in it})
            else:
                slim_items.append(it)   # kalau cuma string hanzi polos
        slim[tema] = slim_items

    out_path = os.path.join(OUT_DIR, "themes_extracted.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(slim, f, ensure_ascii=False, indent=1)
    print(f"✓ themes_extracted.json disimpan ({human_size(out_path)})")


def peek_and_extract_master_hsk(report):
    report.write("=" * 60 + "\n")
    report.write(f"MASTER_FINAL_HSK.JSON  ({human_size(MASTER_HSK_PATH)})\n")
    report.write("=" * 60 + "\n")
    if not os.path.isfile(MASTER_HSK_PATH):
        report.write("File tidak ditemukan, dilewati.\n\n")
        return

    with open(MASTER_HSK_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    report.write(f"Jumlah entri: {len(data)}\n")
    report.write(f"Contoh entri pertama:\n{json.dumps(data[0], ensure_ascii=False, indent=2)}\n\n")

    # Bandingkan dengan app_words.json yang SUDAH dipakai app -> cari kata BARU saja
    existing = set()
    if os.path.isfile(APP_WORDS_PATH):
        with open(APP_WORDS_PATH, "r", encoding="utf-8") as f:
            app_words = json.load(f)
        existing = {w.get("simplified") for w in app_words}
        report.write(f"app_words.json ditemukan: {len(existing)} kata sudah ada di kamus.\n")
    else:
        report.write("⚠ app_words.json TIDAK ditemukan di lokasi APP_WORDS_PATH — "
                      "semua entri akan dianggap 'baru' (tidak difilter).\n")

    new_words = []
    for entry in data:
        simp = entry.get("simplified")
        if simp and simp not in existing:
            new_words.append({
                "simplified": simp,
                "traditional": entry.get("traditional"),
                "pinyin": entry.get("pinyin_raw") or entry.get("pinyin_list"),
                "meanings": entry.get("definitions"),
                "hsk_level": entry.get("hsk_level"),
                "structure": entry.get("structure"),
            })

    report.write(f"Kata yang BELUM ada di app_words.json: {len(new_words)}\n\n")

    out_path = os.path.join(OUT_DIR, "hsk_new_words.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(new_words, f, ensure_ascii=False, indent=1)
    print(f"✓ hsk_new_words.json disimpan ({len(new_words)} kata, {human_size(out_path)})")


def main():
    report_path = os.path.join(OUT_DIR, "peek_report.txt")
    with open(report_path, "w", encoding="utf-8") as report:
        themes_data = peek_themes(report)
        extract_themes(themes_data)
        peek_and_extract_master_hsk(report)

    print(f"\n✓ Selesai. Baca {report_path} dulu, lalu upload:")
    print("   - peek_report.txt")
    print("   - themes_extracted.json (kalau ukurannya masih besar, kabari saya dulu sebelum upload)")
    print("   - hsk_new_words.json")


if __name__ == "__main__":
    main()

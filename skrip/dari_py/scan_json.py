"""
scan_json.py — Pemindai isi file .json di komputer رسلان
============================================================
Tujuan: mengintip SEMUA file .json di dalam:
  - C:\\hanyu_extract  (dan semua subfoldernya)
  - C:\\mandarin_kamus (dan semua subfoldernya)

lalu membuat laporan ringkas: tiap file itu isinya apa (list/dict,
berapa item, field/key apa saja), dan secara khusus mendeteksi
apakah ada entri yang bertanda level HSK 7/8/9 — supaya kita tahu
file mana yang bisa dipakai sebagai acuan kosakata HSK lanjutan.

CARA PAKAI:
  1. Simpan file ini di mana saja, misalnya di Desktop.
  2. Buka Command Prompt / PowerShell.
  3. Jalankan:  python scan_json.py
  4. Setelah selesai, ada 2 file laporan dibuat di folder yang sama
     dengan script ini:
       - laporan_json.txt   (ringkasan gampang dibaca)
       - laporan_json.json  (detail lengkap, mesin-friendly)
  5. Kirim isi laporan_json.txt (atau upload laporan_json.json)
     ke Claude untuk dianalisis.

Tidak mengubah/menghapus file apa pun — murni membaca saja.
============================================================
"""

import json
import os
import sys

# ── FOLDER YANG DIPINDAI (edit di sini kalau lokasinya beda) ───────
ROOT_DIRS = [
    r"C:\hanyu_extract",
    r"C:\mandarin_kamus",
]

# Field yang dicurigai menyimpan info level HSK (nama field bisa macam-macam)
HSK_FIELD_CANDIDATES = ["hsk", "hsk2", "hsk_level", "level", "hsklevel", "hsk_new"]

# Kalau file lebih besar dari ini (MB), tetap dicoba tapi diberi peringatan
BIG_FILE_WARN_MB = 50


def human_size(num_bytes):
    for unit in ["B", "KB", "MB", "GB"]:
        if num_bytes < 1024:
            return f"{num_bytes:.1f}{unit}"
        num_bytes /= 1024
    return f"{num_bytes:.1f}TB"


def find_json_files(root_dirs):
    """Cari semua file .json di dalam root_dirs + subfoldernya."""
    found = []
    for root_dir in root_dirs:
        if not os.path.isdir(root_dir):
            print(f"⚠ Folder tidak ditemukan, dilewati: {root_dir}")
            continue
        for dirpath, _dirnames, filenames in os.walk(root_dir):
            for fn in filenames:
                if fn.lower().endswith(".json"):
                    found.append(os.path.join(dirpath, fn))
    return found


def detect_hsk_levels(obj, depth=0, max_depth=4, sample_limit=20000):
    """Telusuri struktur (list/dict apa pun) & kumpulkan nilai unik dari
    field yang namanya mirip 'hsk'. Dibatasi depth & jumlah item supaya
    tidak terlalu lama untuk file raksasa."""
    levels_found = set()
    count_checked = 0

    def walk(o, d):
        nonlocal count_checked
        if count_checked > sample_limit or d > max_depth:
            return
        if isinstance(o, dict):
            for k, v in o.items():
                count_checked += 1
                if k.lower() in HSK_FIELD_CANDIDATES and v not in (None, ""):
                    levels_found.add(str(v))
                elif isinstance(v, (dict, list)):
                    walk(v, d + 1)
        elif isinstance(o, list):
            for item in o[:sample_limit]:
                walk(item, d + 1)

    walk(obj, depth)
    return levels_found


def summarize_value(v, key_limit=25):
    """Ringkas satu nilai JSON (list/dict/lainnya) jadi deskripsi singkat."""
    if isinstance(v, list):
        n = len(v)
        sample = v[0] if n else None
        sample_keys = list(sample.keys())[:key_limit] if isinstance(sample, dict) else None
        return {
            "tipe": "list",
            "jumlah_item": n,
            "contoh_item_pertama": sample if not isinstance(sample, (dict, list)) else None,
            "key_di_item_pertama": sample_keys,
        }
    elif isinstance(v, dict):
        keys = list(v.keys())
        return {
            "tipe": "dict",
            "jumlah_key": len(keys),
            "daftar_key": keys[:key_limit],
        }
    else:
        return {"tipe": type(v).__name__, "nilai": v}


def scan_file(path):
    result = {"path": path}
    try:
        size_bytes = os.path.getsize(path)
        result["ukuran"] = human_size(size_bytes)
        if size_bytes > BIG_FILE_WARN_MB * 1024 * 1024:
            result["peringatan"] = f"File besar (> {BIG_FILE_WARN_MB}MB), tetap dicoba dibaca."

        with open(path, "r", encoding="utf-8", errors="replace") as f:
            data = json.load(f)

        result["struktur"] = summarize_value(data)
        hsk_levels = detect_hsk_levels(data)
        result["level_hsk_terdeteksi"] = sorted(hsk_levels) if hsk_levels else []
        result["ada_hsk_7_8_9"] = any(lv in ("7", "8", "9") for lv in hsk_levels)
        result["status"] = "OK"

    except json.JSONDecodeError as e:
        result["status"] = "GAGAL_PARSE_JSON"
        result["error"] = str(e)
    except MemoryError:
        result["status"] = "GAGAL_TERLALU_BESAR"
    except Exception as e:
        result["status"] = "GAGAL_LAIN"
        result["error"] = str(e)

    return result


def main():
    print("Memindai folder:")
    for d in ROOT_DIRS:
        print(f"  - {d}")
    print()

    files = find_json_files(ROOT_DIRS)
    print(f"Ditemukan {len(files)} file .json. Memproses satu per satu...\n")

    results = []
    for i, path in enumerate(files, 1):
        print(f"[{i}/{len(files)}] {path}")
        results.append(scan_file(path))

    # ── Simpan laporan detail (JSON) ────────────────────────────────
    out_dir = os.path.dirname(os.path.abspath(__file__))
    json_report_path = os.path.join(out_dir, "laporan_json.json")
    with open(json_report_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=1)

    # ── Simpan laporan ringkas (TXT, gampang dibaca) ────────────────
    txt_report_path = os.path.join(out_dir, "laporan_json.txt")
    with open(txt_report_path, "w", encoding="utf-8") as f:
        f.write(f"LAPORAN PEMINDAIAN FILE JSON\n")
        f.write(f"Folder dipindai: {', '.join(ROOT_DIRS)}\n")
        f.write(f"Total file ditemukan: {len(files)}\n")
        f.write("=" * 70 + "\n\n")

        # Ringkasan file yang punya HSK 7/8/9
        hsk789 = [r for r in results if r.get("ada_hsk_7_8_9")]
        f.write(f"★ FILE YANG MENGANDUNG TAG HSK 7/8/9: {len(hsk789)}\n")
        for r in hsk789:
            f.write(f"   - {r['path']}  (level terdeteksi: {r['level_hsk_terdeteksi']})\n")
        f.write("\n" + "=" * 70 + "\n\n")

        for r in results:
            f.write(f"FILE : {r['path']}\n")
            f.write(f"  Status  : {r['status']}\n")
            if r["status"] != "OK":
                f.write(f"  Error   : {r.get('error', '-')}\n\n")
                continue
            f.write(f"  Ukuran  : {r['ukuran']}\n")
            if "peringatan" in r:
                f.write(f"  ⚠ {r['peringatan']}\n")
            s = r["struktur"]
            if s["tipe"] == "list":
                f.write(f"  Struktur: list berisi {s['jumlah_item']} item\n")
                if s["key_di_item_pertama"]:
                    f.write(f"  Key di tiap item (dari item pertama): {s['key_di_item_pertama']}\n")
            elif s["tipe"] == "dict":
                f.write(f"  Struktur: dict dengan {s['jumlah_key']} key\n")
                f.write(f"  Daftar key: {s['daftar_key']}\n")
            else:
                f.write(f"  Struktur: {s['tipe']} (bukan list/dict)\n")
            f.write(f"  Level HSK terdeteksi di dalam file: {r['level_hsk_terdeteksi']}\n")
            f.write("\n")

    print("\n✓ Selesai!")
    print(f"  Laporan ringkas : {txt_report_path}")
    print(f"  Laporan detail  : {json_report_path}")
    print("\nSilakan kirim/upload salah satu (atau dua-duanya) file laporan itu ke Claude.")


if __name__ == "__main__":
    main()

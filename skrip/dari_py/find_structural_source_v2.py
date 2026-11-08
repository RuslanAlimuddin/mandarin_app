# -*- coding: utf-8 -*-
"""
find_structural_source_v2.py
────────────────────────────────
Perluasan dari find_structural_source.py. Kali ini mencari di:

  1. C:\\mandarin_app\\   (folder aktif -- sudah pernah di-scan, discan
                           ulang untuk konsistensi laporan)
  2. C:\\mandarin_kamus\\ (disebut di enrichment.py & extract_v2.py --
                           BELUM pernah di-scan)
  3. C:\\hanyu_extract\\  (disebut di extract_v2.py -- BELUM pernah
                           di-scan)
  4. Arsip checkpoint (*.zip) di C:\\mandarin_app\\ -- kalau script
     aslinya sudah dihapus dari folder aktif, kemungkinan masih
     terjebak di salah satu zip checkpoint lama. Dicari TANPA
     mengekstrak seluruh zip (cuma intip daftar isi & baca file .py
     yang relevan langsung dari dalam zip).

TIDAK mengubah/menghapus/mengekstrak apa pun secara permanen -- murni
baca. Kalau salah satu dari 3 folder di atas tidak ada di PC anda,
otomatis dilewati (tidak error).

CARA PAKAI:
    cd C:\\mandarin_app
    python find_structural_source_v2.py

Output: source_report_v2.txt di folder yang sama.
"""

import os
import re
import zipfile
from pathlib import Path

CANDIDATE_ROOTS = [
    Path(r"C:\mandarin_app"),
    Path(r"C:\mandarin_kamus"),
    Path(r"C:\hanyu_extract"),
]

SKIP_DIRS = {".git", "node_modules", "__pycache__", ".venv", "venv"}

KEYWORDS = [
    "radical_number", "char_type", "bopomofo", "decomposition",
    "makemeahanzi", "make_me_a_hanzi", "kangxi", "radical", "stroke_count",
]
# Kata kunci "kuat" -- kalau script menyebut ini, kemungkinan besar dialah
# pembangun field struktural (bukan cuma menyebut sambil lalu)
STRONG_KEYWORDS = ["radical_number", "kangxi", "decomposition", "char_type"]

ZIP_DIR = Path(r"C:\mandarin_app")  # lokasi checkpoint zip diduga di sini


def out(lines, s=""):
    print(s)
    lines.append(s)


def scan_folder(root: Path, lines):
    out(lines, "\n" + "=" * 70)
    out(lines, f"SCAN FOLDER: {root}")
    out(lines, "=" * 70)

    if not root.exists():
        out(lines, "  (folder tidak ditemukan di PC ini -- dilewati)")
        return

    py_files = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS and not d.startswith(".")]
        for fn in filenames:
            if fn.lower().endswith(".py"):
                py_files.append(Path(dirpath) / fn)

    out(lines, f"  Total file .py ditemukan: {len(py_files)}")

    hits = []
    for f in py_files:
        try:
            text = f.read_text(encoding="utf-8", errors="ignore").lower()
        except Exception:
            continue
        matched = [k for k in KEYWORDS if k in text]
        strong = [k for k in STRONG_KEYWORDS if k in text]
        if matched:
            hits.append((f, matched, strong))

    # urutkan: yang punya kata kunci KUAT dulu, baru yang banyak match
    hits.sort(key=lambda x: (-len(x[2]), -len(x[1])))

    if hits:
        out(lines, f"\n  Script relevan (diurutkan, paling kuat dulu):")
        for f, matched, strong in hits:
            tag = " ⭐ KANDIDAT KUAT" if strong else ""
            out(lines, f"    - {f}{tag}")
            out(lines, f"        kata kunci: {', '.join(matched)}")
    else:
        out(lines, "  (tidak ada script .py yang menyebut kata kunci relevan)")

    # juga cek file non-.py yang namanya relevan (misal .json output pemetaan radikal)
    out(lines, f"\n  File lain (non-.py) dengan nama mengandung 'radical'/'kangxi'/'stroke':")
    other_hits = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS and not d.startswith(".")]
        for fn in filenames:
            fnl = fn.lower()
            if fnl.endswith(".py"):
                continue
            if any(k in fnl for k in ["radical", "kangxi", "stroke"]):
                other_hits.append(Path(dirpath) / fn)
    if other_hits:
        for f in other_hits:
            out(lines, f"    - {f}")
    else:
        out(lines, "    (tidak ada)")


def scan_zip_archives(lines):
    out(lines, "\n" + "=" * 70)
    out(lines, f"SCAN ARSIP CHECKPOINT (*.zip) di {ZIP_DIR}")
    out(lines, "=" * 70)

    if not ZIP_DIR.exists():
        out(lines, "  (folder tidak ditemukan)")
        return

    zip_files = sorted(ZIP_DIR.glob("*.zip")) + sorted(ZIP_DIR.glob("**/*.zip"))
    zip_files = sorted(set(zip_files))

    if not zip_files:
        out(lines, "  (tidak ada file .zip ditemukan langsung -- cek juga apakah checkpoint")
        out(lines, "   disimpan di subfolder lain, mis. 'checkpoints/' atau 'backup/')")
        return

    out(lines, f"  Total arsip .zip ditemukan: {len(zip_files)}")

    for zpath in zip_files:
        try:
            with zipfile.ZipFile(zpath, "r") as zf:
                names = zf.namelist()
                py_names = [n for n in names if n.lower().endswith(".py")]
                candidate_names = [n for n in py_names if any(
                    k in n.lower() for k in ["radical", "enrich", "struct", "kangxi", "hanzi", "decomp"]
                )]
                if candidate_names:
                    size_mb = zpath.stat().st_size / 1024 / 1024
                    out(lines, f"\n  📦 {zpath.name} ({size_mb:.1f} MB) -- kandidat ditemukan:")
                    for n in candidate_names:
                        out(lines, f"      - {n}")
        except Exception as e:
            out(lines, f"  ⚠ Gagal buka {zpath.name}: {e}")

    out(lines, "\n  (Kalau ada kandidat di atas, beri tahu nama zip + nama file-nya,")
    out(lines, "   nanti saya kasih 1 baris perintah untuk ekstrak file itu SAJA")
    out(lines, "   dari dalam zip, tanpa membongkar seluruh arsip.)")


def main():
    lines = []
    out(lines, "PENCARIAN DIPERLUAS — mandarin_app + mandarin_kamus + hanyu_extract + zip")
    for root in CANDIDATE_ROOTS:
        scan_folder(root, lines)
    scan_zip_archives(lines)

    Path("source_report_v2.txt").write_text("\n".join(lines), encoding="utf-8")
    print(f"\n✓ Laporan disimpan ke source_report_v2.txt")


if __name__ == "__main__":
    main()

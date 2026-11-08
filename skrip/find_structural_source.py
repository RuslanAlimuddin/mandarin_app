# -*- coding: utf-8 -*-
"""
find_structural_source.py
───────────────────────────
Skrip PENCARIAN (bukan pemroses) -- tujuannya cuma menemukan:
  1. Script Python lama yang kemungkinan membangun field struktural
     (radical, radical_number, stroke_count, structure, components,
     bopomofo, char_type) di app_words.json
  2. File data mentah sumber (kemungkinan besar dari proyek Make Me a
     Hanzi -- biasanya bernama dictionary.txt / graphics.txt, atau
     sudah dikonversi ke .json)

TIDAK mengubah file apa pun. Cuma membaca nama file, mencari kata kunci
di dalam isi .py, dan mencetak laporan.

CARA PAKAI:
    cd C:\\mandarin_app
    python find_structural_source.py

Output: dicetak ke layar + disimpan ke source_report.txt (folder yang
sama) -- tinggal buka file itu dan tempel isinya ke chat.
"""

import os
import re
from pathlib import Path

ROOT = Path(".")

# Folder yang dilewati saat scan (supaya cepat, tidak masuk ke folder besar
# yang jelas bukan lokasi script/sumber data)
SKIP_DIRS = {".git", "node_modules", "__pycache__", ".venv", "venv", "backup_zips"}

# Kata kunci yang menandakan file .py ini kemungkinan pembangun field
# struktural -- dicari case-insensitive di NAMA file maupun ISI file
KEYWORDS_STRUCTURAL = [
    "radical", "radikal", "stroke", "goresan", "structure", "struktur",
    "component", "komponen", "bopomofo", "char_type", "makemeahanzi",
    "make_me_a_hanzi", "kangxi", "decomposition", "dekomposisi",
]

# Nama file data mentah yang umum dipakai proyek Make Me a Hanzi /
# CJK dictionary source
KNOWN_RAW_FILENAMES = [
    "dictionary.txt", "graphics.txt", "characters.txt", "radicals.txt",
    "kangxi", "cjk-decomp", "makemeahanzi", "hanzi_decomp",
]


def walk_files():
    for dirpath, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS and not d.startswith(".")]
        for fn in filenames:
            yield Path(dirpath) / fn


def main():
    lines = []

    def out(s=""):
        print(s)
        lines.append(s)

    out("PENCARIAN SUMBER FIELD STRUKTURAL — C:\\mandarin_app")
    out("=" * 70)

    py_files = []
    json_files = []
    raw_candidates = []
    all_files = list(walk_files())

    out(f"\nTotal file terdeteksi (semua jenis, di luar folder yang dilewati): {len(all_files)}")

    for f in all_files:
        suffix = f.suffix.lower()
        name_lower = f.name.lower()
        if suffix == ".py":
            py_files.append(f)
        elif suffix == ".json":
            json_files.append(f)
        # deteksi kandidat file data mentah berdasar nama
        if any(k in name_lower for k in KNOWN_RAW_FILENAMES):
            raw_candidates.append(f)

    # ── 1. Semua file .py yang namanya mengandung kata kunci ──────────
    out(f"\n[1] SCRIPT .py YANG NAMANYA MENGANDUNG KATA KUNCI STRUKTURAL")
    name_matches = [f for f in py_files if any(k in f.name.lower() for k in KEYWORDS_STRUCTURAL)]
    if name_matches:
        for f in sorted(name_matches):
            out(f"  - {f}")
    else:
        out("  (tidak ada nama file yang cocok)")

    # ── 2. Semua file .py yang ISINYA mengandung kata kunci ────────────
    out(f"\n[2] SCRIPT .py YANG ISINYA MENYEBUT KATA KUNCI STRUKTURAL")
    out(f"    (total {len(py_files)} file .py di-scan)")
    content_matches = {}
    for f in py_files:
        try:
            text = f.read_text(encoding="utf-8", errors="ignore").lower()
        except Exception:
            continue
        hits = [k for k in KEYWORDS_STRUCTURAL if k in text]
        if hits:
            content_matches[f] = hits

    if content_matches:
        # urutkan yang paling banyak match dulu (kemungkinan besar itu scriptnya)
        for f, hits in sorted(content_matches.items(), key=lambda x: -len(x[1])):
            out(f"  - {f}")
            out(f"      kata kunci ditemukan: {', '.join(hits)}")
    else:
        out("  (tidak ada isi file .py yang cocok)")

    # ── 3. File data mentah yang namanya khas Make Me a Hanzi / CJK ────
    out(f"\n[3] KANDIDAT FILE DATA MENTAH (nama khas dictionary CJK)")
    if raw_candidates:
        for f in sorted(raw_candidates):
            size_kb = f.stat().st_size / 1024
            out(f"  - {f}  ({size_kb:,.0f} KB)")
    else:
        out("  (tidak ada file dengan nama khas ditemukan)")

    # ── 4. Semua file .json di folder data/ (untuk lihat index apa saja
    #        yang sudah ada -- barangkali sudah ada index_radical_raw.json
    #        atau semacamnya yang belum disebut di kamus-data.js) ───────
    out(f"\n[4] SEMUA FILE .json DI FOLDER data/ (untuk cross-check)")
    data_jsons = [f for f in json_files if "data" in [p.lower() for p in f.parts]]
    if data_jsons:
        for f in sorted(data_jsons):
            size_kb = f.stat().st_size / 1024
            out(f"  - {f}  ({size_kb:,.0f} KB)")
    else:
        out("  (folder data/ tidak ditemukan atau kosong)")

    # ── 5. Cek apakah ada folder "scripts" / "tools" / "build" terpisah ─
    out(f"\n[5] SUB-FOLDER YANG KEMUNGKINAN BERISI SCRIPT BUILD/PIPELINE")
    candidate_dirs = set()
    for f in py_files:
        rel_parts = f.parts
        if len(rel_parts) > 1:
            candidate_dirs.add(rel_parts[0])
    if candidate_dirs:
        for d in sorted(candidate_dirs):
            out(f"  - {d}/")
    else:
        out("  (semua script .py ada langsung di folder root, tidak ada sub-folder)")

    # ── 6. Total ringkasan cepat ─────────────────────────────────────
    out(f"\n[6] RINGKASAN CEPAT")
    out(f"  Total script .py di proyek: {len(py_files)}")
    out(f"  Script .py relevan (nama ATAU isi cocok): "
        f"{len(set(name_matches) | set(content_matches.keys()))}")
    out(f"  Kandidat file data mentah CJK: {len(raw_candidates)}")

    out(f"\n{'=' * 70}")
    out("✓ SELESAI. Kalau [2] menemukan script yang jelas cocok, tempel ISI")
    out("  script itu (bukan cuma nama filenya) ke chat supaya saya bisa")
    out("  pinjam logikanya persis. Kalau [2]/[3] kosong semua, berarti")
    out("  kemungkinan besar field ini dibangun sekali lalu scriptnya sudah")
    out("  dihapus/tidak disimpan -- saya akan pakai Jalan 2 (ambil ulang")
    out("  dari sumber Make Me a Hanzi di GitHub, dengan sample-check ekstra).")

    Path("source_report.txt").write_text("\n".join(lines), encoding="utf-8")
    print(f"\nLaporan disimpan ke: {Path('source_report.txt').resolve()}")


if __name__ == "__main__":
    main()

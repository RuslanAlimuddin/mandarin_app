"""
cari_riwayat_sinonim_di_blueprint.py — READ-ONLY.

Cari di SEMUA file BLUEPRINT_v*.md (v1 sampai v27, di folder Downloads
atau folder manapun yang kamu kasih tau) untuk paragraf yang menyebut
sinonim/antonim -- supaya ketahuan apakah fitur "perkaya sinonim/antonim"
ini pernah dibahas/dikerjakan di sesi-sesi sebelumnya, dan sejauh mana.

Cara pakai:
    python cari_riwayat_sinonim_di_blueprint.py "C:\\Users\\NAMA\\Downloads"

(ganti path dgn folder tempat semua BLUEPRINT_v*.md disimpan -- kalau
tidak yakin, jalankan tanpa argumen dan script akan coba cari otomatis
di beberapa lokasi umum)
"""

import os
import re
import sys
import glob

KEYWORDS = ["sinonim", "antonim", "synonym", "antonym"]

DEFAULT_SEARCH_DIRS = [
    os.path.expanduser("~/Downloads"),
    os.path.expanduser("~/Desktop"),
    os.getcwd(),
]


def find_blueprint_files(search_dir):
    pattern = os.path.join(search_dir, "**", "BLUEPRINT*.md")
    return glob.glob(pattern, recursive=True)


def extract_context_paragraphs(text, keyword, context_chars=400):
    """Cari semua kemunculan keyword, kembalikan potongan teks di sekitarnya."""
    results = []
    for m in re.finditer(re.escape(keyword), text, re.IGNORECASE):
        start = max(0, m.start() - context_chars)
        end = min(len(text), m.end() + context_chars)
        snippet = text[start:end]
        results.append(snippet)
    return results


def main():
    if len(sys.argv) > 1:
        search_dirs = [sys.argv[1]]
    else:
        search_dirs = DEFAULT_SEARCH_DIRS

    all_files = []
    for d in search_dirs:
        if os.path.isdir(d):
            found = find_blueprint_files(d)
            all_files.extend(found)

    all_files = sorted(set(all_files))
    print(f"Ditemukan {len(all_files)} file BLUEPRINT*.md:")
    for f in all_files:
        print(f"  {f}")

    if not all_files:
        print("\nTidak ada file ditemukan di lokasi default. Jalankan ulang dgn path eksplisit:")
        print('  python cari_riwayat_sinonim_di_blueprint.py "C:\\path\\ke\\folder\\blueprint"')
        return

    print("\n" + "=" * 70)
    print("HASIL PENCARIAN 'sinonim'/'antonim'/'synonym'/'antonym' per file")
    print("=" * 70)

    for fpath in all_files:
        try:
            with open(fpath, "r", encoding="utf-8", errors="ignore") as f:
                text = f.read()
        except Exception as e:
            print(f"\n[SKIP] {fpath}: {e}")
            continue

        total_hits = sum(text.lower().count(kw) for kw in KEYWORDS)
        if total_hits == 0:
            continue

        print(f"\n\n########## {os.path.basename(fpath)} ({total_hits} kemunculan) ##########")
        seen_snippets = set()
        for kw in KEYWORDS:
            for snippet in extract_context_paragraphs(text, kw):
                # dedup snippet yg overlap (krn keyword sinonim & synonym mungkin dkt)
                key = snippet[:80]
                if key in seen_snippets:
                    continue
                seen_snippets.add(key)
                print(f"\n--- konteks sekitar '{kw}' ---")
                print(snippet.strip())
                print("...")


if __name__ == "__main__":
    main()

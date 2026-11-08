"""
cari_item_belum_selesai_semua_blueprint.py — READ-ONLY.

Scan SEMUA file BLUEPRINT*.md untuk paragraf yang mengandung penanda
"belum selesai / direncanakan tapi belum dikerjakan", supaya bisa dicek
satu-satu: apakah sudah dikerjakan di sesi SETELAHNYA (kadang disebut di
versi lebih baru sbg "SELESAI"), atau benar-benar masih menggantung
sampai v28 (BLUEPRINT terbaru).

BUKAN pencarian sempurna -- ini alat bantu supaya Claude/رسلان punya
titik awal yg berbasis bukti (bukan mengandalkan ingatan/asumsi), lalu
tiap temuan perlu dicek manual apakah masih relevan atau sudah usang.

Cara pakai:
    python cari_item_belum_selesai_semua_blueprint.py "C:\\Users\\User_iO\\Downloads"
"""

import os
import re
import sys
import glob

# Penanda kuat (biasanya eksplisit menyebut status tertunda)
MARKERS = [
    "belum dikerjakan", "belum dibangun", "belum ada sama sekali",
    "belum selesai", "belum diimplementasi", "belum tersedia",
    "belum tergabung", "belum terintegrasi", "belum dipakai",
    "ditunda", "ditangguhkan", "wishlist", "roadmap masa depan",
    "menggantung", "follow-up", "belum dicek", "belum pernah dibahas",
    "prioritas berikutnya", "prioritas tugas berikutnya",
    "belum dimulai", "opsional (kalau diminta)", "belum masuk",
]

DEFAULT_SEARCH_DIRS = [
    os.path.expanduser("~/Downloads"),
    os.getcwd(),
]


def find_blueprint_files(search_dir):
    return glob.glob(os.path.join(search_dir, "**", "BLUEPRINT*.md"), recursive=True)


def version_key(fname):
    """Urutkan file by versi (v1, v2, ..., v28) supaya hasil kronologis."""
    m = re.search(r'v(\d+)', fname)
    if m:
        return int(m.group(1))
    return -1  # file tanpa versi (mis. BLUEPRINT_akar_kosakata.md) di depan


def extract_context(text, keyword, context_chars=350):
    results = []
    for m in re.finditer(re.escape(keyword), text, re.IGNORECASE):
        start = max(0, m.start() - 100)
        end = min(len(text), m.end() + context_chars)
        results.append(text[start:end])
    return results


def main():
    search_dirs = [sys.argv[1]] if len(sys.argv) > 1 else DEFAULT_SEARCH_DIRS

    all_files = []
    for d in search_dirs:
        if os.path.isdir(d):
            all_files.extend(find_blueprint_files(d))
    all_files = sorted(set(all_files), key=lambda f: version_key(os.path.basename(f)))

    print(f"Ditemukan {len(all_files)} file BLUEPRINT, diurutkan kronologis:\n")
    for f in all_files:
        print(f"  {os.path.basename(f)}")

    print("\n" + "=" * 70)
    print("HASIL PENCARIAN PENANDA 'BELUM SELESAI/DITUNDA/WISHLIST' per file")
    print("(baca dari file PALING LAMA dulu -- kalau item yg sama muncul lagi")
    print("di file lebih baru dgn kata 'SELESAI', berarti sudah dikerjakan)")
    print("=" * 70)

    for fpath in all_files:
        try:
            with open(fpath, "r", encoding="utf-8", errors="ignore") as f:
                text = f.read()
        except Exception as e:
            print(f"\n[SKIP] {fpath}: {e}")
            continue

        hits_in_file = []
        for kw in MARKERS:
            hits_in_file.extend(extract_context(text, kw))

        if not hits_in_file:
            continue

        print(f"\n\n########## {os.path.basename(fpath)} ({len(hits_in_file)} penanda) ##########")
        seen = set()
        for snippet in hits_in_file:
            key = snippet[:60]
            if key in seen:
                continue
            seen.add(key)
            print(f"\n--- {snippet.strip()} ---")


if __name__ == "__main__":
    main()

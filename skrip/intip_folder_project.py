"""
intip_folder_project.py — READ-ONLY.

Menyisir SELURUH folder proyek (termasuk semua subfolder) untuk:
  1. Menampilkan struktur file (dikelompokkan per ekstensi)
  2. Mencari file yang NAMANYA mengandung kata kunci tertentu
  3. Mencari kata kunci di DALAM ISI file teks (.py, .txt, .json, .md, .js, .html, .csv)

Tidak mengubah/menghapus apa pun -- murni membaca dan mencetak ke layar.

Cara pakai:
    cd C:\\mandarin_app
    python intip_folder_project.py

    # atau dengan kata kunci sendiri (bisa lebih dari satu):
    python intip_folder_project.py karakter_mirip confusion gabungkan prompt_1 prompt_2

Kalau dijalankan TANPA argumen, dipakai daftar kata kunci default di
bawah -- silakan ganti/tambah sesuai apa yang sedang dicari.
"""

import os
import sys

ROOT = "."  # folder tempat skrip ini dijalankan (biasanya C:\mandarin_app)
SKIP_DIRS = {".git", "node_modules", "__pycache__", "venv", ".venv", "backups"}
TEXT_EXT = {".py", ".txt", ".json", ".md", ".js", ".html", ".csv"}
MAX_CONTENT_SEARCH_SIZE = 5 * 1024 * 1024  # 5 MB -- lewati file teks raksasa

# Ganti daftar ini kapan saja sesuai apa yang sedang dicari
DEFAULT_KEYWORDS = [
    "karakter_mirip",
    "confusion",
    "gabungkan",
    "candidate",
    "prompt_1",
    "prompt_2",
]


def walk_files(root):
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS and not d.startswith(".")]
        for fn in filenames:
            yield os.path.join(dirpath, fn)


def human_size(n):
    for unit in ["B", "KB", "MB", "GB"]:
        if n < 1024:
            return f"{n:.0f}{unit}"
        n /= 1024
    return f"{n:.0f}TB"


def print_tree(root):
    print("=" * 70)
    print(f"STRUKTUR FILE di bawah: {os.path.abspath(root)}")
    print("=" * 70)
    by_ext = {}
    total = 0
    for path in walk_files(root):
        total += 1
        ext = os.path.splitext(path)[1].lower() or "(tanpa ekstensi)"
        by_ext.setdefault(ext, []).append(path)

    print(f"\nTotal file ditemukan: {total}\n")
    for ext in sorted(by_ext, key=lambda e: -len(by_ext[e])):
        files = by_ext[ext]
        print(f"--- {ext}  ({len(files)} file) ---")
        for p in sorted(files):
            rel = os.path.relpath(p, root)
            try:
                size = human_size(os.path.getsize(p))
            except OSError:
                size = "?"
            print(f"  {rel}  [{size}]")
        print()


def search_filenames(root, keywords):
    print("=" * 70)
    print("FILE yang NAMANYA mengandung salah satu kata kunci:")
    print(", ".join(keywords))
    print("=" * 70)
    found_any = False
    for path in walk_files(root):
        name_lower = os.path.basename(path).lower()
        for kw in keywords:
            if kw.lower() in name_lower:
                rel = os.path.relpath(path, root)
                print(f"  {rel}")
                found_any = True
                break
    if not found_any:
        print("  (tidak ada file dengan nama cocok)")
    print()


def search_content(root, keywords):
    print("=" * 70)
    print("ISI FILE yang mengandung salah satu kata kunci (per baris):")
    print(", ".join(keywords))
    print("=" * 70)
    found_any = False
    for path in walk_files(root):
        ext = os.path.splitext(path)[1].lower()
        if ext not in TEXT_EXT:
            continue
        try:
            if os.path.getsize(path) > MAX_CONTENT_SEARCH_SIZE:
                continue
        except OSError:
            continue
        try:
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                lines = f.readlines()
        except OSError:
            continue

        rel = os.path.relpath(path, root)
        matched_lines = []
        for i, line in enumerate(lines, start=1):
            line_lower = line.lower()
            for kw in keywords:
                if kw.lower() in line_lower:
                    matched_lines.append((i, line.strip()))
                    break

        if matched_lines:
            found_any = True
            print(f"\n  >> {rel}  ({len(matched_lines)} baris cocok)")
            for lineno, text in matched_lines[:10]:
                snippet = text[:120]
                print(f"       L{lineno}: {snippet}")
            if len(matched_lines) > 10:
                print(f"       ... ({len(matched_lines) - 10} baris lain tidak ditampilkan)")
    if not found_any:
        print("  (tidak ada isi file yang cocok)")
    print()


def main():
    keywords = sys.argv[1:] if len(sys.argv) > 1 else DEFAULT_KEYWORDS
    print_tree(ROOT)
    search_filenames(ROOT, keywords)
    search_content(ROOT, keywords)


if __name__ == "__main__":
    main()

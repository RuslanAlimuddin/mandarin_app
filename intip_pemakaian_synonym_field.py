"""
intip_pemakaian_synonym_field.py — READ-ONLY, tidak mengubah file apapun.

Tujuan (E.0.2): sebelum ubah skema field synonyms/antonyms di
app_words.json dari array-of-string (["笑"]) jadi array-of-object
([{"word":"笑","note_id":"menangis"}]), cari SEMUA tempat di kode yang
baca field ini -- supaya tidak ada fitur lain (mis. mode game
sinonim/antonim di flashcard.html) yang diam-diam rusak krn asumsi
lama (array of string).

Cara pakai:
    cd C:\\mandarin_app
    python intip_pemakaian_synonym_field.py
"""

import os
import re

ROOT = os.getcwd()
EXTS = (".html", ".js")
SKIP_DIRS = {".git", "node_modules", "__pycache__"}

# Pola yang mengindikasikan kode mengakses field synonyms/antonyms dari
# objek kata (bukan sekadar nama variabel lokal kebetulan sama)
PATTERNS = [
    r"\.synonyms\b",
    r"\.antonyms\b",
    r"\[.synonyms.\]",
    r"\[.antonyms.\]",
    r"synonym_antonym",
]

def scan():
    hits = []
    for dirpath, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for fname in filenames:
            if not fname.lower().endswith(EXTS):
                continue
            fpath = os.path.join(dirpath, fname)
            try:
                with open(fpath, "r", encoding="utf-8", errors="ignore") as f:
                    lines = f.readlines()
            except Exception as e:
                print(f"[SKIP] {fpath}: {e}")
                continue
            for lineno, line in enumerate(lines, start=1):
                for pat in PATTERNS:
                    if re.search(pat, line):
                        rel = os.path.relpath(fpath, ROOT)
                        hits.append((rel, lineno, line.strip()))
                        break
    return hits


def main():
    hits = scan()
    print(f"Total kemunculan '.synonyms' / '.antonyms' / 'synonym_antonym' di seluruh proyek: {len(hits)}\n")

    by_file = {}
    for rel, lineno, text in hits:
        by_file.setdefault(rel, []).append((lineno, text))

    for rel, occs in sorted(by_file.items()):
        print(f"\n=== {rel} ({len(occs)} kemunculan) ===")
        for lineno, text in occs:
            print(f"  L{lineno}: {text[:150]}")


if __name__ == "__main__":
    main()

# -*- coding: utf-8 -*-
"""
diagnose_missing_chars.py
────────────────────────────
Diagnosis presisi untuk 59 karakter yang masih gagal di Tahap 2.
Untuk TIAP karakter, cek 3 hal terpisah:
  1. Ada di data/dictionary.txt? (kalau ada, tampilkan field radical +
     decomposition mentahnya)
  2. Ada di data/hanzi_writer_data.json? (kalau ada, tampilkan jumlah
     goresan dari panjang array "strokes")
  3. Ada di data/char_etymology_id.json? (sumber ke-3, kurasi manual
     anda sendiri -- siapa tahu radikal/goresan kebetulan tercatat di
     sana meski tidak lewat 2 sumber di atas)

TIDAK mengubah apa pun. Cuma diagnosis.

CARA PAKAI:
    cd C:\\mandarin_app
    python diagnose_missing_chars.py
"""

import json
from pathlib import Path

DATA_DIR = Path("data")
PROBLEM_CHARS = list("侄吱呃呗呣呱呸咔咕咚咦咩咯哐哒哞唷唻啪啵喏喔喵喽嗡嗲嗳嗷嘎嘘嘞嘟嘶嘻噎噜噢噻噼嚓嚯妯娌婶庚沥淅潺甥砰窣窸笃耶襟诶陀") + ["唄", "嫒"]
PROBLEM_CHARS = sorted(set(PROBLEM_CHARS))


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def main():
    lines = []

    def out(s=""):
        print(s)
        lines.append(s)

    out(f"Diagnosis {len(PROBLEM_CHARS)} karakter bermasalah")
    out("=" * 70)

    # Load dictionary.txt sebagai dict
    dict_lookup = {}
    dpath = DATA_DIR / "dictionary.txt"
    if dpath.exists():
        with open(dpath, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    obj = json.loads(line)
                except Exception:
                    continue
                ch = obj.get("character")
                if ch:
                    dict_lookup[ch] = obj

    writer_lookup = {}
    wpath = DATA_DIR / "hanzi_writer_data.json"
    if wpath.exists():
        writer_lookup = load_json(wpath)

    etym_lookup = {}
    epath = DATA_DIR / "char_etymology_id.json"
    if epath.exists():
        etym_lookup = load_json(epath)

    n_missing_dict = 0
    n_missing_writer = 0
    n_in_both = 0
    n_missing_both = 0

    for ch in PROBLEM_CHARS:
        in_dict = ch in dict_lookup
        in_writer = ch in writer_lookup
        in_etym = ch in etym_lookup

        out(f"\n[{ch}]")
        if in_dict:
            d = dict_lookup[ch]
            out(f"  dictionary.txt : ADA -> radical={d.get('radical')!r}, "
                f"decomposition={d.get('decomposition')!r}, pinyin={d.get('pinyin')}")
        else:
            out(f"  dictionary.txt : TIDAK ADA")
            n_missing_dict += 1

        if in_writer:
            w = writer_lookup[ch]
            n_strokes = len(w.get("strokes", [])) if isinstance(w, dict) else None
            out(f"  hanzi_writer   : ADA -> jumlah goresan = {n_strokes}")
        else:
            out(f"  hanzi_writer   : TIDAK ADA")
            n_missing_writer += 1

        if in_etym:
            out(f"  char_etymology : ADA -> {etym_lookup[ch]}")
        else:
            out(f"  char_etymology : TIDAK ADA")

        if in_dict and in_writer:
            n_in_both += 1
        if not in_dict and not in_writer:
            n_missing_both += 1

    out(f"\n{'=' * 70}")
    out(f"RINGKASAN")
    out(f"  Total karakter didiagnosis      : {len(PROBLEM_CHARS)}")
    out(f"  Tidak ada di dictionary.txt      : {n_missing_dict}")
    out(f"  Tidak ada di hanzi_writer_data   : {n_missing_writer}")
    out(f"  Ada di KEDUANYA (harusnya lolos!): {n_in_both}")
    out(f"  Tidak ada di KEDUANYA sama sekali: {n_missing_both}")

    Path("diagnose_missing_chars_report.txt").write_text("\n".join(lines), encoding="utf-8")
    print(f"\n✓ Laporan disimpan ke diagnose_missing_chars_report.txt")


if __name__ == "__main__":
    main()

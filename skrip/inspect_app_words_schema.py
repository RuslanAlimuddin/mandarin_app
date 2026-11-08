# -*- coding: utf-8 -*-
"""
inspect_app_words_schema.py
────────────────────────────
Skrip intip skema app_words.json — dijalankan sekali, cuma BACA
(tidak mengubah data apa pun). Tujuannya: mengumpulkan contoh entri
mentah + daftar semua field yang pernah dipakai, supaya prompt AI
eksternal untuk kata seru/onomatope/sapaan bisa dirancang persis
sesuai skema asli.

CARA PAKAI:
    cd C:\\mandarin_app
    python inspect_app_words_schema.py

Output: dicetak ke layar DAN disimpan ke schema_report.txt (folder yang
sama) supaya gampang di-copy-paste ke chat.
"""

import json
import random
from pathlib import Path
from collections import Counter

DATA_PATH = Path("data/app_words.json")
OUT_PATH  = Path("schema_report.txt")


def load_data():
    if not DATA_PATH.exists():
        raise FileNotFoundError(
            f"Tidak ketemu {DATA_PATH}. Pastikan skrip ini dijalankan dari "
            f"folder C:\\mandarin_app\\ (folder induk dari data/)."
        )
    with open(DATA_PATH, encoding="utf-8") as f:
        return json.load(f)


def pretty(entry):
    return json.dumps(entry, ensure_ascii=False, indent=2)


def main():
    lines = []

    def out(s=""):
        print(s)
        lines.append(s)

    data = load_data()
    out(f"Total entri: {len(data):,}")
    out("=" * 70)

    # ── 1. Semua field yang PERNAH muncul di seluruh dataset ──────────
    field_counter = Counter()
    for w in data:
        field_counter.update(w.keys())

    out("\n[1] SEMUA FIELD YANG PERNAH DIPAKAI (field: jumlah entri yang punya field itu)")
    for field, cnt in field_counter.most_common():
        pct = cnt / len(data) * 100
        out(f"  - {field:<20} {cnt:>7,} entri ({pct:5.1f}%)")

    # ── 2. Contoh entri 1 karakter ─────────────────────────────────────
    one_char = [w for w in data if len((w.get("simplified") or w.get("id") or "")) == 1]
    out(f"\n[2] CONTOH ENTRI 1 KARAKTER (dari {len(one_char):,} entri 1-karakter)")
    if one_char:
        out(pretty(random.choice(one_char)))
    else:
        out("  (tidak ditemukan entri 1 karakter)")

    # ── 3. Contoh entri 2 karakter ─────────────────────────────────────
    two_char = [w for w in data if len((w.get("simplified") or w.get("id") or "")) == 2]
    out(f"\n[3] CONTOH ENTRI 2 KARAKTER (dari {len(two_char):,} entri 2-karakter)")
    if two_char:
        out(pretty(random.choice(two_char)))
    else:
        out("  (tidak ditemukan entri 2 karakter)")

    # ── 4. Contoh entri dengan hsk: null (kalau ada) ───────────────────
    null_hsk = [w for w in data if w.get("hsk") is None]
    out(f"\n[4] CONTOH ENTRI hsk: null (dari {len(null_hsk):,} entri hsk:null)")
    if null_hsk:
        out(pretty(random.choice(null_hsk)))
    else:
        out("  (tidak ada entri dengan hsk: null saat ini)")

    # ── 5. Contoh entri dengan pos = 'e' (Ekskl/kata seru) kalau ada ──
    pos_e = [w for w in data if w.get("pos") == "e" or (isinstance(w.get("pos"), list) and "e" in w.get("pos"))]
    out(f"\n[5] CONTOH ENTRI pos='e' (Ekskl/Kata Seru) (dari {len(pos_e):,} entri)")
    if pos_e:
        out(pretty(random.choice(pos_e)))
    else:
        out("  (tidak ada entri dengan pos='e' saat ini -- kode ini ada di posLabel() tapi belum dipakai)")

    # ── 6. Contoh entri dengan pos = 'o' (Onomatope) kalau ada ────────
    pos_o = [w for w in data if w.get("pos") == "o" or (isinstance(w.get("pos"), list) and "o" in w.get("pos"))]
    out(f"\n[6] CONTOH ENTRI pos='o' (Onomatope) (dari {len(pos_o):,} entri)")
    if pos_o:
        out(pretty(random.choice(pos_o)))
    else:
        out("  (tidak ada entri dengan pos='o' saat ini)")

    # ── 7. Semua nilai unik untuk field yang kemungkinan enum ─────────
    out("\n[7] NILAI UNIK untuk field yang kemungkinan berupa enum/kategori")
    for field in ["pos", "structure", "hsk"]:
        vals = set()
        for w in data:
            v = w.get(field)
            if isinstance(v, list):
                vals.update(v)
            else:
                vals.add(v)
        out(f"  - {field}: {sorted([str(v) for v in vals], key=lambda x: (x is None, x))}")

    # ── 8. Cek field yang isinya list of dict (struktur nested) ───────
    out("\n[8] FIELD BERBENTUK LIST/DICT (struktur nested, perlu contoh detail)")
    sample = random.choice(data)
    for k, v in sample.items():
        if isinstance(v, (list, dict)):
            out(f"  - {k}: contoh isinya -> {json.dumps(v, ensure_ascii=False)[:200]}")

    # ── Simpan ke file ──────────────────────────────────────────────
    OUT_PATH.write_text("\n".join(lines), encoding="utf-8")
    out(f"\n{'=' * 70}")
    out(f"✓ Laporan lengkap disimpan ke: {OUT_PATH.resolve()}")
    out("  Tinggal buka file itu, copy-paste seluruh isinya ke chat.")


if __name__ == "__main__":
    main()

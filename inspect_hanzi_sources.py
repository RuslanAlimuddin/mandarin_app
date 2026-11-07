# -*- coding: utf-8 -*-
"""
inspect_hanzi_sources.py
───────────────────────────
Skrip intip (baca saja, tidak mengubah apa pun) untuk 2 file:

  1. data/dictionary.txt      — diduga sumber Make Me a Hanzi mentah
  2. data/hanzi_writer_data.json — sudah dipakai fitur animasi stroke-order

Tujuannya: memastikan skema PERSIS kedua file ini sebelum saya tulis
script pembangun field struktural (radical, radical_number, stroke_count,
structure, components, bopomofo, char_type) untuk 470 entri leksikon
khusus yang baru.

CARA PAKAI:
    cd C:\\mandarin_app
    python inspect_hanzi_sources.py

Output: dicetak ke layar + disimpan ke hanzi_sources_report.txt
"""

import json
import os

DICT_PATH   = os.path.join("data", "dictionary.txt")
WRITER_PATH = os.path.join("data", "hanzi_writer_data.json")
APP_WORDS   = os.path.join("data", "app_words.json")

# Beberapa karakter yang PASTI ada di app_words.json (dipakai sebagai
# contoh silang -- termasuk 1 karakter yang sudah kita lihat contohnya
# di schema_report.txt sebelumnya: 肺)
PROBE_CHARS = ["肺", "无", "法", "好", "爱", "啊"]


def out(lines, s=""):
    print(s)
    lines.append(s)


def inspect_dictionary_txt(lines):
    out(lines, "=" * 70)
    out(lines, f"[A] {DICT_PATH}")
    out(lines, "=" * 70)

    if not os.path.isfile(DICT_PATH):
        out(lines, "  ⚠ FILE TIDAK DITEMUKAN.")
        return

    size_mb = os.path.getsize(DICT_PATH) / 1024 / 1024
    out(lines, f"  Ukuran file: {size_mb:.2f} MB")

    with open(DICT_PATH, "r", encoding="utf-8") as f:
        first_lines = [f.readline() for _ in range(3)]
        f.seek(0)
        total_lines = sum(1 for _ in f)

    out(lines, f"  Total baris: {total_lines:,}")
    out(lines, "\n  3 baris pertama (mentah, apa adanya):")
    for i, line in enumerate(first_lines, 1):
        out(lines, f"    baris {i}: {line.strip()[:300]}")

    # Coba parse sebagai JSON-per-baris (format khas Make Me a Hanzi)
    out(lines, "\n  Percobaan parse sebagai JSON-per-baris:")
    try:
        with open(DICT_PATH, "r", encoding="utf-8") as f:
            sample_objs = []
            for i, line in enumerate(f):
                line = line.strip()
                if not line:
                    continue
                obj = json.loads(line)
                sample_objs.append(obj)
                if len(sample_objs) >= 3:
                    break
        out(lines, "  ✓ BERHASIL di-parse sebagai JSON-per-baris.")
        out(lines, "\n  Semua field yang muncul di 3 baris pertama:")
        all_keys = set()
        for o in sample_objs:
            all_keys.update(o.keys())
        out(lines, f"    {sorted(all_keys)}")
        out(lines, "\n  Contoh 1 objek lengkap:")
        out(lines, "    " + json.dumps(sample_objs[0], ensure_ascii=False, indent=2).replace("\n", "\n    "))
    except Exception as e:
        out(lines, f"  ✗ GAGAL parse JSON-per-baris: {e}")
        out(lines, "  (mungkin formatnya beda -- lihat 3 baris mentah di atas)")

    # Cari langsung karakter probe di file (cari baris yang match)
    out(lines, "\n  Mencari karakter contoh (肺/无/法/好/爱/啊) di file:")
    try:
        with open(DICT_PATH, "r", encoding="utf-8") as f:
            found = {c: None for c in PROBE_CHARS}
            for line in f:
                line_s = line.strip()
                if not line_s:
                    continue
                try:
                    obj = json.loads(line_s)
                except Exception:
                    continue
                char = obj.get("character") or obj.get("char") or obj.get("simplified")
                if char in found and found[char] is None:
                    found[char] = obj
                if all(v is not None for v in found.values()):
                    break
        for c, obj in found.items():
            if obj:
                out(lines, f"\n  Ketemu '{c}':")
                out(lines, "    " + json.dumps(obj, ensure_ascii=False, indent=2).replace("\n", "\n    "))
            else:
                out(lines, f"\n  '{c}' TIDAK ketemu di file ini.")
    except Exception as e:
        out(lines, f"  (gagal mencari karakter probe: {e})")


def inspect_hanzi_writer(lines):
    out(lines, "\n" + "=" * 70)
    out(lines, f"[B] {WRITER_PATH}")
    out(lines, "=" * 70)

    if not os.path.isfile(WRITER_PATH):
        out(lines, "  ⚠ FILE TIDAK DITEMUKAN.")
        return

    size_mb = os.path.getsize(WRITER_PATH) / 1024 / 1024
    out(lines, f"  Ukuran file: {size_mb:.2f} MB")

    with open(WRITER_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    out(lines, f"  Tipe data top-level: {type(data).__name__}")
    if isinstance(data, dict):
        out(lines, f"  Jumlah key (karakter): {len(data):,}")
        sample_keys = list(data.keys())[:5]
        out(lines, f"  Contoh 5 key pertama: {sample_keys}")
        out(lines, "\n  Isi 1 entri contoh (key pertama):")
        first_key = sample_keys[0]
        val = data[first_key]
        val_str = json.dumps(val, ensure_ascii=False)
        out(lines, f"    key='{first_key}' -> {val_str[:500]}{'...' if len(val_str) > 500 else ''}")

        out(lines, "\n  Cek karakter probe (肺/无/法/好/爱/啊):")
        for c in PROBE_CHARS:
            present = c in data
            out(lines, f"    '{c}': {'ADA' if present else 'tidak ada'}")
            if present:
                v = data[c]
                # kalau value berupa dict, tampilkan keys-nya saja (biar ringkas)
                if isinstance(v, dict):
                    out(lines, f"      keys: {sorted(v.keys())}")
                elif isinstance(v, list):
                    out(lines, f"      (list, panjang={len(v)}) contoh awal: {json.dumps(v[0], ensure_ascii=False)[:200] if v else '(kosong)'}")
    elif isinstance(data, list):
        out(lines, f"  Jumlah entri (list): {len(data):,}")
        out(lines, f"  Contoh entri pertama: {json.dumps(data[0], ensure_ascii=False)[:500]}")


def cross_check_app_words(lines):
    out(lines, "\n" + "=" * 70)
    out(lines, "[C] CROSS-CHECK ke app_words.json (field struktural karakter '好')")
    out(lines, "=" * 70)
    if not os.path.isfile(APP_WORDS):
        out(lines, "  ⚠ app_words.json tidak ditemukan di lokasi ini.")
        return
    with open(APP_WORDS, "r", encoding="utf-8") as f:
        data = json.load(f)
    hit = next((w for w in data if (w.get("simplified") or w.get("id")) == "好" and len(w.get("simplified","")) == 1), None)
    if hit:
        out(lines, "  Entri '好' di app_words.json (field struktural saja):")
        for k in ["radical", "radical_number", "stroke_count", "structure", "components", "char_type", "bopomofo"]:
            out(lines, f"    {k}: {hit.get(k)!r}")
        out(lines, "\n  (Bandingkan angka/nilai ini dengan hasil [A] dan [B] di atas untuk '好' -- ")
        out(lines, "   kalau cocok persis, berarti itu sumbernya.)")
    else:
        out(lines, "  Entri '好' 1-karakter tidak ditemukan.")


def main():
    lines = []
    inspect_dictionary_txt(lines)
    inspect_hanzi_writer(lines)
    cross_check_app_words(lines)

    with open("hanzi_sources_report.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"\n✓ Laporan lengkap disimpan ke hanzi_sources_report.txt")


if __name__ == "__main__":
    main()

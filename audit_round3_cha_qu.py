"""
audit_round3_cha_qu.py
-----------------------
Audit round 3: 差 (cha4/cha1/chai1/ci1) dan 曲 (qu1/qu3)

BEDA dari audit round 1/2: karakter ini BUKAN kasus "bacaan langka salah
jadi default" -- keduanya genuinely ambigu, bacaan yang benar tergantung
makna/konteks kata majemuk. Tujuan script ini BUKAN mendeteksi bug, tapi
memetakan semua kata majemuk + bacaan saat ini, supaya bisa direview
manual satu-satu: apakah bacaan yang tersimpan sudah tepat untuk makna
kata tsb.

Referensi bacaan (untuk bantu review manual, BUKAN ground truth mutlak --
tetap cross-check kamus otoritatif kalau ragu):

差 (chà)  - buruk, kurang baik, hampir (mis. 差劲, 差不多, 差点)
差 (chā)  - selisih, perbedaan, beda (mis. 差异, 差距, 误差, 差别)
差 (chāi) - tugas, utusan, kirim (mis. 出差, 差事, 邮差)
差 (cī)   - jarang dipakai kecuali 参差 (cēn cī, tidak rata/berjajar tak rapi)

曲 (qū)  - bengkok, melengkung, tidak lurus/jujur; wilayah (mis. 弯曲,
           曲线, 曲折, 是非曲直)
曲 (qǔ)  - lagu, melodi, musik (mis. 歌曲, 曲子, 戏曲, 作曲)

Cara pakai: taruh di C:\\mandarin_app\\, jalankan `python audit_round3_cha_qu.py`
READ-ONLY.
"""

import json
import sys
from pathlib import Path

TARGET_CHARS = ["差", "曲"]

DATA_DIR = Path("data")
APP_WORDS = DATA_DIR / "app_words.json"
GRADED_READERS = DATA_DIR / "graded_readers.json"


def load_json(path):
    if not path.exists():
        print(f"[!] File tidak ditemukan: {path}")
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def get_hanzi(entry):
    return entry.get("simplified") or entry.get("hanzi") or entry.get("word") or entry.get("id") or ""


def get_meaning(entry):
    m = entry.get("meanings_id") or entry.get("arti") or entry.get("meaning") or entry.get("gloss")
    if isinstance(m, list):
        return "; ".join(m[:2]) + (" ..." if len(m) > 2 else "")
    return m or "?"


def get_all_items(app_words_data):
    if isinstance(app_words_data, list):
        return app_words_data
    if isinstance(app_words_data, dict):
        vals = list(app_words_data.values())
        if vals and isinstance(vals[0], dict) and ("simplified" in vals[0] or "hanzi" in vals[0]):
            return vals
        flat = []
        for v in vals:
            if isinstance(v, list):
                flat.extend(v)
        if flat:
            return flat
    return []


def syllable_at_position(pinyin_str, hanzi_str, target_char):
    idx = hanzi_str.find(target_char)
    if idx == -1:
        return None
    syllables = pinyin_str.split()
    if len(syllables) == len(hanzi_str):
        return syllables[idx]
    return None


def flatten_readers(data):
    results = []
    if isinstance(data, dict):
        if "glossary" in data:
            results.append(data)
        else:
            for v in data.values():
                results.extend(flatten_readers(v))
    elif isinstance(data, list):
        for item in data:
            results.extend(flatten_readers(item))
    return results


def main():
    print("=" * 78)
    print("AUDIT ROUND 3 — Pemetaan 差 dan 曲 (BUKAN deteksi bug, tapi review manual)")
    print("=" * 78)

    app_words = load_json(APP_WORDS)
    if app_words is None:
        sys.exit(1)
    items = get_all_items(app_words)
    print(f"[info] Total entri terbaca: {len(items)}")

    for c in TARGET_CHARS:
        matches = [e for e in items if c in get_hanzi(e)]
        print(f"\n{'='*78}")
        print(f"KARAKTER: {c}  —  {len(matches)} entri mengandung karakter ini")
        print("=" * 78)

        for e in matches:
            hanzi = get_hanzi(e)
            pinyin = e.get("pinyin", "?")
            meaning = get_meaning(e)
            hsk = e.get("hsk", "?")
            syll = syllable_at_position(pinyin, hanzi, c) or "(posisi tak sejajar)"
            tag = "[TUNGGAL]" if hanzi == c else "[MAJEMUK]"
            print(f"  {tag} {hanzi:10s} {pinyin:18s} [{syll:8s}] HSK{hsk!s:4s} {meaning}")

    # Cross-check ke graded_readers.json
    print(f"\n{'='*78}")
    print("Cross-check ke graded_readers.json (glossary)")
    print("=" * 78)
    gr = load_json(GRADED_READERS)
    if gr is not None:
        readers = flatten_readers(gr)
        for c in TARGET_CHARS:
            print(f"\n--- '{c}' di glossary ---")
            count = 0
            for reader in readers:
                title = reader.get("judul") or reader.get("title") or reader.get("id") or "(tanpa judul)"
                for g in reader.get("glossary", []):
                    gword = g.get("cn") or g.get("hanzi") or g.get("word") or ""
                    if c in gword:
                        count += 1
                        gp = g.get("py") or g.get("pinyin") or "?"
                        gid = g.get("id") or g.get("arti") or ""
                        print(f"    [{title}] {gword}  {gp}  -- {gid}")
            if count == 0:
                print("    (tidak ditemukan)")
    else:
        print("[!] graded_readers.json gagal dibaca.")

    print("\nSelesai. Script ini read-only. Review manual daftar di atas terhadap")
    print("referensi bacaan di docstring script ini, lalu putuskan mana yg perlu fix.")


if __name__ == "__main__":
    main()

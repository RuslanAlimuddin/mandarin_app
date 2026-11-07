"""
qa_round2_check_v2.py
----------------------
QA helper v2 untuk 4 karakter round 2: 落(luo4) 圈(quan1) 藏(cang2) 结(jie2)

Perbaikan dari v1:
- Field arti sekarang pakai "meanings_id" (bukan "arti"/"meaning"/"gloss")
- Pemisahan karakter tunggal vs kata majemuk konsisten pakai get_hanzi()
- Pembanding pinyin sekarang berbasis POSISI SUKU KATA + bandingkan langsung
  dgn ejaan diakritik (bukan numerik), jadi tidak lagi salah flag gara-gara
  "luò" vs "luo"
- Parser graded_readers.json sekarang rekursif -- otomatis cari objek yang
  punya key "glossary" di kedalaman berapa pun, tidak asumsi struktur top-level

READ-ONLY. Tidak mengubah file apapun.
"""

import json
import sys
from pathlib import Path

# char -> (bacaan_baru_diakritik, [daftar bacaan lama yang MASIH VALID di kata majemuk tertentu])
TARGET_CHARS = {
    "落": {"new": "luò", "known_alt": ["là"]},
    "圈": {"new": "quān", "known_alt": ["juān"]},
    "藏": {"new": "cáng", "known_alt": ["zàng"]},
    "结": {"new": "jié", "known_alt": ["jiē"]},
}

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
        # bisa jadi dict-of-entries ATAU dict berisi list di dalamnya
        vals = list(app_words_data.values())
        if vals and isinstance(vals[0], dict) and ("simplified" in vals[0] or "hanzi" in vals[0]):
            return vals
        # coba flatten satu level lagi
        flat = []
        for v in vals:
            if isinstance(v, list):
                flat.extend(v)
        if flat:
            return flat
    return []


def syllable_at_position(pinyin_str, hanzi_str, target_char):
    """Cari suku kata pinyin yg sejajar posisi dengan target_char di hanzi_str,
    dengan asumsi jumlah suku kata (dipisah spasi) = jumlah karakter hanzi.
    Kalau tidak sejajar (mis. erhua, idiom 4-char kadang beda), return None
    dan caller akan fallback ke cek 'apakah muncul di manapun'."""
    idx = hanzi_str.find(target_char)
    if idx == -1:
        return None
    syllables = pinyin_str.split()
    if len(syllables) == len(hanzi_str):
        return syllables[idx]
    return None  # tidak sejajar, fallback ke caller


def classify_entry(entry, target_char, info):
    hanzi = get_hanzi(entry)
    pinyin = entry.get("pinyin", "")
    new_reading = info["new"]
    known_alt = info["known_alt"]

    syll = syllable_at_position(pinyin, hanzi, target_char)
    if syll is not None:
        if syll == new_reading:
            return "OK (bacaan baru)", syll
        elif syll in known_alt:
            return "OK (bacaan alternatif dikenal, sah dlm konteks ini)", syll
        else:
            return "PERLU CEK (bacaan tak dikenal)", syll
    else:
        # fallback: cek keberadaan string saja
        if new_reading in pinyin:
            return "OK (bacaan baru, posisi tak terverifikasi)", pinyin
        elif any(alt in pinyin for alt in known_alt):
            return "OK (bacaan alternatif, posisi tak terverifikasi)", pinyin
        else:
            return "PERLU CEK (posisi tak terverifikasi & bacaan tak cocok)", pinyin


def print_entry(entry, status, syll):
    hanzi = get_hanzi(entry)
    pinyin = entry.get("pinyin", "?")
    meaning = get_meaning(entry)
    flag = "  <-- " + status if status.startswith("PERLU CEK") else ""
    print(f"    {hanzi:8s} {pinyin:18s} [{syll:10s}] {meaning}{flag}")


def scan_app_words(items):
    hits = {c: [] for c in TARGET_CHARS}
    for entry in items:
        hanzi = get_hanzi(entry)
        for c in TARGET_CHARS:
            if c in hanzi:
                hits[c].append(entry)
    return hits


def flatten_readers(data):
    """Rekursif cari semua dict yang punya key 'glossary' di kedalaman berapa pun."""
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
    print("QA ROUND 2 v2 — Cek 落/圈/藏/结 di app_words.json")
    print("=" * 78)

    app_words = load_json(APP_WORDS)
    if app_words is None:
        sys.exit(1)

    items = get_all_items(app_words)
    print(f"[info] Total entri terbaca dari app_words.json: {len(items)}")
    if len(items) == 0:
        print("[!] Tidak ada entri terbaca -- struktur app_words.json beda dari asumsi.")
        print("    Kirim contoh struktur top-level (cukup json.load lalu type(data) & list(data.keys())[:5]).")
        sys.exit(1)

    hits = scan_app_words(items)

    grand_flagged = []

    for c, info in TARGET_CHARS.items():
        entries = hits[c]
        single_char = [e for e in entries if get_hanzi(e) == c]
        compounds = [e for e in entries if get_hanzi(e) != c]

        print(f"\n--- {c} (bacaan baru: {info['new']}, alt dikenal: {info['known_alt']}) "
              f"— {len(entries)} entri ---")

        print(f"  [Karakter tunggal] ({len(single_char)}):")
        for e in single_char:
            status, syll = classify_entry(e, c, info)
            print_entry(e, status, syll)
            if status.startswith("PERLU CEK"):
                grand_flagged.append((c, e, status))

        print(f"  [Kata majemuk] ({len(compounds)}):")
        for e in compounds:
            status, syll = classify_entry(e, c, info)
            print_entry(e, status, syll)
            if status.startswith("PERLU CEK"):
                grand_flagged.append((c, e, status))

    print("\n" + "=" * 78)
    if grand_flagged:
        print(f"⚠️  RINGKASAN: {len(grand_flagged)} entri benar-benar PERLU DICEK MANUAL:")
        for c, e, status in grand_flagged:
            print(f"   [{c}] {get_hanzi(e)}  ({entries_pinyin(e)})  -- {status}")
    else:
        print("✅ RINGKASAN: Tidak ada entri yang perlu dicek manual lebih lanjut.")
        print("   Semua kata majemuk pakai bacaan baru ATAU bacaan alternatif yang sudah dikenal/sah.")

    # Cross-check ke graded_readers.json
    print("\n" + "=" * 78)
    print("Cross-check ke graded_readers.json (glossary)")
    print("=" * 78)
    gr = load_json(GRADED_READERS)
    if gr is not None:
        readers = flatten_readers(gr)
        print(f"[info] Total objek dgn glossary ditemukan: {len(readers)}")
        for c, info in TARGET_CHARS.items():
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

    print("\nSelesai. Script ini read-only, tidak ada file yang diubah.")


def entries_pinyin(e):
    return e.get("pinyin", "?")


if __name__ == "__main__":
    main()

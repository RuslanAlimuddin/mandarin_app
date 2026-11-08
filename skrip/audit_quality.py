#!/usr/bin/env python3
"""
audit_quality.py — Mandarin Interaktif: audit kualitas nuance_pairs.json
=============================================================================
Dijalankan sekali untuk mengecek 1295+ pasangan nuance_pairs.json.

Cara pakai (dari folder C:\\mandarin_app\\):
    python audit_quality.py

Script ini melakukan 2 hal:

  A) PEMERIKSAAN OTOMATIS (heuristik) -- menandai pasangan yang kemungkinan
     bermasalah secara struktural, TANPA perlu saya baca satu-satu:
       - core_distinction_id terlalu pendek/kosong
       - common_mistake_id kosong atau tidak berformat "❌ ... seharusnya:"
       - example_cn TIDAK mengandung kata yang sedang dijelaskan (mismatch)
       - pinyin tanpa tanda nada sama sekali (kemungkinan belum dikoreksi)
       - collocations kurang dari 2 (terlalu sedikit)
       - example_cn yang PERSIS SAMA dipakai berulang di banyak pasangan
         (indikasi AI mengarang generik / malas)
       - words ada duplikat dalam satu pasangan
     Hasilnya disimpan ke audit_report.txt (dibaca sendiri) DAN
     audit_flagged.json (baris-baris yang kena tandai, bisa dikirim ke saya
     kalau mau saya tinjau lebih lanjut).

  B) SAMPEL ACAK -- mengambil 40 pasangan acak (dari seluruh 1295+, bukan cuma
     yang ditandai) dan menyimpannya ke audit_sample_40.json. File ini yang
     رسلان kirim balik ke saya di chat supaya saya baca isinya langsung dan
     nilai kualitas linguistiknya (bukan cuma struktur).
"""
import json
import random
import re
from pathlib import Path
from collections import Counter

NUANCE_PATH = Path("data/nuance_pairs.json")
SAMPLE_SIZE = 40
RANDOM_SEED = 42  # supaya hasil sampel bisa direproduksi kalau dijalankan ulang

TONE_MARKS = "āáǎàēéěèīíǐìōóǒòūúǔùǖǘǚǜü"


def load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def has_tone_mark(pinyin):
    return any(ch in TONE_MARKS for ch in pinyin)


def main():
    if not NUANCE_PATH.exists():
        print(f"[GAGAL] {NUANCE_PATH} tidak ditemukan.")
        return

    data = load_json(NUANCE_PATH)
    pairs = data.get("pairs", [])
    print(f"Total pasangan: {len(pairs)}")

    flagged = []
    example_cn_counter = Counter()
    for p in pairs:
        for c in p.get("comparison", []):
            ex = c.get("example_cn", "")
            if ex:
                example_cn_counter[ex] += 1

    for p in pairs:
        reasons = []       # masalah nyata
        style_notes = []   # kosmetik, bukan masalah
        pid = p.get("id", "?")
        words = p.get("words", [])

        if len(words) != len(set(words)):
            reasons.append("kata duplikat dalam 'words'")

        cd = p.get("core_distinction_id", "") or ""
        if len(cd.strip()) < 10:
            reasons.append("core_distinction_id terlalu pendek/kosong")

        cm = p.get("common_mistake_id", "") or ""
        if not cm.strip():
            reasons.append("common_mistake_id kosong")
        elif "❌" not in cm:
            style_notes.append("common_mistake_id gaya lama (tidak pakai format '❌ ... seharusnya:')")

        for c in p.get("comparison", []):
            word = c.get("word", "")
            pinyin = c.get("pinyin", "") or ""
            ex_cn = c.get("example_cn", "") or ""
            colloc = c.get("collocations", []) or []

            if pinyin and not has_tone_mark(pinyin) and not re.search(r'\d', pinyin):
                reasons.append(f"pinyin '{word}' tanpa tanda nada ('{pinyin}')")

            if ex_cn and word not in ex_cn:
                reasons.append(f"example_cn tidak mengandung kata '{word}'")

            if len(colloc) < 2:
                style_notes.append(f"collocations '{word}' cuma {len(colloc)} (idealnya 3+)")

            if ex_cn and example_cn_counter.get(ex_cn, 0) >= 5:
                reasons.append(f"example_cn dipakai berulang {example_cn_counter[ex_cn]}x lintas pasangan lain: \"{ex_cn}\"")

        if reasons or style_notes:
            flagged.append({"id": pid, "words": words, "reasons": reasons, "style_notes": style_notes})

    real_issues = [f for f in flagged if f["reasons"]]
    style_only = [f for f in flagged if not f["reasons"] and f["style_notes"]]

    # --- Simpan laporan ---
    with open("audit_report.txt", "w", encoding="utf-8") as f:
        f.write(f"AUDIT KUALITAS nuance_pairs.json\n")
        f.write(f"Total pasangan: {len(pairs)}\n")
        f.write(f"MASALAH NYATA (perlu dicek): {len(real_issues)} ({len(real_issues)*100//max(len(pairs),1)}%)\n")
        f.write(f"Cuma catatan gaya kosmetik: {len(style_only)} ({len(style_only)*100//max(len(pairs),1)}%)\n\n")
        f.write("=" * 60 + "\n")
        f.write("BAGIAN 1: MASALAH NYATA\n")
        f.write("=" * 60 + "\n\n")
        for item in real_issues:
            f.write(f"[{item['id']}] {' / '.join(item['words'])}\n")
            for r in item["reasons"]:
                f.write(f"    - {r}\n")
            f.write("\n")
        f.write("=" * 60 + "\n")
        f.write("BAGIAN 2: CATATAN GAYA KOSMETIK SAJA (opsional dibaca)\n")
        f.write("=" * 60 + "\n\n")
        for item in style_only:
            f.write(f"[{item['id']}] {' / '.join(item['words'])}\n")
            for r in item["style_notes"]:
                f.write(f"    - {r}\n")
            f.write("\n")

    with open("audit_flagged.json", "w", encoding="utf-8") as f:
        json.dump({"real_issues": real_issues, "style_only": style_only}, f, ensure_ascii=False, indent=2)

    print(f"MASALAH NYATA: {len(real_issues)} dari {len(pairs)} ({len(real_issues)*100//max(len(pairs),1)}%)")
    print(f"Catatan gaya kosmetik saja: {len(style_only)} ({len(style_only)*100//max(len(pairs),1)}%)")
    print("-> Detail lengkap: audit_report.txt")
    print("-> Versi JSON: audit_flagged.json")

    # --- Sampel acak untuk saya tinjau manual ---
    random.seed(RANDOM_SEED)
    sample = random.sample(pairs, min(SAMPLE_SIZE, len(pairs)))
    with open("audit_sample_40.json", "w", encoding="utf-8") as f:
        json.dump(sample, f, ensure_ascii=False, indent=2)
    print(f"\nSampel acak {len(sample)} pasangan disimpan ke audit_sample_40.json")
    print("-> Kirim file ini ke saya di chat untuk ditinjau kualitas linguistiknya.")


if __name__ == "__main__":
    main()

"""
audit_kata_majemuk_pola.py
=============================
QA read-only untuk kata_majemuk_pola.json (hasil klasifikasi AI eksternal).
Tidak mengubah data apa pun -- cuma baca, hitung, dan laporkan.

Cara pakai:
    python audit_kata_majemuk_pola.py

Yang dicek:
1. Kelengkapan: total terklasifikasi vs total kandidat (harusnya 8867).
2. Duplikat kata (harusnya tidak ada, tapi dicek ulang -- defensive).
3. Distribusi 6 kategori pola -- flag kalau 'lainnya' proporsinya
   mencurigakan tinggi (AI mungkin 'malas' / menghindari klasifikasi
   yang lebih sulit).
4. Kualitas keterangan_id: kosong, terlalu pendek, atau teks yang
   di-copy-paste sama persis berkali-kali (indikasi AI generik/malas).
5. Sanity check: semua kata memang 2 karakter (harus sudah begitu dari
   sumbernya, tapi dicek ulang).
6. Simpan sampel acak per kategori ke file terpisah untuk ditinjau
   manual (oleh رسلان atau Claude).
"""

import json
import os
import random
from collections import Counter, defaultdict

CANDIDATES_PATH = "kata_majemuk_candidates_2char_ALL.json"
CLASSIFIED_PATH = "kata_majemuk_pola.json"
SAMPLE_OUTPUT_PATH = "audit_sample_for_review.json"

VALID_POLA = {"联合式", "偏正式", "动宾式", "主谓式", "补充式", "lainnya"}
SAMPLE_SIZE_PER_POLA = 15
LAINNYA_WARN_THRESHOLD = 0.25   # warning kalau >25% masuk 'lainnya'
SHORT_KETERANGAN_THRESHOLD = 8  # karakter


def load_json(path, default):
    if not os.path.exists(path):
        return default
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def main():
    candidates = load_json(CANDIDATES_PATH, [])
    classified = load_json(CLASSIFIED_PATH, [])

    if not candidates:
        print(f"[ERROR] {CANDIDATES_PATH} tidak ditemukan/kosong.")
        return
    if not classified:
        print(f"[ERROR] {CLASSIFIED_PATH} tidak ditemukan/kosong.")
        return

    total_candidates = len(candidates)
    total_classified = len(classified)
    candidate_words = set(c["word"] for c in candidates)

    print("=" * 60)
    print("1. KELENGKAPAN")
    print("=" * 60)
    print(f"Total kandidat asli   : {total_candidates}")
    print(f"Total terklasifikasi  : {total_classified}")
    missing = candidate_words - set(item["word"] for item in classified)
    if missing:
        print(f"[!] Masih ada {len(missing)} kata BELUM diklasifikasi.")
        print(f"    Jalankan prepare_next_chunk.py lagi. Contoh: {list(missing)[:10]}")
    else:
        print("[OK] Semua kandidat sudah terklasifikasi.")

    print()
    print("=" * 60)
    print("2. DUPLIKAT KATA")
    print("=" * 60)
    word_counts = Counter(item["word"] for item in classified)
    dupes = {w: c for w, c in word_counts.items() if c > 1}
    if dupes:
        print(f"[!] {len(dupes)} kata muncul lebih dari 1 kali (SEHARUSNYA TIDAK ADA):")
        for w, c in list(dupes.items())[:20]:
            print(f"    {w}: {c}x")
    else:
        print("[OK] Tidak ada duplikat kata.")

    print()
    print("=" * 60)
    print("3. DISTRIBUSI KATEGORI POLA")
    print("=" * 60)
    pola_counts = Counter(item["pola"] for item in classified)
    invalid_pola = [item for item in classified if item["pola"] not in VALID_POLA]
    for pola in ["联合式", "偏正式", "动宾式", "主谓式", "补充式", "lainnya"]:
        cnt = pola_counts.get(pola, 0)
        pct = (cnt / total_classified * 100) if total_classified else 0
        print(f"  {pola:8s}: {cnt:5d}  ({pct:.1f}%)")
    if invalid_pola:
        print(f"[!] {len(invalid_pola)} entri punya nilai 'pola' TIDAK VALID (lolos dari import script?!):")
        for item in invalid_pola[:10]:
            print(f"    {item['word']}: '{item['pola']}'")

    lainnya_pct = pola_counts.get("lainnya", 0) / total_classified if total_classified else 0
    if lainnya_pct > LAINNYA_WARN_THRESHOLD:
        print(f"\n[PERHATIAN] Kategori 'lainnya' {lainnya_pct*100:.1f}% dari total -- "
              f"di atas ambang {LAINNYA_WARN_THRESHOLD*100:.0f}%.")
        print("  Kemungkinan AI eksternal terlalu sering 'menghindar' ke kategori ini.")
        print("  Sebaiknya tinjau sampel 'lainnya' di file audit_sample_for_review.json.")

    print()
    print("=" * 60)
    print("4. KUALITAS keterangan_id")
    print("=" * 60)
    empty_keterangan = [i for i in classified if not i.get("keterangan_id", "").strip()]
    short_keterangan = [
        i for i in classified
        if i.get("keterangan_id", "").strip()
        and len(i["keterangan_id"].strip()) < SHORT_KETERANGAN_THRESHOLD
    ]
    print(f"keterangan_id kosong        : {len(empty_keterangan)}")
    print(f"keterangan_id sangat pendek (<{SHORT_KETERANGAN_THRESHOLD} char): {len(short_keterangan)}")
    if empty_keterangan:
        print(f"  Contoh kosong: {[i['word'] for i in empty_keterangan[:10]]}")
    if short_keterangan:
        print(f"  Contoh pendek: {[(i['word'], i['keterangan_id']) for i in short_keterangan[:10]]}")

    # deteksi keterangan_id yang di-copy-paste identik berkali-kali (bukan salah,
    # tapi kalau 1 kalimat generik dipakai utk ratusan kata beda, patut dicurigai)
    keterangan_counts = Counter(i.get("keterangan_id", "").strip() for i in classified)
    overused = {k: c for k, c in keterangan_counts.items() if c >= 10 and k}
    if overused:
        print(f"\n[PERHATIAN] {len(overused)} kalimat keterangan_id dipakai identik >=10 kali "
              "(kemungkinan generik/copy-paste):")
        for k, c in sorted(overused.items(), key=lambda x: -x[1])[:10]:
            preview = k if len(k) <= 70 else k[:70] + "..."
            print(f"    ({c}x) {preview}")

    print()
    print("=" * 60)
    print("5. SANITY CHECK PANJANG KATA")
    print("=" * 60)
    wrong_length = [i for i in classified if len(i["word"]) != 2]
    if wrong_length:
        print(f"[!] {len(wrong_length)} entri BUKAN 2 karakter (seharusnya mustahil):")
        for i in wrong_length[:10]:
            print(f"    {i['word']} ({len(i['word'])} karakter)")
    else:
        print("[OK] Semua entri 2 karakter.")

    print()
    print("=" * 60)
    print("6. SAMPEL UNTUK TINJAUAN MANUAL")
    print("=" * 60)
    by_pola = defaultdict(list)
    for item in classified:
        by_pola[item["pola"]].append(item)

    sample_output = {}
    random.seed(42)  # supaya sampel konsisten kalau dijalankan ulang
    for pola, items in by_pola.items():
        n = min(SAMPLE_SIZE_PER_POLA, len(items))
        sample_output[pola] = random.sample(items, n)

    with open(SAMPLE_OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(sample_output, f, ensure_ascii=False, indent=2)

    total_sampled = sum(len(v) for v in sample_output.values())
    print(f"{total_sampled} entri sampel ({SAMPLE_SIZE_PER_POLA} per kategori, kalau tersedia)")
    print(f"disimpan ke: {SAMPLE_OUTPUT_PATH}")
    print("Kirim file ini ke Claude untuk ditinjau kualitas linguistiknya,")
    print("atau baca sendiri sekilas untuk spot-check.")

    print()
    print("=" * 60)
    print("RINGKASAN")
    print("=" * 60)
    issues = []
    if missing:
        issues.append(f"{len(missing)} kata belum diklasifikasi")
    if dupes:
        issues.append(f"{len(dupes)} kata duplikat")
    if invalid_pola:
        issues.append(f"{len(invalid_pola)} pola tidak valid")
    if lainnya_pct > LAINNYA_WARN_THRESHOLD:
        issues.append(f"'lainnya' {lainnya_pct*100:.1f}% (tinggi)")
    if empty_keterangan:
        issues.append(f"{len(empty_keterangan)} keterangan kosong")
    if overused:
        issues.append(f"{len(overused)} kalimat keterangan generik/overused")
    if wrong_length:
        issues.append(f"{len(wrong_length)} kata bukan 2-karakter")

    if issues:
        print("Ditemukan hal yang perlu ditinjau:")
        for x in issues:
            print(f"  - {x}")
    else:
        print("Tidak ada masalah struktural terdeteksi. Tetap disarankan tinjau")
        print(f"sampel di {SAMPLE_OUTPUT_PATH} untuk kualitas linguistik.")


if __name__ == "__main__":
    main()

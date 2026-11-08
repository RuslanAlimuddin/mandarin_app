#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
intip_polisemi.py — Mandarin Interaktif
Script investigasi READ-ONLY untuk sesi diskusi "Struktur Detail Kata
Polisemi" (lihat BLUEPRINT). TIDAK mengubah file apa pun — cuma membaca
& melaporkan. Aman dijalankan kapan saja.

CARA PAKAI:
  1. Taruh file ini di folder root C:\\mandarin_app\\ (sejajar dgn folder data\\)
  2. Jalankan:  python intip_polisemi.py
  3. Baca ringkasan di terminal, LALU upload file "polisemi_report.json"
     (otomatis dibuat di folder yang sama) ke sesi Claude berikutnya
     untuk lanjut diskusi & menyusun rencana kerja di BLUEPRINT.

YANG DICEK:
  A. data/app_words.json
     - Distribusi jumlah makna (meanings_id) per entri.
     - Sampel acak kata dgn >=3 makna (kandidat polisemi, dinilai manual:
       apakah beneran makna beda konteks, atau cuma sinonim berulang).
     - Kata dgn variasi pos_id lebih dari 1 jenis (sinyal tambahan
       polisemi lintas kelas kata, mis. bisa jadi Kata Kerja & Kata Benda).
     - Homograf: hanzi SAMA tapi ENTRI TERPISAH (kasus 土 seperti yg
       رسلان temukan) — beda dari "1 entri banyak makna".
  B. data/cidict_index.json (kalau ada & ukurannya wajar dimuat)
     - Sama seperti A, sbg pembanding: apakah Cidict py struktur makna
       lebih detail dari app_words.json?
  C. data/cidict_ts.u8 (kalau ada, format teks mentah CC-CEDICT)
     - Parsing kasar format "Trad Simp [pinyin] /gloss1/gloss2/.../"
     - Hitung jumlah gloss per baris (indikasi polisemi) & jumlah baris
       per hanzi (indikasi homograf/multi-bacaan).
"""
import json
import os
import random
import re
from collections import Counter

random.seed(42)  # sampel konsisten kalau dijalankan ulang

DATA_DIR  = "data"
OUT_PATH  = "polisemi_report.json"
SAMPLE_N  = 15
THRESHOLDS = [1, 2, 3, 4, 5, 8]


def load_json_safe(path):
    if not os.path.exists(path):
        return None, f"(tidak ditemukan: {path})"
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f), None
    except Exception as e:
        return None, f"(gagal parse {path}: {e})"


def meanings_len(w):
    m = w.get("meanings_id")
    if isinstance(m, list):
        return len(m)
    if isinstance(m, str) and m.strip():
        return 1
    return 0


def analyze_word_list(data, label):
    print(f"\n{'='*70}\n{label}  ({len(data):,} entri)\n{'='*70}")
    counts = Counter()
    for w in data:
        n = meanings_len(w)
        bucket = n if n < 5 else ("5-7" if n < 8 else "8+")
        counts[bucket] += 1

    print("Distribusi jumlah makna (meanings_id) per entri:")
    for k in sorted(counts.keys(), key=lambda x: (isinstance(x, str), x)):
        pct = counts[k] / len(data) * 100
        print(f"   {str(k):>4} makna : {counts[k]:>6,} entri ({pct:5.1f}%)")

    candidates_by_threshold = {}
    for th in THRESHOLDS:
        matched_n = sum(1 for w in data if meanings_len(w) >= th)
        candidates_by_threshold[th] = matched_n

    print("\nJumlah kata dgn >= N makna (kandidat polisemi berdasar JUMLAH makna):")
    for th, cnt in candidates_by_threshold.items():
        print(f"   >= {th} makna : {cnt:,} kata")

    # Sampel acak kata dgn >=3 makna -- utk dinilai manual: polisemi
    # sungguhan (makna beda konteks) atau cuma sinonim berulang?
    high = [w for w in data if meanings_len(w) >= 3]
    sample = random.sample(high, min(SAMPLE_N, len(high))) if high else []
    print(f"\nSampel acak {len(sample)} kata dgn >=3 makna "
          f"(cek manual: polisemi sungguhan atau bukan?):")
    for w in sample:
        hz = w.get("simplified") or w.get("id") or "?"
        py = w.get("pinyin") or ""
        ms = w.get("meanings_id") or []
        print(f"   {hz} ({py}): " + " | ".join(ms))

    # Sinyal tambahan: variasi pos_id > 1 jenis dlm 1 entri (polisemi
    # lintas kelas kata, mis. KK & KB sekaligus -- biasanya sinyal lebih
    # kuat drpd sekadar banyak sinonim dlm 1 kelas kata yg sama).
    multi_pos = []
    for w in data:
        pos = w.get("pos_id")
        if isinstance(pos, list) and len(set(pos)) > 1:
            multi_pos.append(w)
    print(f"\nKata dgn >1 JENIS pos_id berbeda dlm 1 entri "
          f"(sinyal polisemi lintas kelas kata): {len(multi_pos):,}")
    sample_pos = random.sample(multi_pos, min(SAMPLE_N, len(multi_pos))) if multi_pos else []
    for w in sample_pos:
        hz = w.get("simplified") or w.get("id") or "?"
        print(f"   {hz}: pos_id={w.get('pos_id')}  meanings_id={w.get('meanings_id')}")

    return {
        "total_entri": len(data),
        "distribusi_jumlah_makna": {str(k): v for k, v in counts.items()},
        "kandidat_per_threshold": candidates_by_threshold,
        "sampel_acak_3plus": [
            {"hanzi": w.get("simplified") or w.get("id"), "pinyin": w.get("pinyin"),
             "meanings_id": w.get("meanings_id")}
            for w in sample
        ],
        "jumlah_kata_multi_pos": len(multi_pos),
        "sampel_multi_pos": [
            {"hanzi": w.get("simplified") or w.get("id"), "pos_id": w.get("pos_id"),
             "meanings_id": w.get("meanings_id")}
            for w in sample_pos
        ],
    }


def find_homographs(data, label):
    """Kata dgn `simplified` SAMA tapi ENTRI BEDA (persis kasus 土) --
    kategori terpisah dari 'polisemi 1 entri banyak makna': ini
    'homograf 2+ entri terpisah, hanzi sama'. Ini yg bikin bug klik di
    kamus-detail.js (selectWord mengabaikan idx)."""
    print(f"\n{'='*70}\n{label} — Cek Homograf (hanzi sama, entri BEDA)\n{'='*70}")
    by_hanzi = {}
    for w in data:
        hz = w.get("simplified") or w.get("id")
        if not hz:
            continue
        by_hanzi.setdefault(hz, []).append(w)
    dupes = {hz: ws for hz, ws in by_hanzi.items() if len(ws) > 1}
    print(f"Jumlah hanzi unik yg punya >1 entri terpisah: {len(dupes):,}")
    sample_keys = random.sample(list(dupes.keys()), min(SAMPLE_N, len(dupes))) if dupes else []
    print(f"Sampel acak {len(sample_keys)} kasus homograf:")
    for hz in sample_keys:
        ws = dupes[hz]
        print(f"   {hz}  ({len(ws)} entri terpisah):")
        for w in ws:
            py = w.get("pinyin") or ""
            ms = w.get("meanings_id") or []
            first = ms[0] if ms else ""
            print(f"      - id={w.get('id')!r} pinyin={py!r}  arti#1={first!r}")

    return {
        "jumlah_hanzi_dgn_multi_entri": len(dupes),
        "sampel_acak": {
            hz: [
                {"id": w.get("id"), "pinyin": w.get("pinyin"), "meanings_id": w.get("meanings_id")}
                for w in dupes[hz]
            ]
            for hz in sample_keys
        },
    }


def analyze_cidict_u8(path):
    print(f"\n{'='*70}\nCC-CEDICT mentah: {path}\n{'='*70}")
    if not os.path.exists(path):
        print("(file tidak ditemukan, dilewati)")
        return None

    lines = []
    try:
        with open(path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                lines.append(line)
    except Exception as e:
        print(f"(gagal baca: {e})")
        return None

    print(f"Total baris data: {len(lines):,}")
    print("Contoh 5 baris mentah (utk konfirmasi format):")
    for l in lines[:5]:
        print("   " + l[:150])

    # Format CC-CEDICT umum: Trad Simp [pinyin] /gloss1/gloss2/.../
    pattern = re.compile(r"^(\S+)\s+(\S+)\s+\[([^\]]*)\]\s+/(.*)/$")
    parsed = 0
    gloss_counts = Counter()
    hanzi_line_counts = Counter()
    unparsed_sample = []
    for l in lines:
        m = pattern.match(l)
        if not m:
            if len(unparsed_sample) < 3:
                unparsed_sample.append(l[:150])
            continue
        trad, simp, py, glosses = m.groups()
        parsed += 1
        n_gloss = len([g for g in glosses.split("/") if g.strip()])
        bucket = n_gloss if n_gloss < 8 else "8+"
        gloss_counts[bucket] += 1
        hanzi_line_counts[simp] += 1

    print(f"\nBaris berhasil di-parse format CC-CEDICT standar: {parsed:,} / {len(lines):,}")
    if unparsed_sample:
        print("Contoh baris yg GAGAL di-parse (format file mungkin beda dari dugaan):")
        for u in unparsed_sample:
            print("   " + u)

    print("\nDistribusi jumlah gloss (dipisah '/') per baris:")
    for k in sorted(gloss_counts.keys(), key=lambda x: (isinstance(x, str), x)):
        print(f"   {str(k):>3} gloss : {gloss_counts[k]:>6,} baris")

    multi_line_hanzi = {h: c for h, c in hanzi_line_counts.items() if c > 1}
    print(f"\nJumlah hanzi (simplified) dgn >1 BARIS terpisah di CC-CEDICT "
          f"(indikasi multi-bacaan/homograf): {len(multi_line_hanzi):,}")

    return {
        "total_baris": len(lines),
        "berhasil_parse": parsed,
        "distribusi_jumlah_gloss": {str(k): v for k, v in gloss_counts.items()},
        "jumlah_hanzi_multi_baris": len(multi_line_hanzi),
    }


def main():
    report = {}

    app_words, err = load_json_safe(os.path.join(DATA_DIR, "app_words.json"))
    if app_words is not None:
        report["app_words"] = analyze_word_list(app_words, "app_words.json")
        report["app_words_homograf"] = find_homographs(app_words, "app_words.json")
    else:
        print(f"\n[SKIP] app_words.json: {err}")

    cidict_path = os.path.join(DATA_DIR, "cidict_index.json")
    if os.path.exists(cidict_path):
        size_mb = os.path.getsize(cidict_path) / 1024 / 1024
        print(f"\ncidict_index.json terdeteksi ({size_mb:.1f} MB) — memuat...")
        cidict, err = load_json_safe(cidict_path)
        if cidict is not None:
            report["cidict_index"] = analyze_word_list(cidict, "cidict_index.json")
        else:
            print(f"[SKIP] cidict_index.json: {err}")
    else:
        print(f"\n[SKIP] cidict_index.json tidak ditemukan di {cidict_path}")

    u8_candidates = [os.path.join(DATA_DIR, "cidict_ts.u8"), "cidict_ts.u8"]
    u8_path = next((p for p in u8_candidates if os.path.exists(p)), u8_candidates[0])
    result = analyze_cidict_u8(u8_path)
    if result:
        report["cidict_ts_u8"] = result

    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    print(f"\n{'='*70}")
    print(f"Selesai. Ringkasan lengkap disimpan ke: {OUT_PATH}")
    print("Upload file itu ke sesi Claude berikutnya utk lanjut diskusi & rencana.")
    print(f"{'='*70}")


if __name__ == "__main__":
    main()

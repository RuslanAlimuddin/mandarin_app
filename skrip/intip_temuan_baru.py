#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
intip_temuan_baru.py — Mandarin Interaktif
Diagnostik READ-ONLY (mudah-mudahan yg TERAKHIR) sebelum finalisasi
rencana Tier 1/2/3. Fokus ke 3 file yg namanya sangat relevan tapi
isinya belum pernah dilihat, + sampel entri app_words.json yg SUDAH
punya contoh_kalimat_cn/id/pinyin terisi.

TIDAK mengubah file apa pun.

CARA PAKAI:
  python intip_temuan_baru.py
  -> upload temuan_baru_report.json yg dihasilkan
"""
import json
import os
import random

random.seed(42)
DATA_DIR = "data"
OUT_PATH = "temuan_baru_report.json"
SAMPLE_N = 8


def load_json_safe(path):
    if not os.path.exists(path):
        return None, f"(tidak ditemukan: {path})"
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f), None
    except Exception as e:
        return None, f"(gagal parse {path}: {e})"


def peek_structure(data, label, sample_n=SAMPLE_N):
    """Cetak bentuk struktur data (list vs dict), keys kalau dict, dan
    beberapa sampel isi -- generik, tidak asumsi skema tertentu dulu."""
    print(f"\n{'='*70}\n{label}\n{'='*70}")
    if data is None:
        print("(gagal dimuat / tidak ditemukan)")
        return None

    result = {"type": type(data).__name__}

    if isinstance(data, list):
        print(f"Bentuk: LIST, {len(data):,} item")
        result["length"] = len(data)
        sample = random.sample(data, min(sample_n, len(data))) if data else []
        result["sample"] = sample
        print(f"Sampel {len(sample)} item acak:")
        for item in sample:
            print("   " + json.dumps(item, ensure_ascii=False)[:300])

    elif isinstance(data, dict):
        keys = list(data.keys())
        print(f"Bentuk: DICT/OBJECT, {len(keys):,} key top-level")
        result["top_level_keys_count"] = len(keys)
        result["top_level_keys_sample"] = keys[:20]
        print(f"Contoh 20 key pertama: {keys[:20]}")

        sample_keys = random.sample(keys, min(sample_n, len(keys))) if keys else []
        result["sample"] = {k: data[k] for k in sample_keys}
        print(f"\nSampel {len(sample_keys)} entri acak (key -> value):")
        for k in sample_keys:
            v = data[k]
            v_str = json.dumps(v, ensure_ascii=False)
            if len(v_str) > 300:
                v_str = v_str[:300] + "...(terpotong)"
            print(f"   {k!r}: {v_str}")
    else:
        print(f"Bentuk tak terduga: {type(data)}")
        result["raw_preview"] = str(data)[:500]

    return result


def sample_contoh_kalimat(path=os.path.join(DATA_DIR, "app_words.json")):
    print(f"\n{'='*70}\nSampel entri app_words.json yg SUDAH punya contoh_kalimat\n{'='*70}")
    data, err = load_json_safe(path)
    if data is None:
        print(err)
        return []

    has_contoh = [w for w in data if w.get("contoh_kalimat_cn")]
    print(f"Total entri dgn contoh_kalimat_cn terisi: {len(has_contoh):,}")
    sample = random.sample(has_contoh, min(SAMPLE_N, len(has_contoh))) if has_contoh else []
    result = []
    for w in sample:
        entry = {
            "hanzi": w.get("simplified"),
            "pinyin": w.get("pinyin"),
            "meanings_id": w.get("meanings_id"),
            "contoh_kalimat_cn": w.get("contoh_kalimat_cn"),
            "contoh_kalimat_pinyin": w.get("contoh_kalimat_pinyin"),
            "contoh_kalimat_id": w.get("contoh_kalimat_id"),
            "_source_note": w.get("_source_note"),
        }
        result.append(entry)
        print(f"\n   {entry['hanzi']} ({entry['pinyin']}):")
        print(f"      meanings_id: {entry['meanings_id']}")
        print(f"      contoh_cn  : {entry['contoh_kalimat_cn']}")
        print(f"      contoh_py  : {entry['contoh_kalimat_pinyin']}")
        print(f"      contoh_id  : {entry['contoh_kalimat_id']}")
        if entry["_source_note"]:
            print(f"      _source_note: {entry['_source_note']}")
    return result


def main():
    report = {}

    for fname in ["synonym_antonym.json", "pattern_explanations.json", "confusion_groups.json"]:
        data, err = load_json_safe(os.path.join(DATA_DIR, fname))
        if data is None:
            print(f"\n[SKIP] {fname}: {err}")
            report[fname] = None
        else:
            report[fname] = peek_structure(data, fname)

    report["contoh_kalimat_samples"] = sample_contoh_kalimat()

    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    print(f"\n{'='*70}\nSelesai. Disimpan ke: {OUT_PATH}")
    print("Upload file itu ke sesi Claude berikutnya utk finalisasi rencana.")
    print(f"{'='*70}")


if __name__ == "__main__":
    main()

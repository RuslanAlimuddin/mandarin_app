# -*- coding: utf-8 -*-
"""
analisis_produktivitas.py

Menghitung "produktivitas" tiap karakter tunggal di app_words.json:
yaitu berapa banyak kata majemuk (2+ karakter) dalam database yang
mengandung karakter tersebut. Karakter dengan skor tinggi = "kata dasar"
yang layak dijadikan starting point pembelajaran kosakata (analogi
akar kata dalam ilmu sharaf).

Output: produktif_karakter.json
Struktur:
{
  "电": {
    "hsk": "2",
    "pinyin": "diàn",
    "arti": "listrik",
    "jumlah_turunan": 18,
    "kata_turunan": [
        {"kata": "电脑", "pinyin": "diànnǎo", "arti": "komputer", "hsk": "1"},
        ...
    ]
  },
  ...
}

Cara pakai:
    python analisis_produktivitas.py app_words.json produktif_karakter.json
"""

import json
import sys
from collections import defaultdict


def load_words(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def short_meaning(entry):
    """
    Ambil arti Indonesia pertama saja. TIDAK dipotong -- versi awal memotong
    ke 40 karakter + "..." supaya ringkas di preview, tapi ini bikin teks
    aslinya HILANG PERMANEN di semua tahap turunan (xlsx, HTML mandiri, dst),
    karena versi terpotong itu yang tersimpan di produktif_karakter.json.
    UI yang butuh versi ringkas (kartu, list) harus memotong di sisi
    tampilan (CSS text-overflow/JS), bukan di sini.
    """
    meanings = entry.get("meanings_id") or []
    if not meanings:
        return ""
    return meanings[0]


def analisis(words, min_stroke_filter=None, hsk_max=None):
    # index kata tunggal (karakter dasar)
    single_entries = {}
    for w in words:
        simp = w.get("simplified", "")
        if len(simp) == 1:
            # kalau ada duplikat id, prioritaskan yang frequency lebih rendah (lebih umum)
            w_freq = w.get("frequency") if w.get("frequency") is not None else 99999
            existing_freq = single_entries[simp].get("frequency") if simp in single_entries else None
            existing_freq = existing_freq if existing_freq is not None else 99999
            if simp not in single_entries or w_freq < existing_freq:
                single_entries[simp] = w

    # hitung kemunculan tiap karakter dasar di kata majemuk
    turunan_map = defaultdict(list)
    for w in words:
        simp = w.get("simplified", "")
        if len(simp) <= 1:
            continue
        seen_chars_in_this_word = set()
        for ch in simp:
            if ch in single_entries and ch not in seen_chars_in_this_word:
                turunan_map[ch].append(w)
                seen_chars_in_this_word.add(ch)

    hasil = {}
    for ch, entry in single_entries.items():
        turunan = turunan_map.get(ch, [])
        if not turunan:
            continue
        if hsk_max is not None:
            hsk = entry.get("hsk")
            try:
                if hsk is None or int(hsk) > hsk_max:
                    continue
            except (ValueError, TypeError):
                pass

        turunan_sorted = sorted(
            turunan,
            key=lambda w: (w.get("frequency") if w.get("frequency") is not None else 999999),
        )

        hasil[ch] = {
            "hsk": entry.get("hsk"),
            "pinyin": entry.get("pinyin"),
            "arti": short_meaning(entry),
            "jumlah_turunan": len(turunan),
            "kata_turunan": [
                {
                    "kata": t.get("simplified"),
                    "pinyin": t.get("pinyin"),
                    "arti": short_meaning(t),
                    "hsk": t.get("hsk"),
                }
                for t in turunan_sorted
            ],
        }

    # urutkan hasil berdasarkan jumlah_turunan menurun
    hasil_terurut = dict(
        sorted(hasil.items(), key=lambda kv: kv[1]["jumlah_turunan"], reverse=True)
    )
    return hasil_terurut


def main():
    in_path = sys.argv[1] if len(sys.argv) > 1 else "app_words.json"
    out_path = sys.argv[2] if len(sys.argv) > 2 else "produktif_karakter.json"

    words = load_words(in_path)
    hasil = analisis(words)

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(hasil, f, ensure_ascii=False, indent=2)

    print(f"Total karakter dasar dianalisis: {len(hasil)}")
    print(f"Disimpan ke: {out_path}")
    print("\nTop 20 karakter paling produktif:")
    for i, (ch, d) in enumerate(list(hasil.items())[:20], 1):
        print(f"{i:2d}. {ch} ({d['pinyin']}, HSK{d['hsk']}) - {d['arti']} -> {d['jumlah_turunan']} kata turunan")


if __name__ == "__main__":
    main()

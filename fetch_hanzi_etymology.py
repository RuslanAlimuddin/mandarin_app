# -*- coding: utf-8 -*-
"""
fetch_hanzi_etymology.py — Mandarin Interaktif

Unduh dictionary.txt dari proyek Make Me a Hanzi (skishore/makemeahanzi di
GitHub), lalu filter HANYA karakter yang benar-benar dipakai di
app_words.json (supaya tidak memproses ribuan karakter yang tidak relevan).

Hasil: character_etymology_en.json -- masih Bahasa Inggris, BELUM
diterjemahkan. Field 'etymology' bisa null kalau karakter itu tidak punya
data etimologi di sumbernya (wajar, tidak semua karakter terdokumentasi).

CARA PAKAI:
    1. Taruh skrip ini di folder C:\\mandarin_app\\ (sejajar dengan data\\)
    2. Jalankan: python fetch_hanzi_etymology.py
    3. Tunggu proses unduh (dictionary.txt sekitar 40-an ribu baris, ~beberapa MB)
    4. Hasil ada di data/character_etymology_en.json

Setelah ini selesai, upload file hasilnya (character_etymology_en.json) ke
percakapan Claude berikutnya -- kita lanjutkan proses terjemahan ke Bahasa
Indonesia & kurasi bareng-bareng di sana, bertahap per batch supaya
kualitasnya bisa dicek, bukan asal translate mesin semua sekaligus.
"""

import json
import urllib.request
import os

DICTIONARY_URL = "https://raw.githubusercontent.com/skishore/makemeahanzi/master/dictionary.txt"
APP_WORDS_PATH = "data/app_words.json"
OUTPUT_PATH = "data/character_etymology_en.json"


def get_used_characters():
    """Kumpulkan semua karakter unik yang dipakai di app_words.json."""
    with open(APP_WORDS_PATH, encoding="utf-8") as f:
        words = json.load(f)
    chars = set()
    for w in words:
        s = w.get("simplified", "") or w.get("id", "")
        chars.update(s)
    print(f"Ditemukan {len(chars)} karakter unik di app_words.json.")
    return chars


def download_dictionary():
    print("Mengunduh dictionary.txt dari GitHub (skishore/makemeahanzi)...")
    with urllib.request.urlopen(DICTIONARY_URL) as res:
        raw = res.read().decode("utf-8")
    lines = [l for l in raw.split("\n") if l.strip()]
    print(f"Selesai unduh, {len(lines)} baris data karakter.")
    return lines


def build_filtered_index(lines, used_chars):
    result = {}
    matched = 0
    with_etymology = 0

    for line in lines:
        try:
            entry = json.loads(line)
        except json.JSONDecodeError:
            continue

        char = entry.get("character")
        if not char or char not in used_chars:
            continue

        matched += 1
        etymology = entry.get("etymology")
        if etymology:
            with_etymology += 1

        result[char] = {
            "definition_en": entry.get("definition"),
            "etymology": etymology,  # {type, hint, phonetic, semantic} atau null
        }

    print(f"Cocok dengan karakter di app_words.json: {matched} / {len(used_chars)}")
    print(f"...yang punya data etimologi (bukan null): {with_etymology}")
    return result


def main():
    if not os.path.exists(APP_WORDS_PATH):
        print(f"⚠ Tidak ketemu {APP_WORDS_PATH}.")
        print("  Jalankan skrip ini dari folder root C:\\mandarin_app\\")
        return

    used_chars = get_used_characters()
    lines = download_dictionary()
    result = build_filtered_index(lines, used_chars)

    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"\n✓ Selesai. Hasil disimpan ke {OUTPUT_PATH}")
    print("  Langkah selanjutnya: upload file ini ke percakapan Claude berikutnya")
    print("  untuk proses terjemahan & kurasi ke Bahasa Indonesia.")


if __name__ == "__main__":
    main()

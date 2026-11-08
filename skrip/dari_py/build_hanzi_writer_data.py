# -*- coding: utf-8 -*-
"""
build_hanzi_writer_data.py

Jalankan script ini LOKAL di C:\\mandarin_app (bukan di sini/Claude).

Yang dilakukan:
1. Baca data/app_words.json, ambil SEMUA karakter individu dari SEMUA kata
   (bukan cuma kata 1-huruf lagi -- supaya karakter penyusun kata
   multi-huruf seperti 学习 juga ke-cover, karena animasi goresan sekarang
   mau ditampilkan untuk kata apapun, per-karakter berurutan).
2. Cari file <karakter>.json untuk tiap karakter itu di dalam folder hasil
   ekstrak hanzi-writer-data-master.zip (dicari rekursif, jadi tidak masalah
   filenya ada di subfolder "data/" atau langsung di root -- struktur repo
   ini kadang beda-beda antar versi).
3. Gabungkan semua yang ketemu jadi SATU file: data/hanzi_writer_data.json
   -- supaya rasa web cukup 1x fetch, bukan ratusan request kecil-kecil.
4. Cetak laporan: berapa yang ketemu, berapa yang tidak (kalau ada karakter
   yang tidak ketemu datanya, animasi goresan kuas untuk kata itu nanti
   otomatis fallback ke highlight-komponen yang sekarang, tidak error).

CARA PAKAI:
1. Ekstrak dulu hanzi-writer-data-master.zip dari folder Downloads
   (klik kanan -> Extract All), catat lokasi hasil ekstraknya.
2. Taruh file script ini di C:\\mandarin_app (sejajar dengan folder data/).
3. Jalankan lewat Command Prompt / PowerShell:

     python build_hanzi_writer_data.py "C:\\Users\\NAMA\\Downloads\\hanzi-writer-data-master"

   (ganti path di atas sesuai lokasi hasil ekstrak ZIP-nya)
4. Kalau sukses, akan muncul file baru: data/hanzi_writer_data.json
   Kirim balik ke Claude ringkasan yang dicetak di layar (jumlah ketemu/
   tidak ketemu), supaya saya tahu cakupannya sebelum lanjut integrasi ke
   Kamus & Flashcard.
"""

import json
import os
import sys


def load_needed_characters(app_words_path):
    with open(app_words_path, "r", encoding="utf-8") as f:
        words = json.load(f)

    chars = set()
    for w in words:
        simplified = w.get("simplified") or w.get("cn") or ""
        # PENTING: ambil SEMUA karakter individu dari kata ini, bukan cuma
        # kalau katanya 1-huruf. Supaya karakter penyusun kata multi-huruf
        # (mis. 学 dan 习 dari 学习) juga ke-cover -- rencananya animasi
        # goresan mau ditampilkan untuk kata multi-huruf juga (per-karakter
        # berurutan), bukan cuma kata 1-huruf seperti sebelumnya.
        for ch in simplified:
            if ch.strip():  # lewati spasi/tanda baca kalau ada
                chars.add(ch)
    return chars


def build_char_file_index(data_root):
    """Rekursif: petakan nama-file-tanpa-ekstensi -> path lengkap,
    untuk semua file .json di dalam data_root. Ini memastikan script tetap
    jalan walau strukturnya nested (data/data/..., data/graphics/..., dst)."""
    index = {}
    for dirpath, _dirnames, filenames in os.walk(data_root):
        for fname in filenames:
            if not fname.endswith(".json"):
                continue
            stem = fname[:-5]  # buang ".json"
            # stem seharusnya persis 1 karakter hanzi (mis. "我.json")
            if len(stem) == 1:
                index[stem] = os.path.join(dirpath, fname)
    return index


def main():
    if len(sys.argv) < 2:
        print('Cara pakai: python build_hanzi_writer_data.py "path\\ke\\hanzi-writer-data-master"')
        sys.exit(1)

    data_root = sys.argv[1]
    if not os.path.isdir(data_root):
        print(f"Folder tidak ditemukan: {data_root}")
        sys.exit(1)

    app_words_path = os.path.join("data", "app_words.json")
    if not os.path.isfile(app_words_path):
        print(f"Tidak ketemu {app_words_path} -- jalankan script ini dari folder C:\\mandarin_app")
        sys.exit(1)

    print("Membaca daftar karakter yang dibutuhkan dari app_words.json ...")
    needed = load_needed_characters(app_words_path)
    print(f"  -> {len(needed)} karakter unik ditemukan (dari SEMUA kata, termasuk penyusun kata multi-huruf).")

    print("Mengindeks file di dalam hasil ekstrak hanzi-writer-data (bisa agak lama, ribuan file) ...")
    file_index = build_char_file_index(data_root)
    print(f"  -> {len(file_index)} file karakter ditemukan di dalam folder itu.")

    result = {}
    missing = []
    for ch in sorted(needed):
        path = file_index.get(ch)
        if not path:
            missing.append(ch)
            continue
        try:
            with open(path, "r", encoding="utf-8") as f:
                result[ch] = json.load(f)
        except Exception as e:
            print(f"  ! Gagal baca data untuk '{ch}': {e}")
            missing.append(ch)

    out_path = os.path.join("data", "hanzi_writer_data.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False)

    print()
    print("=" * 50)
    print(f"SELESAI -> {out_path}")
    print(f"  Ketemu   : {len(result)} / {len(needed)} karakter")
    print(f"  Tidak ada: {len(missing)} karakter")
    if missing:
        preview = "".join(missing[:40])
        print(f"  Contoh yang tidak ketemu (maks 40 ditampilkan): {preview}")
    print("=" * 50)
    print()
    print("Kirim ringkasan di atas (angka Ketemu/Tidak ada) balik ke Claude.")


if __name__ == "__main__":
    main()

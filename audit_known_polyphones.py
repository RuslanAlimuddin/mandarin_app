#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
audit_known_polyphones.py

AUDIT READ-ONLY (tidak mengubah file apa pun).

Latar belakang: bug 号(háo→hào)/看(kān→kàn)/说(shuì→shuō) TIDAK tertangkap
oleh DEPRIORITIZE_MARKERS karena bacaan langka itu tidak berlabel eksplisit
"marga/varian/sastra/bentuk terikat" di teks arti -- polanya murni "karakter
ini punya >1 bacaan valid, dan bacaan yang JARANG dipakai berdiri sendiri
kebetulan yang tersimpan sbg pinyin utama di app_words.json."

Pendekatan: daripada coba deteksi otomatis 100% (sudah terbukti tidak
realistis -- lihat Bagian D metodologi BLUEPRINT), script ini memakai
DAFTAR KANDIDAT karakter polifonik umum HSK1-6 yang dikenal luas rawan
programmatic error semacam ini (termasuk 号/看/说 yang sudah dikonfirmasi
rusak). Untuk tiap kandidat yang ADA di app_words.json, script mencetak
pinyin tersimpan + 3 arti pertama, supaya رسلان & Claude bisa sample-check
manual mana yang benar-benar bermasalah vs mana yang sudah OK.

Daftar kandidat SENGAJA lebih luas dari yang sudah dikonfirmasi rusak --
tujuannya menangkap kasus serupa yang belum ketahuan, bukan cuma
mengonfirmasi yang sudah diketahui.

Penggunaan:
    python audit_known_polyphones.py
    python audit_known_polyphones.py --hsk-only     # cuma kata berlabel HSK
    python audit_known_polyphones.py --path data/app_words.json
"""
import json
import argparse
from pathlib import Path

DATA_PATH = Path("data/app_words.json")

# Kandidat karakter polifonik umum (HSK1-6) yang dikenal rawan
# "bacaan jarang jadi default". Format: {char: catatan singkat pengingat}
# Catatan HANYA pengingat untuk reviewer manusia -- script TIDAK memakainya
# untuk keputusan otomatis apa pun.
CANDIDATES = {
    "号": "háo (meraung, sastra) vs hào (nomor/tanggal/tanda -- umum)",
    "看": "kān (menjaga/mengawasi) vs kàn (melihat/menonton -- umum)",
    "说": "shuì (membujuk, sastra) vs shuō (berkata -- umum)",
    "假": "jiǎ (palsu -- umum) vs jià (liburan -- umum, konteks beda)",
    "圈": "quān (lingkaran -- umum) vs juàn (kandang) vs juān (mengurung)",
    "落": "luò (jatuh -- umum) vs là (tertinggal) vs lào (dialek)",
    "差": "chà (kurang/buruk -- umum) vs chā (perbedaan) vs chāi (tugas) vs cī (tak rata)",
    "相": "xiāng (saling -- umum) vs xiàng (penampilan/menteri)",
    "藏": "cáng (menyimpan -- umum) vs zàng (Tibet)",
    "结": "jié (mengikat/menyimpulkan -- umum) vs jiē (berbuah)",
    "曲": "qū (bengkok/salah -- umum) vs qǔ (lagu/melodi -- umum, konteks beda)",
    "强": "qiáng (kuat -- umum) vs qiǎng (memaksa) vs jiàng (keras kepala)",
    "空": "kōng (kosong -- umum) vs kòng (waktu luang -- umum, konteks beda)",
    "种": "zhǒng (jenis -- umum) vs zhòng (menanam -- umum, konteks beda)",
    "教": "jiāo (mengajar -- umum) vs jiào (agama/ajaran -- umum, konteks beda)",
    "血": "xiě (darah, lisan -- umum) vs xuè (darah, formal -- umum, konteks beda)",
    "supersedable": None,  # placeholder dihapus di bawah
}
CANDIDATES.pop("supersedable", None)

# Tambahan: kata majemuk (bukan cuma 1 karakter) yang sering ikut kena efek
# domino kalau karakter penyusunnya salah baca.
COMPOUND_CANDIDATES = ["号码", "看见", "看望", "小说", "说服", "带子", "老板"]


def load_json(path: Path):
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def find_entries(data, word):
    if isinstance(data, dict):
        v = data.get(word)
        return [v] if v is not None else []
    return [e for e in data if e.get("id") == word or e.get("simplified") == word]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--path", default=str(DATA_PATH))
    ap.add_argument("--hsk-only", action="store_true")
    args = ap.parse_args()

    path = Path(args.path)
    if not path.exists():
        print(f"File tidak ditemukan: {path}")
        return

    data = load_json(path)

    print("=== AUDIT: karakter polifonik kandidat (bacaan jarang jadi default) ===\n")
    found_any = False
    for char, note in CANDIDATES.items():
        entries = find_entries(data, char)
        if not entries:
            continue
        for e in entries:
            if args.hsk_only and not (e.get("hsk") or e.get("hsk2")):
                continue
            found_any = True
            print(f"--- {char} ---")
            print(f"  catatan   : {note}")
            print(f"  pinyin    : {e.get('pinyin')}")
            print(f"  bopomofo  : {e.get('bopomofo')}")
            print(f"  hsk       : {e.get('hsk')} / hsk2: {e.get('hsk2')}")
            print(f"  meanings_id (3 pertama): {e.get('meanings_id', [])[:3]}")
            print()

    if not found_any:
        print("(tidak ada kandidat ditemukan di app_words.json)\n")

    print("=== KATA MAJEMUK terkait (cek efek domino) ===\n")
    for word in COMPOUND_CANDIDATES:
        entries = find_entries(data, word)
        if not entries:
            print(f"--- {word} : tidak ditemukan di app_words.json ---\n")
            continue
        for e in entries:
            print(f"--- {word} ---")
            print(f"  pinyin    : {e.get('pinyin')}")
            print(f"  meanings_id (3 pertama): {e.get('meanings_id', [])[:3]}")
            print()

    print("--- CATATAN ---")
    print("Ini audit READ-ONLY. Tidak ada file yang diubah.")
    print("Silakan sample-check tiap entri di atas: apakah pinyin/arti pertama")
    print("sudah mencerminkan bacaan paling umum? Kirim hasilnya untuk direview")
    print("sebelum kita tulis script perbaikan (pola yang sama dgn 18-kata sesi lalu).")


if __name__ == "__main__":
    main()

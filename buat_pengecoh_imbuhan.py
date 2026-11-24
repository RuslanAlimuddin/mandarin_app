#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
buat_pengecoh_imbuhan.py -- daftar pilihan pengecoh untuk soal "Pilih imbuhan yang tepat"
==========================================================================================
Soal (a) latihan imbuhan di Flashcard (keputusan رسلان, 24 November 2026): kata ditampilkan dengan
satu bagian kosong, mis. "记 + ＿" (arti: wartawan), lalu pilih imbuhan yang tepat dari 4 pilihan.
Pilihan yang salah (pengecoh) HARUS tidak membentuk kata yang sah, kalau tidak soalnya punya dua
jawaban benar (mis. 作者 dan 作家 sama-sama kata sah). Pemeriksaan ini butuh kamus CC-CEDICT
(data\\cidict_index.json.gz, 121 ribu kata) yang tidak dimuat di halaman Flashcard, jadi dihitung SEKALI di sini
dan hasilnya disimpan di data\\afiks_pengecoh.json (dipakai permainan secara offline).

Untuk tiap kata contoh (kata, imbuhan) di data\\afiks_kamus.json:
  - dasar   = kata tanpa imbuhannya (akhiran: bagian depan; awalan: bagian belakang)
  - "sama"  = imbuhan lain di KELOMPOK yang sama dengan posisi yang sama, yang bila dipasang pada dasar itu
              TIDAK membentuk kata yang ada di app_words.json maupun CC-CEDICT
  - "lain"  = imbuhan dari kelompok lain (posisi sama) yang juga aman; hanya diisi bila "sama" kurang dari 3
Soal hanya dibuat bila "sama" + "lain" ada minimal 3. Permainan memilih 3 pengecoh secara acak dari daftar ini
(mengutamakan "sama").

CARA PAKAI (dari C:\\mandarin_app>):
  1) Lihat dulu (TIDAK mengubah apa pun):   python buat_pengecoh_imbuhan.py
  2) Tulis berkas:                          python buat_pengecoh_imbuhan.py --apply
Hasil: data\\afiks_pengecoh.json. Aman diulang; bila isinya sudah sama, tidak ada yang ditulis.
Jalankan ulang bila data\\afiks_kamus.json berubah (mis. setelah kontribusi batch kandidat ditambahkan).
"""
import argparse
import gzip
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
AFIKS = ROOT / "data" / "afiks_kamus.json"
KATA = ROOT / "data" / "app_words.json"
CIDICT = ROOT / "data" / "cidict_index.json.gz"
KELUAR = ROOT / "data" / "afiks_pengecoh.json"
MAKS_LAIN = 5


def susun():
    afiks = json.loads(AFIKS.read_text(encoding="utf-8"))
    app = {w["simplified"] for w in json.loads(KATA.read_text(encoding="utf-8"))}
    with gzip.open(CIDICT, "rt", encoding="utf-8") as f:
        cc = {e["simplified"] for e in json.load(f) if e.get("simplified")}
    ada = lambda s: s in app or s in cc
    soal, dilewati, pakai_lain = [], [], 0
    sudah = set()
    for e in afiks:
        ch, pos, kel = e["karakter"], e["posisi"], e["kelompok"]
        for b in e["bagian"]:
            for c in b["contoh"]:
                kata = c["kata"]
                if (kata, ch) in sudah:
                    continue
                sudah.add((kata, ch))
                dasar = kata[:-len(ch)] if pos == "akhiran" else kata[len(ch):]
                if not dasar:
                    dilewati.append((kata, ch, "tanpa dasar"))
                    continue
                sama, lain = [], []
                for o in afiks:
                    if o is e or o["posisi"] != pos or o["karakter"] == ch:
                        continue
                    gabung = dasar + o["karakter"] if pos == "akhiran" else o["karakter"] + dasar
                    if ada(gabung):
                        continue
                    (sama if o["kelompok"] == kel else lain).append(o["karakter"])
                if len(sama) + len(lain) < 3:
                    dilewati.append((kata, ch, "pengecoh aman hanya %d" % (len(sama) + len(lain))))
                    continue
                item = {"kata": kata, "afiks": ch, "sama": sama}
                if len(sama) < 3:
                    item["lain"] = lain[:MAKS_LAIN]
                    pakai_lain += 1
                soal.append(item)
    return soal, dilewati, pakai_lain


def teks(soal):
    data = {
        "keterangan": "Dibuat oleh buat_pengecoh_imbuhan.py dari data/afiks_kamus.json + app_words.json + CC-CEDICT. "
                      "Jangan diubah tangan; jalankan ulang skripnya.",
        "soal": soal,
    }
    return json.dumps(data, ensure_ascii=False, indent=1).replace("\n", "\r\n") + "\r\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true", help="tulis berkas (tanpa ini hanya melihat ringkasan)")
    a = ap.parse_args()
    for p in (AFIKS, KATA, CIDICT):
        if not p.exists():
            print("Tidak menemukan %s" % p)
            return 1
    soal, dilewati, pakai_lain = susun()
    n3 = sum(1 for s in soal if len(s["sama"]) >= 3)
    print("=== Pengecoh soal 'Pilih imbuhan yang tepat' ===")
    print("Soal yang bisa dibuat      : %d (dari %d kata contoh)" % (len(soal), len(soal) + len(dilewati)))
    print("  pengecoh cukup dari kelompok yang sama : %d" % n3)
    print("  perlu tambahan dari kelompok lain      : %d" % pakai_lain)
    print("Dilewati                   : %d" % len(dilewati))
    for kata, ch, alasan in dilewati:
        print("   %s (%s): %s" % (kata, ch, alasan))
    baru = teks(soal)
    ada = KELUAR.read_bytes().decode("utf-8") if KELUAR.exists() else None
    if ada == baru:
        print("\nBerkas data\\afiks_pengecoh.json sudah sesuai. Tidak ada yang perlu diubah.")
        return 0
    if not a.apply:
        print("\nIni baru ringkasan; belum ada yang ditulis. Untuk menulis: python buat_pengecoh_imbuhan.py --apply")
        return 0
    KELUAR.write_bytes(baru.encode("utf-8"))
    ulang = json.loads(KELUAR.read_bytes().decode("utf-8"))
    if ulang["soal"] != soal:
        print("PEMERIKSAAN AKHIR GAGAL. Kirim pesan ini ke Claude.")
        return 1
    print("\nSelesai: %d soal ditulis ke data\\afiks_pengecoh.json (pemeriksaan akhir lolos)." % len(soal))
    print("Berkas yang perlu diunggah ke GitHub: data/afiks_pengecoh.json dan buat_pengecoh_imbuhan.py")
    return 0


if __name__ == "__main__":
    sys.exit(main())

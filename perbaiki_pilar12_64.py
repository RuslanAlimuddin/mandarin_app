#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
perbaiki_pilar12_64.py -- menyesuaikan pelajaran Pilar 12 (data\\pelajaran\\pilar_12.json) dengan 64 entri imbuhan:
  - angka 60 -> 64 (ringkasan, judul dan isi bagian 6, peringatan)
  - "sepuluh kelompok" -> "dua belas kelompok"; akhiran 43 -> 47 (awalan tetap 17)
  - tabel peta: tambah baris kelompok K dan L
  - "materi lanjutan": 族 迷 症 剂 dikeluarkan (sudah dikerjakan); sisa 热 控 炎 盲; baris 上 下 里 外 中 间 menunjuk ke Pilar 13
Tidak mengubah berkas lain.

CARA PAKAI (dari C:\\mandarin_app>):
  1) Lihat dulu (TIDAK mengubah apa pun):   python perbaiki_pilar12_64.py
  2) Pasang:                                python perbaiki_pilar12_64.py --apply
Cadangan: data\\pelajaran\\pilar_12.json.bak_64_<tanggal-jam>. Aman diulang.
"""
import json
import re
import shutil
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
F = ROOT / "data" / "pelajaran" / "pilar_12.json"


def ganti(teks, lama, baru, hitungan):
    n = teks.count(lama)
    if n != hitungan:
        print("GALAT: teks \"%s...\" ditemukan %d kali (seharusnya %d)." % (lama[:40], n, hitungan))
        sys.exit(1)
    return teks.replace(lama, baru)


def main():
    apply = "--apply" in sys.argv
    print("Mode: " + ("PASANG (--apply)" if apply else "LIHAT-DULU (tidak mengubah apa pun)"))
    d = json.loads(F.read_text(encoding="utf-8"))
    if "Peta Cepat 64 Entri" in d["bagian"][5]["judul"]:
        print("Sudah terpasang sebelumnya. Tidak ada yang perlu diubah.")
        return

    # tabel peta: baris K dan L (struktur, bukan teks); hanzi dibungkus span seperti baris lain
    def hzs(daftar):
        return "、".join('<span class="hz">%s</span>' % c for c in daftar)

    def polos(t):
        return re.sub(r"<[^>]+>", "", t)

    tabel = d["bagian"][5]["isi"][1]["baris"]
    assert tabel[-1][0] == "J" and len(tabel) == 10
    tabel.append(["K", "Penggemar dan kelompok orang: " + hzs("族迷"), "2",
                  "Menyebut suku atau kelompok orang dengan ciri yang sama, dan orang yang menggemari sesuatu."])
    tabel.append(["L", "Penyakit dan zat: " + hzs("症剂"), "2",
                  "Menyebut penyakit atau kelainan, serta obat atau bahan olahan."])
    # materi lanjutan
    lanjut = d["bagian"][5]["isi"][3]["baris"]
    assert polos(lanjut[0][0]) == "族、迷、热、控、症、剂、炎、盲", polos(lanjut[0][0])
    lanjut[0] = [hzs("热控炎盲"),
                 "Masih ditunda karena contoh yang memenuhi syarat di Kamus belum cukup (炎 dan 盲 baru punya satu kata contoh)."]
    assert polos(lanjut[1][0]) == "上、下、里、外、中、间", polos(lanjut[1][0])
    lanjut[1][1] = "Sudah dibahas di Pilar 13 (Kata Penunjuk Posisi)."

    s = json.dumps(d, ensure_ascii=False)
    s = ganti(s, "6. Peta Cepat 60 Entri dan Materi yang Menyusul", "6. Peta Cepat 64 Entri dan Materi yang Menyusul", 1)
    s = ganti(s, "berisi 60 entri yang dibagi menjadi sepuluh kelompok. Jumlahnya terdiri dari 43 entri akhiran dan 17 entri awalan.",
              "berisi 64 entri yang dibagi menjadi dua belas kelompok. Jumlahnya terdiri dari 47 entri akhiran dan 17 entri awalan.", 1)
    s = ganti(s, "melihat peta 60 entri", "melihat peta 64 entri", 1)
    s = ganti(s, "yang belum termasuk 60 entri saat ini", "yang belum termasuk 64 entri saat ini", 1)
    s = ganti(s, "belum dimasukkan ke daftar 60", "belum dimasukkan ke daftar 64", 1)
    s = ganti(s, "Daftar 60 ini adalah", "Daftar 64 ini adalah", 1)
    s = ganti(s, "salah satu dari 60 karakter", "salah satu dari 64 karakter", 1)
    d2 = json.loads(s)

    sisa = [m.group(0) for m in re.finditer(r".{30}(\b60\b|sepuluh).{30}", json.dumps(d2, ensure_ascii=False))]
    print("Sisa kata '60'/'sepuluh' setelah perbaikan:", sisa if sisa else "tidak ada")
    print("Bagian 6: judul = " + d2["bagian"][5]["judul"] + "; baris tabel peta = %d (A-L)" % len(d2["bagian"][5]["isi"][1]["baris"]))
    if not apply:
        print("\nBelum ada yang diubah. Jika sudah sesuai, jalankan:  python perbaiki_pilar12_64.py --apply")
        return
    cap = time.strftime("%Y%m%d-%H%M%S")
    cad = F.with_name(F.name + ".bak_64_" + cap)
    shutil.copy2(F, cad)
    F.write_text(json.dumps(d2, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    cek = json.loads(F.read_text(encoding="utf-8"))
    if cek != d2 or len(cek["bagian"]) != 6:
        shutil.copy2(cad, F)
        print("GALAT pemeriksaan akhir; berkas dikembalikan.")
        sys.exit(1)
    print("\nSelesai. Cadangan: " + cad.name)


if __name__ == "__main__":
    main()

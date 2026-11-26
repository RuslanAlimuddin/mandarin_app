#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pasang_imbuhan_tingkat3.py -- menambah 4 akhiran Tingkat 3 ke data\\afiks_kamus.json: 族 迷 症 剂
(炎 dan 盲 DITUNDA: di app_words.json masing-masing hanya punya 1 kata contoh).

Entri baru: AFK-061 族, AFK-062 迷 (kelompok K "Penggemar dan kelompok orang"),
            AFK-063 症, AFK-064 剂 (kelompok L "Penyakit dan zat").
Kata contoh dan kata "bukan" semuanya diperiksa harus ada persis di data\\app_words.json.

CARA PAKAI (dari C:\\mandarin_app>):
  1) Lihat dulu (TIDAK mengubah apa pun):   python pasang_imbuhan_tingkat3.py
  2) Pasang:                                python pasang_imbuhan_tingkat3.py --apply
  3) Lalu buat ulang pengecoh:              python buat_pengecoh_imbuhan.py --apply
Cadangan otomatis: data\\afiks_kamus.json.bak_tingkat3_<tanggal-jam>. Aman diulang (entri yang sudah ada dilewati).
"""
import json
import shutil
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
AFIKS = ROOT / "data" / "afiks_kamus.json"
KATA = ROOT / "data" / "app_words.json"

K = ("K", "Penggemar dan kelompok orang")
L = ("L", "Penyakit dan zat")


def entri(id_, ch, py, kel, arti, fungsi, contoh, bukan, catatan):
    return {
        "id": id_, "karakter": ch, "pinyin": py,
        "kelompok": kel[0], "kelompok_nama": kel[1], "posisi": "akhiran",
        "arti_dasar": arti,
        "bagian": [{"sebagai": "akhiran", "fungsi": fungsi, "arti": arti,
                    "contoh": [{"kata": k} for k in contoh]}],
        "bukan": [{"kata": k, "alasan": a} for k, a in bukan],
        "catatan": catatan,
    }


BARU = [
    entri("AFK-061", "族", "zú", K,
          "kelompok orang yang sebangsa atau punya ciri dan kebiasaan yang sama",
          "Diletakkan di akhir kata untuk menyebut suku bangsa atau sekelompok orang dengan ciri atau kebiasaan yang sama.",
          ["民族", "种族", "贵族", "家族", "上班族"], [],
          "中华民族 memuat 民族, jadi tidak dipisah sebagai contoh sendiri. Arti 族 di 上班族 adalah \"golongan orang dengan kebiasaan yang sama\"; pola ini bisa dipakai membuat sebutan baru."),
    entri("AFK-062", "迷", "mí", K,
          "penggemar; orang yang sangat menyukai sesuatu",
          "Diletakkan di akhir nama kegiatan atau tokoh untuk menyebut orang yang menggemarinya.",
          ["球迷", "歌迷", "影迷"],
          [("昏迷", "昏迷 berarti \"koma/pingsan\"; 迷 di sini berarti kehilangan kesadaran, bukan penggemar."),
           ("低迷", "低迷 berarti \"lesu/suram\"; 迷 di sini berarti samar atau kabur, bukan penggemar.")],
          "沉迷, 痴迷, dan 着迷 memakai 迷 dalam arti \"terpikat\" sebagai kata kerja (bukan sebutan orang), jadi tidak dipakai sebagai contoh maupun daftar \"bukan\". Di depan kata, 迷 berarti tersesat atau memikat (迷路, 迷人)."),
    entri("AFK-063", "症", "zhèng", L,
          "penyakit atau kelainan dengan gejala tertentu",
          "Diletakkan di akhir nama penyebab atau gejala untuk menyebut suatu penyakit atau kelainan.",
          ["癌症", "抑郁症", "后遗症", "炎症", "病症"], [],
          "症状 (gejala) memakai 症 di depan, jadi bukan contoh akhiran. 症 dibaca zhèng; pada 症结 dibaca zhēng."),
    entri("AFK-064", "剂", "jì", L,
          "obat atau bahan olahan dengan fungsi tertentu",
          "Diletakkan di akhir kata yang menyebut fungsi atau jenisnya untuk menamai obat atau bahan olahan.",
          ["兴奋剂", "洗涤剂"], [],
          "Di kamus HSK baru ada dua contoh. 调剂 (kata kerja: menyesuaikan, memberi variasi) tidak dipakai sebagai contoh."),
]


def main():
    apply = "--apply" in sys.argv
    print("Mode: " + ("PASANG (--apply)" if apply else "LIHAT-DULU (tidak mengubah apa pun)"))
    data = json.loads(AFIKS.read_text(encoding="utf-8"))
    app = {w["simplified"] for w in json.loads(KATA.read_text(encoding="utf-8"))}
    ada = {e["karakter"] for e in data}
    ids = {e["id"] for e in data}

    salah = []
    for e in BARU:
        for k in [c["kata"] for c in e["bagian"][0]["contoh"]] + [b["kata"] for b in e["bukan"]]:
            if k not in app:
                salah.append((e["karakter"], k))
            if not k.endswith(e["karakter"]):
                salah.append((e["karakter"], k + " (tidak berakhiran imbuhan)"))
    if salah:
        print("GALAT: kata tidak ditemukan di app_words.json / bukan akhiran:", salah)
        sys.exit(1)

    tambah = []
    for e in BARU:
        if e["karakter"] in ada or e["id"] in ids:
            print("  lewati (sudah ada): %s %s" % (e["id"], e["karakter"]))
        else:
            tambah.append(e)
            print("  tambah: %s %s kelompok %s  contoh=%d bukan=%d" % (
                e["id"], e["karakter"], e["kelompok"], len(e["bagian"][0]["contoh"]), len(e["bukan"])))
    if not tambah:
        print("Tidak ada yang perlu diubah.")
        return
    if not apply:
        print("\nBelum ada yang diubah. Jika sudah sesuai, jalankan:  python pasang_imbuhan_tingkat3.py --apply")
        return

    cap = time.strftime("%Y%m%d-%H%M%S")
    cad = AFIKS.with_name(AFIKS.name + ".bak_tingkat3_" + cap)
    shutil.copy2(AFIKS, cad)
    hasil = data + tambah
    AFIKS.write_text(json.dumps(hasil, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    # pemeriksaan akhir
    cek = json.loads(AFIKS.read_text(encoding="utf-8"))
    ok = (len(cek) == len(data) + len(tambah)
          and len({e["id"] for e in cek}) == len(cek)
          and cek[:len(data)] == data)
    if not ok:
        shutil.copy2(cad, AFIKS)
        print("GALAT pemeriksaan akhir; berkas dikembalikan dari cadangan.")
        sys.exit(1)
    print("\nSelesai: %d entri baru dipasang (total %d). Cadangan: %s" % (len(tambah), len(cek), cad.name))
    print("Langkah berikut:  python buat_pengecoh_imbuhan.py --apply")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
perbaiki_nada_lama.py -- memperbaiki 8 salah tanda nada di contoh pinyin data/nuance_pairs.json
=============================================================================================
Tahap 1 dari penyamaan 1.868 contoh lama (butir 3 rencana v45). Yang diubah HANYA isian example_pinyin
di 8 tempat (satu suku kata tiap tempat):
   成绩 chéngjī -> chéngjì   (2 contoh: 取得 "好成绩" dan 查询 "考试成绩")
   别忘 biè wàng -> bié wàng (伞)
   高涨 gāozhàng -> gāozhǎng
   痕迹 hénjī -> hénjì       (极小)
   供应 gòngyìng -> gōngyìng (供)
   为人 wèirén -> wéirén     (宽厚)
   突然 Túrán -> Tūrán       (声响; pilihan Daratan, sama dengan 8 contoh lain di data)

CARA PAKAI (dari C:\\mandarin_app>):

  1) Lihat dulu (TIDAK mengubah apa pun):
         python perbaiki_nada_lama.py

  2) Terapkan:
         python perbaiki_nada_lama.py --apply

KEAMANAN
  - Tiap perbaikan dikenali dari id pasangan + kata + nama isian, dan hanya dijalankan bila
    isi sekarang SAMA PERSIS dengan yang saya periksa. Bila ada yang berbeda, skrip berhenti
    dan tidak mengubah apa pun. Isian yang sudah berisi nilai baru dilewati (aman diulang).
  - Sebelum menulis dibuat cadangan: data\\nuance_pairs.json.bak_nadalama_<tanggal-jam>
  - Format berkas dijaga persis (JSON indent 2, ensure_ascii=False, akhir baris CRLF).
    Skrip menolak bekerja bila format berkas sekarang tidak bisa ditulis ulang persis sama.
  - Setelah menulis, berkas dibaca ulang dan dibandingkan: hanya isian di atas yang boleh
    berbeda. Bila ada yang tidak cocok, berkas dikembalikan dari cadangan.
"""
import argparse
import copy
import json
import shutil
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PATH = ROOT / "data" / "nuance_pairs.json"

# (nomor, id pasangan, kata, isian, isi sekarang, isi baru)
PERBAIKAN = [
    (1, "b10_quede_chengjiu_3301", "取得", "example_pinyin", "Tā zài kǎoshì zhōng qǔdé le hǎo chéngjī.", "Tā zài kǎoshì zhōng qǔdé le hǎo chéngjì."),
    (2, "bA1_403", "查询", "example_pinyin", "Nǐ kěyǐ dēnglù wǎngzhàn cháxún kǎoshì chéngjī.", "Nǐ kěyǐ dēnglù wǎngzhàn cháxún kǎoshì chéngjì."),
    (3, "b32_payung_teduh_2466", "伞", "example_pinyin", "Chūmén biè wàng le dài sǎn.", "Chūmén bié wàng le dài sǎn."),
    (4, "bA1_499", "高涨", "example_pinyin", "Qiúmí de rèqíng kōngqián gāozhàng.", "Qiúmí de rèqíng kōngqián gāozhǎng."),
    (5, "bA1_196", "极小", "example_pinyin", "Zhè zhǒng bìngdú jíxiǎo, ròuyǎn kàn bùjiàn, liúxià wēixiǎo de hénjī.", "Zhè zhǒng bìngdú jíxiǎo, ròuyǎn kàn bùjiàn, liúxià wēixiǎo de hénjì."),
    (6, "b23_supply_demand_1870", "供", "example_pinyin", "Shìchǎng gòngyìng chōngzú.", "Shìchǎng gōngyìng chōngzú."),
    (7, "bA1_538", "宽厚", "example_pinyin", "Tā wèirén kuānhòu, cóng bù jìchóu.", "Tā wéirén kuānhòu, cóng bù jìchóu."),
    (8, "b30_suara_nada_2689", "声响", "example_pinyin", "Túrán chuánlái yī shēng jùxiǎng.", "Tūrán chuánlái yī shēng jùxiǎng."),
]


def cari_item(data, id_pasangan, kata):
    for p in data.get("pairs", []):
        if p.get("id") == id_pasangan:
            for it in p.get("comparison", []):
                if it.get("word") == kata:
                    return it
    return None


def tulis_teks(data, akhir_baris_akhir):
    return json.dumps(data, ensure_ascii=False, indent=2).replace("\n", "\r\n") + akhir_baris_akhir


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser(description="Perbaiki 8 salah tanda nada di data/nuance_pairs.json")
    ap.add_argument("--apply", action="store_true", help="benar-benar menulis (tanpa ini hanya menampilkan daftar)")
    a = ap.parse_args()

    if not PATH.exists():
        print("Tidak menemukan %s. Letakkan skrip ini di folder utama proyek (mis. C:\\mandarin_app)." % PATH)
        return 1
    print("Berkas: %s" % PATH)
    print("Mode: %s\n" % ("TERAPKAN (--apply)" if a.apply else "LIHAT-DULU (tidak mengubah apa pun)"))

    mentah = PATH.read_bytes().decode("utf-8")
    akhir = "\r\n" if mentah.endswith("\r\n") else ("\n" if mentah.endswith("\n") else "")
    data = json.loads(mentah)

    # Berkas harus bisa ditulis ulang persis sama, supaya hanya isian perbaikan yang berubah.
    if tulis_teks(data, akhir) != mentah:
        print("BERHENTI: format berkas sekarang tidak bisa ditulis ulang persis sama (akan ada perubahan tak terduga).")
        print("Tidak ada yang diubah. Kirim pesan ini ke Claude.")
        return 1

    rencana, sudah, masalah = [], 0, []
    for no, pid, kata, isian, lama, baru in PERBAIKAN:
        it = cari_item(data, pid, kata)
        label = "#%d  %s / %s / %s" % (no, pid, kata, isian)
        if it is None or isian not in it:
            masalah.append("%s -- pasangan, kata, atau isian tidak ditemukan" % label)
            continue
        skrg = it[isian]
        if skrg == lama:
            rencana.append((it, isian, baru))
            print(label)
            print("     sekarang : %s" % lama)
            print("     menjadi  : %s" % baru)
        elif skrg == baru:
            sudah += 1
            print(label)
            print("     sudah diperbaiki: %s" % baru)
        else:
            masalah.append("%s -- isi sekarang berbeda dari yang diperiksa: %s" % (label, skrg))

    print("\n" + "=" * 70)
    print("Akan diperbaiki: %d isian | sudah diperbaiki: %d | bermasalah: %d" % (len(rencana), sudah, len(masalah)))
    if masalah:
        print("\nBERHENTI (tidak ada yang diubah). Isian bermasalah:")
        for m in masalah:
            print("   " + m)
        print("Kirim pesan ini ke Claude.")
        return 1
    if not rencana:
        print("Tidak ada yang perlu diubah.")
        return 0
    if not a.apply:
        print("\nIni baru daftar; belum ada yang diubah. Untuk menerapkan: python perbaiki_nada_lama.py --apply")
        return 0

    # --- terapkan ---
    asli = copy.deepcopy(data)
    cadangan = PATH.with_name("nuance_pairs.json.bak_nadalama_" + datetime.now().strftime("%Y%m%d_%H%M%S"))
    shutil.copy2(PATH, cadangan)
    for it, isian, baru in rencana:
        it[isian] = baru
    PATH.write_bytes(tulis_teks(data, akhir).encode("utf-8"))

    # pemeriksaan akhir: baca ulang, hanya isian perbaikan yang boleh berbeda
    harapan = copy.deepcopy(asli)
    for no, pid, kata, isian, lama, baru in PERBAIKAN:
        it = cari_item(harapan, pid, kata)
        it[isian] = baru
    try:
        ulang = json.loads(PATH.read_bytes().decode("utf-8"))
        cocok = ulang == harapan and len(ulang["pairs"]) == len(asli["pairs"])
    except Exception:
        cocok = False
    if not cocok:
        shutil.copy2(cadangan, PATH)
        print("\nPEMERIKSAAN AKHIR GAGAL: berkas dikembalikan dari cadangan %s. Kirim pesan ini ke Claude." % cadangan.name)
        return 1
    print("\nSelesai: %d isian diperbaiki. Cadangan: %s" % (len(rencana), cadangan.name))
    print("Pemeriksaan akhir lolos (hanya isian di atas yang berubah; %d pasangan utuh)." % len(ulang["pairs"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())

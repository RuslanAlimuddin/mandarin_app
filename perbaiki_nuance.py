#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
perbaiki_nuance.py -- memperbaiki 11 temuan salah ketik di data/nuance_pairs.json
=================================================================================
Isi perbaikan (12 isian, karena temuan nomor 7 menyentuh dua isian):
   9 salah ketik pinyin pada kalimat contoh (闺女 Guīniū -> Guīnü, zugu, Landai, zhuammen,
     gaitai, mishi, quejia, xiūxiū, jùjù)
   2 salah ketik hanzi pada kalimat contoh: 想过 -> 想到 (pasangan 想起/想到) dan 的的 -> 的
   1 terjemahan Indonesia 良知: "akal sehat" -> "hati nurani"

CARA PAKAI (dari C:\\mandarin_app>):

  1) Lihat dulu (TIDAK mengubah apa pun):
         python perbaiki_nuance.py

  2) Terapkan:
         python perbaiki_nuance.py --apply

KEAMANAN
  - Tiap perbaikan dikenali dari id pasangan + kata + nama isian, dan hanya dijalankan bila
    isi sekarang SAMA PERSIS dengan yang saya periksa. Bila ada yang berbeda, skrip berhenti
    dan tidak mengubah apa pun. Isian yang sudah berisi nilai baru dilewati (aman diulang).
  - Sebelum menulis dibuat cadangan: data\\nuance_pairs.json.bak_nuance_<tanggal-jam>
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

# (nomor temuan, id pasangan, kata, isian, isi sekarang, isi baru)
PERBAIKAN = [
    (1, "b23_anak_perempuan_putri_2880", "闺女", "example_pinyin", "Guīniū huílái le!", "Guīnü huílái le!"),
    (2, "b9_shi_pin_357", "食物", "example_pinyin", "Women xuyao zugu de shiwu.", "Women xuyao zugou de shiwu."),
    (3, "b14_zao_cheng_452", "导致", "example_pinyin", "Landai daozhi le ta de shibai.", "Landuo daozhi le ta de shibai."),
    (4, "b19_dui_li_464", "针对", "example_pinyin", "Zhe shi zhuammen zhendui xinshou sheji de kecheng.", "Zhe shi zhuanmen zhendui xinshou sheji de kecheng."),
    (5, "b19_zhu_ce_618", "登记", "example_pinyin", "Qing zai gaitai dengji ruzhu.", "Qing zai guitai dengji ruzhu."),
    (6, "b26_jiao_dai_365", "吩咐", "example_pinyin", "Ta fenfu mishi zhunbei huiyi ziliao.", "Ta fenfu mishu zhunbei huiyi ziliao."),
    (7, "b34_liang_xin_529", "良知", "example_pinyin", "Ta quejia jiben de liangzhi.", "Ta quefa jiben de liangzhi."),
    (7, "b34_liang_xin_529", "良知", "example_id", "Dia kurang akal sehat dasar.", "Dia kurang memiliki hati nurani dasar."),
    (8, "b36_malu_minder_1777", "羞", "example_pinyin", "Tā xiūxiū de dīxiàle tóu.", "Tā hàixiū de dīxiàle tóu."),
    (9, "bA1_430", "急剧", "example_pinyin", "Wùjià zài jùjù shàngzhǎng.", "Wùjià zài jíjù shàngzhǎng."),
    (10, "b6_xiang_qi_223", "想到", "example_cn", "我没想过这个办法。", "我没想到这个办法。"),
    (11, "bA1_403", "询问", "example_cn", "他向前台询问了会议室的的位置。", "他向前台询问了会议室的位置。"),
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
    ap = argparse.ArgumentParser(description="Perbaiki 11 temuan di data/nuance_pairs.json")
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
        print("\nIni baru daftar; belum ada yang diubah. Untuk menerapkan: python perbaiki_nuance.py --apply")
        return 0

    # --- terapkan ---
    asli = copy.deepcopy(data)
    cadangan = PATH.with_name("nuance_pairs.json.bak_nuance_" + datetime.now().strftime("%Y%m%d_%H%M%S"))
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

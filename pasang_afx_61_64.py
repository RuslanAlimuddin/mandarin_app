#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pasang_afx_61_64.py -- menambah poin Tata Bahasa AFX.61-AFX.64 (族 迷 症 剂) untuk "Awalan & Akhiran".

Yang diubah (cadangan otomatis untuk tiap berkas, nama: <berkas>.bak_afx6164_<tanggal-jam>):
  1. data\\grammar_afiks.json : kategori K dan L (4 poin), metadata jadi 64 poin
  2. tatabahasa.html          : dua baris kelompok K dan L di Daftar Isi (topik "Prefix & Suffix (Imbuhan)")
  3. peta-bahasa.html         : teks Pilar 12 "AFX.01-AFX.60 (60 poin)" jadi 64 poin
Syarat: data\\afiks_kamus.json sudah berisi AFK-061 sampai AFK-064 (pasang_imbuhan_tingkat3.py).

CARA PAKAI (dari C:\\mandarin_app>):
  1) Lihat dulu (TIDAK mengubah apa pun):   python pasang_afx_61_64.py
  2) Pasang:                                python pasang_afx_61_64.py --apply
Aman diulang: bagian yang sudah terpasang dilewati.
"""
import json
import shutil
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
GRAM = ROOT / "data" / "grammar_afiks.json"
AFIKS = ROOT / "data" / "afiks_kamus.json"
KATA = ROOT / "data" / "app_words.json"
TB = ROOT / "tatabahasa.html"
PETA = ROOT / "peta-bahasa.html"

KAT = [("K", "K. Penggemar dan kelompok orang"), ("L", "L. Penyakit dan zat")]


def poin(no, kar, py, fungsi, pola, kal, kid):
    return {
        "id": "AFX.%02d" % no, "number": "AFX.%02d" % no,
        "title": "Akhiran —%s (%s)" % (kar, py), "fungsi": fungsi,
        "table": [{"jenis": "Afirmatif", "pola": pola, "contoh": c, "pinyin": p, "terjemahan": t}
                  for c, p, t in kal],
        "kamus_id": kid, "kamus_nama": kar,
    }


POIN = {
    "K": [
        poin(61, "族", "zú", "Menyebut suku bangsa atau sekelompok orang dengan ciri atau kebiasaan yang sama.",
             "Kata + 族",
             [("中国有很多民族。", "Zhōng guó yǒu hěn duō mín zú.", "Tiongkok punya banyak kelompok etnis."),
              ("他是上班族。", "Tā shì shàng bān zú.", "Dia seorang pekerja kantoran.")], "AFK-061"),
        poin(62, "迷", "mí", "Menyebut orang yang sangat menggemari suatu kegiatan atau tokoh.",
             "Bidang/tokoh + 迷",
             [("他是一个球迷。", "Tā shì yī gè qiú mí.", "Dia seorang penggemar bola."),
              ("我姐姐是影迷。", "Wǒ jiě jie shì yǐng mí.", "Kakak perempuan saya penggemar film.")], "AFK-062"),
    ],
    "L": [
        poin(63, "症", "zhèng", "Menyebut suatu penyakit atau kelainan dengan gejala tertentu.",
             "Penyebab/gejala + 症",
             [("医生说这是癌症。", "Yī shēng shuō zhè shì ái zhèng.", "Dokter mengatakan ini kanker."),
              ("他得了抑郁症。", "Tā dé le yì yù zhèng.", "Dia menderita depresi klinis.")], "AFK-063"),
        poin(64, "剂", "jì", "Menamai obat atau bahan olahan menurut fungsi atau jenisnya.",
             "Fungsi/jenis + 剂",
             [("运动员不能用兴奋剂。", "Yùn dòng yuán bù néng yòng xīng fèn jì.", "Atlet tidak boleh memakai doping."),
              ("这种洗涤剂很便宜。", "Zhè zhǒng xǐ dí jì hěn pián yi.", "Deterjen jenis ini sangat murah.")], "AFK-064"),
    ],
}


def fail(msg):
    print("GALAT: " + msg)
    sys.exit(1)


def cad(path, cap):
    c = path.with_name(path.name + ".bak_afx6164_" + cap)
    shutil.copy2(path, c)
    return c


def main():
    apply = "--apply" in sys.argv
    print("Mode: " + ("PASANG (--apply)" if apply else "LIHAT-DULU (tidak mengubah apa pun)"))
    kamus = {e["id"]: e for e in json.loads(AFIKS.read_text(encoding="utf-8"))}
    hsk = {w["simplified"]: w.get("hsk") for w in json.loads(KATA.read_text(encoding="utf-8"))}
    gram = json.loads(GRAM.read_text(encoding="utf-8"))
    ada = {p["id"] for c in gram["categories"] for p in c["points"]}

    # lengkapi tingkat HSK terendah dari kata contoh + pemeriksaan
    for k, daftar in POIN.items():
        for p in daftar:
            e = kamus.get(p["kamus_id"])
            if not e or e["karakter"] != p["kamus_nama"]:
                fail("%s belum ada di data\\afiks_kamus.json (jalankan pasang_imbuhan_tingkat3.py dulu)." % p["kamus_id"])
            lv = [int(hsk[c["kata"]]) for c in e["bagian"][0]["contoh"] if hsk.get(c["kata"])]
            if not lv:
                fail("tidak ada tingkat HSK untuk contoh %s" % p["kamus_nama"])
            p["tingkat_hsk_terendah"] = "HSK %d" % min(lv)
            p["sumber_tingkat_hsk"] = "data/app_words.json, kolom hsk"
            for r in p["table"]:
                if p["kamus_nama"] not in r["contoh"]:
                    fail("kalimat %s tidak memuat %s" % (r["contoh"], p["kamus_nama"]))

    # 1) grammar_afiks.json
    nama = [c["name"] for c in gram["categories"]]
    perlu_json = False
    for k, n in KAT:
        if n in nama:
            print("  lewati kategori (sudah ada): " + n)
            continue
        baru = [p for p in POIN[k] if p["id"] not in ada]
        gram["categories"].append({"name": n, "points": baru})
        perlu_json = True
        print("  tambah kategori %s: %s" % (n, ", ".join("%s %s (%s)" % (p["id"], p["kamus_nama"], p["tingkat_hsk_terendah"]) for p in baru)))
    total = sum(len(c["points"]) for c in gram["categories"])
    gram["metadata"]["total_points"] = total
    gram["metadata"]["groups_completed"] = [c["name"][0] for c in gram["categories"]]

    # 2) tatabahasa.html
    tb = TB.read_text(encoding="utf-8")
    jbaris = '  "J. Tingkat dan keseluruhan": "Prefix & Suffix (Imbuhan)",'
    perlu_tb = KAT[0][1] not in tb
    if perlu_tb:
        if tb.count(jbaris) != 1:
            fail("baris kelompok J tidak ditemukan tepat satu kali di tatabahasa.html")
        tambah = "".join('\n  "%s": "Prefix & Suffix (Imbuhan)",' % n for _, n in KAT)
        tb = tb.replace(jbaris, jbaris + tambah)
        print("  tatabahasa.html: tambah 2 baris Daftar Isi (K, L)")
    else:
        print("  lewati tatabahasa.html (sudah ada)")

    # 3) peta-bahasa.html
    pt = PETA.read_text(encoding="utf-8")
    lama, baru_t = "AFX.01–AFX.60 (60 poin)", "AFX.01–AFX.64 (64 poin)"
    perlu_pt = lama in pt
    if perlu_pt:
        pt = pt.replace(lama, baru_t)
        print("  peta-bahasa.html: 60 poin -> 64 poin")
    else:
        print("  lewati peta-bahasa.html (tidak ada teks lama)")

    print("  total poin AFX setelah pemasangan: %d" % total)
    if not (perlu_json or perlu_tb or perlu_pt):
        print("Tidak ada yang perlu diubah.")
        return
    if not apply:
        print("\nBelum ada yang diubah. Jika sudah sesuai, jalankan:  python pasang_afx_61_64.py --apply")
        return

    cap = time.strftime("%Y%m%d-%H%M%S")
    cs = []
    if perlu_json:
        cs.append((GRAM, cad(GRAM, cap)))
        GRAM.write_text(json.dumps(gram, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if perlu_tb:
        cs.append((TB, cad(TB, cap)))
        TB.write_text(tb, encoding="utf-8")
    if perlu_pt:
        cs.append((PETA, cad(PETA, cap)))
        PETA.write_text(pt, encoding="utf-8")

    cek = json.loads(GRAM.read_text(encoding="utf-8"))
    ids = [p["id"] for c in cek["categories"] for p in c["points"]]
    if len(ids) != 64 or len(set(ids)) != 64 or "AFX.64" not in ids:
        for asli, c in cs:
            shutil.copy2(c, asli)
        fail("pemeriksaan akhir gagal; semua berkas dikembalikan dari cadangan.")
    print("\nSelesai. Cadangan: " + ", ".join(c.name for _, c in cs))


if __name__ == "__main__":
    main()

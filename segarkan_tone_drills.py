#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
segarkan_tone_drills.py -- penyegaran data\\tone_drills.json (butir 4 rencana BLUEPRINT_v46) + 6 kata kapital dan urutan arti marga
==========================================================================================================
Keputusan رسلان (20-21 November 2026), dikerjakan berurutan (langkah yang sudah pernah dijalankan dilewati):

  LANGKAH 1  data\\app_words.json : enam kata biasa yang pinyin-nya tertulis berhuruf kapital karena arti
             pertamanya "marga" dijadikan huruf kecil (pinyin dan pinyin_numeric):
                 日 Rì -> rì (Ri4 -> ri4)      帅 Shuài -> shuài (Shuai4 -> shuai4)
                 遇 Yù -> yù (Yu4 -> yu4)       剪 Jiǎn -> jiǎn (Jian3 -> jian3)
                 景 Jǐng -> jǐng (Jing3 -> jing3)      安 Ān -> ān (An1 -> an1)  [ditemukan belakangan]
  LANGKAH 1b data\\app_words.json : arti "marga ..." (Inggris: "surname ...") di daftar arti 帅 遇 剪 景 闻 安 dipindah
             ke BAGIAN AKHIR daftar (seperti yang sudah terjadi pada 和 dan 从), supaya arti umumnya (tampan,
             bertemu, gunting, pemandangan, mendengar) menjadi arti pertama yang tampil.
  LANGKAH 2  data\\tone_drills.json : dibuat ulang dengan generator resmi skrip\\dari_py\\generate_tone_drills.py
             dari kamus yang sudah dibetulkan di langkah 1. Generator dipakai apa adanya (tidak diubah);
             skrip ini hanya membungkusnya dengan cadangan dan pemeriksaan.

  Dampak di aplikasi: soal "Pilih Nada" dan "Pilih Hanzi" berhenti memakai bacaan salah yang tertinggal
  (mis. 要 yāo -> yào, 说 shuì -> shuō, 上 shǎng -> shàng, 看 kān -> kàn) dan pinyin berhuruf kapital.

Skrip ini boleh dijalankan ulang: langkah 1 untuk 5 kata (日 帅 遇 剪 景) sudah dikerjakan pada 21 November, jadi yang baru
  hanya 安 (langkah 1 dan 1b) serta langkah 2.

Berkas pendukung yang HARUS ada: skrip\\dari_py\\generate_tone_drills.py (sudah ada di repo).

CARA PAKAI (dari C:\\mandarin_app>):

  1) Lihat dulu (TIDAK mengubah apa pun):   python segarkan_tone_drills.py
  2) Terapkan:                              python segarkan_tone_drills.py --apply

KEAMANAN
  - Hasil generator dibuat dulu di folder sementara dan DIPERIKSA sebelum menyentuh berkas aslimu:
    tiap soal "Pilih Nada" bernada 1-4 yang cocok dengan tanda nada pinyin-nya, tidak ada pinyin kapital pada
    kata satu karakter, tiap kelompok "Pilih Hanzi" punya minimal 2 hanzi berbeda dengan dasar pinyin yang
    sama, dan jumlahnya wajar dibanding berkas lama (selisih tidak lebih dari 10 persen).
  - Format app_words.json dijaga persis (JSON indent 2, ensure_ascii=False, akhir baris CRLF); perubahan kamus
    hanya dilakukan bila isian sekarang PERSIS bentuk lama (atau sudah bentuk baru).
  - Sebelum menulis dibuat dua cadangan:
        data\\app_words.json.bak_td_<tanggal-jam>   dan   data\\tone_drills.json.bak_td_<tanggal-jam>
  - Langkah 1b hanya memindahkan urutan arti (tidak ada arti yang dihapus, ditambah, atau diubah teksnya).
  - Setelah menulis, kedua berkas dibaca ulang dan dibandingkan dengan yang diharapkan; bila ada yang tidak
    cocok, KEDUA berkas dikembalikan dari cadangan.
  - Aman diulang: bila sudah mutakhir, dilaporkan "tidak ada yang perlu diubah".
  - Daftar lengkap selisih ditulis ke hasil_tone_drills.txt.
"""
import argparse
import contextlib
import copy
import importlib.util
import io
import json
import re
import shutil
import sys
import tempfile
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent
APP = ROOT / "data" / "app_words.json"
TD = ROOT / "data" / "tone_drills.json"
GEN = ROOT / "skrip" / "dari_py" / "generate_tone_drills.py"
HASIL = ROOT / "hasil_tone_drills.txt"

# langkah 1: (hanzi, (pinyin lama, pinyin_numeric lama), (pinyin baru, pinyin_numeric baru))
KAPITAL = [
    ("日", ("Rì", "Ri4"), ("rì", "ri4")),
    ("帅", ("Shuài", "Shuai4"), ("shuài", "shuai4")),
    ("遇", ("Yù", "Yu4"), ("yù", "yu4")),
    ("剪", ("Jiǎn", "Jian3"), ("jiǎn", "jian3")),
    ("景", ("Jǐng", "Jing3"), ("jǐng", "jing3")),
    ("安", ("Ān", "An1"), ("ān", "an1")),
]
# langkah 1b: kata yang arti "marga" (Inggris: "surname") di daftar artinya dipindah ke akhir
MARGA_AKHIR = ["帅", "遇", "剪", "景", "闻", "安"]
AWALAN_MARGA = {"meanings_id": "marga", "meanings_en": "surname"}
BATAS_SELISIH = 0.10
NADA = "āáǎàēéěèīíǐìōóǒòūúǔùǖǘǚǜ"


def tulis_teks(data, akhir):
    return json.dumps(data, ensure_ascii=False, indent=2).replace("\n", "\r\n") + akhir


def baca_app():
    mentah = APP.read_bytes().decode("utf-8")
    akhir = "\r\n" if mentah.endswith("\r\n") else ("\n" if mentah.endswith("\n") else "")
    data = json.loads(mentah)
    if tulis_teks(data, akhir) != mentah:
        return None, None
    return data, akhir


def rencana_kapital(app):
    """Kembalikan (daftar (indeks, kunci, lama, baru), jumlah_sudah, galat)."""
    daftar, sudah, galat = [], 0, []
    for hz, (py_l, num_l), (py_b, num_b) in KAPITAL:
        cocok = [i for i, e in enumerate(app) if e.get("simplified") == hz]
        if len(cocok) != 1:
            galat.append("%s: ditemukan %d entri (harus tepat 1)" % (hz, len(cocok)))
            continue
        e = app[cocok[0]]
        for kunci, lama, baru in (("pinyin", py_l, py_b), ("pinyin_numeric", num_l, num_b)):
            if e.get(kunci) == baru:
                sudah += 1
            elif e.get(kunci) == lama:
                daftar.append((cocok[0], kunci, lama, baru))
            else:
                galat.append("%s: isian %s sekarang %r, bukan %r (lama) atau %r (baru)" % (hz, kunci, e.get(kunci), lama, baru))
    return daftar, sudah, galat


def rencana_marga(app):
    """Kembalikan (daftar (indeks_entri, medan, teks_arti), jumlah_sudah, galat)."""
    daftar, sudah, galat = [], 0, []
    for hz in MARGA_AKHIR:
        cocok = [i for i, e in enumerate(app) if e.get("simplified") == hz]
        if len(cocok) != 1:
            galat.append("%s: ditemukan %d entri (harus tepat 1)" % (hz, len(cocok)))
            continue
        e = app[cocok[0]]
        for medan, awalan in AWALAN_MARGA.items():
            arti = e.get(medan, [])
            ada = [k for k, m in enumerate(arti) if m.lower().startswith(awalan)]
            if len(ada) != 1:
                galat.append("%s: %s memuat %d arti berawalan '%s' (harus tepat 1)" % (hz, medan, len(ada), awalan))
            elif ada[0] == len(arti) - 1:
                sudah += 1
            else:
                daftar.append((cocok[0], medan, arti[ada[0]]))
    return daftar, sudah, galat


def pindah_marga(app, daftar):
    for i, medan, teks in daftar:
        arti = app[i][medan]
        arti.remove(teks)
        arti.append(teks)


def muat_generator():
    spec = importlib.util.spec_from_file_location("generate_tone_drills", str(GEN))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def buat_baru(app_data):
    """Jalankan generator resmi pada data kamus (di folder sementara) dan kembalikan hasilnya (dict)."""
    mod = muat_generator()
    with tempfile.TemporaryDirectory() as tmp:
        masuk = Path(tmp) / "app_words.json"
        keluar = Path(tmp) / "tone_drills.json"
        masuk.write_text(json.dumps(app_data, ensure_ascii=False), encoding="utf-8")
        mod.INPUT_PATH = str(masuk)
        mod.OUTPUT_PATH = str(keluar)
        with contextlib.redirect_stdout(io.StringIO()):
            mod.main()
        return json.loads(keluar.read_text(encoding="utf-8")), mod


def periksa(baru, lama, mod):
    """Daftar masalah (kosong = lolos)."""
    masalah = []
    for e in baru["singles"]:
        if not all(k in e for k in ("cn", "py", "id", "hsk", "tone", "base")):
            masalah.append("soal Pilih Nada tidak lengkap: %r" % (e,))
            continue
        if mod.single_syllable_tone(e["py"]) != e["tone"] or e["tone"] not in (1, 2, 3, 4):
            masalah.append("nada tidak cocok dengan pinyin: %s %s %s" % (e["cn"], e["py"], e["tone"]))
        if e["base"] != mod.toneless_pinyin(e["py"]):
            masalah.append("dasar pinyin tidak cocok: %s %s %s" % (e["cn"], e["py"], e["base"]))
        if len(e["cn"]) == 1 and e["py"] != e["py"].lower():
            masalah.append("pinyin kapital pada kata satu karakter: %s %s" % (e["cn"], e["py"]))
        if not any(ch in NADA for ch in e["py"]):
            masalah.append("tanpa tanda nada: %s %s" % (e["cn"], e["py"]))
    for dasar, daftar in baru["groups"].items():
        hanzi = [e["cn"] for e in daftar]
        if len(set(hanzi)) < 2 or len(hanzi) != len(set(hanzi)):
            masalah.append("kelompok %s tidak punya >=2 hanzi berbeda tanpa duplikat: %s" % (dasar, hanzi))
        for e in daftar:
            if mod.toneless_pinyin(e["py"]) != dasar:
                masalah.append("kelompok %s memuat %s %s yang dasarnya lain" % (dasar, e["cn"], e["py"]))
            if len(e["cn"]) == 1 and e["py"] != e["py"].lower():
                masalah.append("pinyin kapital pada kata satu karakter di kelompok %s: %s %s" % (dasar, e["cn"], e["py"]))
    for nama, a, b in (("singles", len(baru["singles"]), len(lama["singles"])),
                       ("kelompok", len(baru["groups"]), len(lama["groups"]))):
        if b and abs(a - b) / b > BATAS_SELISIH:
            masalah.append("jumlah %s berubah terlalu jauh: %d -> %d" % (nama, b, a))
    return masalah


def bandingkan(lama, baru):
    """Kembalikan (ringkasan dict, baris laporan)."""
    oc = {e["cn"]: e for e in lama["singles"]}
    nc = {e["cn"]: e for e in baru["singles"]}
    ubah = [(c, oc[c]["py"], nc[c]["py"]) for c in oc if c in nc and oc[c]["py"] != nc[c]["py"]]
    kapital = [x for x in ubah if x[1].lower() == x[2].lower()]
    beda = [x for x in ubah if x[1].lower() != x[2].lower()]
    keluar = [c for c in oc if c not in nc]
    masuk = [c for c in nc if c not in oc]
    arti = [(c, oc[c]["id"], nc[c]["id"]) for c in oc if c in nc and oc[c]["py"] == nc[c]["py"]
            and (oc[c]["id"] != nc[c]["id"] or oc[c]["hsk"] != nc[c]["hsk"])]
    go, gn = set(lama["groups"]), set(baru["groups"])
    isi = []
    for b in sorted(go & gn):
        o = {(e["cn"], e["py"]) for e in lama["groups"][b]}
        n = {(e["cn"], e["py"]) for e in baru["groups"][b]}
        if o != n:
            isi.append((b, sorted(o - n), sorted(n - o)))
    ring = dict(ubah=len(ubah), kapital=len(kapital), beda=len(beda), keluar=keluar, masuk=masuk, arti=len(arti),
                g_tambah=sorted(gn - go), g_hilang=sorted(go - gn), g_isi=len(isi))
    baris = ["## SINGLES (Pilih Nada): bacaan nada/bunyi yang BERBEDA (%d)" % len(beda)]
    baris += ["   %s  %s -> %s" % x for x in beda]
    baris += ["", "## SINGLES: hanya huruf kapital menjadi kecil (%d)" % len(kapital)]
    baris += ["   %s  %s -> %s" % x for x in kapital]
    baris += ["", "## SINGLES: keluar dari soal (%d): %s" % (len(keluar), " ".join(keluar)),
              "## SINGLES: masuk ke soal (%d): %s" % (len(masuk), " ".join(masuk)),
              "", "## SINGLES: arti atau HSK berubah (%d)" % len(arti)]
    baris += ["   %s  %s -> %s" % x for x in arti]
    baris += ["", "## GRUP (Pilih Hanzi): kunci ditambah %s | hilang %s" % (ring["g_tambah"], ring["g_hilang"]),
              "## GRUP: isi berubah (%d)" % len(isi)]
    for b, k, m in isi:
        baris.append("   %s  keluar %s  masuk %s" % (b, k, m))
    return ring, baris


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser(description="Betulkan kata kapital, urutan arti marga, dan buat ulang tone_drills.json")
    ap.add_argument("--apply", action="store_true", help="benar-benar menulis (tanpa ini hanya menampilkan ringkasan)")
    a = ap.parse_args()
    print("Mode: %s\n" % ("TERAPKAN (--apply)" if a.apply else "LIHAT-DULU (tidak mengubah apa pun)"))

    for p in (APP, TD, GEN):
        if not p.exists():
            print("Tidak menemukan %s. Letakkan skrip ini di folder utama proyek (mis. C:\\mandarin_app)." % p)
            return 1
    app, akhir = baca_app()
    if app is None:
        print("BERHENTI: format app_words.json sekarang tidak bisa ditulis ulang persis sama (akan ada perubahan tak terduga).")
        print("Tidak ada yang diubah. Kirim pesan ini ke Claude.")
        return 1

    # ---- langkah 1
    pk, sudah, galat = rencana_kapital(app)
    print("=== Langkah 1. data\\app_words.json: kata biasa berpinyin kapital ===")
    if galat:
        print("BERHENTI: isian kamus tidak seperti yang diharapkan:")
        for g in galat:
            print("     " + g)
        print("Tidak ada yang diubah. Kirim pesan ini ke Claude.")
        return 1
    print("Isian yang akan diubah: %d  (sudah benar: %d)" % (len(pk), sudah))
    for i, kunci, lama, baru in pk:
        print("   %-3s %-15s %s -> %s" % (app[i]["simplified"], kunci, lama, baru))
    app_baru = copy.deepcopy(app)
    for i, kunci, lama, baru in pk:
        app_baru[i][kunci] = baru

    mk, sudah_m, galat_m = rencana_marga(app_baru)
    print("\n=== Langkah 1b. data\\app_words.json: arti \"marga\" dipindah ke akhir daftar arti ===")
    if galat_m:
        print("BERHENTI: daftar arti tidak seperti yang diharapkan:")
        for g in galat_m:
            print("     " + g)
        print("Tidak ada yang diubah. Kirim pesan ini ke Claude.")
        return 1
    print("Daftar arti yang akan diubah: %d  (sudah benar: %d)" % (len(mk), sudah_m))
    for i, medan, teks in mk:
        arti = app_baru[i][medan]
        print("   %-3s %-12s \"%s\"  (urutan %d -> %d, arti pertama baru: \"%s\")" % (
            app_baru[i]["simplified"], medan, teks, arti.index(teks) + 1, len(arti),
            [m for m in arti if m != teks][0][:40]))
    pindah_marga(app_baru, mk)

    # ---- langkah 2
    print("\n=== Langkah 2. data\\tone_drills.json dibuat ulang (generator resmi, di folder sementara) ===")
    lama_td = json.loads(TD.read_bytes().decode("utf-8"))
    try:
        baru_td, mod = buat_baru(app_baru)
    except Exception as e:
        print("BERHENTI: generator gagal dijalankan: %s" % e)
        print("Tidak ada yang diubah. Kirim pesan ini ke Claude.")
        return 1
    masalah = periksa(baru_td, lama_td, mod)
    print("Soal 'Pilih Nada'  (singles): %d -> %d" % (len(lama_td["singles"]), len(baru_td["singles"])))
    print("Soal 'Pilih Hanzi' (grup)   : %d -> %d grup, %d -> %d kata" % (
        len(lama_td["groups"]), len(baru_td["groups"]),
        sum(len(v) for v in lama_td["groups"].values()), sum(len(v) for v in baru_td["groups"].values())))
    ring, baris_selisih = bandingkan(lama_td, baru_td)
    print("Bacaan 'Pilih Nada' yang berubah: %d  (nada atau bunyi benar-benar beda: %d, hanya kapital menjadi kecil: %d)" % (
        ring["ubah"], ring["beda"], ring["kapital"]))
    print("Keluar dari 'Pilih Nada': %d (%s)   Masuk: %d (%s)" % (
        len(ring["keluar"]), " ".join(ring["keluar"]), len(ring["masuk"]), " ".join(ring["masuk"])))
    print("Arti/HSK yang berubah di 'Pilih Nada': %d" % ring["arti"])
    print("Grup 'Pilih Hanzi': ditambah %s, hilang %s, isi berubah: %d" % (ring["g_tambah"], ring["g_hilang"], ring["g_isi"]))
    if masalah:
        print("\nPEMERIKSAAN HASIL GAGAL (%d masalah):" % len(masalah))
        for m in masalah[:15]:
            print("     " + m)
        print("Tidak ada yang diubah. Kirim pesan ini ke Claude.")
        return 1
    print("Pemeriksaan hasil: lolos.")

    teks_td = tulis_teks(baru_td, "")
    sama_td = TD.read_bytes().decode("utf-8") == teks_td
    baris = ["PENYEGARAN tone_drills.json -- %d isian kamus, %d daftar arti, %d bacaan Pilih Nada berubah" % (len(pk), len(mk), ring["ubah"]), ""]
    baris += ["## KAMUS (app_words.json)"] + ["   %s | %s | %s -> %s" % (app[i]["simplified"], k, l, b) for i, k, l, b in pk]
    baris += ["   %s | %s | arti \"%s\" dipindah ke akhir daftar" % (app[i]["simplified"], medan, teks) for i, medan, teks in mk]
    baris += [""] + baris_selisih
    if not pk and not mk and sama_td:
        print("\nTidak ada yang perlu diubah.")
        return 0
    if not a.apply:
        HASIL.write_text("\r\n".join(baris) + "\r\n", encoding="utf-8-sig")
        print("\nIni baru ringkasan; belum ada yang diubah. Daftar lengkap: %s" % HASIL.name)
        print("Untuk menerapkan: python segarkan_tone_drills.py --apply")
        return 0

    # ---- terapkan
    cap = datetime.now().strftime("%Y%m%d_%H%M%S")
    cad_a = APP.with_name("app_words.json.bak_td_" + cap)
    cad_t = TD.with_name("tone_drills.json.bak_td_" + cap)
    shutil.copy2(APP, cad_a)
    shutil.copy2(TD, cad_t)
    ok = True
    try:
        if pk or mk:
            APP.write_bytes(tulis_teks(app_baru, akhir).encode("utf-8"))
        TD.write_bytes(teks_td.encode("utf-8"))
        ulang_a = json.loads(APP.read_bytes().decode("utf-8"))
        ulang_t = json.loads(TD.read_bytes().decode("utf-8"))
        ok = ulang_a == app_baru and ulang_t == baru_td and len(ulang_a) == len(app)
    except Exception as e:
        ok = False
        print("Galat saat menulis: %s" % e)
    if not ok:
        shutil.copy2(cad_a, APP)
        shutil.copy2(cad_t, TD)
        print("\nPEMERIKSAAN AKHIR GAGAL: kedua berkas dikembalikan dari cadangan. Kirim pesan ini ke Claude.")
        return 1
    HASIL.write_text("\r\n".join(baris) + "\r\n", encoding="utf-8-sig")
    print("\nSelesai: %d isian kamus dibetulkan, %d daftar arti diurutkan ulang, dan tone_drills.json dibuat ulang." % (len(pk), len(mk)))
    print("Cadangan: %s dan %s" % (cad_a.name, cad_t.name))
    print("Pemeriksaan akhir lolos (kamus hanya berubah pada isian yang direncanakan; %d kata kamus utuh)." % len(ulang_a))
    print("Daftar lengkap selisih: %s" % HASIL.name)
    return 0


if __name__ == "__main__":
    sys.exit(main())

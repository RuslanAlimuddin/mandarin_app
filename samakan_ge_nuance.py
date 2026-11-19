#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
samakan_ge_nuance.py -- menyamakan 个 penggolong menjadi netral "ge" pada contoh lama
====================================================================================
Tahap 3 dari penyamaan 1.868 contoh lama (butir 3 rencana v45). Data lama menulis 个 kadang "gè"
kadang "ge" (yígè, měi gè, xià gè, wǔ gè rén ... lawan zhège, měi ge, xià ge). 716 contoh baru dan
sebagian contoh lama sudah memakai "ge" netral. Skrip ini menyamakan sisanya.

   gè -> ge : 个 sebagai penggolong (一个, 几个, 五个, 每个, 下个月, 是个, 那个 ...)
   tetap gè : 个 di awal kata (个人, 个性, 个子) dan 整个 (kata tersendiri: zhěnggè, "seluruh")

Yang diubah HANYA satu huruf per 个: "è" menjadi "e" di isian example_pinyin. Susunan spasi,
huruf kapital, dan tanda baca tidak disentuh (mis. "yígè" menjadi "yíge", "wǔ gè rén" menjadi
"wǔ ge rén"). Nada netral lain dikerjakan di tahap 4.

Berkas pendukung yang HARUS ada di folder yang sama: daftar_nada_nuance.py

CARA PAKAI (dari C:\\mandarin_app>):

  1) Lihat dulu (TIDAK mengubah apa pun):
         python samakan_ge_nuance.py

  2) Terapkan:
         python samakan_ge_nuance.py --apply

KEAMANAN
  - Bila pinyin lama tidak bisa disejajarkan dengan hanzi, atau suku kata 个 di data lama bukan
    "gè"/"ge", atau aturan menghendaki "gè" tetapi data lama menulis "ge", skrip berhenti dan
    melapor tanpa mengubah apa pun.
  - Format berkas dijaga persis (JSON indent 2, ensure_ascii=False, akhir baris CRLF); skrip
    menolak bekerja bila format berkas sekarang tidak bisa ditulis ulang persis sama.
  - Sebelum menulis dibuat cadangan: data\\nuance_pairs.json.bak_ge_<tanggal-jam>
  - Setelah menulis, berkas dibaca ulang dan dibandingkan: hanya isian example_pinyin yang boleh
    berbeda, dan di tiap isian hanya huruf "è" milik suku kata 个 (menjadi "e"). Bila ada yang
    tidak cocok, berkas dikembalikan dari cadangan.
  - Aman diulang: yang sudah "ge" dilewati.
  - Daftar lengkap perubahan (lama -> baru) ditulis ke hasil_ge_nuance.txt.
"""
import argparse
import copy
import json
import re
import shutil
import sys
import unicodedata
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
try:
    import daftar_nada_nuance as dn
except ImportError:
    print("Tidak menemukan daftar_nada_nuance.py di folder yang sama. Letakkan keduanya di C:\\mandarin_app.")
    sys.exit(1)

PATH = ROOT / "data" / "nuance_pairs.json"
HASIL = ROOT / "hasil_ge_nuance.txt"

# 个 yang didahului karakter ini TIDAK diubah (kata tersendiri, bukan penggolong biasa)
KECUALI_SEBELUM = {"整"}   # 整个 zhěnggè


def tulis_teks(data, akhir_baris_akhir):
    return json.dumps(data, ensure_ascii=False, indent=2).replace("\n", "\r\n") + akhir_baris_akhir


def _bacaan_lain(hz, app_idx, cc_idx):
    """Semua bacaan satu suku kata untuk karakter tunggal hz (terkurasi dulu, lalu CC-CEDICT)."""
    hasil = []
    for sumber in (app_idx.get(hz, []), cc_idx.get(hz, [])):
        for r in sumber:
            for sy in dn.pecah_suku(r):
                if sy.lower() not in [x.lower() for x in hasil]:
                    hasil.append(sy.lower())
    return hasil


def selaraskan(cn, py, app_idx, cc_idx):
    """Pecah hanzi sehingga huruf (tanpa nada) cocok dengan pinyin lama. Kembalikan (items, idx, huruf) atau None.
    Bila gagal, coba bacaan lain untuk karakter berbacaan ganda yang berdiri sendiri (mis. 都 dū di 文化之都)."""
    t = "".join(ch for ch in unicodedata.normalize("NFD", py) if unicodedata.category(ch) != "Mn").replace("ü", "u")
    ada_nama = bool(re.search(r"[a-z]\s+[A-Z]|[,;:]\s*[A-Z]", t))
    idx = [i for i, ch in enumerate(py) if ch.isalpha()]
    huruf = [py[i] for i in idx]
    polos = "".join(dn.tanpa_nada(ch) for ch in huruf)
    larang, longgar = set(), False
    pertama = None
    for _ in range(5):
        items, gagal = dn.suku_kata_per_karakter(cn, app_idx, cc_idx, frozenset(larang), longgar, ada_nama)
        if gagal:
            return None
        dn.terapkan_yi(items)
        if pertama is None:
            pertama = items
        if polos == "".join(dn.tanpa_nada(it["syl"]) for it in items):
            return items, idx, huruf
        tambahan = {it["seg"] for it in items if len(it["seg"]) > 1 and it["risiko"]}
        if tambahan and not tambahan <= larang:
            larang |= tambahan
            continue
        if not longgar:
            longgar = True
            continue
        break
    # langkah toleran: ganti bacaan karakter berbacaan ganda yang berdiri sendiri
    if pertama is None:
        return None
    var = [k for k, it in enumerate(pertama) if it["risiko"] and len(it["seg"]) == 1][:4]
    if not var:
        return None
    import itertools
    pilihan = [_bacaan_lain(pertama[k]["hz"], app_idx, cc_idx)[:5] for k in var]
    for kombinasi in itertools.product(*pilihan):
        items = copy.deepcopy(pertama)
        for k, sy in zip(var, kombinasi):
            items[k]["syl"] = sy
        dn.terapkan_yi(items)
        if polos == "".join(dn.tanpa_nada(it["syl"]) for it in items):
            return items, idx, huruf
    return None


def usul_ge(cn, py, app_idx, cc_idx):
    """Kembalikan (daftar_perubahan, galat). perubahan = (posisi_karakter_e, suku_lama, suku_baru)."""
    if unicodedata.normalize("NFC", py) != py:
        return None, "pinyin lama tidak dalam bentuk NFC"
    hasil = selaraskan(cn, py, app_idx, cc_idx)
    if hasil is None:
        return None, "pinyin lama tidak bisa disejajarkan dengan hanzi"
    items, idx, huruf = hasil
    perubahan = []
    pos = 0
    for k, it in enumerate(items):
        n = len(dn.tanpa_nada(it["syl"]))
        if it["hz"] == "个":
            lama = "".join(huruf[pos:pos + n])
            if dn.tanpa_nada(lama) != "ge" or lama.lower() not in ("gè", "ge"):
                return None, "suku kata 个 di data lama bukan gè/ge: " + lama
            sebelum = items[k - 1]["hz"] if k > 0 else ""
            if sebelum in KECUALI_SEBELUM:
                pass   # 整个: dibiarkan
            elif it["syl"] == "ge" and lama.lower() == "gè":
                perubahan.append((idx[pos + 1], lama, lama[0] + "e"))
            elif it["syl"] == "gè" and lama.lower() == "ge":
                return None, "aturan menghendaki gè (个人/个性/个子) tetapi data lama menulis ge: " + cn
        pos += n
    return perubahan, None


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser(description="Samakan 个 penggolong menjadi 'ge' pada contoh lama di data/nuance_pairs.json")
    ap.add_argument("--apply", action="store_true", help="benar-benar menulis (tanpa ini hanya menampilkan ringkasan)")
    a = ap.parse_args()

    if not PATH.exists():
        print("Tidak menemukan %s. Letakkan skrip ini di folder utama proyek (mis. C:\\mandarin_app)." % PATH)
        return 1
    print("Berkas: %s" % PATH)
    print("Mode: %s\n" % ("TERAPKAN (--apply)" if a.apply else "LIHAT-DULU (tidak mengubah apa pun)"))

    mentah = PATH.read_bytes().decode("utf-8")
    akhir = "\r\n" if mentah.endswith("\r\n") else ("\n" if mentah.endswith("\n") else "")
    data = json.loads(mentah)
    if tulis_teks(data, akhir) != mentah:
        print("BERHENTI: format berkas sekarang tidak bisa ditulis ulang persis sama (akan ada perubahan tak terduga).")
        print("Tidak ada yang diubah. Kirim pesan ini ke Claude.")
        return 1

    _, app_idx, cc_idx = dn.muat()

    rencana = []   # (pi, ci, lama, baru, posisi_berubah, id, kata, hanzi)
    masalah = []
    tanpa_ge = sudah_sesuai = kemunculan = 0
    for pi, p in enumerate(data["pairs"]):
        for ci, c in enumerate(p["comparison"]):
            cn = c.get("example_cn", "")
            py = c.get("example_pinyin", "")
            if "个" not in cn:
                tanpa_ge += 1
                continue
            label = "%s / %s" % (p["id"], c["word"])
            perubahan, galat = usul_ge(cn, py, app_idx, cc_idx)
            if galat:
                masalah.append("%s -- %s | %s | %s" % (label, galat, cn, py))
                continue
            if not perubahan:
                sudah_sesuai += 1
                continue
            baru = list(py)
            for pos, lama, nbaru in perubahan:
                baru[pos] = "e"
                kemunculan += 1
            rencana.append((pi, ci, py, "".join(baru), [x[0] for x in perubahan], p["id"], c["word"], cn))

    print("Contoh tanpa 个                       : %d" % tanpa_ge)
    print("Contoh dengan 个 yang sudah sesuai    : %d" % sudah_sesuai)
    print("Contoh dengan 个 yang akan diubah     : %d  (kemunculan gè -> ge: %d)" % (len(rencana), kemunculan))
    print("Bermasalah                            : %d" % len(masalah))
    if masalah:
        print("\nBERHENTI (tidak ada yang diubah). Isian bermasalah:")
        for m in masalah:
            print("   " + m)
        print("Kirim pesan ini ke Claude.")
        return 1
    if not rencana:
        print("Tidak ada yang perlu diubah.")
        return 0

    print("\nContoh perubahan (12 pertama):")
    for r in rencana[:12]:
        print("   %s\n      %s\n      -> %s" % (r[7], r[2], r[3]))

    baris = ["DAFTAR PERUBAHAN 个 gè -> ge (lama -> baru) -- %d isian" % len(rencana), ""]
    for r in rencana:
        baris.append("%s / %s" % (r[5], r[6]))
        baris.append("   %s" % r[7])
        baris.append("   lama: %s" % r[2])
        baris.append("   baru: %s" % r[3])
    if not a.apply:
        print("\nIni baru ringkasan; belum ada yang diubah. Untuk menerapkan: python samakan_ge_nuance.py --apply")
        return 0

    # --- terapkan ---
    asli = copy.deepcopy(data)
    cadangan = PATH.with_name("nuance_pairs.json.bak_ge_" + datetime.now().strftime("%Y%m%d_%H%M%S"))
    shutil.copy2(PATH, cadangan)
    for pi, ci, lama, baru, pos, pid, kata, cn in rencana:
        data["pairs"][pi]["comparison"][ci]["example_pinyin"] = baru
    PATH.write_bytes(tulis_teks(data, akhir).encode("utf-8"))

    # pemeriksaan akhir: hanya example_pinyin yang boleh berbeda, dan hanya "è" -> "e" milik 个
    harapan = copy.deepcopy(asli)
    ok = True
    for pi, ci, lama, baru, pos, pid, kata, cn in rencana:
        harapan["pairs"][pi]["comparison"][ci]["example_pinyin"] = baru
        beda = [i for i, (x, y) in enumerate(zip(lama, baru)) if x != y]
        if len(lama) != len(baru) or sorted(beda) != sorted(pos) \
                or any(lama[i] != "è" or baru[i] != "e" for i in beda):
            ok = False
    try:
        ulang = json.loads(PATH.read_bytes().decode("utf-8"))
        cocok = ok and ulang == harapan and len(ulang["pairs"]) == len(asli["pairs"])
    except Exception:
        cocok = False
    if not cocok:
        shutil.copy2(cadangan, PATH)
        print("\nPEMERIKSAAN AKHIR GAGAL: berkas dikembalikan dari cadangan %s. Kirim pesan ini ke Claude." % cadangan.name)
        return 1
    HASIL.write_text("\r\n".join(baris) + "\r\n", encoding="utf-8-sig")
    print("\nSelesai: %d isian diperbaiki. Cadangan: %s" % (len(rencana), cadangan.name))
    print("Pemeriksaan akhir lolos (hanya huruf è milik 个 yang berubah; %d pasangan utuh)." % len(ulang["pairs"]))
    print("Daftar lengkap perubahan: %s" % HASIL.name)
    return 0


if __name__ == "__main__":
    sys.exit(main())

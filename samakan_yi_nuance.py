#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
samakan_yi_nuance.py -- menyamakan nada 一 pada contoh pinyin lama dengan aturan sandhi
=======================================================================================
Tahap 2 dari penyamaan 1.868 contoh lama (butir 3 rencana v45). Contoh lama menulis 一 tanpa
perubahan nada (yī, yīgè, yīxià); 716 contoh baru memakai nada sebenarnya. Skrip ini menyamakan
contoh lama dengan aturan yang sama:

   yī  : 一 sendiri, di akhir kalimat, sesudah angka/urutan (十一, 第一), sebelum 月 号 日 atau angka
   yí  : 一 sebelum nada 4 (termasuk 个 yang netral): yí ge, yí xià, yí yàng, yí dìng
   yì  : 一 sebelum nada 1, 2, 3: yì qǐ, yì xiē, yì zhí, yì diǎn, yì bǎi

Yang diubah HANYA dua huruf suku kata 一 (yī -> yí atau yì) di isian example_pinyin. Kata lain,
huruf kapital, spasi, dan tanda baca tidak disentuh (个 dan nada netral dikerjakan di tahap 3 dan 4).

Berkas pendukung yang HARUS ada di folder yang sama: daftar_nada_nuance.py (versi terbaru)

CARA PAKAI (dari C:\\mandarin_app>):

  1) Lihat dulu (TIDAK mengubah apa pun):
         python samakan_yi_nuance.py

  2) Terapkan:
         python samakan_yi_nuance.py --apply

KEAMANAN
  - PENJAGA: bila ada 一 pada pola khusus yang aturannya berbeda (星期一/周一/礼拜一, kata yang
    berakhiran 一 seperti 统一 唯一 之一 同一 单一 专一, pola ulang seperti 看一看), skrip berhenti
    dan melapor tanpa mengubah apa pun. (Di datamu saat ini tidak ada pola itu.)
  - Bila suku kata 一 di data lama bukan yī/yí/yì, atau pinyin lama tidak bisa disejajarkan
    dengan hanzi, skrip berhenti dan melapor.
  - Format berkas dijaga persis (JSON indent 2, ensure_ascii=False, akhir baris CRLF); skrip
    menolak bekerja bila format berkas sekarang tidak bisa ditulis ulang persis sama.
  - Sebelum menulis dibuat cadangan: data\\nuance_pairs.json.bak_yi_<tanggal-jam>
  - Setelah menulis, berkas dibaca ulang dan dibandingkan: hanya isian example_pinyin yang boleh
    berbeda, dan di tiap isian hanya huruf suku kata 一. Bila ada yang tidak cocok, berkas
    dikembalikan dari cadangan.
  - Aman diulang: yang sudah sesuai aturan dilewati.
  - Daftar lengkap perubahan (lama -> baru) ditulis ke hasil_yi_nuance.txt.
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
HASIL = ROOT / "hasil_yi_nuance.txt"

# pola khusus yang aturannya berbeda: bila muncul, skrip berhenti (tidak menebak)
PENJAGA = [
    (re.compile(r"(星期|周|礼拜)一"), "hari Senin (星期一/周一): 一 tetap yī"),
    (re.compile(r"(统|唯|同|单|专|之|归|合|划)一"), "kata berakhiran 一 (统一 唯一 之一 ...): 一 tetap yī"),
    (re.compile(r"(.)一\1"), "pola ulang (看一看 ...): 一 dibaca netral"),
]


def tulis_teks(data, akhir_baris_akhir):
    return json.dumps(data, ensure_ascii=False, indent=2).replace("\n", "\r\n") + akhir_baris_akhir


def indeks_huruf(py):
    return [i for i, ch in enumerate(py) if ch.isalpha()]


def usul_yi(cn, py, app_idx, cc_idx):
    """Kembalikan (daftar_perubahan, galat). perubahan = (posisi_karakter_y, suku_lama, suku_baru)."""
    if unicodedata.normalize("NFC", py) != py:
        return None, "pinyin lama tidak dalam bentuk NFC"
    for rx, ket in PENJAGA:
        if rx.search(cn):
            return None, "pola khusus: " + ket
    t = "".join(ch for ch in unicodedata.normalize("NFD", py) if unicodedata.category(ch) != "Mn").replace("ü", "u")
    ada_nama = bool(re.search(r"[a-z]\s+[A-Z]|[,;:]\s*[A-Z]", t))
    idx = indeks_huruf(py)
    huruf = [py[i] for i in idx]
    polos_lama = "".join(dn.tanpa_nada(ch) for ch in huruf)
    items = None
    galat = "pinyin lama tidak bisa disejajarkan dengan hanzi"
    for longgar in (False, True):   # percobaan kedua: izinkan kata CC-CEDICT yang memuat karakter berisiko (心地 xīndì)
        items, gagal = dn.suku_kata_per_karakter(cn, app_idx, cc_idx, frozenset(), longgar, ada_nama)
        if gagal:
            galat = "hanzi tak bisa dipecah: " + gagal
            items = None
            continue
        dn.terapkan_yi(items)
        if polos_lama == "".join(dn.tanpa_nada(it["syl"]) for it in items):
            galat = None
            break
        items = None
        galat = "pinyin lama tidak bisa disejajarkan dengan hanzi"
    if items is None:
        return None, galat
    perubahan = []
    pos = 0
    for it in items:
        n = len(dn.tanpa_nada(it["syl"]))
        if it["hz"] == "一":
            if it["risiko"]:
                return None, "一 sebelum suku kata netral: perlu dilihat manual"
            lama = "".join(huruf[pos:pos + n])
            if lama.lower() not in ("yī", "yí", "yì"):
                return None, "suku kata 一 di data lama bukan yī/yí/yì: " + lama
            baru = it["syl"]
            if lama[:1].isupper():
                baru = baru[:1].upper() + baru[1:]
            if baru != lama:
                perubahan.append((idx[pos], lama, baru))
        pos += n
    return perubahan, None


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser(description="Samakan nada 一 pada contoh lama di data/nuance_pairs.json")
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

    rencana = []   # (pi, ci, pinyin_lama, pinyin_baru, posisi_berubah, id, kata, hanzi)
    masalah = []
    tanpa_yi = sudah_sesuai = 0
    jenis = {}
    for pi, p in enumerate(data["pairs"]):
        for ci, c in enumerate(p["comparison"]):
            cn = c.get("example_cn", "")
            py = c.get("example_pinyin", "")
            if "一" not in cn:
                tanpa_yi += 1
                continue
            label = "%s / %s" % (p["id"], c["word"])
            perubahan, galat = usul_yi(cn, py, app_idx, cc_idx)
            if galat:
                masalah.append("%s -- %s | %s | %s" % (label, galat, cn, py))
                continue
            if not perubahan:
                sudah_sesuai += 1
                continue
            baru = list(py)
            for pos, lama, nbaru in perubahan:
                baru[pos] = nbaru[0]
                baru[pos + 1] = nbaru[1]
                kunci = "%s -> %s" % (lama.lower(), nbaru.lower())
                jenis[kunci] = jenis.get(kunci, 0) + 1
            rencana.append((pi, ci, py, "".join(baru), [x[0] for x in perubahan], p["id"], c["word"], cn))

    print("Contoh tanpa 一                      : %d" % tanpa_yi)
    print("Contoh dengan 一 yang sudah sesuai   : %d" % sudah_sesuai)
    print("Contoh dengan 一 yang akan diubah    : %d  (kemunculan 一: %s)"
          % (len(rencana), ", ".join("%s %d" % (k, v) for k, v in sorted(jenis.items()))))
    print("Bermasalah                           : %d" % len(masalah))
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

    baris = ["DAFTAR PERUBAHAN NADA 一 (lama -> baru) -- %d isian" % len(rencana), ""]
    for r in rencana:
        baris.append("%s / %s" % (r[5], r[6]))
        baris.append("   %s" % r[7])
        baris.append("   lama: %s" % r[2])
        baris.append("   baru: %s" % r[3])
    if not a.apply:
        print("\nIni baru ringkasan; belum ada yang diubah. Untuk menerapkan: python samakan_yi_nuance.py --apply")
        return 0

    # --- terapkan ---
    asli = copy.deepcopy(data)
    cadangan = PATH.with_name("nuance_pairs.json.bak_yi_" + datetime.now().strftime("%Y%m%d_%H%M%S"))
    shutil.copy2(PATH, cadangan)
    for pi, ci, lama, baru, pos, pid, kata, cn in rencana:
        data["pairs"][pi]["comparison"][ci]["example_pinyin"] = baru
    PATH.write_bytes(tulis_teks(data, akhir).encode("utf-8"))

    # pemeriksaan akhir: hanya example_pinyin yang boleh berbeda, dan hanya huruf suku kata 一
    harapan = copy.deepcopy(asli)
    ok = True
    for pi, ci, lama, baru, pos, pid, kata, cn in rencana:
        harapan["pairs"][pi]["comparison"][ci]["example_pinyin"] = baru
        beda = [i for i, (x, y) in enumerate(zip(lama, baru)) if x != y]
        boleh = set()
        for q in pos:
            boleh.update((q, q + 1))
        if len(lama) != len(baru) or any(i not in boleh for i in beda):
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
    print("Pemeriksaan akhir lolos (hanya huruf suku kata 一 yang berubah; %d pasangan utuh)." % len(ulang["pairs"]))
    print("Daftar lengkap perubahan: %s" % HASIL.name)
    return 0


if __name__ == "__main__":
    sys.exit(main())

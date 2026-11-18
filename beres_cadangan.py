#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
beres_cadangan.py -- merapikan berkas cadangan lama (*.bak_*) di Mandarin Interaktif
====================================================================================
Cadangan otomatis dari skrip-skrip perbaikan (mis. app_words.json.bak_before_apply_...,
peta-bahasa.html.bak_pilar12_...) menumpuk di folder data/ dan folder utama. Skrip ini
memindahkan yang LAMA ke folder arsip_cadangan_lama\\ . Tidak ada yang DIHAPUS.
Folder arsip itu Anda hapus sendiri kelak bila sudah yakin.

CARA PAKAI (dari C:\\mandarin_app>):

  1) Lihat dulu (TIDAK mengubah apa pun, hanya menampilkan daftar):
         python beres_cadangan.py

  2) Pindahkan cadangan lama ke arsip_cadangan_lama\\ :
         python beres_cadangan.py --apply

  Pilihan tambahan: --hari 3   (batas umur; bawaannya 2 hari)

ATURAN
  - Yang dihitung hanya berkas yang namanya memuat ".bak_".
  - "Satu jenis" = folder + nama berkas asal + label cadangan.
    Contoh: data\\app_words.json dengan label "before_apply" adalah satu jenis,
    dan data\\app_words.json dengan label "bacaan" adalah jenis lain.
  - Di tiap jenis, cadangan TERBARU selalu tetap di tempatnya, begitu juga semua cadangan
    yang umurnya kurang dari batas hari. Sisanya (lebih tua) dipindahkan.
  - Umur dihitung dari tanggal berkas di Windows (yang lebih baru antara tanggal dibuat dan
    tanggal diubah, karena salinan cadangan bisa membawa tanggal ubah berkas aslinya).
  - Susunan folder ditiru di arsip (mis. arsip_cadangan_lama\\data\\...), jadi untuk
    mengembalikan cukup memindahkan berkasnya kembali ke folder yang sama.
  - Tidak disentuh: folder backups\\ (zip checkpoint, diatur oleh checkpoint.py), .git,
    arsip_cadangan_lama\\ sendiri, dan berkas yang namanya tidak memuat ".bak_".
  - Aman dijalankan ulang. Setelah memindahkan, skrip memeriksa bahwa tiap berkas ada
    di tujuan dengan ukuran yang sama, dan menulis catatan pemindahan di folder arsip.
"""
import argparse
import os
import re
import shutil
import sys
import time
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent
ARSIP = "arsip_cadangan_lama"
LEWATI = {".git", ARSIP, "backups", "node_modules", "__pycache__"}
TANDA = ".bak_"


def ukuran_teks(n):
    if n >= 1024 * 1024:
        return "%.1f MB" % (n / 1024 / 1024)
    if n >= 1024:
        return "%.0f KB" % (n / 1024)
    return "%d B" % n


def tanggal_berkas(path):
    """Tanggal berkas: di Windows = yang lebih baru antara dibuat dan diubah; selain itu = diubah."""
    st = os.stat(path)
    if os.name == "nt":
        return max(st.st_mtime, st.st_ctime)
    return st.st_mtime


# pola tanggal-jam di ujung nama: 20261118_153012, 2026-11-18, 2026-11-18_15-30-12, 202611181530
POLA_WAKTU = [
    re.compile(r"[_\- ]?\d{8}[_\-]\d{4,6}$"),
    re.compile(r"[_\- ]?\d{4}-\d{2}-\d{2}(?:[_ T]\d{2}[-:]?\d{2}(?:[-:]?\d{2})?)?$"),
    re.compile(r"[_\-]?\d{12,14}$"),
]


def pecah_nama(nama):
    """Kembalikan (nama berkas asal, label) dari nama cadangan, atau None bila bukan cadangan."""
    m = re.match(r"^(.*?)\.bak_(.+)$", nama)
    if not m:
        return None
    asal, sisa = m.group(1), m.group(2)
    ekstensi = ""
    m2 = re.search(r"(\.[A-Za-z][A-Za-z0-9]{0,4})$", sisa)
    if m2 and len(sisa) > len(m2.group(1)):
        ekstensi = m2.group(1)
        sisa = sisa[: -len(ekstensi)]
    for pola in POLA_WAKTU:
        sisa2 = pola.sub("", sisa)
        if sisa2 != sisa:
            sisa = sisa2
            break
    label = sisa.strip("_- ") or "(tanpa label)"
    return asal + ekstensi, label


def kumpulkan():
    """Cari semua berkas cadangan. Hasil: {jenis: [ (path, ukuran, tanggal) ]}."""
    grup = {}
    for dirpath, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = [d for d in dirnames if d not in LEWATI]
        for f in filenames:
            if TANDA not in f:
                continue
            p = Path(dirpath) / f
            if p.is_symlink() or not p.is_file():
                continue
            hasil = pecah_nama(f)
            if not hasil:
                continue
            folder = p.parent.relative_to(ROOT).as_posix()
            jenis = (folder if folder != "." else "(folder utama)", hasil[0], hasil[1])
            grup.setdefault(jenis, []).append((p, p.stat().st_size, tanggal_berkas(p)))
    return grup


def susun_rencana(grup, hari):
    batas = time.time() - hari * 86400
    rencana = []  # (jenis, path, ukuran, tanggal, status) status: 'terbaru' | 'baru' | 'pindah'
    for jenis in sorted(grup):
        isi = sorted(grup[jenis], key=lambda x: x[2], reverse=True)
        for i, (p, uk, tg) in enumerate(isi):
            if i == 0:
                status = "terbaru"
            elif tg >= batas:
                status = "baru"
            else:
                status = "pindah"
            rencana.append((jenis, p, uk, tg, status))
    return rencana


def tampilkan(rencana, hari):
    if not rencana:
        print("Tidak ada berkas cadangan (*.bak_*) ditemukan.")
        return
    jenis_sekarang = None
    for jenis, p, uk, tg, status in rencana:
        if jenis != jenis_sekarang:
            jenis_sekarang = jenis
            n = sum(1 for r in rencana if r[0] == jenis)
            print("\n[%s] %s  | label: %s  (%d berkas)" % (jenis[0], jenis[1], jenis[2], n))
        tanda = {"pindah": "PINDAH", "terbaru": "tetap (terbaru)", "baru": "tetap (<%d hari)" % hari}[status]
        print("   %-17s %9s  %s  %s" % (tanda, ukuran_teks(uk),
                                         datetime.fromtimestamp(tg).strftime("%Y-%m-%d %H:%M"), p.name))
    total = len(rencana)
    pindah = [r for r in rencana if r[4] == "pindah"]
    tetap = total - len(pindah)
    print("\n" + "=" * 70)
    print("Jenis cadangan : %d" % len({r[0] for r in rencana}))
    print("Seluruh berkas : %d (%s)" % (total, ukuran_teks(sum(r[2] for r in rencana))))
    print("Tetap di tempat: %d (%s)" % (tetap, ukuran_teks(sum(r[2] for r in rencana if r[4] != "pindah"))))
    print("Akan dipindah  : %d (%s) ke %s\\" % (len(pindah), ukuran_teks(sum(r[2] for r in pindah)), ARSIP))


def tujuan_bebas(dest):
    if not dest.exists():
        return dest
    n = 2
    while True:
        cand = dest.with_name("%s__%d" % (dest.name, n))
        if not cand.exists():
            return cand
        n += 1


def jalankan(rencana):
    pindah = [r for r in rencana if r[4] == "pindah"]
    if not pindah:
        print("\nTidak ada yang perlu dipindah.")
        return 0
    arsip = ROOT / ARSIP
    arsip.mkdir(exist_ok=True)
    catatan, gagal, ok = [], [], 0
    for jenis, p, uk, tg, status in pindah:
        rel = p.relative_to(ROOT)
        dest = tujuan_bebas(arsip / rel)
        try:
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(p), str(dest))
            if (not dest.is_file()) or dest.stat().st_size != uk or p.exists():
                raise RuntimeError("pemeriksaan akhir gagal (ukuran atau lokasi tidak cocok)")
            ok += 1
            catatan.append("%s -> %s" % (rel.as_posix(), dest.relative_to(ROOT).as_posix()))
        except Exception as e:  # satu berkas gagal: lanjut yang lain, laporkan di akhir
            gagal.append((rel.as_posix(), str(e)))
    if catatan:
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        with open(arsip / ("_catatan_pemindahan_%s.txt" % stamp), "w", encoding="utf-8") as fh:
            fh.write("Dipindahkan oleh beres_cadangan.py pada %s\n\n" % datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            fh.write("\n".join(catatan) + "\n")
    print("\nSelesai: %d berkas dipindah ke %s\\ (tidak ada yang dihapus)." % (ok, ARSIP))
    if gagal:
        print("PERHATIAN: %d berkas gagal dipindah:" % len(gagal))
        for nama, alasan in gagal:
            print("   %s -- %s" % (nama, alasan))
        return 1
    return 0


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser(description="Pindahkan cadangan lama (*.bak_*) ke arsip_cadangan_lama\\ (tidak menghapus).")
    ap.add_argument("--apply", action="store_true", help="benar-benar memindahkan (tanpa ini hanya menampilkan daftar)")
    ap.add_argument("--hari", type=int, default=2, help="batas umur dalam hari (bawaan 2)")
    a = ap.parse_args()
    if a.hari < 0:
        print("--hari tidak boleh negatif.")
        return 1
    if not (ROOT / "kamus.html").exists() or not (ROOT / "data").is_dir():
        print("Skrip ini harus berada di folder utama proyek (tempat kamus.html dan folder data), mis. C:\\mandarin_app.")
        print("Lokasi skrip sekarang: %s" % ROOT)
        return 1
    print("Folder proyek: %s" % ROOT)
    print("Mode: %s | batas umur: %d hari" % ("PINDAHKAN (--apply)" if a.apply else "LIHAT-DULU (tidak mengubah apa pun)", a.hari))
    rencana = susun_rencana(kumpulkan(), a.hari)
    tampilkan(rencana, a.hari)
    if not a.apply:
        n = sum(1 for r in rencana if r[4] == "pindah")
        if n:
            print("\nIni baru daftar; belum ada yang dipindah. Untuk memindahkan: python beres_cadangan.py --apply")
        return 0
    return jalankan(rencana)


if __name__ == "__main__":
    sys.exit(main())

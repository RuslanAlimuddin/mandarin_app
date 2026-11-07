#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
checkpoint.py — Sistem checkpoint/backup menyeluruh utk Mandarin Interaktif
=============================================================================
Latar belakang: 30 Jul 2026, repair_glossary.py tiba-tiba kosong (0 bytes)
tanpa jejak apa pun -- Previous Versions tidak aktif, Notepad++ tidak
menyimpan riwayat lokal, Recycle Bin kosong. Untung masih ada salinan di
chat sebelumnya. Script ini mencegah insiden itu terulang dgn cara paling
sederhana: snapshot ZIP rutin dari SEMUA script (*.py) + data (data/*.json)
ke folder backups/, dengan rotasi otomatis (tidak numpuk selamanya).

BUKAN pengganti Git -- ini "jaring pengaman" sederhana yg bisa langsung
dipakai hari ini tanpa install apa pun. Kalau nanti رسلان mau upgrade ke
Git utk riwayat lebih detail (per baris, per commit), itu bisa jadi
langkah lanjutan terpisah.

CARA PAKAI (dari C:\\mandarin_app>):

  Bikin checkpoint baru (jalankan di awal & akhir tiap sesi kerja, dan
  SETELAH setiap --apply script perbaikan data yg berhasil):
      python checkpoint.py save
      python checkpoint.py save --note "sebelum audit round 3"

  Lihat daftar checkpoint yang ada:
      python checkpoint.py list

  Pulihkan SATU file dari checkpoint tertentu (tidak menimpa otomatis --
  file dipulihkan dgn akhiran .restored, رسلان cek dulu baru rename manual):
      python checkpoint.py restore-file checkpoint_20260730_200000 repair_glossary.py

  Pulihkan SELURUH checkpoint ke folder terpisah utk diperiksa (aman,
  tidak menimpa apa pun di C:\\mandarin_app langsung):
      python checkpoint.py restore-all checkpoint_20260730_200000

Checkpoint mencakup: semua file *.py di root folder + seluruh isi data/.
Rotasi: checkpoint lebih lama dari 20 checkpoint terakhir otomatis dihapus
(supaya tidak memenuhi disk), TAPI 1 checkpoint tertua tiap bulan tetap
dipertahankan (arsip jangka panjang).
"""
import argparse
import shutil
import sys
import zipfile
from datetime import datetime
from pathlib import Path

ROOT = Path(".")
BACKUPS_DIR = ROOT / "backups"
DATA_DIR = ROOT / "data"
MAX_RECENT_CHECKPOINTS = 20


def files_to_backup():
    files = list(ROOT.glob("*.py"))
    if DATA_DIR.exists():
        files += [p for p in DATA_DIR.rglob("*") if p.is_file()]
    return files


def cmd_save(args):
    BACKUPS_DIR.mkdir(exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    name = f"checkpoint_{ts}"
    zip_path = BACKUPS_DIR / f"{name}.zip"

    files = files_to_backup()
    if not files:
        print("Tidak ada file *.py atau data/ ditemukan. Pastikan dijalankan dari C:\\mandarin_app>")
        return

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for f in files:
            zf.write(f, arcname=f.relative_to(ROOT))
        if args.note:
            zf.writestr("_NOTE.txt", args.note)

    size_kb = zip_path.stat().st_size / 1024
    print(f"Checkpoint dibuat: {zip_path} ({size_kb:.0f} KB, {len(files)} file)")
    if args.note:
        print(f"Catatan: {args.note}")

    rotate_checkpoints()


def rotate_checkpoints():
    """Hapus checkpoint lama, TAPI simpan 1 checkpoint tertua per bulan
    sbg arsip jangka panjang."""
    zips = sorted(BACKUPS_DIR.glob("checkpoint_*.zip"))
    if len(zips) <= MAX_RECENT_CHECKPOINTS:
        return

    # checkpoint yg akan dipertimbangkan utk dihapus: semua kecuali
    # MAX_RECENT_CHECKPOINTS yg paling baru
    candidates = zips[:-MAX_RECENT_CHECKPOINTS]

    # dari kandidat, simpan 1 (yg paling tua) per bulan sbg arsip
    keep_months = set()
    to_delete = []
    for z in candidates:
        # nama: checkpoint_YYYYMMDD_HHMMSS.zip
        stamp = z.stem.replace("checkpoint_", "")
        month_key = stamp[:6]  # YYYYMM
        if month_key not in keep_months:
            keep_months.add(month_key)
            continue  # simpan sbg arsip bulanan
        to_delete.append(z)

    for z in to_delete:
        z.unlink()

    if to_delete:
        print(f"Rotasi: {len(to_delete)} checkpoint lama dihapus (arsip bulanan tetap disimpan).")


def cmd_list(args):
    if not BACKUPS_DIR.exists():
        print("Belum ada checkpoint. Jalankan 'python checkpoint.py save' dulu.")
        return
    zips = sorted(BACKUPS_DIR.glob("checkpoint_*.zip"), reverse=True)
    if not zips:
        print("Belum ada checkpoint.")
        return
    print(f"{len(zips)} checkpoint ditemukan (terbaru di atas):\n")
    for z in zips:
        size_kb = z.stat().st_size / 1024
        note = ""
        try:
            with zipfile.ZipFile(z) as zf:
                if "_NOTE.txt" in zf.namelist():
                    note = " — " + zf.read("_NOTE.txt").decode("utf-8")
        except Exception:
            pass
        print(f"  {z.stem}  ({size_kb:.0f} KB){note}")


def cmd_restore_file(args):
    zip_path = BACKUPS_DIR / f"{args.checkpoint}.zip"
    if not zip_path.exists():
        print(f"Checkpoint tidak ditemukan: {zip_path}")
        print("Jalankan 'python checkpoint.py list' utk lihat checkpoint yang ada.")
        return

    target = args.filepath.replace("\\", "/")
    with zipfile.ZipFile(zip_path) as zf:
        names = zf.namelist()
        if target not in names:
            print(f"File '{target}' tidak ada di checkpoint ini.")
            print("Isi checkpoint:")
            for n in names:
                print(f"  {n}")
            return
        data = zf.read(target)

    out_path = Path(f"{args.filepath}.restored")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_bytes(data)
    print(f"Dipulihkan ke: {out_path}")
    print(f"Cek isinya dulu, baru rename manual jadi '{args.filepath}' kalau sudah yakin.")


def cmd_restore_all(args):
    zip_path = BACKUPS_DIR / f"{args.checkpoint}.zip"
    if not zip_path.exists():
        print(f"Checkpoint tidak ditemukan: {zip_path}")
        return
    out_dir = ROOT / f"{args.checkpoint}_restored"
    with zipfile.ZipFile(zip_path) as zf:
        zf.extractall(out_dir)
    print(f"Seluruh checkpoint dipulihkan ke folder: {out_dir}")
    print("Folder ini TERPISAH dari C:\\mandarin_app, aman diperiksa dulu")
    print("sebelum menyalin file yang dibutuhkan secara manual.")


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="command", required=True)

    p_save = sub.add_parser("save")
    p_save.add_argument("--note", default=None)
    p_save.set_defaults(func=cmd_save)

    p_list = sub.add_parser("list")
    p_list.set_defaults(func=cmd_list)

    p_rf = sub.add_parser("restore-file")
    p_rf.add_argument("checkpoint")
    p_rf.add_argument("filepath")
    p_rf.set_defaults(func=cmd_restore_file)

    p_ra = sub.add_parser("restore-all")
    p_ra.add_argument("checkpoint")
    p_ra.set_defaults(func=cmd_restore_all)

    args = ap.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()

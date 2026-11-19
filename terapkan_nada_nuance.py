#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
terapkan_nada_nuance.py -- mengisi tanda nada pada contoh pinyin yang masih polos
=================================================================================
Mengisi tanda nada pada 716 isian example_pinyin di data/nuance_pairs.json yang ditulis tanpa
tanda nada (mis. "Ta lai wo zheli ba." -> "Tā lái wǒ zhèli ba."). Yang diubah HANYA isian
example_pinyin itu; hanzi, terjemahan, dan isian lain tidak disentuh.

Aturan (sudah kamu setujui):
  - Bacaan dari app_words.json (terkurasi) dulu; CC-CEDICT hanya bila bacaannya tunggal.
  - Nada 3-3 ditulis nada asli seperti kamus (nǐ hǎo). 不 tetap bù.
  - 一 mengikuti perubahan nada sebenarnya (yī / yí / yì).
  - Nada netral mengikuti bacaan terkurasi (xǐhuan, nàli, qǐlai, shang).
  - Karakter berbacaan ganda (golongan B1 dan B2 di laporan) memakai usulan yang sudah kamu setujui.
  - 湖泊: tulisan lama "hubo" diperbaiki menjadi húpō (satu-satunya contoh yang hurufnya ikut berubah).
  - Huruf, huruf kapital, spasi, apostrof, dan tanda baca lama dipertahankan; yang ditambah
    hanya tanda nada (ü ditulis ü bertanda nada).

Berkas pendukung yang HARUS ada di folder yang sama: daftar_nada_nuance.py

CARA PAKAI (dari C:\\mandarin_app>):

  1) Lihat dulu (TIDAK mengubah apa pun):
         python terapkan_nada_nuance.py

  2) Terapkan:
         python terapkan_nada_nuance.py --apply

KEAMANAN (sama seperti perbaiki_nuance.py)
  - Format berkas dijaga persis (JSON indent 2, ensure_ascii=False, akhir baris CRLF). Skrip
    menolak bekerja bila format berkas sekarang tidak bisa ditulis ulang persis sama.
  - Setiap usulan diperiksa: bila huruf pinyin (tanpa nada) berbeda dari tulisan lama, skrip
    berhenti dan tidak mengubah apa pun (kecuali 湖泊 yang memang disetujui).
  - Sebelum menulis dibuat cadangan: data\\nuance_pairs.json.bak_nada_<tanggal-jam>
  - Setelah menulis, berkas dibaca ulang dan dibandingkan: hanya isian example_pinyin yang
    boleh berbeda. Bila ada yang tidak cocok, berkas dikembalikan dari cadangan.
  - Aman diulang: isian yang sudah bernada dilewati.
  - Daftar lengkap perubahan (lama -> baru) ditulis ke hasil_nada_nuance.txt.
"""
import argparse
import copy
import json
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
HASIL = ROOT / "hasil_nada_nuance.txt"

# (id pasangan, kata) -> (tulisan lama, tulisan lama yang dibetulkan hurufnya sebelum diberi nada)
KOREKSI_HURUF = {
    ("b34_jiang_hu_373", "湖泊"): ("Zheli you xuduo meili de hubo.", "Zheli you xuduo meili de hupo."),
}


def tulis_teks(data, akhir_baris_akhir):
    return json.dumps(data, ensure_ascii=False, indent=2).replace("\n", "\r\n") + akhir_baris_akhir


def huruf_dasar(s):
    return dn.tanpa_nada(s)


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser(description="Isi tanda nada contoh pinyin di data/nuance_pairs.json")
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

    rencana = []   # (indeks_pasangan, indeks_banding, lama, baru, golongan, id, kata, hanzi)
    masalah = []
    sudah_bernada = 0
    for pi, p in enumerate(data["pairs"]):
        for ci, c in enumerate(p["comparison"]):
            py = c.get("example_pinyin", "")
            if any(ch in py for ch in dn.TONE_MARKS):
                sudah_bernada += 1
                continue
            label = "%s / %s" % (p["id"], c["word"])
            kunci = (p["id"], c["word"])
            if kunci in KOREKSI_HURUF:
                lama_ok, dibetulkan = KOREKSI_HURUF[kunci]
                if py != lama_ok:
                    masalah.append("%s -- isi sekarang berbeda dari yang diperiksa: %s" % (label, py))
                    continue
                rec = dn.proses_contoh(c["example_cn"], dibetulkan, app_idx, cc_idx)
                boleh_huruf_berubah = True
            else:
                rec = dn.proses_contoh(c["example_cn"], py, app_idx, cc_idx)
                boleh_huruf_berubah = False
            if rec["pinyin_usulan"] is None:
                masalah.append("%s -- tidak bisa diberi nada: %s | %s" % (label, py, "; ".join(rec["catatan"])))
                continue
            baru = rec["pinyin_usulan"]
            if not boleh_huruf_berubah and huruf_dasar(baru) != huruf_dasar(py):
                masalah.append("%s -- huruf berubah: %s -> %s" % (label, py, baru))
                continue
            if not any(ch in baru for ch in dn.TONE_MARKS):
                masalah.append("%s -- hasil tanpa tanda nada sama sekali: %s" % (label, baru))
                continue
            rencana.append((pi, ci, py, baru, rec["golongan"], p["id"], c["word"], c["example_cn"]))

    hitung = {}
    for r in rencana:
        hitung[r[4]] = hitung.get(r[4], 0) + 1
    print("Sudah bernada (dilewati): %d" % sudah_bernada)
    print("Akan diberi nada        : %d  (A pasti: %d | B1 yakin: %d | B2 usulan disetujui: %d)"
          % (len(rencana), hitung.get("A", 0), hitung.get("B1", 0), hitung.get("B2", 0)))
    print("Bermasalah              : %d" % len(masalah))
    if masalah:
        print("\nBERHENTI (tidak ada yang diubah). Isian bermasalah:")
        for m in masalah:
            print("   " + m)
        print("Kirim pesan ini ke Claude.")
        return 1
    if not rencana:
        print("Tidak ada yang perlu diubah.")
        return 0

    print("\nContoh perubahan (10 pertama):")
    for r in rencana[:10]:
        print("   %s\n      %s\n      -> %s" % (r[7], r[2], r[3]))

    baris = ["DAFTAR PERUBAHAN example_pinyin (lama -> baru) -- %d isian" % len(rencana), ""]
    for r in rencana:
        baris.append("[%s] %s / %s" % (r[4], r[5], r[6]))
        baris.append("   %s" % r[7])
        baris.append("   lama: %s" % r[2])
        baris.append("   baru: %s" % r[3])
    if not a.apply:
        print("\nIni baru ringkasan; belum ada yang diubah. Untuk menerapkan: python terapkan_nada_nuance.py --apply")
        return 0

    # --- terapkan ---
    asli = copy.deepcopy(data)
    cadangan = PATH.with_name("nuance_pairs.json.bak_nada_" + datetime.now().strftime("%Y%m%d_%H%M%S"))
    shutil.copy2(PATH, cadangan)
    for pi, ci, lama, baru, gol, pid, kata, cn in rencana:
        data["pairs"][pi]["comparison"][ci]["example_pinyin"] = baru
    PATH.write_bytes(tulis_teks(data, akhir).encode("utf-8"))

    # pemeriksaan akhir: baca ulang, hanya example_pinyin yang boleh berbeda
    harapan = copy.deepcopy(asli)
    for pi, ci, lama, baru, gol, pid, kata, cn in rencana:
        harapan["pairs"][pi]["comparison"][ci]["example_pinyin"] = baru
    try:
        ulang = json.loads(PATH.read_bytes().decode("utf-8"))
        cocok = ulang == harapan and len(ulang["pairs"]) == len(asli["pairs"])
    except Exception:
        cocok = False
    if not cocok:
        shutil.copy2(cadangan, PATH)
        print("\nPEMERIKSAAN AKHIR GAGAL: berkas dikembalikan dari cadangan %s. Kirim pesan ini ke Claude." % cadangan.name)
        return 1
    sisa = sum(1 for p in ulang["pairs"] for c in p["comparison"]
               if not any(ch in c.get("example_pinyin", "") for ch in dn.TONE_MARKS))
    HASIL.write_text("\r\n".join(baris) + "\r\n", encoding="utf-8-sig")
    print("\nSelesai: %d isian diberi nada. Cadangan: %s" % (len(rencana), cadangan.name))
    print("Pemeriksaan akhir lolos (hanya example_pinyin yang berubah; %d pasangan utuh)." % len(ulang["pairs"]))
    print("Contoh yang masih tanpa tanda nada: %d" % sisa)
    print("Daftar lengkap perubahan: %s" % HASIL.name)
    return 0


if __name__ == "__main__":
    sys.exit(main())

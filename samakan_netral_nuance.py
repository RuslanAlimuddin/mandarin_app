#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
samakan_netral_nuance.py -- menyamakan nada netral pada contoh lama dengan bacaan terkurasi
=========================================================================================
Tahap 4 (terakhir) dari penyamaan 1.868 contoh lama (butir 3 rencana v45). Contoh lama kadang
memberi nada penuh pada suku kata yang di kamus terkurasi (data\\app_words.json) bernada netral,
mis. 喜欢 xǐhuān -> xǐhuan, 学生 xuéshēng -> xuésheng, 早上 zǎoshàng -> zǎoshang, 太阳 tàiyáng -> tàiyang,
眼睛 yǎnjīng -> yǎnjing, 关系 guānxì -> guānxi, 起来 qǐlái -> qǐlai. 716 contoh baru sudah memakai
bacaan terkurasi itu; skrip ini menyamakan sisanya.

Yang diubah HANYA tanda nada pada suku kata itu (huruf tetap, mis. "huān" menjadi "huan"), di isian
example_pinyin. Susunan spasi, huruf kapital, dan tanda baca tidak disentuh.

ATURAN
  - Diubah  : suku kata bernada penuh di data lama yang di kamus terkurasi (atau, bila kata tidak ada
              di sana, CC-CEDICT yang bacaannya tunggal) bernada netral.
  - TIDAK diubah, hanya dilaporkan:
      * arah kebalikan: data lama netral tetapi kamus terkurasi bernada penuh (mis. 能不能 bu,
        早晨 zǎochen, 木匠 mùjiang, 房子 fángzi, 精神 jīngshen, 玫瑰 méigui). Di semua kasus itu
        data lama yang benar.
      * selisih nada sungguhan (mis. 一只 zhī lawan zhǐ): data lama yang benar.
      * 里: datamu menulis 里 nada penuh "lǐ" hampir di semua tempat (这里 zhèlǐ, 哪里 nǎlǐ, 家里),
        jadi 那里 nàlǐ dibiarkan walau kamus terkurasi menulis "nà li".
      * 一 dan 个: sudah ditangani di tahap 2 dan 3.
  - Contoh yang pinyin-nya tidak bisa disejajarkan dengan hanzi dilewati dan dilaporkan (tidak diubah).

Berkas pendukung yang HARUS ada di folder yang sama: daftar_nada_nuance.py

CARA PAKAI (dari C:\\mandarin_app>):

  1) Lihat dulu (TIDAK mengubah apa pun):
         python samakan_netral_nuance.py

  2) Terapkan:
         python samakan_netral_nuance.py --apply

KEAMANAN
  - Format berkas dijaga persis (JSON indent 2, ensure_ascii=False, akhir baris CRLF); skrip
    menolak bekerja bila format berkas sekarang tidak bisa ditulis ulang persis sama.
  - Sebelum menulis dibuat cadangan: data\\nuance_pairs.json.bak_netral_<tanggal-jam>
  - Setelah menulis, berkas dibaca ulang dan dibandingkan: hanya isian example_pinyin yang boleh
    berbeda, dan di tiap isian hanya tanda nada pada huruf (huruf dasarnya tetap sama). Bila ada
    yang tidak cocok, berkas dikembalikan dari cadangan.
  - Aman diulang: yang sudah netral dilewati.
  - Daftar lengkap perubahan (lama -> baru) ditulis ke hasil_netral_nuance.txt.
"""
import argparse
import copy
import itertools
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
HASIL = ROOT / "hasil_netral_nuance.txt"

# karakter yang TIDAK dijadikan netral walau kamus terkurasi menulis netral (lihat docstring)
KECUALI_NETRAL = {"里"}
# karakter yang sudah ditangani tahap lain
TAHAP_LAIN = {"一", "个"}


def tulis_teks(data, akhir_baris_akhir):
    return json.dumps(data, ensure_ascii=False, indent=2).replace("\n", "\r\n") + akhir_baris_akhir


def tanpa_tanda(s):
    """Hapus tanda nada tetapi pertahankan ü (diaeresis)."""
    d = unicodedata.normalize("NFD", s)
    d = "".join(ch for ch in d if unicodedata.category(ch) != "Mn" or ch == "\u0308")
    return unicodedata.normalize("NFC", d)


def _bacaan_lain(hz, app_idx, cc_idx):
    hasil = []
    for sumber in (app_idx.get(hz, []), cc_idx.get(hz, [])):
        for r in sumber:
            for sy in dn.pecah_suku(r):
                if sy.lower() not in [x.lower() for x in hasil]:
                    hasil.append(sy.lower())
    return hasil


def selaraskan(cn, py, app_idx, cc_idx):
    """Pecah hanzi sehingga huruf (tanpa nada) cocok dengan pinyin lama. Kembalikan (items, idx, huruf) atau None."""
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
    if pertama is None:
        return None
    var = [k for k, it in enumerate(pertama) if it["risiko"] and len(it["seg"]) == 1][:4]
    if not var:
        return None
    pilihan = [_bacaan_lain(pertama[k]["hz"], app_idx, cc_idx)[:5] for k in var]
    for kombinasi in itertools.product(*pilihan):
        items = copy.deepcopy(pertama)
        for k, sy in zip(var, kombinasi):
            items[k]["syl"] = sy
        dn.terapkan_yi(items)
        if polos == "".join(dn.tanpa_nada(it["syl"]) for it in items):
            return items, idx, huruf
    return None


def usul_netral(cn, py, app_idx, cc_idx):
    """Kembalikan (diubah, dibiarkan, galat).
    diubah   = daftar (posisi_karakter, lama, baru, kata, sumber) -- tanda nada dihapus
    dibiarkan= daftar (jenis, hz, kata, lama, baru) -- dilaporkan saja"""
    if unicodedata.normalize("NFC", py) != py:
        return None, None, "pinyin lama tidak dalam bentuk NFC"
    hasil = selaraskan(cn, py, app_idx, cc_idx)
    if hasil is None:
        return None, None, "pinyin lama tidak bisa disejajarkan dengan hanzi"
    items, idx, huruf = hasil
    diubah, dibiarkan = [], []
    pos = 0
    for it in items:
        n = len(dn.tanpa_nada(it["syl"]))
        lama = "".join(huruf[pos:pos + n])
        awal = pos
        pos += n
        baru = it["syl"]
        if it["hz"] in TAHAP_LAIN or lama.lower() == baru.lower():
            continue
        nl, nb = dn.nada_suku(lama), dn.nada_suku(baru)
        sumber = "kamus terkurasi" if it["seg"] in _APP else "CC-CEDICT"
        if nl != 5 and nb == 5:
            if it["hz"] in KECUALI_NETRAL:
                dibiarkan.append(("pengecualian 里", it["hz"], it["seg"], lama, baru))
                continue
            plain = tanpa_tanda(lama)
            if plain.lower() != baru.lower() and tanpa_tanda(baru).lower() != plain.lower():
                return None, None, "huruf suku kata tidak cocok: %s lawan %s" % (lama, baru)
            diubah.append((idx[awal], idx[awal + n - 1], lama, plain, it["seg"], sumber))
        elif nl == 5 and nb != 5:
            dibiarkan.append(("kebalikan (lama netral, terkurasi nada penuh)", it["hz"], it["seg"], lama, baru))
        elif nl != 5 and nb != 5:
            dibiarkan.append(("selisih nada sungguhan", it["hz"], it["seg"], lama, baru))
    return diubah, dibiarkan, None


_APP = {}


def main():
    global _APP
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser(description="Samakan nada netral pada contoh lama di data/nuance_pairs.json")
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
    _APP = app_idx

    rencana = []     # (pi, ci, lama, baru, daftar_perubahan, id, kata, hanzi)
    dilewati = []    # tak bisa disejajarkan
    laporan = {}     # jenis -> daftar
    sudah = 0
    jenis_ubah = {}
    for pi, p in enumerate(data["pairs"]):
        for ci, c in enumerate(p["comparison"]):
            cn = c.get("example_cn", "")
            py = c.get("example_pinyin", "")
            diubah, dibiarkan, galat = usul_netral(cn, py, app_idx, cc_idx)
            if galat:
                dilewati.append((p["id"], c["word"], cn, py, galat))
                continue
            for jenis, hz, seg, lama, baru in dibiarkan:
                laporan.setdefault(jenis, []).append((seg, lama, baru, cn, py))
            if not diubah:
                sudah += 1
                continue
            teks = list(py)
            for awal, akhir_i, lama, plain, seg, sumber in diubah:
                n = len(lama)
                # ganti huruf-huruf suku kata satu per satu (indeks karakter dalam pinyin)
                huruf_idx = [i for i in range(len(py)) if py[i].isalpha()]
                kunci = "%s -> %s" % (lama, plain)
                jenis_ubah[kunci] = jenis_ubah.get(kunci, 0) + 1
                s0 = huruf_idx.index(awal)
                for k in range(n):
                    teks[huruf_idx[s0 + k]] = plain[k]
            rencana.append((pi, ci, py, "".join(teks), diubah, p["id"], c["word"], cn))

    kemunculan = sum(len(r[4]) for r in rencana)
    print("Contoh tanpa perubahan nada netral    : %d" % sudah)
    print("Contoh yang akan diubah               : %d  (kemunculan: %d)" % (len(rencana), kemunculan))
    print("Dilewati (pinyin tak bisa disejajarkan): %d" % len(dilewati))
    for pid, kata, cn, py, galat in dilewati:
        print("     %s / %s | %s | %s" % (pid, kata, cn, py))
    print("\nTidak diubah, hanya dilaporkan:")
    for jenis, daf in laporan.items():
        print("   %s: %d kemunculan" % (jenis, len(daf)))
    print("\nYang akan diubah (kata: bentuk lama -> baru, jumlah):")
    ringkas = {}
    for r in rencana:
        for awal, akhir_i, lama, plain, seg, sumber in r[4]:
            k = "%s %s -> %s%s" % (seg, lama, plain, "  [CC-CEDICT]" if sumber == "CC-CEDICT" else "")
            ringkas[k] = ringkas.get(k, 0) + 1
    for k, v in sorted(ringkas.items(), key=lambda x: (-x[1], x[0])):
        print("   %-28s %d" % (k, v))

    baris = ["DAFTAR PERUBAHAN NADA NETRAL (lama -> baru) -- %d isian" % len(rencana), ""]
    for r in rencana:
        baris.append("%s / %s" % (r[5], r[6]))
        baris.append("   %s" % r[7])
        baris.append("   lama: %s" % r[2])
        baris.append("   baru: %s" % r[3])
    baris.append("")
    baris.append("TIDAK DIUBAH (hanya dilaporkan)")
    for jenis, daf in laporan.items():
        baris.append("")
        baris.append("## %s (%d)" % (jenis, len(daf)))
        for seg, lama, baru, cn, py in daf:
            baris.append("   %s | %s (kamus terkurasi: %s) | %s | %s" % (seg, lama, baru, cn, py))

    if not rencana:
        print("\nTidak ada yang perlu diubah.")
        return 0
    if not a.apply:
        print("\nIni baru ringkasan; belum ada yang diubah. Untuk menerapkan: python samakan_netral_nuance.py --apply")
        return 0

    # --- terapkan ---
    asli = copy.deepcopy(data)
    cadangan = PATH.with_name("nuance_pairs.json.bak_netral_" + datetime.now().strftime("%Y%m%d_%H%M%S"))
    shutil.copy2(PATH, cadangan)
    for pi, ci, lama, baru, dp, pid, kata, cn in rencana:
        data["pairs"][pi]["comparison"][ci]["example_pinyin"] = baru
    PATH.write_bytes(tulis_teks(data, akhir).encode("utf-8"))

    # pemeriksaan akhir: hanya example_pinyin yang boleh berbeda; di tiap isian hanya tanda nada yang hilang
    harapan = copy.deepcopy(asli)
    ok = True
    for pi, ci, lama, baru, dp, pid, kata, cn in rencana:
        harapan["pairs"][pi]["comparison"][ci]["example_pinyin"] = baru
        if len(lama) != len(baru):
            ok = False
            continue
        for x, y in zip(lama, baru):
            if x != y and tanpa_tanda(x) != y:
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
    print("Pemeriksaan akhir lolos (hanya tanda nada yang berubah; %d pasangan utuh)." % len(ulang["pairs"]))
    print("Daftar lengkap perubahan dan yang dilaporkan: %s" % HASIL.name)
    return 0


if __name__ == "__main__":
    sys.exit(main())

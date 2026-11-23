#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
perbaiki_kapital_kata.py -- huruf kapital keliru pada pinyin 16 kata biasa
==========================================================================
Butir 1 rencana BLUEPRINT_v47 (bagian 5). Keputusan رسلان (22 November 2026):

  A. 14 kata biasa -> pinyin huruf kecil (kapitalnya terbawa dari arti kedua yang berupa nama tempat/orang):
       和平 通道 安定 复兴 互联网 星期天 星期日 礼拜天 吉普 摄氏度 菩萨 一卡通 国会 中医
  B. 2 kata yang pinyinnya rusak:
       美德  měi Dé       -> měi dé
       张扬  zhāng Yáng   -> zhāng yáng, dan arti "Zhang Yang (1967-) ..." dipindah ke URUTAN TERAKHIR
                             (arti pertama menjadi "memamerkan secara mencolok"), di daftar Indonesia dan Inggris.
  C/D. 64 kata sisanya (nama diri; bahasa, agama, hari raya, mata uang, dll.) TETAP berkapital. Tidak disentuh.

  Yang diubah (berdasarkan POSISI isian, bukan bunyi pinyin):
    1) data\\app_words.json         : pinyin dan pinyin_numeric 16 kata (+ urutan arti 张扬)
    2) data\\graded_readers.json    : pinyin di glosarium (互联网, 美德, 张扬); dan arti glosarium 张扬 di bacaan
                                     tema_kebebasan_hsk9 (keputusan 23 November 2026): "Zhang Yang (1967-), sutradara
                                     dan penulis skenario film RRT" -> "memamerkan secara mencolok" (kata kerja di teks)
    3) data\\produktif_karakter.json: pinyin di daftar kata turunan (24 isian)
    4) data\\nuance_pairs.json      : pinyin 和平 dan "Hépíng" di tengah kalimat contoh -> "hépíng"
  Hanya DILAPORKAN (tidak diubah): data\\tone_drills.json -- berkas ini dihasilkan dari kamus; setelah skrip ini,
  jalankan segarkan_tone_drills.py (lihat dulu, lalu --apply).

CARA PAKAI (dari C:\\mandarin_app>):
  1) Lihat dulu (TIDAK mengubah apa pun):   python perbaiki_kapital_kata.py
  2) Terapkan:                              python perbaiki_kapital_kata.py --apply

KEAMANAN
  - Format tiap berkas dijaga persis; skrip menolak bekerja bila format berkas tidak bisa ditulis ulang persis sama.
  - Sebelum menulis dibuat cadangan: data\\<berkas>.bak_kapital_<tanggal-jam> (empat berkas).
  - Isian hanya diubah bila SEKARANG persis sama dengan bentuk lama (atau sudah bentuk baru); bila ada yang lain, skrip berhenti.
  - Setelah menulis, keempat berkas dibaca ulang dan dibandingkan dengan yang diharapkan; hanya isian yang direncanakan
    boleh berbeda. Bila tidak cocok, SEMUA berkas dikembalikan dari cadangan.
  - Aman diulang. Daftar lengkap: hasil_kapital_kata.txt
"""
import argparse
import copy
import json
import shutil
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
BERKAS = {
    "app": DATA / "app_words.json",
    "bacaan": DATA / "graded_readers.json",
    "produktif": DATA / "produktif_karakter.json",
    "nuance": DATA / "nuance_pairs.json",
}
TONE = DATA / "tone_drills.json"
HASIL = ROOT / "hasil_kapital_kata.txt"

# hanzi -> pinyin lama (berspasi). Bentuk baru = huruf kecil semua.
KATA = {
    "和平": "Hé píng", "通道": "Tōng dào", "安定": "Ān dìng", "复兴": "Fù xīng", "互联网": "Hù lián wǎng",
    "星期天": "Xīng qī tiān", "星期日": "Xīng qī rì", "礼拜天": "Lǐ bài tiān", "吉普": "Jí pǔ",
    "摄氏度": "Shè shì dù", "菩萨": "Pú sà", "一卡通": "Yī kǎ tōng", "国会": "Guó huì", "中医": "Zhōng yī",
    "美德": "měi Dé", "张扬": "zhāng Yáng",
}
# kata -> awal arti yang dipindah ke urutan terakhir (di meanings_id dan meanings_en)
PINDAH_ARTI = {"张扬": "Zhang Yang (1967-)"}
# arti glosarium bacaan yang keliru: kata -> (arti lama persis, arti baru)
ARTI_GLOSARIUM = {"张扬": ("Zhang Yang (1967-), sutradara dan penulis skenario film RRT", "memamerkan secara mencolok")}


def baru(lama):
    return lama.lower()


def tulis_teks(data, nl, akhir):
    return json.dumps(data, ensure_ascii=False, indent=2).replace("\n", nl) + akhir


def baca_json(path):
    mentah = path.read_bytes().decode("utf-8")
    nl = "\r\n" if "\r\n" in mentah else "\n"
    akhir = nl if mentah.endswith(nl) else ""
    data = json.loads(mentah)
    if tulis_teks(data, nl, akhir) != mentah:
        return None
    return data, nl, akhir


def ambil(data, path):
    for k in path:
        data = data[k]
    return data


def pasang(data, path, nilai):
    ambil(data, path[:-1])[path[-1]] = nilai


class Rencana:
    def __init__(self):
        self.item = []      # (berkas, path, lama, baru, ket)
        self.sudah = 0
        self.galat = []
        self.laporan = []

    def tambah(self, berkas, path, lama, nilai_baru, ket):
        self.item.append((berkas, tuple(path), lama, nilai_baru, ket))

    def isian(self, berkas, data, path, kata, ket):
        """Pinyin berspasi: ganti lama -> baru bila persis sama."""
        lama = KATA[kata]
        sekarang = ambil(data, path)
        if sekarang == lama:
            self.tambah(berkas, path, lama, baru(lama), "%s | %s" % (kata, ket))
        elif sekarang == baru(lama):
            self.sudah += 1
        else:
            self.galat.append("%s %s %s: isinya %r, diharapkan %r atau %r" % (berkas, kata, "/".join(map(str, path)), sekarang, lama, baru(lama)))


def susun(data):
    r = Rencana()
    app, bacaan, produktif, nuance = data["app"], data["bacaan"], data["produktif"], data["nuance"]

    # 1) kamus
    ditemukan = set()
    for i, e in enumerate(app):
        hz = e.get("simplified")
        if hz not in KATA:
            continue
        ditemukan.add(hz)
        r.isian("app", app, (i, "pinyin"), hz, "pinyin")
        num = e["pinyin_numeric"]
        if num != num.lower():
            if len(num.split()) != len(KATA[hz].split()):
                r.galat.append("app %s: jumlah suku pinyin_numeric %r tidak sama dengan pinyin" % (hz, num))
            else:
                r.tambah("app", (i, "pinyin_numeric"), num, num.lower(), "%s | pinyin_numeric" % hz)
        else:
            r.sudah += 1
        if hz in PINDAH_ARTI:
            awal = PINDAH_ARTI[hz]
            mi, me = e["meanings_id"], e["meanings_en"]
            if len(mi) != len(me) or len(mi) < 2:
                r.galat.append("app %s: daftar arti Indonesia dan Inggris tidak sejajar" % hz)
            elif mi[0].startswith(awal) and me[0].startswith(awal):
                r.tambah("app", (i, "meanings_id"), list(mi), mi[1:] + mi[:1], "%s | arti nama dipindah ke akhir (Indonesia)" % hz)
                r.tambah("app", (i, "meanings_en"), list(me), me[1:] + me[:1], "%s | arti nama dipindah ke akhir (Inggris)" % hz)
            elif mi[-1].startswith(awal) and me[-1].startswith(awal):
                r.sudah += 1
            else:
                r.galat.append("app %s: arti nama tidak di awal maupun di akhir" % hz)
    for hz in KATA:
        if hz not in ditemukan:
            r.galat.append("app: kata %s tidak ditemukan di app_words.json" % hz)

    # 2) glosarium bacaan
    for pi, p in enumerate(bacaan["passages"]):
        for gi, gl in enumerate(p.get("glossary", [])):
            if gl.get("cn") in KATA:
                r.isian("bacaan", bacaan, ("passages", pi, "glossary", gi, "py"), gl["cn"], "bacaan %s" % p["id"])
            if gl.get("cn") in ARTI_GLOSARIUM:
                arti_lama, arti_baru = ARTI_GLOSARIUM[gl["cn"]]
                if gl.get("id") == arti_lama:
                    r.tambah("bacaan", ("passages", pi, "glossary", gi, "id"), arti_lama, arti_baru,
                             "%s | arti glosarium bacaan %s" % (gl["cn"], p["id"]))
                elif gl.get("id") == arti_baru:
                    r.sudah += 1
                else:
                    r.laporan.append("bacaan %s: arti glosarium %s berbeda dari yang diperkirakan (%r); dibiarkan" % (p["id"], gl["cn"], gl.get("id")))

    # 3) kata turunan produktif
    for ch, v in produktif.items():
        if not isinstance(v, dict):
            continue
        for ki, k in enumerate(v.get("kata_turunan", [])):
            if k.get("kata") in KATA:
                r.isian("produktif", produktif, (ch, "kata_turunan", ki, "pinyin"), k["kata"], "karakter %s" % ch)

    # 4) contoh nuansa
    for pi, pr in enumerate(nuance["pairs"]):
        for ci, c in enumerate(pr["comparison"]):
            hz = c.get("word")
            if hz not in KATA:
                continue
            r.isian("nuance", nuance, ("pairs", pi, "comparison", ci, "pinyin"), hz, pr["id"])
            lama_rapat = KATA[hz].replace(" ", "")
            ex = c.get("example_pinyin", "")
            idx = ex.find(lama_rapat)
            if idx > 0 and not ex[:idx].rstrip().endswith((".", "?", "!", "。")):
                r.tambah("nuance", ("pairs", pi, "comparison", ci, "example_pinyin"), ex,
                         ex[:idx] + baru(lama_rapat) + ex[idx + len(lama_rapat):], "%s | kalimat contoh %s" % (hz, pr["id"]))
            elif idx == 0:
                r.laporan.append("nuance %s: %r diawali kapital karena awal kalimat (dibiarkan)" % (pr["id"], ex))
    return r


def kapital_tersisa(app):
    ban, satu = [], []
    for e in app:
        py = e.get("pinyin", "")
        if py != py.lower():
            (ban if len(e["simplified"]) > 1 else satu).append(e["simplified"])
    return ban, satu


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true", help="terapkan perubahan (tanpa ini hanya melihat)")
    a = ap.parse_args()

    data, nl, akhir = {}, {}, {}
    for k, path in BERKAS.items():
        if not path.exists():
            print("Tidak menemukan %s" % path)
            return 1
        hasil = baca_json(path)
        if hasil is None:
            print("BERHENTI: format %s tidak bisa ditulis ulang persis sama. Tidak ada yang diubah. Kirim pesan ini ke Claude." % path.name)
            return 1
        data[k], nl[k], akhir[k] = hasil

    r = susun(data)
    if r.galat:
        print("BERHENTI: isian tidak seperti yang diharapkan:")
        for g in r.galat:
            print("     " + g)
        print("Tidak ada yang diubah. Kirim pesan ini ke Claude.")
        return 1

    # simulasi hasil untuk pemeriksaan sisa kapital
    sim = copy.deepcopy(data)
    for berkas, path, lama, nv, ket in r.item:
        pasang(sim[berkas], path, nv)
    ban_sisa, satu_sisa = kapital_tersisa(sim["app"])

    ket_berkas = {"app": "data\\app_words.json", "bacaan": "data\\graded_readers.json",
                  "produktif": "data\\produktif_karakter.json", "nuance": "data\\nuance_pairs.json"}
    print("=== Pinyin kapital keliru pada 16 kata biasa ===")
    for k in BERKAS:
        n = [x for x in r.item if x[0] == k]
        print("%-32s isian yang akan diubah: %d" % (ket_berkas[k], len(n)))
    print("Sudah benar (dilewati): %d" % r.sudah)
    print()
    per_kata = {}
    for berkas, path, lama, nv, ket in r.item:
        per_kata.setdefault(ket.split(" | ")[0], []).append(berkas)
    for hz, lama in KATA.items():
        print("   %-5s %-16s -> %-16s  (%s)" % (hz, lama, baru(lama), ", ".join(sorted(set(per_kata.get(hz, [])))) or "sudah benar"))
    for hz in PINDAH_ARTI:
        for berkas, path, lama, nv, ket in r.item:
            if berkas == "app" and path[-1] == "meanings_id" and ket.startswith(hz):
                print("   %s: arti Indonesia sekarang berurutan: %s" % (hz, " | ".join(x[:28] for x in nv[:3])) + " ... | " + nv[-1][:28])

    # tone_drills (hanya dilaporkan)
    tone_n = 0
    if TONE.exists():
        mentah = TONE.read_text(encoding="utf-8")
        tone_n = sum(mentah.count('"%s"' % KATA[hz]) for hz in KATA)
    print("\nPinyin lama di data\\tone_drills.json (HANYA dilaporkan): %d isian%s" % (tone_n, " -> setelah ini jalankan segarkan_tone_drills.py" if tone_n else ""))

    # temuan tambahan (dilaporkan)
    temuan = []
    for p in sim["bacaan"]["passages"]:
        for gl in p.get("glossary", []):
            if gl.get("cn") in PINDAH_ARTI and gl.get("id", "").startswith(PINDAH_ARTI[gl["cn"]]):
                temuan.append("Bacaan %s: glosarium memberi %s arti \"%s...\", padahal teksnya memakai %s sebagai kata kerja. TIDAK diubah; perlu keputusan." % (p["id"], gl["cn"], gl["id"][:30], gl["cn"]))
    for t in r.laporan + temuan:
        print("CATATAN: " + t)

    print("\nSetelah perubahan: kata lebih dari satu karakter berpinyin kapital = %d (diharapkan 64: nama diri dan kelompok D tetap);" % len(ban_sisa))
    print("kata satu karakter berpinyin kapital = %d." % len(satu_sisa))

    baris = ["DAFTAR PERUBAHAN KAPITAL KATA -- %d isian" % len(r.item), ""]
    for berkas, path, lama, nv, ket in r.item:
        baris.append("%s | %s | %s" % (ket_berkas[berkas], ket, "/".join(map(str, path))))
        baris.append("   lama: %s" % (lama if not isinstance(lama, list) else " | ".join(lama)))
        baris.append("   baru: %s" % (nv if not isinstance(nv, list) else " | ".join(nv)))
    baris += ["", "## CATATAN"] + r.laporan + temuan
    baris += ["", "## SISA KATA BERKAPITAL (%d, tidak diubah)" % len(ban_sisa), "   " + " ".join(ban_sisa)]

    if not r.item:
        print("\nTidak ada yang perlu diubah.")
        return 0
    if not a.apply:
        HASIL.write_text("\r\n".join(baris) + "\r\n", encoding="utf-8-sig")
        print("\nIni baru ringkasan; belum ada yang diubah. Daftar lengkap: %s" % HASIL.name)
        print("Untuk menerapkan: python perbaiki_kapital_kata.py --apply")
        return 0

    cap = datetime.now().strftime("%Y%m%d_%H%M%S")
    cadangan = {}
    for k, path in BERKAS.items():
        cadangan[k] = path.with_name(path.name + ".bak_kapital_" + cap)
        shutil.copy2(path, cadangan[k])
    asli = copy.deepcopy(data)
    for berkas, path, lama, nv, ket in r.item:
        pasang(data[berkas], path, nv)
    for k, path in BERKAS.items():
        path.write_bytes(tulis_teks(data[k], nl[k], akhir[k]).encode("utf-8"))

    cocok = True
    try:
        for k, path in BERKAS.items():
            ulang = json.loads(path.read_bytes().decode("utf-8"))
            if ulang != sim[k]:
                cocok = False
        ban2, satu2 = kapital_tersisa(json.loads(BERKAS["app"].read_bytes().decode("utf-8")))
        if len(ban2) != len(ban_sisa) or satu2:
            cocok = False
        if len(json.loads(BERKAS["app"].read_bytes().decode("utf-8"))) != len(asli["app"]):
            cocok = False
    except Exception:
        cocok = False
    if not cocok:
        for k, path in BERKAS.items():
            shutil.copy2(cadangan[k], path)
        print("\nPEMERIKSAAN AKHIR GAGAL: semua berkas dikembalikan dari cadangan. Kirim pesan ini ke Claude.")
        return 1
    HASIL.write_text("\r\n".join(baris) + "\r\n", encoding="utf-8-sig")
    print("\nSelesai: %d isian diperbaiki." % len(r.item))
    print("Cadangan: " + ", ".join(c.name for c in cadangan.values()))
    print("Pemeriksaan akhir lolos (hanya isian yang direncanakan berubah; %d kata kamus utuh)." % len(asli["app"]))
    if any(x[0] in ("app", "produktif", "nuance") for x in r.item):
        print("Langkah berikutnya: python segarkan_tone_drills.py  (lihat dulu), lalu  python segarkan_tone_drills.py --apply")
    return 0


if __name__ == "__main__":
    sys.exit(main())

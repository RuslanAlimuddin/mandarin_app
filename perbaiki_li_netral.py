#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
perbaiki_li_netral.py -- penyeragaman 里 (nada netral) + perapian 6 kata kamus terkurasi
========================================================================================
Poin 1 rencana BLUEPRINT_v46 (bagian 5), tahap pertama. Keputusan رسلان (20 November 2026):

  ATURAN 里  (pilihan B)
    - 里 sebagai AKHIRAN TEMPAT setelah kata benda ditulis netral "li":
      家里 jiā li, 心里 xīn li, 手里 shǒu li, 城里 chéng li, 怀里 huái li, 眼里, 夜里,
      森林里, 房间里, 村里, 教室里, 暗地里 dan sejenisnya.
    - 里 tetap nada penuh "lǐ" pada: 这里 那里 哪里 (里 sesudah 这/那/哪), 里面 里头 里边
      (里 di depan), 里程碑, 里拉, 公里, 卡路里, 万里, 尤克里里 (satuan, kata serapan, dsb.).

  TAHAP PERTAMA ini hanya menyentuh dua berkas:
    1) data\\nuance_pairs.json : isian example_pinyin yang memuat 里 (hanya tanda nada pada "li").
    2) data\\app_words.json    : kata-kata di tabel PERUBAHAN_KAMUS di bawah (pinyin, pinyin_numeric,
                                bopomofo, dan sedikit keterangan arti):
         里: 家里 手里 城里 怀里 -> netral; 那里 -> lǐ (nà li lama dibetulkan); 噼里啪啦 -> pīlipālā
         lain: 木匠 mùjiang, 早晨 zǎochen, 玫瑰 méigui; 精神 tetap jīngshén dan 3 artinya yang
               berbacaan netral diberi awalan "[jīngshen]"
         TIDAK diubah: 能不能 (aturan "不 tetap bù"), 鹏程万里, 尤克里里, 里面/里头/里边, dst.
  Berkas lain yang memuat 里 (graded_readers, grammar_hsk*, pelajaran, produktif_karakter, dll.)
  TIDAK disentuh; skrip ini hanya menghitungnya di laporan (tahap kedua dibahas kemudian).

Berkas pendukung yang HARUS ada di folder yang sama: daftar_nada_nuance.py

CARA PAKAI (dari C:\\mandarin_app>):

  1) Lihat dulu (TIDAK mengubah apa pun):
         python perbaiki_li_netral.py

  2) Terapkan:
         python perbaiki_li_netral.py --apply

KEAMANAN
  - Format berkas dijaga persis (JSON indent 2, ensure_ascii=False, akhir baris CRLF); skrip menolak
    bekerja bila format berkas sekarang tidak bisa ditulis ulang persis sama.
  - Sebelum menulis dibuat dua cadangan:
        data\\nuance_pairs.json.bak_li_<tanggal-jam>   dan   data\\app_words.json.bak_li_<tanggal-jam>
  - Perubahan kamus hanya dilakukan bila isian sekarang PERSIS sama dengan yang diharapkan
    (bentuk lama) atau sudah bentuk baru; bila ada yang lain, skrip berhenti dan tidak mengubah apa pun.
  - Setelah menulis, kedua berkas dibaca ulang dan dibandingkan dengan yang diharapkan; hanya isian
    yang direncanakan boleh berbeda. Bila ada yang tidak cocok, KEDUA berkas dikembalikan dari cadangan.
  - Aman diulang: yang sudah benar dilewati.
  - Daftar lengkap perubahan ditulis ke hasil_li_netral.txt.
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

NUANCE = ROOT / "data" / "nuance_pairs.json"
APP = ROOT / "data" / "app_words.json"
HASIL = ROOT / "hasil_li_netral.txt"

# ---------------------------------------------------------------- aturan 里
SESUDAH_PENUNJUK = set("这那哪")           # 这里 那里 哪里 -> lǐ
SESUDAH_ARAH = set("面头边")               # 里面 里头 里边 -> lǐ
SATUAN = set("公英海千万百十路")           # 公里 英里 海里 千里 万里 卡路里 -> lǐ
HANZI = re.compile(r"[\u4e00-\u9fff]")


def klasifikasi(prev, nxt):
    """Kembalikan (jenis, target) dengan target 'penuh' (lǐ) atau 'netral' (li)."""
    if prev in SESUDAH_PENUNJUK:
        return "这里/那里/哪里", "penuh"
    if nxt in SESUDAH_ARAH:
        return "里面/里头/里边", "penuh"
    if not prev or not HANZI.match(prev):
        return "里 di awal kalimat atau frasa", "penuh"
    if prev in SATUAN:
        return "satuan jarak / 卡路里", "penuh"
    return "akhiran tempat setelah kata benda", "netral"


# ---------------------------------------------------------------- perubahan kamus
# (hanzi, {isian: (lama, baru)}); isian: pinyin, pinyin_numeric, bopomofo, id:<arti lama> -> <arti baru>
PERUBAHAN_KAMUS = [
    ("家里", {"pinyin": ("jiā lǐ", "jiā li"), "pinyin_numeric": ("jia1 li3", "jia1 li5"),
             "bopomofo": ("ㄐㄧㄚ ㄌㄧˇ", "ㄐㄧㄚ ㄌㄧ˙")}),
    ("手里", {"pinyin": ("shǒu lǐ", "shǒu li"), "pinyin_numeric": ("shou3 li3", "shou3 li5"),
             "bopomofo": ("ㄕㄡˇ ㄌㄧˇ", "ㄕㄡˇ ㄌㄧ˙")}),
    ("城里", {"pinyin": ("chénglǐ", "chéngli"), "pinyin_numeric": ("cheng2 li3", "cheng2 li5"),
             "bopomofo": ("ㄔㄥˊ ㄌㄧˇ", "ㄔㄥˊ ㄌㄧ˙")}),
    ("怀里", {"pinyin": ("huái lǐ", "huái li"), "pinyin_numeric": ("huai2 li3", "huai2 li5"),
             "bopomofo": ("ㄏㄨㄞˊ ㄌㄧˇ", "ㄏㄨㄞˊ ㄌㄧ˙")}),
    ("那里", {"pinyin": ("nà li", "nà lǐ"), "pinyin_numeric": ("na4 li5", "na4 li3"),
             "bopomofo": ("ㄋㄚˋ ㄌㄧ˙", "ㄋㄚˋ ㄌㄧˇ")}),
    ("噼里啪啦", {"pinyin": ("pī lǐ pā lā", "pī li pā lā"),
               "bopomofo": ("ㄆㄧ ㄌㄧˇ ㄆㄚ ㄌㄚ", "ㄆㄧ ㄌㄧ˙ ㄆㄚ ㄌㄚ")}),
    ("木匠", {"pinyin": ("mù jiàng", "mù jiang"), "pinyin_numeric": ("mu4 jiang4", "mu4 jiang5"),
             "bopomofo": ("ㄇㄨˋ ㄐㄧㄤˋ", "ㄇㄨˋ ㄐㄧㄤ˙")}),
    ("早晨", {"pinyin": ("zǎo chén", "zǎo chen"), "pinyin_numeric": ("zao3 chen2", "zao3 chen5"),
             "bopomofo": ("ㄗㄠˇ ㄔㄣˊ", "ㄗㄠˇ ㄔㄣ˙"),
             "arti:meanings_id": ("juga dibaca [zao3chen5]", "juga dibaca [zao3chen2]"),
             "arti:meanings_en": ("also pr. [zǎo chen]", "also pr. [zǎo chén]")}),
    ("玫瑰", {"pinyin": ("méi guī", "méi gui"), "pinyin_numeric": ("mei2 gui1", "mei2 gui5"),
             "bopomofo": ("ㄇㄟˊ ㄍㄨㄟ", "ㄇㄟˊ ㄍㄨㄟ˙")}),
    ("精神", {"arti:meanings_id:semangat; vitalitas": ("semangat; vitalitas", "[jīngshen] semangat; vitalitas"),
             "arti:meanings_id:bersemangat": ("bersemangat", "[jīngshen] bersemangat"),
             "arti:meanings_id:tampan": ("tampan", "[jīngshen] tampan")}),
]


def tulis_teks(data, akhir_baris_akhir):
    return json.dumps(data, ensure_ascii=False, indent=2).replace("\n", "\r\n") + akhir_baris_akhir


def baca_json(path):
    mentah = path.read_bytes().decode("utf-8")
    akhir = "\r\n" if mentah.endswith("\r\n") else ("\n" if mentah.endswith("\n") else "")
    data = json.loads(mentah)
    if tulis_teks(data, akhir) != mentah:
        return None, None
    return data, akhir


# ---------------------------------------------------------------- penyejajaran (sama dengan skrip tahap 4)
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


def usul_li(cn, py, app_idx, cc_idx):
    """Kembalikan (diubah, tetap, galat).
    diubah = daftar (indeks_huruf_l, lama, baru, jenis, target)
    tetap  = daftar (jenis, target, lama)   -- 里 yang sudah benar"""
    if unicodedata.normalize("NFC", py) != py:
        return None, None, "pinyin lama tidak dalam bentuk NFC"
    hasil = selaraskan(cn, py, app_idx, cc_idx)
    if hasil is None:
        return None, None, "pinyin lama tidak bisa disejajarkan dengan hanzi"
    items, idx, huruf = hasil
    posisi_hanzi = [i for i, ch in enumerate(cn) if HANZI.match(ch)]
    if len(posisi_hanzi) != len(items) or any(cn[posisi_hanzi[k]] != it["hz"] for k, it in enumerate(items)):
        return None, None, "urutan hanzi tidak sejajar dengan hasil pemecahan"
    diubah, tetap = [], []
    pos = 0
    for k, it in enumerate(items):
        n = len(dn.tanpa_nada(it["syl"]))
        lama = "".join(huruf[pos:pos + n])
        awal = pos
        pos += n
        if it["hz"] != "里":
            continue
        i = posisi_hanzi[k]
        prev = cn[i - 1] if i > 0 else ""
        nxt = cn[i + 1] if i + 1 < len(cn) else ""
        jenis, target = klasifikasi(prev, nxt)
        if lama.lower() not in ("li", "lǐ"):
            return None, None, "bacaan 里 tak terduga: %s" % lama
        besar = lama[0].isupper()
        baru = ("L" if besar else "l") + ("ǐ" if target == "penuh" else "i")
        if baru == lama:
            tetap.append((jenis, target, lama))
        else:
            diubah.append((idx[awal], lama, baru, jenis, target))
    return diubah, tetap, None


# ---------------------------------------------------------------- kamus
def rencana_kamus(app):
    """Kembalikan (daftar_perubahan, sudah, galat). daftar_perubahan = (indeks_entri, hanzi, isian, lama, baru)."""
    perubahan, sudah, galat = [], 0, []
    for hz, isian in PERUBAHAN_KAMUS:
        cocok = [i for i, e in enumerate(app) if e.get("simplified") == hz]
        if len(cocok) != 1:
            galat.append("%s: ditemukan %d entri (harus tepat 1)" % (hz, len(cocok)))
            continue
        i = cocok[0]
        e = app[i]
        for kunci, (lama, baru) in isian.items():
            if kunci.startswith("arti:"):
                bagian = kunci.split(":")
                daftar = e.get(bagian[1], [])
                if baru in daftar and lama not in daftar:
                    sudah += 1
                elif daftar.count(lama) == 1:
                    perubahan.append((i, hz, kunci, lama, baru))
                else:
                    galat.append("%s: arti '%s' di %s tidak ditemukan tepat sekali" % (hz, lama, bagian[1]))
            else:
                skrg = e.get(kunci)
                if skrg == baru:
                    sudah += 1
                elif skrg == lama:
                    perubahan.append((i, hz, kunci, lama, baru))
                else:
                    galat.append("%s: isian %s sekarang %r, bukan %r (lama) atau %r (baru)" % (hz, kunci, skrg, lama, baru))
    return perubahan, sudah, galat


def terapkan_kamus(app, perubahan):
    for i, hz, kunci, lama, baru in perubahan:
        if kunci.startswith("arti:"):
            medan = kunci.split(":")[1]
            app[i][medan][app[i][medan].index(lama)] = baru
        else:
            app[i][kunci] = baru


# ---------------------------------------------------------------- laporan berkas lain
def hitung_berkas_lain():
    """Hitung kemunculan hanzi 里 di berkas data lain (HANYA dilaporkan)."""
    hasil = []
    for p in sorted((ROOT / "data").rglob("*.json")):
        if p.name in ("nuance_pairs.json", "app_words.json") or "arsip" in p.parts:
            continue
        try:
            n = p.read_text(encoding="utf-8").count("里")
        except Exception:
            continue
        if n:
            hasil.append((str(p.relative_to(ROOT)).replace("/", "\\"), n))
    return hasil


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser(description="Seragamkan 里 netral dan rapikan 6 kata kamus terkurasi")
    ap.add_argument("--apply", action="store_true", help="benar-benar menulis (tanpa ini hanya menampilkan ringkasan)")
    a = ap.parse_args()

    for p in (NUANCE, APP):
        if not p.exists():
            print("Tidak menemukan %s. Letakkan skrip ini di folder utama proyek (mis. C:\\mandarin_app)." % p)
            return 1
    print("Mode: %s\n" % ("TERAPKAN (--apply)" if a.apply else "LIHAT-DULU (tidak mengubah apa pun)"))

    nuance, akhir_n = baca_json(NUANCE)
    app, akhir_a = baca_json(APP)
    if nuance is None or app is None:
        print("BERHENTI: format berkas sekarang tidak bisa ditulis ulang persis sama (akan ada perubahan tak terduga).")
        print("Tidak ada yang diubah. Kirim pesan ini ke Claude.")
        return 1

    _, app_idx, cc_idx = dn.muat()

    # ---- bagian 1: contoh nuansa
    rencana, dilewati = [], []
    stat = {}   # (jenis, target, status) -> jumlah
    for pi, p in enumerate(nuance["pairs"]):
        for ci, c in enumerate(p["comparison"]):
            cn = c.get("example_cn", "")
            py = c.get("example_pinyin", "")
            if "里" not in cn:
                continue
            diubah, tetap, galat = usul_li(cn, py, app_idx, cc_idx)
            if galat:
                dilewati.append((p["id"], c["word"], cn, py, galat))
                continue
            for jenis, target, lama in tetap:
                stat[(jenis, target, "sudah benar")] = stat.get((jenis, target, "sudah benar"), 0) + 1
            if not diubah:
                continue
            teks = list(py)
            for il, lama, baru, jenis, target in diubah:
                teks[il] = baru[0]
                teks[il + 1] = baru[1]
                kunci = (jenis, target, "diubah %s -> %s" % (lama, baru))
                stat[kunci] = stat.get(kunci, 0) + 1
            rencana.append((pi, ci, py, "".join(teks), diubah, p["id"], c["word"], cn))

    print("=== 1. data\\nuance_pairs.json (contoh kalimat) ===")
    print("Contoh yang akan diubah               : %d  (kemunculan 里: %d)" % (len(rencana), sum(len(r[4]) for r in rencana)))
    print("Dilewati (pinyin tak bisa disejajarkan): %d" % len(dilewati))
    for pid, kata, cn, py, galat in dilewati:
        print("     %s / %s | %s | %s | %s" % (pid, kata, cn, py, galat))
    print("Rincian per jenis 里 (kemunculan):")
    for (jenis, target, status), n in sorted(stat.items(), key=lambda x: (x[0][0], x[0][2])):
        print("   %-36s -> %-6s  %-18s %d" % (jenis, "lǐ" if target == "penuh" else "li", status, n))

    # ---- bagian 2: kamus
    pk, sudah_k, galat_k = rencana_kamus(app)
    print("\n=== 2. data\\app_words.json (kamus terkurasi) ===")
    if galat_k:
        print("BERHENTI: isian kamus tidak seperti yang diharapkan:")
        for g in galat_k:
            print("     " + g)
        print("Tidak ada yang diubah. Kirim pesan ini ke Claude.")
        return 1
    print("Isian yang akan diubah: %d  (sudah benar: %d)" % (len(pk), sudah_k))
    for i, hz, kunci, lama, baru in pk:
        print("   %-5s %-24s %s  ->  %s" % (hz, kunci, lama, baru))

    # ---- rujukan lama di arti kata lain (hanya dilaporkan)
    lama_str = ["jia1 li3", "shou3 li3", "cheng2 li3", "huai2 li3", "na4 li5", "mu4 jiang4", "zao3 chen2", "mei2 gui1"]
    rujukan = []
    for e in app:
        for medan in ("meanings_id", "meanings_en"):
            for m in e.get(medan, []):
                if any(s in m for s in lama_str) and e["simplified"] not in {h for h, _ in PERUBAHAN_KAMUS}:
                    rujukan.append((e["simplified"], medan, m))
    print("Rujukan bacaan lama di arti kata LAIN (dilaporkan, tidak diubah): %d" % len(rujukan))
    for r in rujukan[:10]:
        print("     %s | %s | %s" % r)

    # ---- berkas lain
    lain = hitung_berkas_lain()
    print("\n=== 3. Berkas lain yang memuat hanzi 里 (HANYA dilaporkan, tidak diubah; bahan tahap kedua) ===")
    for nama, n in lain:
        print("   %-48s %d" % (nama, n))

    baris = ["DAFTAR PERUBAHAN 里 NETRAL -- %d contoh nuansa, %d isian kamus" % (len(rencana), len(pk)), "", "## NUANSA"]
    for r in rencana:
        baris += ["%s / %s" % (r[5], r[6]), "   %s" % r[7], "   lama: %s" % r[2], "   baru: %s" % r[3]]
    baris += ["", "## KAMUS (app_words.json)"]
    for i, hz, kunci, lama, baru in pk:
        baris.append("   %s | %s | %s -> %s" % (hz, kunci, lama, baru))
    baris += ["", "## RUJUKAN LAMA DI ARTI KATA LAIN (tidak diubah)"]
    for r in rujukan:
        baris.append("   %s | %s | %s" % r)
    baris += ["", "## BERKAS LAIN (tidak diubah)"]
    for nama, n in lain:
        baris.append("   %s: %d" % (nama, n))
    if dilewati:
        baris += ["", "## DILEWATI"]
        for d in dilewati:
            baris.append("   %s / %s | %s | %s | %s" % d)

    if not rencana and not pk:
        print("\nTidak ada yang perlu diubah.")
        return 0
    if not a.apply:
        HASIL.write_text("\r\n".join(baris) + "\r\n", encoding="utf-8-sig")
        print("\nIni baru ringkasan; belum ada yang diubah. Daftar lengkap: %s" % HASIL.name)
        print("Untuk menerapkan: python perbaiki_li_netral.py --apply")
        return 0

    # ---- terapkan
    cap = datetime.now().strftime("%Y%m%d_%H%M%S")
    cad_n = NUANCE.with_name("nuance_pairs.json.bak_li_" + cap)
    cad_a = APP.with_name("app_words.json.bak_li_" + cap)
    shutil.copy2(NUANCE, cad_n)
    shutil.copy2(APP, cad_a)
    asli_n, asli_a = copy.deepcopy(nuance), copy.deepcopy(app)

    for pi, ci, lama, baru, dp, pid, kata, cn in rencana:
        nuance["pairs"][pi]["comparison"][ci]["example_pinyin"] = baru
    terapkan_kamus(app, pk)
    NUANCE.write_bytes(tulis_teks(nuance, akhir_n).encode("utf-8"))
    APP.write_bytes(tulis_teks(app, akhir_a).encode("utf-8"))

    # pemeriksaan akhir
    harapan_n = copy.deepcopy(asli_n)
    ok = True
    for pi, ci, lama, baru, dp, pid, kata, cn in rencana:
        harapan_n["pairs"][pi]["comparison"][ci]["example_pinyin"] = baru
        if len(lama) != len(baru):
            ok = False
            continue
        for x, y in zip(lama, baru):
            if x != y and {x.lower(), y.lower()} != {"i", "ǐ"}:
                ok = False
    harapan_a = copy.deepcopy(asli_a)
    terapkan_kamus(harapan_a, pk)
    try:
        ulang_n = json.loads(NUANCE.read_bytes().decode("utf-8"))
        ulang_a = json.loads(APP.read_bytes().decode("utf-8"))
        cocok = ok and ulang_n == harapan_n and ulang_a == harapan_a and len(ulang_a) == len(asli_a)
    except Exception:
        cocok = False
    if not cocok:
        shutil.copy2(cad_n, NUANCE)
        shutil.copy2(cad_a, APP)
        print("\nPEMERIKSAAN AKHIR GAGAL: kedua berkas dikembalikan dari cadangan. Kirim pesan ini ke Claude.")
        return 1
    HASIL.write_text("\r\n".join(baris) + "\r\n", encoding="utf-8-sig")
    print("\nSelesai: %d contoh nuansa dan %d isian kamus diperbaiki." % (len(rencana), len(pk)))
    print("Cadangan: %s dan %s" % (cad_n.name, cad_a.name))
    print("Pemeriksaan akhir lolos (hanya isian yang direncanakan berubah; %d kata kamus utuh)." % len(ulang_a))
    print("Daftar lengkap perubahan: %s" % HASIL.name)
    return 0


if __name__ == "__main__":
    sys.exit(main())

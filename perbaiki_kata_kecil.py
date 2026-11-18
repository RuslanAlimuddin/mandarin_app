#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
perbaiki_kata_kecil.py -- beres-beres kecil data kata (18 November 2026)
=======================================================================
Tiga perbaikan yang sudah disetujui:

 1) 儿 (12 kata)
    - 10 kata yang pinyinnya ditulis "r5" (不一会儿 没法儿 小偷儿 胡同儿 名牌儿 有劲儿 有空儿
      离谱儿 笑话儿 贪玩儿) dijadikan format normal: pinyin berspasi dan berakhir " r",
      pinyin_numeric berakhir " r5" (nada diambil dari zhuyin yang sudah benar).
    - 纽扣儿: "niǔ kòu er" -> "niǔ kòu r" dan numerik "...er5" -> "...r5".
    - 干女儿: pinyin_numeric yang kosong diisi "gan1 nü3 er2".
 2) 圣诞: 7 kata benda biasa (圣诞树 圣诞歌 圣诞卡 圣诞晚餐 圣诞帽 圣诞袜 圣诞市场) ditulis dengan huruf
    kecil. 圣诞节 dan 圣诞老人 tetap berkapital.
 3) 焦糖玛奇果 -> 焦糖玛奇朵 (karamel makiato): hanzi, traditional (焦糖瑪奇朵), pinyin duǒ, numerik duo3,
    zhuyin ㄉㄨㄛˇ, jumlah goresan 51 -> 49, komponen 田 -> 几, arti "karamel makiato".

Berkas yang diubah:
    data/app_words.json, data/index_theme.json, data/produktif_karakter.json,
    skrip/build_theme_entries.py   (generator tema: supaya salah ketiknya tidak kembali)
Catatan: perbaiki_frasa.py (skrip sekali pakai) masih memuat tabel lama 纽扣儿; tidak diubah, jangan dijalankan ulang.

CARA PAKAI (dari C:\\mandarin_app>):
  1) Lihat dulu (TIDAK mengubah apa pun):   python perbaiki_kata_kecil.py
  2) Terapkan:                              python perbaiki_kata_kecil.py --apply

KEAMANAN
  - Tiap perubahan hanya dijalankan bila isi sekarang SAMA PERSIS dengan yang saya periksa. Bila ada
    yang berbeda, skrip berhenti dan tidak mengubah apa pun. Yang sudah berisi nilai baru dilewati.
  - Sebelum menulis, tiap berkas dicadangkan: <nama>.bak_datakecil_<tanggal-jam>
  - Format tiap berkas JSON dijaga persis (indent 2, ensure_ascii=False, CRLF); skrip menolak bekerja
    bila sebuah berkas tidak bisa ditulis ulang persis sama.
  - Setelah menulis, hasilnya dibaca ulang dan diperiksa: hanya 20 kata di app_words.json yang boleh
    berbeda, tidak ada lagi "r5" berpola salah, dan 焦糖玛奇果 tidak tersisa. Bila ada yang tidak cocok,
    semua berkas dikembalikan dari cadangan.
"""
import argparse
import copy
import json
import re
import shutil
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent
APP = ROOT / "data" / "app_words.json"
THEME = ROOT / "data" / "index_theme.json"
PROD = ROOT / "data" / "produktif_karakter.json"
GEN = ROOT / "skrip" / "build_theme_entries.py"

# kata, pinyin lama, numerik lama, pinyin baru, numerik baru
ERHUA = [
    ("不一会儿", "bù yīhuǐr5", "bu4 yīhuǐr5", "bù yī huǐ r", "bu4 yi1 hui3 r5"),
    ("没法儿", "méifǎr5", "méifǎr5", "méi fǎ r", "mei2 fa3 r5"),
    ("小偷儿", "xiǎotōur5", "xiǎotōur5", "xiǎo tōu r", "xiao3 tou1 r5"),
    ("胡同儿", "hútòngr5", "hútòngr5", "hú tòng r", "hu2 tong4 r5"),
    ("名牌儿", "míngpáir5", "míngpáir5", "míng pái r", "ming2 pai2 r5"),
    ("有劲儿", "yǒujìnr5", "yǒujìnr5", "yǒu jìn r", "you3 jin4 r5"),
    ("有空儿", "yǒukòngr5", "yǒukòngr5", "yǒu kòng r", "you3 kong4 r5"),
    ("离谱儿", "lí pǔr5", "li2 pǔr5", "lí pǔ r", "li2 pu3 r5"),
    ("笑话儿", "xiàohuar5", "xiàohuar5", "xiào hua r", "xiao4 hua5 r5"),
    ("贪玩儿", "tān wánr5", "tan1 wánr5", "tān wán r", "tan1 wan2 r5"),
    ("纽扣儿", "niǔ kòu er", "niu3 kou4 er5", "niǔ kòu r", "niu3 kou4 r5"),
]
GAN_NV_ER = ("干女儿", "gan1 nü3 er2")  # pinyin_numeric kosong (null) -> diisi

# kata, pinyin lama (berkapital), numerik lama
NATAL = [
    ("圣诞树", "Shèng dàn shù", "Sheng4 dan4 shu4"),
    ("圣诞歌", "Shèng dàn gē", "Sheng4 dan4 ge1"),
    ("圣诞卡", "Shèng dàn kǎ", "Sheng4 dan4 ka3"),
    ("圣诞晚餐", "Shèng dàn wǎn cān", "Sheng4 dan4 wan3 can1"),
    ("圣诞帽", "Shèng dàn mào", "Sheng4 dan4 mao4"),
    ("圣诞袜", "Shèng dàn wà", "Sheng4 dan4 wa4"),
    ("圣诞市场", "Shèng dàn shì chǎng", "Sheng4 dan4 shi4 chang3"),
]
NATAL_TETAP_KAPITAL = {"圣诞节", "圣诞老人"}


def kecil(s):
    return s[0].lower() + s[1:]


KOPI_LAMA, KOPI_BARU = "焦糖玛奇果", "焦糖玛奇朵"
KOPI_APP = [  # isian, lama, baru
    ("id", "焦糖玛奇果", "焦糖玛奇朵"),
    ("simplified", "焦糖玛奇果", "焦糖玛奇朵"),
    ("traditional", "焦糖玛奇果", "焦糖瑪奇朵"),
    ("pinyin", "jiāo táng mǎ qí guǒ", "jiāo táng mǎ qí duǒ"),
    ("pinyin_numeric", "jiao1 tang2 ma3 qi2 guo3", "jiao1 tang2 ma3 qi2 duo3"),
    ("bopomofo", "ㄐㄧㄠ ㄊㄤˊ ㄇㄚˇ ㄑㄧˊ ㄍㄨㄛˇ", "ㄐㄧㄠ ㄊㄤˊ ㄇㄚˇ ㄑㄧˊ ㄉㄨㄛˇ"),
    ("stroke_count", 51, 49),
    ("components", ["隹", "灬", "米", "唐", "王", "马", "大", "可", "田", "木"], ["隹", "灬", "米", "唐", "王", "马", "大", "可", "几", "木"]),
    ("meanings_id", ["karamel machiato"], ["karamel makiato"]),
]
KOPI_NOTE_LAMA = ("AllSet Learning Vocabulary Wiki (CC BY-NC), https://resources.allsetlearning.com/ "
                  "-- traditional diasumsikan sama dgn simplified (TIDAK divalidasi cidict)")
KOPI_NOTE_BARU = KOPI_NOTE_LAMA + " | 18 Nov 2026: hanzi dikoreksi 果->朵, traditional diisi 瑪奇朵"
KOPI_PROD = {"pinyin": ("jiāo táng mǎ qí guǒ", "jiāo táng mǎ qí duǒ"), "arti": ("karamel machiato", "karamel makiato")}
KOPI_PROD_AKAR = {"焦", "糖"}
KOPI_PROD_BARU_ENTRI = {"kata": KOPI_BARU, "pinyin": "jiāo táng mǎ qí duǒ", "arti": "karamel makiato", "hsk": None}

GEN_GANTI = (
    [("'%s': '%s'" % (k, p), "'%s': '%s'" % (k, kecil(p))) for k, p, n in NATAL]
    + [("'焦糖玛奇果':'karamel machiato'", "'焦糖玛奇朵':'karamel makiato'"),
       ("'焦糖玛奇果': 'jiāo táng mǎ qí guǒ'", "'焦糖玛奇朵': 'jiāo táng mǎ qí duǒ'")]
)

POLA_R5 = re.compile(r"[a-zāáǎàēéěèīíǐìōóǒòūúǔùǖǘǚǜ]r5")


def muat_json(path):
    mentah = path.read_bytes().decode("utf-8")
    data = json.loads(mentah)
    teks = tulis_teks(data, "")
    if teks != mentah:
        raise RuntimeError("%s tidak bisa ditulis ulang persis sama (format berbeda dari yang diperiksa)" % path.name)
    return data


def tulis_teks(data, akhir):
    return json.dumps(data, ensure_ascii=False, indent=2).replace("\n", "\r\n") + akhir


class Rencana:
    def __init__(self):
        self.aksi = []       # (objek, kunci, nilai baru)
        self.sudah = 0
        self.masalah = []
        self.catatan = []

    def ubah(self, obj, kunci, lama, baru, label):
        skrg = obj.get(kunci, "<tidak ada>")
        if skrg == lama and lama != baru:
            self.aksi.append((obj, kunci, baru))
            return True
        if skrg == baru:
            self.sudah += 1
            return False
        self.masalah.append("%s -- %s: isi sekarang %r, yang diperiksa %r" % (label, kunci, skrg, lama))
        return False


def cari_kata(app, kata, rencana):
    hit = [w for w in app if w.get("simplified") == kata]
    if len(hit) != 1:
        rencana.masalah.append("app_words.json: kata %s ditemukan %d kali (seharusnya 1)" % (kata, len(hit)))
        return None
    return hit[0]


def susun(app, theme, prod, gen_teks, r):
    # ---------- 1) 儿 ----------
    for kata, pl, nl, pb, nb in ERHUA:
        w = cari_kata(app, kata, r)
        if w is None:
            continue
        a = r.ubah(w, "pinyin", pl, pb, "app_words " + kata)
        b = r.ubah(w, "pinyin_numeric", nl, nb, "app_words " + kata)
        if a or b:
            r.catatan.append(("app_words.json", kata, "pinyin %s -> %s | numerik %s -> %s" % (pl, pb, nl, nb)))
    kata, nb = GAN_NV_ER
    w = cari_kata(app, kata, r)
    if w is not None and r.ubah(w, "pinyin_numeric", None, nb, "app_words " + kata):
        r.catatan.append(("app_words.json", kata, "numerik (kosong/null) -> %s" % nb))
    # salinan di produktif_karakter.json (hanya isian pinyin tampil)
    n_prod = {k: 0 for k, *_ in ERHUA}
    peta = {k: (pl, pb) for k, pl, nl, pb, nb in ERHUA}
    for akar, v in prod.items():
        for e in v.get("kata_turunan", []):
            if e.get("kata") in peta:
                pl, pb = peta[e["kata"]]
                if r.ubah(e, "pinyin", pl, pb, "produktif_karakter akar %s kata %s" % (akar, e["kata"])):
                    n_prod[e["kata"]] += 1
    jml = sum(n_prod.values())
    if jml:
        r.catatan.append(("produktif_karakter.json", "kata 儿", "%d salinan pinyin diperbaiki" % jml))

    # ---------- 2) 圣诞 ----------
    for kata, pl, nl in NATAL:
        w = cari_kata(app, kata, r)
        if w is None:
            continue
        a = r.ubah(w, "pinyin", pl, kecil(pl), "app_words " + kata)
        b = r.ubah(w, "pinyin_numeric", nl, kecil(nl), "app_words " + kata)
        if a or b:
            r.catatan.append(("app_words.json", kata, "%s -> %s | %s -> %s" % (pl, kecil(pl), nl, kecil(nl))))
    peta = {k: (pl, kecil(pl)) for k, pl, nl in NATAL}
    n = 0
    for akar, v in prod.items():
        for e in v.get("kata_turunan", []):
            if e.get("kata") in peta:
                pl, pb = peta[e["kata"]]
                if r.ubah(e, "pinyin", pl, pb, "produktif_karakter akar %s kata %s" % (akar, e["kata"])):
                    n += 1
    if n:
        r.catatan.append(("produktif_karakter.json", "kata 圣诞", "%d salinan pinyin diperbaiki" % n))

    # ---------- 3) 焦糖玛奇朵 ----------
    hit = [w for w in app if w.get("simplified") in (KOPI_LAMA, KOPI_BARU)]
    if len(hit) != 1:
        r.masalah.append("app_words.json: entri 焦糖玛奇果/朵 ditemukan %d kali (seharusnya 1)" % len(hit))
    else:
        w = hit[0]
        for isian, lama, baru in KOPI_APP:
            if r.ubah(w, isian, lama, baru, "app_words 焦糖玛奇果"):
                r.catatan.append(("app_words.json", "焦糖玛奇果", "%s: %s -> %s" % (isian, lama, baru)))
        if r.ubah(w, "_source_note", KOPI_NOTE_LAMA, KOPI_NOTE_BARU, "app_words 焦糖玛奇果"):
            r.catatan.append(("app_words.json", "焦糖玛奇果", "_source_note: ditambah keterangan koreksi"))
    # index_theme.json: nilai teks persis di dalam daftar
    n_tema = [0, 0]

    def jelajah(x):
        if isinstance(x, list):
            for i, el in enumerate(x):
                if el == KOPI_LAMA:
                    r.aksi.append((x, i, KOPI_BARU)); n_tema[0] += 1
                elif el == KOPI_BARU:
                    n_tema[1] += 1
                else:
                    jelajah(el)
        elif isinstance(x, dict):
            for v in x.values():
                jelajah(v)
    jelajah(theme)
    if n_tema[0] + n_tema[1] != 1:
        r.masalah.append("index_theme.json: 焦糖玛奇果/朵 ditemukan %d kali (seharusnya 1)" % (n_tema[0] + n_tema[1]))
    elif n_tema[0]:
        r.catatan.append(("index_theme.json", "tema", "焦糖玛奇果 -> 焦糖玛奇朵"))
    else:
        r.sudah += 1
    # produktif_karakter.json: akar 焦 dan 糖 (ganti), akar 朵 (tambah)
    akar_ada = set()
    for akar, v in prod.items():
        for e in v.get("kata_turunan", []):
            if e.get("kata") in (KOPI_LAMA, KOPI_BARU):
                akar_ada.add(akar)
                lbl = "produktif_karakter akar %s kata 焦糖玛奇果" % akar
                if akar not in KOPI_PROD_AKAR:
                    continue
                ubah_kata = r.ubah(e, "kata", KOPI_LAMA, KOPI_BARU, lbl)
                for fld, (lama, baru) in KOPI_PROD.items():
                    r.ubah(e, fld, lama, baru, lbl)
                if ubah_kata:
                    r.catatan.append(("produktif_karakter.json", "akar " + akar, "焦糖玛奇果 -> 焦糖玛奇朵 (pinyin dan arti ikut)"))
    sisa = akar_ada - KOPI_PROD_AKAR - {"朵"}
    if sisa or not KOPI_PROD_AKAR <= akar_ada:
        r.masalah.append("produktif_karakter.json: kata 焦糖玛奇果 ada di akar %s (diperiksa: 焦 dan 糖)" % sorted(akar_ada))
    d = prod.get("朵")
    if d is None:
        r.masalah.append("produktif_karakter.json: akar 朵 tidak ada")
    elif any(e.get("kata") == KOPI_BARU for e in d["kata_turunan"]):
        r.sudah += 1
    elif d.get("jumlah_turunan") == 1 and len(d["kata_turunan"]) == 1:
        r.aksi.append((d["kata_turunan"], len(d["kata_turunan"]), copy.deepcopy(KOPI_PROD_BARU_ENTRI)))
        r.aksi.append((d, "jumlah_turunan", 2))
        r.catatan.append(("produktif_karakter.json", "akar 朵", "焦糖玛奇朵 ditambahkan (jumlah turunan 1 -> 2)"))
    else:
        r.masalah.append("produktif_karakter.json: akar 朵 berbeda dari yang diperiksa (jumlah_turunan=%r, panjang=%d)"
                         % (d.get("jumlah_turunan"), len(d["kata_turunan"])))
    # generator tema
    gen_baru = gen_teks
    n_gen = 0
    for lama, baru in GEN_GANTI:
        if gen_baru.count(lama) == 1:
            gen_baru = gen_baru.replace(lama, baru); n_gen += 1
        elif gen_baru.count(baru) == 1 and gen_baru.count(lama) == 0:
            r.sudah += 1
        else:
            r.masalah.append("build_theme_entries.py: teks %r ditemukan %d kali (seharusnya 1)" % (lama, gen_baru.count(lama)))
    if n_gen:
        r.catatan.append(("skrip/build_theme_entries.py", "generator", "%d baris diperbaiki (7 pinyin 圣诞 huruf kecil, 焦糖玛奇朵 arti dan pinyin)" % n_gen))
    return gen_baru


def terapkan_aksi(r):
    for obj, kunci, nilai in r.aksi:
        if isinstance(obj, list) and kunci == len(obj):
            obj.append(nilai)
        else:
            obj[kunci] = nilai


def periksa_akhir(app0, app1, prod1, theme1, gen1):
    """Pemeriksaan bebas atas berkas hasil. Kembalikan daftar masalah."""
    m = []
    if len(app0) != len(app1):
        m.append("jumlah kata app_words.json berubah")
        return m
    beda = [i for i, (a, b) in enumerate(zip(app0, app1)) if a != b]
    if len(beda) != 20:
        m.append("yang berubah di app_words.json %d kata, seharusnya 20" % len(beda))
    for i in beda:
        kunci = {k for k in set(app0[i]) | set(app1[i]) if app0[i].get(k) != app1[i].get(k)}
        if not kunci <= {"pinyin", "pinyin_numeric", "id", "simplified", "traditional", "bopomofo", "stroke_count",
                         "components", "meanings_id", "_source_note"}:
            m.append("kata %s: isian tak terduga berubah: %s" % (app0[i]["simplified"], sorted(kunci)))
    for w in app1:
        for f in ("pinyin", "pinyin_numeric"):
            if isinstance(w.get(f), str) and POLA_R5.search(w[f]):
                m.append("masih ada pola r5 salah: %s %s" % (w["simplified"], w[f]))
        if w["simplified"].startswith("圣诞") and w["pinyin"][:1].isupper() != (w["simplified"] in NATAL_TETAP_KAPITAL):
            m.append("huruf kapital 圣诞 tidak sesuai: %s %s" % (w["simplified"], w["pinyin"]))
    for e in (e for v in prod1.values() for e in v["kata_turunan"]):
        if POLA_R5.search(e.get("pinyin") or ""):
            m.append("produktif_karakter: masih ada pola r5: %s" % e["kata"])
        if e["kata"].startswith("圣诞") and e["pinyin"][:1].isupper() != (e["kata"] in NATAL_TETAP_KAPITAL):
            m.append("produktif_karakter: huruf kapital 圣诞 tidak sesuai: %s" % e["kata"])
    for nama, teks in (("app_words.json", json.dumps(app1, ensure_ascii=False)), ("index_theme.json", json.dumps(theme1, ensure_ascii=False)),
                       ("produktif_karakter.json", json.dumps(prod1, ensure_ascii=False)), ("build_theme_entries.py", gen1)):
        if KOPI_LAMA in teks:
            m.append("%s masih memuat 焦糖玛奇果" % nama)
        if KOPI_BARU not in teks:
            m.append("%s tidak memuat 焦糖玛奇朵" % nama)
    if prod1["朵"]["jumlah_turunan"] != 2 or len(prod1["朵"]["kata_turunan"]) != 2:
        m.append("akar 朵 di produktif_karakter.json tidak berisi 2 turunan")
    return m


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser(description="Beres-beres kecil data kata: 儿, 圣诞, 焦糖玛奇朵")
    ap.add_argument("--apply", action="store_true", help="benar-benar menulis (tanpa ini hanya menampilkan daftar)")
    a = ap.parse_args()
    for p in (APP, THEME, PROD, GEN):
        if not p.exists():
            print("Tidak menemukan %s. Letakkan skrip ini di folder utama proyek (mis. C:\\mandarin_app)." % p)
            return 1
    print("Folder proyek: %s" % ROOT)
    print("Mode: %s\n" % ("TERAPKAN (--apply)" if a.apply else "LIHAT-DULU (tidak mengubah apa pun)"))
    try:
        app, theme, prod = muat_json(APP), muat_json(THEME), muat_json(PROD)
    except RuntimeError as e:
        print("BERHENTI: %s\nTidak ada yang diubah. Kirim pesan ini ke Claude." % e)
        return 1
    app0 = copy.deepcopy(app)
    gen_teks = GEN.read_bytes().decode("utf-8")
    r = Rencana()
    gen_baru = susun(app, theme, prod, gen_teks, r)

    berkas = None
    for f, kata, ket in r.catatan:
        if f != berkas:
            berkas = f
            print("\n[%s]" % f)
        print("   %-12s %s" % (kata, ket))
    print("\n" + "=" * 70)
    print("Perubahan: %d isian/entri | sudah diperbaiki: %d | bermasalah: %d" % (len(r.aksi) + (1 if gen_baru != gen_teks else 0), r.sudah, len(r.masalah)))
    if r.masalah:
        print("\nBERHENTI (tidak ada yang diubah). Yang bermasalah:")
        for m in r.masalah:
            print("   " + m)
        print("Kirim pesan ini ke Claude.")
        return 1
    if not r.aksi and gen_baru == gen_teks:
        print("Tidak ada yang perlu diubah.")
        return 0
    if not a.apply:
        print("\nIni baru daftar; belum ada yang diubah. Untuk menerapkan: python perbaiki_kata_kecil.py --apply")
        return 0

    # ---------- terapkan ----------
    terapkan_aksi(r)
    gagal = periksa_akhir(app0, app, prod, theme, gen_baru)  # pemeriksaan atas data di memori sebelum menulis
    if gagal:
        print("\nPEMERIKSAAN SEBELUM MENULIS GAGAL (tidak ada yang ditulis):")
        for m in gagal:
            print("   " + m)
        return 1
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    daftar = [APP, THEME, PROD, GEN]
    cad = {}
    for p in daftar:
        c = p.with_name("%s.bak_datakecil_%s" % (p.name, stamp))
        shutil.copy2(p, c)
        cad[p] = c
    try:
        APP.write_bytes(tulis_teks(app, "").encode("utf-8"))
        THEME.write_bytes(tulis_teks(theme, "").encode("utf-8"))
        PROD.write_bytes(tulis_teks(prod, "").encode("utf-8"))
        GEN.write_bytes(gen_baru.encode("utf-8"))
        app2, theme2, prod2 = muat_json(APP), muat_json(THEME), muat_json(PROD)
        gen2 = GEN.read_bytes().decode("utf-8")
        gagal = periksa_akhir(app0, app2, prod2, theme2, gen2)
        if app2 != app or theme2 != theme or prod2 != prod or gen2 != gen_baru:
            gagal.append("isi berkas hasil tidak sama dengan yang direncanakan")
    except Exception as e:  # apa pun yang salah: kembalikan semua
        gagal = ["galat saat menulis/membaca ulang: %s" % e]
    if gagal:
        for p in daftar:
            shutil.copy2(cad[p], p)
        print("\nPEMERIKSAAN AKHIR GAGAL: semua berkas dikembalikan dari cadangan.")
        for m in gagal:
            print("   " + m)
        print("Kirim pesan ini ke Claude.")
        return 1
    print("\nSelesai. Cadangan (tanggal-jam %s):" % stamp)
    for p in daftar:
        print("   %s" % cad[p].relative_to(ROOT).as_posix())
    print("Pemeriksaan akhir lolos: 20 kata di app_words.json berubah, tidak ada pola r5 salah, 焦糖玛奇果 tidak tersisa.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

# -*- coding: utf-8 -*-
r"""
intip_komponen.py -- SKRIP BACA-SAJA (tidak mengubah file apa pun di data\).

Tujuan: memeriksa bagaimana komponen karakter tersimpan, supaya kita bisa
merancang menu "Per Komponen & Posisi" dan pemisahan Karakter Mirip.

Cara pakai (dari folder C:\mandarin_app):
    python intip_komponen.py
    python intip_komponen.py --data data --csv "C:\\path\\ke\\folder_csv"

Hasil: dicetak ke layar DAN disimpan ke laporan_komponen.txt
(kirim isi laporan_komponen.txt ke Claude; file data besar tidak perlu diunggah).
"""
import argparse
import collections
import csv
import glob
import io
import json
import os
import sys

CONTOH = list("须预住往鹤鸦迁迂铰销谓诵慢漫扬汤推椎")
IDC = set("⿰⿱⿲⿳⿴⿵⿶⿷⿸⿹⿺⿻")

out = io.StringIO()


def p(*a):
    s = " ".join(str(x) for x in a)
    print(s)
    out.write(s + "\n")


def load_json(path):
    with open(path, encoding="utf-8-sig") as f:
        return json.load(f)


def baca_app_words(path):
    data = load_json(path)
    if isinstance(data, dict):
        for k in ("words", "data", "entries"):
            if isinstance(data.get(k), list):
                data = data[k]
                break
    return data if isinstance(data, list) else []


def baca_dictionary(path):
    d = {}
    with open(path, encoding="utf-8-sig") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                o = json.loads(line)
            except Exception:
                continue
            ch = o.get("character")
            if ch:
                d[ch] = o
    return d


def pecah_ids(ids):
    """Pecah IDS tingkat pertama: kembalikan (idc, [bagian1, bagian2,...]) atau None."""
    if not ids or ids[0] not in IDC:
        return None
    idc = ids[0]
    n = 3 if idc in "⿲⿳" else 2
    rest = ids[1:]
    parts = []
    i = 0

    def ambil(s, i):
        # ambil satu operan IDS lengkap mulai posisi i, kembalikan akhir indeks
        if i >= len(s):
            return i
        c = s[i]
        if c in IDC:
            need = 3 if c in "⿲⿳" else 2
            j = i + 1
            for _ in range(need):
                j = ambil(s, j)
            return j
        if c == "&":
            j = s.find(";", i)
            return (j + 1) if j != -1 else i + 1
        return i + 1

    for _ in range(n):
        j = ambil(rest, i)
        if j == i:
            return None
        parts.append(rest[i:j])
        i = j
    return idc, parts


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default="data")
    ap.add_argument("--csv", default=".", help="folder berisi KARAKTER_MIRIP_*.csv (opsional)")
    args = ap.parse_args()

    f_words = os.path.join(args.data, "app_words.json")
    f_dict = os.path.join(args.data, "dictionary.txt")
    if not os.path.exists(f_dict):
        cari = glob.glob(os.path.join("**", "dictionary.txt"), recursive=True)
        if cari:
            f_dict = cari[0]

    p("=" * 70)
    p("1. app_words.json:", f_words, "ada?" , os.path.exists(f_words))
    words = baca_app_words(f_words) if os.path.exists(f_words) else []
    p("   jumlah entri:", len(words))
    if words:
        p("   field entri pertama:", sorted(words[0].keys()))
    singles = {}
    for w in words:
        s = w.get("simplified") or w.get("id") or ""
        if len(s) == 1 and s not in singles:
            singles[s] = w
    p("   entri karakter tunggal:", len(singles))
    punya_komp = [c for c, w in singles.items() if w.get("components")]
    p("   dari itu punya field components:", len(punya_komp))
    p("   punya field structure:", sum(1 for w in singles.values() if w.get("structure")))
    p("   punya field radical:", sum(1 for w in singles.values() if w.get("radical")))

    p("\n   Distribusi jumlah components per karakter tunggal:")
    dist = collections.Counter(len(w.get("components") or []) for w in singles.values())
    for k in sorted(dist):
        p("     %d komponen: %d karakter" % (k, dist[k]))

    p("\n   Contoh (karakter | structure | radical | components):")
    for c in CONTOH:
        w = singles.get(c)
        if w:
            p("     %s | %s | %s | %s" % (c, w.get("structure"), w.get("radical"), w.get("components")))
        else:
            p("     %s | (TIDAK ADA entri tunggal di app_words.json)" % c)

    # apakah radikal ikut di dalam components? apakah urutannya kiri->kanan?
    ikut = sum(1 for w in singles.values()
               if w.get("components") and w.get("radical") in (w.get("components") or []))
    p("\n   components memuat radikalnya sendiri:", ikut, "dari", len(punya_komp))
    p("   (jika angkanya mendekati 100%, radikal ikut tercatat di components)")

    p("\n" + "=" * 70)
    p("2. dictionary.txt:", f_dict, "ada?", os.path.exists(f_dict))
    dic = baca_dictionary(f_dict) if os.path.exists(f_dict) else {}
    p("   jumlah karakter:", len(dic))
    if dic:
        p("   field contoh:", sorted(next(iter(dic.values())).keys()))
    p("\n   Contoh (karakter | decomposition | radical | etymology):")
    for c in CONTOH:
        o = dic.get(c)
        if o:
            et = o.get("etymology") or {}
            p("     %s | %s | %s | %s" % (c, o.get("decomposition"), o.get("radical"), et))
        else:
            p("     %s | (tidak ada di dictionary.txt)" % c)

    idc_cnt = collections.Counter()
    dua_bagian = 0
    for c, o in dic.items():
        r = pecah_ids(o.get("decomposition") or "")
        if r:
            idc_cnt[r[0]] += 1
            if len(r[1]) == 2:
                dua_bagian += 1
    p("\n   Jenis susunan tingkat pertama (IDC):")
    for k, v in idc_cnt.most_common():
        p("     %s : %d" % (k, v))
    p("   karakter dengan 2 bagian tingkat pertama:", dua_bagian)

    p("\n" + "=" * 70)
    p("3. Cakupan karakter dari tiga CSV Karakter Mirip")
    kar = set()
    for nama in ("KARAKTER_MIRIP_FINAL_ACCEPTED.csv", "KARAKTER_MIRIP_REVIEW_REQUIRED.csv"):
        for fp in glob.glob(os.path.join(args.csv, "**", nama), recursive=True)[:1]:
            with open(fp, encoding="utf-8-sig", newline="") as f:
                rd = csv.DictReader(f)
                n = 0
                for r in rd:
                    a, b = (r.get("a") or "").strip(), (r.get("b") or "").strip()
                    if a and b:
                        kar.add(a)
                        kar.add(b)
                        n += 1
            p("   %s: %d baris" % (nama, n))
    if kar:
        p("   karakter unik:", len(kar))
        p("   ada di app_words.json (tunggal):", sum(1 for c in kar if c in singles))
        p("   ada di dictionary.txt:", sum(1 for c in kar if c in dic))
        p("   tidak ada di keduanya:", sorted(c for c in kar if c not in singles and c not in dic)[:40])
    else:
        p("   (CSV tidak ditemukan; jalankan dengan --csv <folder>)")

    with open("laporan_komponen.txt", "w", encoding="utf-8") as f:
        f.write(out.getvalue())
    p("\nTersimpan: laporan_komponen.txt")


if __name__ == "__main__":
    sys.exit(main())

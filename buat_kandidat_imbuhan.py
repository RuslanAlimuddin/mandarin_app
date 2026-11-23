#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
buat_kandidat_imbuhan.py -- berkas kerja untuk AI lain: memperbanyak daftar "bukan" imbuhan
===========================================================================================
Cara B latihan imbuhan (keputusan رسلان, 23 November 2026). Latihan "Imbuhan atau bukan?" di
Flashcard baru punya 40 kata "bukan" (dari 18 imbuhan). Skrip ini mendaftar KANDIDAT dari
data\\app_words.json: kata dua karakter ke atas yang memuat karakter imbuhan di posisi yang benar
(akhiran: di akhir kata; awalan: di awal kata) tetapi belum tercatat sebagai contoh atau "bukan".
Kandidat dibagi menjadi berkas-berkas teks yang SIAP DITEMPEL ke AI lain (satu berkas per percakapan).

TAHAP
  --tahap 1 (bawaan): 20 kata pertama per imbuhan, diutamakan kata berlevel HSK rendah   (735 kata)
  --tahap 2         : SISA kandidat yang tidak masuk tahap 1                              (433 kata)
                      (DITUNDA sampai ada waktu yang tepat -- jalankan nanti bila tahap 1 sudah selesai.)
Pembagian bersifat tetap (urut HSK, lalu urutan di kamus), jadi tahap 2 tidak pernah mengulang tahap 1
selama afiks_kamus.json dan app_words.json tidak berubah.

KONTROL
  Tiap berkas disisipi beberapa kata yang jawabannya SUDAH DIKETAHUI (contoh sah dan "bukan" yang sudah
  ada di data), tanpa tanda apa pun untuk AI. Gunanya mengukur ketelitian AI saat kurasi. Kata kontrol
  tidak ditampilkan di daftar contoh yang diberikan kepada AI. Kuncinya ada di _manifest_tahapN.json.

CARA PAKAI (dari C:\\mandarin_app>):
  1) Lihat dulu (TIDAK menulis apa pun):   python buat_kandidat_imbuhan.py
  2) Tulis berkas kerja:                   python buat_kandidat_imbuhan.py --apply
  Hasil: kerja_gpt_afiks\\kandidat\\tahap1\\batch_01.txt, batch_02.txt, ... , _manifest_tahap1.json,
         dan kerja_gpt_afiks\\kandidat\\CATATAN_LANJUTAN.md
  Skrip TIDAK mengubah data apa pun. Bila folder tahap itu sudah ada, skrip berhenti (tambahkan --timpa
  bila memang ingin membuat ulang).
"""
import argparse
import json
import random
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
AFIKS = ROOT / "data" / "afiks_kamus.json"
KATA = ROOT / "data" / "app_words.json"
KELUAR = ROOT / "kerja_gpt_afiks" / "kandidat"
BATAS_TAHAP1 = 20          # kandidat per imbuhan pada tahap 1
MAKS_PER_BERKAS = 60       # kandidat (termasuk kontrol) per berkas
MAKS_IMBUHAN_PER_BERKAS = 6
BIBIT = 20261123           # supaya penyisipan kontrol selalu sama

PROMPT = """PERAN
Kamu membantu menyusun bahan belajar Mandarin untuk pelajar berbahasa Indonesia.
Tugasmu: menilai apakah karakter imbuhan di dalam setiap kata kandidat BENAR-BENAR berfungsi sebagai
imbuhan yang dimaksud, atau hanya kebetulan ada di kata itu.

CARA MENILAI
Untuk setiap kata kandidat, nilai HANYA terhadap imbuhan dan fungsi yang tertulis pada bagian
"IMBUHAN" di bawah. Jangan memakai arti lain dari karakter itu.
- "imbuhan": karakter itu berfungsi persis seperti definisi yang diberikan.
- "bukan": karakter itu ada di kata tersebut, tetapi tidak berfungsi sebagai imbuhan itu
  (misalnya bagian dari kata dasar, kata serapan, atau punya arti lain).
- "ragu": kamu tidak yakin, atau fungsinya berada di antara keduanya / berbeda dari definisi.
  Lebih baik "ragu" daripada menebak.

ATURAN KERAS (tidak boleh dilanggar)
1. Jangan mengarang. Pinyin dan arti kata sudah diberikan; pakailah itu apa adanya.
2. Beri tepat satu entri untuk SETIAP kata pada daftar, dengan urutan yang sama dengan nomor di daftar.
   Tidak boleh ada yang dilewati dan tidak boleh ada kata tambahan.
3. "alasan" = satu kalimat Bahasa Indonesia sehari-hari yang mudah dipahami (pakai tanda kutip “ ” untuk arti).
   - Untuk "bukan": sebut arti kata, lalu mengapa karakter itu bukan imbuhan.
   - Untuk "imbuhan": jelaskan singkat bagaimana karakter itu berfungsi seperti definisi.
   - Untuk "ragu": jelaskan letak keraguannya.
4. Keluarkan HANYA satu blok JSON (sebuah array), tanpa teks pembuka atau penutup.

CONTOH GAYA "alasan"
- 发生 berarti “terjadi”; 生 menjadi bagian kata kerja, bukan penanda orang.
- 花生 berarti “kacang tanah”; 生 menjadi bagian nama benda, bukan penanda orang.
- 学生 berarti “siswa”; 生 menunjukkan orang dengan status pelajar.

FORMAT KELUARAN
[
  {"afiks": "生", "kata": "发生", "golongan": "bukan", "alasan": "发生 berarti “terjadi”; 生 menjadi bagian kata kerja, bukan penanda orang."}
]
"golongan" hanya boleh salah satu dari: "imbuhan", "bukan", "ragu".
"""


def hsk_kunci(w):
    try:
        return int(w.get("hsk"))
    except (TypeError, ValueError):
        return 99


def baca(path):
    return json.loads(path.read_text(encoding="utf-8"))


def susun_kandidat(afiks, kata):
    """Kembalikan daftar (entri_imbuhan, kandidat_terurut). Urutan tetap: HSK, lalu urutan di kamus."""
    hasil = []
    for e in afiks:
        ch, pos = e["karakter"], e["posisi"]
        dikenal = {c["kata"] for b in e["bagian"] for c in b["contoh"]} | {k["kata"] for k in e.get("bukan", [])}
        cand = []
        for i, w in enumerate(kata):
            s = w["simplified"]
            if len(s) < 2 or s == ch or s in dikenal:
                continue
            if (s.endswith(ch) if pos == "akhiran" else s.startswith(ch)):
                cand.append((hsk_kunci(w), i, w))
        cand.sort(key=lambda t: (t[0], t[1]))
        hasil.append((e, [w for _, _, w in cand]))
    return hasil


def bersihkan_arti(t):
    """Buang sisa format kamus sumber: 'KP:...' dan pinyin angka dalam [ ] (mis. 出差[chu1 chai1])."""
    t = re.sub(r"\s*KP:.*$", "", t)
    t = re.sub(r"\[[^\]]*\]", "", t)
    t = re.sub(r"\s+", " ", t).strip(" ;,")
    return t if len(t) <= 80 else t[:77].rstrip() + "..."


def arti(w):
    m = [bersihkan_arti(x) for x in (w.get("meanings_id") or [])]
    m = [x for x in m if x]
    return "; ".join(m[:2]) if m else "?"


def pilih_tahap(semua, tahap):
    dipilih = []
    for e, cand in semua:
        sel = cand[:BATAS_TAHAP1] if tahap == 1 else cand[BATAS_TAHAP1:]
        if sel:
            dipilih.append((e, sel))
    return dipilih


def pilih_kontrol(e, kata_idx):
    """Satu contoh sah dan satu 'bukan' yang sudah dikenal (bila ada), sebagai soal kontrol."""
    ctr = []
    contoh = [c["kata"] for b in e["bagian"] for c in b["contoh"]]
    if contoh:
        ctr.append((contoh[-1], "imbuhan"))
    if e.get("bukan"):
        ctr.append((e["bukan"][0]["kata"], "bukan"))
    return [(k, g) for k, g in ctr if k in kata_idx]


def bagi_berkas(dipilih):
    berkas, cur, n = [], [], 0
    for item in dipilih:
        e, sel = item
        ukuran = len(sel) + 2
        if cur and (n + ukuran > MAKS_PER_BERKAS or len(cur) >= MAKS_IMBUHAN_PER_BERKAS):
            berkas.append(cur)
            cur, n = [], 0
        cur.append(item)
        n += ukuran
    if cur:
        berkas.append(cur)
    return berkas


def tulis_berkas(nomor, isi_berkas, kata_idx, rng):
    baris = [PROMPT, "", "=" * 60, "DAFTAR YANG HARUS DINILAI (berkas %02d)" % nomor, "=" * 60, ""]
    manifest, no = [], 0
    for e, sel in isi_berkas:
        ctr = pilih_kontrol(e, kata_idx)
        ctr_kata = {k for k, _ in ctr}
        baris.append("-" * 60)
        baris.append("IMBUHAN: %s (%s)  — kelompok %s: %s" % (e["karakter"], e["posisi"], e["kelompok"], e["kelompok_nama"]))
        for b in e["bagian"]:
            baris.append("Fungsi yang dinilai (sebagai %s): %s" % (b["sebagai"], b["fungsi"]))
            baris.append("Arti: %s" % b["arti"])
        sah = [c["kata"] for b in e["bagian"] for c in b["contoh"] if c["kata"] not in ctr_kata]
        baris.append("Contoh yang SAH imbuhan ini (sudah diketahui): %s" % ", ".join(sah))
        bk = [k for k in e.get("bukan", []) if k["kata"] not in ctr_kata]
        if bk:
            baris.append("Contoh yang BUKAN imbuhan ini (sudah diketahui):")
            for k in bk:
                baris.append("   %s — %s" % (k["kata"], k["alasan"]))
        if e.get("catatan"):
            baris.append("Catatan: %s" % e["catatan"])
        baris.append("Kata yang harus dinilai untuk %s:" % e["karakter"])
        entri = [(w["simplified"], w, None) for w in sel] + [(k, kata_idx[k], g) for k, g in ctr]
        rng.shuffle(entri)
        for s, w, benar in entri:
            no += 1
            baris.append("%d. %s | %s | %s" % (no, s, w.get("pinyin", ""), arti(w)))
            manifest.append({"nomor": no, "afiks": e["karakter"], "kata": s, "kontrol": benar is not None, "golongan_benar": benar})
        baris.append("")
    baris.append("Ingat: keluarkan HANYA satu blok JSON (array) berisi %d entri, urut nomor 1 sampai %d." % (no, no))
    return "\r\n".join(baris) + "\r\n", manifest


CATATAN = """# Catatan lanjutan -- kandidat "bukan" imbuhan

Dibuat otomatis oleh buat_kandidat_imbuhan.py (23 November 2026).

## Keadaan
- Tahap 1 = 735 kata kandidat (20 pertama per imbuhan, diutamakan HSK rendah) + kata kontrol.
- Tahap 2 = SISA 433 kandidat. **DITUNDA sampai ada waktu yang tepat** (keputusan رسلان, supaya tidak hilang).
  Jalankan nanti:  python buat_kandidat_imbuhan.py --tahap 2   (lalu  --apply)
  Pembagian tetap, jadi tahap 2 tidak mengulang tahap 1 selama data tidak berubah. Bila afiks_kamus.json
  atau app_words.json sudah berubah, jalankan lihat-dulu dan bandingkan jumlahnya.

## Cara kerja
1. Tempel satu berkas batch_NN.txt ke AI (GPT) per percakapan baru. Simpan jawabannya (satu blok JSON)
   sebagai batch_NN_hasil.json.
2. Tempel hasilnya ke Claude untuk dikurasi. Hanya golongan "bukan" yang diambil; "imbuhan" dan "ragu"
   dipakai untuk memeriksa ketelitian AI (lewat kata kontrol di _manifest_tahapN.json).
3. Setelah kurasi, skrip pemasang menambahkan hasil "bukan" yang disetujui ke data\\afiks_kamus.json.
"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tahap", type=int, choices=(1, 2), default=1)
    ap.add_argument("--apply", action="store_true", help="tulis berkas kerja (tanpa ini hanya melihat ringkasan)")
    ap.add_argument("--timpa", action="store_true", help="boleh menimpa folder tahap yang sudah ada")
    a = ap.parse_args()

    afiks, kata = baca(AFIKS), baca(KATA)
    kata_idx = {}
    for w in kata:
        kata_idx.setdefault(w["simplified"], w)
    semua = susun_kandidat(afiks, kata)
    dipilih = pilih_tahap(semua, a.tahap)
    berkas = bagi_berkas(dipilih)
    jumlah = sum(len(s) for _, s in dipilih)
    total_semua = sum(len(c) for _, c in semua)
    print("=== Kandidat 'bukan' imbuhan -- tahap %d ===" % a.tahap)
    print("Semua kandidat di kamus (60 imbuhan): %d" % total_semua)
    print("Dipilih untuk tahap %d: %d kata dari %d imbuhan -> %d berkas kerja" % (a.tahap, jumlah, len(dipilih), len(berkas)))
    for i, isi in enumerate(berkas, 1):
        print("   batch_%02d: %-30s %d kata (+kontrol)" % (i, " ".join(e["karakter"] for e, _ in isi), sum(len(s) for _, s in isi)))
    folder = KELUAR / ("tahap%d" % a.tahap)
    if not a.apply:
        print("\nIni baru ringkasan; belum ada yang ditulis. Untuk menulis: python buat_kandidat_imbuhan.py%s --apply"
              % (" --tahap 2" if a.tahap == 2 else ""))
        return 0
    if folder.exists() and any(folder.iterdir()) and not a.timpa:
        print("\nBERHENTI: folder %s sudah ada isinya. Tambahkan --timpa bila memang ingin membuat ulang." % folder)
        return 1
    folder.mkdir(parents=True, exist_ok=True)
    rng = random.Random(BIBIT + a.tahap)
    manifest = {"tahap": a.tahap, "berkas": {}}
    for i, isi in enumerate(berkas, 1):
        teks, man = tulis_berkas(i, isi, kata_idx, rng)
        (folder / ("batch_%02d.txt" % i)).write_bytes(teks.encode("utf-8"))
        manifest["berkas"]["batch_%02d" % i] = man
    (folder / ("_manifest_tahap%d.json" % a.tahap)).write_text(json.dumps(manifest, ensure_ascii=False, indent=1), encoding="utf-8")
    (KELUAR / "CATATAN_LANJUTAN.md").write_text(CATATAN, encoding="utf-8")
    print("\nSelesai: %d berkas kerja di %s" % (len(berkas), folder))
    print("Berkas yang perlu diunggah ke GitHub: buat_kandidat_imbuhan.py, kerja_gpt_afiks/kandidat/CATATAN_LANJUTAN.md,")
    print("   kerja_gpt_afiks/kandidat/tahap%d/_manifest_tahap%d.json (dan batch_NN.txt bila ingin disimpan di repo)." % (a.tahap, a.tahap))
    return 0


if __name__ == "__main__":
    sys.exit(main())

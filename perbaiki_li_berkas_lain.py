#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
perbaiki_li_berkas_lain.py -- penyeragaman 里 (nada netral) di berkas data LAIN
================================================================================
Poin 1 rencana BLUEPRINT_v46, TAHAP KEDUA. Tahap pertama (perbaiki_li_netral.py) sudah
mengerjakan data\\nuance_pairs.json dan data\\app_words.json. Skrip ini mengerjakan berkas lain yang
punya pasangan hanzi + pinyin dengan 里, memakai aturan yang sama (pilihan B):

  - 里 akhiran tempat setelah kata benda -> netral "li"  (家里 jiā li, 教室里 jiàoshì li, 心里 xīn li)
  - pola A里AB (糊里糊涂 húlihútu, 啰里啰嗦, 慌里慌张, 古里古怪)  -> netral "li"
  - TETAP nada penuh "lǐ": 这里 那里 哪里; 里面 里头 里边; 里 arah (往里走, 向里, 朝里);
    kata serapan (沙特里亚尔, 尤克里里); satuan dan 卡路里 (公里 万里 卡路里); 里 di awal frasa.

BERKAS YANG DIUBAH (14):
    data\\graded_readers.json  data\\grammar_afiks.json  data\\grammar_hsk1/3/5/6/8/9.json
    data\\pattern_explanations.json  data\\pelajaran\\pilar_4/6/9/10.json  data\\produktif_karakter.json
TIDAK diubah (hanya dilaporkan):
    data\\tone_drills.json  -- dibuat oleh skrip\\dari_py\\generate_tone_drills.py; dibereskan lewat regenerasi
    data\\wb_pools.json     -- dikurasi manual; semua 里 di sana sudah benar

Yang berubah HANYA tanda nada pada "li" di isian pinyin (huruf tetap), dan hanya pada pasangan hanzi+pinyin
yang bisa disejajarkan. Pasangan yang tidak bisa disejajarkan dilewati dan dilaporkan.

Berkas pendukung yang HARUS ada di folder yang sama: daftar_nada_nuance.py

CARA PAKAI (dari C:\\mandarin_app>):
  1) Lihat dulu (TIDAK mengubah apa pun):   python perbaiki_li_berkas_lain.py
  2) Terapkan:                              python perbaiki_li_berkas_lain.py --apply

KEAMANAN
  - Tiap berkas diubah dengan mengganti teks isian pinyin yang sama persis (format, spasi, akhir baris, dan
    urutan berkas TIDAK disentuh). Skrip berhenti bila jumlah isian yang ditemukan tidak sama dengan rencana.
  - Cadangan per berkas yang diubah: <nama>.bak_li2_<tanggal-jam>  (di folder yang sama dengan berkasnya).
  - Setelah menulis, semua berkas dibaca ulang dan dibandingkan dengan yang diharapkan; bila ada yang tidak
    cocok, SEMUA berkas yang diubah dikembalikan dari cadangan.
  - Aman diulang: yang sudah benar dilewati.
  - Daftar lengkap perubahan ditulis ke hasil_li_berkas_lain.txt.
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

DATA = ROOT / "data"
HASIL = ROOT / "hasil_li_berkas_lain.txt"
BERKAS = [
    "graded_readers.json", "grammar_afiks.json", "grammar_hsk1.json", "grammar_hsk3.json",
    "grammar_hsk5.json", "grammar_hsk6.json", "grammar_hsk8.json", "grammar_hsk9.json",
    "pattern_explanations.json", "pelajaran/pilar_4.json", "pelajaran/pilar_6.json",
    "pelajaran/pilar_9.json", "pelajaran/pilar_10.json", "produktif_karakter.json",
]
HANYA_LAPOR = ["tone_drills.json", "wb_pools.json"]
# pasangan (isian hanzi, isian pinyin) yang dikenali
PASANGAN = [("cn", "py"), ("contoh", "pinyin"), ("hanzi", "pinyin"), ("kata", "pinyin"), ("word", "pinyin"),
            ("salah", "salah_py"), ("benar", "benar_py")]

# ---------------------------------------------------------------- aturan 里
SESUDAH_PENUNJUK = set("这那哪")           # 这里 那里 哪里 -> lǐ
SESUDAH_ARAH = set("面头边")               # 里面 里头 里边 -> lǐ
SEBELUM_ARAH = set("往向朝")               # 往里 向里 朝里 (里 = arah "ke dalam") -> lǐ
SATUAN = set("公英海千万百十路")           # 公里 英里 海里 千里 万里 卡路里 -> lǐ
KATA_SERAPAN = ["沙特里亚尔", "尤克里里"]  # -> lǐ
HANZI = re.compile(r"[\u4e00-\u9fff]")


def klasifikasi(cn, i):
    """Kembalikan (jenis, target) untuk 里 pada posisi i di kalimat cn; target 'penuh' (lǐ) atau 'netral' (li)."""
    for kata in KATA_SERAPAN:
        for m in re.finditer(re.escape(kata), cn):
            if m.start() <= i < m.end():
                return "kata serapan", "penuh"
    prev = cn[i - 1] if i > 0 else ""
    nxt = cn[i + 1] if i + 1 < len(cn) else ""
    if prev in SESUDAH_PENUNJUK:
        return "这里/那里/哪里", "penuh"
    if nxt in SESUDAH_ARAH:
        return "里面/里头/里边", "penuh"
    if prev in SEBELUM_ARAH:
        return "里 arah (往里)", "penuh"
    if not prev or not HANZI.match(prev):
        return "里 di awal kalimat atau frasa", "penuh"
    if prev in SATUAN:
        return "satuan jarak / 卡路里", "penuh"
    if nxt == prev:
        return "pola A里AB (糊里糊涂)", "netral"
    return "akhiran tempat setelah kata benda", "netral"


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
    diubah = daftar (indeks_huruf_l, lama, baru, jenis, target); tetap = daftar (jenis, target, lama)"""
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
        jenis, target = klasifikasi(cn, posisi_hanzi[k])
        if lama.lower() not in ("li", "lǐ"):
            return None, None, "bacaan 里 tak terduga: %s" % lama
        baru = ("L" if lama[0].isupper() else "l") + ("ǐ" if target == "penuh" else "i")
        if baru == lama:
            tetap.append((jenis, target, lama))
        else:
            diubah.append((idx[awal], lama, baru, jenis, target))
    return diubah, tetap, None


def baca(path):
    mentah = path.read_bytes().decode("utf-8")
    return mentah, json.loads(mentah.lstrip("\ufeff"))


TOKEN = re.compile(r'"(?:[^"\\]|\\.)*"')


def susun(data):
    """Telusuri data menurut urutan dokumen. Kembalikan (token, pasangan):
    token    = semua teks (kunci dan nilai teks) berurutan, seperti urutan di berkas
    pasangan = daftar (obj, kunci_hanzi, kunci_pinyin, indeks_token_pinyin) untuk hanzi yang memuat 里"""
    token, pasangan = [], []

    def jalan(o):
        if isinstance(o, dict):
            idx = {}
            for k, v in o.items():
                token.append(k)
                if isinstance(v, str):
                    idx[k] = len(token)
                    token.append(v)
                else:
                    jalan(v)
            for a, b in PASANGAN:
                if a in o and b in o and isinstance(o[a], str) and isinstance(o[b], str) and "里" in o[a]:
                    pasangan.append((o, a, b, idx[b]))
        elif isinstance(o, list):
            for v in o:
                if isinstance(v, str):
                    token.append(v)
                else:
                    jalan(v)
    jalan(data)
    return token, pasangan


def analisis(nama, app_idx, cc_idx):
    path = DATA / nama
    mentah, data = baca(path)
    token, pasangan = susun(data)
    rencana, dilewati = [], []
    for obj, a, b, ti in pasangan:
        cn, py = obj[a], obj[b]
        diubah, tetap, galat = usul_li(cn, py, app_idx, cc_idx)
        if galat:
            dilewati.append((cn, py, galat))
            continue
        if not diubah:
            continue
        teks = list(py)
        for il, lama, baru, jenis, target in diubah:
            teks[il], teks[il + 1] = baru[0], baru[1]
        rencana.append((cn, py, "".join(teks), [d[3] for d in diubah], ti))
    return path, mentah, data, token, rencana, dilewati


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser(description="Seragamkan 里 netral di berkas data lain (tahap kedua)")
    ap.add_argument("--apply", action="store_true", help="benar-benar menulis (tanpa ini hanya menampilkan ringkasan)")
    a = ap.parse_args()
    print("Mode: %s\n" % ("TERAPKAN (--apply)" if a.apply else "LIHAT-DULU (tidak mengubah apa pun)"))

    for nama in BERKAS + HANYA_LAPOR:
        if not (DATA / nama).exists():
            print("Tidak menemukan %s. Letakkan skrip ini di folder utama proyek (mis. C:\\mandarin_app)." % (DATA / nama))
            return 1
    _, app_idx, cc_idx = dn.muat()

    semua = []      # (nama, path, mentah, data, token, rencana)
    baris = []
    total_ubah = 0
    print("%-34s %8s %10s" % ("Berkas", "diubah", "dilewati"))
    for nama in BERKAS:
        path, mentah, data, token, rencana, dilewati = analisis(nama, app_idx, cc_idx)
        n = sum(len(r[3]) for r in rencana)
        total_ubah += n
        print("%-34s %8d %10d" % ("data\\" + nama.replace("/", "\\"), n, len(dilewati)))
        semua.append((nama, path, mentah, data, token, rencana))
        if rencana or dilewati:
            baris.append("## data\\" + nama.replace("/", "\\"))
            for cn, lama, baru, jenis, ti in rencana:
                baris += ["   %s | %s" % (cn, ", ".join(sorted(set(jenis)))), "      lama: %s" % lama, "      baru: %s" % baru]
            for cn, py, galat in dilewati:
                baris.append("   DILEWATI: %s | %s | %s" % (cn, py, galat))
    print("%-34s %8d" % ("JUMLAH kemunculan 里 diubah", total_ubah))

    ringkas = {}
    for nama, path, mentah, data, token, rencana in semua:
        for cn, lama, baru, jenis, ti in rencana:
            for j in jenis:
                ringkas[j] = ringkas.get(j, 0) + 1
    print("\nRincian yang akan diubah, per jenis 里:")
    for j, n in sorted(ringkas.items(), key=lambda x: -x[1]):
        print("   %-40s %d" % (j, n))

    print("\nHanya dilaporkan (TIDAK diubah):")
    baris.append("")
    baris.append("## HANYA DILAPORKAN (tidak diubah)")
    for nama in HANYA_LAPOR:
        _, _, _, _, rencana, dilewati = analisis(nama, app_idx, cc_idx)
        n = sum(len(r[3]) for r in rencana)
        print("   data\\%-20s %d butir yang kelak berubah bila dibuat ulang (%s)" % (
            nama, n, "regenerasi generate_tone_drills.py" if nama == "tone_drills.json" else "dikurasi manual"))
        for cn, lama, baru, jenis, ti in rencana:
            baris.append("   %s | %s | %s -> %s" % (nama, cn, lama, baru))

    # ---- rencana ganti teks per berkas: posisi tepat tiap isian pinyin di berkas
    ada_galat = False
    ganti = {}   # nama -> daftar (awal, akhir, literal_lama, literal_baru)
    for nama, path, mentah, data, token, rencana in semua:
        if not rencana:
            continue
        span = [(m.start(), m.end(), m.group(0)) for m in TOKEN.finditer(mentah)]
        try:
            sama = len(span) == len(token) and all(json.loads(s[2]) == tk for s, tk in zip(span, token))
        except Exception:
            sama = False
        if not sama:
            print("BERHENTI: %s: urutan teks di berkas tidak sejajar dengan hasil bacaan JSON." % nama)
            ada_galat = True
            continue
        daftar = []
        for cn, lama, baru, jenis, ti in rencana:
            awal, akhir_i, lit = span[ti]
            if lit != json.dumps(lama, ensure_ascii=False):
                print("BERHENTI: %s: isian untuk %s tertulis %s, bukan seperti yang diharapkan." % (nama, cn, lit))
                ada_galat = True
                continue
            daftar.append((awal, akhir_i, lit, json.dumps(baru, ensure_ascii=False)))
        ganti[nama] = daftar
    if ada_galat:
        print("Tidak ada yang diubah. Kirim pesan ini ke Claude.")
        return 1

    if not ganti:
        print("\nTidak ada yang perlu diubah.")
        return 0
    if not a.apply:
        HASIL.write_text("\r\n".join(baris) + "\r\n", encoding="utf-8-sig")
        print("\nIni baru ringkasan; belum ada yang diubah. Daftar lengkap: %s" % HASIL.name)
        print("Untuk menerapkan: python perbaiki_li_berkas_lain.py --apply")
        return 0

    # ---- terapkan
    cap = datetime.now().strftime("%Y%m%d_%H%M%S")
    cadangan = {}
    ok = True
    try:
        for nama, path, mentah, data, token, rencana in semua:
            if nama not in ganti:
                continue
            cad = path.with_name(path.name + ".bak_li2_" + cap)
            shutil.copy2(path, cad)
            cadangan[nama] = (path, cad)
            baru_teks = mentah
            for awal, akhir_i, lit, lit_baru in sorted(ganti[nama], reverse=True):
                baru_teks = baru_teks[:awal] + lit_baru + baru_teks[akhir_i:]
            path.write_bytes(baru_teks.encode("utf-8"))
        # pemeriksaan akhir: data hasil baca ulang harus sama dengan data lama + hanya isian pinyin yang direncanakan
        for nama, path, mentah, data, token, rencana in semua:
            if nama not in ganti:
                continue
            harapan = copy.deepcopy(data)
            _, pasangan = susun(harapan)
            peta = {ti: baru for cn, lama, baru, jenis, ti in rencana}
            for obj, a, b, ti in pasangan:
                if ti in peta:
                    obj[b] = peta[ti]
            _, ulang = baca(path)
            if ulang != harapan:
                ok = False
                print("Tidak cocok setelah menulis: %s" % nama)
    except Exception as e:
        ok = False
        print("Galat saat menulis: %s" % e)
    if not ok:
        for nama, (path, cad) in cadangan.items():
            shutil.copy2(cad, path)
        print("\nPEMERIKSAAN AKHIR GAGAL: semua berkas dikembalikan dari cadangan. Kirim pesan ini ke Claude.")
        return 1
    HASIL.write_text("\r\n".join(baris) + "\r\n", encoding="utf-8-sig")
    print("\nSelesai: %d kemunculan 里 diperbaiki di %d berkas." % (total_ubah, len(cadangan)))
    print("Cadangan: <nama berkas>.bak_li2_%s (di folder yang sama dengan berkasnya)" % cap)
    print("Pemeriksaan akhir lolos (hanya isian pinyin yang direncanakan berubah).")
    print("Daftar lengkap perubahan: %s" % HASIL.name)
    return 0


if __name__ == "__main__":
    sys.exit(main())

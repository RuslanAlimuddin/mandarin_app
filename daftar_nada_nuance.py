#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
daftar_nada_nuance.py -- LIHAT-DULU: usulan tanda nada untuk contoh pinyin tanpa nada
=====================================================================================
Skrip ini HANYA MEMBACA. Ia TIDAK mengubah data\\nuance_pairs.json atau berkas data mana pun.
Ia hanya menulis dua berkas laporan di folder tempat skrip ini berada:

   laporan_nada_nuance.txt   -- ringkasan angka + daftar yang perlu kamu lihat (dibaca manusia)
   usulan_nada_nuance.json   -- usulan lengkap per contoh (bahan untuk skrip --apply nanti)

CARA PAKAI (dari C:\\mandarin_app>):
       python daftar_nada_nuance.py

APA YANG DILAKUKAN
  Untuk tiap contoh kalimat yang pinyin-nya TANPA tanda nada, skrip memecah kalimat hanzi
  menjadi kata (kata terpanjang dulu), lalu mengambil bacaan tiap kata:
     1) dari data\\app_words.json (bacaan terkurasi) -- dipakai bila hanya ada satu bacaan,
     2) bila kata tidak ada di sana, dari data\\cidict_index.json.gz (CC-CEDICT) -- dipakai
        hanya bila bacaannya tunggal.
  Pinyin tanpa nada yang sudah ada TIDAK diganti hurufnya: skrip hanya memasang tanda nada ke
  huruf yang sudah ada (pengelompokan kata, huruf kapital, tanda baca tetap). Bila huruf
  usulan tidak cocok dengan huruf yang ada, contoh itu masuk golongan "tidak bisa disejajarkan".

  Aturan penulisan (sudah disepakati):
     - Nada 3-3 ditulis nada aslinya seperti kamus (nǐ hǎo, bukan ní hǎo).
     - 不 tetap bù (seperti semua contoh bernada yang sudah ada).
     - 一 mengikuti perubahan nada sebenarnya: yī (sendiri/angka/urutan: 第一, 一月, 十一),
       yí sebelum nada 4 (termasuk 个 yang netral: yí ge), yì sebelum nada 1, 2, 3.
     - ü ditulis ü bertanda nada (lǚ, nǚ, lǜ) -- tulisan "nv/lu" tanpa nada ikut terganti.
     - Nada netral tanpa tanda (zhège, péngyou), mengikuti bacaan di app_words.json.

  GOLONGAN HASIL
     A  PASTI     : tiap suku kata berasal dari satu bacaan terkurasi; tidak ada karakter berisiko.
     B1 USULAN YAKIN  : karakter berisiko yang diselesaikan aturan sederhana (了=le bukan sesudah 不/得;
                    好=hǎo bukan sebelum 学客奇动胜色; 都=dōu; 会=huì) -- tinggal disetujui.
     B2 PERLU DILIHAT : ada karakter berbacaan ganda yang bergantung konteks (了 好 行 都 重 为
                    地 间 发 种 教 应 会 当 只 长 得 还 着 没 假 数 少 觉 乐 便 相 调 传 倒 扇 载
                    涨 别 差 降 干 空 难 处 模 背 将 弹 单 号 片 率 度 量 参 切 称 角 结 夹 省 属 宿 朝 吓 薄) atau kata
                    yang punya lebih dari satu bacaan di data. Usulan tetap diberikan, ditandai.
     C  TIDAK BISA DISEJAJARKAN : hanzi tak bisa dipecah atau huruf usulan tak cocok.
"""
import collections
import gzip
import json
import re
import sys
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
NUANCE = DATA / "nuance_pairs.json"
APP = DATA / "app_words.json"
CIDICT = DATA / "cidict_index.json.gz"
LAPORAN = ROOT / "laporan_nada_nuance.txt"
USULAN = ROOT / "usulan_nada_nuance.json"

TONE_MARKS = "āáǎàēéěèīíǐìōóǒòūúǔùǖǘǚǜ"
HANZI = re.compile(r"[\u4e00-\u9fff]")

# karakter yang bacaannya bergantung konteks -> selalu golongan B bila dipakai sebagai karakter tunggal
RISIKO = set("了好行都重为地间发种教应会当只长得还着没假数少觉乐便相调传倒扇载涨别差降干空难处模背将弹单号片率度量参切称角结夹省属宿朝吓薄")

NADA_DARI_TANDA = {}
for baris, nada in zip(["āēīōūǖ", "áéíóúǘ", "ǎěǐǒǔǚ", "àèìòùǜ"], [1, 2, 3, 4]):
    for ch in baris:
        NADA_DARI_TANDA[ch] = nada

# 一 sandhi: nada asli 1 -> yí / yì
YI_VARIAN = {"yī": "yī", "yí": "yí", "yì": "yì"}


def tanpa_nada(s):
    s = unicodedata.normalize("NFD", s)
    s = "".join(ch for ch in s if unicodedata.category(ch) != "Mn")
    return s.lower().replace("ü", "u").replace("v", "u").replace("'", "")


def tanpa_nada_tanda(s):
    """Bentuk pembanding yang tetap memuat nada (huruf bertanda dipertahankan)."""
    return unicodedata.normalize("NFC", s.lower().replace("'", ""))


def nada_suku(syl):
    """Nada dasar sebuah suku kata bertanda (1-4), atau 5 bila netral/tanpa tanda."""
    for ch in syl:
        if ch in NADA_DARI_TANDA:
            return NADA_DARI_TANDA[ch]
    return 5


SUKU_DASAR = set()  # semua suku kata tanpa nada yang dikenal (diisi dari CC-CEDICT di muat())


def _pisah_sambung(t, k):
    """Pecah string t (tanpa spasi) menjadi tepat k suku kata yang sah; None bila tak bisa."""
    def rek(pos, sisa):
        if sisa == 0:
            return [] if pos == len(t) else None
        for L in range(min(6, len(t) - pos), 0, -1):
            potong = t[pos:pos + L]
            if tanpa_nada(potong) in SUKU_DASAR:
                r = rek(pos + L, sisa - 1)
                if r is not None:
                    return [potong] + r
        return None
    return rek(0, k)


def pecah_suku(pinyin, k=None):
    bagian = [x for x in re.split(r"[\s']+", pinyin.strip()) if x]
    if k is None or len(bagian) == k:
        return bagian
    sambung = unicodedata.normalize("NFC", "".join(bagian))
    r = _pisah_sambung(sambung, k)
    return r if r is not None else bagian


def muat():
    nuance = json.load(open(NUANCE, encoding="utf-8"))
    app = json.load(open(APP, encoding="utf-8"))
    cc = json.load(gzip.open(CIDICT, "rt", encoding="utf-8"))
    app_idx = collections.defaultdict(list)
    cc_idx = collections.defaultdict(list)
    for e in app:
        p = e.get("pinyin", "").strip()
        if p and p not in app_idx[e["simplified"]]:
            app_idx[e["simplified"]].append(p)
    for e in cc:
        p = e.get("pinyin", "").strip()
        if p and p not in cc_idx[e["simplified"]]:
            cc_idx[e["simplified"]].append(p)
    for e in cc:
        for sy in re.split(r"[\s']+", e.get("pinyin", "").strip()):
            if sy:
                SUKU_DASAR.add(tanpa_nada(sy))
    SUKU_DASAR.add("r")
    return nuance, app_idx, cc_idx


def _biaya_potongan(seg, app_idx, cc_idx, larang, longgar, ada_nama):
    """Biaya memakai potongan seg sebagai satu kata; None bila tidak boleh dipakai."""
    if len(seg) > 1 and seg in larang:
        return None
    bacaan = app_idx.get(seg) or cc_idx.get(seg) or []
    nama = len(seg) > 1 and any(r[:1].isupper() for r in bacaan)
    if seg in app_idx:
        return (0.8 if (nama and ada_nama) else 1.0), "app"
    if seg in cc_idx:
        if len(seg) > 1:
            # kata multi-karakter yang hanya ada di CC-CEDICT dan memuat karakter berisiko/的
            # sering salah potong (到了, 美的, 中的): jangan dipakai, kecuali pada percobaan 'longgar'
            if not longgar and any(ch in RISIKO or ch == "的" for ch in seg):
                return None
            return (0.8 if (nama and ada_nama) else 1.3), "cc"
        return 1.2, "cc"
    if len(seg) == 1:
        return 5.0, "tak_ada"
    return None


def _dp_run(run, app_idx, cc_idx, larang, longgar, ada_nama):
    n = len(run)
    terbaik = [None] * (n + 1)  # (biaya, awal, sumber)
    terbaik[0] = (0.0, -1, "")
    for j in range(1, n + 1):
        for L in range(1, min(6, j) + 1):
            i = j - L
            if terbaik[i] is None:
                continue
            seg = run[i:j]
            bs = _biaya_potongan(seg, app_idx, cc_idx, larang, longgar, ada_nama)
            if bs is None:
                continue
            total = terbaik[i][0] + bs[0]
            if terbaik[j] is None or total < terbaik[j][0] - 1e-9:
                terbaik[j] = (total, i, bs[1])
    potongan = []
    j = n
    while j > 0:
        _, i, sumber = terbaik[j]
        potongan.append((run[i:j], sumber))
        j = i
    potongan.reverse()
    return potongan


def segmentasi(kalimat, app_idx, cc_idx, larang=frozenset(), longgar=False, ada_nama=False):
    """Pecah kalimat jadi daftar (potongan, bacaan_utama, kandidat, sumber). Hanzi saja.
    kandidat = semua bacaan (terkurasi dulu, lalu CC-CEDICT) untuk dicoba bila jumlah suku kata tak cocok."""
    hasil = []
    i, n = 0, len(kalimat)
    while i < n:
        if not HANZI.match(kalimat[i]):
            i += 1
            continue
        j = i
        while j < n and HANZI.match(kalimat[j]):
            j += 1
        for seg, sumber in _dp_run(kalimat[i:j], app_idx, cc_idx, larang, longgar, ada_nama):
            if sumber == "app":
                kandidat = list(app_idx[seg]) + [x for x in cc_idx.get(seg, []) if x not in app_idx[seg]]
                hasil.append((seg, app_idx[seg], kandidat, "app"))
            elif sumber == "cc":
                hasil.append((seg, cc_idx[seg], list(cc_idx[seg]), "cc"))
            else:
                hasil.append((seg, [], [], "tak_ada"))
        i = j
    return hasil


def suku_kata_per_karakter(kalimat, app_idx, cc_idx, larang=frozenset(), longgar=False, ada_nama=False):
    """Kembalikan (daftar_suku_kata_per_karakter, gagal).
    Tiap elemen: dict(hz, syl, seg, risiko, yakin, ambigu)."""
    out = []
    gagal = None
    for seg, bacaan, kandidat, sumber in segmentasi(kalimat, app_idx, cc_idx, larang, longgar, ada_nama):
        if not bacaan:
            gagal = "hanzi tidak ada di kamus: " + seg
            out.extend({"hz": ch, "syl": "?", "seg": seg, "risiko": True, "yakin": False, "ambigu": False} for ch in seg)
            continue
        ambigu = len(bacaan) > 1
        sylls = None
        for kand in kandidat:
            cobaan = pecah_suku(kand, len(seg))
            if len(cobaan) == len(seg):
                sylls = cobaan
                break
        if sylls is None:
            gagal = "jumlah suku kata %s tidak sama dengan jumlah hanzi (%s)" % (bacaan[0], seg)
            out.extend({"hz": ch, "syl": "?", "seg": seg, "risiko": True, "yakin": False, "ambigu": False} for ch in seg)
            continue
        for ch, sy in zip(seg, sylls):
            risiko = (len(seg) == 1 and ch in RISIKO)
            if len(seg) > 1 and ch in RISIKO:
                # kata terkurasi yang bacaan karakternya beda dari bacaan tunggalnya (都会 dū huì vs 都 dōu + 会 huì)
                tunggal = app_idx.get(ch) or cc_idx.get(ch) or []
                if tunggal and tanpa_nada_tanda(sy) != tanpa_nada_tanda(tunggal[0]):
                    risiko = True
            out.append({"hz": ch, "syl": sy, "seg": seg, "risiko": risiko, "yakin": False, "ambigu": ambigu})
    nilai_yakin(out)
    return out, gagal


def nilai_yakin(items):
    """Tandai karakter berisiko yang usulannya 'yakin' menurut aturan sederhana (golongan B1).
       了 = le bila bukan sesudah 不/得;  好 = hǎo bila tidak sebelum 学客奇动胜色;
       都 = dōu dan 会 = huì bila berdiri sebagai kata sendiri."""
    n = len(items)
    for i, it in enumerate(items):
        if not it["risiko"] or len(it["seg"]) != 1:
            continue
        sebelum = items[i - 1]["hz"] if i > 0 else ""
        sesudah = items[i + 1]["hz"] if i + 1 < n else ""
        sy = it["syl"]
        if it["hz"] == "了" and sy == "le" and sebelum not in ("不", "得"):
            it["yakin"] = True
        elif it["hz"] == "好" and sy == "hǎo" and sesudah not in tuple("学客奇动胜色"):
            it["yakin"] = True
        elif it["hz"] == "都" and sy == "dōu":
            it["yakin"] = True
        elif it["hz"] == "会" and sy == "huì":
            it["yakin"] = True


def terapkan_yi(items):
    """Terapkan perubahan nada 一 sesuai aturan yang disepakati. Ubah items di tempat."""
    n = len(items)
    for i, it in enumerate(items):
        if it["hz"] != "一":
            continue
        sebelum = items[i - 1]["hz"] if i > 0 else ""
        sesudah = items[i + 1] if i + 1 < n else None
        # yī tetap: angka/urutan/akhir/dikutip
        if sebelum and (sebelum in "十二三四五六七八九零第〇百千万"):
            it["syl"] = "yī"
            continue
        if sesudah is None:
            it["syl"] = "yī"
            continue
        if sesudah["hz"] in "月号日":
            it["syl"] = "yī"
            continue
        if sesudah["hz"] in "一二三四五六七八九十":
            it["syl"] = "yī"
            continue
        # nada suku sesudahnya (nada dasar bila tak bertanda: lihat karakter aslinya)
        nada = nada_suku(sesudah["syl"])
        if nada == 5:
            if sesudah["hz"] == "个":
                nada = 4
            else:
                it["syl"] = "yī"
                it["risiko"] = True  # tak bisa dipastikan: lihat manual
                it["catatan"] = "一 sebelum suku kata netral"
                continue
        it["syl"] = "yí" if nada == 4 else "yì"


def pasang_ke_huruf(pinyin_lama, items):
    """Pasang suku kata bertanda ke susunan huruf pinyin lama (apostrof, huruf kapital, tanda baca
    dipertahankan). Kembalikan (pinyin_baru, galat)."""
    tokens = re.findall(r"[A-Za-züÜ']+|[^A-Za-züÜ']+", pinyin_lama)
    pos = 0
    keluar = []
    for tok in tokens:
        if not re.match(r"[A-Za-züÜ']+", tok):
            keluar.append(tok)
            continue
        # posisi apostrof di token lama, dihitung dalam jumlah huruf sebelumnya
        apos = set()
        n_huruf = 0
        for ch in tok:
            if ch == "'":
                apos.add(n_huruf)
            else:
                n_huruf += 1
        target = tanpa_nada(tok)
        buf = ""
        terpakai = []
        while pos < len(items) and len(buf) < len(target):
            sy = items[pos]["syl"]
            buf += tanpa_nada(sy)
            terpakai.append(sy)
            pos += 1
        if buf != target:
            return None, "huruf lama '%s' tidak cocok dengan usulan '%s'" % (tok, "".join(terpakai))
        baru = ""
        n_huruf = 0
        for sy in terpakai:
            if n_huruf in apos and baru:
                baru += "'"
            baru += sy
            n_huruf += len(tanpa_nada(sy))
        if tok[:1].isupper():
            baru = baru[:1].upper() + baru[1:]
        keluar.append(baru)
    if pos != len(items):
        return None, "ada %d suku kata hanzi yang tidak punya huruf pinyin" % (len(items) - pos)
    return "".join(keluar), None


def main():
    nuance, app_idx, cc_idx = muat()
    hasil = []
    for p in nuance["pairs"]:
        for c in p["comparison"]:
            py = c.get("example_pinyin", "")
            if any(ch in py for ch in TONE_MARKS):
                continue
            rec = {
                "id": p["id"], "kata": c["word"], "example_cn": c["example_cn"],
                "pinyin_lama": py, "pinyin_usulan": None, "golongan": "C",
                "karakter_berisiko": [], "catatan": [],
            }
            larang = set()
            longgar = False
            ada_nama = bool(re.search(r"(?<!^)[A-Z]", py)) and bool(re.search(r"[a-z]\s+[A-Z]|[,;:]\s*[A-Z]", py))
            items, baru = None, None
            for _ in range(5):
                items, gagal = suku_kata_per_karakter(c["example_cn"], app_idx, cc_idx,
                                                      frozenset(larang), longgar, ada_nama)
                if gagal:
                    rec["catatan"] = [gagal]
                    break
                terapkan_yi(items)
                baru, galat = pasang_ke_huruf(py, items)
                if galat is None:
                    rec["catatan"] = []
                    break
                rec["catatan"] = [galat]
                tambahan = {it["seg"] for it in items if len(it["seg"]) > 1 and it["risiko"]}
                if tambahan and not tambahan <= larang:
                    larang |= tambahan
                    continue
                if not longgar:
                    longgar = True
                    continue
                break
            if rec["catatan"]:
                hasil.append(rec)
                continue
            rec["pinyin_usulan"] = baru
            risiko = [it for it in items if it["risiko"]]
            ambigu = [it for it in items if it["ambigu"]]
            if risiko or ambigu:
                rec["karakter_berisiko"] = sorted({"%s=%s" % (it["hz"], it["syl"]) for it in risiko})
                semua_yakin = all(it["yakin"] for it in risiko) and not ambigu
                rec["golongan"] = "B1" if semua_yakin else "B2"
                if ambigu:
                    rec["catatan"].append("kata punya >1 bacaan di data: " + "".join(sorted({it["seg"] for it in ambigu})))
                for it in items:
                    if it.get("catatan"):
                        rec["catatan"].append(it["catatan"])
                if larang:
                    rec["catatan"].append("kata dipecah per karakter: " + ",".join(sorted(larang)))
            else:
                rec["golongan"] = "A"
            hasil.append(rec)

    hitung = collections.Counter(r["golongan"] for r in hasil)
    per_karakter = collections.Counter()
    for r in hasil:
        for x in r["karakter_berisiko"]:
            per_karakter[x] += 1

    baris = []
    baris.append("LAPORAN USULAN TANDA NADA -- contoh pinyin tanpa nada di nuance_pairs.json")
    baris.append("(skrip lihat-dulu: tidak ada data yang diubah)")
    baris.append("")
    baris.append("Jumlah contoh tanpa nada: %d" % len(hasil))
    baris.append("  A  Pasti                  : %d" % hitung["A"])
    baris.append("  B1 Usulan yakin (aturan sederhana, tinggal kamu setujui): %d" % hitung["B1"])
    baris.append("  B2 Perlu kamu lihat satu per satu                      : %d" % hitung["B2"])
    baris.append("  C  Tidak bisa disejajarkan: %d" % hitung["C"])
    baris.append("")
    baris.append("Karakter berisiko yang paling sering (usulan bacaan = yang dipilih skrip):")
    for k, v in per_karakter.most_common(40):
        baris.append("  %-10s %d contoh" % (k, v))
    baris.append("")
    baris.append("=" * 70)
    baris.append("GOLONGAN C (tidak bisa disejajarkan)")
    baris.append("=" * 70)
    for r in hasil:
        if r["golongan"] == "C":
            baris.append("%s | %s | %s" % (r["id"], r["example_cn"], r["pinyin_lama"]))
            baris.append("    -> " + "; ".join(r["catatan"]))
    baris.append("")
    baris.append("=" * 70)
    baris.append("GOLONGAN B2 (perlu kamu lihat), dikelompokkan menurut karakter berisiko")
    baris.append("=" * 70)
    kelompok = collections.defaultdict(list)
    for r in hasil:
        if r["golongan"] == "B2":
            kunci = ",".join(r["karakter_berisiko"]) or "(kata >1 bacaan)"
            kelompok[kunci].append(r)
    for kunci in sorted(kelompok, key=lambda k: -len(kelompok[k])):
        baris.append("")
        baris.append("--- %s (%d contoh) ---" % (kunci, len(kelompok[kunci])))
        for r in kelompok[kunci]:
            baris.append("%s  [%s]" % (r["example_cn"], r["id"]))
            baris.append("    usulan: " + r["pinyin_usulan"])
            if r["catatan"]:
                baris.append("    catatan: " + "; ".join(r["catatan"]))
    baris.append("")
    LAPORAN.write_text("\r\n".join(baris), encoding="utf-8-sig")
    USULAN.write_text(json.dumps(hasil, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print("Contoh tanpa nada: %d  | A pasti: %d  | B1 yakin: %d  | B2 perlu dilihat: %d  | C tak bisa disejajarkan: %d"
          % (len(hasil), hitung["A"], hitung["B1"], hitung["B2"], hitung["C"]))
    print("Laporan  : %s" % LAPORAN)
    print("Usulan   : %s" % USULAN)
    print("Tidak ada data yang diubah.")


if __name__ == "__main__":
    sys.exit(main())

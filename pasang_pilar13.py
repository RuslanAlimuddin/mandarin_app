#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pasang_pilar13.py -- memasang Pilar 13 "Kata Penunjuk Posisi (方位词)" ke Peta Bahasa.

Pekerjaan:
  A. membuat data\\pelajaran\\pilar_13.json (7 bagian pelajaran)
  B. peta-bahasa.html: (1) entri Pilar 13 di akhir daftar pilar, (2) judul "Peta 13 Pilar",
     (3) kartu Pilar 13 terbuka otomatis, (4) teks Pilar 12: "60 entri / A-J" jadi "64 entri / A-L"
Berkas lain tidak disentuh. Pemeriksaan otomatis: setiap kata kamus dalam contoh harus ada di
data\\app_words.json dan pinyinnya harus sama dengan pinyin kamus.

CARA PAKAI (dari C:\\mandarin_app>):
  1) Lihat dulu (TIDAK mengubah apa pun):   python pasang_pilar13.py
  2) Pasang:                                python pasang_pilar13.py --apply
Cadangan: peta-bahasa.html.bak_pilar13_<tanggal-jam>. Aman diulang.
"""
import json
import re
import shutil
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
KATA = ROOT / "data" / "app_words.json"
PIL13 = ROOT / "data" / "pelajaran" / "pilar_13.json"
PETA = ROOT / "peta-bahasa.html"


def hz(s):
    return '<span class="hz">%s</span>' % s


def py(s):
    return '<span class="py">%s</span>' % s


def ks(c, p):  # karakter + pinyin
    return "%s (%s)" % (hz(c), py(p))


def kalimat(c, p, t):
    return [hz(c), py(p), t]


# ---------- kalimat contoh: (hanzi, pinyin, arti) ----------
S = {
    "atas": ("书在桌子上面。", "Shū zài zhuōzi shàngmiàn.", "Buku ada di atas meja."),
    "luar": ("他在外面。", "Tā zài wàimiàn.", "Dia ada di luar."),
    "meja": ("书在桌子上。", "Shū zài zhuōzi shang.", "Buku ada di atas meja."),
    "rumah": ("他在家里。", "Tā zài jiā li.", "Dia ada di rumah."),
    "tangan": ("我手里有一本书。", "Wǒ shǒu li yǒu yī běn shū.", "Di tangan saya ada sebuah buku."),
    "hati": ("我心里很高兴。", "Wǒ xīn li hěn gāoxìng.", "Dalam hati saya senang."),
    "jalan": ("他在路上。", "Tā zài lù shang.", "Dia sedang di jalan."),
    "usia": ("十八岁以上可以来。", "Shíbā suì yǐshàng kěyǐ lái.", "Yang berusia 18 tahun ke atas boleh datang."),
    "kecuali": ("除了他以外，大家都来了。", "Chúle tā yǐwài, dàjiā dōu lái le.", "Selain dia, semuanya sudah datang."),
    "luarnegeri": ("他在国外学习。", "Tā zài guówài xuéxí.", "Dia belajar di luar negeri."),
    "antara": ("我们中间有一张桌子。", "Wǒmen zhōngjiān yǒu yī zhāng zhuōzi.", "Di antara kami ada sebuah meja."),
    "qizhong": ("这里有三本书，其中两本是新的。", "Zhèlǐ yǒu sān běn shū, qízhōng liǎng běn shì xīn de.", "Di sini ada tiga buku, dua di antaranya baru."),
    "waktu": ("我没有时间。", "Wǒ méiyǒu shíjiān.", "Saya tidak punya waktu."),
    "kamar": ("我的房间很大。", "Wǒ de fángjiān hěn dà.", "Kamar saya besar."),
}

# kata kamus yang dipakai di tabel dan kalimat; dicek ada di app_words.json
KAMUS = ("上面 下面 里面 外面 前面 后面 中间 旁边 左边 右边 里边 外边 上边 下边 上头 里头 外头 身上 晚上 早上 地上 路上 "
         "网上 马上 桌子 家里 心里 这里 那里 哪里 手里 以上 以下 以外 之外 国外 国内 之间 时间 空间 房间 其中 当中 "
         "海边 身边 周边 以内 之内 楼下 地下 大家 除了 可以 学习 没有 高兴").split()


def tabel(kolom, baris):
    return {"tipe": "tabel", "kolom": kolom, "baris": baris}


def para(t):
    return {"tipe": "paragraf", "teks": t}


def awas(t):
    return {"tipe": "peringatan", "teks": t}


def kal_tabel(keys, pola):
    return tabel(["Pola", "Contoh", "Pinyin", "Arti"],
                 [[p] + kalimat(*S[k]) for k, p in zip(keys, pola)])


BAGIAN = [
    {"judul": "1. Apa Itu Kata Penunjuk Posisi (方位词)?", "isi": [
        para("Kata penunjuk posisi (%s, %s) menyebut letak atau arah: atas, bawah, dalam, luar, tengah, dan samping. "
             "Tujuh karakter pokoknya adalah %s." % (hz("方位词"), py("fāngwèicí"), hz("上 下 里 外 中 间 边"))),
        tabel(["Karakter", "Arti dasar", "Contoh dari Kamus"], [
            [ks("上", "shàng"), "atas; permukaan", "%s、%s、%s" % (hz("上面"), hz("晚上"), hz("网上"))],
            [ks("下", "xià"), "bawah", "%s、%s、%s" % (hz("下面"), hz("楼下"), hz("地下"))],
            [ks("里", "lǐ"), "dalam", "%s、%s、%s" % (hz("里面"), hz("家里"), hz("这里"))],
            [ks("外", "wài"), "luar", "%s、%s、%s" % (hz("外面"), hz("国外"), hz("以外"))],
            [ks("中", "zhōng"), "tengah; di antara", "%s、%s、%s" % (hz("中间"), hz("其中"), hz("当中"))],
            [ks("间", "jiān"), "ruang atau jarak di antara", "%s、%s、%s" % (hz("之间"), hz("房间"), hz("时间"))],
            [ks("边", "biān"), "sisi; tepi", "%s、%s、%s" % (hz("旁边"), hz("左边"), hz("海边"))],
        ]),
        awas("Tidak semua kata yang berakhiran karakter ini menyebut tempat. %s berarti \"segera\" (secara harfiah "
             "\"di atas kuda\"), %s berarti \"malam\", dan %s berarti \"waktu\". Lihat kata lengkapnya, bukan "
             "karakternya saja." % (hz("马上"), hz("晚上"), hz("时间"))),
    ]},
    {"judul": "2. Bentuk Sederhana dan Bentuk Gabungan", "isi": [
        para("Karakter %s sendirian jarang menjadi kata tempat yang lengkap. Biasanya ia diberi tambahan %s, %s, atau %s "
             "sehingga menjadi kata tempat. Ketiga bentuk itu artinya hampir sama; %s dan %s terasa lebih lisan." % (
                 hz("上 下 里 外"), hz("面"), hz("边"), hz("头"), hz("边"), hz("头"))),
        tabel(["Dasar", "+ 面", "+ 边", "+ 头"], [
            [hz("上"), "%s (%s)" % (hz("上面"), py("shàngmiàn")), "%s (%s)" % (hz("上边"), py("shàngbian")), "%s (%s)" % (hz("上头"), py("shàngtou"))],
            [hz("下"), "%s (%s)" % (hz("下面"), py("xiàmiàn")), "%s (%s)" % (hz("下边"), py("xiàbian")), "belum ada di Kamus"],
            [hz("里"), "%s (%s)" % (hz("里面"), py("lǐmiàn")), "%s (%s)" % (hz("里边"), py("lǐbian")), "%s (%s)" % (hz("里头"), py("lǐtou"))],
            [hz("外"), "%s (%s)" % (hz("外面"), py("wàimiàn")), "%s (%s)" % (hz("外边"), py("wàibian")), "%s (%s)" % (hz("外头"), py("wàitou"))],
        ]),
        kal_tabel(["atas", "luar"], ["Benda + 在 + benda lain + 上面", "S + 在 + 外面"]),
    ]},
    {"judul": "3. Pola Tempat + 上 / 里", "isi": [
        para("Bahasa Indonesia memakai satu kata \"di\" untuk banyak keadaan. Dalam bahasa Mandarin, setelah kata benda dipilih "
             "%s untuk benda yang mempunyai permukaan, dan %s untuk ruang atau wadah. Karakter %s dan %s di sini ditulis "
             "tanpa tanda nada karena dibaca ringan." % (hz("上"), hz("里"), hz("上"), hz("里"))),
        kal_tabel(["meja", "rumah", "tangan", "hati", "jalan"], [
            "Benda + 上 (permukaan)", "Tempat + 里 (ruang)", "Bagian tubuh + 里 (di tangan)",
            "心 + 里 (dalam hati)", "路 + 上 (di sepanjang jalan)"]),
        awas("Untuk \"di rumah\" orang sering cukup berkata %s; %s juga benar. Tidak setiap \"di\" dalam bahasa Indonesia "
             "perlu padanan 上 atau 里." % (hz("在家"), hz("在家里"))),
    ]},
    {"judul": "4. Batas dan Luar: 以上, 以下, 以外, 之外", "isi": [
        para("Dengan %s di depan, karakter penunjuk posisi menyebut batas atau jangkauan. Angka batasnya umumnya ikut "
             "dihitung pada %s dan %s." % (hz("以"), hz("以上"), hz("以下"))),
        tabel(["Kata", "Arti", "Catatan"], [
            [ks("以上", "yǐshàng"), "ke atas; di atas batas itu", "Dipakai untuk angka, tingkat, atau hal yang sudah disebut."],
            [ks("以下", "yǐxià"), "ke bawah; di bawah batas itu", "Pasangan 以上."],
            [ks("以外", "yǐwài"), "selain; di luar", "Sering bersama 除了: 除了…以外."],
            [ks("之外", "zhīwài"), "di luar", "Mirip 以外, terasa lebih tertulis."],
            [ks("以内", "yǐnèi"), "di dalam batas", "Pasangan 以外."],
            [ks("国外", "guówài"), "luar negeri", "Lawan 国内 (guónèi)."],
        ]),
        kal_tabel(["usia", "kecuali", "luarnegeri"], ["Angka + 以上", "除了 + A + 以外", "在 + 国外 + V"]),
    ]},
    {"judul": "5. 中 dan 间: Tengah, Antara, Waktu", "isi": [
        para("Karakter %s dan %s tidak hanya menyebut ruang. Keduanya juga muncul dalam kata untuk \"di antara\", \"kamar\", "
             "dan \"waktu\"." % (hz("中"), hz("间"))),
        tabel(["Kata", "Arti", "Catatan"], [
            [ks("中间", "zhōngjiān"), "tengah", "Letak di tengah-tengah."],
            [ks("之间", "zhījiān"), "antara", "Diletakkan setelah kata benda atau dua pihak: A 和 B 之间."],
            [ks("其中", "qízhōng"), "di antaranya", "Mengambil sebagian dari yang baru disebut."],
            [ks("当中", "dāngzhōng"), "di antara; di tengah", "Hampir sama dengan 其中."],
            [ks("房间", "fángjiān"), "kamar", "间 menamai ruang."],
            [ks("时间", "shíjiān"), "waktu", "间 di sini sudah bergeser dari arti ruang."],
        ]),
        kal_tabel(["antara", "qizhong", "waktu", "kamar"], [
            "A + 中间 + 有 + benda", "…，其中 + jumlah", "没有 + 时间", "Pemilik + 的 + 房间"]),
    ]},
    {"judul": "6. Aturan Bacaan: Kapan Nada Netral?", "isi": [
        para("Banyak karakter penunjuk posisi dibaca ringan (tanpa nada) setelah kata benda, tetapi tidak semuanya. "
             "Tabel ini hanya memuat bacaan yang sama dengan Kamus kita."),
        tabel(["Karakter", "Dibaca ringan (netral) bila…", "Dibaca bernada penuh bila…"], [
            [hz("里"), "setelah kata benda: %s、%s、%s" % (ks("家里", "jiā li"), ks("手里", "shǒu li"), ks("心里", "xīn li")),
             "setelah 这/那/哪: %s、%s、%s (lǐ, nada 3)" % (ks("这里", "zhèlǐ"), ks("那里", "nàlǐ"), ks("哪里", "nǎlǐ"))],
            [hz("上"), "setelah kata benda atau waktu: %s、%s、%s、%s" % (ks("地上", "dì shang"), ks("路上", "lù shang"), ks("身上", "shēn shang"), ks("晚上", "wǎn shang")),
             "dalam kata tetap: %s、%s、%s" % (ks("马上", "mǎshàng"), ks("网上", "wǎngshàng"), ks("以上", "yǐshàng"))],
            [hz("边"), "setelah 左 右 里 外 上 下: %s、%s、%s" % (ks("左边", "zuǒ bian"), ks("右边", "yòu bian"), ks("里边", "lǐ bian")),
             "bila berarti tepi atau sisi: %s、%s、%s" % (ks("旁边", "pángbiān"), ks("身边", "shēnbiān"), ks("海边", "hǎibiān"))],
        ]),
        awas("Bacaan %s tidak seragam di Kamus: %s, %s, %s, dan %s memakai %s penuh, sedangkan %s memakai %s ringan. "
             "Dalam percakapan, %s memang sering dibaca ringan. Ikuti tulisan pada kartu Kamus saat belajar." % (
                 hz("面"), hz("上面"), hz("下面"), hz("里面"), hz("外面"), py("miàn"), hz("后面"), py("hòu mian"), hz("面"))),
    ]},
    {"judul": "7. Pasangan Lawan dan Peta Cepat", "isi": [
        para("Cara cepat mengingat: hafalkan penunjuk posisi sebagai pasangan lawan. Semua kata di bawah ada di Kamus."),
        tabel(["Pasangan", "Arti"], [
            ["%s ↔ %s" % (hz("上面"), hz("下面")), "di atas ↔ di bawah"],
            ["%s ↔ %s" % (hz("里面"), hz("外面")), "di dalam ↔ di luar"],
            ["%s ↔ %s" % (hz("前面"), hz("后面")), "di depan ↔ di belakang"],
            ["%s ↔ %s" % (hz("左边"), hz("右边")), "kiri ↔ kanan"],
            ["%s ↔ %s" % (hz("里边"), hz("外边")), "di dalam ↔ di luar (lisan)"],
            ["%s ↔ %s" % (hz("国内"), hz("国外")), "dalam negeri ↔ luar negeri"],
            ["%s ↔ %s" % (hz("以上"), hz("以下")), "ke atas ↔ ke bawah"],
        ]),
        awas("Jangan menyimpulkan bahwa semua kata yang berakhiran %s, %s, %s, %s, %s, %s, atau %s menyebut posisi. "
             "Periksa arti kata lengkapnya di Kamus." % tuple(hz(c) for c in "上下里外中间边")),
    ]},
]

PILAR = {
    "pilar": 13,
    "judul": "Kata Penunjuk Posisi (方位词)",
    "ringkasan": "Pelajar mengenal tujuh karakter penunjuk posisi (上 下 里 外 中 间 边), membedakan bentuk sederhana dan "
                 "gabungan, memakai pola 在 + tempat + 上/里, memahami batas (以上, 以外), 中 dan 间, serta aturan bacaan netral.",
    "bagian": BAGIAN,
}

ENTRI = """  {
    title: '13. Kata Penunjuk Posisi (方位词)',
    status: 'baru',
    desc: 'Kata yang menyebut letak dan arah: 上 下 里 外 中 间 边. Pelajaran Lengkap berisi bentuk sederhana dan gabungan, pola 在 + tempat + 上/里, batas (以上, 以外), 中 dan 间, serta aturan bacaan netral.',
    subtopics: [
      { name: 'Bentuk gabungan (上面, 里边, 外头, dst.) — cari contohnya di Kamus', status: 'kuat', link: 'kamus.html#search=里面', label: 'Lihat contoh di Kamus →' },
      { name: 'Pola 在 + tempat + 上/里, batas 以上/以外, dan aturan bacaan netral — kini di 📖 Pelajaran Lengkap', status: 'baru' },
    ],
  },
"""


def fail(m):
    print("GALAT: " + m)
    sys.exit(1)


def periksa(kata):
    tidak = [k for k in KAMUS if k not in kata]
    if tidak:
        fail("kata tidak ada di app_words.json: %s" % tidak)
    pak = 0
    for key, (c, p, _t) in S.items():
        flat = re.sub(r"[\s\.,，。]", "", p).lower()
        for k in KAMUS:
            if len(k) >= 2 and k in c:
                dat = re.sub(r"\s", "", kata[k]["pinyin"]).lower()
                if dat not in flat:
                    print("  catatan pinyin [%s] %s: kamus=%s kalimat=%s" % (key, k, kata[k]["pinyin"], p))
                    pak += 1
    return pak


def main():
    apply = "--apply" in sys.argv
    print("Mode: " + ("PASANG (--apply)" if apply else "LIHAT-DULU (tidak mengubah apa pun)"))
    kata = {w["simplified"]: w for w in json.loads(KATA.read_text(encoding="utf-8"))}
    beda = periksa(kata)
    if beda:
        fail("%d pinyin kalimat contoh berbeda dari Kamus (lihat catatan di atas)." % beda)
    print("  pemeriksaan kata dan pinyin: OK (%d kata kamus, %d kalimat)" % (len(KAMUS), len(S)))

    isi_json = json.dumps(PILAR, ensure_ascii=False, indent=2) + "\n"
    perlu_json = not PIL13.exists() or PIL13.read_text(encoding="utf-8") != isi_json
    print("  pilar_13.json: " + ("buat/perbarui (%d bagian)" % len(BAGIAN) if perlu_json else "sudah sama"))

    h = PETA.read_text(encoding="utf-8")
    baru = h
    if "title: '13. Kata Penunjuk Posisi" not in baru:
        akhir = "    ],\n  },\n];"
        if baru.count(akhir) != 1:
            fail("penutup daftar PILLARS tidak ditemukan tepat satu kali di peta-bahasa.html")
        baru = baru.replace(akhir, "    ],\n  },\n" + ENTRI + "];")
    ganti = [
        ("<title>Peta 12 Pilar —", "<title>Peta 13 Pilar —"),
        ("<h1>🗺️ Peta 12 Pilar Bahasa Mandarin</h1>", "<h1>🗺️ Peta 13 Pilar Bahasa Mandarin</h1>"),
        ("awalan & akhiran (60 entri)", "awalan & akhiran (64 entri)"),
        ("dan peta 60 entri.", "dan peta 64 entri."),
        ("Awalan & Akhiran — 60 entri di Kamus (kelompok A–J)", "Awalan & Akhiran — 64 entri di Kamus (kelompok A–L)"),
        ("querySelectorAll('.pillar-card')[11]; // Pilar 12 (index 11) — yang terbaru",
         "querySelectorAll('.pillar-card')[12]; // Pilar 13 (index 12) — yang terbaru"),
    ]
    for a, b in ganti:
        if a in baru:
            baru = baru.replace(a, b)
        elif b not in baru:
            fail("teks tidak ditemukan di peta-bahasa.html: " + a)
    perlu_peta = baru != h
    print("  peta-bahasa.html: " + ("ubah (entri Pilar 13, judul, Pilar 12 jadi 64 entri)" if perlu_peta else "sudah sama"))

    if not (perlu_json or perlu_peta):
        print("Tidak ada yang perlu diubah.")
        return
    if not apply:
        print("\nBelum ada yang diubah. Jika sudah sesuai, jalankan:  python pasang_pilar13.py --apply")
        return

    cap = time.strftime("%Y%m%d-%H%M%S")
    cad = PETA.with_name(PETA.name + ".bak_pilar13_" + cap)
    shutil.copy2(PETA, cad)
    PIL13.parent.mkdir(parents=True, exist_ok=True)
    if perlu_json:
        PIL13.write_text(isi_json, encoding="utf-8")
    if perlu_peta:
        PETA.write_text(baru, encoding="utf-8")
    cek = json.loads(PIL13.read_text(encoding="utf-8"))
    if cek["pilar"] != 13 or len(cek["bagian"]) != 7 or PETA.read_text(encoding="utf-8").count("title: '13. Kata Penunjuk Posisi") != 1:
        shutil.copy2(cad, PETA)
        fail("pemeriksaan akhir gagal; peta-bahasa.html dikembalikan dari cadangan.")
    print("\nSelesai. Cadangan: " + cad.name)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pasang_bukan_imbuhan.py -- tambahkan 102 kata "bukan" imbuhan hasil kurasi ke data\\afiks_kamus.json
==============================================================================================
Cara B latihan imbuhan (keputusan رسلان, 24 November 2026). Bahan: hasil GPT atas 735 kata kandidat
(kerja_gpt_afiks\\kandidat\\tahap1\\batch_01..17_hasil.json), dikurasi Claude. Pedoman kurasi: sebuah kata
masuk daftar "bukan" HANYA bila karakter imbuhan itu benar-benar berarti lain daripada fungsi imbuhannya
(mis. 卫生: 生 = hidup; 老虎: 老 = bagian nama hewan). Kata yang karakternya masih berarti sama dengan fungsi
imbuhan (mis. 就业, 终点, 总统, 同志) TIDAK dimasukkan. Batas 8 kata per imbuhan, dipilih dari HSK terendah.

Yang diubah (hanya data\\afiks_kamus.json): di entri imbuhan yang bersangkutan, kata + alasan DITAMBAHKAN di
akhir daftar "bukan". Daftar "bukan" yang sudah ada dan semua isian lain tidak disentuh.
Hasil: imbuhan yang punya daftar "bukan" naik dari 18 menjadi 38; total kata "bukan" dari 40 menjadi 142.
Otomatis tampil di Kamus > Kelompok > Awalan & Akhiran (kotak "Mirip tetapi bukan") dan dipakai soal
"Imbuhan atau bukan?" di Flashcard. buat_pengecoh_imbuhan.py TIDAK perlu dijalankan ulang (hanya memakai contoh).

CARA PAKAI (dari C:\\mandarin_app>):
  1) Lihat dulu (TIDAK mengubah apa pun):   python pasang_bukan_imbuhan.py
  2) Terapkan:                              python pasang_bukan_imbuhan.py --apply

KEAMANAN
  - Format afiks_kamus.json dijaga persis; skrip menolak bekerja bila formatnya tidak bisa ditulis ulang persis sama.
  - Cadangan sebelum menulis: data\\afiks_kamus.json.bak_bukan_<tanggal-jam>
  - Tiap kata diperiksa: ada persis di app_words.json, posisinya benar (akhiran di belakang, awalan di depan),
    bukan salah satu kata contoh imbuhan itu, dan alasannya memuat kata "bukan". Bila ada yang tidak cocok, berhenti.
  - Setelah menulis, berkas dibaca ulang dan dibandingkan dengan yang diharapkan; bila tidak cocok, dikembalikan dari cadangan.
  - Aman diulang (kata yang sudah ada dilewati). Daftar lengkap: hasil_bukan_imbuhan.txt
"""
import argparse
import copy
import json
import shutil
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent
AFIKS = ROOT / "data" / "afiks_kamus.json"
KATA = ROOT / "data" / "app_words.json"
HASIL = ROOT / "hasil_bukan_imbuhan.txt"

# (imbuhan, kata, alasan)
TABEL = [
    ('家', '在家',
     '在家 berarti “berada di rumah”; 家 berarti rumah atau tempat tinggal, bukan penanda profesi atau keahlian.'),
    ('家', '搬家',
     '搬家 berarti “pindah rumah”; 家 berarti rumah atau tempat tinggal, bukan penanda ahli dalam suatu bidang.'),
    ('家', '老家',
     '老家 berarti “tempat asal” atau “kampung halaman”; 家 menunjuk tempat atau rumah asal, bukan orang yang ahli dalam suatu bidang.'),
    ('家', '人家',
     '人家 berarti “orang lain”; 家 menjadi bagian dari kata yang merujuk kepada orang lain, bukan penanda ahli dalam suatu bidang.'),
    ('家', '老人家',
     '老人家 merupakan sebutan sopan untuk “orang tua”; 家 menjadi bagian dari ungkapan penghormatan, bukan penanda ahli dalam suatu bidang.'),
    ('家', '成家',
     '成家 berarti “menikah dan membangun rumah tangga”; 家 berarti keluarga atau rumah tangga, bukan penanda ahli dalam suatu bidang.'),
    ('家', '管家',
     '管家 berarti “pengurus rumah tangga”; 家 berarti rumah tangga yang diurus, bukan penanda ahli dalam suatu bidang.'),
    ('家', '亲家',
     '亲家 berarti “orang tua besan”; 家 menunjukkan hubungan keluarga, bukan orang yang ahli atau bekerja dalam suatu bidang.'),
    ('员', '裁员',
     '裁员 berarti “memotong staf” atau “memberhentikan karyawan”; 员 merujuk pada karyawan yang dikurangi, bukan membentuk sebutan petugas atau anggota.'),
    ('生', '先生',
     '先生 berarti “tuan” atau “bapak” sebagai sapaan; 生 menjadi bagian dari sapaan yang sudah utuh, bukan penanda status pelajar atau peran tertentu.'),
    ('生', '一生',
     '一生 berarti “seumur hidup”; 生 menyatakan masa hidup, bukan orang dengan status atau peran tertentu.'),
    ('生', '卫生',
     '卫生 berarti “kebersihan” atau “sanitasi”; 生 menjadi bagian kata yang menyatakan konsep kebersihan, bukan penanda orang.'),
    ('生', '诞生',
     '诞生 berarti “terlahir”; 生 menyatakan peristiwa kelahiran, bukan orang dengan status atau peran tertentu.'),
    ('生', '再生',
     '再生 berarti “terlahir kembali” atau “beregenerasi”; 生 menyatakan proses hidup kembali, bukan sebutan orang.'),
    ('生', '野生',
     '野生 berarti “liar” atau “hidup di alam”; 生 menyatakan keadaan hidup, bukan orang dengan status atau peran tertentu.'),
    ('生', '逃生',
     '逃生 berarti “melarikan diri demi menyelamatkan nyawa”; 生 berkaitan dengan nyawa atau hidup, bukan penanda orang.'),
    ('生', '亲生',
     '亲生 berarti “kandung” atau “biologis”; 生 menyatakan hubungan kelahiran, bukan orang dengan status atau peran tertentu.'),
    ('手', '举手',
     '举手 berarti “mengangkat tangan”; 手 menunjuk anggota tubuh yang diangkat, bukan sebutan orang yang melakukan kegiatan.'),
    ('手', '握手',
     '握手 berarti “berjabat tangan”; 手 menunjuk tangan yang digunakan dalam tindakan tersebut, bukan penanda orang.'),
    ('手', '二手',
     '二手 berarti “bekas” atau “diperoleh secara tidak langsung”; 手 menjadi bagian ungkapan yang menyatakan tingkat atau jalur perolehan, bukan penanda orang.'),
    ('手', '分手',
     '分手 berarti “berpisah” atau “putus hubungan”; 手 menjadi bagian kata kerja yang bermakna perpisahan, bukan penanda orang.'),
    ('手', '随手',
     '随手 berarti “sambil lalu” atau “dengan mudah”; 手 menjadi bagian ungkapan yang menerangkan cara melakukan sesuatu, bukan sebutan pelaku.'),
    ('手', '招手',
     '招手 berarti “melambai dengan tangan”; 手 menunjuk anggota tubuh yang digunakan untuk memberi isyarat, bukan sebutan pelaku.'),
    ('手', '双手',
     '双手 berarti “kedua tangan”; 手 menunjuk anggota tubuh, bukan orang yang melakukan kegiatan atau memiliki keterampilan.'),
    ('手', '动手',
     '动手 berarti “mulai bekerja” atau “menggunakan tangan untuk memukul”; 手 menunjuk tindakan menggunakan tangan, bukan sebutan orang.'),
    ('长', '生长',
     '生长 berarti “tumbuh” atau “bertumbuh besar”; 长 menyatakan pertumbuhan, bukan orang yang memimpin kelompok.'),
    ('长', '延长',
     '延长 berarti “memperpanjang”; 长 menyatakan bertambah panjang, bukan jabatan pemimpin.'),
    ('长', '土生土长',
     '土生土长 berarti “lahir dan dibesarkan di daerah setempat”; 长 menyatakan proses tumbuh besar, bukan jabatan pemimpin.'),
    ('长', '全长',
     '全长 berarti “panjang keseluruhan”; 长 menyatakan ukuran panjang, bukan jabatan pemimpin.'),
    ('长', '专长',
     '专长 berarti “keahlian khusus”; 长 dibaca cháng dan menyatakan kemampuan atau keunggulan, bukan pemimpin.'),
    ('长', '特长',
     '特长 berarti “keunggulan” atau “kemampuan khusus”; 长 dibaca cháng dan menyatakan kelebihan seseorang, bukan jabatan pemimpin.'),
    ('长', '修长',
     '修长 berarti “ramping dan jenjang”; 长 dibaca cháng dan menyatakan bentuk yang panjang, bukan pemimpin.'),
    ('性', '索性',
     '索性 berarti “sebaiknya langsung melakukannya”; 性 merupakan bagian dari kata keterangan ini, bukan akhiran yang menyatakan sifat atau karakteristik.'),
    ('度', '态度',
     '态度 berarti “sikap atau pendekatan”; 度 menjadi bagian dari kata yang bermakna sikap, bukan akhiran pengukur tingkat.'),
    ('度', '制度',
     '制度 berarti “sistem atau lembaga”; 度 menjadi bagian dari kata benda tersebut, bukan penanda tingkat atau ukuran.'),
    ('度', '季度',
     '季度 berarti “seperempat tahun”; 度 menjadi bagian dari istilah periode waktu, bukan penanda tingkat atau ukuran keadaan.'),
    ('度', '风度',
     '风度 berarti “keanggunan atau sikap anggun”; 度 menjadi bagian dari kata yang bermakna pembawaan, bukan ukuran tingkat.'),
    ('度', '年度',
     '年度 berarti “tahun atau tahunan”; 度 menjadi bagian dari istilah periode tahunan, bukan penanda tingkat atau ukuran keadaan.'),
    ('度', '一度',
     '一度 berarti “sementara waktu atau pada suatu waktu”; 度 menunjukkan waktu atau kesempatan, bukan tingkat atau ukuran keadaan.'),
    ('度', '调度',
     '调度 berarti “mengirim atau menjadwalkan”; 度 menjadi bagian dari kata kerja tersebut, bukan penanda tingkat atau ukuran.'),
    ('度', '再度',
     '再度 berarti “sekali lagi”; 度 menjadi bagian dari kata keterangan pengulangan, bukan penanda tingkat atau ukuran.'),
    ('率', '表率',
     '表率 berarti “contoh atau model”; 率 dibaca shuài dan bermakna teladan dalam kata ini, bukan akhiran yang menyatakan rasio.'),
    ('感', '流感',
     '流感 berarti “flu atau influenza”; 感 merupakan bagian dari nama penyakit, bukan perasaan atau kesan terhadap sesuatu.'),
    ('力', '巧克力',
     '巧克力 berarti “cokelat”; 力 hanya bagian dari penulisan kata pinjaman, bukan imbuhan yang menyatakan tenaga atau kemampuan.'),
    ('量', '衡量',
     '衡量 berarti “menimbang atau memeriksa”; 量 dibaca sebagai bagian dari kata kerja, bukan akhiran yang menyatakan jumlah atau ukuran.'),
    ('量', '打量',
     '打量 berarti “mengamati seseorang dari atas ke bawah”; 量 menjadi bagian dari kata kerja, bukan akhiran bermakna jumlah atau ukuran.'),
    ('量', '较量',
     '较量 berarti “bersaing atau mengadu kemampuan”; 量 menjadi bagian dari kata kerja, bukan akhiran yang menyatakan jumlah atau ukuran.'),
    ('量', '考量',
     '考量 berarti “mempertimbangkan sesuatu”; 量 menjadi bagian dari kata kerja, bukan akhiran bermakna jumlah atau ukuran.'),
    ('法', '合法',
     '合法 berarti “sah atau sesuai hukum”; 法 bermakna hukum atau aturan, bukan cara atau metode.'),
    ('法', '依法',
     '依法 berarti “sesuai hukum”; 法 bermakna hukum yang menjadi dasar tindakan, bukan cara melakukan tindakan.'),
    ('法', '违法',
     '违法 berarti “ilegal atau melanggar hukum”; 法 bermakna hukum yang dilanggar, bukan cara atau metode.'),
    ('法', '宪法',
     '宪法 berarti “konstitusi negara”; 法 bermakna hukum dalam istilah hukum negara, bukan cara atau metode melakukan sesuatu.'),
    ('法', '执法',
     '执法 berarti “menegakkan hukum”; 法 bermakna hukum yang ditegakkan, bukan metode melakukan tindakan.'),
    ('法', '司法',
     '司法 berarti “yudisial atau administrasi keadilan”; 法 bermakna hukum dalam bidang peradilan, bukan cara melakukan sesuatu.'),
    ('法', '非法',
     '非法 berarti “ilegal”; 法 bermakna hukum atau aturan, bukan cara atau metode.'),
    ('法', '刑法',
     '刑法 berarti “hukum pidana”; 法 bermakna hukum, bukan metode melakukan sesuatu.'),
    ('观', '参观',
     '参观 berarti “mengunjungi atau melihat-lihat”; 观 menjadi bagian kata kerja berkunjung dan mengamati, bukan pandangan atau sikap.'),
    ('观', '壮观',
     '壮观 berarti “spektakuler atau pemandangan megah”; 观 bermakna pemandangan yang terlihat, bukan cara pandang seseorang.'),
    ('观', '外观',
     '外观 berarti “penampilan luar”; 观 menjadi bagian kata yang berarti tampilan, bukan pandangan atau sikap.'),
    ('观', '景观',
     '景观 berarti “lanskap atau pemandangan”; 观 bermakna sesuatu yang terlihat, bukan cara seseorang memandang sesuatu.'),
    ('观', '美观',
     '美观 berarti “sedap dipandang atau cantik”; 观 bermakna terlihat atau dipandang, bukan pandangan atau sikap terhadap suatu hal.'),
    ('观', '可观',
     '可观 berarti “layak dilihat atau cukup besar”; 观 bermakna sesuatu yang dapat dilihat, bukan cara pandang atau sikap.'),
    ('观', '纵观',
     '纵观 berarti “meninjau secara menyeluruh”; 观 menjadi bagian kata kerja meninjau, bukan akhiran pembentuk pandangan atau sikap.'),
    ('观', '旁观',
     '旁观 berarti “menonton sebagai orang luar”; 观 menjadi bagian kata kerja melihat atau menyaksikan, bukan akhiran pembentuk pandangan.'),
    ('点', '一点点',
     '一点点 berarti “sedikit saja”; 点 dipakai sebagai satuan atau penanda jumlah kecil, bukan sisi atau hal tertentu yang dibahas.'),
    ('点', '晚点',
     '晚点 berarti “terlambat atau tertunda”; 点 menjadi bagian ungkapan waktu atau keterlambatan, bukan sisi atau hal yang dibahas.'),
    ('点', '指点',
     '指点 berarti “menunjukkan atau memberi petunjuk”; 点 menjadi bagian kata kerja, bukan akhiran yang menyebut sisi atau hal tertentu.'),
    ('学', '中学',
     '中学 berarti “sekolah menengah”; 学 menjadi bagian nama jenjang atau lembaga pendidikan, bukan nama bidang ilmu.'),
    ('学', '小学',
     '小学 berarti “sekolah dasar”; 学 menjadi bagian nama jenjang atau lembaga pendidikan, bukan nama bidang ilmu.'),
    ('学', '放学',
     '放学 berarti “selesai sekolah pada akhir hari”; 学 menjadi bagian kata tentang kegiatan sekolah, bukan nama bidang ilmu.'),
    ('学', '同学',
     '同学 berarti “teman sekolah atau belajar di sekolah yang sama”; 学 bermakna belajar atau sekolah, bukan akhiran nama bidang ilmu.'),
    ('学', '上学',
     '上学 berarti “pergi ke sekolah atau bersekolah”; 学 menjadi bagian kata tentang kegiatan sekolah, bukan nama bidang ilmu.'),
    ('学', '开学',
     '开学 berarti “sekolah atau semester dimulai”; 学 menjadi bagian ungkapan tentang kegiatan sekolah, bukan nama bidang ilmu.'),
    ('学', '中小学',
     '中小学 berarti “sekolah menengah dan dasar”; 学 menjadi bagian nama jenjang pendidikan, bukan nama bidang ilmu.'),
    ('学', '教学',
     '教学 berarti “pengajaran atau mengajar”; 学 menjadi bagian kata tentang kegiatan belajar-mengajar, bukan nama bidang ilmu.'),
    ('界', '交界',
     '交界 berarti “perbatasan atau batas umum”; 界 menunjukkan garis pertemuan atau batas wilayah, bukan lingkungan atau kelompok bidang.'),
    ('室', '皇室',
     '皇室 berarti “keluarga kerajaan atau rumah tangga kekaisaran”; 室 bermakna keluarga atau garis keturunan, bukan ruangan untuk kegiatan tertentu.'),
    ('场', '立场',
     '立场 berarti “posisi atau sudut pandang”; 场 menjadi bagian kata yang bermakna kiasan, bukan area kegiatan.'),
    ('所', '有所',
     '有所 berarti “agak atau sampai batas tertentu”; 所 menjadi bagian ungkapan tata bahasa, bukan akhiran nama tempat atau lembaga.'),
    ('机', '时机',
     '时机 berarti “kesempatan atau saat yang tepat”; 机 berkaitan dengan peluang, bukan mesin atau perangkat.'),
    ('机', '动机',
     '动机 berarti “motif atau motivasi”; 机 menjadi bagian kata yang bermakna dorongan atau alasan, bukan nama mesin.'),
    ('机', '危机',
     '危机 berarti “krisis”; 机 menjadi bagian kata yang bermakna peluang atau titik perubahan, bukan nama mesin.'),
    ('机', '投机',
     '投机 berarti “cocok atau berspekulasi”; 机 menjadi bagian kata yang berkaitan dengan peluang atau keadaan, bukan nama mesin.'),
    ('机', '随机',
     '随机 berarti “sesuai situasi atau pragmatis”; 机 menjadi bagian kata yang bermakna kesempatan atau keadaan, bukan nama perangkat.'),
    ('机', '有机',
     '有机 berarti “organik”; 机 menjadi bagian kata dengan makna tersendiri, bukan akhiran nama mesin atau perangkat.'),
    ('品', '人品',
     '人品 berarti “karakter atau integritas seseorang”; 品 berarti kualitas moral, bukan akhiran nama barang atau produk.'),
    ('头', '摇头',
     '摇头 berarti “menggelengkan kepala”; 头 menjadi bagian dari ungkapan kerja, bukan akhiran pembentuk kata benda atau penanda posisi.'),
    ('头', '抬头',
     '抬头 berarti “mengangkat kepala” atau “melihat ke atas”; 头 menjadi bagian dari ungkapan kerja, bukan akhiran.'),
    ('头', '低头',
     '低头 berarti “menundukkan kepala” atau “menyerah”; 头 menjadi bagian dari ungkapan kerja, bukan akhiran.'),
    ('老', '老是',
     '老是 berarti “selalu”; 老 menjadi bagian kata keterangan, bukan awalan sebutan orang.'),
    ('老', '老实',
     '老实 berarti “jujur” atau “tulus”; 老 menjadi bagian kata sifat, bukan awalan sebutan sosial.'),
    ('老', '老远',
     '老远 berarti “sangat jauh”; 老 berfungsi sebagai penguat makna, bukan awalan sebutan sosial.'),
    ('老', '老实说',
     '老实说 berarti “terus terang” atau “sejujurnya”; 老 menjadi bagian kata sifat 老实, bukan awalan sebutan orang.'),
    ('老', '老虎',
     '老虎 berarti “harimau”; 老 merupakan bagian tetap dari nama hewan, bukan awalan sebutan orang.'),
    ('老', '老鼠',
     '老鼠 berarti “tikus”; 老 merupakan bagian tetap dari nama hewan, bukan awalan sebutan orang.'),
    ('可', '可谓',
     '可谓 berarti “dapat dikatakan”; 可 menyatakan kemungkinan dalam ungkapan kerja, bukan awalan pembentuk kata sifat.'),
    ('可', '可不是',
     '可不是 berarti “tepat” atau “memang”; 可 menjadi bagian ungkapan penegasan, bukan awalan pembentuk kata sifat.'),
    ('不', '不过',
     '不过 berarti “hanya” atau “semata-mata”; 不 merupakan bagian dari kata yang maknanya sudah menyatu, bukan penyangkalan yang berfungsi seperti awalan.'),
    ('无', '无论',
     '无论 berarti “apa pun” atau “terlepas dari apakah”; 无 merupakan bagian dari kata penghubung tetap, bukan awalan pembentuk kata yang menyatakan ketiadaan.'),
    ('反', '反正',
     '反正 berarti “bagaimanapun” atau “dalam hal apa pun”; 反 menjadi bagian dari kata keterangan tetap, bukan penanda penentangan atau arah berlawanan.'),
    ('总', '总算',
     '总算 berarti “akhirnya”; 总 menjadi bagian dari kata keterangan yang menyatakan hasil setelah proses, bukan penanda keseluruhan.'),
    ('自', '自从',
     '自从 berarti “sejak”; 自 menjadi bagian dari kata depan penanda waktu, bukan awalan bermakna diri sendiri.')
]


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


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true", help="terapkan perubahan (tanpa ini hanya melihat)")
    a = ap.parse_args()
    for p in (AFIKS, KATA):
        if not p.exists():
            print("Tidak menemukan %s" % p)
            return 1
    hasil = baca_json(AFIKS)
    if hasil is None:
        print("BERHENTI: format afiks_kamus.json tidak bisa ditulis ulang persis sama. Tidak ada yang diubah. Kirim pesan ini ke Claude.")
        return 1
    data, nl, akhir = hasil
    ada_kata = {w["simplified"] for w in json.loads(KATA.read_text(encoding="utf-8"))}
    entri = {e["karakter"]: i for i, e in enumerate(data)}

    rencana, sudah, galat = [], 0, []
    for af, kata, alasan in TABEL:
        if af not in entri:
            galat.append("%s: imbuhan tidak ditemukan" % af)
            continue
        e = data[entri[af]]
        if kata not in ada_kata:
            galat.append("%s %s: kata tidak ada di app_words.json" % (af, kata))
        elif not (kata.endswith(af) if e["posisi"] == "akhiran" else kata.startswith(af)):
            galat.append("%s %s: posisi imbuhan tidak sesuai (%s)" % (af, kata, e["posisi"]))
        elif kata in {c["kata"] for b in e["bagian"] for c in b["contoh"]}:
            galat.append("%s %s: kata ini adalah CONTOH imbuhan tersebut, bukan 'bukan'" % (af, kata))
        elif "bukan" not in alasan:
            galat.append("%s %s: alasan tidak memuat kata 'bukan'" % (af, kata))
        elif kata in {k["kata"] for k in e.get("bukan", [])}:
            sudah += 1
        else:
            rencana.append((af, kata, alasan))
    if galat:
        print("BERHENTI: ada isian yang tidak sesuai:")
        for g in galat:
            print("     " + g)
        print("Tidak ada yang diubah. Kirim pesan ini ke Claude.")
        return 1

    sebelum_total = sum(len(e.get("bukan", [])) for e in data)
    sebelum_imb = sum(1 for e in data if e.get("bukan"))
    sesudah = copy.deepcopy(data)
    for af, kata, alasan in rencana:
        sesudah[entri[af]]["bukan"].append({"kata": kata, "alasan": alasan})
    total2 = sum(len(e.get("bukan", [])) for e in sesudah)
    imb2 = sum(1 for e in sesudah if e.get("bukan"))

    print("=== Tambahan daftar 'bukan' imbuhan (data\\afiks_kamus.json) ===")
    print("Kata yang akan ditambahkan : %d  (sudah ada: %d)" % (len(rencana), sudah))
    print("Imbuhan yang punya 'bukan' : %d -> %d" % (sebelum_imb, imb2))
    print("Total kata 'bukan'         : %d -> %d" % (sebelum_total, total2))
    per = {}
    for af, kata, alasan in rencana:
        per.setdefault(af, []).append(kata)
    for af, ks in per.items():
        print("   %-3s (%s) %d + %d : %s" % (af, data[entri[af]]["posisi"], len(data[entri[af]].get("bukan", [])), len(ks), " ".join(ks)))

    baris = ["DAFTAR TAMBAHAN 'BUKAN' IMBUHAN -- %d kata" % len(rencana), ""]
    for af, kata, alasan in rencana:
        baris.append("%s | %s" % (af, kata))
        baris.append("   %s" % alasan)
    if not rencana:
        print("\nTidak ada yang perlu diubah.")
        return 0
    if not a.apply:
        HASIL.write_text("\r\n".join(baris) + "\r\n", encoding="utf-8-sig")
        print("\nIni baru ringkasan; belum ada yang diubah. Daftar lengkap: %s" % HASIL.name)
        print("Untuk menerapkan: python pasang_bukan_imbuhan.py --apply")
        return 0

    cap = datetime.now().strftime("%Y%m%d_%H%M%S")
    cad = AFIKS.with_name(AFIKS.name + ".bak_bukan_" + cap)
    shutil.copy2(AFIKS, cad)
    AFIKS.write_bytes(tulis_teks(sesudah, nl, akhir).encode("utf-8"))
    try:
        ulang = json.loads(AFIKS.read_bytes().decode("utf-8"))
        cocok = ulang == sesudah and sum(len(e.get("bukan", [])) for e in ulang) == total2
    except Exception:
        cocok = False
    if not cocok:
        shutil.copy2(cad, AFIKS)
        print("\nPEMERIKSAAN AKHIR GAGAL: berkas dikembalikan dari cadangan. Kirim pesan ini ke Claude.")
        return 1
    HASIL.write_text("\r\n".join(baris) + "\r\n", encoding="utf-8-sig")
    print("\nSelesai: %d kata 'bukan' ditambahkan." % len(rencana))
    print("Cadangan: %s" % cad.name)
    print("Pemeriksaan akhir lolos (hanya daftar 'bukan' yang bertambah; %d imbuhan utuh)." % len(ulang))
    print("Berkas yang perlu diunggah ke GitHub: data/afiks_kamus.json dan pasang_bukan_imbuhan.py")
    return 0


if __name__ == "__main__":
    sys.exit(main())

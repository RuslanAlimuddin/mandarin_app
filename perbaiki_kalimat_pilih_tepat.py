#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
perbaiki_kalimat_pilih_tepat.py -- 23 kalimat contoh yang membuat soal "Pilih yang Tepat" dilewati
=======================================================================================================
Butir 3 rencana BLUEPRINT_v47 (bagian 5). Keputusan رسلان (23 November 2026):
permainan "Pilih yang Tepat" (flashcard/flashcard-games.js) melewati soal bila kata target tidak
ada utuh di example_cn-nya sendiri. Ada 23 kasus dari 2.584 contoh (6 kata terpisah seperti 生气 dalam
"生我的气", 17 kalimat yang memakai kata lain). Semuanya ditulis ulang supaya kata target utuh.

Yang diubah (hanya data\\nuance_pairs.json, tiga isian per contoh, ditentukan oleh POSISI: id pasangan + kata):
   example_cn, example_pinyin, example_id
Tidak diubah: kata, hsk, collocations, register, dan semua isian lain.

CARA PAKAI (dari C:\\mandarin_app>):
  1) Lihat dulu (TIDAK mengubah apa pun):   python perbaiki_kalimat_pilih_tepat.py
  2) Terapkan:                              python perbaiki_kalimat_pilih_tepat.py --apply

KEAMANAN
  - Format berkas dijaga persis (JSON indent 2, ensure_ascii=False, akhir baris CRLF); skrip menolak bekerja
    bila format sekarang tidak bisa ditulis ulang persis sama.
  - Cadangan sebelum menulis: data\\nuance_pairs.json.bak_pilihtepat_<tanggal-jam>
  - Contoh hanya diubah bila isiannya SEKARANG persis sama dengan bentuk lama (atau sudah bentuk baru);
    bila ada yang lain, skrip berhenti dan tidak mengubah apa pun.
  - Setelah menulis, berkas dibaca ulang dan dibandingkan dengan yang diharapkan; bila tidak cocok,
    berkas dikembalikan dari cadangan. Pemeriksaan tambahan: jumlah contoh yang kata targetnya tidak ada di
    kalimatnya harus 0.
  - Aman diulang. Daftar lengkap: hasil_pilih_tepat.txt
"""
import argparse
import copy
import json
import shutil
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent
NUANCE = ROOT / "data" / "nuance_pairs.json"
HASIL = ROOT / "hasil_pilih_tepat.txt"

# (id pasangan, kata, (cn, pinyin, id) LAMA, (cn, pinyin, id) BARU)
PERUBAHAN = [
    ('shengqi_nanguo_01', '生气',
     ('妈妈生我的气了。', 'Māma shēng wǒ de qì le.', 'Ibu marah padaku.'),
     ('妈妈对我很生气。', 'Māma duì wǒ hěn shēngqì.', 'Ibu sangat marah padaku.')),
    ('b4_qing_jia_619', '请假',
     ('他今天生病了，所以请了一天假。', 'Tā jīntiān shēngbìng le, suǒyǐ qǐng le yì tiān jiǎ.', 'Dia sakit hari ini, jadi minta izin tidak masuk sehari.'),
     ('他今天生病了，所以请假一天。', 'Tā jīntiān shēngbìng le, suǒyǐ qǐngjià yì tiān.', 'Dia sakit hari ini, jadi minta izin sehari.')),
    ('b4_qing_jia_619', '休假',
     ('他下个月要休年假。', 'Tā xià ge yuè yào xiū niánjiǎ.', 'Dia bulan depan akan mengambil cuti tahunan.'),
     ('他下个月要休假一周。', 'Tā xià ge yuè yào xiūjià yì zhōu.', 'Dia bulan depan akan cuti seminggu.')),
    ('b7_salju_bersalju_2268', '下雪',
     ('昨天下了大雪。', 'Zuótiān xià le dà xuě.', 'Kemarin turun salju deras.'),
     ('昨天下雪了，雪很大。', 'Zuótiān xiàxuě le, xuě hěn dà.', 'Kemarin turun salju, saljunya deras.')),
    ('b8_minzu_guojia_3511', '国家',
     ('中国是一个大国。', 'Zhōngguó shì yíge dàguó.', 'Tiongkok adalah negara besar.'),
     ('中国是一个很大的国家。', 'Zhōngguó shì yí ge hěn dà de guójiā.', 'Tiongkok adalah negara yang sangat besar.')),
    ('b12_celana_bawahan_2455', '裤子',
     ('他穿了一条牛仔裤。', 'Tā chuān le yì tiáo niúzǎikù.', 'Dia memakai celana jeans.'),
     ('他穿了一条黑色的裤子。', 'Tā chuān le yì tiáo hēisè de kùzi.', 'Dia memakai celana hitam.')),
    ('b14_warna_corak_2687', '颜色',
     ('我喜欢蓝色。', 'Wǒ xǐhuan lánsè.', 'Saya suka warna biru.'),
     ('我喜欢这个颜色。', 'Wǒ xǐhuan zhè ge yánsè.', 'Saya suka warna ini.')),
    ('b14_shuzi_shujv_3544', '数字',
     ('请写下你的电话号码。', 'Qǐng xiěxià nǐ de diànhuà hàomǎ.', 'Tolong tulis nomor teleponmu.'),
     ('请把这个数字写在这里。', 'Qǐng bǎ zhè ge shùzì xiě zài zhèlǐ.', 'Tolong tulis angka ini di sini.')),
    ('b15_zhuanbian_zhuanyi_3295', '转变',
     ('他最近改变了很多想法。', 'Tā zuìjìn gǎibiàn le hěnduō xiǎngfǎ.', 'Dia baru-baru ini mengubah banyak pikirannya.'),
     ('他的态度最近转变了很多。', 'Tā de tàidu zuìjìn zhuǎnbiàn le hěn duō.', 'Sikapnya belakangan ini banyak berubah.')),
    ('b17_yin_yue_145', '歌曲',
     ('这首歌很好听。', 'Zhè shǒu gē hěn hǎotīng.', 'Lagu ini enak didengar.'),
     ('这首歌曲很好听。', 'Zhè shǒu gēqǔ hěn hǎotīng.', 'Lagu ini enak didengar.')),
    ('b21_ji_jie_209', '季节',
     ('雨季到了。', 'Yǔjì dào le.', 'Musim hujan tiba.'),
     ('你最喜欢哪个季节？', 'Nǐ zuì xǐhuan nǎ ge jìjié?', 'Kamu paling suka musim apa?')),
    ('b25_bi_mian_257', '避免',
     ('为了不迟到，我提前出门了。', 'Wèile bù chídào, wǒ tíqián chūmén le.', 'Untuk menghindari terlambat, saya keluar lebih awal.'),
     ('为了避免迟到，我提前出门了。', 'Wèile bìmiǎn chídào, wǒ tíqián chūmén le.', 'Untuk menghindari terlambat, saya keluar lebih awal.')),
    ('b26_dan_xiao_537', '胆小',
     ('他胆子小，不敢一个人去。', 'Tā dǎnzi xiǎo, bù gǎn yí ge rén qù.', 'Dia penakut, tidak berani pergi sendiri.'),
     ('他很胆小，不敢一个人去。', 'Tā hěn dǎnxiǎo, bù gǎn yí ge rén qù.', 'Dia penakut, tidak berani pergi sendiri.')),
    ('b27_xueke_kemu_3059', '学科',
     ('他在大学里选择了文科。', 'Tā zài dàxué li xuǎnzé le wénkē.', 'Dia memilih humaniora di universitas.'),
     ('他最喜欢的学科是数学。', 'Tā zuì xǐhuan de xuékē shì shùxué.', 'Bidang studi yang paling dia sukai adalah matematika.')),
    ('b28_huobi_zhuanqian_3054', '赚钱',
     ('他想多赚点钱。', 'Tā xiǎng duō zhuàn diǎn qián.', 'Dia ingin mencari lebih banyak uang.'),
     ('他想多赚钱。', 'Tā xiǎng duō zhuànqián.', 'Dia ingin lebih banyak mencari uang.')),
    ('b29_hidung_mulut_2768', '口',
     ('他张开嘴巴说话。', 'Tā zhāngkāi zuǐba shuōhuà.', 'Dia membuka mulut untuk bicara.'),
     ('他张开口，却说不出话来。', 'Tā zhāngkāi kǒu, què shuō bù chū huà lái.', 'Dia membuka mulut, tetapi tidak bisa bicara.')),
    ('b30_suara_nada_2689', '声响',
     ('突然传来一声巨响。', 'Tūrán chuánlái yì shēng jùxiǎng.', 'Tiba-tiba terdengar bunyi keras yang besar.'),
     ('突然传来一阵声响。', 'Tūrán chuánlái yí zhèn shēngxiǎng.', 'Tiba-tiba terdengar bunyi keras.')),
    ('b30_bi_li_591', '比率',
     ('失业率在上升。', 'Shīyè lǜ zài shàngshēng.', 'Tingkat pengangguran sedang naik.'),
     ('失业的比率在上升。', 'Shīyè de bǐlǜ zài shàngshēng.', 'Rasio pengangguran sedang naik.')),
    ('b32_tas_tas_2464', '背包',
     ('学生背着书包上学。', 'Xuésheng bēi zhe shūbāo shàngxué.', 'Siswa membawa ransel ke sekolah.'),
     ('他背着一个大背包去旅行。', 'Tā bēi zhe yí ge dà bēibāo qù lǚxíng.', 'Dia menggendong ransel besar untuk bepergian.')),
    ('b34_mempercepat_memperlambat_1876', '缓',
     ('放慢脚步。', 'Fàngmàn jiǎobù.', 'Perlambat langkah.'),
     ('放缓脚步。', 'Fànghuǎn jiǎobù.', 'Perlambat langkah.')),
    ('b36_murah_mahal_1733', '廉',
     ('这里的物价很便宜实惠。', 'Zhèlǐ de wùjià hěn piányi shíhuì.', 'Harga di sini sangat murah dan terjangkau.'),
     ('这里的物价很低廉。', 'Zhèlǐ de wùjià hěn dīlián.', 'Harga di sini sangat murah.')),
    ('b36_takut_khawatir_1778', '虑',
     ('他担心未来的发展。', 'Tā dānxīn wèilái de fāzhǎn.', 'Dia khawatir tentang perkembangan masa depan.'),
     ('他很忧虑未来的发展。', 'Tā hěn yōulǜ wèilái de fāzhǎn.', 'Dia sangat khawatir akan perkembangan masa depan.')),
    ('bA1_427', '强大',
     ('中国已经成为世界经济强国。', 'Zhōngguó yǐjīng chéngwéi shìjiè jīngjì qiángguó.', 'China telah menjadi kekuatan ekonomi dunia.'),
     ('中国的经济越来越强大。', 'Zhōngguó de jīngjì yuèláiyuè qiángdà.', 'Ekonomi Tiongkok semakin kuat.'))
]


def tulis_teks(data, akhir):
    return json.dumps(data, ensure_ascii=False, indent=2).replace("\n", "\r\n") + akhir


def baca_json(path):
    mentah = path.read_bytes().decode("utf-8")
    akhir = "\r\n" if mentah.endswith("\r\n") else ("\n" if mentah.endswith("\n") else "")
    data = json.loads(mentah)
    if tulis_teks(data, akhir) != mentah:
        return None, None
    return data, akhir


def hitung_terlewat(data):
    return sum(1 for p in data["pairs"] for c in p["comparison"] if c["word"] not in c.get("example_cn", ""))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true", help="terapkan perubahan (tanpa ini hanya melihat)")
    a = ap.parse_args()
    if not NUANCE.exists():
        print("Tidak menemukan %s" % NUANCE)
        return 1
    data, akhir = baca_json(NUANCE)
    if data is None:
        print("BERHENTI: format nuance_pairs.json tidak bisa ditulis ulang persis sama. Tidak ada yang diubah. Kirim pesan ini ke Claude.")
        return 1

    indeks = {}
    for pi, p in enumerate(data["pairs"]):
        for ci, c in enumerate(p["comparison"]):
            indeks[(p["id"], c["word"])] = (pi, ci)

    rencana, sudah, galat = [], 0, []
    for pid, kata, lama, baru in PERUBAHAN:
        if baru[0].find(kata) < 0:
            galat.append("%s %s: kalimat baru tidak memuat kata targetnya" % (pid, kata))
            continue
        if (pid, kata) not in indeks:
            galat.append("%s %s: pasangan/kata tidak ditemukan" % (pid, kata))
            continue
        pi, ci = indeks[(pid, kata)]
        c = data["pairs"][pi]["comparison"][ci]
        sekarang = (c.get("example_cn"), c.get("example_pinyin"), c.get("example_id"))
        if sekarang == baru:
            sudah += 1
        elif sekarang == lama:
            rencana.append((pi, ci, pid, kata, lama, baru))
        else:
            galat.append("%s %s: isinya sekarang %r, bukan bentuk lama maupun baru" % (pid, kata, sekarang))
    if galat:
        print("BERHENTI: isian tidak seperti yang diharapkan:")
        for g in galat:
            print("     " + g)
        print("Tidak ada yang diubah. Kirim pesan ini ke Claude.")
        return 1

    terlewat_sekarang = hitung_terlewat(data)
    print("=== data\\nuance_pairs.json: kalimat contoh untuk soal \"Pilih yang Tepat\" ===")
    print("Contoh yang akan ditulis ulang : %d  (sudah baru: %d)" % (len(rencana), sudah))
    print("Contoh yang kata targetnya tidak ada di kalimatnya: sekarang %d" % terlewat_sekarang)
    for pi, ci, pid, kata, lama, baru in rencana:
        print("   %-4s %s  ->  %s" % (kata, lama[0], baru[0]))
        print("        %s  ->  %s" % (lama[1], baru[1]))

    baris = ["DAFTAR PERUBAHAN KALIMAT 'PILIH YANG TEPAT' -- %d contoh" % len(rencana), ""]
    for pi, ci, pid, kata, lama, baru in rencana:
        baris += ["%s / %s" % (pid, kata), "   cn   lama: %s" % lama[0], "   cn   baru: %s" % baru[0],
                  "   pny  lama: %s" % lama[1], "   pny  baru: %s" % baru[1],
                  "   id   lama: %s" % lama[2], "   id   baru: %s" % baru[2]]
    if not rencana:
        print("\nTidak ada yang perlu diubah.")
        return 0
    if not a.apply:
        HASIL.write_text("\r\n".join(baris) + "\r\n", encoding="utf-8-sig")
        print("\nIni baru ringkasan; belum ada yang diubah. Daftar lengkap: %s" % HASIL.name)
        print("Untuk menerapkan: python perbaiki_kalimat_pilih_tepat.py --apply")
        return 0

    cap = datetime.now().strftime("%Y%m%d_%H%M%S")
    cad = NUANCE.with_name(NUANCE.name + ".bak_pilihtepat_" + cap)
    shutil.copy2(NUANCE, cad)
    asli = copy.deepcopy(data)
    harapan = copy.deepcopy(asli)
    for pi, ci, pid, kata, lama, baru in rencana:
        for dst in (data, harapan):
            c = dst["pairs"][pi]["comparison"][ci]
            c["example_cn"], c["example_pinyin"], c["example_id"] = baru
    NUANCE.write_bytes(tulis_teks(data, akhir).encode("utf-8"))
    try:
        ulang = json.loads(NUANCE.read_bytes().decode("utf-8"))
        cocok = ulang == harapan and hitung_terlewat(ulang) == 0
    except Exception:
        cocok = False
    if not cocok:
        shutil.copy2(cad, NUANCE)
        print("\nPEMERIKSAAN AKHIR GAGAL: berkas dikembalikan dari cadangan. Kirim pesan ini ke Claude.")
        return 1
    HASIL.write_text("\r\n".join(baris) + "\r\n", encoding="utf-8-sig")
    print("\nSelesai: %d contoh ditulis ulang." % len(rencana))
    print("Cadangan: %s" % cad.name)
    print("Pemeriksaan akhir lolos (hanya isian yang direncanakan berubah; contoh yang dilewati permainan: 0).")
    print("Berkas yang perlu diunggah: data/nuance_pairs.json dan perbaiki_kalimat_pilih_tepat.py")
    return 0


if __name__ == "__main__":
    sys.exit(main())

# BLUEPRINT v46 — Mandarin Interaktif

Lanjutan dari BLUEPRINT v44. Sesi ini (19–20 November 2026) menyelesaikan **butir 1, 2, dan 3 rencana v44 bagian 5**:
seluruh **2.584 contoh pinyin** di `data/nuance_pairs.json` kini bernada dan **seragam menurut satu aturan** (lihat bagian 3).
(`BLUEPRINT_v45.md` sempat disusun di tengah sesi tetapi tidak diunggah; isinya yang masih berlaku sudah tergabung di v46, jadi v45 tidak diperlukan.)

**v46 ringkas.** Untuk hal lama baca `BLUEPRINT_v44.md` (varian radikal, beres-beres cadangan, 11 perbaikan `nuance_pairs.json`, format erhua 儿, kapital pinyin)
dan `BLUEPRINT_v43.md` (Paket Pembentukan Kata, aturan kerja lengkap). Bagian 5 v44 **digantikan** oleh bagian 5 di bawah.

---

## 1. Aturan kerja (v43 dan v44 tetap berlaku; tambahan sesi ini)

- Semua aturan v43 bagian 1 dan v44 bagian 1 tetap: diskusi dulu untuk pekerjaan yang menghasilkan kode atau berkas; bahasa sederhana; sebutkan ulang isi dan jumlah poin
  saat merujuk; **instruksi uji dengan jalur klik lengkap**; pola skrip (lihat-dulu dan `--apply`, cadangan, pemeriksaan akhir, aman diulang).
- **Pola kerja pekerjaan data besar (terbukti di sesi ini)**: (1) Claude membuat skrip **lihat-dulu** yang hanya membuat laporan; (2) رسلان memutuskan per golongan; (3) skrip penerapan dibuat;
  (4) bila perlu, dikerjakan **bertahap** (satu jenis perubahan per skrip, tiap tahap diuji di aplikasi sebelum tahap berikutnya).
- Claude **menguji skrip di salinan repo yang bersih** sebelum diserahkan, termasuk memeriksa lewat `git diff` bahwa **hanya isian yang disetujui** yang berubah
  (angka baris berubah sama dengan jumlah perubahan, tidak ada baris lain) dan bahwa menjalankan ulang menjawab "tidak ada yang perlu diubah".
- Claude **memvalidasi metode pada data yang sudah benar** sebelum memakainya pada data baru (di sesi ini: metode pemberi nada dijalankan pada 1.868 contoh lama bernada).
- **Setelah tiap pengunggahan, Claude menarik ulang repo dan memeriksa bahwa yang terunggah benar-benar berkas data di `data/`**. Pada sesi ini sekali data terunggah ke akar repo
  (`nuance_pairs.json`), bukan ke `data/`, sehingga repo sempat tertinggal satu tahap.
- Skrip pengaman membuat cadangan `data\nuance_pairs.json.bak_<tahap>_<tanggal-jam>` (tidak diunggah ke repo; repo belum punya `.gitignore`, jadi berhati-hatilah saat mengunggah folder `data`).

## 2. Selesai sesi ini (19–20 November 2026)

| Butir | Hasil | Skrip |
|---|---|---|
| 1. 716 contoh pinyin tanpa nada | Semua diberi tanda nada: **444 golongan A** (bacaan pasti), **158 B1** (karakter berbacaan ganda yang diselesaikan aturan sederhana), **114 B2** (usulan disetujui رسلان). Hanya isian `example_pinyin` yang berubah (716 baris). 湖泊: "hubo" → **húpō** | `daftar_nada_nuance.py` (usulan), `terapkan_nada_nuance.py` (penerapan) |
| 2. Penulisan ü bercampur | Ikut selesai: ü bertanda nada (nǚhái, lǚxíng, lǜshī), bukan "nv/lv/lu" | sama |
| 3. Nada pada 1.868 contoh lama — tahap 1 | **8 salah nada** diperbaiki: 成绩 chéngjī→**chéngjì** (2 contoh), 别忘 biè→**bié**, 高涨 gāozhàng→**gāozhǎng**, 痕迹 hénjī→**hénjì**, 供应 gòngyìng→**gōngyìng**, 为人 wèirén→**wéirén**, 突然 Túrán→**Tūrán** (pilihan Daratan) | `perbaiki_nada_lama.py` |
| tahap 2 | **一**: 202 contoh disamakan dengan nada sebenarnya (yī→yí 119 kali, yī→yì 84 kali); yī tetap pada 十一, 第一 | `samakan_yi_nuance.py` |
| tahap 3 | **个** penggolong: 75 contoh gè→**ge** (254 sudah ge; 个人/个性/个子 dan 整个 tetap gè) | `samakan_ge_nuance.py` |
| tahap 4 | **Nada netral**: 109 contoh (114 kemunculan) mengikuti bacaan terkurasi (喜欢 xǐhuan, 学生 xuésheng, 起来 qǐlai, 太阳 tàiyang, 眼睛 yǎnjing, 关系 guānxi, 早上 zǎoshang) | `samakan_netral_nuance.py` |

Semua tahap diuji رسلان di aplikasi (jalur: lihat bagian 6) dan lolos. **Verifikasi akhir (Claude, 20 November 2026)** pada `data/nuance_pairs.json` di repo: 2.584 dari 2.584 contoh bernada;
skrip tahap 2, 3, 4, dan `terapkan_nada_nuance.py` pada mode lihat-dulu semuanya menjawab "tidak ada yang perlu diubah".
Catatan: `perbaiki_nada_lama.py` **tidak bisa dijalankan ulang** (satu perbaikan, 声响 "Tūrán…", sudah dimodifikasi tahap 2 sehingga pelindung "isi sekarang harus sama persis" menghentikannya); skrip itu sekali pakai.

## 3. Catatan penting untuk sesi berikutnya

**Aturan penulisan nada final (berlaku untuk seluruh 2.584 contoh):**
- **Bacaan tiga lapis**: (1) bacaan terkurasi `app_words.json` dulu; (2) karakter berbacaan ganda yang bergantung konteks **tidak ditebak** (golongan B); (3) CC-CEDICT hanya bila bacaannya tunggal.
- **Nada 3-3 ditulis nada asli seperti kamus** (nǐ hǎo, bukan ní hǎo). **不 tetap bù** (tidak menjadi bú).
- **一 mengikuti perubahan nada sebenarnya**: yī bila sendiri, angka/urutan (十一, 第一, 一月/号/日), akhir kalimat, atau sebelum angka; **yí sebelum nada 4** (termasuk 个 netral: yí ge);
  **yì sebelum nada 1, 2, 3**. Skrip tahap 2 punya **penjaga** yang berhenti bila ada pola khusus yang aturannya berbeda: 星期一/周一/礼拜一, kata berakhiran 一 (统一 唯一 之一 同一 单一 专一), pola ulang 看一看 (一 netral). Pola itu tidak ada di data saat ini.
- **Nada netral mengikuti bacaan terkurasi** (xǐhuan, zǎoshang, xuésheng, tàiyang; kecuali 里, lihat di bawah). **个 penggolong selalu netral "ge"** (zhè ge, yí ge, jǐ ge rén, xià ge yuè);
  个人/个性/个子 (个 di awal kata) tetap gè; **整个 tetap zhěnggè** (kata tersendiri).
- **Pengecualian 里**: data menulis 里 nada penuh **lǐ** hampir di semua tempat (**96** tempat: 里, 这里, 那里, 哪里, 村里, 里面, 手里, 里头, 卡路里) dan hanya **5** tempat netral "li"
  (森林里, 房间里充满了日光, 这里 ×2, 夜里). Kamus terkurasi sendiri tidak konsisten (这里 "zhè lǐ", 哪里 "nǎ lǐ", tetapi 那里 "nà li"), jadi **那里 tetap nàlǐ**. 道理/有道理 (里 di situ adalah 理) tetap netral: dàoli.
- Huruf, huruf kapital, spasi, apostrof (Tiān'ānmén, dá'àn), dan tanda baca tulisan lama dipertahankan; yang berubah hanya tanda nada. Susunan spasi yang tersambung di data lama (yíge, zhège) **tidak diseragamkan**.

**Data lama yang sengaja TIDAK diubah karena data lama yang benar (hasil tahap 4, dilaporkan saja):**
- **Arah kebalikan, 15 kemunculan** (data lama netral, kamus terkurasi nada penuh): 能不能 bu, 早晨 zǎochen, 木匠 mùjiang, 房子 fángzi, 精神 jīngshen ("bersemangat"), 玫瑰/玫瑰花 méigui, 冷清 lěngqing, 想想 xiǎngxiang, 哦 o.
  Ini calon pembenahan **kamus terkurasi**, bukan data contoh (lihat bagian 5, butir 1).
- **Selisih nada sungguhan, 16 kemunculan**: 只 zhī (一只猫), 种 zhòng (种花), 倒 dǎo, 数 shǔ, 扇 shān, 当 dàng (正当), 搂 lǒu, 载 zài (下载 xiàzài), 空 kòng (空缺), 少 shào (空少), 连襟 lián, 干 gàn (树干).
- **7 contoh dilewati** karena pinyin tidak bisa disejajarkan dengan hanzi oleh pemecah kata: 系好/系鞋带 (jì), 建校纪念日 (jìniànrì), 前程似锦 (sìjǐn), 口风很紧 (jǐn), 宽松的T恤 (T-xù). Tidak ada yang perlu diubah di sana.

**Cara kerja skrip (`daftar_nada_nuance.py`, dipakai oleh semua skrip lain; jangan dihapus):**
- Kalimat dipecah menjadi kata dengan **pemrograman dinamis** (bukan "kata terpanjang dulu"): kata terkurasi lebih disukai daripada kata CC-CEDICT (biaya 1,0 lawan 1,3);
  kata nama diri (pinyin berkapital) lebih disukai bila pinyin lama memuat huruf kapital di tengah kalimat (agar 看中国 tidak menjadi 看中+国). Kata CC-CEDICT multi-karakter
  yang memuat karakter berisiko atau 的 (到了, 美的, 中的) ditolak, kecuali pada percobaan "longgar" saat huruf tak cocok. Suku kata yang tertulis menyambung (zhízi, hǎole) dipecah otomatis.
  Skrip tahap 3 dan 4 menambah langkah **toleran**: bila huruf tak cocok, mencoba bacaan lain untuk karakter berbacaan ganda yang berdiri sendiri (mis. 都 dū di 文化之都).
- **Karakter berisiko** (selalu golongan B bila dipakai sebagai karakter tunggal): 了 好 行 都 重 为 地 间 发 种 教 应 会 当 只 长 得 还 着 没 假 数 少 觉 乐 便 相 调 传 倒 扇 载 涨 别 差 降 干 空 难
  处 模 背 将 弹 单 号 片 率 度 量 参 切 称 角 结 夹 省 属 宿 朝 吓 薄. **B1 (yakin)**: 了=le bila bukan sesudah 不/得; 好=hǎo bila tidak sebelum 学客奇动胜色; 都=dōu; 会=huì (berdiri sendiri).
- **Kelemahan yang diketahui**: aturan "个 sesudah 整 menjadi ge" ada di `daftar_nada_nuance.py` (fungsi `suku_kata_per_karakter`/`koreksi_ge`), tetapi skrip tahap 3 mengecualikan 整个. Bila `daftar_nada_nuance.py` dipakai untuk data baru, periksa 整个 secara manual.
  `daftar_nada_nuance.py` menulis `laporan_nada_nuance.txt` dan `usulan_nada_nuance.json` di akar repo setiap dijalankan.

**Validasi awal sesi (1.868 contoh lama bernada, bahan keputusan butir 3):** 1.477 sama persis; selisihnya 一 (201), 个 (75), nada netral (127), nada berbeda sungguhan (24: 16 data lama yang benar, 8 calon perbaikan yang kemudian diperbaiki di tahap 1).
Pelajaran: data lama **sangat baik** (kesalahan nada sungguhan ±8 dari 1.868), jadi pekerjaan terbesar adalah **keseragaman konvensi**, bukan pembetulan.

## 4. Berkas di repo (ringkas)

- **Dipakai terus**: `daftar_nada_nuance.py` (jangan dihapus; dipakai semua skrip tahap), `data/nuance_pairs.json` (sudah bernada dan seragam).
- **Skrip sekali pakai, sudah dijalankan** (boleh disimpan sebagai catatan atau dihapus): `terapkan_nada_nuance.py`, `perbaiki_nada_lama.py`, `samakan_yi_nuance.py`, `samakan_ge_nuance.py`, `samakan_netral_nuance.py`.
- **Keluaran sekali pakai** (boleh dihapus dari repo): `laporan_nada_nuance.txt`, `usulan_nada_nuance.json`, `hasil_nada_nuance.txt`. (Berkas `hasil_yi_nuance.txt`, `hasil_ge_nuance.txt`, `hasil_netral_nuance.txt` hanya ada di komputer رسلان.)
- **Perlu dihapus**: **`nuance_pairs.json` di akar repo** (salinan lama sebelum tahap 4; aplikasi hanya memakai `data/nuance_pairs.json`). Cara: GitHub → repo `mandarin_app` → buka berkas `nuance_pairs.json` di akar (bukan di folder `data`) → ikon tempat sampah (Delete file) → Commit changes.
- **Tidak diunggah**: berkas `.bak_*` (termasuk `nuance_pairs.json.bak_nada_*`, `_nadalama_`, `_yi_`, `_ge_`, `_netral_`) dan folder `__pycache__`. Repo belum punya `.gitignore`.

## 5. Rencana ke depan (belum diputuskan; pilih saat sesi berikutnya)

1. **Dua keputusan kecil soal 里 dan kamus terkurasi** (disetujui رسلان untuk dibahas di sesi ini, belum diputuskan):
   (a) apakah **5 tempat 里 netral "li"** (森林里, 房间里, 这里 ×2, 夜里) diseragamkan menjadi **lǐ** seperti 96 tempat lain (saran: ya, perubahan kecil, satu skrip singkat);
   (b) apakah **`app_words.json` dirapikan**: 里 (这里 "zhè lǐ", 哪里 "nǎ lǐ", 那里 "nà li" tidak konsisten) dan calon nada netral baku yang kamus tulis penuh (木匠 mùjiàng→mùjiang, 早晨 zǎochén→zǎochen,
   玫瑰 méiguī→méigui, 冷清 lěngqīng→lěngqing, 精神 sebagai kata sifat jīngshen, 能不能 néng bù néng→néng bu néng). Perubahan ini ke **kamus**, jadi memengaruhi seluruh aplikasi (kartu, kuis, daftar kata), perlu dibahas dulu.
2. **Bersih-bersih repo**: hapus `nuance_pairs.json` di akar; pertimbangkan membuat `.gitignore` berisi `*.bak_*` dan `__pycache__/` agar cadangan tidak ikut terunggah; putuskan nasib skrip/keluaran sekali pakai (bagian 4).
3. **22 soal "Pilih yang Tepat" yang dilewati** (lihat v44 bagian 3): tinjau apakah kalimatnya perlu disesuaikan. (Dulu butir 4 v44.)
4. **Penyegaran `tone_drills.json`** lewat `skrip/dari_py/generate_tone_drills.py` (±36 grup dan ±239 butir tertinggal). **Jangan meregenerasi `wb_pools.json`** (dikurasi manual). (Dulu butir 5 v44.)
5. **Pelajaran Pilar 3 (量词)** yang asli, lewat GPT dengan pesan serah terima. (Dulu butir 6 v44.) Catatan: penggolong 个 kini selalu netral "ge" di contoh; sesuaikan bila pelajaran memuatnya.
6. **Tingkat 3 awalan/akhiran** (族 迷 热 控 症 剂 炎 盲, penunjuk posisi 上 下 里 外 中 间, 边) dan **latihan awalan/akhiran** (Flashcard, Word Builder, Ujian HSK). (Dulu butir 7 v44.)
7. **Tautan varian ⺮ 攵 罒** ke tombol 竹 攴 网 yang sudah ada (opsional, kecil). (Dulu butir 8 v44.)
8. Backlog aktif lama tidak berubah (lihat catatan proyek dan v41/v42): pasangan penggolong + rantai kata kerja, 多音字, dikte, dashboard gabungan, skema kata 3+ karakter (1.287 kata), dan seterusnya.

## 6. Cara membuka aplikasi dan cara kerja repo

Tidak berubah dari v42 bagian 8, v43 bagian 6, dan v44 bagian 6. Ringkas: aplikasi dibuka lewat server lokal (Live Server) dari `C:\mandarin_app`; Claude membaca repo
https://github.com/RuslanAlimuddin/mandarin_app (folder `blueprint/` untuk BLUEPRINT terbaru); hasil skrip/berkas baru diberikan lewat percakapan dan رسلان yang mengunggahnya.
Jalur ke contoh nuansa di aplikasi: **Kamus → kolom "Cari hanzi, pinyin, atau arti Indonesia…" → ketik kata → klik hasilnya → gulir ke panel "🆚 Beda dengan Kata Mirip"**
(setelah mengubah data, tekan Ctrl+F5 agar data baru terbaca).
Contoh uji yang dipakai di sesi ini (kata → contoh yang harus tampil): 旅行 → Wǒ jīngcháng qù guówài lǚxíng.; 湖泊 → Zhèlǐ yǒu xǔduō měilì de húpō.; 高涨 → Qiúmí de rèqíng kōngqián gāozhǎng.;
尝 → Nǐ cháng yíxià zhège tāng, hǎohē ma?; 非常 → Tā shì yíge fēicháng cōngmíng de xuéshēng.; 整个 → Zhěnggè chéngshì dōu bèi xuě fùgài le.; 喜欢 → Wǒ xǐhuan tīng yīnyuè.; 那里 → Nàlǐ yǒu yí zuò shān.

## Ringkasan status proyek

- Paket Pembentukan Kata, pembersihan bacaan dan data (v43), varian radikal, beres-beres cadangan, 11 perbaikan nuansa (v44): **selesai**.
- Sesi 19–20 November: **seluruh contoh pinyin nuansa (2.584) bernada dan seragam**, ü bercampur selesai, 8 salah nada diperbaiki: **selesai, teruji di aplikasi, terunggah**.
- Berikutnya: dua keputusan kecil (里 dan kamus terkurasi), bersih-bersih repo, lalu pilih dari bagian 5 menurut minat رسلان.

## 7. Pesan pembuka siap pakai untuk percakapan baru

Salin, lalu ganti bagian dalam tanda kurung siku:

```
Lanjutkan proyek Mandarin Interaktif. Tarik ulang repo
(https://github.com/RuslanAlimuddin/mandarin_app) dan baca
`blueprint/BLUEPRINT_v46.md` (bagian 1 tentang aturan kerja dan bagian 5 tentang rencana).
Butir yang ingin saya kerjakan: [nomor atau nama butir dari bagian 5].
Seperti biasa: diskusi dulu sebelum membuat kode atau berkas, instruksi uji dengan
jalur klik lengkap, dan tarik ulang repo sendiri.
```

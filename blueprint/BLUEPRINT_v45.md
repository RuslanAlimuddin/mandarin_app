# BLUEPRINT v45 — Mandarin Interaktif

Lanjutan dari BLUEPRINT v44. Sesi ini (19 November 2026) menyelesaikan **butir 1 dan butir 2 rencana v44 bagian 5**: 716 contoh pinyin di
`data/nuance_pairs.json` yang tanpa tanda nada kini **semuanya bernada**, dan penulisan ü yang bercampur (nv, lv, nu, lu) ikut terselesaikan.
Skrip sudah dijalankan رسلان di PC dan diuji di aplikasi (tiga uji lolos).

**v45 ringkas.** Untuk hal lama baca `BLUEPRINT_v44.md` (varian radikal, beres-beres cadangan, 11 perbaikan `nuance_pairs.json`, format erhua 儿, kapital pinyin)
dan `BLUEPRINT_v43.md` (Paket Pembentukan Kata, aturan kerja lengkap). Bagian 5 v44 **digantikan** oleh bagian 5 di bawah.

---

## 1. Aturan kerja (v43 dan v44 tetap berlaku; tambahan sesi ini)

- Semua aturan v43 bagian 1 dan v44 bagian 1 tetap: diskusi dulu untuk pekerjaan yang menghasilkan kode atau berkas; bahasa sederhana; sebutkan ulang isi dan jumlah poin
  saat merujuk; **instruksi uji dengan jalur klik lengkap**; pola skrip (lihat-dulu dan `--apply`, cadangan, pemeriksaan akhir, aman diulang).
- **Tambahan pola kerja**: untuk pekerjaan data yang besar, Claude lebih dulu membuat skrip **lihat-dulu** yang hanya membuat laporan, lalu رسلان memutuskan per golongan,
  baru skrip penerapan dibuat. Claude menguji skrip di salinan repo yang bersih sebelum diserahkan, termasuk memeriksa lewat `git diff` bahwa hanya isian yang disetujui yang berubah.
- Claude **memvalidasi metode pada data yang sudah benar** sebelum memakainya pada data baru (di sesi ini: metode pemberi nada dijalankan pada 1.868 contoh lama bernada).
- Tarik ulang repo setelah pengunggahan: pada saat v45 disusun, `data/nuance_pairs.json` di GitHub **masih berisi 716 contoh tanpa nada** (skrip dan laporan sudah terunggah,
  datanya belum). Langkah pertama sesi berikutnya: tarik ulang repo dan pastikan data yang bernada sudah terunggah.

## 2. Selesai sesi ini (19 November 2026)

| Butir | Hasil | Berkas/skrip |
|---|---|---|
| 1. 716 contoh pinyin tanpa nada di `nuance_pairs.json` | Semua diberi tanda nada: **444 golongan A** (bacaan pasti), **158 B1** (karakter berbacaan ganda yang diselesaikan aturan sederhana), **114 B2** (karakter berbacaan ganda yang usulannya disetujui رسلان). Yang berubah hanya isian `example_pinyin` (tepat 716 baris menurut `git diff`); hanzi, terjemahan, dan isian lain tidak disentuh. Sesudahnya 0 contoh tanpa tanda nada. Uji di aplikasi lolos: 旅行 (ü), 湖泊, 一/个 | `daftar_nada_nuance.py` (usulan, lihat-dulu), `terapkan_nada_nuance.py` (penerapan), `data/nuance_pairs.json` |
| 2. Penulisan ü bercampur | Ikut terselesaikan: contoh bernada baru memakai ü bertanda nada (nǚhái, lǚxíng, lǜshī), bukan "nv/lv/lu" | sama dengan di atas |
| 湖泊 | Tulisan lama "hubo" (salah eja) diperbaiki menjadi **húpō** (satu-satunya contoh yang hurufnya ikut berubah; id `b34_jiang_hu_373`) | `terapkan_nada_nuance.py` (tabel `KOREKSI_HURUF`) |

## 3. Catatan penting untuk sesi berikutnya

**Aturan penulisan nada yang disepakati (berlaku untuk 716 contoh baru):**
- **Bacaan tiga lapis**: (1) bacaan terkurasi `app_words.json` dulu; (2) karakter berbacaan ganda yang bergantung konteks **tidak ditebak** (golongan B); (3) CC-CEDICT hanya bila bacaannya tunggal.
- **Nada 3-3 ditulis nada asli seperti kamus** (nǐ hǎo, bukan ní hǎo). **不 tetap bù** (tidak menjadi bú).
- **一 mengikuti perubahan nada sebenarnya**: yī bila sendiri, angka/urutan (十一, 第一, 一月/号/日), akhir kalimat, atau sebelum angka; **yí sebelum nada 4** (termasuk 个 netral: yí ge);
  **yì sebelum nada 1, 2, 3**; sebelum suku kata netral lain tetap yī dan ditandai B2.
- **Nada netral mengikuti bacaan terkurasi** (xǐhuan, nàli, qǐlai, zǎochen, shang pada 早上). **个 penggolong selalu netral "ge"** (zhè ge, yí ge, jǐ ge rén);
  个人/个子/个性 (个 di awal kata) tetap gè. Ini keputusan Claude saat uji, dilaporkan ke رسلان.
- Huruf, huruf kapital, spasi, apostrof (Tiān'ānmén, dá'àn), dan tanda baca tulisan lama dipertahankan; yang bertambah hanya tanda nada.

**Cara kerja skrip (`daftar_nada_nuance.py`, dipakai juga oleh `terapkan_nada_nuance.py`):**
- Kalimat dipecah menjadi kata dengan **pemrograman dinamis** (bukan "kata terpanjang dulu"): kata terkurasi lebih disukai daripada kata CC-CEDICT (biaya 1,0 lawan 1,3);
  kata nama diri (pinyin berkapital) lebih disukai bila pinyin lama memuat huruf kapital di tengah kalimat (agar 看中国 tidak menjadi 看中+国). Kata CC-CEDICT multi-karakter
  yang memuat karakter berisiko atau 的 (到了, 美的, 中的) ditolak, kecuali pada percobaan "longgar" saat huruf tak cocok. Suku kata yang tertulis menyambung di data (zhízi, hǎole) dipecah otomatis.
- **Karakter berisiko** (selalu golongan B bila dipakai sebagai karakter tunggal): 了 好 行 都 重 为 地 间 发 种 教 应 会 当 只 长 得 还 着 没 假 数 少 觉 乐 便 相 调 传 倒 扇 载 涨 别 差 降 干 空 难
  处 模 背 将 弹 单 号 片 率 度 量 参 切 称 角 结 夹 省 属 宿 朝 吓 薄. **B1 (yakin)**: 了=le bila bukan sesudah 不/得; 好=hǎo bila tidak sebelum 学客奇动胜色; 都=dōu; 会=huì (berdiri sendiri).
  Kata terkurasi yang bacaannya beda dari bacaan karakter tunggalnya (都会 dū huì) juga ditandai berisiko.
- Skrip lihat-dulu menulis `laporan_nada_nuance.txt` dan `usulan_nada_nuance.json` (di akar repo); skrip penerapan menulis `hasil_nada_nuance.txt`. Ketiganya **keluaran sekali pakai**,
  boleh dihapus dari repo bila tidak diperlukan lagi.

**Validasi metode pada 1.868 contoh lama yang sudah bernada (bahan butir 3, hasil pendahuluan):**
- Dibandingkan **suku kata demi suku kata**: **1.477 contoh sama persis**; 27 tidak bisa disejajarkan (hampir semuanya salah pecah oleh metode, bukan salah ketik lama: 都会, 系 jì/xì, 长 cháng/zhǎng, 心地, 退还);
  sisanya berbeda dalam empat macam:
  1. **一**: 201 contoh (data lama menulis yī, yīgè, yīxià tanpa perubahan nada; 716 contoh baru memakai yí/yì).
  2. **个 gè/ge**: 75 contoh (data lama campur: yīgè, yī gè, zhège).
  3. **Netral vs nada penuh**: 127 contoh, terbanyak 欢 huān→huan (23), 来 lái→lai (13), 上 shàng→shang (10), 生 shēng→sheng (9), 里 lǐ/li (9), 边 biān/bian (5), 阳 (5), 是 (4), 睛 (4).
  4. **Nada berbeda sungguhan**: 24 contoh. **16 di antaranya data lama yang benar** dan metode yang keliru: 只 zhī ×3, 种 zhòng ×2, 倒 dǎo ×2, 数 shǔ, 扇 shān, 当 dàng (正当),
     搂 lǒu, 连襟 lián, 下载 xiàzài, 干 gàn (树干), 空 kòng (空缺), 少 shào (空少). **8 contoh calon perbaikan data lama** (perlu tinjau satu per satu):
     成绩 chéngjī→**chéngjì** (2 contoh: "好成绩" dan "考试成绩"), 别忘 biè→**bié**, 高涨 gāozhàng→**gāozhǎng**, 痕迹 hénjī→**hénjì**, 供应 gòngyìng→**gōngyìng**,
     为人 wèirén→**wéirén**, 突然 túrán→**tūrán** (variasi Taiwan/Daratan; perlu keputusan).
  - Angka-angka ini hasil uji pendahuluan; hitung ulang saat butir 3 dikerjakan.

## 4. Berkas baru atau berubah di repo (ringkas)

Skrip di akar repo (baru): `daftar_nada_nuance.py`, `terapkan_nada_nuance.py`. Keluaran sekali pakai (boleh dihapus): `laporan_nada_nuance.txt`, `usulan_nada_nuance.json`, `hasil_nada_nuance.txt`.
Data berubah: `data/nuance_pairs.json` (716 isian `example_pinyin`; **perlu diunggah**). **Tidak** diunggah: berkas `.bak_*` (termasuk `nuance_pairs.json.bak_nada_*`) dan folder `__pycache__`.

## 5. Rencana ke depan (belum diputuskan; pilih saat sesi berikutnya)

1. **Tarik ulang repo dan pastikan `data/nuance_pairs.json` yang bernada sudah terunggah** (langkah pertama, bukan butir).
2. **Nada pada 1.868 contoh lama (butir 3 v44)**, kini ada bahan diskusi (bagian 3 di atas). Perlu keputusan: (a) hanya memperbaiki calon salah nada (±8 contoh); (b) menyamakan **一** dengan aturan baru (201 contoh);
   (c) menyamakan **个** (75 contoh); (d) menyamakan **nada netral** (127 contoh). Opsi (b) sampai (d) membuat 2.584 contoh seragam; tanpa itu, 716 contoh baru dan 1.868 contoh lama memakai kebiasaan berbeda.
3. **22 soal "Pilih yang Tepat" yang dilewati** (lihat v44 bagian 3): tinjau apakah kalimatnya perlu disesuaikan. (Dulu butir 4.)
4. **Penyegaran `tone_drills.json`** lewat `skrip/dari_py/generate_tone_drills.py` (±36 grup dan ±239 butir tertinggal). **Jangan meregenerasi `wb_pools.json`** (dikurasi manual). (Dulu butir 5.)
5. **Pelajaran Pilar 3 (量词)** yang asli, lewat GPT dengan pesan serah terima. (Dulu butir 6.)
6. **Tingkat 3 awalan/akhiran** (族 迷 热 控 症 剂 炎 盲, penunjuk posisi 上 下 里 外 中 间, 边) dan **latihan awalan/akhiran** (Flashcard, Word Builder, Ujian HSK). (Dulu butir 7.)
7. **Tautan varian ⺮ 攵 罒** ke tombol 竹 攴 网 yang sudah ada (opsional, kecil). (Dulu butir 8.)
8. Backlog aktif lama tidak berubah (lihat catatan proyek dan v41/v42): pasangan penggolong + rantai kata kerja, 多音字, dikte, dashboard gabungan, skema kata 3+ karakter (1.287 kata), dan seterusnya.

## 6. Cara membuka aplikasi dan cara kerja repo

Tidak berubah dari v42 bagian 8, v43 bagian 6, dan v44 bagian 6. Ringkas: aplikasi dibuka lewat server lokal (Live Server) dari `C:\mandarin_app`; Claude membaca repo
https://github.com/RuslanAlimuddin/mandarin_app (folder `blueprint/` untuk BLUEPRINT terbaru); hasil skrip/berkas baru diberikan lewat percakapan dan رسلان yang mengunggahnya.
Jalur ke contoh nuansa di aplikasi: **Kamus → kolom "Cari hanzi, pinyin, atau arti Indonesia…" → ketik kata → klik hasilnya → gulir ke panel "🆚 Beda dengan Kata Mirip"**
(setelah mengubah data, tekan Ctrl+F5 agar data baru terbaca).

## Ringkasan status proyek

- Paket Pembentukan Kata, pembersihan bacaan dan data (v43), varian radikal, beres-beres cadangan, 11 perbaikan nuansa (v44): **selesai**.
- Sesi 19 November: 716 contoh pinyin diberi tanda nada, ü bercampur selesai: **selesai dan teruji di aplikasi** (data bernada menunggu diunggah).
- Berikutnya: butir 2 (nada 1.868 contoh lama) atau pilih dari bagian 5 menurut minat رسلان.

## 7. Pesan pembuka siap pakai untuk percakapan baru

Salin, lalu ganti bagian dalam tanda kurung siku:

```
Lanjutkan proyek Mandarin Interaktif. Tarik ulang repo
(https://github.com/RuslanAlimuddin/mandarin_app) dan baca
`blueprint/BLUEPRINT_v45.md` (bagian 1 tentang aturan kerja dan bagian 5 tentang rencana).
Butir yang ingin saya kerjakan: [nomor atau nama butir dari bagian 5].
Seperti biasa: diskusi dulu sebelum membuat kode atau berkas, instruksi uji dengan
jalur klik lengkap, dan tarik ulang repo sendiri.
```

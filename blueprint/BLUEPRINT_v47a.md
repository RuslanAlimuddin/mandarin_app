# BLUEPRINT v47 — Mandarin Interaktif

Lanjutan dari BLUEPRINT v46. Sesi ini (20–21 November 2026) menyelesaikan **butir 1, 2 (pembersihan repo), dan 4 rencana v46 bagian 5**:
aturan **里** diputuskan dan diterapkan di seluruh data, **kamus terkurasi dirapikan**, dan **`data/tone_drills.json` dibuat ulang**
(file lama ternyata memuat 40 bacaan nada yang salah dan 183 pinyin berhuruf kapital).

**v47 ringkas.** Untuk hal lama baca `BLUEPRINT_v46.md` (aturan penulisan nada 2.584 contoh nuansa, cara kerja `daftar_nada_nuance.py`),
`BLUEPRINT_v44.md`, dan `BLUEPRINT_v43.md` (aturan kerja lengkap). **Bagian 3 v47 menggantikan "Pengecualian 里" di bagian 3 v46.**
Bagian 5 v47 menggantikan bagian 5 v46.

---

## 1. Aturan kerja (v43, v44, v46 tetap berlaku; tambahan sesi ini)

- Semua aturan sebelumnya tetap: diskusi dulu untuk pekerjaan yang menghasilkan kode atau berkas; bahasa sederhana; sebutkan ulang isi dan jumlah poin saat merujuk;
  **instruksi uji dengan jalur klik lengkap**; pola skrip (lihat-dulu dan `--apply`, cadangan, pemeriksaan akhir, aman diulang); Claude menguji skrip di salinan repo bersih
  dan memeriksa `git diff` bahwa hanya isian yang disetujui yang berubah.
- **Setelah tiap pengunggahan, Claude menarik ulang repo dan menjalankan ulang skrip lihat-dulu pada repo itu; semuanya harus menjawab "tidak ada yang perlu diubah".**
  Claude juga mengingatkan berkas mana yang perlu diunggah setelah tiap perubahan (permintaan رسلان).
- **Penggantian di berkas ditentukan oleh POSISI isian, bukan oleh bunyi pinyin.** Pinyin yang sama bisa milik hanzi berbeda
  (contoh nyata: "xīnlǐ" dipakai 心里 dan 心理 di `graded_readers.json`). `perbaiki_li_berkas_lain.py` memetakan urutan teks JSON ke posisi di berkas,
  menukar tepat isian yang direncanakan, dan berhenti bila urutannya tidak sejajar.
- **Format tiap berkas dijaga apa adanya.** Berkas data tidak seragam formatnya (ada yang indent 2 dengan CRLF seperti `app_words.json`, `tone_drills.json`, `pilar_4.json`,
  `produktif_karakter.json`; ada yang LF; ada yang satu baris seperti `pelajaran/pilar_9.json`). Skrip yang menulis ulang seluruh berkas menolak bekerja bila format tidak bisa ditulis ulang persis sama.
- **Pemeriksaan huruf kapital harus memakai `teks != teks.lower()`, bukan `[A-Z]`.** Kapital bertanda nada ("Ān") lolos dari `[A-Z]`; akibatnya 安 sempat hilang
  dari soal "Pilih Nada" dan tak terdeteksi di laporan pertama. Kesalahan ini diakui dan diperbaiki di `segarkan_tone_drills.py`.
- **Cara mengunggah (aplikasi `GitHub_Transfer_Tool_V6.py`, tkinter, lewat API GitHub dengan token; dijalankan dengan `Jalankan_Aplikasi_V6.bat`; V5 tetap ada sebagai cadangan).**
  Tujuan unggahan ditentukan oleh **folder yang sedang dipilih di pohon**; bila tidak ada yang dipilih, berkas masuk ke **akar repo**
  (sebab `nuance_pairs.json` pernah terunggah ke akar di V5). Jadi: klik dulu folder tujuan (mis. `data` atau `blueprint`) dan periksa baris
  "Tujuan unggah: /data" di panel kanan, baru klik "Unggah file". **V6 menampilkan dialog konfirmasi** (status Baru / Berubah / Sama persis, peringatan bila
  berkas bernama sama sudah ada di folder lain, pesan commit yang bisa diubah) dan mengirim banyak berkas sebagai **satu commit**. V6 memakai **aturan abaikan**:
  bawaan (`*.bak_*`, `__pycache__`, `.env`, dst.) ditambah isi **`.gitignore` di repo**, jadi `.gitignore` kini berfungsi. Nama `.gitignore` **harus berawalan titik**
  (berkas yang diunduh dari percakapan bisa kehilangan titik; perbaiki dengan "Ganti nama / pindahkan" di aplikasi). Sortir dan saringan: klik judul kolom (Nama, Jenis, Ukuran, Diubah),
  kotak cari, filter jenis dan waktu, "Tampilan datar"; tanggal berkas dibaca dari 100 commit terakhir ("Muat tanggal lebih lama" menambah 100). Tema terang atau gelap lewat tombol di kanan atas.

## 2. Selesai sesi ini (20–21 November 2026)

| Butir | Hasil | Skrip |
|---|---|---|
| Aturan 里 (lihat bagian 3) | **Contoh nuansa:** dari 101 kemunculan 里, **61 diubah** (59 menjadi netral "li": 家里, 教室里, 村里, 手里, 汤里, dst.; 2 menjadi "lǐ": 这里 yang tadinya "zhèli"); 40 sudah benar | `perbaiki_li_netral.py` |
| Kamus terkurasi `app_words.json`, tahap 1 | **31 isian di 10 kata**: 家里 jiā li, 手里 shǒu li, 城里 chéng li, 怀里 huái li (netral); 那里 nà **lǐ** (sebelumnya nà li); 噼里啪啦 pī li pā lā; 木匠 mùjiang; 早晨 zǎochen (keterangan "juga dibaca [zao3chen5]" dibalik menjadi **[zao3chen2]**, Inggris "also pr. [zǎo chén]"); 玫瑰 méigui; 精神 tetap jīngshén dengan awalan **"[jīngshen]"** pada tiga artinya yang berbacaan netral (semangat; vitalitas / bersemangat / tampan). Pinyin, pinyin angka, dan zhuyin ikut. | `perbaiki_li_netral.py` |
| 里 di berkas lain, tahap 2 | **44 kemunculan di 14 berkas** (`graded_readers`, `grammar_afiks`, `grammar_hsk1/3/5/6/8/9`, `pattern_explanations`, `pelajaran/pilar_4/6/9/10`, `produktif_karakter`): 31 akhiran tempat → li, 7 pola A里AB → li, 6 → lǐ (这里/那里). | `perbaiki_li_berkas_lain.py` |
| Kata biasa berpinyin kapital | 日 rì, 帅 shuài, 遇 yù, 剪 jiǎn, 景 jǐng, 安 ān (pinyin dan pinyin angka; 12 isian). Penyebab: arti pertamanya "marga …". | `segarkan_tone_drills.py` |
| Arti "marga" | Dipindah ke **akhir** daftar arti (Indonesia dan Inggris) untuk 帅 遇 剪 景 闻 安 (12 daftar), seperti yang sudah terjadi pada 和 dan 从. Tak ada arti yang dihapus. | sama |
| 帅 | Arti "tampan; anggun; gagah; elegan" dinaikkan ke **urutan pertama** (arti pertama sebelumnya "panglima tertinggi"). | sama |
| Butir 4 v46: `tone_drills.json` | Dibuat ulang dengan generator resmi `skrip/dari_py/generate_tone_drills.py` (generator **tidak diubah**). "Pilih Nada" 1.514 → **1.513** soal; "Pilih Hanzi" 1.021 → **1.022** grup (3.055 → **3.058** kata). **223 bacaan berubah: 40 nada/bunyi benar-benar salah** (要 yāo→**yào**, 说 shuì→**shuō**, 上 shǎng→**shàng**, 看 kān→**kàn**, 还 Huán→**hái**, 鸟 diǎo→**niǎo**, 重 chóng→**zhòng**, 行 háng→**xíng**, 略 "lu:è"→**lüè**) dan **183 hanya kapital → huruf kecil**; arti diperbarui di 21 kata (和, 从, 血, dst., yang dulunya "marga …"). 着 dan 得 keluar dari "Pilih Nada" (bacaan utamanya netral); 安 masuk; grup `gei` hilang; `cang` dan `niao` muncul. | `segarkan_tone_drills.py` |

Semua tahap diuji رسلان di aplikasi dan lolos. **Verifikasi akhir (Claude, 21 November 2026)** pada repo hasil unggahan: `perbaiki_li_netral.py`, `perbaiki_li_berkas_lain.py`, dan
`segarkan_tone_drills.py` pada mode lihat-dulu semuanya menjawab "tidak ada yang perlu diubah".

## 3. Catatan penting untuk sesi berikutnya

**Aturan penulisan 里 final (menggantikan "Pengecualian 里" v46; berlaku di contoh nuansa, kamus terkurasi, dan 14 berkas lain):**
- **里 akhiran tempat setelah kata benda → netral "li"**: 家里 jiā li, 心里 xīn li, 手里 shǒu li, 城里 chéng li, 怀里 huái li, 眼里, 夜里, 森林里, 房间里, 村里, 教室里, 暗地里.
- **Pola A里AB → netral "li"**: 糊里糊涂 húlihútú, 啰里啰嗦, 慌里慌张, 古里古怪 (bacaan baku netral; bukan akhiran tempat).
- **Tetap nada penuh "lǐ"**: 这里 那里 哪里 (里 sesudah 这/那/哪); 里面 里头 里边 (里 di depan); **里 arah** (往里走, 向里, 朝里); kata serapan **沙特里亚尔 shā tè lǐ yà ěr** dan **尤克里里 yóu kè lǐ lǐ**;
  satuan dan 卡路里 (公里 万里 鹏程万里 卡路里); 里 di awal frasa. **道理/有道理** tetap dàoli (里 di situ adalah 理).
- Catatan sumber: CC-CEDICT sendiri menulis 家里/手里/怀里 dengan lǐ penuh dan 心里/夜里/暗地里/那里 dengan li netral. Netralnya 家里 dkk. adalah **keputusan proyek** (selaras dengan 学生 xuésheng, 关系 guānxi), bukan salinan CC-CEDICT.

**Keputusan kamus lain:**
- **能不能 tetap "néng bùnéng"** (aturan "不 tetap bù" satu untuk seluruh data). Bacaan baku néng bu néng sengaja tidak dipakai.
- **鹏程万里, 尤克里里, 里面/里头/里边, 公里** tidak diubah. **冷清 dan 想想 bukan entri kamus terkurasi** (jadi tidak ada yang perlu dibenahi di kamus) dan **房子 sudah netral** (fáng zi); butir "arah kebalikan" v46 dengan demikian tuntas.
- **`tone_drills.json` tidak boleh diubah tangan**: ia dihasilkan dari kamus. Bila kamus berubah, jalankan `segarkan_tone_drills.py` (lihat-dulu) lalu `--apply`. **`wb_pools.json` tetap dikurasi manual dan tidak diregenerasi.**

**Temuan yang belum dikerjakan:**
- **80 kata lebih dari satu karakter berpinyin kapital** di `app_words.json`. Sebagian sah (nama diri: 中国, 北京, 欧洲, 微信), sebagian tampak keliru karena kata biasa:
  **和平 Hé píng, 通道 Tōng dào, 安定 Ān dìng, 互联网 Hù lián wǎng, 星期天 Xīng qī tiān**, dan sejenisnya. Perlu ditinjau satu per satu bersama رسلان (lihat-dulu dulu).
- Kata satu karakter berpinyin kapital: sekarang **0** (dicek dengan `!= lower()`).
- Posisi **POS** pertama untuk 帅 masih "nr" (nama orang); tidak diubah.

## 4. Berkas di repo

**Dipakai terus (alat dan pustaka; jangan dihapus):**
- `daftar_nada_nuance.py` — pustaka bersama; **dipakai oleh `perbaiki_li_netral.py` dan `perbaiki_li_berkas_lain.py`** dan skrip tahap nuansa. Setiap dijalankan menulis `laporan_nada_nuance.txt` dan `usulan_nada_nuance.json` di akar.
- `beres_cadangan.py` — memindahkan `*.bak_*` lama ke `arsip_cadangan_lama\` (menyisakan yang terbaru per jenis; tidak menghapus). Mengenali jenis baru sesi ini otomatis.
- `segarkan_tone_drills.py` — **alat yang boleh dijalankan ulang** untuk menyegarkan `tone_drills.json` dari kamus (langkah kamusnya dilewati bila sudah benar). Bila ingin membenahi kata lain, tambah ke tabel `KAPITAL`, `MARGA_AKHIR`, atau `DEPANKAN` di dalamnya.

**Sekali pakai, sudah dijalankan (boleh disimpan sebagai catatan; tetap di akar, tidak dipindah):**
- Sesi ini: `perbaiki_li_netral.py`, `perbaiki_li_berkas_lain.py` (keduanya aman diulang).
- Nuansa (v44–v46): `terapkan_nada_nuance.py`, `samakan_yi_nuance.py`, `samakan_ge_nuance.py`, `samakan_netral_nuance.py`, `perbaiki_nuance.py`.
  **`perbaiki_nada_lama.py` tidak bisa dijalankan ulang** (pelindung "isi sekarang harus sama persis").
- Sesi lama: `arsipkan_pilar3.py`, `bersihkan_sitasi.py`, `pasang_afiks_kamus.py`, `pasang_afiks_tatabahasa.py`, `pasang_pilar12.py`, `perbaiki_frasa.py`,
  `perbaiki_kata_kecil.py`, `perbaiki_majemuk.py`, `terapkan_koreksi_bacaan.py`.
- Folder `skrip/` (101 berkas) tidak berubah.

**Keluaran sekali pakai (rencana pembersihan disetujui): hapus dari repo** `hasil_nada_nuance.txt`, `laporan_nada_nuance.txt`, `usulan_nada_nuance.json`.
Cara (aplikasi unggah): sambungkan → klik berkasnya di pohon (Ctrl+klik untuk beberapa) → **Hapus terpilih** → Ya. Berkas serupa `hasil_li_netral.txt`, `hasil_li_berkas_lain.txt`, `hasil_tone_drills.txt` hanya ada di PC.

**`.gitignore` (baru):** berisi `*.bak_*`, `arsip_cadangan_lama/`, `backups/`, `__pycache__/`, `*.pyc`, `hasil_*.txt`, `laporan_*.txt`, `usulan_*.json`. Letaknya di akar repo.
**Catatan:** aplikasi unggah V6 **membaca `.gitignore` di repo** (ditambah aturan bawaan), sehingga berkas yang cocok aturan dilewati pada "Unggah folder" dan diberi tanda pada "Unggah file".
Pastikan namanya `.gitignore` (berawalan titik).

**Cadangan di PC (tidak diunggah):** label `bak_nada`, `bak_nadalama`, `bak_yi`, `bak_ge`, `bak_netral`, `bak_li`, `bak_li2`, `bak_td`. Rapikan kelak dengan `python beres_cadangan.py` (lihat-dulu, lalu `--apply`).

## 5. Rencana ke depan (belum diputuskan; pilih saat sesi berikutnya)

1. **80 kata berpinyin kapital** (bagian 3): tinjauan satu per satu, dimulai dengan skrip lihat-dulu yang mendaftar semuanya dengan arti dan HSK-nya.
2. **Aplikasi unggah V6: selesai** (21 November 2026): konfirmasi tujuan, peringatan nama sama, aturan abaikan dari `.gitignore`, satu commit untuk banyak berkas, sortir, saringan, tema gelap,
   ganti nama/pindah, hapus folder, proses di latar belakang dengan tombol Batal. Dicatat di sini agar sesi berikutnya tidak menyuruh memakai V5.
3. **22 soal "Pilih yang Tepat" yang dilewati** (lihat v44 bagian 3).
4. **Pelajaran Pilar 3 (量词)** yang asli, lewat GPT dengan pesan serah terima. Catatan: penggolong 个 di contoh kini selalu netral "ge".
5. **Tingkat 3 awalan/akhiran** (族 迷 热 控 症 剂 炎 盲, penunjuk posisi 上 下 里 外 中 间, 边) dan **latihan awalan/akhiran** (Flashcard, Word Builder, Ujian HSK).
   Catatan: aturan 里 baru (bagian 3) berlaku untuk penunjuk posisi 里.
6. **Tautan varian ⺮ 攵 罒** ke tombol 竹 攴 网 (opsional, kecil).
7. Backlog aktif lama tidak berubah (lihat v41/v42 dan catatan proyek): pasangan penggolong + rantai kata kerja, 多音字, dikte, dashboard gabungan, skema kata 3+ karakter (1.287 kata), dan seterusnya.

## 6. Cara membuka aplikasi dan cara kerja repo

Tidak berubah dari v42 bagian 8, v43 bagian 6, dan v44 bagian 6: aplikasi dibuka lewat server lokal (Live Server) dari `C:\mandarin_app`; Claude membaca repo
https://github.com/RuslanAlimuddin/mandarin_app (folder `blueprint/` untuk BLUEPRINT terbaru); hasil skrip dan berkas baru diberikan lewat percakapan dan رسلان yang mengunggahnya (bagian 1: aplikasi unggah).
Setelah mengubah data, tekan **Ctrl+F5** agar data baru terbaca.

**Jalur uji yang sudah dipastikan dari kode aplikasi (sesi ini):**
- **Kamus:** Kamus → kolom "Cari hanzi, pinyin, atau arti Indonesia…" → ketik kata → klik hasilnya (pinyin dan daftar arti tampil; contoh nuansa di panel "🆚 Beda dengan Kata Mirip").
- **Soal "Pilih Nada" dan "Pilih Hanzi" (`tone.html`, memuat `data/tone_drills.json`):** menu atas **Tone** (atau Beranda → kartu **Latihan Nada**) → halaman "Latihan Tone" → tombol **Pilih Nada** atau **Pilih Hanzi**. Soal diacak, jadi kata tertentu tak bisa dipilih; mainkan beberapa soal.
- Jebakan Nada: Flashcard → bilah samping → deck "🎵 Jebakan Nada (Game Audio)" (memakai mekanisme `tone.html`).

**Contoh uji yang dipakai di sesi ini (kata → yang harus tampil di Kamus):** 家里 → **jiā li**; 那里 → **nà lǐ**; 木匠 → **mù jiang**; 早晨 → **zǎo chen**; 玫瑰 → **méi gui**;
日 → **rì** (huruf kecil); 安 → **ān**, arti pertama "(bentuk terikat) tenang; damai"; 景 → arti pertama "(bentuk terikat) pemandangan"; 帅 → arti pertama **"tampan; anggun; gagah; elegan"**, "marga Shuai" di urutan terakhir;
糊里糊涂 (di pelajaran Pilar 9: Kata Sifat, Reduplikasi, dan Intensifikasi) → **húlihútú**.

## Ringkasan status proyek

- Paket Pembentukan Kata, pembersihan bacaan (v43), varian radikal, beres-beres cadangan, 11 perbaikan nuansa (v44): **selesai**.
- Seluruh contoh pinyin nuansa (2.584) bernada dan seragam (v46): **selesai**.
- **Sesi 20–21 November: aturan 里 diterapkan di seluruh data, kamus terkurasi dirapikan (10 kata + 6 kata kapital/arti marga), `tone_drills.json` dibuat ulang: selesai, teruji, terunggah.**
- Berikutnya: hapus 3 keluaran dari repo, lalu pilih dari bagian 5 menurut minat رسلان (usul: 80 kata berpinyin kapital).

## 7. Pesan pembuka siap pakai untuk percakapan baru

Salin, lalu ganti bagian dalam tanda kurung siku:

```
Lanjutkan proyek Mandarin Interaktif. Tarik ulang repo
(https://github.com/RuslanAlimuddin/mandarin_app) dan baca
`blueprint/BLUEPRINT_v47.md` (bagian 1 tentang aturan kerja dan bagian 5 tentang rencana).
Butir yang ingin saya kerjakan: [nomor atau nama butir dari bagian 5].
Seperti biasa: diskusi dulu sebelum membuat kode atau berkas, instruksi uji dengan
jalur klik lengkap, tarik ulang repo sendiri, dan ingatkan berkas mana yang perlu saya unggah.
```

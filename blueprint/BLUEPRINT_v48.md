# BLUEPRINT v48 — Mandarin Interaktif

Lanjutan dari BLUEPRINT v47. Sesi ini (22–25 November 2026) menyelesaikan **butir 1, 3, dan 6 rencana v47 bagian 5**, mengerjakan **latihan awalan/akhiran di Flashcard**
(dua permainan baru) dan **memperbanyak daftar "bukan" imbuhan lewat kerja GPT dan kurasi**. Selain itu dibahas rencana **bahan budaya** (pepatah, puisi, lagu rakyat).

**v48 ringkas.** Untuk hal lama baca `BLUEPRINT_v47.md` (aturan 里, cara unggah V6, tone_drills), `BLUEPRINT_v46.md`, `BLUEPRINT_v44.md`, dan `BLUEPRINT_v43.md` (aturan kerja lengkap).
**Bagian 5 v48 menggantikan bagian 5 v47.** Bagian 3 v48 melengkapi (tidak menggantikan) bagian 3 v47.

---

## 1. Aturan kerja (v43, v44, v46, v47 tetap berlaku; tambahan sesi ini)

- Semua aturan sebelumnya tetap: diskusi dulu untuk pekerjaan yang menghasilkan kode atau berkas (termasuk berkas bantu sekecil apa pun); bahasa sederhana; sebutkan ulang isi dan jumlah poin saat merujuk;
  **instruksi uji dengan jalur klik lengkap**; pola skrip (lihat-dulu dan `--apply`, cadangan, pemeriksaan akhir, aman diulang); Claude menguji skrip di salinan repo bersih dan memeriksa `git diff`;
  setelah tiap pengunggahan Claude menarik ulang repo dan menjalankan ulang skrip lihat-dulu (semuanya harus "tidak ada yang perlu diubah"); Claude mengingatkan berkas mana yang perlu diunggah.
- **Perintah Python harus diketik dengan `python` di depan** (mis. `python segarkan_tone_drills.py`). Mengetik nama berkas saja membuka Python lama dan menghasilkan galat `No module named util`.
- **Claude membaca hasil GPT langsung dari repo** (mis. `kerja_gpt_afiks/kandidat/tahap1/batch_NN_hasil.json`); رسلان cukup menyimpan hasilnya di folder yang sama, mengunggahnya, lalu memberi tahu Claude. Tidak perlu ditempel.
- **Perubahan JavaScript diuji Claude dengan simulasi halaman** (server lokal + jsdom) sebelum diserahkan: memuat halaman asli, menekan tombol, memeriksa tampilan dan galat. Pengujian akhir di aplikasi tetap oleh رسلان.
- **Pola kurasi hasil GPT** (dipakai untuk daftar "bukan" imbuhan, berlaku juga untuk bahan lain): (1) validasi mesin (JSON sah, jumlah dan urutan cocok manifest, kata kontrol), (2) Claude membaca tiap penilaian, (3) hanya yang pasti diambil,
  (4) رسلان menyetujui pedoman dan batas jumlah sebelum skrip pemasang dibuat, (5) skrip pemasang punya cadangan dan pemeriksaan akhir.
- **Pedoman "bukan imbuhan":** sebuah kata masuk daftar "bukan" HANYA bila karakter imbuhan itu **benar-benar berarti lain** daripada fungsi imbuhannya (卫生: 生 = hidup; 老虎: 老 = bagian nama hewan; 握手: 手 = tangan; 合法: 法 = hukum).
  Kata yang karakternya **masih berarti sama** dengan fungsi imbuhan (就业 敬业: 业 tetap "pekerjaan"; 终点 景点: 点 tetap "titik/tempat"; 总统 总理; 同志 同情; 自豪 自在) **tidak** dimasukkan, begitu pula pemakaian imbuhan-mirip
  (独家 赢家 输家 厂家: 家 sebagai "pihak"; 儒家: 家 sebagai "aliran"; 人员). GPT cenderung terlalu ketat (kata kontrol 70/74; semua yang salah berupa "bukan" untuk imbuhan sungguhan), jadi hasilnya tidak boleh dipakai mentah.

## 2. Selesai sesi ini (22–25 November 2026)

| Butir | Hasil | Skrip / berkas |
|---|---|---|
| **Butir 1 v47: 80 kata berpinyin kapital** | **16 kata** diubah ke huruf kecil: 14 kata biasa (和平 通道 安定 复兴 互联网 星期天 星期日 礼拜天 吉普 摄氏度 菩萨 一卡通 国会 中医) + 2 kata rusak (美德 měi Dé→měi dé; 张扬 zhāng Yáng→zhāng yáng, arti nama sutradara dipindah ke **urutan terakhir**). **63 isian** di `app_words.json` (34), `graded_readers.json` (3), `produktif_karakter.json` (24), `nuance_pairs.json` (2; termasuk "Hépíng"→"hépíng" di tengah kalimat), + 1 baris `tone_drills.json` (via `segarkan_tone_drills.py`), + **arti glosarium 张扬** di bacaan `tema_kebebasan_hsk9` diganti "memamerkan secara mencolok" (teksnya memakai kata kerja). **64 kata tetap berkapital** (nama diri: 中国 北京 欧洲 微信 嫦娥, dst., dan kelompok D: bahasa 英语 汉语 中文, agama 佛教 穆斯林, hari raya 春节 中秋节, mata uang 美元 英镑, 华人 京剧, dst.) | `perbaiki_kapital_kata.py` |
| **Butir 3 v47: soal "Pilih yang Tepat" yang dilewati** | Dihitung ulang: **23 kasus** (bukan 22; sebabnya tidak ditelusuri). Semua ditulis ulang di `nuance_pairs.json` (kata target utuh, pinyin dengan nada, terjemah) dan kini **0** yang dilewati. 6 di antaranya kata terpisah (生气 请假 休假 下雪 胆小 赚钱). | `perbaiki_kalimat_pilih_tepat.py` |
| **Butir 6 v47: tautan varian ⺮ 攵 罒** | Tombol 竹 攴 网 (bagian "Lainnya") kini dianggap tujuan tautan sah: halaman ⺮/攵/罒 punya tombol "Lihat 竹/攴/网 →" dan tanda ↔ di daftar; halaman 竹/攴/网 punya baris "Bentuk varian". Hanya kode, data tidak diubah. **Tombol 艸 tidak ditambah** (hanya 2 karakter berradikal 艸 di data sumber, 421 ada di 艹). | `kamus/kamus-komponen-posisi.js` |
| **Butir 5 v47: latihan imbuhan di Flashcard (bagian 1)** | Dua deck permainan baru di sidebar Flashcard: **🧱 Imbuhan (Awalan & Akhiran)** ("Imbuhan atau bukan?", Ya/Bukan + penjelasan, seimbang separuh ya separuh bukan) dan **🧱 Pilih Imbuhan yang Tepat** (isi bagian kosong, mis. 记 + ＿ "wartawan", 4 pilihan hanzi + pinyin). Tanpa suara. | `flashcard.html`, `flashcard/flashcard-decks.js`, `-games.js`, `-session.js`, `-init.js`; data baru `data/afiks_pengecoh.json` (298 soal) dibuat oleh `buat_pengecoh_imbuhan.py` |
| **Butir 5 v47: memperbanyak "bukan" imbuhan (cara B)** | 735 kata kandidat (tahap 1, 17 berkas) dinilai GPT; ke-17 hasil dikurasi Claude (lihat pedoman di bagian 1): 127 kata diterima, **batas 8 per imbuhan** (HSK terendah dulu) → **102 kata** dipasang di `afiks_kamus.json`. Daftar "bukan": **40 → 142 kata; imbuhan yang punya "bukan": 18 → 38.** Tampil di Kamus → Kelompok → Awalan & Akhiran ("Mirip tetapi bukan") dan jadi soal "Imbuhan atau bukan?" (kini **440** soal: 298 imbuhan + 142 bukan). | `buat_kandidat_imbuhan.py`, `kerja_gpt_afiks/kandidat/…`, `pasang_bukan_imbuhan.py` |

Semua tahap diuji رسلان di aplikasi dan lolos; semuanya sudah diunggah ke GitHub (kecuali perbaikan `buat_kandidat_imbuhan.py` dan `CATATAN_LANJUTAN.md` tanggal 25 November, yang diunggah bersama blueprint ini).
**Verifikasi akhir (Claude, 25 November 2026)** pada repo hasil unggahan: `perbaiki_li_netral.py`, `perbaiki_li_berkas_lain.py`, `segarkan_tone_drills.py`, `perbaiki_kapital_kata.py`, `perbaiki_kalimat_pilih_tepat.py`,
`pasang_bukan_imbuhan.py`, dan `buat_pengecoh_imbuhan.py` pada mode lihat-dulu semuanya menjawab "tidak ada yang perlu diubah".

**Keputusan lain sesi ini:**
- **Jenis suara tambahan (laki-laki, anak, resmi, santai): DIBATALKAN** (butuh ratusan MB ruang disk untuk hasil yang tidak signifikan). Di Chrome رسلان hanya ada tiga suara Mandarin Google (daratan, Hong Kong Kanton, Taiwan); suara itu butuh internet.
- **Bahan budaya** (pepatah, puisi, lagu rakyat): lihat bagian 5 butir 6. Dikerjakan رسلان di luar percakapan Claude.

## 3. Catatan penting untuk sesi berikutnya

**Struktur dan aturan latihan imbuhan:**
- Data imbuhan: `data/afiks_kamus.json` (60 imbuhan: 43 akhiran, 17 awalan, kelompok A–J). **Jangan jalankan ulang `pasang_afiks_kamus.py` yang lama** (bisa menimpa daftar "bukan" baru). Daftar "bukan" hanya bertambah lewat `pasang_bukan_imbuhan.py`.
- **`data/afiks_pengecoh.json` dihasilkan oleh `buat_pengecoh_imbuhan.py`** dan harus **dibuat ulang** bila **kata contoh** di `afiks_kamus.json` berubah (daftar "bukan" tidak memengaruhinya). Pengecoh dijamin tidak membentuk kata sah menurut `app_words.json` dan CC-CEDICT (`data/cidict_index.json.gz`). Bila sebuah soal kekurangan pengecoh sekelompok (27 dari 298), ditambah dari kelompok lain.
- Deck baru memakai kotak **"jumlah kartu" Flashcard (bawaan 20)**: 20 soal = 10 imbuhan + 10 bukan. Untuk 10 soal (5 dan 5) isi kotak itu dengan 10 sebelum memilih deck.
- Di soal imbuhan, arti kata dibersihkan dari sisa format CC-CEDICT (`KP:…`, `繁|简[pinyin]`) dan arti pertama berupa nama diri dilewati (fungsi `afiksArtiBersih` di `flashcard-games.js`). **Datanya sendiri tidak diubah:** arti pertama beberapa kata di `app_words.json` masih nama tempat (mis. 郊区 "Distrik Jiao…"); perlu dibenahi seperti kasus 张扬 bila diinginkan.
- Soal "imbuhan atau bukan?" mengikuti SRS kata yang diuji (memakai objek kata asli bila ada).

**`buat_kandidat_imbuhan.py` dan tahap 2 (DITUNDA):**
- Tahap 1 (735 kata, 17 berkas) **selesai dan dikurasi; jangan dijalankan ulang** (kandidatnya sekarang berbeda dari yang pernah dinilai, karena 102 kata sudah menjadi "bukan").
- **Tahap 2 = semua kandidat yang belum dinilai: 433 kata (8 berkas), sengaja ditunda sampai ada waktu yang tepat** (keputusan رسلان; jangan hilang). Jalankan nanti: `python buat_kandidat_imbuhan.py --tahap 2` lalu `--apply`.
  Skrip memilih tahap 2 dari **`kerja_gpt_afiks/kandidat/tahap1/_manifest_tahap1.json`** (berkas ini **harus tetap ada**), bukan dari urutan. (Catatan koreksi: versi awal skrip mengandalkan urutan dan akan melewatkan sekitar 52 kata setelah 102 "bukan" dipasang; sudah diperbaiki 25 November 2026 dan dibuktikan menghasilkan tepat 433 kata tanpa irisan dengan tahap 1.)
- Tiap berkas kerja berisi instruksi lengkap, definisi imbuhan, contoh sah dan "bukan" yang sudah ada, lalu kata kandidat bernomor (dengan pinyin dan arti dari kamus) dan **kata kontrol** (jawabannya sudah diketahui, kuncinya di `_manifest_tahapN.json`). Satu berkas per percakapan GPT baru; simpan jawabannya sebagai `batch_NN_hasil.json`.
- Hasil tahap 1 (di repo): 735 kata dinilai: 491 imbuhan, 229 bukan, 15 ragu; kontrol 70/74 benar. Hanya "bukan" yang diambil.

**Soal "Pilih yang Tepat" dan data nuansa:** kolom `example_cn` harus memuat `word` utuh (aturan permainan). Bila contoh nuansa diubah lagi, jalankan `perbaiki_kalimat_pilih_tepat.py` (lihat-dulu) sebagai pemeriksa: ia melaporkan 0 selama aman.

**Temuan yang belum dikerjakan:**
- Arti pertama berupa nama diri di `app_words.json` (contoh 郊区). Belum dicari berapa kata lain; pemeriksaan bisa dengan skrip lihat-dulu (arti pertama diawali huruf kapital).
- Daftar bahasa Inggris (`meanings_en`) untuk 和平 通道 安定 复兴 menaruh nama tempat di urutan pertama, sedangkan daftar Indonesia tidak memuatnya. Tidak menimbulkan masalah sekarang.
- POS pertama 帅 masih "nr" (nama orang); tidak diubah.
- Kalimat penjelas kecil di halaman 艹 ("艸 adalah bentuk penuhnya; hampir semua karakternya ditulis 艹") disetujui sebagai butir opsional, belum dikerjakan.

## 4. Berkas di repo

**Dipakai terus (alat dan pustaka; jangan dihapus):**
- `daftar_nada_nuance.py` (pustaka bersama), `beres_cadangan.py`, `segarkan_tone_drills.py` (lihat bagian 3 v47).
- **Baru:** `buat_pengecoh_imbuhan.py` (jalankan ulang bila kata contoh imbuhan berubah), `buat_kandidat_imbuhan.py` (untuk tahap 2 nanti).
- **Data baru:** `data/afiks_pengecoh.json` (298 soal pengecoh; jangan diubah tangan); `kerja_gpt_afiks/kandidat/CATATAN_LANJUTAN.md` dan `kerja_gpt_afiks/kandidat/tahap1/` (`_manifest_tahap1.json`, `batch_01..17.txt`, `batch_01..17_hasil.json`) sebagai arsip tahap 1 dan bahan tahap 2.

**Sekali pakai, sudah dijalankan (aman diulang; simpan sebagai catatan):** `perbaiki_kapital_kata.py` (dua tahap: 63 isian lalu arti glosarium 张扬), `perbaiki_kalimat_pilih_tepat.py`, `pasang_bukan_imbuhan.py`. Skrip lama sesi sebelumnya tidak berubah (lihat v47 bagian 4).

**Berkas yang berubah di sesi ini:** `data/app_words.json`, `graded_readers.json`, `produktif_karakter.json`, `nuance_pairs.json`, `tone_drills.json`, `afiks_kamus.json`, `afiks_pengecoh.json` (baru); `kamus/kamus-komponen-posisi.js`; `flashcard.html`, `flashcard/flashcard-decks.js`, `flashcard-games.js`, `flashcard-session.js`, `flashcard-init.js`.

**Cadangan di PC (tidak diunggah):** label baru `bak_kapital`, `bak_pilihtepat`, `bak_bukan`, selain label lama (`bak_td` dst.). Rapikan dengan `python beres_cadangan.py` (lihat-dulu, lalu `--apply`).
**Keluaran yang hanya ada di PC (diabaikan `.gitignore`):** `hasil_kapital_kata.txt`, `hasil_pilih_tepat.txt`, `hasil_bukan_imbuhan.txt`, `hasil_tone_drills.txt`. Pembersihan 3 keluaran lama nuansa dari repo (usul v47) sudah selesai.

## 5. Rencana ke depan (belum diputuskan; pilih saat sesi berikutnya)

1. **Tingkat 3 akhiran: 族 迷 症 剂 炎 盲** (data lewat GPT dengan pesan serah terima, disesuaikan dari `PROMPT_GPT_Pembentukan_Kata.md`, lalu kurasi; entri otomatis ikut ke dua deck latihan). Dukungan di kamus: 族 6 kata, 迷 8, 症 5, 剂 3, 炎 1, 盲 1 (sedikit tetapi cukup).
   **热 dan 控 ditunda** sampai ada kepastian contoh yang cukup (pemakaian imbuhan "demam/penggemar" mungkin tidak ada contohnya di kamus; kata seperti 遥控 失控 memakai 控 dalam arti biasa).
2. **Pelajaran penunjuk posisi (上 下 里 外 中 间 边): halaman/pelajaran TERPISAH**, bukan masuk ke 60 imbuhan (skema `afiks_kamus` aturan 1 melarang 边; sifatnya kata penunjuk tempat). Bahan melimpah (36, 25, 14, 25, 14, 21, 25 kata).
   Perlu **aturan bacaan netral untuk 上 下 外 边** (里 sudah: li setelah kata benda; lǐ sesudah 这/那/哪, 里面 里头 里边; contoh keputusan yang perlu: 里边 lǐbian, 旁边 pángbiān).
3. **Tahap 2 kandidat "bukan" (433 kata)**: ditunda (bagian 3). Setelah selesai, jalankan `buat_pengecoh_imbuhan.py` bila kata contoh imbuhan ikut berubah.
4. **Latihan imbuhan di Word Builder dan Ujian HSK** (terakhir, setelah deck Flashcard terasa baik; رسلان sudah mencoba dan menilai bagus).
5. **Pelajaran Pilar 3 (量词)** yang asli, lewat GPT dengan pesan serah terima (dikerjakan رسلان di luar). Catatan: penggolong 个 di contoh kini selalu netral "ge".
6. **Bahan budaya: pepatah, puisi, lagu rakyat (halaman TERPISAH; data baru; tidak mengubah data yang ada).** Keputusan رسلان:
   - Pakai cara **"teks (hanzi, pinyin) dari data jadi; AI hanya mengisi arti Indonesia, makna kiasan, contoh kalimat sebanyak mungkin, kategori"** (bukan membuat teks dari nol). **Tahap awal 500 chengyu paling umum.**
   - Dikerjakan رسلان di percakapan lain (mengunduh dan menambang); **kurasi di percakapan terpisah** setelah data siap. Percakapan ini tidak ikut menambang.
   - **Sumber yang ditemukan:** `pwxcoo/chinese-xinhua` (MIT; `data/idiom.json` 30.895 chengyu berpinyin tetapi arti dan contoh masih dalam bahasa Mandarin dan contoh sering kutipan sastra modern; `data/xiehouyu.json` 14.032 hanya dua kolom, tanpa pinyin);
     `chinese-poetry/chinese-poetry` (MIT; Tang, Song, 诗经, folder 蒙學 berisi 三字经 千字文 唐诗三百首; sebagian aksara tradisional, umumnya tanpa pinyin); `leslie-wong-h/chinese-poetry-bilingual` (Apache 2.0; Tang berterjemah Inggris, sedikit);
     `hefengbao/jingmo` (GPL-3.0, aplikasi Android; 964 yanyu, 45 绕口令, 42 ribu teka-teki; data di dalam aplikasi, prioritas rendah). **Lagu rakyat dan sajak anak: tidak ada data jadi yang bersih** (perlu ditambang). Hindari lirik pop modern (hak cipta). Arti chengyu di `chinese-xinhua` berasal dari situs kamus lain, jadi untuk pemakaian pribadi offline saja.
   - **Skema entri yang disepakati:** pepatah: hanzi, pinyin (bernada, per suku kata), arti harfiah, makna kiasan, asal-usul, contoh kalimat (hanzi, pinyin, arti; sebanyak mungkin, minimal 3), kategori, catatan, keyakinan (yakin/perlu_dicek); xiehouyu tambah bagian_depan/bagian_belakang.
     Puisi dan lagu: judul (hanzi, pinyin, arti), jenis, pengarang dan zaman, sumber, baris (hanzi, pinyin, arti), catatan_bunyi (bunyi lama agar berima, mis. 斜 dibaca xiá), kata_sulit, keyakinan; lagu rakyat tambah status_hak_cipta.
   - **Aturan keras untuk AI penambang:** hanya karya bebas hak cipta atau tradisional; jangan mengarang; tulis "tidak yakin" bila ragu; teks tepat; pinyin bernada per suku kata; arti Indonesia sehari-hari; keluaran satu blok JSON. Tiga prompt dipisah (A pepatah, B puisi klasik, C lagu rakyat dan sajak anak); versi awal ada di riwayat percakapan 22 November 2026. **Prompt A dan B perlu diubah ke mode "mengisi" (menerima daftar entri dari data jadi)**; prompt C tetap.
   - Teks lagu dipelajari sebagai bacaan berirama tanpa musik (nada dalam lagu mengikuti melodi, bukan nada kata); urutan: chengyu/yanyu/xiehouyu → puisi pendek Tang dan 三字经 → teka-teki dan 绕口令 → lagu rakyat.
7. **Opsional kecil:** kalimat penjelas di halaman 艹; pemeriksaan arti pertama nama diri di `app_words.json`.
8. Backlog aktif lama tidak berubah (lihat v41/v42): pasangan penggolong + rantai kata kerja, 多音字, dikte, dashboard gabungan, skema kata 3+ karakter (1.287 kata), dan seterusnya.

## 6. Cara membuka aplikasi dan cara kerja repo

Tidak berubah dari v47 bagian 6: aplikasi dibuka lewat server lokal (Live Server) dari `C:\mandarin_app`; Claude membaca repo https://github.com/RuslanAlimuddin/mandarin_app (folder `blueprint/` untuk BLUEPRINT terbaru);
hasil skrip dan berkas baru diberikan lewat percakapan dan رسلان yang mengunggahnya (aplikasi unggah V6; klik folder tujuan dulu dan periksa baris "Tujuan unggah"). Setelah mengubah data, tekan **Ctrl+F5**.

**Jalur uji yang sudah dipastikan (sesi ini):**
- **Daftar "bukan" imbuhan:** Kamus → Kelompok → Awalan & Akhiran → klik —手 → kotak **"Mirip tetapi bukan (8)"** (举手, 握手, 二手, …). —学 harus 8, 老— harus 6, —者 tetap 3. Klik sebuah kata di kotak itu untuk mencarinya.
- **Deck Flashcard:** Flashcard → bilah samping bagian game → **🧱 Imbuhan (Awalan & Akhiran)** (angka **440**) atau **🧱 Pilih Imbuhan yang Tepat** (angka **298**) → isi kotak "jumlah kartu" → tombol hijau "🧱 Mulai Game".
- **Tautan varian radikal:** Kamus → Kelompok → Per Radikal → klik ⺮ (harus ada tombol "Lihat 竹 →" dan, di daftar, tanda ↔竹); klik 竹 di bagian "Lainnya" (harus ada "Bentuk varian: ⺮ →"). Ulangi untuk 攵↔攴 dan 罒↔网; 氵 tetap menaut ke 水.
- **Pilih yang Tepat:** Flashcard → 🎯 Pilih yang Tepat → soal untuk 生气, 请假, 下雪, 避免, 虑 kini bisa muncul.
- **Kata berpinyin kecil (Kamus → kolom cari):** 张扬 → **zhāng yáng**, arti pertama "memamerkan secara mencolok"; 星期天 → **xīng qī tiān**; 和平 → **hé píng**; 中国 → tetap **Zhōng guó** (kapital).

## Ringkasan status proyek

- Aturan 里, kamus terkurasi, `tone_drills.json` (v47): **selesai**.
- **Sesi 22–25 November: 80 kata berpinyin kapital (16 diubah, 64 sah), 23 soal "Pilih yang Tepat", tautan varian radikal, dua deck latihan imbuhan, daftar "bukan" imbuhan 40 → 142: selesai, teruji, terunggah.**
- Bahan budaya (pepatah, puisi, lagu rakyat): dirancang; menunggu hasil penambangan رسلان.
- Berikutnya: pilih dari bagian 5 (usul: Tingkat 3 akhiran, lalu pelajaran penunjuk posisi).

## 7. Pesan pembuka siap pakai untuk percakapan baru

Salin, lalu ganti bagian dalam tanda kurung siku:

```
Lanjutkan proyek Mandarin Interaktif. Tarik ulang repo
(https://github.com/RuslanAlimuddin/mandarin_app) dan baca
`blueprint/BLUEPRINT_v48.md` (bagian 1 tentang aturan kerja dan bagian 5 tentang rencana).
Butir yang ingin saya kerjakan: [nomor atau nama butir dari bagian 5].
Seperti biasa: diskusi dulu sebelum membuat kode atau berkas, instruksi uji dengan
jalur klik lengkap, tarik ulang repo sendiri, dan ingatkan berkas mana yang perlu saya unggah.
```

Untuk kurasi bahan budaya (percakapan terpisah), ganti butir dengan: "kurasi hasil penambangan pepatah/puisi/lagu rakyat (bagian 5 butir 6)" dan sebutkan folder tempat hasilnya disimpan di repo.

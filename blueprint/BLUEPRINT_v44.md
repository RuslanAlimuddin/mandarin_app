# BLUEPRINT v44 — Mandarin Interaktif

Lanjutan dari BLUEPRINT v43. Sesi ini (18 November 2026) menyelesaikan **semua butir rencana v43 bagian 5**: (d) varian radikal, (e) skrip beres-beres cadangan,
perbaikan kecil 闺女 (berkembang menjadi 11 perbaikan di `nuance_pairs.json`), dan beres-beres kecil data kata (儿, 圣诞, 焦糖玛奇朵).
Semuanya sudah dijalankan رسلان di PC, diuji, dan diunggah ke repo.

**v44 ringkas.** Untuk hal lama baca `BLUEPRINT_v43.md` (Paket Pembentukan Kata 构词法, pembersihan bacaan, aturan kerja lengkap).
`BLUEPRINT_v42.md` bagian 4 dan 5 **tidak lagi diperlukan** (butir (d) dan (e) sudah selesai).

---

## 1. Aturan kerja (v43 tetap berlaku; tambahan sesi ini)

- Semua aturan v43 bagian 1 tetap: diskusi dulu untuk setiap pekerjaan yang menghasilkan kode atau berkas; bahasa sederhana; menyebutkan ulang isi dan jumlah poin saat merujuk;
  **instruksi uji dengan jalur klik lengkap dari awal sampai tujuan**; pola skrip (lihat-dulu dan `--apply`, cadangan otomatis, menolak bila data berbeda, pemeriksaan akhir, aman diulang).
- **Tambahan pola skrip**: skrip menolak bekerja bila berkas JSON tidak bisa ditulis ulang **persis sama** (agar hanya isian yang disetujui yang berubah); pemeriksaan akhir
  membandingkan berkas hasil dengan rencana, dan semua berkas dikembalikan dari cadangan bila ada yang tidak cocok.
- Claude **menarik ulang repo sendiri** di awal tiap lanjutan dan setelah pengunggahan; kata "sudah saya unggah" hanyalah penanda.
- Skrip sekali pakai yang lama (mis. `perbaiki_frasa.py`, yang masih memuat tabel lama 纽扣儿) **jangan dijalankan ulang**.
- Bila Claude tidak yakin nama menu atau jalur klik persis, ia berterus terang dan meminta رسلان mengoreksi.
- Rutin sesudah banyak `--apply`: jalankan `python beres_cadangan.py` (lihat-dulu), lalu `--apply` bila daftarnya sesuai. Folder `arsip_cadangan_lama\` dihapus رسلان sendiri (yang kemarin sudah dihapus).

## 2. Selesai sesi ini (18 November 2026)

| Butir | Hasil | Berkas/skrip |
|---|---|---|
| (d) Varian radikal di Kamus → Kelompok → Per Radikal | 20 varian dari 186 entri. **13 varian** (氵 钅 扌 亻 纟 忄 讠 犭 饣 刂 衤 礻 灬) bertanda kecil "↔induk" (水 金 手 人 糸 心 言 犬 食 刀 衣 示 火) di tombolnya; urutan tombol **tidak dipindah**. Halaman varian: baris "氵 = bentuk varian dari 水" + tombol "Lihat 水 →"; halaman induk: "Bentuk varian: 氵 →". **艹 ⺮ 攵 罒**: hanya keterangan teks. **阝**: dipakai dua radikal, 阜 (kiri, mis. 阳) dan 邑 (kanan, mis. 都). **⺀ ⺳**: bentuk jarang, masing-masing 2 karakter (冬 枣; 罕 罙). Menu Per Komponen tidak berubah. 7 percobaan uji lolos | `kamus/kamus-komponen-posisi.js` (versi baru), `data/radikal_varian.json` (baru); `index_komponen_posisi.json` tidak diubah |
| (e) Beres-beres cadangan | Hanya berkas yang namanya memuat `.bak_`; "satu jenis" = folder + nama berkas asal + label; yang **terbaru tiap jenis tetap**, begitu juga yang kurang dari **2 hari**; sisanya dipindah ke `arsip_cadangan_lama\` (struktur folder ditiru, ada `_catatan_pemindahan_*.txt`), **tidak dihapus**. Umur dari tanggal berkas (di Windows: yang lebih baru antara dibuat dan diubah, karena `shutil.copy2` membawa tanggal ubah berkas asli). Zip checkpoint di `backups\`, `.git`, dan arsip **tidak disentuh** (diatur `checkpoint.py`). Hasil di PC: 31 jenis, 179 berkas (1.395,1 MB); **148 dipindah (1.262,9 MB)**, 31 tetap (132,2 MB). Arsip sudah dihapus | `beres_cadangan.py` |
| 11 perbaikan `nuance_pairs.json` (12 isian) | **9 salah ketik pinyin contoh**: 闺女 Guīniū→Guīnü; 食物 zugu→zugou; 导致 Landai→Landuo; 针对 zhuammen→zhuanmen; 登记 gaitai→guitai; 吩咐 mishi→mishu; 良知 quejia→quefa; 羞 xiūxiū→hàixiū; 急剧 jùjù→jíjù. **2 hanzi**: 想过→想到 (pasangan 想起/想到, id `b6_xiang_qi_223`), 的的→的 (`bA1_403`). **1 terjemahan**: 良知 menjadi "Dia kurang memiliki hati nurani dasar." (sebelumnya "akal sehat"). Efek samping baik: soal "Pilih yang Tepat" untuk 想起/想到 kini muncul (sebelumnya dilewati karena 想到 tidak ada di kalimatnya) | `perbaiki_nuance.py`, `data/nuance_pairs.json` |
| Beres-beres kecil data kata (84 perubahan; tepat 20 kata di `app_words.json`) | **儿**: 10 kata berpola "r5" (不一会儿 没法儿 小偷儿 胡同儿 名牌儿 有劲儿 有空儿 离谱儿 笑话儿 贪玩儿) dijadikan format normal; 纽扣儿 "er"→"r"; numerik 干女儿 (tadinya `null`) diisi `gan1 nü3 er2`; 20 salinan pinyin di `produktif_karakter.json`. **圣诞**: 7 kata benda biasa (树 歌 卡 晚餐 帽 袜 市场) huruf kecil; **圣诞节 dan 圣诞老人 tetap berkapital**. **焦糖玛奇果 → 焦糖玛奇朵**: id baru, traditional 焦糖瑪奇朵, pinyin duǒ, numerik duo3, zhuyin ㄉㄨㄛˇ, goresan 51→49, komponen 田→几, arti "karamel makiato"; akar 朵 kini punya 2 turunan | `perbaiki_kata_kecil.py`; `data/app_words.json`, `data/index_theme.json`, `data/produktif_karakter.json`, `skrip/build_theme_entries.py` (generator tema ikut diperbaiki agar salah ketik tidak kembali) |

## 3. Catatan penting untuk sesi berikutnya

- **Format erhua 儿**: pinyin tampil berspasi dan berakhir " r" (mis. "yī huì r"), numerik berakhir "r5" (mis. "yi1 hui4 r5"). 儿 yang suku kata sungguhan memakai "ér"/"er2" (女儿 "nǚ ér", "nü3 er2").
  干女儿 pinyin tampilnya "gānnǚ'ér" (tanpa spasi) dibiarkan.
- **Huruf kapital pinyin**: nama perayaan dan nama diri berkapital (春节, 中秋节, 端午节, 国庆节, 圣诞节, 圣诞老人, 上帝, nama negara/kota), kata benda biasa huruf kecil. 元旦 saat ini huruf kecil.
- **Kolom `pinyin_numeric`** dipakai permainan nada Flashcard dan pencarian Kamus (v43). Perubahan kapital 圣诞 ikut ke kolom ini ("sheng4 dan4 shu4").
- **Cara memeriksa pinyin contoh di `nuance_pairs.json`**: kalimat contoh (`example_cn` + `example_pinyin`) dicocokkan **huruf demi huruf** dengan bacaan CC-CEDICT (`data/cidict_index.json.gz`) dan bacaan karakter di `app_words.json`. Ini menangkap salah ketik huruf,
  **belum salah tanda nada**. Sisa 15 hasil sudah diperiksa satu per satu dan semuanya positif palsu: 14 ü yang ditulis "u" di contoh tanpa nada (旅, 策略, 子女) dan 1 "T恤".
- **Permainan "Pilih yang Tepat"** (`flashcard/flashcard-games.js`) melewati soal bila `word` tidak ada di `example_cn`-nya sendiri. Setelah perbaikan masih ada **22 dari 2.584** kasus semacam itu; sebagian karena kata terpisah (生气 dalam "生我的气",
  请假 dalam "请了一天假"), sebagian karena bentuk lain (国家 → 大国). **Belum ditinjau satu per satu.**
- **Induk 竹 攴 网** ternyata sudah punya tombol di bagian "Lainnya (data posisi belum tersedia)" (2, 4, 11 karakter); hanya 艸 yang tidak ada. Jadi varian ⺮ 攵 罒 kelak bisa ditautkan ke tombol yang sudah ada tanpa membuat tombol baru.
- **Filter posisi** (kiri/kanan/atas/bawah/luar/dalam) di Per Radikal/Per Komponen: **sudah terpenuhi** (halaman hasil punya filter Posisi); bukan butir terbuka lagi.
- Generator tema `skrip/build_theme_entries.py` menyimpan pinyin dan arti kata tema; kini sudah selaras dengan data. Id kartu 焦糖玛奇朵 baru: bila dulu ada di SRS, kartunya tampil sebagai kartu baru.

## 4. Berkas baru atau berubah di repo (ringkas)

Skrip di akar repo (baru): `beres_cadangan.py`, `perbaiki_nuance.py`, `perbaiki_kata_kecil.py`.
Data baru: `data/radikal_varian.json`. Kode berubah: `kamus/kamus-komponen-posisi.js`.
Data berubah: `data/nuance_pairs.json`, `data/app_words.json`, `data/index_theme.json`, `data/produktif_karakter.json`; skrip berubah: `skrip/build_theme_entries.py`.
**Tidak** diunggah: berkas `.bak_*` dan folder `arsip_cadangan_lama\`.

## 5. Rencana ke depan (belum diputuskan; pilih saat sesi berikutnya)

1. **716 dari 2.584 contoh pinyin** di `nuance_pairs.json` ditulis **tanpa tanda nada** (28%). Perlu dibahas dulu: nada kata berbacaan ganda tidak bisa ditebak begitu saja (bisa bersumber dari bacaan terkurasi di `app_words.json`).
2. **Penulisan ü bercampur** di contoh tanpa nada: "nvhai", "Zinu", "luyou" (v, u, dan ü dipakai bergantian).
3. **Nada pada 1.868 contoh bertanda nada belum diperiksa** (pemeriksa saat ini hanya huruf).
4. **22 soal "Pilih yang Tepat" yang dilewati** (lihat bagian 3): tinjau apakah kalimatnya perlu disesuaikan.
5. **Penyegaran `tone_drills.json`** lewat generator `skrip/dari_py/generate_tone_drills.py` (±36 grup dan ±239 butir tertinggal). **Jangan meregenerasi `wb_pools.json`** (dikurasi manual).
6. **Pelajaran Pilar 3 (量词)** yang asli, lewat GPT dengan pesan serah terima.
7. **Tingkat 3 awalan/akhiran** (族 迷 热 控 症 剂 炎 盲, penunjuk posisi 上 下 里 外 中 间, 边) dan **latihan awalan/akhiran** (Flashcard, Word Builder, Ujian HSK).
8. **Tautan varian ⺮ 攵 罒** ke tombol 竹 攴 网 yang sudah ada (opsional, kecil).
9. Backlog aktif lama tidak berubah (lihat catatan proyek dan v41/v42): pasangan penggolong + rantai kata kerja, 多音字, dikte, dashboard gabungan, skema kata 3+ karakter (1.287 kata), dan seterusnya.

## 6. Cara membuka aplikasi dan cara kerja repo

Tidak berubah dari v42 bagian 8 dan v43 bagian 6. Ringkas: aplikasi dibuka lewat server lokal (Live Server) dari `C:\mandarin_app`; Claude membaca repo
https://github.com/RuslanAlimuddin/mandarin_app (folder `blueprint/` untuk BLUEPRINT terbaru); hasil skrip/berkas baru diberikan lewat percakapan dan رسلان yang mengunggahnya.

## Ringkasan status proyek

- Paket Pembentukan Kata, pembersihan bacaan dan data (v43): **selesai**.
- Sesi 18 November: varian radikal, beres-beres cadangan, 11 perbaikan `nuance_pairs.json`, beres-beres kecil data kata (儿, 圣诞, 焦糖玛奇朵): **selesai, teruji, dan terunggah**.
- Berikutnya: pilih dari bagian 5 menurut minat رسلان.

## 7. Pesan pembuka siap pakai untuk percakapan baru

Salin, lalu ganti bagian dalam tanda kurung siku:

```
Lanjutkan proyek Mandarin Interaktif. Tarik ulang repo
(https://github.com/RuslanAlimuddin/mandarin_app) dan baca
`blueprint/BLUEPRINT_v44.md` (bagian 1 tentang aturan kerja dan bagian 5 tentang rencana).
Butir yang ingin saya kerjakan: [nomor atau nama butir dari bagian 5].
Seperti biasa: diskusi dulu sebelum membuat kode atau berkas, instruksi uji dengan
jalur klik lengkap, dan tarik ulang repo sendiri.
```

# Laporan Tahap 1 — Data Kamus Pembentukan Kata (构词法)

Tanggal: 13 November 2026  
Repositori: `RuslanAlimuddin/mandarin_app`  
Ruang kerja: `kerja_gpt_afiks/`

## 1. Hasil yang dibuat

- `hasil/afiks_kamus.json`: **60 entri** (43 akhiran dan 17 awalan), kelompok A–J.
- `hasil/afiks_kamus_SKEMA.md`: penjelasan seluruh kolom dan aturan isi.
- Daftar tetap 60 entri. `小`, `边`, dan `副` tidak ditambahkan.
- Tidak ada entri yang memakai posisi `keduanya`: pada contoh yang ditinjau, beberapa karakter yang muncul di posisi berlawanan berfungsi sebagai unsur kata biasa/akar, bukan imbuhan kedua. Catatan pembeda dicantumkan pada entri terkait.

## 2. Pemeriksaan yang dijalankan

Pemeriksaan dilakukan langsung terhadap `data/app_words.json` (11.983 entri).

| Pemeriksaan | Hasil |
|---|---:|
| Entri Kamus | 60 |
| Kata contoh unik | 296 |
| Kata contoh + daftar “bukan” unik | 335 |
| Kata yang ditemukan persis di kolom `simplified` | 335 |
| Kata yang tidak ditemukan | **0** |
| JSON berhasil dibaca ulang (parse) | Ya |
| Jumlah kelompok | A–J, 10 kelompok |

Hitungan 335 kata unik sesuai hitungan pemeriksa Claude yang disampaikan pada serah terima. Semua kata contoh dan kata pembanding yang tercantum pada daftar 60 entri ditemukan di kamus. Tidak ada kata yang diganti.

Pinyin entri menggunakan tanda nada. Untuk 8 karakter yang tidak memiliki entri mandiri di `app_words.json` (师、观、论、馆、器、机、物、儿), bacaan diambil dari kata contoh yang ada dan dijelaskan di kolom catatan. Beberapa bacaan mengikuti fungsi pada contoh, bukan bacaan lain karakter tersebut: 长 = zhǎng, 率 = lǜ, 量 = liàng, 场 = chǎng. 子 dan 们 pada fungsi akhiran menggunakan nada netral.

## 3. Catatan dan temuan (hanya dilaporkan, tidak diperbaiki)

### 3.1 Sisa penanda `[citation:n]` pada kategori awalan/akhiran

Tidak ada penanda sitasi yang disalin ke berkas baru. Penanda yang masih berada di berkas Tata Bahasa asli hanya dilaporkan di sini; tidak dibersihkan.

**HSK 5 — `data/grammar_hsk5.json`, kategori Prefix & Suffix, total 8 sisa:**

| Poin | Jumlah | Lokasi |
|---|---:|---|
| 11.1 化 | 3 | `fungsi` |
| 11.2 性 | 1 | `fungsi` |
| 11.3 度 | 1 | `fungsi` |
| 11.4 老 | 2 | `fungsi` |
| 11.5 阿 | 1 | `fungsi` |

**HSK 6 — `data/grammar_hsk6.json`, kategori 准前缀/准后缀, total 10 sisa:**

| Poin | Jumlah | Penanda |
|---|---:|---|
| 1.1 超— | 1 | `[citation:1]` |
| 1.2 多— | 1 | `[citation:1]` |
| 1.3 反— | 1 | `[citation:1]` |
| 1.4 无— | 1 | `[citation:1]` |
| 1.5 亚— | 1 | `[citation:1]` |
| 1.6 准— | 1 | `[citation:1]` |
| 1.7 —化 | 1 | `[citation:1]` |
| 1.8 —式 | 1 | `[citation:1]` |
| 1.9 —型 | 1 | `[citation:1]` |
| 1.10 —性 | 1 | `[citation:1]` |

Poin 1.11 tidak memiliki sisa penanda pada bagian kategori ini.

**HSK 9 — `data/grammar_hsk9.json`, kategori 准词缀, total 11 sisa:**

| Poin | Jumlah | Lokasi |
|---|---:|---|
| 1.1 准前缀 | 3 | `fungsi` (1), `reference_table.rows[0]` (1), `reference_table.rows[1]` (1) |
| 1.2 准后缀 | 8 | `fungsi` (1), tujuh baris `reference_table.rows[0–6]` (7) |

Jumlah pada kategori yang diperiksa: **29 sisa** (HSK 5: 8, HSK 6: 10, HSK 9: 11). Sebagai konteks keseluruhan, angka audit yang disampaikan pada serah terima untuk semua berkas `grammar_hsk5.json` sampai `grammar_hsk9.json` adalah 437 penanda: HSK 5 = 136, HSK 6 = 113, HSK 7 = 45, HSK 8 = 12, HSK 9 = 131. Pembersihan semua penanda tersebut berada di luar tugas Tahap 1.

### 3.2 Catatan fungsi 们、子、儿、头 pada `data/kata_majemuk_pola.json`

Jumlah kata yang berakhir dengan karakter terkait di data pola: 们 = 7, 子 = 128, 儿 = 17, 头 = 46.

- **们:** tujuh catatan yang diperiksa menyebut fungsi penanda jamak; tidak ditemukan ketidaksesuaian yang jelas.
- **子:** ditemukan **48 kata** yang diberi pola `偏正式` tetapi keterangannya sendiri menyebut 子 sebagai “sufiks”. Daftar: 孩子, 儿子, 房子, 样子, 日子, 肚子, 脑子, 鼻子, 帽子, 脖子, 桌子, 裤子, 狮子, 屋子, 椅子, 兔子, 镜子, 例子, 片子, 种子, 裙子, 牌子, 猴子, 面子, 箱子, 影子, 身子, 杯子, 盒子, 胡子, 院子, 袜子, 瓶子, 绳子, 靴子, 橘子, 圈子, 嗓子, 被子, 鸭子, 帖子, 位子, 盘子, 鸽子, 架子, 虫子, 胆子, 蚊子. Ini tidak selaras dengan perlakuan pada `筷子` (pola `lainnya`, catatan “子 hanya berfungsi sebagai sufiks nomina”). Contoh yang paling jelas dan relevan dengan daftar 60 ialah `桌子`, `椅子`, dan `房子`.
- **儿:** catatan untuk bentuk erhua dan kata penunjuk tempat yang diperiksa konsisten dengan pola `lainnya`; tidak ditemukan ketidaksesuaian jelas.
- **头:** ada lima catatan yang perlu diperiksa: `石头`, `木头`, `骨头`, dan `舌头` menjelaskan 头 sebagai “kepala”, padahal pada contoh afiks yang disetujui 头 berfungsi sebagai akhiran kata benda; `里头` menyebut 头 sebagai “sufiks” tetapi polanya `偏正式`. Temuan ini hanya dicatat, tidak diubah.

### 3.3 Kata yang tidak dipakai

`准妈妈` **tidak dipakai** sebagai kata contoh. Entri 准 diberi catatan bahwa fungsinya sebagai awalan sangat lemah; contoh yang dipertahankan mengikuti daftar yang disetujui Ruslan.

### 3.4 Catatan pinyin dan cakupan

- Delapan karakter target di atas tidak mempunyai entri karakter tunggal pada `app_words.json`; pinyin dibaca dari contoh yang benar-benar ada. Ini bukan berarti kata contohnya hilang.
- Pada karakter yang memiliki beberapa bacaan, pinyin entri mengikuti fungsi contoh: 长 (zhǎng), 率 (lǜ), 量 (liàng), 场 (chǎng).
- `小` dan `边` tetap tidak dibuat sebagai entri baru. Rujukan lama dicatat pada entri `第` (HSK 1 poin 56) dan `们` (HSK 1 poin 57); `边` tetap menunggu pembahasan Tingkat 3.
- Pinyin salah yang sudah diketahui pada kata 重点 (chóngdiǎn seharusnya zhòngdiǎn) tidak diperbaiki karena berada di luar folder dan ruang kerja Tahap 1.

## 4. Berkas yang dibuat

Hanya berkas berikut yang ditambahkan di dalam `kerja_gpt_afiks/`:

1. `kerja_gpt_afiks/hasil/afiks_kamus.json`
2. `kerja_gpt_afiks/hasil/afiks_kamus_SKEMA.md`
3. `kerja_gpt_afiks/laporan/tahap1_kamus.md`

Tidak ada berkas sumber yang disalin pada Tahap 1. Tidak ada berkas di luar `kerja_gpt_afiks/` yang diubah. Tidak ada kode HTML, JavaScript, atau CSS yang dibuat/diubah.

## 5. Status

Tahap 1 selesai. Data Kamus siap diperiksa Claude. Tahap 2 (Tata Bahasa) dan Tahap 3 (Pilar 12) belum dikerjakan.

Menunggu perintah LANJUT dari Ruslan.

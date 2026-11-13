# Laporan Audit Tahap 0 — Pembentukan Kata (构词法)

Tanggal audit: 13 November 2026  
Repositori: `RuslanAlimuddin/mandarin_app`  
Cabang: `main`  
Commit dasar yang diperiksa: `46ead1097a1ed52d4d5129d51f2a4bfe85e6d0bf`

## Ringkasan

Tahap 0 selesai sebagai audit baca-saja. Tidak ada berkas asli aplikasi yang diubah, dihapus, dipindahkan, atau diganti nama. Tidak ada kode HTML, JavaScript, atau CSS yang dibuat atau diubah.

Hasil pencocokan seluruh daftar kata pada rancangan 60 entri:
- Jumlah entri rancangan: 60 (43 akhiran dan 17 awalan).
- Jumlah kata unik yang diperiksa, termasuk daftar "bukan": 340.
- Ditemukan di `data/app_words.json`: 340.
- Tidak ditemukan: 0.

Catatan hitungan: bentuk `主义` terdiri dari dua karakter tetapi disetujui sebagai satu bentuk imbuhan/entri. Karena itu, 60 bentuk entri tersebut menggunakan 61 karakter Hanzi yang berbeda.

## 1. Inventaris bahan yang sudah tersedia

### 1.1 Kamus dan data kosakata

| Berkas | Isi/jumlah | Keterangan |
|---|---:|---|
| `data/app_words.json` | 11.983 entri | Memuat antara lain `simplified`, `pinyin`, `hsk`, `meanings_id`, dan data kata lainnya. Ini menjadi sumber pemeriksaan keberadaan kata contoh. |
| `data/produktif_karakter.json` | 1.389 karakter akar | Setiap karakter mempunyai informasi akar dan daftar kata turunannya. |
| `data/kata_majemuk_pola.json` | 8.867 kata | Data pola pembentukan kata majemuk; bukan daftar imbuhan. |
| `data/char_etymology_id.json` | 1 berkas | Data asal-usul karakter; bukan materi afiks utama. |

Pola pada `kata_majemuk_pola.json` berjumlah:
- 偏正式: 3.830
- 联合式: 2.671
- 动宾式: 1.447
- lainnya: 540
- 补充式: 358
- 主谓式: 21

Kolom utama berkas pola kata majemuk adalah `word`, `pola`, dan `keterangan_id`. Contoh `我们`, `他们`, `你们`, `人们`, dan `咱们` sudah diberi catatan bahwa 们 berfungsi sebagai penanda jamak. Contoh seperti `桌子`, `椅子`, `房子`, dan `筷子` juga memiliki catatan mengenai fungsi 子. Ini perlu diselaraskan dengan penjelasan afiks agar tidak bertentangan.

Halaman `kamus.html` memiliki panel "Pola Pembentukan Kata" yang memakai `kamus/kamus-pola.js` dan data `data/kata_majemuk_pola.json`. Keterangan pada halaman menyebut panel tersebut ditampilkan untuk kata dua karakter yang tersedia di data. Fitur ini menjelaskan susunan internal kata majemuk, sehingga cakupannya berbeda dari pembahasan awalan dan akhiran.

### 1.2 Tata Bahasa

Tersedia sembilan berkas:
`data/grammar_hsk1.json` sampai `data/grammar_hsk9.json`.

Pemetaan topik di `tatabahasa.html` menggabungkan kategori-kategori mentah dari sembilan berkas tersebut ke dalam topik induk "Prefix & Suffix (Imbuhan)". Komentar di halaman menyebut pemetaan manual tersebut mencakup 132 kategori mentah. Jadi, pemeriksaan tidak boleh hanya melihat nama kategori pada satu tingkat HSK.

Materi yang secara langsung berkaitan dengan awalan/akhiran atau bentuk imbuhan ditemukan sebagai berikut:

| Tingkat | Lokasi | Isi yang ditemukan |
|---|---|---|
| HSK 1 | Kategori "AWALAN & AKHIRAN", poin 56–57 | 小— dan 第—; —们 dan —边. |
| HSK 2 | Poin 12.5 | Keterangan akhiran —面 pada kata arah. |
| HSK 3 | Kategori "Prefix & Suffix", poin 11.1–11.3 | 老—, —家, dan —员. Poin 16.3 membahas —子. |
| HSK 4 | Kategori "Prefix & Suffix", poin 11.1–11.4 | 老—, —家, —员, dan —化. |
| HSK 5 | Kategori "Prefix & Suffix", poin 11.1–11.5 | —化, —性, —度, 老—, dan 阿—. |
| HSK 6 | Kategori "准前缀/准后缀", poin 1.1–1.11 | 超—, 多—, 反—, 无—, 亚—, 准—, —化, —式, —型, —性, dan —度. |
| HSK 9 | Kategori "准词缀", poin 1.1–1.2 | 后—, 亲—, —观, —鬼, —界, —然, —坛, —为, dan —制. |

Jumlah lokasi poin yang berkaitan langsung: 29 poin, dengan beberapa bentuk berulang di beberapa tingkat. HSK 7 dan HSK 8 tidak menunjukkan kategori khusus awalan/akhiran dalam pemeriksaan nama dan isi kategori.

**Ketidaksesuaian dengan ringkasan awal proyek:** materi yang sudah ada ternyata bukan hanya HSK 1 poin 56–57, HSK 3 poin 16.3, dan HSK 9. HSK 2 poin 12.5 serta materi HSK 3 poin 11.1–11.3, HSK 4, HSK 5, dan HSK 6 juga harus masuk daftar acuan. HSK 9 juga memiliki —鬼 dan —为, selain bentuk yang disebut dalam ringkasan proyek.

### 1.3 Pelajaran Pilar

Tersedia Pilar 1 sampai Pilar 11. Pemeriksaan bagian yang berkaitan menemukan:

| Pilar | Temuan |
|---|---|
| Pilar 1 — Fonetik dan Sistem Pelafalan | Salah satu tabel nada netral menyebut 子 dan 头 sebagai sufiks pembentuk kata benda tertentu serta 们 sebagai penanda jamak. |
| Pilar 4 — Partikel Struktural dan Aspek | Tidak ditemukan bagian khusus pembentukan kata/afiks dalam pemeriksaan isi. |
| Pilar 8 — Kata Ganti, Penunjuk, dan Sistem Sapaan | Membahas 们 sebagai penanda jamak dan 儿/儿化 pada kata penunjuk tempat. |
| Pilar 9 — Kata Sifat, Reduplikasi, dan Intensifikasi | Tidak ditemukan bagian khusus pembentukan kata/afiks dalam pemeriksaan isi. |
| Pilar 11 — Variasi Bahasa, Sejarah, dan Perkembangan Modern | Menyebut perbedaan kata majemuk dua karakter dalam Mandarin modern dan kecenderungan satu karakter sebagai kata dalam bahasa klasik; sifatnya pengantar umum, bukan pelajaran afiks. |

Pilar 12 belum ada di folder `data/pelajaran/`.

Catatan yang sudah disebut dalam dokumen proyek: `pilar_3.json` merupakan materi Kata Kerja Modal yang juga terdapat pada `pilar_5.json`; masalah ini hanya dicatat dan tidak diperbaiki pada Tahap 0.

### 1.4 Halaman aplikasi yang diperiksa

Halaman yang dibaca tanpa diubah:
- `kamus.html`
- `tatabahasa.html`
- `peta-bahasa.html`
- `wordbuilder.html`

Halaman Tata Bahasa memiliki pemetaan kategori menuju topik "Prefix & Suffix (Imbuhan)". Halaman Kamus memiliki panel pola pembentukan kata majemuk yang terhubung dengan berkas pola. Tidak ada halaman atau kode aplikasi yang diubah pada tahap ini.

## 2. Tumpang tindih dengan rancangan 60 entri

### 2.1 Bentuk yang sudah dibahas dalam Tata Bahasa

- **HSK 1:** 第 dan 们 termasuk dalam rancangan 60 entri. Keduanya harus diberi tanda pendalaman dan rujukan ke poin lama 56 dan 57. 小 dan 边 sudah ada di poin lama, tetapi belum termasuk daftar 60.
- **HSK 2:** —面 sudah dibahas pada poin 12.5, tetapi tidak termasuk daftar 60.
- **HSK 3:** 老, 家, dan 员 sudah dibahas pada poin 11.1–11.3; 子 sudah dibahas pada poin 16.3. Entri baru untuk 子 harus ditandai sebagai pendalaman dan merujuk poin 16.3.
- **HSK 4:** 老, 家, 员, dan 化 berulang dengan cakupan rancangan baru.
- **HSK 5:** 化, 性, 度, dan 老 berulang; 阿 tidak termasuk daftar 60.
- **HSK 6:** 超, 反, 无, 准, 化, 式, 型, 性, dan 度 berulang; 多 dan 亚 tidak termasuk daftar 60.
- **HSK 9:** 观 dan 界 termasuk dalam rancangan 60; 后, 亲, 鬼, 然, 坛, 为, dan 制 berada di luar cakupan 60.

### 2.2 Tumpang tindih dengan Pilar dan data lain

- 子, 头, dan 们 telah disebut secara ringkas di Pilar 1.
- 们 dan 儿 telah dibahas di Pilar 8.
- Sebagian kata contoh berimbuhan juga tercatat dalam data pola kata majemuk, terutama bentuk dengan 们, 子, 儿, dan 头.
- Data Akar Kosakata dapat menjadi rujukan tambahan untuk hubungan karakter dengan kata turunannya, tetapi bukan pengganti penjelasan fungsi afiks.

### 2.3 Bentuk yang perlu dibedakan dari imbuhan

Keberadaan suatu karakter di awal atau akhir kata tidak otomatis menjadikannya awalan atau akhiran. Contohnya:
- 家 pada 作家 berfungsi sebagai unsur pembentuk nama pelaku/profesi; 家 pada 家庭, 家人, atau 家乡 bermakna keluarga/rumah.
- 手 pada 歌手 berbeda fungsi dari 手 pada 手机 atau 手套.
- 机 pada 手机 sebagai unsur akhir tidak otomatis menjadikan 机 pada 机场 atau 机器 sebagai awalan.
- 学 pada 科学/文学 dan 学 pada 学生/学校 sama-sama unsur pembentuk kata, tetapi tidak otomatis merupakan sufiks dan prefiks gramatikal.
- Karakter seperti 力, 场, 同, 总, 部, 院, 站, 物, 观, 法, dan 业 juga muncul di posisi awal maupun akhir pada sejumlah kata. Posisi tersebut harus diperiksa bersama fungsi dan maknanya, bukan dijadikan dasar tunggal untuk mengisi `posisi: "keduanya"`.

Usulan: gunakan posisi "keduanya" hanya bila fungsi pembentukan kata sebagai awalan dan akhiran memang dapat dijelaskan secara terpisah dengan contoh yang tepat. Jika salah satu posisi hanya merupakan akar kata biasa, letakkan sebagai catatan atau contoh "bukan", bukan sebagai fungsi afiks kedua.

## 3. Celah yang ditemukan dan usulan pelengkapan

Usulan berikut belum diterapkan. Perubahan terhadap materi lama hanya boleh dilakukan pada Tahap 4 jika disetujui.

1. **Contoh dan batas fungsi pada Tata Bahasa lama masih ringkas.** Beberapa poin hanya menampilkan satu pola atau beberapa contoh, tanpa pembeda kata yang mirip tetapi bukan afiks. Usulan: biarkan poin lama tetap, lalu tautkan ke entri baru yang memberi fungsi, arti, contoh, dan daftar "bukan".
2. **Materi tersebar di banyak tingkat HSK.** Bentuk yang sama muncul di HSK 3, 4, 5, dan 6. Usulan: jadikan daftar 60 entri sebagai rujukan terpusat, sedangkan poin lama tetap menjadi jalur belajar berdasarkan tingkat.
3. **Pilar 1 dan Pilar 8 hanya memberi pengantar terbatas.** Usulan: Pilar 12 memberi penjelasan sistematis tentang awalan, akhiran, karakter yang memiliki beberapa makna, dan perbandingan bentuk.
4. **Data pola kata majemuk dan data afiks berpotensi membingungkan.** Usulan: jelaskan perbedaan antara unsur pembentuk kata majemuk dan imbuhan yang mempunyai fungsi pembentukan kata. Jangan mengubah klasifikasi lama pada Tahap 0.
5. **Akar Kosakata tidak mencakup semua karakter rancangan.** Dari 61 karakter Hanzi yang digunakan dalam 60 bentuk entri, hanya 52 ditemukan di `produktif_karakter.json`; sembilan yang tidak ditemukan adalah 师、观、论、馆、器、机、物、儿、义. Usulan: catat sebagai celah keterhubungan data; jangan menambah atau mengubah Akar Kosakata dalam proyek ini tanpa instruksi tersendiri.
6. **HSK 9 masih memiliki penanda sitasi sisa.** Teks `[citation:1]` masih terlihat pada fungsi dan keterangan tabel kategori 准词缀. Usulan: bersihkan pada pekerjaan perbaikan terpisah yang disetujui, bukan pada Tahap 0.
7. **Pinyin 重点 perlu diperbaiki pada sumber kamus.** Di `app_words.json` tertulis `chóng diǎn`; bacaan yang benar untuk kata "titik utama/poin penting" adalah `zhòng diǎn`. Ini temuan yang sudah diketahui dan tidak diubah.
8. **Konsistensi cakupan perlu dijaga untuk 主义.** Daftar yang disetujui menghitung 主义 sebagai satu bentuk entri, walaupun terdiri dari dua karakter. Usulan: pertahankan sebagai satu bentuk imbuhan dalam satu entri, jangan memecahnya menjadi dua entri karakter.

## 4. Hasil pencocokan kata contoh

Pemeriksaan dilakukan dengan membaca seluruh `data/app_words.json` dan mencocokkan kolom `simplified` secara persis.

| Pemeriksaan | Hasil |
|---|---:|
| Jumlah entri rancangan | 60 |
| Jumlah kata unik, termasuk daftar "bukan" | 340 |
| Kata ditemukan | 340 |
| Kata tidak ditemukan | 0 |

Tidak ada kata contoh yang perlu dilaporkan sebagai tidak ditemukan. Sesuai aturan proyek, tidak ada kata yang diganti.

Pinyin di tahap ini tidak diubah. Untuk tahap penyusunan data berikutnya, pinyin kata yang tersedia harus mengikuti nilai pada kolom `pinyin` di `app_words.json`, sambil tetap menandai temuan salah yang sudah diketahui seperti 重点.

## 5. Pendapat tentang 小 dan 边

Rekomendasi saya: **jangan menambahkan 小 dan 边 ke dalam 60 entri baru pada saat ini**.

Alasannya:
- 小— sudah dibahas di HSK 1 poin 56.
- —边 sudah dibahas di HSK 1 poin 57.
- Keduanya tidak termasuk daftar 60 yang telah disetujui.
- Memasukkannya sekarang akan mengubah cakupan menjadi 62 bentuk dan menambah pengulangan sebelum ada keputusan pemilik proyek.

Keduanya dapat tetap menjadi materi lama. Jika kelak diperlukan pendalaman yang lebih lengkap, hal itu dapat diputuskan sebagai pekerjaan tersendiri. Tidak ada perubahan terhadap keputusan 60 entri.

## 6. Daftar berkas dan batas perubahan

### Berkas sumber yang diperiksa

- `data/app_words.json`
- `data/grammar_hsk1.json` sampai `data/grammar_hsk9.json`
- `data/pelajaran/pilar_1.json` sampai `data/pelajaran/pilar_11.json`
- `data/produktif_karakter.json`
- `data/kata_majemuk_pola.json`
- `data/char_etymology_id.json`
- `kamus.html`
- `tatabahasa.html`
- `peta-bahasa.html`
- `wordbuilder.html`

### Berkas baru dalam folder kerja

- `kerja_gpt_afiks/acuan/.gitkeep`
- `kerja_gpt_afiks/hasil/.gitkeep`
- `kerja_gpt_afiks/laporan/tahap0_audit.md`

Tidak ada berkas sumber yang disalin ke `acuan/`, karena Tahap 0 hanya audit baca-saja dan belum ada berkas sumber yang perlu diolah. Folder `hasil/` juga belum berisi data pelajaran; hanya disiapkan untuk tahap berikutnya.

Tidak ada berkas di luar `kerja_gpt_afiks/` yang diubah.

## 7. Pemeriksaan mutu Tahap 0

- Membaca dan memeriksa struktur data sumber yang relevan.
- Memastikan jumlah entri `app_words.json` dan mencocokkan seluruh 340 kata unik terhadap kolom `simplified`.
- Memeriksa struktur kategori dan poin Tata Bahasa HSK 1–9.
- Memeriksa bagian relevan Pilar 1–11.
- Menghitung jumlah karakter akar dan memeriksa ketercakupan 61 karakter sasaran.
- Menghitung jumlah data dan kategori pola kata majemuk.
- Memastikan tidak ada data aplikasi asli yang diubah.

**Status:** Tahap 0 selesai. Tidak ada JSON baru yang dibuat pada tahap ini, sehingga pemeriksaan parse JSON untuk hasil Tahap 1–3 belum berlaku.

Menunggu perintah LANJUT dari Ruslan.

# Laporan Tahap 3 — Pelajaran Pilar 12: Pembentukan Kata (构词法)

Tanggal: 13 November 2026  
Repositori: `RuslanAlimuddin/mandarin_app`  
Ruang kerja: `kerja_gpt_afiks/`

## 1. Skema yang ditiru
Sebelum menulis, saya membaca `data/pelajaran/pilar_4.json` dan `data/pelajaran/pilar_9.json`. Skema yang ditiru persis pada struktur utama adalah:
- Tingkat atas: `pilar`, `judul`, `ringkasan`, `bagian`.
- Setiap unsur `bagian`: `judul` dan `isi`.
- Blok `isi`: `tipe` dengan kolom sesuai jenis blok, yaitu `paragraf/teks`, `poin/daftar`, `tabel/kolom/baris`, `contoh/daftar`, dan `peringatan/teks`.
Tidak menambahkan struktur baru di luar skema tersebut.

## 2. Hasil yang dibuat
Berkas `hasil/pilar_12.json` selesai dengan judul **Pembentukan Kata (构词法)** dan enam bagian:
1. Apa itu awalan dan akhiran Mandarin serta perbedaannya dengan imbuhan Indonesia.
2. Cara membaca kartu entri Kamus.
3. Karakter bermakna ganda: 家、生、长、率、手、点、化、头.
4. Perbandingan tujuh akhiran pelaku: 者、家、员、师、生、手、长.
5. Lima awalan penolak/peniadaan: 不、无、非、未、反.
6. Peta sepuluh kelompok untuk 60 entri dan materi yang dapat menyusul kelak.

Isi menggunakan blok paragraf, poin, tabel, contoh, dan peringatan. Pinyin contoh ditulis dengan tanda nada dan huruf awal kalimat kapital. Daftar contoh pokok diselaraskan dengan `afiks_kamus.json` dan `grammar_afiks.json`; daftar 60 entri tidak diubah.

## 3. Pemeriksaan yang dijalankan
- JSON berhasil diparse ulang.
- Struktur tingkat atas: 4 kunci sesuai contoh Pilar 4 dan Pilar 9.
- Jumlah bagian: 6.
- Jumlah blok isi: 31.
- Jenis blok yang dipakai: paragraf, tabel, contoh, peringatan, poin.
- Peta cepat memuat 10 kelompok A–J; jumlahnya 60 entri (43 akhiran + 17 awalan).
- Tidak ditemukan teks `[citation:n]` atau penggunaan `准妈妈`.
- Tidak ada berkas di luar `kerja_gpt_afiks/` yang diubah.

## 4. Keraguan dan daftar pemeriksaan manusia
Mohon periksa khususnya:
1. **非 pada 非常:** Pilar menjelaskan bahwa 非常 adalah kata utuh yang berarti “sangat”, bukan penyangkalan harfiah. Namun, pengelompokan 非 sebagai awalan penolak untuk kata ini perlu dikonfirmasi agar tidak mengajarkan pemecahan yang menyesatkan.
2. **Perbedaan 作者 dan 作家:** 作者 diterjemahkan sebagai penulis suatu karya; 作家 sebagai penulis/sastrawan profesional. Nuansa ini perlu dipastikan sesuai tingkat penyederhanaan yang diinginkan.
3. **Karakter 长 dan 率:** pastikan contoh dan pembedaan bacaan zhǎng/cháng serta lǜ/shuài sudah cukup jelas bagi pelajar pemula.
4. **Karakter 化 dan 头:** pastikan pembeda antara akhiran pembentuk kata dan bagian kata utuh sudah tidak memberi kesan bahwa semua kata berakhiran karakter tersebut mempunyai fungsi yang sama.
5. **Klasifikasi tujuh akhiran pelaku:** batas antara 者、家、员、师、生、手、长 merupakan kecenderungan makna, bukan aturan mutlak. Perlu penilaian manusia apakah uraian cukup sederhana dan tidak terlalu kaku.
6. **Pinyin serta kewajaran semua contoh tambahan Pilar 12:** periksa ulang terutama kalimat tentang 校长、漫长、效率、坦率、手机、非常, serta pemenggalan suku kata pada pinyin.
7. **Kecocokan kosakata Pilar 12 dengan app_words.json:** data kamus utama terlalu besar untuk diambil utuh melalui pembacaan repositori pada sesi ini. Daftar 60 contoh pokok sebelumnya telah lolos pencocokan Tahap 1; pemeriksa lokal Claude sebaiknya memeriksa semua kata tambahan pada Pilar 12.

Tanda `⚠️ perlu dicek` sudah dipakai pada bagian yang memerlukan perhatian khusus, terutama klasifikasi 非常.

## 5. Berkas dibuat atau diperbarui
- `kerja_gpt_afiks/hasil/pilar_12.json` (baru; final enam bagian).
- `kerja_gpt_afiks/laporan/tahap3_pilar12.md` (baru).
- `kerja_gpt_afiks/laporan/catatan_serah_terima.md` (diperbarui).

## 6. Batas pekerjaan
Tahap 3 selesai. Tidak mengubah Pilar 1–11, data aplikasi asli, HTML, JavaScript, CSS, atau berkas di luar `kerja_gpt_afiks/`. Materi lanjutan yang belum disetujui tidak dikerjakan.

Menunggu perintah LANJUT dari Ruslan.

# BLUEPRINT v49 — Mandarin Interaktif
# Dibuat akhir sesi 27 Nov 2026. Baca ini di awal percakapan baru.

---

## 0. CARA KERJA SESI INI (PENTING — dibahas & disepakati 27 Nov 2026)

Sesi-sesi terakhir terasa cepat habis token karena Claude menarik (clone) seluruh
repo dan membaca berkas besar penuh (peta-bahasa.html, app_words.json, dst.)
berkali-kali di dalam percakapan. Mulai sesi berikutnya:

1. **Untuk PENGECEKAN / PEMERIKSAAN (bukan pemasangan):** kembali ke cara lama.
   Claude membuat skrip `.py` kecil yang hanya mencetak bagian yang relevan.
   رسلان menjalankannya sendiri di PC, lalu menempelkan hasil cmd ke chat.
   Claude TIDAK menarik seluruh repo atau membaca berkas besar penuh hanya
   untuk memeriksa sesuatu.
2. **Untuk PEMASANGAN (yang mengubah berkas):** Claude boleh menguji skrip dulu
   di salinan repo sebelum diberikan (supaya tidak salah seperti kejadian
   `perbaiki_pilar12_64.py` yang sempat gagal karena asumsi isi berkas keliru),
   tapi dibatasi: hanya membaca potongan kecil berkas relevan (grep / baris
   tertentu), bukan mencetak seluruh isi berkas berulang-ulang.
3. Hindari membuka ulang berkas besar berkali-kali dalam satu sesi bila isinya
   belum berubah — andalkan apa yang sudah dibaca di awal sesi.
4. Jika sesi mulai terasa berat/panjang, lebih baik disudahi lebih awal dengan
   membuat blueprint baru, daripada memaksakan satu langkah besar lagi yang
   berisiko sesi terputus di tengah jalan.
5. Model: sempat dicoba Sonnet 5 low, kembali ke Sonnet 5.5 medium untuk
   percakapan berikutnya.
6. Project Knowledge / Artifacts cocok untuk sesi diskusi murni (tanpa
   pemasangan); untuk pemasangan, cara lama (skrip + tempel hasil cmd) tetap
   paling hemat karena Claude perlu salinan kerja untuk menguji skrip.

---

## 1. STATUS SAAT INI (semua sudah diuji رسلان dan diunggah ke GitHub)

### Imbuhan (data\afiks_kamus.json) — 64 entri, kelompok A–L
- A–J (60 entri): selesai sesi-sesi sebelumnya.
- **K. Penggemar dan kelompok orang** (BARU, sesi ini): AFK-061 族, AFK-062 迷
- **L. Penyakit dan zat** (BARU, sesi ini): AFK-063 症, AFK-064 剂
- **DITUNDA:** 炎 dan 盲 — di app_words.json masing-masing cuma 1 kata contoh
  (发炎 untuk 炎; 文盲 untuk 盲). Juga masih tertunda dari sesi lebih lama: 热, 控.
- Berkas pemasang (sudah dijalankan, boleh dijalankan ulang dengan aman —
  akan bilang "sudah terpasang"): `pasang_imbuhan_tingkat3.py`

### Tata Bahasa (data\grammar_afiks.json) — 64 poin AFX.01–AFX.64
- AFX.61–64 (族 迷 症 剂) sudah dipasang, tombol "📘 Tata Bahasa" di kartu Kamus
  sudah aktif untuk semua 64 entri.
- Berkas pemasang: `pasang_afx_61_64.py`

### Peta Bahasa — 13 Pilar
- **Pilar 13 BARU: "Kata Penunjuk Posisi (方位词)"** — 7 bagian/21 blok:
  1. Apa itu 方位词 + tabel 7 karakter (上下里外中间边)
  2. Bentuk sederhana vs gabungan (+面/+边/+头)
  3. Pola Tempat + 上/里
  4. Batas dan luar (以上/以下/以外/之外/以内/国外)
  5. 中 dan 间 (中间/之间/其中/当中/房间/时间)
  6. Aturan bacaan netral (里/上/边 — sesuai bacaan di Kamus kita, BUKAN
     mengubah data pinyin)
  7. Pasangan lawan sebagai peta cepat
- Pilar 12 (Pembentukan Kata) diperbarui: "64 entri", "dua belas kelompok",
  "47 akhiran + 17 awalan", tabel peta tambah baris K & L, baris materi
  lanjutan tinggal "热、控、炎、盲"; baris 上下里外中间 kini menunjuk
  "Sudah dibahas di Pilar 13".
- Berkas pemasang: `perbaiki_pilar12_64.py` lalu `pasang_pilar13.py`
  (urutan ini penting: perbaiki_pilar12_64.py dulu, baru pasang_pilar13.py)

### CATATAN PENTING — JANGAN DIJALANKAN ULANG
- `pasang_pilar12.py` (skrip LAMA pembuat Pilar 12 awal) — masih menulis teks
  "60 poin"/versi lama. Kalau dijalankan ulang akan MENIMPA balik perbaikan
  64-poin. Biarkan saja, tidak perlu dihapus, cukup jangan dijalankan.

---

## 2. KEPUTUSAN TEKNIS YANG PERLU DIINGAT

- Pola pemasangan yang dipakai konsisten sejak beberapa sesi: skrip punya mode
  LIHAT-DULU (default) dan `--apply`; selalu bikin cadangan `.bak_<nama>_<jam>`;
  ada pemeriksaan otomatis di akhir (hitung entri, cek silang dengan
  app_words.json) yang mengembalikan dari cadangan bila gagal.
- Semua kata contoh di entri Tata Bahasa/Imbuhan/Pelajaran WAJIB ada persis di
  data\app_words.json (dicek otomatis oleh skrip pemasang). Tingkat HSK poin
  Tata Bahasa diambil dari kata contoh termudah.
- Bacaan 面 di Kamus TIDAK seragam: 上面/下面/里面/外面/前面 pakai "miàn" penuh,
  tapi 后面 pakai "mian" ringan. Ini dicatat sebagai peringatan di Pilar 13
  bagian 6, bukan diseragamkan — data pinyin tidak diubah.
- 里 dibaca "li" (ringan) setelah kata benda biasa (家里, 手里, 心里), tapi "lǐ"
  (nada 3) setelah 这/那/哪 (这里, 那里, 哪里). Dicatat di Pilar 13 bagian 6.

---

## 3. BUTIR BERIKUTNYA (urutan saran, boleh رسلان ubah)

1. **炎 dan 盲**: menunggu kata tambahan. Pilihan lama (sesi 熱/控/炎/盲): atau
   ditunda terus sampai ada lebih banyak kata di app_words.json, atau (opsi C
   yang sempat dibahas dan DITOLAK untuk 炎/盲/族/迷/症/剂 kemarin) menambah kata
   baru dari CC-CEDICT ke app_words.json — opsi ini perlu keputusan baru kalau
   mau dipakai, karena mengubah data inti dan perlu data radikal/goresan/pinyin
   yang tidak otomatis tersedia.
2. **热 dan 控**: juga masih tertunda dari sesi sebelum ini, alasan tertunda
   belum dicatat ulang — perlu dicek lagi alasannya atau langsung disusulkan
   kalau datanya sudah cukup.
3. Hal lain dari BLUEPRINT_v48.md yang belum diangkat sesi ini: cek kembali
   bagian 5 lama untuk melihat apakah masih ada butir lain yang terlewat
   (sesi ini fokus ke imbuhan K/L dan Pilar 13 saja).
4. CATATAN_LANJUTAN.md dan buat_kandidat_imbuhan.py sudah diunggah رسلان ke
   repo sebelumnya — belum sempat dibaca ulang di sesi ini; cek isinya di
   awal sesi berikutnya kalau relevan dengan butir di atas.

---

## 4. BERKAS YANG DIHASILKAN SESI INI (sudah diunggah رسلان ke GitHub)

- `pasang_imbuhan_tingkat3.py`
- `kamus/kamus-afiks.js` (direvisi 2x dalam sesi ini: pertama untuk K/L,
  kedua untuk mengaktifkan tombol Tata Bahasa AFX.61-64)
- `pasang_afx_61_64.py`
- `perbaiki_pilar12_64.py` (versi final, sempat gagal sekali lalu diperbaiki)
- `pasang_pilar13.py`
- `data/afiks_kamus.json`, `data/afiks_pengecoh.json`, `data/grammar_afiks.json`,
  `data/pelajaran/pilar_12.json`, `data/pelajaran/pilar_13.json`
- `tatabahasa.html`, `peta-bahasa.html`

---

## 5. PESAN PEMBUKA UNTUK SESI BERIKUTNYA (salin ini di awal percakapan baru)

> Lanjutkan proyek Mandarin Interaktif. Baca BLUEPRINT_v49.md yang saya
> lampirkan ini (jangan menarik seluruh repo dulu). Untuk sesi ini saya ingin
> membahas [BUTIR_PILIHAN — mis. "炎 dan 盲" atau "热 dan 控" atau hal baru],
> ingat kesepakatan di bagian 0 soal cara kerja hemat token: kalau butuh
> memeriksa isi berkas, buatkan dulu skrip .py kecil untuk saya jalankan
> sendiri, jangan langsung menarik repo.

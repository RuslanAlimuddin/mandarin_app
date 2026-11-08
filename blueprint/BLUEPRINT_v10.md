# BLUEPRINT_v10 — Mandarin Interaktif
### Handoff document dari sesi sebelumnya. Upload file ini di awal percakapan baru.

> Cara pakai: رسلان upload file ini ke percakapan baru. Claude membaca semuanya
> dulu sebelum bertanya apa pun — jangan minta رسلان mengulang konteks yang
> sudah ada di sini.

---

## 1. Tentang aplikasi ini

**Mandarin Interaktif** — aplikasi belajar bahasa Mandarin offline, HTML/CSS/JS
murni (tanpa framework/build step), disimpan lokal di **`C:\mandarin_app\`**.
رسلان mengerjakan ini lintas sesi Claude yang berbeda-beda, makanya blueprint
ini penting sebagai jembatan ingatan.

**Halaman yang sudah ada** (semua saling terhubung lewat navbar):
1. `index.html` — landing page, 7 kartu menuju semua halaman
2. `kamus.html` — kamus 11.470 kata + akses ke `hanyu_extract`/`mandarin_kamus` (125rb+ entri CC-CEDICT mentah, belum diintegrasikan)
3. `flashcard.html` — SRS (spaced repetition), banyak deck & mode game, termasuk deck "🔀 Karakter Mirip"
4. `wordbuilder.html` — susun kalimat dari pola tata bahasa (Tunggal/Majemuk/Fungsi)
5. `tone.html` — latihan nada Mandarin
6. `graded-reader.html` — bacaan berjenjang per level HSK (+ per tema) — **101 bacaan (naik dari 69, sesi ini)**
7. `hsk-exam.html` — simulasi ujian HSK
8. `tatabahasa.html` — referensi tata bahasa lengkap per level HSK 1-9 — semua level teraudit vs standar resmi

**File bersama** (`shared/` atau `data/` di root app):
- `shared/core.js`, `shared/pinyin.js`, `shared/audio.js`, `shared/style.css` — dipakai semua halaman
- `data/app_words.json` — kamus utama, 11.470 kata (field: simplified, pinyin, hsk, hsk2, meanings_id, synonyms, antonyms, radical, structure, dll). **PENTING: ini BUKAN kamus karakter lengkap** — banyak karakter dasar yang umum (士, 相, 体, 众, 物, 世, dll) TIDAK punya entri berdiri sendiri, cuma muncul di dalam kata majemuk tertentu (lihat §4).
- `data/grammar_hsk1.json` s/d `grammar_hsk9.json` — data tata bahasa per level (dipakai `tatabahasa.html`). HSK1-6 direvisi total (414→521 poin), HSK7-9 sudah teraudit di sesi-sesi sebelumnya.
- `data/graded_readers.json` — **101 bacaan total** (naik dari 69 sesi ini; lihat §2.1). Backup sebelum merge tersimpan di `data/graded_readers_backup_sebelum_merge.json`.
- `data/confusion_groups.json` — 53 kelompok karakter mirip, dipakai di Flashcard
- `data/pattern_explanations.json` — dipakai Word Builder, tiap `kesalahan_umum` punya field `salah_py`/`benar_py` terpisah

**PART-file system**: `kamus.html`, `flashcard.html`, `wordbuilder.html`, `index.html`
masing-masing punya folder PART sendiri di root app: `kamus\`, `flashcard\`,
`word\`, `index\`. Halaman lain (`graded-reader.html`, `tone.html`,
`hsk-exam.html`, `tatabahasa.html`) file tunggal, tidak ada PART.

**Konvensi kerja yang SUDAH DISEPAKATI** (jangan diulang tanya ke رسلان):
- Diskusi dulu sebelum coding kalau scope besar/ambigu
- Kirim file di respons yang sama dengan pekerjaannya
- Edit file PART kalau ada (bukan file hasil merge) — lihat blueprint lama §5 soal kapan kirim PART vs kirim .html utuh
- `node --check` untuk semua JS sebelum diserahkan
- Komunikasi dalam Bahasa Indonesia
- Prefer solusi lebih simpel kalau ada pilihan
- **رسلان TIDAK bisa diakses filesystem-nya langsung** — semua kerja lewat upload/download file di chat. Kalau perlu proses file besar yang ada di PC رسلان, tulis skrip Python untuk رسلان jalankan lokal, minta hasilnya diupload balik.
- **SELALU verifikasi file yang diupload رسلان itu VERSI TERBARU** sebelum mulai edit — kalau curiga, minta رسلان jalankan `scan_mandarin_app.py` dulu buat cek isi folder terkini.
- **Untuk bacaan (`graded_readers.json`) dengan penambahan skala besar**: kerja pakai file staging terpisah (bukan langsung timpa file utama), lalu رسلان merge lokal pakai skrip Python. Lihat §5 untuk pola kerja lengkap yang sudah terbukti sesi ini.

---

## 2. Apa yang sudah dikerjakan (kronologis, sesi ini)

### 2.1 Bacaan Per Tema — 69 → 101 bacaan (+32 baru) — SELESAI & terpasang
- Ditulis dalam 4 batch (masing-masing 8 bacaan), disimpan sebagai file staging (`graded_readers_tema6.json` s/d `tema9.json`), digabung via skrip `merge_graded_readers.py` yang رسلان jalankan lokal. Sudah **terverifikasi 101/101 OK** oleh رسلان sendiri.
- **Fokus batch 1-2**: perbaiki ketimpangan level HSK6-9 (sebelumnya HSK6=7, HSK7=5, HSK8=2, HSK9=2 — paling timpang di antara semua level). Tema yang dipakai: Filsafat & Pemikiran, Keuangan, Agama & Kepercayaan, Bisnis & Perdagangan, Negara & Budaya, Pendidikan Tinggi, Pemerintahan & Hukum, Seni & Budaya, Masyarakat & Budaya, Konstruksi & Teknik — masing-masing ditulis di level yang BELUM pernah dipakai tema itu sebelumnya (jadi sekaligus nambah variasi & meratakan level).
- **Fokus batch 3**: variasi tema di HSK2-5 yang tadinya cuma 1 bacaan (Hewan, Buah, Sayuran, Cuaca, Olahraga, Pakaian, Angka, Waktu), masing-masing ditambah 1 bacaan di level lain.
- **Fokus batch 4**: lanjutan penyeimbangan HSK7 (Teknologi, Komunikasi, Lingkungan Hidup, Pendidikan) dan HSK8 (Tekstil & Fashion, Alam & Lingkungan, Pekerjaan, Transportasi).
- **Distribusi level akhir**: HSK1=12, HSK2=13, HSK3=12, HSK4=12, HSK5=12, HSK6=11, HSK7=11, HSK8=10, HSK9=8 — jauh lebih rata dibanding sebelumnya.
- **TEMUAN TEKNIS PENTING** (lihat detail penuh di §4): `verify_coverage.py` versi awal salah asumsi — mengira tokenizer `graded-reader.html` mencocokkan teks ke `app_words.json` GLOBAL. Yang benar: tokenizer mencocokkan teks ke **glossary MILIK bacaan itu sendiri** (greedy longest-match terhadap array `glossary` di tiap passage, bukan terhadap kamus utama). Skrip sudah diperbaiki dan versi final (1 argumen saja: `python verify_coverage.py <file>.json`) sudah dites رسلان sendiri dan 101/101 lolos.
- File pendukung baru: `verify_coverage.py` (versi final, taruh di root app, dipakai lagi kalau nambah bacaan baru lagi ke depannya), `merge_graded_readers.py` (sudah dipakai, boleh dihapus atau disimpan untuk referensi kalau mau nambah batch staging lagi dengan pola serupa).

---

## 3. TODO — urutan prioritas yang disarankan

1. **Diskusi kelayakan OCR kamera / hover-translate** — wishlist paling lama, BELUM PERNAH dibahas kelayakan teknisnya sama sekali. Kemungkinan besar butuh library OCR eksternal / Tesseract.js, perlu dibahas apakah masih bisa "offline murni" sesuai prinsip app.
2. **Bacaan Per Tema** — SUDAH SELESAI sesi ini (§2.1), 101 bacaan, distribusi level jauh lebih rata. Kalau mau lanjut lagi ke depan, opsinya: HSK9 masih paling sedikit (8, vs level lain 10-13) — bisa ditambah lagi kalau mau makin rata; atau ada beberapa tema yang masih cuma 1 bacaan (cek dengan skrip cepat di sesi berikutnya kalau perlu daftar lengkapnya).
3. **Integrasi `hanyu_extract`/`mandarin_kamus`** (125rb+ entri CC-CEDICT) ke Kamus — belum pernah dibahas ulang sejak awal proyek, masih wishlist mentah.
4. Kalau رسلان temukan celah baru pas pakai app (bug, UX kurang pas, dll) — prioritas selalu boleh disisipkan di atas semua ini.

---

## 4. Hal teknis yang perlu diingat

- **Skema `graded_readers.json`**: `{"passages": [...]}` (dibungkus objek, BUKAN array langsung). Tiap bacaan: `{id, level, tema, title, text, translation, glossary:[{cn,py,id}]}`.
- **CARA VERIFIKASI COVERAGE YANG BENAR (revisi penting sesi ini)**: `glossary` WAJIB mencakup SETIAP token yang dihasilkan tokenizer greedy-longest-match terhadap **glossary bacaan itu sendiri** (BUKAN terhadap `app_words.json` global — itu kesalahan asumsi di awal sesi ini, sudah diperbaiki). Pakai `verify_coverage.py` (root app), pemakaian: `python verify_coverage.py data\graded_readers.json`. Ini artinya penulis bacaan BEBAS menggabungkan token semantik sesuai kebutuhan (misal "七点" sebagai satu entri glossary "jam tujuh", bukan harus "七"+"点" terpisah), asalkan konsisten dan setiap potongan teks ke-cover oleh entri glossary itu sendiri.
- **`app_words.json` BUKAN kamus karakter lengkap**: dari 11.470 entri, cuma 1.571 yang berupa karakter tunggal berdiri sendiri. Banyak karakter dasar yang umum digunakan (士, 相, 体, 众, 物, 世, 展, 休, 政, dll) TIDAK punya entri sendiri, cuma ada di dalam kata majemuk tertentu yang juga belum tentu ada. **Implikasi**: kalau mau pakai `app_words.json` sebagai sumber auto-lookup pinyin/arti (misal untuk generate glossary otomatis), akan sering ketemu gap terutama untuk vocab HSK7-9 yang abstrak — tapi ini TIDAK masalah untuk `graded_readers.json` karena verifikasi yang benar toh terhadap glossary sendiri, bukan `app_words.json`. Untuk keperluan LAIN (Word Builder, Flashcard, dll) yang memang bergantung pada `app_words.json` sebagai sumber utama, gap ini tetap relevan untuk diperhatikan.
- **Skema `grammar_hsk{1-6}.json`**: `{level, metadata:{total_points, source, last_updated, audit_status}, categories:[{name, points:[{id, number, title, title_cn, fungsi, tingkat, kategori, source, table:[{jenis,pola,contoh,pinyin,terjemahan}], reference_table?}]}], kesalahan_umum:[...]}`. Penomoran `number`/`id` pakai format `"{no_kategori}.{no_poin}"`.
- **`reference_table`**: dipakai untuk poin yang sifatnya REFERENSI struktural, bukan pola-kalimat buat dilatih aktif. **MASIH BELUM DIVERIFIKASI tampilannya di `tatabahasa.html` sungguhan** — kalau رسلان lihat tampilannya aneh/kosong, kabari Claude buat cek rendering-nya.
- **Skema `pattern_explanations.json`** (dipakai Word Builder): tiap `kesalahan_umum` item `{salah, benar, penjelasan, salah_py, benar_py}` — salah/benar HARUS hanzi murni, pinyin di field terpisah.
- **Skema `confusion_groups.json`**: `{groups:[{id, character, confusable_with:[...], note}], metadata}`. Dipakai Flashcard lewat fungsi `resolveConfusionChar()`.
- **Field HSK di `app_words.json`**: `hsk` (skala lama 1-6, "7"=luar HSK), `hsk2` (skala baru tapi cuma sampai 6 di dataset ini). `meanings_id` adalah LIST — selalu ambil elemen yang bukan pola "varian dari"/"marga "/"KP:"/"Taiwan dibaca" (tanda salah-sense dari CC-CEDICT), bukan asal `[0]`.
- Semua file baru taruh di `C:\mandarin_app\data\` (flat) kecuali diberi tahu lain.

---

## 5. Pola kerja untuk penambahan bacaan skala besar (terbukti efektif sesi ini)

Kalau ke depan رسلان minta tambah bacaan lagi dalam jumlah besar (misal 20+), pola ini terbukti jalan lancar:

1. **Cek distribusi dulu** — pindai `graded_readers.json` existing untuk lihat tema mana yang masih sedikit (1 bacaan) dan level mana yang paling timpang jumlahnya.
2. **Rencanakan alokasi tema×level** sebelum mulai nulis — pilih kombinasi tema+level yang BELUM pernah dipakai, supaya sekaligus nambah variasi tema DAN meratakan distribusi level.
3. **Tulis per batch kecil** (6-8 bacaan per batch) — lebih gampang diverifikasi dan dikirim bertahap daripada semua sekaligus.
4. **Setelah tulis teks, generate glossary, LALU verifikasi pakai `verify_coverage.py` (versi yang cocok ke glossary sendiri, BUKAN ke `app_words.json`)** — kalau ada karakter yang belum ke-cover, cukup tambah entri glossary untuk karakter/kata itu (tidak perlu buru-buru mengganti kata di teks, beda dari asumsi awal sesi ini).
5. **Cek bentrok ID** dengan bacaan yang sudah ada sebelum finalisasi.
6. **Kirim tiap batch sebagai file staging terpisah** (`graded_readers_temaN.json`, array langsung bukan dibungkus `{"passages":...}`), plus skrip `merge_graded_readers.py` di batch terakhir untuk رسلان jalankan lokal (otomatis backup + gabung + kasih instruksi verifikasi final).

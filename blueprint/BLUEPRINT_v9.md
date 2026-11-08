# BLUEPRINT_v9 — Mandarin Interaktif
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
3. `flashcard.html` — SRS (spaced repetition), banyak deck & mode game, **+ deck baru "🔀 Karakter Mirip" (sesi ini)**
4. `wordbuilder.html` — susun kalimat dari pola tata bahasa (Tunggal/Majemuk/Fungsi)
5. `tone.html` — latihan nada Mandarin
6. `graded-reader.html` — bacaan berjenjang per level HSK (+ per tema) — **69 bacaan (naik dari 14)**
7. `hsk-exam.html` — simulasi ujian HSK
8. `tatabahasa.html` — referensi tata bahasa lengkap per level HSK 1-9 — **semua level SUDAH teraudit vs standar resmi (sesi ini)**

**File bersama** (`shared/` atau `data/` di root app):
- `shared/core.js`, `shared/pinyin.js`, `shared/audio.js`, `shared/style.css` — dipakai semua halaman
- `data/app_words.json` — kamus utama, 11.470 kata (field: simplified, pinyin, hsk, hsk2, meanings_id, synonyms, antonyms, radical, structure, dll)
- `data/grammar_hsk1.json` s/d `grammar_hsk9.json` — data tata bahasa per level (dipakai `tatabahasa.html`). **HSK1-6 direvisi total sesi ini** (414→521 poin), HSK7-9 sudah diaudit sesi-sesi sebelumnya.
- `data/graded_readers.json` — **69 bacaan total** (naik dari 14; lihat §2.2)
- `data/confusion_groups.json` — 53 kelompok karakter mirip, **sekarang dipakai** di Flashcard (sebelumnya cuma data siap tanpa fitur)
- `data/pattern_explanations.json` — dipakai Word Builder, sekarang tiap `kesalahan_umum` punya field `salah_py`/`benar_py` terpisah (lihat §4)

**PART-file system**: `kamus.html`, `flashcard.html`, `wordbuilder.html`, `index.html`
masing-masing punya folder PART sendiri di root app: `kamus\`, `flashcard\`,
`word\`, `index\`. Halaman lain (`graded-reader.html`, `tone.html`,
`hsk-exam.html`, `tatabahasa.html`) file tunggal, tidak ada PART.

**Konvensi kerja yang SUDAH DISEPAKATI** (jangan diulang tanya ke رسلان):
- Diskusi dulu sebelum coding kalau scope besar/ambigu
- Kirim file di respons yang sama dengan pekerjaannya
- Edit file PART kalau ada (bukan file hasil merge) — **TAPI lihat §5 soal kapan kirim PART vs kirim .html utuh**
- `node --check` untuk semua JS sebelum diserahkan
- Komunikasi dalam Bahasa Indonesia
- Prefer solusi lebih simpel kalau ada pilihan
- **رسلان TIDAK bisa diakses filesystem-nya langsung** — semua kerja lewat upload/download file di chat. Kalau perlu proses file besar yang ada di PC رسلان, tulis skrip Python untuk رسلان jalankan lokal, minta hasilnya diupload balik.
- **SELALU verifikasi file yang diupload رسلان itu VERSI TERBARU** sebelum mulai edit — beberapa kali ketemu kasus PART files atau `graded_readers.json` yang diupload ternyata versi LAMA (lihat §5 dan §2.2). Kalau curiga, minta رسلان jalankan `scan_mandarin_app.py` dulu buat cek isi folder terkini.

---

## 2. Apa yang sudah dikerjakan (kronologis, sesi ini)

### 2.1 Word Builder — 3 perbaikan Spot-the-Error — SELESAI & terpasang
- Stok `kesalahan_umum` per pola naik dari 2 → 4 (68→136 total), supaya tombol "↺ Ulangi" beneran mengacak
- Skema data dirapikan: field `salah`/`benar` sekarang **hanzi murni** (dulu beberapa nyisip anotasi pinyin/catatan dalam kurung yang bikin bocor duluan sebelum user coba jawab). Pinyin dipindah ke field terpisah `salah_py`/`benar_py`, baru dirender di kartu feedback SETELAH user cek/lihat jawaban.
- `contoh_tambahan` (stok contoh kalimat BENAR) naik dari 88 → 156 total (+2 per pola)
- Pinyin baru digenerate pakai `pypinyin` + segmentasi kata `jieba` (bukan per-karakter) supaya gaya penulisan konsisten dgn yang sudah ada (mis. `xǐhuan` bukan `xǐ huān`)

### 2.2 Flashcard — deck baru "🔀 Karakter Mirip" — SELESAI & terpasang
- Mode game only (mirip "Jebakan Nada"/tone-trap): dengar pengucapan 1 karakter dari kelompok mirip (mis. 己/已/巳), pilih hanzi yang tepat — distraktor HANYA dari kelompok yang sama biar benar-benar melatih pembeda bentuk
- Setelah jawab: tampil catatan pembeda bentuk (field `note` di `confusion_groups.json`)
- **TEMUAN PENTING**: PART files flashcard yang رسلان upload di awal sesi ternyata VERSI LAMA (hilang fitur Sinonim dari sesi sebelumnya). Sudah di-resync dari `flashcard.html` (source of truth) sebelum dikerjakan.

### 2.3 Bacaan Per Tema (`graded_readers.json`) — 14 → 69 bacaan
- **TEMUAN PENTING**: `graded_readers.json` yang رسلان upload juga sempat versi lama (0 bacaan tema, padahal sesi sebelumnya sudah bikin 18). Dipulihkan dari 5 file staging (`graded_readers_tema.json` s/d `tema5.json`).
- **87 entri glosarium salah-sense diperbaiki** di 18 bacaan lama itu (polifon: 都→"marga Du" harusnya "semua"; 还→"marga Huan" harusnya "masih"; dll — tersebar di 15/18 bacaan, bukan cuma yang kelihatan awal)
- **55 bacaan baru ditulis dari nol** (bukan dari `themes_extracted_v2.json` — data itu terbukti tidak reliable, tagging tema-nya kacau, lihat §4). Kosakata HSK1-6 divalidasi silang ke `app_words.json`, semua diverifikasi 100% coverage tokenizer (simulasi greedy-longest-match python persis logika `graded-reader.html`).
- **Semua 40 tema di `themes_extracted_v2.json` sudah terpakai** minimal 1×, KECUALI `kata_fungsi` & `kata_tanya` (sengaja dilewati — itu kategori tata bahasa/kata tanya, bukan topik bacaan naratif, lebih cocok utk Tata Bahasa)
- HSK8-9 yang tadinya 0 bacaan sekarang masing-masing 2
- Distribusi akhir per level: HSK1=12, HSK2=13, HSK3=10, HSK4=9, HSK5=9, HSK6=7, HSK7=5, HSK8=2, HSK9=2

### 2.4 Audit Tata Bahasa HSK1-6 vs Standar Resmi — SELESAI (414→521 poin)
- Sumber resmi: **Silabus Ujian HSK 3.0** (`新版HSK考试大纲1219.pdf`, terbit 中外语言交流合作中心, efektif Juli 2026), section "HSK 语法大纲" halaman 385-406. رسلان sudah punya file ini di `C:\mandarin_app\grammar\`.
- **Audit dilakukan MANUAL/KONSEPTUAL** (baca tiap baris silabus resmi, nilai apa sudah ada padanan konsepnya di `grammar_hsk{level}.json`) — bukan pencarian teks otomatis, karena representasi tulisan beda total (resmi pakai rumus abstrak, data رسلان pakai deskripsi Indonesia per-kata).
- Temuan terbesar: **kata ganti (pronomina)** nyaris tidak ada poinnya di SEMUA level 1-4 (padahal paling dasar). **把字句 & 被动句** di HSK3 cuma ditangani sbg kata depan biasa, bukan pola kalimat utuh dgn variannya (gap paling signifikan di seluruh audit).
- Tiap level juga dapat kategori REFERENSI struktural baru (jenis frasa, unsur kalimat — pakai field `reference_table`, bukan poin latihan aktif, untuk kebutuhan guru — permintaan eksplisit رسلان).
- Rincian per level: HSK1 49→70 (+21), HSK2 57→75 (+18), HSK3 67→96 (+29), HSK4 75→89 (+14), HSK5 84→101 (+17), HSK6 82→90 (+8).
- **HSK7-9 sudah teraudit di sesi-sesi SEBELUM ini** (90/104/55 poin) — TIDAK disentuh lagi sesi ini, statusnya tetap.

### 2.5 Skrip pendukung baru yang dibuat sesi ini
- `scan_mandarin_app.py` — pindai `C:\mandarin_app`, hasilkan `laporan_struktur.json` (daftar semua file + preview struktur JSON). رسلان jalankan kapan pun Claude butuh tahu file apa saja yang ada tanpa upload manual satu-satu.
- `split_to_parts.py` — pecah file `.html` (flashcard/kamus/dll) jadi PART files otomatis, deteksi batas via marker komentar `— PART n:`. Dipakai kalau Claude kirim `.html` utuh (lihat §5).
- `inspect_themes.py` — sampling acak dari file tema besar (`themes_extracted_v2.json`, 8MB) tanpa perlu upload seluruh file. **Kesimpulan: data ini TIDAK RELIABLE**, tagging tema-nya kacau (tema "warna" isinya kata random, bukan warna) — jangan dipakai lagi sebagai sumber ekstraksi vocab, cukup untuk referensi daftar NAMA tema saja.
- `extract_grammar_pages.py` — ekstrak halaman tertentu dari PDF resmi HSK (butuh nomor halaman manual karena PDF itu ada watermark yang merusak pencarian teks otomatis).

---

## 3. TODO — urutan prioritas yang disarankan

1. **Diskusi kelayakan OCR kamera / hover-translate** — wishlist paling lama, BELUM PERNAH dibahas kelayakan teknisnya sama sekali. رسلان sempat mau ini sebelum dialihkan ke audit tata bahasa karena khawatir kepanjangan — worth diskusi scope dulu sebelum mulai coding (kemungkinan besar butuh library OCR eksternal / Tesseract.js, perlu dibahas apakah masih bisa "offline murni" sesuai prinsip app).
2. **32→sisa tema Bacaan Per Tema** — SUDAH SELESAI sesi ini (§2.3), semua 40 tema terpakai. Kalau mau lanjut, opsinya: tambah lebih banyak bacaan LAGI per tema yang sudah ada (variasi), atau naikkan HSK8-9 dari 2 jadi lebih banyak.
3. **Audit HSK1-6 vs standar resmi** — SUDAH SELESAI sesi ini (§2.4). Kalau ada revisi silabus resmi HSK di masa depan, PDF-nya ada di `C:\mandarin_app\grammar\hsk_dagang.pdf` (atau nama file aslinya `新版HSK考试大纲1219.pdf`).
4. **Integrasi `hanyu_extract`/`mandarin_kamus`** (125rb+ entri CC-CEDICT) ke Kamus — belum pernah dibahas ulang sejak awal proyek, masih di §2 blueprint lama sbg wishlist mentah.
5. Kalau رسلان temukan celah baru pas pakai app (bug, UX kurang pas, dll) — prioritas selalu boleh disisipkan di atas semua ini.

---

## 4. Hal teknis yang perlu diingat

- **Skema `graded_readers.json`**: `{"passages": [...]}` (dibungkus objek, BUKAN array langsung — beda dari file staging `tema*.json` lama yang array langsung). Tiap bacaan: `{id, level, tema, title, text, translation, glossary:[{cn,py,id}]}`. `glossary` WAJIB mencakup SETIAP karakter non-tanda-baca (verifikasi pakai simulasi tokenizer greedy-longest-match Python sebelum menyerahkan — lihat pendekatan di §2.3, fungsi `tokenize_greedy`).
- **`themes_extracted_v2.json` (~8MB) TIDAK RELIABLE** — jangan dipakai lagi sebagai sumber vocab/tema. Kalau butuh bacaan baru, tulis sendiri pakai pengetahuan Mandarin + validasi ke `app_words.json` (field `hsk2`), JANGAN dari file itu.
- **Skema `grammar_hsk{1-6}.json`**: `{level, metadata:{total_points, source, last_updated, audit_status}, categories:[{name, points:[{id, number, title, title_cn, fungsi, tingkat, kategori, source, table:[{jenis,pola,contoh,pinyin,terjemahan}], reference_table?}]}], kesalahan_umum:[...]}`. Penomoran `number`/`id` pakai format `"{no_kategori}.{no_poin}"` (mis. `"11.2"` = kategori ke-11, poin ke-2) — **PENTING**: kalau nambah kategori baru, cari `next_cat_num` dari MAX nomor kategori yang benar-benar ada di data (bukan cuma `len(categories)`, karena kadang ada kategori kosong yang dibuang duluan sehingga index tidak match nomor asli — pernah kejadian di HSK2).
- **`reference_table`** (field baru sesi ini): dipakai untuk poin yang sifatnya REFERENSI struktural (jenis frasa, unsur kalimat), bukan pola-kalimat buat dilatih aktif. Field `table`-nya dikosongkan `[]` kalau pakai `reference_table`. **BELUM DIVERIFIKASI tampilannya di `tatabahasa.html` sungguhan** — kalau رسلان lihat tampilannya aneh/kosong, kabari Claude buat cek rendering-nya.
- **Skema `pattern_explanations.json`** (dipakai Word Builder): tiap `kesalahan_umum` item sekarang `{salah, benar, penjelasan, salah_py, benar_py}` — salah/benar HARUS hanzi murni, pinyin di field terpisah. `contoh_tambahan` tetap `{cn, py, id}`.
- **Skema `confusion_groups.json`**: `{groups:[{id, character, confusable_with:[...], note}], metadata}`. Dipakai Flashcard lewat fungsi `resolveConfusionChar()` (cari di `app_words.json` dulu, fallback objek minimal kalau karakter itu bukan entri kamus tersendiri).
- **Field HSK di `app_words.json`**: `hsk` (skala lama 1-6, "7"=luar HSK), `hsk2` (skala baru tapi cuma sampai 6 di dataset ini). `meanings_id` adalah LIST — **selalu ambil elemen yang bukan pola "varian dari"/"marga "/"KP:"/"Taiwan dibaca"** (itu tanda salah-sense dari CC-CEDICT), bukan asal `[0]`.
- Semua file baru taruh di `C:\mandarin_app\data\` (flat) kecuali diberi tahu lain.

---

## 5. Kebijakan PART files vs .html utuh (disepakati sesi ini)

- **Perubahan kecil/lokal** (1-2 PART saja kena) → Claude kirim PART yang berubah saja (hemat token)
- **Perubahan menyebar** (banyak PART kena sekaligus) → Claude kirim `.html` utuh saja
- Kalau رسلان terima `.html` utuh dan mau lanjut edit via PART lagi: jalankan `split_to_parts.py namafile.html folder_tujuan` (lihat §2.5) — **JANGAN pernah assume PART files yang رسلان upload itu versi terbaru** tanpa dicek dulu (sudah 2× kejadian sesi ini: flashcard PART & `graded_readers.json` sama-sama ketemu versi basi). Kalau ragu, minta رسلان jalankan `scan_mandarin_app.py` dulu.

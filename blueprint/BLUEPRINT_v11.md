# BLUEPRINT_v11 — Mandarin Interaktif
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

**Prinsip inti yang TIDAK BOLEH dilanggar**: aplikasi ini **offline murni**.
Jangan pernah usulkan fitur yang butuh API key/koneksi internet/AI generatif
online (misal "generate kalimat pakai AI" langsung di app) — sudah dibahas
eksplisit dan رسلان menolak arah itu.

**Halaman yang sudah ada** (semua saling terhubung lewat navbar, 9 halaman total):
1. `index.html` — landing page
2. `kamus.html` — kamus 11.470 kata (`app_words.json`) + **toggle sumber "HSK/Cidict"** ke `cidict_index.json` (125rb+ entri CC-CIDICT, lazy-load) + fallback otomatis hanzi & arti Indonesia ke Cidict kalau kamus utama nihil hasil
3. `flashcard.html` — SRS, banyak deck & mode game, termasuk deck "🔀 Karakter Mirip"
4. `wordbuilder.html` — susun kalimat dari pola tata bahasa
5. `tone.html` — latihan nada Mandarin
6. `graded-reader.html` — bacaan berjenjang per level HSK (+ per tema) — **104 bacaan**
7. `hsk-exam.html` — simulasi ujian HSK
8. `tatabahasa.html` — referensi tata bahasa lengkap HSK 1-9 — semua level teraudit
9. **`terjemah-bebas.html`** (BARU sesi ini) — tempel teks Mandarin bebas → daftar kata otomatis (hanzi/pinyin/arti) + toggle pinyin + teks bisa diklik per kata. Sumber: `app_words.json` prioritas, fallback ke `cidict_index.json` (ditandai garis putus-putus)

**File bersama** (`shared/` atau `data/` di root app):
- `shared/core.js`, `shared/pinyin.js`, `shared/audio.js`, `shared/style.css` — dipakai semua halaman
- `data/app_words.json` — kamus utama, 11.470 kata. **BUKAN kamus karakter lengkap** — banyak karakter dasar umum tidak punya entri sendiri (lihat §4 blueprint lama untuk daftar contoh).
- `data/cidict_index.json` (25.8 MB, ~121.158 entri) — **CC-CIDICT**, kamus komunitas Mandarin-Indonesia (bukan CC-CEDICT bahasa Inggris — sudah diterjemahkan ke Indonesia sejak sumbernya, proyek "Harmony Mandarin"). Field: `simplified`, `traditional`, `pinyin` (sudah beraksen), `pinyin_numeric`, `meanings_id` (list), `in_hsk`. Dipakai sebagai fallback di `kamus.html` dan `terjemah-bebas.html`, lazy-loaded (baru di-fetch saat benar-benar dibutuhkan, bukan saat halaman dibuka).
- File cidict lain yang ADA tapi TIDAK dipakai kode: `cidict_semantic_index.json` (key pakai aksara tradisional, kurang cocok), `cidict_full.json` (pinyin masih angka nada, butuh konversi ekstra), `cidict_ts.u8` (teks mentah CEDICT, susah diparse langsung di JS). Ketiganya boleh dibiarkan di `data/` untuk sekarang.
- `hanyu_extract`/`mandarin_kamus` (folder terpisah, lokasi belum dikonfirmasi ulang sesi ini) — **kemungkinan besar SUDAH TIDAK TERPAKAI** sejak `cidict_index.json` jadi sumber utama fallback. رسلان sengaja BELUM menghapusnya ("nanti kalau aplikasi ini benar-benar sudah fix" — lihat §3 TODO). **JANGAN hapus tanpa رسلان minta eksplisit.**
- `data/grammar_hsk1.json` s/d `grammar_hsk9.json`, `data/graded_readers.json` (104 bacaan), `data/confusion_groups.json`, `data/pattern_explanations.json` — tidak berubah dari blueprint sebelumnya, lihat BLUEPRINT_v10 §4 untuk skema detail tiap file kalau perlu.

**PART-file system**: `kamus.html`, `flashcard.html`, `wordbuilder.html`, `index.html`
masing-masing punya folder PART sendiri (`kamus\`, `flashcard\`, `word\`, `index\`).
`terjemah-bebas.html` (baru) TIDAK pakai sistem PART — masih single-file
seperti `graded-reader.html`, `tone.html`, dll, karena ukurannya masih kecil.
**Catatan untuk sesi depan**: kalau `kamus.html` terus membesar (sekarang
2.500+ baris hasil gabung), pertimbangkan modularisasi struktur fungsi JS
yang lebih tegas, bukan cuma PART-file untuk pengiriman token saja — lihat
§3 TODO poin 4.

**Konvensi kerja yang SUDAH DISEPAKATI** (jangan diulang tanya ke رسلان):
- Diskusi dulu sebelum coding kalau scope besar/ambigu
- Kirim file di respons yang sama dengan pekerjaannya
- Edit file PART kalau ada (bukan file hasil merge)
- `node --check` untuk semua JS sebelum diserahkan (dan untuk file besar, ekstrak tiap blok `<script>` terpisah lalu cek satu-satu)
- Verifikasi keseimbangan tag (`<div>` count) sebelum & sesudah edit sebagai sanity-check tambahan, khususnya untuk file besar seperti `kamus.html`
- Komunikasi dalam Bahasa Indonesia
- Prefer solusi lebih simpel kalau ada pilihan
- **رسلان TIDAK bisa diakses filesystem-nya langsung** — semua kerja lewat upload/download file di chat. Untuk file besar di PC رسلان, tulis skrip Python untuk رسلان jalankan lokal.
- **SELALU verifikasi file yang diupload رسلان itu VERSI TERBARU** sebelum mulai edit.
- **Untuk penambahan bacaan skala besar**: kerja pakai file staging terpisah + skrip merge Python untuk رسلان jalankan lokal. Pola lengkap ada di BLUEPRINT_v10 §5, terbukti jalan lagi sesi ini.
- **Kalau menulis bacaan baru dengan glossary manual**: SELALU verifikasi cakupan sendiri dulu (replikasi algoritma greedy longest-match) sebelum kirim ke رسلان, jangan cuma andalkan `verify_coverage.py` رسلان sebagai satu-satunya jaring pengaman — sesi ini sempat ketemu 5 kata kelewat di 1 dari 3 bacaan baru, untung ketahuan sebelum dikirim.
- **Kalau menemukan fitur/kode yang sudah ada tapi tidak tercatat di blueprint** (seperti toggle Cidict di `kamus.html` sesi ini): PRIORITASKAN baca kode dulu sebelum asumsi sesuatu belum dikerjakan, dan selalu update blueprint begitu ketahuan.

---

## 2. Apa yang sudah dikerjakan (kronologis, sesi ini)

### 2.1 Halaman baru: Terjemah Bebas — SELESAI & terpasang
`terjemah-bebas.html` dibuat sebagai jawaban atas wishlist lama "OCR
kamera/hover-translate" — setelah didiskusikan, versi OCR kamera fisik dan
widget mengambang lintas-OS **DITUNDA/DI-DROP** (lihat §3), dan yang
dibangun adalah versi "tempel teks lalu lihat arti semua kata sekaligus".
Alur akhir: رسلان tempel teks → tekan "Terjemahkan" → daftar kata otomatis
(hanzi/pinyin/arti) langsung tampil semua tanpa perlu klik, dengan toggle
"Tampilkan Pinyin" (state diingat via localStorage). Teks asli yang bisa
diklik per kata tetap ada di atas daftar untuk pencarian cepat. Tokenizer
pakai maximum-matching (bukan sort-scan seperti glossary kecil di
graded-reader) karena vocab gabungan besar (11rb + 121rb) — App_words.json
dicek dulu tiap posisi sebelum fallback ke Cidict, supaya prioritas kamus
utama terjaga. Link navbar sudah dipasang رسلان di semua 9 halaman.

### 2.2 Kamus: fallback otomatis pencarian hanzi ke CC-CIDICT — SELESAI
**Temuan penting**: toggle sumber "HSK/Cidict" di sidebar `kamus.html`
(lengkap dengan lazy-load) ternyata **sudah dibangun di sesi SEBELUM v10**
tapi tidak tercatat di blueprint manapun. Fallback otomatis untuk pencarian
**arti Indonesia** juga sudah ada (kalau hasil <5 di mode HSK, otomatis
tambah dari Cidict). Yang BELUM ada dan ditambahkan sesi ini: fallback
serupa untuk **pencarian hanzi** — kalau رسلان cari hanzi saat sumber aktif
"HSK" dan nihil hasil, otomatis cari ke Cidict (lazy-load kalau perlu),
tampilkan dengan toast pemberitahuan + penanda visual kelas `.cidict` yang
sudah ada. Sekalian diperbaiki bug laten: `selectWord()` dan
`speakDetailWord()` dulu cuma cari kata di array sumber yang sedang aktif
di sidebar, jadi klik detail/dengarkan pada kartu hasil fallback gagal
senyap — sekarang pakai helper baru `findWordInResults()` yang cek
`STATE.results` (hasil yang sedang tampil) dulu.

### 2.3 Kamus: kolom hanzi kartu hasil diperlebar — SELESAI
`.result-card.result-row .result-hanzi` dari `width: 64px` → `104px`
(varian `.cidict` dari tanpa-lebar-eksplisit → `92px`, sesuai font lebih
kecil 18px). Sebelumnya kata 4+ karakter (terutama entri CC-CIDICT yang
sering lebih panjang dari `app_words.json`) terpotong jadi "...".

### 2.4 Bacaan Per Tema — 101 → 104 bacaan (+3, ratakan HSK9) — SELESAI & terpasang
HSK9 sebelumnya paling timpang (8 bacaan, vs 10-13 di level lain). Ditambah
3 bacaan baru di tema yang belum pernah dipakai di level 9: **Kesehatan**
(dilema etika penyuntingan gen), **Pendidikan Tinggi** (orientasi kerja vs
akademik), **Lingkungan Hidup** (dilema ekonomi vs ekologi). HSK9 sekarang
**11 bacaan**, sejajar HSK7. Sudah diverifikasi 2 lapis: replikasi manual
algoritma greedy longest-match oleh Claude (ketemu & perbaiki 5 kata
kelewat di glossary sebelum dikirim), lalu `verify_coverage.py` رسلان
sendiri — **104/104 OK**. File staging (`graded_readers_hsk9_batch.json`)
dan skrip merge (`merge_graded_readers_hsk9.py`) beserta file backup
(`data/graded_readers_backup_sebelum_merge_hsk9.json`) **sengaja belum
dihapus** رسلان, disimpan untuk jaga-jaga.

---

## 3. TODO — urutan prioritas yang disarankan (hasil diskusi akhir sesi ini)

1. **Dashboard/statistik belajar ringkas** — رسلان setuju ini prioritas tinggi.
   BELUM PERNAH didiskusikan desainnya sama sekali sesi ini — sesi depan
   HARUS mulai dari diskusi (bukan langsung coding): halaman baru atau
   nempel ke `index.html`? Data apa yang ditarik (progres SRS dari
   `flashcard.html`, riwayat `hsk-exam.html`, jumlah kata dikuasai, streak
   harian, dll)? Sumber data localStorage per fitur perlu diinventarisasi
   dulu (banyak key berbeda-beda per halaman, cek `shared/core.js`
   `exportBackup()` untuk lihat pola enumerasi key yang sudah ada).
2. **Cross-link antar fitur** — رسلان setuju. BELUM didiskusikan detail:
   dari Flashcard/Word Builder, tautan ke bacaan (`graded-reader.html`)
   yang mengandung kata yang sedang dipelajari. Perlu didiskusikan: cocokkan
   berdasarkan apa (glossary bacaan vs kata individual), tampil di mana
   (panel detail? tombol baru?), dan biaya performa (bacaan discan tiap
   buka detail kata, atau index dibangun sekali di awal?).
3. **Modularisasi `kamus.html`** — رسلان setuju idenya, tapi ini task
   refactor besar (2.500+ baris) yang butuh perencanaan sendiri sebelum
   eksekusi, bukan sekadar "kerjakan sekarang". Sesi depan sebaiknya
   diskusikan dulu strategi pemecahannya (modul fungsi per fitur:
   search/render/detail/backup, dll) sebelum mulai ubah kode nyata,
   supaya tidak merusak fungsionalitas yang sudah jalan.
4. **Hapus folder `hanyu_extract`/`mandarin_kamus`** — DITUNDA sengaja oleh
   رسلان sampai aplikasi "benar-benar fix". Jangan diusulkan lagi sampai
   رسلان sendiri yang angkat topik ini.
5. **OCR kamera fisik & widget kaca pembesar mengambang lintas-OS** —
   **DI-DROP**, bukan TODO aktif. Di luar kemampuan web app biasa (butuh
   aplikasi native terpisah untuk overlay sistem operasi). Jangan diusulkan
   lagi kecuali رسلان eksplisit mau mulai proyek aplikasi desktop/Android
   native terpisah suatu saat nanti.
6. **Integrasi `hanyu_extract`/`mandarin_kamus` mentah ke Kamus** — SELESAI
   secara efektif lewat `cidict_index.json` (lihat §2.2). Item TODO lama
   ini dianggap tuntas, tidak perlu diulang.
7. Kalau رسلان temukan celah baru pas pakai app (bug, UX kurang pas, dll)
   — prioritas selalu boleh disisipkan di atas semua ini.

---

## 4. Hal teknis tambahan (pelengkap BLUEPRINT_v10 §4, masih berlaku semua)

- **Skema `cidict_index.json`**: array datar, tiap entri
  `{id, simplified, traditional, pinyin, pinyin_numeric, meanings_id: [...], in_hsk}`.
  `pinyin` sudah beraksen (bukan angka nada), `meanings_id` sudah Bahasa
  Indonesia (CC-CIDICT, bukan CC-CEDICT Inggris).
- **Pola fallback dictionary standar yang sudah terbukti di 2 tempat**
  (`kamus.html` dan `terjemah-bebas.html`): cek `app_words.json` dulu
  (prioritas, kurasi manual), baru fallback ke `cidict_index.json` kalau
  nihil/kurang, lazy-load Cidict cuma saat benar-benar dibutuhkan (bukan
  saat halaman dibuka), tandai hasil fallback dengan flag per-item (bukan
  cuma state global) supaya bisa dicampur dengan hasil kamus utama tanpa
  bug — lihat `_cidictFallback` (kamus.html) dan `source: 'cidict'`
  (terjemah-bebas.html) sebagai referensi pola kalau mau dipakai lagi di
  halaman lain ke depannya (misal kalau dashboard nanti butuh lookup kata).
- **`app_words.json` struktur pembungkus**: dikonfirmasi array langsung
  (bukan `{"words": [...]}` atau varian lain) — kode `terjemah-bebas.html`
  punya fallback untuk 3 kemungkinan nama key pembungkus, tapi ternyata
  tidak diperlukan, array langsung yang dipakai.
- Semua hal teknis dari BLUEPRINT_v10 §4 (skema `graded_readers.json`,
  `grammar_hsk{1-6}.json`, `pattern_explanations.json`,
  `confusion_groups.json`, cara verifikasi coverage bacaan, dll) **masih
  berlaku sepenuhnya**, tidak ada perubahan.

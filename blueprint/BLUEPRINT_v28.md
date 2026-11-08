# BLUEPRINT v28 — Mandarin Interaktif

*Ditulis sebagai penutup sesi (lanjutan dari BLUEPRINT v27). Upload file ini
di awal percakapan baru bersama Claude supaya tidak perlu menjelaskan ulang
konteks proyek dari nol.*

---

## A. Ringkasan Proyek

**Mandarin Interaktif** — aplikasi belajar Mandarin offline milik رسلان,
murni HTML/CSS/JS vanilla (tanpa build tool/CDN wajib), berjalan lokal di
`C:\mandarin_app\` lewat `python -m http.server`. رسلان satu-satunya
developer & user. Semua pipeline data pakai Python di root folder proyek.
Backup pakai `checkpoint.py` (zip timestamped, 20 terbaru + arsip bulanan).

**Halaman utama:** `index.html` (dashboard), `kamus.html` (kamus + SRS
lookup), `flashcard.html`, `wordbuilder.html`, `tone.html`, `graded-reader.html`,
`hsk-exam.html`, `tatabahasa.html` (770+ poin grammar HSK1-9 — sekarang
punya hash-router deep-link + Daftar Isi lintas-level, lihat B.2),
`terjemah-bebas.html`, `peta-bahasa.html` (index 11 Pilar, semua badge
sekarang selaras — lihat B.1).

**Metodologi kerja yang sudah baku:** audit (read-only) → sample-check →
`--dry-run` → apply → `checkpoint.py save`. Setiap perubahan data besar wajib
lewat alur ini. Jangan menebak-nebak radikal/struktur karakter yang ambigu.
**Tambahan baru sesi ini:** untuk investigasi struktur data yang belum
jelas, jangan menebak nama field — tulis script kecil read-only ("intip")
yang dump isi & skema apa adanya, baru simpulkan. Lihat pola script di
Bagian D.3.

---

## B. Status Akhir Sesi Ini

Sesi ini murni **housekeeping + perbaikan navigasi + investigasi besar**
(diskusi & perencanaan), BUKAN sesi pembangunan fitur baru. Detail:

### B.1 — `peta-bahasa.html`: Badge status diselaraskan 100%

Ditemukan (dari laporan رسلان soal Pilar 1 & 2) bahwa badge status di
array `PILLARS` banyak yang **belum diupdate** meski `pilar_N.json`
(Pelajaran Lengkap) untuk pilar itu sudah lengkap sejak v27. Sudah
diperbaiki untuk **5 pilar**: 1 (Fonetik, 92.614 karakter — dulu ⚪ Belum),
2 (Angka, 77.876 karakter — dulu 🟡 Sebagian), 8 (Sapaan, dulu 🟡
Sebagian), 10 (Pragmatik, dulu 🟢 Baru), 11 (Variasi Bahasa, dulu 🟡
Sebagian — 4 sub-topik ⚪ diupdate jadi tercakup). **Hasil akhir: 11 dari
11 pilar sekarang ✅ Kuat.**

### B.2 — `tatabahasa.html`: Deep-link diperbaiki + fitur Daftar Isi baru

**Masalah awal:** tombol "Buka Tata Bahasa →" di `peta-bahasa.html`
(7 pilar: 3,4,5,6,7,8,9) semuanya cuma mengarah ke grid HSK kosong,
tidak lompat ke poin spesifik — رسلان bingung harus cari di mana.

**Perbaikan:**
1. Tambah hash-router `tatabahasa.html#search=QUERY` (query boleh
   berisi beberapa token dipisah koma, logika OR terhadap judul poin).
   Kalau hasil persis 1 poin → langsung ke detail. Kalau >1 → daftar
   hasil klik. Query untuk tiap pilar sebagian diambil dari
   `POINT_TO_WB_PATTERN` yang sudah terverifikasi manual (把/被, 可以/
   要/想, 了/过, 比/一样), sebagian tebakan istilah umum (量词, 代词/
   指示, 形容词/重叠 — **رسلان sudah konfirmasi semua tepat sasaran**).
2. **Fitur baru: Daftar Isi (📑 TOC)** — mengelompokkan 770 poin
   gramatika **per topik lintas 9 level HSK sekaligus** (bukan per
   level). Dibangun `CATEGORY_TOPIC_MAP`: tabel manual 74 nama kategori
   mentah → 28 topik kanonis, disusun dengan **mengecek isi**
   tiap kategori dulu (bukan cocokkan nama doang) — supaya kategori yang
   namanya beda gaya tulis tapi topiknya sama (mis. "Partikel" HSK1-9 yang
   tadinya kepisah 3 grup gara-gara kapitalisasi & sufiks "Baru") bisa
   digabung jadi 1, sementara yang isinya beda konten walau nama
   mirip (mis. "Kata Kerja Bantu" vs "Kata Kerja Bentuk Khusus") tetap
   dipisah. **Hasil final: 132 kategori mentah → 28 topik, 770 poin
   total (cocok persis dgn data riil رسلان)**. Accordion expand/collapse
   + kotak filter pencarian. Akses via tombol besar di layar depan,
   link cepat di breadcrumb (bisa dari layar manapun), atau deep-link
   `tatabahasa.html#toc`.

### B.3 — Investigasi besar: Bug Kamus & Fitur "Struktur Detail Kata
Polisemi" (diagnosis LENGKAP, siap eksekusi sesi depan — lihat Bagian E)

Dipicu laporan رسلان: klik 2 kartu 土 berbeda arti di `kamus.html`,
panel detail selalu nampilin entri yang sama. Investigasi meluas jadi
diskusi besar (belum coding, sesuai permintaan رسلان) soal permintaan
struktur detail kata yang lebih kaya (definisi per makna + contoh
kalimat + kelompok kelas kata, terinspirasi app Hanzii). Rangkuman
temuan penuh ada di Bagian D — semua sudah dikonfirmasi via script
read-only yang dijalankan رسلان secara lokal (bukan tebakan), termasuk
napak tilas ke BLUEPRINT v8-v26 utk lacak riwayat 2 file misterius.

---

## C. Arsitektur File Kunci (update dari v27)

**Kode diubah sesi ini:**
- `peta-bahasa.html` — array `PILLARS`: 5 entri diupdate status/desc/
  subtopics (lihat B.1).
- `tatabahasa.html` — tambah `CATEGORY_TOPIC_MAP` (74→28 mapping),
  fungsi `goToTocScreen()`/`buildTocGroups()`/`renderTocScreen()`/
  `renderTocList()`/`toggleTocGroup()`/`onTocFilterInput()`/
  `jumpToTocPoint()`, fungsi pencarian global `loadAllLevelsTolerant()`/
  `searchPointsAcrossLevels()`/`renderGlobalSearchScreen()`/
  `openSearchResult()`, hash-router di `initTataBahasa()` (`#search=`,
  `#toc`), breadcrumb diupdate (akses cepat Daftar Isi dari semua layar).

**Belum diubah — cuma didiagnosis, dieksekusi sesi depan:**
- `kamus/kamus-detail.js` — bug `selectWord(wordId, idx)`: parameter
  `idx` diterima tapi TIDAK PERNAH dipakai. `findWordInResults()` cari
  via `STATE.results.find(w => (w.id||w.simplified)===wordId)` — kalau
  ada 2 entri `wordId` sama di `STATE.results` (homograf), `.find()`
  selalu balikin yang PERTAMA, apapun kartu yg diklik. Fix: pakai
  `STATE.results[idx]` langsung sbg sumber utama, fallback ke pencarian
  by-id kalau idx invalid (utk kompatibilitas pemanggilan lain spt
  `selectWord(c.char, 0)` di `kamus-actions-filters.js:486`).

---

## D. Skema Data — Koreksi & Temuan Penting Sesi Ini

### D.1 — Koreksi skema `data/pelajaran/pilar_N.json` (v27 salah catat)

BLUEPRINT v27 tidak eksplisit soal nama field, dan asumsi awal sesi ini
(`konten`/`isi`, `header`/`baris`, `items`) **SALAH**. Skema riil yang
diverifikasi via audit Pilar 1,2,8,10,11 (semua lolos 100%, 0 isu):
- Tiap bagian: key `judul` + `isi` (array blok, BUKAN `konten`).
- Blok `tipe: "tabel"` pakai `kolom` (array header) + `baris` (array of
  array nilai) — BUKAN `header`.
- Blok `tipe: "contoh"` pakai `daftar` (array of `{hanzi, pinyin, arti,
  catatan}`) — BUKAN `items`.
- Blok `tipe: "poin"` pakai `daftar` juga (bukan `items`).
- 5 tipe blok valid: `paragraf | poin | tabel | contoh | peringatan`.

### D.2 — Skema lengkap `data/app_words.json` (11.983 entri, 29 field)

Field yang SELALU ada di semua entri: `id`, `simplified`, `traditional`,
`pinyin`, `bopomofo`, `radical`, `stroke_count`, `structure`,
`components`, `char_type`. Field yang SERING ada (>90%): `hsk`,
`meanings_id`, `meanings_en`, `pinyin_numeric`, `pos`, `pos_id`,
`frequency`, `radical_number`. Field yang JARANG ada (perlu di-guard
null): `hsk2` (4.991), `themes` (2.364), `contoh_kalimat_cn/pinyin/id`
(257 — ADA tapi TIDAK PERNAH dirender di `kamus-detail.js`, lihat E.0),
`synonyms` (116), `antonyms` (170), `_source_note` (256), `_flag` (21).
Field `pinyin_tone` (1 entri) dan `inyin_numeric` (0 entri, typo lama)
kemungkinan sisa eksperimen, tidak dipakai — aman diabaikan.

**Polusi metadata di `meanings_id`:** 1.437 item (4,5% dari 32.159 total
item) BUKAN makna asli, melainkan metadata yang nyempil: `KP:個|个[ge4]`
(1.038 — info kata-penggolong yang salah tempat), `varian dari X[py]`
(322), `Taiwan pr./dibaca` (68), `lihat juga` (9). **1.361 entri (11,4%)
kena dampak.** PENTING: regex deteksi yang dipakai sesi ini (`^varian
dari`, prefix-only) **TERBUKTI KURANG** — ditemukan varian `"variasi
dari X[py]"` (beda kata) dan pola nempel di TENGAH kalimat (mis. `"...
(varian dari 瞭|了[liao3])"`) yang lolos dari filter. **Perlu regex lebih
longgar (case-insensitive, cari di mana saja dalam string, bukan cuma
prefix) sebelum Tier 2 dieksekusi** — lihat E.2.

Setelah sampah dibersihkan (estimasi kasar dgn regex lama, kemungkinan
sedikit naik setelah regex diperbaiki): kandidat kata polisemi (≥3
makna bersih) **4.526 kata**, ≥5 makna **1.464 kata**, ≥8 makna **370
kata** — dari total 11.983.

### D.3 — Peta lengkap isi folder `data/` (hasil scan sistematis)

67 file total. Yang **aktif dipakai kode** (16 file, terverifikasi via
scan seluruh `.html`/`.js` proyek): `app_words.json`,
`char_etymology_id.json`, `cidict_index.json`, `graded_readers.json`,
`hanzi_writer_data.json`, `index_kelompok_khusus.json`,
`index_phonetic.json`, `index_radical.json`, `index_stroke.json`,
`index_theme.json`, `kata_majemuk_pola.json`, `nuance_pairs.json`,
`pattern_explanations.json`, `produktif_karakter.json`,
`tone_drills.json`, `wb_pools.json`. Plus `grammar_hsk1-9.json` dan
`data/pelajaran/pilar_1-11.json` — **aktif dipakai tapi TIDAK terdeteksi
scanner** karena dipanggil lewat template string (`` `data/grammar_hsk${level}.json` ``),
bukan literal string.

**51 file "yatim"** (tidak disebut kode manapun) — sebagian besar residu
pipeline yang tugasnya sudah selesai (bahan mentah generate index/tema/
graded-reader, laporan `peek_*`, 9 file `.txt` sumber grammar HSK,
backup lama `app_words.json.bak_*`/`graded_readers_backup_*`/
`index_theme_backup.json` — total >250MB tersebar di luar sistem
`checkpoint.py`, boleh dibereskan kapan saja tapi tidak mendesak).

**3 file yang jadi temuan penting** (dilacak via BLUEPRINT v8-v26 +
intip struktur langsung):
1. **`confusion_groups.json`** (53 grup karakter mirip bentuk, mis.
   己/已/巳, 大/太/犬) — **TERKONFIRMASI via BLUEPRINT v8**: "data siap,
   fitur belum dibangun". Sudah ~19 versi BLUEPRINT (v8→v27) tertunda.
   Rencana awal: fitur "Karakter Mirip" di Flashcard/Kamus.
2. **`character_etymology_en.json`** (3.034 karakter, ~586 entri
   `etymology` masih `null`) — BUKAN fitur tertunda, ini sumber mentah
   bahasa Inggris (proyek Make Me a Hanzi) yang dipakai sbg acuan saat
   membangun `char_etymology_id.json` (yang sudah 100% selesai, 2.840
   karakter). Tugasnya sudah selesai, aman diabaikan.
3. **`cidict_semantic_index.json`** (35,27 MB, 122.342 entri, 196.436
   total makna) — **TIDAK PERNAH disebut BLUEPRINT manapun** (dibuat di
   luar sesi terdokumentasi). Skemanya `{char, meanings: [{id, idn,
   context, examples}]}` — **nyaris identik dengan skema yang dibutuhkan
   Tier 3** (lihat E.3). Tapi **terkonfirmasi 0% terisi** di SEMUA
   196.436 makna (`context` selalu `"unknown"`, `examples` selalu `[]`)
   — termasuk di kata fokus polisemi (吃/了/着/那/里/是/打/上/下/麻/保).
   Murni kerangka struktural hasil pemecahan otomatis gloss CC-CEDICT,
   isi `idn`-nya sama-sama kena polusi `varian dari` spt D.2. **Dipakai
   sbg CETAKAN SKEMA untuk Tier 3, bukan sumber konten siap pakai.**

**`synonym_antonym.json`** (terpisah dari 16 file "aktif" di atas,
disebut BLUEPRINT v8: "sudah digabung ke app_words.json" — tapi hasil
scan sesi ini nunjukkin field `synonyms`/`antonyms` di app_words.json
cuma keisi 116-170 entri, sementara `synonym_antonym.json` sendiri
punya struktur lebih kaya per kata: `{word, pinyin, meaning_id, hsk,
synonyms: [{word, pinyin, note_id}], antonyms: [...]}`. Kemungkinan
merge lama tidak lengkap, atau ada versi lebih baru yang belum
tergabung — lihat E.0.

---

## E. Prioritas / Open Items untuk Sesi Berikutnya (5 tingkat, disepakati رسلان)

### E.0 — Kemenangan cepat (data sudah ada, tinggal sambung kode)
1. Render `contoh_kalimat_cn/pinyin/id` (257 entri) di panel detail
   `kamus-detail.js` — field sudah ada di data, belum pernah ditampilkan.
2. Cek & gabungkan `synonym_antonym.json` (struktur lebih kaya, ada
   pinyin+catatan nuansa) ke `app_words.json`, ganti tampilan
   sinonim/antonim yang sekarang cuma chip polos.
3. **Bangun fitur "Karakter Mirip"** pakai `confusion_groups.json`
   (53 grup) — item tertunda dari BLUEPRINT v8.

### E.1 — Bug fix: klik kartu duplikat di Kamus
Perbaiki `selectWord()`/`findWordInResults()` di `kamus-detail.js` spy
pakai `idx` (posisi di `STATE.results`) sbg penentu utama, bukan cari
ulang via `id`/`simplified` yang bisa duplikat (terutama saat sumber
Cidict aktif — 3.140 karakter berpotensi kena). Kecil, kontainable,
tidak ubah data.

### E.2 — Bersih-bersih `meanings_id` (scripted, tanpa AI generatif)
1. **Perbaiki dulu regex deteksi sampah** (lihat D.2) — case-insensitive,
   cari di mana saja dalam string (bukan cuma prefix), tangkap juga
   `"variasi dari"` selain `"varian dari"`.
2. Jalankan ulang dgn regex baru, audit → dry-run → apply.
3. Pindahkan info `KP:...` ke field baru `classifier` (bukan dibuang —
   itu info kata-penggolong yang berguna, cuma salah tempat).
4. Lengkapi terjemahan `pos`/`pos_id` yang masih kode mentah (`u`, `g`,
   `b`, dst — lihat sampel `个`/`了` di D.2).

### E.3 — Proyek besar bertahap: struktur makna kata polisemi
- **Skema**: adopsi bentuk `cidict_semantic_index.json`
  (`meanings: [{id, idn/definisi, context, examples: [{hanzi, pinyin,
  arti}]}]`) sbg cetakan — sudah tervalidasi struktural, tinggal isi
  konten.
- **Cakupan pilot**: JANGAN semua ~4.526 kandidat sekaligus. Mulai dari
  kata fungsi/karakter tersering & paling polisemi — kandidat awal:
  的/了/是/着/那/这/从/里/为/个/吃/打/上/下/错/麻/保 (bisa disesuaikan
  berdasar `frequency` field di app_words.json), targetkan 50-100 kata
  dulu, bertahap tiap sesi (pola sama spt `char_etymology_id.json`).
- **Sumber konten**: WAJIB digenerate (AI eksternal + audit Claude,
  pola sama spt `pilar_N.json`/`nuance_pairs.json`) — TIDAK ADA jalan
  pintas dari data yang sudah ada (semua sumber yang dicek 0% terisi).
- **Pengelompokan per kelas kata** (a. Kata Kerja / b. Kata Benda / dst)
  bisa manfaatkan field `pos`/`pos_id` yang sudah ada per entri (setelah
  E.2 selesai diterjemahkan) sbg starting point pengelompokan.
- Field asal ide رسلان (dari app Hanzii, dipakai sbg acuan FORMAT bukan
  konten yang disalin — pertimbangan hak cipta) juga minta bagian
  sinonim/antonim (sudah ada infrastrukturnya, tinggal E.0.2) dan
  "membedakan makna dgn kata mirip" (`尝` vs `吃`) — itu fitur TERPISAH
  yg sudah ada: `nuance_pairs.json` + `kamus-nuance.js` ("Beda dengan
  Kata Mirip"), tinggal dicek apakah kata pilot Tier 3 kebetulan sudah
  ada di situ juga.

### E.4 — Housekeeping (opsional, tidak mendesak)
Bereskan ~25+ file `app_words.json.bak_TIMESTAMP` (>250MB total) yang
menumpuk lepas di `data/`, di luar sistem `checkpoint.py`. Bisa
dijadwalkan kapan saja, bukan prioritas.

---

*Selesai — dokumen ini menggantikan BLUEPRINT v27 sebagai rujukan utama.*

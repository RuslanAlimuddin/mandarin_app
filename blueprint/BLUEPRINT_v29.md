# BLUEPRINT v29 — Mandarin Interaktif

*Ditulis sebagai penutup sesi (lanjutan dari BLUEPRINT v28). Upload file ini
di awal percakapan baru bersama Claude supaya tidak perlu menjelaskan ulang
konteks proyek dari nol.*

---

## A. Ringkasan Proyek

**Mandarin Interaktif** — aplikasi belajar Mandarin offline milik رسلان,
murni HTML/CSS/JS vanilla, berjalan lokal di `C:\mandarin_app\` lewat
`python -m http.server`. رسلان satu-satunya developer & user. Backup pakai
`checkpoint.py` (zip timestamped).

**Metodologi kerja yang sudah baku (TIDAK BERUBAH, makin terbukti penting
sesi ini):** audit (read-only) → sample-check → `--dry-run` → apply →
`checkpoint.py save`. Untuk investigasi struktur data/bug yang belum jelas,
JANGAN menebak — tulis script kecil read-only ("intip") yang dump isi/state
apa adanya, baru simpulkan. **Pelajaran keras sesi ini**: bahkan script intip
sendiri bisa salah (lihat E.0 poin 3) — verifikasi ulang kalau ada yang
terasa janggal, jangan percaya buta pada hasil audit lama tanpa re-cek kalau
muncul bukti yang bertentangan.

---

## B. Status Akhir Sesi Ini

Sesi ini isinya campuran: **housekeeping data** (E.0.1, E.0.2, E.0.2b),
**bug fix** (E.1, bug jumlah kartu game), dan **fitur besar baru**
(E.0.3 — Karakter Mirip) yang **90% selesai tapi ada 1 bug belum terpecahkan**
di bagian Kelompok Kamus. Detail lengkap di Bagian C-E.

---

## C. SELESAI & Terverifikasi رسلان di App

### C.1 — E.1: Bug klik kartu duplikat di Kamus — SELESAI
`kamus-detail.js`: `findWordInResults(wordId, idx)` sekarang prioritaskan
`STATE.results[idx]` (kalau valid & id-nya cocok) sebelum fallback ke
`.find()` lama. Fix bug lama: klik kartu homograf ke-2 (mis. 2 kartu 土
beda arti) sebelumnya selalu buka entri PERTAMA. **Diverifikasi رسلان
langsung di app, berfungsi baik.**

### C.2 — E.0.1: Render Contoh Kalimat — SELESAI
Field `contoh_kalimat_cn/pinyin/id` (257/11.983 entri) sekarang dirender
di panel detail Kamus (`kamus-detail.js` + `kamus.html`, section baru
`d-section-contoh`). Sebelumnya field ini ADA di data tapi tidak pernah
ditampilkan di kode manapun. **E.0.1b (perluas cakupan) masuk backlog,
lihat Bagian F — belum dikerjakan, رسلان mau fokus sinonim/antonim dulu.**

### C.3 — E.0.2: Perkaya Sinonim/Antonim dengan Nuansa — SELESAI
`data/synonym_antonym.json` (residu merge lama dari BLUEPRINT v8, ternyata
masih ada di `data/` tapi tidak dipakai kode manapun) digali ulang:
134 kata dapat field BARU `synonyms_detail`/`antonyms_detail`
(`{word, pinyin, note_id}` — catatan nuansa relasi, mis. 看→望: "menatap
jauh ke depan"), TANPA mengubah field lama `synonyms`/`antonyms`
(array-of-string, demi keamanan flashcard yang sudah pakai field itu).
`kamus-detail.js`: `renderRelWordChips()` diupgrade, prioritaskan
`note_id` kalau ada, fallback ke lookup arti generik kalau tidak.
**Diverifikasi رسلان di app (kata 看, 哭), berfungsi baik.**

### C.4 — Bug: Jumlah Kartu Game Diabaikan — SELESAI (ditemukan رسلان saat
testing C.3, di luar scope awal)
3 mode game (`tone-trap`/Jebakan Nada, `nuance-choice`/Pilih yang Tepat,
`pola-choice`/Tebak Pola Kata) mengabaikan setting "jumlah kartu" sesi,
selalu load dataset mentah penuh (974/2558/8867 soal). Root cause: 2
lapis — (1) `selectDeck()` di `flashcard-decks.js` tidak pernah shuffle+
slice sesuai `FC.sessionCardLimit` untuk 3 deck ini (beda dari deck
biasa yang lewat `buildDeckQueue()`), (2) `startAudioGame()` di
`flashcard-games.js` build ulang dari dataset PENUH saat classic
"Mulai Game" diklik, mengabaikan potongan yang sudah dibuat `selectDeck()`.
Fix: shuffle+slice di `selectDeck()`, simpan hasil ke
`FC.toneGame.nuanceQuestions`/`polaQuestions`/`groups`, `startAudioGame()`
pakai yang sudah tersimpan itu (bukan build ulang). **Diverifikasi
رسلان, berfungsi baik.**

### C.5 — E.0.2b: Perluas Cakupan Sinonim/Antonim — SELESAI (batch 1)
Sistem **reusable** dibangun untuk scan kandidat & generate prompt AI
eksternal, dipisah 2 tingkat:
- **Tingkat A** (murah): kata yang SUDAH ada relasi `synonyms`/`antonyms`
  tapi belum ada `_detail` (belum overlap dgn 134 kata C.3). AI cuma
  tambah `pinyin`+`note_id` untuk pasangan yang sudah pasti benar.
- **Tingkat B** (lebih mahal): kata HSK1-9 kata konten, relasi kosong
  total. AI tentukan relasi baru dari nol, instruksi ketat "jangan
  paksakan pasangan lemah".
- **Exclude overlap `nuance_pairs.json`** (1.291 kata unik) — supaya
  tidak buang kuota AI untuk kata yang sudah dibahas mendalam di fitur
  "Beda dengan Kata Mirip" (fitur BEDA, lihat catatan D.1).

**Batch 1 SELESAI diterapkan**: Tier A 20 kata (dari 60 kandidat awal,
40 overlap nuance_pairs dikecualikan) + Tier B 90 kata (dari 100 pilot,
9 sengaja kosong karena angka/nama tempat, 1 self-reference dibuang).
**Diverifikasi رسلان di app & flashcard, berfungsi baik.**

**Sisa kandidat Tingkat B murni (belum disentuh): 7.319 kata** dari
total 11.983 — روسلان akan lanjutkan batch berikutnya **di luar sesi
Claude** (dia sendiri yang jalankan pipeline-nya), baru dibawa kembali
untuk diaudit kalau sudah siap. **Sistem sudah reusable, TIDAK PERLU
Claude bikin ulang script apapun** — tinggal jalankan lagi
`generate_prompt_sinonim_antonim_v3.py` (self-updating: otomatis skip
kata yang sudah diisi & yang overlap nuance_pairs).

**Alur mandiri per batch (dari `C:\mandarin_app\`):**
```
python generate_prompt_sinonim_antonim_v3.py
→ proses prompt_tier_a_v3.txt & prompt_tier_b_pilot_v3.txt lewat AI eksternal
→ simpan jawaban sbg hasil_tier_a.json & hasil_tier_b_pilot.json (nama file TETAP SAMA)
python verifikasi_hasil_tier_a.py
python apply_hasil_sinonim_antonim.py --dry-run
python apply_hasil_sinonim_antonim.py
python checkpoint.py save
```
Kapan pun روسلان mau kasih hasil batch berikutnya ke Claude untuk
diaudit (opsional, kalau mau extra sanity-check sebelum apply), tinggal
upload `hasil_tier_a.json` + `hasil_tier_b_pilot.json` di sesi manapun.

---

## D. E.0.3 — Fitur "Karakter Mirip" — 90% SELESAI, 1 BUG BELUM PECAH

Fitur tertunda sejak BLUEPRINT v8 (~19 versi). Scope disepakati: Panel
Kamus + Game Flashcard + **Kelompok Kamus** (yang terakhir ini diminta
رسلان belakangan, di luar scope awal, karena mau "lihat gambaran luas
karakter mirip sekaligus").

### D.1 — Penting: BEDA dari fitur "Beda dengan Kata Mirip" yang sudah ada
Sengaja dipisah & dibedakan jelas:
- **"🆚 Beda dengan Kata Mirip"** (`kamus-nuance.js`, lama) = NUANSA MAKNA
  (尝 vs 吃, dua kata beda konteks pemakaian)
- **"👀 Karakter Mirip"** (`kamus-karakter-mirip.js`, BARU sesi ini) =
  KEMIRIPAN BENTUK TULISAN (己/已/巳, gampang ketuker pas nulis/baca cepat)

### D.2 — Panel Kamus — SELESAI, diverifikasi رسلان
`kamus-karakter-mirip.js` (file baru), arsitektur identik
`kamus-nuance.js`: berdiri sendiri, fetch sendiri dari
`data/confusion_groups.json`, MutationObserver di `#d-hanzi`, auto-hide.
**Index BIDIRECTIONAL** — buka karakter manapun dalam grup (bukan cuma
`character` utama) tetap memicu panel. Section HTML `d-section-mirip` +
CSS baru (`.mirip-chip`, `.mirip-note`) di `kamus.html`.

### D.3 — Game Flashcard — SELESAI, diverifikasi رسلان (setelah beberapa
revisi)
Deck baru "👀 Karakter Mirip" di grup Filter Game. Riwayat revisi (semua
berdasar masukan رسلان langsung, bukan tebakan):
1. Versi awal: audio-only (`qFormat: 'suara'`) — **DIKOREKSI**: inti
   permainan ini soal BENTUK, bukan cara baca, jadi audio tidak menguji
   hal yang tepat.
2. Revisi: `qFormat: 'terjemahan'` tetap (visual murni) — **DIKOREKSI
   lagi**: رسلان minta fleksibilitas kayak deck Antonim/Sinonim (soal
   boleh macam-macam format), TAPI jawaban WAJIB tetap hanzi polos
   (kalau jawaban boleh pinyin, jadi trivial — cuma cocok suara↔pinyin).
3. Final: dropdown baru `ctrl-confusion-qfmt` (Pinyin/Suara/Terjemahan/
   Acak — **Hanzi sengaja TIDAK ada di pilihan**, karena kalau soal=hanzi
   + jawaban=hanzi jadi trivial/cocok gambar identik). Fungsi baru
   `resolveConfusionFormat()` (bukan `resolveGameFormat()` generik) utk
   resolve pilihan "Acak" tanpa hanzi. Opsi jawaban (`aFormat`) DIKUNCI
   `'hanzi'`, tanpa dropdown, dan subtitle pinyin di bawah hanzi jawaban
   DISEMBUNYIKAN khusus mode ini (`renderGameOptions()`, cek
   `FC.toneGame.mode !== 'confusion'`).
4. Bug terpisah: tombol "Mulai Game" awalnya diam saja (tidak ada
   error) — root cause: `startSession()` di `flashcard-session.js`
   punya pengecekan eksplisit per `deckId`, `'confusion'` belum
   terdaftar di situ. **Fixed**, ditambahkan cabang seperti `tone-trap`.

File yang berubah: `flashcard.html` (sidebar item + dropdown + CSS
`.tg-feedback-note`), `flashcard-decks.js` (`loadConfusionData()`,
cabang `confusion` di `selectDeck()` — shuffle+slice sesuai
`sessionCardLimit` dari awal, TIDAK kena bug spt C.4), `flashcard-games.js`
(`buildConfusionGroups()`, cabang `confusion` di `startAudioGame()` /
`renderToneGameQuestion()` / `answerGame()` / `renderGameOptions()`,
`resolveConfusionFormat()`), `flashcard-session.js` (cabang `confusion`
di `startSession()`), `flashcard-init.js` (panggil `loadConfusionData()`).

**PERHATIAN untuk sesi baru**: `flashcard-games.js` yang رسلان upload di
tengah sesi ini sempat berupa **versi SEBELUM fix bug C.4** (kemungkinan
salah upload file lama) — Claude sudah gabungkan ulang kedua fix (C.4 +
D.3) jadi satu file final. **Kalau di sesi baru رسلان upload ulang file
ini, cek dulu apakah fix C.4 (jumlah kartu game) masih ada** sebelum
lanjut edit apapun — jangan asumsikan otomatis ada.

### D.4 — Kelompok Kamus — BELUM SELESAI, 1 BUG MENGGANTUNG

**Tujuan**: tombol baru "👀 Karakter Mirip" di sidebar Kelompok Kamus
(sejajar Radikal/Tema/Akar Kosakata/Kelompok Khusus). Klik tombol →
grid berisi **53 chip** (tiap chip = 1 grup lengkap, mis. chip
"己已巳" sebagai SATU chip gabungan, BUKAN per-karakter). Klik chip →
tampilkan SEMUA karakter dalam grup itu sebagai hasil pencarian
sekaligus.

**File yang sudah diubah** (semua sudah tervalidasi sintaks valid, tidak
ada yang crash):
- `kamus-data.js`: `STATE.dataConfusion` (array, dari `confusion_groups.json.groups`), fetch ditambahkan ke `loadIndexFiles()`, counter `cnt-mirip`.
- `kamus.html`: tombol sidebar `data-filter="group-mirip"` + `onclick="openGroupPanel('mirip')"`, span `id="cnt-mirip"`.
- `kamus-actions-filters.js`: cabang `type === 'mirip'` di `openGroupPanel()` — render 53 chip, tiap chip gabungan semua karakter dalam grup + `title` (tooltip) = catatan pembeda.
- `kamus-cards-ui.js`: cabang `type === 'mirip'` di `selectGroupItem()` (function ini sudah diubah jadi `async function`), plus fungsi baru `renderGroupResultsFromWords(words, label)` (inti render, terima objek kata langsung) yang di-reuse oleh `renderGroupResults(ids, label)` (wrapper lama, tetap dipakai grup lain, perilaku tidak berubah).

**BUG YANG BELUM TERPECAHKAN**: klik chip grup (mis. 己/已/巳, badge
menunjukkan "3") cuma menghasilkan **1 kartu** (`已`), bukan 3. Pola
sama untuk grup lain (大/太/犬 → cuma 2, 又/叉/义 → cuma 2, dst) —
**selalu kurang dari jumlah badge**, dan pola pengurangannya TIDAK
konsisten dengan diagnosis manapun yang sudah dicoba.

**Riwayat diagnosis yang SUDAH DICOBA dan GAGAL (jangan diulang tanpa
verifikasi baru):**

1. **Dugaan #1 (SALAH)**: `renderGroupResults()` mencari pakai
   `w.id || w.simplified` dengan `w.id` diprioritaskan; diduga `w.id`
   beda dari karakter mentah untuk kata homograf. **Fix dicoba**: resolve
   karakter ke `id` asli via `w.simplified` dulu sebelum kirim ke
   `renderGroupResults()`. **HASIL: tidak mengubah apa-apa, bug persis
   sama.**

2. **Dugaan #2 (SEBAGIAN BENAR, tapi bukan penyebab utama)**:
   `STATE.sidebarFilter` masih `'bookmarks'` (nyangkut dari sesi
   browsing sebelumnya), ikut menyaring hasil grup. **Dikonfirmasi via
   console log** (`sidebarFilter: bookmarks`), **fix diterapkan**
   (reset ke `'all'` + update highlight sidebar di awal
   `renderGroupResultsFromWords()`) — ini FIX YANG VALID dan
   KEMUNGKINAN BESAR masih relevan dipertahankan (bug nyata, cuma bukan
   penyebab utama kasus ini). **HASIL setelah fix**: `sidebarFilter`
   terkonfirmasi `'all'` di console, TAPI bug utama (cuma 1 dari 3
   hasil) TETAP TERJADI.

3. **Dugaan #3 (KEMUNGKINAN BESAR BENAR, tapi fix belum berhasil)**:
   via script `intip_unicode_karakter_mirip.py` (dijalankan رسلان,
   hasil lengkap tersedia di riwayat percakapan sesi ini) ditemukan
   **26 dari 115 karakter** di `confusion_groups.json` **memang tidak
   punya entri berdiri sendiri** di `app_words.json` (bukan bug
   encoding — semua codepoint Unicode dicek persis, cocok semua).
   Ini SESUAI keterbatasan yang SUDAH DICATAT di BLUEPRINT v10:
   *"app_words.json BUKAN kamus karakter lengkap — banyak karakter
   dasar umum (士, 相, 体, 众, 物, 世, dll) TIDAK punya entri berdiri
   sendiri"* — dan 士/体 PERSIS disebut di situ, cocok dengan temuan
   sekarang. **PENTING**: verifikasi awal Claude di awal sesi ini
   (`intip_confusion_groups.py`, jauh sebelum bug ini muncul) yang
   bilang "0 karakter hilang" **TERBUKTI CACAT** — salah asumsi
   struktur JSON (`{"groups":[...]}` dikira flat list), jadi loop
   pengecekannya diam-diam tidak pernah jalan.

   **Fix yang dicoba**: fallback ke `cidict_index.json` (125K+ entri,
   lebih lengkap) untuk karakter yang tidak ketemu di `app_words.json`.
   `selectGroupItem()` diubah jadi `async function`, cabang `mirip`
   sekarang: cari di `STATE.dataHsk` dulu, kalau tidak ketemu →
   `await loadCidict()` (kalau `STATE.dataCidict` belum ada) → cari di
   situ, tandai `_cidictFallback = true` di objek kata (konvensi yang
   sudah ada, dipakai `buildResultCard()` untuk styling beda). Hasil
   langsung dikirim ke `renderGroupResultsFromWords()` (BUKAN
   `renderGroupResults()` lama, supaya tidak di-lookup ulang dari
   `STATE.dataHsk` saja).

   **HASIL SETELAH FIX INI (paling membingungkan)**: بug **PERSIS SAMA**
   seperti SEBELUM fix — masih cuma 1 hasil (`已`), padahal 已 SENDIRI
   memang SEHARUSNYA berhasil lewat jalur normal (dia ADA di
   `app_words.json`, dikonfirmasi via `intip_unicode_karakter_mirip.py`).
   **Ini mencurigakan**: kalau fix beneran jalan, minimal harusnya ada
   PERUBAHAN dari 1→lebih banyak (даже kalau belum sempurna). Fakta
   hasilnya IDENTIK byte-per-byte dengan sebelum fix mengindikasikan
   kemungkinan besar **kode yang diedit TIDAK BENAR-BENAR TEREKSEKUSI**
   — dugaan kemungkinan: (a) file yang di-upload/ditimpa رسلان bukan
   versi terbaru yang dikirim Claude, (b) ada definisi
   `selectGroupItem`/`renderGroupResults` LAIN di file berbeda yang
   menimpa/dipanggil duluan (perlu grep SELURUH proyek), (c) caching
   browser meski "live reload" diklaim aktif, (d) event handler chip
   dipasang ganda dari sumber lain (delegasi event di luar
   `openGroupPanel()` yang belum pernah Claude lihat).

**REKOMENDASI LANGKAH PERTAMA di sesi baru** (JANGAN langsung edit kode
lagi, verifikasi eksekusi dulu):
1. Minta رسلان buka DevTools → tab **Sources** → buka
   `kamus/kamus-cards-ui.js` yang BENAR-BENAR ke-load browser → cari
   teks "Cidict fallback" atau "AKAR MASALAH SEBENARNYA" (komentar khas
   dari fix terakhir) — kalau TIDAK KETEMU, berarti file yang di-load
   browser BUKAN file yang sudah di-fix (jawaban langsung: file belum
   ke-update di server/browser, cek ulang proses timpa file / hard
   refresh / restart `python -m http.server`).
2. Kalau teks itu ADA (file sudah benar ke-load), tambah
   `console.log('[DEBUG] masuk cabang mirip, key=', key, 'chars=', chars)`
   sementara di awal cabang `mirip` di `selectGroupItem()`, cek apakah
   log ini MUNCUL sama sekali saat klik chip — kalau TIDAK MUNCUL,
   berarti ada handler lain yang nyegat klik sebelum sampai ke sini
   (grep seluruh proyek untuk `addEventListener` lain yang menyasar
   `.group-chip` atau `.sidebar-item`).
3. Kalau log MUNCUL tapi hasil tetap salah, baru lanjut debug isi
   `chars`/`words` array di titik itu step-by-step.

---

## E. Arsitektur File Kunci (update dari v28)

**Kode diubah/dibuat sesi ini:**
- `kamus/kamus-detail.js` — fix E.1 (idx-based lookup), render contoh
  kalimat E.0.1, upgrade `renderRelWordChips()` E.0.2.
- `kamus.html` — section `d-section-contoh` (E.0.1), `d-section-mirip`
  (D.2), tombol sidebar Kelompok "Karakter Mirip" (D.4), CSS terkait.
- `kamus/kamus-karakter-mirip.js` — **file baru** (D.2).
- `kamus/kamus-data.js` — `STATE.dataConfusion` + fetch (D.4).
- `kamus/kamus-actions-filters.js` — cabang `mirip` di `openGroupPanel()` (D.4).
- `kamus/kamus-cards-ui.js` — cabang `mirip` di `selectGroupItem()`
  (async, D.4, **ada bug**), `renderGroupResultsFromWords()` baru.
- `flashcard-decks.js` — fix C.4 (shuffle+slice 3 deck game), loader +
  cabang `confusion` D.3.
- `flashcard-games.js` — fix C.4, `buildConfusionGroups()`,
  `resolveConfusionFormat()`, cabang `confusion` di beberapa fungsi D.3.
- `flashcard-session.js` — cabang `confusion` di `startSession()` D.3.
- `flashcard-init.js` — panggil `loadConfusionData()` D.3.
- `flashcard.html` — sidebar item + dropdown + CSS D.3.

**Data diubah sesi ini:**
- `data/app_words.json` — field baru `synonyms_detail`/`antonyms_detail`
  (E.0.2, 134 kata), field `synonyms`/`antonyms`/`_detail` baru
  (E.0.2b, 110 kata: 20 Tier A + 90 Tier B).

**Script baru sesi ini** (semua di root `C:\mandarin_app\`, reusable):
`merge_synonym_detail.py`, `scan_kandidat_sinonim_antonim_v2.py`,
`generate_prompt_sinonim_antonim_v3.py` (**yang PALING PENTING —
reusable untuk lanjutan E.0.2b**), `verifikasi_hasil_tier_a.py`,
`apply_hasil_sinonim_antonim.py`, `intip_confusion_groups.py` (⚠️ CACAT,
jangan dipercaya hasilnya), `intip_unicode_karakter_mirip.py` (berguna,
bisa dipakai lagi kalau ada dugaan masalah encoding serupa di masa
depan), beberapa script pencarian riwayat BLUEPRINT (`cari_riwayat_
sinonim_di_blueprint.py`, `cari_item_belum_selesai_semua_blueprint.py`,
`cari_residu_sinonim_di_proyek.py`) — sudah tidak perlu dipakai lagi
kecuali audit serupa dibutuhkan lagi nanti.

---

## F. Prioritas / Open Items untuk Sesi Berikutnya

### F.0 — PALING MENDESAK
**Selesaikan bug D.4** (Kelompok Kamus Karakter Mirip) — ikuti langkah
diagnostik di D.4 sebelum coba fix baru lagi. JANGAN menebak lagi tanpa
verifikasi eksekusi kode dulu.

### F.1 — Sedang berjalan di luar sesi (رسلان kerjakan sendiri)
E.0.2b lanjutan (perluas sinonim/antonim, 7.319 kandidat tersisa) —
sistemnya sudah siap (lihat C.5), tinggal دijalankan رسلان kapan pun,
opsional dibawa balik ke Claude untuk diaudit.

### F.2 — Backlog aktif (dicatat, dikerjakan kalau giliran tiba — SUDAH
tersimpan di memori Claude juga, tapi dicatat ulang di sini demi
portabilitas kalau memori tidak terbawa)
- E.0.1b — perluas cakupan contoh kalimat (259/11.983 masih kosong)
- Perluasan `confusion_groups.json` (Karakter Mirip, 53 grup) — **setelah**
  bug D.4 solve dulu, baru dipikirkan perluasan datanya
- Sufiks/Prefiks Produktif (者/家/化 dst) — grup baru Kamus + referensi
  Tata Bahasa, رسلان setuju arahnya
- Measure word pairing & kata kerja berantai/verb complement — butuh
  kurasi data dari nol, flashcard game + pelajaran
- Pola nada khusus/sandhi 3-3 — masuk pelajaran/Tata Bahasa saja
- 多音字 (karakter multi-bacaan) — prioritas tinggi kalau mau garap
  topik terkait 回文/karakter simetris, scan dulu data lama
- Refactor tombol "Tambah ke Tema" — bukan bikin tema baru, tapi
  "tambahkan kata ke tema existing" (dropdown)
- Statistik Latihan Nada di Dashboard
- Dead code lama `flashcard.html` — bersihkan opportunistic
- Skema kata majemuk 3+ karakter (1.287 kata belum masuk klasifikasi pola)
- Dashboard progres gabungan (SRS+koleksi+riwayat)
- Dictation (dengar→ketik) — masuk flashcard game
- 614 kata di luar HSK1-9 — gabung ke `app_words.json` + field tag
  keterangan (bukan kamus terpisah)
- Placement test HSK — gabung jadi mode "Tes Cepat" di `hsk-exam.html`

### F.3 — Ditunda permanen (jangan diusulkan lagi kecuali رسلان angkat topik)
- Hapus folder `hanyu_extract`/`mandarin_kamus`
- OCR kamera/hover-translate
- Verifikasi ulang ~1.700 kata 动宾式/补充式 (AI eksternal tidak andal)
- Sentence mining pribadi
- UI koleksi Word Builder `mandarin_wb_saved` (dihapus total alurnya)

---

*Selesai — dokumen ini menggantikan BLUEPRINT v28 sebagai rujukan utama.*

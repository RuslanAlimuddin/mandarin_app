# BLUEPRINT_v15 — Mandarin Interaktif
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
online saat aplikasi berjalan. Pengecualian yang sudah disepakati: skrip
Python terpisah yang رسلان jalankan manual sekali di lokal untuk MENYIAPKAN
data itu boleh — bukan bagian aplikasi yang berjalan. **Konsekuensi teknis
penting** (ketemu sesi ini, lihat §2.6): aplikasi yang jalan di browser
TIDAK BISA menulis balik ke file `app_words.json` di disk — jadi fitur apa
pun yang "menambah kata ke kamus" dari dalam aplikasi yang sedang berjalan
cuma bisa nyimpan ke localStorage (data mandiri di tema/deck itu sendiri),
bukan menyatu permanen ke `app_words.json`. Penggabungan permanen ke
`app_words.json` tetap harus lewat Claude/skrip Python lokal seperti biasa.

**Halaman yang sudah ada** (semua saling terhubung lewat navbar, 9 halaman
total, TIDAK ada halaman baru sesi ini): `index.html`, `kamus.html` (modular,
folder `kamus/`), `flashcard.html`, `wordbuilder.html`, `tone.html`,
`graded-reader.html`, `hsk-exam.html`, `tatabahasa.html`,
`terjemah-bebas.html`.

**File data utama**: `app_words.json` sekarang **11.671 entri** (naik dari
11.470 — lihat §2.5), `index_theme.json` diperbarui menyertai. File bersama
& data lain TIDAK BERUBAH dari BLUEPRINT_v14 kecuali yang disebut eksplisit
di §2 bawah ini.

---

## 2. Apa yang dikerjakan sesi ini (semua DI LUAR blueprint v14 — رسلان
### tandai eksplisit tiap kali mengangkat topik baru sesi ini)

### 2.1 Kamus — perbaikan & fitur baru

- **Bug ⿰⿰ dobel di panel Struktur (FIXED)** — `structureLabel()` sudah
  mengembalikan label lengkap dgn ikon di depan (`"⿰ Kiri–Kanan"`), tapi
  kode lama mengekstrak ikon itu lagi & menampilkannya terpisah TANPA
  menghapus dari teks label → tampil dobel. Diperbaiki di `kamus-detail.js`.
  Sekalian badge struktur dibikin bisa **diklik** → buka grup "Per Struktur".
- **Grup "Per Struktur" AKTIF** (sebelumnya "segera hadir" placeholder) —
  ternyata field `structure` sudah ada di semua 1.571+ entri karakter
  tunggal `app_words.json`, tinggal dipakai. Index dibangun client-side
  (`buildStructureIndex()` di `kamus-data.js`, lazy), wiring ke
  `kamus-actions-filters.js` (`openGroupPanel`) & `kamus-cards-ui.js`
  (`selectGroupItem`). Sengaja dibatasi karakter tunggal saja (struktur IDC
  secara konsep tentang komposisi 1 karakter).
- **Grup "Per Pinyin" 2-level** — sebelumnya klik huruf langsung tampilkan
  RATUSAN hasil tak terpilah. Sekarang: klik huruf → tampil turunan suku
  kata yang BENAR-BENAR ada datanya (ba/bi/bo/bu/bai/ban/dst, bukan daftar
  statis), tombol "‹ Kembali". zh/ch/sh dipecah 3 huruf. **Sekalian
  ditemukan & diperbaiki bug laten**: filter pinyin lama membandingkan
  string mentah berdiakritik nada (`bā`) langsung dgn prefix ASCII polos
  (`ba`) — otomatis gagal cocok utk apa pun selain huruf tunggal. Sekarang
  pakai `normalizePinyin()` (utility yg sudah ada di `shared/pinyin.js`).
- **Sinonim/Antonim + pinyin + arti** — sebelumnya chip cuma tampil hanzi
  polos tanpa pinyin/arti. Sekarang chip 2 baris (hanzi + pinyin·arti),
  lookup offline dari `STATE.dataHsk` sendiri via helper baru
  `relWordInfo()`/`renderRelWordChips()` di `kamus-detail.js`.

### 2.2 Flashcard — perbaikan & fitur baru

- **Sinonim/Antonim + pinyin + arti** di kartu jawaban — field ini
  TERNYATA sudah ada sejak awal tapi cuma render teks polos kecil, mudah
  terlewat. Sekarang format `hanzi (pinyin - arti)`, reuse
  `FC.wordBySimplified`. Fungsi baru: `fcRelWordsHtml()`.
- **FIXED — deck kecil "tidak ada kartu yang perlu diulang" (root cause
  ketemu & diperbaiki, 2 lapis perbaikan)**:
  1. **Penyebab akar**: status SRS (due/tidak) melekat pada KATA, bukan
     DECK — satu kata bisa muncul di banyak deck (tema/HSK/radikal) tapi
     jadwal ulangnya cuma satu, dipakai bersama. Untuk deck kecil (tema
     1-5 kartu), begitu semua kartunya kebetulan sudah pernah dinilai di
     deck LAIN & belum jatuh tempo lagi, deck itu tampak "mati total".
  2. **Fix #1 — auto-fallback**: deck tematik/browse (tema, radikal,
     struktur, custom, fonetik, antonim/sinonim, goresan) — kalau semua
     kartunya sudah dikuasai & tidak due, otomatis tampilkan ulang semua
     utk "review bebas" (bukan kosong). Deck inti SRS (hsk-/all-due/
     bookmarks/wrong) SENGAJA tidak disentuh.
  3. **Fix #2 — toggle manual "🔓 Sertakan kartu belum jatuh tempo"** di
     panel Pengaturan Sesi. Berlaku utk deck APA PUN (bukan cuma tematik).
     Status tersimpan (localStorage).
  4. **Bug lanjutan ketemu & diperbaiki**: checkbox toggle di atas
     awalnya cuma nyimpen status (`FC.ignoreDue = checked`) TANPA memicu
     bangun ulang antrian deck yang lagi aktif — jadi kalau رسلان centang
     SETELAH deck kepilih, tidak ada efek sampai deck diklik ulang. Sudah
     diperbaiki: `onchange` sekarang otomatis `selectDeck()` ulang kalau
     ada deck aktif.
  5. **Toast diperjelas** — 3 kondisi beda pesan: toggle manual aktif,
     fallback otomatis (semua sudah dikuasai), normal. Juga dibedakan
     "pool benar-benar 0 kata" vs "ada kata tapi semua lagi tidak due"
     (`FC.lastPoolSize`, `FC.lastQueueReviewReason`).
  6. **Sudah dikonfirmasi رسلان jalan dgn baik** setelah data tema
     diperbesar (§2.5) — kartu baru otomatis masuk kategori "fresh",
     selalu tampil dgn/tanpa toggle. Efek toggle baru kelihatan setelah
     SEMUA kartu di suatu deck sudah direview & ditandai "Mudah"/dst.
- **"+ Tema Baru" DILENGKAPI** — fitur ini TERNYATA sudah ada sebelumnya
  tapi setengah jadi: bikin tema kosong (`words: []`) tanpa cara mengisi
  kata sama sekali. Sekarang tiap tema custom punya tombol **➕** (tambah
  kata — cari dari `FC.allWords` sendiri via ketik hanzi, dipisah koma)
  dan **🗑** (hapus tema). Fungsi baru: `promptAddWordsToCustomTheme()`,
  `promptDeleteCustomTheme()`.
- **Label jumlah kartu di tema** — angka di sidebar tema itu memang
  jumlah kartu (`count` dari `index_theme.json`), sebelumnya ambigu tanpa
  label. Sekarang ada teks kecil "kartu" + tooltip hover, di tema bawaan
  maupun custom.

### 2.3 Word Builder ↔ Tata Bahasa — cross-link baru

- **32 dari 34 pola Word Builder** dipetakan ke poin gramatika HSK yang
  sesuai (dicek satu-satu formulanya, bukan tebak dari judul) — lihat
  `POINT_TO_WB_PATTERN` di `tatabahasa.html`. 2 yang SENGAJA tidak
  dipetakan: `S-V` (terlalu generik, tidak ada poin HSK spesifik) dan
  `S-T-V-O` (tidak ada poin HSK yang cocok).
- Di halaman detail poin `tatabahasa.html`, kalau ada padanannya, muncul
  tombol emas "🧩 Latih pola ini di Word Builder: [nama] →".
- `wordbuilder.html`: fungsi baru `consumeRefPattern()` — baca
  `wb_ref_pattern` dari localStorage (ditulis tatabahasa.html), otomatis
  buka tab (tunggal/majemuk/fungsi, ditentukan dari awalan kunci pola) +
  pola yang dimaksud. Pola sama persis dgn `wb_ref_word` (handoff dari
  Flashcard) yang sudah ada sebelumnya.

### 2.4 Data quality — temuan sampingan (BELUM diperbaiki, dicatat saja)

Saat mengerjakan §2.5, ditemukan beberapa karakter TUNGGAL di
`app_words.json` yang field `pinyin`-nya adalah bacaan LANGKA, bukan
bacaan umum, kalau karakter itu berdiri sendiri — mis. **广** tersimpan
"yǎn" (harusnya "guǎng" utk pemakaian umum), **转** "zhuǎi" (harusnya lebih
sering "zhuǎn"), **提** "dī" (harusnya lebih sering "tí"). Ini BUKAN bug
yang saya buat sesi ini — sudah ada sejak awal, warisan dari sumber data
asli (`drkameleon/complete-hsk-vocabulary` — dicek sesi ini, memang sumber
itu sendiri yang punya bacaan langka utk karakter berdiri sendiri, karena
list itu fokus ke kosakata HSK bukan bacaan-tunggal-paling-umum). Tidak
urgent — kemungkinan besar jarang kelihatan karena karakter ini biasanya
muncul dlm kata majemuk (pinyin kata majemuknya benar), bukan sendirian.
**Belum diperbaiki** — kalau رسلان suatu saat menemukan pinyin karakter
tunggal yang terasa janggal di kamus, ini kemungkinan penyebabnya, bisa
jadi topik audit terpisah nanti (tidak perlu diusulkan proaktif).

### 2.5 Ekspansi 18 tema kecil — 201 kata baru

**Latar belakang**: رسلان komplain banyak tema di Flashcard cuma
berisi 1-6 kartu (mis. "Nama Negara Utama"=1, "Natal"=2). Diselidiki &
diperbaiki total lewat 2 tahap:

- **15 tema** dari `data/unmatched_theme_words.json` milik رسلان sendiri
  (sisa usaha ekspansi tema sebelumnya yang belum sempat digabung — sumber
  asli: AllSet Learning Vocabulary Wiki, lisensi **CC BY-NC**, atribusi
  dicatat per-entri via field `_source_note`). 155 kata, terjemahan
  Indonesia disusun manual satu-satu oleh Claude.
- **3 tema sisa** (Nama Negara Utama, Bentuk & Bangun, sisa Olahraga Bola)
  — TIDAK ada di `unmatched_theme_words.json` (sumbernya sendiri memang
  cuma punya sedikit utk kategori ini), jadi dicari dari
  `data/cidict_index.json` (CC-CEDICT, arti Indonesia sudah tersedia
  langsung di situ). 46 kata.
- **Field yang dihitung** (bukan tebakan) untuk semua 201 kata:
  - **Bopomofo** — dikonversi dari pinyin via rumus konversi standar
    (dibangun & DIVALIDASI sesi ini terhadap 1000 sampel data resmi
    `drkameleon/complete-hsk-vocabulary`, akurasi 99.7% setelah 4 bug
    ditemukan & diperbaiki — lihat kode `pinyin_to_bopomofo()` di
    `build_theme_entries.py`, sudah diserahkan ke رسلان).
  - **Radikal/goresan/struktur/komponen** — dari Make Me a Hanzi
    (`dictionary.txt` + `graphics.txt`, sumber sama dgn kerja etimologi
    `char_etymology_id.json` sebelumnya).
  - **Pinyin** — direkonstruksi per-karakter dari `cidict_index.json`;
    **24 kata** yang hasil rekonstruksi otomatisnya salah (karakter
    multi-bacaan, lihat §2.4) dikoreksi manual satu-satu.
  - **HSK/frekuensi** — SENGAJA `null` utk semua 201 kata. Dicek terhadap
    `complete-hsk-vocabulary` (daftar HSK resmi lengkap): 0 dari 77
    kandidat awal ketemu di situ — jadi ini memang bukan kosakata HSK
    resmi (negara/kota/merek/kosakata niche tidak diuji HSK), bukan celah
    data yang terlewat.
- **Hasil**: semua 18 tema kecil sekarang 8-25 kartu (dari 1-6). Detail
  angka per tema ada di riwayat chat sesi ini kalau perlu dicek ulang.
- **Skrip pendukung** (sudah diserahkan ke رسلان, taruh di `C:\mandarin_app`
  kalau mau disimpan): `build_theme_entries.py` (15 tema pertama, berisi
  konverter bopomofo tervalidasi — REUSABLE utk kerja data lain ke depan),
  `build_remaining_themes.py` (3 tema sisa).

### 2.6 Skrip baru: `scan_local_data.py`

Skrip pengintai read-only (tidak pernah mengubah/menghapus apa pun) untuk
`C:\mandarin_app` & `C:\mandarin_kamus` — memetakan semua file + sampel
acak isinya, supaya Claude sesi depan bisa cek data lokal yang رسلان sudah
punya SEBELUM cari ke sumber luar (GitHub dkk). رسلان jalankan manual,
hasilnya (`scan_report.txt`) di-paste ke chat. **Pola ini terbukti sangat
berguna sesi ini** (nemu `unmatched_theme_words.json` yang jadi sumber
utama §2.5) — disarankan jadi kebiasaan: kalau Claude butuh data yang
mungkin sudah ada lokal, minta رسلان jalankan skrip ini dulu drpd langsung
cari ke GitHub/luar.

---

## 3. TODO — untuk sesi berikutnya

### 3.1 Prioritas #1: رسلان coba `complete_theme_json.py` sendiri
Belum pernah dijalankan رسلان di `C:\mandarin_app` miliknya sendiri —
lihat §3.3. Ini prioritas paling atas sesi depan, sebelum hal lain.

### 3.2 Verifikasi lanjutan lain oleh رسلان
Sebagian besar perbaikan sesi ini SUDAH dikonfirmasi رسلان jalan baik
(toggle ignoreDue, ekspansi tema). Yang masih perlu ditest kalau رسلان
sempat: fitur ➕/🗑 tema custom (belum pernah dites sama sekali), cross-
link tatabahasa→wordbuilder (32 pola — kalau ada mapping yang terasa
kurang pas, tinggal edit satu baris `POINT_TO_WB_PATTERN`), grup "Per
Struktur" & turunan pinyin di kamus.

### 3.3 "Import Tema dari JSON" — skrip SUDAH DIBUAT & DIUJI, رسلان BELUM SEMPAT COBA

**Update dari rencana awal**: setelah didiskusikan ulang, رسلان TIDAK
mempermasalahkan data hasil import tidak menyatu penuh ke `app_words.json`
lewat aplikasi yang berjalan (lihat §1) — alurnya justru dibalik: رسلان
sudah punya kebiasaan minta AI LAIN bikin file JSON tema mentah (prompt
sudah رسلان punya sendiri, formatnya `{theme, words:[{hanzi,pinyin,
translation}]}`), lalu MAU skrip Python yang melengkapi file itu jadi
entri `app_words.json` siap pakai, dijalankan di PC رسلان sendiri.

**Sudah dibangun sesi ini: `complete_theme_json.py`** — generalisasi dari
`build_theme_entries.py`/`build_remaining_themes.py` (§2.5) jadi 1 skrip
reusable utk tema apa pun ke depannya. **100% offline**, baca semua
referensi dari file lokal رسلان yang sudah dikonfirmasi ada (lihat
`scan_report.txt` sesi lalu): `data/dictionary.txt`,
`data/hanzi_writer_data.json`, `data/cidict_index.json`.

**Cara kerja**: untuk tiap kata di JSON mentah — (1) kalau hanzi-nya sudah
ada di `app_words.json`, cuma ditambah tag tema baru (tidak duplikat); (2)
kalau belum ada tapi ketemu di `cidict_index.json`, pakai arti resmi dari
situ (lebih dipercaya drpd "translation" dari AI lain) + radikal/goresan/
struktur/bopomofo dihitung otomatis; (3) kalau benar-benar tidak ada di
manapun, tetap dibangun pakai pinyin+translation dari JSON mentah, tapi
ditandai jelas di laporan sbg "PERLU DICEK MANUAL". `app_words.json` &
`index_theme.json` ditulis LANGSUNG (in-place, dgn backup otomatis
`.bak_TIMESTAMP` sebelum nulis). Aman dijalankan berkali-kali (idempoten
— kata yg sudah ada tidak diduplikasi).

**Sudah diuji Claude** (3 skenario: kata sudah ada/kata baru-tapi-di-cidict/
kata baru sama sekali, + tes idempoten jalankan file sama 2x) — semua
lolos di lingkungan simulasi. **رسلان BELUM SEMPAT COBA LANGSUNG di
`C:\mandarin_app` miliknya sendiri** — ini prioritas #1 sesi berikutnya.
Kalau ada error path/format file lokal yang beda dari asumsi skrip (mis.
`hanzi_writer_data.json` struktur field-nya sedikit beda), laporkan ke
Claude sesi depan utk diperbaiki.

File skrip: `complete_theme_json.py` (sudah diserahkan ke رسلان).

### 3.4 Item lama — status TIDAK BERUBAH dari v14
- Hapus folder `hanyu_extract`/`mandarin_kamus` — TETAP ditunda sampai
  tahap akhir proyek. Jangan diusulkan sampai رسلان sendiri angkat topik.
- OCR kamera fisik & widget kaca pembesar — TETAP di-drop permanen.

---

## 4. Hal teknis tambahan

Semua konvensi dari BLUEPRINT_v12/v13/v14 §4 **masih berlaku penuh**
(diskusi dulu sebelum coding scope besar, `node --check` utk JS, verifikasi
tag seimbang, Bahasa Indonesia, رسلان tidak punya akses filesystem langsung
ke Claude, dll).

**Tambahan baru sesi ini**:
- **Pola baru yang sangat berguna — "intip data lokal dulu"**: sebelum
  Claude cari data ke sumber luar (GitHub dkk), lebih baik minta رسلان
  jalankan `scan_local_data.py` dulu (§2.6) — sesi ini terbukti رسلان sudah
  punya banyak data relevan tersimpan lokal (`unmatched_theme_words.json`,
  dll) yang tidak diketahui Claude sampai diminta.
- **Pola baru — validasi kuantitatif sebelum percaya hasil hitungan
  sendiri**: konverter bopomofo diuji ke 1000 sampel data resmi SEBELUM
  dipakai ke data sungguhan — ketemu 4 bug yang tidak akan ketahuan cuma
  dari baca kode. Pola ini disarankan dipakai lagi utk kerja data
  algoritmik serupa ke depan (bukan cuma spot-check 2-3 contoh).
- **Pola baru — jangan percaya "ambil entri pertama" dari kamus mentah**:
  `cidict_index.json` (CC-CEDICT) bisa punya banyak baris per karakter yg
  sama (beda makna/bacaan) — ambil baris pertama begitu saja bisa kena
  bacaan langka (§2.4). Kalau butuh bacaan "paling umum" utk karakter
  tunggal, lebih aman cross-check ke `app_words.json` yg sudah dipakai
  aplikasi dulu (meski §2.4 menunjukkan itu juga tidak 100% bebas masalah
  utk sebagian kecil karakter).
- **Sumber data baru yang dipakai sesi ini** (semua via `raw.githubusercontent.com`,
  sudah ada di domain yang diizinkan untuk Claude):
  - `drkameleon/complete-hsk-vocabulary` — dipakai utk validasi bopomofo
    & cek cakupan HSK resmi. Berguna utk sesi depan kalau perlu HSK
    level/frekuensi resmi lagi.
  - `skishore/makemeahanzi` (`dictionary.txt`+`graphics.txt`) — sama
    dgn sumber `char_etymology_id.json` sebelumnya, dipakai lagi utk
    radikal/goresan/struktur/komponen kata baru.
- **File-file modular yang disentuh sesi ini**: `kamus/kamus-detail.js`,
  `kamus/kamus-actions-filters.js`, `kamus/kamus-cards-ui.js`,
  `kamus/kamus-data.js`. File modular lain (`kamus-search.js`,
  `kamus-storage-layout.js`, `kamus-stroke-order.js`, `kamus-init.js`)
  TIDAK disentuh sesi ini (kecuali `kamus-search.js` yang SEMPAT dibaca
  untuk referensi `normalizePinyin()` tapi tidak diedit).

---

## 5. Ringkasan file yang berubah/baru sesi ini

| File | Status | Catatan |
|---|---|---|
| `data/app_words.json` | Diperbarui | 11.470 → 11.671 entri (+201, lihat §2.5) |
| `data/index_theme.json` | Diperbarui | 18 tema kecil naik jadi 8-25 kartu tiap tema |
| `kamus/kamus-detail.js` | Diperbarui | Fix bug ⿰⿰, badge struktur clickable, sinonim/antonim +pinyin+arti |
| `kamus/kamus-actions-filters.js` | Diperbarui | Grup Per Struktur aktif, pinyin 2-level |
| `kamus/kamus-cards-ui.js` | Diperbarui | selectGroupItem cabang 'struct', fix filter pinyin (normalizePinyin) |
| `kamus/kamus-data.js` | Diperbarui | STATE.dataStructure + buildStructureIndex() |
| `flashcard.html` | Diperbarui | Sinonim/antonim +pinyin+arti, fix deck kosong (2 lapis), lengkapi tema custom (➕/🗑), label jumlah kartu |
| `wordbuilder.html` | Diperbarui | consumeRefPattern() — terima handoff dari tatabahasa.html |
| `tatabahasa.html` | Diperbarui | POINT_TO_WB_PATTERN (32/34 pola), tombol "Latih pola ini" |
| `scan_local_data.py` | **Baru** | Skrip pengintai read-only C:\mandarin_app & C:\mandarin_kamus |
| `complete_theme_json.py` | **Baru — belum dicoba رسلان** | Lengkapi JSON tema mentah (hasil AI lain) jadi entri app_words.json siap pakai, tulis langsung in-place + backup otomatis. Diuji Claude (3 skenario + idempoten), رسلان belum coba sendiri |
| `build_theme_entries.py` | **Baru** | Skrip build 15 tema + konverter bopomofo tervalidasi (reusable) |
| `build_remaining_themes.py` | **Baru** | Skrip build 3 tema sisa |
| Semua file lain | Tidak berubah | Termasuk `kamus.html`, `style.css`, `kamus-search.js`, `kamus-storage-layout.js`, `kamus-stroke-order.js`, `kamus-init.js` |

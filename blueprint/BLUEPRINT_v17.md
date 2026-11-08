# BLUEPRINT_v17.md — Mandarin Interaktif

**Handoff document untuk sesi Claude berikutnya.** Tempel isi file ini di awal percakapan baru supaya Claude langsung punya konteks penuh tanpa perlu dijelaskan ulang dari nol.

Lokasi proyek: `C:\mandarin_app\` (Windows, رسلان adalah satu-satunya developer & user).
Stack: vanilla HTML/CSS/JS murni, tanpa build step, tanpa dependency eksternal (offline-first 100%).

---

## 1. Ringkasan Aplikasi

Aplikasi belajar Mandarin pribadi, terdiri dari beberapa halaman:
- `index.html` — beranda/dashboard (streak, progres HSK)
- `kamus.html` (+ modul `kamus/*.js`) — kamus/dictionary, tampilan statis untuk menjelajah kata
- `flashcard.html` (+ modul `flashcard/*.js`, **baru dimodularisasi v17**) — SRS (spaced repetition) + berbagai mode game/latihan
- `wordbuilder.html` (+ modul `wordbuilder/*.js`, **baru dimodularisasi v17**) — susun kalimat, kuis pola, spot-the-error
- `graded-reader.html` — bacaan berjenjang HSK **+ percakapan/dialog bubble chat (baru v17)**
- `tone.html`, `hsk-exam.html`, `tatabahasa.html` — modul pendukung lain

**Prinsip arsitektur yang WAJIB dipatuhi:**
- 100% offline, tidak ada CDN/API eksternal.
- `cidict_index.json` = sumber kanonis CC-CEDICT (sudah dalam Bahasa Indonesia), ~125rb entri. **PENTING (baru ketahuan v17): banyak kata punya beberapa entri berbeda bacaan (marga/sastra/modern) — jangan asumsikan entri pertama = bacaan yang benar.** Lihat §3.3.
- Jalankan `node --check` pada semua JS sebelum diserahkan ke رسلان.
- **Selalu baca isi file aktual sebelum mengedit** — jangan pernah asumsi isi file.
- Cek keseimbangan tag HTML (div dsb) per-file DAN gabungan lintas file modular.
- **Alur PART-file (`gabung_*.py`) SUDAH TIDAK BERLAKU untuk `kamus.html`, `flashcard.html`, DAN `wordbuilder.html`** (ketiganya sudah dimodularisasi). Edit langsung ke file modul `.js` yang relevan di masing-masing subfolder.
  - `kamus/` — 8 file (`kamus-data.js` s/d `kamus-init.js`, init **wajib paling akhir**)
  - `flashcard/` — 6 file: `flashcard-srs.js`, `flashcard-decks.js`, `flashcard-session.js`, `flashcard-games.js`, `flashcard-storage-layout.js`, `flashcard-init.js` (**wajib paling akhir**)
  - `wordbuilder/` — 7 file: `wordbuilder-data.js`, `wordbuilder-core.js`, `wordbuilder-builder.js`, `wordbuilder-quiz.js`, `wordbuilder-spot.js`, `wordbuilder-collection.js`, `wordbuilder-init.js` (**wajib paling akhir**)
  - Kalau menambah modul baru: taruh file di subfolder yang sesuai, tambah `<script src="...">` di HTML induk sebelum tag `-init.js`.

---

## 2. Yang Dikerjakan di Sesi Ini (v16 → v17)

Sesi ini sangat padat, dikerjakan berurutan sesuai kesepakatan di awal sesi (diskusi dulu, baru coding tiap tahap).

### 2.1 Pipeline impor bacaan & percakapan — `complete_reading_json.py` (BARU)
Script baru, pola sama persis dengan `complete_theme_json.py`: terima JSON mentah (1 objek atau array), tokenisasi greedy longest-match terhadap `app_words.json` (prioritas) lalu `cidict_index.json` (fallback), bangun glossary otomatis, kasih ID unik, tulis langsung ke `data/graded_readers.json` (backup otomatis).

Mendukung 2 tipe konten lewat field `"type"`:
- `"bacaan"` — field `text` (paragraf), sama seperti skema lama.
- `"percakapan"` (**BARU**) — field `turns: [{speaker, cn, translation}]`, dialog bergantian.

**Field opsional penting: `"names"`** — `[{hanzi, pinyin, translation}]`. WAJIB dipakai untuk nama tokoh di percakapan (mis. 王明, 林娜) supaya tidak salah kena arti kata kamus lain yang kebetulan sama, atau kepecah jadi karakter lepas. Prioritas PALING TINGGI saat tokenisasi, menang di atas app_words.json maupun cidict.

**Cara pakai:**
```
cd C:\mandarin_app
python complete_reading_json.py percakapan_json\NamaFile.json
```
Skema lengkap + contoh bacaan & percakapan ada di docstring paling atas file — buka & baca langsung kalau lupa formatnya. **Konvensi folder** (disepakati رسلان): eksekutor `.py` selalu di root `C:\mandarin_app\`, bahan mentah JSON di folder terpisah `percakapan_json\` (mirror `tema_json\` yang sudah ada duluan untuk tema kosakata).

### 2.2 `verify_coverage.py` — diupdate
Update kecil, bukan file baru: sekarang bisa cek entri `percakapan` (baca `turns`) selain `bacaan` (baca `text`). Cara pakai tidak berubah: `python verify_coverage.py data\graded_readers.json`.

### 2.3 Bug data ditemukan & DIPERBAIKI langsung di `complete_reading_json.py`: bacaan salah untuk karakter bermakna ganda
**Temuan:** karakter super-umum (都, 要, 得, 更, 和, 着, 数, 还, 只, dll — kata fungsi yang muncul di HAMPIR SEMUA kalimat) kadang kena bacaan/arti SALAH karena `cidict_index.json` punya beberapa entri per karakter (marga/sastra/modern) dan sistem asal ambil yang pertama ketemu. Bahkan **`app_words.json` milik رسلان sendiri** ada yang salah (field `pinyin` kata "都" tersimpan sebagai "Dū"/marga Du, padahal maksudnya hampir selalu "dōu"=semua — ini kata HSK1!).

**Solusi yang sudah diimplementasi:** tabel `COMMON_READING_OVERRIDE` (25 karakter) di `complete_reading_json.py`, menang MUTLAK di atas app_words.json maupun cidict untuk karakter-karakter itu. Kalau nanti ketemu kasus baru serupa (arti aneh/tidak nyambung di laporan hasil run), tinggal tambah entrinya di tabel ini — polanya sudah ada, tinggal isi `{'karakter': 'pinyin_yang_benar'}`.

**Catatan:** ini TIDAK memperbaiki `app_words.json` itu sendiri (yang dipakai Kamus/Flashcard juga) — cuma memperbaiki output `complete_reading_json.py`. Kalau رسلان mau, audit serupa terhadap `app_words.json` bisa jadi kandidat kerja sesi mendatang (lihat §4).

### 2.4 Mode Percakapan (bubble chat) di `graded-reader.html`
Percakapan & bacaan **tercampur dalam satu daftar** per level/tema (tidak pakai tab terpisah, cukup badge 💬 di kartu). Desain final (setelah diskusi, lebih simpel dari rencana awal "index_scenario.json terpisah"):
- Field `tema` di percakapan dipakai persis sama seperti bacaan (bukan sistem baru) — filter chip yang sudah ada otomatis jalan.
- Bubble kiri/kanan otomatis berdasar urutan kemunculan `speaker` pertama kali.
- Klik kata → panel arti (reuse `tokenizePassage` + glossary, sama seperti bacaan).
- Toggle Pinyin & Terjemahan jalan di kedua mode; terjemahan percakapan muncul PER BARIS di bawah tiap bubble (bukan 1 blok besar).
- Tombol 🔊 per-bubble (dengar 1 baris) + tombol besar (dengar semua berurutan).
- Modal upload manual (`➕ Upload Bacaan`) juga sudah update terima format percakapan.
- Fungsi kunci baru: `renderBubbles()`, `renderWordSpan()`, `speakTurn()`. `openPassage()`, `toggleTranslation()`, `speakPassage()`, `validatePassageSchema()` dicabang/diupdate mendukung 2 tipe.

### 2.5 Produksi konten: 18 bacaan+percakapan baru (HSK1-9)
`data/graded_readers.json` sekarang **123 bacaan/percakapan** (104 lama + 1 hasil tes رسلان "Di Bandara" + 18 baru sesi ini). Tema baru, tidak duplikat topik lama: Di Toko Buku, Hari Libur Nasional, Waktu Luang, Menelepon Teman, Gaya Hidup Sehat, Wawancara Kerja, Polusi Perkotaan, Rapat Proyek Kantor, Ekonomi Digital, Pendidikan Daring, AI & Pekerjaan, Wawancara Ekonomi, Filsafat Waktu, Diskusi Akademik Sejarah, Kebijakan Publik, Debat Kebijakan Lingkungan (+ 2 tema HSK1 dari tes awal). Semua sudah lolos `verify_coverage.py` (`SEMUA OK`) dan dites render di `graded-reader.html`.

### 2.6 Deteksi & perbaikan tema tumpang-tindih — `audit_tema_overlap.py` + `merge_tema.py` (BARU)
- **`audit_tema_overlap.py`** — laporan read-only, cari pasangan tema di `index_theme.json` yang mencurigakan (overlap kata tinggi via rasio Jaccard, dan/atau nama label mirip via `difflib`). Tidak mengubah data apa pun.
  ```
  python audit_tema_overlap.py
  ```
- **`merge_tema.py`** — eksekusi gabung 2 tema jadi 1, update **DUA file sekaligus** (`index_theme.json` DAN `app_words.json` — lihat kenapa keduanya wajib disinkron di §2.7). Backup otomatis. Dukung `--dry-run` dan `--keep-source`.
  ```
  python merge_tema.py <key_sumber> <key_tujuan>
  ```
- **Sudah dieksekusi رسلان:** 10 pasangan tema berhasil digabung sesi ini (mis. `ext_numeral`→`angka`, `ext_fruit`→`buah`, `ext_religion`→`agama_kepercayaan`, dll — daftar lengkap ada di riwayat chat kalau perlu dicek lagi).

### 2.7 Bug BESAR ditemukan & diperbaiki: `repair_theme_word_sync.py` (BARU, sudah dieksekusi)
**Temuan:** `index_theme.json` (daftar tema → kata) dan tag `themes` per-kata di `app_words.json` (kata → daftar tema) adalah **DUA sumber data terpisah yang seharusnya selalu sinkron**, tapi ternyata **1.850 pasangan (kata, tema) TIDAK sinkron** — mayoritas tema `ext_*` (102 dari 157 tema kena, beberapa sampai 0% konsisten). Akibat nyata: **deck Flashcard untuk tema `ext_*` kosong** (dikonfirmasi رسلان langsung: "Warna (Ext)" tidak bisa dimainkan walau ada isinya di Kamus) — karena `buildDeckQueue()` di Flashcard baca `w.themes` per kata, BUKAN `index_theme.json`.

**Penyebab:** kemungkinan besar sisa impor tema generasi awal SEBELUM `complete_theme_json.py` dibuat (script itu SENDIRI sudah benar, tidak menghasilkan masalah baru — dicek langsung kodenya).

**Perbaikan:** `repair_theme_word_sync.py` — sekali jalan, searah (cuma menambah tag yang KURANG di `app_words.json`, tidak pernah menghapus), backup otomatis. **Sudah dieksekusi رسلان, 1.850 tag berhasil ditambahkan, dikonfirmasi deck "Warna (Ext)" pulih.** Kalau nanti ada tema `ext_*` baru lain yang kelihatan "isinya ada tapi deck-nya kosong", jalankan lagi:
```
python repair_theme_word_sync.py --dry-run   # lihat dulu
python repair_theme_word_sync.py             # eksekusi
```

### 2.8 Beres-beres dead code `flashcard.html` (item lama dari BLUEPRINT_v16, akhirnya dikerjakan)
Dihapus (murni penghapusan, diverifikasi via diff — 0 baris logika aktif tersentuh):
- `buildDeckQueue()` versi lama (tidak punya parameter `ignoreDue`, sudah lama mati)
- `renderSidebarTema()` + `renderSidebarRadikal()` versi lama
- `RADIKAL_POPULER` (konstanta yatim, cuma dipakai fungsi yang sudah mati di atas)
- **Bonus bug fix:** ditemukan 2 event listener `keydown` yang tumpang tindih (peninggalan PART-file lama) — yang lama bisa memicu `rateCard()` DUA KALI tiap tekan angka 1-4 kalau kartu sedang terbalik (dobel proses SRS). Listener lama (buggy, tanpa guard `FC.isFlipped`) dibuang, yang baru (dengan guard + shortcut 'h' buat hint) dipertahankan.

**Catatan:** fungsi `buildItems` yang tadinya kelihatan "3x duplikat" ternyata BUKAN masalah — 3 fungsi lokal terpisah di scope berbeda (`renderSidebarRadikal`, `renderSidebarGoresan`, `renderSidebarFonetik`), kebetulan nama sama, aman.

### 2.9 Modularisasi `flashcard.html` (3974 → 1467 baris) & `wordbuilder.html` (3818 → 1705 baris)
Mengikuti pola `kamus.html` yang sudah lebih dulu dimodularisasi. Detail pembagian modul di §1 atas. Ditemukan juga: struktur lama `flashcard.html` ternyata 3 blok `<script>` terpisah yang literally warisan PART-file lama ("PART 3/4/5") yang tidak pernah digabung rapi — sekalian dibereskan jadi modul per-fitur yang proper.

**Metodologi verifikasi yang dipakai (penting buat sesi mendatang kalau modularisasi file lain):**
1. Petakan semua fungsi top-level + batas baris pasti (brace-matching), termasuk yang pakai `async function`.
2. Cek scope tiap variabel global (`grep` semua pemakaian) sebelum tentukan taruh di modul mana & urutan load yang aman.
3. Assign fungsi ke modul, JAGA urutan asli dalam tiap file (jangan reorder).
4. **Diff baris-per-baris (setelah buang komentar/whitespace) antara gabungan modul baru vs file asli** — cara paling ampuh mendeteksi ada baris yang salah kepindah/hilang/terduplikat.
5. Tes fungsional via jsdom, TAPI **pakai mekanisme `<script>` tag ASLI** (`document.createElement('script'); el.textContent=code; body.appendChild(el)` dengan `runScripts:'dangerously'`) — BUKAN `window.eval()` manual. `window.eval()` di jsdom TIDAK mempertahankan scope `let`/`const` dgn benar antar panggilan terpisah (beda dari browser asli), bikin banyak false-positive gagal tes yang sebenarnya bukan bug kode.

---

## 3. Konvensi & Struktur Data (referensi cepat)

### 3.1 Skema `graded_readers.json` (per entri)
```
bacaan:     { id, level, type:"bacaan" (opsional/default), title, text, translation, glossary[], tema (opsional) }
percakapan: { id, level, type:"percakapan", title, turns:[{speaker,cn,py,translation}], translation, glossary[], tema (opsional), related_theme (opsional) }
```
`tema` = string bebas (bukan slug), dipakai filter chip di UI, SATU sistem yang sama untuk bacaan maupun percakapan.

### 3.2 Dua sumber data tema HARUS selalu sinkron
- `index_theme.json`: `{tema_key: {label_id, label_zh, words[], count}}`
- `app_words.json`: tiap kata punya field `themes: [tema_key, ...]` sendiri
Kalau nambah/ubah tema **manual** (bukan lewat `complete_theme_json.py` yang sudah otomatis benar), WAJIB update dua-duanya. Kalau ragu/lupa, jalankan `repair_theme_word_sync.py --dry-run` buat cek ada yang kelewat atau tidak.

### 3.3 Kualitas data `cidict_index.json` & `app_words.json`
Ada kata (terutama karakter tunggal frekuensi tinggi) yang punya beberapa entri bacaan, dan urutan/pilihan "default"-nya TIDAK selalu benar (contoh nyata: "都" tersimpan sbg bacaan marga di `app_words.json`). `COMMON_READING_OVERRIDE` di `complete_reading_json.py` (§2.3) menambal ini untuk keperluan generate bacaan/percakapan, tapi TIDAK memperbaiki `app_words.json` itu sendiri. Ini murni caveat kualitas data yang perlu diingat, bukan sesuatu yang "harus" langsung dikerjakan.

### 3.4 Struktur folder modul JS (semua per-halaman, pola sama)
```
C:\mandarin_app\
├── kamus\          (8 file, sudah ada sejak v16)
├── flashcard\      (6 file, BARU v17)
├── wordbuilder\    (7 file, BARU v17)
├── percakapan_json\   (bahan mentah utk complete_reading_json.py, BARU v17)
├── tema_json\      (bahan mentah utk complete_theme_json.py, sudah ada)
└── data\           (semua .json termasuk graded_readers.json, app_words.json, index_theme.json, dst)
```

---

## 4. Prioritas / Ide untuk Sesi Berikutnya (belum dikerjakan)

1. **(Ide bebas, belum ada permintaan resmi)** Audit kualitas bacaan default `app_words.json` untuk karakter bermakna ganda lain di luar 25 yang sudah ada di `COMMON_READING_OVERRIDE` — kalau رسلان mau, bisa dibikin script audit serupa `audit_tema_overlap.py` tapi buat cek "apakah field pinyin utama tiap kata masuk akal dibanding kata sejenis di cidict".
2. **Sisa 529 pasangan tema** dari laporan `audit_tema_overlap.py` yang TIDAK direkomendasikan digabung (overlap kebetulan/rendah) — sudah dianggap aman diabaikan, tapi kalau رسلان mau, laporan lengkapnya bisa dibaca ulang kapan saja (`audit_tema_overlap_report_*.txt` tersimpan di folder tempat script dijalankan).
3. Tidak ada item mendesak lain yang tertunda — semua rencana awal sesi (nomor 1-4: pipeline impor, mode percakapan, audit tema, merge tema) plus 2 permintaan tambahan (produksi 18 konten, modularisasi flashcard+wordbuilder) sudah selesai & dikonfirmasi رسلان jalan lancar, konsol bersih tanpa error.

---

## 5. Cara Pakai File Ini

Di percakapan Claude yang baru, رسلان cukup upload/tempel file ini di awal, lalu langsung lanjut minta apa pun yang diinginkan — Claude akan punya konteks penuh soal arsitektur, konvensi, dan riwayat pekerjaan tanpa perlu dijelaskan ulang.

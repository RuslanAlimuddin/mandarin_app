# Mandarin Interaktif — BLUEPRINT v7

> Dokumen ini melanjutkan BLUEPRINT_v6.md. Isinya rekap SATU SESI PANJANG
> yang menindaklanjuti hasil tes menyeluruh رسلان terhadap seluruh
> pekerjaan v6 (`checklist_tes_menyeluruh.md`) — sebagian besar berupa
> catatan "tambahan" per halaman, plus beberapa fitur baru yang lahir dari
> diskusi di tengah sesi. Kalau dokumen ini di-paste di awal percakapan
> baru, cukup baca ini untuk tahu persis di titik mana pekerjaan berhenti.

---

## 0. Status ringkas

**Semua item checklist v6 lolos tes** (رسلان konfirmasi "sudah di tes
semuanya, lancar"), tapi checklist itu berisi banyak catatan "tambahan"
per halaman + beberapa pertanyaan terbuka. Sesi ini menuntaskan HAMPIR
SEMUA tambahan itu, ditambah 2 fitur besar baru yang muncul dari diskusi
(game audio Flashcard, animasi goresan kuas asli).

**Yang masih terbuka / belum dikerjakan** (lihat §7 Wishlist): bacaan per
tema di Bacaan Berjenjang, dan ide besar OCR kamera / kaca pembesar
hover-translate. رسلان belum sempat pilih mana duluan sebelum sesi
ditutup — tawarkan lagi di awal sesi baru.

---

## 1. Prinsip kerja & preferensi رسلان (tetap berlaku, ditegaskan ulang)

Sama seperti v6 §1 (diskusi dulu sebelum coding lewat `ask_user_input_v0`
untuk keputusan desain, edit PART file bukan file gabungan untuk
kamus/flashcard, verifikasi lewat kode bukan tebak-tebakan, uji sintaks
sebelum kirim). Tambahan dari sesi ini:

- **رسلان sangat detail & korektif** — kalau ada asumsi desain yang salah
  (mis. makna "Filter Game", posisi tombol), رسلان akan menjelaskan ulang
  sampai jelas. Jangan buru-buru coding kalau spesifikasi masih ambigu.
- **Untuk fitur yang butuh aset eksternal** (mis. data goresan kuas),
  alur kerjanya: Claude kasih instruksi + script Python → رسلان jalankan
  lokal & download manual → رسلان laporkan hasil (jumlah ketemu/tidak) →
  Claude lanjut integrasi. Claude TIDAK bisa akses filesystem رسلان
  (`C:\mandarin_app`) sama sekali — semua kerja lokal itu murni رسلان.
- **`wordbuilder.html` SEMPAT disangka sudah di-PART-kan** oleh رسلان di
  awal sesi (upload `wordbuilder_PART_1-4.txt`) — ternyata itu snapshot
  LAMA dari sebelum fitur Tier 2/3 ada. **`wordbuilder.html` TETAP file
  tunggal**, jangan pernah asumsikan ada PART barunya kecuali رسلان
  konfirmasi eksplisit dan Claude verifikasi isinya dulu (cek ada/tidaknya
  fungsi-fungsi kunci seperti `toggleExplainPanel`, `consumeRefWord`,
  dll — lihat insiden ini kalau mau tahu detail cara ceknya).
- **Ketika Claude menutup satu batch kerja**, hasilnya SELALU dikirim
  lewat `present_files` di respons yang sama — kalau lupa (pernah terjadi
  sekali sesi ini), رسلان akan bilang "anda belum memberikan filenya" dan
  Claude harus kirim ulang tanpa membuat file baru (file lama di
  `/mnt/user-data/outputs/` masih valid, tinggal `present_files` lagi).

---

## 2. File baru yang lahir sesi ini

| File | Isi |
|---|---|
| `build_hanzi_writer_data.py` | Script lokal (رسلان jalankan sekali, atau ulang kalau cakupan karakter berubah). Baca `data/app_words.json`, ambil SEMUA karakter individu dari SEMUA kata (bukan cuma kata 1-huruf), cari file `<karakter>.json` di dalam hasil ekstrak ZIP `hanzi-writer-data` (dicari rekursif), gabung jadi satu `data/hanzi_writer_data.json`. Cakupan final: **3.034/3.034 karakter (100%)**. |
| `data/hanzi_writer_data.json` | **Dihasilkan رسلان lokal** lewat script di atas (bukan Claude yang generate) — data jalur vektor goresan asli per karakter, sumber: proyek *Make Me a Hanzi* via library **Hanzi Writer** (`shared/hanzi-writer.min.js`, رسلان download manual dari `cdn.jsdelivr.net/npm/hanzi-writer@3/dist/hanzi-writer.min.js`). |

---

## 3. File yang diedit sesi ini (dan bagian mana yang berubah)

### `index.html` (file tunggal)
- Navbar & footer tadinya cuma 3 link (Kamus/Flashcard/Word Builder) — ditambah Tone/Bacaan/Ujian HSK. Grid fitur ditambah 3 card baru (Tone, Bacaan, Ujian HSK).

### `wordbuilder.html` (file tunggal, banyak perubahan)
- Spot-the-Error scope "Pola Ini": dulu semua item `kesalahan_umum` ditumpuk jadi beberapa kontainer sekaligus → sekarang 1 kontainer, tombol "↺ Ulangi" pindah ke soal acak lain dari stok (`renderActiveModeQuestion`).
- Contoh Tambahan (dalam panel Penjelasan Lengkap) + Contoh Kalimat (section terpisah) — dulu 2 kontainer terpisah isinya sama-sama contoh benar → digabung jadi 1 stok, tampil 1 per waktu + tombol "Contoh Lain ▶" acak (`renderExamples`/`renderCurrentExample`/`nextExample`).
- Speaker 🔊 & tombol kecepatan 🐢 dipindah dari menumpuk di dalam kontainer output jadi kolom `.wb-output-tools` di SAMPING kontainer (`.wb-output-row`).
- Tip sintaksis singkat (dulu section tersendiri di tengah) digabung ke header/topbar, satu tempat dengan judul pola (`.wb-topbar-titlerow` + `.wb-tip` di dalam `.wb-topbar`).
- Tombol tab "🧩 Kuis Pola" dipindah dari 1 baris dengan Tunggal/Majemuk/Fungsi (ketutupan/rebutan ruang) ke baris terpisah di bawahnya (`.wb-tabs-secondary`).
- Klik kartu Koleksi Tersimpan: dulu cuma tempel teks output → sekarang buka pola yang tepat DAN isi ulang tiap slot (subjek/objek/tempat/dst) dari snapshot `entry.slotValues` yang disimpan saat `addToFlashcardWB()` (mekanisme `WB.pendingSlotValues`, generalisasi dari `WB.pendingPrefill` yang tadinya cuma 1 slot).
- **Tier 1 (ingat state terakhir lintas-halaman)**: pola & tab aktif tersimpan ke `localStorage` (`mandarin_wb_last_state_v1`), dipulihkan otomatis saat buka halaman lagi (kecuali kalah prioritas sama handoff `wb_ref_word` dari Flashcard).

### `shared/hanzi-writer.min.js` — **BARU, رسلان download manual**, tidak disentuh Claude.

### `kamus_PART_1.txt`
- CSS: fix bug `.group-panel` (Per Radikal/Goresan/dll) meluber keluar box karena tidak ada `overflow:hidden` — sekarang `max-height:min(60vh,420px)` + `overflow:hidden`, plus `.group-panel-grid` dikasih `flex:1;min-height:0` supaya scroll internal beneran jalan.
- Tambah `<script src="shared/hanzi-writer.min.js">`.
- CSS baru: `.hanzi-writer-multi` (kontainer flex multi-slot), `.hanzi-writer-slot`, `.hanzi-writer-nodata`.

### `kamus_PART_5.txt`, `kamus_PART_6.txt`
- **Tier 1 (ingat state terakhir)**: pencarian/mode/filter/sumber-data/kata-terpilih tersimpan ke `mandarin_kamus_last_state_v1`, dipulihkan otomatis (`saveKamusLastState`/`restoreKamusLastState`, dipanggil dari `doSearch`, `selectWord`, `setSidebarFilter`, `setSource`, `setSearchMode`, dan init).
- **Modul Stroke Order dirombak total** (`playStrokeOrder`, ganti nama dari `playComponentOrder` sbg fungsi utama): dulu cuma highlight urutan komponen (fallback), sekarang **animasi goresan kuas ASLI** via Hanzi Writer + `data/hanzi_writer_data.json`. Berlaku untuk **kata apapun** (1 atau banyak karakter, dulu cuma 1-karakter dgn ≥2 komponen tercatat) — kata multi-karakter dianimasikan **berurutan satu-satu** (`chars.forEach` + `onComplete` callback berantai). Kalau ada karakter yang datanya tidak ketemu, karakter itu di-skip (tampil hanzi biasa), sisanya tetap dianimasikan. Fallback ke highlight-komponen lama HANYA kalau kata 1-karakter dan datanya tidak ada sama sekali. Catatan status cakupan otomatis muncul kecil di bawah tombol (`stroke-order-note`).

### `flashcard_PART_1.txt`, `flashcard_PART_2.txt`, `flashcard_PART_4.txt`, `flashcard_PART_5.txt`
- Bug fix: `toggleAccordion()` dulu terkunci-terbuka-selamanya kalau section punya item aktif (khususnya kerasa di RADIKAL) — sekarang klik header SELALU toggle apapun status aktifnya.
- Bug fix nyata (ditemukan sendiri, bukan dilaporkan): `sendToWordBuilder()` cuma simpan `localStorage` + toast, TIDAK PERNAH pindah halaman — sekarang `window.location.href='wordbuilder.html'`.
- Kartu jawaban (belakang) sekarang tampil: **Lawan kata** (`word.antonyms`), **Fonetik** (reverse-lookup dari `index_phonetic.json` → `FC.phoneticReverse`, dibangun sekali saat load).
- **Mode Game Audio** (fitur besar baru, Tier 3):
  - "🎵 Jebakan Nada" berubah dari deck flip-card biasa jadi **game audio sungguhan** (dengar → pilih hanzi dari minimal-pair nada). State `FC.toneGame`.
  - **Toggle global "🎮 Mode Game"** (checkbox di Pengaturan Sesi, `FC.gameModeOn`): kalau aktif, deck APAPUN (selain Jebakan Nada yg selalu game) dimainkan sbg game dengar-pilih generic (distraktor acak dari pool deck yang sama), bukan flip-card.
  - **Deck "↔ Lawan Kata" dapat mesin soal KHUSUS** (mode `'antonym'`, bukan generic) saat toggle aktif: soal & jawaban bisa diformat independen — Hanzi/Pinyin/**Suara**/Terjemahan/**Acak** (2 dropdown baru: `ctrl-antonym-qfmt`, `ctrl-antonym-afmt`, cuma muncul kalau deck aktifnya `antonyms`). Pasangan lawan-kata di-resolve jadi objek kata utuh lewat `buildAntonymPairs()` (butuh `FC.wordBySimplified`, reverse lookup hanzi→kata).
  - **Opsi jawaban format Suara dibuat 2 TAHAP** (bukan sekali-klik-langsung-jawab): tombol "🔊 Dengar" (preview, boleh berkali-kali, urutan bebas) terpisah dari tombol pilih (radio-style, highlight "●"), baru tombol **"✓ Ini Jawaban Saya"** yang commit — supaya tidak "beli kucing dalam karung" (keluhan رسلان soal versi awal yg sekali-klik-langsung-jawab).
  - Semua mode game (tonepairs/generic/antonym) **memengaruhi SRS** sungguhan: benar → rating "Baik" (2), salah → rating "Lagi" (0) + masuk `mandarin_wrong_v1` — persis seperti flip-card biasa.
  - **Tier 1 (ingat state terakhir)**: deck terakhir + toggle gameModeOn tersimpan ke `mandarin_fc_last_state_v1`. Sengaja **TIDAK auto-mulai sesi** saat restore (cuma highlight deck + tombol siap) — supaya tidak mengejutkan رسلان dengan sesi yang tiba-tiba jalan.
  - Tombol "▶ Animasikan Goresan" (dulu "Tunjukkan Urutan Penulisan") di kartu belakang: sama seperti Kamus, sekarang animasi kuas asli via Hanzi Writer, berlaku kata apapun (bukan cuma 1-karakter ≥2 komponen), multi-karakter berurutan, fallback ke highlight-komponen kalau 1-karakter & data tidak ada.

### `tone.html` (file tunggal)
- **Tier 1**: mode terakhir (Pilih Nada/Pilih Hanzi) tersimpan `mandarin_tone_last_state_v1`, dipulihkan sebelum soal pertama dibuat (bukan lewat `setToneMode()` penuh, supaya tidak reset skor 2x).

### `graded-reader.html` (file tunggal)
- **Tier 1**: posisi baca terakhir (level saja / level+daftar bacaan / lagi baca bacaan tertentu) tersimpan `mandarin_gr_last_state_v1`, dipulihkan sampai ke level detailnya (`restoreGrLastState`, dipanggil dari `renderLevelSelector`/`openLevel`/`openPassage`).

### `hsk-exam.html` (file tunggal)
- **Tier 1**: SENGAJA CUMA konfigurasi setup (level + jenis soal dicentang) yang diingat via `mandarin_ex_last_state_v1` — BUKAN sesi ujian yang sedang berjalan (alasan: timer countdown, "lanjutkan" ujian yang ditinggal bisa aneh).
- **Riwayat Ujian (fitur baru, Tier 3)**: tiap hasil ujian selesai otomatis tersimpan ke `mandarin_hsk_history_v1` (maks 100 entri terbaru). Tombol "📊 Riwayat Ujian" di layar setup & layar hasil → tampilkan ringkasan rata-rata skor per level + daftar tiap ujian (skor berwarna hijau/emas/merah, breakdown per jenis soal, tanggal). Tombol hapus riwayat (minta konfirmasi).

---

## 4. Temuan & keputusan penting sepanjang sesi (supaya tidak diulang investigasi-nya)

1. **`wordbuilder_PART_1-4.txt` yang رسلان upload di awal sesi adalah snapshot LAMA** (pra Tier 2/3) — sempat mau dikerjakan di atas file yang salah, ketahuan sebelum sempat edit karena Claude cek isi dulu (tidak ada `toggleExplainPanel`, `consumeRefWord`, dll). رسلان lalu upload `wordbuilder.html` (file tunggal) yang benar.
2. **"Filter Game" di Flashcard (Jebakan Nada dkk) awalnya BUKAN game** — cuma deck flip-card biasa yang difilter kriteria tertentu (mis. kata rawan-tertukar-nada). رسلان kira dari namanya itu game audio sungguhan (mirip tone.html) — ini yang jadi pemicu fitur Mode Game Audio di §3.
3. **`data/app_words.json` TIDAK punya field jalur vektor goresan** (`stroke` cuma jumlah, bukan path) — makanya Modul Stroke Order versi awal (v6) cuma highlight urutan komponen. Ini **BUKAN jalan buntu permanen** seperti sempat disampaikan Claude di awal — ternyata bisa diatasi total pakai library eksternal **Hanzi Writer** (data terbuka, gratis, lisensi permisif). Alur: Claude kasih link + script → رسلان download & jalankan lokal → 100% cakupan (3.034/3.034 karakter).
4. **Audio TTS browser untuk latihan nada memang bisa terasa tidak konsisten** — dijelaskan ke رسلان: (a) mesin TTS sintetis meratakan kontur Nada 3 dibanding penutur asli, (b) **tone sandhi** (nada berubah otomatis tergantung konteks, tulisan pinyin tetap nada dasar) bikin kedengarannya "tidak cocok sama tulisan". Bukan soal pendengaran رسلان.
5. **Pola desain "2 tahap" untuk opsi jawaban berbentuk audio** (preview dulu via tombol dengar terpisah, baru commit via tombol konfirmasi) lahir dari feedback رسلان langsung ("beli kucing dalam karung") setelah versi awal (sekali-klik-langsung-jawab) dicoba. Kalau bikin game audio baru lagi ke depannya, pertimbangkan pola 2-tahap ini dari awal untuk opsi berbentuk suara.
6. **Claude sempat lupa memanggil `present_files` di satu respons** (setelah kirim fix Flashcard) — رسلان menegur "anda belum memberikan filenya". Fixnya cukup panggil `present_files` lagi ke path yang sama di `/mnt/user-data/outputs/`, tidak perlu re-generate file.

---

## 5. Keterbatasan yang disengaja (bukan bug — sudah dikomunikasikan ke رسلان)

- **Cakupan Hanzi Writer**: 100% untuk 3.034 karakter yang muncul di `app_words.json` (HSK). Kata dari **Cidict** (121K, Kamus saja) yang karakternya di luar cakupan itu akan fallback ke highlight-komponen lama (kalau 1-karakter) atau skip-tampil-hanzi-biasa (kalau multi-karakter) — bukan error, cuma kurang presisi.
- **Mode Game "generic"** (deck selain Jebakan Nada & Lawan Kata saat toggle aktif): distraktor jawaban acak dari pool deck yang sama, format SELALU audio→hanzi (belum ada pilihan format kayak Lawan Kata). Kalau رسلان mau deck lain juga dapat kontrol format serupa, itu perluasan lanjutan.
- **Opsi jawaban audio "2 tahap"**: baru diterapkan di game Lawan Kata (satu-satunya yang punya format Suara sejauh ini). Kalau format Suara dipakai deck lain nanti, pola yang sama perlu direplikasi.
- **Riwayat Ujian HSK**: cuma simpan ringkasan (skor, breakdown per jenis, tanggal) — TIDAK simpan detail soal per-butir yang dulu dijawab (beda dari review-jawaban-salah yang cuma ada di sesi saat itu juga, hilang begitu ganti ujian baru).
- Keterbatasan v6 yang masih berlaku (Diff Spot-the-Error, Tata Bahasa HSK Exam tidak leveled, SRS Pīn/ID mode) — lihat BLUEPRINT_v6 §6, tidak berubah sesi ini.

---

## 6. Bug yang ditemukan & diperbaiki SENDIRI oleh Claude saat proses (bukan dilaporkan رسلان)

- `sendToWordBuilder()` di Flashcard tidak pernah pindah halaman (lihat §4.6 / §3).
- `toggleAccordion()` di Flashcard terkunci-terbuka-selamanya kalau ada item aktif di section itu.
- `.group-panel` di Kamus meluber keluar box (butuh scroll halaman) karena `overflow:hidden` tidak diset — dilaporkan رسلان sebagai bug UI, root cause CSS ditemukan Claude.

---

## 7. Wishlist — belum dikomit, tawarkan di awal sesi baru

**Dari sesi ini (baru, belum sempat dipilih رسلان sebelum sesi ditutup):**
- **Bacaan per tema** di Bacaan Berjenjang (di pasar, di kelas, dll) — Claude sudah usul generate sendiri (pola sama seperti 14 bacaan awal, tervalidasi 100% bersih), رسلان setuju caranya tapi belum sempat mulai.
- **Ide besar: OCR kamera / kaca pembesar hover-translate** — دari pertanyaan رسلان di `index.html` section: terjemahan Kamus via foto/kamera, atau overlay "loop" yang menerjemahkan teks Mandarin di halaman web manapun saat di-hover, semua offline. Ini fitur besar, belum didiskusikan detail teknis/kelayakannya sama sekali — mulai dari diskusi dulu, bukan langsung coding.

**Dari v5/v6 yang masih belum dikomit:**
- Dashboard progres gabungan (lintas SRS + koleksi tersimpan + riwayat kamus)
- Placement test / tes penempatan HSK di awal pemakaian
- Dictation (dengar kalimat → ketik hanzi/pinyin)
- Sentence mining pribadi (jurnal kalimat favorit dari Word Builder)
- Streak harian & ringkasan mingguan

Ditolak secara eksplisit (tetap, dari v3/v4/v5): mode gelap/terang, cetak/export PDF.

---

## 8. Kalau memulai sesi baru dari dokumen ini

1. Tanya رسلان dulu: masih ada yang perlu diperbaiki dari sesi v7 ini (kalau ada laporan bug baru), atau langsung lanjut ke salah satu Wishlist §7?
2. Kalau lanjut ke **Bacaan per tema**: konfirmasi dulu berapa tema & berapa bacaan per tema yang رسلان mau, sebelum mulai menulis konten (diskusi dulu sebelum coding).
3. Kalau lanjut ke **OCR/hover-translate**: ini FITUR BESAR & TEKNIS BERAT (kemungkinan butuh library OCR client-side seperti Tesseract.js untuk tetap offline) — mulai dengan diskusi kelayakan teknis & desain interaksi dulu, jangan langsung asumsikan bisa 100% offline tanpa verifikasi library yang dipakai.
4. Ingat: `kamus.html`/`flashcard.html` = edit PART saja; `wordbuilder.html`/`tone.html`/`graded-reader.html`/`hsk-exam.html`/`index.html` = tetap file tunggal utuh.
5. `data/hanzi_writer_data.json` sekarang ada & 100% cakupan (3.034 karakter) — kalau nanti `app_words.json` bertambah kata baru dengan karakter yang belum pernah muncul, رسلان perlu jalankan ulang `build_hanzi_writer_data.py` (masih ada di project, atau minta Claude kirim ulang).

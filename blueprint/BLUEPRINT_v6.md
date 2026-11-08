# Mandarin Interaktif — BLUEPRINT v6

> Dokumen ini melanjutkan BLUEPRINT_v5.md. Isinya rekap SATU SESI PANJANG yang
> menuntaskan **seluruh roadmap Tier 0–3** dari v5. Kalau dokumen ini di-paste
> di awal percakapan baru, cukup baca ini + (kalau ada) `checklist_tes_menyeluruh.md`
> yang sudah diisi hasil tes untuk tahu persis di titik mana pekerjaan berhenti.

---

## 0. Status ringkas

**Seluruh roadmap BLUEPRINT_v5 (Tier 0, 1, 2, 3) sudah dikerjakan dan sudah
ditest oleh رسلان — hasilnya baik di semua bagian**, kecuali kalau
`checklist_tes_menyeluruh.md` yang diupload di percakapan berikutnya
menunjukkan ada baris yang gagal (kalau ada, itu prioritas nomor satu untuk
diperbaiki sebelum lanjut ke pekerjaan baru apapun).

Tidak ada item wajib yang tersisa dari roadmap v5. Yang tersisa cuma
**Wishlist** (§7 di bawah) — ide masa depan, belum disepakati, silakan
tawarkan ke رسلان kalau sesi baru dimulai tanpa arahan spesifik.

---

## 1. Prinsip kerja & preferensi رسلان (tetap berlaku, ditegaskan ulang)

- **Diskusi dulu sebelum coding.** Untuk keputusan desain yang punya beberapa
  opsi valid (bentuk UI, penempatan fitur, format data), presentasikan opsi
  lewat `ask_user_input_v0` sebelum menulis kode.
- **Edit PART file, bukan file gabungan**, untuk `kamus.html` dan
  `flashcard.html` — رسلان punya `gabung_kamus.py` dan `gabung_flashcard.py`
  lokal. **Selalu cari tahu PART mana yang relevan** (grep function name yang
  mau diubah), lalu **hanya kirim PART yang diedit**, jangan pernah kirim
  ulang file HTML gabungan untuk dua halaman ini.
- **`wordbuilder.html`, `tone.html`, `graded-reader.html`, `hsk-exam.html`
  BELUM di-PART-kan** — masih file tunggal utuh. Kalau رسلان mulai memecahnya
  jadi PART juga, ikuti pola yang sama seperti kamus/flashcard.
- **Verifikasi lewat kode container, bukan tebak-tebakan.** Kalau ragu soal
  skema data (field name, tipe, urutan), tulis script Python kecil yang
  رسلان jalankan lokal dan tempel hasilnya balik (pola `eksplorer.py`,
  `inspect_stroke_data.py`) — JANGAN asumsikan skema.
- **Uji sebelum kirim.** Untuk logika non-trivial (algoritma, transformasi
  data, animasi timing), tulis test Node.js/jsdom kecil dan jalankan sebelum
  menyerahkan file ke رسلان. Ini sudah jadi standar sepanjang sesi ini dan
  terbukti menangkap beberapa bug nyata sebelum sempat dikirim (lihat §5).
- **Cek dulu, jangan asumsikan sesuatu belum ada.** Beberapa item roadmap
  ternyata SUDAH selesai dari sesi-sesi sebelumnya (`wb_ref_word`,
  "produksi aktif" via question mode, sinonim/antonim kamus) — selalu grep
  kode yang ada dulu sebelum mulai membangun dari nol.
- **Di akhir sesi kerja panjang, susun checklist tes per-halaman** (format
  "harus ada / harus bisa"), bukan cuma daftar fitur naratif.

---

## 2. File baru yang lahir sesi ini

| File | Isi |
|---|---|
| `shared/srs.js` | Tier 2. Read-only reader `mandarin_srs_v1`/`mandarin_wrong_v1`. `isMastered(hanzi)`, `isWeak(hanzi)`. Cocok berdasar **hanzi**, bukan field `id` asli `app_words.json` (lihat keterbatasan §6). |
| `tone.html` | Halaman baru. Mode "Pilih Nada" (suku kata 1-karakter, tombol nada 1-4) & "Pilih Hanzi" (minimal-pair dari pinyin-tanpa-nada). |
| `generate_tone_drills.py` | Script lokal (رسلان jalankan) → `data/tone_drills.json` dari `data/app_words.json`. |
| `graded-reader.html` | Halaman baru. 7 level HSK, klik-kata untuk arti, upload bacaan tambahan (localStorage `mandarin_custom_readers`). |
| `data/graded_readers.json` | 14 bacaan (2×HSK1-7) ditulis langsung oleh Claude (bukan digenerate), tiap bacaan: `text` + `translation` + `glossary` (dipakai tokenizer greedy longest-match). **Sudah divalidasi 100% bersih** — semua karakter di tiap `text` berhasil dipetakan ke `glossary` atau dikenali tanda baca. |
| `hsk-exam.html` | Halaman baru. Simulasi ujian bertimer, 4 jenis soal (Kosakata/Mendengar/Bacaan/Tata Bahasa), reuse penuh dari `graded_readers.json` + `pattern_explanations.json` — **tidak ada data baru**. |
| `inspect_stroke_data.py` | Script lokal sekali-pakai untuk audit data `components`/`radical`/`structure`/`stroke` sebelum membangun Modul Stroke Order. Hasil auditnya sudah terpakai (lihat §4), boleh diabaikan/dihapus رسلان kalau mau beres-beres. |
| `checklist_tes_menyeluruh.md` | Daftar cek tes untuk seluruh pekerjaan sesi ini. **رسلان akan upload versi terisi di percakapan berikutnya** — baca itu dulu untuk tahu status pasti. |

---

## 3. File yang diedit sesi ini (dan bagian mana yang berubah)

### `wordbuilder.html` (file tunggal, banyak penambahan bertahap)
- Panel "Penjelasan Lengkap" per-pola (6 field dari `pattern_explanations.json`) — **memperbaiki regresi**: fitur ini sempat ada lalu hilang karena PART lama ketimpa; sekarang sudah permanen di file ini.
- Section "Kesalahan Umum" diubah dari kartu statis jadi **Spot-the-Error interaktif** (diff karakter berbasis LCS), dengan toggle scope Pola Ini/Semua Pola.
- UI koleksi tersimpan (`mandarin_wb_saved`): modal lihat/hapus, badge counter navbar.
- `wb_ref_word`: baca & konsumsi sekali-pakai dari localStorage, replikasi logika klasifikasi pool dari `generate_wordbuilder_pools.py` (JS: `pickPoolForRefWord`, `convertRefWordToEntry`).
- Tombol Export/Import backup di navbar (panggil fungsi dari `shared/core.js`).
- `shared/srs.js` di-load, filter radio Mastered/Weak di sidebar, terapan ke `getFilteredPool()`.
- Tab baru "🧩 Kuis Pola" (kebalikan builder: tebak pola dari kalimat, distraktor dari `pola_terkait`).
- Navbar: link Tone, Bacaan, Ujian HSK ditambahkan.

### `shared/core.js`
- Ditambah `exportBackup()`, `importBackupFromFile()`, `handleBackupFileInput()`. Enumerasi SEMUA key localStorage saat export (bukan daftar manual), kecuali `wb_ref_word` (transient).

### `flashcard_PART_2.txt`
- Tombol "📝 Kirim ke Word Builder" default `hidden`, cuma muncul bareng tombol SRS setelah jawaban dibuka (dulu selalu ada, ketutupan visual oleh wajah belakang kartu yang panjang).
- Tombol Export/Import backup + navbar link Tone/Bacaan/Ujian HSK.

### `flashcard_PART_4.txt`
- `showAnswer()`/`renderCurrentCard()`: toggle hidden `btn-send-wb` sinkron dengan `fc-srs-wrap`.
- **Perbaikan akar masalah**: `.fc-card-inner` sekarang menyesuaikan tinggi otomatis (`scrollHeight` via `requestAnimationFrame`) supaya wajah belakang kartu panjang tidak menutupi tombol di bawahnya.

### `kamus_PART_1.txt`
- CSS: tombol Export/Import backup, `.tag-theme` (cursor pointer + hover), CSS Modul Stroke Order (`.structure-order-text`, `.btn-stroke-order`, `.stroke-order-wrap`, animasi highlight komponen).

### `kamus_PART_2.txt`
- Navbar: tombol Export/Import backup, link Tone/Bacaan/Ujian HSK.

### `kamus_PART_5.txt`
- `structureLabel()` diganti total: dari 9 kode yang **ternyata salah/tidak dipakai data riil**, jadi **13 kode asli** (diverifikasi via `inspect_stroke_data.py`). Ditambah `structureOrderText()` (prinsip urutan penulisan per tipe struktur) dan `STRUCTURE_INFO` map.

### `kamus_PART_6.txt`
- Tag tema di panel detail sekarang bisa diklik → `selectGroupItem('theme', key)` (reuse mekanisme "Per Tema" yang sudah ada).
- Struktur: ikon dinamis sesuai tipe (dulu selalu ⿰ walau strukturnya beda), tambah teks prinsip urutan penulisan.
- Komponen karakter: tombol "▶ Tunjukkan Urutan Penulisan" + fungsi `playComponentOrder()` (highlight komponen berurutan, BUKAN animasi goresan kuas — datanya tidak tersedia, lihat §6).

---

## 4. Temuan penting sepanjang sesi (supaya tidak diulang investigasi-nya)

1. **`inspect_stroke_data.py` hasil audit**: `components`/`radical`/`structure` terisi 100% di `app_words.json` (11.470 kata), tapi `stroke` (jumlah goresan) **0% terisi** — field itu memang kosong di sumber data, bukan bug baca. Tidak ada file stroke-order asli (jalur vektor per-goresan) di proyek `C:\mandarin_app` sejauh yang di-scan.
2. **13 tipe struktur riil** (bukan 9): `left-right`(5271), `top-bottom`(3350), `single`(1003), `enclosed-topleft`(468), `enclosed-botleft`(434), `overlapping`(271), `top-mid-bottom`(193), `enclosed-top`(180), `enclosed-topright`(111), `enclosed-full`(108), `left-mid-right`(52), `enclosed-left`(18), `enclosed-bottom`(11).
3. `wb_ref_word` (prefill Flashcard→Word Builder) dan "produksi aktif" (recall hanzi dari pinyin/arti, via mode pertanyaan Pīn/ID di Flashcard) **sudah selesai dari sesi-sesi sebelum ini** — sempat mau dikerjakan ulang, ternyata cuma perlu verifikasi.
4. Sinonim/antonim di Kamus **sudah clickable sejak awal**; yang belum cuma tag Tema.
5. PART file رسلان selalu diverifikasi sinkron dengan hasil gabungan sebelum diedit (`diff` merge asli vs upload) — belum pernah ketemu drift.

---

## 5. Bug yang ditemukan & diperbaiki SENDIRI oleh Claude saat proses (bukan dilaporkan رسلان)

- Fungsi `toggleExplainPanel()` sempat kehapus tidak sengaja saat `str_replace` — ketahuan lewat `node --check`, langsung diperbaiki di giliran yang sama.
- Cabang `identitas` di `pickPoolForRefWord()` awalnya jadi kode mati (ketimpa kondisi `subyek` yang lebih luas) — diperbaiki urutan prioritasnya.
- Soal "Bacaan" di `hsk-exam.html` awalnya menyorot **SEMUA** kemunculan kata target di paragraf (membingungkan untuk partikel umum) — diperbaiki jadi cuma kemunculan pertama.
- 2 konstanta global di `tone.html` (`TONE_MARKS`, `TONE`) bentrok nama dengan kemungkinan isi `shared/pinyin.js` → SyntaxError di production. Diganti nama (`TONE_DISPLAY_MARKS`, `TONE_STATE`) setelah رسلان lapor screenshot console error.
- Glosarium `graded_readers.json` draft awal: 129 karakter partikel umum (的/是/了/在/dst) di berbagai bacaan tidak lengkap ter-cover (cuma ada dalam kombinasi tertentu, tidak berdiri sendiri) — ketahuan lewat test tokenizer otomatis, ditambal terprogram, diverifikasi ulang sampai 0 karakter tak dikenal di 14 bacaan.

---

## 6. Keterbatasan yang disengaja (bukan bug — sudah dikomunikasikan ke رسلان)

- **Stroke Order**: urutan komponen (dari array `components` apa adanya), bukan animasi goresan kuas presisi — data jalur vektor tidak ada.
- **Filter Mastered/Weak**: cocok berdasarkan **hanzi** (`cn`), bukan field `id` asli `app_words.json` (yang dipakai flashcard untuk key SRS) — karena `wb_pools.json` tidak membawa field `id` asli itu. Meleset untuk kata langka yang `id`-nya beda dari hanzinya.
- **Diff Spot-the-Error** (LCS char-level): akurat untuk substitusi partikel tunggal, ambigu untuk kesalahan urutan kata multi-karakter.
- **Tata Bahasa di Ujian HSK**: pool soal dari `pattern_explanations.json` tidak leveled per-HSK, jadi kesulitannya tidak otomatis naik mengikuti level ujian yang dipilih.
- **Mode Pīn/ID Flashcard**: berbagi data SRS yang sama dengan mode Hanzi biasa (bukan tracking terpisah per-mode).

---

## 7. Wishlist — masih sama seperti v5, belum dikomit

- Dashboard progres gabungan (lintas SRS + koleksi tersimpan + riwayat kamus)
- Placement test / tes penempatan HSK di awal pemakaian
- Dictation (dengar kalimat → ketik hanzi/pinyin)
- Sentence mining pribadi (jurnal kalimat favorit dari Word Builder)
- Streak harian & ringkasan mingguan

Ditolak secara eksplisit (tetap, dari v3/v4/v5): mode gelap/terang, cetak/export PDF.

---

## 8. Kalau memulai sesi baru dari dokumen ini

1. Baca `checklist_tes_menyeluruh.md` versi terisi رسلان kalau sudah diupload — itu sumber kebenaran soal apa yang benar-benar jalan.
2. Kalau ada baris checklist yang gagal → itu prioritas pertama, perbaiki sebelum kerja apapun yang lain.
3. Kalau semua checklist lolos dan رسلان belum kasih arahan baru → tawarkan item Wishlist (§7) sebagai langkah berikutnya, jangan langsung mulai coding tanpa diskusi/persetujuan bentuk fitur (lihat prinsip di §1).
4. Ingat: `kamus.html`/`flashcard.html` = edit PART saja; `wordbuilder.html`/`tone.html`/`graded-reader.html`/`hsk-exam.html` = masih file tunggal.

# BLUEPRINT — Mandarin Interaktif — v25
_(Handoff document. Baca Bagian A–B dulu untuk onboarding cepat. Bagian C–E untuk detail teknis. Bagian F untuk riwayat sesi.)_

---

## A. Arsitektur Saat Ini (Living Doc)

**Aplikasi:** "Mandarin Interaktif" — aplikasi belajar Mandarin offline, vanilla HTML/CSS/JS, single-user (رسلان), berjalan lokal di `C:\mandarin_app\` (biasanya via `python -m http.server` / `localhost:8000`).

**Sumber data utama** (folder `data/`): `app_words.json` (~11.726 entri), `cidict_index.json` (~125.000 entri, fallback CC-CEDICT), `graded_readers.json` (123 entri), `char_etymology_id.json` (2.840 karakter), `confusion_groups.json` (53 grup), `nuance_pairs.json` (1.291 pasangan), `produktif_karakter.json` (1.389 akar karakter, 16.179 kata turunan), `kata_majemuk_pola.json` (8.867 kata 2-karakter, 6 pola pembentukan kata majemuk — **sekarang punya UI di kedua halaman, lihat A.4**).

**Isu berulang (masih relevan):** browser sering nge-cache file lama di `localhost:8000`. Fix: `F12 → Application → Storage → Clear site data`, kadang perlu diulang beberapa kali.

**File JS termodularisasi:** `kamus.html` → 10 file di folder `kamus/` (termasuk `kamus-nuance.js` dan **`kamus-pola.js` BARU sesi ini**, keduanya berdiri sendiri lewat `fetch()` + `MutationObserver` di `#d-hanzi`, tidak mengubah `kamus-detail.js`). `flashcard.html` → 6 file (tidak nambah file baru — fitur game pola diintegrasikan ke 4 file modul yang sudah ada: `flashcard-decks.js`, `flashcard-games.js`, `flashcard-init.js`, `flashcard-session.js`). `wordbuilder.html` — berisi latihan pola KALIMAT, BUKAN pembentukan kata — beda lapisan sepenuhnya dari A.4.

---

### A.1 — Fitur "🆚 Beda dengan Kata Mirip" (Kamus) + "🎯 Pilih yang Tepat" (Flashcard)

Tidak berubah dari v24. 1.291 pasangan, 2.558 soal di flashcard.

---

### A.2 — Fitur "🌱 Akar Kosakata"

Tidak berubah dari v24. Selesai, dikonfirmasi jalan di HP.

---

### A.3 — Fitur "Pola Pembentukan Kata Majemuk" — UI SELESAI DIBANGUN (BARU sesi ini)

**Status sesi v24:** data selesai dikurasi (8.867 kata, 6 kategori), UI belum ada sama sekali.
**Status sesi v25 (sekarang): UI SELESAI di kedua halaman, رسلان sudah tes dan konfirmasi jalan baik.**

**Bagian 1 — Panel Kamus "🧩 Pola Pembentukan Kata":**
- File baru `kamus/kamus-pola.js`, pola arsitektur identik `kamus-nuance.js`: berdiri sendiri, `fetch('data/kata_majemuk_pola.json')`, `MutationObserver` di `#d-hanzi`, auto-hide kalau kata tidak ada di data (otomatis mencakup semua kata 1-karakter & kata 3+ karakter).
- Ditempatkan di `kamus.html` tepat setelah panel "Beda dengan Kata Mirip", sebelum "Komponen Karakter".
- Isi panel: nama pola dalam Hanzi (mis. `偏正式`) + label singkat Indonesia (badge, mis. "Modifier–Inti") + deskripsi generik pola + teks `keterangan_id` spesifik kata tersebut.
- **Keputusan styling penting:** awalnya direncanakan 6 warna beda per kategori, tapi setelah cek `kamus.html` ternyata palet CSS yang ada cuma `--gold`/`--red` (tidak ada biru/hijau/ungu/dst.). Diputuskan: TIDAK menambah warna baru (ikuti prinsip yang sudah dipakai di komentar CSS nuance), pembeda 6 kategori pakai label teks saja, badge konsisten warna gold.
- Peta label (`POLA_LABEL`) — 联合式="Koordinatif", 偏正式="Modifier–Inti", 动宾式="Verba–Objek", 主谓式="Subjek–Predikat", 补充式="Verba–Pelengkap", lainnya="Lainnya". **Dicatat: peta ini DUPLIKAT (bukan shared) di 2 tempat — `kamus/kamus-pola.js` dan `flashcard/flashcard-games.js` — karena `kamus.html` & `flashcard.html` adalah 2 halaman terpisah tanpa state bersama. Kalau daftar 6 kategori pernah berubah/ditambah di masa depan, WAJIB update di KEDUA tempat.**

**Bagian 2 — Game Flashcard "🧩 Tebak Pola Kata":**
- TIDAK ada file baru — diintegrasikan ke 4 modul yang sudah ada (`flashcard-decks.js`, `flashcard-games.js`, `flashcard-init.js`, `flashcard-session.js`), plus 1 sidebar item baru di `flashcard.html` (accordion "Filter Game", `data-deck="pola-choice"`, id count `due-pola-kata`).
- Konsep: kata 2-karakter ditampilkan sebagai prompt (audio AMAN didengar di sini — beda dari mode nuance, karena yang ditanya kategori struktur, bukan identitas kata), رسلان pilih dari **6 opsi kategori penuh** (bukan diacak jadi 4 — sengaja, karena kategori memang cuma 6, dan repetisi penuh tiap soal dianggap lebih mendidik daripada subset acak).
- Feedback pasca-jawab pakai `keterangan_id` spesifik kata dari `kata_majemuk_pola.json` (bukan `gameWordMeaning()` generik) — sama filosofinya dengan mode nuance.
- Reuse penuh infrastruktur game generik yang sudah ada (`tg-prompt-area`, `tg-options`, `renderGamePrompt`, dst.) — tidak perlu HTML/CSS layar game baru, cuma nambah 1 sidebar item + logic mode `'pola'` di beberapa fungsi (`selectDeck`, `startAudioGame`, `renderToneGameQuestion`, `renderGameOptions`, `answerGame`).
- Pinyin kata (untuk ditampilkan & didengar) diambil dari `FC.wordBySimplified` saat build soal — `kata_majemuk_pola.json` sendiri tidak menyimpan field pinyin.

**BELUM DIKERJAKAN — sisa dari fitur ini (opsional, lihat Bagian E):** verifikasi lanjutan ~1.700 kata 动宾式/补充式, skema kata 3+ karakter.

---

## B. Status Kualitas Data

Tidak berubah dari v24 — `kata_majemuk_pola.json` tetap 8.867 kata, kualitas baik dengan catatan (~1.700 kata 动宾式/补充式 belum diverifikasi ulang, lihat BLUEPRINT v24 Bagian B untuk detail lengkap). Sesi ini TIDAK menyentuh kualitas data, murni membangun UI/UX di atas data yang sudah ada.

**`nuance_pairs.json`, `graded_readers.json`, `app_words.json`, `produktif_karakter.json`** — tidak berubah.

---

## C. Script/File Sesi Ini (v25)

**Baru dibuat:** `kamus/kamus-pola.js`.

**Dimodifikasi (integrasi, bukan file baru):**
- `kamus.html` — CSS panel pola (`.pola-badge-row`, `.pola-zh`, `.pola-label`, `.pola-desc`, `.pola-keterangan`) + HTML section `#d-section-pola` + tag `<script src="kamus/kamus-pola.js">`.
- `flashcard.html` — 1 sidebar item baru (`data-deck="pola-choice"`, id count `due-pola-kata`) di accordion "Filter Game", sebelah item "Pilih yang Tepat".
- `flashcard/flashcard-decks.js` — state `FC.polaEntries`, field `toneGame.polaQuestions`, blok intercept deck `pola-choice` di `selectDeck()`, fungsi `loadPolaGameData()`.
- `flashcard/flashcard-games.js` — konstanta `POLA_LABEL`/`POLA_KEYS`, fungsi `buildPolaQuestions()`, cabang mode `'pola'` di `startAudioGame()`/`renderToneGameQuestion()`/`renderGameOptions()`/`answerGame()`.
- `flashcard/flashcard-init.js` — panggilan `loadPolaGameData()` sejajar `loadNuanceData()`.
- `flashcard/flashcard-session.js` — intercept deck `pola-choice` di `startSession()`.

**Tidak ada perubahan pipeline data Python sesi ini** — murni kerja frontend di atas `kata_majemuk_pola.json` yang sudah selesai dari v24.

**Dari sesi sebelumnya, tidak berubah:** semua script v18-v24 (lihat BLUEPRINT v24 Bagian C).

---

## D. Metodologi

**Pola baru sesi ini — cek palet CSS yang ADA sebelum merancang skema warna baru.** Rencana awal (6 warna beda per kategori pola) dibatalkan setelah baca langsung `kamus.html` dan ketemu cuma `--gold`/`--red` yang didefinisikan. Pelajaran: untuk keputusan styling/desain, jangan asumsikan dari nama fitur atau kebiasaan umum web design — baca dulu file CSS yang sebenarnya ada, ikuti token yang sudah dipakai, baru putuskan.

**Pola baru — integrasi UI butuh file HTML asli, tidak bisa ditebak dari file JS module saja.** Baik untuk `kamus.html` maupun `flashcard.html`, permintaan upload file HTML (bukan cuma modul JS-nya) dilakukan secara eksplisit sebelum coding, karena markup sidebar/section adalah HTML statis (bukan hasil render JS) — pola ini konsisten dipakai 2× di sesi ini dan sebaiknya jadi kebiasaan baku ke depan kalau kerja di halaman yang belum pernah disentuh di sesi berjalan.

**Pola dari v24 (batas kepercayaan AI eksternal untuk klasifikasi, tahu kapan berhenti mengejar kesempurnaan data) tetap berlaku, tidak berubah — tidak relevan dipakai sesi ini karena tidak ada kerja data baru.**

---

## E. Prioritas Tugas Berikutnya

1. **(Opsional, prioritas rendah, kalau رسلان mau lanjutkan nanti)** Verifikasi lanjutan sisa ~1.700 kata 动宾式/补充式 yang belum ditinjau — kemungkinan besar tidak dikerjakan lagi via AI eksternal yang sama (terbukti tidak andal di v24), mungkin butuh AI eksternal berbeda atau dibiarkan permanen sebagai keterbatasan diketahui.

2. **(Opsional, kalau diminta di masa depan)** Skema untuk kata 3+ karakter (`kata_majemuk_3plus_INFO_ONLY.json`, 1.287 kata) — butuh pendekatan berjenjang/rekursif, belum ada rancangan teknis sama sekali. Kalau dikerjakan, ingat: panel Kamus & game Flashcard yang sudah ada di v25 dirancang KHUSUS skema 6-kategori 2-karakter — kata 3+ karakter kemungkinan besar butuh UI/skema kategori terpisah, bukan sekadar nambah data ke `kata_majemuk_pola.json` yang sama.

3. **(Opsional, prioritas rendah)** Accordion `kamus-nuance.js` untuk 1 kata → >1 pasangan — tetap dianggap tidak perlu untuk saat ini (lihat BLUEPRINT v24 A.1), dicatat ulang murni untuk kelengkapan riwayat.

4. Lanjutkan pola living-doc + changelog terpisah.

---

## F. Riwayat Sesi (changelog)

**Sesi ini (v25):** **Bangun UI lengkap untuk fitur "Pola Pembentukan Kata Majemuk"** (data-nya sudah selesai dari v24). Ringkasan:
1. Desain disepakati di awal sesi (رسلان serahkan sepenuhnya ke keputusan Claude): panel info pasif di Kamus + game pilihan-ganda di Flashcard, ditempatkan setelah fitur nuance yang sudah ada, styling konsisten dengan yang sudah ada.
2. Panel Kamus dibangun: file baru `kamus/kamus-pola.js` mengikuti pola arsitektur `kamus-nuance.js` persis (berdiri sendiri, fetch data sendiri, auto-hide, tidak mengubah `kamus-detail.js`). Rencana 6-warna dibatalkan setelah cek `kamus.html` langsung — palet CSS cuma punya `--gold`/`--red`, jadi pembeda kategori pakai label teks saja.
3. Game Flashcard "🧩 Tebak Pola Kata" dibangun dengan reuse penuh infrastruktur game generik yang sudah ada (tone-game engine) — tidak perlu HTML/CSS baru untuk layar game, cuma logic mode `'pola'` ditambahkan ke 4 modul JS yang sudah ada + 1 sidebar item baru di `flashcard.html`.
4. Kedua fitur diverifikasi: cek sintaks JS (semua file lolos `new Function()` check), cek semua 6 kategori di `kata_majemuk_pola.json` cocok dengan peta label (tidak ada yang jatuh ke fallback), cek keseimbangan tag HTML pasca-sisipan.
5. Integrasi dilakukan bertahap sesuai file yang رسلان upload: `kamus.html` dulu (sesi request awal), lalu modul-modul Flashcard (`flashcard-decks.js`, `flashcard-games.js`, `flashcard-init.js`, `flashcard-session.js`), lalu `flashcard.html` terakhir untuk sidebar item — pola "minta file HTML asli dulu sebelum edit markup" dipakai konsisten 2×.
6. رسلان sudah tes kedua fitur (panel Kamus & game Flashcard) di app dan konfirmasi hasilnya baik.
7. Sesi ditutup dengan BLUEPRINT v25 ini; dua item opsional (verifikasi 动宾式/补充式, skema kata 3+ karakter) tetap belum dikerjakan, dilanjutkan nanti kalau diminta.

**Sebelumnya (lihat BLUEPRINT v24, v23, v22, v21, v20, v19 & v18 utk detail lengkap):** v24 — klasifikasi 8.867 kata ke 6 pola pembentukan kata majemuk (data saja, UI belum ada). v23 — kurasi `nuance_pairs.json` 15→1.291 pasangan. v22 — pengumpulan kandidat nuance, fitur "Akar Kosakata". v21 — 15 pasangan nuance resmi, fitur Flashcard "Pilih yang Tepat". v20 — fitur "Beda dengan Kata Mirip" dari nol. v19/v18 — audit sistemik, sistem checkpoint.py, modularisasi kamus.html.

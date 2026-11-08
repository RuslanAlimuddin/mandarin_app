# BLUEPRINT — Fitur "🌱 Akar Kosakata" (Mandarin Interaktif)

> Tempel dokumen ini di awal percakapan baru dengan Claude supaya konteks sesi ini tidak hilang. Ini bukan mengganti BLUEPRINT utama رسلان (yang sudah mencapai v16+ dari sesi-sesi sebelumnya) — ini ringkasan KHUSUS untuk fitur "Akar Kosakata" yang dikerjakan lintas beberapa sesi terakhir. Gabungkan ke BLUEPRINT utama sesuai penomoran versi رسلان sendiri.

## Konteks Proyek
- Aplikasi: **Mandarin Interaktif** — aplikasi belajar Mandarin offline, vanilla HTML/CSS/JS, disimpan lokal di `C:\mandarin_app\`.
- Developer & user tunggal: رسلان.
- Semua data JSON ada di `C:\mandarin_app\data\`.
- File JS kamus.html dimodularisasi jadi 8 file di folder `kamus/` (bukan lagi 1 file besar).
- File JS flashcard.html dimodularisasi jadi 6 file (decks/games/session/init/srs/storage-layout).
- **Isu berulang**: browser sering nge-cache file lama di `localhost:8000`. Fix: `F12 → Application → Storage → Clear site data`, kadang perlu diulang beberapa kali.

## Ide Awal Fitur Ini
Analogi dari ilmu sharaf bahasa Arab: satu akar kata bisa "beranak-pinak" jadi banyak kosakata lewat wazan. Di Mandarin, padanannya: **satu karakter dasar (akar) muncul sebagai komponen di banyak kata majemuk**. Fitur "Akar Kosakata" mengidentifikasi karakter-karakter paling produktif (paling banyak kata turunannya) dari `app_words.json`, lalu menampilkannya sebagai grup jelajah baru — mirip radikal/tema/goresan yang sudah ada.

## Peta Besar: 5 Lapisan Morfologi Mandarin (konteks ide dari awal percakapan)
Analogi awal: sharaf bahasa Arab (akar konsonan + wazan) → satu unit kecil beranak-pinak jadi banyak kosakata. Untuk Mandarin, رسلان & Claude memetakan 5 lapisan padanan berikut. **Cuma poin 1 yang dikerjakan di sesi ini** — poin 3 & 4 sudah ada dari sesi-sesi SEBELUMNYA (bukan hasil sesi ini), poin 2 & 5 masih sekadar ide, belum ada implementasi:

| # | Lapisan | Status | Keterangan |
|---|---|---|---|
| 1 | **Karakter sebagai morfem** (akar kata, mis. 电 → 电脑/电话/电视...) | ✅ Dibangun sesi ini | Fitur "🌱 Akar Kosakata" — lihat detail di bawah |
| 2 | **Sufiks/prefiks produktif** (mirip wazan, mis. 者/家/性/化/员 → "keluarga kata" berdasar akhiran gramatikal) | ❌ Belum ada sama sekali | Beda dari poin 1: ini butuh daftar kurasi manual sufiks umum (bukan hitung frekuensi otomatis), lalu cari semua kata yang berakhiran/berawalan sufiks itu. Kalau mau dibangun nanti, ini kandidat fitur baru terpisah dari "Akar Kosakata". |
| 3 | **Radikal (部首)** sebagai kategori makna | ✅ Sudah ada (lama) | "Per Radikal" — Kamus (`openGroupPanel('radical')`) & Flashcard (`renderSidebarRadikal`), pakai `index_radical.json` |
| 4 | **Fonetik-semantik (形声字)** | ✅ Sudah ada (lama) | "Per Komponen Fonetik" — Kamus & Flashcard, pakai `index_phonetic.json` |
| 5 | **Pola pembentukan kata majemuk** (V+Objek, Subjek+Predikat, pasangan sinonim/antonim digabung, dll — pola gramatikal pembentuk kata, bukan sekadar berbagi karakter) | ❌ Belum ada sama sekali | Beda dari poin 1 & 2: ini butuh KLASIFIKASI POLA (semantik relasi antar-karakter dalam kata), bukan cuma pengelompokan karakter. Paling kompleks dari 5 poin, belum ada rancangan teknis sama sekali. |



### 1. `analisis_produktivitas.py`
- Input: `app_words.json`
- Proses: untuk tiap karakter tunggal, hitung berapa kata majemuk (2+ karakter) yang mengandungnya (greedy, exclude diri sendiri).
- Output: `produktif_karakter.json` — format:
  ```json
  { "不": { "hsk": "1", "pinyin": "bù", "arti": "tidak; tidak begitu",
            "jumlah_turunan": 216,
            "kata_turunan": [ {"kata":"不过","pinyin":"bù guò","arti":"hanya","hsk":"2"}, ... ] } }
  ```
- Hasil real: **1.389 karakter akar** (dari 1.572 karakter tunggal di app_words.json, yang minimal 1 turunan), **16.179 kata turunan** total. Top produktif: 不(216), 人(150), 子(146), 一(134), 大(121), 心(106)...
- **⚠️ BUG YANG SUDAH DIPERBAIKI**: fungsi `short_meaning()` awalnya memotong arti ke 40 karakter + "..." — ini memotong data PERMANEN di sumbernya, bukan cuma tampilan, sehingga ikut terpotong di semua file turunan (xlsx, HTML mandiri). **Sudah diperbaiki** (dihapus pemotongannya), dan seluruh pipeline sudah di-regenerate dengan versi yang benar. Kalau ada file lama dari sebelum fix ini, harus di-regenerate ulang.

### 2. Integrasi ke `kamus.html` (Kamus, versi Web app)
File yang diubah (BUKAN tambahan file baru, integrasi ke sistem existing):
- `kamus.html` — 1 item sidebar baru: `🌱 Akar Kosakata`, `onclick="openGroupPanel('akar')"`
- `kamus-data.js` — tambah `STATE.dataAkar`, load `data/produktif_karakter.json` lazy bareng index radikal/goresan/tema (di `loadIndexFiles()`)
- `kamus-actions-filters.js` — tambah cabang `else if (type === 'akar')` di `openGroupPanel()`, render grid chip diurutkan `jumlah_turunan` desc
- `kamus-cards-ui.js` — tambah cabang `else if (type === 'akar')` di `selectGroupItem()`, ambil `kata_turunan[].kata` jadi `ids`, panggil `renderGroupResults(ids, label)` yang SUDAH ADA — otomatis dapat render kartu, mode tabel, export/print gratis tanpa kode tambahan.

### 3. Integrasi ke `flashcard.html` (Flashcard SRS)
- `flashcard.html` — 1 section accordion baru "🌱 Akar Kosakata" (pola sama seperti accordion Radikal), search box `search-akar`, container `sidebar-akar-list`
- `flashcard-decks.js`:
  - `FC.dataAkar` ditambah ke state
  - `data/produktif_karakter.json` dimuat bareng index tema/radikal/goresan
  - `renderSidebarAkar()` — fungsi baru, sidebar diurutkan dari paling produktif, `deckId = 'akar-' + encodeURIComponent(char)`
  - `buildDeckQueue()` — cabang baru untuk `deckId.startsWith('akar-')`, pool = kata dari `kata_turunan`
  - Ditambahkan ke `isBrowseDeck` (mode jelajah bebas, bukan rotasi SRS ketat — sama seperti radikal/tema)

### 4. `konversi_tabel_akar.py`
- Mengonversi `produktif_karakter.json` (nested) → tabel Excel FLAT siap print, dengan merge cell per grup akar.
- Kolom: `Akar Kosakata | Pinyin Akar | Arti Akar | Kata Turunan | Pinyin Turunan | Arti Turunan | HSK Turunan | 💡 Bantu Ingat | 📜 Asal-Usul | Radikal`
- **Temuan penting**: fitur "Bantu Ingat" di aplikasi (`kamus-detail.js` → `tryRenderMnemonic()`/`renderMnemonicBox()`) TIDAK berasal dari file terpisah — dihasilkan ALGORITMIK: dekomposisi kata per karakter, lookup makna tiap karakter (prioritas: `char_etymology_id.json` → `app_words.json`), dirangkai jadi rantai "字 (makna) + 字 (makna) → arti". Script Python ini mereplikasi persis logika tsb.
- Kolom "📜 Asal-Usul" ambil dari field `asal_usul_id` di `char_etymology_id.json` (2.840 karakter, coverage 100%).
- Cara pakai:
  ```
  python konversi_tabel_akar.py produktif_karakter.json app_words.json output.xlsx --etimologi char_etymology_id.json
  ```
- Opsi lain: `--min-turunan N` (filter akar minimal N turunan), `--csv` (output CSV alih-alih xlsx).
- Hasil terbaru (setelah fix truncation): 1.389 akar, 16.179 kata turunan, Bantu Ingat terisi 16.164/16.179 (~99,9%), Asal-Usul 16.175/16.179 (~100%).

### 5. `xlsx_ke_html_mandiri.py`
- Mengonversi `akar_kosakata.xlsx` → **1 file HTML berdiri sendiri** (semua data ter-embed sebagai JSON di dalam `<script>`, tanpa fetch, tanpa koneksi ke `mandarin_app/` sama sekali) — untuk dibuka langsung di HP (file lokal, browser apa saja, offline).
- Tema dark-gold konsisten dengan aplikasi utama, tapi dibangun CSS sendiri (tidak bergantung `shared/style.css`).
- Fitur: search bar, sort (Terbanyak/A-Z), tap akar → expand daftar kata (lazy render biar ringan), tap kata → expand detail Bantu Ingat + Asal-Usul + Radikal.
- Cara pakai:
  ```
  python xlsx_ke_html_mandiri.py akar_kosakata.xlsx akar_kosakata_mandiri.html
  ```
- File terakhir: ~4,4 MB (1.389 akar, 16.179 kata, sudah termasuk fix truncation).

## File-File yang Sudah Diserahkan (nama di outputs, رسلان perlu rename/timpa sesuai lokasi asli)
| File | Ditaruh di | Fungsi |
|---|---|---|
| `analisis_produktivitas.py` | mana saja (dijalankan manual) | generate `produktif_karakter.json` dari `app_words.json` |
| `produktif_karakter.json` | `C:\mandarin_app\data\` | data akar-kosakata, dipakai Kamus & Flashcard |
| `kamus.html`, `kamus-data.js`, `kamus-actions-filters.js`, `kamus-cards-ui.js` | `C:\mandarin_app\` dan `C:\mandarin_app\kamus\` | integrasi fitur di Kamus |
| `flashcard.html`, `flashcard-decks.js` | `C:\mandarin_app\` | integrasi fitur di Flashcard |
| `konversi_tabel_akar.py` | mana saja (dijalankan manual) | generate tabel Excel printable |
| `xlsx_ke_html_mandiri.py` | mana saja (dijalankan manual) | generate HTML mandiri untuk HP |
| `akar_kosakata_mandiri.html` | HP رسلان (bukan folder app) | viewer offline mandiri untuk HP |

## Status Saat Sesi Berakhir
- Fitur "Akar Kosakata" di Kamus & Flashcard: **sudah dikonfirmasi bekerja** رسلان (sempat macet karena cache browser, sudah teratasi setelah clear site data berkali-kali).
- Bug truncation 40-karakter: **sudah diperbaiki**, seluruh pipeline (produktif_karakter.json → xlsx → HTML mandiri) sudah di-regenerate dengan versi bebas-potongan.
- File HTML mandiri untuk HP: **sudah dikirim versi terbaru** (pasca-fix), رسلان belum konfirmasi hasil tes ulang di HP.

## Kemungkinan Follow-Up (belum diminta, sekadar catatan potensi)
- `produktif_karakter.json` versi lama (sebelum fix truncation) di `C:\mandarin_app\data\` mungkin masih ke-pakai kalau رسلان belum sempat timpa ulang — perlu dicek/dikonfirmasi.
- Belum ada tombol export/print khusus untuk deck "Akar Kosakata" di Flashcard (Kamus sudah otomatis dapat lewat sistem existing, Flashcard tidak perlu print karena bukan itu fungsinya).
- `xlsx_ke_html_mandiri.py` belum divalidasi tampilannya di browser HP asli (baru divalidasi datanya via parsing JSON di sisi server).
- **Fitur "Sufiks/Prefiks Produktif" (poin 2 peta besar)** — belum dikerjakan. Kalau nanti diminta: butuh daftar kurasi manual sufiks umum (者/家/性/化/员/度/性/主义 dst, mungkin 20-30 entri), lalu script cari semua kata di `app_words.json` yang berakhiran/berawalan sufiks itu, tampilkan sebagai grup "keluarga kata" mirip pola akar kosakata tapi arah pencarian beda (sufiks tetap, akar bervariasi — kebalikan dari Akar Kosakata yang akarnya tetap, turunan bervariasi).
- **Fitur "Pola Pembentukan Kata Majemuk" (poin 5 peta besar)** — belum dikerjakan, belum ada rancangan teknis. Perlu klasifikasi pola gramatikal (V+O, Subjek+Predikat, dst), kemungkinan butuh anotasi manual karena app_words.json tidak punya field untuk pola ini.

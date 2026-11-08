# BLUEPRINT — Mandarin Interaktif — v22
_(Handoff document. Baca Bagian A–B dulu untuk onboarding cepat. Bagian C–E untuk detail teknis. Bagian F untuk riwayat sesi.)_

---

## A. Arsitektur Saat Ini (Living Doc)

**Aplikasi:** "Mandarin Interaktif" — aplikasi belajar Mandarin offline, vanilla HTML/CSS/JS, single-user (رسلان), berjalan lokal di `C:\mandarin_app\` (biasanya via `python -m http.server` / `localhost:8000`).

**Sumber data utama** (folder `data/`): `app_words.json` (~11.726 entri), `cidict_index.json` (~125.000 entri, fallback CC-CEDICT), `graded_readers.json` (123 entri, semua sudah punya field `type`), `char_etymology_id.json` (100% coverage, 2.840 karakter), `confusion_groups.json` (53 grup), `nuance_pairs.json` (**15 pasangan resmi, LENGKAP** — fitur "Beda dengan Kata Mirip" di Kamus + "🎯 Pilih yang Tepat" di Flashcard), **`produktif_karakter.json`** (BARU — lihat di bawah, 1.389 akar karakter, 16.179 kata turunan).

**Isu berulang (dari sesi-sesi sebelumnya, masih relevan):** browser sering nge-cache file lama di `localhost:8000`. Fix: `F12 → Application → Storage → Clear site data`, kadang perlu diulang beberapa kali.

**File JS termodularisasi:** `kamus.html` → 8 file di folder `kamus/`. `flashcard.html` → 6 file (`flashcard-decks.js`, `flashcard-games.js`, `flashcard-session.js`, `flashcard-init.js`, `flashcard-srs.js`, `flashcard-storage-layout.js`).

---

### A.1 — Fitur "🎯 Pilih yang Tepat" (Flashcard, dari v21 — tidak berubah)

Deck game kalimat-rumpang pilihan-ganda reuse `data/nuance_pairs.json`. Tiap kata di `comparison[]` satu pasangan nuance jadi 1 soal (kalimat rumpang dari `example_cn`, opsi = SEMUA kata di `comparison[]` pasangan itu, TIDAK dipadding ke 4). Pasangan berhanzi identik (kasus 借 dua arah) otomatis dikecualikan dari game. Kata majemuk terpisah (离合词, mis. 生气→生我的气) gagal menghasilkan soal kalau `example_cn` memakai bentuk terpisah — sistem skip aman, bukan error.

File yang diubah: `flashcard.html`, `flashcard-decks.js`, `flashcard-games.js`, `flashcard-session.js`, `flashcard-init.js`. **Status: sudah di-QA رسلان langsung di app, dikonfirmasi berjalan baik.** Dengan 15 pasangan resmi, game menghasilkan 28 soal.

**Belum dikerjakan** (dicatat untuk nanti): panel Kamus `kamus-nuance.js` belum mendukung 1 kata → >1 pasangan sekaligus (accordion) — baru relevan setelah kurasi kandidat besar (lihat Bagian E) benar-benar masuk resmi.

---

### A.2 — Fitur "🌱 Akar Kosakata" (BARU digabung ke BLUEPRINT utama — dikerjakan di sesi terpisah sebelumnya)

Analogi dari sharaf bahasa Arab (akar konsonan + wazan): satu karakter dasar (akar) muncul sebagai komponen di banyak kata majemuk (mis. 电 → 电脑/电话/电视...). Fitur ini mengidentifikasi karakter paling produktif dari `app_words.json` dan menampilkannya sebagai grup jelajah baru, sejajar Radikal/Tema/Goresan yang sudah ada.

**Peta besar 5 lapisan morfologi Mandarin** (konteks ide, cuma poin 1 yang dikerjakan):

| # | Lapisan | Status |
|---|---|---|
| 1 | Karakter sebagai morfem (akar → turunan) | ✅ **Dibangun** — ini fitur "Akar Kosakata" |
| 2 | Sufiks/prefiks produktif (者/家/性/化/员 dst → "keluarga kata" berdasar akhiran) | ❌ Belum ada — butuh kurasi manual daftar sufiks, arah pencarian kebalikan dari poin 1 (sufiks tetap, akar bervariasi) |
| 3 | Radikal (部首) sebagai kategori makna | ✅ Sudah ada (lama) — "Per Radikal", `index_radical.json` |
| 4 | Fonetik-semantik (形声字) | ✅ Sudah ada (lama) — "Per Komponen Fonetik", `index_phonetic.json` |
| 5 | Pola pembentukan kata majemuk (V+O, Subjek+Predikat, dll) | ❌ Belum ada, belum ada rancangan teknis — paling kompleks, kemungkinan butuh anotasi manual |

**Pipeline yang dibangun:**

1. **`analisis_produktivitas.py`** — input `app_words.json`, hitung tiap karakter tunggal muncul di berapa kata majemuk. Output `produktif_karakter.json`. Hasil: **1.389 karakter akar** (dari 1.572 karakter tunggal), **16.179 kata turunan** total. Top produktif: 不(216), 人(150), 子(146), 一(134), 大(121), 心(106).
   - ⚠️ **Bug ditemukan & diperbaiki**: `short_meaning()` awalnya memotong arti ke 40 karakter + "..." — memotong data PERMANEN di sumbernya (bukan cuma tampilan). Sudah diperbaiki, seluruh pipeline di-regenerate.

2. **Integrasi Kamus** (`kamus.html`, `kamus-data.js`, `kamus-actions-filters.js`, `kamus-cards-ui.js`) — item sidebar baru `🌱 Akar Kosakata`, lazy-load `produktif_karakter.json`, render grid chip diurutkan `jumlah_turunan` desc, reuse `renderGroupResults()` yang sudah ada (otomatis dapat kartu/tabel/export/print gratis).

3. **Integrasi Flashcard** (`flashcard.html`, `flashcard-decks.js`) — accordion baru "🌱 Akar Kosakata" dgn search box, `FC.dataAkar`, `renderSidebarAkar()`, `deckId = 'akar-' + char`, ditambahkan ke `isBrowseDeck` (mode jelajah bebas kayak radikal/tema).

4. **`konversi_tabel_akar.py`** — konversi `produktif_karakter.json` → Excel flat siap-print (kolom: Akar | Pinyin | Arti | Kata Turunan | Pinyin Turunan | Arti Turunan | HSK | Bantu Ingat | Asal-Usul | Radikal). Kolom "Bantu Ingat" mereplikasi PERSIS logika algoritmik `kamus-detail.js` (dekomposisi kata → lookup makna per karakter dari `char_etymology_id.json` lalu fallback `app_words.json` → rangkai jadi rantai makna) — bukan dari file terpisah. Hasil: Bantu Ingat terisi 16.164/16.179 (~99,9%), Asal-Usul 16.175/16.179 (~100%).

5. **`xlsx_ke_html_mandiri.py`** — konversi xlsx → 1 file HTML berdiri sendiri (data ter-embed, tanpa fetch/koneksi ke `mandarin_app/`) untuk dibuka offline di HP. Tema dark-gold konsisten tapi CSS sendiri. Fitur: search, sort (Terbanyak/A-Z), expand akar → daftar kata (lazy render) → expand kata → Bantu Ingat + Asal-Usul + Radikal. File terakhir ~4,4 MB.

**Status saat digabung ke BLUEPRINT ini:**
- Fitur di Kamus & Flashcard: **sudah dikonfirmasi bekerja رسلان** (sempat macet cache browser, teratasi setelah clear site data berkali-kali).
- Bug truncation 40-karakter: **sudah diperbaiki**, seluruh pipeline sudah di-regenerate versi bebas-potongan.
- File HTML mandiri untuk HP: **sudah dikirim versi terbaru** (pasca-fix), **رسلان BELUM konfirmasi hasil tes ulang di HP** — masih menggantung.

**Follow-up yang belum dikerjakan (dicatat, belum diminta):**
- `produktif_karakter.json` versi LAMA (sebelum fix truncation) mungkin masih ke-pakai di `C:\mandarin_app\data\` kalau رسلان belum sempat timpa ulang — **perlu dicek/dikonfirmasi**.
- Belum ada tombol export/print khusus deck "Akar Kosakata" di Flashcard (dianggap tidak perlu — Kamus sudah otomatis dapat lewat sistem existing).
- `xlsx_ke_html_mandiri.py` belum divalidasi visual di browser HP asli (baru divalidasi datanya via parsing JSON sisi server).
- Fitur "Sufiks/Prefiks Produktif" (poin 2 peta besar) — belum dikerjakan, idenya sudah ada (lihat tabel di atas).
- Fitur "Pola Pembentukan Kata Majemuk" (poin 5 peta besar) — belum dikerjakan, belum ada rancangan teknis sama sekali.

---

## B. Status Kualitas Data

**`nuance_pairs.json` — 15 pasangan resmi, LENGKAP & TERVERIFIKASI** (tidak berubah dari v21).

**`graded_readers.json` — backfill `type` SELESAI** (tidak berubah dari v21, 113 bacaan + 10 percakapan).

**`app_words.json` — entri 参差 ditambahkan** (tidak berubah dari v21).

**`produktif_karakter.json` — BARU, status: sudah di-generate & terintegrasi, bug truncation sudah diperbaiki** (lihat A.2). Perlu dicek apakah versi di `C:\mandarin_app\data\` sudah versi terbaru (pasca-fix) atau masih versi lama — lihat follow-up di A.2.

**Bank kandidat mentah near-synonym — PROSES GENERATE DIHENTIKAN sesi ini atas keputusan رسلان.** Total akhir terkumpul:

| File | Rentang id | Jumlah unik (per-file) |
|---|---|---|
| Daftar A | tabel markdown awal | 575 |
| Daftar B | 581-973 | 393 |
| Daftar C | 974-1100 | 127 |
| Daftar D | 1101-1440 | 334 |
| Daftar E | 1441-1900 | 448 |
| Daftar F | 1901-2470 | 520 |
| Daftar G | 2471-2880 | 405 |
| Daftar H | 2881-3595 | 596 |
| **Total mentah (sebelum dedup lintas-file)** | | **3.398** |
| **Total UNIK setelah dedup PENUH lintas 8 file** (memperhitungkan urutan kata terbalik, mis. a/b = b/a) | | **2.891** |

File gabungan final (`daftar_master_gabungan_2891_unik.txt`) sudah dibuat dan diserahkan ke رسلان — berisi HANYA daftar kata (bukan data lengkap JSON), untuk dipakai sebagai referensi anti-duplikat kalau nanti mau generate lagi.

**Tren kualitas yang tercatat selama proses (penting utk sesi kurasi nanti):**
- Tone mark: masalah fatal di batch B (100% tanpa tone mark), sudah diperbaiki di batch C dst (100% benar sejak itu).
- **1 insiden serius**: batch percobaan pertama untuk id 1441-1830 GAGAL TOTAL (100% field "words" berisi kata Indonesia, bukan hanzi — AI-nya "tersesat" di sesi chat yang kepanjangan). Dibuang seluruhnya, diganti batch baru (Daftar E) yang bersih.
- Duplikat/overlap NAIK BERTAHAP tiap batch — indikasi pool kandidat genuinely baru makin menipis: Daftar D (15%) → Daftar F (19,8%) → Daftar G+H gabungan (20,5%). Ini alasan utama رسلان memutuskan berhenti generate di titik ini.
- **8 file NDJSON mentah (belum di-cross-check ke `app_words.json`, belum masuk skema resmi)** semua tersimpan di riwayat percakapan — رسلان perlu pastikan semua file `sampai_*.txt`/`near-synonym_nuance_pairs1.json` yang pernah diupload masih tersimpan di komputernya sebelum sesi kurasi baru dimulai (Claude tidak menyimpan file antar-sesi).

---

## C. Script/File Sesi-Sesi Terakhir

**Dari v21 (fitur "Pilih yang Tepat"):** `flashcard.html`, `flashcard-decks.js`, `flashcard-games.js`, `flashcard-session.js`, `flashcard-init.js` — lihat A.1.

**Dari sesi Akar Kosakata (digabung v22 ini):** `analisis_produktivitas.py`, `konversi_tabel_akar.py`, `xlsx_ke_html_mandiri.py`, plus perubahan di `kamus.html`/`kamus-data.js`/`kamus-actions-filters.js`/`kamus-cards-ui.js`/`flashcard.html`/`flashcard-decks.js` — lihat A.2.

**Script lama (v18-v20) masih berlaku, tidak berubah:** `checkpoint.py`, `complete_reading_json.py`, `complete_theme_json.py`, `repair_theme_word_sync.py`, `repair_glossary.py`, dst.

---

## D. Metodologi

**Audit/fix data (v18-v21, tidak berubah):** audit read-only → sample-check → `--dry-run` wajib → eksekusi → `checkpoint.py save`.

**Pengumpulan kandidat nuance via AI eksternal (NDJSON workflow, dari v21):** metodologi lengkap ada di BLUEPRINT v21 Bagian D — prompt berjenjang, validasi tiap batch (JSON valid, tone mark, skema, duplikat, overlap, existence), daftar "jangan diulang" disisipkan ulang tiap prompt baru. **Proses ini SELESAI/DIHENTIKAN untuk saat ini** — bukan berarti metodologinya gagal, tapi رسلان menilai 2.891 kandidat unik sudah lebih dari cukup sebagai bank data, dan tren duplikasi yang terus naik menunjukkan diminishing returns kalau diteruskan.

**BARU — metodologi transisi antar-sesi Claude untuk fitur besar:** dari pengalaman fitur "Akar Kosakata" (dikerjakan di sesi terpisah, lalu digabung ke BLUEPRINT utama lewat file ringkasan `BLUEPRINT_akar_kosakata.md`), terbukti berguna: kalau suatu fitur dikerjakan di sesi Claude yang berbeda dari sesi BLUEPRINT utama, رسلان bisa minta Claude di sesi itu menulis ringkasan mandiri (format serupa BLUEPRINT tapi scoped ke 1 fitur), lalu upload balik ke sesi BLUEPRINT utama untuk digabung. Ini mencegah kehilangan detail teknis penting saat kerja paralel di beberapa sesi.

---

## E. Prioritas Tugas Berikutnya

1. **(PALING PENTING — WAJIB SESI BARU)** Tahap KURASI kandidat near-synonym. **رسلان sudah memutuskan ini dikerjakan di sesi percakapan BARU** (bukan lanjutan sesi ini), karena kompleksitasnya besar. Yang perlu dibawa ke sesi baru itu:
   - Ke-8 file NDJSON mentah asli (`sampai_1100.txt`, `sampai_1440.txt`, `sampai_1900.txt`, `sampai_2470.txt`, `sampai_2880.txt`, `sampai_3595.txt`, `near-synonym_nuance_pairs1.json`, `near-synonym-disambiguasi_kosakata_Mandarin.txt`) — Claude TIDAK bisa mengingat isinya dari sesi ini, harus diupload ulang.
   - File `daftar_master_gabungan_2891_unik.txt` (daftar kata saja, buat referensi cepat)
   - `app_words.json` (untuk cross-check existence & pinyin/HSK, seperti proses batch 1-9 di v20)
   - `nuance_pairs.json` yang resmi (15 pasangan) — supaya tahu apa yang JANGAN dimasukkan lagi
   - Alur kurasi yang disarankan: (a) gabung 8 file jadi 1 dataset besar, (b) dedup penuh, (c) filter yang semua katanya ada di `app_words.json`, (d) filter kualitas (buang yang aneh/dangkal), (e) prioritaskan HSK rendah dulu, (f) batch kecil + رسلان uji tiap batch di app (pola v20), (g) baru masuk resmi ke `nuance_pairs.json`.

2. **Setelah kurasi besar mulai masuk resmi** → implementasi `kamus-nuance.js` accordion untuk kasus 1 kata → >1 pasangan (sudah didesain konsepnya di v21 Bagian A, belum diimplementasikan).

3. **Follow-up "Akar Kosakata"** (dari A.2, prioritas rendah/menengah):
   - Konfirmasi `produktif_karakter.json` di `C:\mandarin_app\data\` sudah versi terbaru (pasca-fix truncation), bukan versi lama.
   - رسلان tes `akar_kosakata_mandiri.html` di HP asli, konfirmasi tampilan oke.
   - (Opsional, kalau diminta) Fitur "Sufiks/Prefiks Produktif" (poin 2 peta 5 lapisan).
   - (Opsional, kalau diminta) Fitur "Pola Pembentukan Kata Majemuk" (poin 5 peta 5 lapisan) — paling kompleks, belum ada rancangan.

4. Lanjutkan pola living-doc + changelog terpisah.

---

## F. Riwayat Sesi (changelog)

**Sesi ini (v22):** (1) Melanjutkan pengumpulan kandidat near-synonym dari v21 (yang berhenti di 1.440) — 4 batch tambahan dikumpulkan & divalidasi (Daftar E 1441-1900, Daftar F 1901-2470, Daftar G 2471-2880, Daftar H 2881-3595), total kandidat unik naik dari 1.440 jadi **2.891** (dedup penuh lintas-file). (2) Ditemukan & diatasi: batch gagal total (1441-1830 versi awal, 100% kata Indonesia bukan hanzi) — dibuang, prompt diperkuat dgn peringatan eksplisit; disclaimer platform AI nyempil di tengah data (`sampai_3595.txt`) — dibersihkan otomatis, 708 objek berhasil diselamatkan. (3) Tren duplikasi/overlap dipantau tiap batch, terus naik (15% → 19,8% → 20,5%) — jadi dasar keputusan رسلان untuk **menghentikan proses generate** di titik 3.595/2.891 unik. (4) File gabungan final dibuat & diserahkan (`daftar_master_gabungan_2891_unik.txt`). (5) **BLUEPRINT_akar_kosakata.md digabung ke BLUEPRINT utama** — mendokumentasikan fitur "🌱 Akar Kosakata" yang dikerjakan di sesi Claude terpisah sebelumnya (analisis produktivitas karakter, integrasi Kamus & Flashcard, pipeline Excel + HTML mandiri untuk HP), termasuk status follow-up yang masih menggantung (tes HP, cek versi data lama). (6) **Keputusan eksplisit: tahap kurasi kandidat near-synonym akan dikerjakan di SESI PERCAKAPAN BARU**, bukan lanjutan sesi ini — daftar file yang perlu dibawa ke sesi baru itu dicatat di Bagian E poin 1.

**Sebelumnya (lihat BLUEPRINT_v21, v20, v19 & v18 utk detail lengkap):** v21 — 9 pasangan nuance tersisa dilengkapi (15 resmi total), backfill `type` graded_readers, entri 参差, fitur Flashcard "Pilih yang Tepat" dibangun & di-QA. v20 — fitur "Beda dengan Kata Mirip" dibangun dari nol (6 pasangan pertama). v19/v18 — audit sistemik 461 kata, sistem checkpoint.py, sinkronisasi glossary, modularisasi kamus.html.

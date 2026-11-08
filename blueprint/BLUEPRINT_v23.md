# BLUEPRINT — Mandarin Interaktif — v23
_(Handoff document. Baca Bagian A–B dulu untuk onboarding cepat. Bagian C–E untuk detail teknis. Bagian F untuk riwayat sesi.)_

---

## A. Arsitektur Saat Ini (Living Doc)

**Aplikasi:** "Mandarin Interaktif" — aplikasi belajar Mandarin offline, vanilla HTML/CSS/JS, single-user (رسلان), berjalan lokal di `C:\mandarin_app\` (biasanya via `python -m http.server` / `localhost:8000`).

**Sumber data utama** (folder `data/`): `app_words.json` (~11.726 entri), `cidict_index.json` (~125.000 entri, fallback CC-CEDICT), `graded_readers.json` (123 entri), `char_etymology_id.json` (2.840 karakter), `confusion_groups.json` (53 grup), **`nuance_pairs.json` (BESAR PERUBAHAN — 1.291 pasangan LENGKAP & TERVERIFIKASI, naik dari 15 di v22 — lihat Bagian B)**, `produktif_karakter.json` (1.389 akar karakter, 16.179 kata turunan).

**Isu berulang (masih relevan):** browser sering nge-cache file lama di `localhost:8000`. Fix: `F12 → Application → Storage → Clear site data`, kadang perlu diulang beberapa kali.

**File JS termodularisasi:** `kamus.html` → 9 file di folder `kamus/` (termasuk `kamus-nuance.js`, berdiri sendiri lewat `fetch('data/nuance_pairs.json')` + `MutationObserver` di `#d-hanzi`, tidak mengubah `kamus-detail.js`). `flashcard.html` → 6 file.

---

### A.1 — Fitur "🆚 Beda dengan Kata Mirip" (Kamus) + "🎯 Pilih yang Tepat" (Flashcard) — **STATUS BARU: DATA SELESAI DIKURASI PENUH**

Kedua fitur reuse `data/nuance_pairs.json`. Dengan 1.291 pasangan resmi (naik dari 15), game "Pilih yang Tepat" sekarang menghasilkan **2.558 soal** (dari 28 sebelumnya). Kedua fitur **sudah dikonfirmasi رسلان bekerja normal** di app setelah lonjakan data ini.

**Follow-up dari v22 yang sekarang kemungkinan TIDAK RELEVAN LAGI:** accordion `kamus-nuance.js` untuk 1 kata → >1 pasangan. Alasan: pipeline kurasi baru (lihat A.3) secara desain **mencegah 1 kata dipakai di lebih dari 1 pasangan** (cek `used_words` di tiap script). Jadi dalam praktiknya tidak ada kasus 1 kata → banyak pasangan di data saat ini. Tetap dicatat sebagai opsi kalau nanti رسلان sengaja mau menambah pasangan yang overlap secara manual.

---

### A.2 — Fitur "🌱 Akar Kosakata" (dari v22, tidak berubah sesi ini)

Lihat BLUEPRINT v22 Bagian A.2 untuk detail lengkap (analisis produktivitas karakter, integrasi Kamus & Flashcard, pipeline Excel + HTML mandiri HP). **Follow-up yang masih menggantung dari v22, belum disentuh sesi ini:**
- Konfirmasi `produktif_karakter.json` di `C:\mandarin_app\data\` versi terbaru (pasca-fix truncation).
- رسلان belum konfirmasi tes `akar_kosakata_mandiri.html` di HP asli.

---

### A.3 — BARU: Pipeline Kurasi `nuance_pairs.json` Skala Besar (15 → 1.291 pasangan) — **SESI INI, SELESAI**

Ini pekerjaan utama sesi ini, dikerjakan di sesi percakapan baru sesuai rencana v22 Bagian E poin 1.

**Sumber data mentah** (8 file dari v22, total 3.398 mentah / 2.891 unik pasca-dedup — lihat v22 Bagian B untuk rincian per-file):
- Daftar A (575, tabel markdown sederhana — nuansa/kolokasi/contoh/kesalahan, TANPA skema `comparison` lengkap)
- Daftar B–H (2.816, skema lengkap — `comparison[]` per kata dengan pinyin/usage_id/collocations/example/register)

**Pipeline yang dibangun (2 jalur independen, sama-sama menulis ke `nuance_pairs.json` yang sama, urutan bebas, tidak saling bergantung):**

**Jalur 1 — Daftar B–H, otomatis penuh (tidak butuh AI eksternal):**
1. Dedup penuh lintas 8 file, exclude yang sudah jadi 15 pasangan resmi → 2.737 kandidat unik.
2. Filter existence: semua kata pasangan harus ada di `app_words.json` **atau** `cidict_index.json` (fallback ganda ditambahkan setelah ditemukan 555 kandidat valid yang sempat ke-skip cuma karena existence-check awal hanya cek `app_words.json`) → 2.545 kandidat final, tersimpan di `candidates_sorted_by_hsk.json` (diurutkan HSK termudah dulu).
3. **`generate_next_batch.py`** — dijalankan berulang oleh رسلان sendiri di PC (`python generate_next_batch.py 30`). Tiap jalan: pilih N kandidat berikutnya yang katanya belum "kepakai" di pasangan manapun (no-overlap constraint), koreksi pinyin/HSK dari `app_words.json`/`cidict_index.json` (bukan percaya mentah dari kandidat), kasih id `bN_...`, langsung `json.dump` ke `nuance_pairs.json` (aman, tidak pernah rusak format). Dijalankan sampai habis — status akhir: **"Tidak ada kandidat baru yang tersisa"**.

**Jalur 2 — Daftar A, hybrid dengan AI eksternal (ide رسلان, terbukti efisien):**
1. Daftar A dibersihkan (dedup, filter hanzi, filter existence) → 560 pasangan bersih, disimpan `daftarA_clean_pairs.txt` (cuma daftar kata, tanpa skema).
2. رسلان kirim daftar ini (per-chunk 25-40 pasangan) ke AI lain (ChatGPT/Gemini/dst) memakai prompt siap-pakai (`PROMPT_untuk_AI_lain.md`) yang isinya skema JSON persis + 1 contoh lengkap + aturan output NDJSON.
3. **`import_daftarA_batch.py`** — validasi hasil AI lain (JSON valid, jumlah `words`==jumlah `comparison` — mendukung grup 2-arah MAUPUN 3-arah, semua kata ada di `app_words.json`/`cidict_index.json`, tidak overlap kata dengan pasangan yang sudah ada), koreksi pinyin/HSK, gabung aman ke `nuance_pairs.json`.
4. Hasil: **560/560 pasangan Daftar A berhasil masuk (100%)**. Termasuk 1 pasangan terakhir (`朴实/质朴`) yang ditulis langsung oleh Claude (bukan AI eksternal) karena cuma tersisa 1, tidak sepadan kirim ke AI lain untuk itu saja.

**Insight penting soal pola kerja hybrid ini** (dicatat untuk dipakai lagi di tugas serupa ke depan): untuk tugas yang skemanya sudah didefinisikan jelas dan tinggal "isi berulang" (bukan butuh judgment kompleks per-item), delegasikan penulisan konten ke AI eksternal yang رسلان jalankan sendiri, sementara Claude fokus di: (a) menyiapkan skema+prompt presisi, (b) membangun script validasi/keamanan yang menolak input rusak dan mencegah data korup, (c) meninjau kualitas sampel. Ini jauh lebih cepat daripada Claude menulis semua konten sendiri lewat banyak giliran chat.

**Bug ditemukan & diperbaiki selama proses:**
- **Insiden JSON rusak**: رسلان sempat manual-paste batch pertama tanpa koma pemisah antar pasangan (`}{` nempel) → `nuance_pairs.json` gagal parse total, fitur mati untuk SEMUA kata (bukan cuma yang baru). Diperbaiki manual sekali, lalu SEMUA proses setelahnya otomatis lewat script (`json.dump`) — tidak akan terulang.
- **`audit_quality.py`** (script baru, dibuat setelah kurasi selesai untuk QA) menemukan **5 pasangan dengan bug lama** dari data sumber Daftar B (bukan dari pipeline sesi ini): field `"words"` typo terduplikasi (mis. `["对面","对面"]`) padahal seharusnya 2 kata berbeda. **`fix_duplicate_words_bug.py`** dibuat untuk menangani: 1 pasangan bisa diperbaiki (data lengkap ada di `comparison[]`, cuma `words` yang typo — `人间/人间` → `人间/世界`), 4 pasangan lainnya data rusak permanen (comparison cuma punya 1 kata, tidak ada info kata kedua sama sekali) → dihapus. Hasil akhir: **1.291 pasangan bersih**.
- Cek ukuran file (`check_file_sizes.py`, script baru): `nuance_pairs.json` 2,1 MB / ~27ms parse — aman, jauh di bawah `app_words.json` (9MB) dan `cidict_index.json` (26MB) yang sudah lama dipakai tanpa masalah performa.

**File yang SUDAH TIDAK RELEVAN, aman dihapus dari `C:\mandarin_app\`:** `batch1/2/3_nuance_pairs.json`, `daftarA_clean_pairs.txt`, `PROMPT_untuk_AI_lain.md`, `daftarA_output_*.jsonl`, `candidates_sorted_by_hsk.json` (pool sudah habis terpakai).

**Script yang MASIH LAYAK DISIMPAN** (reusable untuk maintenance data ke depan): `generate_next_batch.py` (kalau nanti ada sumber kandidat baru lagi), `import_daftarA_batch.py` (kalau nanti ada batch AI-eksternal lagi), `audit_quality.py` + `check_file_sizes.py` (QA rutin), `checkpoint.py` (backup, tidak berubah dari v18-v22).

---

## B. Status Kualitas Data

**`nuance_pairs.json` — 1.291 pasangan, LENGKAP & TERVERIFIKASI STRUKTURAL** (naik drastis dari 15 di v22). Audit otomatis (`audit_quality.py`) + tinjauan sampel manual 40 pasangan oleh Claude: kualitas linguistik bagus, nuansa akurat, contoh kalimat natural. ~19 kasus "example_cn tidak mengandung kata yang dijelaskan" ternyata heuristik terlalu ketat (contohnya aman secara makna, false positive), bukan kesalahan sungguhan — tidak perlu tindakan lebih lanjut kecuali رسلان menemukan kasus konkret saat pemakaian normal.

**`graded_readers.json` — tidak berubah dari v21/v22** (113 bacaan + 10 percakapan, field `type` lengkap).

**`app_words.json` — tidak berubah dari v22.**

**`produktif_karakter.json` — tidak berubah dari v22**, status follow-up (cek versi terbaru di app) masih menggantung, lihat A.2.

**Bank kandidat mentah near-synonym dari v22 (2.891 unik) — SUDAH HABIS TERPAKAI SEPENUHNYA** lewat pipeline A.3. Tidak ada lagi sisa kandidat di sumber 8 file lama itu.

---

## C. Script/File Sesi Ini (v23)

**Pipeline kurasi nuance_pairs (baru, lihat A.3 untuk detail):**
- `generate_next_batch.py` — auto-pilih & gabung kandidat Daftar B-H, no-overlap constraint, fallback pinyin/HSK app_words→cidict.
- `import_daftarA_batch.py` — validasi & gabung hasil AI eksternal untuk Daftar A, mendukung grup 2-arah & 3-arah.
- `fix_duplicate_words_bug.py` — one-off, perbaiki/hapus 5 pasangan dengan bug `words` typo dari data lama.
- `audit_quality.py` — QA heuristik (pisah "masalah nyata" vs "gaya kosmetik") + sampling acak untuk tinjauan manual.
- `check_file_sizes.py` — cek ukuran & waktu parse semua file `data/`.

**Dari v22 (Akar Kosakata), tidak berubah:** `analisis_produktivitas.py`, `konversi_tabel_akar.py`, `xlsx_ke_html_mandiri.py`.

**Script lama (v18-v21), tidak berubah:** `checkpoint.py`, `complete_reading_json.py`, `complete_theme_json.py`, `repair_theme_word_sync.py`, `repair_glossary.py`, dst.

---

## D. Metodologi

**Audit/fix data (v18-v22, tidak berubah):** audit read-only → sample-check → `--dry-run` wajib → eksekusi → `checkpoint.py save`. **Sesi ini mengikuti pola ini secara ketat**: checkpoint dibuat SEBELUM kurasi besar dimulai (`checkpoint_20260805_104411.zip`), semua script pipeline mendukung `--dry-run`.

**BARU — Pola kerja hybrid Claude + AI eksternal untuk tugas isi-berulang skala besar** (lihat insight lengkap di A.3): cocok dipakai lagi kapan pun ada tugas dengan skema jelas + volume besar + judgment-per-item rendah. Peran Claude bergeser dari "menulis semua konten" jadi "merancang skema+prompt, membangun jaring pengaman validasi, QA sampel".

**BARU — Pola "2 jalur independen, tujuan sama":** kalau ada sumber data campuran (sebagian skema lengkap, sebagian belum), tidak perlu dipaksa 1 alur linear. Boleh dibuat beberapa script yang sama-sama menulis ke file tujuan yang sama, dijalankan dengan urutan bebas oleh پngguna, asal masing-masing aman (validasi + no-overlap + safe JSON write) dan tidak saling bergantung.

**Pengumpulan kandidat nuance via AI eksternal (NDJSON workflow, dari v21/v22):** metodologi dasar tetap sama, tapi v23 menambahkan lapisan keamanan baru: script importer TIDAK PERNAH minta رسلان copy-paste manual ke `nuance_pairs.json` — semua lewat `json.dump` terprogram, menghilangkan risiko kesalahan format (`}{` tanpa koma) yang sempat terjadi 1x di awal sesi ini.

---

## E. Prioritas Tugas Berikutnya

1. **Follow-up "Akar Kosakata"** (dari v22, masih menggantung, prioritas rendah/menengah):
   - Konfirmasi `produktif_karakter.json` di `C:\mandarin_app\data\` versi terbaru (pasca-fix truncation).
   - رسلان tes `akar_kosakata_mandiri.html` di HP asli, konfirmasi tampilan oke.

2. **(Opsional, kalau diminta) Fitur "Sufiks/Prefiks Produktif"** — poin 2 dari peta 5 lapisan morfologi (lihat v22 A.2), belum dikerjakan sama sekali.

3. **(Opsional, kalau diminta) Fitur "Pola Pembentukan Kata Majemuk"** — poin 5 peta 5 lapisan, paling kompleks, belum ada rancangan teknis.

4. **(Opsional, prioritas rendah)** Accordion `kamus-nuance.js` untuk 1 kata → >1 pasangan — lihat catatan A.1, kemungkinan tidak diperlukan lagi karena desain pipeline sudah mencegah overlap kata.

5. Bersihkan file-file sisa pipeline yang sudah tidak relevan di `C:\mandarin_app\` (daftar lengkap di A.3) kalau رسلان belum sempat.

6. Lanjutkan pola living-doc + changelog terpisah.

---

## F. Riwayat Sesi (changelog)

**Sesi ini (v23):** **Kurasi besar-besaran `nuance_pairs.json` dari 15 → 1.291 pasangan**, menuntaskan pekerjaan yang direncanakan di v22 Bagian E poin 1. Ringkasan:
1. Diagnosis awal: fitur "Beda dengan Kata Mirip" ternyata belum pernah punya UI terpasang (`kamus-nuance.js` sudah ada dari v20/v21 tapi belum dites end-to-end) — dikonfirmasi kode sudah lengkap (script tag, HTML markup, CSS), masalah nyatanya baru muncul belakangan (insiden JSON rusak, lihat poin 4).
2. Membangun pipeline 2-jalur: `generate_next_batch.py` (Daftar B-H, otomatis penuh) dan `import_daftarA_batch.py` (Daftar A, hybrid AI eksternal + validasi Claude) — ide hybrid ini diusulkan رسلان sendiri, terbukti jauh lebih efisien daripada rencana awal Claude mengerjakan semua manual di chat.
3. Existence-check awal cuma cek `app_words.json`, ternyata membuang 555+121 kandidat valid yang sebenarnya ada di `cidict_index.json` (kosakata di luar cakupan HSK) — diperbaiki, kedua script di-upgrade dukung fallback cidict.
4. **Insiden**: رسلان sempat manual-paste JSON tanpa koma pemisah → `nuance_pairs.json` rusak total, fitur mati untuk semua kata. Diperbaiki, لalu SEMUA proses selanjutnya otomatis lewat script (tidak ada lagi copy-paste manual).
5. Kedua jalur pipeline dijalankan sampai habis: Daftar B-H **"Tidak ada kandidat baru yang tersisa"**, Daftar A **560/560 (100%)**.
6. QA pasca-kurasi: `audit_quality.py` + `check_file_sizes.py` dibuat, dijalankan رسلان. Ditemukan 5 pasangan dengan bug `words` typo dari data sumber LAMA (bukan dari pipeline sesi ini) — diperbaiki/dihapus lewat `fix_duplicate_words_bug.py`. Ukuran file dikonfirmasi aman (2,1 MB). Sampel 40 pasangan ditinjau Claude — kualitas linguistik bagus.
7. Hasil akhir terkonfirmasi رسلان langsung di app: panel "🆚 Beda dengan Kata Mirip" di Kamus dan game "🎯 Pilih yang Tepat" (2.558 soal) berjalan normal.
8. Checkpoint dibuat sebelum kurasi besar dimulai (`checkpoint_20260805_104411.zip`).

**Sebelumnya (lihat BLUEPRINT v22, v21, v20, v19 & v18 utk detail lengkap):** v22 — pengumpulan 2.891 kandidat mentah near-synonym (Daftar A-H), fitur "Akar Kosakata" digabung dari sesi terpisah. v21 — 15 pasangan nuance resmi, fitur Flashcard "Pilih yang Tepat" dibangun. v20 — fitur "Beda dengan Kata Mirip" dibangun dari nol (6 pasangan pertama). v19/v18 — audit sistemik 461 kata, sistem checkpoint.py, sinkronisasi glossary, modularisasi kamus.html.

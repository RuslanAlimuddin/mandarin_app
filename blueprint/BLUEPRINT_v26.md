# BLUEPRINT — Mandarin Interaktif — v26
_(Handoff document. Baca Bagian A–B dulu untuk onboarding cepat. Bagian C–E untuk detail teknis. Bagian F untuk riwayat sesi.)_

---

## A. Arsitektur Saat Ini (Living Doc)

**Aplikasi:** "Mandarin Interaktif" — aplikasi belajar Mandarin offline, vanilla HTML/CSS/JS, single-user (رسلان), berjalan lokal di `C:\mandarin_app\` (biasanya via `python -m http.server` / `localhost:8000`).

**Sumber data utama** (folder `data/`): `app_words.json` (~11.726 entri), `cidict_index.json` (~125.000 entri, fallback CC-CEDICT), `graded_readers.json` (123 entri), `char_etymology_id.json` (2.840 karakter), `confusion_groups.json` (53 grup), `nuance_pairs.json` (1.291 pasangan), `produktif_karakter.json` (1.389 akar karakter), `kata_majemuk_pola.json` (8.867 kata, 6 pola pembentukan kata), `grammar_hsk1.json`–`grammar_hsk9.json` (770 poin tata bahasa, dipakai `tatabahasa.html`).

**BARU sesi ini** — 2 file sumber karakter mentah proyek **Make Me a Hanzi** (skishore/makemeahanzi, lisensi Arphic Public License, offline-safe):
- `data\dictionary.txt` (9.574 karakter — field `character`/`radical`/`decomposition`/`pinyin`/`definition`/`etymology`)
- `data\graphics.txt` (9.574 karakter, BARU disimpan sesi ini — field `character`/`strokes` (array path SVG, `len(strokes)` = jumlah goresan) /`medians`). Ini PASANGAN `dictionary.txt` dari proyek sama, join lewat field `character`, urutan baris dijamin sama.
- `data\hanzi_writer_data.json` (3.034 karakter) — sub-set lama dari `graphics.txt`, dipakai fitur animasi stroke-order. `graphics.txt` sekarang jadi sumber utama yang lebih lengkap untuk kebutuhan lain (enrichment data karakter baru), `hanzi_writer_data.json` tetap dipakai khusus untuk fitur animasi (tidak perlu diganti).
- `kangxi_radical_map.json` (di root, sebaiknya dipindah ke `data\`) — tabel 214 radikal Kangxi standar (nomor → karakter kanonis), diambil dari `C:\mandarin_kamus\database\`.

**Isu berulang (masih relevan):** browser sering nge-cache file lama di `localhost:8000`. Fix: `F12 → Application → Storage → Clear site data`, kadang perlu diulang beberapa kali.

**Proyek eksternal terkait (di luar `mandarin_app`, ditemukan sesi ini):** `C:\mandarin_kamus\` dan `C:\hanyu_extract\` adalah 2 proyek Python terpisah yang dulu dipakai membangun `app_words.json` awal (lewat `build_app_words.py` di `mandarin_kamus`). Proyek-proyek ini TIDAK dihapus, tapi juga TIDAK di-maintain aktif lagi — dipakai sesi ini murni sebagai sumber referensi (`kangxi_radical_map.json`) dan pembanding logika (`build_app_words.py` dibaca untuk memahami aturan agregasi field struktural kata multi-karakter, lihat Bagian D).

---

### A.1–A.3 — Fitur Nuansa, Akar Kosakata, Pola Pembentukan Kata

Tidak berubah dari v25. Semua sudah selesai & dikonfirmasi jalan (lihat BLUEPRINT v25 untuk detail).

---

### A.4 — Peta 11 Pilar Bahasa Mandarin — DISKUSI SELESAI, IMPLEMENTASI BELUM DIMULAI

**Konteks:** رسلان upload 11 dokumen "Pilar" (kerangka bahasa Mandarin komprehensif: fonetik, angka, kata bantu bilangan, partikel & aspek, modal, struktur kalimat, konstruksi lanjutan, kata ganti & sapaan, kata sifat, pragmatik & budaya, variasi bahasa). Tujuan: peta yang menyatukan seluruh fitur app yang tersebar di 8+ halaman, supaya رسلان (bukan cuma Claude) bisa lihat gambaran utuh "pilar mana sudah ada di mana".

**Hasil pemetaan (diverifikasi langsung dari isi `grammar_hsk1-9.json`, bukan tebakan):**

| Pilar | Status | Lokasi |
|---|---|---|
| 1. Fonetik & Pelafalan | ⚪ Belum ada (cuma game "Jebakan Nada", bukan referensi konsep) | — |
| 2. Sistem Angka | 🟡 Sebagian (kosakata ada, logika sistem belum) | Kamus |
| 3. Kata Bantu Bilangan (量词) | ✅ Kuat — muncul di semua 9 level HSK | `tatabahasa.html` |
| 4. Partikel & Aspek | ✅ Kuat | `tatabahasa.html` |
| 5. Kata Kerja Modal | ✅ Ada (HSK1-5) | `tatabahasa.html` |
| 6. Struktur Kalimat & Perbandingan | ✅ Kuat | `tatabahasa.html` + `wordbuilder.html` |
| 7. Konstruksi Lanjutan (把/被/dst.) | ✅ Kuat | `tatabahasa.html` |
| 8. Kata Ganti, Penunjuk, Sapaan | 🟡 Mekanisme gramatikal ✅, sistem sapaan kekerabatan/sosial **BARU digarap sesi ini** | `tatabahasa.html` + Kamus (leksikon khusus, lihat A.5) |
| 9. Kata Sifat, Reduplikasi | ✅ Ada | `tatabahasa.html` |
| 10. Pragmatik & Ekspresi Lisan | 🟢 **BARU digarap penuh sesi ini** (kata seru, onomatope, partikel modal) | Kamus (leksikon khusus) |
| 11. Variasi Bahasa & Sejarah | 🟡 Radikal/komponen karakter ✅ kuat (Etimologi, Akar Kosakata); 成语/dialek/bahasa gaul/klasik/Zhuyin ⚪ belum |

**Keputusan desain yang disepakati** (belum diimplementasi — masih tahap konten/data, lihat A.5):
1. Halaman baru `peta-bahasa.html` — index 11 pilar, tiap sub-topik berstatus ✅/🟡/⚪ dengan tombol lompat ke lokasi persisnya.
2. Ditaruh sebagai section baru di `index.html`, idealnya tepat setelah Hero (bukan cuma 1 kartu kecil di Grid Fitur — fungsinya orientasi utama).
3. Untuk deep-link ke konten yang tidak bisa direduksi ke 1 kata (kata seru, sapaan, dst.) — **REUSE pola "Kelompok" yang SUDAH ADA** di sidebar Kamus (`openGroupPanel(type)`, sama seperti Per Radikal/Per Tema/Akar Kosakata), BUKAN membangun infrastruktur baru. Tambah 1 tipe grup baru (`type === 'khusus'`) yang membaca `index_kelompok_khusus.json` (format sama seperti `index_theme.json`).
4. `index.html` (dashboard) ternyata **sudah ketinggalan** dari `kamus.html` — nav bar & Grid Fitur belum punya link ke `tatabahasa.html`/`terjemah-bebas.html`. Perlu diperbaiki bersamaan saat nambah kartu Peta 11 Pilar.

**BELUM DIKERJAKAN:** pembuatan `peta-bahasa.html` itu sendiri, perluasan `openGroupPanel()`/`selectGroupItem()` di `kamus-cards-ui.js`, perbaikan nav `index.html`. Semua menunggu data leksikon khusus (A.5) di-apply dulu ke `app_words.json`.

---

### A.5 — Leksikon Khusus (Kata Seru, Onomatope, Sapaan, Partikel Modal) — DATA SIAP 445/470, BELUM DI-APPLY

**Tujuan:** mengisi Pilar 10 (penuh) + sebagian Pilar 8 (sistem sapaan) lewat 5 kategori leksikon baru yang sebelumnya tidak ada/minim di `app_words.json`.

**Pipeline yang dipakai (pola baku baru, kemungkinan dipakai ulang untuk leksikon lain di masa depan):**

1. **Generate via AI eksternal** — 5 prompt terpisah (lihat riwayat chat / `prompt_leksikon_khusus.md`), tiap prompt targetkan 1 kategori dengan skema JSON persis field `app_words.json` (field struktural sengaja dikosongkan `null` di tahap ini, field tambahan spesifik kategori seperti `pihak`/`generasi`/`jenis`/`formalitas`/`sumber_bunyi`/`register` ditambahkan untuk kebutuhan pengelompokan nanti).
2. **Audit** (`audit_leksikon_khusus.py`) — perbaiki sintaks JSON (AI sering lupa koma antar-objek), dedup persis, normalisasi kode `pos` menyimpang (`pron`→`r`), tandai (bukan hapus) entri dialek/di luar cakupan lewat field `_flag`.
3. **Enrichment field struktural** (`enrich_leksikon_khusus.py`, TAHAP 2, lihat Bagian D untuk arsitektur lengkap) — isi `radical`/`radical_number`/`stroke_count`/`structure`/`components`/`char_type`/`bopomofo` lewat strategi 2 lapis (Lapis 1: lookup dari 1.572 karakter tunggal yang sudah ada di `app_words.json`; Lapis 2: `dictionary.txt`+`graphics.txt`+`kangxi_radical_map.json`).
4. **Diagnosis iteratif** (`diagnose_missing_chars.py`, `diagnose_remaining_gaps.py`) — dipakai berulang untuk mempersempit gap dari 197/470 (42%) di percobaan pertama sampai **445/470 (95%)** di percobaan terakhir.

**Hasil final per kategori:**

| Kategori | Total | Lengkap | Belum lengkap |
|---|---|---|---|
| Kata Seru (interjeksi) | 83 | 79 | 4 |
| Onomatope | 61 | 59 | 2 |
| Sapaan Keluarga | 141 | 133 | 8 |
| Sapaan Sosial & Hormat | 97 | 88 | 9 |
| Partikel Modal (语气词) | 88 | 86 | 2 |
| **TOTAL** | **470** | **445 (95%)** | **25 (5%)** |

**25 entri sisa — SEMUA sudah teridentifikasi presisi penyebabnya, TIDAK ada lagi yang misteri:**
- Mayoritas: karakter pertama mengandung radikal **ambigu** (`月` bisa "bulan"/radikal 74 ATAU varian "daging"/radikal 130; `阝` bisa "阜"/radikal 170 (kiri) ATAU "邑"/radikal 163 (kanan)) — SENGAJA dibiarkan kosong + ditandai `_missing_fields`, bukan ditebak, karena risiko salah 50/50 kalau dipaksa.
- `唻` (partikel_modal) — 1 karakter yang benar-benar tidak ada di `dictionary.txt` maupun `graphics.txt` (kemungkinan varian sangat langka/tidak standar).
- `呣` (ḿ, kata seru) — pinyin dengan konsonan bersuku (di luar pola pinyin standar yang ditangani algoritma bopomofo).

**BELUM DIKERJAKAN (prioritas sesi berikutnya, lihat Bagian E):**
1. Keputusan untuk 25 entri sisa (isi manual satu-satu vs biarkan kosong sebagian vs exclude dari data).
2. Apply 470 entri ke `app_words.json` (dengan `hsk: null`, mengikuti pola `nuance_pairs.json`/kata majemuk sebelumnya) + buang field tambahan kategori-spesifik (`pihak`/`generasi`/dst.) dari record utama.
3. Bangun `index_kelompok_khusus.json` dari field tambahan yang dibuang di langkah 2 (dipakai untuk grup baru di sidebar Kamus, lihat A.4 poin 3).
4. Baru lanjut ke implementasi UI (A.4).

---

## B. Status Kualitas Data

Tidak berubah dari v25 untuk `nuance_pairs.json`, `kata_majemuk_pola.json`, `graded_readers.json`, `produktif_karakter.json`.

**BARU:** 470 entri leksikon khusus (lihat A.5) — kualitas semantik (arti/contoh kalimat) sudah di-generate AI eksternal dan LOLOS audit sintaks+dedup+normalisasi `pos`, TAPI **belum pernah di-sample-check manual oleh رسلان** untuk akurasi makna/kealamian bahasa (beda dengan field struktural yang sudah divalidasi ketat lewat self-test otomatis). Disarankan sample-check ringan sebelum apply final, terutama untuk kategori Sapaan Keluarga (paling rumit secara sistem kekerabatan) dan Partikel Modal (paling rawan nuansa halus).

---

## C. Script/File Sesi Ini (v26)

**Baru dibuat (disimpan permanen, jadi "alat baku" seperti `checkpoint.py` — sebaiknya dipindah ke folder `py\`):**
- `enrich_leksikon_khusus.py` — TAHAP 2 enrichment field struktural. **Ini alat umum, bukan sekali pakai** — bisa dipakai ulang kapan pun ada kosakata baru yang butuh field struktural diisi (misal nanti untuk 成语 di Pilar 11).
- `audit_leksikon_khusus.py` — audit sintaks+dedup+normalisasi untuk output AI eksternal berformat mirip.
- `diagnose_missing_chars.py`, `diagnose_remaining_gaps.py`, `find_structural_source_v2.py` — alat diagnosis, prioritas lebih rendah untuk disimpan tapi tidak ada ruginya.
- `inspect_app_words_schema.py`, `inspect_hanzi_sources.py`, `find_structural_source.py` — alat intip satu-kali-pakai dari sesi ini, boleh dibuang atau disimpan di `py\` untuk referensi.

**File data baru (disimpan permanen di `data\`):**
- `graphics.txt` (30 MB, dari GitHub skishore/makemeahanzi) — DIKONFIRMASI رسلان sudah simpan.
- `kangxi_radical_map.json` — perlu dipindah dari root ke `data\` biar konsisten.
- `stroke_supplement_58chars.json` — sudah agak redundan sejak `graphics.txt` disimpan penuh, tapi tidak masalah tetap disimpan.

**File staging (belum final, di folder `staging\`, BELUM di-apply ke `app_words.json`):**
`kata_seru_enriched.json`, `onomatope_enriched.json`, `sapaan_keluarga_enriched.json`, `sapaan_sosial_enriched.json`, `partikel_modal_enriched.json` — total 470 entri, 445 siap pakai.

**Prompt eksternal (referensi, kalau perlu generate ulang/kategori baru serupa):** `prompt_leksikon_khusus.md` — 5 prompt final yang dipakai untuk generate leksikon khusus ini.

---

## D. Metodologi

### D.1 — Arsitektur field struktural karakter (BARU, penting untuk sesi berikutnya)

**Field struktural itu computed PER-KARAKTER, ditempel ke level kata dengan aturan agregasi tetap** (diverifikasi langsung dari `build_app_words.py`, proyek `mandarin_kamus`, dan dikonfirmasi cocok 100% dengan data asli lewat contoh `好`/`无法`):
- `stroke_count` = SUM stroke_count tiap karakter dalam kata
- `structure` = structure karakter PERTAMA saja (bukan tata letak seluruh kata)
- `components` = UNION (dedup, urutan dipertahankan) dari komponen dekomposisi tiap karakter
- `char_type` = `'compound'` otomatis kalau kata >1 karakter
- `radical`/`radical_number` = dari karakter PERTAMA saja
- `bopomofo` = bopomofo tiap karakter disambung spasi

**2 radikal AMBIGU yang tidak boleh ditebak:** `月` (bulan/radikal 74 ATAU varian daging/radikal 130) dan `阝` (阜/radikal 170 di kiri ATAU 邑/radikal 163 di kanan). Kalau ketemu, biarkan `radical_number` kosong + tandai — JANGAN menebak 50/50.

**Sumber data karakter:** `dictionary.txt` (radikal mentah + `decomposition` sebagai IDS string, mis. `⿰女子`) dan `graphics.txt` (goresan, lewat `len(strokes)`) itu SEPASANG dari proyek sama (Make Me a Hanzi), join lewat field `character`. `kangxi_radical_map.json` dipakai buat translate radikal mentah (kadang berupa varian glyph seperti `氵`/`讠`/`亻`/`⺮`/`罒`) ke nomor radikal Kangxi baku — tabel padanan varian→kanonis WAJIB terus di-perluas kalau ketemu radikal baru yang belum tercakup (lihat `VARIANT_TO_KANGXI` di `enrich_leksikon_khusus.py`).

**Konversi pinyin→bopomofo itu deterministik** (bukan tebakan) — bisa dihitung langsung dari field `pinyin` tiap entri, TIDAK perlu lookup per-karakter. 2 jebakan yang sudah ditemukan & diperbaiki:
- Kombinasi `n`/`l` + `ü` (mis. 女=nǚ, 律=lǜ) — banyak tabel referensi cuma catat `j`/`q`/`x`/`y` bisa diikuti `ü`, padahal `n`/`l` juga bisa.
- Tanda kutip (`'`) sebagai pemisah suku kata sebelum suku kata berawalan vokal (mis. `nǚ'ér`) — harus diperlakukan sama seperti spasi.
- AI eksternal TIDAK KONSISTEN menulis pinyin kata multi-karakter (kadang pakai spasi antar suku kata, kadang digabung tanpa spasi) — script enrichment perlu coba pemisahan spasi dulu, baru fallback ke segmentasi otomatis (backtracking "potongan terpanjang dulu", dibatasi tepat sejumlah karakter hanzi kata itu) kalau gagal.

### D.2 — Pola kerja diagnosis bertahap (dikonfirmasi ulang efektif sesi ini)

Pola dari sesi-sesi sebelumnya (cek CSS yang ADA sebelum desain, minta HTML asli sebelum edit markup) **tetap berlaku**, plus 1 pola baru yang terbukti sangat efektif sesi ini:

**Untuk data yang sudah lama tidak disentuh (script/sumber data dari fase awal proyek), JANGAN asumsikan hilang — cari dulu secara sistematis sebelum bangun ulang dari nol.** Urutan pencarian yang terbukti efektif: (1) folder proyek aktif, (2) folder proyek terkait di luar folder aktif (disebut di komentar/path import script lain), (3) arsip backup/checkpoint. Baru kalau semua nihil, bangun dari sumber primer (dalam kasus ini: GitHub proyek open-source aslinya).

**Validasi otomatis (self-test) WAJIB untuk logika konversi/perhitungan yang rumit** (bopomofo, radikal, dll) — bukan cuma percaya visual sekali lihat. Pola: tanam 2-3 kasus uji dengan jawaban yang SUDAH DIKETAHUI BENAR (dari data asli yang sudah tervalidasi produksi) langsung di dalam script, jalankan otomatis tiap kali script dipanggil, STOP total kalau gagal (jangan lanjut proses ratusan entri dengan logika yang belum terbukti benar).

---

## E. Prioritas Tugas Berikutnya

1. **(Prioritas utama)** Putuskan nasib 25 entri leksikon khusus yang belum lengkap (lihat A.5) — isi manual, biarkan sebagian kosong, atau exclude.
2. **(Prioritas utama)** Apply 470 entri ke `app_words.json` (dengan checkpoint backup dulu sesuai kebiasaan), buang field tambahan kategori-spesifik dari record utama.
3. **(Prioritas utama)** Bangun `index_kelompok_khusus.json` dari field tambahan (pihak/generasi/jenis/formalitas/sumber_bunyi/register) yang dibuang di langkah 2.
4. Perluas `selectGroupItem()`/`openGroupPanel()` di `kamus-cards-ui.js` + sidebar `kamus.html` untuk grup baru "Kelompok Khusus".
5. Bangun `peta-bahasa.html` (lihat A.4 untuk desain yang sudah disepakati).
6. Perbaiki `index.html`: tambah kartu Peta 11 Pilar + perbaiki nav yang ketinggalan (belum ada link `tatabahasa.html`/`terjemah-bebas.html`).
7. **(Setelah 1-6 selesai)** Lanjut isi konten Pilar yang masih ⚪: Pilar 1 (Fonetik) → sisa Pilar 8 (kalau ada) → Pilar 11 (成语, dialek, bahasa gaul, dll — pakai pipeline yang sama seperti A.5, sudah terbukti jalan).
8. **(Opsional, prioritas rendah, carry-over dari v24-v25)** Verifikasi lanjutan ~1.700 kata 动宾式/补充式 di `kata_majemuk_pola.json`; skema kata 3+ karakter.
9. **(Housekeeping kecil)** Pindahkan `kangxi_radical_map.json` dari root ke `data\`; pindahkan script-script baru sesi ini ke folder `py\`.

---

## F. Riwayat Sesi (changelog)

**Sesi ini (v26):** Dua alur kerja besar — (1) diskusi mendalam pemetaan 11 Pilar bahasa Mandarin terhadap app existing, (2) pipeline lengkap generate+audit+enrich 470 entri leksikon khusus baru. Ringkasan:

1. **Pemetaan 11 Pilar**: رسلان upload 11 dokumen pilar, Claude cross-reference terhadap isi app (termasuk baca langsung 770 poin `grammar_hsk1-9.json`, bukan tebakan) — hasilnya Pilar 3-9 ternyata sudah kuat, celah nyata cuma di Pilar 1 (fonetik), sebagian Pilar 8 (sapaan), Pilar 10 (pragmatik, kosong total), dan sebagian Pilar 11 (成语/dialek/gaul).
2. **Desain infrastruktur disepakati**: `peta-bahasa.html` sebagai index navigasi, REUSE pola "Kelompok" sidebar Kamus yang sudah ada (bukan bangun baru) untuk kata-kata yang tidak bisa direduksi ke 1 entri kamus biasa.
3. **5 prompt leksikon khusus disusun** (kata seru, onomatope, sapaan keluarga, sapaan sosial+hormat, partikel modal 语气词 — kategori terakhir ini BARU ditemukan lewat pengecekan skema `pos` yang ternyata sudah punya kode `'y'` belum terpakai). Direvisi 1× setelah رسلان upload riset tambahan dari AI lain (diperdalam Onomatope & Sapaan Keluarga, bukan bikin kategori baru — kecuali Partikel Modal yang memang layak jadi prompt ke-5 tersendiri).
4. **Generate + audit**: AI eksternal over-generate jauh dari target (kata seru 30-35→83 realisasi, dll — cuma Onomatope yang pas target), ada bug sintaks JSON (koma hilang) di 4/5 file, ada duplikat persis, ada kode `pos` menyimpang (`pron`), ada partikel dialek nyelip di Partikel Modal — semua diaudit & didokumentasikan, رسلان putuskan pertahankan semua data (termasuk dialek, ditandai `_flag` bukan dihapus) dan masukkan makian ringan dengan tag `register: kasar`.
5. **Pencarian sumber field struktural**: script lama untuk membangun field struktural (radikal/goresan/dst.) ternyata ada di proyek eksternal `C:\mandarin_kamus\` (`build_app_words.py`), tapi scriptnya cuma MEWARISI field dari sumber lebih hulu lagi (tidak menghitung sendiri) — jadi pendekatan diubah ke Lapis 1 (lookup dari `app_words.json` yang sudah ada) + Lapis 2 (`dictionary.txt`).
6. **Iterasi enrichment 4 putaran**: 217→324→412→445 dari 470 entri lengkap, tiap putaran nemuin & benerin bug spesifik (bopomofo Lapis 2 selalu kosong by design → dihitung dari pinyin langsung; pinyin tanpa spasi untuk kata panjang → segmentasi otomatis; radikal ambigu `阝`/`月` → sengaja dikosongkan bukan ditebak; kombinasi `n`/`l`+`ü` dan tanda kutip pemisah suku kata → diperbaiki di algoritma bopomofo).
7. **`graphics.txt` (pasangan `dictionary.txt`) ditemukan & diunduh dari GitHub resmi proyek Make Me a Hanzi** untuk menutup gap 58 karakter yang tidak ada di `hanzi_writer_data.json` lokal (yang cuma sub-set 3.034 dari total 9.574) — رسلان sudah simpan permanen di `data\`.
8. Sesi ditutup di 445/470 (95%) entri leksikon khusus siap-pakai, BLUEPRINT v26 ini menandai titik berhenti — langkah apply ke `app_words.json` & implementasi UI (`peta-bahasa.html`, grup Kamus baru) BELUM dikerjakan, jadi prioritas utama sesi berikutnya (lihat Bagian E).

**Sebelumnya (lihat BLUEPRINT v25 dan seterusnya untuk detail lengkap):** v25 — UI lengkap fitur Pola Pembentukan Kata Majemuk. v24 — klasifikasi 8.867 kata ke 6 pola. v23 — kurasi `nuance_pairs.json` ke 1.291 pasangan. v22 dan sebelumnya — lihat riwayat blueprint lama.

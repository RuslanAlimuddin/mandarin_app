# BLUEPRINT PROYEK — Mandarin Interaktif
**Versi:** 4.0
**Tanggal terakhir diperbarui:** Juli 2026
**Status:** Sesi A, B, & C SELESAI — Lanjutan: wb_ref_word + UI koleksi tersimpan Word Builder

---

## 1. GAMBARAN PROYEK

Aplikasi web lokal untuk belajar Bahasa Mandarin. Dijalankan via `python -m http.server 8000` di folder `C:\mandarin_app`. Terdiri dari beberapa halaman HTML yang berbagi data JSON dan stylesheet bersama.

**Stack:** HTML + CSS + Vanilla JS (tidak ada framework). Tidak ada build step. Semua file langsung dijalankan di browser. **Prinsip arsitektur:** HTML murni struktur, CSS terpisah, JS logika, dan **semua data (termasuk kosakata dan konten pembelajaran) berasal dari file `.json`** — tidak ada data besar yang di-hardcode di JS, mengikuti pola file turunan hasil generate dari `app_words.json` via script Python.

---

## 2. STRUKTUR FOLDER

```
C:\mandarin_app\
├── index.html
├── kamus.html                     ← gabungan PART 1-5
├── flashcard.html                 ← gabungan PART 1-4
├── wordbuilder.html                ← gabungan PART 1-4 (SELESAI Sesi C)
├── gabung_kamus.py                 ← script penggabung PART → HTML
├── gabung_flashcard.py             ← script penggabung PART → HTML
├── gabung_wordbuilder.py           ← script penggabung PART → HTML (BARU)
├── generate_wordbuilder_pools.py   ← generate data/wb_pools.json dari app_words.json (BARU)
├── wb_overrides.json               ← koreksi manual kata bermasalah di wb_pools (BARU)
├── combine_explanations.py         ← gabung 7 part JSON penjelasan pola (BARU)
├── pattern_explanations_part1_dasar.json               ← (BARU, disimpan di root sebelum digabung)
├── pattern_explanations_part2_deskripsi.json           ← (BARU)
├── pattern_explanations_part3_waktu_aspek.json         ← (BARU)
├── pattern_explanations_part4_tanya.json               ← (BARU)
├── pattern_explanations_part5_majemuk_hubungan.json    ← (BARU)
├── pattern_explanations_part6_majemuk_perbandingan.json← (BARU)
├── pattern_explanations_part7_fungsi.json              ← (BARU)
│
├── shared/
│   └── style.css       ← stylesheet global (TIDAK diubah di Sesi A/B/C)
│
├── data/
│   ├── app_words.json               ← 11.470 kata HSK, sumber utama
│   ├── cidict_index.json            ← 124.966 kata Cidict
│   ├── index_theme.json             ← 157 tema (38 internal + 119 ext_)
│   ├── index_radical.json           ← index radikal
│   ├── index_phonetic.json          ← 965 komponen fonetik
│   ├── index_theme_backup.json      ← backup sebelum terjemahan label
│   ├── wb_pools.json                ← BARU: 9 pool kata Word Builder, per-HSK, digenerate dari app_words.json
│   └── pattern_explanations.json    ← BARU: penjelasan lengkap 34 pola Word Builder (hasil gabung 7 part)
│
└── parts/                      ← file kerja yang diupload ke Claude
    ├── kamus_PART_1.txt .. kamus_PART_5.txt
    ├── flashcard_PART_1.txt .. flashcard_PART_4.txt
    └── wordbuilder_PART_1.txt .. wordbuilder_PART_4.txt   ← BARU, SELESAI Sesi C
```

---

## 3. CARA KERJA FILE PARTS

Setiap halaman HTML dipecah menjadi beberapa PART `.txt` agar mudah diedit Claude (hindari token overflow). Setelah Claude selesai mengedit PART yang relevan, jalankan script gabung di PC:

```bash
python gabung_kamus.py         # → menghasilkan kamus.html
python gabung_flashcard.py     # → menghasilkan flashcard.html
python gabung_wordbuilder.py   # → menghasilkan wordbuilder.html
```

**Konvensi penting:**
- Upload hanya PART yang relevan dengan fix yang akan dikerjakan
- Claude mengedit PART, output via `present_files`, Anda download dan replace di folder `parts/`
- Laporan detail selalu disertakan sebagai `laporan_sesi_X.txt`
- Ringkasan di chat diminimalkan — detail ada di laporan
- **Data besar (kosakata, konten pembelajaran) TIDAK di-hardcode di PART JS** — selalu berupa file `.json` terpisah di `data/`, di-generate via script Python dari `app_words.json` kalau memungkinkan, lalu di-`fetch()` saat runtime

---

## 4. FORMAT app_words.json (REFERENSI)

Setiap entry kata memiliki field berikut (semua 11.470 kata punya semua field ini):

```json
{
  "id": "...",
  "simplified": "好",
  "traditional": "好",
  "pinyin": "hǎo",
  "pinyin_numeric": "hao3",
  "bopomofo": "ㄏㄠˇ",
  "hsk": 1,
  "hsk2": "...",
  "frequency": 123,
  "pos": ["adj"],
  "pos_id": ["kata sifat"],
  "meanings_id": ["baik", "bagus"],
  "meanings_en": ["good", "well"],
  "radical": "女",
  "radical_number": 38,
  "stroke_count": 6,
  "structure": "left-right",
  "components": ["女", "子"],
  "char_type": "phono-semantic",
  "themes": ["keluarga", "ext_greetings"],
  "synonyms": ["棒"],
  "antonyms": ["坏"]
}
```

**CATATAN PENTING (ditemukan di Sesi C):**
- Field `pos`, `pos_id`, dan `themes` **berupa list**, bukan string tunggal — satu kata bisa punya beberapa tag sekaligus (mis. `["v","n"]`). Script Python yang memproses field ini WAJIB menangani list, bukan asumsi string.
- Field `hsk` **tersimpan sebagai string** (`"1"`, bukan `1`), meski contoh di dokumentasi awal menunjukkan integer. Normalisasi tipe data diperlukan sebelum membandingkan/mem-filter berdasarkan level HSK.
- Peta tag `pos` yang relevan (ditemukan dari analisis langsung ke data):

| pos | Arti | Kegunaan |
|---|---|---|
| `v` | kata kerja | pool kata_kerja |
| `n` | kata benda | pool objek_umum |
| `a` | kata sifat | pool kata_sifat |
| `r` | kata ganti (pronomina) | pool subyek |
| `q` | kata ukuran (量词/classifier) | pool satuan |
| `t` | kata waktu | pool waktu |
| `m` | kata bilangan | pool angka |
| `f` | kata tempat | pool tempat |

- **Data quality issue:** sebagian kata (terutama karakter multi-bacaan/多音字 dan kata dengan bacaan marga/nama) punya field `pinyin`+`meanings_id[0]` yang salah pasangan (mis. 钱 muncul sebagai "marga Qian" alih-alih "uang"). Solusi: file `wb_overrides.json` menyimpan koreksi manual per kombinasi pool+hanzi, diterapkan otomatis oleh `generate_wordbuilder_pools.py`. Kalau menemukan kata aneh lain di masa depan, cukup tambah entry baru di `wb_overrides.json` dan generate ulang — tidak perlu ubah kode.

---

## 5. SESI A — KAMUS (SELESAI ✓)

**File yang diubah:** `kamus_PART_1.txt`, `kamus_PART_4.txt`, `kamus_PART_5.txt`
`kamus_PART_2.txt` tidak berubah (disertakan agar set lengkap untuk `gabung_kamus.py`).

### Fix A1 — Pencarian Pinyin Presisi Nada ✓
**File:** `kamus_PART_5.txt` → fungsi `searchPinyin()`
**Solusi:** Deteksi apakah query mengandung nada (numerik atau diakritik). Jika ya → hanya jalur match presisi, TIDAK fallback ke loose match.

### Fix A2 — Kartu Hasil 1 Baris ✓
Kartu jadi 1 baris flex: `Hanzi (64px) | Pinyin (110px) | Arti (flex-grow)`. Class CSS baru: `.result-card.result-row`.

### Fix A3 — Sort by Arti + Tombol Sort Cepat ✓
State: `STATE.cardSortKey`, `STATE.cardSortDir`. Fungsi baru: `getCardSortedResults()`, `setCardSort(key)`, `renderCardSortControls(header)`.

### Fix A4 — Drag Handle Resizable Panel Detail ✓
Element baru: `panel-resize-handle`. Fungsi baru: `setupResizeHandle()`, `applyDetailPanelWidth(px)`. Batas lebar: 280px–600px, tersimpan di `localStorage` key `mandarin_detail_width`.

---

## 6. SESI B — FLASHCARD (SELESAI ✓)

**File yang diubah:** `flashcard_PART_1.txt`, `flashcard_PART_2.txt`, `flashcard_PART_4.txt`
`flashcard_PART_3.txt` (SRS Engine) **tidak diubah sama sekali**.

Fitur yang diselesaikan: Back Card selalu tampil Hanzi (Fix B6), Sidebar Accordion Collapsible (Fix B1), Radikal semua 214 + collapse/expand (Fix B3), Tema Custom parsial (Fix B2), Filter Struktur Karakter (Fix B5a), Jebakan Nada (Fix B5b), Goresan Ekstrem (Fix B5c), Lawan Kata (Fix B5d), Komponen Fonetik (Fitur B4).

**CATATAN TEKNIS PENTING — buildDeckQueue:** `flashcard_PART_4.txt` mendefinisikan ulang `buildDeckQueue` yang sama dengan `flashcard_PART_3.txt` (override otomatis karena digabung jadi 1 file HTML). WAJIB berisi logika deck LAMA secara inline — TIDAK BOLEH memanggil versi PART_3 secara rekursif.

---

## 7. SESI C — WORD BUILDER (SELESAI ✓)

### Temuan awal sesi
`wordbuilder.html` ternyata **BUKAN skeleton kosong** seperti dicatat di blueprint v3 — sudah ada 34 pola kalimat lengkap (17 tunggal, 5 majemuk, di-breakdown jadi 3 tab: Tunggal/Majemuk/Fungsi) dengan engine render slot, output builder, dan fitur simpan-ke-koleksi yang sudah berfungsi. Yang benar-benar kosong hanya: (1) sumber kata di `WORD_POOLS` yang di-hardcode manual, dan (2) penjelasan pola yang masih sangat singkat (1 kalimat `tip`).

### Bagian 1 — Word Pools Dinamis ✓
**Masalah:** `WORD_POOLS` di `wordbuilder_PART_3.txt` berisi kosakata manual, bukan dari `app_words.json` (11.470 kata).

**Solusi:**
- `generate_wordbuilder_pools.py` — baca `app_words.json`, filter per pool berdasarkan tag `pos` (lihat tabel di Bagian 4), batasi maks 15 kata per level HSK per pool (kecuali `angka`, tidak dibatasi), urutkan berdasarkan `frequency`.
- **Ditemukan & diperbaiki 2 kelas masalah kualitas data:**
  1. **Polusi bacaan marga/nama** — karakter multi-bacaan (说/要/上/钱/水 dll.) kadang mengambil bacaan marga/langka alih-alih bacaan umum. Solusi: deteksi otomatis pinyin berhuruf kapital (indikasi bacaan marga) → buang, kecuali untuk pool `tempat` dengan tema `negara_budaya` (中国, dll. memang sah berpinyin kapital). Plus override manual untuk kasus lolos deteksi (karakter dengan bacaan salah tapi tetap huruf kecil, mis. 说 seharusnya "shuō" bukan "shuì").
  2. **Gloss teknis kamus** — sebagian `meanings_id[0]` berupa catatan "varian dari X" (self-referential, tidak berguna) atau diawali "(bentuk terikat)". Solusi: logika `primary_meaning()` otomatis skip gloss varian dan strip prefix bentuk-terikat.
- **`wb_overrides.json`** — 94 koreksi manual + 13 drop, diterapkan otomatis oleh script generate. Kalau menemukan kata aneh lain nanti, tinggal tambah 1 baris di sini dan generate ulang.
- **Hasil akhir:** 9 pool (`subyek`, `kata_kerja`, `objek_umum`, `kata_sifat`, `tempat`, `waktu`, `angka`, `satuan`, `identitas`), tersimpan di `data/wb_pools.json`, masing-masing entry berformat `{cn, py, id, hsk}`.
- **UI filter HSK** — checkbox HSK1-7 + toggle "Semua"/"Kosongkan" di sidebar (di atas tab kategori pola), tersimpan di `localStorage` key `mandarin_wb_hsk`. Kalau pool kosong/sedikit akibat filter, muncul pesan hint di bawah dropdown (bukan disable, bukan fallback diam-diam).

**File yang diubah:** `wordbuilder_PART_1.txt` (CSS filter HSK), `wordbuilder_PART_2.txt` (HTML filter HSK), `wordbuilder_PART_3.txt` (hapus `WORD_POOLS` hardcode, 34 pola `PATTERNS` TIDAK diubah), `wordbuilder_PART_4.txt` (`fetch('data/wb_pools.json')`, `getFilteredPool()`, `toggleHskLevel()`, dll.)

### Bagian 2 — Penjelasan Pola Diperluas ✓
**Masalah:** Setiap pola cuma punya 1 kalimat `tip` singkat — tidak cukup untuk pelajar Indonesia yang sangat awam.

**Solusi:** Setiap dari 34 pola sekarang punya 6 bagian penjelasan lengkap, disimpan di `data/pattern_explanations.json` (bukan hardcode di JS):
1. `penjelasan_dasar` — kenapa pola ini begini, kapan dipakai
2. `perbandingan_indonesia` — persamaan/perbedaan dengan logika bahasa Indonesia
3. `kapan_tidak_boleh` — batasan pemakaian pola
4. `kesalahan_umum` — pasangan salah/benar + penjelasan (array)
5. `contoh_tambahan` — 2-4 kalimat contoh baru di luar `examples` bawaan
6. `pola_terkait` — pola lain yang berhubungan + alasan, ditampilkan sebagai chip yang bisa diklik langsung (`goToPattern()`, otomatis pindah tab kalau perlu)

**Proses:** konten disusun oleh Claude sendiri (pengetahuan gramatika + verifikasi, bukan scraping/copy-paste), dibantu referensi dokumen `struktur_kata.txt` yang diupload user. Dikerjakan 7 part terpisah (per grup sidebar: Dasar, Deskripsi, Waktu&Aspek, Tanya, Majemuk-Hubungan, Majemuk-Perbandingan, Fungsi) lalu digabung via `combine_explanations.py`.

**File yang diubah:** `wordbuilder_PART_1.txt` (CSS section penjelasan), `wordbuilder_PART_2.txt` (HTML 6 bagian), `wordbuilder_PART_4.txt` (`fetch('data/pattern_explanations.json')`, `renderExplanation()`, `goToPattern()`). `wordbuilder_PART_3.txt` TIDAK diubah lagi di bagian ini (definisi 34 pola tetap sama dari Bagian 1).

### Yang BELUM dikerjakan di Sesi C (lanjut ke sesi berikutnya)
- **`wb_ref_word` belum diimplementasikan** — tombol "📝 Kirim ke Word Builder" di flashcard sudah menyimpan ke `localStorage`, tapi `wordbuilder.html` belum membaca key ini sama sekali.
- **Tidak ada UI untuk melihat/mengelola koleksi tersimpan** (`mandarin_wb_saved`) — data tersimpan tapi tidak ada tempat untuk melihat/menghapusnya di dalam Word Builder.
- **Audio pinyin** — disepakati ditunda, akan dikerjakan di sesi lain.

---

## 8. SRS ENGINE (flashcard_PART_3 — JANGAN DIUBAH TANPA ALASAN KUAT)

**Storage key:** `mandarin_srs_v1`
**Format per kata:** `{ interval, ease, due, reps, lapses }`
**Algoritma:** SM-2 disederhanakan
**Rating:** 0=Lagi, 1=Sulit, 2=Baik, 3=Mudah
**Wrong cards key:** `mandarin_wrong_v1`

---

## 9. DATA SCRIPTS (SEMUA SELESAI ✓)

### generate_phonetic_index.py ✓
Input: `app_words.json` (field `components`). Output: `data/index_phonetic.json`. Filter: komponen ≥2 kata. Hasil: 965 komponen dari 1.123 unik.

### translate_theme_labels.py ✓
Input/Output: `data/index_theme.json` (in-place). Backup: `data/index_theme_backup.json`. Hasil: 119/119 label `ext_` diterjemahkan.

### generate_wordbuilder_pools.py ✓ (BARU, Sesi C)
Input: `app_words.json` + `wb_overrides.json`. Output: `data/wb_pools.json`. Lihat detail di Bagian 7.

### combine_explanations.py ✓ (BARU, Sesi C)
Input: 7 file `pattern_explanations_part*.json`. Output: `data/pattern_explanations.json`. Validasi otomatis: cek semua 34 pola punya 6 field lengkap, cek tidak ada key duplikat antar part.

---

## 10. FITUR INTEGRASI ANTAR HALAMAN

### Kamus → Flashcard
Tombol "+ Flashcard" di panel detail kamus → `addToFlashcard()` → simpan ke `localStorage`.

### Flashcard → Word Builder
Tombol "📝 Kirim ke Word Builder" → `sendToWordBuilder()` → simpan ke `localStorage` key: `wb_ref_word`.
**BELUM SELESAI:** Sisi penerima di `wordbuilder.html` belum membaca key ini. Prioritas sesi berikutnya.

### Word Builder → (internal)
Tombol "+ Simpan ke Flashcard" di Word Builder → `addToFlashcardWB()` → simpan ke `localStorage` key `mandarin_wb_saved` (nama key agak menyesatkan — sebenarnya koleksi internal Word Builder, bukan terhubung ke flashcard.html).
**BELUM SELESAI:** Tidak ada UI untuk melihat/mengelola isi `mandarin_wb_saved`.

---

## 11. PREFERENSI & KONVENSI CODING

1. **Tidak ada framework** — vanilla JS, CSS variables dari `shared/style.css`
2. **Data besar SELALU dari `.json`**, tidak di-hardcode di JS — konvensi baru ditegaskan di Sesi C, berlaku untuk semua halaman ke depan
3. **CSS variables utama:** `--bg-card`, `--bg-card2`, `--border`, `--border-gold`, `--text-main`, `--text-dim`, `--text-muted`, `--gold`, `--gold-dim`, `--gold-bg`, `--gold-bg-hover`, `--red`, `--red-bg`, `--radius`, `--radius-lg`, `--transition`. Badge HSK: `--hsk1-text` s/d `--hsk7-text`, class `.badge-hsk.hsk-1` s/d `.hsk-7`
4. **Helper functions** kamus_PART_5: `$(id)`, `escHtml(str)`, `highlight(text, q)`, `showToast(msg, type)`, `normalizePinyin(py)`, `numericToDiacritic(py)`, `detectMode(q)`
5. **Helper functions** flashcard_PART_4: `$$(id)`, `showToast(msg, type)`, `showScreen(name)`
6. **Helper functions** wordbuilder_PART_4 (BARU): `$w(id)`, `escHtml(str)`, `showToast(msg, type)`, `getFilteredPool(poolName)`, `goToPattern(key)`
7. **localStorage keys** yang sudah dipakai — JANGAN bentrok:
   - `mandarin_srs_v1` — data SRS
   - `mandarin_wrong_v1` — set kata salah
   - `mandarin_bookmarks` — bookmark kamus
   - `mandarin_recent` — riwayat kamus
   - `mandarin_detail_width` — lebar panel detail kamus
   - `mandarin_custom_themes` — tema custom flashcard
   - `wb_ref_word` — referensi kata dari flashcard ke Word Builder (BELUM dibaca sisi penerima)
   - `mandarin_wb_saved` — koleksi kalimat tersimpan dari Word Builder (BARU, belum ada UI lihat/hapus)
   - `mandarin_wb_hsk` — filter level HSK aktif di Word Builder (BARU, Sesi C)
8. **Output selalu:** file hasil edit + `laporan_sesi_X.txt`. Ringkasan di chat minimal.
9. **Verifikasi sintaks JS** sebelum output: `node --check` (ekstrak isi `<script>` dulu kalau filenya HTML utuh). **Verifikasi JSON** dengan `python3 -c "import json; json.load(...)"` untuk setiap file data baru.
10. **Diskusi dulu** sebelum coding jika ada ambiguitas — tidak langsung coding
11. **File besar/proses panjang** — pecah jadi beberapa part kecil, kirim satu-per-satu begitu selesai (jangan tunggu semua part kelar), supaya aman dari risiko kehabisan proses sebelum sempat diunduh

---

## 12. WISHLIST / DITUNDA

| Item | Keterangan |
|---|---|
| **`wb_ref_word` di Word Builder** | Prioritas utama sesi berikutnya — baca localStorage saat load, prefill slot yang relevan |
| **UI koleksi tersimpan Word Builder** | Lihat/hapus isi `mandarin_wb_saved` dari dalam halaman |
| **Audio pinyin** | Untuk pola kalimat & kosakata — ditunda, dikerjakan di sesi lain |
| Import tema dari file JSON eksternal | Menunggu رسلان menemukan sumber data |
| Isi kata ke tema custom | Butuh UI di kamus (tombol "Tambah ke Tema") |
| Terjemahan label tema jika ada data baru | Jalankan ulang `translate_theme_labels.py` |
| Cidict search mode | Sudah ada toggle di sidebar kamus, belum dievaluasi penuh |

---

## 13. CARA MEMULAI PERCAKAPAN BARU

Upload file-file berikut ke chat baru Claude:
1. `BLUEPRINT_v4.md` (file ini)
2. PART file yang akan diedit (sesuai kebutuhan sesi)

Lalu tulis:
> "Lanjutkan proyek Mandarin Interaktif berdasarkan blueprint. Sesi berikutnya: [nama sesi]."

Claude akan membaca blueprint, memahami posisi saat ini, dan melanjutkan tanpa perlu penjelasan ulang.

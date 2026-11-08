# BLUEPRINT PROYEK — Mandarin Interaktif
**Versi:** 3.0  
**Tanggal terakhir diperbarui:** Juli 2026  
**Status:** Sesi A & B SELESAI — Lanjutan: Word Builder + fitur tambahan

---

## 1. GAMBARAN PROYEK

Aplikasi web lokal untuk belajar Bahasa Mandarin. Dijalankan via `python -m http.server 8000` di folder `C:\mandarin_app`. Terdiri dari beberapa halaman HTML yang berbagi data JSON dan stylesheet bersama.

**Stack:** HTML + CSS + Vanilla JS (tidak ada framework). Tidak ada build step. Semua file langsung dijalankan di browser.

---

## 2. STRUKTUR FOLDER

```
C:\mandarin_app\
├── index.html
├── kamus.html          ← gabungan PART 1-5
├── flashcard.html      ← gabungan PART 1-4
├── wordbuilder.html    ← belum diedit, scope berikutnya
├── gabung_kamus.py     ← script penggabung PART → HTML
├── gabung_flashcard.py ← script penggabung PART → HTML
│
├── shared/
│   └── style.css       ← stylesheet global (TIDAK diubah di Sesi A/B)
│
├── data/
│   ├── app_words.json          ← 11.470 kata HSK, sumber utama
│   ├── cidict_index.json       ← 124.966 kata Cidict
│   ├── index_theme.json        ← 157 tema (38 internal + 119 ext_)
│   ├── index_radical.json      ← index radikal
│   ├── index_phonetic.json     ← ✓ BARU dibuat (965 komponen fonetik)
│   └── index_theme_backup.json ← backup sebelum terjemahan label
│
└── parts/                      ← file kerja yang diupload ke Claude
    ├── kamus_PART_1.txt        ← <head> + CSS lokal kamus
    ├── kamus_PART_2.txt        ← HTML sidebar kiri kamus
    ├── kamus_PART_3.txt        ← HTML main panel kamus (search bar, results)
    ├── kamus_PART_4.txt        ← HTML panel detail kanan kamus
    ├── kamus_PART_5.txt        ← <script> JS kamus (semua logika)
    ├── flashcard_PART_1.txt    ← <head> + CSS lokal flashcard
    ├── flashcard_PART_2.txt    ← HTML body (navbar, sidebar, main area)
    ├── flashcard_PART_3.txt    ← <script> SRS Engine (SM-2)
    └── flashcard_PART_4.txt    ← <script> FC logic + fitur Sesi B
```

---

## 3. CARA KERJA FILE PARTS

Setiap halaman HTML dipecah menjadi beberapa PART `.txt` agar mudah diedit Claude (hindari token overflow). Setelah Claude selesai mengedit PART yang relevan, jalankan script gabung di PC:

```bash
python gabung_kamus.py       # → menghasilkan kamus.html
python gabung_flashcard.py   # → menghasilkan flashcard.html
```

**Konvensi penting:**
- Upload hanya PART yang relevan dengan fix yang akan dikerjakan
- Claude mengedit PART, output via `present_files`, Anda download dan replace di folder `parts/`
- Laporan detail selalu disertakan sebagai `laporan_sesi_X.txt`
- Ringkasan di chat diminimalkan — detail ada di laporan

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
  "pos": "adj",
  "pos_id": "kata sifat",
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

---

## 5. SESI A — KAMUS (SELESAI ✓)

**File yang diubah:** `kamus_PART_1.txt`, `kamus_PART_4.txt`, `kamus_PART_5.txt`  
`kamus_PART_2.txt` tidak berubah (disertakan agar set lengkap untuk `gabung_kamus.py`).

### Fix A1 — Pencarian Pinyin Presisi Nada ✓
**File:** `kamus_PART_5.txt` → fungsi `searchPinyin()`  
**Masalah:** Query dengan nada eksplisit (`ma1`, `má`) bocor ke hasil nada lain.  
**Solusi:** Deteksi apakah query mengandung nada (numerik atau diakritik). Jika ya → hanya jalur match presisi, TIDAK fallback ke loose match.

### Fix A2 — Kartu Hasil 1 Baris ✓
**File:** `kamus_PART_1.txt` (CSS), `kamus_PART_5.txt` → `buildResultCard()`  
**Masalah:** Kartu hasil terlalu ramai — ada badge HSK, radikal, goresan, tipe di setiap kartu.  
**Solusi:** Kartu jadi 1 baris flex: `Hanzi (64px) | Pinyin (110px) | Arti (flex-grow)`. Badge detail dipindah ke panel kanan saja. Class CSS baru: `.result-card.result-row`.

### Fix A3 — Sort by Arti + Tombol Sort Cepat ✓
**File:** `kamus_PART_1.txt` (CSS), `kamus_PART_5.txt`  
**Perubahan:**
- Mode tabel: tambah kolom "Arti" yang bisa di-sort (key: `'meaning'`)
- Mode kartu: toolbar tombol sort cepat `#card-sort-controls` dirender dinamis ke `#results-header`
- Opsi sort: Relevansi / Hanzi / Pinyin / Arti / HSK
- State: `STATE.cardSortKey`, `STATE.cardSortDir`
- Fungsi baru: `getCardSortedResults()`, `setCardSort(key)`, `renderCardSortControls(header)`

### Fix A4 — Drag Handle Resizable Panel Detail ✓
**File:** `kamus_PART_1.txt` (CSS), `kamus_PART_4.txt` (HTML handle), `kamus_PART_5.txt` (JS)  
**Perubahan:**
- Element baru: `<div class="panel-resize-handle" id="resize-handle">` disisipkan sebelum `<aside class="detail-panel">`
- Fungsi baru: `setupResizeHandle()`, `applyDetailPanelWidth(px)`
- Batas lebar: 280px–600px
- Lebar tersimpan di `localStorage` key: `mandarin_detail_width`
- Dipanggil di `DOMContentLoaded`

---

## 6. SESI B — FLASHCARD (SELESAI ✓)

**File yang diubah:** `flashcard_PART_1.txt`, `flashcard_PART_2.txt`, `flashcard_PART_4.txt`  
`flashcard_PART_3.txt` (SRS Engine) **tidak diubah sama sekali**.

### Fix B6 — Back Card Selalu Tampilkan Hanzi ✓
**File:** `flashcard_PART_4.txt` → `renderCurrentCard()`, blok "MUKA BELAKANG"  
**Masalah:** `fc-back-hanzi` disembunyikan saat mode pertanyaan = Hanzi.  
**Solusi:** Hanzi besar SELALU tampil di belakang kartu, apapun mode pertanyaan.

### Fix B1 — Sidebar Accordion Collapsible ✓
**File:** `flashcard_PART_1.txt` (CSS), `flashcard_PART_2.txt` (HTML), `flashcard_PART_4.txt` (JS)  
**CSS baru:** `.sidebar-section-header`, `.accordion-arrow`, `.sidebar-section-body.collapsed`  
**Fungsi baru:** `toggleAccordion(id)`, `ensureAccordionVisible(deckId)`  
**Default state:**
- `acc-hsk` → EXPANDED
- `acc-koleksi`, `acc-tema`, `acc-radikal`, `acc-game`, `acc-fonetik` → collapsed  

**Behavior:** Section yang berisi item aktif tidak bisa di-collapse. `selectDeck()` otomatis membuka section yang relevan.

### Fix B3 — Radikal Semua 214 + Collapse/Expand ✓
**File:** `flashcard_PART_4.txt` → `renderSidebarRadikal()`  
**Sebelum:** Hardcoded 20 radikal populer.  
**Sesudah:** Baca semua dari `FC.dataRadical`, urutkan terbanyak dulu, tampilkan 20 + tombol expand.

### Fix B2 — Tema Custom ✓ (parsial)
**File:** `flashcard_PART_4.txt`  
**Diimplementasikan:** Tombol "+ Tema Baru" → `window.prompt()` → simpan ke `localStorage` key `mandarin_custom_themes`.  
**Belum diimplementasikan:** UI untuk mengisi kata ke tema custom (ditunda — menunggu sumber data eksternal yang akan diimport).  
**Format localStorage:** `{ "custom_nama": { label: "Nama", words: [] } }`

### Fix B5a — Filter Struktur Karakter ✓
**File:** `flashcard_PART_2.txt` (HTML `#sidebar-struktur-list`), `flashcard_PART_4.txt` → `renderSidebarStruktur()`  
**Deck ID:** `struct-<encoded-struktur>`  
**Label struktur:** left-right, top-bottom, full/single, enclosed, semi-enclosed, dll.

### Fix B5b — Jebakan Nada ✓
**File:** `flashcard_PART_4.txt` → `buildToneTrapPool()`  
**Logika:** Kelompokkan kata per pinyin-tanpa-nada, ambil grup yang punya ≥2 nada berbeda.  
**Deck ID:** `tone-trap`

### Fix B5c — Goresan Ekstrem ✓
**File:** `flashcard_PART_2.txt` (HTML), `flashcard_PART_4.txt` (filter di `buildDeckQueue`)  
**Deck ID:** `stroke-easy` (1–3 goresan), `stroke-hard` (≥15 goresan)

### Fix B5d — Lawan Kata ✓
**File:** `flashcard_PART_2.txt` (HTML `#due-antonyms`), `flashcard_PART_4.txt` → `checkAntonymsData()`  
**Deck ID:** `antonyms`  
**Filter:** `w.antonyms` array tidak kosong atau truthy.

### Fitur B4 — Komponen Fonetik ✓
**File:** `flashcard_PART_2.txt` (section `acc-fonetik`), `flashcard_PART_4.txt` → `loadPhoneticData()`, `renderSidebarFonetik()`  
**Data:** `data/index_phonetic.json` — 965 komponen, format `{ "komponen": ["id1", "id2", ...] }`  
**Deck ID:** `phonetic-<encoded-komponen>`

### CATATAN TEKNIS PENTING — buildDeckQueue
`flashcard_PART_3.txt` mendefinisikan `buildDeckQueue` untuk deck standar (hsk-, bookmarks, dll).  
`flashcard_PART_4.txt` mendefinisikan ulang `buildDeckQueue` yang sama (override otomatis karena digabung jadi 1 file HTML).  
**WAJIB:** `flashcard_PART_4.txt` harus selalu berisi logika deck LAMA (hsk-, bookmarks, wrong, all-due, theme-, radical-) secara inline di fungsi `buildDeckQueue`-nya — TIDAK BOLEH memanggil versi PART_3 secara rekursif (menyebabkan stack overflow).

---

## 7. SRS ENGINE (PART_3 — JANGAN DIUBAH TANPA ALASAN KUAT)

**Storage key:** `mandarin_srs_v1`  
**Format per kata:** `{ interval, ease, due, reps, lapses }`  
**Algoritma:** SM-2 disederhanakan  
**Rating:** 0=Lagi, 1=Sulit, 2=Baik, 3=Mudah  
**Wrong cards key:** `mandarin_wrong_v1`

---

## 8. DATA SCRIPTS (SELESAI ✓)

### generate_phonetic_index.py ✓
- Input: `data/app_words.json` (field `components`, array karakter)
- Output: `data/index_phonetic.json`
- Filter: komponen yang muncul di ≥2 kata
- Hasil: 965 komponen dari 1.123 unik

### translate_theme_labels.py ✓
- Input/Output: `data/index_theme.json` (in-place)
- Backup: `data/index_theme_backup.json`
- Hasil: 119/119 label `ext_` berhasil diterjemahkan ke Bahasa Indonesia

---

## 9. FITUR INTEGRASI ANTAR HALAMAN

### Kamus → Flashcard
- Tombol "+ Flashcard" di panel detail kamus → `addToFlashcard()` → simpan ke `localStorage`

### Flashcard → Word Builder
- Tombol "📝 Kirim ke Word Builder" → `sendToWordBuilder()` → simpan ke `localStorage` key: `wb_ref_word`
- **CATATAN:** Sisi penerima di `wordbuilder.html` belum membaca key ini. Harus diimplementasikan di sesi Word Builder.

---

## 10. PREFERENSI & KONVENSI CODING

1. **Tidak ada framework** — vanilla JS, CSS variables dari `shared/style.css`
2. **CSS variables utama** (dari style.css, gunakan ini di CSS lokal):
   - `--bg-card`, `--bg-card2`, `--border`, `--border-gold`
   - `--text-main`, `--text-dim`, `--text-muted`
   - `--gold`, `--gold-dim`, `--gold-bg`, `--gold-bg-hover`
   - `--red`, `--red-bg`, `--radius`, `--radius-lg`, `--transition`
   - Badge HSK: `--hsk1-text` s/d `--hsk7-text`, class `.badge-hsk.hsk-1` s/d `.hsk-7`
3. **Helper functions** yang sudah ada di kamus_PART_5:
   - `$(id)` → `document.getElementById`
   - `escHtml(str)`, `highlight(text, q)`, `showToast(msg, type)`
   - `normalizePinyin(py)`, `numericToDiacritic(py)`, `detectMode(q)`
4. **Helper functions** di flashcard_PART_4:
   - `$$(id)` → `document.getElementById`
   - `showToast(msg, type)`, `showScreen(name)`
5. **localStorage keys** yang sudah dipakai — JANGAN bentrok:
   - `mandarin_srs_v1` — data SRS
   - `mandarin_wrong_v1` — set kata salah
   - `mandarin_bookmarks` — bookmark kamus
   - `mandarin_recent` — riwayat kamus
   - `mandarin_detail_width` — lebar panel detail kamus
   - `mandarin_custom_themes` — tema custom flashcard
   - `wb_ref_word` — referensi kata dari flashcard ke Word Builder
6. **Output selalu:** file hasil edit + `laporan_sesi_X.txt`. Ringkasan di chat minimal.
7. **Verifikasi sintaks JS** sebelum output: `node --check file.js`
8. **Diskusi dulu** sebelum coding jika ada ambiguitas — tidak langsung coding

---

## 11. SESI BERIKUTNYA — WORD BUILDER

### Status saat ini
`wordbuilder.html` belum diedit sama sekali. Tidak ada error di console (F12) berdasarkan inspeksi awal.

### Yang sudah tersedia untuk Word Builder
- Data kata lengkap di `app_words.json`
- Integrasi masuk dari flashcard via `localStorage` key `wb_ref_word`
- CSS variables dan komponen UI (sidebar, card, badge) dari `shared/style.css`

### Langkah memulai sesi Word Builder
1. Upload `wordbuilder.html` (atau dalam bentuk PART jika sudah dipecah)
2. Upload blueprint ini
3. Inspeksi fitur yang sudah ada vs yang perlu ditambah
4. Diskusi → setujui scope → coding

---

## 12. WISHLIST / DITUNDA

| Item | Keterangan |
|---|---|
| Import tema dari file JSON eksternal | Menunggu رسلان menemukan sumber data |
| Isi kata ke tema custom | Butuh UI di kamus (tombol "Tambah ke Tema") |
| Terjemahan label tema jika ada data baru | Jalankan ulang `translate_theme_labels.py` |
| Word Builder | Scope sesi berikutnya |
| Cidict search mode | Sudah ada toggle di sidebar kamus, belum dievaluasi penuh |

---

## 13. CARA MEMULAI PERCAKAPAN BARU

Upload file-file berikut ke chat baru Claude:
1. `BLUEPRINT_v3.md` (file ini)
2. PART file yang akan diedit (sesuai kebutuhan sesi)

Lalu tulis:
> "Lanjutkan proyek Mandarin Interaktif berdasarkan blueprint. Sesi berikutnya: [nama sesi]."

Claude akan membaca blueprint, memahami posisi saat ini, dan melanjutkan tanpa perlu penjelasan ulang.


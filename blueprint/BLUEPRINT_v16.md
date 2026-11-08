# BLUEPRINT_v16.md — Mandarin Interaktif

**Handoff document untuk sesi Claude berikutnya.** Tempel isi file ini di awal percakapan baru supaya Claude langsung punya konteks penuh tanpa perlu dijelaskan ulang dari nol.

Lokasi proyek: `C:\mandarin_app\` (Windows, رسلان adalah satu-satunya developer & user).
Stack: vanilla HTML/CSS/JS murni, tanpa build step, tanpa dependency eksternal (offline-first 100%).

---

## 1. Ringkasan Aplikasi

Aplikasi belajar Mandarin pribadi, terdiri dari beberapa halaman:
- `index.html` — beranda/dashboard (streak, progres HSK)
- `kamus.html` (+ modul `kamus/*.js`) — kamus/dictionary, tampilan statis untuk menjelajah kata
- `flashcard.html` — SRS (spaced repetition) + berbagai mode game/latihan
- `wordbuilder.html`, `tone.html`, `graded-reader.html`, `hsk-exam.html`, `tatabahasa.html` — modul pendukung lain

**Prinsip arsitektur yang WAJIB dipatuhi:**
- 100% offline, tidak ada CDN/API eksternal.
- `cidict_index.json` = sumber kanonis CC-CEDICT (sudah dalam Bahasa Indonesia).
- Jalankan `node --check` pada semua JS sebelum diserahkan ke رسلان.
- **Selalu baca isi file aktual sebelum mengedit** — jangan pernah asumsi isi file.
- Cek keseimbangan tag HTML (div dsb) per-file DAN gabungan lintas file modular.
- `kamus.html` sudah dimodularisasi jadi 8 file di folder `kamus/`: `kamus-data.js`, `kamus-search.js`, `kamus-cards-ui.js`, `kamus-detail.js`, `kamus-actions-filters.js`, `kamus-storage-layout.js`, `kamus-stroke-order.js`, dan `kamus-init.js` (**WAJIB paling akhir** dimuat). Alur PART-file lama (`gabung_kamus.py`) sudah **tidak berlaku** untuk kamus — edit langsung ke file `kamus/*.js` yang relevan. Alur PART-file (`gabung_flashcard.py`) **masih berlaku** untuk `flashcard.html` (belum dimodularisasi).

---

## 2. Yang Dikerjakan di Sesi Ini (v15 → v16)

### 2.1 Import tema baru via `complete_theme_json.py`
- رسلان dapat kosakata tema dari AI lain dalam format `{theme, words:[{hanzi,pinyin,translation}]}`, disimpan 1 file JSON per tema di `C:\mandarin_app\tema_json\`.
- Alur kerja yang sudah terbukti jalan: `cd C:\mandarin_app` → `python complete_theme_json.py tema_json\NamaFile.json`. Skrip otomatis backup `app_words.json`, isi kata baru (pakai `cidict_index.json` kalau ketemu, kalau tidak pakai data AI + tandai "PERLU DICEK MANUAL"), lalu tag tema ke `index_theme.json` — **tanpa perlu klik apa pun di aplikasi**, otomatis muncul di sidebar Flashcard & panel "Per Tema" Kamus setelah refresh.
- **Diputuskan (dan disetujui رسلان):** tombol "+ Tema Baru" di Flashcard (sistem `localStorage`, terpisah dari `index_theme.json`) **TIDAK dipakai** untuk alur impor tema besar ini — hanya untuk deck ad-hoc kecil milik رسلان sendiri. Alasan: custom theme localStorage tidak muncul di Kamus dan tidak persisten lintas-browser/device.
- Contoh sukses: tema "Perjalanan & Wisata" (128 kata mentah → 139 kata di app setelah dedup dengan kata yang sudah ada).

### 2.2 Bug fix: pencocokan tema pakai substring
`buildDeckQueue()` di `flashcard.html` sebelumnya pakai `w.themes.some(t => t === theme || t.includes(theme))` — kalau suatu saat ada key tema pendek yang jadi substring dari key tema lain, kata akan salah nyasar ke deck yang salah. **Sudah diperbaiki** jadi `t === theme` (exact match saja), di kedua lokasi (termasuk definisi lama yang sudah dead code — lihat 2.6).

### 2.3 Fitur: Pencarian cepat sidebar
Kotak input `🔍 Cari…` ditambahkan di dalam accordion **Tema, Radikal, Fonetik** (dan **Goresan** yang baru ditambah di 2.5) di `flashcard.html`. Filter murni sisi klien lewat fungsi generik `filterSidebarList(inputId, listContainerId)` — otomatis menangani kasus item yang tersembunyi di balik tombol "+ Tampilkan semua".

### 2.4 Reorder UI Flashcard
Urutan sidebar sekarang: **Tema → Radikal → Goresan → Komponen Fonetik → Pinyin → Filter Game → Pengaturan Sesi**. (Fonetik dipindah dekat Radikal, Filter Game dipindah ke paling akhir dekat Pengaturan Sesi, sesuai permintaan رسلان.)

### 2.5 Fitur: Ekspor hasil di Kamus
Tombol **"⬇ Ekspor"** di `results-header` Kamus (satu tombol, berlaku untuk APA PUN yang sedang ditampilkan — pencarian bebas, grup Radikal/Goresan/Tema/Pinyin/Struktur/Fonetik, atau koleksi bookmark/riwayat). Klik → modal berisi:
- Kotak teks format `Hanzi<TAB>Pinyin<TAB>Arti`, siap tempel ke Word/Excel/Sheets.
- Tombol **📋 Salin ke Clipboard** (pakai Clipboard API, fallback `execCommand`).
- Tombol **🖨 Cetak / Simpan PDF** (buka tab baru dengan tabel rapi + judul kontekstual, langsung trigger dialog print).
Ekspor selalu mengambil **SELURUH** `STATE.results` (bukan cuma yang sudah ter-render lewat infinite scroll), urut sesuai sort yang sedang aktif di layar.
Fungsi kunci: `getExportRows()`, `openExportPanel()`, `copyExportToClipboard()`, `printExportResults()` — semua di `kamus-actions-filters.js`.

### 2.6 Fitur silang Kamus ↔ Flashcard
- **Kamus** dapat tambahan grup **"Per Komponen Fonetik"** (sejajar Radikal/Goresan/Tema/Pinyin/Struktur di panel kelompok), baca `index_phonetic.json` (file yang sama dipakai Flashcard).
- **Flashcard** dapat tambahan deck baru:
  - **Goresan** — per jumlah goresan PASTI (1,2,3,...), beda dari "Goresan Mudah/Sulit" yang sudah ada duluan (2 kelompok kasar, tetap dipertahankan terpisah). Deck ID: `strokecount-<n>`. Sumber data: `index_stroke.json` (baru pertama kali di-fetch oleh Flashcard di sesi ini — sebelumnya cuma dipakai Kamus).
  - **Pinyin** — 2 tingkat sama seperti panel Kamus (klik huruf awal → pilih turunan suku kata nyata → main). Deck ID: `pinyin-<suku kata>`. Dihitung client-side dari `FC.allWords`, tidak perlu file index baru.
  - **Struktur** ternyata sudah ada duluan di dalam accordion "Filter Game" (dari sesi sebelum v15) — tidak perlu ditambah lagi, cuma dikonfirmasi sudah terpenuhi.
- `isBrowseDeck` (whitelist yang bikin deck kosong-karena-SRS fallback nampilin ulang semua kartu) sudah diupdate mencakup `strokecount-` dan `pinyin-`.

### 2.7 Diagnostik penting yang ditemukan (bukan bug data, tapi dicatat)
- **Struktur `flashcard.html` punya definisi fungsi ganda** untuk `renderSidebarTema()`, `renderSidebarRadikal()`, dan `buildDeckQueue()` — sisa dari alur PART-file merge lama. JavaScript otomatis pakai definisi yang PALING BAWAH/TERAKHIR; definisi pertama jadi dead code (tidak berbahaya, tapi membingungkan kalau dibaca ulang tanpa sadar ada duplikat). **Belum dibersihkan** — kandidat kerja beres-beres di sesi mendatang kalau رسلان mau.
- **Gotcha cache browser:** kalau setelah `complete_theme_json.py` dijalankan data terasa usang di aplikasi (angka tema salah, tema baru tidak muncul) padahal file & server sudah benar — ini SELALU cache browser, bukan bug. **Solusi pasti:** `F12` → tab **Application** → **Storage** → **Clear site data** → refresh. Hard refresh (`Ctrl+Shift+R`) saja TERBUKTI kadang tidak cukup.
- Ada file kosong `C:\Users\User_iO\kamus.html` (0 byte) — sisa tidak berbahaya, aman dihapus kapan saja, tidak mempengaruhi apa pun.
- Skrip bantuan `cari_duplikat.py` sudah dibuat (scan seluruh `C:\` cari salinan `index_theme.json`/`flashcard.html`/`kamus.html`, plus baca `count` tema `ext_currency` di tiap salinan) — simpan untuk dipakai lagi kalau ada kecurigaan file/data ganda di masa depan.

---

## 3. Konvensi Deck ID di Flashcard (referensi cepat)

| Prefix/ID persis      | Sumber data                          | Ditambahkan sesi |
|------------------------|---------------------------------------|-------------------|
| `hsk-1` .. `hsk-7`      | `app_words.json` field `hsk`          | lama |
| `bookmarks`, `wrong`, `all-due` | localStorage SRS state       | lama |
| `theme-<key>`           | `index_theme.json`                   | lama |
| `radical-<char>`        | `index_radical.json`                 | lama |
| `struct-<tipe>`         | field `structure` per kata            | lama |
| `phonetic-<komponen>`   | `index_phonetic.json`                | lama |
| `custom-<key>`          | localStorage `mandarin_custom_themes`| lama |
| `stroke-easy` / `stroke-hard` | field `stroke_count` (1-3 / 15+)| lama |
| `tone-trap`, `antonyms`, `synonyms` | field khusus per kata     | lama |
| `strokecount-<n>`       | `index_stroke.json`                  | **v16 (baru)** |
| `pinyin-<suku kata>`    | dihitung client-side dari `FC.allWords` | **v16 (baru)** |

Kalau menambah jenis deck browse baru di masa depan: (1) tambah prefix di `buildDeckQueue()`, (2) tambahkan ke whitelist `isBrowseDeck`, (3) render sidebar section-nya dengan pola `COLLAPSE_AT` yang sama seperti Radikal/Goresan kalau daftarnya panjang.

---

## 4. Prioritas / Ide untuk Sesi Berikutnya (belum dikerjakan)

1. **Beres-beres dead code** — hapus definisi fungsi duplikat lama di `flashcard.html` (`renderSidebarTema`, `renderSidebarRadikal`, `buildDeckQueue` versi pertama) supaya file tidak membingungkan kalau dibaca ulang. Risiko rendah tapi butuh ekstra hati-hati (pastikan tidak ada pemanggilan yang bergantung ke versi lama).
2. Tidak ada item mendesak lain yang tertunda dari daftar sebelumnya — semua (poin 1-6 dari diskusi v15) sudah selesai & dikonfirmasi رسلان jalan lancar per sesi ini.
3. (Ide bebas رسلان) — belum ada permintaan fitur baru yang mengantre saat file ini ditulis.

---

## 5. Cara Pakai File Ini

Di percakapan Claude yang baru, رسلان cukup upload/tempel file ini di awal, lalu langsung lanjut minta apa pun yang diinginkan — Claude akan punya konteks penuh soal arsitektur, konvensi, dan riwayat pekerjaan tanpa perlu dijelaskan ulang.

# BLUEPRINT v27 — Mandarin Interaktif

*Ditulis sebagai penutup sesi (lanjutan dari BLUEPRINT v26). Upload file ini
di awal percakapan baru bersama Claude supaya tidak perlu menjelaskan ulang
konteks proyek dari nol.*

---

## A. Ringkasan Proyek

**Mandarin Interaktif** — aplikasi belajar Mandarin offline milik رسلان,
murni HTML/CSS/JS vanilla (tanpa build tool/CDN wajib), berjalan lokal di
`C:\mandarin_app\` lewat `python -m http.server`. رسلان satu-satunya
developer & user. Semua pipeline data pakai Python di root folder proyek.
Backup pakai `checkpoint.py` (zip timestamped, 20 terbaru + arsip bulanan).

**Halaman utama:** `index.html` (dashboard), `kamus.html` (kamus + SRS
lookup), `flashcard.html`, `wordbuilder.html`, `tone.html`, `graded-reader.html`,
`hsk-exam.html`, `tatabahasa.html` (770+ poin grammar HSK1-9), `terjemah-bebas.html`,
`peta-bahasa.html` (BARU sesi ini — lihat Bagian C).

**Metodologi kerja yang sudah baku:** audit (read-only) → sample-check →
`--dry-run` → apply → `checkpoint.py save`. Setiap perubahan data besar wajib
lewat alur ini. Jangan menebak-nebak radikal/struktur karakter yang ambigu
(prinsip "jangan menebak 50/50" dari BLUEPRINT v18-19, masih berlaku).

---

## B. Status Akhir Sesi Ini — Milestone "Peta 11 Pilar" SELESAI 100%

BLUEPRINT v26 menyebut milestone ini "~95% selesai, sisa: perdalam JSON
pilar 1/4/6/7/9 + selesaikan duplikat pilar_5_versi2". **Keduanya sudah
tuntas di sesi ini.** Rincian final:

### B.1 — Leksikon Khusus (kata seru/onomatope/sapaan/partikel modal)
- `app_words.json`: **11.726 → 11.983 entri** (+257 kata baru, 213 duplikat
  di-skip otomatis dari total 470 kandidat).
- `index_kelompok_khusus.json`: **37 grup**, format konsisten dgn
  `index_theme.json` (label_id/label_zh/words/count).
- UI Kamus: sidebar "💬 Kelompok Khusus" dgn menu **berjenjang 3 level**
  (kategori → sub-grup → khusus Sapaan Keluarga dpt level tambahan per
  Generasi) — bukan 37 tombol datar lagi.

### B.2 — `peta-bahasa.html` (halaman baru)
- Index navigasi 11 Pilar bahasa Mandarin, status ✅Kuat/🟢Baru/🟡Sebagian/⚪Belum
  per sub-topik, tombol lompat nyata ke lokasi masing-masing.
- Hash-router deep-link ditambahkan ke `kamus-init.js`:
  `kamus.html#group=theme:angka`, `#opengroup=khusus`, `#search=...`
- Nav `peta-bahasa.html` sudah konsisten di SEMUA 10 halaman lain.
- `index.html` dapat section CTA baru (setelah Hero) + 2 feature-card
  (Tata Bahasa, Terjemah Bebas) yang sebelumnya hilang total dari dashboard.

### B.3 — Sistem "Pelajaran Lengkap" (data eksternal, bukan hardcode)
Setiap pilar di `peta-bahasa.html` punya tombol "📖 Pelajaran Lengkap" yang
fetch `data/pelajaran/pilar_N.json` on-demand (lazy-load + cache, pola sama
seperti `loadCidict()`). **Semua 11 file sudah lengkap dan tervalidasi:**

| Pilar | Karakter | Pilar | Karakter |
|---|---|---|---|
| 1 — Fonetik | 71.158 | 7 — Konstruksi Lanjutan | 69.483 |
| 2 — Angka | 58.580 | 8 — Sapaan | 53.270 |
| 3 — 量词 | 46.224 | 9 — Kata Sifat/Reduplikasi | 78.997 |
| 4 — Partikel & Aspek | 70.702 | 10 — Pragmatik | 60.842 |
| 5 — Modal | 100.594 | 11 — Variasi Bahasa | 51.163 |
| 6 — Struktur & Perbandingan | 70.868 | | |

**Total ~732.000 karakter**, nol isu struktural di semua 11 file (skema
`{tipe: paragraf|poin|tabel|contoh|peringatan}` diikuti konsisten), semua
tag `<span class="hz/py">` seimbang.

**2 dokumen prompt reusable dihasilkan** (masih relevan untuk pilar/topik
baru di masa depan):
- `PROMPT_GENERATOR_PELAJARAN.md` — generate `pilar_N.json` dari nol dari
  dokumen sumber `PILAR_N.txt`.
- `PROMPT_PENDALAMAN_PILAR.md` — memperdalam `pilar_N.json` yang sudah ada
  (target konkret: ≥2.000-3.000 karakter/bagian, ≥3-5 contoh/bagian, tambah
  dimensi regional/formal-informal/gaul internet/klasik/kesalahan umum/
  latihan/rekap kalau relevan).

### B.4 — Isu Teknis yang Ditemukan & Metode Perbaikannya (dicatat utk masa depan)
**Masalah berulang:** AI yang رسلان pakai untuk generate `pilar_N.json`
kadang tidak meng-escape tanda kutip ganda di dalam nilai string (`<span
class="hz">` ditulis mentah, bukan `\"hz\"`) — merusak validitas JSON,
kadang di RATUSAN baris sekaligus. **Sudah ditambahkan aturan eksplisit
(#3b) di kedua prompt di atas**, tapi kalau masih terjadi lagi: solusinya
BUKAN menebak-nebak per karakter, tapi parser presisi per baris (regex
`"key": "value"` → escape semua `"` internal yang belum di-escape). Metode
ini sudah 3× dipakai sukses (Pilar 3, 8, 9 versi awal) — kalau perlu lagi,
minta Claude jalankan metode yang sama, jangan re-derive dari nol.

**Cara validasi cepat sebuah `pilar_N.json`** (dipakai berulang sesi ini):
1. `json.load()` — cek valid dulu.
2. Cek tiap `tipe` blok termasuk 5 nilai yang diizinkan.
3. Cek `tabel`: jumlah kolom tiap baris = jumlah header.
4. Cek `contoh`: tiap item punya `hanzi`.
5. Cek keseimbangan `<span class="hz/py">` vs `</span>`.
6. Ukur "kedalaman nyata" pakai total karakter teks + jumlah item
   contoh/poin/baris tabel — **JANGAN pakai jumlah "bagian" sebagai proksi
   kelengkapan**, itu terbukti menyesatkan (pilar dgn byte 34 bagian bisa
   lebih dangkal dari pilar dgn 20 bagian kalau tiap bagiannya cuma
   1 paragraf pendek).

### B.5 — `grammar_hsk1-9.json` — folder sumber
Dikonfirmasi via kode (`tatabahasa.html` baris fetch): app SELALU baca dari
`C:\mandarin_app\data\`, BUKAN `C:\mandarin_app\grammar\` (folder itu sisa
lama, tidak dirujuk kode manapun). رسلان sudah menghapus folder `grammar\`
setelah perbandingan head-to-head (data/ menang 9/9 level).

### B.6 — Housekeeping kecil yang juga selesai
- `VARIANT_TO_KANGXI` di `enrich_leksikon_khusus.py` dapat 4 mapping baru
  (⺮→118, 丷→12, 贝→154, 门→169) — cegah radikal kosong berulang di masa depan.
- `patch_25_entries.py` — 25 entri leksikon khusus yang sempat kosong
  (radikal ambigu 阝/月, bopomofo konsonan silabis ḿ, karakter langka 唻)
  sudah dilengkapi manual dgn penjelasan linguistik per kasus.

---

## C. Arsitektur File Kunci (update dari v26)

**Data baru sesi ini:**
- `data/index_kelompok_khusus.json` — index grup leksikon khusus.
- `data/pelajaran/pilar_1.json` … `pilar_11.json` — konten edukasi lengkap
  per pilar (skema di Bagian B.3).

**Kode baru/diubah sesi ini:**
- `peta-bahasa.html` — halaman baru, fetch on-demand ke `data/pelajaran/`.
- `kamus/kamus-data.js` — tambah `STATE.dataKhusus`, `STATE.indexFilesPromise`.
- `kamus/kamus-actions-filters.js` — `openGroupPanel('khusus')` 3-level,
  fungsi `renderKhususLevel1/2/3()`.
- `kamus/kamus-cards-ui.js` — `selectGroupItem('khusus', key)`.
- `kamus/kamus-init.js` — `handleUrlHash()` (hash-router deep-link).
- `index.html`, `kamus.html`, `tatabahasa.html`, `terjemah-bebas.html`,
  `flashcard.html`, `wordbuilder.html`, `tone.html`, `graded-reader.html`,
  `hsk-exam.html` — nav link `peta-bahasa.html` ditambahkan ke semua.

**Scripts Python yang dipakai sesi ini** (kemungkinan masih berguna,
disimpan di root proyek کalau belum):
- `apply_leksikon_khusus.py` — merge leksikon khusus ke `app_words.json`
  + bangun `index_kelompok_khusus.json` (dry-run/apply, checkpoint-aware).
- `patch_25_entries.py` — perbaikan 25 entri leksikon khusus yang kosong.
- `compare_grammar_folders.py` — bandingkan folder `data/` vs `grammar/`
  head-to-head (sudah tidak relevan lagi karena `grammar/` sudah dihapus,
  tapi polanya bisa dipakai ulang kalau ada kasus folder-duplikat lain).

---

## D. Prioritas / Open Items untuk Sesi Berikutnya

**Tidak ada item mendesak yang menggantung dari sesi ini** — semua yang
direncanakan di v26 sudah tuntas. Kandidat pekerjaan berikutnya (belum
diputuskan prioritasnya, murni usulan):

1. **Selaraskan status badge di `peta-bahasa.html`** — array `PILLARS` di
   JS (status ✅/🟢/🟡/⚪ per sub-topik) ditulis SEBELUM sistem "Pelajaran
   Lengkap" ada. Sekarang beberapa sub-topik yang tadinya ditandai ⚪ Belum
   (mis. 成语, dialek, bahasa klasik di Pilar 11) kemungkinan sudah
   tercakup di `pilar_11.json` — perlu dicek ulang & badge-nya di-update
   supaya tidak menyesatkan.
2. Kalau رسلان mau, bisa audit ulang kualitas Pilar 8 & 11 (yang sudah
   dalam sejak generate pertama, belum pernah lewat proses "pendalaman"
   eksplisit) — mungkin masih ada ruang, meski dari data terakhir keduanya
   sudah solid (51-53rb karakter).
3. Housekeeping: pastikan `checkpoint.py save` dijalankan setelah semua
   perubahan sesi ini (data pelajaran + app_words.json + kode) — kalau
   belum, sangat disarankan sebelum sesi berikutnya.
4. Di luar topik "Peta 11 Pilar": tidak ada proyek lain yang disebut
   رسلان di sesi ini. Sesi berikutnya kemungkinan mulai dari kebutuhan baru.

---

*Selesai — dokumen ini menggantikan BLUEPRINT v26 sebagai rujukan utama.*

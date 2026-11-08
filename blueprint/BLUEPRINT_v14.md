# BLUEPRINT_v14 — Mandarin Interaktif
### Handoff document dari sesi sebelumnya. Upload file ini di awal percakapan baru.

> Cara pakai: رسلان upload file ini ke percakapan baru. Claude membaca semuanya
> dulu sebelum bertanya apa pun — jangan minta رسلان mengulang konteks yang
> sudah ada di sini.

---

## 1. Tentang aplikasi ini

**Mandarin Interaktif** — aplikasi belajar bahasa Mandarin offline, HTML/CSS/JS
murni (tanpa framework/build step), disimpan lokal di **`C:\mandarin_app\`**.
رسلان mengerjakan ini lintas sesi Claude yang berbeda-beda, makanya blueprint
ini penting sebagai jembatan ingatan.

**Prinsip inti yang TIDAK BOLEH dilanggar**: aplikasi ini **offline murni**.
Jangan pernah usulkan fitur yang butuh API key/koneksi internet/AI generatif
online saat aplikasi berjalan. Pengecualian yang sudah disepakati: skrip
Python terpisah yang رسلان jalankan manual sekali di lokal untuk MENYIAPKAN
data itu boleh — bukan bagian aplikasi yang berjalan.

**Halaman yang sudah ada** (semua saling terhubung lewat navbar, 9 halaman
total — TIDAK ada halaman baru sesi ini): `index.html`, `kamus.html` (modular,
folder `kamus/`), `flashcard.html`, `wordbuilder.html`, `tone.html`,
`graded-reader.html`, `hsk-exam.html`, `tatabahasa.html`,
`terjemah-bebas.html`. Detail arsitektur tiap halaman yang TIDAK BERUBAH sesi
ini tidak diulang di sini — lihat BLUEPRINT_v12/v13 kalau perlu detail lama.

**File bersama & data utama**: TIDAK BERUBAH dari BLUEPRINT_v13, KECUALI
`data/char_etymology_id.json` yang sekarang **SUDAH TUNTAS 100%**
(lihat §2.1 — tidak ada lagi batch tersisa, beda dari sesi-sesi sebelumnya).

---

## 2. Apa yang sudah dikerjakan sesi ini (kronologis)

### 2.1 Etimologi karakter TUNTAS TOTAL — 2.840/2.840 (100%)

Melanjutkan dari BLUEPRINT_v13 (batch 1-11, 1.428 karakter dari 2.653 target
yang punya data di Make Me a Hanzi):

- **Batch 12-21** (10 batch, pola sama seperti sebelumnya — 130
  karakter/batch, diverifikasi otomatis tiap batch: kandidat sesuai
  ekspektasi, tidak overlap dengan data lama, semua field terisi) →
  menuntaskan **2.653/2.653** karakter yang memang punya data etimologi di
  sumber Make Me a Hanzi.
- **187 karakter tambahan** ditemukan: karakter ini ADA di
  `character_etymology_en.json` tapi field `etymology`-nya `null` (kosong) —
  ternyata kebanyakan karakter DASAR yang sangat umum (无/发/事/成/用/实/体/
  后/前/于, dst), bukan karakter langka. Claude menyusun sendiri gloss +
  asal-usulnya berdasarkan pengetahuan karakter Tionghoa umum (2 batch, ~94 +
  93 karakter), BUKAN turunan Make Me a Hanzi — jadi tidak terikat lisensi
  mereka, beda status dengan 2.653 sisanya.
- **Hasil akhir: `data/char_etymology_id.json` berisi 2.840/2.840 karakter
  — SEMUA karakter yang muncul di kata 2+ karakter di `app_words.json`,
  tanpa kecuali.** Tidak ada lagi "batch selanjutnya" untuk fitur ini.
- Catatan kualitas: 2.653 entri dari Make Me a Hanzi kualitasnya sudah
  terverifikasi pola sebelumnya. 187 entri buatan Claude sendiri — cukup
  yakin untuk karakter dasar, kurang bisa diverifikasi silang untuk yang
  agak jarang (misal 贞/戴/虔/皂). رسلان sudah bilang tidak perlu
  dikhawatirkan/ditandai proaktif — cukup diperbaiki reaktif kalau رسلان
  sendiri menemukan yang terasa janggal.

### 2.2 Statistik Latihan Nada di Dashboard

- **`tone.html`**: sebelumnya skor cuma hidup di memori (hilang tiap pindah
  halaman/ganti mode). Sekarang setiap jawaban dicatat persisten ke
  `localStorage` key **`mandarin_tone_stats_v1`**, format:
  `{ total:{ok,bad}, byTone:{1:{ok,bad},2,3,4}, byMode:{nada:{ok,bad},
  hanzi:{ok,bad}}, lastPracticed }`.
- **`index.html`**: kartu baru "Akurasi Latihan Nada" di grid Progres
  Belajar + section baru "Statistik Latihan Nada" (breakdown per nada 1-4,
  reuse styling `.level-progress-list` yang sudah ada) + insight otomatis
  nada mana yang paling perlu dilatih (dihitung dari akurasi terendah,
  minimal 3 percobaan biar representatif).

### 2.3 Enhancement "Bantu Ingat" full coverage (Kamus)

Dengan data etimologi 100% lengkap, tampilan mnemonic di `kamus-detail.js`
diubah dari rantai teks + daftar catatan terpisah (subset) jadi **grid kartu
per-karakter** — tiap kartu langsung menyatukan hanzi + makna + asal-usul,
karena sekarang hampir semua karakter punya catatan lengkap. Styling pakai
inline style dengan CSS variable global (`var(--gold)` dst dari
`shared/style.css`) — TIDAK menyentuh `kamus.html`/`shared/style.css`.

### 2.4 Tiga ide lanjutan (disepakati رسلان setelah diskusi pasca-poin 2.1-2.3)

1. **Bantu Ingat di Flashcard SRS** (`flashcard.html`): load
   `data/char_etymology_id.json` (fungsi `loadFcCharEtymology()`), mnemonic
   dirender di `#fc-back-mnemonic` — bagian dari sisi BELAKANG kartu flip,
   jadi otomatis hanya kelihatan SETELAH kartu dibalik (bukan sebelum,
   supaya tidak jadi contekan yang melemahkan latihan ingatan). Tidak perlu
   logic gating tambahan karena flip-card sudah alami begitu.
2. **Insight nada terlemah jadi actionable**: `tone.html` sekarang terima
   parameter URL `?focus=N` (N=1-4). Soal TETAP acak dari 4 pilihan nada
   (supaya tidak trivial/ketebak), tapi kemunculan soal bernada target
   dibobotkan **60%** lebih sering (`TONE_FOCUS_WEIGHT` di
   `pickWeightedByTone()`), berlaku di mode Nada maupun Hanzi. Ada banner
   "🎯 Latihan fokus: Nada N" dengan tombol batalkan. `index.html` insight
   nada terlemah sekarang punya tombol "Latih sekarang →" yang link ke
   `tone.html?focus=N`.
3. **Explorer komponen/radikal** (`kamus.html`): klik chip radikal/komponen
   di panel detail (misal 氵) sekarang buka `#group-panel` (infrastruktur
   yang sudah ada, dipakai ulang) berisi grid SEMUA karakter lain yang
   berbagi radikal/komponen itu (field `radical`/`components` di entri
   1-karakter `app_words.json`), masing-masing dengan gloss singkat dari
   `char_etymology_id.json`. Klik satu karakter di grid → langsung lompat
   ke detail karakter itu (`selectWord()`, tanpa perlu search dulu). Fungsi
   baru: `getCharsByComponent()` + `openComponentExplorer()` di
   `kamus-actions-filters.js`. TIDAK perlu file data baru — murni dari data
   yang sudah ada. Beda dari `searchExample()` lama: itu cari KATA yang
   literally mengandung karakter itu; ini cari KARAKTER LAIN yang berbagi
   komponen struktural.

**Semua sudah رسلان tes langsung dan hasilnya memuaskan.**

---

## 3. TODO — urutan prioritas yang disarankan

Tidak ada item mendesak yang menggantung dari sesi ini — semua yang
direncanakan sudah selesai & diverifikasi. Opsi untuk sesi berikutnya
(TANYA dulu ke رسلان, jangan asumsi mana yang dipilih):

1. **Kalau رسلان temukan celah baru pas pakai app** (bug, UX kurang pas,
   entri etimologi yang terasa janggal terutama dari 187 karakter buatan
   Claude) — prioritas selalu boleh disisipkan di atas semua ini.
2. Ide-ide exploratory yang belum diangkat sesi ini (kalau رسلان masih
   berminat mengembangkan arah "manfaatkan data lengkap" lebih jauh):
   tidak ada yang eksplisit menggantung — 3 ide dari diskusi sebelumnya
   semua sudah dikerjakan (§2.4).
3. **Item lama dari blueprint sebelumnya yang statusnya TIDAK BERUBAH**:
   - Hapus folder `hanyu_extract`/`mandarin_kamus` — رسلان eksplisit bilang
     ini ditunda sampai **tahap akhir sekali** dari seluruh proyek. Jangan
     diusulkan sampai رسلان sendiri angkat topik ini.
   - OCR kamera fisik & widget kaca pembesar — **DI-DROP PERMANEN**, sudah
     dikonfirmasi رسلان untuk dihilangkan total dari rencana, jangan
     diusulkan lagi sama sekali di sesi manapun ke depannya.

---

## 4. Hal teknis tambahan

Semua konvensi dari BLUEPRINT_v12/v13 §4 **masih berlaku sepenuhnya**
(diskusi dulu sebelum coding scope besar, `node --check` utk JS, verifikasi
tag seimbang, Bahasa Indonesia, رسلان tidak punya akses filesystem langsung,
dll).

**Tambahan baru sesi ini**:
- **Pola "diskusi dulu, baru coding"** dipakai eksplisit sesi ini untuk fitur
  UX baru (bukan cuma kerja data) — Claude memaparkan rencana konkret per
  poin (termasuk keputusan desain seperti "mnemonic muncul setelah kartu
  dibalik, bukan sebelum") sebelum mulai implementasi, رسلان
  mengonfirmasi/mengoreksi, baru Claude eksekusi. Pola ini terbukti efektif,
  pakai lagi untuk fitur besar berikutnya.
- **Saat file pendukung (CSS/HTML utama) tidak diupload**, Claude tetap bisa
  jalan dengan asumsi konservatif: pakai CSS variable global lewat inline
  style (bukan bikin class baru di file yang tidak dipunya). Sesi ini
  asumsi itu terbukti 100% akurat setelah رسلان upload `style.css` &
  `kamus.html` untuk verifikasi — jadi pola ini aman dipakai lagi kalau
  situasi serupa terulang (asal tetap dicek ulang kalau ada kesempatan,
  jangan jadi kebiasaan malas verifikasi).
- **Reuse infrastruktur lama lebih diutamakan dari bikin baru**: explorer
  komponen (§2.4 poin 3) sengaja pakai ulang `#group-panel` yang sudah ada
  alih-alih bikin modal/panel baru — mengurangi CSS baru yang perlu
  dipelihara jangka panjang.
- **File-file modular `kamus/*.js` yang disentuh sesi ini**:
  `kamus-detail.js` (render mnemonic + wiring klik chip komponen) dan
  `kamus-actions-filters.js` (fungsi explorer baru). File modular `kamus/`
  lain (`kamus-data.js`, `kamus-search.js`, `kamus-cards-ui.js`,
  `kamus-storage-layout.js`, `kamus-stroke-order.js`, `kamus-init.js`)
  TIDAK disentuh sesi ini.

---

## 5. Ringkasan file yang berubah/baru sesi ini

| File | Status | Catatan |
|---|---|---|
| `data/char_etymology_id.json` | **TUNTAS 100%** | 1.428 → 2.840/2.840 karakter — SELESAI TOTAL, tidak ada batch lagi |
| `index.html` | Diperbarui | Kartu + section statistik nada, insight nada terlemah + tombol aksi ke tone.html |
| `tone.html` | Diperbarui | Localstorage stats persisten (`mandarin_tone_stats_v1`), fitur `?focus=N` weighted practice |
| `flashcard.html` | Diperbarui | "Bantu Ingat" ditambahkan di sisi belakang kartu SRS |
| `kamus/kamus-detail.js` | Diperbarui | Mnemonic box jadi grid kartu; klik chip radikal/komponen buka explorer |
| `kamus/kamus-actions-filters.js` | Diperbarui | Fungsi baru `getCharsByComponent()` + `openComponentExplorer()` |
| Semua file lain | Tidak berubah | Termasuk `kamus.html`, `style.css`, dan modul `kamus/*.js` lainnya |

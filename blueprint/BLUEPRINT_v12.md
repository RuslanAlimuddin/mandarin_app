# BLUEPRINT_v12 — Mandarin Interaktif
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
online saat aplikasi berjalan. Pengecualian yang SUDAH disepakati: skrip
Python terpisah yang رسلان jalankan manual sekali di lokal untuk MENYIAPKAN
data (misal unduh dataset publik dari GitHub) itu boleh — itu bukan bagian
dari aplikasi yang berjalan, hasilnya jadi file JSON statis yang lalu dipakai
offline seperti biasa. Lihat §2.5 untuk contoh nyata (etimologi karakter).

**Halaman yang sudah ada** (semua saling terhubung lewat navbar, 9 halaman total
— TIDAK ada halaman baru sesi ini, semua pekerjaan menambah/memperkuat halaman
yang sudah ada):
1. `index.html` — landing page **+ Dashboard progres** (lihat §2.2)
2. `kamus.html` — kamus 11.470 kata (`app_words.json`) + toggle sumber
   "HSK/Cidict" ke `cidict_index.json` + fallback otomatis + **cross-link ke
   bacaan** (§2.1) + **fitur mnemonic "Bantu Ingat"** (§2.4-2.5) — **kini
   MODULAR**, lihat §2.3 untuk detail arsitektur baru
3. `flashcard.html` — SRS, banyak deck & mode game + **cross-link ke bacaan**
   di panel belakang kartu (§2.1)
4. `wordbuilder.html` — susun kalimat dari pola tata bahasa. **Cross-link ke
   bacaan SENGAJA TIDAK ditambahkan di sini** — sudah didiskusikan tuntas,
   paradigma UI-nya (menyusun kalimat dari slot dropdown, bukan fokus 1 kata)
   tidak cocok dengan pola cross-link yang dipakai di Kamus/Flashcard. Jangan
   diusulkan lagi kecuali رسلان sendiri yang angkat topik ini.
5. `tone.html` — latihan nada Mandarin. **Catatan penting**: halaman ini
   **TIDAK punya sistem pencatatan skor/akurasi sama sekali** (cuma menyimpan
   mode terakhir dipilih di localStorage). Kalau رسلان suatu saat minta
   "statistik latihan nada" di Dashboard, itu perlu kerja BARU membangun
   sistem pencatatan dulu di `tone.html`, bukan sekadar baca data yang sudah
   ada — lihat §3 TODO.
6. `graded-reader.html` — bacaan berjenjang per level HSK (+ per tema), 104
   bacaan. **Fitur baru sesi ini**: toggle "拼 Pinyin" (§2.6).
7. `hsk-exam.html` — simulasi ujian HSK. Riwayat ujian (`mandarin_hsk_history_v1`)
   sekarang ditarik ke Dashboard di `index.html` (§2.2).
8. `tatabahasa.html` — referensi tata bahasa lengkap HSK 1-9.
9. `terjemah-bebas.html` — tempel teks Mandarin bebas → daftar kata otomatis.

**File bersama** (`shared/` di root app):
- `shared/core.js` — **berubah sesi ini**: tambah `touchStreak()` (§2.2),
  jalan otomatis tiap kali file ini dimuat. `index.html` sekarang IKUT
  memuat `shared/core.js` (sebelumnya tidak).
- `shared/pinyin.js`, `shared/audio.js`, `shared/style.css` — tidak berubah.

**Data utama** (`data/` di root app):
- `data/app_words.json` — kamus utama, 11.470 kata. Tidak berubah strukturnya.
- `data/cidict_index.json` — CC-CIDICT, 121rb+ entri. Tidak berubah.
- `data/graded_readers.json` — 104 bacaan, `{"passages": [...]}`, tiap passage
  punya `id, level, title, text, translation, glossary [{cn, py, id}], tema`.
  Field `glossary[].cn` dipakai sebagai basis index cross-link (§2.1).
- **`data/char_etymology_id.json` — FILE BARU sesi ini** (§2.4-2.5). Peta
  `karakter → {gloss_id, asal_usul_id}`, dibangun BERTAHAP per batch
  berdasarkan frekuensi kemunculan karakter. **Progres saat ini: 518 dari
  3.034 karakter (~17%), batch 1-4 SELESAI. Sesi berikutnya lanjut BATCH 5.**
  Detail lengkap cara lanjutkan ada di §2.5 — WAJIB dibaca sebelum mulai.

---

## 2. Apa yang sudah dikerjakan (kronologis, sesi ini)

### 2.1 Cross-link antar fitur ke bacaan berjenjang — SELESAI (Flashcard + Kamus)
Ide awal: dari Flashcard/Word Builder, tautan ke bacaan yang mengandung kata
yang sedang dipelajari. Setelah didiskusikan:
- **Flashcard**: SELESAI. Panel belakang kartu (`fc-back-bacaan`) menampilkan
  s.d. 5 bacaan yang mengandung kata itu, prioritas level HSK terdekat.
- **Kamus**: SELESAI (diusulkan Claude sebagai pengganti Word Builder — lihat
  di bawah). Section baru "📖 Muncul di Bacaan" di panel detail, pola sama.
- **Word Builder**: DI-DROP setelah diskusi. Paradigma UI-nya (susun kalimat
  dari beberapa kata sekaligus lewat dropdown) tidak cocok dengan cross-link
  per-kata-tunggal. Jangan diusulkan lagi kecuali رسلان minta.

**Mekanisme teknis** (dipakai di kedua halaman, pola identik): index
`kata → daftar bacaan` dibangun lazy-load sekali dari
`data/graded_readers.json` (`glossary[].cn`), di-cache di memori. Klik bacaan
→ tulis ke `localStorage['mandarin_gr_last_state_v1']` (key yang SAMA dipakai
mekanisme "ingat posisi terakhir" `graded-reader.html` yang sudah ada
sebelumnya) → redirect ke `graded-reader.html` → otomatis terbuka ke bacaan
itu. **`graded-reader.html` sendiri TIDAK PERNAH disentuh** untuk fitur ini.

### 2.2 Dashboard di index.html — DIPERLUAS (bukan dibangun dari nol)
**Temuan penting**: `index.html` SUDAH punya dashboard dasar sebelum sesi ini
(Hero stats, Kata Hari Ini, Ringkasan Progres 4 kartu) — tidak tercatat di
blueprint manapun sebelumnya. Sesi ini menambah:
- **Streak harian** — logika BARU di `shared/core.js`: `touchStreak()`,
  key `mandarin_streak_v1` = `{current, longest, lastDate}`. Jalan otomatis
  tiap `core.js` dimuat di halaman MANAPUN (bukan cuma index.html) — jadi
  tetap tercatat walau رسلان mulai belajar dari Kamus/Flashcard duluan.
- **Rata-rata skor Ujian HSK** — baca `mandarin_hsk_history_v1` (sudah ada
  dari `hsk-exam.html` sebelumnya, cuma belum ditarik ke dashboard).
- **Breakdown progres per level HSK** (1-7, level 7 = gabungan HSK7-9) — bar
  per level, hitung kata di `mandarin_srs_v1` (Flashcard) vs total per level
  di `app_words.json`.
- **TIDAK ditambahkan**: statistik latihan nada — `tone.html` belum punya
  sistem pencatatan skor sama sekali, lihat §1 poin 5 dan §3 TODO.

### 2.3 Modularisasi kamus.html — SELESAI
`kamus.html` menyusut dari **2.751 → 1.087 baris** (murni HTML+CSS sekarang).
Seluruh JS (1.667 baris) dipecah jadi **8 file terpisah** di folder
`kamus/` (folder BARU, beda dari folder PART lama):

| File | Isi |
|---|---|
| `kamus/kamus-data.js` | STATE, utils, load data & index radikal/goresan/tema, **+ index etimologi karakter (§2.5)** |
| `kamus/kamus-search.js` | Mesin pencarian, render kartu, mode tabel |
| `kamus/kamus-cards-ui.js` | Panel grup, builder kartu, helper UI |
| `kamus/kamus-storage-layout.js` | localStorage, infinite scroll, drag-resize, last-state |
| `kamus/kamus-detail.js` | Panel detail kata, cross-link bacaan (§2.1), **mnemonic (§2.4)** |
| `kamus/kamus-stroke-order.js` | Animasi goresan |
| `kamus/kamus-actions-filters.js` | Aksi detail, filter, search-example |
| `kamus/kamus-init.js` | Init + keyboard shortcut — **WAJIB dimuat paling akhir** |

**Cara kerja**: `<script src>` biasa (BUKAN ES module) — semua fungsi tetap
di scope global, urutan file lain relatif bebas KECUALI `kamus-init.js` yang
harus terakhir. `'use strict'` cuma di 5 file yang berasal dari blok script
pertama file lama (data, search, cards-ui, storage-layout, init) — bukan di
3 file dari blok kedua (detail, stroke-order, actions-filters), demi
menjaga perilaku identik dengan sebelumnya.

**DAMPAK WORKFLOW PENTING**: `kamus.html` sekarang cukup pendek untuk dikirim
langsung 1 file per sesi — **sistem PART lama untuk kamus.html
(`kamus_PART_1-4.txt`, `gabung_kamus.py`) TIDAK RELEVAN LAGI untuk konten JS**.
Kalau ada perubahan JS ke depan, kirim langsung file `.js` yang relevan dari
folder `kamus/` (jauh lebih ringan). PART-file system TETAP dipakai untuk
`flashcard.html` dan `wordbuilder.html` seperti biasa (tidak diubah).

### 2.4 Fitur mnemonic "Bantu Ingat" di Kamus — SELESAI (mekanisme), ONGOING (data)
Panel baru di detail kata `kamus.html`, di bawah "Arti (Indonesia)". Untuk
kata 2+ karakter, tampilkan dekomposisi tiap karakter jadi jembatan mengingat
— BUKAN terjemahan resmi. Contoh: *💡 Bantu ingat: 医 (obat) + 生 (hidup) →
dokter*. Kalau ada data etimologi (§2.5), muncul juga baris tambahan di
bawahnya: *📜 医 — [cerita bentuk karakter]*.

**Aturan (disepakati رسلان, LONGGAR)**: karakter yang maknanya tidak ketemu
dilewati saja (bukan bikin seluruh panel hilang), asal minimal 2 dari N
karakter kata itu berhasil ditemukan maknanya. رسلان eksplisit menerima
kualitas "kurang akurat asal membantu" untuk kata 3+ karakter.

**Prioritas sumber makna per karakter** (fungsi `getCharMeaning()` di
`kamus-data.js`):
1. `data/char_etymology_id.json` (§2.5) — paling akurat, kurasi manual
2. `app_words.json` (`meanings_id[0]` entri 1 karakter) — fallback
3. Cidict (lazy-load, fallback terakhir)

### 2.5 Data etimologi karakter (char_etymology_id.json) — BATCH 1-4 SELESAI, LANJUT BATCH 5

**Kenapa fitur ini ada**: `meanings_id[0]` (sumber #2 di atas) kadang
menyesatkan untuk mnemonic — contoh nyata: `路` (jalan) makna pertamanya di
`app_words.json` adalah **"marga Lu"** (nama keluarga), bukan "jalan". Untuk
memperbaiki ini secara sistematis, رسلان setuju pakai data etimologi
eksternal: **proyek open-source [Make Me a Hanzi](https://github.com/skishore/makemeahanzi)**
(dipakai juga oleh Hanzi Writer, library stroke-order yang app ini sudah
pakai). File sumbernya `dictionary.txt` — tiap baris JSON berisi `character`,
`definition` (Inggris), `etymology {type, hint, phonetic, semantic}`.

**Alur kerja yang SUDAH BERJALAN dan TERBUKTI**, wajib diikuti sama persis
di sesi berikutnya:

1. **رسلان sudah punya di lokal** (dari sesi-sesi sebelumnya):
   - `fetch_hanzi_etymology.py` — skrip Python (cuma pakai `urllib` bawaan,
     tidak perlu install apa-apa) yang mengunduh `dictionary.txt` dari GitHub
     dan MEMFILTER hanya karakter yang benar-benar dipakai di
     `app_words.json` (3.034 karakter unik dari total ~9.500 di sumber asli).
   - Hasil dari skrip itu: **`data/character_etymology_en.json`** — file
     MENTAH Bahasa Inggris, 3.034 karakter, 2.839 di antaranya (93,6%) punya
     data etimologi (sisanya `null`, karakter langka tanpa dokumentasi).
     **رسلان perlu upload file ini lagi di awal sesi berikutnya** kalau
     belum ada di percakapan (Claude butuh ini utk tahu kandidat batch 5).

2. **Proses penerjemahan per batch** (dilakukan Claude langsung di
   percakapan, BUKAN via skrip terjemahan otomatis — tiap karakter
   diterjemahkan dengan pertimbangan manual supaya gloss-nya benar-benar
   pas dipakai untuk mnemonic, bukan cuma translate literal):
   - Hitung frekuensi tiap karakter di seluruh `app_words.json`, HANYA
     untuk kata 2+ karakter (karena mnemonic cuma berlaku di situ).
   - Ambil karakter dengan skor tertinggi yang BELUM ada di
     `data/char_etymology_id.json` yang sudah terkumpul, dan yang PUNYA
     data etimologi (bukan `null`) di `character_etymology_en.json`.
   - Batch ukuran **~130 karakter** per sesi/pesan (angka ini bukan aturan
     kaku, cuma yang terbukti nyaman dikerjakan sekali jalan).
   - Tiap karakter dapat 2 field: `gloss_id` (gloss singkat 1-3 kata,
     pengganti `meanings_id[0]`) dan `asal_usul_id` (1 kalimat pendek cerita
     bentuk/asal karakter, ditampilkan sbg baris 📜 tambahan di UI).
   - Setelah ditulis, WAJIB verifikasi terprogram: jumlah key harus PERSIS
     sama dengan kandidat batch (tidak kurang/lebih), tidak ada tumpang
     tindih dengan batch-batch sebelumnya, tidak ada `gloss_id` kosong.
   - Gabung ke `data/char_etymology_id.json` (merge dict, bukan timpa).

3. **Progres per batch sejauh ini** (batas peringkat frekuensi kumulatif):
   - Batch 1: peringkat ~1-150 → 128 karakter (yang punya etimologi)
   - Batch 2: peringkat ~150-400 → 130 karakter
   - Batch 3: peringkat ~400-700 → 130 karakter
   - Batch 4: peringkat ~700-1000 → 130 karakter
   - **Total: 518 karakter. Batch 5 lanjut dari peringkat ~1000 ke atas.**

**Kode Python pola yang dipakai tiap batch** (tinggal ganti angka rentang
frekuensi & nomor batch untuk batch 5 dst):
```python
import json
from collections import Counter
words = json.load(open('app_words.json', encoding='utf-8'))
etym = json.load(open('character_etymology_en.json', encoding='utf-8'))
done = json.load(open('char_etymology_id.json', encoding='utf-8'))  # akumulasi semua batch sebelumnya

freq = Counter()
for w in words:
    s = w.get('simplified','') or w.get('id','')
    if len(s) >= 2:
        for c in s:
            freq[c] += 1

ranked = [c for c, _ in freq.most_common(1300)]  # naikkan batas tiap batch
candidates = [c for c in ranked if c not in done and etym.get(c, {}).get('etymology')]
batch5 = candidates[:130]
```

**Catatan kualitas jujur** (perlu diketahui, bukan masalah yang harus
diperbaiki kecuali رسلان minta): `gloss_id` diambil dari makna INTI karakter
(sering beda dari `meanings_id[0]` yang kadang makna langka/nama marga),
sedangkan `asal_usul_id` adalah kondensasi dari field `hint`/`semantic`/
`phonetic` sumber Inggris — untuk karakter *pictophonetic* (mayoritas kasus),
komponen fonetiknya cuma memberi BUNYI, bukan makna, jadi catatan asal-usul
kadang lebih ke "struktur pembentukan" daripada "kenapa artinya begitu". Ini
sudah sesuai ekspektasi رسلان ("kurang akurat asal membantu").

**Lisensi**: proyek Make Me a Hanzi punya file `COPYING` dengan lisensi
campuran (sebagian data diturunkan dari Unihan/CJKlib). Belum ada masalah
apapun sejauh ini (pemakaian offline pribadi), tapi kalau رسلان suatu saat
berencana membagikan aplikasi ini ke orang lain, sarankan رسلان cek ulang
file itu dulu.

### 2.6 Toggle "Tampilkan Pinyin" di graded-reader.html — SELESAI
Sebelumnya TIDAK ADA sama sekali (رسلان kira sudah ada, mengira mirip
`terjemah-bebas.html`, ternyata belum). Ditambahkan: tombol "拼 Pinyin" di
toolbar bacaan, pinyin muncul kecil di atas tiap kata (gaya furigana,
`<span class="gr-word-py">`), state diingat via
`localStorage['mandarin_gr_show_pinyin_v1']`. Data pinyin per-kata sudah ada
dari awal (`t.py` per token), tidak perlu data tambahan.

---

## 3. TODO — urutan prioritas yang disarankan

1. **[PALING PRIORITAS] Lanjutkan batch penerjemahan etimologi karakter**
   (§2.5) — batch 5 dst. رسلان sudah eksplisit minta ini dilanjutkan sampai
   entah kapan (tidak ada target akhir yang disebutkan, cuma "lanjutkan
   bertahap"). Kalau رسلان buka sesi baru dan belum bilang topik lain, ini
   yang paling mungkin jadi kelanjutan otomatis — tapi tetap TANYA dulu ke
   رسلان, jangan asumsi.
2. **Statistik Latihan Nada di Dashboard** — BELUM dikerjakan, sempat
   disinggung tapi diputuskan tunda karena `tone.html` belum punya sistem
   pencatatan skor sama sekali (kerja baru, bukan sekadar tarik data yang
   sudah ada). Cuma dikerjakan kalau رسلان eksplisit minta.
3. Kalau رسلان temukan celah baru pas pakai app (bug, UX kurang pas, dll)
   — prioritas selalu boleh disisipkan di atas semua ini, seperti biasa.

**Item lama dari blueprint sebelumnya yang statusnya TIDAK BERUBAH** (masih
berlaku semua, tidak perlu diulang tanya):
- Hapus folder `hanyu_extract`/`mandarin_kamus` — masih DITUNDA sengaja
  رسلان, jangan diusulkan sampai رسلان sendiri angkat topik ini.
- OCR kamera fisik & widget kaca pembesar — masih DI-DROP, di luar
  kemampuan web app biasa.

---

## 4. Hal teknis tambahan (pelengkap blueprint lama, semua masih berlaku)

- **Konvensi kerja yang SUDAH DISEPAKATI** (dari blueprint lama, masih
  berlaku semua): diskusi dulu sebelum coding kalau scope besar/ambigu,
  kirim file di respons yang sama dengan pekerjaannya, `node --check` untuk
  semua JS sebelum diserahkan, verifikasi keseimbangan tag `<div>`/`<span>`
  sebelum & sesudah edit (sekarang HARUS dicek GABUNGAN lintas file kalau
  kerja di `kamus/` — lihat pola di §2.3, jumlah tag di `kamus.html` + semua
  file `kamus/*.js` harus sama persis dengan sebelum modularisasi),
  komunikasi dalam Bahasa Indonesia, prefer solusi lebih simpel kalau ada
  pilihan, رسلان tidak bisa diakses filesystem-nya langsung (semua lewat
  upload/download file di chat, skrip Python untuk رسلان jalankan lokal
  kalau perlu proses file besar).
- **SELALU verifikasi file yang diupload رسلان itu VERSI TERBARU** sebelum
  mulai edit — kalau ragu file sudah berubah sejak terakhir diberikan,
  minta رسلان upload ulang (pernah terjadi sesi ini: `index.html` sempat
  "hilang" dari workspace Claude karena upload lama sudah tidak tersimpan,
  harus minta رسلان upload ulang).
- **Kalau menemukan fitur/kode yang sudah ada tapi tidak tercatat di
  blueprint**: pola ini TERULANG BEBERAPA KALI sesi ini (toggle radikal
  214 di kamus.html, dashboard dasar di index.html) — PRIORITASKAN baca
  kode dulu sebelum asumsi sesuatu belum dikerjakan, dan selalu update
  blueprint begitu ketahuan.
- **Pola verifikasi "rekonsiliasi total" untuk refactor besar** (dipakai di
  §2.3): setelah split/pindah kode antar file, WAJIB diff ulang hasil
  rekonstruksi vs kode asli byte-per-byte (bukan cuma baca sekilas) — cara
  ini berhasil menangkap potensi kesalahan sebelum dikirim ke رسلان.
- **Pola verifikasi "cakupan lengkap" untuk kerja data batch** (dipakai di
  §2.5): setelah tiap batch terjemahan, WAJIB cek terprogram — jumlah key
  hasil == jumlah kandidat, tidak ada yang kelewat, tidak ada tumpang
  tindih antar batch, tidak ada value kosong. Jangan cuma percaya diri
  tanpa verifikasi, walau terasa "sudah pasti benar".
- Semua hal teknis dari BLUEPRINT_v10/v11 (skema `graded_readers.json`,
  `grammar_hsk{1-6}.json`, `pattern_explanations.json`,
  `confusion_groups.json`, `cidict_index.json`, cara verifikasi coverage
  bacaan, dll) **masih berlaku sepenuhnya**, tidak ada perubahan.

---

## 5. Ringkasan file yang berubah/baru sesi ini (untuk cepat cocokkan versi)

| File | Status | Catatan |
|---|---|---|
| `index.html` | Diubah | + dashboard streak/ujian/breakdown level, + load `shared/core.js` |
| `shared/core.js` | Diubah | + `touchStreak()` |
| `flashcard.html` | Diubah | + cross-link bacaan di panel belakang kartu |
| `kamus.html` | **Diubah besar** | 2.751→1.087 baris, JS dipecah ke `kamus/*.js` (8 file baru), + panel mnemonic |
| `kamus/kamus-*.js` (8 file) | **Baru** | Lihat tabel §2.3 |
| `graded-reader.html` | Diubah | + toggle pinyin |
| `data/char_etymology_id.json` | **Baru, ongoing** | 518/3.034 karakter, lanjut batch 5 |
| `fetch_hanzi_etymology.py` | Baru (skrip lokal رسلان) | Sudah dijalankan, hasilnya `character_etymology_en.json` |
| `wordbuilder.html` | Tidak berubah | Cross-link sengaja di-drop, lihat §2.1 |
| `tone.html`, `hsk-exam.html`, `tatabahasa.html`, `terjemah-bebas.html` | Tidak berubah | — |

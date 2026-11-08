# BLUEPRINT_v8 — Mandarin Interaktif
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

**Halaman yang sudah ada** (semua saling terhubung lewat navbar):
1. `index.html` — landing page, 7 kartu menuju semua halaman
2. `kamus.html` — kamus 11.470 kata + akses ke `hanyu_extract`/`mandarin_kamus` (125rb+ entri CC-CEDICT mentah, belum diintegrasikan)
3. `flashcard.html` — SRS (spaced repetition), banyak deck & mode game
4. `wordbuilder.html` — susun kalimat dari pola tata bahasa (Tunggal/Majemuk/Fungsi)
5. `tone.html` — latihan nada Mandarin
6. `graded-reader.html` — bacaan berjenjang per level HSK (+ per tema, baru)
7. `hsk-exam.html` — simulasi ujian HSK
8. `tatabahasa.html` — **halaman baru sesi ini**: referensi tata bahasa lengkap per level HSK 1-9

**File bersama** (`shared/` atau `data/` di root app):
- `shared/core.js`, `shared/pinyin.js`, `shared/audio.js`, `shared/style.css` — dipakai semua halaman
- `data/app_words.json` — kamus utama, 11.470 kata (field: simplified, pinyin, hsk, hsk2, meanings_id, synonyms, antonyms, radical, structure, dll)
- `data/grammar_hsk1.json` s/d `grammar_hsk9.json` — data tata bahasa per level (dipakai `tatabahasa.html`)
- `data/graded_readers.json` — bacaan built-in (2 per level, sudah ada dari sebelum sesi ini)
- `data/graded_readers_tema*.json` — bacaan bertema (baru, lihat §3)

**Konvensi kerja yang SUDAH DISEPAKATI** (jangan diulang tanya ke رسلان):
- Diskusi dulu sebelum coding kalau scope besar/ambigu
- Kirim file di respons yang sama dengan pekerjaannya
- Edit file PART kalau ada (bukan file hasil merge)
- `node --check` untuk semua JS sebelum diserahkan
- Komunikasi dalam Bahasa Indonesia
- Prefer solusi lebih simpel kalau ada pilihan
- **رسلان TIDAK bisa diakses filesystem-nya langsung** — semua kerja lewat upload/download file di chat. Kalau perlu proses file besar yang ada di PC رسلان (folder `C:\hanyu_extract`, `C:\mandarin_kamus`), tulis skrip Python untuk رسلان jalankan lokal, minta hasilnya diupload balik.

---

## 2. Apa yang sudah dikerjakan (kronologis, sesi terakhir)

### 2.1 Dunia Tata Bahasa (`tatabahasa.html`) — SELESAI & terpasang
- Halaman baru: pilih level HSK → kategori → poin → detail (fungsi + tabel pola Afirmatif/Negatif/dst + tombol 🔊)
- Data sumber: 9 file `.txt` tata bahasa yang رسلان kumpulkan (HSK1: 48 poin s/d HSK9: 70+ poin), di-parse jadi `grammar_hsk1-9.json`
- **Audit HSK7-9 vs acuan resmi (`HSK_7-9.json`, 134 poin) — 100% selesai:**
  - 句子的类型 (kalimat majemuk & pola khusus, 31 poin) ✅
  - 短语 (14 pola AB berulang + 25 penanda wacana, 39 poin) ✅
  - 固定格式 (32 konstruksi idiomatik kompleks) ✅
  - 语段/句群 (7 teknik tingkat wacana: urutan waktu/ruang/logika, topic switching, elipsis) ✅
  - Total HSK7-9 sekarang: **HSK7=90 poin, HSK8=104 poin, HSK9=55 poin**
- **HSK1-6 BELUM diaudit** vs standar resmi (belum ada file acuan resmi seperti `HSK_7-9.json` untuk level ini)

### 2.2 Bacaan Per Tema (`graded-reader.html`) — 18 bacaan baru
Fitur "per tema" ditambahkan: filter chip tema di layar daftar level, badge tema di kartu bacaan.
Bacaan yang sudah dibuat (semua tervalidasi 100% coverage glossary — setiap kata bisa diklik):

| Tema | Level |
|---|---|
| Di Pasar, Di Kelas, Di Restoran | HSK1, 2, 3 (9 bacaan) |
| Di Bandara, Di Rumah Sakit | HSK4 |
| Di Kantor Pos | HSK5 |
| Di Kantor | HSK6 |
| Kesehatan (wabah penyakit) | HSK7 |
| Keluarga | HSK1 |
| Cuaca | HSK2 |
| Olahraga | HSK3 |
| Teknologi | HSK5 |

**Metodologi penting**: kosakata untuk bacaan HSK1-6 divalidasi silang ke `app_words.json` (field `hsk2`). Untuk HSK7-9, **tidak bisa dibedakan per-kata** karena standar HSK 3.0 resmi menggabungkan level 7,8,9 jadi SATU tier kosakata bersama (5.947 kata) — pembeda 7 vs 8 vs 9 ada di kompleksitas tata bahasa/wacana, bukan daftar kata.

**BELUM dikerjakan**: 32 dari 40 tema di `themes_extracted_v2.json` belum dipakai sama sekali (hewan, olahraga sudah, tapi belanja, perjalanan_wisata, komunikasi, perasaan_emosi, arah_lokasi, warna, hobi_hiburan, bisnis_perdagangan, keuangan, dll masih kosong). Level HSK8-9 juga belum ada bacaan sama sekali.

### 2.3 Flashcard — fitur "🟰 Sinonim" — SELESAI & terpasang
Mencerminkan persis fitur "↔ Lawan Kata" yang sudah ada: kartu belakang tampilkan baris Sinonim, deck baru di sidebar, kontrol format soal/jawaban independen, mode game (dengar → pilih sinonimnya). Data dari field `synonyms` di `app_words.json` (sudah diperkaya, lihat §2.5).

### 2.4 Data eksternal ditemukan & diproses
رسلان punya database jauh lebih kaya di `C:\hanyu_extract` dan `C:\mandarin_kamus` (812 file JSON total, lihat `laporan_json.json` kalau perlu re-scan). Yang sudah diproses:

| File | Isi | Status |
|---|---|---|
| `themes_extracted_v2.json` (~8MB) | 40 tema × kosakata dengan hsk3_level | ✅ dipakai sebagian (lihat §2.2). **AWAS**: pinyin/arti kadang salah untuk karakter polifon (ambil bacaan pertama di data mentah, kadang bukan yang umum — mis. 还 tertulis "Huán" padahal umumnya "hái"). Selalu override manual untuk kata fungsi umum. |
| `synonym_antonym_expanded.json` (100 kelompok) | ✅ sudah digabung ke `app_words.json` (synonyms 44→116 kata, antonyms 103→170 kata) |
| `confusion_groups_expanded.json` → gabung jadi `confusion_groups.json` final (53 kelompok) | ✅ data siap, **fitur belum dibangun** (lihat §3) |
| `hsk_7_9_grammar_reference.json` (134 poin resmi) | ✅ dipakai untuk audit §2.1, masih berguna untuk audit ulang kalau ada revisi |
| `hsk_words.json` | ❌ TERNYATA identik 100% dengan `app_words.json` (field beda nama doang) — jangan diproses ulang |
| `hsk_new_words_v2.json` (112rb kata) | ❌ Dicoba jadi kosakata tambahan, ternyata 99.9% karakter langka/kuno tidak berguna — JANGAN dipakai |
| `master_final_hsk.json` (125rb entri CC-CEDICT mentah) | ❌ Dicoba, isinya nomor telepon/istilah teknis/nama tempat asing — TIDAK relevan untuk app belajar |
| `grammar_hsk7-9_expanded.json` + `Daftar_Pola_4-Karakter_yang_Hilang.txt` | ❌ Dicek silang: 20/24 "pola yang hilang" itu TERNYATA levelnya HSK1-6 (sudah ada di situ), bukan HSK7-9 — sumbernya kelihatan tidak tervalidasi ke `HSK_7-9.json` resmi. JANGAN dipakai sebagai acuan HSK7-9. |

---

## 3. TODO — urutan prioritas yang disarankan

1. **Word Builder — 3 perbaikan kecil yang KEBAHAS TAPI BELUM DIKODE** (sempat tertunda karena sesi belok ke Dunia Tata Bahasa):
   - a) Stok tambahan contoh kalimat SALAH di Spot-the-Error, tampil acak
   - b) Kontainer contoh salah cuma tampilkan HANZI dulu; pinyin+keterangan baru muncul setelah klik "Lihat Jawaban"
   - c) Tambah stok contoh kalimat BENAR juga (sama seperti poin a, biar tidak itu-itu saja)
2. **Fitur "Karakter Mirip"** di Flashcard atau Kamus — datanya sudah siap (`confusion_groups.json`, 53 kelompok), tinggal desain UI & kode (bisa cerminkan pola deck Lawan Kata/Sinonim yang sudah ada)
3. **Lanjutkan Bacaan Per Tema** — masih 32 dari 40 tema belum dipakai, dan HSK8-9 belum ada bacaan sama sekali
4. **OCR kamera / loop hover-translate** — wishlist paling lama, belum pernah dibahas kelayakan teknisnya sama sekali
5. **Audit HSK1-6** vs standar resmi — baru bisa jalan kalau رسلان punya/temukan referensi resmi setara `HSK_7-9.json` untuk level di bawahnya

---

## 4. Hal teknis yang perlu diingat

- **Skema `graded_readers_tema*.json`**: array langsung `[...]` (BUKAN dibungkus `{"passages":[...]}`) — ini sempat jadi bug upload, sudah diperbaiki, jangan diulang.
- **Skema tiap bacaan**: `{id, level, tema, title, text, translation, glossary:[{cn,py,id}]}`. `glossary` WAJIB mencakup SETIAP kata di `text` (termasuk partikel seperti 了/的/也) supaya fitur klik-kata jalan. Selalu verifikasi programatis (simulasikan tokenizer greedy-longest-match) sebelum menyerahkan bacaan baru — jangan cuma dicek visual.
- **Skema `grammar_hsk*.json`**: `{level, categories:[{name, points:[{id, number, title, fungsi, table:[{jenis,pola,contoh,pinyin,terjemahan}], reference_table?}]}], kesalahan_umum:[...]}`. Field `reference_table` opsional untuk poin yang bukan pola-kalimat (mis. daftar afiks HSK9).
- **Field HSK di `app_words.json`**: `hsk` (skala lama, 1-6, "7"=luar HSK), `hsk2` (skala baru tapi cuma sampai 6 di dataset ini). **Tidak ada** pembeda HSK7/8/9 di level kosakata — itu memang desain resmi standar HSK 3.0, bukan celah data.
- Semua file baru sesi ini taruh di `C:\mandarin_app\data\` (flat, satu folder saja) kecuali diberi tahu lain.

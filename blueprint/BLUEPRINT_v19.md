# BLUEPRINT — Mandarin Interaktif — v19
_(Handoff document. Baca Bagian A–B dulu untuk onboarding cepat. Bagian C–E untuk detail teknis. Bagian F untuk riwayat sesi.)_

---

## A. Arsitektur Saat Ini (Living Doc)

**Aplikasi:** "Mandarin Interaktif" — aplikasi belajar Mandarin offline, vanilla HTML/CSS/JS, single-user (رسلان), berjalan lokal di `C:\mandarin_app\` (biasanya via `python -m http.server` / `localhost:8000`).

**Sumber data utama** (folder `data/`): `app_words.json` (~11.725 entri), `cidict_index.json` (~125.000 entri, fallback CC-CEDICT), `graded_readers.json` (123 entri, `bacaan` + `percakapan`), `char_etymology_id.json` (100% coverage), `confusion_groups.json` (53 grup). Detail struktur field tidak berubah dari v18 — lihat v18 kalau perlu.

**BARU sejak v19 — sistem checkpoint/backup:** `checkpoint.py` (baru dibuat sesi ini). Membungkus semua `*.py` + isi `data/` jadi file `.zip` bertanggal di folder `backups/`, dengan rotasi otomatis (20 checkpoint terakhir + 1 arsip per bulan). **WAJIB dijalankan** (`python checkpoint.py save`) di awal tiap sesi kerja baru dan setelah tiap `--apply` yang berhasil. Ini jaring pengaman terpisah dari backup `.bak_*` per-script yang sudah ada — dibuat setelah insiden `repair_glossary.py` sempat kosong tanpa jejak (lihat Bagian F).

**Halaman utama, gotcha cache browser:** tidak berubah dari v18.

---

## B. Status Kualitas Data (per akhir sesi 30 Jul 2026, lanjutan)

Melanjutkan audit besar-besaran dari sesi sebelumnya (v18). Total sejauh ini across 2 hari: **~458 kata** di `app_words.json` sudah dikoreksi (428 batch awal + 18 kata manual + 15 kata round 2 — beberapa overlap kemungkinan, angka pasti lihat log tiap batch).

**Audit round 2 (sesi ini) — 15 kata, 2 pola bug baru ditemukan:**
- **Pola A** (bacaan langka/sastra dipromosikan jadi pinyin utama, mirip 上/单 sebelumnya): 号(háo→hào), 看(kān→kàn), 说(shuì→shuō), 落(là→luò), 圈(juān→quān), 藏(zàng→cáng), 结(jiē→jié).
- **Pola B** (nama merek dagang jadi arti pertama, kata majemuk 2+ karakter): 苹果(Apple→apel), 吉利(Geely→baik/beruntung), 标致(Peugeot→cantik), 全家(FamilyMart→seluruh keluarga), 老板(Robam→bos/pemilik bisnis).
- **Bug field lain** (bukan cuma urutan): 假 (field `pinyin`+`traditional` salah total: "gēi"/"叚" → "jiǎ"/"假"), 血 (baris arti sampah "lihat 血[xue4]" referensi ke diri sendiri, dihapus), 严寒 (typo spasi "yangMenusuk"→"yang menusuk").
- **Temuan pola baru**: beberapa entri (假, 老板, 说) punya baris "varian dari X[...]" yang ternyata **referensi ke diri sendiri** (self-referential garbage) — bukan cuma bacaan/arti salah, tapi baris sampah murni. Dihapus saat perbaikan.
- Semua 15 kata sudah disinkronkan ke `graded_readers.json` (46 entri, 58 kata diperbarui, 0 masih mencurigakan).

**Sisa backlog dari v18 (belum dikerjakan sesi ini):**
- 18 kata "exclude/mencurigakan" dari BLUEPRINT v18 (以, 现代, 大众, 大学, 美德, 比, 率, 红, 上, 新, 加, 哈, 单, 保, 签, 佛, 扬, 头条) — **SUDAH SELESAI di awal sesi ini**, jangan bingung dgn daftar v18 yang menganggapnya belum selesai.
- Kata ambigu yang SENGAJA tidak difix (bacaan sama-sama umum tergantung konteks, sulit tentukan default): **差** (chà/chā/chāi/cī), **曲** (qū/qǔ). Prioritas rendah, revisit kalau ada laporan pengguna konkret.

**File backup penting (folder `data/`, JANGAN dihapus):** semua backup dari v18 tetap berlaku, ditambah:
- `app_words.bak_manual18_20260730_173849.json` — baseline sebelum batch 18-kata manual.
- `app_words.bak_round2_20260730_190609.json` — baseline sebelum batch 15-kata round 2. **Baseline PALING AKURAT untuk audit round 3 nanti** (lebih presisi dari file bak_manual18 yang mencakup 2 putaran sekaligus).
- `graded_readers.json.bak_20260730_194328` — sebelum sync glossary round 2.
- `backups/checkpoint_20260730_195004.zip` — checkpoint pertama sistem baru (lihat Bagian A).

---

## C. Script Baru Sesi Ini

| Script | Fungsi | Catatan |
|---|---|---|
| `audit_known_polyphones.py` | Audit read-only kandidat karakter polifonik umum HSK1-6 (~16 kandidat) yang rawan "bacaan jarang jadi default" | Read-only. Daftar kandidat di kode, bisa diperluas |
| `audit_brand_first_meaning.py` | Audit read-only seluruh `app_words.json`, cari kata majemuk (2+ karakter) dengan nama merek/proper-noun di arti pertama | Read-only. Banyak false positive (nama tempat/app yang memang benar) — WAJIB sample-check manual |
| `fix_15_words_round2.py` | Perbaiki 15 kata dari 2 audit di atas | Sudah dieksekusi & selesai. `--dry-run` wajib dulu (pola sama dgn script v18) |
| `checkpoint.py` | Sistem backup/versioning menyeluruh (lihat Bagian A) | **Pakai rutin mulai sekarang** |
| `extract_12_words.py`, `extract_3_words.py` | Script sekali-pakai untuk intip entri lengkap saat investigasi sesi ini | Bisa diabaikan, sudah tidak perlu dipakai ulang |

**Insiden teknis sesi ini:** `repair_glossary.py` sempat berubah jadi 0 bytes tanpa jejak penyebab (Previous Versions nonaktif, Notepad++ tidak simpan riwayat lokal, Recycle Bin kosong). Dipulihkan dari salinan yang رسلان masih punya dari chat sebelumnya — **bukan** rekonstruksi tebakan. Ini pemicu langsung dibuatnya `checkpoint.py`.

---

## D. Metodologi (tidak berubah dari v18, tetap terbukti efektif)

1. Audit dulu (read-only) → sample-check manual → fix dgn `--dry-run` wajib → baru eksekusi.
2. Script sync lintas-fitur (`repair_glossary.py`) HARUS scope ke kata TERVERIFIKASI berubah via `--baseline`, bukan percaya "state sekarang" membabi buta.
3. Heuristik otomatis tidak akan pernah 100% — proses berkelanjutan, bukan target selesai total. Audit round 2 sesi ini membuktikan ini: heuristik `DEPRIORITIZE_MARKERS` (v18) tidak menangkap pola baru (bacaan langka tanpa label eksplisit, nama merek di kata majemuk) — perlu heuristik kandidat/regex terpisah per pola.
4. **BARU:** jalankan `python checkpoint.py save` di awal tiap sesi kerja dan setelah tiap `--apply` berhasil. Ini bukan pengganti backup `.bak_*` per-script (yang tetap jalan otomatis), tapi lapisan tambahan yang mencakup SEMUA script sekaligus, untuk kasus file individual rusak/kosong tanpa peringatan.
5. Saat memilih `--baseline` untuk `repair_glossary.py` di sesi mendatang, pakai backup app_words.json **PALING BARU sebelum batch terakhir**, bukan baseline yang menumpuk beberapa putaran (lebih presisi, walau menumpuk juga terbukti tetap aman krn sifat idempotent script).

---

## E. Prioritas Tugas Berikutnya

1. **Dashboard `index.html`** — belum diupdate refleksikan 123 entri graded reader + jenis konten percakapan (item lama, masih belum dikerjakan).
2. **QA manual** untuk 15 kata round 2 (belum dilakukan sesi ini — disarankan sebelum lanjut audit round 3) — terutama cek tampilan 落/圈/藏/结 di `graded-reader.html` dan Kamus, karena perubahan pinyin utama pada karakter-karakter ini cukup signifikan.
3. **Audit round 3** — kandidat lanjutan: 差, 曲 (ambigu, butuh keputusan konteks), plus kemungkinan pola bug baru lain yang belum ketahuan. Bisa jalankan `audit_known_polyphones.py`/`audit_brand_first_meaning.py` lagi dengan daftar kandidat diperluas.
4. **Evaluasi Git** sebagai upgrade dari `checkpoint.py` (opsional, didiskusikan tapi belum diputuskan — checkpoint.py dianggap cukup untuk saat ini).
5. Lanjutkan pola living-doc + changelog terpisah (BLUEPRINT v19 ini konsisten dgn pola v18).

---

## F. Riwayat Sesi (changelog)

**Sesi 30 Jul 2026 (lanjutan, sore–malam)** (sesi ini): Melanjutkan dari v18 — eksekusi 18 kata manual (exclude+mencurigakan) yang tersisa dari v18, lalu audit round 2 menemukan 2 pola bug baru (bacaan langka tanpa label eksplisit; nama merek di kata majemuk) via 2 script audit read-only baru, temukan & fix 15 kata tambahan (termasuk 2 bug field non-urutan: 假 pinyin+traditional salah total, 血 baris sampah self-referential). Insiden `repair_glossary.py` kosong tanpa jejak → dipulihkan dari salinan chat → dibuatkan `checkpoint.py` sbg jaring pengaman baru. Total kata diperbaiki sesi ini: 18+15=33 kata, disinkronkan penuh ke `graded_readers.json` (103 entri, 145 kata glossary diperbarui gabungan 2 batch).

**Sebelumnya (lihat BLUEPRINT_v18 utk detail lengkap):** Audit sistemik besar-besaran 428 kata + patch override + sinkronisasi glossary awal (69→104→123 entri graded reader), dst.

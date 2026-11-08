# BLUEPRINT — Mandarin Interaktif — v18
_(Handoff document. Baca Bagian A–B dulu untuk onboarding cepat. Bagian C–E untuk detail teknis. Bagian F untuk riwayat sesi.)_

---

## A. Arsitektur Saat Ini (Living Doc — selalu update bagian ini, jangan cuma tambah di bawah)

**Aplikasi:** "Mandarin Interaktif" — aplikasi belajar Mandarin offline, vanilla HTML/CSS/JS, single-user (رسلان), berjalan lokal di `C:\mandarin_app\` (biasanya via `python -m http.server` / `localhost:8000`).

**Sumber data utama** (folder `data/`):
- `app_words.json` (~11.725 entri) — kamus prioritas utama. Field: `simplified`, `pinyin`, `pinyin_numeric`, `bopomofo`, `hsk`, `hsk2`, `frequency` (makin kecil = makin sering dipakai), `pos`, `meanings_id`, `meanings_en`, `radical`, `stroke_count`, `themes`, `synonyms`, `antonyms`, dll.
- `cidict_index.json` (~125.000 entri, berbasis CC-CEDICT) — fallback kalau kata tidak ada di `app_words.json`. Field lebih ringkas: `simplified`, `pinyin`, `meanings_id`. **Satu hanzi bisa punya banyak entri** (bacaan berbeda-beda: umum, marga, sastra, dst) — ini sumber utama bug bacaan yang ditemukan sesi ini (lihat Bagian F).
- `graded_readers.json` (123 entri) — bacaan (`type: "bacaan"`) dan dialog (`type: "percakapan"`) berbagi satu file, dibedakan field `type`. Percakapan pakai `turns` (list `{speaker, cn}`), keduanya pakai `glossary` (list `{cn, py, id}`) sebagai daftar kosakata yang sudah diresolusi.
- `char_etymology_id.json` — 100% coverage (2.840 karakter), etimologi + gloss Indonesia.
- `confusion_groups.json` — 53 grup karakter mirip, dipakai game "Karakter Mirip".

**Pipeline generate bacaan baru:** `complete_reading_json.py`
- Tokenizer greedy longest-match: `app_words.json` (prioritas) → `cidict_index.json` (fallback).
- `COMMON_READING_OVERRIDE` (dict di dalam file, ~25 karakter: 都,和,要,更,得,中,着,数,还,只,长,行,分,少,倒,重,难,当,校,传,曾,系,为,会,没) — override manual utk karakter yang terbukti sering salah baca. **Prioritas MUTLAK**, dicek sebelum apa pun (termasuk sebelum `app_words.json`).
- `DEPRIORITIZE_MARKERS` = `('marga ', 'varian', '(sastra)', 'nama keluarga', '(bentuk terikat)')` — dipakai `pick_best_cidict_entry()` utk hindari bacaan langka saat fallback ke cidict. **Heuristik ini TIDAK sempurna** — lihat Bagian F, ada pola bad-reading lain yang tidak tertangkap (singkatan negara, bound-form yang sebenarnya umum, arti kiasan).
- Field `names` (dari file JSON mentah `percakapan_json/`, `tema_json/`) mencegah tokenizer salah pecah nama tokoh — **TIDAK tersimpan di entri final** `graded_readers.json` (hanya memengaruhi glossary yang dihasilkan saat generate).

**Halaman utama:** `index.html` (dashboard — belum update refleksikan 123 entri + percakapan), `kamus.html` (modularized: `kamus/` subfolder, 8 file JS), `flashcard` (SRS, game deck, audio "Jebakan Nada"), `tone.html` (drill nada + statistik), `graded-reader.html` (bacaan + percakapan bubble-chat), `hsk-exam.html`, `terjemah-bebas.html`, `tatabahasa.html` (5-layar), Word Builder.

**Gotcha penting:** cache browser `localhost:8000` sering bikin data terlihat tidak sinkron padahal file sudah diupdate — fix: `F12 → Application → Storage → Clear site data`.

---

## B. Status Kualitas Data (per akhir sesi 30 Jul 2026)

Sesi ini (29–30 Jul 2026) adalah **audit & perbaikan besar-besaran kualitas bacaan/arti** di `app_words.json`, dipicu temuan bug "都" (kepilih bacaan marga "Dū" padahal seharusnya "dōu"=semua).

- **428 kata** di `app_words.json` sudah dikoreksi (bacaan dan/atau urutan arti default) melalui audit sistematis.
- **667 entri glossary** di **119 dari 123** entri `graded_readers.json` sudah disinkronkan mengikuti perbaikan itu.
- **8 kata SENGAJA dikecualikan** dari sinkronisasi (perbaikan otomatis untuk kata ini sendiri kurang tepat, arti defaultnya jadi nama merek/negara/kiasan yang salah — butuh perbaikan manual di `app_words.json` dulu sebelum disinkronkan ke graded_readers.json): **以, 现代, 大众, 大学, 美德, 比, 率, 红**.
- **10 kata masih ditandai "mencurigakan"** meski sudah disinkronkan (bacaan/nada-nya sudah benar, tapi artinya masih kurang ideal — prioritas lebih rendah): **上, 新, 加, 哈, 单, 保, 签, 佛, 扬, 头条**.
- **Bug LAMA yang TIDAK terkait** pekerjaan sesi ini, ditemukan tapi SENGAJA TIDAK disentuh (di luar cakupan yang divalidasi): **号** (háo harusnya hào/nomor), **看** (kān harusnya kàn/menonton), **说** (shuì harusnya shuō/berkata), **带** (arti "pita" harusnya "membawa" di beberapa konteks), **老板** ("Robam merek" harusnya "pemilik toko"). Ini backlog terpisah untuk audit lanjutan.

**File backup penting (folder `data/`, JANGAN dihapus):**
- `app_words.json.bak_20260729_221158` — **baseline SEBELUM semua perbaikan sesi ini dimulai**. Dipakai sebagai referensi `--baseline` oleh `repair_glossary.py`. Kalau nanti ada perbaikan susulan ke 18 kata di atas, baseline ini tetap yang dipakai untuk hitung ulang cakupan.
- `app_words.json.bak_override_20260730_071443` — snapshot sebelum koreksi 9 kata `COMMON_READING_OVERRIDE`.
- `graded_readers.json.bak_20260730_133133` — snapshot sebelum sinkronisasi glossary.

---

## C. Script Baru Sesi Ini (semua di `C:\mandarin_app\`, sejajar `complete_reading_json.py`)

| Script | Fungsi | Catatan |
|---|---|---|
| `audit_polysemy_batch.py` | Audit kata multi-pinyin di batch tertentu `graded_readers.json` (baca dari `glossary` tersimpan, bukan re-tokenisasi — aman utk nama tokoh) | Read-only. `--last N` / `--ids ...` |
| `audit_app_words_readings.py` | Audit SISTEMATIS seluruh `app_words.json` — cari kata dgn bacaan/arti default mencurigakan (marga/varian/sastra/bentuk-terikat) padahal ada alternatif umum | Read-only. `--hsk-only` opsional |
| `fix_app_words_readings.py` | Perbaiki `app_words.json` berdasar temuan audit di atas | **WAJIB `--dry-run` dulu**. Sudah ditambal utk selalu hormati `COMMON_READING_OVERRIDE` (bug awal: jalur "SEDANG" pernah mengabaikannya) |
| `patch_override_words.py` | Koreksi khusus 25 kata di `COMMON_READING_OVERRIDE` (re-cek match app_words vs override, walau kelihatan "sudah benar" secara heuristik umum) | `--dry-run` dulu |
| `repair_glossary.py` (v2, scoped) | Sinkronkan `graded_readers.json` mengikuti perbaikan `app_words.json` | **WAJIB `--baseline <path_backup>`** (scope ke kata yang TERVERIFIKASI berubah, bukan percaya seluruh app_words.json — supaya bug lama tak terkait tidak ikut ter-propagate). Dukung `--exclude kata1 kata2 ...` |
| `extract_flagged_words.py`, `sample_dict_structure.py` | Script sekali-pakai untuk verifikasi/intip struktur data saat debugging sesi ini | Bisa diabaikan/dihapus, sudah tidak perlu dipakai ulang |

---

## D. Metodologi yang Terbukti Efektif (replikasi untuk audit data-quality lain nanti)

1. **Audit dulu (read-only report) → sample-check manual bareng رسلان → fix dgn `--dry-run` wajib → baru eksekusi.** Jangan pernah lompat ke eksekusi.
2. **Untuk perbaikan yang menyentuh data dipakai banyak fitur** (spt `app_words.json`, dipakai Kamus/Flashcard/WordBuilder/graded-reader sekaligus): script turunan (spt `repair_glossary.py`) HARUS scope ke kata yang **TERVERIFIKASI berubah** (baseline diff), JANGAN percaya "state sekarang" secara membabi buta — ada bug data lama tak terkait yang bisa ikut ter-propagate kalau tidak di-scope (kasus nyata: 号/看/说/带/老板).
3. **Heuristik "kata langka" (`DEPRIORITIZE_MARKERS`) tidak sempurna** — pola bad-default terus bermunculan dalam bentuk baru (singkatan negara, bound-form yang sebenarnya umum, arti kiasan/derivatif). Pendekatan pragmatis yang disepakati: **jangan kejar 100% otomatis** — proses berkelanjutan, tambal manual berdasar laporan pengguna saat pakai aplikasi sehari-hari, bukan coba tangkap semua di depan.
4. Selalu test script baru dengan **data sintetis** yang meniru persis kasus edge yang jadi perhatian (termasuk kasus kontrol yang HARUS tidak berubah) sebelum diserahkan ke رسلان.

---

## E. Prioritas Tugas Berikutnya

1. **Perbaiki manual 18 kata** (8 exclude + 10 masih-mencurigakan, lihat Bagian B) di `app_words.json`, lalu re-run `repair_glossary.py` (tanpa exclude untuk kata yang sudah dibetulkan) memakai baseline yang sama.
2. **Audit lanjutan** utk pola bug seperti 号/看/说/带/老板 (bug lama, di luar cakupan sesi ini) — mungkin perlu heuristik baru sama sekali karena tidak match `DEPRIORITIZE_MARKERS`.
3. **Dashboard `index.html`** — belum diupdate refleksikan 123 entri graded reader + jenis konten percakapan (item lama, belum dikerjakan).
4. **Strategi backup/versioning menyeluruh** untuk `data/*.json` (item lama, belum dikerjakan — saat ini baru ada backup otomatis per-script).
5. (Selesai sebagian) Restrukturisasi format BLUEPRINT jadi living-doc + changelog terpisah — diterapkan mulai v18 ini, lanjutkan pola ini ke v19 dst.

---

## F. Riwayat Sesi (changelog, boleh dibaca kalau perlu konteks historis — tidak wajib dibaca ulang tiap sesi baru)

**Sesi 29–30 Jul 2026** (sesi ini): Dipicu kecurigaan dari QA batch 19 entri graded reader terbaru (resolusi kata polisemis belum tervalidasi). Alur penemuan: `audit_polysemy_batch.py` → ketemu pola "都" salah baca → `audit_app_words_readings.py` (scan penuh) → ketemu ~430 kata bermasalah, ternyata sistemik (bug lama "都" cuma puncak gunung es) → `fix_app_words_readings.py` (dengan 1 bug ditemukan & ditambal: prioritas `COMMON_READING_OVERRIDE` diabaikan di jalur "sedang") → `patch_override_words.py` (koreksi 9 kata tambahan) → `repair_glossary.py` v1 (bug: sync membabi buta, propagate bug lama tak terkait spt 号/看/说) → v2 scoped dengan `--baseline` + `--exclude` → eksekusi final: 428 kata app_words.json + 667 entri glossary diperbaiki di 119/123 entri.

**Sebelumnya (lihat BLUEPRINT_v17 kalau perlu detail lengkap):** Pipeline `complete_reading_json.py` utk import bacaan/percakapan bertahap dibangun; tab percakapan bubble-chat; audit/merge overlap tema; `repair_theme_word_sync.py` (fix desync tag tema→kata); modularisasi `kamus.html`; graded readers 69→104→123 entri; tools grammar/etimologi/mnemonic/tone-drill; dsb (lihat versi sebelumnya untuk detail per fitur).

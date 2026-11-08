# BLUEPRINT — Mandarin Interaktif — v24
_(Handoff document. Baca Bagian A–B dulu untuk onboarding cepat. Bagian C–E untuk detail teknis. Bagian F untuk riwayat sesi.)_

---

## A. Arsitektur Saat Ini (Living Doc)

**Aplikasi:** "Mandarin Interaktif" — aplikasi belajar Mandarin offline, vanilla HTML/CSS/JS, single-user (رسلان), berjalan lokal di `C:\mandarin_app\` (biasanya via `python -m http.server` / `localhost:8000`).

**Sumber data utama** (folder `data/`): `app_words.json` (~11.726 entri), `cidict_index.json` (~125.000 entri, fallback CC-CEDICT), `graded_readers.json` (123 entri), `char_etymology_id.json` (2.840 karakter), `confusion_groups.json` (53 grup), `nuance_pairs.json` (1.291 pasangan), `produktif_karakter.json` (1.389 akar karakter, 16.179 kata turunan), **`kata_majemuk_pola.json` (BARU sesi ini — 8.867 kata 2-karakter, masing-masing berlabel salah satu dari 6 pola pembentukan kata majemuk, lihat Bagian A.4).**

**Isu berulang (masih relevan):** browser sering nge-cache file lama di `localhost:8000`. Fix: `F12 → Application → Storage → Clear site data`, kadang perlu diulang beberapa kali.

**File JS termodularisasi:** `kamus.html` → 9 file di folder `kamus/` (termasuk `kamus-nuance.js`, berdiri sendiri lewat `fetch('data/nuance_pairs.json')` + `MutationObserver` di `#d-hanzi`, tidak mengubah `kamus-detail.js`). `flashcard.html` → 6 file. `wordbuilder.html` — dikonfirmasi sesi ini berisi latihan **pola KALIMAT** (S+是+O, S+有+O, dst.), BUKAN pembentukan kata — beda lapisan sepenuhnya dari fitur A.4 baru.

---

### A.1 — Fitur "🆚 Beda dengan Kata Mirip" (Kamus) + "🎯 Pilih yang Tepat" (Flashcard)

Tidak berubah dari v23. 1.291 pasangan, `kamus-nuance.js` berjalan normal, 2.558 soal di flashcard. Accordion untuk 1 kata → >1 pasangan **belum diperlukan** (desain pipeline no-overlap constraint mencegah kasus ini di data saat ini) — TIDAK dikerjakan sesi ini, رسلان memutuskan tidak perlu untuk saat ini.

---

### A.2 — Fitur "🌱 Akar Kosakata"

Tidak berubah dari v23. **رسلان sudah konfirmasi tes di HP asli, tampilan oke.** Follow-up dari v22/v23 dianggap SELESAI.

---

### A.3 — Bersih-bersih file sisa pipeline nuance_pairs

**SELESAI.** رسلان sudah menghapus file-file sisa yang tidak relevan (`batch1/2/3_nuance_pairs.json`, `daftarA_clean_pairs.txt`, dll — daftar lengkap di BLUEPRINT v23 Bagian A.3).

---

### A.4 — BARU: Fitur "Pola Pembentukan Kata Majemuk" — Data SELESAI Dikurasi, UI BELUM Dibangun

**Konsep:** klasifikasi struktur gramatikal internal kata 2-karakter Mandarin ke 6 kategori: 联合式 (koordinatif/sinonim), 偏正式 (modifier-head), 动宾式 (verba-objek), 主谓式 (subjek-predikat), 补充式 (verba-komplemen), lainnya (serapan/kata fungsi/tidak jelas). **Beda total dari `wordbuilder.html`** (yang mengajarkan pola KALIMAT, bukan struktur internal kata) — dua lapisan gramatika berbeda, tidak tumpang tindih.

**Cakupan:** HANYA kata 2-karakter (skema 5-pola dirancang khusus untuk itu). Kata 3+ karakter (1.287 kata, tersimpan di `kata_majemuk_3plus_INFO_ONLY.json`) **sengaja dikecualikan** — butuh skema berjenjang/rekursif berbeda, belum dirancang, رسلان setuju dibahas terpisah nanti kalau diminta.

**Pipeline yang dibangun (mirip pola hybrid Claude + AI eksternal dari nuance_pairs, tapi untuk KLASIFIKASI bukan generasi konten):**
1. `scope_kata_majemuk_full.py` — scoping read-only, hasilkan `kata_majemuk_candidates_2char_ALL.json` (8.867 kata, semua level HSK termasuk HSK 7-9 dan tanpa HSK) + `kata_majemuk_3plus_INFO_ONLY.json` (1.287 kata, referensi saja).
2. `prepare_next_chunk.py` — siapkan chunk 250 kata berikutnya yang belum diklasifikasi, tracking otomatis lewat `kata_majemuk_pola.json` yang sudah ada.
3. `PROMPT_untuk_AI_pola_majemuk.md` — prompt klasifikasi awal, skema 6 kategori + contoh.
4. `import_kata_majemuk_batch.py` — validasi (existence check, pola valid, no-duplicate) + `json.dump` aman (atomic write via `.tmp` + rename) ke `kata_majemuk_pola.json`.
5. Dijalankan ~36 batch sampai semua 8.867 kata terklasifikasi.

**QA & perbaikan pasca-klasifikasi awal (SEMUA SELESAI sesi ini):**
- `audit_kata_majemuk_pola.py` — cek kelengkapan, duplikat, distribusi kategori, kualitas `keterangan_id` (flag kalimat generik dipakai >10x), sanity check panjang kata, sampling acak per kategori untuk tinjauan manual.
- **Perbaikan `keterangan_id` generik** (47 kata, mis. nama kota, kata sapaan ganda, kata kerja arah) — via `extract_recheck_batches.py keterangan` + `PROMPT_perbaiki_keterangan.md` + `import_corrections.py`. Selesai, semua diterapkan.
- **Reklasifikasi ulang penuh 主谓式** (106 kata) — ditemukan Claude lewat tinjauan manual bahwa AI eksternal sering salah urutan subjek-predikat (mis. 发炎 seharusnya 动宾式 bukan 主谓式). Via `extract_recheck_batches.py subjek-predikat` + `PROMPT_reklasifikasi_subjek_predikat.md` (aturan ketat: subjek wajib di posisi 1, partikel negasi tidak boleh jadi "subjek"). 85/106 berhasil direklasifikasi. 1 anomali kecil (痛心) dibiarkan, dampak diabaikan.
- **Verifikasi 动宾式/补充式 (1.685+356=2.041 kata) — DIHENTIKAN, tidak selesai sepenuhnya.** AI eksternal رسلان pakai terbukti TIDAK ANDAL untuk tugas verifikasi bernuansa ini: berulang kali (4× percobaan, termasuk dengan prompt v2 yang jauh lebih ketat) menandai ratusan kata umum sebagai `联合式` secara serampangan, termasuk kesalahan jelas (kata dengan komplemen arah/hasil seperti verba+到/见/住/着, kata dengan objek konkret seperti 生病/开会/收费, partikel gramatikal 于/为 dianggap sinonim). **Batch yang gagal (balasan40) di-revert penuh.** Batch-batch berikutnya (41-44) DITINJAU MANUAL SATU-PER-SATU oleh Claude (bukan diterima mentah), dengan proses penyaringan bertingkat (`filter_balasan41.py` → `filter_balasan41_v2.py`, mengecualikan ~66 kata bermasalah yang teridentifikasi dari tinjauan manual). Hasil akhir: total ~346 koreksi 动宾式/补充式→联合式 diterapkan (dari balasan41 terfilter + 42 + 43 + 44), SISANYA (~1.700 kata) TIDAK diverifikasi lebih lanjut — dibiarkan dengan klasifikasi awal, dianggap "cukup baik" berdasarkan tinjauan sampel awal, dengan potensi kesalahan minor tersisa yang bisa diperbaiki manual kalau ditemukan رسلان saat pakai app.

**Insight penting dicatat untuk pola kerja serupa ke depan:** tugas KLASIFIKASI (memilih 1 dari N kategori tetap) ternyata TIDAK sama mudahnya dengan tugas GENERASI KONTEN terstruktur (seperti nuance_pairs) untuk didelegasikan ke AI eksternal tanpa pengawasan ketat — AI eksternal رسلان pakai jauh lebih rentan generalisasi berlebihan pada tugas klasifikasi bernuansa (menandai hampir semua kata ke 1 kategori "aman") dibanding tugas menulis konten per-item. Ke depan, kalau ada tugas klasifikasi serupa: (a) uji dengan sampel kecil dulu sebelum batch besar, (b) siapkan aturan pengecualian eksplisit di prompt SEJAK AWAL (bukan setelah insiden), (c) tetap rencanakan tinjauan manual sampel oleh Claude sebagai lapisan verifikasi terakhir, jangan asumsikan validasi struktural (JSON valid, existence check) cukup untuk menjamin kualitas linguistik.

**File yang masih ada di `C:\mandarin_app\` terkait fitur ini (semua REUSABLE untuk maintenance/ekstensi masa depan, TIDAK perlu dihapus):**
`kata_majemuk_candidates_2char_ALL.json`, `kata_majemuk_3plus_INFO_ONLY.json`, `kata_majemuk_pola.json` (hasil akhir, 8.867 kata), `scope_kata_majemuk_full.py`, `prepare_next_chunk.py`, `import_kata_majemuk_batch.py`, `audit_kata_majemuk_pola.py`, `extract_recheck_batches.py`, `import_corrections.py`, `revert_batch.py`, `reset_verifikasi_tracking.py`, prompt-prompt terkait (`PROMPT_untuk_AI_pola_majemuk.md`, `PROMPT_perbaiki_keterangan.md`, `PROMPT_reklasifikasi_subjek_predikat.md`, `PROMPT_verifikasi_dongbin_buchong_v2.md`).

**Boleh dihapus/diabaikan (sisa proses gagal, tidak reusable):** `balasan*.txt` (semua file balasan AI), `chunk_*_to_send.txt`, `next_chunk_to_send.txt`, `balasan41_FILTERED*.txt`, `verifikasi_reviewed_words.json`, `audit_sample_for_review.json`.

**BELUM DIKERJAKAN — prioritas sesi berikutnya:** integrasi tampilan `kata_majemuk_pola.json` ke `kamus.html`, mirip pola `kamus-nuance.js` (berdiri sendiri, fetch data sendiri, tidak mengubah `kamus-detail.js`, sembunyi otomatis kalau kata tidak ada di data). Belum ada rancangan teknis UI-nya sama sekali — akan dibahas dari nol di percakapan baru.

---

## B. Status Kualitas Data

**`kata_majemuk_pola.json` — 8.867 kata 2-karakter, SELESAI DIKLASIFIKASIKAN, kualitas BAIK dengan catatan.** Distribusi akhir kira-kira: 偏正式 (~43%) dan 联合式 (~29%, naik dari 27% awal berkat koreksi manual) adalah kategori terbesar, 动宾式 (~19%), lainnya (~6%), 补充式 (~4%), 主谓式 (~1%, sudah direklasifikasi ketat). 主谓式 dan `keterangan_id` generik sudah diperbaiki tuntas. Kategori 动宾式/补充式 punya potensi kesalahan minor tersisa (~1.700 kata belum diverifikasi ulang) — TIDAK dianggap blocker untuk lanjut ke UI, tapi رسلان perlu tahu ini bukan data 100% sempurna.

**`nuance_pairs.json`, `graded_readers.json`, `app_words.json`, `produktif_karakter.json`** — tidak berubah dari v23.

---

## C. Script/File Sesi Ini (v24)

**Pipeline klasifikasi awal:** `scope_kata_majemuk.py` (versi awal, digantikan), `scope_kata_majemuk_full.py` (versi final dipakai), `prepare_next_chunk.py`, `import_kata_majemuk_batch.py`, `PROMPT_untuk_AI_pola_majemuk.md`.

**QA & koreksi:** `audit_kata_majemuk_pola.py`, `extract_recheck_batches.py` (3 mode: keterangan/subjek-predikat/verifikasi), `import_corrections.py`, `revert_batch.py`, `reset_verifikasi_tracking.py`, `filter_balasan41.py`, `filter_balasan41_v2.py`.

**Prompt:** `PROMPT_perbaiki_keterangan.md`, `PROMPT_reklasifikasi_subjek_predikat.md`, `PROMPT_verifikasi_dongbin_buchong.md` (v1, gagal), `PROMPT_verifikasi_dongbin_buchong_v2.md` (v2, masih gagal untuk AI eksternal رسلان, tapi tetap disimpan sebagai referensi kalau nanti dicoba AI eksternal lain).

**Dari sesi sebelumnya, tidak berubah:** semua script v18-v23 (`checkpoint.py`, pipeline nuance_pairs, pipeline Akar Kosakata, dll — lihat BLUEPRINT v23 Bagian C).

---

## D. Metodologi

**Pola baru penting dari sesi ini — batas kepercayaan pada AI eksternal untuk tugas KLASIFIKASI:** tidak semua tugas yang "terlihat mekanis" (skema jelas, tinggal pilih 1 dari N kategori) benar-benar aman didelegasikan penuh ke AI eksternal tanpa pengawasan. Tugas GENERASI konten terstruktur (nuance_pairs) terbukti bisa diandalkan dengan validasi struktural saja (existence check, no-overlap, format JSON). Tugas KLASIFIKASI bernuansa (pola majemuk) TERBUKTI TIDAK — perlu tinjauan manual sampel oleh Claude sebagai lapisan wajib, bukan opsional, SEBELUM data diterapkan skala besar. Ke depan: untuk tugas klasifikasi serupa, rencanakan dari awal alur "AI eksternal → dry-run → tinjauan manual sampel oleh Claude → baru terapkan", jangan asumsikan validasi otomatis (JSON valid + existence check) cukup.

**Pola baru — tahu kapan berhenti mengejar kesempurnaan data:** setelah 4× percobaan verifikasi 动宾式/补充式 gagal dengan pola sama, diputuskan berhenti (bukan terus mencoba prompt v3, v4, dst.) karena fitur ini pelengkap bukan inti aplikasi, dan sisa potensi kesalahan (~1.700 dari 8.867 kata, sebagian besar kemungkinan tetap benar) tidak sepadan dengan waktu tambahan. Prinsip: "cukup baik" boleh menjadi kondisi berhenti yang sah, tidak semua ketidaksempurnaan harus dikejar sampai tuntas.

**Pola dari v23 (audit/fix data, checkpoint sebelum perubahan besar) tetap berlaku, tidak berubah.**

---

## E. Prioritas Tugas Berikutnya

1. **PRIORITAS UTAMA (disepakati untuk percakapan baru):** Desain & bangun integrasi tampilan `kata_majemuk_pola.json` ke `kamus.html`. Belum ada rancangan sama sekali — mulai dari nol: keputusan UI (di mana panel ditaruh di halaman detail Kamus, bagaimana styling-nya, apakah perlu game/latihan terpisah seperti "Pilih yang Tepat" atau cukup panel informasi seperti "Beda dengan Kata Mirip"), lalu implementasi teknis (kemungkinan besar file JS berdiri sendiri baru, mengikuti pola `kamus-nuance.js`).

2. **(Opsional, prioritas rendah, kalau رسلان mau lanjutkan nanti)** Verifikasi lanjutan sisa ~1.700 kata 动宾式/补充式 yang belum ditinjau — kemungkinan besar tidak dikerjakan lagi via AI eksternal yang sama (terbukti tidak andal), mungkin butuh AI eksternal berbeda atau dibiarkan permanen sebagai keterbatasan diketahui.

3. **(Opsional, kalau diminta di masa depan)** Skema untuk kata 3+ karakter (`kata_majemuk_3plus_INFO_ONLY.json`, 1.287 kata) — butuh pendekatan berjenjang/rekursif, belum ada rancangan teknis sama sekali.

4. **(Opsional, prioritas rendah)** Accordion `kamus-nuance.js` untuk 1 kata → >1 pasangan — tetap dianggap tidak perlu untuk saat ini (lihat A.1), dicatat ulang di sini murni untuk kelengkapan riwayat.

5. Lanjutkan pola living-doc + changelog terpisah.

---

## F. Riwayat Sesi (changelog)

**Sesi ini (v24):** **Klasifikasi struktur pola pembentukan kata majemuk untuk 8.867 kata 2-karakter**, fitur baru "Pola Pembentukan Kata Majemuk". Ringkasan:
1. Dijelaskan konsep 5 pola gramatikal (联合式/偏正式/动宾式/主谓式/补充式) dan dibedakan dari `wordbuilder.html` (pola kalimat, bukan pola kata) berdasarkan pembacaan langsung isi file tersebut.
2. Scoping: total 8.867 kata 2-karakter (semua level HSK termasuk HSK 7-9 dan tanpa HSK) dan 1.287 kata 3+ karakter (dikecualikan, referensi saja) ditemukan dari `app_words.json` (11.726 entri total).
3. Pipeline klasifikasi dibangun: kandidat → chunk 250 kata/batch → AI eksternal → validasi & impor aman (atomic write). ~36 batch dijalankan sampai semua 8.867 kata terklasifikasi.
4. Audit otomatis (`audit_kata_majemuk_pola.py`) + tinjauan manual sampel oleh Claude menemukan 2 masalah signifikan: (a) `keterangan_id` generik dipakai berulang untuk banyak kata berbeda — diperbaiki (47 kata), (b) kategori 主谓式 banyak salah urutan subjek-predikat — direklasifikasi ulang dengan aturan ketat (85/106 kata berubah).
5. **Insiden signifikan:** upaya verifikasi kategori 动宾式/补充式 (mencari kasus yang seharusnya 联合式) gagal berulang kali — AI eksternal رسلان pakai secara sistematis over-generalisasi, menandai ratusan kata umum (termasuk pola verba+komplemen arah seperti 想到/看到/学会, dan verba+objek konkret seperti 开会/收费) sebagai "sinonim" padahal jelas bukan. Dicoba 2 versi prompt (longgar dan sangat ketat dengan daftar hitam eksplisit) — keduanya gagal dengan pola sama. Satu batch penuh (430 kata, balasan40) di-revert total setelah diterapkan tanpa tinjauan cukup ketat.
6. **Pemulihan:** batch-batch berikutnya (41-44) DITINJAU MANUAL oleh Claude satu-per-satu (bukan diterima berdasarkan pola/asumsi) — proses ini sendiri melalui 2 putaran koreksi (Claude sempat salah menolak balasan43/44 berdasarkan pola dari batch gagal sebelumnya tanpa membaca isi sebenarnya, lalu mengoreksi diri setelah رسلان upload file mentahnya). Total ~346 koreksi valid akhirnya diterapkan lewat proses penyaringan bertingkat (`filter_balasan41.py` → `filter_balasan41_v2.py`, ~66 kata dikecualikan berdasarkan pola kesalahan yang teridentifikasi).
7. **Keputusan sadar untuk berhenti:** sisa ~1.700 kata 动宾式/补充式 TIDAK diverifikasi lebih lanjut — diputuskan bersama bahwa upaya lebih lanjut tidak sepadan untuk fitur pelengkap ini, "cukup baik" diterima sebagai kondisi akhir.
8. رسلان menghapus file sisa tidak relevan dari sesi v23 dan mengonfirmasi tes "Akar Kosakata" di HP — kedua follow-up dari v22/v23 dinyatakan selesai.
9. Sesi ditutup dengan BLUEPRINT v24 ini; integrasi UI ke `kamus.html` akan dilanjutkan di percakapan baru.

**Sebelumnya (lihat BLUEPRINT v23, v22, v21, v20, v19 & v18 utk detail lengkap):** v23 — kurasi `nuance_pairs.json` 15→1.291 pasangan. v22 — pengumpulan kandidat nuance, fitur "Akar Kosakata". v21 — 15 pasangan nuance resmi, fitur Flashcard "Pilih yang Tepat". v20 — fitur "Beda dengan Kata Mirip" dari nol. v19/v18 — audit sistemik, sistem checkpoint.py, modularisasi kamus.html.

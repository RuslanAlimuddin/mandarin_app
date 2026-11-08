# BLUEPRINT — Mandarin Interaktif — v21
_(Handoff document. Baca Bagian A–B dulu untuk onboarding cepat. Bagian C–E untuk detail teknis. Bagian F untuk riwayat sesi.)_

---

## A. Arsitektur Saat Ini (Living Doc)

**Aplikasi:** "Mandarin Interaktif" — aplikasi belajar Mandarin offline, vanilla HTML/CSS/JS, single-user (رسلان), berjalan lokal di `C:\mandarin_app\` (biasanya via `python -m http.server` / `localhost:8000`).

**Sumber data utama** (folder `data/`): `app_words.json` (~11.726 entri, +1 dari v20 yaitu 参差), `cidict_index.json` (~125.000 entri, fallback CC-CEDICT), `graded_readers.json` (123 entri, SEMUA sudah punya field `type` eksplisit sejak v21 — lihat catatan di Bagian B), `char_etymology_id.json` (100% coverage), `confusion_groups.json` (53 grup), `nuance_pairs.json` (**15 pasangan resmi, LENGKAP** — lihat Bagian B).

**BARU sejak v21 — Fitur Flashcard "🎯 Pilih yang Tepat" (near-synonym game mode):**
Deck game baru di Flashcard yang reuse `data/nuance_pairs.json` (file yang sama dipakai panel "Beda dengan Kata Mirip" di Kamus, dibangun v20) — sesuai rencana yang sudah disepakati sejak v20 Bagian E poin 4. Ini bukan flip-card SRS biasa, tapi mode game kalimat-rumpang pilihan-ganda.

- **Mekanisme soal**: tiap KATA dalam `comparison[]` satu pasangan nuance jadi 1 soal terpisah — kalimat rumpang dari `example_cn` kata itu (kata dihilangkan jadi `___`), opsi jawaban = SEMUA kata di `comparison[]` pasangan yang sama (2 atau lebih). **SENGAJA TIDAK dipadding ke 4 opsi** seperti game Lawan Kata/Sinonim — karena inti latihannya justru menguji beda nuansa antar kata-kata yang mirip itu sendiri, bukan tebak di antara kata acak.
- **Pengecualian otomatis**: pasangan dengan hanzi identik di `comparison[]` (kasus 借 dua arah pinjam) dilewati dari game ini — tidak ada yang bisa "dipilih" secara visual kalau opsinya kelihatan sama persis. Pasangan itu tetap tampil normal di panel Kamus, cuma tidak dipakai di game.
- **Batasan yang ditemukan & didokumentasikan**: kata majemuk yang bisa "terpisah" dalam kalimat (离合词, mis. 生气 → 生我的气) akan GAGAL menghasilkan soal kalau `example_cn`-nya menulis bentuk terpisah, karena sistem highlight berbasis substring match persis. Sistem sengaja SKIP soal itu dengan aman (tidak error), tapi ini catatan penting untuk penulisan `example_cn` batch nuance berikutnya: **pakai bentuk utuh berurutan**, hindari bentuk terpisah.
- **File yang diubah** (murni penambahan, tidak ada kode lama yang diubah/dihapus): `flashcard.html` (sidebar item baru + CSS `.tg-prompt-sentence`), `flashcard-decks.js` (state `FC.nuancePairs`, dispatch `selectDeck()` mirip `tone-trap`, fungsi `loadNuanceData()`), `flashcard-games.js` (`buildNuanceQuestions()`, `renderNuancePrompt()`, cabang mode `'nuance'` di `startAudioGame()`/`renderToneGameQuestion()`/`answerGame()`), `flashcard-session.js` (bypass 1 baris di `startSession()`), `flashcard-init.js` (panggilan `loadNuanceData()`).
- **Status**: sudah di-QA رسلان langsung di app, **berjalan baik**. Dengan 15 pasangan resmi saat ini, game menghasilkan **28 soal** otomatis (dari maksimal 31 kemungkinan: -2 dari pasangan 借 yang dikecualikan by design, -1 dari kasus 离合词 生气 yang di-skip aman).

**Belum dikerjakan (di luar scope v21, dicatat untuk nanti):**
- Panel Kamus `kamus-nuance.js` belum mendukung 1 kata → >1 pasangan sekaligus (accordion). Belum relevan karena belum ada tabrakan di 15 pasangan resmi — baru jadi prioritas kalau/pas kandidat data besar (lihat di bawah) benar-benar dikurasi masuk resmi.
- Toggle format soal/jawaban (kayak Lawan Kata/Sinonim punya Hanzi/Pinyin/Suara/Terjemahan/Acak) sengaja diskip dulu di versi pertama "Pilih yang Tepat" untuk kesederhanaan.

---

## B. Status Kualitas Data (per akhir sesi ini)

**`nuance_pairs.json` — 15 pasangan resmi, LENGKAP & TERVERIFIKASI.**
9 pasangan baru ditambahkan sesi ini (大/巨大, 高兴/开心, 差不多/几乎, 可以/能/会, 已经/曾经, 还/再, 用/拿, 觉得/认为, 生气/难过), melengkapi 6 pasangan dari v20. Semua kata di 9 pasangan baru dicek silang pinyin & HSK-nya terhadap `app_words.json` — **100% cocok, tidak ada mismatch**. Semua 15 pasangan sekarang jadi bahan bakar fitur Flashcard "Pilih yang Tepat" (lihat Bagian A).

**`graded_readers.json` — backfill `type` SELESAI.** 104 entri lama yang tidak punya field `type` eksplisit sudah diberi `type: "bacaan"` (diverifikasi dulu semuanya format bacaan asli via cek field `text`/`turns`, lalu `--dry-run` → `--apply` → diff-check konfirmasi tidak ada konten lain berubah). Total sekarang: 113 bacaan + 10 percakapan = 123. **Item ini resmi ditutup.**

**`app_words.json` — entri 参差 (cēn cī) ditambahkan.** Field radical/stroke_count/components/structure dihitung mengikuti konvensi persis kata majemuk lain (radikal & struktur dari karakter pertama, stroke_count gabungan 8+9=17). Diff-check konfirmasi cuma 1 entri ditambahkan di akhir file, 11.725 entri lain tidak tersentuh. **Item ini resmi ditutup.**

**BARU — Bank kandidat mentah near-synonym (BELUM masuk `nuance_pairs.json` resmi, masih tahap pengumpulan):**
رسلان mengumpulkan kandidat pasangan near-synonym tambahan lewat AI eksternal (bukan lewat sesi Claude ini), memakai prompt NDJSON terstruktur yang disusun bersama. Sampai akhir sesi ini terkumpul **4 file kandidat, total 1.440 pasangan mentah** (sebelum dedup/kurasi):

| File | Jumlah | Rentang id | Catatan kualitas |
|---|---|---|---|
| `near-synonym-disambiguasi_kosakata_Mandarin.txt` (Daftar A) | 575 pasangan (580 baris, 5 duplikat) | tabel markdown, bukan skema resmi | Format terlalu tipis (1 baris nuansa, tanpa pinyin/HSK/contoh lengkap) — cuma bahan mentah, BUKAN siap-pakai |
| `near-synonym_nuance_pairs1.json` (Daftar B, 581-973) | 393 pasangan valid | NDJSON | **100% pinyin TANPA tone mark** (masalah fatal, sudah diperbaiki instruksinya di prompt lanjutan), 18 pasangan overlap dgn yang resmi, 82 pasangan katanya belum ada di `app_words.json` |
| `sampai_1100.txt` (Daftar C, 974-1100) | 127 pasangan unik (129 objek, 2 duplikat identik dibuang) | NDJSON | Tone mark sudah 100% benar. 2 baris sempat tergabung tanpa newline (sudah diberi instruksi perbaikan) |
| `sampai_1440.txt` (Daftar D, 1101-1440) | 334 pasangan unik (340 objek, 6 duplikat dibuang) | NDJSON | Tone mark 100% benar, integritas penomoran sempurna (tanpa lubang/duplikat nomor). Kualitas isi bagus: HSK 1-6 semua (tidak melebar ke sastra), 99 kategori nuansa unik (masih genuine eksplorasi, bukan pengulangan sempit). Overlap dgn daftar sebelumnya naik ke 15% (51/340) — tanda pool kandidat baru mulai menipis |

**Status: SEMUA 1.440 kandidat ini MASIH MENTAH, belum dikurasi/di-cross-check penuh ke `app_words.json`, belum masuk `nuance_pairs.json` resmi.** رسلان memutuskan lanjut kumpulkan lebih banyak dulu (prompt lanjutan sudah disiapkan, id lanjut dari 1441) sebelum masuk tahap kurasi. Lihat Bagian D untuk metodologi & Bagian E untuk rencana ke depan.

---

## C. Script/File Baru Sesi Ini

Sesi ini TIDAK ada script Python baru (beda dari sesi v20) — pekerjaan data (backfill, entri 参差, penambahan 9 pasangan nuance) dikerjakan langsung via script sekali-pakai di sesi Claude (tidak disimpan sbg file terpisah di `mandarin_app/`, karena sifatnya one-off dan sudah diverifikasi lewat diff-check langsung).

**File kode yang diubah sesi ini** (lihat Bagian A untuk detail): `flashcard.html`, `flashcard-decks.js`, `flashcard-games.js`, `flashcard-session.js`, `flashcard-init.js`.

**Script lama (v18-v20) masih berlaku, tidak berubah:** `checkpoint.py`, `complete_reading_json.py`, `complete_theme_json.py`, `repair_theme_word_sync.py`, `repair_glossary.py`, dst.

---

## D. Metodologi

**Tidak berubah dari v18-v20** untuk audit/fix data (audit read-only → sample-check → `--dry-run` wajib → eksekusi → `checkpoint.py save`).

**BARU sesi ini — metodologi pengumpulan kandidat nuance via AI eksternal (NDJSON workflow):**
Karena kebutuhan رسلان untuk kandidat near-synonym dalam jumlah besar (target semua level HSK) melebihi kapasitas wajar 1 respons AI, dikembangkan alur kerja "prompt berjenjang":
1. Prompt terstruktur disusun (skema JSON persis sama dgn `nuance_pairs.json`), format **NDJSON** (satu objek JSON per baris) — dipilih spesifik supaya kalau respons AI terpotong di tengah karena batas panjang, baris terakhir yang rusak tinggal dibuang tanpa merusak baris-baris lain.
2. رسلان jalankan prompt di AI eksternal (di luar sesi Claude ini), ketik "lanjutkan" tiap kali AI berhenti, sampai jumlah yang diinginkan terkumpul.
3. Hasil di-upload balik ke sesi Claude untuk divalidasi: cek JSON valid per baris, cek tone mark lengkap, cek skema field lengkap, cek duplikat id/internal, cek overlap dengan daftar sebelumnya, cek existence kata di `app_words.json`.
4. Prompt lanjutan disusun ulang tiap batch, menyisipkan SEMUA kata/pasangan yang sudah pernah muncul (baik yang resmi di `nuance_pairs.json` MAUPUN seluruh kandidat mentah sebelumnya) sebagai daftar "jangan diulang" — supaya AI tidak generate pasangan yang sama dua kali.
5. **Masalah yang ditemukan & pelajaran**: (a) pinyin tanpa tone mark (batch awal 100% gagal di sini — pelajaran: instruksi tone mark harus SANGAT eksplisit dgn contoh benar/salah, bukan cuma disebut sekali); (b) baris JSON kadang tergabung tanpa newline (butuh brace-matching parser, bukan cuma `split('\n')`, untuk parsing yang robust); (c) tingkat duplikat/overlap naik seiring bertambahnya total kandidat (wajar — pool kombinasi kata near-synonym yang genuinely valid itu terbatas); (d) kata majemuk 离合词 (mis. 生气) butuh instruksi khusus supaya `example_cn`-nya ditulis dalam bentuk utuh (bukan bentuk terpisah), supaya kompatibel dgn mekanisme highlight/blank berbasis substring match yang dipakai fitur Flashcard baru.
6. **Kurasi resmi ke `nuance_pairs.json` BELUM dimulai** — رسلان memilih terus kumpulkan dulu sebelum masuk tahap filter/pilih. Ini keputusan sadar, bukan terlewat.

**Metodologi konten linguistik nuance pairs (dari v20, tidak berubah):** batch kecil + رسلان uji langsung di app tiap batch, skema data fleksibel dari awal supaya kasus tidak biasa (borrow 2 arah, 3+ kata) tidak perlu ubah struktur.

---

## E. Prioritas Tugas Berikutnya

1. **(Prioritas utama, sedang berjalan)** Lanjutkan pengumpulan kandidat near-synonym via AI eksternal, mulai dari id_1441. Prompt lanjutan sudah disiapkan (menyertakan kembali 15 daftar resmi + Daftar A/B/C/D sebagai "jangan diulang"). رسلان yang menjalankan prompt ini sendiri di AI lain, lalu upload hasilnya balik ke sesi Claude untuk divalidasi tiap batch (pola yang sudah berjalan baik sesi ini).

2. **Setelah رسلان merasa cukup mengumpulkan** → mulai tahap KURASI: filter 1.440+ kandidat mentah ke yang (a) semua katanya sudah ada di `app_words.json`, (b) tidak overlap dgn 15 resmi atau sesama kandidat, (c) prioritas kepraktisan (HSK umum dulu). Baru masuk proses batch-kecil-plus-QA seperti metodologi v20 untuk resmi masuk `nuance_pairs.json`.

3. **Saat kurasi besar itu terjadi** → kemungkinan besar akan muncul kasus 1 kata masuk >1 pasangan (mis. 觉得 sudah ada di `juede_renwei_01`, tapi kandidat baru punya 觉得/感觉 juga). Sudah diputuskan desainnya (lihat Bagian A): panel Kamus akan tampilkan SEMUA yang relevan via accordion. **Implementasi `kamus-nuance.js` untuk accordion ini belum dikerjakan** — jadi prasyarat sebelum kurasi besar-besaran masuk resmi.

4. **(Opsional, prioritas rendah, dari v20, masih belum dikerjakan)** — tidak ada tugas opsional tersisa dari v20; keduanya (backfill `type`, entri 参差) sudah selesai sesi ini.

5. Lanjutkan pola living-doc + changelog terpisah.

---

## F. Riwayat Sesi (changelog)

**Sesi ini (v21):** (1) Melengkapi 9 pasangan nuance tersisa (target awal v20) — semua 15 pasangan resmi `nuance_pairs.json` kini LENGKAP, tervalidasi 100% cocok pinyin/HSK ke `app_words.json`. (2) Backfill `type: "bacaan"` ke 104 entri `graded_readers.json` — selesai, terverifikasi bersih via diff-check. (3) Entri 参差 ditambahkan ke `app_words.json` — selesai, terverifikasi. (4) File kandidat near-synonym 580-pasangan (tabel markdown) dievaluasi — diputuskan BUKAN langsung dipakai (format tidak cocok skema, banyak kata belum ada di kamus), jadi bank kandidat untuk dikurasi nanti; ditangguhkan sementara untuk fokus BLUEPRINT dulu. (5) Prompt NDJSON terstruktur disusun untuk pengumpulan kandidat via AI eksternal — melalui 3 iterasi prompt (perbaikan: tone mark eksplisit, anti baris-tergabung, anti-duplikat), terkumpul total 1.440 kandidat pasangan mentah (575+393+127+334, sebelum dedup) dari 4 file berbeda, masing-masing divalidasi (JSON validity, tone mark, skema, duplikat, overlap, existence di app_words.json). (6) Diskusi desain skala besar: diputuskan panel Kamus akan pakai accordion utk kasus 1 kata >1 pasangan (implementasi ditunda sampai kurasi besar terjadi), dan cara "menemukan" pasangan nuance tetap pasif via Kamus (tidak bikin halaman browse baru) — pelengkapnya adalah akses aktif lewat Flashcard. (7) **Fitur baru dibangun end-to-end: Flashcard "🎯 Pilih yang Tepat"** — deck game kalimat-rumpang pilihan-ganda reuse `nuance_pairs.json`, 5 file diubah (flashcard.html/flashcard-decks.js/flashcard-games.js/flashcard-session.js/flashcard-init.js), murni penambahan tanpa mengubah kode lama, disyntax-check + di-trace-test terhadap data resmi (28 soal dihasilkan dari 15 pasangan, sesuai ekspektasi), **sudah di-QA رسلان langsung di app dan dikonfirmasi berjalan baik**. Prompt lanjutan pengumpulan kandidat (mulai id_1441) disiapkan untuk sesi/proses berikutnya.

**Sebelumnya (lihat BLUEPRINT_v20, v19 & v18 utk detail lengkap):** Fitur "Beda dengan Kata Mirip" dibangun dari nol di Kamus (v20, 6 pasangan pertama). Audit sistemik 428+18+15=461 kata, sistem checkpoint.py, sinkronisasi glossary (69→104→123 entri graded reader), modularisasi kamus.html, dst.

# RESUME PERJALANAN PROYEK — Mandarin Interaktif

*Peta orientasi dari seluruh blueprint (KAMUS_v1, LANJUTAN_v2, v3 s/d v35). Ini BUKAN pengganti blueprint akhir sesi. Fungsinya hanya memberi gambaran utuh: apa yang sudah pernah dikerjakan, apa yang pernah direncanakan lalu terlupakan, dan apa yang sedang atau akan dikerjakan.*

*Dibuat pada 28 September 2026, dari pembacaan ulang semua file blueprint (bukan dari ingatan sesi).*

---

## 0. JAWABAN LANGSUNG: posisi "Karakter Mirip" (`confusion_groups.json`)

**Status: SUDAH pernah dibangun, dua kali. Yang BELUM dilakukan hanya ekspansi data melewati 71 grup.**

| Tahap | Versi | Apa yang terjadi |
|---|---|---|
| Ide pertama | v2 (LANJUTAN) | Muncul sebagai "Kembaran Visual (huruf mirip bentuk)". Ditunda karena butuh data-prep. |
| Data disiapkan | v8 | `confusion_groups_expanded.json` (dari riset رسلان) digabung jadi `confusion_groups.json`, 53 kelompok. Tertulis "data siap, fitur belum dibangun". |
| **Build ke-1** | **v9** | Deck Flashcard "🔀 Karakter Mirip": dengar satu karakter, pilih hanzi yang tepat, distraktor hanya dari grup yang sama, catatan `note` tampil setelah menjawab. Memakai `resolveConfusionChar()`. |
| Hilang tanpa jejak | v10 → v27 | Masih disebut sebagai data di v10–v25, tetapi tidak ada catatan perubahan apa pun. Kemungkinan tertimpa saat resync PART-file atau modularisasi flashcard (v17). **Penyebabnya tidak terdokumentasi; ini dugaan.** |
| Ditemukan "yatim" | v28 | Scan folder `data/` menunjukkan `confusion_groups.json` tidak dirujuk kode mana pun. v28 keliru menyimpulkan "fitur belum pernah dibangun" (hanya membaca v8, tidak v9). |
| **Build ke-2** | **v29** | Dibangun ulang penuh: (a) panel Kamus `kamus-karakter-mirip.js` (indeks dua arah), (b) deck Flashcard `confusion` dengan dropdown format soal (Pinyin/Suara/Terjemahan/Acak; jawaban dikunci hanzi), (c) tombol "Karakter Mirip" di Kelompok Kamus. |
| Bug terakhir tuntas | v30 | D.4 (grup hanya menampilkan 1 kartu) dinyatakan RESOLVED. Ternyata 26 dari 115 karakter tidak punya entri sendiri di `app_words.json`, sehingga perlu fallback ke Cidict. |
| Data diperluas | v30 | 53 → **71 grup** (id 54–71), 156 karakter unik. |
| Pipeline ekspansi | v30 | Diklaim "dibangun, siap pakai": `prompt_1_cari_karakter_mirip.txt`, `prompt_2_verifikasi_karakter_mirip.txt`, `gabungkan_karakter_mirip.py`. |
| **Fakta hari ini** | scan 28 Sep 2026 | **Ketiga file pipeline itu TIDAK ADA di disk** (0 dari 696 file cocok, baik nama maupun isi). Kemungkinan besar tidak pernah tersimpan. |
| Rencana | v35 | "Ekspansi `confusion_groups.json` siap dimulai kapan saja." |

**Yang benar-benar tersisa untuk Karakter Mirip:**
1. Membangun pipeline ekspansi dari nol (kandidat → verifikasi → merge + dedup).
2. Memutuskan target jumlah grup baru.
3. Bersih-bersih kecil: komentar usang "53 grup" di `kamus.html` dan `flashcard-decks.js` (data sebenarnya 71); `intip_confusion_groups.py` cacat (tidak menembus wrapper `{"groups":[...]}`, melaporkan "0 karakter" secara keliru); 53 dari 156 karakter tidak punya entri di `app_words.json` (sudah ditangani fallback Cidict di sisi Kamus, tetapi perlu diingat saat memvalidasi kandidat baru).

---

## 1. Gambaran proyek

Aplikasi belajar Mandarin offline milik رسلان: HTML/CSS/JS murni, dijalankan lokal di `C:\mandarin_app\` lewat `python -m http.server`. Antarmuka Bahasa Indonesia. Pengembang dan pengguna tunggal: رسلان. Data diproses dengan skrip Python lokal, dan sebagian konten dihasilkan lewat AI eksternal lalu divalidasi.

**Prinsip yang berlaku sepanjang perjalanan:** offline murni (skrip persiapan data boleh, aplikasi berjalan tidak boleh bergantung internet); diskusi dulu sebelum coding besar; baca file aktual sebelum edit; `node --check` untuk JS; audit read-only → sample-check → `--dry-run` → apply → `checkpoint.py save`.

**Halaman yang ada sekarang (±11):** `index.html`, `kamus.html`, `flashcard.html`, `wordbuilder.html`, `tone.html`, `graded-reader.html`, `hsk-exam.html`, `tatabahasa.html`, `terjemah-bebas.html`, `peta-bahasa.html`, plus `akar_kosakata_mandiri.html` (versi HP).

**Skala data saat ini (kira-kira):** `app_words.json` 11.983 entri; `cidict_index.json` ±125.000; `graded_readers.json` 123; `char_etymology_id.json` 2.840 karakter (100%); `nuance_pairs.json` 1.291 pasangan; `kata_majemuk_pola.json` 8.867 kata; `produktif_karakter.json` 1.389 akar; `grammar_hsk1–9.json` ±770 poin; `pilar_1–11.json` ±732.000 karakter; `confusion_groups.json` 71 grup.

---

## 2. Perjalanan kronologis

### Fase A — Fondasi (v1 – v4)
| Versi | Isi |
|---|---|
| KAMUS v1 | Perancangan: 3 modul (Kamus, Flashcard SRS, Word Builder), tema gelap emas-merah, metode penulisan bersegmen (PART). Data sudah selesai, kode belum. |
| LANJUTAN v2 | Antrean perbaikan hasil tes: pinyin presisi nada, kartu hasil 1 baris, sort arti, panel bisa di-resize, sidebar accordion, tema custom, radikal 214, `index_phonetic.json` (537 grup), 119 tema eksternal AllSet. **Roadmap "ditunda"** memuat: Kembaran Visual, Measure Word, Verb Complement, Saudara Kembar Inggris, Pola Nada 3-3, Palindrom. |
| v3 | Sesi A (Kamus) dan Sesi B (Flashcard) selesai. |
| v4 | Sesi C (Word Builder) selesai: `wb_pools.json` (9 pool), `pattern_explanations.json` (34 pola × 6 bagian). |

### Fase B — Melengkapi ekosistem (v5 – v11)
| Versi | Isi |
|---|---|
| v5 | Roadmap arsitektur Tier 0–3 disepakati (`shared/core.js`, `pinyin.js`, `audio.js`, `srs.js`, dst.). |
| v6 | Seluruh roadmap v5 dikerjakan: audio TTS, backup ekspor/impor, `tone.html`, `graded-reader.html`, `hsk-exam.html`, spot-the-error, kuis pola, filter Mastered/Weak. |
| v7 | Tindak lanjut tes: animasi goresan kuas asli (Hanzi Writer, 3.034 karakter), game audio Flashcard (Jebakan Nada, Lawan Kata, format soal/jawaban), ingat state terakhir, riwayat ujian. |
| v8 | `tatabahasa.html` lahir; audit HSK7–9 vs standar resmi; 18 bacaan tema; deck Sinonim. |
| v9 | Spot-the-error diperkaya; **deck Karakter Mirip (build ke-1)**; audit HSK1–6 (414→521 poin); bacaan 14→69; skrip `scan_mandarin_app.py`. |
| v10 | Bacaan 101; koreksi metode verifikasi coverage (terhadap glossary bacaan itu sendiri). |
| v11 | `terjemah-bebas.html`; fallback Cidict di Kamus; bacaan 104. |

### Fase C — Kedalaman konten & modularisasi (v12 – v17)
| Versi | Isi |
|---|---|
| v12 | Cross-link ke bacaan (Kamus, Flashcard); dashboard streak; **modularisasi `kamus.html`** (8 file JS); fitur "Bantu Ingat"; etimologi karakter mulai (batch 1–4); toggle pinyin di reader. |
| v13 | Etimologi batch 5–11 (1.428 karakter). |
| v14 | **Etimologi TUNTAS 2.840/2.840**; statistik latihan nada; "Bantu Ingat" jadi grid; explorer komponen/radikal; mnemonic di Flashcard; `tone.html?focus=N`. |
| v15 | Grup Per Struktur & Per Pinyin 2 tingkat; fix deck kecil kosong; tema custom dilengkapi; cross-link tatabahasa→wordbuilder (32/34 pola); 201 kata baru; `complete_theme_json.py`. |
| v16 | Import tema JSON; pencarian sidebar; ekspor hasil Kamus; deck Goresan/Pinyin; grup Fonetik di Kamus. |
| v17 | `complete_reading_json.py` (bacaan + percakapan bubble-chat); audit & merge tema tumpang tindih; `repair_theme_word_sync.py` (1.850 tag disinkronkan); **modularisasi `flashcard.html` dan `wordbuilder.html`**; bacaan 123; dead code dibersihkan. |

### Fase D — Kualitas data & fitur linguistik lanjutan (v18 – v25)
| Versi | Isi |
|---|---|
| v18–v19 | Audit sistemik bacaan/arti default (±461 kata diperbaiki); `repair_glossary.py` v2 berbasis baseline; `checkpoint.py` dibuat setelah insiden file kosong. |
| v20 | QA bersih; dashboard `index.html` diperbarui; audit 差/曲 (tidak ada bug); **fitur "Beda dengan Kata Mirip" dibangun** (6 pasangan). |
| v21 | 15 pasangan nuance; game Flashcard "Pilih yang Tepat"; backfill `type` bacaan; entri 参差; pengumpulan kandidat near-synonym dimulai. |
| v22 | 2.891 kandidat unik dikumpulkan lalu dihentikan; fitur **"Akar Kosakata"** digabung. |
| v23 | Kurasi `nuance_pairs.json` **15 → 1.291** (pipeline dua jalur). |
| v24 | **Klasifikasi 8.867 kata** ke 6 pola pembentukan kata majemuk. Verifikasi ±1.700 kata 动宾式/补充式 dihentikan sadar. |
| v25 | UI pola kata majemuk: panel Kamus (`kamus-pola.js`) + game "Tebak Pola Kata". |

### Fase E — Peta bahasa, leksikon khusus, tata bahasa (v26 – v28)
| Versi | Isi |
|---|---|
| v26 | Pemetaan **11 Pilar** terhadap isi aplikasi; 470 entri leksikon khusus (kata seru, onomatope, sapaan, partikel modal) di-generate dan di-enrich (445 siap). |
| v27 | 257 kata masuk `app_words.json`; `index_kelompok_khusus.json` (37 grup, menu 3 tingkat); **`peta-bahasa.html`**; `pilar_1–11.json` (±732rb karakter); milestone "Peta 11 Pilar" tuntas. |
| v28 | Badge status peta diselaraskan (11/11 ✅); deep-link `tatabahasa.html#search=`; **Daftar Isi tata bahasa** (770 poin → 28 topik); investigasi bug klik kartu duplikat; scan lengkap folder `data/`. |

### Fase F — Sinonim/antonim & Karakter Mirip (v29 – v35)
| Versi | Isi |
|---|---|
| v29 | E.1 (klik kartu duplikat) selesai; E.0.1 (render contoh kalimat) selesai; E.0.2 (sinonim/antonim + nuansa, 134 kata) selesai; bug jumlah kartu game diperbaiki; E.0.2b batch 1; **Karakter Mirip build ke-2 (90%, bug D.4 menggantung)**. |
| v30 | D.4 RESOLVED; grup 53→71; Tier A tuntas; mekanisme `_tb_empty_streak`. |
| v31 | ±17 cycle Tier B; **insiden** skrip batch3 v1 menghapus 1.800 relasi sehat → dipulihkan, v2 aman menghapus 187; `apply_...` v3.2. |
| v32–v34 | Review manual Tier B; `flagged_relations_batch4/5/6`; tool baru `cek_dan_bersihkan_hasil_tier_b.py`. |
| **v35** | **Tier B (E.0.2b) TUNTAS** (pool 100→77→25→9→0); batch4/5/6 + exclude sesi v35 semua di-apply (bug `checkpoint.save` diperbaiki). |

---

## 3. Fitur yang sudah selesai (ringkas)

- **Kamus:** pencarian hanzi/pinyin/arti + fallback Cidict; grup Radikal/Goresan/Tema/Pinyin/Struktur/Fonetik/Akar Kosakata/Kelompok Khusus/Karakter Mirip; panel: Bantu Ingat, Beda dengan Kata Mirip, Pola Pembentukan Kata, Karakter Mirip, Contoh Kalimat, Sinonim/Antonim ber-nuansa, Muncul di Bacaan, animasi goresan; ekspor/cetak; deep-link hash.
- **Flashcard (SRS SM-2):** puluhan deck browse + game audio (Jebakan Nada, Lawan Kata, Sinonim, Pilih yang Tepat, Tebak Pola Kata, **Karakter Mirip**), toggle Mode Game, Bantu Ingat di kartu belakang.
- **Word Builder:** 34 pola kalimat, filter HSK, penjelasan lengkap, spot-the-error, kuis pola, koleksi tersimpan, handoff dari Flashcard dan Tata Bahasa.
- **Tata Bahasa:** 770 poin HSK1–9 (teraudit vs standar resmi), Daftar Isi 28 topik, pencarian lintas level.
- **Bacaan berjenjang:** 123 bacaan + percakapan bubble-chat, toggle pinyin/terjemahan, audio.
- **Lainnya:** Tone drill + statistik, simulasi ujian HSK + riwayat, Terjemah Bebas, dashboard (streak, progres per level), Peta 11 Pilar + 11 pelajaran lengkap, etimologi 100%, Akar Kosakata (+ versi HP), sistem `checkpoint.py`.

---

## 4. Direncanakan tapi terlupakan / tidak terkonfirmasi

Ini bagian yang paling perlu dicek. "Tidak terkonfirmasi" berarti tercatat pernah direncanakan, tetapi blueprint sesudahnya tidak menyebut selesai atau dibatalkan.

| Item | Asal | Status |
|---|---|---|
| **E.2 Bersihkan polusi `meanings_id`** (1.437 item / 1.361 entri kena `KP:`, `varian dari`, `Taiwan pr.`; pindahkan `KP:` ke field `classifier`; terjemahkan kode `pos` mentah) | v28 E.2 | **Hilang dari daftar setelah v28.** v29 dan seterusnya tidak menyebut. Regex deteksi lama juga terbukti kurang (harus longgar, mencakup "variasi dari" dan pola di tengah kalimat). |
| **E.3 Struktur makna kata polisemi** (definisi per makna + contoh + kelompok kelas kata, ala Hanzii; pilot 50–100 kata seperti 的/了/是/着…) | v28 E.3 | **Hilang dari daftar setelah v28.** Proyek terbesar yang pernah didiagnosis lengkap. |
| **E.0.1b** Perluas contoh kalimat (±259 dari 11.983 masih kosong; tercatat ada 257 berisi) | v29 | Backlog, belum dikerjakan. |
| **E.4 Housekeeping** file `.bak_*` (>250MB) di `data/` dan 51 file yatim | v28 | Belum. Scan hari ini menunjukkan ratusan file `.bak_before_apply_sinonim_antonim_*` malah bertambah. |
| **Sufiks/Prefiks produktif** (者/家/性/化/员 → "keluarga kata"; lapisan 2 dari peta 5 lapisan morfologi) | v22 → v35 | Disepakati sejak v22, belum disentuh. |
| **Measure word pairing** dan **Verb complement / verba berantai** | v2 → v35 | Terdaftar sejak v2 (±33 versi), belum pernah dikerjakan. Butuh kurasi data dari nol. |
| **Dictation** (dengar → ketik) | v5 → v35 | Wishlist sejak v5. |
| **Pola nada khusus / sandhi 3-3** | v2 → v29 | Rencana: masuk pelajaran/Tata Bahasa saja. |
| **多音字** (karakter multi-bacaan, terkait 回文/karakter simetris) | v29 | Backlog "prioritas tinggi kalau digarap". |
| Refactor tombol "Tambah ke Tema" (dropdown tema existing) | v29 | Backlog. |
| 614 kata luar HSK1–9 (`unmatched_theme_words.json`) | v2, v15, v29 | Sebagian (155 kata) masuk di v15; sisanya belum. |
| Placement test HSK (mode "Tes Cepat" di `hsk-exam.html`) | v5 → v29 | Wishlist. |
| Skema kata majemuk **3+ karakter** (1.287 kata) | v24, v25, v29 | Belum ada rancangan. |
| `bersihkan_relasi_angka.py` | v30, v31 | Status tidak pernah dikonfirmasi; kemungkinan aman diabaikan. |
| Patch heuristik negasi `未` di `cek_dan_bersihkan_hasil_tier_b.py` | v35 | Belum dipatch (tidak mendesak, Tier B sudah tuntas). |
| Audit pinyin karakter tunggal bacaan langka (广 yǎn, 转 zhuǎi, 提 dī) | v15 §2.4 | Mungkin sudah tertutup audit v18–v19, **tidak pernah dikonfirmasi**. |

**Catatan hati-hati:** daftar backlog di v29 F.2 masih mencantumkan beberapa item yang sebenarnya sudah selesai di versi lebih awal ("Statistik Latihan Nada di Dashboard" selesai v14; "Dead code flashcard" selesai v17; "Dashboard progres gabungan" sebagian besar selesai v12/v14). Jadi backlog v29 tidak bisa dipercaya mentah-mentah, cek dulu ke versi sebelumnya.

---

## 5. Ditunda permanen atau di-drop (jangan diusulkan lagi kecuali رسلان yang membuka topiknya)

- Hapus folder `hanyu_extract` / `mandarin_kamus` (ditunda sampai tahap akhir proyek).
- OCR kamera dan kaca pembesar / hover-translate (di-drop permanen).
- Verifikasi ulang ±1.700 kata 动宾式/补充式 (AI eksternal terbukti tidak andal; "cukup baik" diterima).
- Sentence mining pribadi.
- UI koleksi Word Builder `mandarin_wb_saved` (alurnya dihapus total).
- Cross-link bacaan di Word Builder (di-drop v12).
- Mode gelap/terang dan cetak/export PDF (ditolak sejak v3–v5).
- Accordion `kamus-nuance.js` untuk 1 kata → banyak pasangan (tidak perlu karena pipeline mencegah overlap).

---

## 6. Yang sedang dan akan dilakukan

**Sedang (sesi ini):** memulai **ekspansi `confusion_groups.json`**. رسلان setuju ini prioritas pertama, lalu urutan berikutnya: Productive suffixes/prefixes → Measure word pairing & verb complement → Dictation game. Langkah yang sudah dilakukan hari ini: scan seluruh folder proyek, hasilnya pipeline lama tidak ada di disk.

**Berikutnya, urutan yang disepakati:**
1. Ekspansi Karakter Mirip (bangun pipeline dari nol).
2. Productive suffixes/prefixes (者/家/化, dst.).
3. Measure word pairing dan verb-chaining/complement.
4. Dictation game (listen-and-type).

**Layak dipertimbangkan setelahnya (belum diputuskan):** E.2 (bersihkan `meanings_id`) sebagai prasyarat E.3 (struktur polisemi); E.0.1b; housekeeping `.bak`.

---

## 7. Pola kerja yang terbukti (untuk dipakai ulang)

1. **"Intip" dulu, jangan menebak.** Skrip read-only untuk memeriksa struktur data sebelum menyimpulkan. (Tapi skrip intip sendiri bisa cacat, contoh `intip_confusion_groups.py`.)
2. **Generasi vs klasifikasi.** Menyerahkan *penulisan konten terstruktur* ke AI eksternal berhasil dengan validasi struktural (nuance, leksikon). Menyerahkan *klasifikasi bernuansa* gagal tanpa tinjauan manual (pola majemuk, sinonim/antonim Tier B).
3. **Jangan hapus data lewat pencocokan pola teks.** Insiden batch3 v1 (1.800 relasi sehat terhapus). Hanya hapus dari daftar pasangan eksplisit yang sudah diverifikasi.
4. **Verifikasi bahwa kode benar-benar tereksekusi** sebelum menebak bug lagi (D.4: cache/berkas lama).
5. **Blueprint bisa salah.** Klaim "belum dibangun" (v28), "pipeline siap" (v30), dan backlog usang (v29) semuanya perlu dicek ke kode/disk. Sumber kebenaran: scan folder + baca kode.
6. **File modul:** `kamus/` (10), `flashcard/` (6), `wordbuilder/` (7) sudah modular; alur PART-file sudah tidak berlaku. Cek juga versi upload agar bukan file lama.
7. **Checkpoint** (`python checkpoint.py save`) sebelum dan sesudah tiap `--apply`.

---

## 8. Catatan cakupan rangkuman ini

Semua 37 file blueprint sudah dibaca isinya. Rentang tanggal yang tertera di blueprint: Juli–September 2026. Dokumen ini merangkum, bukan menggantikan; detail teknis per fitur ada di blueprint aslinya (terutama v29–v30 untuk Karakter Mirip, v28 untuk skema data dan diagnosis polisemi, v35 untuk status Tier B).

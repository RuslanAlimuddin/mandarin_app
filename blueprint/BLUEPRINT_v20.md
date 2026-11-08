# BLUEPRINT — Mandarin Interaktif — v20
_(Handoff document. Baca Bagian A–B dulu untuk onboarding cepat. Bagian C–E untuk detail teknis. Bagian F untuk riwayat sesi.)_

---

## A. Arsitektur Saat Ini (Living Doc)

**Aplikasi:** "Mandarin Interaktif" — aplikasi belajar Mandarin offline, vanilla HTML/CSS/JS, single-user (رسلان), berjalan lokal di `C:\mandarin_app\` (biasanya via `python -m http.server` / `localhost:8000`).

**Sumber data utama** (folder `data/`): `app_words.json` (~11.725 entri), `cidict_index.json` (~125.000 entri, fallback CC-CEDICT), `graded_readers.json` (123 entri: 9 `bacaan` eksplisit + 10 `percakapan` eksplisit + 104 entri lama tanpa field `type` — lihat catatan di Bagian E), `char_etymology_id.json` (100% coverage), `confusion_groups.json` (53 grup — karakter mirip BENTUK/TULISAN, bukan makna).

**BARU sejak v20 — fitur "Beda dengan Kata Mirip" (near-synonym nuance pairs):**
Fitur baru untuk pasangan kata yang gramatikal sama-sama valid tapi beda nuansa penggunaan (jumlah/tujuan/register/arah), BUKAN karakter mirip bentuk (itu sudah ditangani `confusion_groups.json`) dan bukan sekadar sinonim (itu field `synonyms` yang sudah ada). Contoh kasus: 尝 (mencicipi sedikit) vs 吃 (makan sungguhan).

- **`data/nuance_pairs.json`** — data terstruktur, field per pasangan: `core_distinction_id`, `comparison[]` (tiap kata: usage, quantity, purpose, collocations, contoh kalimat), `common_mistake_id`, opsional `related_but_different`. Skema fleksibel — `comparison` array bisa >2 item (untuk kasus kayak 可以/能/会 nanti) dan bisa berisi hanzi yang SAMA dengan usage beda (kasus 借 arah pinjam-dari vs pinjamkan-ke).
- **`kamus/kamus-nuance.js`** — render logic, BERDIRI SENDIRI, tidak menyentuh `kamus-detail.js`. Auto-detect kata aktif via `MutationObserver` di elemen `#d-hanzi`, fetch data sekali di awal, tampilkan/sembunyikan section otomatis tergantung kata yang lagi dibuka.
- **Markup di `kamus.html`**: section baru `#d-section-nuance`, ditaruh setelah panel "Bantu Ingat" di detail view kanan (bukan halaman terpisah — keputusan disepakati sesi ini). CSS 100% reuse variabel yang sudah ada (`--gold`, `--red`, `--bg-card2`, `--border`, dst.) — tidak ada warna/font baru.
- **Interaksi:** hanzi di dalam panel bisa diklik, memanggil fungsi `searchExample()` yang sudah ada di `kamus-detail.js` untuk lompat cari kata pasangannya.
- **Layout: vertikal bertumpuk** (bukan dua kolom berdampingan) — dipilih karena sidebar detail biasanya sempit meski bisa di-drag lebar. Sudah di-QA رسلان dan berjalan baik untuk 6 pasangan pertama termasuk kasus unik 借 (hanzi sama, dua arah beda).
- **Rencana scale ke Flashcard**: kalau nanti dataset near-synonym ini di-scale besar, arahnya jadi deck/game mode baru di Flashcard ("Pilih yang Tepat" — kalimat rumpang pilih kata pasangan yang cocok konteks), REUSE `nuance_pairs.json` yang sama. Bukan halaman baru di luar Kamus+Flashcard — disepakati eksplisit oleh رسلان.

**Status isi data nuance_pairs.json per akhir sesi ini: 6 dari 15 pasangan kandidat.**
Sudah lengkap (linguistik + contoh kalimat + kesalahan umum, sudah di-QA رسلان langsung di app):
1. 尝 (cháng) vs 吃 (chī) — jumlah & tujuan makan/mencicipi
2. 看 (kàn) vs 看见 (kànjiàn) — aktivitas vs hasil (resultative verb)
3. 一点儿 (yìdiǎnr) vs 有点儿 (yǒudiǎnr) — posisi kata menentukan nuansa
4. 借 (jiè) vs 借 (jiè) — arah preposisi pada kata yang SAMA (kasus unik)
5. 关心 (guānxīn) vs 担心 (dānxīn) — peduli vs khawatir
6. 穿 (chuān) vs 戴 (dài) — jenis pakaian vs aksesoris

**Checkpoint/backup system** (`checkpoint.py`, dari v19): tidak berubah. **WAJIB dijalankan** (`python checkpoint.py save`) di awal tiap sesi kerja baru dan setelah tiap `--apply`/edit data yang berhasil — termasuk sesi ini setelah update `nuance_pairs.json` dan `kamus.html`.

---

## B. Status Kualitas Data (per akhir sesi 31 Jul 2026)

**QA Round 2 (dari v19) — DIKONFIRMASI BERSIH.** 33 kata (18 manual + 15 round 2) sudah diverifikasi via script `qa_round2_check_v2.py`: semua kata majemuk mengandung 落/圈/藏/结 menggunakan bacaan yang benar sesuai posisi & konteks (termasuk kasus bacaan ganda yang sah seperti 结果/结实 = jiē, vs 结束/结构 = jié). Cross-check ke `graded_readers.json` (123 entri) juga bersih, tidak ada kebocoran bacaan lama. **Item ini resmi ditutup, tidak perlu direvisit kecuali ada laporan pengguna konkret.**

**Audit Round 3 (差/曲) — SELESAI, TIDAK ADA YANG PERLU DI-FIX.** Berbeda dari round 1/2 (itu kasus bug bacaan salah), 差 dan 曲 memang genuinely ambigu tergantung konteks — dan setelah dipetakan penuh via `audit_round3_cha_qu.py` (17 entri untuk 差, 12 entri untuk 曲, plus cross-check glossary), **semua entri sudah punya bacaan yang tepat sesuai makna** (chà=buruk/hampir, chā=selisih, chāi=tugas dinas untuk 差; qū=bengkok, qǔ=lagu untuk 曲). Kekhawatiran di v18/v19 bahwa ini "berpotensi bug tersembunyi" ternyata tidak terbukti. **Item ini resmi ditutup.**

**Temuan sampingan (bukan bug, backlog opsional prioritas rendah):**
- 参差 (cēn cī) sebagai entri tersendiri belum ada di `app_words.json` — cuma muncul dalam bentuk idiom 参差不齐 di glossary bacaan. Boleh ditambahkan kapan saja, tidak mendesak.
- 104 dari 123 entri `graded_readers.json` tidak punya field `type` eksplisit (kemungkinan entri lama dari sebelum field ini diperkenalkan). Terdeteksi via `check_reader_hsk_range.py`. Tidak mengganggu fungsi aplikasi saat ini, tapi backfill `type: "bacaan"` ke 104 entri itu akan bikin data lebih konsisten untuk keperluan filter/statistik di masa depan.

---

## C. Script Baru Sesi Ini

| Script | Fungsi | Catatan |
|---|---|---|
| `qa_round2_check_v2.py` | QA read-only untuk verifikasi bacaan 落/圈/藏/结 di app_words.json + cross-check graded_readers.json, berbasis posisi suku kata (bukan substring naif) | Sudah dipakai, hasil bersih. Bisa dipakai lagi kalau ada karakter lain yang perlu di-QA serupa |
| `audit_round3_cha_qu.py` | Audit read-only pemetaan 差/曲 — BUKAN deteksi bug, tapi listing lengkap utk review manual | Sudah dipakai, hasil bersih (tidak ada fix diperlukan) |
| `check_reader_hsk_range.py` | Cek rentang HSK & breakdown tipe konten (`bacaan`/`percakapan`) di graded_readers.json | Sudah dipakai — hasil: HSK 1–9, 9 bacaan eksplisit + 10 percakapan eksplisit + 104 tanpa type |

**Script lama (v18/v19) masih berlaku, tidak berubah:** `checkpoint.py`, `complete_reading_json.py`, `complete_theme_json.py`, `repair_theme_word_sync.py`, `repair_glossary.py`, dst. — lihat BLUEPRINT v18/v19 kalau perlu detail.

---

## D. Metodologi

**Tidak berubah dari v18/v19** untuk audit/fix data (audit read-only → sample-check → `--dry-run` wajib → eksekusi → `checkpoint.py save`).

**BARU sesi ini — metodologi khusus konten linguistik (nuance pairs):**
Berbeda dari audit bug-fixing yang bisa diverifikasi programatik, penulisan `nuance_pairs.json` adalah kerja konten linguistik murni — tidak ada "ground truth" yang bisa dicek otomatis, jadi:
1. Kerjakan dalam **batch kecil** (sesi ini: 6 pasangan, bukan semua 15 sekaligus) supaya kualitas & akurasi tiap pasangan tetap terjaga.
2. **رسلان WAJIB uji langsung di app** tiap batch selesai (bukan cuma baca JSON-nya) — karena nuansa bahasa itu sensitif, salah highlight bisa lebih berbahaya daripada tidak ada penjelasan sama sekali.
3. Skema data (`nuance_pairs.json`) sengaja dibuat fleksibel dari awal (comparison array tidak dibatasi 2 item, boleh hanzi sama dgn usage beda) supaya kasus-kasus tidak biasa (kayak 借 dua arah, atau 可以/能/会 yang 3 kata) tidak perlu ubah struktur data maupun kode render.

---

## E. Prioritas Tugas Berikutnya

1. **Lanjutkan 9 pasangan nuance yang tersisa** (prioritas utama sesi depan) — daftar kandidat sudah disepakati:
   - 大 (dà) vs 巨大 (jùdà) — besar biasa vs sangat besar
   - 高兴 (gāoxìng) vs 开心 (kāixīn) — senang formal vs santai
   - 差不多 (chàbuduō) vs 几乎 (jīhū) — hampir (dua jenis)
   - 可以 (kěyǐ) vs 能 (néng) vs 会 (huì) — izin vs kapabilitas vs keahlian (3 kata)
   - 已经 (yǐjīng) vs 曾经 (céngjīng) — sudah vs pernah
   - 还 (hái) vs 再 (zài) — masih vs lagi
   - 用 (yòng) vs 拿 (ná) — pakai cara vs pegang fisik
   - 觉得 (juéde) vs 认为 (rènwéi) — opini ringan vs formal
   - 生气 (shēngqì) vs 难过 (nánguò) — marah vs sedih

   Saran: kerjakan lagi dalam batch (mis. 4-5 per sesi) + رسلان uji tiap batch, ikuti pola sesi ini.

2. **(Opsional, prioritas rendah)** Backfill field `type: "bacaan"` ke 104 entri `graded_readers.json` yang belum punya field itu — demi konsistensi data, tidak mendesak/mengganggu fungsi.

3. **(Opsional, prioritas rendah)** Tambahkan entri 参差 (cēn cī) ke `app_words.json` — saat ini cuma ada sbg bagian idiom 参差不齐.

4. Setelah 15 pasangan nuance selesai semua → evaluasi apakah worth di-scale lebih jauh (lebih banyak pasangan) atau alihkan effort ke fitur Flashcard "Pilih yang Tepat" yang sudah didiskusikan (reuse `nuance_pairs.json`).

5. Lanjutkan pola living-doc + changelog terpisah (BLUEPRINT v20 ini konsisten dgn pola v18/v19).

---

## F. Riwayat Sesi (changelog)

**Sesi 31 Jul 2026** (sesi ini): (1) QA manual round 2 dikonfirmasi bersih via script terverifikasi (`qa_round2_check_v2.py`) — 33 kata resmi selesai, tidak perlu direvisit. (2) Dashboard `index.html` diupdate: statistik kata (11.470→11.725, 121K→125K Cidict), kartu Bacaan Berjenjang (14→123 entri, ditambah info jenis konten percakapan, rentang HSK dikonfirmasi 1–9 via script baru `check_reader_hsk_range.py`). (3) Audit round 3 (差/曲) selesai — hasil bersih, tidak ada fix diperlukan, item ditutup. (4) **Fitur baru dibangun dari nol: "Beda dengan Kata Mirip"** (near-synonym nuance pairs) — didiskusikan arsitekturnya dulu (menyatu di Kamus, bukan halaman baru), dibuat prototipe visual, disederhanakan menyesuaikan desain kamus.html asli (reuse variabel CSS, tanpa warna baru), diimplementasi penuh (`kamus.html` + `kamus/kamus-nuance.js` baru yang berdiri sendiri tanpa mengubah `kamus-detail.js` + `data/nuance_pairs.json` baru), sudah di-QA رسلان langsung di app dan berfungsi baik untuk 6 pasangan pertama (尝/吃, 看/看见, 一点儿/有点儿, 借×2, 关心/担心, 穿/戴). 9 pasangan sisa jadi prioritas sesi berikutnya.

**Sebelumnya (lihat BLUEPRINT_v19 & v18 utk detail lengkap):** Audit sistemik 428+18+15=461 kata, sistem checkpoint.py dibuat setelah insiden repair_glossary.py kosong tanpa jejak, sinkronisasi glossary (69→104→123 entri graded reader), dst.

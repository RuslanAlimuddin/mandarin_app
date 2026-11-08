# BLUEPRINT v37 — Mandarin Interaktif

Lanjutan dari BLUEPRINT v36. Sesi ini (25–29 Oktober 2026) satu topik: **kurasi kandidat
"Karakter Mirip" tahap P2 (kemiripan longgar ±70%)** dari sumber luar (AI kandidat), dinilai
Claude, dan dikumpulkan untuk digabung ke `data/confusion_groups.json`.

**Status data: `confusion_groups.json` BELUM berubah.** Tidak ada `--apply` sepanjang sesi ini
(masih 160 grup, 328 karakter unik seperti akhir v36). Semua hasil kurasi masih berupa file CSV/NDJSON
di luar database. Penggabungan dilakukan di akhir sesi P3 (lihat bagian 6).

Sesi berikutnya: **P3 batch01** (percakapan baru, lihat bagian 8).

---

## 1. Alur kerja baru (berbeda dari v36)

v36 memakai pipeline internal (`buat_prompt…`, `tambang…`, `gabungkan…`). Sesi ini alurnya:

1. **AI kandidat** (di luar Claude) menghasilkan CSV 100 pasangan (`karakter_mirip_P2_batchNN_100_review.csv`).
2. **Claude menilai** tiap pasangan dan mengisi kolom kosong: `decision` (**Terima / Tolak**),
   `final_tier` (T1/T2/T3), `reviewer_notes` (catatan beda, singkat), `human_status` (= `REVIEWED_BY_CLAUDE`).
3. Hasil dikembalikan ke AI kandidat; رسلان mengumpulkan versi final. **Prinsipnya saling melengkapi**:
   kalau AI kandidat atau Claude merevisi keputusan, **versi final yang dikirim رسلان yang berlaku**.
4. Di **akhir sesi**, seluruh pasangan "Terima" digabung menjadi grup dan dimasukkan ke
   `confusion_groups.json` (dry-run → `--apply`).

Claude berhak menolak kandidat yang disetujui رسلان (kemiripan <70%); رسلان menyerahkan penilaian
visual kepada Claude ("keterbatasan logika saya").

**Format file:** batch01–07 memakai pemisah `;`; batch08 ke atas dan P1 memakai `,`.
Kolom dasar: `pair_id, a, b, visual_best_rank, hsk_a, hsk_b, hsk_pair_band, sources, manual_group_ids,
ai_recommendation, ai_tier_recommendation, ai_similarity_band, ai_difference_note, ai_screening_reason,
decision, final_tier, reviewer_notes, human_status`. Batch01–03 membawa saran AI (`ai_recommendation`);
**batch04 ke atas kosong** sehingga seluruh penilaian dari Claude. Satu insiden awal: `TERIMA/TOLAK`
pernah tertulis di kolom `manual_group_ids` bukan `decision`; sudah diperbaiki.

---

## 2. Tingkat kemiripan (disepakati رسلان)

| Tingkat | Perkiraan | Ciri |
|---|---|---|
| **T1** | ±85–95% | Beda satu goresan/titik/panjang garis, atau komponen kecil sama dengan satu goresan beda (mis. 古/吉, 勺/匀, 已/巴). |
| **T2** | ±75–85% | Satu komponen/radikal beda, atau satu karakter memuat karakter lain (mis. 唁 = 言 + 口), komponen sama dengan radikal samping beda. |
| **T3** | ±70–75% | Komponen utama sama tetapi bentuk keseluruhan mulai berbeda; atau radikal berbeda cukup jauh (mis. 亻/钅). |

Pasangan <70% = **Tolak**. Persentase adalah perkiraan visual Claude, bukan ukuran pasti.
**Disepakati: tingkat ditampilkan terpisah** (supaya T2/T3 tidak membanjiri T1 yang tajam).
**Disepakati: catatan grup berisi >2 karakter memakai satu kalimat gabungan** (Claude menyusun saat penggabungan).

---

## 3. Hasil kurasi

Total pasangan **Terima baru: 528** (T1 **32**, T2 **331**, T3 **165**). Dari ±2.060 pasangan yang dinilai, ±1.500 Tolak dan 29 duplikat P1 dilewati. Tidak ada pasangan Terima yang bentrok dengan `confusion_groups.json` (160 grup) maupun antarbatch.

| Sumber | Terima | T1 | T2 | T3 | Catatan |
|---|---|---|---|---|---|
| P1 (91 pasangan) | 58 baru | 3 | 43 | 12 | +29 duplikat data lama (dilewati), 4 Tolak |
| P2-01 | 41 | 4 | 31 | 6 | |
| P2-02 | 40 | 4 | 22 | 14 | |
| P2-03 | 43 | 4 | 35 | 4 | |
| P2-04 | 31 | 2 | 17 | 12 | saran AI kosong |
| P2-05 | 27 | 0 | 21 | 6 | |
| P2-06 | 24 | 0 | 20 | 4 | |
| P2-07 | 6 | 0 | 3 | 3 | pasangan acak radikal 扌 |
| P2-08 | 30 | 3 | 20 | 7 | |
| P2-09 | 26 | 4 | 16 | 6 | |
| P2-10 | 24 | 2 | 15 | 7 | |
| P2-11 | 28 | 0 | 20 | 8 | |
| P2-12 | 28 | 1 | 18 | 9 | |
| P2-13 | 17 | 3 | 8 | 6 | |
| P2-14 | 18 | 1 | 7 | 10 | |
| P2-15 | 26 | 0 | 12 | 14 | |
| P2-16 | 21 | 1 | 10 | 10 | |
| P2-17 | 10 | 0 | 4 | 6 | |
| P2-18 | 12 | 0 | 3 | 9 | |
| P2-23 | 13 | 0 | 5 | 8 | |
| P2-24 | 5 | 0 | 1 | 4 | hanya 70 baris |

**Batch 19–22 tidak pernah diterima Claude** (urutan loncat dari 18 ke 23). Kalau masih ada,
proses sebelum penggabungan; kalau tidak, dianggap dilewati.

Tren: hasil Terima turun dari ±40 per batch (batch01–03) menjadi 5–13 (batch17–24); T1 kosong
berturut-turut sejak batch17. Pasangan terbaik sudah terambil di batch awal.

**T1 yang diterima (32 pasangan)** — sebaiknya dicek ulang di animasi goresan Kamus:
勺/匀 夫/矢 材/村 什/仟 仅/仪 仲/伸 侣/倡 元/无 凤/风 半/牛 卯/卵 句/旬 吏/更 呜/鸣 坏/坯 宁/守
巳/巴 早/旱 枉/柱 枯/桔 毋/母 沦/沧 沽/洁 洁/浩 白/臼 矢/矣 苦/苫 针/钎 钓/钧 闭/闲 佐/佑 已/巴

**Duplikat dengan data lama yang ditolak/dilewati** (±55 pasangan, semuanya sudah tercakup): P1 29 pasangan
(mis. 今/令 id 23, 免/兔 id 5, 玉/王 id 51, 种/钟 id 86); P2 mis. 义/又 id 12, 乌/鸟 id 29, 乓/兵 id 122,
冶/治 id 65, 刀/刃 id 132, 勿/匆 id 149, 大/太 id 2, 很/恨/狠 id 82, 戊/戌/戍/戎 id 59, 折/析 id 109,
拔/拨 id 14, 洛/落 id 90, 责/贵 id 70, 辩/辫 id 58, 日/曰 id 144, 木/术 id 54.

---

## 4. Kebijakan penilaian (dipertahankan dari v36, ditambah)

1. **Catatan hanya klaim yang pasti**: sebut komponen (X memuat Y, radikal kiri A vs B), **tanpa**
   posisi/arah garis kecuali yakin. Kalau susunan komponen tidak pasti, catatan sengaja **umum**
   ("sangat mirip secara keseluruhan", "berkerangka 衣 dengan unsur di tengah") — contoh: 篡/纂, 幂/幕, 衰/衷/袁.
2. **Tolak bila tidak yakin komposisi** (contoh: 啮/齿, 蓑/襄) daripada menulis catatan yang mungkin salah.
3. **Hindari karakter langka** (𢦏, 𠂤, 𰻝, dll.) di catatan karena tidak tampil di font standar;
   gunakan penjelasan umum.
4. **Jenis B (radikal samping beda) diterima** di P2 karena kriteria sengaja dilonggarkan, tetapi
   **hanya jika komponen non-radikal sama atau mirip** (kiri: 亻/扌/木/氵/讠/钅/忄/饣/纟; kanan: komponen yang sama).
   Pasangan yang **hanya berbagi radikal** dengan komponen utama berbeda = Tolak (bagian terbesar dari Tolak).
5. Dedup dilakukan terhadap `confusion_groups.json` **dan** antarbatch sebelum menyetujui.
6. Konsistensi tingkat: pola sama → tingkat sama (mis. 扌 vs 木 + komponen sama = T2; radikal 亻 vs 钅 + komponen sama = T3).

---

## 5. Temuan metodologi

1. **Sumber `confused_chinese` berurutan per radikal** menghasilkan banyak pasangan acak. Yield terbaik
   datang dari pasangan dengan **komponen non-radikal sama** atau **beda 1–2 goresan** (contoh batch08, 09).
2. Batch tanpa saran AI (04+) tetap bisa dinilai cepat; kolom `hsk_*` membantu memprioritaskan.
3. Pasangan yang berkaitan (satu karakter muncul di banyak pasangan) menghasilkan **keluarga** yang
   perlu disatukan saat penggabungan: 己/已/巳/巴; 莫 (募/幕/暮/墓/慕); 戈 (戎/戌/成/戍/戒/戏);
   隹 (推/椎/谁/难/堆/锥/雏/惟/稚/维); 周 (稠/调/绸/铜); 古/吉/舌 (沽/洁/活/浩/枯/桔/括);
   其 (其/箕/典/斯/期/欺); 申 (伸/神/坤); 木+撇 (未/末/朱/来).

---

## 6. Rencana penggabungan akhir (belum dikerjakan)

1. Unggah ulang `confusion_groups.json` terbaru (pastikan belum ada perubahan) dan, kalau mau skrip
   disesuaikan, `gabungkan_karakter_mirip.py`.
2. Bangun grup dari `karakter_mirip_DITERIMA_semua_P1_P2.csv` (528 pasangan) **per tingkat**:
   pasangan yang tersambung dalam tingkat yang sama disatukan (batasi ±4 anggota; keluarga besar dipecah),
   dengan satu kalimat catatan per grup. Grup 3+ karakter diberi catatan gabungan.
3. **Skema:** data lama tidak punya field `tier`. Usulan: field `tier` (angka 1/2/3) pada grup baru;
   **grup lama dianggap T1 secara default**. `gabungkan_karakter_mirip.py` kemungkinan menolak field
   tak dikenal → perlu disesuaikan (terima `tier`, validasi 1–3, tanpa mengubah grup lama).
4. Dry-run dulu; periksa peringatan "memperluas grup lama" (mis. grup yang memuat 借/惜 id 56, 己/已/巳 id 1);
   baru `--apply` (checkpoint otomatis dari skrip).
5. Setelah di-apply: tes tampilan Kamus dan game Flashcard; tambahkan **pemisahan tingkat di UI**
   (filter/badge T1·T2·T3) agar T2/T3 tidak membanjiri.

Perkiraan hasil: ±250–320 grup baru dari 528 pasangan (jumlah akhir bergantung pada penyatuan keluarga).
Catatan: `verifikasi_karakter_mirip_batch5_FIXED.txt` (88 grup dari P1 + P2-01) hanya draf awal;
**sumber kebenaran untuk penggabungan adalah file `…DITERIMA_semua_P1_P2.csv`** (sudah memuat batch itu).

---

## 7. File sesi ini (arsip)

Semua berada di folder keluaran sesi ini dan sebaiknya disimpan ke `C:\mandarin_app\arsip_karakter_mirip\p2\`:

- `karakter_mirip_P2_batch01…18, 23, 24_100_REVIEWED.csv` (20 file) dan `karakter_mirip_review_P1_91_REVIEWED.csv`
- `karakter_mirip_DITERIMA_semua_P1_P2.csv` — **ringkasan siap pakai**: kolom `sumber, a, b, tier, catatan_pasangan` (528 baris)
- `verifikasi_karakter_mirip_batch5_FIXED.txt` — draf NDJSON (88 grup; skema: `character, confusable_with, note, tier`)
- `arsip_karakter_mirip_P2_REVIEWED.zip` — semua di atas dalam satu berkas
- `BLUEPRINT_v37.md` (file ini)

---

## 8. Sesi berikutnya: P3 batch01

Percakapan baru yang segar akan memproses `karakter_mirip_P3_batch01_100_review.csv` dan batch P3 lanjutan
sampai selesai, dengan cara yang sama (Claude mengisi `decision`/`final_tier`/`reviewer_notes`).

Yang perlu disiapkan di sesi baru:
1. Unggah `BLUEPRINT_v37.md` (dan v36 bila perlu), `confusion_groups.json`, dan
   `karakter_mirip_DITERIMA_semua_P1_P2.csv` (agar Claude dapat mengecek duplikat antar-P2/P3).
2. Tentukan di awal **kriteria dan sumber P3** (belum dibahas di sesi ini). Saran Claude: minta AI kandidat
   hanya mengusulkan pasangan **non-radikal** (komponen sama atau beda 1–2 goresan), bukan urutan radikal,
   karena itu yang paling produktif dan P2 sudah jenuh.
3. Format kolom tetap seperti bagian 1; Claude memakai pemisah sesuai file yang diunggah (`;` atau `,`).
4. Penggabungan akhir (bagian 6) dilakukan setelah P3 selesai, atau sebelumnya bila رسلان memutuskan.

---

## 9. Yang masih tertunda dari v36 (tidak disentuh sesi ini)

- Tes tampilan Karakter Mirip untuk grup batch 3 dan 4 (石/右, 尸/尺, 夕/歹, dll.).
- Perbaikan tampilan: istilah "titik" pada notes, komentar usang "53 grup" di `kamus.html`/`flashcard-decks.js`.
- Enrichment catatan id 112 (天/夫) dan 158 (木/未/末).
- Housekeeping: checkpoint ±289 MB per `save`, `.bak_before_apply_*` di `data\`.
- Backlog aktif: productive suffixes/prefixes → measure word pairing & verb complement → dictation game.

---

## Ringkasan status keseluruhan proyek

- ✅ Karakter Mirip — 160 grup (v36), **belum ditambah**.
- ✅ **P2 dikurasi: 528 pasangan Terima (T1 32 / T2 331 / T3 165)**, siap digabung; skema `tier` perlu disepakati dengan skrip penggabung.
- 🔜 **P3 batch01 (sesi baru)**, lalu penggabungan akhir + tampilan per tingkat.
- ⏸ Ditunda sadar: perbaikan tampilan, enrichment id 112/158, housekeeping, backlog fitur lain.

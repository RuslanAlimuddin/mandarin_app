# BLUEPRINT v38 — Mandarin Interaktif

Lanjutan dari BLUEPRINT v37. Sesi ini (31 Oktober 2026) satu topik: **kurasi kandidat "Karakter Mirip" tahap P3**
(batch01–13) dari sumber luar (AI kandidat), dinilai Claude, dikumpulkan untuk digabung ke `data/confusion_groups.json`.

**Status data: `confusion_groups.json` BELUM berubah.** Tidak ada `--apply` di v37 maupun v38
(masih 160 grup, 328 karakter unik seperti akhir v36). Semua hasil kurasi P2 + P3 masih berupa file CSV di luar database.

Sesi berikutnya: **P4** (percakapan baru, lihat bagian 8).

---

## 1. Alur kerja (tidak berubah dari v37)

1. **AI kandidat** menghasilkan CSV 100 pasangan (`karakter_mirip_P3_batchNN_100_review.csv`). Pemisah kolom: `,`.
2. **Claude menilai** tiap pasangan dan mengisi kolom kosong: `decision` (**Terima / Tolak**), `final_tier` (T1/T2/T3),
   `reviewer_notes` (catatan beda, singkat), `human_status` (= `REVIEWED_BY_CLAUDE`). Hasil disimpan sebagai
   `…_REVIEWED.csv`.
3. **Versi final yang dikirim رسلان yang berlaku** bila AI kandidat atau Claude merevisi keputusan.
4. Di **akhir sesi**, seluruh pasangan "Terima" digabung menjadi grup dan dimasukkan ke `confusion_groups.json`
   (dry-run → `--apply`).

Kolom dasar: `pair_id, a, b, visual_best_rank, hsk_a, hsk_b, hsk_pair_band, sources, manual_group_ids,
ai_recommendation, ai_tier_recommendation, ai_similarity_band, ai_difference_note, ai_screening_reason,
decision, final_tier, reviewer_notes, human_status`. Batch P3 tidak membawa saran AI (kolom `ai_*` kosong),
jadi seluruh penilaian dari Claude. Tulis ulang CSV dengan `utf-8-sig` (BOM) dan header yang sama.

Claude berhak menolak kandidat yang disetujui رسلان (kemiripan <70%); رسلان menyerahkan penilaian visual kepada Claude.

---

## 2. Tingkat kemiripan (disepakati رسلان, tidak berubah)

| Tingkat | Perkiraan | Ciri |
|---|---|---|
| **T1** | ±85–95% | Beda satu goresan/titik/panjang garis, atau komponen kecil sama dengan satu goresan beda (mis. 古/吉, 勺/匀, 已/巴). |
| **T2** | ±75–85% | Satu komponen/radikal beda, atau satu karakter memuat karakter lain (mis. 唁 = 言 + 口), komponen sama dengan radikal samping beda. |
| **T3** | ±70–75% | Komponen utama sama tetapi bentuk keseluruhan mulai berbeda; atau radikal berbeda cukup jauh (mis. 亻/钅). |

Pasangan <70% = **Tolak**. Persentase adalah perkiraan visual Claude, bukan ukuran pasti.
Tingkat ditampilkan terpisah; catatan grup >2 karakter memakai satu kalimat gabungan (disusun Claude saat penggabungan).

---

## 3. Hasil kurasi P3

**Total pasangan dinilai: 1.215** (batch01–12 masing-masing 100 baris; **batch13 hanya 15 baris**, jadi sumber P3 tampaknya habis).
**Terima: 45** (T1 **0**, T2 **14**, T3 **31**) ≈ 3,7%. Bandingkan P2: 528 dari ±2.060 (≈25%).
Tidak ada T1 di seluruh P3.

| Batch | Terima | Batch | Terima |
|---|---|---|---|
| P3-01 | 7 | P3-08 | 2 |
| P3-02 | 3 | P3-09 | 5 |
| P3-03 | 6 | P3-10 | 1 |
| P3-04 | 7 | P3-11 | 1 |
| P3-05 | 2 | P3-12 | 1 |
| P3-06 | 7 | P3-13 | 0 (15 baris) |
| P3-07 | 3 | **Jumlah** | **45** |

Daftar lengkap ada di `karakter_mirip_DITERIMA_P3.csv` (kolom: `sumber, a, b, tier, catatan_pasangan`).

**T2 (14):** 其/欺 完/宪 戍/戏 戍/戒 斯/欺 镇/真 咸/戌 戊/成 戎/或 戏/戒 缎/段 真/颠 其/期 咸/戊
**T3 (31):** 傍/镑 填/慎 悄/稍 惟/稚 括/桔 约/钓 绚/钩 表/衰 表/袁 顷/颁 堆/谁 悄/销 慎/镇 戒/或 扦/钎 欺/箕
稚/难 稚/雏 约/钩 维/难 咸/戒 戊/戒 戍/或 维/谁 克/免 咸/戍 堆/惟 戎/成 惟/锥 稚/维 惟/维

**Duplikat belum dicek.** `confusion_groups.json` dan `karakter_mirip_DITERIMA_semua_P1_P2.csv` tidak diunggah di sesi P3,
jadi pasangan P3 belum dibandingkan dengan 160 grup lama maupun 528 pasangan P2. Banyak pasangan P3 berada di keluarga
yang sama dengan P2 (其, 隹, 戈, 古/吉/舌), jadi sebagian besar kemungkinan duplikat atau perluasan grup — cek di dry-run.
Perhatikan khusus: 克/免 (免/兔 sudah ada sebagai id 5), 其/期 (期 disebut dalam keluarga 其 di v37), 稚/维 dan 惟/稚 (keluarga 隹).

---

## 4. Kebijakan penilaian (dipertahankan dari v36–v37, ditambah dari P3)

1. **Catatan hanya klaim yang pasti**: sebut komponen (X memuat Y, radikal kiri A vs B), tanpa posisi/arah garis kecuali yakin.
   Bila susunan komponen tidak pasti, catatan sengaja **umum** (contoh: "Sama-sama berkerangka 戈; unsur tambahan berbeda",
   "Sama-sama berkerangka 衣 dengan unsur di tengah").
2. **Tolak bila tidak yakin komposisi** (contoh: 尧, 啮/齿, 蓑/襄).
3. **Hindari karakter langka** di catatan; pakai penjelasan umum.
4. **Jenis B (radikal samping beda) diterima hanya jika komponen non-radikal sama atau mirip.**
   Pasangan yang **hanya berbagi radikal** (亻 扌 木 钅 页 辶 dll.) dengan komponen utama berbeda = **Tolak**.
   Ini penyebab ±96% Tolak di P3.
5. Dedup terhadap `confusion_groups.json` **dan** antarbatch sebelum menyetujui.
6. Konsistensi tingkat: pola sama → tingkat sama (扌 vs 木 + komponen sama = T2; 亻/钅, 忄/钅, 纟/钅, 忄/禾 + komponen sama = T3).

**Pola keputusan P3 yang sebaiknya dipakai lagi di P4:**
- Keluarga 隹 (komponen kanan sama, kiri berbeda): Terima bila kiri = 忄 / 禾 / 纟 / 又 / 讠 / 土 / 钅 (T3).
  Tolak bila kiri 牙, 小, 焦(灬), 亻+圭, 刍 (kecuali 稚/雏 yang sudah diterima di batas bawah).
- Keluarga 戈 (戊 戌 戍 戎 戒 戏 成 咸 或): Terima pasangan sesama kerangka 戈 dengan catatan **umum**.
  Tolak bila hanya satu pihak yang berkerangka 戈 (mis. 伐/戎, 伐/戒, 战/戌, 戍/放).
- Keluarga 勺/句/旬 (约/钓, 绚/钩, 约/钩): Terima jika ada komponen mirip + radikal 纟/钅 (T3).
  Tolak 均/绚 (radikal 土 vs 纟 terlalu jauh).
- Pasangan 扌 dengan komponen kanan berbeda total: Tolak (mayoritas batch02, 05, 09, 11).

---

## 5. Temuan metodologi

1. Sumber P3 = urutan radikal (`confused_chinese`). Hampir semuanya pasangan acak yang berbagi radikal;
   yield jatuh dari 7/100 (batch01) menjadi 1/100 (batch10–12) dan 0/15 (batch13).
2. Tren sama dengan P2 batch17–24: pasangan terbaik sudah terambil di batch awal dan di P1/P2.
   **Jangan kirim batch urutan-radikal lagi.** Untuk P4, minta AI kandidat membuat pasangan **non-radikal**:
   komponen non-radikal sama, atau beda 1–2 goresan, atau satu karakter memuat karakter lain.
3. **Keluarga hasil P3** (perlu disatukan/dipecah saat penggabungan, ±4 anggota per grup):
   - 戈: 戊/戌/戍/戎/戒/戏/成/咸/或 (terbesar; usulan pecah: 戍/戒/戏 dan 戊/成/戌/戎, lalu 咸/或 sesuai kedekatan)
   - 隹: 稚/难/雏/维/惟/堆/谁/锥 (+ keluarga 隹 P2: 推/椎/谁/难/堆/锥/雏/惟/稚/维)
   - 真: 填/慎/镇/真/颠
   - 其: 其/欺/箕/斯/期
   - 肖: 悄/稍/销
   - 勺/句/旬: 约/钓/钩/绚 (+ 勺/匀 T1 dan 句/旬 T1 dari P2)
   - 衣: 表/衰/袁 (+ 衰/衷/袁 dari P2)
   - lainnya berdiri sendiri: 傍/镑, 完/宪, 括/桔 (keluarga 古/吉/舌), 扦/钎 (+ 针/钎 T1 P2), 缎/段, 顷/颁, 克/免, 堆/谁.

---

## 6. Rencana penggabungan akhir (belum dikerjakan)

1. Unggah ulang `confusion_groups.json` terbaru (pastikan belum berubah), `gabungkan_karakter_mirip.py`
   (bila skrip perlu disesuaikan), `karakter_mirip_DITERIMA_semua_P1_P2.csv`, dan `karakter_mirip_DITERIMA_P3.csv`
   (+ `…_DITERIMA_P4.csv` bila P4 sudah selesai).
2. Bangun grup dari gabungan P1 + P2 + P3 (+ P4) **per tingkat**: pasangan yang tersambung dalam tingkat yang sama disatukan
   (maksimal ±4 anggota; keluarga besar dipecah), satu kalimat catatan per grup, grup 3+ karakter diberi catatan gabungan.
   Dedup dulu antara P2 dan P3 (pasangan identik: pakai tingkat yang lebih tinggi/tajam bila berbeda, lalu catat konfliknya).
3. **Skema:** data lama tidak punya field `tier`. Usulan: field `tier` (angka 1/2/3) pada grup baru; grup lama dianggap T1.
   `gabungkan_karakter_mirip.py` kemungkinan menolak field tak dikenal → sesuaikan (terima `tier`, validasi 1–3,
   tanpa mengubah grup lama).
4. Dry-run dulu; periksa peringatan "memperluas grup lama" (mis. 借/惜 id 56, 己/已/巳 id 1, 免/兔 id 5);
   baru `--apply` (checkpoint otomatis dari skrip).
5. Setelah di-apply: tes tampilan Kamus dan game Flashcard; tambahkan pemisahan tingkat di UI (filter/badge T1·T2·T3).

Perkiraan: P2 528 + P3 45 = 573 pasangan sebelum dedup → ±250–330 grup baru (bergantung penyatuan keluarga).
Sumber kebenaran: `…DITERIMA_semua_P1_P2.csv` (P1+P2) dan `…DITERIMA_P3.csv`. Draf `verifikasi_karakter_mirip_batch5_FIXED.txt` bukan sumber.

---

## 7. File sesi ini (arsip)

Simpan ke `C:\mandarin_app\arsip_karakter_mirip\p3\`:

- `karakter_mirip_P3_batch01…13_100_REVIEWED.csv` (13 file; batch13 berisi 15 baris)
- `karakter_mirip_DITERIMA_P3.csv` — ringkasan siap pakai (45 baris: `sumber, a, b, tier, catatan_pasangan`)
- `BLUEPRINT_v38.md` (file ini)

Arsip P2 (`C:\mandarin_app\arsip_karakter_mirip\p2\`) tetap berlaku; jangan ditimpa.

---

## 8. Sesi berikutnya: P4

Percakapan baru yang segar akan memproses file CSV P4 (`karakter_mirip_P4_batchNN_100_review.csv`) sampai selesai,
dengan cara yang sama (Claude mengisi `decision`/`final_tier`/`reviewer_notes`/`human_status`).

Yang perlu disiapkan di sesi baru:
1. Unggah `BLUEPRINT_v38.md` (dan v37 bila perlu), `confusion_groups.json`,
   `karakter_mirip_DITERIMA_semua_P1_P2.csv`, dan `karakter_mirip_DITERIMA_P3.csv` — **semuanya**, supaya Claude bisa
   mengecek duplikat sejak batch pertama (di P3 ini tidak dilakukan).
2. Tentukan di awal **kriteria dan sumber P4** (belum dibahas). Saran: hanya pasangan **non-radikal** (komponen sama,
   beda 1–2 goresan, atau satu karakter memuat karakter lain); **hindari** urutan radikal; larang pasangan yang hanya
   berbagi radikal; minta AI kandidat mengecualikan pasangan yang sudah ada di P1–P3.
3. Format kolom tetap; pemisah `,` (cek header file yang diunggah).
4. Rencana evaluasi: bila 2 batch berturut-turut menghasilkan ≤2 Terima, berhenti dan langsung ke penggabungan.
5. Penggabungan akhir (bagian 6) dilakukan setelah P4 selesai, atau sebelumnya bila رسلان memutuskan.

Catatan kerja: Claude menilai tanpa saran AI; Tolak bila ragu; catatan umum bila susunan komponen tidak pasti;
satu pesan per batch dengan file hasil + ringkasan singkat (pasangan ragu, keluarga, total berjalan).

---

## 9. Yang masih tertunda dari v36–v37 (tidak disentuh)

- Tes tampilan Karakter Mirip untuk grup batch 3 dan 4 (石/右, 尸/尺, 夕/歹, dll.).
- Perbaikan tampilan: istilah "titik" pada notes, komentar usang "53 grup" di `kamus.html`/`flashcard-decks.js`.
- Enrichment catatan id 112 (天/夫) dan 158 (木/未/末).
- Housekeeping: checkpoint ±289 MB per `save`, `.bak_before_apply_*` di `data\`.
- Cek ulang animasi goresan Kamus untuk T1 P2 (32 pasangan) dan pasangan ragu P3 (克/免, 稚/雏, 约/钩, 绚/钩, 咸/戊).
- Backlog aktif: productive suffixes/prefixes → measure word pairing & verb complement → dictation game.
- Batch P2-19 s.d. 22 tidak pernah diterima Claude (masih terbuka dari v37).

---

## Ringkasan status keseluruhan proyek

- ✅ Karakter Mirip — 160 grup (v36), **belum ditambah**.
- ✅ P2 dikurasi: 528 pasangan Terima (T1 32 / T2 331 / T3 165).
- ✅ **P3 dikurasi: 45 pasangan Terima (T1 0 / T2 14 / T3 31)** dari 1.215 pasangan; sumber P3 habis (batch13 = 15 baris).
- 🔜 **P4 (sesi baru)**, lalu penggabungan akhir P1–P4 + tampilan per tingkat.
- ⏸ Ditunda sadar: perbaikan tampilan, enrichment id 112/158, housekeeping, backlog fitur lain.

# BLUEPRINT v39 — Mandarin Interaktif

Lanjutan dari BLUEPRINT v38. Sesi ini (1 November 2026) satu topik: **kurasi kandidat "Karakter Mirip" tahap P4**
(batch01–13) dari sumber **hanzigrid**, dinilai Claude, dikumpulkan untuk digabung ke `data/confusion_groups.json`.

**Status data: `confusion_groups.json` BELUM berubah.** Tidak ada `--apply` di v37, v38, maupun v39
(masih 160 grup, 328 karakter unik seperti akhir v36). Semua hasil kurasi P2 + P3 + P4 masih berupa file CSV di luar database.

Sesi berikutnya: **penggabungan akhir** (lihat bagian 7), bukan kurasi batch baru.

---

## 1. Alur kerja (sama dengan v38)

1. Sumber P4 mengirim CSV 100 pasangan (`karakter_mirip_P4_batchNN_100_review.csv`). Pemisah kolom `,`.
   Sumber P4 = **hanzigrid** (dikonfirmasi رسلان). Kolom `manual_group_ids` berisi kode `HZG-xxxx`; kolom `ai_*` kosong.
2. **Claude menilai** tiap pasangan: `decision` (**Terima / Tolak**), `final_tier` (T1/T2/T3), `reviewer_notes`
   (catatan beda, singkat), `human_status` (= `REVIEWED_BY_CLAUDE`). Hasil disimpan sebagai `…_REVIEWED.csv`
   (`utf-8-sig`, header sama).
3. **Versi final yang dikirim رسلان yang berlaku** bila ada revisi keputusan.
4. Di **akhir**, pasangan "Terima" digabung menjadi grup dan dimasukkan ke `confusion_groups.json` (dry-run → `--apply`).

Tingkat kemiripan tetap seperti v38: **T1** ±85–95%, **T2** ±75–85%, **T3** ±70–75%; <70% = Tolak.
Claude berhak menolak kandidat yang disetujui رسلان (kemiripan <70%).

---

## 2. Keputusan kriteria P4 (penting)

- **Batch01–07: kriteria LONGGAR.** Menerima pasangan tipe "X memuat Y" (mis. 传/专, 惊/京) dan "komponen sama + radikal samping berbeda" (mis. 位/拉, 吵/抄) sebagai T2/T3. Yield 33–52%.
- **Batch08–13: kriteria KETAT (Pilihan B, diputuskan رسلان setelah batch07).**
  Hanya terima bila **benar-benar mirip secara visual**, bukan sekadar "yang satu berisi yang lain".
  - Terima: beda satu goresan (T1), satu goresan tambahan (白/百, 皿/血, 目/自), radikal samping hampir kembar
    (忄 vs 氵, 扌 vs 氵) dengan komponen sama (慢/漫, 情/清, 抄/沙), kerangka sama dengan satu garis tegak berbeda (田/由/甲/申).
  - Tolak: tipe "X memuat Y", pasangan yang hanya berbagi radikal, radikal samping berbeda jauh (亻 vs 土/车/阝,
    氵 vs 讠, 氵 vs 犭, 氵 vs 辶), komposisi tidak pasti.
  Yield jatuh ke 2–13%.
- Keputusan batch01–07 **tidak disaring ulang**. Kolom `kriteria` di rekap menandai `longgar` / `ketat` agar bisa dipilih saat penggabungan.

---

## 3. Hasil kurasi P4

**Total pasangan dinilai: 1.258** (batch01–12 masing-masing 100 baris; **batch13 hanya 58 baris**, sumber tampak habis).
**Terima: 361** (T1 **35**, T2 **202**, T3 **124**) ≈ 29%.

| Batch | Terima | T1/T2/T3 | Kriteria |
|---|---|---|---|
| P4-01 | 49 | 9/30/10 | longgar |
| P4-02 | 52 | 2/21/29 | longgar |
| P4-03 | 42 | 0/23/19 | longgar |
| P4-04 | 33 | 0/26/7 | longgar |
| P4-05 | 50 | 3/25/22 | longgar |
| P4-06 | 52 | 4/22/26 | longgar |
| P4-07 | 37 | 1/26/10 | longgar |
| **Subtotal longgar** | **315** | | |
| P4-08 | 13 | 0/12/1 | ketat |
| P4-09 | 10 | 3/7/0 | ketat |
| P4-10 | 6 | 3/3/0 | ketat |
| P4-11 | 12 | 10/2/0 | ketat |
| P4-12 | 2 | 0/2/0 | ketat |
| P4-13 (58 baris) | 3 | 0/3/0 | ketat |
| **Subtotal ketat** | **46** | | |
| **Jumlah** | **361** | **35/202/124** | |

Rekap siap pakai: `karakter_mirip_DITERIMA_P4.csv` (kolom: `sumber, a, b, tier, catatan_pasangan, kriteria`).

**Aturan berhenti** (≤2 Terima dua batch berturut-turut) tidak terpenuhi persis (batch12 = 2, batch13 = 3),
tetapi sumber P4 habis, jadi P4 dianggap selesai.

---

## 4. Keluarga hasil P4 (perlu disatukan/dipecah saat penggabungan)

Keluarga kriteria ketat (kecil, bersih):
- 田/由/甲/申 (6 pasangan T1, satu grup 4 karakter) + 申/电 (T2)
- 白/百, 皿/血, 目/自, 狠/狼, 止/正, 火/灭, 汁/汗 (T1); 母/每, 水/永, 棵/稞, 老/考, 篮/蓝, 问/闻, 部/都, 针/钉, 竟/章 (T2)
- 日/白, 木/本, 未/禾, 末/禾 (T1/T2) — beririsan dengan id 158 (木/未/末)
- 扌/氵 + komponen sama: 扬/汤, 抄/沙, 投/没, 抬/治, 抽/油; 忄/氵: 慢/漫, 情/清, 怕/拍; 我/找, 手/毛, 扎/打, 心/必, 思/息

Keluarga kriteria longgar (besar, perlu dipecah ±4 anggota per grup):
- 亻 + komponen kanan (价/份/介/分, 他/也/地/她, 位/立/拉/垃, 保/呆, 偷/输/愉/俞, 你/您/尔, dll.)
- 口 + komponen kanan (吗/妈/马, 咳/孩/该/刻, 吵/少/抄/沙/炒/秒, 啊/阿, 听 dan 嗳/暖 dll.)
- 元 (园/完/玩/远), 京 (凉/就/惊/谅), 且 (姐/祖/租/粗), 生 (姓/性/胜), 台 (始/抬/治), 又 (又/双/汉/叉/及/极/级/友/反/发/饭), 匕 (匕/化/北/比/华/花)
- 大/夫/矢 (天/夫/失/矢/太/犬), 巾 (巾/币/市/布/带), 土 + 成 (城/诚), dll.

**Pasangan ragu** (cek ulang visual saat tes Kamus): 万/方, 上/正, 中/由, 中/甲, 九/刀, 亮/高, 么/云, 会/合, 介/分, 傅/博,
允/充, 价/份, 即/既, 桌/卓, 友/发, 反/发, 北/比, 党/堂, 其/具, 共/并, 全/金, 先/光, 内/肉, 句/可, 司/同, 同/向,
右/后, 后/石, 哭/器, 复/夏, 在/左, 失/天, 字/学, 尺/尽, 州/川, 月/用, 术/犬, 竟/章.

**Contoh Tolak yang sebaiknya konsisten:** pasangan yang hanya berbagi radikal (亻 扌 木 氵 讠 钅 贝 舟 彳 等), tipe 听/呢/所/诉,
群 贝 (财/败/购), 舟 (股/航/般/船), 让/达/还/这/送, 线/试/钱/饿, 疼/病/瘦, 究/穷/空/穿/突, 简/间/闻.

---

## 5. Kebijakan penilaian (dipertahankan dari v38)

1. Catatan hanya klaim yang pasti (sebut komponen, tanpa posisi/arah garis kecuali yakin). Bila tidak pasti, catatan umum.
2. Tolak bila tidak yakin komposisi (mis. 印/却, 剧/据, 健/聿).
3. Hindari karakter langka di catatan.
4. Dedup terhadap `confusion_groups.json` **dan** antarbatch sebelum menyetujui (**P4 belum didedup**, lihat bagian 6).
5. Konsistensi tingkat: pola sama → tingkat sama.

---

## 6. Duplikat belum dicek

`confusion_groups.json`, `karakter_mirip_DITERIMA_semua_P1_P2.csv`, dan `karakter_mirip_DITERIMA_P3.csv` **tidak diunggah** di sesi P4,
jadi 361 pasangan P4 belum dibandingkan dengan 160 grup lama, 528 pasangan P2, dan 45 pasangan P3.
Perkiraan overlap tinggi di: 也/他/地/她, 止/正/证, 田/由/甲/申, 木/本/未/末, 母/每, 免/兔, 己/已/巳, 借/惜, 天/夫/失, 犬/太/术, 云/京/元, 隹.
Selain itu ada **overlap antar-P4** (batch longgar), mis. 净/静, 俩/辆, 咳/孩/该, 凉/就/惊, 吵/抄/沙, 空/突 keluarga.

---

## 7. Rencana penggabungan akhir (sesi berikutnya)

1. Unggah: `confusion_groups.json` terbaru (pastikan masih 160 grup), `karakter_mirip_DITERIMA_semua_P1_P2.csv`,
   `karakter_mirip_DITERIMA_P3.csv`, `karakter_mirip_DITERIMA_P4.csv`, serta `gabungkan_karakter_mirip.py` bila ada
   (catatan lama v35: skrip ini **tidak ada di disk**; perlu dibangun dari nol).
2. **Keputusan awal yang perlu dibahas dulu** (kebiasaan kita: diskusi dua arah sebelum membangun):
   a. Pakai semua 361 pasangan P4, hanya yang `ketat` (46), atau `ketat` + T1/T2 terbaik dari `longgar`?
   b. Penyaringan ulang batch longgar? (opsional)
   c. Cara memecah keluarga besar (亻, 口, 又, dll.): per komponen atau per radikal, maksimal ±4 anggota per grup.
   d. Skema `tier` (angka 1/2/3) pada grup baru; grup lama dianggap T1; perluasan grup lama (借/惜 id 56, 己/已/巳 id 1, 免/兔 id 5, 木/未/末 id 158, 天/夫 id 112).
3. Bangun grup per tingkat (pasangan tersambung dalam tingkat yang sama), satu kalimat catatan per grup, catatan gabungan untuk 3+ karakter.
   Dedup dulu antara P2, P3, P4 (pasangan identik: pakai tingkat yang lebih tajam, catat konflik).
4. Dry-run dulu; periksa peringatan "memperluas grup lama"; baru `--apply` (checkpoint otomatis).
5. Setelah di-apply: tes tampilan Kamus dan game Flashcard; tambahkan pemisahan tingkat di UI (filter/badge T1·T2·T3).

Perkiraan: P2 528 + P3 45 + P4 (46 sampai 361) pasangan sebelum dedup → jumlah grup baru bergantung pada keputusan 2a dan 2c.

---

## 8. File sesi ini (arsip)

Simpan ke `C:\mandarin_app\arsip_karakter_mirip\p4\` (juga ke repo GitHub pribadi bila diinginkan; upload dilakukan sendiri oleh رسلان):

- `karakter_mirip_P4_batch01…12_100_REVIEWED.csv` (12 file)
- `karakter_mirip_P4_batch13_REVIEWED.csv` (58 baris)
- `karakter_mirip_DITERIMA_P4.csv` — rekap 361 baris (`sumber, a, b, tier, catatan_pasangan, kriteria`)
- `BLUEPRINT_v39.md` (file ini)

Arsip P2 dan P3 tetap berlaku; jangan ditimpa.

---

## 9. Yang masih tertunda dari v36–v38 (tidak disentuh)

- Tes tampilan Karakter Mirip untuk grup batch 3 dan 4 (石/右, 尸/尺, 夕/歹, dll.).
- Perbaikan tampilan: istilah "titik" pada notes, komentar usang "53 grup" di `kamus.html`/`flashcard-decks.js`.
- Enrichment catatan id 112 (天/夫) dan 158 (木/未/末).
- Housekeeping: checkpoint ±289 MB per `save`, `.bak_before_apply_*` di `data\`.
- Cek ulang animasi goresan Kamus untuk T1 P2 (32 pasangan), pasangan ragu P3 (克/免, 稚/雏, 约/钩, 绚/钩, 咸/戊), dan pasangan ragu P4 (bagian 4).
- Backlog aktif: productive suffixes/prefixes → measure word pairing & verb complement → dictation game.
- Batch P2-19 s.d. 22 tidak pernah diterima Claude (masih terbuka dari v37).

---

## Ringkasan status keseluruhan proyek

- ✅ Karakter Mirip — 160 grup (v36), **belum ditambah**.
- ✅ P2 dikurasi: 528 Terima (T1 32 / T2 331 / T3 165).
- ✅ P3 dikurasi: 45 Terima (T1 0 / T2 14 / T3 31) dari 1.215 pasangan.
- ✅ **P4 dikurasi: 361 Terima (T1 35 / T2 202 / T3 124) dari 1.258 pasangan; 315 kriteria longgar + 46 kriteria ketat.**
- 🔜 **Penggabungan akhir P1–P4 (sesi baru)** + tampilan per tingkat.
- ⏸ Ditunda sadar: perbaikan tampilan, enrichment id 112/158, housekeeping, backlog fitur lain.

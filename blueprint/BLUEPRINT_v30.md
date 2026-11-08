# BLUEPRINT v30 — Mandarin Interaktif

Lanjutan dari BLUEPRINT v29. Sesi ini menyelesaikan bug D.4, memperluas
`confusion_groups.json`, dan melanjutkan pipeline E.0.2b (sinonim/antonim
Tier B) dengan perbaikan mekanisme signifikan.

---

## D.4 — Bug "Karakter Mirip" di Kelompok Kamus — **RESOLVED**

Root cause dari BLUEPRINT v29 (26 dari 115 karakter tidak punya entri sendiri
di `app_words.json`, perlu fallback ke Cidict) sudah benar dari sisi kode.
Masalah "hasil masih 1 kartu" ternyata isu eksekusi/cache di sesi
sebelumnya, bukan bug logika. Dikonfirmasi via debug `console.log` +
verifikasi visual pada beberapa grup (己/已/巳, 大/太/犬, 又/叉/义) — semua
tampil sesuai badge. Debug log sudah dibersihkan dari kode production.

## `confusion_groups.json` — 53 → 71 grup

- Ditambahkan 18 grup baru (id 54–71), 156 karakter unik total, sudah
  divalidasi (id berurutan, tanpa duplikat karakter dgn 53 grup lama).
- File final ada di `/mnt/user-data/outputs/confusion_groups.json` dari
  sesi ini — **رسلان perlu timpa file lokal `confusion_groups.json` kalau
  belum dilakukan**.
- Dibangun pipeline 3-tahap utk perluasan berikutnya (belum pernah
  dijalankan, siap dipakai kapan saja):
  1. `prompt_1_cari_karakter_mirip.txt` — AI cari kandidat baru
  2. `prompt_2_verifikasi_karakter_mirip.txt` — AI lain verifikasi/koreksi
  3. `gabungkan_karakter_mirip.py` — merge ke database dgn dedup otomatis

## E.0.2b lanjutan — Sinonim/Antonim Tier A & Tier B

**Tier A: dinyatakan TUNTAS.** 40 kandidat tersisa semuanya overlap dgn
`nuance_pairs.json` (dikonfirmasi via `diagnosa_tier_a.py`), akan selalu
0 selama Tier B tidak pernah menghasilkan kata yg overlap kondisi itu
(dan secara desain, tidak akan). **Boleh skip langkah AI utk Tier A**,
tapi `hasil_tier_a.json` (isi `[]`) tetap harus ada di folder krn
`apply_hasil_sinonim_antonim.py` akan error kalau file itu tidak ada.

**Tier B: berjalan aktif, banyak cycle sudah diproses sesi ini** (fill-rate
19–94/100 tergantung batch & AI yg dipakai). Pool awal 7.229 kandidat,
sisa terhitung ~5.938 setelah sesi ini (lihat `hitung_sisa_tier_b.py`,
estimasi 85–237 cycle lagi tergantung fill-rate).

### Perbaikan mekanisme (v3.1) — sudah diterapkan ke kedua skrip inti:
- **`_tb_empty_streak`**: counter di tiap kata, +1 tiap kali AI kembalikan
  synonyms+antonyms kosong. Reset ke 0 kalau kata itu berhasil dapat relasi
  kapan pun. Kata dgn streak ≥3 otomatis dikecualikan permanen dari pool
  Tier B (`generate_prompt_sinonim_antonim_v3.py`).
- **Exclude angka murni proaktif**: kata yg tersusun seluruhnya dari
  karakter angka (`一`...`亿`, `两`, gabungan spt `千万`) dikecualikan dari
  pool SEJAK AWAL (tidak menunggu streak), krn AI kadang berhalusinasi
  membuat "antonim" antar angka berurutan (mis. `9`↔`8`) alih-alih
  kembalikan kosong — ini tidak bisa diandalkan pada mekanisme streak.
- Instruksi tambahan di prompt Tier B: larangan eksplisit relasi
  hipernim/hiponim (mengurangi tapi tidak menghilangkan kesalahan jenis
  ini — kualitasnya **sangat bergantung pada AI eksternal yg dipakai**,
  bukan cuma prompt; رسلان menemukan satu AI jauh lebih patuh instruksi
  drpd AI lainnya).

### Pembersihan data yang sudah dilakukan sesi ini:
- **Batch 1** (`bersihkan_relasi_janggal.py`, 16 relasi, 13 kata utama):
  `当↔咚`, `铁↔金属`, `冰雪↔雪冰`, `瓜↔甜瓜/南瓜`, `细节↔详节`,
  `竟然↔当然`, `胶带↔透明胶带`, `入门↔入口/出口`, `研究生↔硕士生/博士生`,
  `迷信↔愚信`, `大于↔等于`, `被动↔被逼`, `受灾↔遇难`. **Sudah dijalankan.**
- **Batch angka** (`bersihkan_relasi_angka.py`): dibuat tapi **kemungkinan
  TIDAK PERNAH dijalankan** — رسلان memilih tidak apply batch yg
  terkontaminasi relasi angka palsu sama sekali (generate ulang dgn skrip
  v3.1 yg sudah exclude angka), jadi kontaminasi tidak sempat masuk
  `app_words.json`. **Cek status ini di awal sesi berikutnya** — kalau
  belum pernah dijalankan sama sekali, aman diabaikan (skrip tetap ada
  di outputs kalau suatu saat perlu).
- **Batch 2** (`bersihkan_relasi_janggal_batch2.py`, 8 relasi, 4 kata
  utama): `瓜↔果/果实` (lagi, kena hipernim kedua kalinya dari AI
  berbeda), `证书↔文凭/执照`, `法规↔法律`, `面子↔表面/外面/里面`.
  **Status akhir sesi: رسلان baru diminta menjalankan, belum
  dikonfirmasi hasilnya — cek di awal sesi berikutnya.**

### Yang perlu dicek di awal sesi berikutnya:
1. Apakah `bersihkan_relasi_janggal_batch2.py` sudah dijalankan +
   `checkpoint.py save`?
2. Apakah batch Tier B terakhir (berisi `肩`, `兔`, `震惊`, `不止`, `不许`,
   dll — 93/100 fill-rate) sudah di-apply tanpa `--dry-run`?
3. Lanjutkan siklus generate→AI→dry-run→apply seperti biasa. Prioritaskan
   AI yg lebih patuh instruksi anti-hipernim/hiponim kalau رسلان ingat
   yang mana.

### File-file skrip aktif (semua di `C:\mandarin_app\`, sudah diberikan
sesi ini, kemungkinan sudah ditimpa ke lokasi asli):
- `generate_prompt_sinonim_antonim_v3.py` (v3.1, dgn exclude streak + angka)
- `apply_hasil_sinonim_antonim.py` (v3.1, dgn pencatatan streak)
- `bersihkan_relasi_janggal.py`, `bersihkan_relasi_janggal_batch2.py`
- `bersihkan_relasi_angka.py` (kemungkinan belum pernah dipakai)
- `hitung_sisa_tier_b.py`, `diagnosa_tier_a.py` (diagnostik, reusable)

---

## Ringkasan status keseluruhan proyek

- ✅ D.4 (Karakter Mirip render bug) — selesai
- ✅ confusion_groups.json 53→71 grup — selesai, pipeline lanjutan siap pakai
- 🔄 E.0.2b Tier B — aktif berjalan, ~5.900 kata tersisa dari pool awal
  7.229, kemungkinan puluhan-ratusan cycle lagi (proses jangka panjang,
  bukan sesuatu yg akan "selesai" dlm sesi manapun — lanjutkan bertahap)
- Backlog aktif lain (lihat memori proyek): productive suffixes/prefixes,
  measure word pairing, dictation game, dll — belum disentuh sesi ini

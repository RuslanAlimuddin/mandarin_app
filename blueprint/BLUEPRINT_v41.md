# BLUEPRINT v41 — Mandarin Interaktif

Lanjutan dari BLUEPRINT v40. Sesi ini (11–12 November 2026): **perbaikan kecil dari bagian 8 v40**,
**tombol saring "Peran" (Bunyi/Makna)** dan **tanda 音/义 di kartu hasil** pada menu Per Komponen / Per Radikal.

**Status data:** `data/confusion_groups.json` (160 grup lama) kini **berubah di bagian catatan saja** (28 catatan, bagian 2).
`data/karakter_mirip_pasangan.json` tetap 1.174 pasangan (1.375 karakter), semua pasangan kini punya catatan.
Semua perubahan di bawah sudah diperiksa رسلان di PC, sudah terpasang, dan sudah diunggah ke repo.

---

## 1. Perbaikan kecil kode

- `kamus/kamus-data.js` baris 201: pesan "Memuat Cidict (16 MB)…" → **"Memuat Cidict (±26 MB)…"** (file Cidict hasil buka = 25,8 MiB).
- Komentar usang "53 grup" diperbarui: `kamus.html` baris 307 (kini "160 grup + 1.174 pasangan") dan
  `flashcard/flashcard-decks.js` baris 1219 ("160 grup"). Hanya komentar, tampilan tidak berubah.

## 2. Perbaikan data catatan

- **14 pasangan tanpa catatan kini terisi** (28 baris karena dua arah): 推/排, 推/摊, 成/戍, 载/截, 志/忠, 微/徽, 德/惩, 忍/忽,
  念/忿, 思/恩, 恬/悟, 患/惠, 惑/感, 授/援. Disusun dari pembongkaran bentuk di `dictionary.txt`; 患/惠 (bagian atas 惠
  tertulis "？" di dictionary) dikonfirmasi رسلان lewat animasi goresan. 2 pasangan tanpa tingkat sudah T3 di JSON (tidak ada yang diubah).
- **Kata "titik" diganti "goresan pendek"** pada **55 catatan** (26 grup lama + 29 pasangan baru), ditulis ulang satu per satu
  sesuai bentuk karakter (氵 = tiga goresan pendek, 冫 = dua). Koreksi sekaligus: **压** (grup 102) goresan pendeknya di **samping 土**,
  bukan di atas; **下/于** kini "下 goresan pendek di kanan batang, 于 berkait"; sisa catatan internal dibuang
  ("gpt_audit_note=" di 冶/治, 刀/刃, 勿/匆, 卯/卵; "Catatan duplikat dari reviewer…" di 戊/戍).
- **Catatan grup 112 (天/夫) dan 158 (木/未/末) diperkaya**, pasangan 天/夫 dan 未/末 di berkas pasangan disamakan.
  天: garis atas lebih panjang dari garis bawahnya; 夫: garis atas lebih pendek. 未: garis atas lebih pendek; 末: garis atas lebih panjang
  (dikonfirmasi di animasi goresan). Catatan internal "(kemungkinan sudah ada di id 35/158)" dibuang.
- Pembanding lama/baru 55 catatan disimpan sebagai `periksa_55_catatan_titik.csv` (di PC رسلان, bukan di repo).
- `karakter_mirip_FINAL_diterima.csv` (sumber kebenaran, bagian 3 v40) **tidak ada di repo**; di repo hanya
  `karakter_mirip/hasil_gabungan/KARAKTER_MIRIP_FINAL_ACCEPTED.csv` (419 pasangan sepakat). Aplikasi hanya membaca JSON, jadi tidak berpengaruh.

## 3. Menu Per Komponen / Per Radikal: tombol Peran dan tanda 音/义

Semua di `kamus/kamus-komponen-posisi.js` (file tambahan; `kamus-cards-ui.js` **tidak diubah**).

- **Tombol saring "Peran 〈komponen〉: Semua | Bunyi (n) | Makna (n)"** di bar saring, di sebelah baris Posisi. Bunyi/Makna hanya
  menampilkan karakter yang memakai komponen sebagai penanda bunyi (cara baca) / makna (arti). Bisa digabung dengan filter Posisi.
  Kata dua karakter disembunyikan saat Bunyi/Makna aktif; memilih "Kata" atau komponen lain mengembalikan ke "Semua".
  Judul hasil ikut berubah ("· hanya penanda bunyi/makna"). Tombol hanya muncul bila komponen punya daftar bunyi atau makna.
- **Tanda kecil di ujung kanan kartu karakter tunggal:** **音** (yīn, bunyi; biru) dan **义** (yì, makna; hijau). Tooltip contoh:
  "音 yīn · bunyi: 青 memberi petunjuk cara baca 情". Satu baris keterangan "音 yīn = bunyi · 义 yì = makna" di bar saring.
  Karakter yang belum tercatat dan kata dua karakter **tidak diberi tanda**. Kartu tetap satu baris (Fix A2).
- **Cara pasang (lapisan tambahan, bukan ganti):** `kamus-komponen-posisi.js` membungkus `window.buildResultCard` (menambah tanda bila
  `roleOn`) dan `window.selectGroupItem` / `doSearch` / `renderGroupResultsFromWords` (mematikan `roleOn` di menu lain).
  Flag `roleOn` hanya aktif saat hasil Komponen/Radikal tampil; menu Karakter Mirip, Tema, pencarian, dan Flashcard tidak memakainya.
  Gaya CSS (`.kp-role`, `.kp-yin`, `.kp-yi`) disisipkan dari file yang sama.
- **Data:** `index_komponen_posisi.json` sudah punya daftar `bunyi` dan `makna` per komponen; tidak ada data baru.
  Dari ±16.900 entri karakter di daftar komponen, ±3.900 (23%) belum tercatat bunyi maupun makna (tidak ada yang tercatat keduanya).
  Karena itu jumlah Bunyi + Makna bisa lebih kecil dari Semua (wajar).
- **Keputusan رسلان:** tombol saring dulu (A), lalu tanda di kartu (B); opsi hasil dipisah dua bagian (C) **tidak dipakai**.

## 4. Keputusan: tautan langsung Karakter Mirip dilewati

- Tidak ada tombol atau halaman yang membuat `#group=mirip:<indeks>`. Tautan `#group=` hanyalah pintu umum di `kamus-init.js`;
  `peta-bahasa.html` hanya memakainya untuk tema, kelompok khusus, radikal, dan akar kosakata.
- Cabang `selectGroupItem('mirip', idx)` (v29) dibuat untuk klik di menu lama (160 grup). Menu Karakter Mirip yang tampil sekarang
  dikelola `openMirip()` di `kamus-komponen-posisi.js` (tombol per karakter), jadi kode lama praktis tidak terpakai.
- **Dilewati.** Bila kelak ingin "bagikan/simpan tautan satu karakter", itu fitur baru yang dibahas dulu.

## 5. Pemeriksaan di sisi رسلان (semua selesai)

- Tes tampilan Karakter Mirip grup batch 3–4 (karakter hanya-di-Cidict: 石/右, 尸/尺, 夕/歹, 矢, 夫, 申, 旦, 乏, 匆) di panel Kamus
  dan game Flashcard: **semua tampil normal**.
- Cek animasi goresan **T1 dari P2 (32 pasangan)**: **semuanya benar-benar sangat mirip**; tidak ada yang diturunkan.
- **Pasangan ragu P3 (克/免, 稚/雏, 约/钩, 绚/钩, 咸/戊) dan P4 (±37 pasangan, daftar di v39 bagian 4):** putusan **TETAP untuk semuanya**.

## 6. Cara kerja membaca repo (untuk sesi berikut)

- Alat baca web **tidak bisa membuka halaman GitHub biasa** (ditolak robots). Claude mengambil repo dengan `git clone` lalu
  `git pull`; folder `blueprint/` terbaca penuh. Setelah mengunggah berkas baru, beri tahu "sudah saya unggah" agar Claude menarik ulang.
- Pertahankan pola nama `BLUEPRINT_v<angka>.md` di `blueprint/`.

## 7. Yang masih tertunda

- Opsi: kelompokkan bentuk varian radikal (氵 扌 忄 …) di bawah 214 radikal Kangxi. Detail "jumlah varian per radikal" belum ada;
  bisa dihitung dari `data/index_komponen_posisi.json` (`radikal`, 186 entri).
- Housekeeping: checkpoint dan `.bak_before_apply_*`.
- Opsional: sekitar 23% karakter di daftar komponen belum tercatat bunyi/maknanya (tanda 音/义 tidak muncul untuknya).
- Backlog fitur: productive suffixes/prefixes → measure word pairing & verb complement → dictation game.

## Ringkasan status proyek

- ✅ Karakter Mirip: 1.174 pasangan baru (+160 grup lama), semua bercatatan; kata "titik" sudah diganti "goresan pendek".
- ✅ Menu Per Komponen / Per Radikal: filter Karakter/Kata, Posisi, **Peran (Bunyi/Makna)**, dan tanda **音/义** per kartu.
- ✅ Semua pemeriksaan visual v36–v40 (batch 3–4, T1 P2, pasangan ragu P3/P4) selesai.
- ✅ Repo GitHub publik berisi seluruh file aplikasi untuk dibaca Claude.
- 🔜 Opsi varian radikal, housekeeping, lalu backlog fitur.

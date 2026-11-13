# BLUEPRINT v42 — Mandarin Interaktif

Lanjutan dari BLUEPRINT v41. Sesi ini (12–13 November 2026) adalah **sesi diskusi desain**: **tidak ada kode atau data aplikasi yang diubah**.
Topik: fitur **Awalan & Akhiran produktif (Tingkat 2, 60 entri)**, pelajaran **Pilar 12**, opsi **varian radikal**, **beres-beres cadangan**,
dan **pembagian kerja dengan GPT**. Semua keputusan di bawah sudah disepakati رسلان; **belum ada yang dibangun**.

Berkas pendamping (simpan di `blueprint/`): **`PROMPT_GPT_Pembentukan_Kata.md`** (prompt lengkap untuk GPT, memuat 60 entri beserta kata contoh yang sudah disetujui).

---

## 1. Aturan kerja (diperbarui)

- **Diskusi dulu untuk SETIAP pekerjaan yang menghasilkan kode atau berkas**, sekecil apa pun (memperluas butir 8 di v3 yang hanya berlaku bila ada ambiguitas).
  Alur: tanya-jawab dua arah (رسلان bertanya, Claude menjawab dan juga bertanya agar tidak ada yang terlewat) → ada kesepakatan → baru dikerjakan. Disebut "kebiasaan kita".
- Bahasa sederhana, tanpa istilah teknis (atau jelaskan dengan kata sehari-hari).
- Saat merujuk ke hal yang sudah disampaikan, **sebutkan ulang isi dan jumlah poinnya** (mis. "daftar di atas: akhiran 43 poin dan awalan 17 poin").
- Satu berkas .bat peluncur sempat dibuat tanpa diskusi dalam sesi ini; **dibatalkan**, tidak dipakai (lihat bagian 8).

## 2. Keputusan fitur "Awalan & Akhiran" (Tingkat 2)

- **60 entri**, satu entri per karakter: **akhiran 43** + **awalan 17**. **副 dikeluarkan** (hanya 1 kata di kamus).
  - **A. Orang/pelaku (7):** 者 家 员 师 生 手 长
  - **B. Sifat dan konsep abstrak (10):** 化 性 度 率 感 力 量 法 观 点
  - **C. Jenis dan gaya (3):** 型 式 类
  - **D. Bidang dan ilmu (5):** 学 论 主义 业 界
  - **E. Tempat dan lembaga (9):** 馆 室 站 场 院 店 所 区 部
  - **F. Alat, barang, biaya (5):** 器 机 品 物 费
  - **G. Pelengkap kata benda (4):** 们 子 儿 头
  - **H. Awalan: penanda awal (4):** 老 第 初 可
  - **I. Awalan: menolak/meniadakan (5):** 不 无 非 未 反
  - **J. Awalan: tingkat dan keseluruhan (8):** 超 准 总 半 自 全 同 共
  - Kata contoh lengkap (3–5 per entri, semua dari `app_words.json`, sudah disetujui) ada di `PROMPT_GPT_Pembentukan_Kata.md`.
- **Kata contoh (Pilihan C):** komputer mengumpulkan kandidat dari kamus, dipilih 3–5 terbaik per entri, kata yang menyesatkan dibuang dan dicatat sebagai
  **"mirip tetapi bukan"** (mis. 国家 bukan akhiran 家; 或者 bukan akhiran 者; 动员 kata kerja). رسلان memeriksa daftar sebelum dipasang.
- **Karakter dua posisi** (mis. 手 家 力 机 场 学 同 总): **satu entri per karakter**, dengan bagian "sebagai akhiran" dan "sebagai awalan"; di menu muncul sekali
  dengan tanda "awalan + akhiran". Pemakaian depan yang hanya kata biasa (家 di 家庭) masuk catatan "mirip tetapi bukan", bukan "awalan".
- **准** dipertahankan dengan catatan: awalan paling lemah (di kamus berarti "tepat/boleh", bukan "calon" seperti 准妈妈).
- **小 dan 边** (sudah ada di Tata Bahasa HSK 1, poin 56 dan 57) **tidak ditambahkan** (opsi B): di menu Kamus cukup catatan "Lihat juga" dengan tombol ke poin itu.
  Data: 边 = 25 kata (hampir semua HSK 1), 小 = 48 kata tetapi hampir semuanya kata biasa "kecil". **边 diurus kelak bersama kata penunjuk posisi (Tingkat 3).**
- **Permainan latihan (Flashcard tes kecil → Word Builder dan/atau Ujian HSK latihan lebih serius): putaran berikutnya**, setelah semuanya terpasang. Bukan sekarang.
  (Catatan: Word Builder saat ini melatih pola kalimat, bukan pembentukan kata; menambah soal baru di sana lebih besar daripada sekadar tombol.)
- **Tingkat 3 ditunda**: 族 迷 热 控 症 剂 炎 盲, kata penunjuk posisi (上 下 里 外 中 间 + 边), serta ide dari dokumen 汉语构词法: 客 友 体 形 色 心 气, awalan 阿/小/大, 多/单.

## 3. Penempatan: tiga lapis yang saling tertaut

- **Kamus (`kamus.html`)**: item baru **"🧩 Awalan & Akhiran"** di bagian **Kelompok**, **tepat di bawah 🌱 Akar Kosakata** (bilah samping sekarang: Per Radikal,
  Per Goresan, Per Tema, Per Pinyin, Per Struktur, Per Komponen Fonetik, Akar Kosakata, Kelompok Khusus, Karakter Mirip). Isi: daftar entri menurut kelompok;
  klik entri → arti, catatan, kata contoh yang bisa diklik (mirip menu Per Radikal). Saling tautan dengan Akar Kosakata.
- **Tata Bahasa (`tatabahasa.html`)**: **memperluas topik yang sudah ada "Prefix & Suffix (Imbuhan)"** lewat **berkas data baru**; **poin lama tidak diubah** (770 poin utuh).
  Topik itu kini berisi: HSK 1 poin 56 (小— 第—) dan 57 (—们 —边), HSK 3 poin 16.3 (—子), HSK 9 kategori "准词缀" (后— 亲— —观 —界 —然 —坛 —制 —鬼 …).
  Entri baru untuk **第, 们, 子** ditandai **pendalaman** dan menyebut nomor poin lama. Tiap entri: penjelasan singkat, **2 kalimat contoh** (Mandarin + pinyin + terjemahan),
  keterangan tingkat HSK, tautan ke Kamus. Penomoran awalan `AFX.` agar tidak bentrok.
- **Pelajaran (Peta Bahasa)**: **Pilar 12 "Pembentukan Kata (构词法)"** sebagai rumah topik, memakai sistem Pelajaran Lengkap yang sudah ada (`data/pelajaran/pilar_N.json`).
  Enam bagian: (1) apa itu awalan/akhiran Mandarin (beda dengan imbuhan Indonesia), (2) cara membaca kartu entri, (3) karakter bermakna ganda (家 生 长 率 手 点 化 头),
  (4) tabel perbandingan akhiran pelaku 者 家 员 师 生 手 长, (5) awalan penolak 不 无 非 未 反, (6) peta cepat 60 entri dan apa yang menyusul.
  **Pilar lama tidak ditulis ulang.** Peta hanya dirapikan ringan: Akar Kosakata dipindah dari Pilar 11 ke Pilar 12, Pola Pembentukan Kata Majemuk didaftarkan,
  Reduplikasi diberi tombol ke Pilar 9.
- **Pembagian tugas:** Pelajaran = pintu masuk dan konsep; Kamus = mencari dan menjelajah (kata bisa diklik); Tata Bahasa = penjelasan per entri dan kalimat; ketiganya
  tertaut lewat tombol. **Tidak ada menu baru di bilah atas** (sudah 9 halaman).
- Dokumen usulan kurikulum 汉语构词法 (7 modul) **tidak diadopsi penuh**: modul kata majemuk, kata berulang, partikel, dan penggolong sebagian besar sudah ada
  (Pola Pembentukan Kata Majemuk, Akar Kosakata, Pilar 3/4/9) → modul 3–7 masuk rencana lanjutan. Ide yang dipakai: pelajaran pengantar, format tetap tiap entri,
  halaman karakter bermakna ganda, tidak memaksa karakter menjadi imbuhan.

## 4. Opsi varian radikal (opsi B)

Dari **186 entri** `radikal` di `data/index_komponen_posisi.json`, **20 adalah bentuk varian** dari radikal induk (jumlah karakter): 氵 (465, 水), 艹 (418, 艸), 钅 (357, 金),
扌 (341, 手), 亻 (276, 人), 纟 (264, 糸), 忄 (169, 心), 阝 (159, 邑/阜), ⺮ (145, 竹), 讠 (143, 言), 犭 (87, 犬), 饣 (86, 食), 刂 (74, 刀), 衤 (72, 衣), 礻 (44, 示),
攵 (41, 攴), 灬 (29, 火), 罒 (26, 网), ⺀ (2), ⺳ (2).
**Keputusan:** entri varian **tetap terpisah**, diberi keterangan **"bentuk varian dari <induk>"** dan **tautan dua arah** ke induk, diletakkan **berdekatan dengan induk**
di daftar. ⺀, ⺳, dan 阝 (asal dua radikal berbeda) dibiarkan dengan keterangan singkat. Data lama tidak berubah.

## 5. Beres-beres cadangan (opsi A)

Skrip: **daftar dulu** (nama, ukuran, tanggal), **mode lihat-dulu**, lalu cadangan lama (`checkpoint`, `.bak_before_apply_*`) **dipindah** ke folder `arsip_cadangan_lama`,
**bukan dihapus**. "Lama" = **lebih tua dari 2 hari**; satu cadangan terbaru tiap jenis dan semua yang dibuat dalam 2 hari terakhir tetap di tempatnya.
Folder arsip dihapus رسلان sendiri kelak.

## 6. Pembagian kerja dengan GPT (folder `kerja_gpt_afiks/`)

- **GPT = pengisi data. Claude = pengatur aplikasi (semua kode) dan pemeriksa mutu.**
- GPT membuat folder **`kerja_gpt_afiks/`** di repo (subfolder `acuan/`, `hasil/`, `laporan/`), **menyalin hanya berkas relevan**, **menulis hanya di folder itu**,
  tidak mengubah berkas asli, tidak menyentuh kode. (Dipilih folder baru, bukan cabang/branch.)
- **Tahap:** 0 audit (laporan, lalu berhenti) → 1 data Kamus (`afiks_kamus.json` + skema) → 2 poin Tata Bahasa (`grammar_afiks.json`, skema = poin `grammar_hsk*.json`)
  → 3 Pilar 12 (`pilar_12.json`) → 4 perluasan bagian yang sudah ada (hanya bila usulan Tahap 0 disetujui). Tiap tahap berakhir laporan dan berhenti, menunggu "LANJUT".
- **Cakupan "perluasan":** seluruh topik pembentukan kata. GPT melihat dulu apa yang sudah ada, lalu **mengusulkan** cara melengkapinya (tidak langsung menulis).
- **Pemeriksaan oleh Claude** (git clone folder itu): JSON valid; semua kata contoh ada di `app_words.json`; pinyin bernada; tidak ada sisa `[citation:n]` atau catatan internal;
  berkas asli tidak tersentuh; skema cocok dengan yang dibutuhkan kode.
- **Penilaian GPT dilakukan di percakapan baru** (rencana رسلان). Claude disarankan menilai **per tahap** (mulai dari laporan Tahap 0), bukan menunggu semuanya selesai.

## 7. Temuan dari pembacaan repo (BELUM diperbaiki, hanya dicatat)

- **`data/pelajaran/pilar_3.json`** (Pilar 3, 量词) **isinya salinan pelajaran Kata Kerja Modal** (isi JSON sama dengan `pilar_5.json`, 40 bagian). Pelajaran 量词 belum ada;
  hanya sebagian kecil di Pilar 9 (bagian K, reduplikasi 量词).
- **`app_words.json`:** 重点 tercatat *chóngdiǎn*, seharusnya *zhòngdiǎn* (belum dicek di aplikasi).
- **`grammar_hsk9.json`**, kategori "准词缀": teks memuat sisa penanda `[citation:1]`.
- **Akar Kosakata** (`produktif_karakter.json`): 师 tidak ada di daftar akar. Akar Kosakata dicantumkan di bawah Pilar 11 (Variasi Bahasa & Sejarah) pada Peta Bahasa;
  **Pola Pembentukan Kata Majemuk** tidak ditemukan terdaftar di `peta-bahasa.html` (fiturnya ada di Kamus dan Flashcard).
- Pilar 4 (26 bagian: 的 得 地 了 着 过 …) dan Pilar 9 (38 bagian: reduplikasi AA, AABB, ABAB …) sudah sangat lengkap.

## 8. Cara membuka aplikasi dan cara kerja repo

- **Peluncur resmi = ekstensi Live Server di VS Code** (pembuat: Ritwick Dey): klik kanan file .html → **Open with Live Server**. رسلان sudah memasangnya kembali; semua .html terbuka normal.
  Dobel klik .html langsung menampilkan **"Gagal Memuat Data (CORS)"** (aplikasi harus lewat localhost). Alasan memilih Live Server: file yang baru diedit selalu di urutan teratas
  (urut Date Modified) dan langsung terbuka di halaman itu. Cadangan jika perlu: `python -m http.server 8000` di folder `mandarin_app`, buka `http://localhost:8000`.
- Claude membaca repo dengan **`git clone`** (termasuk `--filter=blob:none`, 377 berkas); `git pull` untuk memperbarui. Daftar folder lewat API GitHub terkena batas laju;
  `raw.githubusercontent.com` bisa untuk satu berkas; `web_fetch` ke halaman GitHub dan ke tautan bagikan DeepSeek **ditolak**. Isi percakapan DeepSeek harus ditempel manual.
- Setelah mengunggah berkas baru, beri tahu **"sudah saya unggah"** agar Claude menarik ulang. Pertahankan pola nama `BLUEPRINT_v<angka>.md`.

## 9. Rencana ke depan (urutan)

1. **GPT mengerjakan Tahap 0–3** (prompt: `PROMPT_GPT_Pembentukan_Kata.md`). Persetujuan Tahap 0 menentukan perlu tidaknya Tahap 4.
2. **Percakapan baru: penilaian kinerja GPT** per tahap (Claude memeriksa folder `kerja_gpt_afiks/` dengan skrip otomatis dan memberi laporan untuk diteruskan ke GPT).
3. **Paket pembangunan (setelah data GPT lolos pemeriksaan), tiap butir dibahas dulu:**
   (a) item "🧩 Awalan & Akhiran" + panel di Kamus, (b) pemuat data baru di Tata Bahasa (memperluas topik Prefix & Suffix), (c) Pilar 12 + perapian Peta Bahasa,
   (d) varian radikal (bagian 4), (e) skrip beres-beres cadangan (bagian 5). **Catatan:** (d) dan (e) **tidak bergantung pada data GPT**, jadi boleh dikerjakan kapan saja.
   Teks Pilar 12 dan kalimat Tata Bahasa diperiksa رسلان dulu sebelum dipasang.
4. **Putaran berikutnya:** latihan awalan/akhiran (Flashcard → Word Builder/Ujian HSK); Tingkat 3; perbaikan temuan bagian 7.
5. **Backlog lama:** pasangan penggolong & pelengkap kata kerja → permainan dikte; opsional 23% karakter di daftar komponen belum tercatat bunyi/maknanya.
6. **Ide opsional:** penanda HSK 2.0 dan HSK 3.0 terpisah di entri (data sudah punya dua kolom).

## Ringkasan status proyek

- ✅ (v36–v41) Karakter Mirip, menu Per Komponen / Per Radikal dengan Peran Bunyi/Makna dan tanda 音/义, semua pemeriksaan visual selesai.
- ✅ Sesi ini: **desain lengkap** fitur Awalan & Akhiran (60 entri), penempatan tiga lapis, varian radikal, beres-beres cadangan, pembagian kerja dengan GPT, dan prompt GPT.
- ✅ Peluncur aplikasi (Live Server) berfungsi lagi.
- 🔜 GPT mengisi data → penilaian → pembangunan paket (a–e) → latihan → Tingkat 3.

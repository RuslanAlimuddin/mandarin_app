# BLUEPRINT v40 — Mandarin Interaktif

Lanjutan dari BLUEPRINT v39. Sesi ini (11 November 2026): **penggabungan akhir Karakter Mirip P1–P4**,
**pemisahan "kemiripan bentuk" dari "komponen sama, posisi beda"**, dan **menu Kelompok baru di Kamus**.

**Status data:** `data/confusion_groups.json` **tidak diubah** (masih 160 grup lama, dianggap T1).
Semua hasil baru berada di dua file data baru (bagian 4). Tahap 3 (kode Kamus) sudah terpasang dan berjalan baik.

---

## 1. Rekonsiliasi P1–P4 (hasil dari GPT, 51 file digabung jadi 3)

- `KARAKTER_MIRIP_FINAL_ACCEPTED.csv` = 419 (GPT dan Claude sepakat terima)
- `KARAKTER_MIRIP_FINAL_REJECTED.csv` = 3.440 (keduanya tolak)
- `KARAKTER_MIRIP_REVIEW_REQUIRED.csv` = 1.012 (610 beda pendapat, 400 tak terbaca, 2 konflik)

**Temuan yang mengubah angka REVIEW_REQUIRED:**
1. **300 pasangan "belum dinilai" ternyata sudah dinilai Claude** (P2-01, 03, 04; `human_status = REVIEWED_BY_CLAUDE`).
   Penyebab terbaca kosong: file memakai pemisah `;` dan keputusan ada di kolom `decision` yang sudah ada.
   Hasil: **115 Terima (T1 10, T2 83, T3 22), 185 Tolak.** Rincian: `pemulihan_300_pasangan_dinilai_claude.csv`.
2. **71 pasangan P2-20 dinilai AI lain**, bukan Claude (status APPROVED/REJECTED, tingkat TIER_A/B/C).
   Keputusan رسلان: pakai aturan Claude + GPT saja → hanya **估/悟 (T3) diterima**, 70 ditolak.
   Daftar pembanding: `pembanding_71_pasangan_batch20.csv`.
3. **Tingkat lama TIER_A → T2, TIER_B → T3** (133 pasangan di P2-19/21/22; penilai tidak pasti, diberi tanda di kolom asal).

## 2. Aturan keputusan (رسلان)

- **Diterima** bila Claude **atau** GPT menerima. **Ditolak** bila keduanya menolak.
- Pasangan yang hanya satu pihak menilai mengikuti pihak itu.
- **Aturan pemisahan:** pasangan berbagi **komponen utama** (≥3 goresan, posisi sama):
  T1/T2 → tampil di **Karakter Mirip dan grup komponen**; T3 → **grup komponen saja**.
  Berbagi komponen kecil (<3 goresan) → tetap Karakter Mirip. Tidak berbagi komponen → Karakter Mirip.
- Komponen kecil dikumpulkan dalam satu kategori "Komponen Kecil". Grup berkunci radikal: hanya radikal sisi **kanan**
  (页 鸟 阝 刂 攵 欠 隹 见 力) disertakan di grup utama; radikal kiri/atas/bawah dilewati.

## 3. Hasil akhir

**1.174 pasangan diterima** (T1 95, T2 621, T3 458), 1.375 karakter unik.
Asal: disepakati 419, hanya Claude 708, hanya GPT 47 (termasuk 29 "Claude belum menilai").
Jalur tampil: Karakter Mirip saja 631, Karakter Mirip + komponen 298, komponen saja 245.
Catatan: 14 pasangan tanpa catatan; 2 tanpa tingkat (diisi T3, diberi keterangan di kolom catatan).
Sumber kebenaran: `karakter_mirip_FINAL_diterima.csv` (kolom: a, b, tingkat, asal_keputusan, jalur_tampil,
jenis_kemiripan, komponen_sama, posisi, catatan).

## 4. File data baru (di `data/`)

| File | Isi |
|---|---|
| `karakter_mirip_pasangan.json` | 1.375 karakter → daftar `[karakter lain, tingkat, catatan, asal]`; asal: s = disepakati, c = hanya Claude, g = hanya GPT |
| `index_komponen_posisi.json` | `komponen` (1.038) dan `radikal` (186): karakter per posisi (kiri/kanan/atas/bawah/luar/dalam), tanda `kecil`, label bunyi/makna, daftar karakter penanda bunyi/makna |

Dibangun dari `dictionary.txt` (Make Me a Hanzi, 9.574 karakter; pembongkaran tingkat pertama), bentuk tradisional
dinormalisasi (鳥→鸟 dst.), jumlah goresan dari `hanzi_writer_data.json`/`app_words.json`/`dictionary.txt`.
Pinyin dan arti tidak disimpan; Kamus mengambil dari `app_words.json` atau Cidict.

## 5. Perubahan kode Kamus (terpasang)

- `kamus/kamus-karakter-mirip.js` **versi 2**: panel detail membaca grup lama + pasangan baru; tiap pasangan punya lencana
  tingkat, catatan sendiri, dan tombol "Hanya yang disepakati". Satu karakter boleh punya banyak pasangan.
- `kamus/kamus-komponen-posisi.js` (file **tambahan**, dimuat **sebelum `kamus-init.js`** di `kamus.html`):
  - menu "Per Komponen" (ganti nama dari "Per Komponen Fonetik") dan "Per Radikal" dengan filter **Semua | Karakter | Kata**
    dan **posisi**; karakter di luar HSK lewat Cidict;
  - entri lama yang belum ada di data baru ditampilkan di bagian "Lainnya (data posisi belum tersedia)";
  - badge sidebar: Per Radikal 245, Per Komponen 1.298, Karakter Mirip menurut jumlah karakter;
  - menu Kelompok → Karakter Mirip: chip per karakter, penyaring tingkat T1/T2/T3.
- Cadangan versi lama disimpan رسلان di PC. File lain di Kamus tidak diubah.

## 6. Temuan teknis (penting untuk sesi berikut)

- `index_phonetic.json` adalah **indeks komponen umum** (965 kunci, kata + karakter), bukan hanya fonetik.
- Menu Kelompok selalu memakai `app_words.json` (HSK, 11.983 entri) apa pun saklar sumber (HSK/Cidict); karena itu badge tidak berubah.
- Badge Per Radikal lama dihitung dari field `radical` di `app_words.json` (须 tercatat radikal 彡, bukan 页).
- `components` di `app_words.json` hanya satu tingkat dan kadang berbeda dari `dictionary.txt` (mis. 扬); `dictionary.txt` kadang memuat "？".
- Panel Karakter Mirip lama hanya mengingat satu grup per karakter (batasan, sudah diperbaiki di versi 2).
- Radikal Kangxi resmi = 214; indeks aplikasi memuat bentuk varian (氵 扌 忄 …), jadi jumlahnya lebih besar.

## 7. Repo GitHub (publik)

`https://github.com/RuslanAlimuddin/mandarin_app` — cermin struktur `C:\mandarin_app`:
77 file aplikasi (10 halaman HTML, `shared/`, `kamus/`, `flashcard/`, `wordbuilder/`, `data/` termasuk
`grammar_hsk1–9.json` dan `pelajaran/pilar_1–11.json`), `data/cidict_index.json.gz` (dikompres), `data/dictionary.txt`,
`blueprint/`, `karakter_mirip/`, `skrip/`. Claude membaca repo dengan `git clone` (hanya baca). Alat bantu:
`scan_kamus.py` (menelusuri file yang dipakai halaman, membuat folder salinan), `intip_komponen.py` (laporan komponen).
Jangan unggah: checkpoint, `.bak*`, ZIP, `cidict_split/`, `balasan/`, `py/laporan_json*`, `New folder/`.

## 8. Yang masih tertunda

- Lencana "penanda bunyi/makna" per karakter di kartu hasil (saat ini hanya di judul hasil Per Komponen).
- Deep-link `#group=mirip:<indeks>` dan `selectGroupItem('mirip', …)` masih memakai 160 grup lama.
- Opsi: kelompokkan bentuk varian radikal di bawah 214 radikal Kangxi.
- Pesan "Memuat Cidict (16 MB)" usang (file kini ±25,8 MB).
- 14 pasangan tanpa catatan dan 2 tanpa tingkat (lihat bagian 3).
- Dari v36–v39: tes tampilan Karakter Mirip grup batch 3–4; istilah "titik" pada notes; komentar usang "53 grup";
  enrichment catatan id 112 (天/夫) dan 158 (木/未/末); housekeeping checkpoint dan `.bak_before_apply_*`;
  cek animasi goresan untuk T1 P2 dan pasangan ragu P3/P4; backlog fitur (productive suffixes/prefixes →
  measure word pairing & verb complement → dictation game).

## Ringkasan status proyek

- ✅ Karakter Mirip: 1.174 pasangan baru (+160 grup lama) tampil per pasangan dengan tingkat dan asal.
- ✅ Menu Per Komponen / Per Radikal dengan filter karakter/kata dan posisi.
- ✅ Repo GitHub publik berisi seluruh file aplikasi untuk dibaca Claude.
- 🔜 Perbaikan kecil di bagian 8, lalu backlog fitur.

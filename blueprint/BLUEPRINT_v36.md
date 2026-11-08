# BLUEPRINT v36 — Mandarin Interaktif

Lanjutan dari BLUEPRINT v35. Sesi ini (24 Oktober 2026) satu topik: **menuntaskan ekspansi dan
audit "Karakter Mirip"** (`data/confusion_groups.json`), item pertama dari backlog aktif v35.
Hasil akhir: **71 → 160 grup, 156 → 328 karakter unik**, dan 17 catatan lama yang terbukti
salah sudah dikoreksi.

Sesi ini juga menghasilkan `RESUME_PERJALANAN_PROYEK.md` (peta seluruh blueprint v1–v35).
File itu hanya gambaran arah, bukan pengganti blueprint.

---

## 1. Koreksi catatan sejarah (penting, jangan diulang kesalahannya)

- **BLUEPRINT v28 keliru** menyebut Karakter Mirip "belum pernah dibangun". Fitur ini sudah
  dibangun di v9 (deck Flashcard), hilang tanpa catatan (kemungkinan tertimpa saat
  resync PART-file/modularisasi), ditemukan "yatim" di v28, lalu dibangun ulang di v29
  (panel Kamus + deck Flashcard + Kelompok Kamus). Bug D.4 tuntas di v30.
- **BLUEPRINT v30 keliru** menyebut pipeline 3-tahap ekspansi "dibangun, siap pakai".
  Scan seluruh folder (696 file) menunjukkan `prompt_1_*.txt`, `prompt_2_*.txt`, dan
  `gabungkan_karakter_mirip.py` **tidak pernah ada di disk**. Pipeline dibangun dari nol sesi ini.
- Pelajaran umum: klaim "sudah dibangun/siap pakai" di blueprint harus dicek ke disk
  (`intip_folder_project.py`) sebelum dipercaya.

---

## 2. Hasil ekspansi data

| Batch | Cara | Grup baru | id | Total grup |
|---|---|---|---|---|
| (awal) | — | — | 1–71 | 71 |
| 1 | AI 1 + AI 2 (prompt awal) | 39 | 72–110 | 110 |
| 2 | AI 1 + AI 2 (prompt diperketat ke jenis A) | 22 | 111–132 | 132 |
| 3 | AI 1 + AI 2 | **1** (石/右) | 133 | 133 |
| 4 | **Penambang data** + AI 2 | 27 | 134–160 | **160** |

Karakter unik: 156 → 262 → 292 → 294 → **328**.

**Jenis kemiripan** yang dipakai sebagai pedoman prompt:
- **Jenis A** (diprioritaskan): selisih kecil bentuk — satu goresan/titik, panjang atau arah garis,
  satu komponen kecil di dalam/luar bingkai (mis. 己/已/巳, 末/未, 干/午, 了/子).
- **Jenis B** (keluarga komponen: komponen sama, radikal samping beda, mis. 他/她/地/池):
  batch 1 didominasi jenis ini (±33 dari 39 grup). Sudah banyak dan tumpang tindih dengan fitur
  Komponen Fonetik, jadi **dihentikan** mulai batch 2.

**Temuan: pencarian lewat ingatan AI jenuh** (batch 3: 14 dari 30 kandidat sudah tercakup, 15 di-drop,
1 lolos). Solusinya `tambang_karakter_mirip.py` yang mencari dari data, bukan ingatan AI (lihat bagian 3).

**Kandidat yang ditahan / dibuang** (bisa dipertimbangkan lagi kalau ada bukti visual):
- Ditahan karena struktur tidak bisa dipastikan: **目/且**, **旦/且** (struktur 且), **头/买** (dekomposisi
  data mendukung 买 = 乛 + 头, tapi AI verifikator menolak).
- Dibuang: 八/小 (小 bukan 八 + satu goresan), 又/丈, 月/且/甩 (bukan selisih satu goresan),
  丘/乒/乓 (duplikat hubungan 兵/乒/乓, id 122).
- Anggota tambahan yang valid tetapi belum dimasukkan (dari AI sesi lain): 荷 (河/何/荷),
  络 (落/络/洛), 底 (纸/低/底), 朱 (未/末/朱, notes AI menolak dengan alasan HSK yang lemah).

---

## 3. Alat baru (semua di `C:\mandarin_app\`)

| File | Fungsi |
|---|---|
| `buat_prompt_karakter_mirip.py` | Membuat prompt tahap 1 (cari kandidat; memuat daftar grup yang sudah ada sebagai "jangan diulang") dan tahap 2 (verifikasi). Prompt tahap 1 fokus jenis A; tahap 2 memeriksa klaim posisi/komponen dan men-drop jenis B. Memberi **peringatan** kalau ada file batch yang disimpan setelah `confusion_groups.json` terakhir berubah dan belum di-apply. |
| `gabungkan_karakter_mirip.py` | Validasi + merge ke `confusion_groups.json`. **Dry-run default**; `--apply` = checkpoint (subprocess `checkpoint.py save`) + backup `.bak_<waktu>` + tulis atomik. Menolak: skema salah, note bukan Bahasa Indonesia/di luar 12–220 karakter, karakter tak ada di `app_words.json` maupun Cidict, duplikat/turunan grup lama atau sesama batch. Peringatan: karakter hanya di Cidict, grup memperluas grup lama. **Arsip otomatis** ke `arsip_karakter_mirip\batch_<waktu>\` (salinan, file asli tidak dipindah). Parser tahan terhadap teks pengantar, pagar ```, baris menempel, objek terpotong. |
| `tambang_karakter_mirip.py` | Penambang kandidat **jenis A** dari `data/dictionary.txt` (dekomposisi IDS): karakter X = karakter dasar Y + **satu goresan tunggal**, hanya untuk karakter di himpunan "umum" (`char_etymology_id.json` + entri 1-karakter `app_words.json`), pasangan yang sudah tercakup dibuang. Tanpa flag = laporan saja; `--tulis` menulis `kandidat_karakter_mirip.txt`. Note keluarannya sengaja polos (fakta dari dekomposisi); AI 2 yang menyempurnakan. |
| `perbaiki_note_karakter_mirip.py` | Mengganti **hanya field `note`** grup yang sudah ada, dari file NDJSON `{"id","character","note"}`. Pengaman: id harus ada, karakter harus cocok dengan id, struktur lain diverifikasi tidak berubah, checkpoint + backup, idempoten. |
| `intip_folder_project.py` | Menyisir seluruh folder proyek (struktur, nama file, isi file) berdasarkan kata kunci. Alat utama untuk memeriksa apa yang benar-benar ada di disk. |

File data/arsip sesi ini (disimpan sebagai referensi): `verifikasi_karakter_mirip_FIXED.txt` (batch 1),
`…_batch2_FIXED.txt`, `…_batch3_FIXED.txt`, `…_batch4_FIXED.txt`, `perbaikan_note_lama.txt` (14 note),
`perbaikan_note_lama_2.txt` (3 note), folder `arsip_karakter_mirip\`.

Alat lama yang sengaja **tidak dipakai lagi**: `intip_confusion_groups.py` (cacat: tidak menembus
wrapper `{"groups":[…]}`, melaporkan "0 karakter" secara keliru).

---

## 4. Alur kerja baku untuk batch berikutnya

Jalankan dari `C:\mandarin_app\`. **Selalu awali dengan `python`** (sempat terjadi `--apply` yang
tidak jalan karena kata `python` terlupa; tanpa output sama sekali = tidak berjalan).

**Jalur A — kandidat dari AI** (sudah jenuh, hanya kalau ada ide pola baru):
1. `python buat_prompt_karakter_mirip.py` → salin `prompt_karakter_mirip_1_cari.txt` ke AI 1.
2. Tab Notepad++ `kandidat_karakter_mirip.txt`: `Ctrl+A`, `Ctrl+V`, `Ctrl+S`.

**Jalur B — kandidat dari data** (lebih produktif):
1. `python tambang_karakter_mirip.py` (laporan) lalu `python tambang_karakter_mirip.py --tulis`.

**Lanjutan (kedua jalur):**
3. `python buat_prompt_karakter_mirip.py kandidat_karakter_mirip.txt` → salin
   `prompt_karakter_mirip_2_verifikasi.txt` ke AI 2.
4. Tab `verifikasi_karakter_mirip.txt`: `Ctrl+A`, `Ctrl+V` (**hanya baris `{"character"…`**), `Ctrl+S`.
5. `python gabungkan_karakter_mirip.py verifikasi_karakter_mirip.txt` (dry-run) → **kirim hasilnya
   dan upload file `verifikasi_…txt` ke Claude** (laporan memotong note di 70 karakter; kesalahan
   hanya terlihat dari isi penuh).
6. Claude meninjau dan membuat `…_FIXED.txt`. رسلان dry-run ulang, lalu `--apply`.
7. **Jangan membuat prompt batch berikutnya sebelum `--apply` selesai** (daftar "jangan diulang"
   dibaca dari file data; batch yang belum di-apply menyebabkan AI mengulang usulan yang sama).

File batch lama boleh tetap di tempatnya dan terbuka di Notepad++; tinggal ditimpa.

---

## 5. Audit catatan lama (id 1–71): 17 dari 71 salah (±24%)

Dipicu catatan baru 木/未/末 yang bertentangan dengan id 35. رسلان memverifikasi lewat animasi
goresan di Kamus bahwa 末 garis atas lebih panjang dan 失 diawali goresan miring, sehingga id 35
dan id 26 terbukti **terbalik**. Audit penuh lalu menemukan 17 catatan salah, semuanya sudah
diganti lewat `perbaiki_note_karakter_mirip.py`:

- **14 dari pengetahuan Claude** (keyakinan 90–98%): id 1 (己已巳), 2 (大太犬), 4 (少小), 13 (直真),
  20 (告吉), 25 (贝见), 26 (失夫), 27 (天夭), 34 (体休), 35 (末未), 36 (目自), 49 (云会动),
  52 (土士), 58 (辨辩辫瓣).
- **3 dari pengamatan langsung رسلان** pada animasi goresan: id 11 (刀力), 15 (午牛), 28 (开井).

Catatan id 72–160 ditinjau Claude saat dimasukkan (beberapa notes AI diperbaiki, lihat bagian 6),
tetapi belum diperiksa ulang secara visual.

---

## 6. Pelajaran metodologi

1. **Verifikasi AI wajib ditinjau.** Kesalahan yang ditemukan di notes buatan AI: komponen
   tradisional untuk karakter sederhana (柬 untuk 练/炼; seharusnya 东), posisi komponen
   (颗: 果 di kiri, bukan kanan), arah panjang garis terbalik (天/夫), kalimat obrolan AI ikut
   masuk ke `note` ("丘 tidak dipertahankan…"), dan AI verifikator tidak konsisten (men-drop
   子/孔 dan 舌/乱 sebagai "jenis B" tetapi meloloskan 弓/引).
2. **Kebijakan penulisan note yang aman:** tulis hanya klaim yang pasti; hindari menyebut posisi
   (kiri/kanan/atas/bawah) atau arah panjang garis kecuali yakin atau sudah diverifikasi visual.
   Bentuk yang aman: "X pada dasarnya adalah Y dengan satu goresan tambahan".
3. **Sumber kebenaran visual: animasi goresan di Kamus**, diamati رسلان. Ketika meminta
   verifikasi, ajukan **pertanyaan deskriptif** ("ceritakan apa yang terlihat"), bukan
   "benarkah …?" yang cenderung dijawab "ya".
4. **Data lebih andal daripada ingatan AI** untuk menemukan kandidat (penambang menemukan 27
   grup setelah AI jenuh), tetapi ia buta terhadap pasangan yang dekomposisinya memakai `？`
   (mis. 白 = ？+日), pasangan yang tidak berselisih satu goresan (日/目), dan karakter di luar
   himpunan "umum".
5. **Tempel hanya jawaban final AI.** Satu kali AI 2 menempelkan proses berpikirnya sebelum
   jawaban; skrip tetap membacanya, tetapi draf bisa terbaca lebih dulu daripada versi final.
6. **Istilah "titik"** pada note bisa menyesatkan: 点 (丶) berbentuk goresan pendek miring,
   bukan tanda ".", dan animasi di Kamus menampilkannya sebagai garis pendek ke bawah.

---

## 7. Yang perlu dicek di awal sesi berikutnya

1. **Tes tampilan Karakter Mirip untuk grup batch 3 dan 4** yang berisi karakter hanya-di-Cidict
   (mis. 石/右, 尸/尺, 夕/歹, 矢, 夫, 申, 旦, 乏, 匆). Cek di panel Kamus dan di game Flashcard
   (deck ada di accordion **FILTER GAME**). Batch 1–2 sudah dites normal.
2. **Perbaikan tampilan yang ditunda:**
   - Pada notes, ganti/jelaskan kata "titik" (mis. "titik (点)", atau keterangan kecil di panel).
   - Komentar usang "53 grup" di `kamus.html` dan `flashcard-decks.js` (data sebenarnya 160).
   - Badge Kamus membaca jumlah grup dari file data (sudah benar setelah `F5`/hapus cache).
3. **Enrichment opsional:** catatan id 158 (木/未/末) sengaja tanpa arah panjang garis; kini 末 atas
   lebih panjang sudah terbukti, sehingga bisa ditambahkan. Catatan id 112 (天/夫) juga tanpa
   arah dan belum diverifikasi visual.
4. **Opsional — ekspansi lagi:** pasangan yang ditahan (目/且, 旦/且, 头/买) bila struktur 且 dan
   头/买 bisa dipastikan visual; anggota tambahan 荷, 络, 底, 朱; atau memperluas penambang
   (komponen sama dengan posisi tertukar, penggantian satu komponen kecil, penanganan `？`).
5. **Housekeeping:** tiap `checkpoint.py save` ±289 MB (±375 file); dengan rotasi 20 terbaru,
   ruang disk ±5,8 GB. Ditambah ratusan `app_words.json.bak_before_apply_*` (±12 MB) di `data\`.
   Belum mendesak, tetapi perlu dipantau.

---

## 8. Backlog aktif berikutnya (urutan yang sudah disepakati رسلان)

1. ~~Ekspansi `confusion_groups.json` (Karakter Mirip)~~ — **TUNTAS sesi ini** (pada level yang
   dianggap cukup; lihat bagian 7 poin 4 jika ingin dilanjutkan).
2. **Productive suffixes/prefixes** (者/家/性/化/员 → "keluarga kata") — siap dimulai.
3. **Measure word pairing** dan **verb-chaining/complement** — butuh kurasi data dari nol.
4. **Dictation game** (listen-and-type).

Item lama yang pernah direncanakan lalu terlupakan (lihat `RESUME_PERJALANAN_PROYEK.md` bagian 4
untuk daftar lengkap): bersihkan polusi `meanings_id` (E.2), struktur makna kata polisemi (E.3),
perluasan contoh kalimat (E.0.1b), skema kata majemuk 3+ karakter, patch heuristik negasi `未` di
`cek_dan_bersihkan_hasil_tier_b.py` (tidak mendesak, Tier B tuntas).

---

## Ringkasan status keseluruhan proyek

- ✅ D.4, E.0.2b Tier B (sinonim/antonim) — selesai (v30–v35)
- ✅ **Karakter Mirip — 160 grup, catatan lama diaudit dan dikoreksi (v36).** Pipeline ekspansi,
  penambang data, dan alat perbaikan catatan tersedia dan teruji.
- 🔜 Berikutnya: productive suffixes/prefixes → measure word pairing & verb complement →
  dictation game.
- ⏸ Ditunda sadar: perbaikan tampilan Karakter Mirip (istilah "titik", komentar usang),
  enrichment catatan id 112/158, housekeeping `.bak` dan checkpoint.

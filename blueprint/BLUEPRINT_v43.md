# BLUEPRINT v43 — Mandarin Interaktif

Lanjutan dari BLUEPRINT v42. Sesi ini (13–18 November 2026) **membangun dan memasang** paket "Pembentukan Kata (构词法)" yang dirancang di v42,
lalu melakukan **pembersihan data** (sitasi, Pilar 3, bacaan dan zhuyin kata, frasa, kata majemuk).
Semuanya sudah dijalankan رسلان di PC, diuji, dan diunggah ke repo. Yang tersisa ada di bagian 5.

Berkas pendamping di `blueprint/`: `BLUEPRINT_v42.md` (rancangan, **bagian 4 dan 5 masih berlaku**), `PROMPT_GPT_Pembentukan_Kata.md`, `RESUME_PERJALANAN_PROYEK.md`.

---

## 1. Aturan kerja (v42 + tambahan sesi ini)

- **Diskusi dulu untuk SETIAP pekerjaan yang menghasilkan kode atau berkas** ("kebiasaan kita"): tanya-jawab dua arah sampai sepakat, baru dikerjakan.
- Bahasa sederhana tanpa istilah teknis; saat merujuk ke hal sebelumnya, **sebutkan ulang isi dan jumlah poinnya**.
- **BARU: instruksi uji coba harus lengkap dan padat**: tulis jalur klik dari awal sampai tujuan
  (mis. Kamus → Kelompok → Awalan & Akhiran → —者), jangan terlalu singkat seperti "buka kartu 者".
- **Pola skrip yang dipakai semua pekerjaan data**: mode lihat-dulu (tidak mengubah apa pun) dan `--apply`; cadangan otomatis
  `<berkas>.bak_<jenis>_<tanggal-jam>`; menolak bekerja bila data berbeda dari yang diperiksa; pemeriksaan akhir setelah menulis (kembali ke cadangan bila gagal); aman dijalankan ulang.
- Claude menguji skrip dan fitur di **salinan repo** (peramban tiruan) sebelum dikirim; رسلان menguji di PC lalu mengunggah berkas yang berubah (**bukan** berkas `.bak_*`).
- Claude **menarik ulang repo sendiri** setelah GPT menulis ke repo; kata pemicu "sudah saya unggah" hanya untuk berkas yang diunggah manual.
- Pekerjaan GPT diberi pesan serah terima untuk **percakapan GPT baru** (percakapan GPT cepat penuh) dengan "rem": berhenti di batas bagian dan menulis `catatan_serah_terima.md`.
- **Cache peramban** bisa menahan data lama (mis. bacaan `gě` tampil padahal data sudah `gè`): bersihkan lewat F12 → Application → Storage → Clear site data, lalu cari ulang.
- Format berkas data: JSON indent 2, `ensure_ascii=False`, akhir baris CRLF (kecuali `graded_readers.json` LF). Skrip menulis dengan format persis itu.

## 2. Paket Pembentukan Kata: SELESAI dan terpasang

Data GPT (folder `kerja_gpt_afiks/`, Tahap 0–3, Tahap 4 dilewati) sudah diperiksa Claude dan dipasang:

| Butir | Hasil | Berkas/skrip |
|---|---|---|
| (a) Menu Kamus | "🧩 Awalan & Akhiran": satu layar 60 tombol dalam 10 kelompok A–J, kartu keterangan, kata contoh, daftar "mirip tetapi bukan", tombol ke Tata Bahasa, Pilar 12, Akar Kosakata | `kamus/kamus-afiks.js`, `data/afiks_kamus.json`, `pasang_afiks_kamus.py` |
| (b) Tata Bahasa | 60 poin AFX.01–AFX.60 sebagai level ke-10; Daftar Isi (topik Prefix & Suffix), pencarian, `#point=AFX.nn`, tombol ke Kamus dan poin lama (第 56, 们 57, 子 16.3) | `data/grammar_afiks.json`, `pasang_afiks_tatabahasa.py` |
| (c) Peta Bahasa | Pilar 12 "Pembentukan Kata (构词法)" (6 bagian), Akar Kosakata pindah dari Pilar 11, `#pilar-N`, penanda Hanzi/pinyin | `data/pelajaran/pilar_12.json`, `pasang_pilar12.py` |
| (f) Rincian kata dan pencarian | bagian "Awalan & Akhiran" di rincian kata (335 kata data, termasuk daftar "bukan") dan bilah petunjuk saat yang diketik tepat satu entri | `kamus/kamus-afiks.js` (versi baru) |

Keputusan yang berlaku: 60 entri Tingkat 2 (akhiran 43, awalan 17); 副, 小, dan 边 tidak jadi entri; **nol entri "awalan + akhiran"**;
bagian di rincian kata hanya untuk kata yang ada di data (bukan semua kata berakhiran 者).
**Ditunda**: Tingkat 3 (族 迷 热 控 症 剂 炎 盲, penunjuk posisi 上 下 里 外 中 间, 边) dan permainan latihan awalan/akhiran (Flashcard, Word Builder, Ujian HSK).

## 3. Pembersihan data: SELESAI

| Skrip | Hasil |
|---|---|
| `bersihkan_sitasi.py` | 437 penanda `[citation:n]` dihapus dari `grammar_hsk5–9.json` |
| `arsipkan_pilar3.py` | `pilar_3.json` (salinan Pilar 5) dipindah ke `data/pelajaran/arsip/`; Pilar 3 (量词) kini menampilkan "belum dibuat" |
| `terapkan_koreksi_bacaan.py` | 140 kata berbacaan ganda yang memakai bacaan dan arti jarang (mis. 听 *yǐn* "tersenyum", 个 *gě*, 打 *dá*) diperbaiki: pinyin, pinyin angka, zhuyin, arti Indonesia dan Inggris; 22 kata dua-bacaan: bacaan lazim di depan, bacaan lain jadi keterangan `[bacaan] arti`; 12 tulisan `u:`→`ü`; 34 zhuyin; salinan di `tone_drills`, `wb_pools`, `nuance_pairs`, `graded_readers`, `produktif_karakter` ikut |
| `perbaiki_frasa.py` | pinyin angka dan zhuyin 44 frasa (23 wisata + 21 lain); 这时候→*zhè shíhou*, 见过→*jiànguo*, 城里 zhuyin nada 3 |
| `perbaiki_majemuk.py` | 7 kata: 犹太节日 *jié*, 看得见 dan 懒得 *de* netral, 延误 *yán wù*, 欧洲, 奥运会, 闺女 |

Temuan penting untuk sesi berikutnya:
- Penyebab masalah bacaan: untuk kata berbacaan ganda, data awal memakai **bacaan/arti CC-CEDICT yang jarang**. Kini 10.144 kata majemuk diperiksa: 10.034 cocok CC-CEDICT, 110 tidak ada di CC-CEDICT (diperiksa manual), tanpa suku kata mustahil; pinyin tampil, pinyin angka, dan zhuyin kini selaras untuk semua kata berangka valid.
- Kolom `pinyin_numeric` dipakai **permainan nada Flashcard** (urutan nada diambil dari angkanya) dan **pencarian Kamus**; jangan merusaknya.
- Generator bawaan ada di `skrip/dari_py/` (`generate_tone_drills.py`, `generate_wordbuilder_pools.py`). `tone_drills.json` sudah tertinggal dari `app_words.json` sejak sebelum sesi ini (±36 grup dan ±239 butir berbeda dari keluaran generator). **Jangan meregenerasi `wb_pools.json`**: daftarnya dikurasi manual.
- Berkas turunan yang membawa bacaan kata: `tone_drills`, `wb_pools`, `nuance_pairs`, `graded_readers`, `produktif_karakter` (mengikuti `app_words.json`).
- Ada 257 kata tanpa pinyin angka (kata seru dan frasa lisan) dan 333 berangka huruf kapital (nama/marga); keduanya sengaja dibiarkan.

## 4. Berkas baru di repo (ringkas)

`kamus/kamus-afiks.js`; `data/afiks_kamus.json`; `data/grammar_afiks.json`; `data/pelajaran/pilar_12.json`; `data/pelajaran/arsip/pilar_3_salinan_pilar5.json`;
skrip di akar repo: `pasang_afiks_kamus.py`, `pasang_afiks_tatabahasa.py`, `pasang_pilar12.py`, `bersihkan_sitasi.py`, `arsipkan_pilar3.py`, `terapkan_koreksi_bacaan.py`, `perbaiki_frasa.py`, `perbaiki_majemuk.py`;
folder kerja GPT `kerja_gpt_afiks/` (laporan Tahap 0–3, `hasil/`). Berkas yang berubah: `kamus.html` (item sidebar + satu baris script), `tatabahasa.html`, `peta-bahasa.html`.
Berkas cadangan `.bak_*` di `data/` **tidak** untuk diunggah dan kini cukup banyak (lihat butir (e)).

## 5. Rencana ke depan (urutan, sudah disetujui)

1. **Butir (d) varian radikal** (opsi B, lihat v42 bagian 4): 20 dari 186 entri Per Radikal (氵 扌 艹 钅 亻 纟 dst.) tetap terpisah, diberi keterangan "bentuk varian dari <induk>", tautan dua arah, ditaruh berdekatan induknya; ⺀ ⺳ 阝 dibiarkan dengan keterangan singkat. Diskusi dulu soal daftar 20 entri dan induknya.
2. **Butir (e) skrip beres-beres cadangan** (opsi A, lihat v42 bagian 5): daftar dulu; cadangan lama (batas **2 hari**) dipindah ke folder arsip, **tidak dihapus**; رسلان sendiri menghapus arsip kelak.
   Jenis cadangan yang kini ada: checkpoint, `.bak_before_apply_*`, serta `.bak_afiks_*`, `.bak_sitasi_*`, `.bak_bacaan_*`, `.bak_frasa_*`, `.bak_majemuk_*` (di `data/` dan akar proyek).
3. **Perbaikan kecil yang disetujui**: `nuance_pairs.json` 闺女 `example_pinyin` "Guīniū huílái le!" → "Guīnü huílái le!"; kumpulkan temuan serupa sebelum membuat skrip.
4. **Belum diputuskan** (angkat bila perlu): 10 kata berakhiran 儿 dengan penulisan `r5` (zhuyin benar); penyegaran `tone_drills.json` lewat generator; 圣诞 berhuruf kapital (4 kata); 焦糖玛奇果 kemungkinan salah ketik (玛奇朵?);
   pelajaran Pilar 3 (量词) yang sebenarnya (lewat GPT dengan pesan serah terima); Tingkat 3 awalan/akhiran; latihan awalan/akhiran (Flashcard, Word Builder, Ujian HSK); filter posisi di menu Per Radikal/Per Komponen.
5. Backlog aktif lama tidak berubah (lihat v41/v42 dan catatan proyek): pasangan penggolong + rantai kata kerja, 多音字, dikte, dashboard gabungan, dan seterusnya.

## 6. Cara membuka aplikasi dan cara kerja repo

Tidak berubah dari v42 bagian 8. Ringkas: aplikasi dibuka lewat server lokal (Live Server) dari `C:\mandarin_app`; Claude membaca repo
https://github.com/RuslanAlimuddin/mandarin_app (folder `blueprint/` untuk BLUEPRINT terbaru); hasil skrip/berkas baru diberikan lewat percakapan dan رسلان yang mengunggahnya.

## Ringkasan status proyek

- Paket Pembentukan Kata (Kamus, Tata Bahasa, Pilar 12, rincian kata, pencarian): **selesai, terpasang, teruji**.
- Pembersihan data (sitasi, Pilar 3, bacaan 140 kata, 44 frasa, 7 kata majemuk): **selesai dan terunggah**.
- Berikutnya: (d) varian radikal → (e) beres-beres cadangan → perbaikan kecil 闺女 → butir "belum diputuskan" sesuai minat.

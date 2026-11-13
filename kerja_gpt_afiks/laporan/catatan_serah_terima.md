# Catatan Serah Terima — Pembentukan Kata (构词法)

Tanggal: 13 November 2026

## Status Tahap 2
- Selesai seluruh kelompok A–J.
- Hasil akhir: 60 poin AFX.01–AFX.60, 120 kalimat contoh, 10 kelompok.
- Berkas akhir: kerja_gpt_afiks/hasil/grammar_afiks.json.
- Laporan akhir: kerja_gpt_afiks/laporan/tahap2_tatabahasa.md.

## Skema
Mengikuti struktur grammar_hsk3.json dan grammar_hsk4.json: level, categories, kesalahan_umum, metadata; kategori name/points; poin id/number/title/fungsi/table; baris tabel jenis/pola/contoh/pinyin/terjemahan. Kolom tambahan dicatat dalam laporan Tahap 2.

## Keraguan dan pemeriksaan
- JSON valid; urutan AFX.01–AFX.60 benar; setiap poin memiliki tepat 2 kalimat.
- Kata/token kalimat yang tidak ada di app_words.json: tidak ada.
- Poin bertanda perlu dicek: tidak ada.
- Pendalaman: AFX.40 们 → HSK 1 poin 57; AFX.41 子 → HSK 3 poin 16.3; AFX.45 第 → HSK 1 poin 56.
- Kelompok yang belum selesai: tidak ada.

## Perintah yang ditunggu
Menunggu perintah LANJUT dari Ruslan.


## Status Tahap 3 — penyimpanan sementara (bagian 1–3)
- Selesai: bagian 1 (pengertian awalan/akhiran dan perbandingan dengan imbuhan Indonesia), bagian 2 (cara membaca kartu entri), bagian 3 (karakter bermakna ganda: 家、生、长、率、手、点、化、头).
- Belum selesai: bagian 4 (perbandingan akhiran pelaku), bagian 5 (awalan penolak), bagian 6 (peta cepat 60 entri dan rencana lanjutan).
- Berkas sementara: `kerja_gpt_afiks/hasil/pilar_12.json` — baru memuat tiga bagian pertama dan akan dilengkapi, bukan hasil final.
- Skema yang ditiru: persis struktur tingkat atas `pilar`, `judul`, `ringkasan`, `bagian`; setiap bagian berisi `judul` dan `isi`; blok isi memakai `tipe` dan pasangan kolom sesuai tipe, yaitu `paragraf/teks`, `poin/daftar`, `tabel/kolom/baris`, `contoh/daftar`, dan `peringatan/teks`. Acuan yang dibaca: `data/pelajaran/pilar_4.json` dan `data/pelajaran/pilar_9.json`.
- Keraguan sementara: contoh tambahan dalam Pilar 12 perlu pemeriksaan manusia atas ketepatan pinyin, kewajaran kalimat, dan keberadaan semua kata di `data/app_words.json`; berkas kamus utama terlalu besar untuk diambil utuh melalui pembacaan repo pada sesi ini.
- Perintah yang ditunggu: belum ada; lanjutkan bagian 4–6 dalam pekerjaan ini, lalu susun laporan Tahap 3 final.

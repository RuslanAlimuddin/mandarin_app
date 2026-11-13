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



## Status Tahap 3 — selesai
- Selesai: seluruh bagian 1–6 Pilar 12.
- Berkas final: `kerja_gpt_afiks/hasil/pilar_12.json`.
- Laporan final: `kerja_gpt_afiks/laporan/tahap3_pilar12.md`.
- Skema meniru `data/pelajaran/pilar_4.json` dan `data/pelajaran/pilar_9.json`: tingkat atas `pilar/judul/ringkasan/bagian`, bagian `judul/isi`, dan blok paragraf, poin, tabel, contoh, peringatan.
- Pemeriksaan dasar: JSON valid, 6 bagian, 10 kelompok A–J, 60 entri (43 akhiran + 17 awalan), tidak ada `[citation:n]` dan tidak ada `准妈妈`.
- Hal yang perlu diperiksa manusia: klasifikasi 非常 di kelompok 非; nuansa 作者/作家; bacaan 长 dan 率; pembatasan fungsi 化 dan 头; pembedaan tujuh akhiran pelaku; pinyin dan kewajaran contoh tambahan; keberadaan semua kata tambahan di app_words.json.
- Kelompok/bagian belum selesai: tidak ada.
- Perintah yang ditunggu: menunggu pemeriksaan Ruslan/Claude dan perintah berikutnya.

# Laporan Tahap 2 — Tata Bahasa Pembentukan Kata (构词法)

Tanggal: 13 November 2026  
Repositori: RuslanAlimuddin/mandarin_app  
Ruang kerja: kerja_gpt_afiks/

## 1. Hasil yang dibuat
- grammar_afiks.json: **60 poin** AFX.01–AFX.60 dalam 10 kelompok A–J.
- Setiap poin memiliki penjelasan, 2 kalimat contoh Mandarin, pinyin bernada, terjemahan Indonesia, tingkat HSK terendah, dan hubungan ke entri Kamus melalui kamus_id (AFK-001 sampai AFK-060).
- Total kalimat contoh: **120**.
- Pendalaman: AFX.40 们 merujuk HSK 1 poin 57; AFX.41 子 merujuk HSK 3 poin 16.3; AFX.45 第 merujuk HSK 1 poin 56. Poin lama tidak diubah.

## 2. Skema yang ditiru
Sebelum menyusun data, saya membaca data/grammar_hsk3.json dan data/grammar_hsk4.json. Skema yang ditiru persis untuk struktur utama:
- Tingkat utama: level, categories, kesalahan_umum, metadata.
- Kategori: name, points.
- Poin: id, number, title, fungsi, table.
- Baris tabel: jenis, pola, contoh, pinyin, terjemahan.

Kolom tambahan pada setiap poin baru untuk kebutuhan proyek: tingkat_hsk_terendah, sumber_tingkat_hsk, kamus_id, dan kamus_nama. Tiga poin pendalaman juga memiliki pendalaman dan rujukan_lama. Nilai tingkat HSK diambil dari kolom **hsk** pada data/app_words.json; pinyin setiap token kata diambil dari kolom **pinyin** pada berkas yang sama.

## 3. Pemeriksaan yang dijalankan
| Pemeriksaan | Hasil |
|---|---:|
| JSON berhasil diparse ulang | Ya |
| Jumlah poin | 60 |
| Urutan ID AFX.01–AFX.60 | Lulus |
| Kalimat contoh | 120 |
| Dua kalimat per poin | Lulus |
| Kata/token kalimat yang tidak ada di app_words.json | 0 |
| Token pinyin yang perlu dicek | 0 |
| Poin tanpa kata contoh utama | 0 |
| Pemakaian 准妈妈 | Tidak ada |
| Sisa [citation:n] | Tidak ada |

## 4. Daftar kata yang tidak ada dan poin perlu dicek
- Kata/token kalimat yang tidak ditemukan di kolom simplified app_words.json: Tidak ada.
- Poin bertanda “⚠️ perlu dicek”: Tidak ada.
- Poin yang kalimatnya tidak memuat kata contoh utama: Tidak ada.

## 5. Berkas yang dibuat atau diperbarui
- kerja_gpt_afiks/hasil/grammar_afiks.json (baru; sementara sebelumnya sudah disimpan per kelompok A–C dan D–F, kini dilengkapi menjadi 60 poin).
- kerja_gpt_afiks/laporan/tahap2_tatabahasa.md (baru).
- kerja_gpt_afiks/laporan/catatan_serah_terima.md (diperbarui sebagai catatan penyelesaian).

Tidak ada berkas asli di luar kerja_gpt_afiks/ yang diubah. Tidak ada kode HTML, JavaScript, atau CSS yang dibuat atau diubah.

Menunggu perintah LANJUT dari Ruslan.

# Laporan Perbaikan Tahap 2 — Tata Bahasa Pembentukan Kata

Tanggal: 13 November 2026

## Perubahan
- AFX.01 dan AFX.02: terjemahan dibedakan. 作者 dijelaskan sebagai penulis suatu karya; 作家 sebagai penulis/sastrawan profesional.
- AFX.17: pinyin kalimat 每个人都有优点 diperbaiki menjadi `Měi gè rén dōu yǒu yōu diǎn.`
- AFX.20: kalimat 人类有很多种类 diganti dengan kalimat yang lebih wajar: 人类需要不同种类的食物。
- AFX.32: kalimat ambigu 研究所在北京 diganti menjadi 这家研究所很有名。
- AFX.39: pinyin 学费不便宜 diperbaiki menjadi `Xué fèi bù pián yi.`
- Huruf pertama pinyin pada seluruh 120 kalimat diubah menjadi huruf besar, mengikuti gaya grammar_hsk3.json.
- Daftar 60 poin dan dua kalimat per poin tetap dipertahankan.

## Temuan data yang dilaporkan
- Pada data/app_words.json, 个 tercatat dengan pinyin `gě`, padahal pada kalimat AFX.17 harus dibaca `gè`.
- Pada data/app_words.json, 便宜 tercatat `biàn yí`, padahal pada kalimat AFX.39 harus dibaca `pián yi`.
- Kedua nilai sumber tidak diubah karena berada di luar folder kerja.
- Pemeriksaan seluruh 120 kalimat juga menemukan 13 pemakaian `gě` yang keliru untuk 个 (misalnya 这个, 两个, 一个); semuanya diperbaiki menjadi `gè`. Bentuk `gěi` pada 给 dalam AFX.03 tetap dipertahankan karena memang benar.
- Selain dua masalah sumber yang telah disebut dan pemakaian 个, tidak ditemukan bacaan lain yang jelas salah pada kalimat yang diperiksa.

## Pemeriksaan ulang
- JSON Kamus dan Tata Bahasa berhasil diparse.
- Entri Kamus: 60.
- Poin Tata Bahasa: 60 (AFX.01–AFX.60).
- Kalimat contoh: 120; tepat 2 per poin.
- Pinyin: seluruh 120 baris diawali huruf besar.
- AFX.17 dan AFX.39 memuat bacaan kontekstual yang benar.
- AFX.20 dan AFX.32 telah diganti tanpa mengubah jumlah kalimat.
- Kata contoh dan daftar “bukan” pada Kamus tidak diubah; daftar contoh utama tetap sama.
- ⚠️ Validasi ulang menyeluruh terhadap app_words.json perlu mengandalkan skrip lokal Claude karena berkas sumber terlalu besar untuk ditampilkan utuh melalui pembacaan repositori pada sesi ini.

## Berkas
- `kerja_gpt_afiks/hasil/afiks_kamus.json` (diperbarui: catatan 场 dan uraian 儿).
- `kerja_gpt_afiks/hasil/grammar_afiks.json` (diperbarui: pinyin, terjemahan, dan kalimat).
- `kerja_gpt_afiks/laporan/tahap2_perbaikan.md` (baru).

Menunggu perintah LANJUT dari Ruslan.

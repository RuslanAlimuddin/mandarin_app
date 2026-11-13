# Skema `afiks_kamus.json`

Berkas ini menjelaskan struktur data Kamus untuk 60 entri awalan dan akhiran. Setiap objek dalam berkas JSON mewakili satu entri. Contoh kata tidak menyimpan tingkat HSK karena aplikasi mengambil informasi itu langsung dari `app_words.json`.

| Kolom | Jenis | Keterangan |
|---|---|---|
| `id` | teks | Kode unik entri, misalnya `AFK-001`. |
| `karakter` | teks | Karakter atau bentuk imbuhan yang dibahas. `主义` dipertahankan sebagai satu entri sesuai keputusan proyek. |
| `pinyin` | teks | Cara baca karakter/bentuk imbuhan dengan tanda nada. Nada netral ditulis tanpa tanda nada, misalnya `men` dan `zi`. Untuk karakter yang tidak mempunyai entri mandiri di kamus, bacaan diambil dari kata contoh yang tersedia. |
| `kelompok` | teks | Kode kelompok A sampai J sesuai daftar yang disetujui. |
| `kelompok_nama` | teks | Nama kelompok dalam Bahasa Indonesia. |
| `posisi` | teks | Fungsi utama entri: `akhiran` atau `awalan`. Nilai `keduanya` hanya dipakai bila satu bentuk benar-benar berfungsi sebagai awalan dan akhiran. |
| `arti_dasar` | teks | Ringkasan makna utama imbuhan dalam Bahasa Indonesia sederhana. |
| `bagian` | daftar objek | Rincian fungsi berdasarkan posisi. Setiap objek memiliki `sebagai`, `fungsi`, `arti`, dan `contoh`. |
| `bagian[].sebagai` | teks | Posisi yang dijelaskan, yaitu `awalan` atau `akhiran`. |
| `bagian[].fungsi` | teks | Penjelasan singkat tentang cara imbuhan membentuk atau mengubah makna kata. |
| `bagian[].arti` | teks | Makna yang dibawa imbuhan pada posisi tersebut. |
| `bagian[].contoh` | daftar objek | Kata-kata contoh yang telah disetujui. |
| `bagian[].contoh[].kata` | teks | Bentuk Hanzi yang harus cocok persis dengan kolom `simplified` di `app_words.json`. |
| `bukan` | daftar objek | Kata yang tampak mirip tetapi tidak memakai imbuhan dengan fungsi yang sedang dibahas. Boleh kosong. |
| `bukan[].kata` | teks | Bentuk Hanzi yang perlu dibedakan. |
| `bukan[].alasan` | teks | Satu kalimat yang menjelaskan mengapa kata tersebut bukan contoh fungsi imbuhan ini. |
| `catatan` | teks | Keterangan tambahan, batas pemakaian, bacaan khusus, tautan ke poin Tata Bahasa lama, atau peringatan yang perlu diperhatikan. |

## Aturan pemakaian

1. Satu entri berisi satu bentuk dari daftar 60 yang telah disetujui; jangan menambahkan `小`, `边`, atau `副`.
2. Setiap entri mempunyai satu objek `bagian` untuk posisi yang sudah dipastikan. Posisi karakter di awal/akhir kata saja tidak cukup untuk menyebutnya imbuhan.
3. Semua `bagian[].contoh[].kata` dan `bukan[].kata` harus ditemukan persis pada `app_words.json`.
4. Jangan menambahkan kolom HSK ke contoh. Tingkat HSK dibaca aplikasi dari kamus utama.
5. Jangan menafsirkan `准` sebagai 'calon'; `准妈妈` tidak digunakan sebagai kata contoh.
6. Poin Tata Bahasa yang sudah ada tidak diubah. Catatan rujukan lama: `第` → HSK 1 poin 56; `们` → HSK 1 poin 57; `子` → HSK 3 poin 16.3.

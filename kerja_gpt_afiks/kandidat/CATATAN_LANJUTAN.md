# Catatan lanjutan -- kandidat "bukan" imbuhan

Dibuat otomatis oleh buat_kandidat_imbuhan.py (23 November 2026).

## Keadaan
- Tahap 1 = 735 kata kandidat (20 pertama per imbuhan, diutamakan HSK rendah) + kata kontrol.
- Tahap 2 = semua kandidat yang BELUM dinilai (433 kata per 25 November 2026). **DITUNDA sampai ada waktu yang
  tepat** (keputusan رسلان, supaya tidak hilang).
  Jalankan nanti:  python buat_kandidat_imbuhan.py --tahap 2   (lalu  --apply)
  Tahap 2 memakai daftar yang sudah dinilai di tahap1\_manifest_tahap1.json (JANGAN dihapus), bukan urutan,
  sehingga aman walau afiks_kamus.json sudah bertambah (102 kata "bukan" dipasang 25 November 2026).
- Tahap 1 sudah selesai: 17 hasil GPT dikurasi (102 kata "bukan" baru dipasang). Jangan jalankan ulang --tahap 1
  (kandidatnya sekarang berbeda dari yang pernah dinilai).

## Cara kerja
1. Tempel satu berkas batch_NN.txt ke AI (GPT) per percakapan baru. Simpan jawabannya (satu blok JSON)
   sebagai batch_NN_hasil.json.
2. Unggah hasilnya ke repo (folder yang sama), lalu minta Claude mengurasinya (Claude membaca langsung dari repo).
   Hanya golongan "bukan" yang diambil; "imbuhan" dan "ragu"
   dipakai untuk memeriksa ketelitian AI (lewat kata kontrol di _manifest_tahapN.json).
3. Setelah kurasi, skrip pemasang menambahkan hasil "bukan" yang disetujui ke data\afiks_kamus.json.

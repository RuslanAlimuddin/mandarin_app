# Catatan lanjutan -- kandidat "bukan" imbuhan

Dibuat otomatis oleh buat_kandidat_imbuhan.py (23 November 2026).

## Keadaan
- Tahap 1 = 735 kata kandidat (20 pertama per imbuhan, diutamakan HSK rendah) + kata kontrol.
- Tahap 2 = SISA 433 kandidat. **DITUNDA sampai ada waktu yang tepat** (keputusan رسلان, supaya tidak hilang).
  Jalankan nanti:  python buat_kandidat_imbuhan.py --tahap 2   (lalu  --apply)
  Pembagian tetap, jadi tahap 2 tidak mengulang tahap 1 selama data tidak berubah. Bila afiks_kamus.json
  atau app_words.json sudah berubah, jalankan lihat-dulu dan bandingkan jumlahnya.

## Cara kerja
1. Tempel satu berkas batch_NN.txt ke AI (GPT) per percakapan baru. Simpan jawabannya (satu blok JSON)
   sebagai batch_NN_hasil.json.
2. Tempel hasilnya ke Claude untuk dikurasi. Hanya golongan "bukan" yang diambil; "imbuhan" dan "ragu"
   dipakai untuk memeriksa ketelitian AI (lewat kata kontrol di _manifest_tahapN.json).
3. Setelah kurasi, skrip pemasang menambahkan hasil "bukan" yang disetujui ke data\afiks_kamus.json.

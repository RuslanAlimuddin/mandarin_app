# BLUEPRINT v33 — Mandarin Interaktif

Lanjutan dari BLUEPRINT v32. Sesi ini review manual 9 cycle Tier B lagi
(~900 kata, mulai dari 果园/纪念馆 sampai 干部/半岛/蜡/蜜月), plus temuan pola
kualitas baru dan diskusi strategi ke depan dgn رسلان.

---

## E.0.2b Tier B — Review manual 9 cycle sesi ini

Pola kerja sama seperti v32: رسلان jalankan `--dry-run` lokal → Claude scan
`note_id` tiap cycle utk indikasi hipernim/hiponim/wrong-sense/padding →
رسلان apply → generate cycle berikutnya.

**Fill-rate & flag-rate per cycle** (flag-rate = perkiraan % relasi
bermasalah dari scan manual):
| Cycle (kata pertama) | Fill-rate | Flag-rate kasar | Catatan |
|---|---|---|---|
| 果园/纪念馆... | 82/100 | ~9/100 | bersih |
| 秃/透支... | 90/100 | ~13/100 | wajar |
| (regenerasi cycle di atas via prompt v3_1) | 73/100 | ~4/100 | **bukti regenerate efektif** |
| 十字路口/炎症... | 95/100 | ~69/100 | tinggi |
| 书记/喷泉... | 68/100 | ~37/100 | sedang |
| 腺/脾... | 79/100 | ~9/100 | bersih |
| 温室/牧场... | 77/100 | ~46/100 | tinggi, +3 kata suspicious-invented |
| 二氧化碳/运河... | 89/100 | **82/100** | **tertinggi, banyak padding** |
| 干部/半岛... | 88/100 | **75/100** | **tinggi lagi, padding lanjut** |

### Temuan pola baru sesi ini:

**1. Pola "padding self+afiks"** — AI menambahkan prefiks/sufiks ke kata
utama itu sendiri sbg "sinonim" (mis. `庄园→庄园住宅`, `双向→双向的`,
`过关→过关成功`), sering disertai note_id yg **mengaku sendiri** itu "bukan
pengganti baku/umum/standar". Muncul jelas di 2 cycle terakhir sesi ini
(17 pasangan terkumpul di kategori baru `suspicious_padding`). Beda dari
hipernim biasa — ini AI gagal ikuti instruksi "lebih baik kosong daripada
dipaksakan" di prompt.

**2. Heuristik murah utk deteksi pola #1**: kalau kata "sinonim" yg
diusulkan mengandung kata utama sbg substring persis, hampir selalu bukan
sinonim asli. Fungsi referensi `is_suspicious_padding()` sudah ditulis di
`bersihkan_relasi_janggal_batch5.py` (tidak dipanggil otomatis di situ,
disediakan utk رسلان copy ke skrip generate/apply kalau mau deteksi
otomatis tanpa nunggu review Claude).

**3. Bukti empiris regenerate efektif**: 1 cycle dgn flag-rate ~69/100
di-generate ulang persis (kata sama, prompt sama) dan hasilnya turun ke
~4/100. رسلان & Claude sepakat: regenerate-saat-flag-rate-tinggi masuk
jadi kebijakan standar mulai sekarang, bukan cuma solusi darurat.

**4. Observasi 2 cycle terakhir**: flag-rate 82/100 lalu 75/100 beruntun
— kemungkinan penurunan kualitas berkepanjangan (bukan cuma fluktuasi
acak), tapi belum dikonfirmasi krn سesi ditutup di titik ini. **Perlu
dicek di awal sesi berikutnya**: apakah pola tinggi ini berlanjut di
cycle² selanjutnya atau mereda sendiri.

### Rencana yg disepakati رسلان & Claude:
- Regenerate cycle kalau flag-rate tinggi (bukan cuma di kasus darurat) —
  jadi kebijakan default mulai sekarang.
- رسلان masih berencana coba banding Claude sbg generator alternatif vs
  ChatGPT (belum dieksekusi — tercatat sejak v32, masih relevan).
- Pertimbangkan tambah heuristik `is_suspicious_padding()` ke pipeline
  lokal رسلان biar deteksi pola padding otomatis tanpa nunggu review Claude.

### File-file baru sesi ini (di `/mnt/user-data/outputs/`, رسلان perlu
pindahkan ke `C:\mandarin_app\`):

1. **`flagged_relations_batch5.json`** — 89 pasangan `high_confidence` +
   17 pasangan `suspicious_padding` (kategori baru) + 23 pasangan
   `borderline_review_needed`. Terkumpul dari scan manual 9 cycle sesi ini.
2. **`bersihkan_relasi_janggal_batch5.py`** — extend dari batch4, path
   `app_words.json` sudah benar (`data/app_words.json`, ikut fix sesi
   sebelumnya). 3 tingkat opt-in: `high_confidence` (default),
   `--include-padding`, `--include-borderline`. Berisi juga fungsi
   referensi `is_suspicious_padding()` (tidak dipanggil otomatis, lihat
   docstring di file). **Belum pernah dites thd `app_words.json`
   sebenarnya** — jalankan dry-run dulu.

### Yang perlu dicek di awal sesi berikutnya:
1. Jalankan `bersihkan_relasi_janggal_batch5.py` dry-run → cek semua
   pasangan `high_confidence` ketemu → `--apply`.
2. Review manual 17 pasangan `suspicious_padding` — kategori baru,
   belum divalidasi lintas-sesi, disarankan رسلان cek sendiri dulu
   sebelum `--include-padding`.
3. Review 23 pasangan `borderline_review_needed` (opsional).
4. `flagged_relations_batch4.json` + `bersihkan_relasi_janggal_batch4.py`
   dari sesi v32 — **belum dikonfirmasi statusnya, cek apakah sudah
   dijalankan/di-apply.**
5. Pantau apakah pola flag-rate tinggi beruntun (82→75) berlanjut di
   cycle berikutnya — kalau ya, prioritaskan regenerate/ganti approach
   sesuai kesepakatan di atas.
6. Lanjutkan cycle generate→AI→dry-run→(Claude review)→apply seperti
   biasa, dgn kebijakan regenerate-saat-flag-tinggi yg baru disepakati.

---

## Ringkasan status keseluruhan proyek

- ✅ D.4, confusion_groups.json, insiden batch3 v1 — selesai (v30-v31)
- 🔄 E.0.2b Tier B — aktif berjalan, sesi v32+v33 gabungan proses ~1.800
  kata lagi, total 221 pasangan high_confidence + 17 padding + 48
  borderline terkumpul lintas 2 sesi (batch4 + batch5), belum semua
  dieksekusi cleanup-nya. Proses jangka panjang, blm akan "selesai".
- Backlog aktif lain (lihat memori proyek): productive suffixes/prefixes,
  measure word pairing, dictation game, dll — belum disentuh sesi ini

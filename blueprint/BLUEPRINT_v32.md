# BLUEPRINT v32 — Mandarin Interaktif

Lanjutan dari BLUEPRINT v31. Sesi ini fokus pada review manual pipeline
E.0.2b Tier B prompt v3.1 (pilot) + 8 cycle reguler berikutnya, dan
menyiapkan pembersihan data untuk sesi selanjutnya.

---

## E.0.2b Tier B — Review manual 1 pilot + 8 cycle (~900 kata)

Sesi ini TIDAK menjalankan `apply_hasil_sinonim_antonim.py --apply` sendiri
— رسلان yang menjalankan tiap `--dry-run` lokal lalu Claude mereview isi
`hasil_tier_b_pilot.json` per cycle sebelum رسلان lanjut ke `--apply`.
Pola: dry-run → Claude scan note_id untuk indikasi hipernim/hiponim/wrong-
sense → رسلان apply → generate cycle berikutnya.

**Hasil per cycle** (fill-rate = kata yg dpt ≥1 relasi dari 100):
| Cycle | Fill-rate | Kata baru masuk exclude permanen |
|---|---|---|
| Pilot | 99/100 | - |
| 2 | 96/100 | - |
| 3 | 93/100 | 熊 |
| 4 | 94/100 | 领事, 牡丹 |
| 5 | 91/100 | 热气球, 五星级 |
| 6 | 90/100 | 燕子, 地下水 |
| 7 | 76/100 | 惯性, 菩萨, 太极 |
| 8 | 72/100 | 灯笼, 墓碑, 椰子, 口罩 |
| 9 | 95/100 | 贝壳, 俄语 |
| 10 (terakhir sesi ini) | belum di-apply — cycle terakhir yg direview: rate flag 61/100 (tinggi), kata: 后遗症, 定金, 家禽, 沼泽, dll |

**Observasi kualitas:** rate hipernim/hiponim ("flag rate" per 100 kata)
berfluktuasi tajam antar cycle (cth. cycle 6 dan cycle terakhir sesi ini
~60 flag/100, cycle 7-8 cuma 2-11 flag/100) — pola konsisten dgn catatan
v30/v31 bahwa kualitas **sangat bergantung pada AI eksternal yg dipakai**,
bukan cuma prompt. رسلان saat ini selalu pakai ChatGPT untuk generate
Tier B. Claude menyarankan رسلان coba banding dgn Claude (Opus 5, mode
reasoning) sbg AI generator alternatif utk 1 batch percobaan, lalu
bandingkan flag rate-nya dgn cara yg sama (scan note_id) sblm memutuskan
ganti generator reguler — **belum dicoba, masih rencana**.

### File-file baru sesi ini (di `/mnt/user-data/outputs/` sesi ini, رسلان perlu
pindahkan ke `C:\mandarin_app\`):

1. **`flagged_relations_batch4.json`** — 132 pasangan relasi confidence
   tinggi (hipernim/hiponim jelas atau self-admitted beda makna oleh AI
   sendiri di note_id) + 25 pasangan borderline (confidence rendah, perlu
   review manual رسلان sebelum dihapus). Terkumpul dari scan manual Claude
   sepanjang 9 batch (pilot + 8 cycle) sesi ini.
2. **`bersihkan_relasi_janggal_batch4.py`** — skrip pembersih baru,
   mengikuti desain aman batch3 v2 (HANYA exact-match pasangan eksplisit
   dari `flagged_relations_batch4.json`, TIDAK ADA pattern-matching/regex).
   Default dry-run, default hanya proses daftar `high_confidence` (bukan
   borderline). Pakai `--apply` utk eksekusi, `--include-borderline` utk
   ikut proses daftar borderline. Memanggil `checkpoint.py` otomatis
   sebelum `--apply` kalau modul itu ada di folder yg sama — **skrip ini
   belum pernah dites terhadap `app_words.json` yg sebenarnya**, cek dulu
   dry-run-nya sebelum `--apply`.

### Yang perlu dicek di awal sesi berikutnya:
1. Jalankan `bersihkan_relasi_janggal_batch4.py` (dry-run dulu) — cek
   apakah semua 132 pasangan `high_confidence` ketemu di `app_words.json`
   (harusnya ya, karena semua sudah ter-apply lewat
   `apply_hasil_sinonim_antonim.py` sepanjang sesi ini). Kalau hasil dry-
   run masuk akal, lanjut `--apply`.
2. Review 25 pasangan `borderline_review_needed` manual — putuskan mau
   dihapus jg (`--include-borderline`) atau dibiarkan.
3. Cycle Tier B ke-10 (terakhir sesi ini) — رسلان sudah dapat dry-run
   dgn flag rate tinggi (~61/100) tapi **belum di-apply**. Kalau mau
   dilanjut, apply dulu baru generate cycle 11.
4. Kalau رسلان sempat coba banding Claude vs ChatGPT sbg generator Tier B,
   laporkan hasil flag-rate perbandingannya di awal sesi berikutnya.
5. Lanjutkan siklus generate→AI→dry-run→(Claude review)→apply seperti
   biasa. Pool Tier B masih besar (~5.900 dari estimasi terakhir BLUEPRINT
   v30, sesi ini baru proses ~900 kata lagi).

---

## Ringkasan status keseluruhan proyek

- ✅ D.4 (Karakter Mirik render bug) — selesai (v30)
- ✅ confusion_groups.json 53→71 grup — selesai (v30)
- ✅ Insiden bug batch3 v1 (hapus 1.800 relasi salah) — diperbaiki jadi v2,
  187 relasi dibersihkan (v31)
- 🔄 E.0.2b Tier B — aktif berjalan, sesi ini proses ~900 kata lagi (1
  pilot + 8 cycle), 132+25 pasangan baru terflag utk batch4 cleanup
  (belum dieksekusi, skrip & data siap di outputs). Proses jangka panjang,
  belum akan "selesai" dlm sesi manapun.
- Backlog aktif lain (lihat memori proyek): productive suffixes/prefixes,
  measure word pairing, dictation game, dll — belum disentuh sesi ini

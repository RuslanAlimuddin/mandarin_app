# BLUEPRINT v34 — Mandarin Interaktif

Lanjutan dari BLUEPRINT v33. Sesi ini: (1) bikin & uji coba tool baru
`cek_dan_bersihkan_hasil_tier_b.py` sbg penyaring awal sebelum review
manual Claude, (2) review 6 cycle Tier B lagi (~600 kata) pakai tool itu,
(3) temukan & perbaiki 2 bug di heuristik tool-nya.

---

## Tool baru: `cek_dan_bersihkan_hasil_tier_b.py`

Dibuat sesi ini utk mempercepat proses review manual yg selama ini Claude
lakukan tiap cycle (baca 100 kata mentah satu-satu). Tool ini jalan
LANGSUNG di atas `hasil_tier_b_pilot.json` (SEBELUM apply), pakai 2
heuristik: (1) substring-check "padding" (kata sinonim mengandung kata
utama), (2) keyword-scan "self-admission" di note_id (frasa spt "lebih
luas/spesifik/bukan pengganti baku").

**Alur kerja baru yg disepakati** (6 langkah, sudah jadi kebiasaan mulai
sesi ini):
1. `generate_prompt_sinonim_antonim_v3.py` → dapat prompt
2. Paste ke ChatGPT → simpan `hasil_tier_b_pilot.json`
3. `python cek_dan_bersihkan_hasil_tier_b.py` → laporan PADDING + SELF-ADMISSION
4. Kalau flag-rate tinggi (skrip kasih rekomendasi otomatis) → regenerate dulu
5. Paste laporan (atau upload json) ke Claude → Claude pilah genuine vs false-positive
6. `apply_hasil_sinonim_antonim.py --dry-run` lalu apply beneran

`--strip` (auto-hapus candidat flagged) **belum dipakai** -- heuristiknya
masih terlalu banyak false-positive utk auto-strip tanpa mata manusia,
terutama utk kata utama 1-karakter (lihat di bawah).

### 2 bug ditemukan & diperbaiki di tool ini sesi ini:
1. **Antonim negasi `不/无/无法` false-flagged sbg padding** (mis.
   `均匀→不均匀`, `胜任→无法胜任`) -- padahal itu pola antonim BAKU di
   Mandarin. Sudah diperbaiki (skip check kalau candidate = prefiks negasi
   + kata utama, utk `不/非/无/无法/不能/没有`).
2. **Kata utama 1-karakter bikin heuristik padding jauh lebih tidak
   akurat** -- krn kata majemuk 2-karakter di Mandarin memang lazim dibentuk
   dgn nempel 1 karakter ke kata 1-karakter, jadi PADDING check jadi
   overtriggered (mis. `痰→痰液`, `议→议论`, `裁→裁剪` -- semua false
   positive, kata baku beneran). Sudah ditambah PERINGATAN otomatis di
   output kalau kata utama cuma 1 karakter -- TAPI belum ada fix
   struktural (skrip masih flag, cuma kasih warning). Kalau muncul lagi
   pola serupa, pertimbangkan exclude kata utama 1-karakter dari PADDING
   check sepenuhnya, atau naikkan threshold-nya.

## E.0.2b Tier B — 6 cycle direview sesi ini

| Cycle (kata pertama) | Fill-rate | Kata baru exclude | Catatan |
|---|---|---|---|
| 天桥/四季... | 97/100 | 芭蕾 | flag rendah, semua sudah di-apply |
| 美景/苗... | 92/100 | 海绵 | pola antonim palsu ditemukan (人品→人品差, 士气→士气低落) |
| 雪山/冷战... | 92/100 | 太平 | - |
| 揭示/司令... | 89/100 | 火山, 芝麻, 张扬 | - |
| 筑/痰... | 85/100 | 直径, 金字塔, 天鹅 | **hampir semua PADDING flag = false positive (kata utama 1-karakter)** |
| 化验/阶层... | 93/100 | 电报 | bersih, flag genuine hampir semua |

### Pola baru ditemukan sesi ini:
**Antonim palsu berupa frasa deskriptif** -- AI kadang bikin "antonim" dgn
nempel kata sifat negatif ke kata utama sendiri (`人品→人品差`,
`士气→士气低落`) alih-alih cari kata antonim asli. Beda dari padding
biasa krn ini di kolom antonyms, bukan synonyms. Baru 1 cycle ditemukan,
blm cukup data utk bikin heuristik otomatis -- tetap perlu mata manusia.

### File-file baru sesi ini (di `/mnt/user-data/outputs/`, رسلان perlu
pindahkan ke `C:\mandarin_app\`):

1. **`flagged_relations_batch6.json`** — ~100 pasangan `high_confidence`
   + 14 pasangan `borderline_review_needed` + 6 pasangan
   `suspicious_padding_single_char_caution` (BUKAN utk dihapus -- daftar
   false-positive terkonfirmasi, disimpan sbg referensi/contoh kasus).
2. **`bersihkan_relasi_janggal_batch6.py`** — sama desainnya dgn batch4/5.
   TIDAK memproses kategori `suspicious_padding_single_char_caution` sama
   sekali (defaultnya cuma `high_confidence`, opt-in `--include-borderline`).
3. **`cek_dan_bersihkan_hasil_tier_b.py`** (update) — 2 bug fix di atas
   sudah masuk. رسلان perlu timpa versi lokal dgn ini.

### Yang perlu dicek di awal sesi berikutnya:
1. Jalankan `bersihkan_relasi_janggal_batch6.py` dry-run → cek semua
   pasangan `high_confidence` ketemu → `--apply`.
2. `flagged_relations_batch4.json` (v32) dan `batch5.json` (v33) --
   **masih belum dikonfirmasi statusnya dari sesi-sesi sebelumnya**, cek
   lagi apakah sudah pernah dijalankan.
3. Pantau apakah pola "antonim palsu" (`X→X差`) muncul lagi di cycle
   berikutnya -- kalau sering, bisa ditambah heuristik baru di
   `cek_dan_bersihkan_hasil_tier_b.py` (candidate antonim yg dimulai
   dgn kata utama + diikuti kata sifat pendek).
4. Kalau ketemu lagi kasus kata utama 1-karakter dgn PADDING flag banyak
   false-positive, pertimbangkan exclude 1-karakter dari heuristik itu
   sepenuhnya drpd cuma warning.
5. رسلان masih belum coba Claude sbg generator alternatif Tier B vs
   ChatGPT (tercatat sejak v32, masih pending -- 3 sesi berturut-turut).
6. Lanjutkan cycle generate→AI→cek_dan_bersihkan→(Claude review)→apply,
   pakai 6-langkah yg sudah disepakati di atas.

---

## Ringkasan status keseluruhan proyek

- ✅ D.4, confusion_groups.json, insiden batch3 v1 — selesai (v30-v31)
- 🔄 E.0.2b Tier B — aktif berjalan, sesi v32-v34 gabungan proses ~2.400
  kata lagi. Tooling makin matang (cek_dan_bersihkan_hasil_tier_b.py
  sbg penyaring otomatis). flagged_relations batch4/5/6 terkumpul,
  belum semua dieksekusi cleanup-nya -- perlu dicek statusnya. Proses
  jangka panjang, blm akan "selesai".
- Backlog aktif lain (lihat memori proyek): productive suffixes/prefixes,
  measure word pairing, dictation game, dll — belum disentuh sesi ini

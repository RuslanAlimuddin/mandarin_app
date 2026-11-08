# BLUEPRINT v35 — Mandarin Interaktif

Lanjutan dari BLUEPRINT v34. Sesi ini: (1) menuntaskan seluruh sisa pool
Tier B (E.0.2b) sampai benar-benar habis, (2) menemukan & memperbaiki
beberapa bug tooling, (3) menutup 3 backlog cleanup lama (batch4/5/6)
yang belum pernah dieksekusi sejak v32-v34.

---

## Milestone besar: E.0.2b Tier B TUNTAS

Pool kata Tier B yang sejak v30 terus diproses cycle demi cycle akhirnya
**benar-benar habis** sesi ini. Progres pool per cycle: 100 → 77 → 25 →
9 → **0 kata**. `generate_prompt_sinonim_antonim_v3.py` mengembalikan
array kosong `[]` di cycle terakhir, mengonfirmasi tidak ada kata lagi
yang perlu diproses.

Menjelang akhir, fill-rate menurun tajam (95% → turun ke 44% → 11/25 →
4/9) karena sisa pool didominasi **morfem terikat/makna arkais/dialek**
(mis. 格 hanya bermakna "dipakai dalam 格登", 罗 = "kasa/kain kasa", 素 =
"sutra mentah", 制/业/主义 sbg prefiks/sufiks abstrak) — kategori kata
yang secara alami memang sulit dicarikan sinonim, bukan tanda kualitas
AI menurun.

## Bug yang ditemukan & diperbaiki sesi ini

1. **`verifikasi_hasil_tier_a.py`** — pesan sukses hardcode `"SEMUA 20
   ENTRI LOLOS"` alih-alih pakai `len(hasil)` yang sebenarnya (jadi
   selalu bilang "20" walau isinya 0). Diperbaiki pakai f-string dgn
   `len(hasil)`.
2. **`cek_dan_bersihkan_hasil_tier_b.py`** — header `[SELF-ADMISSION]`
   menghitung SEMUA entri dgn alasan self-admission (termasuk yg juga
   kena PADDING), tapi loop print men-skip entri dobel-flag itu (sudah
   tercetak di seksi PADDING) → angka header selalu > jumlah baris yg
   benar-benar tercetak. Diperbaiki dgn menghitung `admission_only_flags`
   sekali lalu dipakai utk header maupun loop print.
3. **Heuristik PADDING belum cover prefiks negasi `未`** — pola
   `成年→未成年` [antonyms] ke-flag sbg padding padahal itu antonim
   negasi baku (sama kelasnya dgn 不/非/无/无法/不能/没有 yg sudah
   di-whitelist sejak v34). **Belum dipatch** — masuk backlog.
4. **`bersihkan_relasi_janggal_batch4/5/6.py`** — ketiganya crash di
   `checkpoint.save()` dgn `AttributeError: module 'checkpoint' has no
   attribute 'save'`. Sebabnya: `checkpoint.py` didesain sbg CLI
   (`python checkpoint.py save`), bukan modul yg diimpor — tidak ada
   fungsi `save()` di level modul (yg ada `cmd_save(args)` internal).
   Diperbaiki dgn memanggil `checkpoint.py` via `subprocess.run([...])`
   persis spt dipakai dari command line, sehingga snapshot ZIP lengkap
   (semua `*.py` + `data/`, dgn rotasi) tetap terbentuk sebelum menulis
   perubahan. **Ketiga skrip sudah diperbaiki & berhasil dijalankan
   ulang dgn sukses sesi ini** (lihat di bawah).

## Temuan pola baru sesi ini

- **Prompt regenerate ulang batch yg sama kalau belum ada apply
  beneran** — sempat dikira bug ("kata yg sama terus muncul"), ternyata
  perilaku normal: pool kata cuma maju setelah `apply_hasil_sinonim_
  antonim.py` dijalankan TANPA `--dry-run`. Menjalankan generate +
  dry-run berulang tanpa apply beneran akan terus menghasilkan batch
  100 kata yang identik.
- **Regresi bahasa note_id** — satu batch pernah balik 100% dalam bahasa
  Mandarin alih-alih Bahasa Indonesia (melanggar instruksi eksplisit di
  prompt). Solusinya cukup regenerate ulang (bukan masalah di
  prompt/skrip) — hasil regenerate langsung bersih lagi. Kontaminasi
  kecil (1-2 kata Mandarin nyelip di tengah kalimat Indonesia)
  sesekali masih muncul di beberapa batch lain, tapi dampaknya minor.
- **Pola antonim palsu `X→X<sifat negatif>`** (dicatat pertama kali di
  v34: 人品→人品差, 士气→士气低落) — sudah dikonfirmasi & dieksekusi
  cleanup-nya lewat batch6 sesi ini.

## Review Tier B sesi ini — ringkasan

Sekitar 18 cycle direview manual (satu per satu, sampai pool habis).
Kebijakan yang konsisten dipakai sepanjang sesi:
- Akar 1-karakter + kompoun natural = **keep**, KECUALI note eksplisit
  menyebut beda cakupan/sense asli (mis. 蒸→蒸发, 削→削皮, 业→行业/产业).
- Kata dasar + perpanjangan idiom 4-karakter = **exclude** (mis.
  无能→无能为力, 生死→生死存亡).
- Note self-admission ("lebih luas/umum/spesifik") = **exclude**
  (pola hipernim/hiponim).
- Total **134 pasangan unik** dikumpulkan jadi
  `exclude_list_sesi_v35.json` + skrip `bersihkan_relasi_janggal_sesi_
  v35.py` — sudah di-`--apply` sesi ini (258 relasi terhapus dari
  119 kata; 5 pasangan sudah otomatis bersih dari awal krn kata
  terkait tidak pernah tersimpan relasinya).

## Backlog lama (v32-v34) — DITUTUP sesi ini

- ✅ `bersihkan_relasi_janggal_batch4.py --apply` — 140 relasi dihapus,
  124 dilewati (sudah bersih)
- ✅ `bersihkan_relasi_janggal_batch5.py --apply` — 107 relasi dihapus,
  71 dilewati
- ✅ `bersihkan_relasi_janggal_batch6.py --apply` — 122 relasi dihapus
  (dry-run sempat memprediksi 124; selisih 2 krn `错觉↔幻觉` sudah lebih
  dulu terhapus oleh batch5 barusan), 104 dilewati

Semua checkpoint ZIP tersimpan otomatis di `backups/` sebelum tiap
`--apply` (via `checkpoint.py save`, sekarang dipanggil dgn benar lewat
subprocess).

### File-file baru/berubah sesi ini (perlu dipindahkan ke `C:\mandarin_app\`)

1. **`verifikasi_hasil_tier_a.py`** (fix) — pesan sukses pakai count asli
2. **`cek_dan_bersihkan_hasil_tier_b.py`** (fix) — hitung SELF-ADMISSION benar
3. **`bersihkan_relasi_janggal_batch4.py`** (fix) — checkpoint via subprocess
4. **`bersihkan_relasi_janggal_batch5.py`** (fix) — checkpoint via subprocess
5. **`bersihkan_relasi_janggal_batch6.py`** (fix) — checkpoint via subprocess
6. **`exclude_list_sesi_v35.json`** — 134 pasangan hasil review sesi ini
   (sudah di-apply, disimpan sbg arsip/referensi)
7. **`bersihkan_relasi_janggal_sesi_v35.py`** — skrip cleanup-nya
   (sudah dijalankan, disimpan sbg arsip)

## Yang perlu dicek di awal sesi berikutnya

1. **Patch heuristik negasi `未`** di `cek_dan_bersihkan_hasil_tier_b.py`
   — tambahkan ke daftar prefiks negasi yg sudah ada (不/非/无/无法/
   不能/没有), meski Tier B generate sendiri sudah tidak relevan lagi
   krn pool habis, heuristik ini mungkin masih dipakai kalau ada
   pool/putaran baru nanti.
2. **E.0.2b Tier B resmi ditutup** — tidak ada lagi cycle rutin yg perlu
   dijalankan kecuali رسلان memutuskan menambah kata baru ke pool (mis.
   dari HSK band lain atau kosakata baru).
3. **Backlog aktif berikutnya** (dari daftar lama yg belum disentuh):
   productive suffixes/prefixes, measure word pairing, dictation game,
   ekspansi `confusion_groups.json` (sengaja ditunda sampai fase
   synonym/antonym selesai — sekarang sudah saatnya mulai).

---

## Ringkasan status keseluruhan proyek

- ✅ D.4, confusion_groups.json (v1), insiden batch3 v1 — selesai (v30-v31)
- ✅ **E.0.2b Tier B — TUNTAS sesi ini.** Seluruh pool sinonim/antonim
  yg direncanakan sejak v30 sudah diproses & direview manual habis.
  flagged_relations batch4/5/6 (v32-v34) + exclude_list sesi v35 semua
  sudah dieksekusi cleanup-nya.
- 🔜 Backlog aktif berikutnya: productive suffixes/prefixes, measure
  word pairing, dictation game, ekspansi confusion_groups.json (siap
  dimulai kapan saja).

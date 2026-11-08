# BLUEPRINT v31 — Mandarin Interaktif

Lanjutan dari BLUEPRINT v30. Sesi ini murni fokus pada **E.0.2b Tier B**:
menjalankan banyak cycle generate→AI→dry-run→apply, sambil me-review
kualitas tiap batch secara manual (tidak ada pekerjaan lain di sesi ini).

---

## Checklist dari BLUEPRINT v30 — **sudah selesai** (dikonfirmasi رسلان)

1. ✅ `bersihkan_relasi_janggal_batch2.py` — sudah dijalankan + checkpoint disimpan.
2. ✅ Batch Tier B terakhir dari sesi v30 (berisi `肩`, `兔`, `震惊`, `不止`,
   `不许` dll, fill-rate 93/100) — sudah di-apply tanpa `--dry-run`.
3. `bersihkan_relasi_angka.py` — statusnya tidak dicek ulang sesi ini
   (bukan prioritas); kemungkinan masih belum pernah dijalankan sama
   sekali seperti dicatat di v30. **Cek lagi di awal sesi berikutnya.**

## E.0.2b Tier B — ~17 cycle dijalankan sesi ini

- Setiap cycle: generate 100 kata → proses lewat AI eksternal → apply
  (dgn dry-run dulu, lalu tanpa dry-run setelah رسلان review). Fill-rate
  bervariasi 75–99/100 tergantung batch.
- **~1.700 kata tambahan** sudah diproses (approx, 17 cycle × ~100).
  Sisa pool belum dihitung ulang sesi ini — **jalankan
  `hitung_sisa_tier_b.py` di awal sesi berikutnya** untuk angka pasti
  (perkiraan awal v30: ~5.900 tersisa, jadi sisa sekarang mungkin
  sekitar ~4.200, tapi ini kasar, bukan hasil hitung ulang).
- `_tb_empty_streak` mechanism bekerja seperti dirancang — beberapa kata
  baru kena ambang gagal-berulang tiap cycle dan otomatis dikecualikan
  (mis. `挣`, `剪`, `甲`, `馒头`, `法语`, `师长`, `阿拉伯语`, dll — daftar
  lengkap ada di riwayat percakapan kalau perlu ditelusuri, tidak
  dicatat ulang di sini karena sudah otomatis tersimpan di file streak).

### Temuan penting: kualitas relasi AI eksternal bervariasi drastis antar-batch

Sepanjang ~17 cycle, رسلان me-review manual tiap hasil sebelum apply.
Pola yang konsisten muncul: **banyak relasi sinonim yang note_id-nya
SENDIRI mengaku bahwa kata itu lebih luas/lebih sempit/tidak sepenuhnya
sepadan** — persis pelanggaran yang instruksi anti-hipernim di prompt
coba cegah, tapi AI tetap memasukkannya (kadang dengan note jujur
"lebih umum", kadang note dalam bahasa Mandarin "范围更广").

**~150 pasangan kata bermasalah** terkumpul dari review manual sesi ini.
Semua sudah didaftar di `flagged_relations_batch3.json` (dibuat sesi
ini, ada di `/mnt/user-data/outputs/` dari sesi ini — رسلان perlu
salin ke `C:\mandarin_app\`).

Contoh pola yang berulang: `美容→美化`, `传输→传递`, `高档→高级`,
`难点→难题`, `研讨→讨论`, `波折→曲折`, dll — puluhan pasangan dengan
note eksplisit "lebih umum/luas". Juga ditemukan beberapa kasus mismatch
konsep (bukan sekadar hipernim), mis. `凶手→犯罪嫌疑人` (pelaku terbukti
vs tersangka — beda konsep hukum), `上帝→神` (khusus Kristen vs umum),
`占卜→预测` (mistis vs prediksi umum), `水货→走私货` (barang tak resmi vs
barang selundupan).

Beberapa batch di tengah sesi note_id-nya ditulis dalam **bahasa Mandarin**
alih-alih Indonesia seperti seharusnya — kemungkinan AI eksternal yang
dipakai berbeda dan tidak/kurang patuh instruksi bahasa di prompt.
رسلان sempat bilang "AI ini lebih patuh drpd yg lain" soal anti-hipernim
di v30 — temuan sesi ini menunjukkan **kepatuhan itu masih jauh dari
sempurna bahkan pada AI yang lebih baik**, jadi review manual tetap perlu
dilakukan tiap batch, bukan cuma diandalkan ke prompt saja.

### Bug baru: item string polos di synonyms/antonyms (bukan dict)

Ditemukan 2x sesi ini (`apply_hasil_sinonim_antonim.py --dry-run` crash
dgn `AttributeError: 'str' object has no attribute 'get'` di
`strip_self_reference()`):
- 1x: kata `奶牛` — `"synonyms": ["奶牛"]` (self-reference sbg string polos)
- 1x (6 kata sekaligus): `纪实`, `继父`, `成问题`, `功臣` (2x, synonyms
  & antonyms), `海藻` — semua isinya string polos bukan dict standar
  `{"word":..., "pinyin":..., "note_id":...}`.

رسلان sudah memperbaiki manual (kosongkan jadi `[]`) untuk kedua
kejadian ini. **Solusi permanen belum diterapkan ke source asli** —
lihat `PATCH_apply_hasil_sinonim_antonim.md` (dibuat sesi ini) untuk
patch tertarget di fungsi `strip_self_reference()`. Claude tidak
pernah melihat source lengkap file ini (hanya traceback), jadi tidak
membuat versi pengganti utuh — hanya patch minimal + instruksi manual.
**Prioritas tinggi untuk diterapkan di awal sesi berikutnya**, karena
pola ini kemungkinan akan terus muncul di cycle-cycle selanjutnya.

---

## File baru dari sesi ini (di `/mnt/user-data/outputs/` sesi ini,
## رسلان perlu salin ke `C:\mandarin_app\`):

- `bersihkan_relasi_janggal_batch3_v2.py` — **PAKAI VERSI INI, bukan
  `bersihkan_relasi_janggal_batch3.py` (v1) yang sudah usang/berbahaya**.
  Riwayat: v1 sempat dijalankan `--apply` dan **menghapus 1.800 relasi**
  (target semula cuma ~150) karena trigger pattern-matching-nya
  ("lebih umum", "lebih luas", "更广"/"更宽", "偏" sendirian, "tidak
  selalu", dll) ternyata terlalu longgar dan menangkap ribuan relasi
  SEHAT sebagai "janggal" (mis. `两↔二`, `声↔声音`, `懂↔明白` ikut
  terhapus padahal itu sinonim wajar). رسلان restore dari
  `data\app_words.json.bak` yang otomatis dibuat sebelum apply.

  **Perbaikan di v2:**
  1. Pattern matching sekarang **HANYA laporan**, tidak pernah
     auto-hapus lagi (bahkan dengan `--apply`).
  2. Trigger phrase dipersempit drastis — hanya frasa yang benar-benar
     eksplisit ("bukan sinonim", "tidak lazim", "dipaksakan", dst),
     bukan kata umum yang muncul di deskripsi nuansa normal.
  3. Yang benar-benar terhapus dengan `--apply` **HANYA** dari daftar
     eksplisit (`flagged_relations_batch3.json`) yang sudah
     diverifikasi manual — bukan hasil pattern-matching otomatis.

  Sudah dijalankan 2x dgn v2, hasil aman terkendali: **161 relasi**
  (dari 143 pasangan lama + duplikat) lalu **26 relasi tambahan**
  (dari 26 pasangan baru hasil review manual putaran kedua) — total
  **187 relasi janggal berhasil dibersihkan** dari `app_words.json`.
  Checkpoint sudah disimpan (`checkpoint_20260901_134256.zip`, catatan
  "batch3 cleanup: 161+26=187 relasi janggal dibersihkan").

- `flagged_relations_batch3.json` — **169 pasangan** (naik dari 143,
  setelah 26 tambahan dikonfirmasi lewat review manual putaran kedua).
  Sudah habis dipakai (semua sudah di-apply), file ini tetap disimpan
  sbg riwayat/referensi kalau perlu jalankan skrip lagi di masa depan
  dgn pasangan baru ditambahkan.
- `intip_app_words.py` — alat bantu cek struktur & sampel acak
  `app_words.json`. **Sudah dipakai & terbukti akurat** — semua asumsi
  field (`simplified`, `synonyms`, `antonyms`, `synonyms_detail`,
  `antonyms_detail`, struktur list-of-dict) dikonfirmasi 100% cocok
  dgn data asli.
- `apply_hasil_sinonim_antonim.py` (v3.2) — **sudah menggantikan** versi
  رسلان. Perbaikan: fungsi baru `normalize_relation_items()` menangani
  item synonyms/antonyms yg AI kembalikan sbg string polos (bukan dict)
  — sebelumnya bikin crash `AttributeError`, sekarang dinormalisasi
  otomatis (relasi valid spt `海藻→海草` tetap tersimpan, bukan hilang).
- `PATCH_apply_hasil_sinonim_antonim.md` — **usang, abaikan**, sudah
  digantikan langsung oleh v3.2 di atas.

### 10 kandidat review yg BELUM dikonfirmasi (bukan janggal jelas,
### tapi bukan pasti aman juga — perlu رسلان putuskan manual):

  `值得→不值`, `值→不值`, `零→没有`, `小学→小学学校`, `常规↔非常规`,
  `盒子→箱子`, `父子→父亲和儿子`, `世界杯→世界盃`, `发电→产生电力`,
  `打印机→印表机`

Sengaja TIDAK ditambahkan ke `flagged_relations_batch3.json` krn
kelihatan lebih seperti false-positive (mis. `父子→父亲和儿子` itu pola
ekspansi bentuk lengkap yg sudah diterima di tempat lain spt
`师生→教师和学生`; `盒子↔箱子` itu sinonim kasual umum). Tapi belum
100% pasti — رسلان bisa putuskan sendiri kalau mau, atau biarkan saja.

## Yang perlu dicek di awal sesi berikutnya:

1. ~~Terapkan patch ke `apply_hasil_sinonim_antonim.py`~~ — **selesai**,
   v3.2 sudah menggantikan langsung.
2. ~~Jalankan `bersihkan_relasi_janggal_batch3.py`~~ — **selesai**, pakai
   v2, 187 relasi terhapus, checkpoint tersimpan.
3. Jalankan `hitung_sisa_tier_b.py` untuk angka pasti sisa pool Tier B
   (perkiraan kasar ~4.200, belum dihitung ulang).
4. Cek status `bersihkan_relasi_angka.py` (belum dicek ulang dari v30).
5. Lanjutkan siklus generate→AI→dry-run→apply seperti biasa —
   **tetap review manual tiap batch**, jangan asumsikan AI sudah patuh
   instruksi anti-hipernim meski sudah pernah kelihatan bagus di batch
   sebelumnya (kualitas terbukti tidak konsisten antar-cycle dari AI
   yang sama).
6. **Pelajaran dari insiden batch3 v1**: kalau bikin skrip otomatis
   berbasis pattern-matching teks (note_id, deskripsi, dst) utk
   MENGHAPUS data, JANGAN percaya trigger phrase pendek/generik tanpa
   uji dulu di data asli dalam mode dry-run/report-only. Kata-kata
   umum (spt "lebih", "umum", "luas", karakter tunggal Mandarin)
   punya risiko sangat tinggi match ribuan kasus sehat.

---

## Ringkasan status keseluruhan proyek

- ✅ D.4, confusion_groups.json 53→71 — selesai (dari v30)
- 🔄 E.0.2b Tier B — aktif, ~1.700 kata tambahan diproses sesi ini,
  sisa pool perlu dihitung ulang (perkiraan kasar ~4.200 dari ~5.900 di
  v30); proses jangka panjang, belum akan "selesai" dlm sesi manapun
- ✅ Bug item string-polos di hasil AI — **selesai**, patch diterapkan
  langsung ke `apply_hasil_sinonim_antonim.py` v3.2
- ✅ Pembersihan 187 relasi janggal dari review manual sesi ini —
  **selesai**, via `bersihkan_relasi_janggal_batch3_v2.py`, checkpoint
  tersimpan. (Sempat ada insiden v1 over-deletion 1.800 relasi, sudah
  di-restore & diperbaiki — lihat detail di atas)
- Backlog aktif lain (lihat memori proyek) — belum disentuh sesi ini

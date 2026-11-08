# BLUEPRINT LANJUTAN v2 — Mandarin Interaktif
# Percakapan Baru: Perbaikan Kamus, Flashcard Lanjutan, Data Fonetik
# Status proyek sebelumnya: Sesi 1-3 selesai (lihat BLUEPRINT_LANJUTAN.md untuk histori)

---

## 0. KONTEKS — APA YANG SUDAH SELESAI

Sesi 1 (kamus_PART_5): Fix #1,2,3 — pinyin angka (masih ada bug, lihat #A1 di bawah), mode
auto ID/pinyin, cidict array. SELESAI dengan catatan perbaikan lanjutan.

Sesi 2 (flashcard semua PART): Fix #6-11 — tema & radikal dinamis, jumlah kartu & mode sesi,
mode pertanyaan, back card lengkap (ADA BUG, lihat #B6), kirim ke Word Builder. SELESAI
dengan catatan perbaikan lanjutan.

Sesi 3 (kamus semua PART): Fix #4,5,12-14 — komponen radikal vs lainnya, tabel hasil + sort,
kelompok per radikal/goresan/tema/pinyin. SELESAI, perlu penyempurnaan (lihat bagian A).

Sesi ini (v2) fokus ke hasil testing رسلان: bug fix presisi, layout, dan fitur game flashcard
baru.

---

## 1. STRUKTUR FILE (tidak berubah dari v1)

```
C:\mandarin_app\
├── data\
│   ├── app_words.json
│   ├── cidict_index.json
│   ├── index_radical.json
│   ├── index_stroke.json
│   ├── index_theme.json        ← DIPERBARUI sesi ini (+119 tema eksternal, prefix ext_)
│   ├── index_theme_backup.json ← BARU, backup versi sebelum digabung tema eksternal
│   └── index_phonetic.json     ← BARU, SUDAH SIAP (537 grup, dibuat via extract_phonetic.py)
├── shared\style.css
├── index.html                  ← tidak diubah
├── kamus.html                  ← PERLU DIPERBAIKI (gabungan kamus_PART_1..6)
├── flashcard.html              ← PERLU DIPERBAIKI (gabungan flashcard_PART_1..5)
└── wordbuilder.html            ← tidak diubah sesi ini (tidak ada keluhan)
```

Rebuild setelah edit PART:
```
python gabung_kamus.py       → kamus.html
python gabung_flashcard.py   → flashcard.html
```

---

## 2. ANTRIAN PERBAIKAN — TAB KAMUS

### Fix A1: Pencarian Nada Terlalu Longgar (BUG)
**Masalah:** Ketik `ma1` atau `má` masih menampilkan ma1-ma5 / semua nada lainnya.
**Root cause:** Di `searchPinyin()` (kamus_PART_5.txt), saat `qDiacritic` ada (artinya user
mengetik nada eksplisit), kode tetap fallback ke pengecekan `pyLoose` (tanpa nada) yang
SELALU match karena loose form sama untuk semua nada. Akibatnya filter presisi nada tidak
benar-benar eksklusif.

**Fix:** Jika user mengetik nada eksplisit (terdeteksi via `hasTone` ATAU karakter pinyin
mengandung diakritik), HANYA gunakan jalur match presisi (`pyDiacritic`). Jalur `pyLoose`
HANYA dipakai jika query benar-benar tanpa nada sama sekali (`ma`, bukan `ma1`/`má`).

```javascript
function searchPinyin(data, query) {
  const qLower = query.toLowerCase().trim();
  const hasNumericTone   = /\d/.test(qLower);
  const hasDiacriticTone = /[āáǎàēéěèīíǐìōóǒòūúǔùǖǘǚǜü]/.test(qLower);
  const hasTone = hasNumericTone || hasDiacriticTone;

  if (hasTone) {
    // Mode presisi: HARUS exact match nada, tidak fallback ke loose
    const qDiacritic = (hasNumericTone ? numericToDiacritic(qLower) : qLower)
      .replace(/\s+/g, '');
    return data.filter(w => {
      const pyDiacritic = (w.pinyin || '').toLowerCase().replace(/\s+/g, '');
      return pyDiacritic === qDiacritic ||
             pyDiacritic.startsWith(qDiacritic) ||
             pyDiacritic.includes(qDiacritic);
    });
  }

  // Mode longgar: tanpa nada sama sekali → cocokkan semua nada
  const qLoose = normalizePinyin(qLower).replace(/\s+/g, '');
  return data.filter(w => {
    const pyLoose    = normalizePinyin(w.pinyin || '').replace(/\s+/g, '');
    const pyNumLoose = (w.pinyin_numeric || '').toLowerCase().replace(/\d/g, '').replace(/\s+/g, '');
    return pyLoose === qLoose || pyLoose.startsWith(qLoose) || pyLoose.includes(qLoose) ||
           pyNumLoose === qLoose || pyNumLoose.startsWith(qLoose) || pyNumLoose.includes(qLoose);
  });
}
```

### Fix A2: Hasil Pencarian Disederhanakan Jadi 1 Baris
**Masalah:** Kartu hasil saat ini menampilkan banyak badge (HSK, radikal, goresan, char_type)
yang membuat layar ramai dan boros ruang vertikal.

**Yang diinginkan:** 1 baris per hasil, hanya 3 unsur: Hanzi — Pinyin — Arti Indonesia
(contoh: `马路  mǎ lù  jalan`). Semua info tambahan (HSK, radikal, goresan, char_type,
struktur) dipindah PENUH ke panel detail kanan saja (sudah ada infrastrukturnya dari Fix #4
sesi lalu, tidak perlu dibuat ulang).

**Implementasi:** Rombak `buildResultCard()` di kamus_PART_5.txt jadi layout flex 1 baris:
hanzi (lebar tetap) | pinyin (lebar tetap) | arti (flex-grow, ellipsis jika kepanjangan).
Hapus elemen `.result-tags` dari card (HSK/radikal/stroke/type), pertahankan hanya saat mode
tabel (yang memang sudah menampilkan kolom-kolom itu secara terpisah).

### Fix A3: Tambah Filter pada Arti
**Status:** Sort by Pinyin/HSK/Goresan/Frekuensi sudah ada (mode tabel, sesi 3).
**Yang kurang:** Sort/filter berdasarkan Arti (alfabetis arti Indonesia).

**Implementasi:** Tambah kolom "Arti" jadi sortable di `renderResultsTable()`
(kamus_PART_5.txt) — klik header Arti akan sort `meanings_id[0]` alfabetis. Juga tambahkan
opsi sort yang sama di mode Kartu lewat dropdown/tombol kecil di `results-header` (bukan
cuma di mode tabel), supaya pengguna tak perlu pindah ke tabel hanya untuk mengurutkan.

### Fix A4: Panel Kanan Resizable (Drag Handle)
**Yang diinginkan:** Drag handle di antara panel tengah (`main-panel`) dan panel kanan
(`detail-panel`) supaya pengguna bisa memperlebar panel detail secara manual, mengurangi
kebutuhan scroll karena banyaknya komponen info.

**Implementasi (kamus_PART_1.txt CSS + kamus_PART_2/4.txt HTML + script baru):**
```html
<div class="panel-resize-handle" id="resize-handle"></div>
```
```javascript
// Drag listener sederhana: mousedown pada handle → mousemove ubah width detail-panel →
// mouseup selesai. Simpan lebar terakhir ke localStorage (key: 'mandarin_detail_width')
// supaya konsisten antar sesi. Beri batas min/max (mis. 280px – 600px).
```
CSS: `.panel-resize-handle { width: 5px; cursor: col-resize; background: var(--border); }`
dengan hover state highlight warna gold.

---

## 3. ANTRIAN PERBAIKAN — TAB FLASHCARD

### Fix B1: Sidebar Accordion (Collapsible per Section)
**Yang diinginkan:** Section HSK, Koleksi, Tema, Radikal masing-masing punya header yang bisa
diklik untuk expand/collapse. Saat collapse, hanya judul section yang tampil. Item yang
sedang aktif/dipilih (`.sidebar-item.active`) TETAP terlihat meski section-nya di-collapse
(section itu otomatis tetap terbuka, atau tampilkan badge kecil di header section yang
menunjukkan item aktif).
Pengaturan Sesi (kontrol jumlah kartu + mode) TETAP statis di bawah, TIDAK ikut collapse.

**Implementasi:** Tambah header collapsible per `.sidebar-section`, state expand/collapse
disimpan di JS object (tidak perlu localStorage, reset tiap reload itu OK). Default: HSK
section expanded, lainnya collapsed.

### Fix B2: Tombol "Tambah Tema" — Custom Theme dari Kata Pilihan
**Yang diinginkan:** Pengguna bisa membuat tema baru sendiri (custom, bukan dari
`index_theme.json`) dengan memilih kata-kata tertentu, lalu tema custom itu muncul di
sidebar sebagai deck tambahan.

**Implementasi:**
- Tombol "+ Tema Baru" di section Tema sidebar → modal/prompt sederhana: nama tema.
- Mode "tambah ke tema": saat aktif, klik kata di kamus ATAU di kartu flashcard yang sedang
  tampil akan menambahkan kata itu ke tema custom yang sedang dibuat.
- Simpan ke localStorage key BARU: `mandarin_custom_themes` —
  format: `{ "nama_tema": ["id1","id2",...] }`.
- Render tema custom di bawah daftar tema bawaan, dengan badge "custom" dan tombol hapus.
- `buildDeckQueue()` di flashcard_PART_3.txt perlu menerima deckId baru pola
  `custom-{nama}` yang membaca dari localStorage, bukan dari `app_words.json` filter.

### Fix B3: Radikal Populer → Semua 214 Radikal (Mode Semantik)
**Status:** `index_radical.json` SUDAH mencakup semua radikal HSK (bukan cuma 20 populer).
**Yang kurang:** Sidebar hanya menampilkan ~20 radikal hardcoded (`RADIKAL_POPULER`).

**Implementasi:** Ganti daftar hardcoded jadi render SEMUA entries dari
`STATE.dataRadical`/`FC.dataRadical`, diurutkan berdasarkan jumlah kata (terbanyak dulu),
dengan opsi "tampilkan semua" / "lebih sedikit" (collapse default 15-20 teratas + tombol
expand) supaya sidebar tidak kebanjiran 214 item sekaligus.

### Fix B4: Komponen Fonetik (声符) — DATA SUDAH SIAP ✅✅
**Status: SELESAI.** `data\index_phonetic.json` sudah berhasil dibuat dan diverifikasi.

Hasil akhir (setelah 1x perbaikan bug filter regularity — lihat catatan di bawah):
- 11.470 kata HSK diproses, 3.034 karakter unik dianalisis
- 4.351 kata punya match fonetik kuat, 537 grup komponen fonetik
- Sample tervalidasi: `卜→不/不过/不要`, `青→请/情/清/清楚`, `扌→手/选手/手术`,
  `刂→到/看到/找到` (valid — 刂 historis dari 刀/dāo, 到/dào satu rumpun bunyi)

**Catatan penting (untuk referensi, BUKAN perlu dikerjakan ulang):** percobaan pertama
salah filter karena skala `regularity` di hanzipy itu kebalikan dari intuisi (1=match
terkuat, 4=match terlemah/banyak noise). Filter awal `reg >= 1` salah meloloskan skor 4
sehingga grup terbesar berisi noise (`一`, `丨`, `十` — goresan dasar, bukan fonetik
bermakna). Sudah diperbaiki jadi `reg in {1, 2}` saja + filter tambahan buang goresan
dasar (`BASIC_STROKES` di `extract_phonetic.py`).

File final yang dipakai: `data/index_phonetic.json` — siap dipakai untuk UI flashcard mode
"Komponen Fonetik" di sesi kerja kode berikutnya.

### Catatan: Tema Tambahan dari Sumber Eksternal — DATA SUDAH SIAP ✅✅
**Status: SELESAI.** Scraper `scrape_allset_themes.py` berhasil mengambil 123 halaman dari
AllSet Learning Vocabulary Wiki (CC BY-NC, atribusi otomatis tersimpan per tema), lalu
`merge_themes.py` mencocokkan kata-katanya dengan `app_words.json`.

Hasil akhir:
- 119 tema berhasil di-scrape, 2.466 entri kata mentah
- 119 tema baru berhasil ditambahkan ke `data/index_theme.json` (key berprefix `ext_`,
  mis. `ext_colors`, `ext_education`, `ext_chinese_idioms`)
- 1.852 kata berhasil dicocokkan dengan ID yang sudah ada di `app_words.json`
- 614 kata TIDAK ditemukan (dilaporkan terpisah di `unmatched_theme_words.json` — kosakata
  di luar cakupan HSK 1-9 milik رسلان, opsional untuk ditambahkan manual nanti, TIDAK
  diproses otomatis karena butuh data lengkap radikal/goresan/komponen yang tidak tersedia
  dari hasil scrape)

File `data/index_theme_backup.json` adalah backup tema lama SEBELUM digabung, untuk jaga-jaga.

**Tindak lanjut opsional (bukan prioritas):** `label_id` di tema baru masih pakai
`label_en` (judul Inggris) sebagai placeholder — رسلان bisa terjemahkan manual ke Bahasa
Indonesia kapan saja langsung di `index_theme.json`, tidak mempengaruhi fungsi aplikasi.

### Fix B5: Filter Game Baru (Prioritas: yang sudah ada datanya)
Disepakati: kerjakan dulu yang TIDAK perlu data tambahan, sisanya (measure word, verb
complement, kembaran visual) ditunda ke roadmap data-prep terpisah.

#### B5a: Filter "Struktur Karakter" (sudah ada field `structure`)
Mirip pola radikal/tema: pilih struktur (Kiri-Kanan, Atas-Bawah, dst — pakai
`structureLabel()` yang sudah ada di kamus_PART_5.txt, port ke flashcard) → deck kata dengan
struktur itu. Tidak perlu index file baru, bisa filter langsung dari `FC.allWords` di client.

#### B5b: Filter "Jebakan Nada" (Tone Trap) — auto-derived, tanpa data tambahan
Kelompokkan kata-kata yang punya `pinyin_numeric` tanpa nada sama tapi nada beda (mis. mai →
mǎi vs mài). Dihasilkan dinamis di client: build map `pinyinTanpaNada → [kata...]`, filter
yang grupnya punya ≥2 nada berbeda, sajikan sebagai deck "Jebakan Nada" gabungan (semua
pasangan jadi satu deck besar, atau per-suku-kata jika datanya banyak — putuskan saat
implementasi berdasar ukuran data).

#### B5c: Filter "Goresan Ekstrem" (sudah ada field `stroke_count`)
Dua sub-deck cepat: "1-3 Goresan" (mudah) dan "15+ Goresan" (sulit). Filter langsung dari
`stroke_count`, tidak perlu data baru.

#### B5d: Filter "Lawan Kata" (field `antonyms` — PERLU DICEK DULU)
**Sebelum implementasi:** Claude/رسلان cek dulu berapa persen `app_words.json` punya
`antonyms` terisi (tidak kosong). Jika cukup banyak (mis. >100 kata punya pasangan), baru
develop mode "Temukan Pasangan" (tampilkan 1 kartu, user pilih lawan katanya dari beberapa
opsi). Jika datanya terlalu sedikit, fitur ini ditunda sampai data diperkaya.

**Item yang DITUNDA (perlu data prep terpisah, di luar sesi ini):**
- Kembaran Visual (huruf mirip bentuk)
- Measure Word pairing
- Kata Kerja Berantai (verb complement)
- Saudara Kembar Inggris (near-synonym clustering)
- Pola Nada Khusus (kombinasi nada 3-3 dst — bisa didekati otomatis tapi linguistik rumit,
  perlu rule tambahan)
- Karakter Ambivalen / Palindrom — perlu kurasi manual

### Fix B6: Back Card Selalu Tampilkan Hanzi (BUG)
**Masalah:** Saat mode pertanyaan = Hanzi, kode sesi lalu SEMBUNYIKAN `fc-back-hanzi` karena
dianggap redundan (sudah tampil di depan kartu). Padahal secara pedagogis tetap perlu
ditampilkan di belakang untuk penguatan visual.

**Fix:** Di `renderCurrentCard()` (flashcard_PART_4.txt), HAPUS kondisi yang menyembunyikan
`fc-back-hanzi` saat `actualMode === 'hanzi'`. Selalu tampilkan hanzi di belakang kartu,
apapun mode pertanyaannya — back card minimal SELALU berisi: Hanzi besar, Pinyin, Arti
Indonesia (sudah benar untuk mode lain, tinggal samakan untuk mode hanzi).

---

## 4. TAB WORD BUILDER

Tidak ada keluhan/perubahan untuk sesi ini. **JANGAN DIUBAH.**

---

## 5. URUTAN PENGERJAAN YANG DIREKOMENDASIKAN

```
Sesi A (kamus_PART_1,2,4,5):
1. Fix A1 — perbaiki searchPinyin() agar nada presisi tidak leak ke nada lain
2. Fix A2 — sederhanakan buildResultCard() jadi 1 baris (hanzi/pinyin/arti)
3. Fix A3 — tambah sort by Arti di tabel + tombol sort cepat di mode kartu
4. Fix A4 — drag handle resizable panel kanan
5. Gabung → test kamus.html

Sesi B (flashcard_PART_1,2,3,4):
6. Fix B6 — bug back card hanzi (quick fix, kerjakan duluan karena simpel)
7. Fix B1 — sidebar accordion per section
8. Fix B3 — perluas radikal jadi semua 214 + collapse/expand
9. Fix B2 — tombol tambah tema custom + localStorage
10. Fix B5a, B5b, B5c — filter struktur, jebakan nada, goresan ekstrem
11. Fix B5d — cek data antonyms, implementasi jika layak
12. BARU — UI mode "Komponen Fonetik" (data index_phonetic.json sudah siap, lihat status
    SELESAI di bagian 3 Fix B4) — pola sama seperti radikal: pilih fonetik → deck kata
13. BARU — 119 tema eksternal (prefix ext_) otomatis ikut tampil di sidebar Tema karena
    sudah masuk index_theme.json — TIDAK perlu kode tambahan, hanya perlu dipastikan
    label_id (saat ini placeholder bahasa Inggris) ditampilkan dengan baik di UI, dan
    opsional rsalan terjemahkan ke Bahasa Indonesia manual di file JSON kapan saja.
14. Gabung → test flashcard.html

Sesi C (data prep) — SELESAI ✅, tidak perlu dikerjakan ulang:
~~13. رسلان: pip install hanzipy --break-system-packages~~ SELESAI
~~14. Fix B4 — extract_phonetic.py~~ SELESAI — index_phonetic.json siap (537 grup)
~~scrape_allset_themes.py + merge_themes.py~~ SELESAI — 119 tema baru di index_theme.json

Roadmap masa depan (belum dijadwalkan):
15. Kembaran Visual, Measure Word, Verb Complement, Near-Synonym, Pola Nada 3-3, Palindrom
    — semua butuh data prep signifikan, didiskusikan ulang kapan رسلان siap kerjakan.
16. Opsional: tambahkan manual 614 kata di unmatched_theme_words.json ke app_words.json
    (di luar cakupan HSK 1-9 yang sudah ada) jika رسلان berminat memperluas data dasar.
```

---

## 6. CATATAN TEKNIS PENTING (carry-over dari v1, masih berlaku)

1. Setiap PART ditulis/diedit dengan `str_replace` atau `bash_tool` heredoc, BUKAN
   `create_file` jika file sudah ada.
2. WAJIB gabung ulang (`python gabung_*.py`) setelah edit PART, sebelum test.
3. Guard check (`if (!STATE.dataHsk) return;` dsb.) jangan dihapus saat refactor.
4. localStorage keys baru sesi ini: `mandarin_custom_themes` (B2),
   `mandarin_detail_width` (A4). Jangan ubah nama key yang sudah ada (lihat tabel di v1).
5. `index_phonetic.json` adalah file BARU, formatnya disepakati saat script Python dibuat
   (lihat B4) — kemungkinan besar mirip `index_radical.json`: `{ "马": ["妈","骂",...] }`.
6. Semua heuristik otomatis (Jebakan Nada) harus dianggap draf awal, bukan kebenaran
   linguistik mutlak — رسلان akan melakukan spot-check sebelum dianggap final.
7. Data fonetik (B4) SUDAH SELESAI — pakai paket Python `hanzipy`
   (https://github.com/Synkied/hanzipy), hasil tersimpan di `data/index_phonetic.json`
   (537 grup, sudah divalidasi). Lihat detail & catatan bug-fix di bagian 3, Fix B4.
8. Tema eksternal (119 tema, 1.852 kata) SUDAH SELESAI digabung ke `data/index_theme.json`
   via `scrape_allset_themes.py` + `merge_themes.py`. Backup tema lama ada di
   `data/index_theme_backup.json`.


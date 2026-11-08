# BLUEPRINT PROYEK: KAMUS MANDARIN INTERAKTIF
# Versi: 1.0 — Dokumen Sambungan Percakapan
# Tujuan: Dokumen ini adalah rekap lengkap dari percakapan sebelumnya.
# Paste dokumen ini di awal percakapan baru agar Claude langsung mengerti
# konteks, status, dan cara melanjutkan proyek tanpa perlu penjelasan ulang.

---

## BAGIAN 1: IDENTITAS PROYEK

**Nama proyek**: Kamus Mandarin Interaktif (Full Offline)
**Platform**: Multi-file HTML — berjalan di browser tanpa server
**Bahasa UI**: Indonesia
**Target pengguna**: Pelajar bahasa Mandarin berbahasa Indonesia

### Fitur utama (3 modul):
1. **Kamus** — pencarian hanzi / pinyin / terjemahan Indonesia
2. **Flashcard SRS** — sistem pengulangan terjadwal (Spaced Repetition), 4 tombol penilaian, mirip Anki
3. **Word Builder** — pembentukan kalimat interaktif berdasarkan 9 pola sintaksis Mandarin

---

## BAGIAN 2: KEPUTUSAN DESAIN (SUDAH FINAL)

### Tema Visual
- **Mode**: Dark mode elegan, nuansa tradisional Tiongkok
- **Warna utama**: Emas `#C9A84C` (aksen dominan), Merah `#C0392B` (aksen sekunder)
- **Background**: `#0F0F0F` (latar utama), `#1A1A1A` (kartu), `#111110` (sidebar/panel)
- **Teks**: `#F0EAD6` (utama), `#8A8070` (redup), `#555048` (muted)
- **Border**: `#2E2A24` (default), `#3A3020` (emas redup)

### CSS Variables Wajib (didefinisikan di setiap file HTML):
```css
:root {
  --gold: #C9A84C;
  --gold-dim: #8B6914;
  --red: #C0392B;
  --bg-dark: #0F0F0F;
  --bg-card: #1A1A1A;
  --bg-card2: #242424;
  --bg-input: #2A2A2A;
  --text-main: #F0EAD6;
  --text-dim: #8A8070;
  --text-muted: #555048;
  --border: #2E2A24;
  --border-gold: #3A3020;
}
```

### Tipografi
- Font: system-ui (tidak perlu Google Fonts, offline)
- Hanzi tampil besar: 28px di kartu hasil pencarian, 72px di panel detail
- Pinyin: warna emas `--gold`

### Struktur File (MULTI-FILE, SUDAH FINAL):
```
mandarin_app/
├── index.html              ← halaman utama / landing / navigasi
├── kamus.html              ← Modul 1: Pencarian Kamus
├── flashcard.html          ← Modul 2: Flashcard SRS
├── wordbuilder.html        ← Modul 3: Word Builder
├── data/
│   ├── app_words.json      ← 6.6 MB — data utama 11.470 kata HSK
│   ├── cidict_index.json   ← 16 MB — kamus extended 121.158 kata
│   ├── themes.json         ← 19 MB — 40 tema tematik
│   ├── word_builder_data.json ← 36 KB — data pola kalimat
│   ├── index_hsk.json      ← 97 KB — index per level HSK
│   ├── index_radical.json  ← 1.3 MB — index per radikal
│   └── index_stroke.json   ← 1.3 MB — index per jumlah goresan
└── shared/
    ├── style.css           ← CSS bersama (variabel, komponen umum)
    ├── nav.js              ← navigasi antar modul
    └── srs.js              ← engine SRS bersama (dipakai flashcard.html)
```

### Lokasi Data di PC:
```
C:\mandarin_kamus\database\generated\app_words.json
C:\mandarin_kamus\database\generated\word_builder_data.json
C:\mandarin_kamus\output\themes.json
C:\mandarin_kamus\database\cidict_index.json
C:\mandarin_kamus\indexes\index_hsk.json
C:\mandarin_kamus\indexes\index_radical.json
C:\mandarin_kamus\indexes\index_stroke.json
```
→ Semua file di atas akan dicopy ke folder `mandarin_app/data/` saat deploy.

---

## BAGIAN 3: STRUKTUR DATA (SUDAH FINAL)

### app_words.json — field per entri:
```json
{
  "id": "明",
  "simplified": "明",
  "traditional": "明",
  "pinyin": "míng",
  "pinyin_numeric": "ming2",
  "bopomofo": "ㄇㄧㄥˊ",
  "hsk": "3",
  "hsk2": "3",
  "frequency": 1234,
  "pos": ["a", "tg"],
  "pos_id": ["kata sifat", "kata waktu"],
  "meanings_id": ["terang; cerah", "memahami", "bulan depan"],
  "meanings_en": ["bright", "clear", "next month"],
  "radical": "日",
  "radical_number": 72,
  "stroke_count": 8,
  "structure": "left-right",
  "components": ["日", "月"],
  "char_type": "ideogram",
  "themes": ["hari_tanggal", "warna", "sifat_deskripsi"],
  "synonyms": [],
  "antonyms": []
}
```

### word_builder_data.json — struktur:
```
{
  "sentence_patterns": [ 9 pola kalimat ],
  "conjunctions": [ 4 pola majemuk ],
  "function_types": [ 4 tipe fungsi ],
  "word_categories": { 3 kategori kosakata }
}
```

### Pola kalimat yang tersedia (sentence_patterns):
| ID | Nama |
|----|------|
| verbal | Kalimat Verbal (S+KK+O) |
| adjectival | Kalimat Adjektival (S+很+KS) |
| shi_sentence | Kalimat 是 (Identifikasi) |
| you_sentence | Kalimat 有 (Ada/Punya) |
| ba_sentence | Kalimat 把 (Penanganan Objek) |
| bei_sentence | Kalimat Pasif 被 |
| bi_comparison | Kalimat Perbandingan 比 |
| serial_verb | Kalimat Seri Verba |
| topic_comment | Kalimat Topik-Komentar |

---

## BAGIAN 4: DESAIN TIAP MODUL

### 4A. kamus.html — Layout 3-Panel

```
┌─────────────────────────────────────────────────────────┐
│  NAV: 漢 Kamus Mandarin | [Kamus] [Flashcard] [Builder] │
├──────────┬────────────────────────────┬──────────────────┤
│ SIDEBAR  │  AREA PENCARIAN            │  PANEL DETAIL    │
│ 220px    │  (flex-1)                  │  280px           │
│          │  ┌──────────────────────┐  │                  │
│ Filter:  │  │ 🔍 Cari hanzi/pinyin│  │  [Hanzi besar]   │
│ - Semua  │  └──────────────────────┘  │  72px            │
│ - HSK 1  │  [Pills filter mode]       │                  │
│ - HSK 2  │  ─────────────────────     │  Pinyin (emas)   │
│ - HSK 3  │  [Kartu hasil 1]           │                  │
│ - HSK 4-7│  [Kartu hasil 2] ←selected│  Arti (list)     │
│          │  [Kartu hasil 3]           │  Komponen        │
│ Kelompok:│  [Kartu hasil 4]           │  日 + 月 = 明    │
│ - Radikal│  ...                       │                  │
│ - Stroke │                            │  Meta: stroke,   │
│ - Tema   │                            │  radikal,        │
│ - Pinyin │                            │  struktur, tipe  │
│          │                            │                  │
│ [cidict] │                            │  [+Flashcard]    │
│ 121K kata│                            │  [Simpan]        │
└──────────┴────────────────────────────┴──────────────────┘
```

**Fitur pencarian:**
- Real-time search saat mengetik (debounce 300ms)
- Deteksi otomatis mode input: hanzi / pinyin / terjemahan Indonesia
- Pencarian primer: `app_words.json` (11.470 HSK)
- Pencarian sekunder: `cidict_index.json` (121.158) jika hasil < 5
- Sorting: relevansi → frekuensi → HSK level
- Highlight teks yang match di hasil

**Kartu hasil pencarian** menampilkan:
- Hanzi (28px), Pinyin (emas), Badge HSK
- Arti pertama (Indonesia)
- Tags: radikal, stroke, struktur, tipe karakter

**Panel detail** menampilkan:
- Hanzi besar (72px)
- Semua arti Indonesia (numbered list)
- Komponen visual (日 + 月 = 明) dengan penjelasan
- Grid meta: radikal, stroke, struktur, tipe, tradisional, bopomofo
- Tema (tags)
- Tombol: tambah ke flashcard, simpan ke bookmark

### 4B. flashcard.html — SRS Engine

**Deck yang tersedia (dipilih dari sidebar):**
1. Per HSK Level (1, 2, 3, 4, 5, 6, 7-9)
2. Per Radikal (214 radikal Kangxi)
3. Per Jumlah Goresan (1-20+)
4. Per Tema (40 tema)
5. Per Pinyin (grouped by initial)
6. Per Struktur Karakter (left-right, top-bottom, dll)
7. Per Tipe (pictogram, ideogram, compound)
8. Kartu Tersimpan (dari bookmark kamus)
9. Kartu Salah (review ulang)

**Layout kartu:**
```
┌────────────────────────────────────┐
│  [Deck: HSK 1] [Sesi: 20/50]       │
│  Progress bar ━━━━━━━━━━━━░░░░ 40% │
├────────────────────────────────────┤
│                                    │
│           明                       │ ← FRONT (hanzi saja)
│                                    │
│      [ Tampilkan Jawaban ]         │
│                                    │
├────────────────────────────────────┤
│  míng                              │ ← BACK (setelah klik)
│  ──────────────────                │
│  terang; cerah; memahami           │
│  komponen: 日 + 月                 │
│  radikal: 日 | stroke: 8           │
│                                    │
│  [Lagi]  [Sulit]  [Baik]  [Mudah] │
│   1 hari  3 hari  7 hari  14 hari  │
└────────────────────────────────────┘
```

**SRS Algorithm (SM-2 disederhanakan):**
- 4 tombol: Lagi (0), Sulit (1), Baik (2), Mudah (3)
- Interval awal: 1, 3, 7, 14 hari
- Ease factor: 2.5 (default), naik/turun berdasarkan jawaban
- Data disimpan di `localStorage` key: `mandarin_srs_v1`
- Format storage:
```json
{
  "明": {
    "interval": 7,
    "ease": 2.5,
    "due": "2026-07-04",
    "reps": 5,
    "lapses": 1
  }
}
```

### 4C. wordbuilder.html — Pembentuk Kalimat

**Layout:**
```
┌─────────────────────────────────────────────────────┐
│  NAV                                                │
├──────────────┬──────────────────────────────────────┤
│ PILIH POLA   │  AREA BUILDER                        │
│              │                                      │
│ ○ Verbal     │  Pola: Kalimat Verbal (S+KK+O)       │
│ ○ Adjektival │  ─────────────────────────────       │
│ ○ 是-句      │                                      │
│ ○ 有-句      │  [Subjek ▼]  [Modal ▼]  [KK ▼]      │
│ ○ 把-句      │   我/你/他    能/会/想    吃/喝/学     │
│ ○ 被-句      │                                      │
│ ○ 比较句     │  [Aspek ▼]  [Objek ▼]               │
│ ○ 连动句     │   了/着/过   饭/水/书                 │
│ ○ 话题句     │                                      │
│              │  ┌─────────────────────────────────┐ │
│ ── Majemuk ──│  │  我 喝 水。                      │ │
│ ○ 因为…所以  │  │  Wǒ hē shuǐ.                    │ │
│ ○ 如果…就    │  │  Saya minum air.                 │ │
│ ○ 虽然…但是  │  └─────────────────────────────────┘ │
│ ○ 一边…一边  │                                      │
│              │  [Reset]  [Acak]  [+Flashcard]       │
│ ── Fungsi ── │                                      │
│ ○ Tanya 吗   │  💡 Tip: Verba harus diikuti         │
│ ○ Tanya WH   │  komplemen hasil (不能 telanjang)    │
│ ○ Perintah   │                                      │
│ ○ Seru/Ekskl │  [ Contoh kalimat lain ▼ ]          │
└──────────────┴──────────────────────────────────────┘
```

### 4D. index.html — Landing Page
- Hero dengan karakter animasi 漢字
- 3 kartu modul (Kamus, Flashcard, Word Builder)
- Statistik: jumlah kata, deck tersedia, dll
- Link ke masing-masing modul

---

## BAGIAN 5: METODE PENULISAN SCRIPT — WAJIB DIIKUTI

### ⚠️ PENTING: PENULISAN BERTAHAP (SEGMENTED) — WAJIB

Karena setiap file HTML besar (estimasi 800–1500 baris per file),
penulisannya HARUS dipecah menjadi segmen-segmen kecil.
Setiap segmen adalah file terpisah yang TIDAK berfungsi sendiri,
namun ketika SEMUA segmen digabungkan menjadi satu file utuh,
maka akan berfungsi dengan sempurna.

**ALASAN**: Jika ditulis langsung dalam satu respons, Claude akan
kehabisan token di tengah jalan dan output menjadi terpotong / rusak.

---

### FORMAT SEGMEN

Setiap segmen diberi nama dengan format:
```
[NAMA_FILE]_PART_[NOMOR].txt
```

Contoh untuk kamus.html yang dipecah 5 bagian:
```
kamus_PART_1.txt  ← DOCTYPE, <head>, CSS lengkap
kamus_PART_2.txt  ← <body> pembuka, navbar, sidebar HTML
kamus_PART_3.txt  ← area pencarian + panel hasil HTML
kamus_PART_4.txt  ← panel detail HTML + penutup </body>
kamus_PART_5.txt  ← seluruh JavaScript (search engine, event handler)
```

---

### CARA MENGGABUNGKAN SEGMEN

**Metode A — Manual Copy-Paste:**
Buka text editor (Notepad++, VS Code), buka semua PART_*.txt,
copy isi masing-masing secara berurutan ke file HTML tujuan.

**Metode B — Script Python (direkomendasikan):**
Claude akan menyertakan script `gabung_[namafile].py` yang bila
dijalankan akan otomatis menggabungkan semua segmen:

```python
# gabung_kamus.py
parts = ['kamus_PART_1.txt', 'kamus_PART_2.txt',
         'kamus_PART_3.txt', 'kamus_PART_4.txt', 'kamus_PART_5.txt']

with open('kamus.html', 'w', encoding='utf-8') as out:
    for part in parts:
        with open(part, 'r', encoding='utf-8') as f:
            out.write(f.read())

print("✅ kamus.html berhasil dibuat!")
```

---

### PEMBAGIAN SEGMEN PER FILE

#### kamus.html (estimasi ~1200 baris)
| Segmen | Isi | Estimasi baris |
|--------|-----|----------------|
| PART_1 | `<!DOCTYPE>` → `</style>` (head + seluruh CSS) | ~250 baris |
| PART_2 | `<body>` → navbar + sidebar HTML | ~150 baris |
| PART_3 | Area pencarian + daftar hasil HTML (kosong, diisi JS) | ~100 baris |
| PART_4 | Panel detail HTML + `</body></html>` | ~150 baris |
| PART_5 | `<script>` — load data, search engine, render kartu | ~350 baris |
| PART_6 | `<script>` lanjutan — panel detail, event handler, init | ~200 baris |

#### flashcard.html (estimasi ~1000 baris)
| Segmen | Isi | Estimasi baris |
|--------|-----|----------------|
| PART_1 | head + CSS (termasuk animasi flip kartu) | ~250 baris |
| PART_2 | HTML: sidebar deck, area kartu, tombol SRS | ~200 baris |
| PART_3 | JS: SRS engine (algoritma SM-2, localStorage) | ~250 baris |
| PART_4 | JS: load deck, render kartu, event handler | ~200 baris |
| PART_5 | JS: statistik, progress, init | ~150 baris |

#### wordbuilder.html (estimasi ~900 baris)
| Segmen | Isi | Estimasi baris |
|--------|-----|----------------|
| PART_1 | head + CSS | ~200 baris |
| PART_2 | HTML: sidebar pola + area builder | ~200 baris |
| PART_3 | JS: load word_builder_data.json, render slot dropdown | ~200 baris |
| PART_4 | JS: build kalimat, validasi, contoh, event handler | ~250 baris |

#### index.html (estimasi ~300 baris)
| Segmen | Isi |
|--------|-----|
| PART_1 | head + CSS + HTML lengkap (satu file, tidak dipecah) |

#### shared/style.css (estimasi ~200 baris)
| Segmen | Isi |
|--------|-----|
| PART_1 | Reset, variabel, komponen bersama (satu file) |

#### shared/srs.js (estimasi ~150 baris)
| Segmen | Isi |
|--------|-----|
| PART_1 | SRS class/engine yang bisa diimport (satu file) |

---

### PROTOKOL PENULISAN — WAJIB DIIKUTI CLAUDE

Setiap kali Claude menulis segmen baru, WAJIB:

1. **Nyatakan segmen yang sedang ditulis** di baris pertama komentar:
   ```html
   <!-- ═══════════════════════════════════════════════
        kamus.html — PART 1/6
        ISI: DOCTYPE, head, semua CSS
        SAMBUNG KE: kamus_PART_2.txt
   ═══════════════════════════════════════════════ -->
   ```

2. **Akhiri setiap segmen** dengan komentar penutup:
   ```html
   <!-- END PART 1 — lanjut ke kamus_PART_2.txt -->
   ```

3. **Jangan pernah menulis segmen yang melebihi ~300 baris** dalam
   satu respons. Jika mendekati batas, potong dan beri tahu:
   ```
   ⚠️ Segmen ini sudah ~280 baris. Lanjut di PART berikutnya.
   Ketik: "lanjut PART 3" untuk melanjutkan.
   ```

4. **Sertakan checklist progres** di akhir setiap respons:
   ```
   ✅ kamus_PART_1.txt — SELESAI
   ✅ kamus_PART_2.txt — SELESAI
   🔄 kamus_PART_3.txt — SEDANG DIKERJAKAN
   ⬜ kamus_PART_4.txt — BELUM
   ⬜ kamus_PART_5.txt — BELUM
   ⬜ kamus_PART_6.txt — BELUM
   ```

---

### URUTAN PENGERJAAN (SUDAH DISEPAKATI)

```
TAHAP 1: shared/style.css         ← fondasi visual bersama
TAHAP 2: kamus.html (PART 1-6)    ← MODUL PERTAMA (prioritas)
TAHAP 3: gabung_kamus.py          ← script penggabung
TAHAP 4: TEST kamus.html          ← pengguna menguji, lapor bug
TAHAP 5: flashcard.html (PART 1-5)
TAHAP 6: gabung_flashcard.py
TAHAP 7: TEST flashcard.html
TAHAP 8: wordbuilder.html (PART 1-4)
TAHAP 9: gabung_wordbuilder.py
TAHAP 10: TEST wordbuilder.html
TAHAP 11: index.html
TAHAP 12: Integrasi & polish akhir
```

---

## BAGIAN 6: KOMPONEN UI — REFERENSI VISUAL

### Warna badge HSK:
```css
.hsk-1 { background: rgba(192,57,43,0.15); color: #E74C3C; }   /* merah */
.hsk-2 { background: rgba(230,126,34,0.15); color: #E67E22; }   /* oranye */
.hsk-3 { background: rgba(241,196,15,0.15); color: #F1C40F; }   /* kuning */
.hsk-4 { background: rgba(39,174,96,0.15); color: #2ECC71; }    /* hijau */
.hsk-5 { background: rgba(52,152,219,0.15); color: #3498DB; }   /* biru */
.hsk-6 { background: rgba(155,89,182,0.15); color: #9B59B6; }   /* ungu */
.hsk-7 { background: rgba(201,168,76,0.15); color: #C9A84C; }   /* emas */
```

### Warna tag tipe:
```css
.tag-radical    { border-color: rgba(192,57,43,0.3); color: #C0392B; }
.tag-stroke     { border-color: rgba(52,152,219,0.3); color: #5DADE2; }
.tag-structure  { border-color: rgba(39,174,96,0.3); color: #58D68D; }
.tag-type       { border-color: rgba(155,89,182,0.3); color: #C39BD3; }
```

### Tombol SRS:
```css
.btn-lagi   { background: rgba(231,76,60,0.15);  color: #E74C3C; }  /* merah */
.btn-sulit  { background: rgba(230,126,34,0.15); color: #E67E22; }  /* oranye */
.btn-baik   { background: rgba(39,174,96,0.15);  color: #2ECC71; }  /* hijau */
.btn-mudah  { background: rgba(52,152,219,0.15); color: #3498DB; }  /* biru */
```

---

## BAGIAN 7: LOGIKA JAVASCRIPT UTAMA

### Search Engine (kamus.html):
```javascript
// Pseudocode search engine
function search(query) {
  query = query.trim();
  if (!query) return [];

  const mode = detectMode(query);
  // mode: 'hanzi' | 'pinyin' | 'indonesian' | 'english'

  let results = [];

  if (mode === 'hanzi') {
    // Exact match dulu
    results = appWords.filter(w =>
      w.simplified.includes(query) || w.traditional.includes(query)
    );
  } else if (mode === 'pinyin') {
    // Normalize: hilangkan tone marks untuk fuzzy search
    results = appWords.filter(w =>
      normalizePinyin(w.pinyin).includes(normalizePinyin(query))
    );
  } else {
    // Indonesian/English: cari di meanings
    results = appWords.filter(w =>
      w.meanings_id.some(m => m.toLowerCase().includes(query.toLowerCase())) ||
      w.meanings_en.some(m => m.toLowerCase().includes(query.toLowerCase()))
    );
  }

  // Jika hasil < 5, tambah dari cidict
  if (results.length < 5) {
    const extra = searchCidict(query);
    results = [...results, ...extra];
  }

  // Sort: exact match > starts with > contains; lalu by frequency
  return sortResults(results, query).slice(0, 50);
}

function detectMode(query) {
  if (/[\u4e00-\u9fff]/.test(query)) return 'hanzi';
  if (/^[a-züāáǎàēéěèīíǐìōóǒòūúǔùǖǘǚǜ\s]+$/i.test(query)) return 'pinyin';
  return 'indonesian';
}
```

### SRS Engine (srs.js):
```javascript
class SRSEngine {
  constructor() {
    this.data = JSON.parse(localStorage.getItem('mandarin_srs_v1') || '{}');
  }

  // Ambil kartu yang jatuh tempo hari ini
  getDueCards(deck) {
    const today = new Date().toISOString().split('T')[0];
    return deck.filter(card => {
      const d = this.data[card.id];
      return !d || d.due <= today;
    });
  }

  // Proses jawaban pengguna (0=Lagi, 1=Sulit, 2=Baik, 3=Mudah)
  answer(cardId, quality) {
    const card = this.data[cardId] || { interval: 1, ease: 2.5, reps: 0, lapses: 0 };

    if (quality === 0) {
      card.interval = 1;
      card.lapses++;
      card.ease = Math.max(1.3, card.ease - 0.2);
    } else {
      const multiplier = [null, 1.2, card.ease, card.ease * 1.3][quality];
      card.interval = Math.round(
        card.reps === 0 ? 1 :
        card.reps === 1 ? 3 :
        card.interval * multiplier
      );
      card.ease = Math.max(1.3, card.ease + [0, -0.15, 0, 0.1][quality]);
    }

    card.reps++;
    const due = new Date();
    due.setDate(due.getDate() + card.interval);
    card.due = due.toISOString().split('T')[0];

    this.data[cardId] = card;
    this.save();
    return card.interval;
  }

  save() {
    localStorage.setItem('mandarin_srs_v1', JSON.stringify(this.data));
  }
}
```

---

## BAGIAN 8: STATUS PROYEK SAAT INI

### Data (semua SELESAI):
- [x] `app_words.json` — 11.470 kata, semua field terisi
- [x] `word_builder_data.json` — 9 pola kalimat, 4 majemuk, 4 fungsi
- [x] `structure_map.json` — 103.006 karakter, 8 tipe struktur
- [x] `component_map.json` — 103.006 karakter, komponen IDS
- [x] `character_type_map.json` — pictogram/ideogram/compound
- [x] `themes.json` — 40 tema, setiap tema punya field words lengkap
- [x] `cidict_index.json` — 121.158 kata dengan meanings_id Indonesia
- [x] Semua index: hsk, radical, stroke, pinyin

### Coding (BELUM DIMULAI):
- [ ] shared/style.css
- [ ] shared/srs.js
- [ ] kamus.html (PART 1-6)
- [ ] flashcard.html (PART 1-5)
- [ ] wordbuilder.html (PART 1-4)
- [ ] index.html

---

## BAGIAN 9: INSTRUKSI UNTUK CLAUDE DI PERCAKAPAN BARU

Jika Anda adalah Claude yang membaca dokumen ini di percakapan baru:

1. Baca dokumen ini secara menyeluruh sebelum merespons
2. Status proyek: **data selesai, coding belum dimulai**
3. Modul pertama yang dikerjakan: **kamus.html**
4. Urutan pengerjaan: style.css → kamus PART1 → PART2 → dst
5. WAJIB gunakan metode segmented seperti dijelaskan di Bagian 5
6. WAJIB sertakan checklist progres di setiap respons
7. Tanya pengguna: "Mulai dari mana? style.css dulu atau langsung kamus PART 1?"
8. Jangan menulis ulang data atau blueprint — langsung ke coding

### Perintah yang bisa diucapkan pengguna:
- "mulai style.css" → tulis shared/style.css
- "lanjut PART [N]" → tulis segmen berikutnya
- "ulangi PART [N]" → tulis ulang segmen yang diminta
- "gabung semua" → tulis script Python penggabung
- "lanjut flashcard" → mulai flashcard.html setelah kamus selesai

---

*Blueprint ini dibuat berdasarkan percakapan panjang yang mencakup:*
*inventarisasi data, inspeksi mendalam, preprocessing, dan perancangan visual.*
*Semua keputusan di dokumen ini sudah disepakati bersama pengguna.*
*Versi mockup visual sudah disetujui (dark mode, emas+merah, 3-panel).*

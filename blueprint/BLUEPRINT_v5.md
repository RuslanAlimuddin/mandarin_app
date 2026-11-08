# Mandarin Interaktif — BLUEPRINT v5

> Dokumen ini adalah hasil sesi diskusi arsitektur mendalam (tanpa coding) yang
> melanjutkan BLUEPRINT_v4.md. Tujuannya: mengunci keputusan struktural dulu
> supaya eksekusi per-sesi ke depan tidak perlu bongkar ulang kode yang sudah jadi.

---

## 1. Koreksi dari BLUEPRINT_v4

Verifikasi langsung ke localStorage (bukan cuma dari catatan lama) menemukan:

| Ditulis di v4 | Ternyata | Catatan |
|---|---|---|
| `mandarin_wb_saved` | **`builder_flashcards`** | Ini key asli untuk koleksi kalimat tersimpan Word Builder |
| — | `mandarin_wrong_v1` | Array flat berisi hanzi yang pernah dijawab salah, contoh: `["匹配","低","画面",...]` |
| — | `mandarin_wb_hsk` | Kemungkinan status checkbox filter HSK (belum diverifikasi isi persis) |
| — | `wb_ref_word` | 1 objek kata lengkap (skema sama seperti entry `app_words.json`) — bukan array/antrian |

`mandarin_srs_v1` terverifikasi berisi field: `interval`, `ease`, `due`, `reps`, `lapses` — key-nya hanzi langsung.
(Catatan: field aslinya `reps`/`due`, bukan `repetitions`/`dueDate` seperti dugaan awal.)

---

## 2. Arsitektur `shared/` yang disepakati

```
shared/
├── style.css        (sudah ada)
├── core.js           BARU — generik UI/DOM
├── pinyin.js         BARU — utilitas pinyin (pindahan dari kamus)
├── audio.js          BARU (Tier 1) — wrapper TTS browser
└── srs.js            BARU (Tier 2) — helper baca-saja status SRS
```

### `shared/core.js`
- `$(id)` — ganti semua nama beda-beda: `$$()` di flashcard dan `$w()` di wordbuilder **dihapus total**,
  disatukan jadi `$()` di ketiga halaman. **Tidak ada alias tersisa** — migrasi tuntas sekali jalan.
- `showToast(msg, type)`
- `escHtml(str)`
- ⚠️ Verifikasi saat coding: pastikan implementasi `showToast` identik di 3 halaman sebelum disatukan;
  kalau ada perbedaan kecil, putuskan versi final saat itu juga.

### `shared/pinyin.js`
- `normalizePinyin(str)`, `numericToDiacritic(str)`, `detectMode(query)` — pindah dari kamus tanpa ubah logika.
- Sengaja dipisah dari `core.js` (bukan digabung) karena `audio.js` kemungkinan besar akan butuh
  fungsi-fungsi ini juga nanti (untuk membaca nada dengan benar).

### `shared/audio.js` (Tier 1)
- Berbasis **browser `SpeechSynthesis` API** (bukan file rekaman) — alasan: 100% lokal/offline,
  tidak butuh hosting ribuan file, dan satu-satunya cara yang bisa menjangkau kalimat generatif Word Builder.
- `speak(text, opts)` — default `rate: 0.8` (lambat), ada toggle ke kecepatan normal di UI.
- Kalau voice Mandarin tidak tersedia di perangkat: tombol speaker **tetap muncul**,
  baru munculkan toast error saat diklik dan gagal (bukan disembunyikan dari awal).
- Dipasang ke kamus + flashcard + wordbuilder **sekaligus dalam 1 sesi**.

### `shared/srs.js` (Tier 2)
- Read-only, dipakai Word Builder untuk baca status dari `mandarin_srs_v1` & `mandarin_wrong_v1`
  tanpa menyentuh logika tulis milik flashcard.
- `isMastered(hanzi)` → `true` jika `reps >= 3 DAN interval >= 14`
- `isWeak(hanzi)` → `true` jika hanzi ada di array `mandarin_wrong_v1`

---

## 3. Fitur Word Builder baru (Tier 2)

Radio filter tambahan di samping filter HSK yang sudah ada:
- ⭘ Semua kata (default, seperti sekarang)
- ⭘ Hanya kata yang sudah dikuasai
- ⭘ Fokus kata yang sering salah

---

## 4. Roadmap — urutan dependency

| Tier | Item | Halaman terdampak |
|---|---|---|
| **0** | `shared/core.js` (rename $$/$w → $, showToast, escHtml) | kamus, flashcard, wordbuilder |
| **0** | `shared/pinyin.js` | kamus (pindahan) |
| **1** | `shared/audio.js` + tombol speaker | kamus, flashcard, wordbuilder (1 sesi) |
| **1** | Export/Import backup (semua localStorage app jadi 1 file `.json`) | semua halaman |
| **1** | `wb_ref_word` — prefill Word Builder dari flashcard (hapus key setelah dibaca) | wordbuilder |
| **1** | UI koleksi tersimpan `builder_flashcards` — lihat/hapus | wordbuilder |
| **2** | `shared/srs.js` + radio filter Mastered/Weak di Word Builder | wordbuilder |
| **3** | Spot-the-error (pakai `kesalahan_umum` dari `pattern_explanations.json`) | wordbuilder |
| **3** | Modul latihan Tone (minimal pair, dengar-pilih nada) | baru |
| **3** | Modul Stroke order (pakai data `components`/`radical`/`structure`) | baru / kamus |
| **3** | Graded reader generator (bacaan pendek dari kosakata sesuai HSK level) | baru |
| **3** | Kuis pola kalimat (kebalikan Word Builder — tebak pola dari kalimat) | baru |
| **3** | Latihan produksi aktif — recall hanzi dari pinyin/arti (bukan cuma recognition) | flashcard (mode baru) |
| **3** | Eksplorasi kata terkait (sinonim/antonim/tema, dari data yang sudah ada) | kamus |
| **3** | Simulasi ujian HSK bertimer | baru |

Tier 0 & 1 dikerjakan berurutan seperti di atas karena saling bergantung.
Tier 3 boleh dikerjakan dalam urutan apa saja sesuai minat/waktu.

---

## 5. Wishlist — ide masa depan (belum dikomit, sekadar radar)

- Dashboard progres gabungan (lintas SRS + koleksi tersimpan + riwayat kamus)
- Placement test / tes penempatan HSK di awal pemakaian
- Dictation (dengar kalimat → ketik hanzi/pinyin) — logis dikerjakan **setelah** `audio.js` ada
- Sentence mining pribadi (jurnal kalimat favorit dari Word Builder)
- Streak harian & ringkasan mingguan (olah data `due` yang sudah ada, tanpa struktur baru)

Ditolak secara eksplisit (tidak masuk roadmap): mode gelap/terang, cetak/export PDF.

---

## 6. Prinsip kerja (tetap berlaku dari v3/v4)

- Diskusi & sepakat dulu sebelum coding.
- HTML pure struktur, semua data dari `.json`, tidak hardcode di JS.
- File dipecah PART kecil (~300 baris), digabung skrip Python `gabung_*.py` lokal.
- Perubahan kecil-kecil tapi **tidak menyebar** — 1 sesi = 1 tier/item yang jelas cakupannya,
  sesuai roadmap dependency di atas, bukan berdasarkan mood.

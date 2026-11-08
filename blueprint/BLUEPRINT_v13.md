# BLUEPRINT_v13 — Mandarin Interaktif
### Handoff document dari sesi sebelumnya. Upload file ini di awal percakapan baru.

> Cara pakai: رسلان upload file ini ke percakapan baru. Claude membaca semuanya
> dulu sebelum bertanya apa pun — jangan minta رسلان mengulang konteks yang
> sudah ada di sini.

---

## 1. Tentang aplikasi ini

**Mandarin Interaktif** — aplikasi belajar bahasa Mandarin offline, HTML/CSS/JS
murni (tanpa framework/build step), disimpan lokal di **`C:\mandarin_app\`**.
رسلان mengerjakan ini lintas sesi Claude yang berbeda-beda, makanya blueprint
ini penting sebagai jembatan ingatan.

**Prinsip inti yang TIDAK BOLEH dilanggar**: aplikasi ini **offline murni**.
Jangan pernah usulkan fitur yang butuh API key/koneksi internet/AI generatif
online saat aplikasi berjalan. Pengecualian yang SUDAH disepakati: skrip
Python terpisah yang رسلان jalankan manual sekali di lokal untuk MENYIAPKAN
data (misal unduh dataset publik dari GitHub) itu boleh — itu bukan bagian
dari aplikasi yang berjalan, hasilnya jadi file JSON statis yang lalu dipakai
offline seperti biasa. Lihat §2.5 untuk contoh nyata (etimologi karakter).

**Halaman yang sudah ada** (semua saling terhubung lewat navbar, 9 halaman
total — TIDAK ada halaman baru sesi ini juga, sesi ini murni kerja data,
lihat §2.5): `index.html`, `kamus.html` (modular, folder `kamus/`),
`flashcard.html`, `wordbuilder.html`, `tone.html`, `graded-reader.html`,
`hsk-exam.html`, `tatabahasa.html`, `terjemah-bebas.html`. Detail arsitektur
tiap halaman TIDAK BERUBAH dari BLUEPRINT_v12 — lihat file itu kalau perlu
detail lengkap tiap halaman (tidak diulang di sini supaya ringkas, karena
sesi ini fokus 100% di §2.5 saja, tidak menyentuh kode aplikasi sama sekali).

**File bersama & data utama**: TIDAK BERUBAH dari BLUEPRINT_v12, KECUALI
`data/char_etymology_id.json` yang terus bertambah isinya (lihat §2.5).

---

## 2. Apa yang sudah dikerjakan (kronologis, sesi ini)

Sesi ini **murni melanjutkan batch penerjemahan etimologi karakter** — tidak
ada perubahan kode aplikasi sama sekali (halaman, `shared/`, dll semua persis
seperti BLUEPRINT_v12).

### 2.5 Data etimologi karakter (char_etymology_id.json) — BATCH 5-11 SELESAI, LANJUT BATCH 12

**Konteks & alur kerja**: TIDAK BERUBAH dari BLUEPRINT_v12 §2.5 — baca
dokumen itu kalau perlu latar belakang lengkap (kenapa fitur ini ada, sumber
data Make Me a Hanzi, dll). Ringkasan cepat: peta `karakter → {gloss_id,
asal_usul_id}` dipakai fitur mnemonic "Bantu Ingat" di Kamus, dibangun
bertahap ~130 karakter per batch, urut berdasarkan frekuensi kemunculan
karakter di `app_words.json` (kata 2+ karakter saja).

**KOREKSI PENTING ditemukan sesi ini** (dari BLUEPRINT_v12 §1 yang menyebut
"3.034 karakter" sebagai penyebut target): angka itu adalah jumlah TOTAL
entri di `character_etymology_en.json` (file mentah dari Make Me a Hanzi,
sudah difilter ke karakter yang match `app_words.json`). Tapi tidak semua
3.034 karakter itu benar-benar muncul di kata 2+ karakter — dihitung ulang
sesi ini pakai kode Python langsung:
- Karakter unik yang benar-benar dipakai di kata 2+ karakter `app_words.json`:
  **2.840**
- Dari situ yang punya data etimologi tersedia (bukan `null`): **2.653** ←
  **INI angka penyebut yang benar untuk target progres**, bukan 3.034.
- Sisanya (~187 karakter) memang dipakai di app tapi tidak ada data
  etimologi di sumber Make Me a Hanzi sama sekali (karakter langka/jarang
  didokumentasikan) — akan tetap kosong terus kecuali رسلان suatu saat minta
  dicarikan sumber tambahan.

**Progres per batch** (batas peringkat frekuensi kumulatif — dipakai fungsi
`freq.most_common(N)` lalu filter yang belum ada di `done` dan yang punya
etimologi; N dinaikkan tiap batch sampai kandidat baru ≥130):

| Batch | Cutoff `most_common(N)` | Karakter baru | Total kumulatif |
|---|---|---|---|
| 1-4 (sesi lalu) | s.d. ~1000 | 518 | 518 |
| 5 | 1300 | 130 | 648 |
| 6 | 1600 | 130 | 778 |
| 7 | 1900 | 130 | 908 |
| 8 | 2300 | 130 | 1.038 |
| 9 | 2700 | 130 | 1.168 |
| 10 | 3100 | 130 | 1.298 |
| 11 | 3600 | 130 | **1.428** |

**Progres saat ini: 1.428 dari 2.653 karakter (~54%). Sisa: 1.225 karakter
≈ 9-10 batch lagi (130/batch) untuk selesai total.**

**Kode Python pola yang dipakai tiap batch** (jalankan dulu untuk cek berapa
kandidat tersedia di cutoff tertentu — kalau kurang dari 130, naikkan N
sampai cukup; tidak ada rumus pasti kenaikan N per batch, tergantung densitas
karakter langka di rentang itu):
```python
import json
from collections import Counter
words = json.load(open('app_words.json', encoding='utf-8'))
etym = json.load(open('character_etymology_en.json', encoding='utf-8'))
done = json.load(open('char_etymology_id.json', encoding='utf-8'))  # akumulasi semua batch sebelumnya

freq = Counter()
for w in words:
    s = w.get('simplified','') or w.get('id','')
    if len(s) >= 2:
        for c in s:
            freq[c] += 1

ranked = [c for c, _ in freq.most_common(4000)]  # naikkan sampai kandidat cukup 130
candidates = [c for c in ranked if c not in done and etym.get(c, {}).get('etymology')]
batch12 = candidates[:130]
```

**Verifikasi WAJIB tiap batch** (pola sama seperti sebelumnya, TERBUKTI
menangkap kesalahan — jangan dilewati):
```python
expected = set(candidates[:130])
got = set(batch_baru.keys())
assert expected == got  # tidak kurang/lebih dari kandidat
assert not (got & set(done.keys()))  # tidak tumpang tindih batch lama
assert all(v.get('gloss_id','').strip() for v in batch_baru.values())
assert all(v.get('asal_usul_id','').strip() for v in batch_baru.values())
```

**Alur kerja praktis per batch** (efisiensi token — didiskusikan & disepakati
sesi ini): Claude TIDAK menulis ulang seluruh akumulasi tiap batch. Yang
ditulis di respons chat cuma 130 karakter BARU. Penggabungan
`done.update(batch_baru)` dilakukan lewat kode Python di sandbox (bash tool),
bukan diketik ulang — hasil gabungan (file JSON lengkap) langsung disimpan
ke disk dan dikirim sebagai file download. رسلان cukup timpa file lokal
`data/char_etymology_id.json` dengan file yang dikirim tiap batch.

**Progres batch selanjutnya (BATCH 12) belum dimulai** — sesi berikutnya
lanjut dari sini. رسلان sudah bilang mau lanjut terus sampai tuntas (2.653
karakter), tidak ada target berhenti selain "selesai total".

**Catatan kualitas & lisensi**: TIDAK BERUBAH dari BLUEPRINT_v12 §2.5 —
`gloss_id` diambil dari makna inti (bukan makna langka `meanings_id[0]`),
`asal_usul_id` kondensasi dari `hint`/`semantic`/`phonetic` sumber Inggris,
kualitas "kurang akurat asal membantu" sudah diterima رسلان. Lisensi Make Me
a Hanzi masih perlu dicek ulang رسلان kalau suatu saat mau membagikan app ke
orang lain (belum masalah untuk pemakaian offline pribadi).

---

## 3. TODO — urutan prioritas yang disarankan

1. **[PALING PRIORITAS] Lanjutkan batch penerjemahan etimologi karakter**
   (§2.5) — **BATCH 12**, cutoff mulai dari `most_common(4000)` atau lebih
   (cek dulu jumlah kandidat tersedia, naikkan N kalau <130). رسلان sudah
   eksplisit minta lanjut sampai tuntas (2.653 karakter, bukan 3.034 — lihat
   koreksi di §2.5). Kalau رسلان buka sesi baru dan belum bilang topik lain,
   ini yang paling mungkin jadi kelanjutan otomatis — tapi tetap TANYA dulu
   ke رسلان, jangan asumsi.
2. **File yang WAJIB diminta رسلان upload di awal sesi baru** (Claude tidak
   otomatis punya ini): `character_etymology_en.json` (data mentah Inggris)
   dan `char_etymology_id.json` (akumulasi hasil batch 1-11 = 1.428 entri,
   file terakhir yang dikirim sesi ini). `app_words.json` juga dibutuhkan
   untuk hitung frekuensi karakter kalau belum ada di percakapan.
3. **Statistik Latihan Nada di Dashboard** — masih BELUM dikerjakan (lihat
   BLUEPRINT_v12 §1 poin 5 dan §3 TODO lama), cuma dikerjakan kalau رسلان
   eksplisit minta.
4. Kalau رسلان temukan celah baru pas pakai app (bug, UX kurang pas, dll)
   — prioritas selalu boleh disisipkan di atas semua ini, seperti biasa.

**Item lama dari blueprint sebelumnya yang statusnya TIDAK BERUBAH**:
- Hapus folder `hanyu_extract`/`mandarin_kamus` — masih DITUNDA sengaja
  رسلان, jangan diusulkan sampai رسلان sendiri angkat topik ini.
- OCR kamera fisik & widget kaca pembesar — masih DI-DROP.

---

## 4. Hal teknis tambahan

Semua konvensi dari BLUEPRINT_v12 §4 **masih berlaku sepenuhnya** (diskusi
dulu sebelum coding scope besar, `node --check` utk JS, verifikasi tag
seimbang, Bahasa Indonesia, رسلان tidak punya akses filesystem langsung, dll).

**Tambahan baru sesi ini**:
- **Pola efisiensi token untuk kerja data batch** (§2.5): jangan tulis ulang
  akumulasi lama di respons chat, cukup tulis delta batch baru + gabungkan
  lewat kode di sandbox, kirim hasil gabungan sebagai file. Ini sudah
  terbukti efisien dan disetujui رسلان — pakai terus pola ini utk batch 12
  dst, dan pola serupa cocok dipakai lagi kalau ada kerja data bertahap lain
  di masa depan (bukan cuma untuk etimologi karakter).
- **Selalu hitung ulang angka penyebut/target secara terprogram** daripada
  percaya angka dari blueprint lama begitu saja — koreksi 3.034→2.653 di
  §2.5 ditemukan justru karena dihitung ulang, bukan diasumsikan.

---

## 5. Ringkasan file yang berubah/baru sesi ini

| File | Status | Catatan |
|---|---|---|
| `data/char_etymology_id.json` | **Diperbarui** | 518→1.428 dari 2.653 karakter (~54%), batch 5-11 selesai, lanjut batch 12 |
| Semua file lain | Tidak berubah | Sesi ini murni kerja data, tidak menyentuh kode aplikasi sama sekali |

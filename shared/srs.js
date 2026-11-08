/* ═══════════════════════════════════════════════════════════════
   shared/srs.js — Mandarin Interaktif (Tier 2)
   Read-only reader status SRS, dipakai Word Builder untuk filter
   "Sudah Dikuasai" / "Sering Salah" TANPA menyentuh logika tulis
   milik flashcard.html (SRS engine asli ada di flashcard PART 3).

   Sumber data (dibaca apa adanya, tidak pernah ditulis dari sini):
     - mandarin_srs_v1   -> { [key]: { interval, ease, due, reps, lapses } }
     - mandarin_wrong_v1 -> [ key, key, ... ]

   CATATAN PENTING soal key pencocokan:
   flashcard.html menyimpan SRS/wrong pakai key `w.id || w.simplified`
   dari app_words.json. WORD_POOLS di Word Builder (wb_pools.json) TIDAK
   membawa field `id` asli itu (field `id` di sana artinya "arti
   Indonesia", beda arti) -- yang tersisa cuma `cn` (hanzi/simplified).
   Modul ini karena itu mencocokkan berdasarkan HANZI (`cn`), bukan `id`
   app_words.json asli. Untuk kata yang tidak punya `id` unik di
   app_words.json (mayoritas, fallback ke simplified), ini cocok
   sempurna. Untuk kata langka yang kebetulan punya `id` berbeda dari
   hanzinya, pencocokan bisa meleset -- keterbatasan yang diketahui,
   bukan bug tersembunyi.

   WAJIB dimuat setelah shared/core.js, sebelum script utama halaman.
═══════════════════════════════════════════════════════════════ */

const SRSReader = {
  STORAGE_KEY: 'mandarin_srs_v1',
  WRONG_KEY:   'mandarin_wrong_v1',
  MASTER_MIN_REPS:     3,
  MASTER_MIN_INTERVAL: 14,

  data:     {},   // cache di-refresh tiap kali srsReaderRefresh() dipanggil
  wrongSet: new Set(),
};

/* ── MUAT ULANG DARI localStorage ──────────────────────────────
   Dipanggil sekali saat halaman load, dan boleh dipanggil ulang
   kapan saja (mis. setelah modal/tab lain kemungkinan mengubah data). */
function srsReaderRefresh() {
  try {
    SRSReader.data = JSON.parse(localStorage.getItem(SRSReader.STORAGE_KEY) || '{}');
  } catch (e) {
    console.error('srs.js: gagal membaca mandarin_srs_v1', e);
    SRSReader.data = {};
  }

  try {
    const arr = JSON.parse(localStorage.getItem(SRSReader.WRONG_KEY) || '[]');
    SRSReader.wrongSet = new Set(Array.isArray(arr) ? arr : []);
  } catch (e) {
    console.error('srs.js: gagal membaca mandarin_wrong_v1', e);
    SRSReader.wrongSet = new Set();
  }
}

/* ── isMastered(hanzi) ──────────────────────────────────────────
   true kalau reps >= 3 DAN interval >= 14 (sesuai BLUEPRINT_v5 §2) */
function isMastered(hanzi) {
  const card = SRSReader.data[hanzi];
  if (!card) return false;
  return (card.reps || 0) >= SRSReader.MASTER_MIN_REPS
      && (card.interval || 0) >= SRSReader.MASTER_MIN_INTERVAL;
}

/* ── isWeak(hanzi) ──────────────────────────────────────────────
   true kalau hanzi ada di array mandarin_wrong_v1 */
function isWeak(hanzi) {
  return SRSReader.wrongSet.has(hanzi);
}

srsReaderRefresh(); // muat sekali saat file di-load

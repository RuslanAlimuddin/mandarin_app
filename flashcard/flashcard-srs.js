/* ═══════════════════════════════════════════════════════════════
   flashcard-srs.js — Mesin SRS (SM-2 disederhanakan)
   Storage key: mandarin_srs_v1
   Format per kata: { interval, ease, due, reps, lapses }
═══════════════════════════════════════════════════════════════ */
'use strict';

/* ── KONSTANTA SRS ─────────────────────────────────────────── */
const SRS = {
  STORAGE_KEY:  'mandarin_srs_v1',
  WRONG_KEY:    'mandarin_wrong_v1',  // set kata yang pernah salah
  EASE_DEFAULT: 2.5,
  EASE_MIN:     1.3,
  EASE_BONUS:   0.15,   // mudah
  EASE_PENALTY: 0.20,   // sulit
  EASE_HARD:    0.15,   // lagi (lebih besar)

  // Interval (hari) per rating, untuk kartu BARU (reps === 0)
  NEW_INTERVALS: [1, 3, 7, 14],

  // Interval minimum untuk kartu review
  MIN_INTERVAL: 1,
};

/* ── BACA / TULIS SRS DATA ─────────────────────────────────── */
function srsLoad() {
  try {
    return JSON.parse(localStorage.getItem(SRS.STORAGE_KEY) || '{}');
  } catch { return {}; }
}

function srsSave(data) {
  try {
    localStorage.setItem(SRS.STORAGE_KEY, JSON.stringify(data));
  } catch (e) {
    console.warn('SRS: gagal menyimpan', e);
  }
}

function wrongLoad() {
  try {
    return new Set(JSON.parse(localStorage.getItem(SRS.WRONG_KEY) || '[]'));
  } catch { return new Set(); }
}

function wrongSave(set) {
  try {
    localStorage.setItem(SRS.WRONG_KEY, JSON.stringify([...set]));
  } catch {}
}

/* ── UTILITAS TANGGAL ──────────────────────────────────────── */
function today() {
  return new Date().toISOString().slice(0, 10);
}

function addDays(dateStr, n) {
  const d = new Date(dateStr);
  d.setDate(d.getDate() + n);
  return d.toISOString().slice(0, 10);
}

function isDue(dateStr) {
  return dateStr <= today();
}

/* ── INISIALISASI KARTU BARU ───────────────────────────────── */
function srsInitCard(wordId, srsData) {
  if (!srsData[wordId]) {
    srsData[wordId] = {
      interval: 0,
      ease:     SRS.EASE_DEFAULT,
      due:      today(),
      reps:     0,
      lapses:   0,
    };
  }
}

/* ── HITUNG INTERVAL BERIKUTNYA ────────────────────────────── */
/**
 * rating: 0=Lagi, 1=Sulit, 2=Baik, 3=Mudah
 * Mengembalikan { interval, ease, due } yang diperbarui
 */
function srsCalculate(card, rating) {
  let { interval, ease, reps, lapses } = card;

  if (rating === 0) {
    // Lagi: reset interval ke 1, turunkan ease, tambah lapses
    lapses   += 1;
    ease      = Math.max(SRS.EASE_MIN, ease - SRS.EASE_HARD);
    interval  = SRS.NEW_INTERVALS[0]; // 1 hari
    reps      = 0; // reset
  } else if (reps === 0) {
    // Kartu baru (pertama kali berhasil)
    interval  = SRS.NEW_INTERVALS[rating];
    reps      = 1;
    if (rating === 1) ease = Math.max(SRS.EASE_MIN, ease - SRS.EASE_PENALTY);
    if (rating === 3) ease = ease + SRS.EASE_BONUS;
  } else {
    // Kartu review
    if (rating === 1) {
      // Sulit: interval × 1.2, ease turun
      interval  = Math.max(SRS.MIN_INTERVAL, Math.round(interval * 1.2));
      ease      = Math.max(SRS.EASE_MIN, ease - SRS.EASE_PENALTY);
    } else if (rating === 2) {
      // Baik: interval × ease
      interval  = Math.max(SRS.MIN_INTERVAL, Math.round(interval * ease));
    } else {
      // Mudah: interval × ease × 1.3, ease naik
      interval  = Math.max(SRS.MIN_INTERVAL, Math.round(interval * ease * 1.3));
      ease      = ease + SRS.EASE_BONUS;
    }
    reps += 1;
  }

  const due = addDays(today(), interval);
  return { interval, ease, due, reps, lapses };
}

/* ── PREVIEW INTERVAL (untuk label tombol) ─────────────────── */
function srsPreviewIntervals(card) {
  const previews = [0, 1, 2, 3].map(r => {
    const next = srsCalculate(card, r);
    return next.interval;
  });
  return previews; // [lagi, sulit, baik, mudah]
}

function formatInterval(days) {
  if (days <= 0)  return 'sekarang';
  if (days === 1) return '1 hari';
  if (days < 7)   return days + ' hari';
  if (days < 30)  return Math.round(days / 7) + ' minggu';
  if (days < 365) return Math.round(days / 30) + ' bulan';
  return Math.round(days / 365) + ' tahun';
}

function shuffle(arr) {
  for (let i = arr.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [arr[i], arr[j]] = [arr[j], arr[i]];
  }
  return arr;
}

/* ── HITUNG DUE COUNT PER DECK ─────────────────────────────── */
function countDueForDeck(deckId, allWords, srsData, bookmarkSet, wrongSet) {
  const queue = buildDeckQueue(deckId, allWords, srsData, bookmarkSet, wrongSet, 9999, 'mastery');
  return queue.length;
}

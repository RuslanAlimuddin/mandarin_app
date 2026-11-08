/* ═══════════════════════════════════════════════════════════════
   flashcard-init.js — Bootstrap: event listener top-level, keyboard
   shortcut, swipe gesture, urutan pemuatan awal.
   WAJIB DIMUAT PALING AKHIR (setelah 5 modul lain).
═══════════════════════════════════════════════════════════════ */
'use strict';

/* ── INIT: muat data awal ──────────────────────────────────── */
document.addEventListener('DOMContentLoaded', () => {
  // loadWords mencakup renderSidebarTema, renderSidebarRadikal, updateAllDueCounts
  loadWords().then(() => {
    // Tambahan setelah data siap: fonetik, struktur, antonyms
    loadPhoneticData();
    renderSidebarStruktur();
    checkAntonymsData();
    checkSynonymsData();
    loadNuanceData(); // Tier 4: deck "Pilih yang Tepat", data/nuance_pairs.json
    loadPolaGameData(); // Tier 4: deck "🧩 Tebak Pola Kata", data/kata_majemuk_pola.json
    loadConfusionData(); // E.0.3: deck "👀 Karakter Mirip", data/confusion_groups.json
    // Pastikan accordion HSK default open
    const hskBody = $('acc-hsk');
    if (hskBody) { hskBody.style.maxHeight = ''; }
  });

  // CATATAN PEMBERSIHAN (modularisasi flashcard.html): di sini DULU ada
  // listener keydown kedua (duplikat dari yg di bawah, tanpa cek
  // FC.isFlipped) -- itu BUG lama: menekan 1/2/3/4 akan memicu rateCard()
  // DUA KALI sekaligus kalau kartu sedang terbalik (dobel proses SRS).
  // Dibuang di sini, listener keydown yang benar (dgn guard isFlipped +
  // shortcut 'h' utk hint) tetap ada di bawah, satu-satunya sekarang.

  // Session mode toggle
  const modeEl = $('ctrl-session-mode');
  if (modeEl) modeEl.addEventListener('change', function() {
    const row = $('ctrl-limit-row');
    if (row) row.style.display = this.value === 'fixed' ? '' : 'none';
  });
});

/* showToast() sekarang dari shared/core.js */

/* ── KEYBOARD SHORTCUTS ────────────────────────────────────── */
document.addEventListener('keydown', (e) => {
  // Abaikan jika sedang mengetik di input
  if (e.target.closest('input, textarea, select')) return;

  switch (e.key) {
    case ' ':
    case 'Enter':
      e.preventDefault();
      if (!FC.isFlipped) showAnswer();
      break;
    case '1':
      if (FC.isFlipped) rateCard(0);
      break;
    case '2':
      if (FC.isFlipped) rateCard(1);
      break;
    case '3':
      if (FC.isFlipped) rateCard(2);
      break;
    case '4':
      if (FC.isFlipped) rateCard(3);
      break;
    case 'h':
    case 'H':
      if (!FC.isFlipped) showHint();
      break;
  }
});

/* ── SWIPE GESTURE (mobile) ────────────────────────────────── */
(function setupSwipe() {
  let startX = 0, startY = 0;

  document.addEventListener('touchstart', (e) => {
    startX = e.touches[0].clientX;
    startY = e.touches[0].clientY;
  }, { passive: true });

  document.addEventListener('touchend', (e) => {
    const dx = e.changedTouches[0].clientX - startX;
    const dy = e.changedTouches[0].clientY - startY;

    // Hanya proses swipe horizontal (dx > 50, dy kecil)
    if (Math.abs(dx) < 50 || Math.abs(dy) > 60) return;
    if (!FC.isFlipped) return;

    if (dx > 0) {
      // Swipe kanan → Baik (2)
      rateCard(2);
    } else {
      // Swipe kiri → Lagi (0)
      rateCard(0);
    }
  }, { passive: true });
})();

/* ── KLIK KARTU UNTUK FLIP ─────────────────────────────────── */
document.addEventListener('DOMContentLoaded', () => {
  const cardWrap = $('fc-card-wrap');
  if (cardWrap) {
    cardWrap.addEventListener('click', () => {
      if (!FC.isFlipped) showAnswer();
    });
  }
});

/* ── INIT ───────────────────────────────────────────────────── */
document.addEventListener('DOMContentLoaded', () => {
  // Tampilkan screen pilih deck
  showScreen('choose');

  // Mulai muat data, lalu tampilkan lagi deck yang terakhir dipilih
  // (kalau ada) -- TIDAK otomatis mulai sesi, cuma highlight + tombol
  // "Mulai Sesi" siap, supaya tidak mengejutkan رسلان dengan sesi yang
  // tiba-tiba jalan sendiri saat balik dari halaman lain lewat navbar.
  loadWords().then(() => restoreFlashcardLastState());
});

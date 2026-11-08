/* ═══════════════════════════════════════════════════════════════
   wordbuilder-init.js — Bootstrap. WAJIB DIMUAT PALING AKHIR.
═══════════════════════════════════════════════════════════════ */
'use strict';

/* ── INIT ───────────────────────────────────────────────────── */
document.addEventListener('DOMContentLoaded', async () => {
  // Pastikan tab tunggal aktif dulu sebagai default (di-override oleh
  // restoreLastViewState() di bawah kalau ada state tersimpan)
  switchTab('tunggal');

  // Muat preferensi filter HSK dari localStorage (default: semua aktif)
  loadHskFilterFromStorage();
  initHskChips();

  // Muat data kata dari data/wb_pools.json + penjelasan pola dari data/pattern_explanations.json
  await Promise.all([
    loadWordPools(),
    loadPatternExplanations()
  ]);

  // Tampilkan jumlah kalimat tersimpan di badge navbar
  updateCollectionBadge();

  // Kalau datang dari Flashcard (wb_ref_word ada), langsung buka pola +
  // isi slot yang cocok -- prioritas di atas "state terakhir" biasa.
  // Kalau datang dari Tata Bahasa (wb_ref_pattern ada), langsung buka
  // tab + pola yang cocok -- prioritas sama, di bawah Flashcard saja
  // karena kasusnya jauh lebih jarang tabrakan bersamaan.
  // Kalau tidak keduanya, tampilkan pola & tab yang terakhir dilihat
  // (Tier 1: ingat state lintas-halaman lewat navbar).
  const cameFromFlashcard = consumeRefWord();
  if (!cameFromFlashcard) {
    const cameFromTatabahasa = consumeRefPattern();
    if (!cameFromTatabahasa) restoreLastViewState();
  }
});

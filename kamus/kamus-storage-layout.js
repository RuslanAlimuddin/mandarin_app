/* ═══════════════════════════════════════════════════════════════
   kamus/kamus-storage-layout.js — Mandarin Interaktif
   localStorage (bookmark/riwayat), infinite scroll, drag-resize panel & kolom, ingat state terakhir
   Bagian dari modularisasi kamus.html. Dimuat sebagai <script src>
   biasa (bukan ES module) -- semua fungsi tetap di scope global,
   jadi urutan file lain relatif bebas KECUALI kamus-init.js yang
   WAJIB paling akhir.
   ═══════════════════════════════════════════════════════════════ */

'use strict';

/* ── STORAGE (localStorage) ────────────────────────────────── */
function loadStorageData() {
  try {
    const bm = localStorage.getItem('mandarin_bookmarks');
    if (bm) STATE.bookmarks = new Set(JSON.parse(bm));

    const rw = localStorage.getItem('mandarin_recent');
    if (rw) STATE.recentWords = JSON.parse(rw);

    $('cnt-bookmarks').textContent = STATE.bookmarks.size;
    $('cnt-recent').textContent    = Math.min(STATE.recentWords.length, 50);
  } catch (e) { /* ignore */ }
}

function saveBookmarks() {
  try {
    localStorage.setItem('mandarin_bookmarks', JSON.stringify([...STATE.bookmarks]));
    $('cnt-bookmarks').textContent = STATE.bookmarks.size;
  } catch (e) { /* ignore */ }
}

function addToRecent(wordId) {
  STATE.recentWords = [wordId, ...STATE.recentWords.filter(x => x !== wordId)].slice(0, 50);
  try {
    localStorage.setItem('mandarin_recent', JSON.stringify(STATE.recentWords));
    $('cnt-recent').textContent = STATE.recentWords.length;
  } catch (e) { /* ignore */ }
}

/* ── INFINITE SCROLL ───────────────────────────────────────── */
function setupInfiniteScroll() {
  const sentinel = $('scroll-sentinel');
  const observer = new IntersectionObserver((entries) => {
    if (entries[0].isIntersecting && STATE.rendered < STATE.results.length) {
      $('load-more-spinner').classList.remove('hidden');
      setTimeout(() => {
        renderResultsBatch();
      }, 80);
    }
  }, { rootMargin: '100px' });
  observer.observe(sentinel);
}

/* ── DRAG HANDLE RESIZABLE PANEL DETAIL (Fix A4) ───────────── */
const PANEL_WIDTH_KEY = 'mandarin_detail_width';
const PANEL_MIN_WIDTH = 280;
const PANEL_MAX_WIDTH = 600;

function applyDetailPanelWidth(px) {
  const panel = $('detail-panel');
  if (!panel) return;
  const clamped = Math.min(PANEL_MAX_WIDTH, Math.max(PANEL_MIN_WIDTH, px));
  panel.style.width = clamped + 'px';
  panel.style.flex = `0 0 ${clamped}px`;
  return clamped;
}

/* ── LEBAR KOLOM HANZI BISA DI-DRAG (Fix: kartu hasil) ─────────────
   Pola sama dengan setupResizeHandle() (panel detail) di atas, bedanya
   di sini handle-nya banyak (satu per kartu hasil, dibuat dinamis lewat
   buildResultCard()), jadi pakai event delegation di #cards-container
   supaya tidak perlu daftar ulang listener tiap kartu baru dirender. */
const HANZI_COL_WIDTH_KEY = 'mandarin_kamus_hanzi_col_w';

function applyHanziColWidth(px) {
  const clamped = Math.min(220, Math.max(50, px));
  document.documentElement.style.setProperty('--hanzi-col-w', clamped + 'px');
  return clamped;
}

function setupHanziColResize() {
  const container = $('cards-container');
  if (!container) return;

  // Terapkan lebar tersimpan dari sesi sebelumnya
  try {
    const saved = parseInt(localStorage.getItem(HANZI_COL_WIDTH_KEY), 10);
    if (saved) applyHanziColWidth(saved);
  } catch (e) { /* ignore */ }

  let dragging  = false;
  let activeHandle = null;

  container.addEventListener('mousedown', (e) => {
    const handle = e.target.closest('.hanzi-col-resize-handle');
    if (!handle) return;
    dragging = true;
    activeHandle = handle;
    handle.classList.add('dragging');
    document.body.style.userSelect = 'none';
    e.preventDefault();
  });

  document.addEventListener('mousemove', (e) => {
    if (!dragging) return;
    const cardRect = activeHandle.closest('.result-card').getBoundingClientRect();
    const newWidth = e.clientX - cardRect.left - 14; // 14px = padding kiri kartu
    applyHanziColWidth(newWidth);
  });

  document.addEventListener('mouseup', () => {
    if (!dragging) return;
    dragging = false;
    activeHandle.classList.remove('dragging');
    activeHandle = null;
    document.body.style.userSelect = '';
    try {
      const current = getComputedStyle(document.documentElement).getPropertyValue('--hanzi-col-w');
      localStorage.setItem(HANZI_COL_WIDTH_KEY, parseInt(current, 10));
    } catch (e) { /* ignore */ }
  });

  // Dukungan sentuh (HP/tablet)
  container.addEventListener('touchstart', (e) => {
    const handle = e.target.closest('.hanzi-col-resize-handle');
    if (!handle) return;
    dragging = true;
    activeHandle = handle;
    handle.classList.add('dragging');
  }, { passive: true });

  document.addEventListener('touchmove', (e) => {
    if (!dragging) return;
    const touch = e.touches[0];
    const cardRect = activeHandle.closest('.result-card').getBoundingClientRect();
    const newWidth = touch.clientX - cardRect.left - 14;
    applyHanziColWidth(newWidth);
    e.preventDefault();
  }, { passive: false });

  document.addEventListener('touchend', () => {
    if (!dragging) return;
    dragging = false;
    activeHandle.classList.remove('dragging');
    activeHandle = null;
    try {
      const current = getComputedStyle(document.documentElement).getPropertyValue('--hanzi-col-w');
      localStorage.setItem(HANZI_COL_WIDTH_KEY, parseInt(current, 10));
    } catch (e) { /* ignore */ }
  });
}

function setupResizeHandle() {
  const handle = $('resize-handle');
  const panel  = $('detail-panel');
  if (!handle || !panel) return;

  // Terapkan lebar tersimpan dari sesi sebelumnya
  try {
    const saved = parseInt(localStorage.getItem(PANEL_WIDTH_KEY), 10);
    if (saved) applyDetailPanelWidth(saved);
  } catch (e) { /* ignore */ }

  let dragging = false;

  handle.addEventListener('mousedown', (e) => {
    dragging = true;
    handle.classList.add('dragging');
    document.body.style.userSelect = 'none';
    e.preventDefault();
  });

  document.addEventListener('mousemove', (e) => {
    if (!dragging) return;
    const layoutRect = document.querySelector('.app-layout').getBoundingClientRect();
    const newWidth = layoutRect.right - e.clientX;
    applyDetailPanelWidth(newWidth);
  });

  document.addEventListener('mouseup', () => {
    if (!dragging) return;
    dragging = false;
    handle.classList.remove('dragging');
    document.body.style.userSelect = '';
    try {
      const currentWidth = panel.getBoundingClientRect().width;
      localStorage.setItem(PANEL_WIDTH_KEY, Math.round(currentWidth));
    } catch (e) { /* ignore */ }
  });
}

/* ── INGAT STATE TERAKHIR (Tier 1 lintas-halaman) ──────────────────
   Setiap kali pencarian/filter/kata dipilih berubah, disimpan ke
   localStorage supaya kalau رسلان pindah ke halaman lain lewat navbar
   lalu balik lagi, Kamus menampilkan pencarian & kata yang terakhir
   dilihat -- bukan mulai dari layar kosong. */
const KAMUS_LAST_STATE_KEY = 'mandarin_kamus_last_state_v1';

function saveKamusLastState() {
  try {
    localStorage.setItem(KAMUS_LAST_STATE_KEY, JSON.stringify({
      query:         STATE.query,
      searchMode:    STATE.searchMode,
      sidebarFilter: STATE.sidebarFilter,
      source:        STATE.source,
      selectedId:    STATE.selectedId,
    }));
  } catch (e) { /* abaikan senyap -- bukan fitur kritis */ }
}

function restoreKamusLastState() {
  let saved;
  try {
    saved = JSON.parse(localStorage.getItem(KAMUS_LAST_STATE_KEY) || 'null');
  } catch (e) { return; }
  if (!saved) return;

  const proceed = () => {
    // Mode pencarian (pill Auto/Hanzi/Pinyin/dst) — cukup set state + UI,
    // doSearch sungguhan dipanggil di bawah supaya tidak search 2x.
    if (saved.searchMode) {
      STATE.searchMode = saved.searchMode;
      document.querySelectorAll('.pill').forEach(p => {
        p.classList.toggle('active', p.dataset.mode === saved.searchMode);
      });
    }

    // Filter Koleksi/Terakhir Dilihat: pakai fungsi aslinya supaya
    // tampilan showCollection() ikut benar, lalu berhenti di sini (tidak
    // ada "query" pencarian teks yang relevan untuk direstorasi).
    if (saved.sidebarFilter === 'bookmarks' || saved.sidebarFilter === 'recent') {
      setSidebarFilter(saved.sidebarFilter);
      return;
    }

    if (saved.query) {
      $('search-input').value = saved.query;
      $('search-clear').classList.add('visible');
      doSearch(saved.query);
      if (saved.selectedId) {
        // Beri waktu render kartu hasil dulu sebelum pilih detail kata
        setTimeout(() => selectWord(saved.selectedId), 60);
      }
    }
  };

  if (saved.source === 'cidict') {
    STATE.source = 'cidict';
    $('src-hsk').classList.remove('active');
    $('src-cidict').classList.add('active');
    loadCidict().then(proceed);
  } else {
    proceed();
  }
}


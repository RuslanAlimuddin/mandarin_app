/* ═══════════════════════════════════════════════════════════════
   kamus/kamus-search.js — Mandarin Interaktif
   Mesin pencarian (hanzi/pinyin/arti), render kartu hasil, mode tabel
   Bagian dari modularisasi kamus.html. Dimuat sebagai <script src>
   biasa (bukan ES module) -- semua fungsi tetap di scope global,
   jadi urutan file lain relatif bebas KECUALI kamus-init.js yang
   WAJIB paling akhir.
   ═══════════════════════════════════════════════════════════════ */

'use strict';

/* ── SEARCH ENGINE ─────────────────────────────────────────── */
function doSearch(rawQuery) {
  // Guard: data belum siap
  if (!STATE.dataHsk || !Array.isArray(STATE.dataHsk)) {
    showToast('Data masih dimuat, tunggu sebentar…');
    return;
  }

  const query = rawQuery.trim();
  STATE.query = query;

  if (!query) {
    clearResults();
    showLanding(true);
    return;
  }

  showLanding(false);
  $('results-header').style.display = 'none';

  const mode = detectMode(query);
  updateModeBadge(mode);

  // Pilih dataset
  const data = (STATE.source === 'cidict' && STATE.dataCidict)
    ? STATE.dataCidict
    : (STATE.dataHsk || []);

  let results = [];

  if (mode === 'hanzi') {
    results = searchHanzi(data, query);
    // Fallback otomatis ke CC-CIDICT kalau kamus utama tidak menemukan apa-apa
    // (disepakati رسلان: hanzi saja, bukan pinyin/arti — itu sudah ada fallback-nya sendiri di bawah)
    if (results.length === 0 && STATE.source === 'hsk') {
      if (STATE.dataCidict) {
        const fallbackResults = searchHanzi(STATE.dataCidict, query)
          .map(w => ({ ...w, _cidictFallback: true }));
        if (fallbackResults.length) {
          results = fallbackResults;
          showToast('Tidak ditemukan di kamus utama — menampilkan hasil dari CC-CIDICT');
        }
      } else {
        loadCidict().then(() => {
          // Guard: batalkan kalau query sudah berubah selagi loading (رسلان lanjut mengetik)
          if ($('search-input').value.trim() !== query) return;
          doSearch(query);
        });
      }
    }
  } else if (mode === 'pinyin') {
    results = searchPinyin(data, query);
  } else if (mode === 'en') {
    results = searchMeanings(data, query, 'en');
  } else {
    // 'id' atau 'auto' fallback ke Indonesia
    results = searchMeanings(data, query, 'id');
    // Jika kurang dari 5 dan pakai HSK, coba cidict
    if (results.length < 5 && STATE.source === 'hsk' && STATE.dataCidict) {
      const extra = searchMeanings(STATE.dataCidict, query, 'id')
        .filter(c => !results.find(h => h.id === c.id))
        .map(w => ({ ...w, _cidictFallback: true }));
      results = [...results, ...extra];
    }
  }

  // Terapkan filter sidebar
  results = applySidebarFilter(results);

  // Sort: relevansi (exact match dulu) → frekuensi → HSK
  results = sortResults(results, query, mode);

  STATE.results  = results;
  STATE.rendered = 0;

  renderResultsBatch();
  updateResultsHeader(results.length);
  saveKamusLastState();
}

function searchHanzi(data, query) {
  return data.filter(w => {
    const s = w.simplified || w.id || '';
    const t = w.traditional || '';
    return s === query || t === query ||
           s.includes(query) || t.includes(query);
  });
}

function searchPinyin(data, query) {
  const qLower = query.toLowerCase().trim();
  const hasNumericTone   = /\d/.test(qLower);
  const hasDiacriticTone = /[āáǎàēéěèīíǐìōóǒòūúǔùǖǘǚǜü]/.test(qLower);
  const hasTone = hasNumericTone || hasDiacriticTone;

  if (hasTone) {
    // Mode presisi: user mengetik nada eksplisit → HARUS exact match nada,
    // TIDAK boleh fallback ke pencarian longgar (Fix A1).
    const qDiacritic = (hasNumericTone ? numericToDiacritic(qLower) : qLower)
      .replace(/\s+/g, '');
    return data.filter(w => {
      const pyDiacritic = (w.pinyin || '').toLowerCase().replace(/\s+/g, '');
      return pyDiacritic === qDiacritic ||
             pyDiacritic.startsWith(qDiacritic) ||
             pyDiacritic.includes(qDiacritic);
    });
  }

  // Mode longgar: query benar-benar tanpa nada → cocokkan semua nada
  const qLoose = normalizePinyin(qLower).replace(/\s+/g, '');
  return data.filter(w => {
    const pyRaw      = (w.pinyin || '').toLowerCase();
    const pyLoose    = normalizePinyin(pyRaw).replace(/\s+/g, '');
    const pyNumLoose = (w.pinyin_numeric || '').toLowerCase().replace(/\d/g, '').replace(/\s+/g, '');
    return pyLoose === qLoose || pyLoose.startsWith(qLoose) || pyLoose.includes(qLoose) ||
           pyNumLoose === qLoose || pyNumLoose.startsWith(qLoose) || pyNumLoose.includes(qLoose);
  });
}

function searchMeanings(data, query, lang) {
  const q = query.toLowerCase();
  const field = lang === 'en' ? 'meanings_en' : 'meanings_id';
  return data.filter(w => {
    const meanings = w[field];
    if (!meanings) return false;
    if (Array.isArray(meanings)) {
      return meanings.some(m => m && m.toLowerCase().includes(q));
    }
    return String(meanings).toLowerCase().includes(q);
  });
}

function applySidebarFilter(results) {
  const f = STATE.sidebarFilter;
  if (f === 'all') return results;
  if (f.startsWith('hsk-')) {
    const level = f.replace('hsk-', '');
    const targetLevel = level === '7' ? [7, 8, 9] : [parseInt(level)];
    return results.filter(w => targetLevel.includes(parseInt(w.hsk)));
  }
  if (f === 'bookmarks') {
    return results.filter(w => STATE.bookmarks.has(w.id || w.simplified));
  }
  if (f === 'recent') {
    const set = new Set(STATE.recentWords);
    return results.filter(w => set.has(w.id || w.simplified));
  }
  return results;
}

function sortResults(results, query, mode) {
  const q = query.toLowerCase();
  return results.slice().sort((a, b) => {
    // 1. Exact match dulu
    const aId = (a.id || a.simplified || '').toLowerCase();
    const bId = (b.id || b.simplified || '').toLowerCase();
    const aExact = aId === q ? 1 : 0;
    const bExact = bId === q ? 1 : 0;
    if (bExact !== aExact) return bExact - aExact;

    // 2. Starts with
    const aSw = aId.startsWith(q) ? 1 : 0;
    const bSw = bId.startsWith(q) ? 1 : 0;
    if (bSw !== aSw) return bSw - aSw;

    // 3. HSK level (lebih rendah lebih mudah → tampilkan dulu)
    const aHsk = parseInt(a.hsk) || 99;
    const bHsk = parseInt(b.hsk) || 99;
    if (aHsk !== bHsk) return aHsk - bHsk;

    // 4. Frekuensi (lebih tinggi → lebih umum)
    const aFreq = a.frequency || 0;
    const bFreq = b.frequency || 0;
    return bFreq - aFreq;
  });
}

/* ── RENDER KARTU ──────────────────────────────────────────── */
function getCardSortedResults() {
  const key = STATE.cardSortKey;
  if (!key) return STATE.results; // default: urutan relevansi dari sortResults()
  const dir = STATE.cardSortDir;
  return STATE.results.slice().sort((a, b) => {
    let av, bv;
    if (key === 'simplified') { av = a.simplified || a.id || ''; bv = b.simplified || b.id || ''; }
    else if (key === 'pinyin') { av = a.pinyin || ''; bv = b.pinyin || ''; }
    else if (key === 'meaning') {
      av = Array.isArray(a.meanings_id) ? (a.meanings_id[0] || '') : (a.meanings_id || '');
      bv = Array.isArray(b.meanings_id) ? (b.meanings_id[0] || '') : (b.meanings_id || '');
    } else if (key === 'hsk') { av = parseInt(a.hsk) || 99; bv = parseInt(b.hsk) || 99; }
    else { av = a[key]; bv = b[key]; }

    if (typeof av === 'string' || typeof bv === 'string') {
      av = (av || '').toString().toLowerCase();
      bv = (bv || '').toString().toLowerCase();
      return av < bv ? -1 * dir : av > bv ? 1 * dir : 0;
    }
    av = av || 0; bv = bv || 0;
    return (av - bv) * dir;
  });
}

function setCardSort(key) {
  if (STATE.cardSortKey === key) {
    STATE.cardSortDir *= -1;
  } else {
    STATE.cardSortKey = key;
    STATE.cardSortDir = 1;
  }
  STATE.rendered = 0;
  renderResultsBatch();
  updateResultsHeader(STATE.results.length); // refresh tombol aktif
}

function renderResultsBatch() {
  if (STATE.viewMode === 'table') {
    renderResultsTable();
    return;
  }

  const container = $('cards-container');
  if (!container) return; // guard: DOM belum siap
  const items = getCardSortedResults();
  const start = STATE.rendered;
  const end   = Math.min(start + STATE.PAGE_SIZE, items.length);

  if (start === 0) container.innerHTML = '';

  const frag = document.createDocumentFragment();

  for (let i = start; i < end; i++) {
    const word = items[i];
    const el = buildResultCard(word, i);
    frag.appendChild(el);
  }

  container.appendChild(frag);
  STATE.rendered = end;

  $('empty-state').classList.add('hidden');
  $('load-more-spinner').classList.add('hidden');

  if (items.length === 0) {
    $('empty-state').classList.remove('hidden');
    const emMsg = $('empty-message');
    if (emMsg) emMsg.textContent = `Tidak ada hasil untuk "${STATE.query}".`;
  }
}

/* ── MODE TABEL (Fix #5) ──────────────────────────────────── */
function toggleView(mode) {
  STATE.viewMode = mode;
  document.querySelectorAll('.view-toggle-btn').forEach(b => {
    b.classList.toggle('active', b.dataset.view === mode);
  });
  STATE.rendered = 0;
  renderResultsBatch();
  updateResultsHeader(STATE.results.length);
}

function sortResultsByColumn(key) {
  if (STATE.tableSortKey === key) {
    STATE.tableSortDir *= -1;
  } else {
    STATE.tableSortKey = key;
    STATE.tableSortDir = 1;
  }
  renderResultsTable();
}

function renderResultsTable() {
  const container = $('cards-container');
  if (!container) return;

  const items = STATE.results.slice();
  const key   = STATE.tableSortKey;
  const dir   = STATE.tableSortDir;

  if (key) {
    items.sort((a, b) => {
      let av = a[key], bv = b[key];
      if (key === 'simplified') { av = a.simplified || a.id || ''; bv = b.simplified || b.id || ''; }
      if (key === 'meaning') {
        av = Array.isArray(a.meanings_id) ? (a.meanings_id[0] || '') : (a.meanings_id || '');
        bv = Array.isArray(b.meanings_id) ? (b.meanings_id[0] || '') : (b.meanings_id || '');
      }
      if (typeof av === 'string' || typeof bv === 'string') {
        av = (av || '').toString().toLowerCase();
        bv = (bv || '').toString().toLowerCase();
        return av < bv ? -1 * dir : av > bv ? 1 * dir : 0;
      }
      av = av || 0; bv = bv || 0;
      return (av - bv) * dir;
    });
  }

  const arrow = (k) => STATE.tableSortKey === k ? (STATE.tableSortDir === 1 ? ' ▲' : ' ▼') : ' ↕';

  let html = `<table class="results-table">
    <thead><tr>
      <th onclick="sortResultsByColumn('simplified')">Hanzi${arrow('simplified')}</th>
      <th onclick="sortResultsByColumn('pinyin')">Pinyin${arrow('pinyin')}</th>
      <th onclick="sortResultsByColumn('hsk')">HSK${arrow('hsk')}</th>
      <th onclick="sortResultsByColumn('stroke_count')">Goresan${arrow('stroke_count')}</th>
      <th onclick="sortResultsByColumn('frequency')">Frekuensi${arrow('frequency')}</th>
      <th onclick="sortResultsByColumn('meaning')">Arti${arrow('meaning')}</th>
    </tr></thead>
    <tbody>`;

  items.slice(0, 200).forEach(w => {
    const id = w.id || w.simplified || '';
    const firstMeaning = Array.isArray(w.meanings_id) ? (w.meanings_id[0] || '') : (w.meanings_id || '');
    html += `<tr onclick="selectWord('${escHtml(id).replace(/'/g, "\\'")}', 0)">
      <td class="table-hanzi">${escHtml(w.simplified || id)}</td>
      <td>${escHtml(w.pinyin || '')}</td>
      <td>${w.hsk ? hskLabel(w.hsk) : '—'}</td>
      <td>${w.stroke_count || '—'}</td>
      <td>${w.frequency ? '#' + w.frequency : '—'}</td>
      <td class="table-meaning">${escHtml(firstMeaning)}</td>
    </tr>`;
  });

  html += '</tbody></table>';
  if (items.length > 200) {
    html += `<div style="padding:10px;text-align:center;color:var(--text-muted);font-size:0.78rem">Menampilkan 200 dari ${items.length} hasil. Persempit pencarian untuk melihat lebih spesifik.</div>`;
  }

  container.innerHTML = html;
  STATE.rendered = items.length;

  $('empty-state').classList.add('hidden');
  $('load-more-spinner').classList.add('hidden');
  if (items.length === 0) {
    $('empty-state').classList.remove('hidden');
  }
}


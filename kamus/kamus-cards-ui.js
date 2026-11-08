/* ═══════════════════════════════════════════════════════════════
   kamus/kamus-cards-ui.js — Mandarin Interaktif
   Panel grup (radikal/goresan/tema/pinyin), builder kartu hasil, helper UI umum
   Bagian dari modularisasi kamus.html. Dimuat sebagai <script src>
   biasa (bukan ES module) -- semua fungsi tetap di scope global,
   jadi urutan file lain relatif bebas KECUALI kamus-init.js yang
   WAJIB paling akhir.
   ═══════════════════════════════════════════════════════════════ */

'use strict';

/* ── GROUP PANEL: PER RADIKAL / GORESAN / TEMA / PINYIN (Fix #12-14) ── */

/* Inti render hasil grup -- terima OBJEK KATA langsung (bukan ids yg perlu
   di-resolve ulang). Dipakai renderGroupResults() (lookup dari STATE.dataHsk
   by id, spt biasa) DAN grup 'mirip' (E.0.3, butuh fallback ke Cidict utk
   karakter yg tidak ada entri berdiri sendiri di app_words.json). */
function renderGroupResultsFromWords(words, label) {
  showLanding(false);

  // Fix: reset sidebarFilter ke 'all' sebelum tampilkan hasil grup.
  // Bug lama (baru ketahuan lewat laporan Karakter Mirip, tapi berlaku
  // utk SEMUA jenis grup -- Radikal/Tema/Struktur/dll): kalau filter
  // Bookmarks/Recent/HSK-level masih aktif dari sesi sebelumnya, hasil
  // grup kesaring diam-diam jadi cuma sebagian (renderResultsBatch()
  // menerapkan sidebarFilter ke STATE.results apapun sumbernya). Grup
  // seharusnya SELALU tampilkan semua anggotanya, tidak peduli filter apa
  // yang aktif sebelumnya.
  STATE.sidebarFilter = 'all';
  document.querySelectorAll('.sidebar-item').forEach(el => {
    el.classList.toggle('active', el.dataset.filter === 'all');
  });

  STATE.query    = '';
  STATE.results  = words;
  STATE.rendered = 0;
  renderResultsBatch();
  updateResultsHeader(words.length);
  $('results-source').textContent = label;
}

function renderGroupResults(ids, label) {
  const data = STATE.dataHsk || [];
  const results = ids
    .map(id => data.find(w => (w.id || w.simplified) === id))
    .filter(Boolean);
  renderGroupResultsFromWords(results, label);
}

async function selectGroupItem(type, key) {
  if (type === 'radical') {
    const ids = (STATE.dataRadical && STATE.dataRadical[key]) || [];
    renderGroupResults(ids, 'Radikal: ' + key);
  } else if (type === 'stroke') {
    const ids = (STATE.dataStroke && STATE.dataStroke[key]) || [];
    renderGroupResults(ids, key + ' Goresan');
  } else if (type === 'theme') {
    const themeObj = (STATE.dataTheme && STATE.dataTheme[key]) || {};
    const ids = themeObj.words || [];
    renderGroupResults(ids, 'Tema: ' + (themeObj.label_id || key));
  } else if (type === 'struct') {
    const ids = (STATE.dataStructure && STATE.dataStructure[key]) || [];
    renderGroupResults(ids, structureLabel(key));
  } else if (type === 'phonetic') {
    const ids = (STATE.dataPhonetic && STATE.dataPhonetic[key]) || [];
    renderGroupResults(ids, 'Komponen Fonetik: ' + key);
  } else if (type === 'akar') {
    const entry = (STATE.dataAkar && STATE.dataAkar[key]) || null;
    const ids = entry ? (entry.kata_turunan || []).map(t => t.kata) : [];
    const label = entry
      ? `Akar: ${key} (${entry.pinyin || ''} — ${entry.arti || ''})`
      : 'Akar: ' + key;
    renderGroupResults(ids, label);
  } else if (type === 'khusus') {
    const obj = (STATE.dataKhusus && STATE.dataKhusus[key]) || {};
    const ids = obj.words || [];
    renderGroupResults(ids, 'Khusus: ' + (obj.label_id || key));
  }   else if (type === 'mirip') {
    // (E.0.3) key = index numerik ke STATE.dataConfusion.
    // ... (komentar lama tetap) ...
    const g = (STATE.dataConfusion && STATE.dataConfusion[key]) || null;
    console.log('[DEBUG] g=', g);
    if (g) {
      const chars = [g.character].concat(g.confusable_with || []);
      console.log('[DEBUG] chars=', chars, 'jumlah=', chars.length);
      if (!STATE.dataCidict) {
        showToast('Memuat data tambahan untuk karakter yang jarang dipakai…');
        await loadCidict();
      }
      const dataH = STATE.dataHsk || [];
      const dataC = STATE.dataCidict || [];
      const words = [];
      chars.forEach(c => {
        let hit = dataH.find(w => w.simplified === c);
        if (!hit) {
          hit = dataC.find(w => w.simplified === c);
          if (hit) hit._cidictFallback = true;
        }
        console.log('[DEBUG] karakter=', c, 'hit ditemukan?', !!hit, 'via cidict?', hit ? !!hit._cidictFallback : 'n/a');
        if (hit) words.push(hit);
      });
      console.log('[DEBUG] words final sebelum render, jumlah=', words.length, words);
      const label = 'Karakter Mirip: ' + chars.join('/');
      renderGroupResultsFromWords(words, label);
    }
  } else if (type === 'pinyin') {
    const data = STATE.dataHsk || [];
    const keyLower = key.toLowerCase();
    const results = data.filter(w => {
      const firstSyl = (w.pinyin || '').toLowerCase().split(/\s+/)[0] || '';
      return normalizePinyin(firstSyl).startsWith(keyLower);
    });
    STATE.query    = '';
    STATE.results  = results;
    STATE.rendered = 0;
    showLanding(false);
    renderResultsBatch();
    updateResultsHeader(results.length);
    $('results-source').textContent = 'Pinyin: ' + key.toUpperCase() + '…';
  }
  closeGroupPanel();
}

function buildResultCard(word, idx) {
  const id       = word.id || word.simplified || '';
  const hanzi    = word.simplified || id;
  const pinyin   = word.pinyin || '';

  // Arti pertama Indonesia
  let firstMeaning = '';
  if (Array.isArray(word.meanings_id) && word.meanings_id.length) {
    firstMeaning = word.meanings_id[0];
  } else if (word.meanings_id) {
    firstMeaning = String(word.meanings_id);
  }

  const q = STATE.query;
  const mode = detectMode(q);

  // Buat elemen kartu — Fix A2: 1 baris (hanzi | pinyin | arti), tanpa badge tambahan.
  // Info lengkap (HSK/radikal/goresan/tipe/struktur) sudah ada di panel detail kanan.
  const card = document.createElement('div');
  card.className = 'result-card result-row';
  card.dataset.id = id;
  card.dataset.idx = idx;
  if (STATE.source === 'cidict' || word._cidictFallback) card.classList.add('cidict');
  card.addEventListener('click', () => selectWord(id, idx));

  // Hanzi
  const hanziEl = document.createElement('div');
  hanziEl.className = 'result-hanzi';
  hanziEl.textContent = hanzi;

  // Handle drag lebar kolom hanzi (satu per kartu, semua terhubung ke variabel CSS yang sama)
  const resizeHandle = document.createElement('div');
  resizeHandle.className = 'hanzi-col-resize-handle';

  // Pinyin (highlight jika mode pinyin)
  const pinyinEl = document.createElement('div');
  pinyinEl.className = 'result-pinyin';
  pinyinEl.innerHTML = (mode === 'pinyin')
    ? highlight(pinyin, q)
    : escHtml(pinyin);

  // Arti (highlight jika mode id/en) — flex-grow, ellipsis jika kepanjangan
  const meaningEl = document.createElement('div');
  meaningEl.className = 'result-meaning';
  meaningEl.innerHTML = (mode === 'id' || mode === 'en')
    ? highlight(firstMeaning, q)
    : escHtml(firstMeaning);

  card.appendChild(hanziEl);
  card.appendChild(resizeHandle);
  card.appendChild(pinyinEl);
  card.appendChild(meaningEl);

  return card;
}

/* ── UI HELPERS ────────────────────────────────────────────── */
function showLanding(show) {
  $('landing-state').classList.toggle('hidden', !show);
}

function showLoading(show) {
  $('loading-state').classList.toggle('hidden', !show);
  $('landing-state').classList.toggle('hidden', show);
}

function clearResults() {
  $('cards-container').innerHTML = '';
  $('results-header').style.display = 'none';
  $('empty-state').classList.add('hidden');
  STATE.results  = [];
  STATE.rendered = 0;
  STATE.query    = '';
  updateModeBadge('');
  $('search-clear').classList.remove('visible');
  $('search-mode-badge').classList.remove('visible');
}

function updateResultsHeader(count) {
  const header = $('results-header');
  const source = $('results-source');
  header.style.display = 'flex';
  $('results-count').textContent = count.toLocaleString('id') + ' hasil';

  if (STATE.source === 'cidict') {
    source.textContent  = 'Cidict';
    source.className    = 'results-source extended';
  } else {
    source.textContent  = 'HSK';
    source.className    = 'results-source';
  }

  renderCardSortControls(header);
}

/* Fix A3: tombol sort cepat untuk mode kartu — dibangun dinamis supaya tidak
   bergantung pada markup statis (hanya muncul saat viewMode === 'card'). */
function renderCardSortControls(header) {
  let bar = $('card-sort-controls');
  if (STATE.viewMode !== 'card') {
    if (bar) bar.classList.add('hidden');
    return;
  }
  if (!bar) {
    bar = document.createElement('div');
    bar.id = 'card-sort-controls';
    bar.className = 'card-sort-controls';
    header.appendChild(bar);
  }
  bar.classList.remove('hidden');

  const OPTIONS = [
    { key: null,        label: 'Relevansi' },
    { key: 'simplified',label: 'Hanzi' },
    { key: 'pinyin',    label: 'Pinyin' },
    { key: 'meaning',   label: 'Arti' },
    { key: 'hsk',       label: 'HSK' },
  ];

  bar.innerHTML = OPTIONS.map(opt => {
    const active = STATE.cardSortKey === opt.key;
    const arrow  = active && opt.key ? (STATE.cardSortDir === 1 ? ' ▲' : ' ▼') : '';
    const keyArg = opt.key ? `'${opt.key}'` : 'null';
    return `<button class="card-sort-btn${active ? ' active' : ''}" onclick="setCardSort(${keyArg})">${opt.label}${arrow}</button>`;
  }).join('');
}

function updateModeBadge(mode) {
  const badge = $('search-mode-badge');
  const LABELS = { hanzi: '漢字', pinyin: 'Pīnyīn', id: 'ID', en: 'EN', auto: '' };
  const label  = LABELS[mode] || '';
  badge.textContent = label;
  badge.classList.toggle('visible', !!label && label !== '');
}

function updateSidebarCounts() {
  if (!STATE.dataHsk) return;
  const data = STATE.dataHsk;
  for (let lv = 1; lv <= 7; lv++) {
    const target = lv === 7 ? [7, 8, 9] : [lv];
    const cnt = data.filter(w => target.includes(parseInt(w.hsk))).length;
    const el  = $(`cnt-hsk${lv}`);
    if (el) el.textContent = cnt.toLocaleString('id');
  }
  $('cnt-all').textContent = data.length.toLocaleString('id');
}


/* ═══════════════════════════════════════════════════════════════
   wordbuilder-spot.js — Mode Spot-the-Error (cari kesalahan kalimat)
═══════════════════════════════════════════════════════════════ */
'use strict';


/* ── SPOT-THE-ERROR (Tier 3) ───────────────────────────────────
   Sumber soal: field kesalahan_umum {salah, benar, penjelasan,
   salah_py, benar_py} di pattern_explanations.json (per pola kini
   4 soal, diacak). salah/benar sudah HANZI MURNI (tanpa anotasi
   pinyin di dalamnya) -- pinyin disimpan terpisah di salah_py/benar_py
   dan cuma ditampilkan di feedback SETELAH user cek/lihat jawaban,
   supaya kartu soal awal cuma tampil hanzi tanpa bocoran cara baca.
   User klik karakter yang dianggap salah, lalu dicek terhadap hasil
   diff karakter salah↔benar (LCS-based).
   Catatan: untuk kesalahan urutan kata (bukan substitusi partikel),
   hasil diff kadang ambigu -- batasan wajar dari pendekatan ini. */

const SPOT = {
  scope:      'active', // 'active' (pola ini saja) | 'all' (semua pola)
  allPool:    null,      // dibangun sekali (lazy), array {patternKey, salah, benar, penjelasan}
  allIndex:   0,
  activeIndex: null,     // index soal yang sedang tampil di scope 'active'
  cards:      {},        // state tiap kartu aktif: { selected:Set, answered:bool, salah, benar, penjelasan }
};

function lcsTable(a, b) {
  const m = a.length, n = b.length;
  const dp = Array.from({ length: m + 1 }, () => new Array(n + 1).fill(0));
  for (let i = 1; i <= m; i++) {
    for (let j = 1; j <= n; j++) {
      dp[i][j] = (a[i - 1] === b[j - 1])
        ? dp[i - 1][j - 1] + 1
        : Math.max(dp[i - 1][j], dp[i][j - 1]);
    }
  }
  return dp;
}


// Kembalikan Set indeks karakter di `salah` yang tidak match dengan `benar`
// (hasil backtrack LCS) -- ini yang dianggap "bagian yang salah".
function charDiffWrongIndices(salah, benar) {
  const a = Array.from(salah);
  const b = Array.from(benar);
  const dp = lcsTable(a, b);
  let i = a.length, j = b.length;
  const matched = new Set();
  while (i > 0 && j > 0) {
    if (a[i - 1] === b[j - 1]) { matched.add(i - 1); i--; j--; }
    else if (dp[i - 1][j] >= dp[i][j - 1]) i--;
    else j--;
  }
  const wrong = new Set();
  for (let k = 0; k < a.length; k++) if (!matched.has(k)) wrong.add(k);
  return wrong;
}


/* ── PENJELASAN LENGKAP (accordion) ────────────────────────── */
function toggleExplainPanel() {
  const toggle = $('wb-explain-toggle');
  const panel  = $('wb-explain-panel');
  const willOpen = !panel.classList.contains('open');
  toggle.classList.toggle('open', willOpen);
  panel.classList.toggle('open', willOpen);
}


function renderPatternExplanation(patternKey) {
  const toggle = $('wb-explain-toggle');
  const panel  = $('wb-explain-panel');

  // Selalu kembali ke collapsed setiap ganti pola
  toggle.classList.remove('open');
  panel.classList.remove('open');
  panel.innerHTML = '';

  if (!explanationsLoaded) {
    panel.innerHTML = '<p class="wb-explain-text">⚠ Penjelasan lengkap belum berhasil dimuat.</p>';
    return;
  }

  const ex = PATTERN_EXPLANATIONS[patternKey];
  if (!ex) {
    panel.innerHTML = '<p class="wb-explain-text">Belum ada penjelasan lengkap untuk pola ini.</p>';
    return;
  }

  let html = '';

  if (ex.penjelasan_dasar) {
    html += `<div>
      <div class="wb-explain-block-title">Penjelasan Dasar</div>
      <div class="wb-explain-text">${escHtml(ex.penjelasan_dasar)}</div>
    </div>`;
  }

  if (ex.perbandingan_indonesia) {
    html += `<div>
      <div class="wb-explain-block-title">Perbandingan dengan Bahasa Indonesia</div>
      <div class="wb-explain-text">${escHtml(ex.perbandingan_indonesia)}</div>
    </div>`;
  }

  if (ex.kapan_tidak_boleh) {
    html += `<div>
      <div class="wb-explain-block-title">Kapan Tidak Boleh Dipakai</div>
      <div class="wb-explain-text">${escHtml(ex.kapan_tidak_boleh)}</div>
    </div>`;
  }

  if (Array.isArray(ex.kesalahan_umum) && ex.kesalahan_umum.length) {
    html += `<div>
      <div class="wb-explain-block-title">Kesalahan Umum — Latihan</div>
      <div class="wb-spot-scope-toggle">
        <button class="wb-spot-scope-btn" data-scope="active" onclick="setSpotScope('active')">Pola Ini</button>
        <button class="wb-spot-scope-btn" data-scope="all" onclick="setSpotScope('all')">Semua Pola</button>
      </div>
      <div id="wb-spot-container"></div>
    </div>`;
  }

  if (Array.isArray(ex.pola_terkait) && ex.pola_terkait.length) {
    let badges = '';
    ex.pola_terkait.forEach(r => {
      const relatedName = (PATTERNS[r.key] && PATTERNS[r.key].name) || r.key;
      badges += `<span class="wb-related-badge" data-related-key="${escHtml(r.key)}">
        ${escHtml(relatedName)}
        ${r.alasan ? `<span class="wb-related-reason">${escHtml(r.alasan)}</span>` : ''}
      </span>`;
    });
    html += `<div>
      <div class="wb-explain-block-title">Pola Terkait</div>
      <div class="wb-related-wrap">${badges}</div>
    </div>`;
  }

  panel.innerHTML = html || '<p class="wb-explain-text">Belum ada penjelasan lengkap untuk pola ini.</p>';

  // Klik badge pola terkait → pindah ke pola itu
  panel.querySelectorAll('.wb-related-badge').forEach(badge => {
    badge.addEventListener('click', () => {
      const key = badge.dataset.relatedKey;
      if (PATTERNS[key]) loadPattern(key);
    });
  });

  // Render latihan spot-the-error (kalau pola ini punya kesalahan_umum)
  if (Array.isArray(ex.kesalahan_umum) && ex.kesalahan_umum.length) {
    refreshSpotScopeButtons();
    renderSpotContainer(patternKey);
  }
}


/* ── SPOT-THE-ERROR: toggle scope + render kontainer ───────────── */
function setSpotScope(scope) {
  SPOT.scope = scope;
  if (scope === 'all' && !SPOT.allPool) buildAllPatternsSpotPool();
  refreshSpotScopeButtons();
  renderSpotContainer(WB.activePattern);
}


function refreshSpotScopeButtons() {
  document.querySelectorAll('.wb-spot-scope-btn').forEach(btn => {
    btn.classList.toggle('active', btn.dataset.scope === SPOT.scope);
  });
}


function buildAllPatternsSpotPool() {
  const pool = [];
  Object.keys(PATTERN_EXPLANATIONS).forEach(key => {
    const ex = PATTERN_EXPLANATIONS[key];
    if (Array.isArray(ex.kesalahan_umum)) {
      ex.kesalahan_umum.forEach(item => {
        pool.push({
          patternKey: key, salah: item.salah, benar: item.benar, penjelasan: item.penjelasan,
          salah_py: item.salah_py, benar_py: item.benar_py,
        });
      });
    }
  });
  // Acak urutan (Fisher-Yates)
  for (let i = pool.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [pool[i], pool[j]] = [pool[j], pool[i]];
  }
  SPOT.allPool  = pool;
  SPOT.allIndex = 0;
}


function renderSpotContainer(patternKey) {
  const container = $('wb-spot-container');
  if (!container) return;

  if (SPOT.scope === 'active') {
    // Dulu: semua item kesalahan_umum pola ini ditumpuk jadi beberapa
    // kontainer sekaligus. Sekarang: cuma 1 kontainer, dan tombol
    // "↺ Ulangi" (lihat resetSpotCard) yang memunculkan soal acak lain
    // dari stok -- supaya hemat ruang & tidak monoton.
    SPOT.activeIndex = null; // paksa pilih baru setiap ganti pola
    renderActiveModeQuestion(patternKey);

  } else {
    // scope === 'all'
    if (!SPOT.allPool) buildAllPatternsSpotPool();
    if (!SPOT.allPool.length) {
      container.innerHTML = '<p class="wb-explain-text">Belum ada data kesalahan umum yang bisa dipakai.</p>';
      return;
    }
    renderAllModeQuestion();
  }
}


/* ── SPOT-THE-ERROR: mode "Pola Ini" -- 1 kartu, acak dari stok ──── */
function renderActiveModeQuestion(patternKey, avoidRepeat) {
  const container = $('wb-spot-container');
  if (!container) return;

  const ex    = PATTERN_EXPLANATIONS[patternKey];
  const items = (ex && Array.isArray(ex.kesalahan_umum)) ? ex.kesalahan_umum : [];

  if (!items.length) {
    container.innerHTML = '<p class="wb-explain-text">Belum ada soal kesalahan umum untuk pola ini.</p>';
    return;
  }

  let idx = Math.floor(Math.random() * items.length);
  if (avoidRepeat && items.length > 1 && idx === SPOT.activeIndex) {
    idx = (idx + 1) % items.length;
  }
  SPOT.activeIndex = idx;

  const item   = items[idx];
  const cardId = 'active-' + idx;
  SPOT.cards = {};
  SPOT.cards[cardId] = {
    salah: item.salah, benar: item.benar, penjelasan: item.penjelasan,
    salah_py: item.salah_py, benar_py: item.benar_py,
    selected: new Set(), answered: false,
  };

  container.innerHTML = buildSpotCardHTML(cardId);
  attachSpotCardListeners(cardId);
}


function renderAllModeQuestion() {
  const container = $('wb-spot-container');
  if (!container) return;

  const item   = SPOT.allPool[SPOT.allIndex];
  const cardId = 'all-' + SPOT.allIndex;
  SPOT.cards = {};
  SPOT.cards[cardId] = {
    salah: item.salah, benar: item.benar, penjelasan: item.penjelasan,
    salah_py: item.salah_py, benar_py: item.benar_py,
    selected: new Set(), answered: false,
  };

  const patternName = (PATTERNS[item.patternKey] && PATTERNS[item.patternKey].name) || item.patternKey;

  let html = `<div class="wb-spot-progress">Soal ${SPOT.allIndex + 1} / ${SPOT.allPool.length}</div>`;
  html += `<div class="wb-spot-source-pattern">Pola: ${escHtml(patternName)}</div>`;
  html += buildSpotCardHTML(cardId);
  html += `<div style="margin-top:10px;text-align:right">
    <button class="btn-wb btn-wb-secondary" onclick="nextSpotQuestion()">Soal Berikutnya ▶</button>
  </div>`;

  container.innerHTML = html;
  attachSpotCardListeners(cardId);
}


function nextSpotQuestion() {
  SPOT.allIndex = (SPOT.allIndex + 1) % SPOT.allPool.length;
  renderAllModeQuestion();
}


/* ── SPOT-THE-ERROR: kartu individual ──────────────────────────── */
function buildSpotCardHTML(cardId) {
  const card  = SPOT.cards[cardId];
  const chars = Array.from(card.salah);
  const charsHtml = chars.map((ch, i) =>
    `<span class="wb-spot-char" data-card="${cardId}" data-idx="${i}">${escHtml(ch)}</span>`
  ).join('');

  return `<div class="wb-spot-card" data-card-id="${cardId}">
    <div class="wb-spot-instruction">Klik karakter yang menurutmu SALAH, lalu klik "Cek Jawaban":</div>
    <div class="wb-spot-sentence" id="wb-spot-sentence-${cardId}">${charsHtml}</div>
    <div class="wb-spot-controls">
      <button class="btn-wb btn-wb-primary"   onclick="checkSpotAnswer('${cardId}')">Cek Jawaban</button>
      <button class="btn-wb btn-wb-secondary" onclick="revealSpotAnswer('${cardId}')">Lihat Jawaban</button>
      <button class="btn-wb btn-wb-secondary" onclick="resetSpotCard('${cardId}')">↺ Ulangi</button>
    </div>
    <div class="wb-spot-feedback" id="wb-spot-feedback-${cardId}"></div>
  </div>`;
}


function attachSpotCardListeners(cardId) {
  const sentEl = $('wb-spot-sentence-' + cardId);
  if (!sentEl) return;
  sentEl.querySelectorAll('.wb-spot-char').forEach(span => {
    span.addEventListener('click', () => {
      const card = SPOT.cards[cardId];
      if (!card || card.answered) return;
      const idx = parseInt(span.dataset.idx, 10);
      if (card.selected.has(idx)) {
        card.selected.delete(idx);
        span.classList.remove('selected');
      } else {
        card.selected.add(idx);
        span.classList.add('selected');
      }
    });
  });
}


function checkSpotAnswer(cardId) {
  const card = SPOT.cards[cardId];
  if (!card || card.answered) return;
  if (!card.selected.size) {
    showToast('Klik dulu karakter yang menurutmu salah.');
    return;
  }
  const wrongIdx = charDiffWrongIndices(card.salah, card.benar);
  const gotIt = [...card.selected].some(i => wrongIdx.has(i));
  finalizeSpotCard(cardId, wrongIdx, gotIt ? 'ok' : 'miss');
}


function revealSpotAnswer(cardId) {
  const card = SPOT.cards[cardId];
  if (!card || card.answered) return;
  const wrongIdx = charDiffWrongIndices(card.salah, card.benar);
  finalizeSpotCard(cardId, wrongIdx, null);
}


function finalizeSpotCard(cardId, wrongIdx, status) {
  const card = SPOT.cards[cardId];
  card.answered = true;

  const sentEl = $('wb-spot-sentence-' + cardId);
  sentEl.querySelectorAll('.wb-spot-char').forEach(span => {
    const idx        = parseInt(span.dataset.idx, 10);
    const isWrong    = wrongIdx.has(idx);
    const isSelected = card.selected.has(idx);
    span.classList.add('disabled');
    if (isWrong && isSelected)       span.classList.add('mark-correct'); // ketemu
    else if (isWrong && !isSelected) span.classList.add('mark-missed');  // kelewat
    else if (!isWrong && isSelected) span.classList.add('mark-off');     // salah pilih
  });

  let statusHtml = '';
  if (status === 'ok') {
    statusHtml = '<div class="wb-spot-feedback-status ok">✓ Tepat! Kamu menemukan bagian yang salah.</div>';
  } else if (status === 'miss') {
    statusHtml = '<div class="wb-spot-feedback-status miss">Belum tepat — perhatikan bagian bergaris putus-putus di bawah.</div>';
  }

  $('wb-spot-feedback-' + cardId).innerHTML = `
    ${statusHtml}
    ${card.salah_py ? `<div class="wb-spot-feedback-pinyin">${escHtml(card.salah_py)}</div>` : ''}
    <div class="wb-spot-feedback-benar">✅ ${escHtml(card.benar)}</div>
    ${card.benar_py ? `<div class="wb-spot-feedback-pinyin">${escHtml(card.benar_py)}</div>` : ''}
    ${card.penjelasan ? `<div class="wb-spot-feedback-note">${escHtml(card.penjelasan)}</div>` : ''}
  `;
}


function resetSpotCard(cardId) {
  // Scope "Pola Ini": kalau stok kesalahan_umum pola ini > 1 item, tombol
  // "↺ Ulangi" pindah ke soal ACAK lain (bukan cuma bersihkan pilihan di
  // kartu yang sama) -- sesuai permintaan رسلان supaya latihan bervariasi.
  if (SPOT.scope === 'active') {
    const ex    = PATTERN_EXPLANATIONS[WB.activePattern];
    const items = (ex && Array.isArray(ex.kesalahan_umum)) ? ex.kesalahan_umum : [];
    if (items.length > 1) {
      renderActiveModeQuestion(WB.activePattern, true /* avoidRepeat */);
      return;
    }
  }

  const card = SPOT.cards[cardId];
  if (!card) return;
  card.selected  = new Set();
  card.answered  = false;

  const sentEl = $('wb-spot-sentence-' + cardId);
  sentEl.querySelectorAll('.wb-spot-char').forEach(span => {
    span.classList.remove('selected', 'disabled', 'mark-correct', 'mark-missed', 'mark-off');
  });
  $('wb-spot-feedback-' + cardId).innerHTML = '';
}

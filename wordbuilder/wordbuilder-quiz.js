/* ═══════════════════════════════════════════════════════════════
   wordbuilder-quiz.js — Mode Kuis Pola (tebak pola dari kalimat)
═══════════════════════════════════════════════════════════════ */
'use strict';


/* ── KUIS POLA KALIMAT (Tier 3) — kebalikan builder ─────────────
   Tebak pola dari kalimat. Sumber soal: examples per pola +
   contoh_tambahan dari pattern_explanations.json. Distraktor
   diutamakan dari pola_terkait (mirip/mudah tertukar), sisanya acak. */

const QUIZ_POLA = {
  pool:     null,  // dibangun sekali (lazy): [{cn, py, id, patternKey}]
  current:  null,
  answered: false,
  score:    { ok: 0, bad: 0 },
};

function buildQuizPolaPool() {
  const pool = [];
  Object.keys(PATTERNS).forEach(key => {
    const pattern = PATTERNS[key];
    if (Array.isArray(pattern.examples)) {
      pattern.examples.forEach(ex => {
        pool.push({ cn: ex.cn, py: ex.py, id: ex.id, patternKey: key });
      });
    }
    const ex2 = PATTERN_EXPLANATIONS[key];
    if (ex2 && Array.isArray(ex2.contoh_tambahan)) {
      ex2.contoh_tambahan.forEach(c => {
        pool.push({ cn: c.cn, py: c.py, id: c.id, patternKey: key });
      });
    }
  });
  QUIZ_POLA.pool = pool;
}


function startQuizQuestion() {
  if (!QUIZ_POLA.pool) buildQuizPolaPool();
  if (!QUIZ_POLA.pool.length) {
    $('wb-quiz-body').innerHTML = '<p class="wb-explain-text">Belum ada data kalimat untuk kuis ini.</p>';
    return;
  }
  QUIZ_POLA.answered = false;
  const item    = QUIZ_POLA.pool[Math.floor(Math.random() * QUIZ_POLA.pool.length)];
  const options = buildQuizOptions(item.patternKey);
  QUIZ_POLA.current = { item, options };
  renderQuizQuestion();
}


function buildQuizOptions(correctKey) {
  const ex      = PATTERN_EXPLANATIONS[correctKey];
  const related = (ex && Array.isArray(ex.pola_terkait)) ? ex.pola_terkait.map(r => r.key) : [];

  const options = [correctKey];
  // Distraktor diutamakan dari pola_terkait (mirip/mudah tertukar)
  for (const k of related) {
    if (options.length >= 4) break;
    if (!options.includes(k) && PATTERNS[k]) options.push(k);
  }
  // Kalau masih kurang dari 4, isi sisanya acak dari semua pola
  const allKeys = Object.keys(PATTERNS);
  while (options.length < 4 && options.length < allKeys.length) {
    const rk = allKeys[Math.floor(Math.random() * allKeys.length)];
    if (!options.includes(rk)) options.push(rk);
  }
  // Acak urutan tampil (Fisher-Yates)
  for (let i = options.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [options[i], options[j]] = [options[j], options[i]];
  }
  return options;
}


function renderQuizQuestion() {
  const { item, options } = QUIZ_POLA.current;
  const body = $('wb-quiz-body');
  body.innerHTML = `
    <div class="wb-quiz-card">
      <div>
        <div class="wb-quiz-sentence-cn">${escHtml(item.cn)}</div>
        <div class="wb-quiz-sentence-py">${escHtml(item.py)}</div>
        <div class="wb-quiz-sentence-id">${escHtml(item.id)}</div>
      </div>
      <div class="wb-quiz-instruction">Kalimat ini menggunakan pola kalimat apa?</div>
      <div class="wb-quiz-options" id="wb-quiz-options">
        ${options.map(key => `
          <button class="wb-quiz-option-btn" data-key="${key}" onclick="selectQuizAnswer('${key}')">
            ${escHtml(PATTERNS[key].name)}
            <span style="opacity:0.6">(${escHtml(PATTERNS[key].formula)})</span>
          </button>
        `).join('')}
      </div>
      <div class="wb-quiz-feedback" id="wb-quiz-feedback"></div>
    </div>
  `;
}


function selectQuizAnswer(pickedKey) {
  if (QUIZ_POLA.answered) return;
  QUIZ_POLA.answered = true;

  const correctKey = QUIZ_POLA.current.item.patternKey;
  const isCorrect  = pickedKey === correctKey;

  document.querySelectorAll('.wb-quiz-option-btn').forEach(btn => {
    btn.disabled = true;
    const key = btn.dataset.key;
    if (key === correctKey)     btn.classList.add('mark-correct');
    else if (key === pickedKey) btn.classList.add('mark-wrong');
  });

  if (isCorrect) QUIZ_POLA.score.ok++;
  else           QUIZ_POLA.score.bad++;
  $('wb-quiz-score-ok').textContent  = QUIZ_POLA.score.ok;
  $('wb-quiz-score-bad').textContent = QUIZ_POLA.score.bad;

  // Kalau jawaban salah kebetulan pola yang "terkait" (mudah tertukar),
  // tampilkan alasan bedanya supaya jadi pelajaran, bukan cuma vonis salah.
  let noteHtml = '';
  if (!isCorrect) {
    const ex  = PATTERN_EXPLANATIONS[correctKey];
    const rel = (ex && Array.isArray(ex.pola_terkait))
      ? ex.pola_terkait.find(r => r.key === pickedKey)
      : null;
    if (rel && rel.alasan) {
      noteHtml = `<div class="wb-quiz-feedback-note">${escHtml(rel.alasan)}</div>`;
    }
  }

  const feedback = $('wb-quiz-feedback');
  feedback.classList.add('visible');
  feedback.innerHTML = `
    <div class="wb-quiz-feedback-status ${isCorrect ? 'ok' : 'bad'}">
      ${isCorrect ? '✓ Tepat!' : '✗ Kurang tepat — jawaban benar: ' + escHtml(PATTERNS[correctKey].name)}
    </div>
    ${noteHtml}
    <button class="wb-quiz-next-btn" onclick="startQuizQuestion()">Soal Berikutnya ▶</button>
  `;
}

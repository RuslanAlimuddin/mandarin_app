/* ═══════════════════════════════════════════════════════════════
   wordbuilder-builder.js — Engine susun kalimat: render slot, bangun
   output, contoh kalimat, ucapkan & salin hasil
═══════════════════════════════════════════════════════════════ */
'use strict';


/* ── LOAD POLA ──────────────────────────────────────────────── */
function loadPattern(patternKey) {
  const pattern = PATTERNS[patternKey];
  if (!pattern) return;

  if (!wordPoolsLoaded) {
    showToast('Data kata masih dimuat, tunggu sebentar…');
    return;
  }

  WB.activePattern = patternKey;
  WB.slotValues    = {};
  saveLastViewState();

  // Update sidebar aktif
  document.querySelectorAll('.sidebar-item').forEach(el => {
    el.classList.toggle('active', el.dataset.pattern === patternKey);
  });

  // Tampilkan topbar
  $('wb-topbar').classList.remove('hidden');
  $('wb-pattern-name').textContent    = pattern.name;
  $('wb-pattern-formula').textContent = pattern.formula;

  // Tampilkan area konten
  $('wb-choose-screen').classList.add('hidden');
  $('wb-content').classList.remove('hidden');

  // Render slot
  renderSlots(pattern);

  // Render tip
  $('wb-tip').innerHTML = pattern.tip || '';

  // Render penjelasan lengkap (accordion, selalu kembali collapsed saat ganti pola)
  renderPatternExplanation(patternKey);

  // Render contoh -- gabungkan contoh bawaan pola + "contoh tambahan" dari
  // pattern_explanations.json jadi SATU stok (dulu 2 kontainer terpisah
  // yang isinya sama-sama contoh benar, sekarang 1 kontainer + tombol
  // "Contoh Lain" supaya hemat ruang & tetap ada variasi).
  const ex2 = PATTERN_EXPLANATIONS[patternKey];
  const combinedExamples = [
    ...(pattern.examples || []),
    ...((ex2 && Array.isArray(ex2.contoh_tambahan)) ? ex2.contoh_tambahan : []),
  ];
  renderExamples(combinedExamples);

  // Reset output
  resetOutput();
}


/* ── RENDER SLOT ────────────────────────────────────────────── */
function renderSlots(pattern) {
  const container = $('wb-slots-container');
  container.innerHTML = '';

  const row = document.createElement('div');
  row.className = 'wb-slot-row';

  let prefillApplied = false;

  pattern.slots.forEach((slot, idx) => {

    // Slot tetap (fixed) — tampilkan sebagai teks, bukan dropdown
    if (slot.fixed) {
      WB.slotValues[slot.id] = slot.fixed; // langsung set nilainya

      if (slot.fixed.cn) { // hanya tampilkan jika ada teks (bukan kosong)
        const sep = document.createElement('div');
        sep.className = 'wb-slot-sep';
        sep.innerHTML = `<span style="font-size:1.4rem;color:var(--gold)">${escHtml(slot.fixed.cn)}</span>`;
        row.appendChild(sep);
      }
      return;
    }

    // Slot dropdown
    const wrap = document.createElement('div');
    wrap.className = 'wb-slot' + (slot.required ? '' : ' optional');

    const label = document.createElement('div');
    label.className = 'wb-slot-label';
    label.innerHTML = escHtml(slot.label) +
      (slot.required
        ? '<span class="slot-required">*</span>'
        : '<span class="slot-optional">(ops)</span>');

    const select = document.createElement('select');
    select.className  = 'wb-select';
    select.dataset.slotId = slot.id;

    // Opsi default
    const defOpt = document.createElement('option');
    defOpt.value       = '';
    defOpt.textContent = '— pilih —';
    select.appendChild(defOpt);

    // Isi opsi dari pool terfilter HSK
    let pool = getFilteredPool(slot.pool);

    // Prefill sekali pakai dari wb_ref_word (1 slot, dari Flashcard) ATAU
    // dari Koleksi Tersimpan (banyak slot sekaligus, lihat pendingSlotValues)
    let prefillIdx  = null;
    let prefillWord = null;
    if (WB.pendingPrefill && WB.pendingPrefill.slotId === slot.id) {
      prefillWord = WB.pendingPrefill.entry;
    } else if (WB.pendingSlotValues && WB.pendingSlotValues[slot.id]) {
      prefillWord = WB.pendingSlotValues[slot.id];
    }
    if (prefillWord) {
      const existingIdx = pool.findIndex(w => w.cn === prefillWord.cn && w.py === prefillWord.py);
      if (existingIdx >= 0) {
        prefillIdx = existingIdx;
      } else {
        // Kata tidak ada di pool terfilter saat ini (mis. level HSK-nya tidak
        // dicentang) — tetap sisipkan di urutan teratas supaya tetap terpilih.
        pool = [prefillWord, ...pool];
        prefillIdx = 0;
      }
    }

    pool.forEach((word, wIdx) => {
      const opt = document.createElement('option');
      opt.value       = wIdx;
      opt.textContent = word.cn + '  ' + word.py + '  (' + word.id + ')';
      select.appendChild(opt);
    });

    if (prefillIdx !== null) {
      select.value = prefillIdx;
      WB.slotValues[slot.id] = pool[prefillIdx];
      prefillApplied = true;
    }

    // Event: saat dipilih
    select.addEventListener('change', () => {
      const idx = select.value;
      if (idx === '') {
        delete WB.slotValues[slot.id];
      } else {
        WB.slotValues[slot.id] = pool[parseInt(idx)];
      }
      buildOutput();
    });

    wrap.appendChild(label);
    wrap.appendChild(select);

    // Pesan hint kalau pool kosong/sangat sedikit — bedakan penyebab
    // (filter HSK vs filter mastery Tier 2) supaya sarannya tepat sasaran
    if (pool.length === 0) {
      const hint = document.createElement('div');
      hint.className = 'wb-slot-hint empty';
      if (WB.masteryFilter === 'mastered') {
        hint.textContent = 'Belum ada kata yang dikuasai di sini. Coba pilih "Semua Kata" atau berlatih dulu di Flashcard.';
      } else if (WB.masteryFilter === 'weak') {
        hint.textContent = 'Belum ada kata yang sering salah di sini — bagus! Coba pilih "Semua Kata".';
      } else {
        hint.textContent = 'Tidak ada kata di level HSK terpilih. Coba centang level lain.';
      }
      wrap.appendChild(hint);
    } else if (pool.length < 5) {
      const hint = document.createElement('div');
      hint.className = 'wb-slot-hint';
      hint.textContent = `Hanya ${pool.length} kata tersedia — centang level lain untuk variasi lebih banyak.`;
      wrap.appendChild(hint);
    }

    row.appendChild(wrap);
  });

  container.appendChild(row);

  // Prefill dari wb_ref_word / Koleksi Tersimpan hanya berlaku sekali
  WB.pendingPrefill     = null;
  WB.pendingSlotValues  = null;
  if (prefillApplied) buildOutput();
}


/* ── BUILD OUTPUT ───────────────────────────────────────────── */
function buildOutput() {
  const pattern = PATTERNS[WB.activePattern];
  if (!pattern) return;

  const result = pattern.build(WB.slotValues);

  const placeholder = $('wb-output-placeholder');
  const resultEl    = $('wb-output-result');
  const copyBtn     = $('wb-copy-btn');
  const speakBtn    = $('btn-speak-wb');

  if (!result) {
    // Belum lengkap
    placeholder.classList.remove('hidden');
    resultEl.classList.add('hidden');
    copyBtn.style.display = 'none';
    speakBtn.style.display = 'none';
    return;
  }

  // Tampilkan hasil
  placeholder.classList.add('hidden');
  resultEl.classList.remove('hidden');
  copyBtn.style.display = '';
  speakBtn.style.display = '';

  $('wb-out-chinese').textContent     = result.cn;
  $('wb-out-pinyin').textContent      = result.py;
  $('wb-out-translation').textContent = result.id;
}


/* ── RESET OUTPUT ───────────────────────────────────────────── */
function resetOutput() {
  $('wb-output-placeholder').classList.remove('hidden');
  $('wb-output-result').classList.add('hidden');
  $('wb-copy-btn').style.display = 'none';
  $('btn-speak-wb').style.display = 'none';
  $('wb-out-chinese').textContent     = '';
  $('wb-out-pinyin').textContent      = '';
  $('wb-out-translation').textContent = '';
}


/* ── RESET SLOT ─────────────────────────────────────────────── */
function resetSlots() {
  if (!WB.activePattern) return;

  WB.slotValues = {};

  // Reset semua dropdown ke — pilih —
  document.querySelectorAll('.wb-select').forEach(sel => {
    sel.value = '';
  });

  // Reset fixed slots
  const pattern = PATTERNS[WB.activePattern];
  if (pattern) {
    pattern.slots.forEach(slot => {
      if (slot.fixed) WB.slotValues[slot.id] = slot.fixed;
    });
  }

  resetOutput();
}


/* ── ISI ACAK ───────────────────────────────────────────────── */
function randomFill() {
  if (!WB.activePattern) return;

  const pattern = PATTERNS[WB.activePattern];
  if (!pattern) return;

  WB.slotValues = {};

  pattern.slots.forEach(slot => {
    if (slot.fixed) {
      WB.slotValues[slot.id] = slot.fixed;
      return;
    }

    const pool = getFilteredPool(slot.pool);
    if (!pool.length) return; // tidak ada kata di level HSK terpilih, lewati slot ini

    const randIdx = Math.floor(Math.random() * pool.length);
    WB.slotValues[slot.id] = pool[randIdx];

    // Update tampilan dropdown
    const sel = document.querySelector(`.wb-select[data-slot-id="${slot.id}"]`);
    if (sel) sel.value = String(randIdx);
  });

  buildOutput();
}


/* ── RENDER CONTOH ──────────────────────────────────────────── */
function renderExamples(examples) {
  WB.exampleStock = examples || [];
  WB.exampleIndex = 0;

  const container = $('wb-examples');
  if (!WB.exampleStock.length) {
    container.innerHTML = '<p class="text-muted text-sm">Tidak ada contoh.</p>';
    return;
  }
  renderCurrentExample();
}


function renderCurrentExample() {
  const container = $('wb-examples');
  const stock = WB.exampleStock;
  if (!stock.length) return;

  const ex = stock[WB.exampleIndex];
  container.innerHTML =
    `<div class="wb-example-card" id="wb-example-card-single">
       <div class="wb-example-cn">${escHtml(ex.cn)}</div>
       <div class="wb-example-py">${escHtml(ex.py)}</div>
       <div class="wb-example-id">${escHtml(ex.id)}</div>
     </div>` +
    (stock.length > 1
      ? `<div class="wb-example-nav">
           <button class="btn-wb btn-wb-secondary" onclick="nextExample()">Contoh Lain ▶</button>
           <span class="wb-example-nav-count">${WB.exampleIndex + 1} / ${stock.length}</span>
         </div>`
      : '');

  // Klik contoh (bukan tombol Contoh Lain) → isi output langsung
  $('wb-example-card-single').addEventListener('click', () => {
    $('wb-output-placeholder').classList.add('hidden');
    $('wb-output-result').classList.remove('hidden');
    $('wb-copy-btn').style.display = '';
    $('btn-speak-wb').style.display = '';
    $('wb-out-chinese').textContent     = ex.cn;
    $('wb-out-pinyin').textContent      = ex.py;
    $('wb-out-translation').textContent = ex.id;
    showToast('Contoh ditampilkan di output.');
  });
}


function nextExample() {
  const stock = WB.exampleStock;
  if (stock.length < 2) return;
  // Acak, hindari mengulang contoh yang sama persis 2x berturut-turut
  let idx = Math.floor(Math.random() * stock.length);
  if (idx === WB.exampleIndex) idx = (idx + 1) % stock.length;
  WB.exampleIndex = idx;
  renderCurrentExample();
}



function speakOutput() {
  const cn = $('wb-out-chinese').textContent;
  if (!cn) return;
  speak(cn, { rate: AudioTTS.rate });
}


function copyOutput() {
  const cn  = $('wb-out-chinese').textContent;
  const py  = $('wb-out-pinyin').textContent;
  const id  = $('wb-out-translation').textContent;

  if (!cn) return;

  const text = cn + '\n' + py + '\n' + id;

  if (navigator.clipboard) {
    navigator.clipboard.writeText(text)
      .then(() => showToast('✓ Disalin ke clipboard!', 'success'))
      .catch(() => fallbackCopy(text));
  } else {
    fallbackCopy(text);
  }
}


function fallbackCopy(text) {
  const ta = document.createElement('textarea');
  ta.value = text;
  ta.style.position = 'fixed';
  ta.style.opacity  = '0';
  document.body.appendChild(ta);
  ta.select();
  try {
    document.execCommand('copy');
    showToast('✓ Disalin!', 'success');
  } catch {
    showToast('⚠ Tidak bisa menyalin otomatis.', 'error');
  }
  document.body.removeChild(ta);
}

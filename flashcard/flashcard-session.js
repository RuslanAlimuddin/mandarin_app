/* ═══════════════════════════════════════════════════════════════
   flashcard-session.js — Sesi belajar inti: render kartu, jawaban,
   hint, rating SRS, mnemonic, animasi goresan, kirim ke wordbuilder
═══════════════════════════════════════════════════════════════ */
'use strict';


/* ── SET MODE PERTANYAAN (Fix #9) ───────────────────────────── */
function setQuestionMode(mode) {
  FC.questionMode = mode;
  document.querySelectorAll('.qm-btn').forEach(btn => {
    btn.classList.toggle('active', btn.dataset.mode === mode);
  });
  // Re-render kartu saat ini kalau sesi sedang berjalan
  if (FC.currentWord && !FC.isFlipped) renderCurrentCard();
}


/* ── MULAI SESI ─────────────────────────────────────────────── */
function startSession() {
  if (FC.deckId === 'tone-trap') {
    startAudioGame('tonepairs');
    return;
  }

  // "👀 Karakter Mirip" (E.0.3) -- sama spt tone-trap, selalu game
  // dengar-pilih, tidak punya bentuk flip-card biasa yang masuk akal.
  if (FC.deckId === 'confusion') {
    startAudioGame('confusion');
    return;
  }

  // "Pilih yang Tepat" (near-synonym nuance) -- selalu game kalimat-rumpang,
  // sama seperti Jebakan Nada tidak bergantung toggle "Mode Game" (soal
  // kalimat rumpang tidak punya bentuk flip-card biasa yang masuk akal).
  if (FC.deckId === 'nuance-choice') {
    startAudioGame('nuance');
    return;
  }

  // "🧩 Tebak Pola Kata" -- sama seperti nuance-choice, selalu game
  // pilihan-ganda, tidak punya bentuk flip-card biasa yang masuk akal.
  if (FC.deckId === 'pola-choice') {
    startAudioGame('pola');
    return;
  }

  if (!FC.queue.length) return;

  if (FC.gameModeOn) {
    // Deck Lawan Kata & Sinonim dapat mesin soal khusus (relasi makna,
    // bukan cuma pengenalan bunyi) -- deck lain tetap game generic biasa.
    const relationMode = FC.deckId === 'antonyms' ? 'antonym'
                        : FC.deckId === 'synonyms' ? 'synonym'
                        : 'generic';
    startAudioGame(relationMode);
    return;
  }

  // Reset statistik sesi
  FC.queueIndex      = 0;
  FC.sessionTotal    = FC.queue.length;
  FC.sessionCorrect  = 0;
  FC.sessionAgain    = 0;
  FC.sessionNew      = 0;
  FC.sessionReview   = 0;
  FC.isFlipped       = false;

  // Tampilkan topbar
  $('fc-topbar').classList.remove('hidden');
  $('fc-deck-name').textContent = FC.deckName;

  // Sembunyikan tombol mulai
  $('btn-start-session').classList.add('hidden');

  // Tampilkan screen sesi
  showScreen('session');

  // Render kartu pertama
  renderCurrentCard();
}


/* ── AUDIO: UCAPKAN KARTU SAAT INI ─────────────────────────── */
function speakCurrentCard() {
  if (!FC.currentWord) return;
  const word = FC.currentWord;
  const simplified = word.simplified || word.id;
  speak(simplified, { rate: AudioTTS.rate });
}


/* ── RENDER KARTU SAAT INI ─────────────────────────────────── */
/* ── CROSS-LINK KE BACAAN BERJENJANG (Tier baru) ──────────────────
   Index dibangun sekali dari data/graded_readers.json, lazy-load
   supaya tidak membebani load awal flashcard.html. Peta:
   kata (glossary[].cn) -> daftar bacaan yang mengandungnya.
   Pola sama seperti index radikal di kamus.html: fetch sekali,
   simpan di memori, dipakai berulang tanpa fetch ulang. ── */
let FC_READING_INDEX = null;
let fcReadingIndexPromise = null;

function loadFcReadingIndex() {
  if (fcReadingIndexPromise) return fcReadingIndexPromise;
  fcReadingIndexPromise = fetch('data/graded_readers.json')
    .then(res => res.ok ? res.json() : { passages: [] })
    .then(data => {
      const idx = {};
      (data.passages || []).forEach(p => {
        (p.glossary || []).forEach(g => {
          if (!g.cn) return;
          if (!idx[g.cn]) idx[g.cn] = [];
          idx[g.cn].push({ id: p.id, title: p.title, level: p.level, tema: p.tema || null });
        });
      });
      FC_READING_INDEX = idx;
      return idx;
    })
    .catch(e => {
      console.warn('data/graded_readers.json tidak tersedia utk cross-link bacaan:', e);
      FC_READING_INDEX = {};
      return {};
    });
  return fcReadingIndexPromise;
}


// Buka graded-reader.html langsung ke bacaan tertentu, reuse mekanisme
// "ingat posisi terakhir" yang sudah ada di graded-reader.html
// (restoreGrLastState via key mandarin_gr_last_state_v1) -- tidak perlu
// tambah dukungan query-param baru di graded-reader.html.
function openReadingFromFc(passageId) {
  try {
    localStorage.setItem('mandarin_gr_last_state_v1', JSON.stringify({
      view: 'reading',
      activeLevel: null,
      activeTema: null,
      passageId: passageId,
    }));
  } catch (e) { /* abaikan senyap -- bukan fitur kritis */ }
  window.location.href = 'graded-reader.html';
}


function renderCurrentCard() {
  if (FC.queueIndex >= FC.queue.length) {
    finishSession();
    return;
  }

  const word = FC.queue[FC.queueIndex];
  FC.currentWord = word;
  FC.isFlipped   = false;
  FC.hintShown   = false;

  const id         = word.id || word.simplified;
  const simplified = word.simplified || id;
  const hskLv      = word.hsk;

  // Tentukan mode aktual pertanyaan (Fix #9)
  const qMode = FC.questionMode;
  const actualMode = qMode === 'random'
    ? ['hanzi','pinyin','id'][Math.floor(Math.random() * 3)]
    : qMode;

  // Reset flip
  $('fc-card-inner').classList.remove('flipped');

  // ── MUKA DEPAN ──
  const frontHanzi = $('fc-front-hanzi');
  if (actualMode === 'hanzi') {
    frontHanzi.textContent = simplified;
    frontHanzi.style.fontSize = '88px';
  } else if (actualMode === 'pinyin') {
    frontHanzi.textContent = word.pinyin || simplified;
    frontHanzi.style.fontSize = '2rem';
  } else {
    // id mode: tampilkan terjemahan Indonesia
    const firstMeaning = Array.isArray(word.meanings_id) ? word.meanings_id[0] : (word.meanings_id || '');
    frontHanzi.textContent = firstMeaning;
    frontHanzi.style.fontSize = '1.6rem';
  }

  // Badges di muka depan
  const badgesEl = $('fc-front-badges');
  badgesEl.innerHTML = '';
  if (hskLv) {
    const hEl = document.createElement('span');
    hEl.className   = `badge-hsk ${hskClass(hskLv)}`;
    hEl.textContent = hskLabel(hskLv);
    badgesEl.appendChild(hEl);
  }
  const card  = FC.srsData[id];
  const isNew = !card || card.reps === 0;
  const typeBadge = document.createElement('span');
  typeBadge.className   = 'tag';
  typeBadge.textContent = isNew ? '✦ Baru' : '↻ Ulang';
  typeBadge.style.fontSize = '0.65rem';
  badgesEl.appendChild(typeBadge);

  // Hint (tersembunyi dulu)
  const hintEl = $('fc-front-hint');
  hintEl.classList.remove('visible');
  const radical = word.radical;
  const stroke  = word.stroke_count;
  let hintText  = '';
  if (radical) hintText += 'Radikal: ' + radical;
  if (stroke)  hintText += (hintText ? '  ·  ' : '') + stroke + ' goresan';
  if (actualMode !== 'hanzi') hintText = simplified + (hintText ? '  ·  ' + hintText : '');
  hintEl.textContent = hintText;

  // ── MUKA BELAKANG (Fix #10 + Fix B6) ──
  // Hanzi besar — SELALU tampil di belakang kartu, apapun mode pertanyaannya.
  // Penguatan visual: melihat hanzi lagi setelah menjawab memperkuat memori.
  const backHanzi = $('fc-back-hanzi');
  backHanzi.textContent = simplified;
  backHanzi.classList.remove('hidden');

  $('fc-back-pinyin').textContent   = word.pinyin || '';
  $('fc-back-bopomofo').textContent = word.bopomofo ? `(${word.bopomofo})` : '';

  // Arti Indonesia
  const meaningsEl = $('fc-back-meanings');
  meaningsEl.innerHTML = '';
  const mArr = Array.isArray(word.meanings_id) ? word.meanings_id : [word.meanings_id || ''];
  mArr.slice(0, 5).forEach((m, i) => {
    const div = document.createElement('div');
    div.className = 'fc-back-meaning-item';
    div.innerHTML = `<span class="fc-back-meaning-num">${i + 1}.</span><span>${escHtml(m)}</span>`;
    meaningsEl.appendChild(div);
  });

  // Arti Inggris singkat (Fix #10)
  const enEl = $('fc-back-en');
  const enArr = Array.isArray(word.meanings_en) ? word.meanings_en : [];
  enEl.textContent = enArr.length ? 'EN: ' + enArr.slice(0, 3).join(', ') : '';

  // Bantu Ingat (mnemonic dekomposisi karakter) -- reuse data etimologi
  renderFcMnemonic(word);

  // Komponen karakter (formula 日+月=明, butuh ≥2 komponen tercatat) +
  // tombol Animasikan Goresan (Tier 3, animasi kuas asli via Hanzi Writer,
  // berlaku utk kata apapun -- multi-karakter dianimasikan per-karakter
  // berurutan lewat playFcStrokeOrder()).
  const compEl = $('fc-back-components');
  const strokeBtnEl = $('fc-back-stroke-btn');
  const hwMultiEl = $('fc-hanzi-writer-multi');
  if (hwMultiEl) { hwMultiEl.classList.add('hidden'); hwMultiEl.innerHTML = ''; }
  const comps  = word.components || [];
  const isSingleChar = simplified.length === 1;

  if (comps.length >= 2 && isSingleChar) {
    compEl.innerHTML = comps
      .map((c, i) => `<span class="fc-back-comp-char" id="fc-comp-${i}">${escHtml(c)}</span>`)
      .join('<span style="color:var(--text-muted)"> + </span>') +
      `<span style="color:var(--text-muted)"> = </span>` +
      `<span class="fc-back-comp-char" style="color:var(--text-main)">${escHtml(simplified)}</span>`;
    compEl.style.display = 'flex';
  } else {
    compEl.innerHTML = '';
    compEl.style.display = 'none';
  }

  if (strokeBtnEl) strokeBtnEl.classList.remove('hidden'); // berlaku utk semua kata

  /* Format daftar lawan kata/sinonim jadi "hanzi (pinyin) - arti", bukan
     hanzi polos seperti sebelumnya. Lookup pinyin/arti offline dari
     FC.allWords sendiri (reuse FC.wordBySimplified yang sudah dipakai
     Jebakan Lawan Kata/Sinonim -- dibangun lazy kalau belum ada). Kalau
     kata terkait tidak ketemu (jarang), fallback aman ke hanzi saja. */
  function fcRelWordsHtml(words) {
    if (!FC.wordBySimplified) {
      FC.wordBySimplified = {};
      (FC.allWords || []).forEach(w => { FC.wordBySimplified[w.simplified] = w; });
    }
    return words.map(w => {
      const hit = FC.wordBySimplified[w];
      const meaning = hit ? (Array.isArray(hit.meanings_id) ? hit.meanings_id[0] : hit.meanings_id) : '';
      const detail = hit ? [hit.pinyin, meaning].filter(Boolean).join(' - ') : '';
      return escHtml(w) + (detail ? ` (${escHtml(detail)})` : '');
    }).join(', ');
  }

  // Meta info (Fix #10: tambah HSK; tambahan: Antonim + Fonetik)
  const metaEl = $('fc-back-meta');
  metaEl.innerHTML = '';
  const antonyms = Array.isArray(word.antonyms) ? word.antonyms.filter(Boolean) : [];
  const synonyms = Array.isArray(word.synonyms) ? word.synonyms.filter(Boolean) : [];
  const phoneticComps = (FC.phoneticReverse && FC.phoneticReverse[id]) || [];
  const metaItems = [
    hskLv                  ? `<strong>HSK:</strong> ${hskLabel(hskLv)}` : null,
    word.radical           ? `<strong>Radikal:</strong> ${escHtml(word.radical)}` : null,
    word.stroke_count      ? `<strong>Goresan:</strong> ${word.stroke_count}` : null,
    word.structure         ? `<strong>Struktur:</strong> ${escHtml(word.structure)}` : null,
    Array.isArray(word.pos) && word.pos.length
                           ? `<strong>Kelas:</strong> ${word.pos.join(', ')}` : null,
    antonyms.length         ? `<strong>Lawan kata:</strong> ${fcRelWordsHtml(antonyms)}` : null,
    synonyms.length         ? `<strong>Sinonim:</strong> ${fcRelWordsHtml(synonyms)}` : null,
    phoneticComps.length    ? `<strong>Fonetik:</strong> ${phoneticComps.map(escHtml).join(', ')}` : null,
  ].filter(Boolean);
  metaItems.forEach(html => {
    const span = document.createElement('span');
    span.className = 'fc-back-meta-item';
    span.innerHTML = html;
    metaEl.appendChild(span);
  });

  // Cross-link ke bacaan berjenjang yang mengandung kata ini (Tier baru).
  // Async lazy-load index -- pakai penjaga FC.currentWord !== word supaya
  // tidak salah render kalau رسلان sudah pindah kartu selagi fetch berjalan.
  const bacaanEl = $('fc-back-bacaan');
  if (bacaanEl) {
    bacaanEl.style.display = 'none';
    bacaanEl.innerHTML = '';
    loadFcReadingIndex().then(idx => {
      if (FC.currentWord !== word) return;
      const matches = idx[simplified] || [];
      if (!matches.length) return;
      const sorted = [...matches]
        .sort((a, b) => Math.abs((a.level || 0) - (hskLv || 0)) - Math.abs((b.level || 0) - (hskLv || 0)))
        .slice(0, 5);
      bacaanEl.innerHTML = '<div class="fc-back-bacaan-label">📖 Muncul di bacaan:</div>' +
        sorted.map(p =>
          `<button class="fc-back-bacaan-item" onclick="event.stopPropagation(); openReadingFromFc('${p.id}')">` +
          `${escHtml(p.title)} <span style="color:var(--text-muted)">(HSK ${p.level})</span></button>`
        ).join('');
      bacaanEl.style.display = 'flex';
    });
  }

  // Update label interval tombol SRS
  updateSrsButtonLabels(id);

  // Sesuaikan tinggi kartu mengikuti konten TERTINGGI (depan/belakang).
  // Wajah kartu posisinya position:absolute (supaya bisa flip 3D), jadi
  // tidak otomatis mendorong tinggi .fc-card-inner -- tanpa ini, wajah
  // belakang yang lebih panjang (pinyin+arti+komponen+meta) akan tumpang
  // tindih/menutupi tombol SRS & "Kirim ke Word Builder" di bawahnya.
  requestAnimationFrame(() => {
    const inner = $('fc-card-inner');
    const front = $('fc-card-front');
    const back  = $('fc-card-back');
    const tallest = Math.max(260, front.scrollHeight, back.scrollHeight);
    inner.style.minHeight = tallest + 'px';
  });

  // Tampilkan tombol jawaban, sembunyikan SRS + Kirim ke Word Builder
  $('fc-show-wrap').classList.remove('hidden');
  $('fc-srs-wrap').classList.add('hidden');
  $('fc-shortcut-hint').style.opacity = '0.6';
  $('btn-send-wb').classList.add('hidden');

  // Update progress & stats
  updateTopbar();
}


/* ── BANTU INGAT (mnemonic dekomposisi karakter) ────────────────
   Pola sama seperti kamus/kamus-data.js + kamus-detail.js, dipindah ke
   sini supaya rasa hafalan yang sudah رسلان bangun di Kamus juga hadir
   saat SRS review -- momen paling penting untuk penguatan ingatan.
   Prioritas sumber makna karakter tunggal:
     1) data/char_etymology_id.json (gloss_id + asal_usul_id) -- akurat
     2) FC.allWords entri 1-karakter (meanings_id[0]) -- fallback */
FC.charEtymology    = null;
FC.charMeaningIndex  = null;

function loadFcCharEtymology() {
  fetch('data/char_etymology_id.json')
    .then(res => res.ok ? res.json() : {})
    .then(data => { FC.charEtymology = data; })
    .catch(() => { FC.charEtymology = {}; }); // gagal senyap -- fitur mnemonic tetap jalan pakai fallback (2)
}


function buildFcCharMeaningIndex() {
  const idx = {};
  (FC.allWords || []).forEach(w => {
    const s = w.simplified || w.id;
    if (s && s.length === 1 && w.meanings_id && w.meanings_id.length) {
      if (!idx[s]) idx[s] = w.meanings_id[0];
    }
  });
  FC.charMeaningIndex = idx;
}


function getFcCharMeaning(char) {
  if (FC.charEtymology && FC.charEtymology[char] && FC.charEtymology[char].gloss_id) {
    return FC.charEtymology[char].gloss_id;
  }
  if (!FC.charMeaningIndex) buildFcCharMeaningIndex();
  if (FC.charMeaningIndex && FC.charMeaningIndex[char]) {
    return FC.charMeaningIndex[char];
  }
  return null;
}


function renderFcMnemonic(word) {
  const box = $('fc-back-mnemonic');
  if (!box) return;

  const simplified = word.simplified || word.id || '';
  if (simplified.length < 2) { box.classList.add('hidden'); return; }

  const chars = [...simplified];
  const resolved = [];
  chars.forEach(ch => {
    const meaning = getFcCharMeaning(ch);
    if (meaning) {
      const etym = FC.charEtymology && FC.charEtymology[ch];
      resolved.push({ char: ch, meaning, note: etym ? etym.asal_usul_id : null });
    }
  });

  // Sama seperti di Kamus: minimal 2 karakter berhasil resolve supaya
  // rantai mnemonic-nya cukup bermakna, bukan cuma 1 fragmen kosong.
  if (resolved.length < 2) { box.classList.add('hidden'); return; }

  const mainMeaning = Array.isArray(word.meanings_id) ? word.meanings_id[0] : (word.meanings_id || '');
  const chain = resolved.map(r => `${escHtml(r.char)} (${escHtml(r.meaning)})`).join(' + ');
  const cards = resolved.map(r => {
    const noteHtml = r.note
      ? `<div style="font-size:0.72rem;color:var(--text-muted);margin-top:3px">📜 ${escHtml(r.note)}</div>`
      : '';
    return `<div style="margin-top:6px"><strong style="color:var(--gold)">${escHtml(r.char)}</strong> — ${escHtml(r.meaning)}${noteHtml}</div>`;
  }).join('');

  box.innerHTML = `💡 <strong style="color:var(--gold)">Bantu ingat:</strong> ${chain} → ${escHtml(mainMeaning)}${cards}`;
  box.classList.remove('hidden');
}


/* ── ANIMASI GORESAN (Tier 3): kuas asli via Hanzi Writer, dengan
   fallback ke highlight urutan komponen kalau data goresan presisi
   tidak tersedia untuk karakter ini (data dari
   data/hanzi_writer_data.json, disaring cuma utk kata 1-karakter). ── */
let FC_HANZI_WRITER_DATA = null;
let fcHanziWriterDataPromise = null;

function loadFcHanziWriterData() {
  if (fcHanziWriterDataPromise) return fcHanziWriterDataPromise;
  fcHanziWriterDataPromise = fetch('data/hanzi_writer_data.json')
    .then(res => res.ok ? res.json() : {})
    .then(data => { FC_HANZI_WRITER_DATA = data; return data; })
    .catch(e => {
      console.warn('data/hanzi_writer_data.json tidak tersedia:', e);
      FC_HANZI_WRITER_DATA = {};
      return {};
    });
  return fcHanziWriterDataPromise;
}


function playFcStrokeOrder() {
  if (!FC.currentWord) return;
  const word  = FC.currentWord;
  const wordStr = word.simplified || word.id;

  loadFcHanziWriterData().then(data => {
    const chars   = Array.from(wordStr);
    const multiEl = $('fc-hanzi-writer-multi');
    if (!multiEl) return;

    // 1 karakter DAN datanya tidak ada -- fallback ke highlight komponen
    if (chars.length === 1 && (!data[chars[0]] || !window.HanziWriter)) {
      multiEl.classList.add('hidden');
      playFcComponentOrder();
      return;
    }

    // Multi-karakter tapi tidak ada satupun datanya -- tidak ada yang
    // bisa dianimasikan
    if (!chars.some(ch => data[ch]) || !window.HanziWriter) {
      multiEl.classList.add('hidden');
      return;
    }

    multiEl.innerHTML = '';
    multiEl.classList.remove('hidden');

    const slots = chars.map(ch => {
      const slot = document.createElement('div');
      slot.className = 'hanzi-writer-slot';
      multiEl.appendChild(slot);
      return { ch, slot };
    });

    let idx = 0;
    function playNext() {
      if (idx >= slots.length) return;
      const { ch, slot } = slots[idx];
      const charData = data[ch];

      if (charData) {
        slot.innerHTML = '';
        const writer = HanziWriter.create(slot, ch, {
          width: chars.length > 1 ? 90 : 130,
          height: chars.length > 1 ? 90 : 130,
          padding: 6,
          strokeAnimationSpeed: 1,
          delayBetweenStrokes: 220,
          strokeColor: '#c9a84c',
          outlineColor: 'rgba(255,255,255,0.15)',
          charDataLoader: () => charData,
        });
        writer.animateCharacter({
          onComplete: () => { idx++; setTimeout(playNext, 350); },
        });
      } else {
        slot.innerHTML = `<div class="hanzi-writer-nodata" title="Data goresan tidak tersedia">${escHtml(ch)}</div>`;
        idx++;
        setTimeout(playNext, 150);
      }
    }
    playNext();
  });
}


/* ── FALLBACK LAMA: highlight urutan komponen ──────────────────
   Dipakai playFcStrokeOrder() di atas kalau data goresan presisi tidak
   tersedia untuk karakter ini. Highlight sesuai array `components` apa
   adanya -- prinsip urutan komponen, bukan goresan kuas presisi. */
function playFcComponentOrder() {
  if (!FC.currentWord) return;
  const comps = FC.currentWord.components || [];
  if (comps.length < 2) return;

  const btn = $('fc-back-stroke-btn');
  if (btn) btn.disabled = true;

  comps.forEach((_, i) => {
    const span = $('fc-comp-' + i);
    if (span) span.classList.remove('stroke-order-active', 'stroke-order-done');
  });

  let i = 0;
  const STEP_MS = 650;
  const step = () => {
    if (i > 0) {
      const prev = $('fc-comp-' + (i - 1));
      if (prev) { prev.classList.remove('stroke-order-active'); prev.classList.add('stroke-order-done'); }
    }
    if (i < comps.length) {
      const cur = $('fc-comp-' + i);
      if (cur) cur.classList.add('stroke-order-active');
      i++;
      setTimeout(step, STEP_MS);
    } else if (btn) {
      btn.disabled = false;
    }
  };
  step();
}


/* ── LABEL INTERVAL TOMBOL SRS ─────────────────────────────── */
function updateSrsButtonLabels(wordId) {
  const card   = FC.srsData[wordId] || {
    interval: 0, ease: SRS.EASE_DEFAULT, reps: 0, lapses: 0
  };
  const ivals  = srsPreviewIntervals(card);
  const labels = ['days-lagi', 'days-sulit', 'days-baik', 'days-mudah'];
  labels.forEach((id, i) => {
    const el = $(id);
    if (el) el.textContent = formatInterval(ivals[i]);
  });
}


/* ── TAMPILKAN JAWABAN ─────────────────────────────────────── */
function showAnswer() {
  if (FC.isFlipped) return;
  FC.isFlipped = true;

  $('fc-card-inner').classList.add('flipped');
  $('fc-show-wrap').classList.add('hidden');
  $('fc-srs-wrap').classList.remove('hidden');
  $('btn-send-wb').classList.remove('hidden');
}


/* ── TAMPILKAN HINT ────────────────────────────────────────── */
function showHint() {
  if (FC.hintShown) return;
  FC.hintShown = true;
  $('fc-front-hint').classList.add('visible');
}


/* ── RATING KARTU (SRS) ────────────────────────────────────── */
function rateCard(rating) {
  if (!FC.isFlipped) return;

  const word = FC.currentWord;
  const id   = word.id || word.simplified;

  // Pastikan kartu ada di SRS data
  srsInitCard(id, FC.srsData);
  const oldCard = FC.srsData[id];
  const isNew   = oldCard.reps === 0;

  // Hitung interval baru
  const updated = srsCalculate(oldCard, rating);
  FC.srsData[id] = updated;
  srsSave(FC.srsData);

  // Catat salah
  if (rating === 0) {
    FC.wrongSet.add(id);
    wrongSave(FC.wrongSet);
    FC.sessionAgain++;
  } else if (rating >= 2) {
    FC.sessionCorrect++;
    // Hapus dari wrong jika berhasil
    if (rating === 3 && FC.wrongSet.has(id)) {
      FC.wrongSet.delete(id);
      wrongSave(FC.wrongSet);
    }
  }

  if (isNew) FC.sessionNew++;
  else FC.sessionReview++;

  // Jika "Lagi" (atau mode mastery + rating < 3), masukkan kembali ke antrian
  const shouldReinsert = rating === 0 ||
    (FC.sessionMode === 'mastery' && rating < 3);

  if (shouldReinsert) {
    const insertAt = Math.min(FC.queueIndex + 4, FC.queue.length);
    FC.queue.splice(insertAt, 0, word);
  }

  // Maju ke kartu berikutnya
  FC.queueIndex++;
  setTimeout(() => renderCurrentCard(), 180);
}


/* ── KIRIM KE WORD BUILDER (Fix #11) ───────────────────────── */
function sendToWordBuilder() {
  if (!FC.currentWord) return;
  try {
    localStorage.setItem('wb_ref_word', JSON.stringify(FC.currentWord));
    // Bug lama: cuma menyimpan ke localStorage + toast, tidak pernah pindah
    // halaman -- رسلان harus klik navbar "Word Builder" sendiri secara
    // manual. Sekarang langsung navigasi; wordbuilder.html sudah otomatis
    // membuka pola yang cocok lewat consumeRefWord() saat halaman dimuat.
    window.location.href = 'wordbuilder.html';
  } catch (e) {
    showToast('Gagal menyimpan ke Word Builder', 'error');
  }
}


/* ── UPDATE TOPBAR ─────────────────────────────────────────── */
function updateTopbar() {
  const total   = FC.queue.length;
  const current = FC.queueIndex + 1;
  const done    = FC.queueIndex;
  const pct     = total > 0 ? Math.round((done / total) * 100) : 0;

  $('fc-session-info').textContent = `${current} / ${total}`;
  $('fc-progress').style.width     = pct + '%';

  // Hitung sisa baru vs review di antrian
  let remNew = 0, remReview = 0;
  for (let i = FC.queueIndex; i < FC.queue.length; i++) {
    const w  = FC.queue[i];
    const id = w.id || w.simplified;
    const c  = FC.srsData[id];
    if (!c || c.reps === 0) remNew++;
    else remReview++;
  }

  $('stat-new').textContent    = remNew + ' baru';
  $('stat-review').textContent = remReview + ' ulang';
  $('stat-done').textContent   = done + ' selesai';
}


/* ── SELESAI SESI ──────────────────────────────────────────── */
function finishSession() {
  showScreen('done');

  $('done-val-total').textContent   = FC.sessionTotal;
  $('done-val-correct').textContent = FC.sessionCorrect;
  $('done-val-again').textContent   = FC.sessionAgain;

  const pct = FC.sessionTotal > 0
    ? Math.round((FC.sessionCorrect / FC.sessionTotal) * 100)
    : 0;

  $('done-sub').textContent =
    `Akurasi sesi ini: ${pct}% — ` +
    `${FC.sessionNew} kartu baru, ${FC.sessionReview} kartu ulang.`;

  // Update due count di sidebar
  FC.srsData = srsLoad();
  updateAllDueCounts();
}

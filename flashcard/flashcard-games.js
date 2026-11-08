/* ═══════════════════════════════════════════════════════════════
   flashcard-games.js — Mode game: Jebakan Nada (audio), deck
   Antonim/Sinonim, engine game tone/pilihan ganda, "Pilih yang
   Tepat" (nuance), "Tebak Pola Kata" (pola pembentukan kata)
═══════════════════════════════════════════════════════════════ */
'use strict';

/* Peta pola -> label Indonesia -- SENGAJA DUPLIKAT dari kamus-pola.js
   (bukan di-share lewat shared/core.js) supaya modul ini tetap berdiri
   sendiri, sama seperti kamus-pola.js berdiri sendiri dari kamus.html
   lain -- flashcard.html & kamus.html adalah dua halaman terpisah tanpa
   state bersama. Kalau daftar 6 kategori pernah berubah, ingat update
   di DUA tempat: sini dan kamus/kamus-pola.js. */
const POLA_LABEL = {
  '联合式': { singkat: 'Koordinatif', deskripsi: 'dua unsur setara/sinonim' },
  '偏正式': { singkat: 'Modifier–Inti', deskripsi: 'unsur 1 menerangkan unsur 2' },
  '动宾式': { singkat: 'Verba–Objek', deskripsi: 'unsur 1 tindakan, unsur 2 sasaran' },
  '主谓式': { singkat: 'Subjek–Predikat', deskripsi: 'unsur 1 pelaku, unsur 2 keadaan/aksi' },
  '补充式': { singkat: 'Verba–Pelengkap', deskripsi: 'unsur 2 melengkapi hasil/arah unsur 1' },
  'lainnya': { singkat: 'Lainnya', deskripsi: 'serapan / kata fungsi / tidak baku pola' }
};
const POLA_KEYS = Object.keys(POLA_LABEL);


/* ── B5b: bangun pool Jebakan Nada (LAMA -- tidak lagi dipakai) ──────
   Dulu dipakai buat deck flip-card SRS biasa. Sekarang 'tone-trap'
   di-intercept lebih awal di selectDeck() dan pakai buildToneTrapGroups()
   di bawah (mode game audio). Fungsi ini dibiarkan (tidak dihapus) supaya
   tidak mengubah signature buildDeckQueue kalau ada kode lain yang masih
   bergantung padanya, tapi praktiknya sudah dead code untuk 'tone-trap'. */
function buildToneTrapPool(allWords) {
  // Kelompokkan: pinyin tanpa nada → array kata
  const map = {};
  for (const w of allWords) {
    const py = (w.pinyin_numeric || w.pinyin || '').toLowerCase()
      .replace(/\s+/g, '').replace(/[1-5]/g, '');
    if (!py) continue;
    if (!map[py]) map[py] = [];
    map[py].push(w);
  }
  // Hanya kelompok yang punya ≥2 nada berbeda
  const pool = [];
  for (const [, group] of Object.entries(map)) {
    if (group.length < 2) continue;
    const tones = new Set(
      group.map(w => (w.pinyin_numeric || '').replace(/[^1-5]/g, '') || '0')
    );
    if (tones.size >= 2) pool.push(...group);
  }
  return pool;
}


/* ── GAME AUDIO: JEBAKAN NADA (Tier 3) ──────────────────────────────
   Reuse mekanisme "dengar → pilih" dari tone.html (mode Pilih Hanzi):
   dengarkan audio, lalu pilih hanzi yang cocok dari beberapa opsi
   minimal-pair (pinyin toneless sama, nada beda). Ini BUKAN flip-card
   SRS biasa -- murni skor benar/salah sesi, tidak menyentuh SRS. */

function buildToneTrapGroups(allWords) {
  const map = {};
  for (const w of allWords) {
    const py = (w.pinyin_numeric || w.pinyin || '').toLowerCase()
      .replace(/\s+/g, '').replace(/[1-5]/g, '');
    if (!py) continue;
    if (!map[py]) map[py] = [];
    map[py].push(w);
  }
  const groups = [];
  for (const [, group] of Object.entries(map)) {
    if (group.length < 2) continue;
    const tones = new Set(
      group.map(w => (w.pinyin_numeric || '').replace(/[^1-5]/g, '') || '0')
    );
    if (tones.size >= 2) groups.push(group);
  }
  return groups;
}


/* ── Game Audio: "👀 Karakter Mirip" (E.0.3, kemiripan BENTUK TULISAN) ──
   Beda dari buildToneTrapGroups (kelompok pinyin sama, nada beda): ini
   kelompok KARAKTER MIRIP BENTUK dari data/confusion_groups.json (mis.
   己/已/巳), tidak ada hubungannya dgn pinyin/nada. Tiap grup dilengkapi
   "note" (penjelasan pembeda bentuk) yg dipakai sbg feedback edukatif
   setelah jawab -- beda dari tone-trap yg tidak punya keterangan serupa. */
function buildConfusionGroups(allWords) {
  if (!FC.wordBySimplified) {
    FC.wordBySimplified = {};
    allWords.forEach(w => { FC.wordBySimplified[w.simplified] = w; });
  }
  const raw = FC.confusionGroupsRaw || [];
  const groups = [];
  for (const g of raw) {
    const charsStr = [g.character].concat(g.confusable_with || []);
    const chars = charsStr.map(c => FC.wordBySimplified[c]).filter(Boolean);
    if (chars.length >= 2) {
      groups.push({ chars, note: g.note || '' });
    }
  }
  return groups;
}


function startAudioGame(mode) {
  const tg = FC.toneGame;
  tg.mode = mode;

  if (mode === 'tonepairs') {
    if (!tg.groups.length) return;
    tg.order = shuffle([...Array(tg.groups.length).keys()]);

  } else if (mode === 'antonym') {
    tg.pairs = buildAntonymPairs(FC.queue);
    if (!tg.pairs.length) {
      showToast('Tidak ada kata di deck ini yang lawan katanya bisa ditemukan datanya.', 'info');
      return;
    }
    tg.order = shuffle([...Array(tg.pairs.length).keys()]);

  } else if (mode === 'synonym') {
    tg.pairs = buildSynonymPairs(FC.queue);
    if (!tg.pairs.length) {
      showToast('Tidak ada kata di deck ini yang sinonimnya bisa ditemukan datanya.', 'info');
      return;
    }
    tg.order = shuffle([...Array(tg.pairs.length).keys()]);

  } else if (mode === 'nuance') {
    // Fix bug jumlah kartu diabaikan: dulu SELALU build ulang dari
    // FC.nuancePairs penuh (2558 soal) di sini, mengabaikan potongan yg
    // sudah dibuat selectDeck() sesuai FC.sessionCardLimit. Sekarang pakai
    // versi yg sudah dipotong itu (tg.nuanceQuestions) kalau ada; fallback
    // build ulang cuma sbg jaga-jaga (mis. dipanggil di luar alur normal).
    tg.nuanceQuestions = (tg.nuanceQuestions && tg.nuanceQuestions.length)
      ? tg.nuanceQuestions
      : buildNuanceQuestions(FC.nuancePairs || []);
    if (!tg.nuanceQuestions.length) {
      showToast('Belum ada soal pasangan nuansa yang bisa dimainkan.', 'info');
      return;
    }
    tg.order = shuffle([...Array(tg.nuanceQuestions.length).keys()]);

  } else if (mode === 'pola') {
    // Fix sama spt 'nuance' di atas (dulu build ulang dari FC.polaEntries
    // penuh, 8867 soal).
    tg.polaQuestions = (tg.polaQuestions && tg.polaQuestions.length)
      ? tg.polaQuestions
      : buildPolaQuestions(FC.polaEntries || []);
    if (!tg.polaQuestions.length) {
      showToast('Belum ada soal pola pembentukan kata yang bisa dimainkan.', 'info');
      return;
    }
    tg.order = shuffle([...Array(tg.polaQuestions.length).keys()]);

  } else if (mode === 'confusion') {
    // (E.0.3) Karakter Mirip -- pakai tg.confusionGroups yg sudah
    // dipotong sessionCardLimit di selectDeck() (pola sama spt tonepairs,
    // yg juga baca tg.groups langsung tanpa build ulang di sini).
    if (!tg.confusionGroups || !tg.confusionGroups.length) {
      showToast('Belum ada soal Karakter Mirip yang bisa dimainkan.', 'info');
      return;
    }
    tg.order = shuffle([...Array(tg.confusionGroups.length).keys()]);

  } else {
    // generic: pool = antrian deck yang barusan dipilih (FC.queue)
    tg.pool = FC.queue;
    if (!tg.pool.length) return;
    tg.order = shuffle([...Array(tg.pool.length).keys()]);
  }

  tg.active = true;
  tg.idx    = 0;
  tg.score  = { ok: 0, bad: 0 };
  updateToneGameScore();

  $('fc-topbar').classList.remove('hidden');
  $('fc-deck-name').textContent = FC.deckName + (mode !== 'tonepairs' ? ' 🎮' : '');
  $('btn-start-session').classList.add('hidden');

  showScreen('session');

  // Sembunyikan UI flip-card biasa, tampilkan UI game
  $('qm-toggle').classList.add('hidden');
  $('fc-card-wrap').classList.add('hidden');
  $('fc-show-wrap').classList.add('hidden');
  $('fc-srs-wrap').classList.add('hidden');
  $('fc-shortcut-hint').classList.add('hidden');
  $('btn-send-wb').classList.add('hidden');
  $('tone-game-wrap').classList.remove('hidden');

  renderToneGameQuestion();
}


/* ── Bangun pasangan Lawan Kata yang antonimnya bisa di-resolve jadi
   objek kata utuh (supaya pinyin/terjemahan/audio-nya ada) ──────── */
function buildAntonymPairs(pool) {
  if (!FC.wordBySimplified) {
    FC.wordBySimplified = {};
    FC.allWords.forEach(w => { FC.wordBySimplified[w.simplified] = w; });
  }
  const pairs = [];
  for (const w of pool) {
    const ants = Array.isArray(w.antonyms) ? w.antonyms : (w.antonyms ? [w.antonyms] : []);
    for (const a of ants) {
      const aWord = FC.wordBySimplified[a];
      if (aWord) { pairs.push({ word: w, antonym: aWord }); break; }
    }
  }
  return pairs;
}


/* ── Sama seperti buildAntonymPairs, tapi untuk relasi Sinonim ────── */
function buildSynonymPairs(pool) {
  if (!FC.wordBySimplified) {
    FC.wordBySimplified = {};
    FC.allWords.forEach(w => { FC.wordBySimplified[w.simplified] = w; });
  }
  const pairs = [];
  for (const w of pool) {
    const syns = Array.isArray(w.synonyms) ? w.synonyms : (w.synonyms ? [w.synonyms] : []);
    for (const s of syns) {
      const sWord = FC.wordBySimplified[s];
      if (sWord) { pairs.push({ word: w, synonym: sWord }); break; }
    }
  }
  return pairs;
}


/* ── Bangun soal "Pilih yang Tepat" (near-synonym, Tier 4) dari
   data/nuance_pairs.json ────────────────────────────────────────────
   Beda dari buildAntonymPairs/buildSynonymPairs: tidak butuh FC.allWords
   sama sekali -- nuance_pairs.json sudah lengkap berdiri sendiri (pinyin,
   contoh kalimat, terjemahan sudah ada langsung di datanya).

   Tiap KATA dalam comparison[] satu pasangan jadi 1 soal terpisah
   (kalimat rumpang dari example_cn kata itu, opsi jawaban = SEMUA kata
   di comparison[] pasangan yang sama -- 2 atau lebih, SENGAJA TIDAK
   dipadding ke 4 seperti game lain, karena intinya justru menguji beda
   nuansa antar kata-kata itu sendiri, bukan tebak di antara kata acak).

   Pasangan dengan hanzi identik di comparison[] (kasus 借 dua arah
   pinjam) OTOMATIS DILEWATI -- tidak ada yang bisa "dipilih" secara
   visual kalau pilihannya kelihatan sama persis. Pasangan itu tetap
   berfungsi normal di panel Kamus, cuma tidak dipakai di game ini. */
function buildNuanceQuestions(pairs) {
  if (!Array.isArray(pairs)) return [];
  const questions = [];

  pairs.forEach(pair => {
    const comps = pair.comparison || [];
    const uniqueWords = new Set(comps.map(c => c.word));
    if (comps.length < 2 || uniqueWords.size < comps.length) return;

    comps.forEach(target => {
      if (!target.word || !target.example_cn) return;
      const blanked = target.example_cn.replace(target.word, '___');
      if (blanked === target.example_cn) return; // kata target tidak ketemu di kalimatnya sendiri -- data tidak konsisten, lewati

      questions.push({
        pairId:         pair.id,
        sentence:       blanked,
        translation:    target.example_id || '',
        correctWord:    target.word,
        correctPinyin:  target.pinyin || '',
        options:        comps.map(c => ({ simplified: c.word, id: c.word, pinyin: c.pinyin })),
      });
    });
  });

  return questions;
}


/* ── Bangun soal "🧩 Tebak Pola Kata" dari data/kata_majemuk_pola.json ──
   Beda dari buildNuanceQuestions: tiap ENTRY (1 kata) langsung jadi 1
   soal (bukan per-item di dalam grup). Prompt = kata itu sendiri (boleh
   didengar audionya -- BEDA dari mode nuance, di sini mendengar
   pengucapan kata TIDAK membocorkan jawaban, karena yang ditanya adalah
   kategori struktur gramatikalnya, bukan identitas katanya). Opsi
   jawaban SELALU 6 kategori penuh (bukan subset acak) -- jumlahnya
   sudah tetap & kecil, jadi lebih mendidik kalau رسلان lihat semua
   pilihan tiap kali, biar lama-lama hafal keenamnya.

   Pinyin kata (kalau ada) diambil dari FC.wordBySimplified -- data
   kata_majemuk_pola.json sendiri tidak menyimpan pinyin. */
function buildPolaQuestions(entries) {
  if (!Array.isArray(entries)) return [];
  if (!FC.wordBySimplified && Array.isArray(FC.allWords)) {
    FC.wordBySimplified = {};
    FC.allWords.forEach(w => { FC.wordBySimplified[w.simplified] = w; });
  }

  const questions = [];
  entries.forEach(entry => {
    if (!entry || !entry.word || !entry.pola || !POLA_LABEL[entry.pola]) return;
    const wordObj = (FC.wordBySimplified && FC.wordBySimplified[entry.word]) || null;

    questions.push({
      word:           entry.word,
      pinyin:         wordObj ? (wordObj.pinyin || '') : '',
      correctPola:    entry.pola,
      correctLabel:   POLA_LABEL[entry.pola].singkat,
      keterangan:     entry.keterangan_id || '',
    });
  });

  return questions;
}


/* ── Render prompt khusus "Pilih yang Tepat": kalimat rumpang + terjemahan.
   TIDAK reuse renderGamePrompt() -- itu selalu tampilkan tombol 🔊 Dengar
   yang mengucapkan promptWord, dan di sini promptWord justru KATA
   JAWABANNYA sendiri (beda dari antonym/synonym di mana promptWord adalah
   kata LAIN dari jawabannya) -- kalau dipaksa reuse, tombol dengar itu
   akan membocorkan jawaban sebelum dijawab. Makanya dibuat fungsi sendiri,
   sengaja TANPA tombol audio sama sekali. ── */
function renderNuancePrompt(q) {
  const area = $('tg-prompt-area');
  area.innerHTML = `
    <div class="tg-prompt-sentence">${escHtml(q.sentence)}</div>
    <div class="tg-prompt-sentence-hint">Pilih kata yang tepat mengisi bagian rumpang</div>
  `;
}


/* ── Resolusi format 'acak' KHUSUS Karakter Mirip -- 'hanzi' sengaja
   dikecualikan (beda dari resolveGameFormat() generik yg dipakai
   antonym/synonym). Alasan: jawaban mode ini SELALU hanzi (lihat
   renderToneGameQuestion), jadi soal=hanzi + jawaban=hanzi jadi trivial
   (cuma cocokkan gambar yang identik, tidak menguji apapun). Juga jaga-
   jaga kalau FC.confusionQFormat kebetulan masih tersimpan 'hanzi' dari
   sesi lama (sebelum opsi ini dibuang dari dropdown) -- diperlakukan
   sama spt 'acak'. */
function resolveConfusionFormat(setting) {
  const choices = ['pinyin', 'suara', 'terjemahan'];
  if (!setting || setting === 'acak' || setting === 'hanzi') {
    return choices[Math.floor(Math.random() * choices.length)];
  }
  return setting;
}


/* ── Resolusi format 'acak' jadi salah satu format nyata setiap soal ── */
function resolveGameFormat(setting) {
  if (setting !== 'acak') return setting;
  const choices = ['hanzi', 'pinyin', 'suara', 'terjemahan'];
  return choices[Math.floor(Math.random() * choices.length)];
}


function gameWordMeaning(w) {
  return Array.isArray(w.meanings_id) ? (w.meanings_id[0] || '?') : (w.meanings_id || '?');
}


/* ── Render area prompt (soal) sesuai format ─────────────────────── */
function renderGamePrompt(format, word, hintText) {
  FC.toneGame.promptAudioWord = word;
  const area = $('tg-prompt-area');

  if (format === 'suara') {
    area.innerHTML = `<button class="tone-play-btn" onclick="playGamePromptAudio()" title="Dengarkan">🔊</button>
      <div class="tone-play-hint">${escHtml(hintText || 'Dengarkan, lalu pilih jawabannya')}</div>`;
    return;
  }

  let token;
  if (format === 'pinyin')          token = word.pinyin || '?';
  else if (format === 'terjemahan') token = gameWordMeaning(word);
  else                               token = word.simplified || word.id; // hanzi (default)

  area.innerHTML = `<div class="tg-prompt-token">${escHtml(token)}</div>
    <button class="fc-stroke-btn" onclick="playGamePromptAudio()" style="margin-top:10px">🔊 Dengar</button>`;
}


function playGamePromptAudio() {
  const w = FC.toneGame.promptAudioWord;
  if (w) speak(w.simplified || w.id, { rate: AudioTTS.rate });
}


/* ── Render opsi jawaban sesuai format ────────────────────────────── */
function renderGameOptions(options, format) {
  const optsEl = $('tg-options');
  FC.toneGame.selectedIdx = null;

  if (format === 'suara') {
    // Audio butuh 2 tahap: dengar dulu (boleh berkali-kali, bebas urutan),
    // baru tandai pilihan lewat tombol pilih -- BUKAN sekali klik langsung
    // dianggap jawaban (itu "beli kucing dalam karung", sesuai keluhan رسلان).
    optsEl.innerHTML = options.map((w, i) => `
      <div class="tg-audio-option" data-idx="${i}">
        <button class="tg-audio-play-btn" onclick="previewGameOption(${i})" title="Dengar opsi ini">🔊 Dengar</button>
        <button class="tg-audio-select-btn" onclick="selectGameOption(${i})" title="Tandai sebagai pilihan">
          <span class="tg-select-mark">○</span> Opsi ${i + 1}
        </button>
      </div>`).join('');
    $('tg-confirm-wrap').classList.remove('hidden');
    $('tg-confirm-btn').disabled = true;
    return;
  }

  $('tg-confirm-wrap').classList.add('hidden');

  optsEl.innerHTML = options.map((w, i) => {
    let inner;
    if (format === 'pinyin') {
      inner = `<span class="tg-option-hanzi" style="font-size:1.15rem">${escHtml(w.pinyin || '?')}</span>`;
    } else if (format === 'terjemahan') {
      inner = `<span class="tg-option-hanzi" style="font-size:1rem">${escHtml(gameWordMeaning(w))}</span>`;
    } else if (format === 'pola') {
      // Opsi kategori pola -- w = {pola, label}, bukan objek kata.
      inner = `<span class="tg-option-hanzi" style="font-size:1rem">${escHtml(w.pola)}</span><span class="tg-option-pinyin">${escHtml(w.label)}</span>`;
    } else { // hanzi
      // Mode 'confusion' (Karakter Mirip) sengaja TIDAK tampilkan pinyin
      // di bawah hanzi -- kalau pinyin kelihatan, jawaban jadi trivial
      // (tinggal cocokkan bunyi, tidak menguji bentuk tulisan sama sekali,
      // sesuai koreksi رسلان). Mode lain (antonym/synonym) tetap pinyin.
      const showPinyin = FC.toneGame.mode !== 'confusion';
      inner = `<span class="tg-option-hanzi">${escHtml(w.simplified || w.id)}</span>`
            + (showPinyin ? `<span class="tg-option-pinyin">${escHtml(w.pinyin || '')}</span>` : '');
    }
    return `<button class="tg-option-btn" data-idx="${i}" onclick="answerGame(${i})">${inner}</button>`;
  }).join('');
}


/* ── Preview audio (BUKAN jawab) -- boleh diklik berkali-kali, bebas
   urutan, sebelum رسلان yakin dan menekan tombol pilih ────────────── */
function previewGameOption(idx) {
  const tg = FC.toneGame;
  if (tg.answered || !tg.current) return;
  const w = tg.current.options[idx];
  if (w) speak(w.simplified || w.id, { rate: AudioTTS.rate });
}


/* ── Tandai satu opsi audio sebagai pilihan sementara (belum commit) ── */
function selectGameOption(idx) {
  const tg = FC.toneGame;
  if (tg.answered) return;
  tg.selectedIdx = idx;

  document.querySelectorAll('.tg-audio-option').forEach((el, i) => {
    const isSel = i === idx;
    el.classList.toggle('selected', isSel);
    const mark = el.querySelector('.tg-select-mark');
    if (mark) mark.textContent = isSel ? '●' : '○';
  });
  $('tg-confirm-btn').disabled = false;
}


/* ── Konfirmasi jawaban akhir (cuma dipakai format Suara) ──────────── */
function confirmGameAnswer() {
  const tg = FC.toneGame;
  if (tg.selectedIdx === null || tg.selectedIdx === undefined) return;
  answerGame(tg.selectedIdx);
}


function renderToneGameQuestion() {
  const tg = FC.toneGame;
  if (tg.idx >= tg.order.length) { finishToneGame(); return; }

  let promptWord, correct, options, qFormat, aFormat;

  if (tg.mode === 'tonepairs') {
    const group    = tg.groups[tg.order[tg.idx]];
    const shuffled = shuffle([...group]);
    options    = shuffled.slice(0, Math.min(4, shuffled.length));
    correct    = options[Math.floor(Math.random() * options.length)];
    promptWord = correct;
    qFormat    = 'suara';
    aFormat    = 'hanzi';

  } else if (tg.mode === 'confusion') {
    // (E.0.3, revisi ke-2) Sekarang bentuk SOAL bisa dipilih via dropdown
    // FC.confusionQFormat (hanzi/pinyin/suara/terjemahan/acak) -- sama
    // fleksibilitasnya spt Lawan Kata/Sinonim. TAPI bentuk JAWABAN
    // SENGAJA dikunci 'hanzi', TIDAK ADA dropdown-nya sama sekali --
    // kalau jawaban boleh diganti ke pinyin, soal jadi cuma mencocokkan
    // suara<->pinyin, tidak menguji BENTUK TULISAN sama sekali (padahal
    // itu inti tantangan fitur ini, sesuai koreksi رسلان).
    const group    = tg.confusionGroups[tg.order[tg.idx]];
    const shuffled = shuffle([...group.chars]);
    options    = shuffled.slice(0, Math.min(4, shuffled.length));
    correct    = options[Math.floor(Math.random() * options.length)];
    promptWord = correct;
    qFormat    = resolveConfusionFormat(FC.confusionQFormat || 'acak');
    aFormat    = 'hanzi';
    tg.currentNote = group.note; // dibaca answerGame() utk feedback edukatif

  } else if (tg.mode === 'antonym') {
    const pair = tg.pairs[tg.order[tg.idx]];
    promptWord = pair.word;
    correct    = pair.antonym;
    const distractSource = tg.pairs.filter(p => p.antonym !== correct).map(p => p.antonym);
    const others = shuffle([...new Set(distractSource)]).slice(0, 3);
    // Kalau stok distraktor unik kurang dari 3, tambal dari kata acak lain
    while (others.length < 3 && others.length < FC.allWords.length - 1) {
      const rand = FC.allWords[Math.floor(Math.random() * FC.allWords.length)];
      if (rand !== correct && !others.includes(rand)) others.push(rand);
    }
    options = shuffle([correct, ...others]);
    qFormat = resolveGameFormat(FC.antonymQFormat);
    aFormat = resolveGameFormat(FC.antonymAFormat);

  } else if (tg.mode === 'synonym') {
    const pair = tg.pairs[tg.order[tg.idx]];
    promptWord = pair.word;
    correct    = pair.synonym;
    const distractSource = tg.pairs.filter(p => p.synonym !== correct).map(p => p.synonym);
    const others = shuffle([...new Set(distractSource)]).slice(0, 3);
    while (others.length < 3 && others.length < FC.allWords.length - 1) {
      const rand = FC.allWords[Math.floor(Math.random() * FC.allWords.length)];
      if (rand !== correct && !others.includes(rand)) others.push(rand);
    }
    options = shuffle([correct, ...others]);
    qFormat = resolveGameFormat(FC.synonymQFormat);
    aFormat = resolveGameFormat(FC.synonymAFormat);

  } else if (tg.mode === 'nuance') {
    const q = tg.nuanceQuestions[tg.order[tg.idx]];
    const correctObj = q.options.find(o => o.simplified === q.correctWord);

    // promptWord DISENGAJA diisi correctObj (bukan null) supaya SRS
    // tracking di answerGame() tetap jalan normal (dia baca
    // tg.current.promptWord.id/simplified) -- meski di mode ini
    // "prompt"-nya sebenarnya kalimat, bukan kata tunggal.
    tg.current  = { question: q, promptWord: correctObj, correct: correctObj, options: q.options };
    tg.answered = false;

    $('tg-feedback').innerHTML = '';
    $('tg-next-btn').classList.add('hidden');
    $('tg-progress').textContent = `Soal ${tg.idx + 1} / ${tg.order.length}`;

    renderNuancePrompt(q);
    renderGameOptions(q.options, 'hanzi');
    return; // beda dari mode lain: skip renderGamePrompt/qFormat/aFormat generik di bawah

  } else if (tg.mode === 'pola') {
    const q = tg.polaQuestions[tg.order[tg.idx]];

    // promptWord sintetis (sama trik seperti mode nuance) supaya SRS
    // tracking di answerGame() tetap jalan normal lewat id/simplified.
    const promptWordObj = { simplified: q.word, id: q.word, pinyin: q.pinyin };
    const options = shuffle(POLA_KEYS.map(k => ({ pola: k, label: POLA_LABEL[k].singkat })));
    const correctOption = options.find(o => o.pola === q.correctPola);

    tg.current  = { question: q, promptWord: promptWordObj, correct: correctOption, options };
    tg.answered = false;

    $('tg-feedback').innerHTML = '';
    $('tg-next-btn').classList.add('hidden');
    $('tg-progress').textContent = `Soal ${tg.idx + 1} / ${tg.order.length}`;

    // Reuse renderGamePrompt biasa (format hanzi) -- BEDA dari mode nuance,
    // tombol dengar aman dipakai di sini karena tidak membocorkan jawaban.
    renderGamePrompt('hanzi', promptWordObj, 'Kata ini termasuk pola pembentukan apa?');
    renderGameOptions(options, 'pola');
    return; // beda dari mode lain: skip qFormat/aFormat generik di bawah

  } else {
    // generic
    correct    = tg.pool[tg.order[tg.idx]];
    promptWord = correct;
    const distractSource = tg.pool.length >= 4 ? tg.pool : FC.allWords;
    const others = shuffle(distractSource.filter(w => w !== correct)).slice(0, 3);
    options = shuffle([correct, ...others]);
    qFormat = 'suara';
    aFormat = 'hanzi';
  }

  tg.current  = { promptWord, correct, options };
  tg.answered = false;

  $('tg-feedback').innerHTML = '';
  $('tg-next-btn').classList.add('hidden');
  $('tg-progress').textContent = `Soal ${tg.idx + 1} / ${tg.order.length}`;

  const hint = tg.mode === 'antonym' ? 'Dengarkan, lalu pilih LAWAN KATANYA'
             : tg.mode === 'synonym' ? 'Dengarkan, lalu pilih kata yang artinya SAMA/MIRIP'
             : tg.mode === 'confusion' ? 'Cocokkan dengan karakter yang BENAR (hati-hati, bentuknya mirip!)'
             : null;
  renderGamePrompt(qFormat, promptWord, hint);
  renderGameOptions(options, aFormat);
}


function answerGame(idx) {
  const tg = FC.toneGame;
  if (tg.answered || !tg.current) return;
  tg.answered = true;

  const picked    = tg.current.options[idx];
  const isCorrect = picked === tg.current.correct;

  // SRS mengikuti kata yang SEDANG DIUJI (promptWord) -- untuk mode
  // antonym itu kata soalnya sendiri (bukan lawan katanya), karena yang
  // sedang dilatih ingatannya ya kata itu.
  const trackedWord = tg.current.promptWord;
  const id = trackedWord.id || trackedWord.simplified;

  srsInitCard(id, FC.srsData);
  const oldCard = FC.srsData[id];
  const rating  = isCorrect ? 2 : 0;
  FC.srsData[id] = srsCalculate(oldCard, rating);
  srsSave(FC.srsData);

  if (isCorrect) {
    tg.score.ok++;
  } else {
    tg.score.bad++;
    FC.wrongSet.add(id);
    wrongSave(FC.wrongSet);
  }
  updateToneGameScore();

  document.querySelectorAll('.tg-option-btn').forEach((btn, i) => {
    btn.classList.add('disabled');
    const w = tg.current.options[i];
    if (w === tg.current.correct) btn.classList.add('correct');
    else if (i === idx) btn.classList.add('wrong');
  });
  document.querySelectorAll('.tg-audio-option').forEach((el, i) => {
    el.classList.add('disabled');
    const w = tg.current.options[i];
    if (w === tg.current.correct) el.classList.add('correct');
    else if (i === idx) el.classList.add('wrong');
  });
  $('tg-confirm-wrap').classList.add('hidden');

  if (tg.mode === 'nuance') {
    // Feedback pakai example_id (terjemahan kalimat) dari nuance_pairs.json,
    // BUKAN gameWordMeaning() generik -- opsi jawaban di sini objek sintetis
    // {simplified, id, pinyin} saja, tidak punya field meanings_id.
    const q = tg.current.question;
    $('tg-feedback').innerHTML = isCorrect
      ? `<span class="tg-feedback-ok">✓ Benar! ${escHtml(q.correctWord)} (${escHtml(q.correctPinyin)}) — "${escHtml(q.translation)}"</span>`
      : `<span class="tg-feedback-bad">✗ Salah. Jawaban benar: ${escHtml(q.correctWord)} (${escHtml(q.correctPinyin)}) — "${escHtml(q.translation)}"</span>`;
  } else if (tg.mode === 'pola') {
    // Feedback pakai keterangan_id spesifik kata dari kata_majemuk_pola.json,
    // BUKAN gameWordMeaning() generik -- opsi jawaban di sini objek kategori
    // {pola, label}, bukan objek kata.
    const q = tg.current.question;
    $('tg-feedback').innerHTML = isCorrect
      ? `<span class="tg-feedback-ok">✓ Benar! ${escHtml(q.correctPola)} (${escHtml(q.correctLabel)}) — ${escHtml(q.keterangan)}</span>`
      : `<span class="tg-feedback-bad">✗ Salah. Jawaban benar: ${escHtml(q.correctPola)} (${escHtml(q.correctLabel)}) — ${escHtml(q.keterangan)}</span>`;
  } else if (tg.mode === 'confusion') {
    // (E.0.3) Feedback tambahkan catatan pembeda BENTUK dari
    // confusion_groups.json (tg.currentNote, diisi saat render soal) --
    // inilah nilai edukatif utamanya, beda dari tone-trap yg tidak
    // punya keterangan serupa.
    const cw = tg.current.correct;
    const meaning = gameWordMeaning(cw);
    const note = tg.currentNote || '';
    const noteHtml = note ? `<br><span class="tg-feedback-note">👀 ${escHtml(note)}</span>` : '';
    $('tg-feedback').innerHTML = isCorrect
      ? `<span class="tg-feedback-ok">✓ Benar! ${escHtml(cw.simplified || cw.id)} (${escHtml(cw.pinyin || '')}) — ${escHtml(meaning)}${noteHtml}</span>`
      : `<span class="tg-feedback-bad">✗ Salah. Jawaban benar: ${escHtml(cw.simplified || cw.id)} (${escHtml(cw.pinyin || '')}) — ${escHtml(meaning)}${noteHtml}</span>`;
  } else {
    const cw = tg.current.correct;
    const meaning = gameWordMeaning(cw);
    const label = tg.mode === 'antonym' ? 'Lawan katanya'
                : tg.mode === 'synonym' ? 'Sinonimnya'
                : 'Jawaban benar';
    $('tg-feedback').innerHTML = isCorrect
      ? `<span class="tg-feedback-ok">✓ Benar! ${escHtml(cw.simplified || cw.id)} (${escHtml(cw.pinyin || '')}) — ${escHtml(meaning)}</span>`
      : `<span class="tg-feedback-bad">✗ Salah. ${escHtml(label)}: ${escHtml(cw.simplified || cw.id)} (${escHtml(cw.pinyin || '')}) — ${escHtml(meaning)}</span>`;
  }

  $('tg-next-btn').classList.remove('hidden');
}


function nextToneGameQuestion() {
  FC.toneGame.idx++;
  renderToneGameQuestion();
}


function updateToneGameScore() {
  $('tg-score-ok').textContent  = FC.toneGame.score.ok;
  $('tg-score-bad').textContent = FC.toneGame.score.bad;
}


function finishToneGame() {
  const tg = FC.toneGame;
  tg.active = false;
  showToast(`Selesai! Benar ${tg.score.ok} · Salah ${tg.score.bad}`, 'success');

  showScreen('choose');

  // Kembalikan UI flip-card biasa supaya deck lain normal lagi
  $('tone-game-wrap').classList.add('hidden');
  $('qm-toggle').classList.remove('hidden');
  $('fc-card-wrap').classList.remove('hidden');
  $('fc-shortcut-hint').classList.remove('hidden');
}

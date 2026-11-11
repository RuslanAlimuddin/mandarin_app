/* ═══════════════════════════════════════════════════════════════
   flashcard-decks.js — State FC, load data, deck queue, sidebar
   (Tema/Radikal/Goresan/Fonetik/Struktur/Pinyin), tema custom
═══════════════════════════════════════════════════════════════ */
'use strict';

/* ═══════════════════════════════════════════════════════════════
   flashcard.html — PART 4: Load deck, render kartu, event handler
═══════════════════════════════════════════════════════════════ */

/* ── STATE SESI ────────────────────────────────────────────── */
const FC = {
  allWords:     null,   // array app_words.json
  dataTheme:    null,   // object index_theme.json
  dataRadical:  null,   // object index_radical.json
  dataStroke:   null,   // object index_stroke.json -- Fix B6: Goresan sebagai deck jelajah/latihan
  dataPhonetic: null,   // object index_phonetic.json — Fix B4
  dataAkar:     null,   // object produktif_karakter.json — "Akar Kosakata": karakter dasar → daftar kata turunan (analogi akar/sharaf), fitur silang dgn Kamus
  phoneticReverse: null, // reverse lookup wordId → [komponen fonetik], dibangun sekali dari dataPhonetic

  // Mode Game Audio (Tier 3) -- dengar lalu pilih, reuse mekanisme
  // tone.html. 'tonepairs' = khusus Jebakan Nada (distraktor dari grup
  // pinyin-sama-nada-beda). 'generic' = deck manapun lain kalau toggle
  // gameModeOn aktif (distraktor acak dari pool deck itu sendiri).
  gameModeOn: false,  // toggle: mainkan deck (selain Jebakan Nada) sebagai game, bukan flip-card
  ignoreDue:  false,  // toggle: sertakan kartu yang belum jatuh tempo (deck jadi 'jelajah bebas', bukan rotasi SRS ketat)
  wordBySimplified: null, // reverse lookup hanzi → objek kata, dibangun sekali lazy (dipakai game Lawan Kata resolve antonim jadi objek kata utuh)

  // Format soal/jawaban KHUSUS game Lawan Kata (Tier 3) -- رسلان minta
  // bisa pilih independen: Hanzi | Pinyin | Suara | Terjemahan | Acak
  antonymQFormat: 'acak',
  antonymAFormat: 'hanzi',

  // Sama seperti antonym, tapi untuk game Sinonim
  synonymQFormat: 'acak',
  synonymAFormat: 'hanzi',

  // Deck "Pilih yang Tepat" (near-synonym nuance, Tier 4) -- data DILUAR
  // app_words.json, reuse data/nuance_pairs.json yang sama dipakai panel
  // "Beda dengan Kata Mirip" di kamus-nuance.js. Lazy-load sekali via
  // loadNuanceData(), lihat bagian bawah file ini.
  nuancePairs: null,

  // Deck "🧩 Tebak Pola Kata" (Tier 4, BARU) -- data DILUAR app_words.json,
  // reuse data/kata_majemuk_pola.json yang sama dipakai panel "Pola
  // Pembentukan Kata" di kamus-pola.js (Kamus). Lazy-load sekali via
  // loadPolaGameData(), lihat bagian bawah file ini.
  polaEntries: null,

  toneGame: {
    active:  false,
    mode:    'tonepairs', // 'tonepairs' | 'generic' | 'antonym' | 'synonym' | 'nuance' | 'pola'
    groups:  [],    // dipakai kalau mode tonepairs
    pool:    [],    // dipakai kalau mode generic
    pairs:   [],    // dipakai kalau mode antonym/synonym -- array {word, antonym} atau {word, synonym} (keduanya objek kata utuh)
    nuanceQuestions: [], // dipakai kalau mode nuance -- array soal kalimat-rumpang, lihat buildNuanceQuestions() di flashcard-games.js
    polaQuestions: [], // dipakai kalau mode pola -- array soal tebak-kategori, lihat buildPolaQuestions() di flashcard-games.js
    order:   [],
    idx:     0,
    current: null,  // { promptWord, correct, options }
    answered: false,
    score:   { ok: 0, bad: 0 },
  },
  srsData:      {},     // data SRS dari localStorage
  bookmarkSet:  new Set(),
  wrongSet:     new Set(),

  deckId:       null,   // deck yang sedang aktif
  deckName:     '',
  queue:        [],     // urutan kartu sesi ini
  queueIndex:   0,      // posisi saat ini

  currentWord:  null,   // objek kata yang sedang tampil
  isFlipped:    false,  // kartu sedang tampil jawaban?
  hintShown:    false,

  // Fix #9: mode pertanyaan
  questionMode: 'hanzi',   // 'hanzi'|'pinyin'|'id'|'random'
  // Fix #8: mode & limit sesi
  sessionMode:      'fixed',
  sessionCardLimit: 20,

  // Statistik sesi
  sessionTotal:   0,
  sessionCorrect: 0,  // rating >= 2
  sessionAgain:   0,  // rating === 0
  sessionNew:     0,  // kartu baru diproses
  sessionReview:  0,  // kartu review diproses
};

/* ── UTILS ─────────────────────────────────────────────────── */
/* $(), showToast(), escHtml() sekarang dari shared/core.js */


function hskClass(level) {
  const l = parseInt(level);
  if (l >= 7) return 'hsk-7';
  return `hsk-${l}`;
}


function hskLabel(level) {
  const l = parseInt(level);
  return l >= 7 ? 'HSK 7-9' : `HSK ${l}`;
}


/* ── LOAD DATA ─────────────────────────────────────────────── */
async function loadWords() {
  try {
    const res = await fetch('data/app_words.json');
    if (!res.ok) throw new Error('Gagal memuat app_words.json');
    FC.allWords = await res.json();

    FC.srsData     = srsLoad();
    FC.bookmarkSet = new Set(JSON.parse(localStorage.getItem('mandarin_bookmarks') || '[]'));
    FC.wrongSet    = wrongLoad();

    // Fix #6,7: load index file tema, radikal, goresan
    try {
      const [resTheme, resRadical, resStroke, resAkar] = await Promise.all([
        fetch('data/index_theme.json'),
        fetch('data/index_radical.json'),
        fetch('data/index_stroke.json'),
        fetch('data/produktif_karakter.json'),
      ]);
      if (resTheme.ok)   FC.dataTheme   = await resTheme.json();
      if (resRadical.ok) FC.dataRadical = await resRadical.json();
      if (resStroke.ok)  FC.dataStroke  = await resStroke.json();
      if (resAkar.ok)    FC.dataAkar    = await resAkar.json();
    } catch (e) { console.warn('index file gagal dimuat:', e); }

    renderSidebarTema();
    renderSidebarRadikal();
    renderSidebarAkar();
    renderSidebarGoresan();
    renderSidebarPinyinBrowse();
    updateAllDueCounts();
    loadFcCharEtymology(); // "Bantu Ingat" -- file kecil, tidak perlu diblokir/ditunggu
  } catch (err) {
    const isCors = err.name === 'TypeError' || err.message.includes('Failed to fetch');
    showToast(isCors
      ? '⚠ CORS Error — Jalankan: python -m http.server 8000'
      : '⚠ Gagal memuat data: ' + err.message, 'error');
    const choose = document.getElementById('screen-choose');
    if (choose) choose.innerHTML = `
      <div style="color:var(--red);text-align:center;padding:20px;max-width:380px">
        <div style="font-size:2rem;margin-bottom:12px">⚠</div>
        <div style="font-weight:600;margin-bottom:8px;color:var(--text-main)">Gagal Memuat Data</div>
        <div style="font-size:0.82rem;line-height:1.8;color:var(--text-dim)">
          Browser memblokir akses file lokal (CORS).<br>
          Buka terminal di folder <strong>mandarin_app/</strong>:<br>
          <code style="background:var(--bg-card2);padding:4px 12px;border-radius:4px;display:inline-block;margin:8px 0;color:var(--gold)">python -m http.server 8000</code><br>
          Kemudian buka: <strong>http://localhost:8000</strong>
        </div>
      </div>`;
    console.error(err);
  }
}


/* ── RENDER SIDEBAR TEMA DARI index_theme.json ─────────────── */
const TEMA_EMOJI = {
  angka:'🔢', waktu:'🕐', keluarga:'👨‍👩‍👧', makanan:'🍜',
  minuman:'🥤', warna:'🎨', tubuh:'🫁', pakaian:'👗',
  rumah:'🏠', sekolah:'📚', pekerjaan:'💼', transportasi:'🚌',
  alam:'🌿', hewan:'🐾', cuaca:'🌤️', kota:'🏙️',
  olahraga:'⚽', seni:'🎭', teknologi:'💻', kesehatan:'💊',
  emosi:'😊', sifat:'✨', arah:'🧭', ukuran:'📏',
  agama:'🕌', politik:'🏛️', ekonomi:'💰', hukum:'⚖️',
  pendidikan:'📖', lingkungan:'🌍', budaya:'🎎', bahasa:'💬',
  perjalanan:'✈️', hobi:'🎯',
};

/* ── UPDATE DUE COUNT DI SIDEBAR ───────────────────────────── */
function updateAllDueCounts() {
  if (!FC.allWords) return;

  const decks = [
    'hsk-1','hsk-2','hsk-3','hsk-4','hsk-5','hsk-6','hsk-7',
    'bookmarks','wrong','all-due',
  ];

  for (const deckId of decks) {
    const cnt = countDueForDeck(deckId, FC.allWords, FC.srsData, FC.bookmarkSet, FC.wrongSet);
    const el  = $(`due-${deckId}`);
    if (el) el.textContent = cnt > 0 ? cnt : '—';
  }
}


/* ── PILIH DECK ─────────────────────────────────────────────── */
function selectDeck(deckId, deckName) {
  FC.deckId   = deckId;
  FC.deckName = deckName;

  // Update sidebar visual
  document.querySelectorAll('.sidebar-item').forEach(el => {
    el.classList.toggle('active', el.dataset.deck === deckId);
  });

  if (!FC.allWords) {
    showToast('Data belum selesai dimuat, tunggu sebentar…');
    return;
  }

  // "Jebakan Nada" sekarang game audio (dengar → pilih), BUKAN flip-card
  // SRS biasa -- jalur build queue-nya beda sendiri (lihat buildToneTrapGroups).
  if (deckId === 'tone-trap') {
    // Fix bug jumlah kartu diabaikan: sebelumnya FC.toneGame.groups diisi
    // dataset MENTAH PENUH (974 grup) tanpa peduli FC.sessionCardLimit,
    // krn jalur ini tidak lewat buildDeckQueue() spt deck biasa. Sekarang
    // shuffle dulu (biar variatif tiap sesi, bukan selalu N pertama yg
    // sama), baru potong ke sessionCardLimit -- pola identik dgn yg
    // dipakai buildDeckQueue() (lihat baris ~974/1009/1014).
    let groups = buildToneTrapGroups(FC.allWords);
    groups = groups.slice();
    shuffle(groups);
    groups = groups.slice(0, FC.sessionCardLimit || 20);
    FC.toneGame.groups = groups;

    $('ctrl-antonym-fmt-row-q').classList.add('hidden');
    $('ctrl-antonym-fmt-row-a').classList.add('hidden');
    $('ctrl-synonym-fmt-row-q').classList.add('hidden');
    $('ctrl-synonym-fmt-row-a').classList.add('hidden');
    $('ctrl-confusion-fmt-row-q').classList.add('hidden');

    if (!groups.length) {
      showToast('Data belum cukup untuk game Jebakan Nada.', 'info');
      $('btn-start-session').classList.add('hidden');
      return;
    }

    const btn = $('btn-start-session');
    btn.textContent = `Mulai Game (${groups.length} soal)`;
    btn.classList.remove('hidden');
    showToast(`${deckName}: ${groups.length} soal siap`);
    ensureAccordionVisible(deckId);
    saveFlashcardLastState();
    return;
  }

  // "Karakter Mirip" (E.0.3) -- game audio spt tone-trap: dengar 1
  // karakter dari grup mirip bentuk, pilih hanzi yg tepat, distraktor
  // HANYA dari grup yg sama (ide asli BLUEPRINT v9, ~19 versi tertunda).
  // Pola shuffle+slice dari awal (bukan bug "jumlah kartu diabaikan" spt
  // yg sempat kejadian di tone-trap/nuance/pola versi lama).
  if (deckId === 'confusion') {
    let groups = buildConfusionGroups(FC.allWords);
    groups = groups.slice();
    shuffle(groups);
    groups = groups.slice(0, FC.sessionCardLimit || 20);
    FC.toneGame.confusionGroups = groups;

    $('ctrl-antonym-fmt-row-q').classList.add('hidden');
    $('ctrl-antonym-fmt-row-a').classList.add('hidden');
    $('ctrl-synonym-fmt-row-q').classList.add('hidden');
    $('ctrl-synonym-fmt-row-a').classList.add('hidden');
    $('ctrl-confusion-fmt-row-q').classList.remove('hidden');

    if (!groups.length) {
      showToast('Data belum cukup untuk game Karakter Mirip.', 'info');
      $('btn-start-session').classList.add('hidden');
      return;
    }

    const btn = $('btn-start-session');
    btn.textContent = `Mulai Game (${groups.length} soal)`;
    btn.classList.remove('hidden');
    showToast(`${deckName}: ${groups.length} soal siap`);
    ensureAccordionVisible(deckId);
    saveFlashcardLastState();
    return;
  }

  // "Pilih yang Tepat" (Tier 4) -- juga bukan flip-card SRS biasa, jalur
  // build queue-nya sendiri dari data/nuance_pairs.json (lihat
  // buildNuanceQuestions() di flashcard-games.js), bukan dari app_words.json.
  if (deckId === 'nuance-choice') {
    // Fix bug jumlah kartu diabaikan (sama spt tone-trap di atas) --
    // sebelumnya questions = seluruh dataset nuance_pairs.json (2558 soal).
    let questions = buildNuanceQuestions(FC.nuancePairs || []);
    questions = questions.slice();
    shuffle(questions);
    questions = questions.slice(0, FC.sessionCardLimit || 20);
    // Simpan versi yg SUDAH dipotong -- startAudioGame('nuance') di
    // flashcard-games.js akan pakai ini kalau sudah ada, bukan build ulang
    // dari FC.nuancePairs penuh (itu penyebab asli bug jumlah kartu diabaikan).
    FC.toneGame.nuanceQuestions = questions;

    $('ctrl-antonym-fmt-row-q').classList.add('hidden');
    $('ctrl-antonym-fmt-row-a').classList.add('hidden');
    $('ctrl-synonym-fmt-row-q').classList.add('hidden');
    $('ctrl-synonym-fmt-row-a').classList.add('hidden');
    $('ctrl-confusion-fmt-row-q').classList.add('hidden');

    if (!questions.length) {
      showToast('Data pasangan nuansa belum cukup utk dijadikan soal (butuh ≥2 kata BEDA per pasangan + contoh kalimat).', 'info');
      $('btn-start-session').classList.add('hidden');
      return;
    }

    const btn = $('btn-start-session');
    btn.textContent = `🎯 Mulai Game (${questions.length} soal)`;
    btn.classList.remove('hidden');
    showToast(`${deckName}: ${questions.length} soal siap`);
    ensureAccordionVisible(deckId);
    saveFlashcardLastState();
    return;
  }

  // "🧩 Tebak Pola Kata" (Tier 4, BARU) -- juga bukan flip-card SRS biasa,
  // jalur build queue-nya sendiri dari data/kata_majemuk_pola.json (lihat
  // buildPolaQuestions() di flashcard-games.js), bukan dari app_words.json.
  if (deckId === 'pola-choice') {
    // Fix bug jumlah kartu diabaikan (sama spt 2 mode di atas) --
    // sebelumnya questions = seluruh dataset kata_majemuk_pola.json (8867 soal).
    let questions = buildPolaQuestions(FC.polaEntries || []);
    questions = questions.slice();
    shuffle(questions);
    questions = questions.slice(0, FC.sessionCardLimit || 20);
    // Simpan versi yg SUDAH dipotong (sama alasannya spt nuance-choice di atas).
    FC.toneGame.polaQuestions = questions;

    $('ctrl-antonym-fmt-row-q').classList.add('hidden');
    $('ctrl-antonym-fmt-row-a').classList.add('hidden');
    $('ctrl-synonym-fmt-row-q').classList.add('hidden');
    $('ctrl-synonym-fmt-row-a').classList.add('hidden');
    $('ctrl-confusion-fmt-row-q').classList.add('hidden');

    if (!questions.length) {
      showToast('Data pola pembentukan kata belum tersedia utk dijadikan soal.', 'info');
      $('btn-start-session').classList.add('hidden');
      return;
    }

    const btn = $('btn-start-session');
    btn.textContent = `🧩 Mulai Game (${questions.length} soal)`;
    btn.classList.remove('hidden');
    showToast(`${deckName}: ${questions.length} soal siap`);
    ensureAccordionVisible(deckId);
    saveFlashcardLastState();
    return;
  }

  // Bangun antrian (deck flip-card biasa)
  const queue = buildDeckQueue(deckId, FC.allWords, FC.srsData, FC.bookmarkSet, FC.wrongSet, FC.sessionCardLimit, FC.sessionMode, FC.ignoreDue);

  $('ctrl-antonym-fmt-row-q').classList.toggle('hidden', deckId !== 'antonyms');
  $('ctrl-antonym-fmt-row-a').classList.toggle('hidden', deckId !== 'antonyms');
  $('ctrl-synonym-fmt-row-q').classList.toggle('hidden', deckId !== 'synonyms');
  $('ctrl-synonym-fmt-row-a').classList.toggle('hidden', deckId !== 'synonyms');
  $('ctrl-confusion-fmt-row-q').classList.add('hidden');

  if (queue.length === 0) {
    showToast('Tidak ada kartu yang perlu diulang untuk deck ini.', 'info');
    $('btn-start-session').classList.add('hidden');
    return;
  }

  FC.queue = queue;

  // Tampilkan tombol mulai + info jumlah (label ikut toggle Mode Game)
  const btn = $('btn-start-session');
  btn.classList.remove('hidden');
  refreshStartButtonLabel();

  showToast(
    FC.lastQueueReviewReason === 'toggle'
      ? `${deckName}: mode jelajah bebas aktif — ${queue.length} kartu ditampilkan (jadwal SRS diabaikan)`
      : FC.lastQueueReviewReason === 'mastered'
        ? `${deckName}: semua kartu sudah dikuasai — ${queue.length} kartu ditampilkan untuk review bebas`
        : `${deckName}: ${queue.length} kartu siap`
  );

  // Pastikan section accordion yang berisi item ini terbuka
  ensureAccordionVisible(deckId);

  saveFlashcardLastState();
}


/* ── LABEL TOMBOL MULAI (ikut toggle Mode Game) ─────────────── */
function refreshStartButtonLabel() {
  const btn = $('btn-start-session');
  if (!btn || btn.classList.contains('hidden')) return;
  if (FC.deckId === 'tone-trap') return; // label deck ini sudah diset sendiri di selectDeck

  btn.textContent = FC.gameModeOn
    ? `🎮 Mulai Game (${FC.queue.length} kata)`
    : `Mulai Sesi (${FC.queue.length} kartu)`;
}


/* ── Fix B1: ACCORDION SIDEBAR ─────────────────────────────── */
const _accordionOpen = { 'acc-hsk': true }; // HSK default expanded

function toggleAccordion(id) {
  const body = $(id);
  const arrow = $('arr-' + id);
  if (!body) return;

  // Catatan: dulu ada guard "jangan collapse kalau ada item aktif di
  // dalamnya" -- ini menyebabkan section seperti RADIKAL terkunci terbuka
  // selamanya begitu satu item di dalamnya jadi deck aktif, karena klik
  // header tidak pernah bisa menutupnya lagi. Klik header sekarang SELALU
  // toggle terbuka/tutup apapun status aktifnya. Auto-buka paksa saat
  // pindah deck dari section lain tetap jalan lewat ensureAccordionVisible().
  if (_accordionOpen[id]) {
    _accordionOpen[id] = false;
    body.style.maxHeight = body.scrollHeight + 'px';
    requestAnimationFrame(() => { body.classList.add('collapsed'); });
    if (arrow) arrow.classList.add('collapsed');
  } else {
    _accordionOpen[id] = true;
    body.classList.remove('collapsed');
    body.style.maxHeight = body.scrollHeight + 'px';
    setTimeout(() => { body.style.maxHeight = ''; }, 230);
    if (arrow) arrow.classList.remove('collapsed');
  }
}


/* ── PENCARIAN CEPAT SIDEBAR (Tema/Radikal/Fonetik) ────────────
   Filter murni di sisi klien terhadap item yang SUDAH dirender --
   tidak menyentuh data sama sekali, jadi aman dipasang di atas
   ketiga daftar tanpa peduli data itu sumbernya index_theme.json,
   index_radical.json, atau dataPhonetic. Dipanggil lewat oninput
   pada kotak <input class="sidebar-search-box">. */
function filterSidebarList(inputId, listContainerId) {
  const input     = document.getElementById(inputId);
  const container = document.getElementById(listContainerId);
  if (!input || !container) return;
  const q = input.value.trim().toLowerCase();

  // Radikal & Fonetik punya kontainer "-extra" (item ke-16/21 dst, di
  // belakang tombol "+ Tampilkan semua", collapsed via class 'hidden').
  // Selama pencarian aktif, paksa tampil supaya isinya ikut kena filter --
  // kalau tidak, item yang dicari tapi kebetulan ada di balik tombol itu
  // tidak akan pernah ketemu. Tema tidak punya mekanisme ini (aman, extra
  // akan bernilai null dan blok ini dilewati begitu saja).
  const extra = container.querySelector('[id$="-extra"]');
  if (extra) {
    const toggleBtn = container.querySelector('button.sidebar-item');
    if (q) {
      extra.classList.remove('hidden');
      if (toggleBtn) toggleBtn.style.display = 'none';
    } else {
      extra.classList.add('hidden');
      if (toggleBtn) toggleBtn.style.display = '';
    }
  }

  let anyVisible = false;
  container.querySelectorAll('div.sidebar-item').forEach(el => {
    const match = !q || el.textContent.toLowerCase().includes(q);
    el.style.display = match ? '' : 'none';
    if (match) anyVisible = true;
  });

  // Pesan "tidak ada hasil" kalau pencarian tidak menemukan apa pun
  let emptyMsg = container.querySelector('.sidebar-search-empty');
  if (q && !anyVisible) {
    if (!emptyMsg) {
      emptyMsg = document.createElement('div');
      emptyMsg.className = 'sidebar-search-empty';
      emptyMsg.style.cssText = 'font-size:0.75rem;color:var(--text-muted);padding:6px 10px';
      container.appendChild(emptyMsg);
    }
    emptyMsg.textContent = `Tidak ada hasil untuk "${input.value.trim()}"`;
  } else if (emptyMsg) {
    emptyMsg.remove();
  }

  // Refresh tinggi accordion supaya tidak terpotong saat jumlah item
  // yang tampil berubah (pola sama seperti toggleAccordion()).
  const body = container.closest('.sidebar-section-body');
  if (body && !body.classList.contains('collapsed')) {
    body.style.maxHeight = body.scrollHeight + 'px';
  }
}


/* Pastikan section accordion item aktif selalu terlihat */
function ensureAccordionVisible(deckId) {
  const item = document.querySelector(`.sidebar-item[data-deck="${CSS.escape(deckId)}"]`);
  if (!item) return;
  const body = item.closest('.sidebar-section-body');
  if (body && body.classList.contains('collapsed')) {
    const accId = body.id;
    _accordionOpen[accId] = false; // force re-open
    toggleAccordion(accId);
  }
}


/* ── Fix B2: TEMA CUSTOM ────────────────────────────────────── */
const CUSTOM_THEMES_KEY = 'mandarin_custom_themes';

function loadCustomThemes() {
  try { return JSON.parse(localStorage.getItem(CUSTOM_THEMES_KEY) || '{}'); }
  catch { return {}; }
}


function saveCustomThemes(obj) {
  try { localStorage.setItem(CUSTOM_THEMES_KEY, JSON.stringify(obj)); }
  catch {}
}


function promptAddCustomTheme() {
  const name = window.prompt('Nama tema baru (contoh: Kata Favorit Saya):');
  if (!name || !name.trim()) return;
  const key = 'custom_' + name.trim().toLowerCase().replace(/\s+/g, '_').replace(/[^a-z0-9_]/g, '');
  const customs = loadCustomThemes();
  if (customs[key]) { showToast('Tema dengan nama itu sudah ada.', 'info'); return; }
  customs[key] = { label: name.trim(), words: [] };
  saveCustomThemes(customs);
  renderSidebarTema();
  showToast('✓ Tema "' + name.trim() + '" ditambahkan — klik ➕ untuk isi kata', 'success');
}


// Melengkapi tema custom yang tadinya cuma bisa dibuat kosong (words: [])
// tanpa cara mengisi. Cari kata dari FC.allWords sendiri (app_words.json,
// offline) berdasarkan hanzi persis -- bukan dari sumber luar (GitHub/Anki/
// dsb -- itu perlu alur terpisah lewat skrip Python lokal, bukan tombol
// dalam aplikasi, supaya prinsip offline-murni tidak dilanggar).
function promptAddWordsToCustomTheme(key) {
  const customs = loadCustomThemes();
  const theme = customs[key];
  if (!theme) return;

  const input = window.prompt(
    `Tambah kata ke tema "${theme.label}"\nKetik hanzi, pisahkan dengan koma kalau lebih dari satu:\ncontoh: 篮球, 足球, 排球`
  );
  if (!input || !input.trim()) return;

  const tokens = input.split(/[,，\s]+/).map(s => s.trim()).filter(Boolean);
  const found = [];
  const notFound = [];
  const alreadyIn = [];

  tokens.forEach(tok => {
    const w = (FC.allWords || []).find(x => (x.simplified || x.id) === tok);
    if (!w) { notFound.push(tok); return; }
    const id = w.id || w.simplified;
    if (theme.words.includes(id)) { alreadyIn.push(tok); return; }
    theme.words.push(id);
    found.push(tok);
  });

  saveCustomThemes(customs);
  renderSidebarTema();

  const parts = [];
  if (found.length)     parts.push(`✓ ditambah: ${found.join(', ')}`);
  if (alreadyIn.length) parts.push(`sudah ada: ${alreadyIn.join(', ')}`);
  if (notFound.length)  parts.push(`tidak ditemukan di kamus: ${notFound.join(', ')}`);
  showToast(parts.join(' — ') || 'Tidak ada kata yang ditambahkan', notFound.length && !found.length ? 'info' : 'success');
}


function promptDeleteCustomTheme(key, label) {
  if (!window.confirm(`Hapus tema "${label}"? Ini tidak menghapus kata dari kamus, cuma menghapus kelompok temanya.`)) return;
  const customs = loadCustomThemes();
  delete customs[key];
  saveCustomThemes(customs);
  renderSidebarTema();
  showToast('Tema "' + label + '" dihapus', 'info');
}


/* ── Fix B3: RENDER RADIKAL LENGKAP (214) ──────────────────── */
function renderSidebarRadikal() {
  const container = $('sidebar-radikal-list');
  if (!container) return;

  if (!FC.dataRadical) {
    container.innerHTML = '<div style="font-size:0.75rem;color:var(--text-muted);padding:6px 10px">Data radikal tidak tersedia</div>';
    return;
  }

  // Ambil semua radikal dari data, urutkan terbanyak dulu
  const entries = Object.entries(FC.dataRadical)
    .map(([rad, words]) => ({ rad, count: words.length }))
    .sort((a, b) => b.count - a.count);

  const COLLAPSE_AT = 20; // tampilkan 20 dulu
  container.innerHTML = '';

  function buildItems(list) {
    const frag = document.createDocumentFragment();
    list.forEach(({ rad, count }) => {
      const deckId = 'radical-' + encodeURIComponent(rad);
      const el = document.createElement('div');
      el.className = 'sidebar-item';
      el.dataset.deck = deckId;
      el.innerHTML = `<span style="font-size:1.05rem">${rad}</span><span class="item-count">${count}</span>`;
      el.addEventListener('click', () => selectDeck(deckId, 'Radikal: ' + rad));
      frag.appendChild(el);
    });
    return frag;
  }

  container.appendChild(buildItems(entries.slice(0, COLLAPSE_AT)));

  if (entries.length > COLLAPSE_AT) {
    const extra = document.createElement('div');
    extra.id = 'radikal-extra';
    extra.classList.add('hidden');
    extra.appendChild(buildItems(entries.slice(COLLAPSE_AT)));
    container.appendChild(extra);

    const toggleBtn = document.createElement('button');
    toggleBtn.className = 'sidebar-item';
    toggleBtn.id = 'radikal-toggle-btn';
    toggleBtn.style.cssText = 'width:100%;text-align:center;color:var(--text-muted);font-size:0.75rem;justify-content:center;';
    toggleBtn.textContent = `+ Tampilkan semua (${entries.length - COLLAPSE_AT} lagi)`;
    toggleBtn.addEventListener('click', () => {
      const ex = $('radikal-extra');
      const btn = $('radikal-toggle-btn');
      const hidden = ex.classList.toggle('hidden');
      btn.textContent = hidden
        ? `+ Tampilkan semua (${entries.length - COLLAPSE_AT} lagi)`
        : '− Tampilkan lebih sedikit';

      // Refresh tinggi accordion jika terbuka
      const body = container.closest('.sidebar-section-body');
      if (body && !body.classList.contains('collapsed')) body.style.maxHeight = '';
    });
    container.appendChild(toggleBtn);
  }
}


/* ── AKAR KOSAKATA (analogi akar/sharaf: 1 karakter dasar -> banyak kata
   turunan). Pola identik renderSidebarRadikal() di atas, bedanya diurut
   dari jumlah_turunan terbanyak (karakter paling "produktif" dulu), dan
   deckId-nya 'akar-<karakter>' -- ditangani buildDeckQueue() (lihat
   bawah, dekat pool 'radical-'). Data: data/produktif_karakter.json,
   hasil analisis_produktivitas.py, dimuat bareng tema/radikal/goresan
   di loadWords() di atas. */
function renderSidebarAkar() {
  const container = $('sidebar-akar-list');
  if (!container) return;

  if (!FC.dataAkar) {
    container.innerHTML = '<div style="font-size:0.75rem;color:var(--text-muted);padding:6px 10px">Data akar kosakata tidak tersedia</div>';
    return;
  }

  const entries = Object.entries(FC.dataAkar)
    .map(([akar, d]) => ({ akar, count: d.jumlah_turunan || 0, pinyin: d.pinyin || '', arti: d.arti || '' }))
    .sort((a, b) => b.count - a.count);

  const COLLAPSE_AT = 20;
  container.innerHTML = '';

  function buildItems(list) {
    const frag = document.createDocumentFragment();
    list.forEach(({ akar, count, pinyin, arti }) => {
      const deckId = 'akar-' + encodeURIComponent(akar);
      const el = document.createElement('div');
      el.className = 'sidebar-item';
      el.dataset.deck = deckId;
      el.title = `${pinyin} — ${arti}`;
      el.innerHTML = `<span style="font-size:1.05rem">${escHtml(akar)}</span><span class="item-count">${count}</span>`;
      el.addEventListener('click', () => selectDeck(deckId, 'Akar: ' + akar + (arti ? ' (' + arti + ')' : '')));
      frag.appendChild(el);
    });
    return frag;
  }

  container.appendChild(buildItems(entries.slice(0, COLLAPSE_AT)));

  if (entries.length > COLLAPSE_AT) {
    const extra = document.createElement('div');
    extra.id = 'akar-extra';
    extra.classList.add('hidden');
    extra.appendChild(buildItems(entries.slice(COLLAPSE_AT)));
    container.appendChild(extra);

    const toggleBtn = document.createElement('button');
    toggleBtn.className = 'sidebar-item';
    toggleBtn.id = 'akar-toggle-btn';
    toggleBtn.style.cssText = 'width:100%;text-align:center;color:var(--text-muted);font-size:0.75rem;justify-content:center;';
    toggleBtn.textContent = `+ Tampilkan semua (${entries.length - COLLAPSE_AT} lagi)`;
    toggleBtn.addEventListener('click', () => {
      const ex = $('akar-extra');
      const btn = $('akar-toggle-btn');
      const hidden = ex.classList.toggle('hidden');
      btn.textContent = hidden
        ? `+ Tampilkan semua (${entries.length - COLLAPSE_AT} lagi)`
        : '− Tampilkan lebih sedikit';
      const body = container.closest('.sidebar-section-body');
      if (body && !body.classList.contains('collapsed')) body.style.maxHeight = '';
    });
    container.appendChild(toggleBtn);
  }
}


/* ── Fix B6: RENDER SIDEBAR GORESAN (fitur silang dgn Kamus) ───────
   Pola identik dengan renderSidebarRadikal() di atas, bedanya diurut
   NAIK berdasar jumlah goresan (1, 2, 3, ...) -- bukan terbanyak dulu --
   karena progresi goresan itu sendiri yang bermakna buat رسلان (dari
   yang paling mudah), bukan seberapa populer jumlah goresan tsb. */
function renderSidebarGoresan() {
  const container = $('sidebar-goresan-list');
  if (!container) return;

  if (!FC.dataStroke) {
    container.innerHTML = '<div style="font-size:0.75rem;color:var(--text-muted);padding:6px 10px">Data goresan tidak tersedia</div>';
    return;
  }

  const entries = Object.entries(FC.dataStroke)
    .map(([stroke, words]) => ({ stroke, count: words.length }))
    .sort((a, b) => parseInt(a.stroke) - parseInt(b.stroke));

  const COLLAPSE_AT = 20;
  container.innerHTML = '';

  function buildItems(list) {
    const frag = document.createDocumentFragment();
    list.forEach(({ stroke, count }) => {
      const deckId = 'strokecount-' + encodeURIComponent(stroke);
      const el = document.createElement('div');
      el.className = 'sidebar-item';
      el.dataset.deck = deckId;
      el.innerHTML = `<span>${escHtml(stroke)} goresan</span><span class="item-count">${count}</span>`;
      el.addEventListener('click', () => selectDeck(deckId, stroke + ' Goresan'));
      frag.appendChild(el);
    });
    return frag;
  }

  container.appendChild(buildItems(entries.slice(0, COLLAPSE_AT)));

  if (entries.length > COLLAPSE_AT) {
    const extra = document.createElement('div');
    extra.id = 'goresan-extra';
    extra.classList.add('hidden');
    extra.appendChild(buildItems(entries.slice(COLLAPSE_AT)));
    container.appendChild(extra);

    const toggleBtn = document.createElement('button');
    toggleBtn.className = 'sidebar-item';
    toggleBtn.id = 'goresan-toggle-btn';
    toggleBtn.style.cssText = 'width:100%;text-align:center;color:var(--text-muted);font-size:0.75rem;justify-content:center;';
    toggleBtn.textContent = `+ Tampilkan semua (${entries.length - COLLAPSE_AT} lagi)`;
    toggleBtn.addEventListener('click', () => {
      const ex = $('goresan-extra');
      const btn = $('goresan-toggle-btn');
      const hidden = ex.classList.toggle('hidden');
      btn.textContent = hidden
        ? `+ Tampilkan semua (${entries.length - COLLAPSE_AT} lagi)`
        : '− Tampilkan lebih sedikit';
      const body = container.closest('.sidebar-section-body');
      if (body && !body.classList.contains('collapsed')) body.style.maxHeight = '';
    });
    container.appendChild(toggleBtn);
  }
}


/* ── Fix B6: RENDER SIDEBAR PINYIN (fitur silang dgn Kamus) ────────
   Sama seperti panel "Per Pinyin" di Kamus: 2 tingkat, biar tidak
   perlu tampilkan ratusan suku kata teoretis yang datanya kosong.
   Level 1: 26 huruf awal. Level 2 (setelah diklik): turunan suku
   kata nyata utk huruf itu, dihitung langsung dari FC.allWords. */
function getPinyinSubgroupsFC(letter) {
  const data = FC.allWords || [];
  const counts = {};
  data.forEach(w => {
    const firstSyl = (w.pinyin || '').toLowerCase().split(/\s+/)[0] || '';
    const norm = normalizePinyin(firstSyl).replace(/[^a-z]/g, '');
    if (!norm.startsWith(letter)) return;
    const prefixLen = /^(zh|ch|sh)/.test(norm) ? 3 : 2;
    const prefix = norm.slice(0, Math.min(prefixLen, norm.length));
    counts[prefix] = (counts[prefix] || 0) + 1;
  });
  return counts;
}


function renderSidebarPinyinBrowse() {
  const container = $('sidebar-pinyin-list');
  if (!container) return;
  if (!FC.allWords) {
    container.innerHTML = '<div style="font-size:0.75rem;color:var(--text-muted);padding:6px 10px">Memuat…</div>';
    return;
  }
  renderPinyinLetterGridFC();
}


function renderPinyinLetterGridFC() {
  const container = $('sidebar-pinyin-list');
  if (!container) return;
  container.innerHTML = '';
  'abcdefghijklmnopqrstuvwxyz'.split('').forEach(l => {
    const el = document.createElement('div');
    el.className = 'sidebar-item';
    el.innerHTML = `<span>${l.toUpperCase()}…</span>`;
    el.addEventListener('click', () => renderPinyinSubGridFC(l));
    container.appendChild(el);
  });
}


function renderPinyinSubGridFC(letter) {
  const container = $('sidebar-pinyin-list');
  if (!container) return;
  container.innerHTML = '';

  const back = document.createElement('div');
  back.className = 'sidebar-item';
  back.style.cssText = 'color:var(--text-muted)';
  back.innerHTML = '<span>‹ Kembali</span>';
  back.addEventListener('click', renderPinyinLetterGridFC);
  container.appendChild(back);

  const counts = getPinyinSubgroupsFC(letter);
  Object.entries(counts)
    .sort((a, b) => b[1] - a[1])
    .forEach(([prefix, count]) => {
      const deckId = 'pinyin-' + encodeURIComponent(prefix);
      const el = document.createElement('div');
      el.className = 'sidebar-item';
      el.dataset.deck = deckId;
      el.innerHTML = `<span>${escHtml(prefix)}</span><span class="item-count">${count}</span>`;
      el.addEventListener('click', () => selectDeck(deckId, 'Pinyin: ' + prefix + '…'));
      container.appendChild(el);
    });

  const body = container.closest('.sidebar-section-body');
  if (body && !body.classList.contains('collapsed')) body.style.maxHeight = '';
}


/* ── Fix B2: RENDER SIDEBAR TEMA (override, tambah custom + tombol +Tema) ── */
function renderSidebarTema() {
  const container = $('sidebar-tema-list');
  if (!container) return;

  container.innerHTML = '';

  // Tombol tambah tema custom
  const addBtn = document.createElement('button');
  addBtn.className = 'sidebar-item';
  addBtn.style.cssText = 'width:100%;color:var(--gold-dim);font-size:0.78rem;border:1px dashed var(--border-gold);border-radius:var(--radius);margin-bottom:4px;justify-content:center;';
  addBtn.innerHTML = '＋ Tema Baru';
  addBtn.addEventListener('click', promptAddCustomTheme);
  container.appendChild(addBtn);

  // Tema custom (dari localStorage)
  const customs = loadCustomThemes();
  Object.entries(customs).forEach(([key, val]) => {
    const deckId = 'custom-' + key;
    const count  = (val.words || []).length;
    const el = document.createElement('div');
    el.className = 'sidebar-item';
    el.dataset.deck = deckId;
    el.title = `${count} kartu dalam tema ini`;
    el.style.cssText = 'display:flex;align-items:center;gap:4px';
    el.innerHTML = `
      <span class="custom-theme-label" style="flex:1;cursor:pointer">🗂 ${escHtml(val.label)}</span>
      <span style="display:flex;align-items:center;gap:3px"><span class="item-count">${count}</span><span style="font-size:0.65rem;color:var(--text-muted)">kartu</span></span>
      <button title="Tambah kata ke tema ini" style="border:none;background:none;color:var(--gold-dim);cursor:pointer;font-size:0.9rem;padding:2px 4px">➕</button>
      <button title="Hapus tema ini" style="border:none;background:none;color:var(--text-muted);cursor:pointer;font-size:0.85rem;padding:2px 4px">🗑</button>
    `;
    el.querySelector('.custom-theme-label').addEventListener('click', () => selectDeck(deckId, 'Tema: ' + val.label));
    el.querySelectorAll('button')[0].addEventListener('click', (e) => { e.stopPropagation(); promptAddWordsToCustomTheme(key); });
    el.querySelectorAll('button')[1].addEventListener('click', (e) => { e.stopPropagation(); promptDeleteCustomTheme(key, val.label); });
    container.appendChild(el);
  });

  if (!FC.dataTheme) {
    const msg = document.createElement('div');
    msg.style.cssText = 'font-size:0.75rem;color:var(--text-muted);padding:6px 10px';
    msg.textContent = 'Data tema tidak tersedia';
    container.appendChild(msg);
    return;
  }

  const entries = Object.entries(FC.dataTheme)
    .sort((a, b) => b[1].count - a[1].count);

  entries.forEach(([key, val]) => {
    const deckId = 'theme-' + key;
    // Label: tema eksternal (prefix ext_) pakai label_en jika label_id masih bahasa Inggris
    const label  = val.label_id || val.label_en || key;
    const count  = val.count || 0;
    const isExt  = key.startsWith('ext_');
    const emoji  = TEMA_EMOJI[key.replace('ext_','')] || (isExt ? '🌐' : '📌');

    const el = document.createElement('div');
    el.className = 'sidebar-item';
    el.dataset.deck = deckId;
    el.title = `${count} kartu dalam tema ini`;
    el.innerHTML = `<span>${emoji} ${escHtml(label)}</span><span style="display:flex;align-items:center;gap:3px"><span class="item-count">${count}</span><span style="font-size:0.65rem;color:var(--text-muted)">kartu</span></span>`;
    el.addEventListener('click', () => selectDeck(deckId, 'Tema: ' + label));
    container.appendChild(el);
  });
}


/* ── Fix B5: FILTER BARU ─────────────────────────────────────
   buildDeckQueue sudah menangani theme- dan radical-, kita tambah:
   - struct-<struktur>  → B5a
   - tone-trap         → B5b
   - stroke-easy / stroke-hard → B5c
   - antonyms          → B5d
   - synonyms          → B5d (Sinonim, cermin dari antonyms)
   - phonetic-<komponen> → B4 UI
   - custom-<key>      → B2
   Logika diinjeksi ke buildDeckQueue via patch extend di sini.
──────────────────────────────────────────────────────────────── */

/* Override buildDeckQueue dari PART_3 — tambahkan deck-deck baru.
   CATATAN: karena PART_3 dan PART_4 digabung menjadi satu file,
   fungsi ini menimpa (overrides) yang di PART_3.
   Logika deck lama (hsk-, bookmarks, dll) disalin inline di bawah. */
function buildDeckQueue(deckId, allWords, srsData, bookmarkSet, wrongSet, sessionCardLimit, sessionMode, ignoreDue) {
  sessionCardLimit = sessionCardLimit || 20;
  sessionMode      = sessionMode      || 'fixed';

  let pool = null;

  // ── Deck-deck BARU (Sesi B) ──
  if (deckId.startsWith('struct-')) {
    const struct = decodeURIComponent(deckId.replace('struct-', ''));
    pool = allWords.filter(w => w.structure === struct);

  } else if (deckId === 'tone-trap') {
    pool = buildToneTrapPool(allWords);

  } else if (deckId === 'stroke-easy') {
    pool = allWords.filter(w => w.stroke_count >= 1 && w.stroke_count <= 3);

  } else if (deckId === 'stroke-hard') {
    pool = allWords.filter(w => w.stroke_count >= 15);

  } else if (deckId === 'antonyms') {
    pool = allWords.filter(w =>
      Array.isArray(w.antonyms) ? w.antonyms.length > 0 : !!w.antonyms
    );

  } else if (deckId === 'synonyms') {
    pool = allWords.filter(w =>
      Array.isArray(w.synonyms) ? w.synonyms.length > 0 : !!w.synonyms
    );

  } else if (deckId.startsWith('phonetic-')) {
    const phoneticComp = decodeURIComponent(deckId.replace('phonetic-', ''));
    const ids = (FC.dataPhonetic && FC.dataPhonetic[phoneticComp]) || [];
    const idSet = new Set(ids);
    pool = allWords.filter(w => idSet.has(w.id || w.simplified));

  } else if (deckId.startsWith('strokecount-')) {
    // Fix B6: Goresan per-jumlah-pasti (beda dari 'stroke-easy'/'stroke-hard'
    // yang cuma 2 kelompok kasar) -- fitur silang dengan panel "Per Goresan"
    // di Kamus, sekarang bisa dimainkan juga di Flashcard.
    const strokeNum = parseInt(decodeURIComponent(deckId.replace('strokecount-', '')));
    pool = allWords.filter(w => parseInt(w.stroke_count) === strokeNum);

  } else if (deckId.startsWith('pinyin-')) {
    // Fix B6: fitur silang dengan panel "Per Pinyin" di Kamus (2 tingkat:
    // huruf awal → turunan suku kata). deckId menyimpan suku kata (mis.
    // "ba", "zho"), dicocokkan longgar (tanpa nada) sama seperti Kamus.
    const prefix = decodeURIComponent(deckId.replace('pinyin-', '')).toLowerCase();
    pool = allWords.filter(w => {
      const firstSyl = (w.pinyin || '').toLowerCase().split(/\s+/)[0] || '';
      return normalizePinyin(firstSyl).startsWith(prefix);
    });

  } else if (deckId.startsWith('custom-')) {
    const key = deckId.replace('custom-', '');
    const customs = loadCustomThemes();
    const wordIds = (customs[key] && customs[key].words) || [];
    const idSet = new Set(wordIds);
    pool = allWords.filter(w => idSet.has(w.id || w.simplified));

  // ── Deck-deck LAMA (inline dari PART_3, tanpa rekursi) ──
  } else if (deckId.startsWith('hsk-')) {
    const level = deckId.replace('hsk-', '');
    const targetLevels = level === '7' ? [7, 8, 9] : [parseInt(level)];
    pool = allWords.filter(w => targetLevels.includes(parseInt(w.hsk)));

  } else if (deckId === 'bookmarks') {
    pool = allWords.filter(w => bookmarkSet.has(w.id || w.simplified));

  } else if (deckId === 'wrong') {
    pool = allWords.filter(w => wrongSet.has(w.id || w.simplified));

  } else if (deckId === 'all-due') {
    const dueIds = Object.entries(srsData)
      .filter(([, v]) => isDue(v.due))
      .map(([k]) => k);
    const dueSet = new Set(dueIds);
    pool = allWords.filter(w => dueSet.has(w.id || w.simplified));

  } else if (deckId.startsWith('theme-')) {
    const theme = deckId.replace('theme-', '');
    pool = allWords.filter(w =>
      Array.isArray(w.themes) && w.themes.some(t => t === theme)
    );

  } else if (deckId.startsWith('radical-')) {
    const radical = decodeURIComponent(deckId.replace('radical-', ''));
    pool = allWords.filter(w => w.radical === radical);

  } else if (deckId.startsWith('akar-')) {
    const akar = decodeURIComponent(deckId.replace('akar-', ''));
    const entry = FC.dataAkar && FC.dataAkar[akar];
    const kataSet = new Set((entry && entry.kata_turunan || []).map(t => t.kata));
    pool = allWords.filter(w => kataSet.has(w.id || w.simplified));

  } else {
    pool = []; // deck tidak dikenal
  }

  // Toggle manual "🔓 Sertakan kartu belum jatuh tempo" (رسلان kontrol
  // sendiri lewat checkbox) -- kalau aktif, deck apa pun (termasuk HSK/
  // Bookmark/dll, bukan cuma deck tematik) ditampilkan APA ADANYA, tanpa
  // peduli jadwal SRS. Ini beda dari fallback otomatis di bawah: toggle
  // ini selalu didahulukan kalau رسلان nyalakan, bahkan kalau sebagian
  // kartu sebenarnya masih due/fresh (semua tetap ikut ditampilkan).
  if (ignoreDue && pool.length > 0) {
    const allPool = pool.slice();
    shuffle(allPool);
    FC.lastQueueReviewReason = 'toggle';
    return allPool.slice(0, sessionCardLimit);
  }

  // ── Logika due/fresh (sama untuk semua deck) ──
  const due   = [];
  const fresh = [];
  for (const w of pool) {
    const id   = w.id || w.simplified;
    const card = srsData[id];
    if (!card)                fresh.push(w);
    else if (isDue(card.due)) due.push(w);
    // else: card ada tapi belum jatuh tempo -> sengaja dilewati (lihat fallback di bawah)
  }
  shuffle(due);
  shuffle(fresh);

  // Fix: deck TEMATIK/BROWSE (tema, radikal, struktur, custom, fonetik,
  // antonim/sinonim, goresan) sebelumnya bisa jadi kosong TOTAL kalau semua
  // kartunya kebetulan sudah pernah direview & belum jatuh tempo lagi --
  // paling kentara di tema kecil (1-5 kartu): sekali direview, tema itu
  // "hilang" sampai jatuh tempo. Deck-deck ini memang untuk dijelajah/
  // dilihat ulang sesuka hati, bukan rotasi SRS ketat -- jadi kalau due+fresh
  // kosong tapi pool-nya sebenarnya ada isi, tampilkan ulang semua kartu
  // (mode review bebas) alih-alih kosong. Deck inti SRS (hsk-/all-due/
  // bookmarks/wrong) SENGAJA tidak disentuh di sini -- kalau رسلان mau
  // deck itu juga bebas dari jadwal, tinggal nyalakan toggle di atas.
  const isBrowseDeck = deckId.startsWith('theme-') || deckId.startsWith('radical-') ||
    deckId.startsWith('struct-') || deckId.startsWith('custom-') || deckId.startsWith('phonetic-') ||
    deckId.startsWith('strokecount-') || deckId.startsWith('pinyin-') || deckId.startsWith('akar-') ||
    deckId === 'antonyms' || deckId === 'synonyms' || deckId === 'stroke-easy' || deckId === 'stroke-hard';

  if (isBrowseDeck && due.length === 0 && fresh.length === 0 && pool.length > 0) {
    const reviewPool = pool.slice();
    shuffle(reviewPool);
    FC.lastQueueReviewReason = 'mastered'; // dibaca selectDeck() untuk toast yang beda
    return reviewPool.slice(0, sessionCardLimit);
  }
  FC.lastQueueReviewReason = null;

  if (sessionMode === 'fixed') {
    return [...due, ...fresh].slice(0, sessionCardLimit);
  }
  return [...due, ...fresh.slice(0, 20)];
}


/* ── B4: LOAD DATA FONETIK + RENDER SIDEBAR ────────────────── */
async function loadPhoneticData() {
  try {
    const res = await fetch('data/index_phonetic.json');
    if (res.ok) {
      FC.dataPhonetic = await res.json();
      // index_phonetic.json aslinya component → [wordId, ...]. Untuk
      // ditampilkan per-kartu di muka belakang, dibalik jadi
      // wordId → [component, ...] sekali saja di sini (bukan tiap render).
      FC.phoneticReverse = {};
      for (const [comp, ids] of Object.entries(FC.dataPhonetic)) {
        for (const id of ids) {
          if (!FC.phoneticReverse[id]) FC.phoneticReverse[id] = [];
          FC.phoneticReverse[id].push(comp);
        }
      }
    }
    renderSidebarFonetik();
  } catch (e) { console.warn('index_phonetic.json tidak tersedia:', e); }
}


function renderSidebarFonetik() {
  const container = $('sidebar-fonetik-list');
  if (!container || !FC.dataPhonetic) return;

  const entries = Object.entries(FC.dataPhonetic)
    .map(([comp, ids]) => ({ comp, count: ids.length }))
    .sort((a, b) => b.count - a.count);

  const COLLAPSE_AT = 15;
  container.innerHTML = '';

  function buildItems(list) {
    const frag = document.createDocumentFragment();
    list.forEach(({ comp, count }) => {
      const deckId = 'phonetic-' + encodeURIComponent(comp);
      const el = document.createElement('div');
      el.className = 'sidebar-item';
      el.dataset.deck = deckId;
      el.innerHTML = `<span style="font-size:1.05rem">${comp}</span><span class="item-count">${count}</span>`;
      el.addEventListener('click', () => selectDeck(deckId, 'Fonetik: ' + comp));
      frag.appendChild(el);
    });
    return frag;
  }

  container.appendChild(buildItems(entries.slice(0, COLLAPSE_AT)));

  if (entries.length > COLLAPSE_AT) {
    const extra = document.createElement('div');
    extra.id = 'fonetik-extra';
    extra.classList.add('hidden');
    extra.appendChild(buildItems(entries.slice(COLLAPSE_AT)));
    container.appendChild(extra);

    const btn = document.createElement('button');
    btn.className = 'sidebar-item';
    btn.style.cssText = 'width:100%;text-align:center;color:var(--text-muted);font-size:0.75rem;justify-content:center;';
    btn.textContent = `+ Tampilkan semua (${entries.length - COLLAPSE_AT} lagi)`;
    btn.addEventListener('click', () => {
      const ex = $('fonetik-extra');
      const hidden = ex.classList.toggle('hidden');
      btn.textContent = hidden
        ? `+ Tampilkan semua (${entries.length - COLLAPSE_AT} lagi)`
        : '− Tampilkan lebih sedikit';
      const body = container.closest('.sidebar-section-body');
      if (body && !body.classList.contains('collapsed')) body.style.maxHeight = '';
    });
    container.appendChild(btn);
  }
}


/* ── B5a: RENDER SIDEBAR STRUKTUR ───────────────────────────── */
function renderSidebarStruktur() {
  const container = $('sidebar-struktur-list');
  if (!container || !FC.allWords) return;

  const STRUCT_LABELS = {
    'left-right':        '⿰ Kiri-Kanan',
    'top-bottom':        '⿱ Atas-Bawah',
    'full':              '□ Tunggal',
    'enclosed':          '⿴ Terkurung',
    'semi-enclosed':     '⿶ Semi-Kurung',
    'surrounding':       '⿵ Mengelilingi',
    'overlapping':       '⿻ Bertumpuk',
    'left-middle-right': '⿲ Kiri-Tengah-Kanan',
    'top-middle-bottom': '⿳ Atas-Tengah-Bawah',
  };

  // Hitung jumlah per struktur
  const counts = {};
  FC.allWords.forEach(w => {
    const s = w.structure;
    if (s) counts[s] = (counts[s] || 0) + 1;
  });

  container.innerHTML = '';
  Object.entries(counts)
    .sort((a, b) => b[1] - a[1])
    .forEach(([struct, count]) => {
      const deckId = 'struct-' + encodeURIComponent(struct);
      const label  = STRUCT_LABELS[struct] || struct;
      const el = document.createElement('div');
      el.className = 'sidebar-item';
      el.dataset.deck = deckId;
      el.innerHTML = `<span>${label}</span><span class="item-count">${count}</span>`;
      el.addEventListener('click', () => selectDeck(deckId, 'Struktur: ' + label));
      container.appendChild(el);
    });
}


/* ── B5d: Cek data antonyms ─────────────────────────────────── */
function checkAntonymsData() {
  if (!FC.allWords) return;
  const withAntonyms = FC.allWords.filter(w =>
    Array.isArray(w.antonyms) ? w.antonyms.length > 0 : !!w.antonyms
  );
  const el = $('due-antonyms');
  if (el) el.textContent = withAntonyms.length > 0 ? withAntonyms.length : '—';
}


/* ── Sama seperti checkAntonymsData, tapi untuk Sinonim ────────── */
function checkSynonymsData() {
  if (!FC.allWords) return;
  const withSynonyms = FC.allWords.filter(w =>
    Array.isArray(w.synonyms) ? w.synonyms.length > 0 : !!w.synonyms
  );
  const el = $('due-synonyms');
  if (el) el.textContent = withSynonyms.length > 0 ? withSynonyms.length : '—';
}


/* ── E.0.3: Load data Karakter Mirip (kemiripan bentuk tulisan) ─────
   Datanya file terpisah data/confusion_groups.json (160 grup, BUKAN
   turunan field app_words.json) -- file yang sama dipakai panel
   "👀 Karakter Mirip" di kamus-karakter-mirip.js (Kamus). Lazy-fetch
   sekali di sini, dipanggil dari flashcard-init.js sejajar checkAntonymsData(). */
async function loadConfusionData() {
  // Data mentah disimpan apa adanya (belum di-resolve ke objek kata) --
  // resolusi ke FC.wordBySimplified dilakukan di buildConfusionGroups()
  // (flashcard-games.js) saat deck dipilih, sama pola spt buildToneTrapGroups().
  try {
    const res = await fetch('data/confusion_groups.json');
    if (res.ok) {
      const data = await res.json();
      FC.confusionGroupsRaw = Array.isArray(data.groups) ? data.groups : [];
    } else {
      FC.confusionGroupsRaw = [];
    }
  } catch (e) {
    console.warn('[flashcard] gagal load data/confusion_groups.json:', e);
    FC.confusionGroupsRaw = [];
  }
}

/* ── B-nuance: Load data pasangan near-synonym (Tier 4) ─────────────
   Beda dari checkAntonymsData/checkSynonymsData di atas: datanya BUKAN
   turunan field app_words.json, melainkan file terpisah
   data/nuance_pairs.json -- persis file yang sama dipakai panel "Beda
   dengan Kata Mirip" di kamus-nuance.js (Kamus). Lazy-fetch sekali di
   sini, dipanggil dari flashcard-init.js sejajar checkAntonymsData(). */
async function loadNuanceData() {
  try {
    const res = await fetch('data/nuance_pairs.json');
    if (res.ok) {
      const data = await res.json();
      FC.nuancePairs = Array.isArray(data.pairs) ? data.pairs : [];
    } else {
      FC.nuancePairs = [];
    }
  } catch (e) {
    console.warn('data/nuance_pairs.json tidak tersedia:', e);
    FC.nuancePairs = [];
  }

  // Hitung jumlah SOAL (bukan jumlah pasangan) -- pasangan dgn hanzi sama
  // (kasus 借 dua arah) tidak menghasilkan soal, lihat buildNuanceQuestions().
  const count = buildNuanceQuestions(FC.nuancePairs).length;
  const el = $('due-nuance');
  if (el) el.textContent = count > 0 ? count : '—';
}


/* ── B-pola: Load data pola pembentukan kata (Tier 4, BARU) ─────────
   Beda dari checkAntonymsData/checkSynonymsData: datanya BUKAN turunan
   field app_words.json, melainkan file terpisah data/kata_majemuk_pola.json
   -- persis file yang sama dipakai panel "Pola Pembentukan Kata" di
   kamus-pola.js (Kamus). Lazy-fetch sekali di sini, dipanggil dari
   flashcard-init.js sejajar loadNuanceData(). */
async function loadPolaGameData() {
  try {
    const res = await fetch('data/kata_majemuk_pola.json');
    if (res.ok) {
      const data = await res.json();
      FC.polaEntries = Array.isArray(data) ? data : [];
    } else {
      FC.polaEntries = [];
    }
  } catch (e) {
    console.warn('data/kata_majemuk_pola.json tidak tersedia:', e);
    FC.polaEntries = [];
  }

  const count = buildPolaQuestions(FC.polaEntries).length;
  const el = $('due-pola-kata');
  if (el) el.textContent = count > 0 ? count : '—';
}

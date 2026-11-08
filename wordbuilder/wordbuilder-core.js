/* ═══════════════════════════════════════════════════════════════
   wordbuilder-core.js — State WB, load word pools & penjelasan pola,
   filter HSK, ingat state terakhir, cross-link Flashcard/Tatabahasa,
   switchTab
═══════════════════════════════════════════════════════════════ */
'use strict';

const HSK_LEVELS = [1, 2, 3, 4, 5, 6, 7];
const HSK_STORAGE_KEY = 'mandarin_wb_hsk';

let WORD_POOLS      = {};   // dimuat dari data/wb_pools.json via loadWordPools()
let wordPoolsLoaded = false;

let PATTERN_EXPLANATIONS   = {};   // dimuat dari data/pattern_explanations.json
let explanationsLoaded     = false;

const WB = {
  activePattern: null,   // key dari PATTERNS
  slotValues:    {},     // { slotId: { cn, py, id, hsk } }
  hskFilter:     new Set(HSK_LEVELS), // level HSK aktif, default semua
  pendingPrefill: null,  // { slotId, entry } — sekali pakai, dari wb_ref_word
  pendingSlotValues: null, // { slotId: {cn,py,id,hsk}, ... } — sekali pakai, dari Koleksi Tersimpan
  masteryFilter: 'all',  // 'all' | 'mastered' | 'weak' (Tier 2)
  exampleStock:  [],     // stok gabungan Contoh Kalimat + Contoh Tambahan, pola aktif
  exampleIndex:  0,
  currentTab:    'tunggal', // 'tunggal' | 'majemuk' | 'fungsi' | 'kuis' -- utk ingat state terakhir
};

/* ── UTILS ─────────────────────────────────────────────────── */
/* $(), showToast(), escHtml() sekarang dari shared/core.js */

/* ── MUAT WORD_POOLS DARI JSON ─────────────────────────────── */
async function loadWordPools() {
  try {
    const res = await fetch('data/wb_pools.json');
    if (!res.ok) throw new Error('HTTP ' + res.status);
    WORD_POOLS      = await res.json();
    wordPoolsLoaded  = true;
  } catch (e) {
    console.error('Gagal memuat data/wb_pools.json:', e);
    showToast('⚠ Gagal memuat data kata. Cek data/wb_pools.json ada di folder data/.', 'error');
  }
}


/* ── MUAT PENJELASAN POLA DARI JSON ────────────────────────── */
async function loadPatternExplanations() {
  try {
    const res = await fetch('data/pattern_explanations.json');
    if (!res.ok) throw new Error('HTTP ' + res.status);
    PATTERN_EXPLANATIONS = await res.json();
    explanationsLoaded    = true;
  } catch (e) {
    console.error('Gagal memuat data/pattern_explanations.json:', e);
    // Gagal senyap: panel "Penjelasan Lengkap" tetap ada, cuma kosong.
    // Tidak menghalangi fitur inti (susun kalimat) yang tidak bergantung pada ini.
  }
}


/* ── wb_ref_word: PREFILL DARI FLASHCARD ───────────────────────
   wb_ref_word disimpan flashcard.html memakai skema ENTRY MENTAH
   app_words.json (field: simplified, pinyin, meanings_id, hsk, pos,
   themes, frequency, ...) — BUKAN skema {cn,py,id,hsk} yang dipakai
   WORD_POOLS. Fungsi-fungsi di bawah ini me-replika logika yang sama
   persis dengan py/generate_wordbuilder_pools.py supaya kata yang
   di-prefill konsisten dengan pool aslinya. */

function asList(val) {
  if (val === null || val === undefined) return [];
  return Array.isArray(val) ? val : [val];
}


function asHskInt(val) {
  if (val === null || val === undefined || typeof val === 'boolean') return null;
  if (typeof val === 'number') return Math.trunc(val);
  if (typeof val === 'string') {
    const digits = val.replace(/\D/g, '');
    return digits ? parseInt(digits, 10) : null;
  }
  return null;
}


function primaryMeaningJS(word) {
  let meanings = word.meanings_id || [];
  if (typeof meanings === 'string') meanings = [meanings];
  if (!meanings.length) return '';

  const isVariantNote = (m) => {
    const low = m.toLowerCase();
    return low.startsWith('varian dari') || low.startsWith('varian lama dari');
  };
  const stripBoundForm = (m) => {
    const prefix = '(bentuk terikat)';
    return m.toLowerCase().startsWith(prefix) ? m.slice(prefix.length).trim() : m;
  };

  for (const m of meanings) {
    if (!isVariantNote(m)) return stripBoundForm(m);
  }
  return meanings[0];
}


// Ubah entry mentah app_words.json -> skema {cn, py, id, hsk} (sama seperti WORD_POOLS)
function convertRefWordToEntry(raw) {
  return {
    cn:  raw.simplified || '',
    py:  raw.pinyin || '',
    id:  primaryMeaningJS(raw),
    hsk: asHskInt(raw.hsk),
  };
}


// Tentukan 1 pool paling representatif untuk kata ini, mengikuti urutan
// prioritas yang sama dengan generate_wordbuilder_pools.py (dengan sedikit
// penyesuaian: cabang 'identitas' dicek sebelum 'subyek' supaya kata profesi
// diarahkan ke pola "S + 是 + O", bukan tenggelam jadi subjek generik).
function pickPoolForRefWord(raw) {
  const pos    = asList(raw.pos);
  const themes = asList(raw.themes);

  if (pos.includes('q')) return 'satuan';
  if (pos.includes('m')) return 'angka';
  if (pos.includes('t') || themes.includes('waktu') || themes.includes('hari_tanggal')) return 'waktu';
  if (pos.includes('f') || themes.includes('arah_lokasi') || themes.includes('negara_budaya')) return 'tempat';
  if (pos.includes('r')) return 'subyek'; // pronomina selalu jadi subjek
  if ((pos.includes('n') || pos.includes('vn')) && themes.includes('pekerjaan')) return 'identitas';
  if ((pos.includes('n') || pos.includes('vn')) && themes.includes('keluarga')) return 'subyek';
  if (pos.includes('v') || pos.includes('vn')) return 'kata_kerja';
  if (pos.includes('a')) return 'kata_sifat';
  return 'objek_umum'; // fallback: kata benda umum
}


// Pool -> pola default + slot tujuan yang paling representatif untuk kata itu.
const REF_WORD_TARGET_MAP = {
  satuan:     { pattern: 'S-Num-M-N', slot: 'm'   },
  angka:      { pattern: 'S-Num-M-N', slot: 'num' },
  waktu:      { pattern: 'S-T-V-O',   slot: 't'   },
  tempat:     { pattern: 'S-zai-L',   slot: 'l'   },
  subyek:     { pattern: 'S-V-O',     slot: 's'   },
  kata_kerja: { pattern: 'S-V-O',     slot: 'v'   },
  kata_sifat: { pattern: 'S-hen-Adj', slot: 'adj' },
  identitas:  { pattern: 'S-shi-O',   slot: 'o'   },
  objek_umum: { pattern: 'S-V-O',     slot: 'o'   },
};

// Baca wb_ref_pattern (kalau ada), lalu langsung buka tab + pola yang cocok.
// Disimpan tatabahasa.html saat رسلان klik "Latih pola ini →" pada poin
// gramatika yang match salah satu dari 34 pola Word Builder. Beda dengan
// wb_ref_word (isi 1 slot dari kata Flashcard): ini cuma buka pola & tab
// yang benar, tidak ada prefill slot. Key WAJIB dihapus setelah dibaca.
function consumeRefPattern() {
  const patternKey = localStorage.getItem('wb_ref_pattern');
  if (!patternKey) return false;

  localStorage.removeItem('wb_ref_pattern'); // hapus dulu -- sekali pakai

  if (!PATTERNS[patternKey]) {
    console.error('wb_ref_pattern berisi kunci pola yang tidak dikenal, diabaikan:', patternKey);
    return false;
  }

  const tab = patternKey.startsWith('C-') ? 'majemuk'
            : patternKey.startsWith('F-') ? 'fungsi'
            : 'tunggal';
  switchTab(tab);
  loadPattern(patternKey);
  return true;
}


// Baca wb_ref_word (kalau ada), lalu langsung buka pola + isi slot yang cocok.
// Key WAJIB dihapus setelah dibaca, apapun hasilnya (sukses/gagal parse).
// Return true kalau berhasil dikonsumsi -- dipakai init() untuk tahu apakah
// harus skip restoreLastViewState() (handoff dari Flashcard prioritas lebih
// tinggi daripada sekadar "state terakhir").
function consumeRefWord() {
  const raw = localStorage.getItem('wb_ref_word');
  if (!raw) return false;

  localStorage.removeItem('wb_ref_word'); // hapus dulu -- sekali pakai

  let word;
  try {
    word = JSON.parse(raw);
  } catch (e) {
    console.error('wb_ref_word rusak (bukan JSON valid), diabaikan:', e);
    return false;
  }

  if (!word || !word.simplified) {
    console.error('wb_ref_word tidak punya field "simplified", diabaikan.');
    return false;
  }

  const entry  = convertRefWordToEntry(word);
  const pool   = pickPoolForRefWord(word);
  const target = REF_WORD_TARGET_MAP[pool] || REF_WORD_TARGET_MAP.objek_umum;

  WB.pendingPrefill = { slotId: target.slot, entry };
  loadPattern(target.pattern);
  showToast(`✓ "${entry.cn}" otomatis diisi dari Flashcard.`, 'success');
  return true;
}


/* ── INGAT STATE TERAKHIR (Tier 1 lintas-halaman) ──────────────────
   Setiap kali pola/tab dipilih, disimpan ke localStorage supaya kalau
   رسلان pindah ke halaman lain lewat navbar lalu balik lagi, Word Builder
   menampilkan pola & tab yang terakhir dilihat -- bukan mulai dari nol. */
const WB_LAST_STATE_KEY = 'mandarin_wb_last_state_v1';

function saveLastViewState() {
  try {
    localStorage.setItem(WB_LAST_STATE_KEY, JSON.stringify({
      pattern: WB.activePattern,
      tab:     WB.currentTab || 'tunggal',
    }));
  } catch (e) { /* abaikan senyap -- bukan fitur kritis */ }
}


function restoreLastViewState() {
  let saved;
  try {
    saved = JSON.parse(localStorage.getItem(WB_LAST_STATE_KEY) || 'null');
  } catch (e) { return; }
  if (!saved) return;

  if (saved.tab && saved.tab !== 'kuis') switchTab(saved.tab);
  if (saved.pattern && PATTERNS[saved.pattern]) {
    loadPattern(saved.pattern);
  }
}



/* ── FILTER HSK ─────────────────────────────────────────────── */
function loadHskFilterFromStorage() {
  try {
    const raw = localStorage.getItem(HSK_STORAGE_KEY);
    if (!raw) return; // default: semua level aktif
    const arr = JSON.parse(raw);
    if (Array.isArray(arr) && arr.length) {
      WB.hskFilter = new Set(arr);
    }
  } catch (e) { /* abaikan, pakai default */ }
}


function saveHskFilterToStorage() {
  try {
    localStorage.setItem(HSK_STORAGE_KEY, JSON.stringify([...WB.hskFilter]));
  } catch (e) { /* localStorage penuh/nonaktif, abaikan */ }
}


function initHskChips() {
  const container = $('wb-hsk-chips');
  container.innerHTML = '';
  HSK_LEVELS.forEach(lvl => {
    const chip = document.createElement('button');
    chip.type = 'button';
    chip.className = 'wb-hsk-chip' + (WB.hskFilter.has(lvl) ? ' active' : '');
    chip.textContent = 'HSK' + lvl;
    chip.addEventListener('click', () => toggleHskLevel(lvl));
    container.appendChild(chip);
  });
  updateHskAllLabel();
}


function toggleHskLevel(level) {
  if (WB.hskFilter.has(level)) {
    WB.hskFilter.delete(level);
  } else {
    WB.hskFilter.add(level);
  }
  saveHskFilterToStorage();
  refreshHskChipsUI();
  reRenderActivePatternSlots();
}


function toggleHskAll() {
  // Kalau semua sudah aktif -> kosongkan. Kalau belum -> aktifkan semua.
  if (WB.hskFilter.size === HSK_LEVELS.length) {
    WB.hskFilter.clear();
  } else {
    WB.hskFilter = new Set(HSK_LEVELS);
  }
  saveHskFilterToStorage();
  refreshHskChipsUI();
  reRenderActivePatternSlots();
}


function refreshHskChipsUI() {
  document.querySelectorAll('.wb-hsk-chip').forEach((chip, i) => {
    chip.classList.toggle('active', WB.hskFilter.has(HSK_LEVELS[i]));
  });
  updateHskAllLabel();
}


function updateHskAllLabel() {
  const btn = $('wb-hsk-toggle-all');
  if (!btn) return;
  btn.textContent = (WB.hskFilter.size === HSK_LEVELS.length) ? 'Kosongkan' : 'Semua';
}


function getFilteredPool(poolName) {
  const pool = WORD_POOLS[poolName] || [];
  return pool
    .filter(w => WB.hskFilter.has(w.hsk))
    .filter(w => {
      if (WB.masteryFilter === 'mastered') return isMastered(w.cn);
      if (WB.masteryFilter === 'weak')     return isWeak(w.cn);
      return true; // 'all'
    });
}


/* ── FILTER MASTERY (Tier 2): Semua / Sudah Dikuasai / Sering Salah ── */
function setMasteryFilter(value) {
  WB.masteryFilter = value;
  srsReaderRefresh(); // baca ulang data terbaru (jaga-jaga diubah dari flashcard di tab lain)
  reRenderActivePatternSlots();
}


function reRenderActivePatternSlots() {
  if (!WB.activePattern) return;
  const pattern = PATTERNS[WB.activePattern];
  if (!pattern) return;
  WB.slotValues = {};
  renderSlots(pattern);
  resetOutput();
}


/* ── TAB SWITCHER ───────────────────────────────────────────── */
function switchTab(tabName) {
  WB.currentTab = tabName;
  saveLastViewState();

  // Update tab button (Tunggal/Majemuk/Fungsi)
  document.querySelectorAll('.wb-tab').forEach(t => {
    t.classList.toggle('active', t.dataset.tab === tabName);
  });
  // Tombol Kuis Pola sekarang di baris terpisah dengan class sendiri
  const kuisBtn = document.querySelector('.wb-tab-kuis');
  if (kuisBtn) kuisBtn.classList.toggle('active', tabName === 'kuis');
  // Tampilkan konten tab (daftar pola di sidebar)
  ['tunggal', 'majemuk', 'fungsi'].forEach(name => {
    const el = $('tab-' + name);
    if (el) el.classList.toggle('hidden', name !== tabName);
  });

  if (tabName === 'kuis') {
    $('wb-choose-screen').classList.add('hidden');
    $('wb-content').classList.add('hidden');
    $('wb-quiz-screen').classList.remove('hidden');
    startQuizQuestion();
  } else {
    $('wb-quiz-screen').classList.add('hidden');
    // Kembalikan tampilan builder sesuai ada/tidaknya pola aktif
    if (WB.activePattern) {
      $('wb-choose-screen').classList.add('hidden');
      $('wb-content').classList.remove('hidden');
    } else {
      $('wb-choose-screen').classList.remove('hidden');
      $('wb-content').classList.add('hidden');
    }
  }
}

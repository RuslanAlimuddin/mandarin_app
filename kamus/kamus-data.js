/* ═══════════════════════════════════════════════════════════════
   kamus/kamus-data.js — Mandarin Interaktif
   STATE global, utilitas kecil (debounce/highlight/label), load data kamus & index radikal/goresan/tema
   Bagian dari modularisasi kamus.html. Dimuat sebagai <script src>
   biasa (bukan ES module) -- semua fungsi tetap di scope global,
   jadi urutan file lain relatif bebas KECUALI kamus-init.js yang
   WAJIB paling akhir.
   ═══════════════════════════════════════════════════════════════ */

'use strict';

/* ── STATE ─────────────────────────────────────────────────── */
const STATE = {
  dataHsk:      null,   // array dari app_words.json
  dataCidict:   null,   // array dari cidict_index.json
  indexHsk:     null,   // objek dari index_hsk.json
  dataRadical:  null,   // object index_radical.json — Fix #12
  dataStroke:   null,   // object index_stroke.json — Fix #14
  dataTheme:    null,   // object index_theme.json — Fix #13
  dataPhonetic: null,   // object index_phonetic.json — fitur silang dgn Flashcard (komponen fonetik → [wordId,...])
  dataAkar:     null,   // object produktif_karakter.json — "Akar Kosakata": karakter dasar → daftar kata turunan (analogi akar/sharaf)
  dataKhusus:   null,   // object index_kelompok_khusus.json — leksikon khusus (kata seru/onomatope/sapaan/partikel modal), format sama seperti index_theme.json (Peta 11 Pilar, A.4/A.5)
  dataConfusion:null,   // array confusion_groups.json.groups — "Karakter Mirip" (E.0.3, kemiripan BENTUK TULISAN, mis. 己/已/巳), tertunda sejak BLUEPRINT v8
  dataStructure:null,   // object dibangun client-side oleh buildStructureIndex() -- bukan file index terpisah, karena field `structure` sudah ada langsung di tiap entri app_words.json
  source:       'hsk',  // 'hsk' | 'cidict'
  searchMode:   'auto', // 'auto' | 'hanzi' | 'pinyin' | 'id' | 'en'
  sidebarFilter:'all',  // 'all' | 'hsk-1' .. 'hsk-7' | 'bookmarks' | 'recent'
  query:        '',
  results:      [],     // hasil pencarian penuh
  rendered:     0,      // jumlah kartu yang sudah dirender
  PAGE_SIZE:    40,     // kartu per batch
  selectedId:   null,   // ID kata yg dipilih di detail
  bookmarks:    new Set(),
  recentWords:  [],     // max 50
  viewMode:     'card', // Fix #5: 'card' | 'table'
  tableSortKey: null,
  tableSortDir: 1,       // 1 = asc, -1 = desc
  cardSortKey:  null,    // Fix A3: sort cepat di mode kartu — null = relevansi (default)
  cardSortDir:  1,
  groupType:    null,    // Fix #12-14: 'radical'|'stroke'|'theme'|'pinyin' aktif di panel
};

/* ── UTILS ─────────────────────────────────────────────────── */
/* $(), showToast(), escHtml() dari shared/core.js.
   isProbablyHanzi, isProbablyPinyin, isProbablyIndonesian, ID_STOPWORDS,
   detectMode, normalizePinyin, numericToDiacritic, TONE_MARKS,
   numericSyllableToDiacritic sekarang dari shared/pinyin.js */

function debounce(fn, ms) {
  let t;
  return (...args) => { clearTimeout(t); t = setTimeout(() => fn(...args), ms); };
}

function highlight(text, query) {
  if (!query || !text) return escHtml(text);
  const safe = escHtml(text);
  const q = escHtml(query.toLowerCase());
  const idx = safe.toLowerCase().indexOf(q);
  if (idx === -1) return safe;
  return safe.slice(0, idx) +
         '<mark>' + safe.slice(idx, idx + q.length) + '</mark>' +
         safe.slice(idx + q.length);
}

function hskClass(level) {
  const l = parseInt(level);
  if (l >= 7) return 'hsk-7';
  return `hsk-${l}`;
}

function hskLabel(level) {
  const l = parseInt(level);
  return l >= 7 ? 'HSK 7-9' : `HSK ${l}`;
}

/* Peta 13 tipe struktur SESUAI data riil app_words.json (diverifikasi via
   inspect_stroke_data.py) -- bukan 9 tipe seperti versi lama. Setiap tipe
   juga punya "order": prinsip urutan penulisan UMUM (bukan jalur goresan
   presisi per karakter, karena data itu tidak tersedia -- lihat catatan
   di UI Modul Stroke Order). */
const STRUCTURE_INFO = {
  'left-right':       { label: '⿰ Kiri–Kanan',            order: 'Tulis komponen KIRI dulu, baru KANAN.' },
  'top-bottom':       { label: '⿱ Atas–Bawah',            order: 'Tulis komponen ATAS dulu, baru BAWAH.' },
  'single':           { label: '□ Tunggal',               order: 'Karakter utuh, tidak tersusun dari komponen terpisah.' },
  'overlapping':      { label: '⿻ Bertumpuk',             order: 'Komponen saling tumpang-tindih; ikuti urutan goresan standar tiap bagian.' },
  'left-mid-right':   { label: '⿲ Kiri–Tengah–Kanan',     order: 'Tulis KIRI, lalu TENGAH, baru KANAN.' },
  'top-mid-bottom':   { label: '⿳ Atas–Tengah–Bawah',     order: 'Tulis ATAS, lalu TENGAH, baru BAWAH.' },
  'enclosed-full':    { label: '⿴ Terkurung Penuh',       order: 'Tulis bagian LUAR (pembungkus) dulu, ISI di dalamnya, baru tutup sisi bawah pembungkus.' },
  'enclosed-top':     { label: '⿵ Terkurung Atas',        order: 'Tulis bagian pembungkus ATAS dulu, baru ISI di dalamnya.' },
  'enclosed-bottom':  { label: '⿶ Terkurung Bawah',       order: 'Tulis ISI dulu, baru bagian pembungkus BAWAH.' },
  'enclosed-left':    { label: '⿷ Terkurung Kiri',        order: 'Tulis bagian pembungkus KIRI dulu, baru ISI di dalamnya.' },
  'enclosed-topleft': { label: '⿸ Terkurung Kiri-Atas',   order: 'Tulis bagian pembungkus (kiri-atas) dulu, baru ISI.' },
  'enclosed-topright':{ label: '⿹ Terkurung Kanan-Atas',  order: 'Tulis ISI dulu, baru bagian pembungkus (kanan-atas).' },
  'enclosed-botleft': { label: '⿺ Terkurung Kiri-Bawah',  order: 'Tulis ISI dulu, baru bagian pembungkus (kiri-bawah) -- pola radikal seperti 辶/廴.' },
};

function structureLabel(s) {
  const info = STRUCTURE_INFO[s];
  return info ? info.label : (s || '—');
}

function structureOrderText(s) {
  const info = STRUCTURE_INFO[s];
  return info ? info.order : '';
}

function posLabel(pos) {
  const MAP = {
    'n': 'KB', 'v': 'KK', 'a': 'KS', 'r': 'KB-Ganti',
    'd': 'Ket', 'p': 'Prepos', 'c': 'Konj', 'u': 'Part',
    'm': 'K-Bil', 'q': 'Satuan', 'e': 'Ekskl', 'o': 'Onomatope',
    'tg': 'K-Waktu', 'f': 'K-Tempat', 'vn': 'KK-Nom',
    'an': 'KS-Nom', 'vi': 'KK-Intr',
  };
  return MAP[pos] || pos;
}

/* ── LOAD DATA ─────────────────────────────────────────────── */
async function loadData() {
  showLoading(true);
  try {
    const res = await fetch('data/app_words.json');
    if (!res.ok) throw new Error('Gagal memuat app_words.json');
    STATE.dataHsk = await res.json();
    buildCharMeaningIndex();
    loadCharEtymology(); // file kecil, dimuat sekalian -- lihat catatan di bawah
    updateSidebarCounts();
    loadStorageData();
    showLoading(false);
    showLanding(true);
    // Fix #12-14: load index radikal/goresan/tema/khusus di background (tidak
    // di-await di sini supaya render awal tetap cepat) -- promise-nya disimpan
    // di STATE supaya pemanggil lain (mis. hash-router deep-link di
    // kamus-init.js) bisa await selesai-nya sebelum baca STATE.dataTheme/dst.
    STATE.indexFilesPromise = loadIndexFiles();
  } catch (err) {
    showLoading(false);
    const isCors = err.message.includes('Failed to fetch') || err.name === 'TypeError';
    const msg = isCors
      ? '⚠ CORS Error — Jalankan via: python -m http.server 8000'
      : '⚠ Gagal memuat data: ' + err.message;
    showToast(msg, 'error');
    const landing = $('landing-state');
    if (landing) landing.innerHTML = `
      <div style="color:var(--red);text-align:center;padding:20px;max-width:380px">
        <div style="font-size:2rem;margin-bottom:12px">⚠</div>
        <div style="font-weight:600;margin-bottom:8px;color:var(--text-main)">Gagal Memuat Data</div>
        <div style="font-size:0.82rem;line-height:1.8;color:var(--text-dim)">
          Browser memblokir akses file lokal (CORS).<br>
          Buka terminal di folder <strong>mandarin_app/</strong> lalu jalankan:<br>
          <code style="background:var(--bg-card2);padding:4px 12px;border-radius:4px;display:inline-block;margin:8px 0;color:var(--gold)">python -m http.server 8000</code><br>
          Kemudian buka: <strong>http://localhost:8000</strong>
        </div>
      </div>`;
    console.error(err);
  }
}

/* ── LOAD INDEX RADIKAL/GORESAN/TEMA (Fix #12-14) ──────────── */
async function loadIndexFiles() {
  try {
    const [resR, resS, resT, resP, resA, resK, resM] = await Promise.all([
      fetch('data/index_radical.json'),
      fetch('data/index_stroke.json'),
      fetch('data/index_theme.json'),
      fetch('data/index_phonetic.json'),
      fetch('data/produktif_karakter.json'),
      fetch('data/index_kelompok_khusus.json'),
      fetch('data/confusion_groups.json'),
    ]);
    if (resR.ok) STATE.dataRadical  = await resR.json();
    if (resS.ok) STATE.dataStroke   = await resS.json();
    if (resT.ok) STATE.dataTheme    = await resT.json();
    if (resP.ok) STATE.dataPhonetic = await resP.json();
    if (resA.ok) {
      STATE.dataAkar = await resA.json();
      const cntEl = $('cnt-akar');
      if (cntEl) cntEl.textContent = Object.keys(STATE.dataAkar).length.toLocaleString('id');
    }
    if (resK.ok) {
      STATE.dataKhusus = await resK.json();
      const cntEl = $('cnt-khusus');
      if (cntEl) cntEl.textContent = Object.keys(STATE.dataKhusus).length.toLocaleString('id');
    }
    if (resM.ok) {
      // (E.0.3) confusion_groups.json dibungkus {groups:[...], metadata:{...}}
      // -- ambil array groups-nya saja, sama pola spt loadNuanceData() di
      // flashcard-decks.js yg juga ambil .pairs dari pembungkusnya.
      const dataM = await resM.json();
      STATE.dataConfusion = Array.isArray(dataM.groups) ? dataM.groups : [];
      const cntEl = $('cnt-mirip');
      if (cntEl) cntEl.textContent = STATE.dataConfusion.length.toLocaleString('id');
    }
  } catch (e) {
    console.warn('Gagal memuat index file kelompok:', e);
  }
}

async function loadCidict() {
  if (STATE.dataCidict) return; // sudah dimuat
  showToast('Memuat Cidict (±26 MB)…');
  try {
    const res = await fetch('data/cidict_index.json');
    if (!res.ok) throw new Error('Gagal memuat cidict_index.json');
    STATE.dataCidict = await res.json();
    showToast('✓ Cidict siap (' + STATE.dataCidict.length.toLocaleString('id') + ' kata)', 'success');
  } catch (err) {
    showToast('⚠ Gagal memuat Cidict: ' + err.message, 'error');
  }
}

/* ── INDEX MAKNA KARAKTER TUNGGAL (fitur mnemonic "Bantu Ingat") ────
   Dipakai renderDetail() (kamus-detail.js) untuk kata 2+ karakter.
   Prioritas sumber (dari paling akurat):
     1) data/char_etymology_id.json -- kurasi manual berbasis proyek
        Make Me a Hanzi (github.com/skishore/makemeahanzi), diterjemahkan
        & disesuaikan ke Bahasa Indonesia bertahap per batch (BUKAN semua
        karakter tercakup -- baru sebagian, terus bertambah tiap sesi).
     2) app_words.json (meanings_id[0] entri 1 karakter) -- fallback kalau
        karakter belum ada di batch etimologi.
     3) Cidict (lazy-load) -- fallback terakhir kalau app_words.json juga
        tidak punya entri karakter itu. */
STATE.charMeaningIndex = null; // dibangun oleh buildCharMeaningIndex() -- sumber (2)
STATE.charEtymology    = null; // dimuat oleh loadCharEtymology() -- sumber (1), prioritas tertinggi

async function loadCharEtymology() {
  try {
    const res = await fetch('data/char_etymology_id.json');
    if (!res.ok) { STATE.charEtymology = {}; return; }
    STATE.charEtymology = await res.json();
  } catch (e) {
    STATE.charEtymology = {}; // gagal senyap -- fitur mnemonic tetap jalan pakai sumber (2)/(3)
  }
}

/* Index untuk grup "Per Struktur" -- dibangun sekali dari STATE.dataHsk yang
   sudah ada di memori (bukan fetch file index_*.json terpisah seperti
   radikal/goresan/tema, karena field `structure` sudah tersedia langsung di
   tiap entri). Sengaja dibatasi HANYA karakter tunggal (length === 1):
   entri multi-karakter juga punya field `structure` di data, tapi nilainya
   tidak relevan secara konsep -- struktur IDC (⿰/⿱/dst) menjelaskan
   komposisi SATU karakter, bukan susunan kata. */
function buildStructureIndex() {
  const idx = {};
  (STATE.dataHsk || []).forEach(w => {
    const s = w.simplified || w.id || '';
    if (s.length !== 1) return;
    const struct = w.structure;
    if (!struct) return;
    if (!idx[struct]) idx[struct] = [];
    idx[struct].push(w.id || w.simplified);
  });
  STATE.dataStructure = idx;
}

function buildCharMeaningIndex() {
  const idx = {};
  (STATE.dataHsk || []).forEach(w => {
    const s = w.simplified || w.id;
    if (s && s.length === 1 && w.meanings_id && w.meanings_id.length) {
      if (!idx[s]) idx[s] = w.meanings_id[0]; // makna pertama = paling umum/singkat
    }
  });
  STATE.charMeaningIndex = idx;
}

// Sinkron: cek char_etymology_id.json dulu (paling akurat), lalu
// app_words.json, lalu Cidict KALAU sudah dimuat (tidak memicu fetch
// di sini -- pemanggil yang urus lazy-load-nya).
function getCharMeaning(char) {
  if (STATE.charEtymology && STATE.charEtymology[char] && STATE.charEtymology[char].gloss_id) {
    return STATE.charEtymology[char].gloss_id;
  }
  if (STATE.charMeaningIndex && STATE.charMeaningIndex[char]) {
    return STATE.charMeaningIndex[char];
  }
  if (STATE.dataCidict) {
    const hit = STATE.dataCidict.find(w => w.simplified === char);
    if (hit && hit.meanings_id && hit.meanings_id.length) {
      if (STATE.charMeaningIndex) STATE.charMeaningIndex[char] = hit.meanings_id[0]; // cache
      return hit.meanings_id[0];
    }
  }
  return null;
}


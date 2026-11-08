/* ═══════════════════════════════════════════════════════════════
   kamus/kamus-actions-filters.js — Mandarin Interaktif
   Aksi panel detail (dengarkan/simpan/flashcard), filter sidebar & sumber data, search-example, clear search
   Bagian dari modularisasi kamus.html. Dimuat sebagai <script src>
   biasa (bukan ES module) -- semua fungsi tetap di scope global,
   jadi urutan file lain relatif bebas KECUALI kamus-init.js yang
   WAJIB paling akhir.
   ═══════════════════════════════════════════════════════════════ */

/* ── AKSI DETAIL ───────────────────────────────────────────── */
function speakDetailWord() {
  const id = STATE.selectedId;
  if (!id) return;
  const word = findWordInResults(id);
  if (!word) return;
  speak(word.simplified || word.id, { rate: AudioTTS.rate });
}

function addToFlashcard() {
  const id = STATE.selectedId;
  if (!id) return;
  try {
    const srsKey = 'mandarin_srs_v1';
    const srs    = JSON.parse(localStorage.getItem(srsKey) || '{}');
    if (srs[id]) {
      showToast('Sudah ada di flashcard: ' + id);
    } else {
      const today = new Date().toISOString().slice(0, 10);
      srs[id] = { interval: 1, ease: 2.5, due: today, reps: 0, lapses: 0 };
      localStorage.setItem(srsKey, JSON.stringify(srs));
      showToast('✓ Ditambahkan ke flashcard: ' + id, 'success');
    }
  } catch (e) {
    showToast('⚠ Gagal menyimpan ke flashcard', 'error');
  }
}

function toggleBookmark() {
  const id = STATE.selectedId;
  if (!id) return;
  if (STATE.bookmarks.has(id)) {
    STATE.bookmarks.delete(id);
    showToast('Dihapus dari koleksi: ' + id);
  } else {
    STATE.bookmarks.add(id);
    showToast('✓ Disimpan ke koleksi: ' + id, 'success');
  }
  saveBookmarks();
  updateBookmarkBtn(id);
}

function updateBookmarkBtn(id) {
  const btn = $('btn-bookmark');
  if (!btn) return;
  const saved = STATE.bookmarks.has(id);
  btn.textContent = saved ? '★ Tersimpan' : '☆ Simpan';
  btn.classList.toggle('saved', saved);
}

/* ── FILTER & SOURCE CONTROL ───────────────────────────────── */
function setSidebarFilter(filter) {
  STATE.sidebarFilter = filter;
  closeGroupPanel();

  // Update visual aktif sidebar
  document.querySelectorAll('.sidebar-item').forEach(el => {
    el.classList.toggle('active', el.dataset.filter === filter);
  });

  // Jika filter bookmarks/recent, tampilkan koleksi
  if (filter === 'bookmarks') {
    showCollection('bookmarks');
  } else if (filter === 'recent') {
    showCollection('recent');
  } else {
    // Re-run pencarian dengan filter baru
    if (STATE.query && STATE.dataHsk) {
      doSearch(STATE.query);
    }
  }
  saveKamusLastState();
}

function showCollection(type) {
  showLanding(false);
  const data = STATE.dataHsk || [];
  let ids;
  if (type === 'bookmarks') {
    ids = [...STATE.bookmarks];
  } else {
    ids = STATE.recentWords.slice(0, 50);
  }

  const results = ids
    .map(id => data.find(w => (w.id || w.simplified) === id))
    .filter(Boolean);

  STATE.results  = results;
  STATE.rendered = 0;
  renderResultsBatch();
  updateResultsHeader(results.length);

  $('results-source').textContent = type === 'bookmarks' ? 'Koleksi' : 'Terakhir Dilihat';
}

function setSource(src) {
  STATE.source = src;
  $('src-hsk').classList.toggle('active',    src === 'hsk');
  $('src-cidict').classList.toggle('active', src === 'cidict');

  if (src === 'cidict' && !STATE.dataCidict) {
    loadCidict().then(() => {
      if (STATE.query) doSearch(STATE.query);
    });
  } else if (STATE.query) {
    doSearch(STATE.query);
  }
  saveKamusLastState();
}

function setSearchMode(mode) {
  STATE.searchMode = mode;
  document.querySelectorAll('.pill').forEach(p => {
    p.classList.toggle('active', p.dataset.mode === mode);
  });
  if (STATE.query && STATE.dataHsk) doSearch(STATE.query);
  saveKamusLastState();
}

function openGroupPanel(type) {
  STATE.groupType = type;
  const panel = $('group-panel');
  const grid  = $('group-panel-grid');
  const title = $('group-panel-title');

  const TITLES = {
    radical: 'Pilih Radikal',
    stroke:  'Pilih Jumlah Goresan',
    theme:   'Pilih Tema',
    pinyin:  'Pilih Inisial Pinyin',
    struct:  'Pilih Struktur Karakter',
    phonetic:'Pilih Komponen Fonetik',
    akar:    'Pilih Akar Kosakata',
    khusus:  'Pilih Kelompok Khusus',
    mirip:   'Pilih Grup Karakter Mirip',
  };
  title.textContent = TITLES[type] || 'Pilih';
  grid.innerHTML = '';

  if (type === 'radical') {
    if (!STATE.dataRadical) {
      grid.innerHTML = '<span style="color:var(--text-muted);font-size:0.8rem">Data radikal belum dimuat, tunggu sebentar lalu coba lagi.</span>';
    } else {
      const entries = Object.entries(STATE.dataRadical).sort((a, b) => b[1].length - a[1].length);
      entries.forEach(([rad, ids]) => {
        const chip = document.createElement('div');
        chip.className = 'group-chip';
        chip.innerHTML = `<span>${escHtml(rad)}</span><span class="gc-count">${ids.length}</span>`;
        chip.addEventListener('click', () => selectGroupItem('radical', rad));
        grid.appendChild(chip);
      });
    }
  } else if (type === 'stroke') {
    if (!STATE.dataStroke) {
      grid.innerHTML = '<span style="color:var(--text-muted);font-size:0.8rem">Data goresan belum dimuat, tunggu sebentar lalu coba lagi.</span>';
    } else {
      const entries = Object.entries(STATE.dataStroke)
        .sort((a, b) => parseInt(a[0]) - parseInt(b[0]));
      entries.forEach(([stroke, ids]) => {
        const chip = document.createElement('div');
        chip.className = 'group-chip';
        chip.innerHTML = `<span>${escHtml(stroke)} grs</span><span class="gc-count">${ids.length}</span>`;
        chip.addEventListener('click', () => selectGroupItem('stroke', stroke));
        grid.appendChild(chip);
      });
    }
  } else if (type === 'theme') {
    if (!STATE.dataTheme) {
      grid.innerHTML = '<span style="color:var(--text-muted);font-size:0.8rem">Data tema belum dimuat, tunggu sebentar lalu coba lagi.</span>';
    } else {
      const entries = Object.entries(STATE.dataTheme).sort((a, b) => b[1].count - a[1].count);
      entries.forEach(([key, val]) => {
        const chip = document.createElement('div');
        chip.className = 'group-chip';
        chip.innerHTML = `<span>${escHtml(val.label_id || key)}</span><span class="gc-count">${val.count || 0}</span>`;
        chip.addEventListener('click', () => selectGroupItem('theme', key));
        grid.appendChild(chip);
      });
    }
  } else if (type === 'pinyin') {
    renderPinyinLetterGrid();
  } else if (type === 'struct') {
    if (!STATE.dataStructure) buildStructureIndex();
    const entries = Object.entries(STATE.dataStructure).sort((a, b) => b[1].length - a[1].length);
    entries.forEach(([key, ids]) => {
      const chip = document.createElement('div');
      chip.className = 'group-chip';
      chip.innerHTML = `<span>${escHtml(structureLabel(key))}</span><span class="gc-count">${ids.length}</span>`;
      chip.addEventListener('click', () => selectGroupItem('struct', key));
      grid.appendChild(chip);
    });
  } else if (type === 'phonetic') {
    if (!STATE.dataPhonetic) {
      grid.innerHTML = '<span style="color:var(--text-muted);font-size:0.8rem">Data komponen fonetik belum dimuat, tunggu sebentar lalu coba lagi.</span>';
    } else {
      const entries = Object.entries(STATE.dataPhonetic).sort((a, b) => b[1].length - a[1].length);
      entries.forEach(([comp, ids]) => {
        const chip = document.createElement('div');
        chip.className = 'group-chip';
        chip.innerHTML = `<span style="font-size:1.05rem">${escHtml(comp)}</span><span class="gc-count">${ids.length}</span>`;
        chip.addEventListener('click', () => selectGroupItem('phonetic', comp));
        grid.appendChild(chip);
      });
    }
  } else if (type === 'akar') {
    // "Akar Kosakata": analogi akar kata pada sharaf/wazan bahasa Arab --
    // satu karakter dasar yang jadi cikal-bakal banyak kata majemuk.
    // Data dari data/produktif_karakter.json (hasil analisis_produktivitas.py),
    // dimuat lazy bersama index radikal/goresan/tema (lihat loadIndexFiles()).
    if (!STATE.dataAkar) {
      grid.innerHTML = '<span style="color:var(--text-muted);font-size:0.8rem">Data akar kosakata belum dimuat, tunggu sebentar lalu coba lagi.</span>';
    } else {
      const entries = Object.entries(STATE.dataAkar)
        .sort((a, b) => (b[1].jumlah_turunan || 0) - (a[1].jumlah_turunan || 0));
      entries.forEach(([akar, d]) => {
        const chip = document.createElement('div');
        chip.className = 'group-chip';
        chip.title = `${d.pinyin || ''} — ${d.arti || ''}`;
        chip.innerHTML = `<span style="font-size:1.05rem">${escHtml(akar)}</span><span class="gc-count">${d.jumlah_turunan || 0}</span>`;
        chip.addEventListener('click', () => selectGroupItem('akar', akar));
        grid.appendChild(chip);
      });
    }
  } else if (type === 'khusus') {
    renderKhususLevel1();
  } else if (type === 'mirip') {
    // (E.0.3) "Karakter Mirip" masuk Kelompok Kamus -- beda dari
    // radikal/tema/dst yg tiap chip = 1 KATEGORI berisi banyak kata,
    // di sini tiap chip = 1 GRUP KEMIRIPAN BENTUK (mis. "己已巳"), isi
    // klik-nya nunjukin SEMUA karakter dalam grup itu sekaligus --
    // sesuai permintaan رسلان: "melihat gambaran luas bersamaan
    // karakter-karakter yang mirip bentuknya".
    if (!STATE.dataConfusion) {
      grid.innerHTML = '<span style="color:var(--text-muted);font-size:0.8rem">Data karakter mirip belum dimuat, tunggu sebentar lalu coba lagi.</span>';
    } else {
      STATE.dataConfusion.forEach((g, idx) => {
        const allChars = [g.character].concat(g.confusable_with || []);
        const chip = document.createElement('div');
        chip.className = 'group-chip';
        chip.title = g.note || '';
        chip.innerHTML = `<span style="font-size:1.05rem">${escHtml(allChars.join(''))}</span><span class="gc-count">${allChars.length}</span>`;
        chip.addEventListener('click', () => selectGroupItem('mirip', idx));
        grid.appendChild(chip);
      });
    }
  } else {
    grid.innerHTML = '<span style="color:var(--text-muted);font-size:0.8rem">Fitur ini dalam pengembangan.</span>';
  }

  panel.classList.remove('hidden');
}

function closeGroupPanel() {
  $('group-panel').classList.add('hidden');
  STATE.groupType = null;
}

/* ── KELOMPOK KHUSUS: 2-3 LEVEL (kategori → sub → generasi utk Sapaan
   Keluarga) ────────────────────────────────────────────────────────
   Sebelumnya: 1 layar berisi 37 chip datar (Sapaan Keluarga sendiri 25
   chip) -- terlalu banyak, susah discan. Sekarang dipecah bertingkat:
   Level 1 = 5 kategori (Kata Seru/Onomatope/Partikel Modal/Sapaan
   Keluarga/Sapaan Sosial) dengan total kata masing-masing.
   Level 2 = sub-grup di dalam kategori terpilih (mis. Onomatope -> 7
   sumber bunyi). Kalau kategori cuma 1 grup (Partikel Modal), skip
   langsung ke hasil kata -- tidak ada gunanya nampilin 1 tombol doang.
   Level 3 = KHUSUS Sapaan Keluarga (25 grup terlalu banyak utk 1 layar)
   -- dipecah dulu per Generasi (8 chip), baru di dalamnya sub Jenis+Pihak. */
const KHUSUS_KATEGORI = [
  { key: 'kata_seru',       label: '😮 Kata Seru' },
  { key: 'onomatope',       label: '🔊 Onomatope' },
  { key: 'partikel_modal',  label: '💭 Partikel Modal' },
  { key: 'sapaan_keluarga', label: '👪 Sapaan Keluarga' },
  { key: 'sapaan_sosial',   label: '🤝 Sapaan Sosial' },
];

function setGroupPanelTitle(text, backHandler) {
  const title = $('group-panel-title');
  title.innerHTML = '';
  if (!backHandler) {
    title.textContent = text;
    return;
  }
  const back = document.createElement('span');
  back.textContent = '← ' + text;
  back.style.cursor = 'pointer';
  back.style.color = 'var(--gold-dim)';
  back.addEventListener('click', backHandler);
  title.appendChild(back);
}

function khususEntriesFor(katKey) {
  if (!STATE.dataKhusus) return [];
  return Object.entries(STATE.dataKhusus).filter(([k]) => k.startsWith(katKey));
}

function renderKhususLevel1() {
  const grid = $('group-panel-grid');
  setGroupPanelTitle('Pilih Kelompok Khusus');
  grid.innerHTML = '';

  if (!STATE.dataKhusus) {
    grid.innerHTML = '<span style="color:var(--text-muted);font-size:0.8rem">Data kelompok khusus belum dimuat, tunggu sebentar lalu coba lagi.</span>';
    return;
  }

  KHUSUS_KATEGORI.forEach(kat => {
    const entries = khususEntriesFor(kat.key);
    const total = entries.reduce((s, [, v]) => s + (v.count || 0), 0);
    const chip = document.createElement('div');
    chip.className = 'group-chip';
    chip.innerHTML = `<span>${kat.label}</span><span class="gc-count">${total}</span>`;
    chip.addEventListener('click', () => renderKhususLevel2(kat.key, kat.label));
    grid.appendChild(chip);
  });
}

function renderKhususLevel2(katKey, katLabel) {
  const grid = $('group-panel-grid');
  const entries = khususEntriesFor(katKey);

  // Kategori dgn cuma 1 grup (mis. Partikel Modal) -- tidak ada gunanya
  // nampilin 1 tombol doang, langsung tampilkan hasil katanya.
  if (entries.length <= 1) {
    if (entries.length === 1) selectGroupItem('khusus', entries[0][0]);
    return;
  }

  setGroupPanelTitle(katLabel, renderKhususLevel1);
  grid.innerHTML = '';

  if (katKey === 'sapaan_keluarga') {
    // 25 grup terlalu banyak utk 1 layar -- pecah dulu per Generasi.
    // Urutan label_id sudah pasti "Sapaan Keluarga - <Generasi> - <Jenis> - <Pihak>"
    // (field diurut alfabetis saat index_kelompok_khusus.json dibangun: generasi < jenis < pihak).
    const byGenerasi = {};
    entries.forEach(([k, v]) => {
      const generasi = (v.label_id || '').split(' - ')[1] || 'Lainnya';
      (byGenerasi[generasi] = byGenerasi[generasi] || []).push([k, v]);
    });
    // Urutan generasi dari tertua ke termuda, bukan abjad -- lebih natural dibaca
    const GENERASI_ORDER = ['Canggah', 'Buyut', 'Kakek/Nenek', 'Orang Tua', 'Sendiri', 'Anak', 'Cucu', 'Cicit'];
    const sortedGenerasi = Object.keys(byGenerasi).sort(
      (a, b) => GENERASI_ORDER.indexOf(a) - GENERASI_ORDER.indexOf(b)
    );
    sortedGenerasi.forEach(generasi => {
      const items = byGenerasi[generasi];
      const total = items.reduce((s, [, v]) => s + (v.count || 0), 0);
      const chip = document.createElement('div');
      chip.className = 'group-chip';
      chip.innerHTML = `<span>${escHtml(generasi)}</span><span class="gc-count">${total}</span>`;
      chip.addEventListener('click', () => renderKhususLevel3(katKey, katLabel, generasi, items));
      grid.appendChild(chip);
    });
    return;
  }

  entries.sort((a, b) => b[1].count - a[1].count).forEach(([key, val]) => {
    // Buang prefix nama kategori dari label (sudah ada di breadcrumb atas)
    const subLabel = (val.label_id || '').split(' - ').slice(1).join(' - ') || key;
    const chip = document.createElement('div');
    chip.className = 'group-chip';
    chip.innerHTML = `<span>${escHtml(subLabel)}</span><span class="gc-count">${val.count || 0}</span>`;
    chip.addEventListener('click', () => selectGroupItem('khusus', key));
    grid.appendChild(chip);
  });
}

function renderKhususLevel3(katKey, katLabel, generasi, items) {
  const grid = $('group-panel-grid');
  setGroupPanelTitle(generasi, () => renderKhususLevel2(katKey, katLabel));
  grid.innerHTML = '';

  items.sort((a, b) => b[1].count - a[1].count).forEach(([key, val]) => {
    // Buang "Sapaan Keluarga - <Generasi> - " dari label, sisakan Jenis+Pihak
    const subLabel = (val.label_id || '').split(' - ').slice(2).join(' - ') || key;
    const chip = document.createElement('div');
    chip.className = 'group-chip';
    chip.innerHTML = `<span>${escHtml(subLabel)}</span><span class="gc-count">${val.count || 0}</span>`;
    chip.addEventListener('click', () => selectGroupItem('khusus', key));
    grid.appendChild(chip);
  });
}

/* ── GRUP PINYIN 2-LEVEL: huruf awal → turunan suku kata ──────
   Sebelumnya: klik "B" langsung tampilkan SEMUA kata berawalan B (ratusan
   hasil, tidak terpilah). Sekarang: klik "B" dulu tampilkan turunan suku
   kata yang BENAR-BENAR ada datanya (ba/bi/bo/bu/bai/ban/... — bukan daftar
   statis 400+ kombinasi teoretis pinyin, biar tidak ada tombol kosong).
   Pakai normalizePinyin() (sudah ada di shared/pinyin.js) supaya nada
   diakritik (nǐ, bā, dst) tidak bikin startsWith() gagal cocok. */
function renderPinyinLetterGrid() {
  const grid  = $('group-panel-grid');
  const title = $('group-panel-title');
  title.textContent = 'Pilih Inisial Pinyin';
  grid.innerHTML = '';
  'abcdefghijklmnopqrstuvwxyz'.split('').forEach(l => {
    const chip = document.createElement('div');
    chip.className = 'group-chip';
    chip.innerHTML = `<span>${l.toUpperCase()}</span>`;
    chip.addEventListener('click', () => renderPinyinSubGrid(l));
    grid.appendChild(chip);
  });
}

function getPinyinSubgroups(letter) {
  const data = STATE.dataHsk || [];
  const counts = {};
  data.forEach(w => {
    const firstSyl = (w.pinyin || '').toLowerCase().split(/\s+/)[0] || '';
    const norm = normalizePinyin(firstSyl).replace(/[^a-z]/g, '');
    if (!norm.startsWith(letter)) return;
    // zh/ch/sh butuh 3 huruf biar terpilah berarti (zha/zhe/zhi/zhong dst),
    // konsonan lain cukup 2 huruf (ba/be/bi/bo/bu). Suku kata vokal murni
    // (a/ai/an/e/er/o/ou dst) otomatis ikut aturan 2 huruf yang sama.
    const prefixLen = /^(zh|ch|sh)/.test(norm) ? 3 : 2;
    const prefix = norm.slice(0, Math.min(prefixLen, norm.length));
    counts[prefix] = (counts[prefix] || 0) + 1;
  });
  return counts;
}

function renderPinyinSubGrid(letter) {
  const grid  = $('group-panel-grid');
  const title = $('group-panel-title');
  title.textContent = 'Pinyin ' + letter.toUpperCase() + '…';
  grid.innerHTML = '';

  const back = document.createElement('div');
  back.className = 'group-chip';
  back.innerHTML = '<span>‹ Kembali</span>';
  back.addEventListener('click', renderPinyinLetterGrid);
  grid.appendChild(back);

  const counts = getPinyinSubgroups(letter);
  Object.entries(counts)
    .sort((a, b) => b[1] - a[1])
    .forEach(([prefix, count]) => {
      const chip = document.createElement('div');
      chip.className = 'group-chip';
      chip.innerHTML = `<span>${escHtml(prefix)}</span><span class="gc-count">${count}</span>`;
      chip.addEventListener('click', () => selectGroupItem('pinyin', prefix));
      grid.appendChild(chip);
    });
}

/* ── EXPLORER KOMPONEN/RADIKAL (ide baru: data etimologi 100% lengkap) ──
   Beda dengan searchExample(): itu cari KATA yang literally mengandung
   karakter tsb. Ini cari KARAKTER LAIN yang berbagi radikal/komponen yang
   sama (field `radical`/`components` di entri 1-karakter app_words.json),
   dilengkapi gloss + asal-usul dari char_etymology_id.json -- memperkuat
   pattern recognition rasa "oh, karakter-karakter ini satu keluarga". */
function getCharsByComponent(comp) {
  if (!STATE.dataHsk) return [];
  STATE._componentIndex = STATE._componentIndex || {};
  if (STATE._componentIndex[comp]) return STATE._componentIndex[comp];

  const seen = new Set();
  const results = [];
  STATE.dataHsk.forEach(w => {
    const s = w.simplified || w.id || '';
    if (s.length !== 1 || s === comp) return; // hanya karakter tunggal, exclude diri sendiri
    const isMatch = w.radical === comp || (w.components || []).includes(comp);
    if (!isMatch || seen.has(s)) return;
    seen.add(s);
    results.push({
      char:    s,
      meaning: getCharMeaning(s) || '',
    });
  });
  results.sort((a, b) => a.char.localeCompare(b.char, 'zh'));
  STATE._componentIndex[comp] = results;
  return results;
}

function openComponentExplorer(comp) {
  const panel = $('group-panel');
  const grid  = $('group-panel-grid');
  const title = $('group-panel-title');

  const chars = getCharsByComponent(comp);
  title.textContent = `Karakter dengan Komponen: ${comp} (${chars.length})`;
  grid.innerHTML = '';

  if (!chars.length) {
    grid.innerHTML = '<span style="color:var(--text-muted);font-size:0.8rem">Tidak ditemukan karakter lain dengan komponen ini di data.</span>';
  } else {
    chars.forEach(c => {
      const chip = document.createElement('div');
      chip.className = 'component-chip';
      chip.title     = 'Klik untuk lihat detail karakter ini';
      chip.innerHTML =
        `<span class="comp-hanzi">${escHtml(c.char)}</span>
         <span class="comp-info">${escHtml(c.meaning || '—')}</span>`;
      chip.addEventListener('click', () => {
        closeGroupPanel();
        selectWord(c.char, 0); // langsung ke detail karakter itu, tanpa perlu search dulu
      });
      grid.appendChild(chip);
    });
  }

  panel.classList.remove('hidden');
  panel.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

/* ── EKSPOR HASIL (salin/print) ───────────────────────────────
   Satu tombol, berlaku untuk APA PUN yang sedang ditampilkan di
   #results-list -- pencarian bebas, grup per radikal/goresan/tema/
   pinyin/struktur, atau koleksi bookmark/riwayat. Sengaja ambil dari
   STATE.results (SELURUH hasil), bukan cuma kartu yang sudah dirender
   lewat infinite scroll, supaya tema besar (ratusan kata) tetap
   terekspor lengkap. Urutannya ikut apa yang رسلان lihat di layar
   (mode kartu ikut cardSort, mode tabel ikut tableSort). */
function getExportRows() {
  let items;
  if (STATE.viewMode === 'table' && STATE.tableSortKey) {
    const key = STATE.tableSortKey;
    const dir = STATE.tableSortDir;
    items = STATE.results.slice().sort((a, b) => {
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
  } else if (typeof getCardSortedResults === 'function') {
    items = getCardSortedResults();
  } else {
    items = STATE.results;
  }

  return items.map(w => {
    const id = w.id || w.simplified || '';
    const meaning = Array.isArray(w.meanings_id) ? (w.meanings_id[0] || '') : (w.meanings_id || '');
    return { hanzi: w.simplified || id, pinyin: w.pinyin || '', arti: meaning || '' };
  });
}

function openExportPanel() {
  const rows = getExportRows();
  if (!rows.length) {
    showToast('Tidak ada hasil untuk diekspor -- lakukan pencarian atau pilih grup dulu.');
    return;
  }

  const header = 'Hanzi\tPinyin\tArti';
  const body   = rows.map(r => `${r.hanzi}\t${r.pinyin}\t${r.arti}`).join('\n');

  const ta = $('export-textarea');
  ta.value = header + '\n' + body;
  $('export-count').textContent = rows.length.toLocaleString('id') + ' kata';
  $('export-panel').classList.remove('hidden');

  // Langsung pilih semua teks -- kalau رسلان mau Ctrl+C manual juga bisa,
  // tidak wajib pakai tombol "Salin ke Clipboard".
  setTimeout(() => { ta.focus(); ta.select(); }, 50);
}

function closeExportPanel() {
  $('export-panel').classList.add('hidden');
}

async function copyExportToClipboard() {
  const ta = $('export-textarea');
  try {
    await navigator.clipboard.writeText(ta.value);
    showToast('✓ Disalin ke clipboard -- tinggal Paste (Ctrl+V) di Word/Excel/dll', 'success');
  } catch (e) {
    // Fallback kalau Clipboard API ditolak browser (jarang, tapi jaga-jaga)
    ta.focus();
    ta.select();
    try {
      document.execCommand('copy');
      showToast('✓ Disalin ke clipboard', 'success');
    } catch (e2) {
      showToast('⚠ Gagal menyalin otomatis -- blok teks di kotak lalu Ctrl+C manual', 'error');
    }
  }
}

function printExportResults() {
  const rows = getExportRows();
  if (!rows.length) return;

  const sourceEl = $('results-source');
  const title = (sourceEl && sourceEl.textContent) ? sourceEl.textContent : 'Daftar Kata';

  const rowsHtml = rows.map((r, i) =>
    `<tr><td>${i + 1}</td><td class="ph">${escHtml(r.hanzi)}</td><td>${escHtml(r.pinyin)}</td><td>${escHtml(r.arti)}</td></tr>`
  ).join('');

  const win = window.open('', '_blank');
  if (!win) {
    showToast('⚠ Browser memblokir jendela cetak -- izinkan pop-up untuk halaman ini, lalu coba lagi.', 'error');
    return;
  }
  win.document.write(`<!DOCTYPE html><html><head><meta charset="utf-8">
<title>${escHtml(title)} — Mandarin Interaktif</title>
<style>
  body{font-family:Georgia,'Noto Serif',serif;padding:24px;color:#111}
  h1{font-size:1.2rem;margin-bottom:4px}
  .meta{color:#666;font-size:0.85rem;margin-bottom:16px}
  table{border-collapse:collapse;width:100%}
  th,td{border:1px solid #ccc;padding:6px 10px;text-align:left;font-size:0.92rem;vertical-align:top}
  th{background:#eee}
  .ph{font-size:1.15rem}
  @media print { body{padding:0} }
</style></head><body>
<h1>${escHtml(title)}</h1>
<div class="meta">Mandarin Interaktif — ${rows.length} kata — dicetak ${new Date().toLocaleDateString('id-ID')}</div>
<table><thead><tr><th>#</th><th>Hanzi</th><th>Pinyin</th><th>Arti</th></tr></thead>
<tbody>${rowsHtml}</tbody></table>
<script>window.onload = function(){ window.print(); };</script>
</body></html>`);
  win.document.close();
}

/* ── SEARCH EXAMPLE (chips landing) ───────────────────────── */
function searchExample(term) {
  const input = $('search-input');
  input.value = term;
  $('search-clear').classList.add('visible');
  doSearch(term);
  input.focus();
}

/* ── CLEAR SEARCH ──────────────────────────────────────────── */
function clearSearch() {
  $('search-input').value = '';
  $('search-clear').classList.remove('visible');
  $('search-mode-badge').classList.remove('visible');
  clearResults();
  showLanding(true);
  $('search-input').focus();
}

/* showToast() sekarang dari shared/core.js */


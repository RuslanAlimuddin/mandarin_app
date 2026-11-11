/* kamus-komponen-posisi.js -- menu KELOMPOK "Per Komponen" dan "Per Radikal" versi baru.
   FILE TAMBAHAN: tidak mengubah file Kamus lain. Dimuat SEBELUM kamus-init.js.
   Data: data/index_komponen_posisi.json (karakter per komponen/radikal per posisi).
   Kata diambil dari index lama (STATE.dataPhonetic / STATE.dataRadical).
   Filter: Semua | Karakter | Kata, lalu posisi (Kiri/Kanan/Atas/Bawah/Luar/Dalam).
   Posisi hanya berlaku untuk karakter tunggal. Karakter di luar HSK memakai Cidict. */
(function () {
  var IDX = null, keep = false, S = { t: 'phonetic', k: '', tipe: 'semua', pos: 'semua' };
  var POS = ['kiri', 'kanan', 'atas', 'bawah', 'luar', 'dalam'];
  var hskMap = null, idMap = null, cidMap = null;

  function loadIdx() {
    if (IDX) return Promise.resolve(IDX);
    return fetch('data/index_komponen_posisi.json').then(function (r) {
      if (!r.ok) throw new Error('HTTP ' + r.status);
      return r.json();
    }).then(function (j) { IDX = j; return j; });
  }

  function buildMaps() {
    if (!hskMap) {
      hskMap = new Map(); idMap = new Map();
      (STATE.dataHsk || []).forEach(function (w) {
        var s = w.simplified || w.id || '';
        idMap.set(w.id || s, w);
        if (s.length === 1 && !hskMap.has(s)) hskMap.set(s, w);
      });
    }
    if (STATE.dataCidict && !cidMap) {
      cidMap = new Map();
      STATE.dataCidict.forEach(function (w) {
        if (w.simplified && w.simplified.length === 1 && !cidMap.has(w.simplified)) cidMap.set(w.simplified, w);
      });
    }
  }

  function total(e) {
    var seen = {};
    POS.forEach(function (p) { (e.posisi[p] || []).forEach(function (c) { seen[c] = 1; }); });
    (e.lg || []).forEach(function (c) { seen[c] = 1; });
    return Object.keys(seen).length;
  }

  var legDone = {};
  function ensureLegacy(type) {
    if (legDone[type] || !IDX) return;
    var src = type === 'phonetic' ? IDX.komponen : IDX.radikal;
    var w = type === 'phonetic' ? STATE.dataPhonetic : STATE.dataRadical;
    if (!w) return;
    legDone[type] = 1;
    Object.keys(w).forEach(function (k) {
      if (src[k]) return;
      src[k] = { kecil: 0, leg: 1, posisi: {}, label: '', lg: w[k].filter(function (i) { return String(i).length === 1; }) };
    });
  }

  /* ── daftar komponen / radikal di panel ── */
  function openKP(type) {
    STATE.groupType = type;
    var panel = $('group-panel'), grid = $('group-panel-grid');
    $('group-panel-title').textContent = type === 'phonetic' ? 'Pilih Komponen' : 'Pilih Radikal';
    grid.innerHTML = '<span style="color:var(--text-muted);font-size:0.8rem">Memuat…</span>';
    panel.classList.remove('hidden');
    loadIdx().then(function () {
      ensureLegacy(type);
      var src = type === 'phonetic' ? IDX.komponen : IDX.radikal;
      var list = Object.keys(src).map(function (k) { return { k: k, e: src[k], n: total(src[k]) }; })
        .sort(function (a, b) { return b.n - a.n; });
      grid.innerHTML = '';
      function head(txt) {
        var h = document.createElement('div');
        h.textContent = txt;
        h.style.cssText = 'width:100%;flex-basis:100%;grid-column:1/-1;color:var(--text-muted);font-size:.78rem;margin:8px 0 2px';
        grid.appendChild(h);
      }
      function chips(arr) {
        arr.forEach(function (x) {
          var c = document.createElement('div');
          c.className = 'group-chip';
          c.title = x.e.label ? 'Umumnya penanda ' + x.e.label : '';
          c.innerHTML = '<span style="font-size:1.05rem">' + escHtml(x.k) + '</span><span class="gc-count">' + x.n + '</span>';
          c.addEventListener('click', function () { pick(type, x.k); });
          grid.appendChild(c);
        });
      }
      var big = list.filter(function (x) { return !x.e.kecil && !x.e.leg; });
      var leg = list.filter(function (x) { return x.e.leg; });
      var small = list.filter(function (x) { return x.e.kecil; });
      head(type === 'phonetic' ? 'Komponen' : 'Radikal');
      chips(big);
      if (small.length) { head('Komponen Kecil (kurang dari 3 goresan)'); chips(small); }
      if (leg.length) { head('Lainnya (data posisi belum tersedia)'); chips(leg); }
    }).catch(function (err) {
      grid.innerHTML = '<span style="color:var(--text-muted);font-size:0.8rem">Gagal memuat data/index_komponen_posisi.json: ' + escHtml(err.message) + '</span>';
    });
  }

  function pick(type, key) {
    S = { t: type, k: key, tipe: 'semua', pos: 'semua' };
    closeGroupPanel();
    render();
  }

  /* ── tampilkan hasil + bar filter ── */
  async function render() {
    var src = S.t === 'phonetic' ? IDX.komponen : IDX.radikal;
    var e = src[S.k];
    if (!e) return;
    if (!STATE.dataCidict) {
      showToast('Memuat data tambahan untuk karakter yang jarang dipakai…');
      await loadCidict();
    }
    buildMaps();
    var chars = [];
    POS.forEach(function (p) {
      if (S.pos === 'semua' || S.pos === p) (e.posisi[p] || []).forEach(function (c) { if (chars.indexOf(c) < 0) chars.push(c); });
    });
    if (S.pos === 'semua') (e.lg || []).forEach(function (c) { if (chars.indexOf(c) < 0) chars.push(c); });
    var inHsk = [], other = [];
    chars.forEach(function (c) {
      var h = hskMap.get(c);
      if (h) { inHsk.push(h); return; }
      var d = cidMap && cidMap.get(c);
      if (d) { d._cidictFallback = true; other.push(d); }
    });
    var out = [];
    if (S.tipe !== 'kata') out = inHsk.concat(other);
    var wIdx = S.t === 'phonetic' ? STATE.dataPhonetic : STATE.dataRadical;
    var words = ((wIdx && wIdx[S.k]) || []).filter(function (id) { return String(id).length > 1; })
      .map(function (id) { return idMap.get(id); }).filter(Boolean);
    if (S.tipe !== 'kar' && S.pos === 'semua') out = out.concat(words);
    var label = (S.t === 'phonetic' ? 'Komponen: ' : 'Radikal: ') + S.k +
      (e.label ? ' · umumnya penanda ' + e.label : '') + (S.pos !== 'semua' ? ' · ' + S.k + ' di ' + S.pos : '');
    keep = true;
    renderGroupResultsFromWords(out, label);
    drawBar(e, words.length);
  }

  function drawBar(e, nWords) {
    var bar = $('kp-bar');
    if (!bar) {
      bar = document.createElement('div');
      bar.id = 'kp-bar';
      bar.style.cssText = 'display:flex;flex-wrap:wrap;gap:6px;align-items:center;padding:6px 14px';
      $('results-header').insertAdjacentElement('afterend', bar);
    }
    bar.style.display = 'flex';
    bar.innerHTML = '';
    function btn(txt, on, fn) {
      var b = document.createElement('button');
      b.className = 'card-sort-btn' + (on ? ' active' : '');
      b.textContent = txt;
      b.onclick = fn;
      bar.appendChild(b);
    }
    btn('Semua', S.tipe === 'semua', function () { S.tipe = 'semua'; render(); });
    btn('Karakter (' + total(e) + ')', S.tipe === 'kar', function () { S.tipe = 'kar'; render(); });
    btn('Kata (' + nWords + ')', S.tipe === 'kata', function () { S.tipe = 'kata'; S.pos = 'semua'; render(); });
    if (S.tipe !== 'kata') {
      var sp = document.createElement('span');
      sp.textContent = 'Posisi ' + S.k + ':';
      sp.style.cssText = 'color:var(--text-muted);font-size:.78rem;margin-left:10px';
      bar.appendChild(sp);
      btn('Semua', S.pos === 'semua', function () { S.pos = 'semua'; render(); });
      POS.forEach(function (p) {
        var n = (e.posisi[p] || []).length;
        if (n) btn(p.charAt(0).toUpperCase() + p.slice(1) + ' (' + n + ')', S.pos === p, function () {
          S.pos = p;
          if (S.tipe === 'kata') S.tipe = 'kar';
          render();
        });
      });
    }
  }

  function hideBar() { var b = $('kp-bar'); if (b) b.style.display = 'none'; }

  /* ── menu Kelompok > Karakter Mirip: baca pasangan baru (per karakter) ── */
  var MP = null, M = { c: '', tier: 'semua', agreed: false };
  function loadMP() {
    if (MP) return Promise.resolve(MP);
    function J(u, fb) { return fetch(u).then(function (r) { return r.json(); }).catch(function () { return fb; }); }
    return Promise.all([J('data/confusion_groups.json', { groups: [] }), J('data/karakter_mirip_pasangan.json', { pasangan: {} })]).then(function (r) {
      MP = {};
      (r[0].groups || []).forEach(function (g) {
        var all = [g.character].concat(g.confusable_with || []);
        all.forEach(function (c) { all.forEach(function (o) { if (o !== c) (MP[c] = MP[c] || []).push([o, 'T1', '', 'l']); }); });
      });
      var P = r[1].pasangan || {};
      Object.keys(P).forEach(function (c) {
        MP[c] = MP[c] || [];
        P[c].forEach(function (p) { if (!MP[c].some(function (x) { return x[0] === p[0]; })) MP[c].push(p); });
      });
      return MP;
    });
  }
  function openMirip() {
    STATE.groupType = 'mirip';
    var grid = $('group-panel-grid');
    $('group-panel-title').textContent = 'Pilih Karakter (menampilkan karakter-karakter yang mirip dengannya)';
    grid.innerHTML = '<span style="color:var(--text-muted);font-size:0.8rem">Memuat…</span>';
    $('group-panel').classList.remove('hidden');
    loadMP().then(function () {
      grid.innerHTML = '';
      Object.keys(MP).sort(function (a, b) { return MP[b].length - MP[a].length; }).forEach(function (c) {
        var ch = document.createElement('div');
        ch.className = 'group-chip';
        ch.innerHTML = '<span style="font-size:1.05rem">' + escHtml(c) + '</span><span class="gc-count">' + MP[c].length + '</span>';
        ch.addEventListener('click', function () { M = { c: c, tier: 'semua', agreed: false }; closeGroupPanel(); renderMirip(); });
        grid.appendChild(ch);
      });
    });
  }
  async function renderMirip() {
    var all = MP[M.c] || [];
    var list = all.filter(function (p) { return (M.tier === 'semua' || p[1] === M.tier) && (!M.agreed || p[3] === 's' || p[3] === 'l'); });
    if (!STATE.dataCidict) { showToast('Memuat data tambahan untuk karakter yang jarang dipakai…'); await loadCidict(); }
    buildMaps();
    var out = [];
    [M.c].concat(list.map(function (p) { return p[0]; })).forEach(function (c) {
      var h = hskMap.get(c) || (cidMap && cidMap.get(c));
      if (h) { if (!hskMap.get(c)) h._cidictFallback = true; out.push(h); }
    });
    keep = true;
    renderGroupResultsFromWords(out, 'Karakter Mirip: ' + M.c + ' (' + list.length + ' pasangan)');
    var bar = $('kp-bar');
    if (!bar) { drawBar({ posisi: {} }, 0); bar = $('kp-bar'); }
    bar.style.display = 'flex'; bar.innerHTML = '';
    function btn(t, on, fn) { var b = document.createElement('button'); b.className = 'card-sort-btn' + (on ? ' active' : ''); b.textContent = t; b.onclick = fn; bar.appendChild(b); }
    btn('Semua tingkat (' + all.length + ')', M.tier === 'semua', function () { M.tier = 'semua'; renderMirip(); });
    ['T1', 'T2', 'T3'].forEach(function (t) {
      var n = all.filter(function (p) { return p[1] === t; }).length;
      if (n) btn(t + ' (' + n + ')', M.tier === t, function () { M.tier = t; renderMirip(); });
    });
    btn(M.agreed ? 'Tampilkan semua asal' : 'Hanya yang disepakati', M.agreed, function () { M.agreed = !M.agreed; renderMirip(); });
  }

  /* ── badge jumlah di sidebar ── */
  function setBadge(filter, n) {
    var it = document.querySelector('[data-filter="' + filter + '"]');
    if (!it) return;
    var b = it.querySelector('.item-count');
    if (!b) { b = document.createElement('span'); b.className = 'item-count'; it.appendChild(b); }
    b.textContent = n.toLocaleString('id');
  }
  function badges(tries) {
    if (!IDX || !STATE.dataPhonetic || !STATE.dataRadical) { if (tries < 40) setTimeout(function () { badges(tries + 1); }, 500); return; }
    ensureLegacy('phonetic'); ensureLegacy('radical');
    setBadge('group-phonetic', Object.keys(IDX.komponen).length);
    setBadge('group-radical', Object.keys(IDX.radikal).length);
    loadMP().then(function () { setBadge('group-mirip', Object.keys(MP).length); });
  }

  /* ── pasang ke fungsi Kamus yang sudah ada (dibungkus, bukan diganti) ── */
  var origRender = window.renderGroupResultsFromWords;
  window.renderGroupResultsFromWords = function (w, l) {
    if (!keep) hideBar();
    keep = false;
    return origRender(w, l);
  };
  var origOpen = window.openGroupPanel;
  window.openGroupPanel = function (type) {
    if (type === 'phonetic' || type === 'radical') { openKP(type); return; }
    if (type === 'mirip') { openMirip(); return; }
    origOpen(type);
  };
  var origSearch = window.doSearch;
  window.doSearch = function (q) { hideBar(); return origSearch(q); };

  document.addEventListener('DOMContentLoaded', function () {
    var s = document.querySelector('[data-filter="group-phonetic"] span');
    if (s) s.textContent = 'Per Komponen';
    loadIdx().then(function () { badges(0); }).catch(function () {});
  });
})();

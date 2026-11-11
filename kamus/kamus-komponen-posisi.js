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
    return Object.keys(seen).length;
  }

  /* ── daftar komponen / radikal di panel ── */
  function openKP(type) {
    STATE.groupType = type;
    var panel = $('group-panel'), grid = $('group-panel-grid');
    $('group-panel-title').textContent = type === 'phonetic' ? 'Pilih Komponen' : 'Pilih Radikal';
    grid.innerHTML = '<span style="color:var(--text-muted);font-size:0.8rem">Memuat…</span>';
    panel.classList.remove('hidden');
    loadIdx().then(function () {
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
      var big = list.filter(function (x) { return !x.e.kecil; });
      var small = list.filter(function (x) { return x.e.kecil; });
      head(type === 'phonetic' ? 'Komponen' : 'Radikal');
      chips(big);
      if (small.length) { head('Komponen Kecil (kurang dari 3 goresan)'); chips(small); }
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
    origOpen(type);
  };
  var origSearch = window.doSearch;
  window.doSearch = function (q) { hideBar(); return origSearch(q); };

  document.addEventListener('DOMContentLoaded', function () {
    var s = document.querySelector('[data-filter="group-phonetic"] span');
    if (s) s.textContent = 'Per Komponen';
  });
})();

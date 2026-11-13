/* kamus-afiks.js -- menu KELOMPOK "Awalan & Akhiran" (60 entri, kelompok A-J).
   FILE TAMBAHAN: tidak mengubah file Kamus lain. Dimuat SETELAH kamus-komponen-posisi.js
   dan SEBELUM kamus-init.js (cara yang sama dengan fitur Komponen & Posisi).
   Data: data/afiks_kamus.json (disusun GPT, diperiksa Claude). Kata contoh diambil dari
   STATE.dataHsk. Hasil klik satu tombol = kartu keterangan di atas daftar kata contoh.
   Tautan langsung: kamus.html#opengroup=afiks  dan  kamus.html#group=afiks:者 */
(function () {
  'use strict';
  var DATA = null, MAP = null, keep = false, shown = '';
  var HSKIDX = null, HSKSRC = null;
  var KEL = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J'];

  /* poin lama di Tata Bahasa untuk karakter yang pernah dibahas di sana */
  var LAMA = {
    '第': { t: 'HSK 1 · poin 56 (小— 第—)', q: 'Awalan 小— dan 第—' },
    '们': { t: 'HSK 1 · poin 57 (—们 —边)', q: 'Akhiran —们 dan —边' },
    '子': { t: 'HSK 3 · poin 16.3 (—子)', q: 'Akhiran —子 (pembentuk kata benda)' }
  };

  (function () {
    var st = document.createElement('style');
    st.textContent =
      '#afx-card{margin:6px 14px;padding:12px 14px;background:var(--bg-card2);border:1px solid var(--border);' +
        'border-left:3px solid var(--gold);border-radius:var(--radius);font-size:.86rem;line-height:1.5}' +
      '#afx-card .afx-top{display:flex;flex-wrap:wrap;align-items:baseline;gap:6px 12px}' +
      '#afx-card .afx-big{font-size:1.9rem;color:var(--gold);line-height:1}' +
      '#afx-card .afx-py{color:var(--text-dim)}' +
      '#afx-card .afx-tag{font-size:.72rem;padding:2px 7px;border-radius:4px;background:var(--gold-bg);color:var(--gold)}' +
      '#afx-card .afx-grp{color:var(--text-muted);font-size:.78rem}' +
      '#afx-card .afx-arti{margin-top:6px;font-weight:600}' +
      '#afx-card .afx-fungsi{margin-top:4px;color:var(--text-dim)}' +
      '#afx-card .afx-note{margin-top:8px;padding:6px 8px;background:var(--gold-bg);border-radius:4px;color:var(--text-dim)}' +
      '#afx-card .afx-row{margin-top:8px;font-size:.8rem;color:var(--text-dim)}' +
      '#afx-card .afx-row a{color:var(--gold)}' +
      '#afx-card .afx-bk-box{margin-top:10px;border-top:1px dashed var(--border);padding-top:8px}' +
      '#afx-card .afx-bk-title{color:var(--text-muted);font-size:.76rem;margin-bottom:4px}' +
      '#afx-card .afx-bk-item{margin:3px 0;color:var(--text-dim)}' +
      '#afx-card .afx-bk{color:var(--gold);cursor:pointer;font-size:1rem;margin-right:6px;text-decoration:underline dotted}';
    document.head.appendChild(st);
  })();

  function dash(e) { return e.posisi === 'awalan' ? e.karakter + '—' : '—' + e.karakter; }
  function tag(e) { return e.posisi === 'awalan' ? 'Awalan' : 'Akhiran'; }
  function nContoh(e) {
    var n = 0;
    (e.bagian || []).forEach(function (b) { n += (b.contoh || []).length; });
    return n;
  }

  function loadData() {
    if (DATA) return Promise.resolve(DATA);
    return fetch('data/afiks_kamus.json').then(function (r) {
      if (!r.ok) throw new Error('HTTP ' + r.status);
      return r.json();
    }).then(function (j) {
      if (!Array.isArray(j)) throw new Error('format data tidak dikenal');
      DATA = j; MAP = {};
      j.forEach(function (e) { MAP[e.karakter] = e; });
      return j;
    });
  }

  /* kata contoh dicari lewat tulisan sederhananya di data kamus utama */
  function hskIndex() {
    if (HSKIDX && HSKSRC === STATE.dataHsk) return HSKIDX;
    HSKIDX = {}; HSKSRC = STATE.dataHsk;
    (STATE.dataHsk || []).forEach(function (w) {
      var s = w.simplified || w.id;
      if (s && !(s in HSKIDX)) HSKIDX[s] = w;
    });
    return HSKIDX;
  }

  /* ── kotak pilihan: 60 tombol di bawah 10 judul kelompok ── */
  function openAfiks() {
    STATE.groupType = 'afiks';
    var panel = $('group-panel'), grid = $('group-panel-grid');
    $('group-panel-title').textContent = 'Pilih Awalan / Akhiran';
    grid.innerHTML = '<span style="color:var(--text-muted);font-size:0.8rem">Memuat…</span>';
    panel.classList.remove('hidden');
    loadData().then(function () {
      grid.innerHTML = '';
      KEL.forEach(function (k) {
        var list = DATA.filter(function (e) { return e.kelompok === k; });
        if (!list.length) return;
        var h = document.createElement('div');
        h.textContent = k + ' · ' + list[0].kelompok_nama + ' (' + list.length + ')';
        h.style.cssText = 'width:100%;flex-basis:100%;grid-column:1/-1;color:var(--text-muted);font-size:.78rem;margin:8px 0 2px';
        grid.appendChild(h);
        list.forEach(function (e) {
          var c = document.createElement('div');
          c.className = 'group-chip';
          c.title = tag(e) + ' · ' + e.arti_dasar;
          c.innerHTML = '<span style="font-size:1.05rem">' + escHtml(dash(e)) + '</span>' +
                        '<span class="gc-count">' + nContoh(e) + '</span>';
          c.addEventListener('click', function () { pick(e.karakter); });
          grid.appendChild(c);
        });
      });
      var n = document.createElement('div');
      n.style.cssText = 'width:100%;flex-basis:100%;grid-column:1/-1;color:var(--text-muted);font-size:.76rem;margin-top:10px';
      n.innerHTML = '小— dan —边 tidak termasuk 60 entri ini; keduanya sudah dibahas di Tata Bahasa: ' +
        '<a style="color:var(--gold)" href="tatabahasa.html#search=' + encodeURIComponent('Awalan 小— dan 第—') + '">HSK 1 · poin 56</a> · ' +
        '<a style="color:var(--gold)" href="tatabahasa.html#search=' + encodeURIComponent('Akhiran —们 dan —边') + '">HSK 1 · poin 57</a>';
      grid.appendChild(n);
    }).catch(function (err) {
      grid.innerHTML = '<span style="color:var(--text-muted);font-size:0.8rem">Gagal memuat data/afiks_kamus.json: ' + escHtml(err.message) + '</span>';
    });
  }

  function pick(key) {
    closeGroupPanel();
    render(key);
  }

  /* ── hasil: daftar kata contoh + kartu keterangan di atasnya ── */
  function render(key) {
    var e = MAP && MAP[key];
    if (!e) return;
    if (!STATE.dataHsk) { showToast('Data kamus belum selesai dimuat. Coba lagi sebentar lagi.'); return; }
    var idx = hskIndex(), words = [];
    (e.bagian || []).forEach(function (b) {
      (b.contoh || []).forEach(function (c) {
        var w = idx[c.kata];
        if (w && words.indexOf(w) < 0) words.push(w);
      });
    });
    keep = true;
    window.renderGroupResultsFromWords(words, tag(e) + ' ' + dash(e) + ' · ' + e.kelompok_nama);
    keep = false;
    drawCard(e);
  }

  function hideCard() {
    var c = $('afx-card');
    if (c) c.style.display = 'none';
    shown = '';
  }

  function drawCard(e) {
    var card = $('afx-card');
    if (!card) {
      card = document.createElement('div');
      card.id = 'afx-card';
      $('results-header').insertAdjacentElement('afterend', card);
    }
    shown = e.karakter;
    var h = '<div class="afx-top"><span class="afx-big">' + escHtml(dash(e)) + '</span>' +
            '<span class="afx-py">' + escHtml(e.pinyin) + '</span>' +
            '<span class="afx-tag">' + tag(e) + '</span>' +
            '<span class="afx-grp">' + escHtml(e.kelompok + ' · ' + e.kelompok_nama + ' · ' + e.id) + '</span></div>';
    h += '<div class="afx-arti">' + escHtml(e.arti_dasar) + '</div>';
    var bag = e.bagian || [];
    bag.forEach(function (b) {
      var t = (bag.length > 1 ? '<b>Sebagai ' + escHtml(b.sebagai || '') + ':</b> ' : '') + escHtml(b.fungsi || '');
      if (bag.length > 1 && b.arti) t += ' <i>(' + escHtml(b.arti) + ')</i>';
      h += '<div class="afx-fungsi">' + t + '</div>';
    });
    if (e.catatan) h += '<div class="afx-note">💡 ' + escHtml(e.catatan) + '</div>';
    var lm = LAMA[e.karakter];
    if (lm) {
      h += '<div class="afx-row">Lihat juga di Tata Bahasa: <a href="tatabahasa.html#search=' +
           encodeURIComponent(lm.q) + '">' + escHtml(lm.t) + '</a></div>';
    }
    h += '<div class="afx-row" id="afx-links"></div>';
    var bk = e.bukan || [];
    if (bk.length) {
      h += '<div class="afx-bk-box"><div class="afx-bk-title">Mirip tetapi bukan (' + bk.length + ') · klik kata untuk mencarinya</div>';
      bk.forEach(function (b) {
        h += '<div class="afx-bk-item"><span class="afx-bk" data-k="' + escHtml(b.kata) + '">' + escHtml(b.kata) +
             '</span>' + escHtml(b.alasan || '') + '</div>';
      });
      h += '</div>';
    }
    card.innerHTML = h;
    card.style.display = '';
    Array.prototype.forEach.call(card.querySelectorAll('.afx-bk'), function (s) {
      s.addEventListener('click', function () { searchExample(s.getAttribute('data-k')); });
    });
    /* tombol ke Akar Kosakata: hanya untuk karakter yang ada di sana */
    var p = STATE.indexFilesPromise ? STATE.indexFilesPromise.catch(function () {}) : Promise.resolve();
    p.then(function () {
      if (shown !== e.karakter || !STATE.dataAkar || !STATE.dataAkar[e.karakter]) return;
      var box = $('afx-links');
      if (!box || box.querySelector('button')) return;
      var b = document.createElement('button');
      b.className = 'card-sort-btn';
      b.textContent = '🌱 Akar Kosakata: ' + e.karakter;
      b.title = 'Lihat kata-kata turunan dengan ' + e.karakter + ' di Akar Kosakata';
      b.onclick = function () { window.selectGroupItem('akar', e.karakter); };
      box.appendChild(b);
    });
  }

  /* ── angka di sidebar ── */
  function badge() {
    loadData().then(function (d) {
      var el = $('cnt-afiks');
      if (el) el.textContent = d.length.toLocaleString('id');
    }).catch(function () {});
  }

  /* ── pasang ke fungsi Kamus yang sudah ada (dibungkus, bukan diganti) ── */
  var origRender = window.renderGroupResultsFromWords;
  window.renderGroupResultsFromWords = function (w, l) {
    if (!keep) hideCard();
    keep = false;
    return origRender(w, l);
  };
  var origOpen = window.openGroupPanel;
  window.openGroupPanel = function (type) {
    if (type === 'afiks') { openAfiks(); return; }
    return origOpen.apply(this, arguments);
  };
  var origSel = window.selectGroupItem;
  window.selectGroupItem = function (type, key) {
    if (type === 'afiks') {
      return loadData().then(function () { closeGroupPanel(); render(key); })
        .catch(function (err) { showToast('Gagal memuat data Awalan & Akhiran: ' + err.message); });
    }
    return origSel.apply(this, arguments);
  };
  ['doSearch', 'setSidebarFilter', 'showCollection', 'clearResults'].forEach(function (name) {
    var o = window[name];
    if (typeof o !== 'function') return;
    window[name] = function () { hideCard(); return o.apply(this, arguments); };
  });
  var origLanding = window.showLanding;
  if (typeof origLanding === 'function') {
    window.showLanding = function (show) { if (show) hideCard(); return origLanding.apply(this, arguments); };
  }

  document.addEventListener('DOMContentLoaded', badge);
})();

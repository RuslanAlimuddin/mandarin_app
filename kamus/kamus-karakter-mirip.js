/* kamus-karakter-mirip.js (versi 2) -- Panel "Karakter Mirip (Bentuk Tulisan)"
   Membaca DUA sumber: data/confusion_groups.json (160 grup lama, dianggap T1)
   dan data/karakter_mirip_pasangan.json (pasangan baru per karakter, ada tingkat T1-T3
   dan asal keputusan). Satu karakter boleh punya banyak pasangan.
   Asal: s = disepakati GPT+Claude, c = hanya Claude, g = hanya GPT, l = grup lama. */
(function () {
  var idx = null, onlyAgreed = false, current = '';
  var TIER = { T1: 'sangat mirip', T2: 'mirip', T3: 'agak mirip' };
  var ASAL = { s: 'disepakati GPT dan Claude', c: 'hanya Claude', g: 'hanya GPT', l: 'grup lama' };

  function getJson(u, fb) {
    return fetch(u).then(function (r) { if (!r.ok) throw 0; return r.json(); }).catch(function () { return fb; });
  }

  function load() {
    return Promise.all([
      getJson('data/confusion_groups.json', { groups: [] }),
      getJson('data/karakter_mirip_pasangan.json', { pasangan: {} })
    ]).then(function (res) {
      idx = {};
      (res[0].groups || []).forEach(function (g) {
        var all = [g.character].concat(g.confusable_with || []);
        all.forEach(function (c) {
          all.forEach(function (o) {
            if (o !== c) (idx[c] = idx[c] || []).push([o, 'T1', g.note || '', 'l']);
          });
        });
      });
      var P = res[1].pasangan || {};
      Object.keys(P).forEach(function (c) {
        idx[c] = idx[c] || [];
        P[c].forEach(function (p) {
          if (!idx[c].some(function (x) { return x[0] === p[0]; })) idx[c].push(p);
        });
      });
    });
  }

  function mk(tag, cls, txt) {
    var e = document.createElement(tag);
    if (cls) e.className = cls;
    if (txt) e.textContent = txt;
    return e;
  }

  function render(hanzi) {
    current = hanzi;
    var sec = document.getElementById('d-section-mirip');
    var box = document.getElementById('d-mirip-chips');
    var noteEl = document.getElementById('d-mirip-note');
    if (!sec || !box || !idx) return;
    var list = (idx[hanzi] || []).filter(function (p) { return !onlyAgreed || p[3] === 's' || p[3] === 'l'; });
    var total = (idx[hanzi] || []).length;
    if (!total) { sec.classList.add('hidden'); return; }
    if (noteEl) noteEl.style.display = 'none';
    box.innerHTML = '';
    list.forEach(function (p) {
      var row = mk('div');
      row.style.cssText = 'display:flex;align-items:baseline;gap:8px;margin:4px 0;flex-wrap:wrap';
      var chip = mk('span', 'mirip-chip', p[0]);
      chip.title = 'Cari "' + p[0] + '" di Kamus';
      chip.onclick = function () { if (typeof searchExample === 'function') searchExample(p[0]); };
      var badge = mk('span', '', p[1] + ' · ' + (TIER[p[1]] || ''));
      badge.style.cssText = 'font-size:.72rem;color:var(--gold);border:1px solid var(--gold);border-radius:9px;padding:0 7px';
      badge.title = 'Asal keputusan: ' + (ASAL[p[3]] || '');
      row.appendChild(chip);
      row.appendChild(badge);
      if (p[2]) {
        var n = mk('span', '', p[2]);
        n.style.cssText = 'font-size:.78rem;color:var(--text-dim)';
        row.appendChild(n);
      }
      box.appendChild(row);
    });
    if (total > 0) {
      var tg = mk('button', '', onlyAgreed ? 'Tampilkan semua (' + total + ')' : 'Hanya yang disepakati');
      tg.style.cssText = 'margin-top:6px;font-size:.75rem;cursor:pointer';
      tg.onclick = function () { onlyAgreed = !onlyAgreed; render(current); };
      box.appendChild(tg);
    }
    sec.classList.remove('hidden');
  }

  function currentHanzi() {
    var d = document.getElementById('d-hanzi');
    return d ? d.textContent.trim() : '';
  }

  function init() {
    var t = document.getElementById('d-hanzi');
    if (!t) return;
    new MutationObserver(function () { var h = currentHanzi(); if (h) render(h); })
      .observe(t, { childList: true, characterData: true, subtree: true });
    var h = currentHanzi();
    if (h) render(h);
  }

  load().then(function () {
    if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
    else init();
  });
})();

/* ═══════════════════════════════════════════════════════════════
   kamus-nuance.js — Panel "Beda dengan Kata Mirip"
   ═══════════════════════════════════════════════════════════════
   Fitur near-synonym nuance pairs (mis. 尝 vs 吃): pasangan kata yang
   gramatikal sama-sama valid tapi beda nuansa (jumlah, tujuan, register).
   Beda dari field "synonyms" yang sudah ada di app_words.json -- ini
   khusus utk pasangan yang SERING TERTUKAR pembelajar, dengan
   penjelasan pembeda eksplisit.

   Berdiri sendiri: fetch data sendiri dari data/nuance_pairs.json,
   auto-detect kata yang lagi dibuka lewat MutationObserver di #d-hanzi.
   TIDAK mengubah kamus-detail.js -- supaya aman diintegrasikan tanpa
   perlu paham detail alur render yang sudah ada.

   Kalau kata aktif tidak ada di data/nuance_pairs.json, section
   otomatis disembunyikan (class "hidden") -- sama seperti pola
   section mnemonic "Bantu Ingat".
═══════════════════════════════════════════════════════════════ */

(function () {
  let nuanceIndex = null; // Map: hanzi -> [pair, ...]

  async function loadNuanceData() {
    try {
      const res = await fetch('data/nuance_pairs.json');
      if (!res.ok) throw new Error('HTTP ' + res.status);
      const data = await res.json();
      nuanceIndex = {};
      (data.pairs || []).forEach(function (pair) {
        (pair.words || []).forEach(function (w) {
          if (!nuanceIndex[w]) nuanceIndex[w] = [];
          nuanceIndex[w].push(pair);
        });
      });
    } catch (e) {
      console.warn('[kamus-nuance] gagal load data/nuance_pairs.json:', e);
      nuanceIndex = {};
    }
  }

  function el(tag, cls, text) {
    const e = document.createElement(tag);
    if (cls) e.className = cls;
    if (text !== undefined) e.textContent = text;
    return e;
  }

  function renderNuancePanel(hanzi) {
    const section = document.getElementById('d-section-nuance');
    const coreEl = document.getElementById('d-nuance-core');
    const blocksEl = document.getElementById('d-nuance-blocks');
    const mistakeBox = document.getElementById('d-nuance-mistake');
    const mistakeText = document.getElementById('d-nuance-mistake-text');
    if (!section || !nuanceIndex) return;

    const pairs = nuanceIndex[hanzi];
    if (!pairs || pairs.length === 0) {
      section.classList.add('hidden');
      return;
    }

    // Kalau 1 kata punya >1 pasangan terdaftar (jarang, tapi mungkin di masa
    // depan), untuk sekarang tampilkan pasangan pertama saja.
    const pair = pairs[0];

    coreEl.textContent = pair.core_distinction_id || '';
    blocksEl.innerHTML = '';

    (pair.comparison || []).forEach(function (item) {
      const block = el('div', 'nuance-block');

      const head = el('div', 'nuance-head');
      const hz = el('span', 'nuance-hanzi', item.word);
      hz.title = 'Cari "' + item.word + '" di Kamus';
      hz.onclick = function () {
        if (typeof searchExample === 'function') searchExample(item.word);
      };
      head.appendChild(hz);
      if (item.pinyin) head.appendChild(el('span', 'nuance-pinyin', item.pinyin));
      block.appendChild(head);

      if (item.usage_id) block.appendChild(el('div', 'nuance-usage', item.usage_id));

      if (item.collocations && item.collocations.length) {
        const colloc = el('div', 'nuance-colloc');
        item.collocations.forEach(function (c) {
          colloc.appendChild(el('span', '', c));
        });
        block.appendChild(colloc);
      }

      if (item.example_cn) {
        const ex = el('div', 'nuance-example');
        ex.appendChild(el('div', 'ne-cn', item.example_cn));
        if (item.example_pinyin) ex.appendChild(el('div', 'ne-py', item.example_pinyin));
        if (item.example_id) ex.appendChild(el('div', 'ne-id', item.example_id));
        block.appendChild(ex);
      }

      blocksEl.appendChild(block);
    });

    if (pair.common_mistake_id) {
      mistakeText.textContent = pair.common_mistake_id;
      mistakeBox.classList.remove('hidden');
    } else {
      mistakeBox.classList.add('hidden');
    }

    section.classList.remove('hidden');
  }

  function currentHanzi() {
    const d = document.getElementById('d-hanzi');
    return d ? d.textContent.trim() : '';
  }

  function init() {
    const target = document.getElementById('d-hanzi');
    if (!target) {
      console.warn('[kamus-nuance] #d-hanzi tidak ditemukan, panel nuance tidak aktif');
      return;
    }

    const observer = new MutationObserver(function () {
      const hz = currentHanzi();
      if (hz) renderNuancePanel(hz);
    });
    observer.observe(target, { childList: true, characterData: true, subtree: true });

    // Jaga-jaga kalau detail panel sudah keisi duluan sebelum observer dipasang
    const hz = currentHanzi();
    if (hz) renderNuancePanel(hz);
  }

  loadNuanceData().then(function () {
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', init);
    } else {
      init();
    }
  });
})();

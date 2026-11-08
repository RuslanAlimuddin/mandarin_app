/* ═══════════════════════════════════════════════════════════════
   kamus-karakter-mirip.js — Panel "👀 Karakter Mirip (Bentuk Tulisan)"
   ═══════════════════════════════════════════════════════════════
   E.0.3 -- fitur tertunda sejak BLUEPRINT v8 (data siap, UI belum
   dibangun). BEDA dari kamus-nuance.js ("🆚 Beda dengan Kata Mirip"):
   itu soal NUANSA MAKNA (尝 vs 吃, dua kata beda konteks pemakaian),
   ini soal KEMIRIPAN BENTUK TULISAN (己/已/巳, gampang ketuker pas
   nulis/baca cepat) -- dua masalah belajar yang beda sama sekali.

   Berdiri sendiri: fetch data sendiri dari data/confusion_groups.json,
   auto-detect karakter yang lagi dibuka lewat MutationObserver di
   #d-hanzi. TIDAK mengubah kamus-detail.js.

   Index BIDIRECTIONAL: confusion_groups.json cuma nyimpen 1 "character"
   utama + array "confusable_with". Tapi kalau user buka salah SATU
   karakter lain dalam grup itu (bukan yang "utama"), panelnya harus
   tetap muncul juga (mis. buka 已 harus tetap nunjukin grup 己/已/巳,
   bukan cuma waktu buka 己). Makanya index dibangun dari SEMUA karakter
   dalam grup (character + confusable_with), bukan cuma key "character".

   Kalau karakter aktif tidak ada di data/confusion_groups.json, section
   otomatis disembunyikan (class "hidden") -- sama seperti pola section
   mnemonic/nuance yang sudah ada.
═══════════════════════════════════════════════════════════════ */

(function () {
  let miripIndex = null; // Map: hanzi -> group {allChars: [...], note}

  async function loadMiripData() {
    try {
      const res = await fetch('data/confusion_groups.json');
      if (!res.ok) throw new Error('HTTP ' + res.status);
      const data = await res.json();
      miripIndex = {};
      (data.groups || []).forEach(function (g) {
        const allChars = [g.character].concat(g.confusable_with || []);
        allChars.forEach(function (c) {
          // Index per karakter -- kalau karakter ini dibuka, tampilkan
          // SEMUA karakter LAIN dalam grup yang sama (kecualikan dirinya
          // sendiri saat render, bukan di sini, supaya data mentah tetap utuh).
          miripIndex[c] = { allChars: allChars, note: g.note || '' };
        });
      });
    } catch (e) {
      console.warn('[kamus-karakter-mirip] gagal load data/confusion_groups.json:', e);
      miripIndex = {};
    }
  }

  function renderMiripPanel(hanzi) {
    const section = document.getElementById('d-section-mirip');
    const chipsEl = document.getElementById('d-mirip-chips');
    const noteEl = document.getElementById('d-mirip-note');
    if (!section || !miripIndex) return;

    const group = miripIndex[hanzi];
    if (!group) {
      section.classList.add('hidden');
      return;
    }

    const others = group.allChars.filter(function (c) { return c !== hanzi; });
    if (others.length === 0) {
      section.classList.add('hidden');
      return;
    }

    chipsEl.innerHTML = '';
    others.forEach(function (c) {
      const chip = document.createElement('span');
      chip.className = 'mirip-chip';
      chip.textContent = c;
      chip.title = 'Cari "' + c + '" di Kamus';
      chip.onclick = function () {
        if (typeof searchExample === 'function') searchExample(c);
      };
      chipsEl.appendChild(chip);
    });

    noteEl.textContent = group.note || '';
    noteEl.style.display = group.note ? '' : 'none';

    section.classList.remove('hidden');
  }

  function currentHanzi() {
    const d = document.getElementById('d-hanzi');
    return d ? d.textContent.trim() : '';
  }

  function init() {
    const target = document.getElementById('d-hanzi');
    if (!target) {
      console.warn('[kamus-karakter-mirip] #d-hanzi tidak ditemukan, panel tidak aktif');
      return;
    }

    const observer = new MutationObserver(function () {
      const hz = currentHanzi();
      if (hz) renderMiripPanel(hz);
    });
    observer.observe(target, { childList: true, characterData: true, subtree: true });

    // Jaga-jaga kalau detail panel sudah keisi duluan sebelum observer dipasang
    const hz = currentHanzi();
    if (hz) renderMiripPanel(hz);
  }

  loadMiripData().then(function () {
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', init);
    } else {
      init();
    }
  });
})();

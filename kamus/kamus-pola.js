/* ═══════════════════════════════════════════════════════════════
   kamus-pola.js — Panel "🧩 Pola Pembentukan Kata"
   ═══════════════════════════════════════════════════════════════
   Fitur klasifikasi struktur gramatikal internal kata 2-karakter
   Mandarin ke 6 kategori: 联合式 (koordinatif), 偏正式 (modifier-inti),
   动宾式 (verba-objek), 主谓式 (subjek-predikat), 补充式 (verba-
   pelengkap), lainnya. Beda total dari wordbuilder.html (pola KALIMAT,
   bukan struktur kata) -- dua lapisan gramatika berbeda.

   Berdiri sendiri: fetch data sendiri dari data/kata_majemuk_pola.json,
   auto-detect kata yang lagi dibuka lewat MutationObserver di #d-hanzi.
   TIDAK mengubah kamus-detail.js -- sama seperti pola kamus-nuance.js.

   Kalau kata aktif tidak ada di data/kata_majemuk_pola.json (mis. kata
   3+ karakter, atau kata 1 karakter), section otomatis disembunyikan
   (class "hidden") -- sama seperti pola section nuance & mnemonic.
═══════════════════════════════════════════════════════════════ */

(function () {
  // Peta pola -> { label_id, singkat_id } utk ditampilkan di badge.
  // Sengaja tidak pakai warna berbeda per kategori (palet kamus.html
  // cuma punya token --gold/--red) -- pembeda visual pakai label teks,
  // bukan warna baru, supaya konsisten dgn palet yang sudah ada.
  var POLA_LABEL = {
    '联合式': { singkat: 'Koordinatif', deskripsi: 'dua unsur setara/sinonim' },
    '偏正式': { singkat: 'Modifier–Inti', deskripsi: 'unsur 1 menerangkan unsur 2' },
    '动宾式': { singkat: 'Verba–Objek', deskripsi: 'unsur 1 tindakan, unsur 2 sasaran' },
    '主谓式': { singkat: 'Subjek–Predikat', deskripsi: 'unsur 1 pelaku, unsur 2 keadaan/aksi' },
    '补充式': { singkat: 'Verba–Pelengkap', deskripsi: 'unsur 2 melengkapi hasil/arah unsur 1' },
    'lainnya': { singkat: 'Lainnya', deskripsi: 'serapan / kata fungsi / tidak baku pola' }
  };

  let polaIndex = null; // Map: hanzi -> entry {word, pola, keterangan_id}

  async function loadPolaData() {
    try {
      const res = await fetch('data/kata_majemuk_pola.json');
      if (!res.ok) throw new Error('HTTP ' + res.status);
      const data = await res.json();
      polaIndex = {};
      (data || []).forEach(function (entry) {
        if (entry && entry.word) polaIndex[entry.word] = entry;
      });
    } catch (e) {
      console.warn('[kamus-pola] gagal load data/kata_majemuk_pola.json:', e);
      polaIndex = {};
    }
  }

  function el(tag, cls, text) {
    const e = document.createElement(tag);
    if (cls) e.className = cls;
    if (text !== undefined) e.textContent = text;
    return e;
  }

  function renderPolaPanel(hanzi) {
    const section = document.getElementById('d-section-pola');
    const zhEl = document.getElementById('d-pola-zh');
    const labelEl = document.getElementById('d-pola-label');
    const descEl = document.getElementById('d-pola-desc');
    const keteranganEl = document.getElementById('d-pola-keterangan');
    if (!section || !polaIndex) return;

    const entry = polaIndex[hanzi];
    if (!entry) {
      section.classList.add('hidden');
      return;
    }

    const meta = POLA_LABEL[entry.pola] || { singkat: entry.pola, deskripsi: '' };

    zhEl.textContent = entry.pola;
    labelEl.textContent = meta.singkat;
    descEl.textContent = meta.deskripsi;
    keteranganEl.textContent = entry.keterangan_id || '';

    section.classList.remove('hidden');
  }

  function currentHanzi() {
    const d = document.getElementById('d-hanzi');
    return d ? d.textContent.trim() : '';
  }

  function init() {
    const target = document.getElementById('d-hanzi');
    if (!target) {
      console.warn('[kamus-pola] #d-hanzi tidak ditemukan, panel pola tidak aktif');
      return;
    }

    const observer = new MutationObserver(function () {
      const hz = currentHanzi();
      if (hz) renderPolaPanel(hz);
    });
    observer.observe(target, { childList: true, characterData: true, subtree: true });

    // Jaga-jaga kalau detail panel sudah keisi duluan sebelum observer dipasang
    const hz = currentHanzi();
    if (hz) renderPolaPanel(hz);
  }

  loadPolaData().then(function () {
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', init);
    } else {
      init();
    }
  });
})();

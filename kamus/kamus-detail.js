/* ═══════════════════════════════════════════════════════════════
   kamus/kamus-detail.js — Mandarin Interaktif
   Pilih & tampilkan panel detail kata, termasuk cross-link ke bacaan berjenjang
   Bagian dari modularisasi kamus.html. Dimuat sebagai <script src>
   biasa (bukan ES module) -- semua fungsi tetap di scope global,
   jadi urutan file lain relatif bebas KECUALI kamus-init.js yang
   WAJIB paling akhir.
   ═══════════════════════════════════════════════════════════════ */

/* ── SINONIM/ANTONIM: chip dengan pinyin+arti ─────────────────
   Sebelumnya chip sinonim/antonim cuma tampil hanzi polos. Sekarang
   dilengkapi pinyin+arti lookup dari STATE.dataHsk sendiri (offline,
   tidak fetch tambahan). Kalau kata terkait tidak ketemu di app_words.json
   (jarang, tapi mungkin), fallback aman ke hanzi saja seperti sebelumnya.

   (E.0.2) detailList opsional: array {word, pinyin, note_id} dari field
   synonyms_detail/antonyms_detail (hasil merge synonym_antonym.json,
   baru ada utk 134 kata). Kalau kata di chip ini punya note_id (catatan
   NUANSA hubungan, mis. "望" -> "menatap jauh ke depan" utk 看), itu
   dipakai sbg sub-teks krn lebih spesifik & berguna drpd arti kamus
   generik. Kalau tidak ada, fallback penuh ke relWordInfo() spt biasa
   -- jadi kata yg belum punya detail tampil persis spt sebelumnya. */
function relWordInfo(hanzi) {
  const data = STATE.dataHsk || [];
  const hit = data.find(w => (w.simplified || w.id) === hanzi);
  if (!hit) return null;
  const meaning = Array.isArray(hit.meanings_id) ? hit.meanings_id[0] : hit.meanings_id;
  return { pinyin: hit.pinyin || '', meaning: meaning || '' };
}

function renderRelWordChips(words, detailList) {
  const detailByWord = {};
  (detailList || []).forEach(d => { if (d && d.word) detailByWord[d.word] = d; });

  return words.map(s => {
    const detail = detailByWord[s];
    const info = relWordInfo(s);
    // Prioritas sub-teks: note_id (nuansa relasional) > arti kamus generik
    const pinyinText = (detail && detail.pinyin) || (info && info.pinyin) || '';
    const subText = (detail && detail.note_id) || (info && info.meaning) || '';
    const sub = (pinyinText || subText)
      ? `<span style="display:block;font-size:0.72rem;font-weight:400;color:var(--text-muted);line-height:1.3">${escHtml(pinyinText)}${pinyinText && subText ? ' · ' : ''}${escHtml(subText)}</span>`
      : '';
    return `<span class="rel-word-chip" style="display:inline-flex;flex-direction:column;align-items:flex-start;line-height:1.4" onclick="searchExample('${escHtml(s)}')">
      <span>${escHtml(s)}</span>${sub}
    </span>`;
  }).join('');
}

/* ── SELECT & TAMPILKAN DETAIL ─────────────────────────────── */
// Fix: cari dulu di STATE.results (hasil pencarian yang sedang tampil) sebelum
// fallback ke array sumber global — perlu karena hasil fallback CC-CIDICT
// (mode hanzi/id saat STATE.source === 'hsk') tidak ada di STATE.dataHsk,
// jadi pencarian lama (langsung ke dataHsk/dataCidict sesuai STATE.source)
// akan gagal senyap untuk kartu-kartu hasil fallback itu.
function findWordInResults(wordId, idx) {
  // Fix bug kartu duplikat: kalau idx (posisi asli di STATE.results) valid
  // DAN id-nya cocok dgn wordId, pakai itu langsung -- ini kunci fix-nya,
  // karena .find() di bawah selalu balikin entri PERTAMA yg id-nya sama,
  // padahal utk homograf (mis. 2 kartu 土 arti beda) posisi ke-2 dst yg
  // seharusnya dibuka. Ini juga otomatis nutup celah race lama: kalau
  // STATE.results berubah (search baru) SEBELUM klik diproses, idx basi
  // tidak akan cocok id-nya -> jatuh ke fallback, bukan salah nampilin data.
  if (typeof idx === 'number' && STATE.results[idx] &&
      (STATE.results[idx].id || STATE.results[idx].simplified) === wordId) {
    return STATE.results[idx];
  }
  // Fallback: idx tidak diisi / tidak valid (mis. pemanggilan selectWord(c.char, 0)
  // dari luar konteks hasil pencarian, lihat kamus-actions-filters.js:486)
  // -- cari by id spt perilaku lama.
  const fromResults = STATE.results.find(w => (w.id || w.simplified) === wordId);
  if (fromResults) return fromResults;
  const data = (STATE.source === 'cidict' && STATE.dataCidict)
    ? STATE.dataCidict
    : (STATE.dataHsk || []);
  return data.find(w => (w.id || w.simplified) === wordId);
}

function selectWord(wordId, idx) {
  if (!STATE.dataHsk) return; // guard
  // Highlight kartu terpilih
  document.querySelectorAll('.result-card').forEach(c => c.classList.remove('selected'));
  const card = document.querySelector(`.result-card[data-id="${CSS.escape(wordId)}"]`);
  if (card) card.classList.add('selected');

  // Cari data kata
  const word = findWordInResults(wordId, idx);

  if (!word) return;

  STATE.selectedId = wordId;
  addToRecent(wordId);
  renderDetail(word);
  saveKamusLastState();
}

/* ── CROSS-LINK KE BACAAN BERJENJANG ───────────────────────────
   Index dibangun sekali dari data/graded_readers.json, lazy-load
   (fetch baru terjadi saat detail kata pertama kali dibuka, bukan
   saat halaman kamus.html dibuka). Pola sama seperti dipakai di
   flashcard.html. Peta: kata (glossary[].cn) -> daftar bacaan. */
let KAMUS_READING_INDEX = null;
let kamusReadingIndexPromise = null;

function loadKamusReadingIndex() {
  if (kamusReadingIndexPromise) return kamusReadingIndexPromise;
  kamusReadingIndexPromise = fetch('data/graded_readers.json')
    .then(res => res.ok ? res.json() : { passages: [] })
    .then(data => {
      const idx = {};
      (data.passages || []).forEach(p => {
        (p.glossary || []).forEach(g => {
          if (!g.cn) return;
          if (!idx[g.cn]) idx[g.cn] = [];
          idx[g.cn].push({ id: p.id, title: p.title, level: p.level, tema: p.tema || null });
        });
      });
      KAMUS_READING_INDEX = idx;
      return idx;
    })
    .catch(e => {
      console.warn('data/graded_readers.json tidak tersedia utk cross-link bacaan:', e);
      KAMUS_READING_INDEX = {};
      return {};
    });
  return kamusReadingIndexPromise;
}

// Buka graded-reader.html langsung ke bacaan tertentu, reuse mekanisme
// "ingat posisi terakhir" yang sudah ada di graded-reader.html
// (restoreGrLastState via key mandarin_gr_last_state_v1).
function openReadingFromKamus(passageId) {
  try {
    localStorage.setItem('mandarin_gr_last_state_v1', JSON.stringify({
      view: 'reading',
      activeLevel: null,
      activeTema: null,
      passageId: passageId,
    }));
  } catch (e) { /* abaikan senyap -- bukan fitur kritis */ }
  window.location.href = 'graded-reader.html';
}

// Coba render panel "Bantu Ingat" utk kata N-karakter (N>=2). Aturan
// longgar: karakter yang tidak ketemu maknanya dilewati saja (bukan
// bikin seluruh panel disembunyikan), asal minimal 2 karakter berhasil.
// Kalau ada karakter yang belum ketemu & Cidict belum dimuat, coba
// fallback sekali, lalu render ulang dengan data yang sudah lebih lengkap.
function tryRenderMnemonic(chars, mainMeaning) {
  const resolved = [];
  let hasUnresolved = false;
  chars.forEach(c => {
    const m = getCharMeaning(c);
    if (m) {
      const etym = STATE.charEtymology && STATE.charEtymology[c];
      resolved.push({ char: c, meaning: m, note: (etym && etym.asal_usul_id) || null });
    } else {
      hasUnresolved = true;
    }
  });

  if (resolved.length >= 2) {
    renderMnemonicBox(resolved, mainMeaning);
  }

  if (hasUnresolved && !STATE.dataCidict) {
    const guardId = STATE.selectedId;
    loadCidict().then(() => {
      if (STATE.selectedId !== guardId) return; // رسلان sudah pindah kata
      const resolved2 = [];
      chars.forEach(c => {
        const m = getCharMeaning(c);
        if (m) {
          const etym = STATE.charEtymology && STATE.charEtymology[c];
          resolved2.push({ char: c, meaning: m, note: (etym && etym.asal_usul_id) || null });
        }
      });
      if (resolved2.length >= 2) renderMnemonicBox(resolved2, mainMeaning);
    });
  }
}

// Fix (etimologi 100% lengkap -- 2.840/2.840 karakter): sebelumnya hanya
// SEBAGIAN karakter punya catatan asal-usul (📜), jadi ditampilkan sebagai
// daftar terpisah di bawah rantai teks. Sekarang hampir semua karakter
// dari data/app_words.json punya catatan, jadi tampilan diubah jadi grid
// kartu per-karakter -- setiap kartu langsung menyatukan hanzi, makna,
// dan asal-usulnya, tanpa perlu daftar catatan terpisah.
// CSS pakai custom property global (var(--gold) dst, dari shared/style.css)
// lewat inline style -- supaya konsisten dengan tema tanpa perlu menyentuh
// file CSS kamus.html/shared/style.css yang di luar cakupan modul JS ini.
function renderMnemonicBox(resolved, mainMeaning) {
  const mnemoBox = $('d-mnemonic');

  const chain = resolved
    .map(r => `${escHtml(r.char)} (${escHtml(r.meaning)})`)
    .join(' + ');
  const summary = `💡 <strong>Bantu ingat:</strong> ${chain} → ${escHtml(mainMeaning || '')}`;

  const cards = resolved.map(r => {
    const noteHtml = r.note
      ? `<div style="font-size:0.78rem;color:var(--text-dim);line-height:1.5;margin-top:6px">📜 ${escHtml(r.note)}</div>`
      : `<div style="font-size:0.78rem;color:var(--text-muted);font-style:italic;margin-top:6px">Catatan asal-usul belum tersedia untuk karakter ini.</div>`;
    return `
      <div style="background:var(--bg-card2);border:1px solid var(--border);border-radius:var(--radius);padding:12px 14px;display:flex;flex-direction:column;gap:2px">
        <div style="display:flex;align-items:baseline;gap:8px">
          <span style="font-size:1.5rem;color:var(--text-main);font-weight:300">${escHtml(r.char)}</span>
          <span style="font-size:0.84rem;color:var(--gold)">${escHtml(r.meaning)}</span>
        </div>
        ${noteHtml}
      </div>`;
  }).join('');

  mnemoBox.innerHTML = `
    <div>${summary}</div>
    <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:8px;margin-top:10px">
      ${cards}
    </div>`;

  $('d-section-mnemonic').classList.remove('hidden');
}

function renderDetail(word) {
  // Guard: pastikan elemen DOM ada
  if (!$('detail-content') || !$('detail-empty-state')) return;
  // Sembunyikan empty state, tampilkan content
  $('detail-empty-state').classList.add('hidden');
  $('detail-content').classList.remove('hidden');
  $('detail-actions').classList.remove('hidden');

  const simplified   = word.simplified || word.id || '';
  const traditional  = word.traditional || '';
  const pinyin       = word.pinyin || '';
  const bopomofo     = word.bopomofo || '';
  const hskLv        = word.hsk;
  const radical      = word.radical || '—';
  const radicalNum   = word.radical_number || '—';
  const stroke       = word.stroke_count || '—';
  const charType     = word.char_type || '—';
  const structure    = word.structure || '';
  const components   = word.components || [];
  const meanings_id  = word.meanings_id || [];
  const meanings_en  = word.meanings_en || [];
  const pos_id       = word.pos_id || [];
  const themes       = word.themes || [];
  const synonyms     = word.synonyms || [];
  const antonyms     = word.antonyms || [];
  const frequency    = word.frequency;

  // Hanzi utama
  $('d-hanzi').textContent = simplified;

  // Tradisional
  if (traditional && traditional !== simplified) {
    $('d-traditional').innerHTML =
      'Tradisional: <span>' + escHtml(traditional) + '</span>';
    $('d-traditional').style.display = 'block';
  } else {
    $('d-traditional').style.display = 'none';
  }

  // Pinyin
  $('d-pinyin').textContent = pinyin;

  // Bopomofo
  if (bopomofo) {
    $('d-bopomofo').textContent = bopomofo;
    $('d-bopomofo').style.display = 'block';
  } else {
    $('d-bopomofo').style.display = 'none';
  }

  // Part of speech
  const posWrap = $('d-pos');
  posWrap.innerHTML = '';
  if (pos_id.length) {
    pos_id.forEach(p => {
      const span = document.createElement('span');
      span.className = 'detail-pos-tag';
      span.textContent = p;
      posWrap.appendChild(span);
    });
  } else if (word.pos && Array.isArray(word.pos)) {
    word.pos.forEach(p => {
      const span = document.createElement('span');
      span.className = 'detail-pos-tag';
      span.textContent = posLabel(p);
      posWrap.appendChild(span);
    });
  }

  // Arti Indonesia
  const meaningsEl = $('d-meanings-id');
  meaningsEl.innerHTML = '';
  const mArr = Array.isArray(meanings_id) ? meanings_id : [meanings_id];
  mArr.forEach((m, i) => {
    const li = document.createElement('li');
    li.className = 'detail-meaning-item';
    li.innerHTML =
      `<span class="detail-meaning-num">${i + 1}.</span>
       <span>${escHtml(m)}</span>`;
    meaningsEl.appendChild(li);
  });

  // Arti Inggris (secondary)
  const enArr = Array.isArray(meanings_en) ? meanings_en : [meanings_en];
  $('d-meanings-en').textContent = enArr.filter(Boolean).join('; ');

  // Contoh Kalimat (E.0.1) -- field contoh_kalimat_cn/pinyin/id, string
  // tunggal per field (dikonfirmasi via script intip, bukan array), jadi
  // paling banyak 1 contoh per kata. Baru ada di 257/11.983 entri, section
  // disembunyikan total kalau kata ini belum punya datanya.
  const contohCn     = word.contoh_kalimat_cn || '';
  const contohPinyin = word.contoh_kalimat_pinyin || '';
  const contohId     = word.contoh_kalimat_id || '';
  const contohSection = $('d-section-contoh');
  if (contohCn) {
    $('d-contoh-kalimat').innerHTML =
      `<div class="contoh-kalimat-cn">${escHtml(contohCn)}</div>
       <div class="contoh-kalimat-pinyin">${escHtml(contohPinyin)}</div>
       <div class="contoh-kalimat-id">${escHtml(contohId)}</div>`;
    contohSection.classList.remove('hidden');
  } else {
    contohSection.classList.add('hidden');
  }

  // Bantu Ingat (mnemonic dekomposisi karakter) -- BUKAN arti literal
  // resmi, cuma jembatan mengingat. Berlaku utk kata 2+ karakter.
  // Aturan LONGGAR (disepakati رسلان): tampilkan karakter yang KETEMU
  // maknanya saja, lewati yang tidak -- asal minimal 2 karakter berhasil
  // ditemukan, tetap tampil (walau tidak 100% lengkap/akurat).
  $('d-section-mnemonic').classList.add('hidden');
  if (simplified.length >= 2) {
    const mnChars = [...simplified];
    tryRenderMnemonic(mnChars, mArr[0]);
  }

  // Komponen karakter (Fix #4: pisahkan radikal semantik vs komponen lain)
  const compSection  = $('d-section-components');
  const compGrid     = $('d-components');
  const otherComps   = components.filter(c => c !== radical);
  const isSingleChar = simplified.length === 1;

  // Section ini sekarang SELALU tampil -- minimal ada tombol Animasikan
  // Goresan yang berlaku untuk kata apapun (1 atau banyak karakter),
  // terlepas dari ada tidaknya data komponen tercatat.
  {
    compGrid.innerHTML = '';

    if (components.length > 0) {
      // Radikal semantik (selalu ditampilkan terpisah jika ada & valid)
      if (radical && radical !== '—') {
        const chip = document.createElement('div');
        chip.className = 'component-chip';
        chip.title     = 'Radikal semantik — klik untuk lihat karakter lain yang berbagi radikal ini';
        chip.innerHTML =
          `<span class="comp-hanzi">${escHtml(radical)}</span>
           <span class="comp-info">⺄ radikal</span>`;
        chip.addEventListener('click', () => openComponentExplorer(radical));
        compGrid.appendChild(chip);
      }

      // Komponen lain (bukan radikal)
      otherComps.forEach(comp => {
        const chip = document.createElement('div');
        chip.className = 'component-chip';
        chip.title     = 'Komponen lain — klik untuk lihat karakter lain yang berbagi komponen ini';
        chip.innerHTML =
          `<span class="comp-hanzi">${escHtml(comp)}</span>
           <span class="comp-info">⿰ komponen</span>`;
        chip.addEventListener('click', () => openComponentExplorer(comp));
        compGrid.appendChild(chip);
      });

      // Tampilkan formula: 日 + 月 = 明 (butuh ≥2 komponen tercatat)
      if (components.length >= 2 && isSingleChar) {
        const formula = document.createElement('div');
        formula.className = 'component-visual mt-8';
        formula.innerHTML = components.map(c => `<span class="comp-char">${escHtml(c)}</span>`)
          .join('<span class="comp-op">+</span>') +
          '<span class="comp-op">=</span>' +
          `<span class="comp-result">${escHtml(simplified)}</span>`;
        compGrid.appendChild(formula);
      }
    }

    // Modul Stroke Order (Tier 3): animasi goresan kuas ASLI via Hanzi
    // Writer (data dari data/hanzi_writer_data.json). Sekarang berlaku
    // untuk kata APAPUN, tidak cuma 1-karakter -- kata multi-karakter
    // dianimasikan per-karakter berurutan (lihat playStrokeOrder).
    {
      const orderWrap = document.createElement('div');
      orderWrap.className = 'stroke-order-wrap mt-8';
      orderWrap.innerHTML = `
        <div class="hanzi-writer-multi hidden" id="hanzi-writer-multi"></div>
        <button class="btn-stroke-order" id="btn-stroke-order">▶ Animasikan Goresan</button>
        <div class="stroke-order-note" id="stroke-order-note">Memuat data goresan…</div>
      `;
      compGrid.appendChild(orderWrap);

      const playBtn = orderWrap.querySelector('#btn-stroke-order');
      playBtn.addEventListener('click', () => playStrokeOrder(simplified, compGrid, components));

      loadHanziWriterData().then(data => {
        const noteEl = $('stroke-order-note');
        if (!noteEl) return; // panel sudah berganti kata lain
        const chars   = Array.from(simplified);
        const covered = chars.filter(ch => data[ch]).length;

        if (covered === chars.length) {
          noteEl.textContent = chars.length > 1
            ? 'Animasi goresan kuas asli, per karakter berurutan (data: Make Me a Hanzi).'
            : 'Animasi goresan kuas asli (data: Make Me a Hanzi).';
        } else if (covered > 0) {
          noteEl.textContent = `Goresan asli tersedia untuk ${covered}/${chars.length} karakter kata ini, sisanya ditampilkan sebagai hanzi biasa.`;
        } else {
          noteEl.textContent = chars.length === 1 && components.length >= 2
            ? 'Data goresan presisi tidak tersedia untuk kata ini — pakai urutan komponen.'
            : 'Data goresan presisi tidak tersedia untuk kata ini.';
        }
      });
    }

    compSection.classList.remove('hidden');
  }

  // Struktur (+ prinsip urutan penulisan -- Modul Stroke Order, Tier 3)
  const structSection = $('d-section-structure');
  const structEl      = $('d-structure');
  if (structure) {
    const label     = structureLabel(structure);
    const iconMatch = label.match(/^\S+/); // ambil karakter ideographic description di depan label
    const icon      = iconMatch ? iconMatch[0] : '⿰';
    // Fix bug ⿰⿰: `label` SUDAH mengandung ikon di depan (mis. "⿰ Kiri–Kanan").
    // Sebelumnya ikon itu ditampilkan lagi terpisah di .struct-icon TANPA
    // dihapus dari teks label, jadi ikonnya tampil dobel. labelText di sini
    // adalah label TANPA ikon depan, karena ikon sudah ada di .struct-icon.
    const labelText = label.replace(/^\S+\s*/, '');
    const orderText = structureOrderText(structure);

    structEl.innerHTML =
      `<span class="structure-badge" style="cursor:pointer" title="Lihat karakter lain dengan struktur ini">
         <span class="struct-icon">${escHtml(icon)}</span>
         ${escHtml(labelText)}
       </span>
       ${orderText ? `<div class="structure-order-text">✍️ ${escHtml(orderText)}</div>` : ''}`;
    const structBadge = structEl.querySelector('.structure-badge');
    if (structBadge) structBadge.addEventListener('click', () => selectGroupItem('struct', structure));
    structSection.classList.remove('hidden');
  } else {
    structSection.classList.add('hidden');
  }

  // Meta grid
  $('d-radical').textContent      = radical;
  $('d-radical-num').textContent  = radicalNum;
  $('d-stroke').textContent       = stroke + (stroke !== '—' ? ' goresan' : '');
  $('d-type').textContent         = charType;
  $('d-hsk').textContent          = hskLv ? hskLabel(hskLv) : '—';
  $('d-frequency').textContent    = frequency ? '#' + frequency.toLocaleString('id') : '—';

  // Tema — Fix Tier 3: sekarang bisa diklik, langsung tampilkan kata lain
  // dengan tema yang sama (pakai mekanisme "Per Tema" yang sudah ada).
  const themeSection = $('d-section-themes');
  const themesWrap   = $('d-themes');
  if (themes.length) {
    themesWrap.innerHTML = themes.map(t =>
      `<span class="tag tag-theme" data-theme-key="${escHtml(t)}" title="Lihat kata lain dengan tema ini">${escHtml(t.replace(/_/g, ' '))}</span>`
    ).join('');
    themesWrap.querySelectorAll('.tag-theme').forEach(el => {
      el.addEventListener('click', () => selectGroupItem('theme', el.dataset.themeKey));
    });
    themeSection.classList.remove('hidden');
  } else {
    themeSection.classList.add('hidden');
  }

  // Sinonim
  const synSection = $('d-section-synonyms');
  const synWrap    = $('d-synonyms');
  if (synonyms.length) {
    synWrap.innerHTML = renderRelWordChips(synonyms, word.synonyms_detail);
    synSection.classList.remove('hidden');
  } else {
    synSection.classList.add('hidden');
  }

  // Antonim
  const antSection = $('d-section-antonyms');
  const antWrap    = $('d-antonyms');
  if (antonyms.length) {
    antWrap.innerHTML = renderRelWordChips(antonyms, word.antonyms_detail);
    antSection.classList.remove('hidden');
  } else {
    antSection.classList.add('hidden');
  }

  // Cross-link ke bacaan berjenjang yang mengandung kata ini.
  // Async lazy-load index -- pakai penjaga STATE.selectedId supaya tidak
  // salah render kalau رسلان sudah pindah kata selagi fetch berjalan.
  const bacaanSection = $('d-section-bacaan');
  const bacaanWrap    = $('d-bacaan');
  const bacaanWordId  = word.id || word.simplified;
  bacaanSection.classList.add('hidden');
  bacaanWrap.innerHTML = '';
  loadKamusReadingIndex().then(idx => {
    if (STATE.selectedId !== bacaanWordId) return;
    const matches = idx[simplified] || [];
    if (!matches.length) return;
    const sorted = [...matches]
      .sort((a, b) => Math.abs((a.level || 0) - (hskLv || 0)) - Math.abs((b.level || 0) - (hskLv || 0)))
      .slice(0, 5);
    bacaanWrap.innerHTML = sorted.map(p =>
      `<span class="rel-word-chip" onclick="openReadingFromKamus('${p.id}')">${escHtml(p.title)} <span style="color:var(--text-muted)">(HSK ${p.level})</span></span>`
    ).join('');
    bacaanSection.classList.remove('hidden');
  });

  // Update tombol bookmark
  updateBookmarkBtn(word.id || word.simplified);
}


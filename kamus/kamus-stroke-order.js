/* ═══════════════════════════════════════════════════════════════
   kamus/kamus-stroke-order.js — Mandarin Interaktif
   Animasi urutan goresan (Hanzi Writer + fallback komponen)
   Bagian dari modularisasi kamus.html. Dimuat sebagai <script src>
   biasa (bukan ES module) -- semua fungsi tetap di scope global,
   jadi urutan file lain relatif bebas KECUALI kamus-init.js yang
   WAJIB paling akhir.
   ═══════════════════════════════════════════════════════════════ */

/* ── MODUL STROKE ORDER (Tier 3): animasi goresan kuas asli ───
   Data dari data/hanzi_writer_data.json (proyek Make Me a Hanzi, lewat
   library Hanzi Writer). Di-fetch SEKALI, di-cache di memori. Kalau
   datanya tidak ada untuk suatu karakter (mis. dari Cidict yang tidak
   ke-cover saat penyaringan), fallback ke highlight-urutan-komponen. */
let HANZI_WRITER_DATA = null;
let hanziWriterDataPromise = null;

function loadHanziWriterData() {
  if (hanziWriterDataPromise) return hanziWriterDataPromise;
  hanziWriterDataPromise = fetch('data/hanzi_writer_data.json')
    .then(res => res.ok ? res.json() : {})
    .then(data => { HANZI_WRITER_DATA = data; return data; })
    .catch(e => {
      console.warn('data/hanzi_writer_data.json tidak tersedia:', e);
      HANZI_WRITER_DATA = {};
      return {};
    });
  return hanziWriterDataPromise;
}

function playStrokeOrder(word, compGrid, components) {
  loadHanziWriterData().then(data => {
    const chars   = Array.from(word); // Array.from aman utk karakter multi-byte
    const multiEl = $('hanzi-writer-multi');
    if (!multiEl) return;

    // Kasus lama: 1 karakter DAN datanya tidak ada -- fallback ke
    // highlight komponen (masih relevan & berguna utk kasus ini).
    if (chars.length === 1 && (!data[chars[0]] || !window.HanziWriter)) {
      multiEl.classList.add('hidden');
      playComponentOrder(compGrid, components);
      return;
    }

    // Kata multi-karakter TAPI tidak ada satupun datanya -- tidak ada
    // yang bisa dianimasikan, diam saja (catatan di bawah tombol sudah
    // menjelaskan ini).
    if (!chars.some(ch => data[ch]) || !window.HanziWriter) {
      multiEl.classList.add('hidden');
      return;
    }

    multiEl.innerHTML = '';
    multiEl.classList.remove('hidden');

    const slots = chars.map(ch => {
      const slot = document.createElement('div');
      slot.className = 'hanzi-writer-slot';
      multiEl.appendChild(slot);
      return { ch, slot };
    });

    // Animasikan satu-satu berurutan (bukan bersamaan) -- lebih mudah
    // diikuti matanya untuk kata beberapa karakter.
    let idx = 0;
    function playNext() {
      if (idx >= slots.length) return;
      const { ch, slot } = slots[idx];
      const charData = data[ch];

      if (charData) {
        slot.innerHTML = '';
        const writer = HanziWriter.create(slot, ch, {
          width: chars.length > 1 ? 90 : 140,
          height: chars.length > 1 ? 90 : 140,
          padding: 6,
          strokeAnimationSpeed: 1,
          delayBetweenStrokes: 220,
          strokeColor: '#c9a84c',
          outlineColor: 'rgba(255,255,255,0.15)',
          charDataLoader: () => charData,
        });
        writer.animateCharacter({
          onComplete: () => { idx++; setTimeout(playNext, 350); },
        });
      } else {
        // Karakter ini tidak ada datanya -- tampilkan hanzi biasa, lanjut
        slot.innerHTML = `<div class="hanzi-writer-nodata" title="Data goresan tidak tersedia">${escHtml(ch)}</div>`;
        idx++;
        setTimeout(playNext, 150);
      }
    }
    playNext();
  });
}

/* ── MODUL STROKE ORDER (fallback lama): urutan komponen ──────
   Dipakai kalau data goresan presisi tidak tersedia untuk karakter ini
   (lihat playStrokeOrder di atas). Highlight mengikuti urutan APA ADANYA
   di array `components` -- prinsip urutan komponen, bukan goresan presisi. */
function findChipByChar(chips, ch) {
  return chips.find(c => {
    const hanziEl = c.querySelector('.comp-hanzi');
    return hanziEl && hanziEl.textContent === ch;
  });
}

function playComponentOrder(compGrid, components) {
  const chips = Array.from(compGrid.querySelectorAll('.component-chip'));
  chips.forEach(chip => chip.classList.remove('stroke-order-active', 'stroke-order-done'));

  const seq = components.slice();
  let i = 0;

  function step() {
    if (i > 0) {
      const prevChip = findChipByChar(chips, seq[i - 1]);
      if (prevChip) {
        prevChip.classList.remove('stroke-order-active');
        prevChip.classList.add('stroke-order-done');
      }
    }
    if (i >= seq.length) return;
    const chip = findChipByChar(chips, seq[i]);
    if (chip) chip.classList.add('stroke-order-active');
    i++;
    setTimeout(step, 900);
  }
  step();
}


/* ═══════════════════════════════════════════════════════════════
   wordbuilder-collection.js — Koleksi Tersimpan: simpan ke Flashcard,
   modal koleksi, hapus item
═══════════════════════════════════════════════════════════════ */
'use strict';


/* ── SIMPAN KE FLASHCARD ────────────────────────────────────── */
function addToFlashcardWB() {
  const cn = $('wb-out-chinese').textContent;
  const py = $('wb-out-pinyin').textContent;
  const id = $('wb-out-translation').textContent;

  if (!cn) {
    showToast('Lengkapi kalimat terlebih dahulu.');
    return;
  }

  try {
    // Simpan sebagai entri kustom di localStorage (terpisah dari SRS kata)
    const key  = 'mandarin_wb_saved';
    const saved = JSON.parse(localStorage.getItem(key) || '[]');
    // slotValues disimpan juga supaya nanti waktu diklik dari koleksi, tiap
    // slot (subjek/objek/tempat/dst) bisa direstorasi utuh, bukan cuma
    // teks hasil akhirnya saja.
    const entry = {
      cn, py, id,
      pattern: WB.activePattern,
      ts: Date.now(),
      slotValues: JSON.parse(JSON.stringify(WB.slotValues)),
    };

    // Cegah duplikasi
    if (saved.find(e => e.cn === cn)) {
      showToast('Kalimat ini sudah tersimpan.');
      return;
    }

    saved.unshift(entry);
    localStorage.setItem(key, JSON.stringify(saved.slice(0, 200)));
    showToast('✓ Kalimat disimpan ke koleksi Word Builder!', 'success');
    updateCollectionBadge();
  } catch (e) {
    showToast('⚠ Gagal menyimpan.', 'error');
  }
}


/* ── KOLEKSI TERSIMPAN (lihat/hapus) ────────────────────────── */
const COLLECTION_KEY = 'mandarin_wb_saved';

function getCollection() {
  try {
    return JSON.parse(localStorage.getItem(COLLECTION_KEY) || '[]');
  } catch (e) {
    return [];
  }
}


function updateCollectionBadge() {
  const el = $('wb-collection-count');
  if (el) el.textContent = getCollection().length;
}


function openCollectionModal() {
  renderCollectionList();
  $('wb-collection-modal').classList.add('open');
}


function closeCollectionModal() {
  $('wb-collection-modal').classList.remove('open');
}


function renderCollectionList() {
  const container = $('wb-collection-list');
  const saved = getCollection();

  if (!saved.length) {
    container.innerHTML = '<div class="wb-collection-empty">Belum ada kalimat tersimpan.</div>';
    return;
  }

  container.innerHTML = '';
  saved.forEach(entry => {
    const patternName = (PATTERNS[entry.pattern] && PATTERNS[entry.pattern].name) || entry.pattern || '';
    const card = document.createElement('div');
    card.className = 'wb-collection-card';
    card.innerHTML =
      `<div class="wb-collection-info">
         <div class="wb-collection-pattern">${escHtml(patternName)}</div>
         <div class="wb-example-cn">${escHtml(entry.cn)}</div>
         <div class="wb-example-py">${escHtml(entry.py)}</div>
         <div class="wb-example-id">${escHtml(entry.id)}</div>
       </div>
       <button class="wb-collection-delete" title="Hapus" data-ts="${entry.ts}">🗑</button>`;

    // Klik kartu (selain tombol hapus) → buka pola yang cocok + isi tiap
    // slot (subjek/objek/tempat/dst) seperti semula, bukan cuma tempel
    // teks hasil akhir ke output.
    card.addEventListener('click', (e) => {
      if (e.target.closest('.wb-collection-delete')) return;
      closeCollectionModal();

      if (entry.pattern && PATTERNS[entry.pattern]) {
        if (entry.slotValues && Object.keys(entry.slotValues).length) {
          WB.pendingSlotValues = entry.slotValues;
          loadPattern(entry.pattern); // renderSlots otomatis isi tiap slot + buildOutput
        } else {
          // Data lama (disimpan sebelum slotValues ikut disimpan) — buka
          // pola-nya tapi slot tetap kosong, cuma output ditempel manual.
          loadPattern(entry.pattern);
          $('wb-output-placeholder').classList.add('hidden');
          $('wb-output-result').classList.remove('hidden');
          $('wb-copy-btn').style.display = '';
          $('btn-speak-wb').style.display = '';
          $('wb-out-chinese').textContent     = entry.cn;
          $('wb-out-pinyin').textContent      = entry.py;
          $('wb-out-translation').textContent = entry.id;
        }
        showToast(`Dibuka di pola "${PATTERNS[entry.pattern].name}".`, 'success');
      } else {
        // Pattern tidak dikenali (data korup/lama) — fallback tempel output saja
        $('wb-output-placeholder').classList.add('hidden');
        $('wb-output-result').classList.remove('hidden');
        $('wb-copy-btn').style.display = '';
        $('btn-speak-wb').style.display = '';
        $('wb-out-chinese').textContent     = entry.cn;
        $('wb-out-pinyin').textContent      = entry.py;
        $('wb-out-translation').textContent = entry.id;
        showToast('Kalimat dari koleksi ditampilkan di output.');
      }
    });

    card.querySelector('.wb-collection-delete').addEventListener('click', () => {
      deleteCollectionItem(entry.ts);
    });

    container.appendChild(card);
  });
}


function deleteCollectionItem(ts) {
  const saved = getCollection().filter(e => e.ts !== ts);
  localStorage.setItem(COLLECTION_KEY, JSON.stringify(saved));
  renderCollectionList();
  updateCollectionBadge();
  showToast('Kalimat dihapus dari koleksi.');
}


function clearAllCollection() {
  if (!getCollection().length) return;
  if (!confirm('Hapus semua kalimat tersimpan? Tindakan ini tidak bisa dibatalkan.')) return;
  localStorage.setItem(COLLECTION_KEY, JSON.stringify([]));
  renderCollectionList();
  updateCollectionBadge();
  showToast('Semua kalimat di koleksi telah dihapus.');
}

/* ═══════════════════════════════════════════════════════════════
   flashcard-storage-layout.js — Simpan/pulihkan state terakhir,
   ganti layar (showScreen), statistik global ringkasan
═══════════════════════════════════════════════════════════════ */
'use strict';


/* ── INGAT DECK TERAKHIR (Tier 1 lintas-halaman) ────────────────────
   Kalau رسلان pindah ke halaman lain lewat navbar lalu balik lagi,
   deck yang terakhir dipilih otomatis di-highlight lagi + tombol "Mulai
   Sesi" siap -- TIDAK auto-mulai sesi (biar tidak mengejutkan). */
const FC_LAST_STATE_KEY = 'mandarin_fc_last_state_v1';

function saveFlashcardLastState() {
  try {
    localStorage.setItem(FC_LAST_STATE_KEY, JSON.stringify({
      deckId:     FC.deckId,
      deckName:   FC.deckName,
      gameModeOn: FC.gameModeOn,
      ignoreDue:  FC.ignoreDue,
    }));
  } catch (e) { /* abaikan senyap -- bukan fitur kritis */ }
}

function restoreFlashcardLastState() {
  let saved;
  try {
    saved = JSON.parse(localStorage.getItem(FC_LAST_STATE_KEY) || 'null');
  } catch (e) { return; }
  if (!saved) return;

  if (typeof saved.gameModeOn === 'boolean') {
    FC.gameModeOn = saved.gameModeOn;
    const cb = $('ctrl-game-mode');
    if (cb) cb.checked = saved.gameModeOn;
  }

  if (typeof saved.ignoreDue === 'boolean') {
    FC.ignoreDue = saved.ignoreDue;
    const cbId = $('ctrl-ignore-due');
    if (cbId) cbId.checked = saved.ignoreDue;
  }

  if (!saved.deckId) return;

  // Hanya restore kalau item deck itu memang masih ada di sidebar
  // (mis. deck tema/radikal lama yang datanya berubah, item bisa hilang)
  const el = document.querySelector(`.sidebar-item[data-deck="${CSS.escape(saved.deckId)}"]`);
  if (!el) return;

  selectDeck(saved.deckId, saved.deckName);
}

/* ═══════════════════════════════════════════════════════════════
   flashcard.html — PART 5: UI helpers, statistik, keyboard, init
═══════════════════════════════════════════════════════════════ */

/* ── SCREEN SWITCHER ───────────────────────────────────────── */
function showScreen(name) {
  // name: 'choose' | 'session' | 'done'
  $('screen-choose').classList.toggle('hidden',  name !== 'choose');
  $('screen-done').classList.toggle('visible',   name === 'done');
  $('screen-done').style.display = name === 'done' ? 'flex' : 'none';

  const sessionEl = $('screen-session');
  if (name === 'session') {
    sessionEl.classList.remove('hidden');
    sessionEl.style.display = 'flex';
  } else {
    sessionEl.classList.add('hidden');
    sessionEl.style.display = 'none';
  }
}

/* ── STATISTIK GLOBAL (ringkasan semua waktu) ──────────────── */
function getGlobalStats() {
  const srs = srsLoad();
  const entries = Object.values(srs);
  if (!entries.length) return null;

  const total   = entries.length;
  const dueNow  = entries.filter(c => isDue(c.due)).length;
  const mature  = entries.filter(c => c.interval >= 21).length;
  const totalReps = entries.reduce((a, c) => a + (c.reps || 0), 0);

  return { total, dueNow, mature, totalReps };
}

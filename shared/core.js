/* ═══════════════════════════════════════════════════════════════
   shared/core.js — Mandarin Interaktif
   Utilitas UI/DOM generik dipakai bersama oleh kamus.html, flashcard.html,
   dan wordbuilder.html.

   WAJIB dimuat SEBELUM script utama tiap halaman, contoh urutan tag:
     1) shared/core.js
     2) shared/pinyin.js
     3) shared/audio.js
     4) PART 1, 2, 3, dst (script utama halaman)

   Menggantikan total: $$() di flashcard.html dan $w() di wordbuilder.html.
   Tidak ada alias tersisa — semua halaman sekarang pakai $() saja.
═══════════════════════════════════════════════════════════════ */

/* ── SELECTOR ──────────────────────────────────────────────── */
function $(id) {
  return document.getElementById(id);
}

/* ── TOAST ─────────────────────────────────────────────────── */
function showToast(msg, type = '') {
  const wrap  = $('toast-wrap');
  const toast = document.createElement('div');
  toast.className   = 'toast' + (type ? ' ' + type : '');
  toast.textContent = msg;
  wrap.appendChild(toast);
  setTimeout(() => toast.remove(), 3000);
}

/* ── ESCAPE HTML ───────────────────────────────────────────── */
function escHtml(str) {
  if (!str) return '';
  return String(str)
    .replace(/&/g, '&amp;').replace(/</g, '&lt;')
    .replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}

/* ── EXPORT / IMPORT BACKUP (Tier 1) ──────────────────────────
   Backup semua localStorage app jadi 1 file .json, dipakai bersama
   oleh kamus.html, flashcard.html, wordbuilder.html.

   Desain: enumerasi SEMUA key localStorage origin ini saat export
   (bukan daftar manual per-nama) supaya otomatis mencakup key baru
   yang ditambahkan di masa depan tanpa perlu update fungsi ini lagi.
   Satu pengecualian: wb_ref_word (sinyal transit sekali-pakai
   Flashcard → Word Builder, bukan data asli — kalau ikut di-restore
   bisa memicu prefill pola yang tidak diharapkan). */

const BACKUP_EXCLUDE_KEYS = ['wb_ref_word'];

function exportBackup() {
  try {
    const data = {};
    for (let i = 0; i < localStorage.length; i++) {
      const key = localStorage.key(i);
      if (BACKUP_EXCLUDE_KEYS.includes(key)) continue;
      data[key] = localStorage.getItem(key);
    }

    if (!Object.keys(data).length) {
      showToast('Belum ada data tersimpan untuk di-backup.');
      return;
    }

    const payload = {
      app:         'Mandarin Interaktif',
      exported_at: new Date().toISOString(),
      data,
    };

    const blob = new Blob([JSON.stringify(payload, null, 2)], { type: 'application/json' });
    const url  = URL.createObjectURL(blob);
    const a    = document.createElement('a');
    const dateStr = new Date().toISOString().slice(0, 10);
    a.href     = url;
    a.download = `mandarin_backup_${dateStr}.json`;
    document.body.appendChild(a);
    a.click();
    a.remove();
    URL.revokeObjectURL(url);

    showToast('✓ Backup diunduh.', 'success');
  } catch (e) {
    console.error('Gagal membuat backup:', e);
    showToast('⚠ Gagal membuat backup.', 'error');
  }
}

function importBackupFromFile(file) {
  if (!file) return;

  const reader = new FileReader();

  reader.onload = () => {
    let payload;
    try {
      payload = JSON.parse(reader.result);
    } catch (e) {
      showToast('⚠ File bukan JSON yang valid.', 'error');
      return;
    }

    // Toleransi: file backup format baru ({app, exported_at, data}) atau
    // seandainya dulu pernah ada versi mentah (langsung {key: value}).
    const data = (payload && typeof payload === 'object' && payload.data) ? payload.data : payload;
    if (!data || typeof data !== 'object' || Array.isArray(data)) {
      showToast('⚠ Format file backup tidak dikenali.', 'error');
      return;
    }

    const keys = Object.keys(data).filter(k => !BACKUP_EXCLUDE_KEYS.includes(k));
    if (!keys.length) {
      showToast('File backup kosong atau tidak berisi data yang dikenali.');
      return;
    }

    const confirmMsg =
      `Import akan menimpa ${keys.length} data tersimpan yang key-nya sama ` +
      `(progres SRS, koleksi, bookmark, dll). Data yang tidak ada di file ini ` +
      `TIDAK akan dihapus. Lanjutkan?`;
    if (!confirm(confirmMsg)) return;

    let restored = 0;
    keys.forEach(key => {
      try {
        localStorage.setItem(key, data[key]);
        restored++;
      } catch (e) {
        console.error('Gagal restore key:', key, e);
      }
    });

    showToast(`✓ ${restored} data berhasil di-restore. Memuat ulang halaman...`, 'success');
    setTimeout(() => location.reload(), 1200);
  };

  reader.onerror = () => {
    showToast('⚠ Gagal membaca file.', 'error');
  };

  reader.readAsText(file);
}

// Dipanggil dari onchange <input type="file"> di tiap halaman
function handleBackupFileInput(inputEl) {
  const file = inputEl.files && inputEl.files[0];
  importBackupFromFile(file);
  inputEl.value = ''; // reset supaya file yang sama bisa dipilih lagi nanti
}

/* ── STREAK HARIAN (dipakai Dashboard di index.html) ──────────────
   Dicatat di sini (bukan cuma di index.html) supaya tetap ke-update
   walau رسلان belajar lewat Kamus/Flashcard/Word Builder/Bacaan/Tone/
   Ujian HSK tanpa pernah buka index.html duluan hari itu. Dipanggil
   otomatis sekali di akhir file ini, setiap kali core.js dimuat --
   core.js sudah jadi urutan pertama load di semua halaman. */
const STREAK_KEY = 'mandarin_streak_v1';

function touchStreak() {
  try {
    const todayStr = new Date().toISOString().slice(0, 10);
    let s = JSON.parse(localStorage.getItem(STREAK_KEY) || 'null');

    if (!s) {
      s = { current: 1, longest: 1, lastDate: todayStr };
      localStorage.setItem(STREAK_KEY, JSON.stringify(s));
      return s;
    }
    if (s.lastDate === todayStr) return s; // sudah tercatat hari ini, jangan dobel

    const yesterday = new Date(Date.now() - 86400000).toISOString().slice(0, 10);
    s.current = (s.lastDate === yesterday) ? s.current + 1 : 1; // lanjut atau putus
    s.longest = Math.max(s.longest || 0, s.current);
    s.lastDate = todayStr;
    localStorage.setItem(STREAK_KEY, JSON.stringify(s));
    return s;
  } catch (e) {
    return null; // abaikan senyap -- bukan fitur kritis
  }
}

touchStreak();


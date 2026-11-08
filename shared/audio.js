/* ═══════════════════════════════════════════════════════════════
   shared/audio.js — Mandarin Interaktif (Tier 1)
   Wrapper browser SpeechSynthesis API — 100% lokal/offline, tidak
   butuh file rekaman, bisa menjangkau kalimat generatif Word Builder.

   WAJIB dimuat SETELAH shared/core.js (butuh showToast) dan setelah
   shared/pinyin.js, contoh urutan file yang dimuat:
     1) shared/core.js
     2) shared/pinyin.js
     3) shared/audio.js

   Tombol speaker SELALU tampil di UI, apapun kondisi voice-nya.
   Toast error hanya muncul saat tombol diklik dan memang gagal —
   bukan disembunyikan dari awal.

   Kecepatan default LAMBAT (0.8x) dan RESET ke lambat setiap halaman
   dibuka (sesuai keputusan: tidak disimpan ke localStorage).
═══════════════════════════════════════════════════════════════ */

const AudioTTS = {
  RATE_SLOW:   0.8,
  RATE_NORMAL: 1.0,
  rate:  0.8,   // selalu mulai dari lambat tiap page load
  voice: null,
};

/* ── CARI VOICE MANDARIN TERBAIK YANG TERSEDIA ─────────────── */
function pickMandarinVoice() {
  if (!('speechSynthesis' in window)) return null;
  const voices = window.speechSynthesis.getVoices() || [];
  return voices.find(v => v.lang === 'zh-CN')
      || voices.find(v => v.lang && v.lang.toLowerCase().startsWith('zh'))
      || null;
}

/* ── INIT: coba cari voice saat load, dan saat daftar voice siap ──
   (di banyak browser, getVoices() kosong di awal lalu terisi async
   lewat event 'voiceschanged') */
function initAudioVoices() {
  if (!('speechSynthesis' in window)) return;
  AudioTTS.voice = pickMandarinVoice();
  window.speechSynthesis.onvoiceschanged = () => {
    AudioTTS.voice = pickMandarinVoice();
  };
}

/* ── UCAPKAN TEKS (fungsi utama) ────────────────────────────── */
function speak(text, opts = {}) {
  if (!text) return;

  if (!('speechSynthesis' in window)) {
    showToast('⚠ Browser tidak mendukung Text-to-Speech.', 'error');
    return;
  }

  const voice = AudioTTS.voice || pickMandarinVoice();
  if (!voice) {
    // Tetap lanjut coba bicara pakai voice default browser (mungkin
    // aksennya kurang pas), tapi beri tahu penggunanya.
    showToast('⚠ Voice Mandarin tidak ditemukan di perangkat ini.', 'error');
  }

  // Hentikan ucapan sebelumnya supaya tidak menumpuk kalau diklik cepat
  window.speechSynthesis.cancel();

  const utter = new SpeechSynthesisUtterance(text);
  utter.lang = 'zh-CN';
  utter.rate = opts.rate || AudioTTS.rate;
  if (voice) utter.voice = voice;

  utter.onerror = (e) => {
    // 'interrupted' terjadi karena cancel() kita sendiri di atas — bukan error asli
    if (e.error !== 'interrupted') {
      showToast('⚠ Gagal memutar suara.', 'error');
    }
  };

  window.speechSynthesis.speak(utter);
}

/* ── TOGGLE KECEPATAN LAMBAT ↔ NORMAL ───────────────────────── */
function toggleAudioRate() {
  AudioTTS.rate = (AudioTTS.rate === AudioTTS.RATE_SLOW)
    ? AudioTTS.RATE_NORMAL
    : AudioTTS.RATE_SLOW;

  document.querySelectorAll('.audio-speed-btn').forEach(btn => {
    const isSlow = AudioTTS.rate === AudioTTS.RATE_SLOW;
    btn.textContent = isSlow ? '🐢' : '🐇';
    btn.title = isSlow
      ? 'Kecepatan: Lambat (klik untuk normal)'
      : 'Kecepatan: Normal (klik untuk lambat)';
  });
}

document.addEventListener('DOMContentLoaded', initAudioVoices);

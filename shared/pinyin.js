/* ═══════════════════════════════════════════════════════════════
   shared/pinyin.js — Mandarin Interaktif
   Utilitas pinyin, pindahan dari kamus.html tanpa ubah logika.
   Dipisah dari shared/core.js karena shared/audio.js (Tier 1) akan
   butuh fungsi-fungsi ini juga untuk membaca nada dengan benar.

   CATATAN SCOPE: detectMode() aslinya dipakai kamus.html dan bergantung
   pada isProbablyHanzi/isProbablyPinyin/isProbablyIndonesian/ID_STOPWORDS,
   jadi semuanya dipindah sebagai satu paket utuh (bukan cuma 3 fungsi
   yang disebut di BLUEPRINT_v5, supaya detectMode tidak pecah).

   detectMode() masih membaca variabel global STATE.searchMode — ini
   hanya relevan untuk kamus.html yang memang mendefinisikan STATE.
   Halaman lain (flashcard/wordbuilder) aman memuat file ini karena
   mereka tidak memanggil detectMode().
═══════════════════════════════════════════════════════════════ */

/* ── DETEKSI JENIS INPUT ───────────────────────────────────── */
function isProbablyHanzi(str) {
  return /[\u3400-\u9FFF\uF900-\uFAFF]/.test(str);
}

function isProbablyPinyin(str) {
  // Mengandung huruf latin + opsional angka nada atau diakritik
  return /^[a-zāáǎàēéěèīíǐìōóǒòūúǔùǖǘǚǜüA-Z0-9\s]+$/.test(str.trim()) &&
         !isProbablyHanzi(str);
}

// Fix #2: pembeda kata Indonesia vs pinyin (keduanya huruf latin)
const ID_STOPWORDS = new Set([
  'yang','dan','di','ke','dari','untuk','dengan','pada','ini','itu',
  'tidak','ada','juga','sudah','akan','bisa','saya','kamu','dia','kami',
  'mereka','kita','atau','jika','kalau','karena','seperti','adalah',
  'apa','siapa','kapan','dimana','mengapa','bagaimana','berapa',
  'makan','minum','pergi','buku','rumah','sekolah','belajar','kerja',
  'orang','hari','waktu','tahun','bulan','minggu','baik','besar','kecil',
  'banyak','sedikit','semua','tetapi','namun','agar','supaya','setelah',
  'sebelum','selama','tentang','antara','melalui','terhadap','bagi',
]);

function isProbablyIndonesian(str) {
  const words = str.toLowerCase().trim().split(/\s+/);
  // >1 kata + ada partikel/stopword Indonesia → hampir pasti ID
  if (words.length > 1 && words.some(w => ID_STOPWORDS.has(w))) return true;
  // 1 kata tapi cocok persis stopword umum (mis. "makan", "rumah")
  if (words.length === 1 && ID_STOPWORDS.has(words[0])) return true;
  return false;
}

function detectMode(query) {
  if (STATE.searchMode !== 'auto') return STATE.searchMode;
  if (!query) return 'auto';
  if (isProbablyHanzi(query)) return 'hanzi';
  // Cek Indonesia DULU sebelum pinyin, karena keduanya huruf latin
  if (isProbablyIndonesian(query)) return 'id';
  if (isProbablyPinyin(query)) return 'pinyin';
  return 'id';
}

/* ── NORMALISASI PINYIN (untuk matching) ──────────────────── */
function normalizePinyin(str) {
  // Sederhanakan diakritik pinyin → huruf latin biasa untuk matching
  return str.toLowerCase()
    .replace(/[āáǎà]/g, 'a').replace(/[ēéěè]/g, 'e')
    .replace(/[īíǐì]/g, 'i').replace(/[ōóǒò]/g, 'o')
    .replace(/[ūúǔù]/g, 'u').replace(/[ǖǘǚǜü]/g, 'u')
    .replace(/\d/g, ''); // hapus angka nada
}

/* Fix #1: konversi pinyin angka nada → diakritik (ma1 → mā, ni3 hao3 → nǐ hǎo) */
const TONE_MARKS = {
  a: ['a','ā','á','ǎ','à'], e: ['e','ē','é','ě','è'],
  i: ['i','ī','í','ǐ','ì'], o: ['o','ō','ó','ǒ','ò'],
  u: ['u','ū','ú','ǔ','ù'],
  'ü': ['ü','ǖ','ǘ','ǚ','ǜ'], v: ['ü','ǖ','ǘ','ǚ','ǜ'],
};

function numericSyllableToDiacritic(syll) {
  const m = syll.match(/^([^aeiouv\d]*)([aeiouv]+)([^aeiouv\d]*)([1-5])$/i);
  if (!m) return syll.replace(/[1-5]$/, '');
  let [, pre, vowels, post, toneStr] = m;
  const tone = parseInt(toneStr, 10);
  if (tone === 5 || tone === 0) return pre + vowels + post; // tanpa nada (netral)

  // Aturan penempatan tanda nada: a/e diutamakan, lalu o, lalu vokal terakhir (iu/ui dst)
  let target;
  if (vowels.includes('a')) target = 'a';
  else if (vowels.includes('e')) target = 'e';
  else if (vowels.includes('o')) target = 'o';
  else target = vowels[vowels.length - 1]; // i/u/ü tunggal atau gabungan iu/ui

  const targetKey = target === 'v' ? 'ü' : target;
  const idx = vowels.lastIndexOf(target);
  const marked = vowels.slice(0, idx) + TONE_MARKS[targetKey][tone] + vowels.slice(idx + 1);
  return pre + marked + post;
}

function numericToDiacritic(str) {
  return str.toLowerCase().trim().split(/\s+/)
    .map(numericSyllableToDiacritic).join(' ');
}

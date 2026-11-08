/* ═══════════════════════════════════════════════════════════════
   kamus/kamus-init.js — Mandarin Interaktif
   Inisialisasi DOMContentLoaded + keyboard shortcut -- dimuat PALING TERAKHIR
   Bagian dari modularisasi kamus.html. Dimuat sebagai <script src>
   biasa (bukan ES module) -- semua fungsi tetap di scope global,
   jadi urutan file lain relatif bebas KECUALI kamus-init.js yang
   WAJIB paling akhir.
   ═══════════════════════════════════════════════════════════════ */

'use strict';

/* ── INISIALISASI ──────────────────────────────────────────── */
document.addEventListener('DOMContentLoaded', () => {
  loadData().then(async () => {
    const handled = await handleUrlHash();
    if (!handled) restoreKamusLastState();
  });
  setupInfiniteScroll();
  setupResizeHandle();
  setupHanziColResize();

  // Event listener search input
  const input = $('search-input');
  const debouncedSearch = debounce((val) => doSearch(val), 300);

  input.addEventListener('input', (e) => {
    const val = e.target.value;
    $('search-clear').classList.toggle('visible', val.length > 0);
    debouncedSearch(val);
  });

  input.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') clearSearch();
  });
});

/* ── DEEP-LINK VIA URL HASH (Peta 11 Pilar, A.4) ──────────────
   Dipanggil sekali setelah loadData() selesai, SEBELUM restoreKamusLastState()
   -- kalau ada hash valid, itu yang menang (bukan state sesi terakhir).
   Format yang didukung (ditulis di link peta-bahasa.html / halaman lain):
     kamus.html#group=theme:angka        -> langsung tampilkan grup, panel tertutup
     kamus.html#group=khusus:kata_seru_netral
     kamus.html#opengroup=khusus         -> buka panel grup, رسلان pilih sendiri
     kamus.html#search=料理               -> langsung cari kata tertentu
   Return true kalau hash valid diproses (supaya kamus.html tidak dobel
   jalan restoreKamusLastState() sesudahnya). Tipe grup yang datanya dimuat
   lewat loadIndexFiles() (radical/stroke/theme/phonetic/akar/khusus) di-await
   dulu lewat STATE.indexFilesPromise -- kalau tidak, data belum siap saat
   halaman baru dibuka via deep-link (race condition, bukan masalah kalau
   رسلان klik dari sidebar sesudah halaman lama-lama terbuka). */
const GROUP_TYPES_NEED_INDEX = new Set(['radical', 'stroke', 'theme', 'phonetic', 'akar', 'khusus']);

async function handleUrlHash() {
  const raw = window.location.hash.slice(1);
  if (!raw) return false;

  let params;
  try { params = new URLSearchParams(raw); } catch (e) { return false; }

  const group     = params.get('group');
  const openGroup = params.get('opengroup');
  const search    = params.get('search');

  const type = group ? group.slice(0, group.indexOf(':')) : openGroup;
  if (type && GROUP_TYPES_NEED_INDEX.has(type) && STATE.indexFilesPromise) {
    await STATE.indexFilesPromise;
  }

  if (group) {
    const sep = group.indexOf(':');
    if (sep > -1) {
      const gType = group.slice(0, sep);
      const key   = group.slice(sep + 1);
      if (gType && key) {
        selectGroupItem(gType, key); // sudah menutup panel sendiri
        return true;
      }
    }
  }
  if (openGroup) {
    openGroupPanel(openGroup);
    return true;
  }
  if (search) {
    $('search-input').value = search;
    $('search-clear').classList.toggle('visible', search.length > 0);
    doSearch(search);
    return true;
  }
  return false;
}

/* ── KEYBOARD SHORTCUT ─────────────────────────────────────── */
document.addEventListener('keydown', (e) => {
  // '/' atau Ctrl+F → fokus search
  if ((e.key === '/' || (e.ctrlKey && e.key === 'f')) && !e.target.closest('input')) {
    e.preventDefault();
    $('search-input').focus();
    $('search-input').select();
  }
});

# -*- coding: utf-8 -*-
"""
xlsx_ke_html_mandiri.py

Mengonversi akar_kosakata.xlsx (hasil konversi_tabel_akar.py) menjadi SATU
file HTML yang berdiri sendiri -- semua data + CSS + JS ter-embed di
dalamnya, tanpa fetch/koneksi apa pun. Cocok dibuka langsung dari
penyimpanan HP (file://), tidak perlu server, tidak nyambung ke folder
mandarin_app/ sama sekali.

Cara pakai:
    python xlsx_ke_html_mandiri.py akar_kosakata.xlsx akar_kosakata.html
"""

import json
import sys

from openpyxl import load_workbook


def load_rows(xlsx_path):
    wb = load_workbook(xlsx_path, data_only=True)
    ws = wb.active
    rows = list(ws.iter_rows(min_row=2, values_only=True))
    return rows


def build_tree(rows):
    """
    Forward-fill kolom akar (1-3, di-merge di Excel -> None di baris
    lanjutan) lalu susun jadi list bersarang:
    [{ c: akar, py, ar, w: [ {k, py, ar, h, m, e, r}, ... ] }, ...]
    Key disingkat supaya ukuran file JSON tertanam lebih kecil.
    """
    tree = []
    current = None

    for row in rows:
        akar, py_akar, ar_akar, kata, py, ar, hsk, mnemonic, etimologi, radikal = (
            list(row) + [None] * (10 - len(row))
        )[:10]

        if akar:  # baris baru dgn akar terisi = mulai grup baru
            current = {
                "c": akar,
                "py": py_akar or "",
                "ar": ar_akar or "",
                "w": [],
            }
            tree.append(current)

        if current is None:
            continue  # jaga-jaga kalau baris pertama tidak terisi akar

        current["w"].append({
            "k": kata or "",
            "py": py or "",
            "ar": ar or "",
            "h": str(hsk) if hsk else "",
            "m": mnemonic or "",
            "e": etimologi or "",
            "r": radikal or "",
        })

    return tree


HTML_TEMPLATE = r"""<!DOCTYPE html>
<html lang="id">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1">
<title>🌱 Akar Kosakata — Mandarin Interaktif</title>
<style>
  :root{
    --bg:#15120d;
    --bg-card:#201b14;
    --bg-card2:#2a2318;
    --border:#3c3323;
    --gold:#d4b45f;
    --gold-dim:#a68b45;
    --gold-bg:rgba(212,180,95,0.12);
    --text-main:#f2ead9;
    --text-dim:#cbbfa4;
    --text-muted:#8c8067;
    --red:#d9736a;
    --radius:10px;
  }
  *{box-sizing:border-box;-webkit-tap-highlight-color:transparent}
  html,body{margin:0;padding:0;background:var(--bg);color:var(--text-main);
    font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,"Noto Sans",sans-serif;}
  body{padding-bottom:40px}

  header{
    position:sticky;top:0;z-index:20;
    background:linear-gradient(180deg, #1c1710 0%, #17130d 100%);
    border-bottom:1px solid var(--border);
    padding:14px 16px 12px;
  }
  header h1{
    margin:0;font-size:1.15rem;font-weight:700;color:var(--gold);
    display:flex;align-items:center;gap:8px;letter-spacing:0.01em;
  }
  header .sub{margin:3px 0 0;font-size:0.74rem;color:var(--text-muted)}

  .toolbar{
    position:sticky;top:56px;z-index:19;
    background:var(--bg);
    padding:10px 16px 8px;
    display:flex;gap:8px;flex-wrap:wrap;
    border-bottom:1px solid var(--border);
  }
  .search-box{
    flex:1;min-width:160px;
    background:var(--bg-card2);border:1px solid var(--border);
    border-radius:var(--radius);color:var(--text-main);
    padding:9px 12px;font-size:0.9rem;outline:none;
  }
  .search-box:focus{border-color:var(--gold-dim)}
  .search-box::placeholder{color:var(--text-muted)}

  .sort-group{display:flex;border:1px solid var(--border);border-radius:var(--radius);overflow:hidden;flex-shrink:0}
  .sort-btn{
    background:var(--bg-card2);color:var(--text-dim);border:none;
    padding:9px 12px;font-size:0.78rem;cursor:pointer;white-space:nowrap;
  }
  .sort-btn.active{background:var(--gold-bg);color:var(--gold)}

  .meta-row{
    padding:8px 16px;font-size:0.72rem;color:var(--text-muted);
  }

  #root-list{padding:6px 10px 10px}

  .root-card{
    background:var(--bg-card);
    border:1px solid var(--border);
    border-left:3px solid var(--gold-dim);
    border-radius:var(--radius);
    margin-bottom:8px;
    overflow:hidden;
  }
  .root-head{
    display:flex;align-items:center;gap:10px;
    padding:11px 12px;cursor:pointer;
  }
  .root-hanzi{font-size:1.4rem;color:var(--text-main);min-width:38px;text-align:center;font-weight:500}
  .root-info{flex:1;min-width:0}
  .root-pinyin{font-size:0.8rem;color:var(--gold-dim)}
  .root-arti{font-size:0.78rem;color:var(--text-dim);
    overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
  .root-count{
    font-size:0.72rem;color:var(--gold);background:var(--gold-bg);
    border-radius:20px;padding:3px 9px;flex-shrink:0;white-space:nowrap;
  }
  .root-arrow{color:var(--text-muted);font-size:0.7rem;transition:transform .15s;flex-shrink:0}
  .root-card.open .root-arrow{transform:rotate(180deg)}

  .root-body{display:none;border-top:1px solid var(--border)}
  .root-card.open .root-body{display:block}

  .word-row{
    padding:10px 12px;border-bottom:1px solid var(--border);
    cursor:pointer;
  }
  .word-row:last-child{border-bottom:none}
  .word-row:active{background:var(--bg-card2)}
  .word-top{display:flex;align-items:baseline;gap:8px;flex-wrap:wrap}
  .word-hanzi{font-size:1.1rem;color:var(--text-main)}
  .word-pinyin{font-size:0.78rem;color:var(--gold-dim)}
  .word-hsk{
    font-size:0.65rem;color:var(--text-muted);border:1px solid var(--border);
    border-radius:20px;padding:1px 7px;margin-left:auto;flex-shrink:0;
  }
  .word-arti{font-size:0.82rem;color:var(--text-dim);margin-top:2px}

  .word-detail{
    display:none;margin-top:8px;padding:9px 10px;
    background:var(--bg-card2);border-radius:8px;
    font-size:0.76rem;color:var(--text-dim);line-height:1.6;
  }
  .word-row.open .word-detail{display:block}
  .word-detail .dt-line{margin-bottom:5px}
  .word-detail .dt-line:last-child{margin-bottom:0}
  .word-detail b{color:var(--gold)}

  .empty{padding:40px 20px;text-align:center;color:var(--text-muted);font-size:0.85rem}

  footer{padding:18px 16px 30px;text-align:center;color:var(--text-muted);font-size:0.7rem}
</style>
</head>
<body>

<header>
  <h1>🌱 Akar Kosakata</h1>
  <p class="sub">__SUBTITLE__</p>
</header>

<div class="toolbar">
  <input type="text" class="search-box" id="q" placeholder="Cari akar, kata, pinyin, atau arti…" autocomplete="off">
  <div class="sort-group">
    <button class="sort-btn active" id="sort-count" onclick="setSort('count')">↓ Terbanyak</button>
    <button class="sort-btn" id="sort-az" onclick="setSort('az')">A-Z</button>
  </div>
</div>
<div class="meta-row" id="meta-row"></div>

<div id="root-list"></div>

<footer>Mandarin Interaktif — Akar Kosakata · dibuat offline, tidak menyimpan/mengirim data apa pun</footer>

<script>
const DATA = __DATA_JSON__;

let sortMode = 'count';
let query = '';

function esc(s){
  return String(s==null?'':s).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
}

function matchesQuery(root, q){
  if(!q) return true;
  if(root.c.includes(q)) return true;
  if((root.py||'').toLowerCase().includes(q)) return true;
  if((root.ar||'').toLowerCase().includes(q)) return true;
  return root.w.some(w =>
    w.k.includes(q) ||
    (w.py||'').toLowerCase().includes(q) ||
    (w.ar||'').toLowerCase().includes(q)
  );
}

function getSorted(){
  let list = DATA.filter(r => matchesQuery(r, query));
  if(sortMode === 'az'){
    list = list.slice().sort((a,b) => a.c.localeCompare(b.c, 'zh'));
  } else {
    list = list.slice().sort((a,b) => b.w.length - a.w.length);
  }
  return list;
}

function buildWordDetail(w){
  const parts = [];
  if(w.m) parts.push(`<div class="dt-line">💡 <b>Bantu Ingat:</b> ${esc(w.m)}</div>`);
  if(w.e) parts.push(`<div class="dt-line">📜 <b>Asal-Usul:</b> ${esc(w.e)}</div>`);
  if(w.r) parts.push(`<div class="dt-line">⺁ <b>Radikal:</b> ${esc(w.r)}</div>`);
  return parts.join('') || '<div class="dt-line" style="font-style:italic">Tidak ada catatan tambahan.</div>';
}

function buildWordRow(w, qLower){
  const hsk = w.h ? `<span class="word-hsk">HSK ${esc(w.h)}</span>` : '';
  return `
    <div class="word-row" onclick="this.classList.toggle('open')">
      <div class="word-top">
        <span class="word-hanzi">${esc(w.k)}</span>
        <span class="word-pinyin">${esc(w.py)}</span>
        ${hsk}
      </div>
      <div class="word-arti">${esc(w.ar)}</div>
      <div class="word-detail">${buildWordDetail(w)}</div>
    </div>`;
}

function buildRootCard(root){
  return `
    <div class="root-card" data-root="${esc(root.c)}">
      <div class="root-head" onclick="toggleRoot(this.closest('.root-card'))">
        <span class="root-hanzi">${esc(root.c)}</span>
        <div class="root-info">
          <div class="root-pinyin">${esc(root.py)}</div>
          <div class="root-arti">${esc(root.ar)}</div>
        </div>
        <span class="root-count">${root.w.length}</span>
        <span class="root-arrow">▼</span>
      </div>
      <div class="root-body"></div>
    </div>`;
}

function toggleRoot(card){
  const isOpen = card.classList.contains('open');
  if(isOpen){
    card.classList.remove('open');
    return;
  }
  // Render kata turunan LAZY -- baru dibangun saat pertama kali dibuka,
  // supaya render awal (1000+ kartu akar) tetap ringan di HP.
  const body = card.querySelector('.root-body');
  if(!body.dataset.rendered){
    const rootChar = card.dataset.root;
    const root = DATA.find(r => r.c === rootChar);
    body.innerHTML = root.w.map(w => buildWordRow(w)).join('');
    body.dataset.rendered = '1';
  }
  card.classList.add('open');
}

function render(){
  const list = getSorted();
  const container = document.getElementById('root-list');
  const meta = document.getElementById('meta-row');

  meta.textContent = query
    ? `${list.length.toLocaleString('id-ID')} akar cocok dengan pencarian`
    : `${list.length.toLocaleString('id-ID')} akar kosakata · ${DATA.reduce((a,r)=>a+r.w.length,0).toLocaleString('id-ID')} kata turunan`;

  if(!list.length){
    container.innerHTML = `<div class="empty">Tidak ada hasil untuk "${esc(query)}".</div>`;
    return;
  }

  container.innerHTML = list.map(buildRootCard).join('');
}

function setSort(mode){
  sortMode = mode;
  document.getElementById('sort-count').classList.toggle('active', mode === 'count');
  document.getElementById('sort-az').classList.toggle('active', mode === 'az');
  render();
}

let debounceTimer;
document.getElementById('q').addEventListener('input', (e) => {
  clearTimeout(debounceTimer);
  const val = e.target.value.trim().toLowerCase();
  debounceTimer = setTimeout(() => { query = val; render(); }, 150);
});

render();
</script>
</body>
</html>
"""


def main():
    if len(sys.argv) < 3:
        print("Cara pakai: python xlsx_ke_html_mandiri.py akar_kosakata.xlsx akar_kosakata.html")
        sys.exit(1)

    xlsx_path = sys.argv[1]
    out_path = sys.argv[2]

    rows = load_rows(xlsx_path)
    tree = build_tree(rows)

    total_kata = sum(len(r["w"]) for r in tree)
    subtitle = f"{len(tree):,} karakter akar · {total_kata:,} kata turunan".replace(",", ".")

    data_json = json.dumps(tree, ensure_ascii=False, separators=(",", ":"))
    # Jaga-jaga: cegah "</script>" di dalam data JSON menutup tag script lebih awal
    data_json = data_json.replace("</", "<\\/")

    html = HTML_TEMPLATE.replace("__DATA_JSON__", data_json).replace("__SUBTITLE__", subtitle)

    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)

    size_mb = len(html.encode("utf-8")) / 1024 / 1024
    print(f"Selesai. {len(tree)} akar, {total_kata} kata turunan -> {out_path} ({size_mb:.1f} MB)")


if __name__ == "__main__":
    main()

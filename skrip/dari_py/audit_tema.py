#!/usr/bin/env python3
# audit_tema.py
# Jalankan: python audit_tema.py
# Output  : C:\mandarin_app\data\LAPORAN_AUDIT_TEMA.txt

import json, os
from collections import defaultdict, Counter

DATA_DIR   = r"C:\mandarin_app\data"
IN_WORDS   = os.path.join(DATA_DIR, "app_words.json")
OUT_REPORT = os.path.join(DATA_DIR, "LAPORAN_AUDIT_TEMA.txt")

lines = []
def log(s=""):
    print(s)
    lines.append(str(s))

def sep(title=""):
    log("\n" + "═"*60)
    log(f"  {title}")
    log("═"*60)

with open(IN_WORDS, "r", encoding="utf-8") as f:
    words = json.load(f)

log(f"Total kata: {len(words):,}")

# ── 1. Cek tema per kata: berapa banyak tema yang dimiliki tiap kata ──
sep("Distribusi jumlah tema per kata")
tema_count = Counter()
for w in words:
    th = w.get("themes") or []
    tema_count[len(th)] += 1

for n, cnt in sorted(tema_count.items()):
    log(f"  {n:>3} tema : {cnt:>6,} kata")

# ── 2. Kata yang punya BANYAK tema (>10) — ini yang mencurigakan ──
sep("Kata dengan > 10 tema (sampel 30)")
banyak_tema = [(w['simplified'], len(w.get('themes',[])), w.get('themes',[])) 
               for w in words if len(w.get('themes',[]) or []) > 10]
banyak_tema.sort(key=lambda x: -x[1])
log(f"  Total kata dengan >10 tema: {len(banyak_tema):,}")
for simp, n, th in banyak_tema[:30]:
    log(f"  {simp:<6}  {n:>3} tema  HSK:{[w['hsk'] for w in words if w['simplified']==simp][0] if any(w['simplified']==simp for w in words) else '?'}")

# ── 3. Kata dasar (的了我是) ada di tema apa saja ──
sep("Tema yang dimiliki kata-kata dasar")
kata_dasar = ['的', '了', '我', '是', '你', '他', '和', '在', '不', '有']
for w in words:
    if w.get('simplified') in kata_dasar:
        log(f"  {w['simplified']:<4} HSK:{w.get('hsk','?')}  {len(w.get('themes',[]) or [])} tema: {w.get('themes',[])}")

# ── 4. Tema WARNA — isinya apa saja ──
sep("Isi tema 'warna' (semua kata)")
warna_words = [w for w in words if 'warna' in (w.get('themes') or [])]
log(f"  Total kata tema warna: {len(warna_words)}")
log(f"  Semua kata:")
for w in sorted(warna_words, key=lambda x: x.get('frequency', 99999)):
    log(f"    {w['simplified']:<8} {w.get('pinyin',''):<15} {(w.get('meanings_id') or [''])[0][:40]}")

# ── 5. Tema KELUARGA ──
sep("Isi tema 'keluarga' (semua kata)")
kel_words = [w for w in words if 'keluarga' in (w.get('themes') or [])]
log(f"  Total kata tema keluarga: {len(kel_words)}")
for w in sorted(kel_words, key=lambda x: x.get('frequency', 99999))[:40]:
    log(f"    {w['simplified']:<8} {w.get('pinyin',''):<15} {(w.get('meanings_id') or [''])[0][:40]}")

# ── 6. Tema HEWAN ──
sep("Isi tema 'hewan' (20 pertama)")
hewan_words = [w for w in words if 'hewan' in (w.get('themes') or [])]
log(f"  Total kata tema hewan: {len(hewan_words)}")
for w in sorted(hewan_words, key=lambda x: x.get('frequency', 99999))[:20]:
    log(f"    {w['simplified']:<8} {w.get('pinyin',''):<15} {(w.get('meanings_id') or [''])[0][:40]}")

# ── 7. Cek apakah ada kata yang punya POS tertentu di tema spesifik ──
sep("Analisis: apakah kata fungsi (partikel) ada di tema konkret?")
tema_konkret = ['warna', 'hewan', 'keluarga', 'makanan_minuman', 'buah', 'sayuran']
pos_fungsi   = ['u', 'p', 'c', 'e', 'd']  # partikel, preposisi, konjungsi, dll

for tema in tema_konkret:
    kata_fungsi_di_tema = [
        w for w in words
        if tema in (w.get('themes') or [])
        and any(p in (w.get('pos') or []) for p in pos_fungsi)
    ]
    log(f"  {tema:<25} {len(kata_fungsi_di_tema):>4} kata fungsi/partikel yang tidak relevan")
    for w in kata_fungsi_di_tema[:5]:
        log(f"    {w['simplified']:<6} pos:{w.get('pos')} pinyin:{w.get('pinyin')}")

# ── 8. Apakah themes adalah list unik atau ada duplikat? ──
sep("Cek duplikat tema dalam satu kata")
duplikat = 0
for w in words:
    th = w.get('themes') or []
    if len(th) != len(set(th)):
        duplikat += 1
log(f"  Kata dengan tema duplikat: {duplikat}")

# Simpan
with open(OUT_REPORT, "w", encoding="utf-8") as f:
    f.write("\n".join(lines))

print(f"\n✅ Selesai! Buka: {OUT_REPORT}")

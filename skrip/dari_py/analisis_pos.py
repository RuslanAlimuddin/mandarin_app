import json
from collections import Counter, defaultdict

with open('data/app_words.json', encoding='utf-8') as f:
    words = json.load(f)

def as_list(val):
    """Normalisasi field yang mungkin string tunggal atau list."""
    if val is None:
        return ['(kosong)']
    if isinstance(val, list):
        return val if val else ['(kosong)']
    return [val]

lines = []
def p(msg=''):
    print(msg)
    lines.append(str(msg))

p(f"Total kata: {len(words)}\n")

# 1. Nilai unik 'pos' (bisa list) -- hitung tiap tag individual
pos_counter = Counter()
for w in words:
    for tag in as_list(w.get('pos')):
        pos_counter[tag] += 1

p("=== Nilai unik 'pos' (kode, dihitung per tag individual) ===")
for pos, count in pos_counter.most_common():
    p(f"  {str(pos):15s} : {count}")

# 2. Nilai unik 'pos_id' (label Indonesia, mungkin juga list)
pos_id_counter = Counter()
for w in words:
    for tag in as_list(w.get('pos_id')):
        pos_id_counter[tag] += 1

p("\n=== Nilai unik 'pos_id' (label Indonesia) ===")
for pos_id, count in pos_id_counter.most_common():
    p(f"  {str(pos_id):20s} : {count}")

# 3. Cross-tab: pos x hsk level
p("\n=== pos x HSK level ===")
cross = defaultdict(Counter)
for w in words:
    hsk = w.get('hsk', '(kosong)')
    for tag in as_list(w.get('pos')):
        cross[tag][hsk] += 1

for pos in pos_counter:
    hsk_dist = cross[pos]
    hsk_str = ', '.join(f"HSK{k}:{v}" for k, v in sorted(hsk_dist.items(), key=lambda x: str(x[0])))
    p(f"  {str(pos):15s} -> {hsk_str}")

# 4. Contoh 2 entri per pos
p("\n=== Contoh 2 entri per pos ===")
examples = defaultdict(list)
for w in words:
    for tag in as_list(w.get('pos')):
        if len(examples[tag]) < 2:
            examples[tag].append(w)

for pos, exs in examples.items():
    p(f"\n-- pos: {pos} --")
    for ex in exs:
        p(f"  {ex.get('simplified')} | {ex.get('pinyin')} | {ex.get('meanings_id')} | themes={ex.get('themes')}")

# 5. Cari theme yang berkaitan dengan tempat/waktu
p("\n=== Cari theme yang mengandung kata 'tempat'/'waktu'/'lokasi'/'time' ===")
theme_counter = Counter()
for w in words:
    for t in as_list(w.get('themes')):
        theme_counter[t] += 1

relevant = {t: c for t, c in theme_counter.items()
            if any(k in str(t).lower() for k in ['tempat', 'waktu', 'lokasi', 'time', 'place'])}
for t, c in sorted(relevant.items(), key=lambda x: -x[1]):
    p(f"  {str(t):25s} : {c}")

# 6. Semua theme unik (top 40) -- buat referensi umum
p("\n=== Semua theme (top 40 by count) ===")
for t, c in theme_counter.most_common(40):
    p(f"  {str(t):25s} : {c}")

# Simpan semua output ke file
with open('analisis_pos_output.txt', 'w', encoding='utf-8') as out:
    out.write('\n'.join(lines))

print("\n\n✓ Selesai. Upload file 'analisis_pos_output.txt' ke chat.")

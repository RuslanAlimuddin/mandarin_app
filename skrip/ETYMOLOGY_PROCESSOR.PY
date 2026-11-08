import json

# 1. Cek isi synonym_antonym.json
sa = json.load(open('data/synonym_antonym.json', encoding='utf-8'))
if isinstance(sa, list):
    print(f"synonym_antonym.json: LIST, {len(sa)} entries")
    if len(sa) > 0:
        print(f"  Sample keys: {list(sa[0].keys()) if isinstance(sa[0], dict) else type(sa[0])}")
        print(f"  First 3: {sa[:3]}")
elif isinstance(sa, dict):
    print(f"synonym_antonym.json: DICT, {len(sa)} keys")
    keys = list(sa.keys())[:5]
    for k in keys:
        print(f"  '{k}': {sa[k]}")

# 2. Cek themes_extracted_v2.json structure
tv2 = json.load(open('data/themes_extracted_v2.json', encoding='utf-8'))
if isinstance(tv2, list):
    print(f"\nthemes_extracted_v2.json: LIST, {len(tv2)} entries")
    if len(tv2) > 0:
        print(f"  Sample: {tv2[0]}")
elif isinstance(tv2, dict):
    print(f"\nthemes_extracted_v2.json: DICT, {len(tv2)} keys")
    keys = list(tv2.keys())[:10]
    for k in keys:
        val = tv2[k]
        if isinstance(val, list):
            print(f"  '{k}': {len(val)} items, sample: {val[:3]}")
        else:
            print(f"  '{k}': {val}")

# 3. Cek index_theme.json structure  
it = json.load(open('data/index_theme.json', encoding='utf-8'))
if isinstance(it, dict):
    print(f"\nindex_theme.json: DICT, {len(it)} themes")
    keys = list(it.keys())[:15]
    for k in keys:
        print(f"  '{k}': {len(it[k])} words")

# 4. Cek unmatched_theme_words.json
um = json.load(open('data/unmatched_theme_words.json', encoding='utf-8'))
if isinstance(um, dict):
    print(f"\nunmatched_theme_words.json: DICT, {len(um)} themes")
    total_unmatched = sum(len(v) for v in um.values() if isinstance(v, list))
    print(f"  Total unmatched words: {total_unmatched}")
    keys = list(um.keys())[:5]
    for k in keys:
        print(f"  '{k}': {um[k][:5]}")
elif isinstance(um, list):
    print(f"\nunmatched_theme_words.json: LIST, {len(um)} entries")

# 5. Words yang punya themes - distribution
words = json.load(open('data/app_words.json', encoding='utf-8'))
from collections import Counter
theme_counts = Counter()
for w in words:
    for t in (w.get('themes') or []):
        theme_counts[t] += 1
print(f"\nTheme distribution in app_words ({len(theme_counts)} unique themes):")
for theme, count in theme_counts.most_common(30):
    print(f"  {theme}: {count}")
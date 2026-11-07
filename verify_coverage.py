import json, sys

PUNCT = set('，。！？、；：""''（）《》…—·,.!?;:()[]"\' \n\t“”0123456789')

def tokenize_against_glossary(text, glossary_cn_set, maxlen=8):
    """
    Greedy longest-match, tapi kamusnya adalah glossary MILIK bacaan itu
    sendiri (bukan app_words.json global). Ini yang persis dipakai
    graded-reader.html untuk highlight & tooltip kata.
    """
    tokens = []
    i = 0
    n = len(text)
    while i < n:
        ch = text[i]
        if ch in PUNCT:
            i += 1
            continue
        matched = None
        for L in range(min(maxlen, n - i), 0, -1):
            cand = text[i:i+L]
            if cand in glossary_cn_set:
                matched = cand
                break
        if matched:
            tokens.append(matched)
            i += len(matched)
        else:
            tokens.append(text[i])
            i += 1
    return tokens

def verify_passage(passage):
    glossary_cn = set(g['cn'] for g in passage['glossary'])
    if passage.get('type') == 'percakapan':
        # Percakapan: gabungkan semua baris dialog jadi satu teks buat dicek
        text = ''.join(t['cn'] for t in passage['turns'])
    else:
        text = passage['text']
    tokens = tokenize_against_glossary(text, glossary_cn)
    missing = [tok for tok in tokens if tok not in PUNCT and tok not in glossary_cn]
    return missing, tokens

def verify_file(path):
    with open(path, encoding='utf-8') as f:
        data = json.load(f)
    passages = data['passages'] if isinstance(data, dict) else data
    all_ok = True
    for p in passages:
        missing, tokens = verify_passage(p)
        if missing:
            all_ok = False
            print(f"[GAGAL] {p['id']}: karakter tidak ke-cover glossary -> {missing}")
        else:
            print(f"[OK] {p['id']} ({len(tokens)} token, {len(p['glossary'])} entri glossary)")
    return all_ok

if __name__ == '__main__':
    # Pemakaian: python verify_coverage.py <file_bacaan.json>
    if len(sys.argv) < 2:
        print("Pemakaian: python verify_coverage.py <file_bacaan.json>")
        sys.exit(1)
    path = sys.argv[1]
    ok = verify_file(path)
    print('\nSEMUA OK' if ok else '\nADA YANG GAGAL — perbaiki dulu sebelum diserahkan')

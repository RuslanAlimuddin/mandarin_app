"""
intip_synonym_antonym.py — READ-ONLY, tidak mengubah file apapun.

Tujuan (E.0.2): cek struktur PERSIS data/synonym_antonym.json, lalu
bandingkan dgn field synonyms/antonyms yang sudah ada di app_words.json
(116-170 entri) -- supaya ketahuan:
  1. Apakah synonym_antonym.json beneran punya info LEBIH (pinyin per
     pasangan, note_id/catatan nuansa) yg tidak ada di app_words.json.
  2. Berapa kata yg ADA di synonym_antonym.json tapi field
     synonyms/antonyms-nya di app_words.json masih KOSONG (kandidat
     merge paling jelas untungnya).
  3. Berapa kata yg ADA DI KEDUANYA -- apakah isinya beda (utk tau versi
     mana yg lebih baru/lengkap).
  4. Field note_id itu string bebas atau lookup ke sesuatu (mis. index
     nuance_pairs.json)?

Cara pakai:
    cd C:\\mandarin_app
    python intip_synonym_antonym.py
"""

import json
import os

PATH_SYN = os.path.join("data", "synonym_antonym.json")
PATH_WORDS = os.path.join("data", "app_words.json")


def describe(value):
    if isinstance(value, list):
        return f"list[len={len(value)}]  item_types={sorted(set(type(x).__name__ for x in value))}"
    if isinstance(value, dict):
        return f"dict  keys={sorted(value.keys())}"
    if isinstance(value, str):
        return f"str[len={len(value)}]"
    return type(value).__name__


def main():
    with open(PATH_SYN, "r", encoding="utf-8") as f:
        syn_data = json.load(f)
    with open(PATH_WORDS, "r", encoding="utf-8") as f:
        words_data = json.load(f)

    print(f"Tipe top-level synonym_antonym.json: {type(syn_data).__name__}")
    if isinstance(syn_data, dict):
        print(f"Jumlah key top-level: {len(syn_data)}")
        sample_keys = list(syn_data.keys())[:3]
        print(f"Contoh key: {sample_keys}")
        entries = list(syn_data.values())
    else:
        entries = syn_data
    print(f"Jumlah entri total: {len(entries)}")

    print("\n" + "=" * 70)
    print("3 CONTOH ENTRI LENGKAP (mentah, apa adanya)")
    print("=" * 70)
    for e in entries[:3]:
        print(json.dumps(e, ensure_ascii=False, indent=2)[:800])
        print("---")

    print("\n" + "=" * 70)
    print("SKEMA: field apa saja yg muncul di level entri & di dalam syn/ant item")
    print("=" * 70)
    top_fields = set()
    syn_item_fields = set()
    ant_item_fields = set()
    for e in entries:
        if isinstance(e, dict):
            top_fields.update(e.keys())
            for item in e.get("synonyms", []) or []:
                if isinstance(item, dict):
                    syn_item_fields.update(item.keys())
            for item in e.get("antonyms", []) or []:
                if isinstance(item, dict):
                    ant_item_fields.update(item.keys())
    print(f"Field top-level per entri: {sorted(top_fields)}")
    print(f"Field di dalam tiap item synonyms[]: {sorted(syn_item_fields)}")
    print(f"Field di dalam tiap item antonyms[]: {sorted(ant_item_fields)}")

    # Cek apakah note_id berisi teks langsung atau semacam ID/kode
    print("\n" + "=" * 70)
    print("5 CONTOH nilai note_id (cek: teks bebas / kode ID / kosong)")
    print("=" * 70)
    shown = 0
    for e in entries:
        if not isinstance(e, dict):
            continue
        for item in (e.get("synonyms") or []) + (e.get("antonyms") or []):
            if isinstance(item, dict) and item.get("note_id"):
                print(f"  word={e.get('word')!r}  ->  note_id={item['note_id']!r}")
                shown += 1
                if shown >= 5:
                    break
        if shown >= 5:
            break
    if shown == 0:
        print("  (note_id tidak pernah terisi di 5 entri pertama yg dicek -- perlu scan penuh)")

    # ── Bandingkan cakupan dengan app_words.json ──
    print("\n" + "=" * 70)
    print("PERBANDINGAN CAKUPAN dgn app_words.json")
    print("=" * 70)

    # index app_words by simplified/id
    words_by_key = {}
    for w in words_data:
        key = w.get("simplified") or w.get("id")
        if key:
            words_by_key[key] = w

    syn_words = set()
    for e in entries:
        if isinstance(e, dict) and e.get("word"):
            syn_words.add(e["word"])

    print(f"Total kata unik di synonym_antonym.json: {len(syn_words)}")

    only_in_syn_file = 0       # ada di syn file, tidak ada entrinya sama sekali di app_words
    in_both_but_empty = 0      # ada di app_words, tapi field synonyms/antonyms kosong -> kandidat merge jelas
    in_both_and_filled = 0     # ada di app_words DAN field synonyms/antonyms sudah terisi -> perlu cek beda
    diff_content_sample = []

    for sw in syn_words:
        w = words_by_key.get(sw)
        if not w:
            only_in_syn_file += 1
            continue
        existing_syn = w.get("synonyms") or []
        existing_ant = w.get("antonyms") or []
        if not existing_syn and not existing_ant:
            in_both_but_empty += 1
        else:
            in_both_and_filled += 1
            if len(diff_content_sample) < 5:
                diff_content_sample.append((sw, existing_syn, existing_ant))

    print(f"Kata di synonym_antonym.json TAPI TIDAK ADA entrinya di app_words.json: {only_in_syn_file}")
    print(f"Kata ADA DI KEDUANYA, tapi synonyms/antonyms di app_words.json masih KOSONG (kandidat merge jelas): {in_both_but_empty}")
    print(f"Kata ADA DI KEDUANYA, dan app_words.json SUDAH ADA isinya (perlu cek konflik/duplikat): {in_both_and_filled}")

    if diff_content_sample:
        print("\nContoh 5 kata yg 'sudah ada isinya' di app_words.json (utk cek apa isinya sama/beda):")
        for sw, es, ea in diff_content_sample:
            print(f"  {sw}: app_words.synonyms={es}  app_words.antonyms={ea}")


if __name__ == "__main__":
    main()

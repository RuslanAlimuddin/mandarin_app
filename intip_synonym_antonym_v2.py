"""
intip_synonym_antonym_v2.py — READ-ONLY, tidak mengubah file apapun.

Perbaikan dari versi 1: struktur asli synonym_antonym.json ternyata:
    {
      "synonyms": { "看": {word, pinyin, meaning_id, hsk, synonyms:[...]}, ... },
      "antonyms": { "大": {word, pinyin, meaning_id, hsk, antonyms:[...]}, ... },
      "combined": { "哭": {synonyms:[...], antonyms:[...]}, ... }
    }
-- 3 kunci top-level, BUKAN flat per-kata. "combined" tampaknya union dari
2 dict lain, tapi TANPA field word/pinyin/meaning_id/hsk di level kata
(cuma array synonyms/antonyms). Script ini gali level yang benar & cek:
  1. Apakah "combined" itu superset lengkap dari "synonyms" + "antonyms"
     (union), atau ada kata yg hilang.
  2. note_id -- benaran teks catatan nuansa bebas, bukan kode/ID.
  3. Cakupan vs app_words.json (yg mana kandidat merge jelas: field
     synonyms/antonyms di app_words.json masih kosong tapi ada datanya
     di sini).
  4. Konflik: kata yg app_words.json-nya SUDAH ada isi synonyms/antonyms,
     apakah sama atau beda dgn synonym_antonym.json.

Cara pakai:
    cd C:\\mandarin_app
    python intip_synonym_antonym_v2.py
"""

import json
import os

PATH_SYN = os.path.join("data", "synonym_antonym.json")
PATH_WORDS = os.path.join("data", "app_words.json")


def main():
    with open(PATH_SYN, "r", encoding="utf-8") as f:
        raw = json.load(f)
    with open(PATH_WORDS, "r", encoding="utf-8") as f:
        words_data = json.load(f)

    print("Kunci top-level:", list(raw.keys()))
    d_syn = raw.get("synonyms", {})
    d_ant = raw.get("antonyms", {})
    d_combined = raw.get("combined", {})

    print(f"Jumlah kata di 'synonyms': {len(d_syn)}")
    print(f"Jumlah kata di 'antonyms': {len(d_ant)}")
    print(f"Jumlah kata di 'combined': {len(d_combined)}")

    union_syn_ant = set(d_syn.keys()) | set(d_ant.keys())
    print(f"Union kata (synonyms ∪ antonyms): {len(union_syn_ant)}")
    only_in_combined = set(d_combined.keys()) - union_syn_ant
    missing_from_combined = union_syn_ant - set(d_combined.keys())
    print(f"Kata yg ADA di 'combined' tapi TIDAK di union syn/ant: {len(only_in_combined)}  {list(only_in_combined)[:10]}")
    print(f"Kata yg ADA di union syn/ant tapi HILANG dari 'combined': {len(missing_from_combined)}  {list(missing_from_combined)[:10]}")

    # Cek isi combined utk 1 kata yg juga ada di d_syn (bandingkan detail)
    print("\n" + "=" * 70)
    print("Bandingkan 1 kata yg sama di 'synonyms' vs 'combined' (cek konsistensi)")
    print("=" * 70)
    sample_word = next(iter(d_syn.keys()))
    print(f"Kata contoh: {sample_word!r}")
    print("Di 'synonyms':", json.dumps(d_syn[sample_word], ensure_ascii=False, indent=2))
    print("Di 'combined':", json.dumps(d_combined.get(sample_word, "TIDAK ADA"), ensure_ascii=False, indent=2))

    # Cek isi note_id yg sebenarnya (di dalam array synonyms/antonyms tiap kata)
    print("\n" + "=" * 70)
    print("10 contoh note_id (dari 'combined', gabungan synonyms+antonyms)")
    print("=" * 70)
    shown = 0
    for word, entry in d_combined.items():
        for item in (entry.get("synonyms") or []) + (entry.get("antonyms") or []):
            print(f"  {word} -> {item.get('word')}: note_id={item.get('note_id')!r}")
            shown += 1
            if shown >= 10:
                break
        if shown >= 10:
            break

    # ── Bandingkan cakupan dgn app_words.json, pakai 'combined' sbg sumber utama ──
    print("\n" + "=" * 70)
    print("PERBANDINGAN CAKUPAN 'combined' vs app_words.json")
    print("=" * 70)

    words_by_key = {}
    for w in words_data:
        key = w.get("simplified") or w.get("id")
        if key:
            words_by_key[key] = w

    not_found_in_app_words = []
    empty_in_app_words = []   # kandidat merge jelas
    filled_in_app_words = []  # perlu cek konflik

    for word, entry in d_combined.items():
        w = words_by_key.get(word)
        if not w:
            not_found_in_app_words.append(word)
            continue
        existing_syn = w.get("synonyms") or []
        existing_ant = w.get("antonyms") or []
        if not existing_syn and not existing_ant:
            empty_in_app_words.append(word)
        else:
            filled_in_app_words.append((word, existing_syn, existing_ant, entry.get("synonyms") or [], entry.get("antonyms") or []))

    print(f"Kata di 'combined' TAPI entrinya TIDAK ADA di app_words.json: {len(not_found_in_app_words)}")
    if not_found_in_app_words:
        print(f"  contoh: {not_found_in_app_words[:10]}")

    print(f"Kata ADA di app_words.json, synonyms/antonyms MASIH KOSONG (kandidat merge jelas): {len(empty_in_app_words)}")
    print(f"  contoh: {empty_in_app_words[:15]}")

    print(f"Kata ADA di app_words.json, synonyms/antonyms SUDAH TERISI (perlu cek konflik): {len(filled_in_app_words)}")
    for word, es, ea, ns, na in filled_in_app_words[:5]:
        print(f"\n  kata: {word}")
        print(f"    app_words.json  -> synonyms={es}  antonyms={ea}")
        print(f"    synonym_antonym.json -> synonyms={[i.get('word') for i in ns]}  antonyms={[i.get('word') for i in na]}")

    # Total kata unik gabungan (untuk gambaran skala merge)
    print("\n" + "=" * 70)
    print("RINGKASAN SKALA")
    print("=" * 70)
    print(f"Total kata unik di synonym_antonym.json (union semua): {len(union_syn_ant | set(d_combined.keys()))}")
    print(f"Total kata di app_words.json yg synonyms/antonyms-nya SUDAH terisi (sebelum merge): "
          f"{sum(1 for w in words_data if w.get('synonyms') or w.get('antonyms'))}")


if __name__ == "__main__":
    main()

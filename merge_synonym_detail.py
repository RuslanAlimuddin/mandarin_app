"""
merge_synonym_detail.py — E.0.2

Tambah field BARU `synonyms_detail` / `antonyms_detail` ke entri di
app_words.json, diisi dari data/synonym_antonym.json (kunci "combined",
134 kata). Field LAMA `synonyms`/`antonyms` (array-of-string) TIDAK
disentuh sama sekali -- demi keamanan flashcard-games.js/
flashcard-session.js/flashcard-decks.js yang sudah pakai field itu.

Field baru hanya array-of-object {word, pinyin, note_id}, dipakai
kamus-detail.js utk nampilin catatan nuansa (mis. kenapa 快 vs 迅速
beda pemakaian) di chip sinonim/antonim, TANPA ubah data lama.

Cara pakai:
    cd C:\\mandarin_app
    python merge_synonym_detail.py --dry-run     # cek dulu, tidak nulis apapun
    python merge_synonym_detail.py                # baru benerin apply

Selalu checkpoint.py save SETELAH apply, sebelum lanjut sesi berikutnya.
"""

import json
import os
import sys
import shutil
from datetime import datetime

PATH_WORDS = os.path.join("data", "app_words.json")
PATH_SYN = os.path.join("data", "synonym_antonym.json")

DRY_RUN = "--dry-run" in sys.argv


def main():
    with open(PATH_WORDS, "r", encoding="utf-8") as f:
        words = json.load(f)
    with open(PATH_SYN, "r", encoding="utf-8") as f:
        syn_raw = json.load(f)

    combined = syn_raw.get("combined", {})
    print(f"Kata di 'combined': {len(combined)}")

    words_by_key = {}
    for w in words:
        key = w.get("simplified") or w.get("id")
        if key:
            words_by_key[key] = w

    updated = 0
    not_found = []
    already_had_detail = 0
    sample_changes = []

    for word, entry in combined.items():
        w = words_by_key.get(word)
        if not w:
            not_found.append(word)
            continue

        syn_list = entry.get("synonyms") or []
        ant_list = entry.get("antonyms") or []

        new_syn_detail = [
            {"word": i.get("word"), "pinyin": i.get("pinyin", ""), "note_id": i.get("note_id", "")}
            for i in syn_list if i.get("word")
        ]
        new_ant_detail = [
            {"word": i.get("word"), "pinyin": i.get("pinyin", ""), "note_id": i.get("note_id", "")}
            for i in ant_list if i.get("word")
        ]

        if "synonyms_detail" in w or "antonyms_detail" in w:
            already_had_detail += 1

        if new_syn_detail:
            w["synonyms_detail"] = new_syn_detail
        if new_ant_detail:
            w["antonyms_detail"] = new_ant_detail

        if new_syn_detail or new_ant_detail:
            updated += 1
            if len(sample_changes) < 5:
                sample_changes.append((word, new_syn_detail, new_ant_detail))

    print(f"Kata di 'combined' TAPI tidak ketemu entrinya di app_words.json: {len(not_found)}  {not_found}")
    print(f"Kata yg SUDAH punya synonyms_detail/antonyms_detail sebelumnya (bakal ditimpa): {already_had_detail}")
    print(f"Total entri app_words.json yg akan di-update: {updated}")

    print("\n--- Contoh 5 perubahan ---")
    for word, sd, ad in sample_changes:
        print(f"\n{word}:")
        print(f"  synonyms_detail = {json.dumps(sd, ensure_ascii=False)}")
        print(f"  antonyms_detail = {json.dumps(ad, ensure_ascii=False)}")

    # Verifikasi field LAMA tidak berubah sama sekali (sanity check keamanan)
    print("\n--- Sanity check: field lama 'synonyms'/'antonyms' TIDAK diubah ---")
    sample_word = next(iter(combined.keys()))
    w = words_by_key.get(sample_word)
    if w:
        print(f"{sample_word}: synonyms(lama)={w.get('synonyms')}  antonyms(lama)={w.get('antonyms')}")
        print("(bandingkan manual dgn app_words.json SEBELUM script ini dijalankan -- harus identik)")

    if DRY_RUN:
        print("\n[DRY RUN] Tidak ada file yang ditulis. Jalankan tanpa --dry-run untuk apply.")
        return

    # Backup dulu sebelum tulis (selain checkpoint.py, jaga-jaga)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = PATH_WORDS + f".bak_before_merge_synonym_detail_{ts}"
    shutil.copy2(PATH_WORDS, backup_path)
    print(f"\nBackup dibuat: {backup_path}")

    with open(PATH_WORDS, "w", encoding="utf-8") as f:
        json.dump(words, f, ensure_ascii=False, indent=2)

    print(f"\n[APPLIED] {updated} entri app_words.json sudah diupdate dgn synonyms_detail/antonyms_detail.")
    print("Jangan lupa: jalankan checkpoint.py save setelah ini.")


if __name__ == "__main__":
    main()

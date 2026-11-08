"""
verifikasi_hasil_tier_a.py — READ-ONLY.

Verifikasi KETAT: pastikan hasil_tier_a.json TIDAK mengubah/menambah/
menghapus kata apapun di synonyms/antonyms dibanding app_words.json ASLI
-- AI cuma boleh menambah pinyin+note_id, TIDAK BOLEH mengubah relasi.

Cara pakai (setelah hasil_tier_a.json disimpan di C:\\mandarin_app\\):
    cd C:\\mandarin_app
    python verifikasi_hasil_tier_a.py
"""

import json
import os

PATH_WORDS = os.path.join("data", "app_words.json")
PATH_HASIL = "hasil_tier_a.json"


def main():
    with open(PATH_WORDS, "r", encoding="utf-8") as f:
        words = json.load(f)
    with open(PATH_HASIL, "r", encoding="utf-8") as f:
        hasil = json.load(f)

    words_by_key = {w.get("simplified"): w for w in words}

    print(f"Total entri hasil_tier_a.json: {len(hasil)}")
    all_ok = True

    for item in hasil:
        simp = item.get("simplified")
        orig = words_by_key.get(simp)
        if not orig:
            print(f"[MASALAH] {simp}: TIDAK DITEMUKAN di app_words.json!")
            all_ok = False
            continue

        orig_syn = orig.get("synonyms") or []
        orig_ant = orig.get("antonyms") or []
        ai_syn = [w.get("word") for w in item.get("synonyms", [])]
        ai_ant = [w.get("word") for w in item.get("antonyms", [])]

        syn_ok = (ai_syn == orig_syn)
        ant_ok = (ai_ant == orig_ant)

        # cek kelengkapan pinyin/note_id
        missing_detail = []
        for lst_name, lst in [("synonyms", item.get("synonyms", [])), ("antonyms", item.get("antonyms", []))]:
            for w in lst:
                if not w.get("pinyin") or not w.get("note_id"):
                    missing_detail.append(f"{lst_name}:{w.get('word')}")

        status = "OK" if (syn_ok and ant_ok and not missing_detail) else "MASALAH"
        if status == "MASALAH":
            all_ok = False

        print(f"[{status}] {simp}")
        if not syn_ok:
            print(f"    synonyms asli={orig_syn}")
            print(f"    synonyms AI  ={ai_syn}")
        if not ant_ok:
            print(f"    antonyms asli={orig_ant}")
            print(f"    antonyms AI  ={ai_ant}")
        if missing_detail:
            print(f"    field kosong: {missing_detail}")

    print("\n" + "=" * 60)
    if all_ok:
        print(f"SEMUA {len(hasil)} ENTRI LOLOS VERIFIKASI -- aman untuk apply.")
    else:
        print("ADA MASALAH -- JANGAN apply dulu, perbaiki manual atau minta AI ulang kata bermasalah.")


if __name__ == "__main__":
    main()

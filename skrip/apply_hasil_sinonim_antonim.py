"""
apply_hasil_sinonim_antonim.py — E.0.2b, langkah APPLY final.

v3.2: tambahan normalize_relation_items() -- beberapa AI eksternal kadang
mengembalikan item synonyms/antonyms berupa STRING POLOS (mis. "海草")
alih-alih dict {"word":..., "pinyin":..., "note_id":...}, yg sebelumnya
menyebabkan AttributeError di strip_self_reference() dan terpaksa
diperbaiki manual (dikosongkan) oleh رسلان saat ditemukan. Sekarang
dinormalisasi otomatis jadi dict minimal (pinyin/note_id kosong) SEBELUM
diproses lebih lanjut -- relasi yg ternyata valid (bukan self-reference)
jadi tetap tersimpan alih-alih hilang percuma. Diterapkan di TIER A
(sebelum verifikasi ulang) dan TIER B (sebelum filter self-reference).

v3.1: tambahan pencatatan "_tb_empty_streak" -- tiap kali sebuah kata Tier B
hasilnya kosong (synonyms DAN antonyms sama2 kosong dari AI setelah filter
self-reference), counter ini ditambah 1. Kalau sebuah kata BERHASIL dapat
relasi (syn atau ant terisi), counter ini dihapus/reset. Dipakai oleh
generate_prompt_sinonim_antonim_v3.py utk mengecualikan kata yg sudah gagal
berulang kali dari pool Tier B ke depannya (lihat TIER_B_EMPTY_THRESHOLD di
sana) -- supaya kata spt angka/partikel yg memang tidak akan pernah dapat
relasi tidak terus membebani tiap batch 100-kata.

Gabungkan hasil_tier_a.json + hasil_tier_b_pilot.json ke app_words.json:

  TIER A (20 kata): relasi SUDAH ADA di field lama (synonyms/antonyms,
  array-of-string) -- TIDAK disentuh. Cuma isi synonyms_detail/
  antonyms_detail (pinyin+note_id), pola sama persis spt merge_synonym_detail.py
  sebelumnya (E.0.2). Sebelum apply, diverifikasi ULANG kata-katanya identik
  dgn field lama (jaga-jaga, walau sudah lolos verifikasi terpisah).

  TIER B (100 kata, minus self-reference dibuang): relasi BARU, field lama
  (synonyms/antonyms) MASIH KOSONG utk kata-kata ini -- jadi diisi
  DUA-DUANYA: field lama (array-of-string, spy otomatis kepakai
  flashcard-decks.js/games.js/session.js yg sudah baca field itu) DAN
  field detail (pinyin+note_id, dipakai kamus-detail.js).

Filter otomatis: buang item synonym/antonym yg word == simplified kata itu
sendiri (self-reference).

Cara pakai:
    cd C:\\mandarin_app
    python apply_hasil_sinonim_antonim.py --dry-run
    python apply_hasil_sinonim_antonim.py
"""

import json
import os
import sys
import shutil
from datetime import datetime

PATH_WORDS = os.path.join("data", "app_words.json")
PATH_HASIL_A = "hasil_tier_a.json"
PATH_HASIL_B = "hasil_tier_b_pilot.json"

DRY_RUN = "--dry-run" in sys.argv


def normalize_relation_items(items):
    """v3.2: beberapa AI eksternal kadang mengembalikan item synonyms/antonyms
    berupa STRING POLOS (mis. "海草") alih-alih dict standar
    {"word":..., "pinyin":..., "note_id":...} -- ditemukan 7x pada sesi
    pilot terakhir (kata "奶牛", "纪实", "继父", "成问题", "功臣" x2, "海藻"),
    dan sebelumnya menyebabkan AttributeError di strip_self_reference().

    Daripada membuang info itu begitu saja (beberapa di antaranya adalah
    relasi VALID, bukan cuma self-reference kebetulan -- mis. 海藻→海草),
    di sini kita normalisasi jadi dict minimal dulu (pinyin/note_id kosong).
    Self-reference asli (spt 奶牛→奶牛) tetap akan terfilter otomatis oleh
    strip_self_reference() setelah fungsi ini dipanggil.
    """
    normalized = []
    for it in items:
        if isinstance(it, dict):
            normalized.append(it)
        elif isinstance(it, str):
            normalized.append({"word": it, "pinyin": "", "note_id": ""})
        # tipe lain (angka, None, dst) sengaja dilewati/dibuang -- tidak
        # masuk akal sbg relasi kata.
    return normalized


def strip_self_reference(items, simplified):
    cleaned = []
    removed = []
    for it in items:
        if it.get("word") == simplified:
            removed.append(it)
        else:
            cleaned.append(it)
    return cleaned, removed


def main():
    with open(PATH_WORDS, "r", encoding="utf-8") as f:
        words = json.load(f)
    with open(PATH_HASIL_A, "r", encoding="utf-8") as f:
        hasil_a = json.load(f)
    with open(PATH_HASIL_B, "r", encoding="utf-8") as f:
        hasil_b = json.load(f)

    words_by_key = {w.get("simplified"): w for w in words}

    # ── TIER A ──
    print("=" * 70)
    print("TIER A (verifikasi ulang + apply synonyms_detail/antonyms_detail)")
    print("=" * 70)
    tier_a_applied = 0
    tier_a_failed = []

    for item in hasil_a:
        simp = item.get("simplified")
        w = words_by_key.get(simp)
        if not w:
            tier_a_failed.append(f"{simp}: tidak ditemukan di app_words.json")
            continue

        raw_syn = normalize_relation_items(item.get("synonyms", []))
        raw_ant = normalize_relation_items(item.get("antonyms", []))

        orig_syn = w.get("synonyms") or []
        orig_ant = w.get("antonyms") or []
        ai_syn = [x.get("word") for x in raw_syn]
        ai_ant = [x.get("word") for x in raw_ant]

        if ai_syn != orig_syn or ai_ant != orig_ant:
            tier_a_failed.append(f"{simp}: relasi TIDAK COCOK dgn data asli (dilewati demi keamanan)")
            continue

        syn_detail, _ = strip_self_reference(raw_syn, simp)
        ant_detail, _ = strip_self_reference(raw_ant, simp)

        if syn_detail:
            w["synonyms_detail"] = [
                {"word": x["word"], "pinyin": x.get("pinyin", ""), "note_id": x.get("note_id", "")}
                for x in syn_detail
            ]
        if ant_detail:
            w["antonyms_detail"] = [
                {"word": x["word"], "pinyin": x.get("pinyin", ""), "note_id": x.get("note_id", "")}
                for x in ant_detail
            ]
        tier_a_applied += 1

    print(f"Berhasil diverifikasi & akan diterapkan: {tier_a_applied}/{len(hasil_a)}")
    if tier_a_failed:
        print("GAGAL verifikasi (TIDAK diterapkan):")
        for f_ in tier_a_failed:
            print(f"  - {f_}")

    # ── TIER B ──
    print("\n" + "=" * 70)
    print("TIER B (relasi BARU -- isi field lama + detail, filter self-reference)")
    print("=" * 70)
    tier_b_applied = 0
    tier_b_not_found = []
    tier_b_already_filled = []
    self_ref_removed = []
    empty_streak_incremented = []
    empty_streak_reached_threshold = []
    sample_changes = []

    for item in hasil_b:
        simp = item.get("simplified")
        w = words_by_key.get(simp)
        if not w:
            tier_b_not_found.append(simp)
            continue

        if w.get("synonyms") or w.get("antonyms"):
            # Sudah keburu terisi (mis. dari sesi lain) -- skip demi keamanan,
            # jangan menimpa data yg mungkin sudah ada.
            tier_b_already_filled.append(simp)
            continue

        raw_syn = normalize_relation_items(item.get("synonyms", []))
        raw_ant = normalize_relation_items(item.get("antonyms", []))
        syn_items, syn_removed = strip_self_reference(raw_syn, simp)
        ant_items, ant_removed = strip_self_reference(raw_ant, simp)
        if syn_removed or ant_removed:
            self_ref_removed.append((simp, syn_removed + ant_removed))

        syn_words = [x["word"] for x in syn_items]
        ant_words = [x["word"] for x in ant_items]

        if syn_words or ant_words:
            # Berhasil dapat relasi -- reset counter gagal kalau ada
            if "_tb_empty_streak" in w:
                del w["_tb_empty_streak"]

            # Field LAMA (array-of-string) -- spy otomatis kepakai flashcard
            if syn_words:
                w["synonyms"] = syn_words
            if ant_words:
                w["antonyms"] = ant_words

            # Field detail (pinyin+note_id) -- dipakai kamus-detail.js
            if syn_items:
                w["synonyms_detail"] = [
                    {"word": x["word"], "pinyin": x.get("pinyin", ""), "note_id": x.get("note_id", "")}
                    for x in syn_items
                ]
            if ant_items:
                w["antonyms_detail"] = [
                    {"word": x["word"], "pinyin": x.get("pinyin", ""), "note_id": x.get("note_id", "")}
                    for x in ant_items
                ]

            tier_b_applied += 1
            if len(sample_changes) < 5:
                sample_changes.append((simp, syn_words, ant_words))
        else:
            # Kosong dari AI (baik memang tidak ada relasi, maupun cuma
            # self-reference yg dibuang) -- catat sebagai satu percobaan gagal
            new_streak = w.get("_tb_empty_streak", 0) + 1
            w["_tb_empty_streak"] = new_streak
            empty_streak_incremented.append((simp, new_streak))
            if new_streak >= 3:
                empty_streak_reached_threshold.append(simp)

    print(f"Berhasil diterapkan (punya minimal 1 relasi): {tier_b_applied}/{len(hasil_b)}")
    print(f"Kata dgn keduanya kosong (dicatat sbg 1 percobaan gagal): {len(empty_streak_incremented)}")
    if tier_b_not_found:
        print(f"Tidak ditemukan di app_words.json: {tier_b_not_found}")
    if tier_b_already_filled:
        print(f"Dilewati krn field lama SUDAH terisi (cegah timpa data): {tier_b_already_filled}")
    if self_ref_removed:
        print("Self-reference dibuang otomatis:")
        for simp, removed in self_ref_removed:
            print(f"  {simp}: {[r['word'] for r in removed]}")
    if empty_streak_reached_threshold:
        print(f"\nKata yg BARU SAJA mencapai ambang gagal-berulang (akan dikecualikan mulai cycle berikutnya): {len(empty_streak_reached_threshold)}")
        for simp in empty_streak_reached_threshold:
            print(f"  - {simp}")

    print("\n--- Contoh 5 kata Tier B yg diterapkan ---")
    for simp, syn, ant in sample_changes:
        print(f"  {simp}: synonyms={syn}  antonyms={ant}")

    if DRY_RUN:
        print("\n[DRY RUN] Tidak ada file yang ditulis. Jalankan tanpa --dry-run untuk apply.")
        return

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = PATH_WORDS + f".bak_before_apply_sinonim_antonim_{ts}"
    shutil.copy2(PATH_WORDS, backup_path)
    print(f"\nBackup dibuat: {backup_path}")

    with open(PATH_WORDS, "w", encoding="utf-8") as f:
        json.dump(words, f, ensure_ascii=False, indent=2)

    print(f"\n[APPLIED] Tier A: {tier_a_applied} kata. Tier B: {tier_b_applied} kata.")
    print("Jangan lupa: jalankan checkpoint.py save setelah ini.")


if __name__ == "__main__":
    main()

"""
cek_dan_bersihkan_hasil_tier_b.py
====================================
Tool BARU -- jalankan ini SEBELUM apply_hasil_sinonim_antonim.py, langsung
di atas hasil mentah AI (hasil_tier_b_pilot.json). Tujuannya: tangkap 2
pola masalah yang selama ini Claude cari manual tiap cycle, TANPA perlu
paste hasil ke Claude tiap kali.

2 heuristik yang dipakai:
  1. SUBSTRING PADDING -- kata "sinonim" yg diusulkan mengandung kata utama
     sbg substring persis (mis. 庄园 -> 庄园住宅, 双向 -> 双向的). Pola ini
     ditemukan berulang di BLUEPRINT v33 sbg tanda AI 'memaksakan' jawaban.
  2. SELF-ADMISSION -- note_id AI sendiri mengandung kata kunci yg
     mengindikasikan dia sadar itu bukan sinonim yang pas (mis. "lebih
     luas", "lebih spesifik", "bukan pengganti umum/baku/standar", "beda
     makna", "cakupan berbeda", dll).

PENTING -- INI HEURISTIK, BUKAN PENGGANTI PENILAIAN:
  Kedua heuristik ini punya angka false-positive yg nggak kecil -- banyak
  catatan "lebih umum/lisan" itu memang cuma soal register formal vs
  informal (SAH, bukan masalah), bukan hipernim. Makanya defaultnya
  cuma REPORT, TIDAK auto-hapus. رسلان (atau Claude kalau mau dobel-cek)
  yg putuskan mana yg genuine dibuang dari daftar report ini.

Cara pakai:
  python cek_dan_bersihkan_hasil_tier_b.py
      -> cuma cetak laporan candidat bermasalah, TIDAK ubah file apa pun

  python cek_dan_bersihkan_hasil_tier_b.py --strip
      -> setelah cetak laporan, tulis salinan baru
         hasil_tier_b_pilot_cleaned.json dgn SEMUA candidat yg flagged
         (baik padding maupun self-admission) sudah dibuang dari
         synonyms/antonyms. File asli TIDAK disentuh.
         Lanjut jalankan apply_hasil_sinonim_antonim.py di atas file
         *_cleaned.json ini (ganti nama jadi hasil_tier_b_pilot.json,
         atau edit APP_WORDS_PATH di apply script kalau mau baca nama beda).

  python cek_dan_bersihkan_hasil_tier_b.py --strip --padding-only
      -> --strip tapi HANYA buang yg kena heuristik padding (confidence
         jauh lebih tinggi drpd self-admission keyword scan yg longgar).
         Disarankan pakai opsi ini kalau mau auto-strip tanpa baca laporan
         dulu -- padding hampir selalu genuine masalah, self-admission
         keyword scan masih perlu mata manusia.

File input default: hasil_tier_b_pilot.json (di folder yg sama)
"""

import json
import sys
import argparse
from pathlib import Path
from typing import Optional

INPUT_PATH = Path("hasil_tier_b_pilot.json")
OUTPUT_PATH = Path("hasil_tier_b_pilot_cleaned.json")

# kata kunci self-admission -- dikumpulkan dari pola berulang sepanjang
# sesi-sesi review manual (BLUEPRINT v32-v33). Longgar disengaja (banyak
# false positive spt "lebih umum/lisan" yg sebenarnya cuma register) --
# makanya kategori ini WAJIB direview manual, jangan auto-strip tanpa baca.
SELF_ADMISSION_KEYWORDS = [
    "lebih luas", "cakupan lebih luas", "cakupannya lebih luas",
    "lebih spesifik", "lebih sempit",
    "beda makna", "berbeda makna", "makna berbeda", "maknanya berbeda",
    "cakupan berbeda", "beda cakupan", "beda fokus", "fokus berbeda",
    "bukan pengganti umum", "bukan pengganti baku", "bukan pengganti standar",
    "bukan pengganti mutlak", "tidak selalu", "tidak khusus",
    "kurang umum",
]


def is_substring_padding(main_word: str, candidate_word: str, rel_type: str = "synonyms") -> bool:
    """True kalau candidate_word mengandung main_word persis sbg substring
    (dan bukan sama persis). PENGECUALIAN: utk antonyms, kalau candidate
    persis = '不' + main_word (atau '非'/'无' + main_word), itu pola negasi
    baku Mandarin utk bikin antonim (mis. 均匀 -> 不均匀), BUKAN padding --
    jangan di-flag."""
    if not candidate_word or candidate_word == main_word:
        return False
    if rel_type == "antonyms":
        for prefix in ("不", "非", "无", "无法", "不能", "没有"):
            if candidate_word == prefix + main_word:
                return False
    return main_word in candidate_word


def has_self_admission(note_id: str) -> Optional[str]:
    """Kembalikan keyword yg cocok kalau note_id mengandung salah satu
    frasa self-admission, else None."""
    note_lower = (note_id or "").lower()
    for kw in SELF_ADMISSION_KEYWORDS:
        if kw in note_lower:
            return kw
    return None


def scan_entry(entry):
    """Kembalikan list flag utk satu entri kata: (rel_type, idx, candidate,
    note_id, list_alasan)."""
    flags = []
    main_word = entry.get("simplified", "")
    for rel_type in ("synonyms", "antonyms"):
        rel_list = entry.get(rel_type) or []
        for idx, rel in enumerate(rel_list):
            if not isinstance(rel, dict):
                continue
            candidate = rel.get("word", "")
            note_id = rel.get("note_id", "")
            reasons = []
            if is_substring_padding(main_word, candidate, rel_type):
                reasons.append("PADDING (substring)")
            kw = has_self_admission(note_id)
            if kw:
                reasons.append(f"SELF-ADMISSION ('{kw}')")
            if reasons:
                flags.append((rel_type, idx, candidate, note_id, reasons))
    return flags


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--strip", action="store_true",
                         help="Tulis hasil_tier_b_pilot_cleaned.json dgn candidat flagged dibuang")
    parser.add_argument("--padding-only", action="store_true",
                         help="Dipakai bareng --strip: hanya buang yg kena heuristik padding (lebih aman utk auto-strip)")
    parser.add_argument("--input", type=str, default=None, help="Path file input custom")
    args = parser.parse_args()

    input_path = Path(args.input) if args.input else INPUT_PATH
    if not input_path.exists():
        print(f"ERROR: file tidak ditemukan: {input_path}")
        sys.exit(1)

    with open(input_path, encoding="utf-8") as f:
        data = json.load(f)

    print("=" * 70)
    print(f"CEK KUALITAS HASIL TIER B -- {input_path.name}")
    print(f"Total kata: {len(data)}")
    print("=" * 70)

    all_flags = []  # (main_word, rel_type, idx, candidate, note_id, reasons)
    for entry in data:
        for rel_type, idx, candidate, note_id, reasons in scan_entry(entry):
            all_flags.append((entry.get("simplified", ""), rel_type, idx, candidate, note_id, reasons))

    padding_flags = [f for f in all_flags if any("PADDING" in r for r in f[5])]
    admission_flags = [f for f in all_flags if any("SELF-ADMISSION" in r for r in f[5])]

    print(f"\n[PADDING] {len(padding_flags)} kandidat (confidence tinggi -- kata 'sinonim' mengandung kata utama):")
    for main_word, rel_type, idx, candidate, note_id, reasons in padding_flags:
        warn = "  [PERINGATAN: kata utama 1 karakter -- confidence RENDAH, banyak false positive utk kata majemuk baku]" if len(main_word) == 1 else ""
        print(f"  {main_word} -> {candidate} [{rel_type}]  note: \"{note_id}\"{warn}")

    # Entri yg SUDAH tercetak di seksi PADDING tidak boleh ikut dihitung/dicetak
    # ulang di sini -- kalau tidak, header (dihitung dari admission_flags mentah,
    # termasuk yg dobel-flag PADDING+SELF-ADMISSION) akan lebih besar drpd jumlah
    # baris yg benar-benar tercetak (yg sengaja skip duplikat PADDING).
    admission_only_flags = [f for f in admission_flags if not any("PADDING" in r for r in f[5])]

    print(f"\n[SELF-ADMISSION] {len(admission_only_flags)} kandidat (perlu review manual -- banyak false positive):")
    for main_word, rel_type, idx, candidate, note_id, reasons in admission_only_flags:
        print(f"  {main_word} -> {candidate} [{rel_type}]  note: \"{note_id}\"")

    total_unique = len(all_flags)
    print("\n" + "-" * 70)
    print(f"Total kandidat ter-flag: {total_unique} dari {sum(len(e.get('synonyms') or []) + len(e.get('antonyms') or []) for e in data)} relasi")
    if total_unique == 0:
        print("Batch ini bersih menurut heuristik -- aman lanjut apply_hasil_sinonim_antonim.py.")
    else:
        est_pct = 100 * total_unique / max(1, sum(len(e.get('synonyms') or []) + len(e.get('antonyms') or []) for e in data))
        print(f"Perkiraan flag-rate: ~{est_pct:.0f}%")
        if est_pct >= 30:
            print("REKOMENDASI: flag-rate tinggi -- pertimbangkan REGENERATE batch ini drpd strip+apply.")

    if args.strip:
        to_remove = padding_flags if args.padding_only else all_flags
        removed_count = 0
        for entry in data:
            main_word = entry.get("simplified", "")
            for rel_type in ("synonyms", "antonyms"):
                rel_list = entry.get(rel_type) or []
                candidates_to_remove = {
                    c for (mw, rt, idx, c, note, reasons) in to_remove
                    if mw == main_word and rt == rel_type
                }
                if candidates_to_remove:
                    new_list = [r for r in rel_list if r.get("word") not in candidates_to_remove]
                    removed_count += len(rel_list) - len(new_list)
                    entry[rel_type] = new_list

        with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        mode_label = "padding saja" if args.padding_only else "padding + self-admission"
        print(f"\n{removed_count} relasi dibuang ({mode_label}). File bersih ditulis ke: {OUTPUT_PATH}")
        print("File asli TIDAK diubah. Jalankan apply_hasil_sinonim_antonim.py di atas file *_cleaned.json ini.")
    else:
        print("\nIni baru laporan (belum ada file ditulis). Jalankan ulang dgn --strip "
              "kalau mau langsung buang candidat yg flagged.")


if __name__ == "__main__":
    main()

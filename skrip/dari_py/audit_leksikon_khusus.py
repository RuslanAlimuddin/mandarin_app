# -*- coding: utf-8 -*-
"""
audit_leksikon_khusus.py
─────────────────────────
Audit hasil generate AI eksternal untuk 5 kategori leksikon khusus
(kata seru, onomatope, sapaan keluarga, sapaan sosial, partikel modal).

TIDAK mengubah app_words.json. Ini tahap AUDIT (baca mentah → tulis
versi bersih ke folder staging/), sesuai kebiasaan proyek:
  audit → sample-check → dry-run → apply → checkpoint
Skrip ini = langkah "audit". Langkah "apply" ke app_words.json dikerjakan
terpisah setelah anda tinjau laporan ini.

APA YANG DIPERBAIKI OTOMATIS (aman, mekanis):
  1. Koma yang hilang di antara objek JSON (bug umum output AI panjang)
  2. Duplikat entri yang PERSIS sama (byte-per-byte)
  3. Kode pos "pron" dinormalisasi ke "r" (sesuai skema app_words.json anda)

APA YANG DITANDAI TAPI TIDAK DIHAPUS (butuh keputusan anda):
  1. Entri dialek (啦/咯/啵 dkk) -- melanggar aturan "hanya Mandarin standar"
  2. Entri di luar cakupan target Partikel Modal (di luar 10 lema inti
     yang diminta di prompt)
  3. Entri yang melebihi jumlah target per kategori (info saja, tidak
     ditandai per-item -- lihat ringkasan jumlah)

CARA PAKAI:
  1. Taruh 5 file mentah (hasil AI, .json atau .txt) di folder yang sama
     dengan skrip ini, sesuai nama di INPUT_FILES di bawah (sesuaikan
     nama file kalau beda).
  2. Jalankan: python audit_leksikon_khusus.py
  3. Cek folder staging/ untuk hasil bersih + laporan.txt untuk ringkasan.
"""

import json
import re
from pathlib import Path
from collections import Counter

# ── KONFIGURASI ──────────────────────────────────────────────────────
INPUT_FILES = {
    "kata_seru":       "PROMPT_1___Kata_Seru__Interjeksi_.txt",
    "onomatope":        "PROMPT_2___Onomatope.txt",
    "sapaan_keluarga":  "PROMPT_3___Sapaan_Kekerabatan.txt",
    "sapaan_sosial":    "PROMPT_4___Sapaan_Sosial___Bahasa_Hormat__Social___Honorific_Address_.txt",
    "partikel_modal":   "PROMPT_5___Partikel_Modal_Akhir_Kalimat__语气词_.txt",
}

TARGETS = {
    "kata_seru":       (30, 35),
    "onomatope":        (55, 65),
    "sapaan_keluarga":  (55, 65),
    "sapaan_sosial":    (25, 30),
    "partikel_modal":   (10, 12),
}

# Kode pos yang menyimpang dari skema app_words.json -> perbaikan otomatis
POS_FIX = {
    "pron": ("r", "kata ganti"),
}

# Karakter/kata yang dianggap dialek (bukan Mandarin standar) -- ditandai
DIALECT_MARKERS = {"啦", "咯", "啵", "唄"}  # 唄 = varian tulisan lama dari 呗, dicurigai typo/OCR juga

# Lema inti yang diminta di Prompt 5 (Partikel Modal) -- di luar ini akan
# ditandai "di luar cakupan" untuk ditinjau (BUKAN otomatis dihapus)
PARTIKEL_MODAL_CORE = {"啊", "呢", "吧", "嘛", "呗", "喽", "了", "的", "罢了", "而已"}

STAGING_DIR = Path("staging")
REPORT_PATH = Path("laporan_audit.txt")


def repair_json_syntax(raw: str) -> str:
    """Perbaiki koma yang hilang di antara objek array JSON.
    Menangani baik format 1-baris maupun pretty-printed (berindentasi)."""
    return re.sub(r"\}(\s*\r?\n\s*)\{", r"},\1{", raw)


def load_raw(path: Path):
    raw = path.read_text(encoding="utf-8")
    fixed = repair_json_syntax(raw)
    return json.loads(fixed)


def dedup_exact(entries):
    seen = set()
    unique = []
    removed = 0
    for e in entries:
        key = json.dumps(e, sort_keys=True, ensure_ascii=False)
        if key in seen:
            removed += 1
            continue
        seen.add(key)
        unique.append(e)
    return unique, removed


def normalize_pos(entries):
    fixed_count = 0
    for e in entries:
        pos = e.get("pos")
        if isinstance(pos, list):
            new_pos = []
            changed = False
            for p in pos:
                if p in POS_FIX:
                    new_pos.append(POS_FIX[p][0])
                    changed = True
                else:
                    new_pos.append(p)
            if changed:
                e["pos"] = new_pos
                # sinkronkan pos_id juga kalau formatnya 1:1
                pos_id = e.get("pos_id")
                if isinstance(pos_id, list) and len(pos_id) == len(new_pos):
                    for i, p in enumerate(pos):
                        if p in POS_FIX:
                            pos_id[i] = POS_FIX[p][1]
                fixed_count += 1
    return fixed_count


def flag_dialect(entries):
    """Exact-match saja (BUKAN substring) -- supaya kata seperti 哗啦/咯咯
    (onomatope yang kebetulan memuat karakter yang sama) tidak salah
    tertandai. Deteksi dialek cuma relevan untuk kata seru/partikel
    yang PERSIS berupa karakter dialek itu sendiri."""
    flagged = []
    for e in entries:
        s = e.get("simplified", "")
        if s in DIALECT_MARKERS:
            e["_flag"] = "dialek_non_standar"
            flagged.append(e)
    return flagged


def flag_out_of_scope(entries, core_set):
    flagged = []
    for e in entries:
        s = e.get("simplified", "")
        if s not in core_set and "_flag" not in e:
            e["_flag"] = "diluar_cakupan_prompt"
            flagged.append(e)
    return flagged


def main():
    STAGING_DIR.mkdir(exist_ok=True)
    report_lines = []

    def out(s=""):
        print(s)
        report_lines.append(s)

    out("AUDIT LEKSIKON KHUSUS")
    out("=" * 70)

    for key, filename in INPUT_FILES.items():
        path = Path(filename)
        out(f"\n[{key}] sumber: {filename}")
        if not path.exists():
            out(f"  ⚠ FILE TIDAK DITEMUKAN, dilewati.")
            continue

        try:
            data = load_raw(path)
        except Exception as e:
            out(f"  ✗ GAGAL PARSE bahkan setelah perbaikan otomatis: {e}")
            out(f"    -> perlu perbaikan manual, cek sekitar karakter yang disebutkan di atas.")
            continue

        raw_count = len(data)

        # 1. Dedup exact
        data, removed_dup = dedup_exact(data)

        # 2. Normalize pos
        pos_fixed = normalize_pos(data)

        # 3. Flag dialect (semua kategori, jaga-jaga)
        dialect_flagged = flag_dialect(data)

        # 4. Flag out-of-scope khusus partikel_modal
        scope_flagged = []
        if key == "partikel_modal":
            scope_flagged = flag_out_of_scope(data, PARTIKEL_MODAL_CORE)

        # Simpan hasil bersih (termasuk yang ditandai -- field _flag menempel)
        out_path = STAGING_DIR / f"{key}.json"
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=1)

        lo, hi = TARGETS[key]
        clean_count = len(data)
        flagged_total = len(dialect_flagged) + len(scope_flagged)
        unflagged_count = clean_count - flagged_total

        out(f"  Jumlah mentah:        {raw_count}")
        out(f"  Duplikat persis dibuang: {removed_dup}")
        out(f"  Kode pos diperbaiki:   {pos_fixed}")
        out(f"  Total setelah dedup:   {clean_count}  (target: {lo}-{hi})")
        if dialect_flagged:
            out(f"  ⚑ Ditandai DIALEK ({len(dialect_flagged)}): " +
                ", ".join(sorted(set(e['simplified'] for e in dialect_flagged))))
        if scope_flagged:
            out(f"  ⚑ Ditandai DI LUAR CAKUPAN ({len(scope_flagged)}): " +
                ", ".join(sorted(set(e['simplified'] for e in scope_flagged))))
        out(f"  Entri bersih tanpa tanda: {unflagged_count}")
        out(f"  -> disimpan ke: {out_path}")

    out("\n" + "=" * 70)
    out("SELESAI. Entri dengan field \"_flag\" BELUM dihapus -- tinjau manual")
    out("dulu (buka staging/*.json, cari \"_flag\"), baru putuskan dibuang")
    out("atau dipertahankan sebelum tahap apply ke app_words.json.")

    REPORT_PATH.write_text("\n".join(report_lines), encoding="utf-8")
    print(f"\n✓ Laporan lengkap juga disimpan ke {REPORT_PATH.resolve()}")


if __name__ == "__main__":
    main()

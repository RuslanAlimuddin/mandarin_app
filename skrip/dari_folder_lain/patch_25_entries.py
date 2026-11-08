# -*- coding: utf-8 -*-
"""
Patch untuk melengkapi 25 entri leksikon khusus yang belum lengkap
(hasil audit BLUEPRINT v26 - lihat penjelasan di chat).

Kategori 1 (15 entri): gap VARIANT_TO_KANGXI -> tambahkan mapping ini
  permanen ke enrich_leksikon_khusus.py juga, supaya kata baru masa
  depan dengan radikal ini tidak nyangkut lagi.
Kategori 2 (8 entri): radikal ambigu 阝/月, ditentukan manual per-kata
  (BUKAN ditebak - dicek makna & posisi tiap karakter).
Kategori 3 (1 entri): edge case bopomofo untuk konsonan silabis 'm'.
Kategori 4 (1 entri): 唻 di luar cakupan dictionary.txt/graphics.txt,
  diisi manual dari analisis komposisi karakter (confidence lebih rendah,
  disarankan رسلان cek ulang).
"""
import json
import shutil
from pathlib import Path

BASE = Path(".")

# ---------- Kategori 1: mapping varian radikal yang belum ada di VARIANT_TO_KANGXI ----------
VARIANT_FIX = {
    "⺮": 118,  # 竹 (bamboo) - dipakai di 算, 笑
    "丷": 12,   # varian atas 八 - dipakai di 养
    "贝": 154,  # 貝 (kerang/harta) - dipakai di 贤
    "门": 169,  # 門 (pintu) - dipakai di 阁
}

# ---------- Kategori 2: radikal ambigu 阝/月, ditentukan manual per kata ----------
# key = simplified word, value = radical_number yang benar untuk KARAKTER PERTAMA
AMBIGUOUS_FIX = {
    "阿弥陀佛": 170,  # 阿: 阝 di KIRI -> 阜 (mound), radikal 170
    "隆隆":     170,  # 隆: 阝 di KIRI -> 阜, radikal 170
    "阿嚏":     170,  # 阿: sama seperti di atas
    "阿姨":     170,  # 阿: sama seperti di atas (muncul di 2 file)
    "鄙人":     163,  # 鄙: 阝 di KANAN -> 邑 (city), radikal 163
    "朋友":     74,   # 朋: Kangxi mengklasifikasikan sbg radikal 月 itu sendiri (74), bukan varian daging (130)
}

# ---------- Kategori 3 & 4: fix spesifik per-field ----------
SPECIAL_FIX = {
    "呣": {"bopomofo": "ㄇˊ"},  # ḿ = konsonan silabis, tidak punya final -> ditulis initial+tone langsung
    "唻": {
        "radical": "口",
        "radical_number": 30,
        "stroke_count": 10,       # 口(3) + 来(7)
        "components": ["口", "来"],  # sebelumnya ['唻'] (atomic fallback krn tidak ada di dictionary.txt)
        # NOTE(رسلان): karakter ini di luar cakupan 9.574 char Make Me a Hanzi.
        # Nilai di atas dari analisis komposisi manual, BUKAN dari Lapis 1/2 otomatis.
        # Disarankan verifikasi sekali lagi sebelum apply final ke app_words.json.
    },
}

FILES = [
    "kata_seru_enriched.json",
    "onomatope_enriched.json",
    "partikel_modal_enriched.json",
    "sapaan_keluarga_enriched.json",
    "sapaan_sosial_enriched.json",
]

def fix_entry(e):
    changed = []
    simp = e.get("simplified")

    # Kategori 1: variant radical mapping
    if e.get("radical_number") in (None, "") and e.get("radical") in VARIANT_FIX:
        e["radical_number"] = VARIANT_FIX[e["radical"]]
        changed.append("radical_number(variant-map)")

    # Kategori 2: ambiguous 阝/月, resolved manually
    if e.get("radical_number") in (None, "") and simp in AMBIGUOUS_FIX:
        e["radical_number"] = AMBIGUOUS_FIX[simp]
        changed.append("radical_number(ambiguous-resolved)")

    # Kategori 3 & 4: special per-char fixes
    if simp in SPECIAL_FIX:
        for k, v in SPECIAL_FIX[simp].items():
            if e.get(k) in (None, "", []):
                e[k] = v
                changed.append(k)

    if changed and "_missing_fields" in e:
        del e["_missing_fields"]

    return changed

def main():
    total_fixed = 0
    for fname in FILES:
        path = BASE / fname
        if not path.exists():
            print(f"SKIP (tidak ditemukan): {fname}")
            continue
        data = json.loads(path.read_text(encoding="utf-8"))
        file_changes = 0
        for e in data:
            changed = fix_entry(e)
            if changed:
                file_changes += 1
                print(f"  [{fname}] {e.get('simplified')}: fixed {changed}")
        if file_changes:
            # backup dulu sebelum overwrite
            backup = path.with_suffix(".json.bak")
            shutil.copy(path, backup)
            path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
            print(f"-> {fname}: {file_changes} entri diperbaiki, backup disimpan ke {backup.name}")
        total_fixed += file_changes
    print(f"\nTOTAL entri diperbaiki: {total_fixed}/25")

if __name__ == "__main__":
    main()

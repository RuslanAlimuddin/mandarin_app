# -*- coding: utf-8 -*-
"""
Apply 470 entri leksikon khusus (kata_seru, onomatope, partikel_modal,
sapaan_keluarga, sapaan_sosial) ke app_words.json.

Alur: AUDIT -> DRY-RUN -> APPLY -> CHECKPOINT
(pastikan checkpoint.py sudah dijalankan dulu SEBELUM apply=True,
 sebagai lapisan pengaman tambahan di luar script ini)

Field kategori-spesifik (pihak, generasi, jenis, formalitas, sumber_bunyi,
register) DIBUANG dari record utama app_words.json, tapi ditampung ke
index_kelompok_khusus.json sebagai basis grup baru di sidebar Kamus.

CATATAN: field 'register' juga dipakai di kata_seru - tetap dianggap
kategori-spesifik (bukan field standar app_words.json) sehingga ikut dibuang.
"""
import json
import shutil
from pathlib import Path
from datetime import datetime

BASE = Path(".")
APP_WORDS_PATH = BASE / "app_words.json"

STAGING_FILES = [
    "kata_seru_enriched.json",
    "onomatope_enriched.json",
    "partikel_modal_enriched.json",
    "sapaan_keluarga_enriched.json",
    "sapaan_sosial_enriched.json",
]

# Field yang HANYA relevan untuk leksikon khusus, tidak ada di schema app_words.json standar
CATEGORY_SPECIFIC_FIELDS = [
    "pihak", "generasi", "jenis", "formalitas", "sumber_bunyi", "register",
]

# Field enriched yang TIDAK ada di skema standar app_words.json.
# 'kategori' dibuang (info-nya sudah terekam di nama file asal / index_kelompok_khusus.json).
# contoh_kalimat_* DIPERTAHANKAN sbg field baru di app_words.json (konten berharga,
# skema JSON fleksibel - entri lama yg tidak punya field ini tetap aman/tidak error).
DROP_FIELDS = ["kategori", "_missing_fields"]

# Default utk field standar app_words.json yang tidak ada di data enriched
NEW_ENTRY_DEFAULTS = {
    "hsk": None,
    "hsk2": None,
    "frequency": None,
    "synonyms": [],
    "antonyms": [],
    "themes": [],
}

def load_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))

def make_word_key(entry):
    # PENTING: app_words.json rasilan pakai SATU entri per 'simplified' (id == simplified,
    # tidak ada homograf terpisah). Jadi kunci duplikat HARUS simplified saja,
    # bukan (simplified, pinyin) - kalau tidak, varian nada/spasi pinyin (mis. 'yéye'
    # vs 'yé ye', atau 啊 á/ǎ/à vs ā yang sudah tergabung di satu entri) akan lolos
    # sebagai 'baru' dan menciptakan simplified ganda yang melanggar skema.
    return entry.get("simplified")

def strip_category_fields(entry):
    """Kembalikan (entry_bersih_siap_masuk_app_words, field_kategori_yang_dibuang)."""
    clean = dict(entry)
    extracted = {}
    for f in CATEGORY_SPECIFIC_FIELDS:
        if f in clean:
            extracted[f] = clean.pop(f)
    for f in DROP_FIELDS:
        clean.pop(f, None)
    # lengkapi field standar yang belum ada di data enriched
    clean.setdefault("id", clean.get("simplified"))
    for f, default in NEW_ENTRY_DEFAULTS.items():
        clean.setdefault(f, default)
    return clean, extracted

def audit(staging_entries, existing_keys):
    """existing_keys HARUS mencakup app_words asli + semua entri baru yang
    sudah 'dikomit' dari file-file sebelumnya dalam loop yang sama - supaya
    duplikat ANTAR FILE (mis. 哟/嘶/噢 muncul baik di kata_seru maupun
    onomatope) juga ketangkep, bukan cuma duplikat dalam 1 file atau
    duplikat vs app_words.json awal. existing_keys diupdate in-place."""
    duplicates, new_entries = [], []
    for e in staging_entries:
        k = make_word_key(e)
        if k in existing_keys:
            duplicates.append(e)
        else:
            new_entries.append(e)
            existing_keys.add(k)
    return new_entries, duplicates

# Label Indonesia utk tiap nilai field kategori-spesifik (dipakai bangun label_id)
VALUE_LABELS = {
    # register (kata_seru)
    "netral": "Netral", "kasar": "Kasar/Informal",
    # sumber_bunyi (onomatope)
    "air_hujan": "Air & Hujan", "benda_lain": "Benda Lain",
    "benturan_gesekan": "Benturan & Gesekan", "hewan": "Hewan",
    "makanan_masak": "Makanan & Masak", "mesin_kendaraan": "Mesin & Kendaraan",
    "tubuh_manusia": "Tubuh Manusia",
    # pihak (sapaan_keluarga)
    "ayah": "Pihak Ayah", "ibu": "Pihak Ibu",
    # generasi (sapaan_keluarga) - 'netral' utk pihak sudah dicover di atas
    "canggah": "Canggah", "buyut": "Buyut", "kakek_nenek": "Kakek/Nenek",
    "orangtua": "Orang Tua", "sendiri": "Sendiri", "anak": "Anak",
    "cucu": "Cucu", "cicit": "Cicit",
    # jenis (sapaan_keluarga)
    "kandung": "Kandung", "tiri": "Tiri", "angkat": "Angkat",
    "ipar": "Ipar", "mertua": "Mertua",
    # formalitas (sapaan_sosial)
    "formal": "Formal", "akrab": "Akrab",
}
KATEGORI_LABELS = {
    "kata_seru": "Kata Seru", "onomatope": "Onomatope",
    "partikel_modal": "Partikel Modal", "sapaan_keluarga": "Sapaan Keluarga",
    "sapaan_sosial": "Sapaan Sosial",
}

def build_kelompok_khusus_index(all_extracted_by_kategori):
    """
    Struktur output DISESUAIKAN dgn format index_theme.json yang sudah ada
    (flat, 1 level, tiap grup punya label_id/label_zh/words/count):

    {
      "kata_seru_netral": {"label_id": "Kata Seru - Netral", "label_zh": "", "words": [...], "count": N},
      "onomatope_hewan": {"label_id": "Onomatope - Hewan", "label_zh": "", "words": [...], "count": N},
      "partikel_modal": {"label_id": "Partikel Modal", "label_zh": "", "words": [...], "count": N},
      "sapaan_keluarga_ayah_kakek_nenek_kandung": {...},
      ...
    }
    label_zh dikosongkan (bukan tema per-kata seperti index_theme.json,
    jadi tidak relevan) - isi manual kalau رسلان mau nanti.
    """
    groups = {}  # group_key -> {label_parts: [...], words: [...]}
    for kategori, items in all_extracted_by_kategori.items():
        for simplified, extracted in items:
            if not extracted:
                key_parts, label_parts = [kategori], [KATEGORI_LABELS.get(kategori, kategori)]
            else:
                sorted_items = sorted(extracted.items())  # urutan konsisten: formalitas/generasi/jenis/pihak/register/sumber_bunyi
                key_parts = [kategori] + [str(v) for _, v in sorted_items]
                label_parts = [KATEGORI_LABELS.get(kategori, kategori)] + \
                              [VALUE_LABELS.get(str(v), str(v)) for _, v in sorted_items]
            group_key = "_".join(key_parts)
            groups.setdefault(group_key, {"label_parts": label_parts, "words": []})
            groups[group_key]["words"].append(simplified)

    index = {}
    for group_key, g in groups.items():
        index[group_key] = {
            "label_id": " - ".join(g["label_parts"]),
            "label_zh": "",
            "words": g["words"],
            "count": len(g["words"]),
        }
    return index

def main(apply=True):
    if not APP_WORDS_PATH.exists():
        print("app_words.json TIDAK DITEMUKAN di folder ini. Taruh file ini di folder yang sama, lalu jalankan ulang.")
        return

    app_words = load_json(APP_WORDS_PATH)
    print(f"app_words.json saat ini: {len(app_words)} entri")

    all_new, all_dup = [], []
    extracted_by_kategori = {}
    running_keys = {make_word_key(e) for e in app_words}  # diupdate tiap file diproses

    for fname in STAGING_FILES:
        path = BASE / fname
        if not path.exists():
            print(f"  SKIP (tidak ditemukan): {fname}")
            continue
        staging = load_json(path)
        new_entries, dup_entries = audit(staging, running_keys)
        print(f"  {fname}: {len(staging)} total | {len(new_entries)} baru | {len(dup_entries)} duplikat (skip)")
        if dup_entries:
            for d in dup_entries[:10]:
                print(f"    - duplikat: {d.get('simplified')} ({d.get('pinyin')})")
            if len(dup_entries) > 10:
                print(f"    ... dan {len(dup_entries)-10} lainnya")

        kategori = fname.replace("_enriched.json", "")
        extracted_by_kategori[kategori] = []
        for e in new_entries:
            clean, extracted = strip_category_fields(e)
            all_new.append(clean)
            extracted_by_kategori[kategori].append((clean.get("simplified"), extracted))
        all_dup.extend(dup_entries)

    print(f"\nRINGKASAN: {len(all_new)} entri baru siap ditambahkan, {len(all_dup)} duplikat di-skip")

    kelompok_index = build_kelompok_khusus_index(extracted_by_kategori)
    print(f"\nPreview index_kelompok_khusus.json: {len(kelompok_index)} grup total")
    for k, v in list(kelompok_index.items())[:8]:
        print(f"  {k}: label_id='{v['label_id']}', count={v['count']}, contoh_words={v['words'][:3]}")
    if len(kelompok_index) > 8:
        print(f"  ... dan {len(kelompok_index)-8} grup lainnya")

    if not apply:
        print("\n>>> INI DRY-RUN. Tidak ada file yang diubah. Set apply=True untuk benar-benar menulis. <<<")
        return

    # ---- APPLY ----
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = APP_WORDS_PATH.with_name(f"app_words.json.bak_{ts}")
    shutil.copy(APP_WORDS_PATH, backup_path)
    print(f"\nBackup app_words.json -> {backup_path.name}")

    app_words.extend(all_new)
    APP_WORDS_PATH.write_text(json.dumps(app_words, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"app_words.json ditulis ulang: {len(app_words)} entri total (+{len(all_new)})")

    kelompok_path = BASE / "index_kelompok_khusus.json"
    kelompok_path.write_text(json.dumps(kelompok_index, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"index_kelompok_khusus.json ditulis: {kelompok_path}")

    print("\nSELESAI. Jangan lupa clear cache browser (F12 -> Application -> Storage -> Clear site data).")

if __name__ == "__main__":
    main(apply=True)

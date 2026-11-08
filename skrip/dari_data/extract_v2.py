"""
extract_v2.py — Ekstraksi lebih ketat & adaptif
============================================================
Revisi dari peek_and_extract.py. Berdasarkan peek_report.txt kemarin,
saya sekarang tahu:

  - themes.json: tiap tema = {key, label_id, label_zh, word_count, words}
    "words" isinya kemungkinan entri kamus PENUH (termasuk field
    meanings_id yang bisa berisi 5-8 definisi panjang per kata) —
    itu sebabnya 19MB cuma jadi 15.8MB walau sudah difilter kemarin.
    Kali ini SETIAP field yang namanya mengandung "mean"/"arti"/
    "definition" akan dipotong jadi cuma definisi PERTAMA saja
    (bukan semua), dan field lain yang tidak relevan (pos, bopomofo,
    forms, dst) dibuang total.

  - master_final_hsk.json: dari 124.966 entri, kebanyakan punya
    hsk_level = null (kemungkinan nomor telepon, istilah teknis,
    entri langka) — TIDAK berguna untuk pembelajar. Kali ini HANYA
    entri yang: (a) hsk_level TERISI, ATAU (b) semantic_group TERISI
    (artinya sudah pernah diproses/dikategorikan), DAN mengandung
    karakter Han asli (bukan angka/simbol) — yang akan diambil.

Tidak mengubah file asli, murni baca & tulis file baru.
============================================================
"""

import json
import os
import re

THEMES_PATH      = r"C:\mandarin_kamus\output\themes.json"
MASTER_HSK_PATH  = r"C:\hanyu_extract\output_final\master_final_hsk.json"
APP_WORDS_PATH   = r"app_words.json"

OUT_DIR = os.path.dirname(os.path.abspath(__file__))
HAN_RE = re.compile(r'[\u3400-\u9FFF]')

MEANING_KEY_HINTS = ["mean", "arti", "definition", "gloss"]
DROP_KEY_HINTS    = ["_en", "bopomofo", "forms", "pos", "stroke", "radical_number"]


def human_size(path):
    if not os.path.isfile(path):
        return "TIDAK DITEMUKAN"
    n = os.path.getsize(path)
    for unit in ["B", "KB", "MB", "GB"]:
        if n < 1024:
            return f"{n:.1f}{unit}"
        n /= 1024
    return f"{n:.1f}TB"


def slim_word_entry(entry):
    """Ambil field penting saja dari satu entri kata, potong field
    'arti/meaning' supaya cuma definisi pertama (bukan array panjang)."""
    if not isinstance(entry, dict):
        return entry
    out = {}
    for k, v in entry.items():
        kl = k.lower()
        if any(h in kl for h in DROP_KEY_HINTS):
            continue
        if any(h in kl for h in MEANING_KEY_HINTS):
            # ambil cuma definisi pertama, potong maks 80 karakter
            if isinstance(v, list) and v:
                out[k] = str(v[0])[:80]
            elif isinstance(v, str):
                out[k] = v[:80]
            continue
        # field lain (hanzi/pinyin/hsk/dst) -- simpan apa adanya kalau
        # bukan struktur besar (list/dict panjang)
        if isinstance(v, (list, dict)) and len(v) > 3:
            continue  # kemungkinan field berat yang tidak perlu
        out[k] = v
    return out


def extract_themes():
    print(f"Membaca {THEMES_PATH} ({human_size(THEMES_PATH)}) ...")
    if not os.path.isfile(THEMES_PATH):
        print("  -> tidak ditemukan, dilewati.")
        return
    with open(THEMES_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    slim = {}
    for tema, val in data.items():
        if not isinstance(val, dict) or "words" not in val:
            slim[tema] = val
            continue
        slim[tema] = {
            "label_id": val.get("label_id"),
            "label_zh": val.get("label_zh"),
            "word_count": val.get("word_count"),
            "words": [slim_word_entry(w) for w in val["words"]],
        }

    out_path = os.path.join(OUT_DIR, "themes_extracted_v2.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(slim, f, ensure_ascii=False, indent=1)
    print(f"✓ themes_extracted_v2.json disimpan ({human_size(out_path)})")


def extract_master_hsk():
    print(f"Membaca {MASTER_HSK_PATH} ({human_size(MASTER_HSK_PATH)}) ...")
    if not os.path.isfile(MASTER_HSK_PATH):
        print("  -> tidak ditemukan, dilewati.")
        return
    with open(MASTER_HSK_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    existing = set()
    if os.path.isfile(APP_WORDS_PATH):
        with open(APP_WORDS_PATH, "r", encoding="utf-8") as f:
            app_words = json.load(f)
        existing = {w.get("simplified") for w in app_words}
        print(f"  app_words.json: {len(existing)} kata sudah ada di kamus (akan dilewati).")
    else:
        print("  ⚠ app_words.json tidak ditemukan -- semua entri relevan akan diambil.")

    kept = []
    for entry in data:
        simp = entry.get("simplified")
        if not simp or simp in existing:
            continue
        if not HAN_RE.search(simp):
            continue   # buang entri angka/simbol/non-hanzi seperti "110"
        has_hsk = entry.get("hsk_level") not in (None, "", "null")
        has_semantic = entry.get("semantic_group") not in (None, "", "null")
        if not (has_hsk or has_semantic):
            continue   # buang entri yang belum pernah diproses/dikategorikan sama sekali

        kept.append({
            "simplified": simp,
            "traditional": entry.get("traditional"),
            "pinyin": entry.get("pinyin_raw"),
            "meaning": (entry.get("definitions") or [""])[0][:100],
            "hsk_level": entry.get("hsk_level"),
            "semantic_group": entry.get("semantic_group"),
            "char_count": entry.get("char_count_simplified"),
        })

    out_path = os.path.join(OUT_DIR, "hsk_new_words_v2.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(kept, f, ensure_ascii=False, indent=1)
    print(f"✓ hsk_new_words_v2.json disimpan ({len(kept)} kata, dari {len(data)} total -- {human_size(out_path)})")


def main():
    extract_themes()
    print()
    extract_master_hsk()
    print("\nSelesai. Cek dulu ukuran 2 file baru itu (themes_extracted_v2.json,")
    print("hsk_new_words_v2.json) -- kalau masih di atas ~5MB, kabari saya jumlah")
    print("kata & ukurannya (tidak perlu upload dulu), nanti saya perketat lagi filternya.")


if __name__ == "__main__":
    main()

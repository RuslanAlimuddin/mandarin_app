#!/usr/bin/env python3
# periksa_data.py
# Jalankan di PC: python periksa_data.py
# Hasil akan disimpan ke: C:\mandarin_app\data\LAPORAN_DATA.txt

import json
import os
from collections import Counter, defaultdict

DATA_DIR  = r"C:\mandarin_app\data"
KAMUS_DIR = r"C:\mandarin_kamus"
OUTPUT    = os.path.join(DATA_DIR, "LAPORAN_DATA.txt")

lines = []
def log(s=""):
    print(s)
    lines.append(s)

def separator(title=""):
    s = "\n" + "═"*60
    if title:
        s += f"\n  {title}\n" + "═"*60
    log(s)

def load_json(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f), None
    except Exception as e:
        return None, str(e)

# ══════════════════════════════════════════════════════════════
separator("1. PEMERIKSAAN app_words.json")
# ══════════════════════════════════════════════════════════════

path_words = os.path.join(DATA_DIR, "app_words.json")
data, err = load_json(path_words)

if err:
    log(f"  ✗ GAGAL memuat: {err}")
else:
    log(f"  ✓ Berhasil dimuat")
    log(f"  Tipe root     : {type(data).__name__}")

    if isinstance(data, list):
        log(f"  Jumlah item   : {len(data):,}")

        # Ambil sampel item pertama
        sample = data[0] if data else {}
        log(f"\n  ── Semua field yang ada di item pertama ──")
        for k, v in sample.items():
            tipe = type(v).__name__
            preview = str(v)[:80].replace('\n', ' ')
            log(f"    {k:<20} [{tipe}]  {preview}")

        # Cek kelengkapan field penting
        separator("  Kelengkapan Field Penting (dari semua data)")

        fields_to_check = [
            "simplified", "traditional", "pinyin", "pinyin_numeric",
            "bopomofo", "meanings_id", "meanings_en", "hsk",
            "radical", "radical_number", "stroke_count",
            "structure", "char_type", "components",
            "semantic_component", "phonetic_component",
            "themes", "pos", "pos_id",
            "frequency", "synonyms", "antonyms",
        ]

        for field in fields_to_check:
            count_filled = sum(
                1 for w in data
                if w.get(field) not in (None, "", [], {})
            )
            pct = count_filled / len(data) * 100 if data else 0
            status = "✓" if pct > 80 else ("△" if pct > 20 else "✗")
            log(f"    {status}  {field:<25} {count_filled:>6,} / {len(data):,}  ({pct:.1f}%)")

        # ── TEMA ──
        separator("  Analisis Field 'themes'")
        tema_counter = Counter()
        kata_tanpa_tema = 0
        for w in data:
            th = w.get("themes")
            if not th:
                kata_tanpa_tema += 1
            else:
                if isinstance(th, list):
                    for t in th:
                        tema_counter[t] += 1
                else:
                    tema_counter[str(th)] += 1

        log(f"  Kata TANPA tema  : {kata_tanpa_tema:,} dari {len(data):,}")
        log(f"  Jumlah tema unik : {len(tema_counter)}")
        log(f"\n  Top 30 tema terbanyak:")
        for tema, cnt in tema_counter.most_common(30):
            log(f"    {tema:<30} {cnt:>5} kata")

        # ── KOMPONEN (radikal semantik vs fonetik) ──
        separator("  Analisis Field Komponen Karakter")
        has_components       = sum(1 for w in data if w.get("components"))
        has_semantic         = sum(1 for w in data if w.get("semantic_component"))
        has_phonetic         = sum(1 for w in data if w.get("phonetic_component"))
        has_ids              = sum(1 for w in data if w.get("ids"))
        has_ids_decomp       = sum(1 for w in data if w.get("ids_decomposition"))

        log(f"  components          terisi: {has_components:,}")
        log(f"  semantic_component  terisi: {has_semantic:,}")
        log(f"  phonetic_component  terisi: {has_phonetic:,}")
        log(f"  ids                 terisi: {has_ids:,}")
        log(f"  ids_decomposition   terisi: {has_ids_decomp:,}")

        # Tampilkan contoh komponen
        log(f"\n  Contoh 5 kata dengan field komponen:")
        shown = 0
        for w in data:
            if w.get("components") and shown < 5:
                log(f"    {w.get('simplified','')} | components: {w.get('components')} | semantic: {w.get('semantic_component')} | phonetic: {w.get('phonetic_component')}")
                shown += 1

        # ── RADIKAL ──
        separator("  Analisis Field 'radical'")
        radical_counter = Counter()
        tanpa_radical = 0
        for w in data:
            r = w.get("radical")
            if not r:
                tanpa_radical += 1
            else:
                radical_counter[r] += 1

        log(f"  Kata TANPA radikal : {tanpa_radical:,}")
        log(f"  Jumlah radikal unik: {len(radical_counter)}")
        log(f"\n  Top 20 radikal terbanyak:")
        for rad, cnt in radical_counter.most_common(20):
            log(f"    {rad}  {cnt:>5} kata")

        # ── PINYIN NUMERIC ──
        separator("  Analisis Pinyin")
        has_py_num = sum(1 for w in data if w.get("pinyin_numeric"))
        log(f"  pinyin           terisi: {sum(1 for w in data if w.get('pinyin')):,}")
        log(f"  pinyin_numeric   terisi: {has_py_num:,}")
        if has_py_num == 0:
            log(f"\n  ⚠ pinyin_numeric KOSONG — pencarian ma1/ma2 harus pakai konversi dari pinyin")
        # Tampilkan sampel
        log(f"\n  Sampel 5 kata (pinyin & pinyin_numeric):")
        for w in data[:5]:
            log(f"    {w.get('simplified','')} | pinyin: {w.get('pinyin','')} | pinyin_numeric: {w.get('pinyin_numeric','—')}")

    elif isinstance(data, dict):
        log(f"  Root adalah dict, keys: {list(data.keys())[:10]}")


# ══════════════════════════════════════════════════════════════
separator("2. PEMERIKSAAN cidict_index.json")
# ══════════════════════════════════════════════════════════════

path_cidict = os.path.join(DATA_DIR, "cidict_index.json")
cdata, cerr = load_json(path_cidict)

if cerr:
    log(f"  ✗ GAGAL memuat: {cerr}")
else:
    log(f"  ✓ Berhasil dimuat")
    log(f"  Tipe root : {type(cdata).__name__}")

    if isinstance(cdata, list):
        log(f"  Jumlah item: {len(cdata):,}")
        if cdata:
            sample = cdata[0]
            log(f"\n  ── Field di item pertama ──")
            for k, v in (sample.items() if isinstance(sample, dict) else []):
                preview = str(v)[:80]
                log(f"    {k:<20} {preview}")

            log(f"\n  Sampel 3 item:")
            for item in cdata[:3]:
                log(f"    {str(item)[:120]}")

    elif isinstance(cdata, dict):
        log(f"  Keys (10 pertama): {list(cdata.keys())[:10]}")
        # Ambil nilai pertama sebagai sampel
        first_key = list(cdata.keys())[0]
        first_val = cdata[first_key]
        log(f"\n  Sampel key '{first_key}': {str(first_val)[:200]}")


# ══════════════════════════════════════════════════════════════
separator("3. SCAN FILE JSON DI C:\\mandarin_kamus")
# ══════════════════════════════════════════════════════════════

if not os.path.exists(KAMUS_DIR):
    log(f"  Folder tidak ditemukan: {KAMUS_DIR}")
else:
    all_json = []
    for root, dirs, files in os.walk(KAMUS_DIR):
        for fn in files:
            if fn.endswith(".json"):
                full = os.path.join(root, fn)
                size = os.path.getsize(full)
                all_json.append((full, size))

    log(f"  Total file .json ditemukan: {len(all_json)}")
    log(f"\n  Daftar semua file (ukuran):")
    for path, size in sorted(all_json, key=lambda x: -x[1]):
        rel = path.replace(KAMUS_DIR, "").lstrip("\\")
        size_str = f"{size/1024/1024:.1f} MB" if size > 1024*1024 else f"{size/1024:.1f} KB"
        log(f"    {size_str:>10}  {rel}")

    # Intip isi tiap file (field saja)
    log(f"\n  ── Sampel struktur tiap file ──")
    for path, size in sorted(all_json, key=lambda x: -x[1]):
        rel = path.replace(KAMUS_DIR, "").lstrip("\\")
        d, e = load_json(path)
        if e:
            log(f"\n  [{rel}] ERROR: {e}")
            continue
        tipe = type(d).__name__
        if isinstance(d, list):
            pjg = len(d)
            fields = list(d[0].keys()) if d and isinstance(d[0], dict) else ["—"]
            log(f"\n  [{rel}]  list × {pjg:,}")
            log(f"    Fields: {fields}")
            log(f"    Item[0]: {str(d[0])[:150]}")
        elif isinstance(d, dict):
            log(f"\n  [{rel}]  dict × {len(d):,} keys")
            log(f"    Keys (10): {list(d.keys())[:10]}")
            first = list(d.values())[0]
            log(f"    Val[0]: {str(first)[:150]}")


# ══════════════════════════════════════════════════════════════
separator("SELESAI")
# ══════════════════════════════════════════════════════════════
log(f"\n  Laporan disimpan ke: {OUTPUT}")

# Simpan ke file
os.makedirs(DATA_DIR, exist_ok=True)
with open(OUTPUT, "w", encoding="utf-8") as f:
    f.write("\n".join(lines))

print(f"\n✅ Selesai! Buka file: {OUTPUT}")

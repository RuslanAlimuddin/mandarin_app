import json
import os
import base64

print("=" * 60)
print("FIXED BUILDER - Arabic Learning HTML")
print("=" * 60)

# --- BACA SEMUA FILE DATA ---
print("\n[1] Membaca p1.json dan p2.json...")
with open("p1.json", "r", encoding="utf-8") as f:
    p1 = json.load(f)
with open("p2.json", "r", encoding="utf-8") as f:
    p2 = json.load(f)

# --- BACA CSS ---
print("[2] Membaca p3.css...")
with open("p3.css", "r", encoding="utf-8") as f:
    CSS = f.read()

# --- BACA JS ---
print("[3] Membaca p4.js (JS murni)...")
with open("p4.js", "r", encoding="utf-8") as f:
    JS = f.read()

# ================================================================
# BANGUN ULANG DATA DENGAN STRUKTUR YANG BENAR
# ================================================================

print("[4] Membangun ulang data dengan struktur yang benar...")

# ---- 1. Huruf ----
huruf = []
for h in p1["huruf"]:
    huruf.append({
        "letter": h["l"],
        "name": h["n"],
        "name_ar": h["na"],
        "translit": h["t"],
        "type": h["tp"],
        "sound": h["s"]
    })

# ---- 2. Tashkeel ----
tashkeel = []
for t in p1["tashkeel"]:
    tashkeel.append({
        "mark": t["m"],
        "name": t["n"],
        "name_ar": t["na"],
        "sound": t["s"]
    })

# ---- 3. Roots ----
roots = []

# Fungsi untuk mengkonversi root dengan tashrif yang benar
def convert_root(r):
    # Konversi tashrif dari format {m:{...}, u:{...}, r:{...}}
    # ke format {fi'il_madhi:{...}, fi'il_mudhari:{...}, fi'il_amr:{...}}
    tf = r.get("tf", {})
    tashrif_full = {}
    if "m" in tf:
        tashrif_full["fi'il_madhi"] = tf["m"]
    if "u" in tf:
        tashrif_full["fi'il_mudhari"] = tf["u"]
    if "r" in tf:
        tashrif_full["fi'il_amr"] = tf["r"]

    # Konversi derivatives
    derivatives = []
    for d in r.get("d", []):
        derivatives.append({
            "word": d["w"],
            "transliteration": d["t"],
            "meaning_id": d["m"],
            "meaning_en": d.get("e", ""),
            "type": d["tp"],
            "wazan": d["wz"],
            "pattern": d.get("pattern", "")
        })

    # Konversi examples
    examples = []
    for ex in r.get("ex", []):
        examples.append({
            "ar": ex["ar"],
            "translit": ex["t"],
            "meaning_id": ex["m"],
            "irab": ex.get("ir", "")
        })

    return {
        "root": r["r"],
        "root_letters": r["rl"],
        "meaning_id": r["m"],
        "meaning_en": r.get("e", ""),
        "bab": r["bab"],
        "wazan_base": r["wb"],
        "level": r["lv"],
        "frequency": r["fr"],
        "quran_occurrences": r["qc"],
        "derivatives": derivatives,
        "examples": examples,
        "tashrif_full": tashrif_full
    }

# Proses semua roots dari p1 dan p2
for r in p1.get("roots_a", []):
    roots.append(convert_root(r))
for r in p2.get("roots_b", []):
    roots.append(convert_root(r))

# ---- 4. Themes ----
themes = []

def convert_theme(t):
    words = []
    for w in t.get("w", []):
        words.append({
            "word": w["w"],
            "transliteration": w["t"],
            "meaning_id": w["m"],
            "type": w["tp"]
        })
    examples = []
    for ex in t.get("ex", []):
        examples.append({
            "ar": ex["ar"],
            "translit": ex["t"],
            "meaning_id": ex["m"]
        })
    return {
        "id": t["id"],
        "name_id": t["ni"],
        "name_en": t.get("ne", ""),
        "name_ar": t["na"],
        "level": t["lv"],
        "word_count": len(words),
        "words": words,
        "examples": examples,
        "notes": t.get("notes", "")
    }

for t in p1.get("themes_a", []):
    themes.append(convert_theme(t))
for t in p2.get("themes_b", []):
    themes.append(convert_theme(t))

# ---- 5. Phrases ----
phrases = []
for p in p2.get("phrases", []):
    phrases.append({
        "phrase_ar": p["ar"],
        "translit": p["t"],
        "meaning_id": p["m"],
        "context": p["c"],
        "level": p["lv"]
    })

# ---- 6. Nahwu ----
nahwu = []
for n in p2.get("nahwu", []):
    item = {
        "topic_ar": n["ta"],
        "topic_id": n["ti"],
        "lv": n["lv"],
        "df": n["df"],
        "cp": n.get("cp", []),
        "fe": n.get("fe", [])
    }
    if "ct" in n:
        item["ct"] = n["ct"]
    nahwu.append(item)

# ---- 7. Shorof ----
shorof = {}
for key, sec in p2.get("shorof", {}).items():
    s = {
        "name_id": sec.get("ni", ""),
        "description_id": sec.get("di", "")
    }
    babs = []
    for b in sec.get("babs", []):
        nb = {}
        # Ambil semua field yang ada
        for k, v in b.items():
            nb[k] = v
        # Tambahkan alias untuk kompatibilitas
        if "wm" in nb and "wazan_madhi" not in nb:
            nb["wazan_madhi"] = nb["wm"]
        if "wu" in nb and "wazan_mudhari" not in nb:
            nb["wazan_mudhari"] = nb["wu"]
        if "wa" in nb and "wazan_amr" not in nb:
            nb["wazan_amr"] = nb["wa"]
        if "eg" in nb and "example" not in nb:
            nb["example"] = nb["eg"]
        if "no" in nb and "note" not in nb:
            nb["note"] = nb["no"]
        if "mn" in nb and "meaning_note" not in nb:
            nb["meaning_note"] = nb["mn"]
        if "ms" in nb and "masdar" not in nb:
            nb["masdar"] = nb["ms"]
        babs.append(nb)
    s["babs"] = babs

    if "pats" in sec:
        patterns = []
        for p in sec["pats"]:
            patterns.append({
                "name_ar": p.get("na", ""),
                "description_id": p.get("di", ""),
                "example": p.get("eg", "")
            })
        s["patterns"] = patterns

    shorof[key] = s

# ---- 8. Vocabulary (dibangun otomatis dari roots + themes + phrases) ----
vocabulary = []

# Dari roots
for r in roots:
    for d in r["derivatives"]:
        vocabulary.append({
            "word": d["word"],
            "transliteration": d["transliteration"],
            "meaning_id": d["meaning_id"],
            "meaning_en": d.get("meaning_en", ""),
            "type": d["type"],
            "root": r["root"],
            "root_meaning_id": r["meaning_id"],
            "wazan": d["wazan"],
            "pattern": d.get("pattern", ""),
            "level": r["level"],
            "frequency": r["frequency"],
            "source": "root",
            "tags": [r["meaning_id"], d["type"]]
        })

# Dari themes
for t in themes:
    for w in t["words"]:
        vocabulary.append({
            "word": w["word"],
            "transliteration": w["transliteration"],
            "meaning_id": w["meaning_id"],
            "meaning_en": "",
            "type": w["type"],
            "root": "",
            "root_meaning_id": "",
            "wazan": "",
            "pattern": "",
            "level": t["level"],
            "frequency": "high",
            "source": "thematic",
            "theme": t["name_id"],
            "theme_ar": t["name_ar"],
            "tags": [t["name_id"], w["type"]]
        })

# Dari phrases
for p in phrases:
    vocabulary.append({
        "word": p["phrase_ar"],
        "transliteration": p["translit"],
        "meaning_id": p["meaning_id"],
        "meaning_en": "",
        "type": "phrase",
        "root": "",
        "root_meaning_id": "",
        "wazan": "",
        "pattern": "",
        "level": p["level"],
        "frequency": "high",
        "source": "phrase",
        "context": p["context"],
        "tags": ["frasa", p["context"]]
    })

# ---- 9. Dictionary ----
dict_map = {}
for v in vocabulary:
    w = v["word"]
    if w not in dict_map:
        dict_map[w] = {"word": w, "entries": []}
    dict_map[w]["entries"].append({
        "transliteration": v["transliteration"],
        "meaning_id": v["meaning_id"],
        "meaning_en": v.get("meaning_en", ""),
        "type": v["type"],
        "root": v["root"],
        "wazan": v["wazan"],
        "level": v["level"],
        "source": v["source"]
    })
dictionary = list(dict_map.values())

# ---- 10. Word Builder ----
word_builder = {
    "composition_principles": [
        {
            "name_id": "Idhafah (Posesif)",
            "description_id": "Dua isim dihubungkan kepemilikan. Mudhaf tidak dapat alif-lam, mudhaf ilaih majrur.",
            "examples": [
                {"compound": "كِتَابُ الطَّالِبِ", "translit": "kitābu aṭ-ṭālibi", "meaning_id": "buku siswa"}
            ]
        },
        {
            "name_id": "Jar Majrur (Prepositional)",
            "description_id": "Huruf jar + isim majrur. Berfungsi sebagai khabar, sifat, atau hal.",
            "examples": [
                {"phrase": "فِي الْمَكْتَبِ", "translit": "fī al-maktabi", "meaning_id": "di kantor"}
            ]
        },
        {
            "name_id": "Angka + Yang Dihitung",
            "description_id": "Angka 1-2 mengikuti gender. Angka 3-9 BERLAWANAN gender dengan yang dihitung.",
            "examples": [
                {"ar": "ثَلَاثَةُ كُتُبٍ", "meaning_id": "tiga buku (kutub=mudzakkar, angka=muannath)"}
            ]
        }
    ]
}

# ================================================================
# GABUNGKAN SEMUA
# ================================================================

DATA = {
    "metadata": {
        "schema_version": "1.0.0",
        "generated_at": "2025-01-01",
        "statistics": {
            "total_vocabulary": len(vocabulary),
            "total_dictionary_entries": len(dictionary),
            "total_roots": len(roots),
            "total_themes": len(themes),
            "total_nahwu_topics": len(nahwu),
            "total_phrases": len(phrases),
            "total_letters": len(huruf),
            "total_tashkeel": len(tashkeel)
        },
        "levels_used": sorted(set(v["level"] for v in vocabulary))
    },
    "huruf": huruf,
    "tashkeel": tashkeel,
    "vocabulary": vocabulary,
    "dictionary": dictionary,
    "roots": roots,
    "themes": themes,
    "nahwu": nahwu,
    "shorof": shorof,
    "word_builder": word_builder,
    "phrases": phrases
}

print(f"  Vocabulary  : {len(vocabulary)}")
print(f"  Dictionary  : {len(dictionary)}")
print(f"  Roots       : {len(roots)}")
print(f"  Themes      : {len(themes)}")
print(f"  Nahwu       : {len(nahwu)}")
print(f"  Phrases     : {len(phrases)}")

# ================================================================
# SIMPAN JSON UNTUK VERIFIKASI
# ================================================================

with open("arabic_learning_data_fixed.json", "w", encoding="utf-8") as f:
    json.dump(DATA, f, ensure_ascii=False, indent=2)
print("[5] Data JSON disimpan ke arabic_learning_data_fixed.json")

# ================================================================
# BANGUN HTML DENGAN BASE64
# ================================================================

print("[6] Mengencode data ke Base64...")
B64 = base64.b64encode(json.dumps(DATA, ensure_ascii=False).encode("utf-8")).decode("ascii")

print("[7] Membangun arabic-learning.html...")

# Sidebar items
sidebar_items = [
    ("dashboard", "fa-chart-pie", "Dashboard"),
    ("flashcard", "fa-clone", "Flashcard"),
    ("dictionary", "fa-book", "Kamus"),
    ("roots", "fa-seedling", "Akar Kata"),
    ("wordbuilder", "fa-cubes", "Word Builder"),
    ("shorof", "fa-sitemap", "Shorof"),
    ("nahwu", "fa-scroll", "Nahwu"),
    ("themes", "fa-palette", "Tema Kosakata"),
    ("huruf", "fa-font", "Huruf & Harakat"),
    ("phrases", "fa-comments", "Frasa Umum"),
]

html = """<!DOCTYPE html>
<html lang="id">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Arabic Learning Suite</title>
<link href="https://fonts.googleapis.com/css2?family=Amiri:wght@400;700&family=Plus+Jakarta+Sans:wght@400;600;700&display=swap" rel="stylesheet">
<link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css" rel="stylesheet">
<style>
""" + CSS + """
</style>
</head>
<body>
<nav class="sidebar">
<h1><i class="fas fa-book-quran" style="margin-right:5px"></i>Arabic Suite</h1>
<p>Data Preview & Learning Tool</p>
"""

for i, (tab, icon, label) in enumerate(sidebar_items):
    cls = ' class="active"' if i == 0 else ''
    html += f'<a data-tab="{tab}"{cls}><i class="fas {icon}"></i>{label}</a>\n'

html += """<a data-tab="export" style="color:var(--green);margin-top:10px"><i class="fas fa-download"></i>Export JSON</a>
</nav>
<main class="main" id="content"></main>
<div class="ft" id="toast"></div>
<script>
const DATA64 = \"""" + B64 + """\";
""" + JS + """
</script>
</body>
</html>"""

with open("arabic-learning.html", "w", encoding="utf-8") as f:
    f.write(html)

size_kb = os.path.getsize("arabic-learning.html") / 1024
print(f"[8] arabic-learning.html selesai ({size_kb:.1f} KB)")

print("\n" + "=" * 60)
print("✅ SELESAI!")
print("=" * 60)
print("File yang dihasilkan:")
print(f"  - arabic_learning_data_fixed.json  (data mentah untuk verifikasi)")
print(f"  - arabic-learning.html             (buka di browser)")
print("\nSekarang buka arabic-learning.html di Chrome/Edge.")
print("Semua tab seharusnya berfungsi dengan sempurna.")
print("=" * 60)
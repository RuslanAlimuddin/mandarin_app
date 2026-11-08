"""
tambang_karakter_mirip.py -- cari kandidat "Karakter Mirip" JENIS A dari DATA, bukan dari
ingatan AI. Cara ini dipakai karena pencarian lewat AI sudah jenuh (batch 3 hanya
menghasilkan 1 grup baru).

IDE: data/dictionary.txt (Make Me a Hanzi) memuat dekomposisi tiap karakter. Karakter X yang
tersusun dari SATU karakter dasar Y + SATU goresan tunggal (titik, garis miring, garis
mendatar, dst.) adalah pasangan mirip-bentuk jenis A.
Contoh yang seharusnya ketemu: 主=丶+王, 本=木+一, 刃=刀+丶, 白=丿+日, 灭=一+火.

Cara pakai (dari C:\\mandarin_app):
    python tambang_karakter_mirip.py            # LAPORAN SAJA (tidak menulis apa pun)
    python tambang_karakter_mirip.py --tulis    # + tulis kandidat_karakter_mirip.txt
    python tambang_karakter_mirip.py --n=40     # jumlah grup yang ditulis (default 40)

File --tulis berformat sama dengan hasil AI tahap 1, jadi langsung lanjut ke Tahap 2:
    python buat_prompt_karakter_mirip.py kandidat_karakter_mirip.txt
(AI kedua yang memeriksa dan menambah posisi goresan yang tepat; note buatan skrip ini
sengaja polos dan hanya memuat fakta dari dekomposisi.)

Syarat: Y dan X harus ada di himpunan "karakter umum" = karakter di data/char_etymology_id.json
ditambah entri 1-karakter di data/app_words.json. Pasangan yang sudah tercakup di
data/confusion_groups.json dibuang.
"""

import json
import os
import sys

DATA = "data"
PATH_DICT = os.path.join(DATA, "dictionary.txt")
PATH_ETYM = os.path.join(DATA, "char_etymology_id.json")
PATH_WORDS = os.path.join(DATA, "app_words.json")
PATH_GROUPS = os.path.join(DATA, "confusion_groups.json")
OUT = "kandidat_karakter_mirip.txt"

BINARY_OPS = set("⿰⿱⿴⿵⿶⿷⿸⿹⿺⿻")
STROKE_NAME = {
    "丶": "titik (丶)",
    "丿": "goresan miring kiri (丿)",
    "乀": "goresan miring kanan (乀)",
    "一": "garis mendatar (一)",
    "丨": "garis tegak (丨)",
    "亅": "kait tegak (亅)",
    "乙": "goresan berkelok (乙)",
    "乚": "goresan berkelok (乚)",
    "乛": "goresan siku (乛)",
    "𠃊": "goresan siku (𠃊)",
}
MAX_CONF = 4
# pasangan (dasar, turunan) yang SEHARUSNYA bisa ditemukan -- uji kelayakan di data riil
CONTOH = [("王", "主"), ("王", "玉"), ("大", "太"), ("大", "犬"), ("木", "本"), ("木", "末"),
          ("刀", "刃"), ("日", "白"), ("火", "灭"), ("十", "千"), ("止", "正"), ("日", "目")]


def is_stroke(c):
    return c in STROKE_NAME or "\u31c0" <= c <= "\u31ef"


def stroke_label(c):
    return STROKE_NAME.get(c, f"goresan tunggal ({c})")


def load_json(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError):
        return None


def load_common_and_freq():
    common, freq = set(), {}
    et = load_json(PATH_ETYM)
    if isinstance(et, dict):
        common.update(k for k in et if isinstance(k, str) and len(k) == 1)
    elif isinstance(et, list):
        for it in et:
            if isinstance(it, dict):
                c = it.get("char") or it.get("character") or it.get("simplified")
                if isinstance(c, str) and len(c) == 1:
                    common.add(c)
    words = load_json(PATH_WORDS)
    if isinstance(words, list):
        for w in words:
            s = (w.get("simplified") or w.get("id") or "") if isinstance(w, dict) else ""
            if len(s) == 1:
                common.add(s)
                fr = w.get("frequency")
                if isinstance(fr, (int, float)):
                    freq[s] = min(freq.get(s, 10**9), fr)
    return common, freq


def main():
    tulis = "--tulis" in sys.argv
    n = 40
    for a in sys.argv[1:]:
        if a.startswith("--n="):
            n = int(a.split("=", 1)[1])

    if not os.path.exists(PATH_DICT):
        print(f"[BERHENTI] {PATH_DICT} tidak ditemukan. Jalankan dari C:\\mandarin_app.")
        sys.exit(1)

    common, freq = load_common_and_freq()
    print(f"Himpunan karakter umum: {len(common)} "
          f"({'char_etymology_id + app_words' if common else 'KOSONG -> tanpa filter, hasil akan berisik'})")

    groups_data = load_json(PATH_GROUPS) or {"groups": []}
    existing = [frozenset([g["character"], *g.get("confusable_with", [])]) for g in groups_data["groups"]]

    # ---- baca dictionary.txt
    n_lines = n_dec = n_bin = n_stroke = 0
    decomp, raw_samples = {}, []
    with open(PATH_DICT, "r", encoding="utf-8", errors="replace") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            n_lines += 1
            if len(raw_samples) < 2:
                raw_samples.append(line[:150])
            try:
                o = json.loads(line)
            except json.JSONDecodeError:
                continue
            c, d = o.get("character"), o.get("decomposition")
            if isinstance(c, str) and len(c) == 1 and isinstance(d, str) and d:
                decomp[c] = d
                n_dec += 1

    # ---- cari X = dasar Y + 1 goresan
    pairs = []  # (Y, X, stroke)
    for x, d in decomp.items():
        if common and x not in common:
            continue
        if len(d) == 3 and d[0] in BINARY_OPS:
            n_bin += 1
            a, b = d[1], d[2]
            for st, y in ((a, b), (b, a)):
                if is_stroke(st) and not is_stroke(y) and y != x and (not common or y in common):
                    n_stroke += 1
                    pairs.append((y, x, st))
                    break

    # ---- kelompokkan per dasar Y, buang pasangan yang sudah tercakup
    by_y = {}
    for y, x, st in pairs:
        by_y.setdefault(y, []).append((x, st))
    status = {}
    cand = []
    for y, xs in by_y.items():
        baru = []
        for x, st in xs:
            if any({y, x} <= s for s in existing):
                status[(y, x)] = "sudah tercakup"
            else:
                status[(y, x)] = "KANDIDAT BARU"
                baru.append((x, st))
        baru.sort(key=lambda t: freq.get(t[0], 10**9))
        for i in range(0, len(baru), MAX_CONF):
            chunk = baru[i:i + MAX_CONF]
            note = "Perbedaan pada satu goresan tambahan: " + ", ".join(
                f"{x} = {y} + {stroke_label(st)}" for x, st in chunk) + "."
            score = max([freq.get(y, 10**9)] + [freq.get(x, 10**9) for x, _ in chunk])
            cand.append((score, {"character": y, "confusable_with": [x for x, _ in chunk], "note": note}))
    cand.sort(key=lambda t: (t[0], t[1]["character"]))

    # ---- laporan
    print("\nDIAGNOSIS dictionary.txt")
    print(f"  baris dibaca            : {n_lines}")
    print(f"  punya decomposition     : {n_dec}")
    print(f"  bentuk biner (3 simbol) : {n_bin}  (dari karakter umum)")
    print(f"  = dasar + 1 goresan     : {n_stroke}")
    print(f"  grup kandidat BARU      : {len(cand)}  (setelah membuang pasangan yang sudah tercakup)")
    if raw_samples:
        print("  contoh baris mentah     :")
        for s in raw_samples:
            print("    ", s)

    print("\nUJI KELAYAKAN (pasangan yang seharusnya ketemu):")
    for y, x in CONTOH:
        s = status.get((y, x))
        if s is None:
            d = decomp.get(x, "(tidak ada di dictionary)")
            s = f"tidak terdeteksi (dekomposisi {x}: {d})"
        print(f"  {y} -> {x}: {s}")

    print(f"\n{min(n, len(cand))} kandidat teratas (urut dari yang paling umum):")
    for _, o in cand[:n]:
        print(f"  {o['character']}{''.join(o['confusable_with'])}  -- {o['note']}")

    if not tulis:
        print("\n(LAPORAN SAJA -- tidak ada file ditulis. Tambah --tulis untuk menulis "
              f"{OUT}.)")
        return
    if not cand:
        print("\nTidak ada kandidat -- tidak ada file ditulis.")
        return
    with open(OUT, "w", encoding="utf-8", newline="\n") as f:
        for _, o in cand[:n]:
            f.write(json.dumps(o, ensure_ascii=False) + "\n")
    print(f"\n[OK] {OUT} ditulis: {min(n, len(cand))} kandidat. Lanjut: "
          "python buat_prompt_karakter_mirip.py kandidat_karakter_mirip.txt")


if __name__ == "__main__":
    main()

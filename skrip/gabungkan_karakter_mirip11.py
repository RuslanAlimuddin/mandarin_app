"""
gabungkan_karakter_mirip.py -- validasi & gabung kandidat "Karakter Mirip"
ke data/confusion_groups.json.

DEFAULT = DRY-RUN (hanya laporan, tidak menulis apa pun).
Tambah --apply untuk benar-benar menulis. Sebelum menulis, otomatis:
  1. python checkpoint.py save   (lewat subprocess, sama spt batch4/5/6 v35)
  2. backup data/confusion_groups.json.bak_<timestamp>
  3. tulis atomik (.tmp lalu rename)

Cara pakai (dari C:\\mandarin_app):
    python gabungkan_karakter_mirip.py kandidat.txt              # dry-run
    python gabungkan_karakter_mirip.py verifikasi.txt            # dry-run
    python gabungkan_karakter_mirip.py verifikasi.txt --apply    # tulis beneran

Format input: NDJSON (satu objek per baris; toleran thd blok ```, baris
yang nempel tanpa newline, dan teks pengantar AI). Tiap objek:
    {"character":"X","confusable_with":["Y","Z"],"note":"..."}
Objek berisi kunci "drop" (keluaran prompt verifikasi) hanya dicatat & dilewati.
Tidak perlu field "id" -- id diberikan otomatis (lanjut dari id terbesar).

Aturan penolakan (kelompok TIDAK dimasukkan):
  - skema salah / karakter bukan 1 hanzi / confusable_with kosong atau >4
  - note kosong, terlalu pendek/panjang, atau bukan Bahasa Indonesia
  - ada karakter yang tidak ditemukan di app_words.json MAUPUN cidict_index.json
    (ini juga menyaring aksara tradisional & karangan AI)
  - duplikat persis, atau seluruh karakternya sudah tercakup di 1 grup lama
    (mis. 已/己 kalau 己已巳 sudah ada), atau duplikat di dalam batch yang sama
Peringatan (tetap masuk, tapi ditandai di laporan):
  - karakter hanya ada di Cidict (bukan app_words.json)
  - grup memperluas grup lama (superset) atau beririsan sebagian
"""

import json
import os
import re
import subprocess
import sys
import time

DATA_DIR = "data"
PATH_GROUPS = os.path.join(DATA_DIR, "confusion_groups.json")
PATH_WORDS = os.path.join(DATA_DIR, "app_words.json")
PATH_CIDICT = os.path.join(DATA_DIR, "cidict_index.json")

MAX_CONFUSABLE = 4
NOTE_MIN, NOTE_MAX = 12, 220


# ---------------------------------------------------------------- parsing --
def iter_json_objects(text):
    """Ambil semua objek {...} seimbang dari teks bebas (abaikan isi string).
    Tahan thd: pagar ```, teks pengantar, dan 2 objek yang nempel di 1 baris."""
    text = text.replace("\ufeff", "")
    depth, start, in_str, esc = 0, None, False, False
    for i, ch in enumerate(text):
        if in_str:
            if esc:
                esc = False
            elif ch == "\\":
                esc = True
            elif ch == '"':
                in_str = False
            continue
        if ch == '"' and depth > 0:
            in_str = True
        elif ch == "{":
            if depth == 0:
                start = i
            depth += 1
        elif ch == "}" and depth > 0:
            depth -= 1
            if depth == 0 and start is not None:
                chunk = text[start:i + 1]
                start = None
                try:
                    yield json.loads(chunk)
                except json.JSONDecodeError:
                    yield {"_rusak": chunk[:80]}
    if depth > 0 and start is not None:  # objek terakhir terpotong (respons AI kepotong)
        yield {"_rusak": "TERPOTONG di akhir file: " + text[start:start + 60]}


def is_hanzi(c):
    return len(c) == 1 and ("\u4e00" <= c <= "\u9fff" or "\u3400" <= c <= "\u4dbf")


# ---------------------------------------------------------- data existing --
def load_groups():
    with open(PATH_GROUPS, "r", encoding="utf-8") as f:
        return json.load(f)


def group_chars(g):
    return [g["character"]] + list(g.get("confusable_with", []))


def count_unique_chars(groups):
    s = set()
    for g in groups:
        s.update(group_chars(g))
    return len(s)


def dump_groups(data):
    """Tulis dgn gaya PERSIS file asli (indent 1 spasi, confusable_with 1 baris)."""
    out = ['{', ' "groups": [']
    gs = data["groups"]
    for i, g in enumerate(gs):
        conf = "[" + ", ".join(json.dumps(c, ensure_ascii=False) for c in g["confusable_with"]) + "]"
        out.append("  {")
        out.append(f'   "id": {g["id"]},')
        out.append(f'   "character": {json.dumps(g["character"], ensure_ascii=False)},')
        out.append(f'   "confusable_with": {conf},')
        out.append(f'   "note": {json.dumps(g["note"], ensure_ascii=False)}')
        out.append("  }" + ("," if i < len(gs) - 1 else ""))
    out.append(" ],")
    out.append(' "metadata": {')
    md = data["metadata"]
    keys = list(md.keys())
    for j, k in enumerate(keys):
        out.append(f'  "{k}": {json.dumps(md[k], ensure_ascii=False)}'
                   + ("," if j < len(keys) - 1 else ""))
    out.append(" }")
    out.append("}")
    return "\n".join(out) + "\n"


def load_simplified_set(path, label):
    if not os.path.exists(path):
        print(f"[PERINGATAN] {path} tidak ada -- pengecekan {label} dilewati.")
        return None
    with open(path, "r", encoding="utf-8") as f:
        arr = json.load(f)
    return {(w.get("simplified") or w.get("id") or "") for w in arr if isinstance(w, dict)}


# --------------------------------------------------------------- validasi --
def validate_schema(obj):
    if "_rusak" in obj:
        return f"JSON rusak: {obj['_rusak']}"
    ch, conf, note = obj.get("character"), obj.get("confusable_with"), obj.get("note")
    if not isinstance(ch, str) or not is_hanzi(ch):
        return "character bukan 1 hanzi"
    if not isinstance(conf, list) or not conf:
        return "confusable_with kosong/bukan list"
    if len(conf) > MAX_CONFUSABLE:
        return f"confusable_with > {MAX_CONFUSABLE}"
    if not all(isinstance(c, str) and is_hanzi(c) for c in conf):
        return "confusable_with berisi non-hanzi/lebih dari 1 karakter"
    if len(set(conf)) != len(conf) or ch in conf:
        return "karakter dobel di dalam grup"
    if not isinstance(note, str) or not (NOTE_MIN <= len(note.strip()) <= NOTE_MAX):
        return f"note kosong/di luar {NOTE_MIN}-{NOTE_MAX} karakter"
    if not re.search(r"[A-Za-z]{3,}", note):
        return "note bukan Bahasa Indonesia (tanpa huruf Latin)"
    return None


def arsipkan(input_path, stamp):
    """Salin (BUKAN pindah) file batch ke arsip_karakter_mirip/batch_<stamp>/ . Gagal arsip
    tidak boleh membatalkan hasil apply."""
    try:
        import shutil
        folder = os.path.join("arsip_karakter_mirip", f"batch_{stamp}")
        os.makedirs(folder, exist_ok=True)
        disalin = []
        for fn in dict.fromkeys([input_path, "kandidat_karakter_mirip.txt",
                                 "prompt_karakter_mirip_1_cari.txt",
                                 "prompt_karakter_mirip_2_verifikasi.txt"]):
            if os.path.exists(fn):
                shutil.copy2(fn, folder)
                disalin.append(os.path.basename(fn))
        print(f"     Arsip : {folder}  ({', '.join(disalin)})")
        print("             (salinan; file asli tetap di tempatnya -- tinggal ditimpa utk batch berikutnya)")
    except OSError as e:
        print(f"     [peringatan] arsip otomatis gagal ({e}); hasil apply tetap sah.")


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    apply_ = "--apply" in sys.argv
    skip_cp = "--skip-checkpoint" in sys.argv
    if not args:
        print(__doc__)
        sys.exit(1)

    with open(args[0], "r", encoding="utf-8", errors="replace") as f:
        raw = f.read()
    data = load_groups()
    groups = data["groups"]
    next_id = max(g["id"] for g in groups) + 1
    existing_sets = [(g["id"], frozenset(group_chars(g))) for g in groups]

    words = load_simplified_set(PATH_WORDS, "app_words.json") or set()
    cidict = None  # lazy (26 MB)

    accepted, rejected, dropped, warnings = [], [], [], []
    seen_batch = []

    for obj in iter_json_objects(raw):
        if "drop" in obj:
            dropped.append((obj.get("character", "?"), obj["drop"]))
            continue
        err = validate_schema(obj)
        label = obj.get("character", "?") + "".join(obj.get("confusable_with", []) if isinstance(obj.get("confusable_with"), list) else [])
        if err:
            rejected.append((label, err))
            continue

        chars = group_chars(obj)
        cset = frozenset(chars)

        # --- keberadaan karakter
        only_cidict = []
        missing = []
        for c in chars:
            if c in words:
                continue
            if cidict is None:
                cidict = load_simplified_set(PATH_CIDICT, "cidict_index.json") or set()
            (only_cidict if c in cidict else missing).append(c)
        if missing:
            rejected.append((label, f"tidak ada di app_words maupun Cidict: {''.join(missing)}"))
            continue

        # --- duplikat
        dup = next((gid for gid, s in existing_sets if cset <= s), None)
        if dup is not None:
            rejected.append((label, f"sudah tercakup penuh di grup id={dup}"))
            continue
        if any(cset <= s for s in seen_batch):
            rejected.append((label, "duplikat/turunan kandidat lain di batch ini"))
            continue

        # --- peringatan
        w = []
        if only_cidict:
            w.append(f"hanya di Cidict: {''.join(only_cidict)}")
        sup = [gid for gid, s in existing_sets if s < cset]
        if sup:
            w.append("memperluas grup id=" + ",".join(map(str, sup)) + " (grup lama tetap ada)")
        part = [gid for gid, s in existing_sets if len(s & cset) >= 2 and not s < cset]
        if part:
            w.append("beririsan >=2 karakter dgn id=" + ",".join(map(str, part)))

        entry = {"id": next_id, "character": obj["character"],
                 "confusable_with": list(obj["confusable_with"]), "note": obj["note"].strip()}
        next_id += 1
        accepted.append(entry)
        seen_batch.append(cset)
        if w:
            warnings.append((entry["id"], "".join(chars), w))

    # ------------------------------------------------------------ laporan --
    print("=" * 70)
    print(f"Grup lama: {len(groups)} | karakter unik lama: {count_unique_chars(groups)} "
          f"(metadata: {data['metadata'].get('total_characters')})")
    print(f"DITERIMA: {len(accepted)} | DITOLAK: {len(rejected)} | "
          f"di-drop verifikator: {len(dropped)}")
    print("=" * 70)
    for e in accepted:
        print(f"  + id={e['id']:<3} {e['character']}{''.join(e['confusable_with'])}  -- {e['note'][:70]}")
    if warnings:
        print("\n[PERINGATAN] (tetap diterima, cek manual):")
        for gid, cs, w in warnings:
            print(f"  ! id={gid} {cs}: {'; '.join(w)}")
    if rejected:
        print("\n[DITOLAK]:")
        for lab, why in rejected:
            print(f"  x {lab}: {why}")
    if dropped:
        print("\n[DI-DROP oleh prompt verifikasi]:")
        for lab, why in dropped:
            print(f"  - {lab}: {why}")

    if not apply_:
        print("\n(DRY-RUN -- tidak ada yang ditulis. Tambah --apply setelah dicek.)")
        return
    if not accepted:
        print("\nTidak ada yang diterima -- tidak ada yang ditulis.")
        return

    # --------------------------------------------------------------- apply --
    if not skip_cp:
        if not os.path.exists("checkpoint.py"):
            print("\n[BERHENTI] checkpoint.py tidak ada di folder ini. "
                  "Jalankan dari C:\\mandarin_app atau pakai --skip-checkpoint.")
            sys.exit(2)
        r = subprocess.run([sys.executable, "checkpoint.py", "save"])
        if r.returncode != 0:
            print("\n[BERHENTI] checkpoint.py save gagal -- tidak menulis apa pun.")
            sys.exit(2)

    stamp = time.strftime("%Y%m%d_%H%M%S")
    bak = PATH_GROUPS + f".bak_{stamp}"
    with open(PATH_GROUPS, "rb") as fi, open(bak, "wb") as fo:
        fo.write(fi.read())

    groups.extend(accepted)
    md = data["metadata"]
    md["total_groups"] = len(groups)
    md["total_characters"] = count_unique_chars(groups)
    md["notes"] = (md.get("notes", "").rstrip() +
                   f" | Ekspansi {time.strftime('%Y-%m-%d')}: +{len(accepted)} grup "
                   f"(id {accepted[0]['id']}-{accepted[-1]['id']}).")

    tmp = PATH_GROUPS + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="\n") as f:
        f.write(dump_groups(data))
    json.load(open(tmp, "r", encoding="utf-8"))  # pastikan valid sebelum menimpa
    os.replace(tmp, PATH_GROUPS)
    print(f"\n[OK] Ditulis: {len(accepted)} grup baru. Total sekarang "
          f"{md['total_groups']} grup / {md['total_characters']} karakter unik.")
    print(f"     Backup: {bak}")
    arsipkan(args[0], stamp)


if __name__ == "__main__":
    main()

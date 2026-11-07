"""
perbaiki_note_karakter_mirip.py -- ganti NOTE grup yang SUDAH ADA di data/confusion_groups.json.

DEFAULT = DRY-RUN (hanya menampilkan perbandingan LAMA vs BARU, tidak menulis apa pun).
Tambah --apply untuk menulis. Sebelum menulis otomatis:
  1. python checkpoint.py save   (subprocess)
  2. backup data/confusion_groups.json.bak_<timestamp>
  3. tulis atomik (.tmp lalu rename), format file sama persis dengan aslinya

Cara pakai (dari C:\\mandarin_app, satu folder dgn gabungkan_karakter_mirip.py):
    python perbaiki_note_karakter_mirip.py perbaikan_note_lama.txt            # dry-run
    python perbaiki_note_karakter_mirip.py perbaikan_note_lama.txt --apply    # tulis

Format input (NDJSON, satu objek per baris):
    {"id": 35, "character": "末", "note": "catatan baru ..."}

Pengaman:
  - id harus ada, dan "character" harus SAMA dengan karakter utama grup itu (cegah salah id)
  - hanya field "note" yang berubah; grup lain, id, karakter, confusable_with tidak disentuh
    (diverifikasi ulang sebelum menulis)
  - note baru divalidasi seperti di gabungkan_karakter_mirip.py (panjang, Bahasa Indonesia)
  - idempoten: menjalankan ulang file yang sama setelah --apply -> "tidak ada perubahan"
"""

import json
import os
import re
import subprocess
import sys
import time

from gabungkan_karakter_mirip import (NOTE_MAX, NOTE_MIN, PATH_GROUPS, count_unique_chars,
                                      dump_groups, iter_json_objects, load_groups)


def cek_note(note):
    if not isinstance(note, str) or not (NOTE_MIN <= len(note.strip()) <= NOTE_MAX):
        return f"note kosong/di luar {NOTE_MIN}-{NOTE_MAX} karakter"
    if not re.search(r"[A-Za-z]{3,}", note):
        return "note bukan Bahasa Indonesia (tanpa huruf Latin)"
    return None


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    apply_ = "--apply" in sys.argv
    skip_cp = "--skip-checkpoint" in sys.argv
    if not args:
        print(__doc__)
        sys.exit(1)

    with open(args[0], "r", encoding="utf-8", errors="replace") as f:
        patches = list(iter_json_objects(f.read()))
    data = load_groups()
    by_id = {g["id"]: g for g in data["groups"]}
    before = json.loads(json.dumps(data["groups"]))  # salinan dalam utk verifikasi akhir

    ok, skip, tolak, seen = [], [], [], set()
    for p in patches:
        if "_rusak" in p:
            tolak.append(("?", f"JSON rusak: {p['_rusak']}"))
            continue
        gid, ch, note = p.get("id"), p.get("character"), p.get("note")
        lab = f"id={gid} {ch}"
        if gid in seen:
            tolak.append((lab, "id dobel di file perbaikan"))
            continue
        seen.add(gid)
        if gid not in by_id:
            tolak.append((lab, "id tidak ada di database"))
            continue
        g = by_id[gid]
        if g["character"] != ch:
            tolak.append((lab, f"karakter utama id ini di database adalah {g['character']}, bukan {ch}"))
            continue
        err = cek_note(note)
        if err:
            tolak.append((lab, err))
            continue
        if g["note"].strip() == note.strip():
            skip.append(lab)
            continue
        ok.append((g, note.strip()))

    print("=" * 70)
    print(f"Grup di database: {len(data['groups'])} | siap diganti: {len(ok)} | "
          f"sudah sama: {len(skip)} | ditolak: {len(tolak)}")
    print("=" * 70)
    for g, note in ok:
        print(f"\nid={g['id']}  {g['character']}{''.join(g['confusable_with'])}")
        print(f"  LAMA: {g['note']}")
        print(f"  BARU: {note}")
    if skip:
        print("\n[SUDAH SAMA]:", ", ".join(skip))
    if tolak:
        print("\n[DITOLAK]:")
        for lab, why in tolak:
            print(f"  x {lab}: {why}")

    if not apply_:
        print("\n(DRY-RUN -- tidak ada yang ditulis. Tambah --apply setelah dicek.)")
        return
    if not ok:
        print("\nTidak ada perubahan -- tidak ada yang ditulis.")
        return

    for g, note in ok:
        g["note"] = note

    # verifikasi: hanya note dari id terdaftar yang boleh berbeda
    ids_ok = {g["id"] for g, _ in ok}
    for old, new in zip(before, data["groups"]):
        assert old["id"] == new["id"] and old["character"] == new["character"] \
            and old["confusable_with"] == new["confusable_with"], f"struktur berubah di id={old['id']}"
        if old["id"] not in ids_ok:
            assert old["note"] == new["note"], f"note id={old['id']} berubah tanpa diminta"
    assert len(before) == len(data["groups"])

    if not skip_cp:
        if not os.path.exists("checkpoint.py"):
            print("\n[BERHENTI] checkpoint.py tidak ada di folder ini. Jalankan dari C:\\mandarin_app.")
            sys.exit(2)
        r = subprocess.run([sys.executable, "checkpoint.py", "save"])
        if r.returncode != 0:
            print("\n[BERHENTI] checkpoint.py save gagal -- tidak menulis apa pun.")
            sys.exit(2)

    stamp = time.strftime("%Y%m%d_%H%M%S")
    bak = PATH_GROUPS + f".bak_{stamp}"
    with open(PATH_GROUPS, "rb") as fi, open(bak, "wb") as fo:
        fo.write(fi.read())

    md = data["metadata"]
    md["total_groups"] = len(data["groups"])
    md["total_characters"] = count_unique_chars(data["groups"])
    md["notes"] = (md.get("notes", "").rstrip() +
                   f" | Perbaikan note {time.strftime('%Y-%m-%d')}: {len(ok)} grup lama "
                   f"(id {', '.join(str(i) for i in sorted(ids_ok))}).")

    tmp = PATH_GROUPS + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="\n") as f:
        f.write(dump_groups(data))
    json.load(open(tmp, "r", encoding="utf-8"))
    os.replace(tmp, PATH_GROUPS)
    print(f"\n[OK] {len(ok)} note diganti. Total tetap {md['total_groups']} grup / "
          f"{md['total_characters']} karakter unik.")
    print(f"     Backup: {bak}")


if __name__ == "__main__":
    main()

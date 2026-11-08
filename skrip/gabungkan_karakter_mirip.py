#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
gabungkan_karakter_mirip.py  (v1, gelombang 1: KARAKTER_MIRIP_FINAL_ACCEPTED.csv)

Hanya memakai pustaka standar Python.

Mode:
  (tanpa opsi)       DRY-RUN. Tidak mengubah confusion_groups.json.
                     Menulis hasil_gabung/preview_grup_baru.csv + laporan di layar.
  --sample N         Menulis hasil_gabung/confusion_groups_TEST.json = 160 grup lama + N grup contoh
                     (untuk tes tampilan). File asli tidak disentuh.
  --apply            Backup (.bak_before_apply_*), checkpoint.py save (bila ada), lalu menulis
                     confusion_groups.json dengan SEMUA grup baru.
  --notes-override F JSON {"karakter|karakter|...": "catatan"} (kunci = anggota grup diurutkan
                     dengan '|') untuk mengganti catatan otomatis, terutama grup 3+ karakter.

  --merge            Mode PENGGABUNGAN GRUP TUMPANG TINDIH (grup lama + grup baru). Hanya menghasilkan usulan:
                     hasil_gabung/usulan_gabung.csv dan hasil_gabung/confusion_groups_MERGED_DRAF.json.
                     Tidak mengubah confusion_groups.json. (--apply tidak berlaku di mode ini.)
  --keluarga F       JSON keluarga manual (default keluarga_manual.json): {"seeds": [...], "pasangan_manual": [...]}
  --cap N            Ukuran grup maksimal saat menggabung (default 6).
                     Gabung otomatis hanya bila dua grup berbagi >=2 karakter, atau 1 karakter yang menjadi hub
                     di kedua grup; gabungan lain lewat "seeds" di keluarga_manual.json.

Aturan (disepakati):
  - Pasangan yang kedua karakternya sudah satu grup lama  -> diabaikan.
  - Pasangan yang menyentuh grup lama yang berbeda        -> tetap dibuat grup BARU (grup lama tidak diubah).
  - Komponen terhubung <= 4 karakter -> satu grup. Lebih besar -> dipecah, maks 4 anggota per grup.
  - Tingkat pasangan = tingkat Claude; bila kosong, tingkat GPT; bila keduanya kosong -> 3 (ditandai).
  - Tingkat grup = yang PALING LONGGAR (angka terbesar) dari pasangan di dalam grup.
  - Skema: {id, character, confusable_with, note, tier}; grup lama tidak punya tier (dianggap T1).
"""
import argparse
import csv
import json
import re
import shutil
import subprocess
import sys
from collections import Counter, defaultdict
from datetime import datetime
from itertools import combinations
from pathlib import Path

MAX_MEMBERS = 4
OUT_DIR = Path("hasil_gabung")


# ---------------------------------------------------------------- baca data
def parse_tier(s):
    m = re.search(r"T([123])", s or "")
    return int(m.group(1)) if m else None


def parse_note(s, key):
    s = (s or "").strip()
    i = s.find(key + "=")
    if i < 0:
        return ""
    s = s[i + len(key) + 1:]
    return s.split(" | ")[0].strip()


def load_pairs(path):
    pairs, order, dup = {}, {}, 0
    with open(path, encoding="utf-8-sig", newline="") as f:
        for r in csv.DictReader(f):
            a, b = r["a"].strip(), r["b"].strip()
            if not a or not b or a == b:
                continue
            key = frozenset((a, b))
            if key in pairs:
                dup += 1
                continue
            for ch in (a, b):
                order.setdefault(ch, len(order))
            t_c, t_g = parse_tier(r.get("claude_tier_data")), parse_tier(r.get("gpt_tier_data"))
            tier = t_c or t_g or 3
            tier_src = "claude" if t_c else ("gpt" if t_g else "DEFAULT")
            n_c = parse_note(r.get("claude_reason_data"), "claude_note")
            n_g = (parse_note(r.get("gpt_reason_data"), "gpt_difference_note")
                   or parse_note(r.get("gpt_reason_data"), "gpt_audit_note"))
            pairs[key] = {
                "a": a, "b": b, "tier": tier, "tier_src": tier_src,
                "note": n_c or n_g, "note_src": "claude" if n_c else ("gpt" if n_g else "KOSONG"),
                "batch": r.get("source_batches", ""),
            }
    return pairs, order, dup


# ---------------------------------------------------------------- bangun grup
def components(pairs):
    adj = defaultdict(set)
    for k in pairs:
        a, b = tuple(k)
        adj[a].add(b)
        adj[b].add(a)
    seen, comps = set(), []
    for start in adj:
        if start in seen:
            continue
        stack, comp = [start], set()
        while stack:
            x = stack.pop()
            if x in comp:
                continue
            comp.add(x)
            stack.extend(adj[x] - comp)
        seen |= comp
        comps.append(comp)
    return comps, adj


def split_big(nodes, pairs, adj, order):
    """Tutup semua pasangan dengan grup <= MAX_MEMBERS (satu karakter boleh muncul di >1 grup)."""
    edges = {k for k in pairs if k <= nodes}
    uncovered = set(edges)
    out = []
    while uncovered:
        deg = Counter(x for e in uncovered for x in e)
        hub = max(deg, key=lambda x: (deg[x], -order[x]))
        nb = [y for y in adj[hub] if frozenset((hub, y)) in uncovered]
        nb.sort(key=lambda y: (pairs[frozenset((hub, y))]["tier"], -deg[y], order[y]))
        chosen = [hub]
        first_tier = pairs[frozenset((hub, nb[0]))]["tier"]
        while nb and len(chosen) < MAX_MEMBERS:
            def score(y):
                mutual = sum(1 for c in chosen[1:] if frozenset((c, y)) in pairs)
                t = pairs[frozenset((hub, y))]["tier"]
                return (abs(t - first_tier), -mutual, -deg[y], order[y])
            nb.sort(key=score)
            chosen.append(nb.pop(0))
        for a, b in combinations(chosen, 2):
            uncovered.discard(frozenset((a, b)))
        out.append(chosen)
    return out


def make_group(members, pairs, order, adj):
    inner = [k for k in pairs if k <= set(members)]
    deg = Counter(x for k in inner for x in k)
    hub = max(members, key=lambda x: (deg[x], -order[x]))
    spokes = sorted([m for m in members if m != hub], key=lambda x: order[x])
    tier = max(pairs[k]["tier"] for k in inner)
    notes, seen = [], set()
    for k in sorted(inner, key=lambda k: min(order[x] for x in k)):
        n = pairs[k]["note"]
        if n and n not in seen:
            seen.add(n)
            notes.append(n)
    return {
        "character": hub, "confusable_with": spokes, "tier": tier,
        "note": ("; ".join(n.rstrip(".。 ") for n in notes) + ".") if notes else "", "n_pairs": len(inner),
        "complete": len(inner) == len(members) * (len(members) - 1) // 2,
        "note_src": "/".join(sorted({pairs[k]["note_src"] for k in inner})),
        "tier_src": "/".join(sorted({pairs[k]["tier_src"] for k in inner})),
        "tier_mixed": len({pairs[k]["tier"] for k in inner}) > 1,
    }


def build(pairs, order, old_groups):
    mem = defaultdict(set)
    for g in old_groups:
        for c in [g["character"]] + g["confusable_with"]:
            mem[c].add(g["id"])
    redundant = {k for k in pairs if mem[tuple(k)[0]] & mem[tuple(k)[1]]}
    live = {k: v for k, v in pairs.items() if k not in redundant}
    comps, adj = components(live)
    comps.sort(key=lambda c: min(order[x] for x in c))
    groups = []
    for comp in comps:
        if len(comp) <= MAX_MEMBERS:
            sets = [sorted(comp, key=lambda x: order[x])]
        else:
            sets = split_big(comp, live, adj, order)
        for members in sets:
            g = make_group(members, live, order, adj)
            g["from_component"] = len(comp)
            g["touch_old"] = sorted(set().union(*(mem[m] for m in members)))
            groups.append(g)
    return groups, redundant


# ---------------------------------------------------------------- mode --merge
def tier_compatible(a, b, semua=False):
    """Bawaan: T1 dan T2 boleh dicampur; T3 hanya dengan T3. Dengan semua=True semua tingkat boleh dicampur."""
    return True if semua else ((a <= 2 and b <= 2) or (a == 3 and b == 3))


def pick_hub(parts, order_hint):
    cnt = Counter(c for p in parts for c in p["m"])
    first_hub = parts[0]["hub"]
    return max(cnt, key=lambda c: (cnt[c], c == first_hub, -order_hint.get(c, 10**6)))


def new_item(parts, tier=None):
    m = set().union(*(p["m"] for p in parts))
    t = tier if tier is not None else max(p["tier"] for p in parts)
    notes = []
    for p in parts:
        for n in p["notes"]:
            if n and n not in notes:
                notes.append(n)
    return {"m": m, "tier": t, "parts": parts, "notes": notes,
            "src": [x for p in parts for x in p["src"]],
            "old_ids": sorted({i for p in parts for i in p["old_ids"]})}


def absorb_subsets(items, semua=False):
    """Grup yang anggotanya seluruhnya ada di grup lain diserap, kecuali T1/T2 yang berada di dalam T3
    (supaya pasangan T1/T2 tidak hanya muncul di grup T3)."""
    changed = True
    while changed:
        changed = False
        for i, a in enumerate(items):
            for j, b in enumerate(items):
                if i != j and a["m"] < b["m"] and (semua or not (a["tier"] <= 2 and b["tier"] == 3)):
                    b["parts"] += a["parts"]
                    b["src"] = b["src"] + a["src"]
                    b["old_ids"] = sorted(set(b["old_ids"]) | set(a["old_ids"]))
                    b["kind"] = "gabung" if b.get("kind") != "seed" else "seed"
                    del items[i]
                    changed = True
                    break
            if changed:
                break
    return items


def merge_groups(old, new_groups, start_id, seeds, manual_pairs, cap, order, semua=False, berbagi="hub"):
    items = []
    for g in old:
        m = {g["character"], *g["confusable_with"]}
        items.append({"m": m, "hub": g["character"], "tier": 1, "notes": [g["note"]],
                      "src": [f"L{g['id']}"], "old_ids": [g["id"]], "kind": "lama"})
    for i, g in enumerate(new_groups, start_id):
        m = {g["character"], *g["confusable_with"]}
        items.append({"m": m, "hub": g["character"], "tier": g["tier"], "notes": [g["note"]],
                      "src": [f"B{i}"], "old_ids": [], "kind": "baru"})
    for mp in manual_pairs:
        m = set(mp["anggota"])
        items.append({"m": m, "hub": mp["anggota"][0], "tier": mp.get("tier", 2), "notes": [mp.get("note", "")],
                      "src": ["M"], "old_ids": [], "kind": "manual"})
    for it in items:
        it["parts"] = [dict(m=it["m"], hub=it["hub"], tier=it["tier"], notes=it["notes"],
                            src=it["src"], old_ids=it["old_ids"])]

    # 1) seed keluarga: grup yang seluruh anggotanya ada di seed diserap; seed tidak diubah lagi
    fixed = []
    for sd in seeds:
        S = set(sd)
        absorbed = [it for it in items if it["m"] <= S]
        items = [it for it in items if it not in absorbed]
        if absorbed:
            parts = [p for it in absorbed for p in it["parts"]]
            ni = new_item(parts)
        else:
            ni = new_item([dict(m=S, hub=sd[0], tier=2, notes=[""], src=["SEED"], old_ids=[])])
        ni["m"] = S
        ni["hub"] = pick_hub(ni["parts"], order)
        ni["kind"] = "seed"
        fixed.append(ni)

    # 2) grup yang merupakan bagian dari grup lain dibuang (diserap)
    items = absorb_subsets(items, semua)

    # 3) gabung bertahap grup yang berbagi karakter (maks cap anggota, T1/T2 boleh campur, T3 hanya T3;
    #    syarat berbagi: >=2 karakter, atau 1 karakter yang menjadi hub kedua grup)
    while True:
        best = None
        for i in range(len(items)):
            for j in range(i + 1, len(items)):
                a, b = items[i], items[j]
                shared = a["m"] & b["m"]
                ov = len(shared)
                if not ov or not tier_compatible(a["tier"], b["tier"], semua):
                    continue
                # Gabung hanya bila berbagi >=2 karakter, atau 1 karakter yang menjadi HUB di kedua grup
                # (mencegah rantai A-B-C-D yang ujungnya tidak mirip).
                if berbagi == "hub" and ov < 2 and not (a["hub"] in shared and b["hub"] in shared):
                    continue
                u = len(a["m"] | b["m"])
                if u > cap:
                    continue
                sc = (ov, -u, -i)
                if best is None or sc > best[0]:
                    best = (sc, i, j)
        if not best:
            break
        _, i, j = best
        a, b = items[i], items[j]
        ni = new_item(a["parts"] + b["parts"])
        ni["hub"] = pick_hub(ni["parts"], order)
        ni["kind"] = "gabung"
        items[i] = ni
        del items[j]
    items = absorb_subsets(items, semua)

    for it in items:
        if "hub" not in it or it["hub"] not in it["m"]:
            it["hub"] = pick_hub(it["parts"], order)
        if len(it["parts"]) == 1 and it["kind"] in ("lama", "baru", "manual"):
            pass
        elif it["kind"] not in ("gabung",):
            it["kind"] = it.get("kind", "gabung")
    allg = fixed + items
    # id: grup yang memuat grup lama memakai id lama terkecil; sisanya id baru berurutan
    nxt = start_id + len(new_groups) + 1  # id sementara untuk manual
    used = set()
    for g in sorted(allg, key=lambda x: (min(x["old_ids"]) if x["old_ids"] else 10**9)):
        if g["old_ids"]:
            g["id"] = min(g["old_ids"])
            used.add(g["id"])
    nxt = max(g["id"] for g in old) + 1
    for g in sorted([g for g in allg if not g["old_ids"]], key=lambda x: min(order.get(c, 10**6) for c in x["m"])):
        g["id"] = nxt
        nxt += 1
    return sorted(allg, key=lambda g: g["id"])


def run_merge(a, data, old, groups, order, start_id):
    kel = Path(a.keluarga)
    seeds, manual = [], []
    if kel.exists():
        k = json.load(open(kel, encoding="utf-8"))
        seeds, manual = k.get("seeds", []), k.get("pasangan_manual", [])
    for sd in seeds:
        assert all(len(c) == 1 for c in sd), f"seed tidak valid: {sd}"
    cap = a.cap if a.cap > 0 else 10**6
    allg = merge_groups(old, groups, start_id, seeds, manual, cap, order, a.semua_tingkat, a.berbagi)

    def kind_label(g):
        n_old = len(g["old_ids"])
        n_src = len(g["src"])
        if g["kind"] == "seed":
            return "KELUARGA"
        if n_src == 1:
            return {"lama": "TETAP_LAMA", "baru": "BARU_UTUH", "manual": "MANUAL"}[g["kind"]]
        return "GABUNG"

    OUT_DIR.mkdir(exist_ok=True)
    rows, out_groups = [], []
    for g in allg:
        hub = g["hub"]
        spokes = sorted([c for c in g["m"] if c != hub], key=lambda x: order.get(x, 10**6))
        lab = kind_label(g)
        single = lab in ("TETAP_LAMA", "BARU_UTUH", "MANUAL")
        note = g["notes"][0] if single else "; ".join(n.rstrip(".。 ") for n in g["notes"] if n) + "."
        old_changed = bool(g["old_ids"]) and lab in ("GABUNG", "KELUARGA")
        rows.append([g["id"], hub, "".join(spokes), g["tier"], 1 + len(spokes), lab,
                     "+".join(g["src"]), ",".join(map(str, g["old_ids"])), "ya" if old_changed else "",
                     "ya" if not single else "", note])
        out_groups.append({"id": g["id"], "character": hub, "confusable_with": spokes,
                           "note": note, **({"tier": g["tier"]} if not (g["old_ids"] and single) else {})})
    with open(OUT_DIR / "usulan_gabung.csv", "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        w.writerow(["id_usulan", "character", "confusable_with", "tier", "jumlah_anggota", "jenis", "sumber",
                    "id_lama_terlibat", "mengubah_grup_lama", "perlu_catatan_baru", "note_draf"])
        w.writerows(rows)
    draf = {"groups": out_groups, "metadata": dict(data["metadata"])}
    draf["metadata"]["total_groups"] = len(out_groups)
    draf["metadata"]["notes"] += " | DRAF GABUNG (belum resmi): catatan gabungan masih draf."
    json.dump(draf, open(OUT_DIR / "confusion_groups_MERGED_DRAF.json", "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)

    n_before = len(old) + len(groups) + len(manual)
    print("=" * 60)
    print(f"MODE GABUNG (cap {a.cap or 'tanpa batas'}, {'semua tingkat boleh campur' if a.semua_tingkat else 'T1/T2 boleh campur, T3 hanya dengan T3'}, berbagi={a.berbagi})")
    print(f"Sebelum: {len(old)} lama + {len(groups)} baru + {len(manual)} manual = {n_before} grup")
    print(f"Sesudah: {len(allg)} grup")
    print("  per jenis:", dict(Counter(r[5] for r in rows)))
    print("  per tingkat:", dict(sorted(Counter(r[3] for r in rows).items())))
    print("  per jumlah anggota:", dict(sorted(Counter(r[4] for r in rows).items())))
    print(f"  grup LAMA yang berubah (digabung): {sum(1 for r in rows if r[8] == 'ya')}")
    print(f"  grup yang perlu catatan baru: {sum(1 for r in rows if r[9] == 'ya')}")
    print("Pratinjau: hasil_gabung/usulan_gabung.csv dan confusion_groups_MERGED_DRAF.json")
    print("\n(mode gabung: confusion_groups.json TIDAK diubah)")


# ---------------------------------------------------------------- tulis
def key_of(g):
    return "|".join(sorted([g["character"]] + g["confusable_with"]))


def write_preview(groups, start_id, path):
    OUT_DIR.mkdir(exist_ok=True)
    with open(path, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        w.writerow(["id_baru", "character", "confusable_with", "tier", "jumlah_anggota", "jumlah_pasangan",
                    "klik_lengkap", "dari_komponen", "tingkat_campuran", "sumber_tingkat", "sumber_catatan",
                    "menyentuh_grup_lama", "perlu_tinjau_catatan", "note"])
        for i, g in enumerate(groups, start_id):
            review = g["n_pairs"] > 1 or "gpt" in g["note_src"] or "KOSONG" in g["note_src"]
            w.writerow([i, g["character"], "".join(g["confusable_with"]), g["tier"],
                        1 + len(g["confusable_with"]), g["n_pairs"], "ya" if g["complete"] else "tidak",
                        g["from_component"], "ya" if g["tier_mixed"] else "", g["tier_src"], g["note_src"],
                        ",".join(map(str, g["touch_old"])), "ya" if review else "", g["note"]])


def to_json_group(i, g):
    return {"id": i, "character": g["character"], "confusable_with": g["confusable_with"],
            "note": g["note"], "tier": g["tier"]}


def pick_sample(groups, n):
    """Contoh beragam: menyentuh grup lama, T1/T2/T3, 3+ anggota, hasil pemecahan."""
    buckets = [
        [g for g in groups if g["touch_old"]],
        [g for g in groups if g["tier"] == 1],
        [g for g in groups if g["tier"] == 2 and len(g["confusable_with"]) == 1],
        [g for g in groups if g["tier"] == 3 and len(g["confusable_with"]) == 1],
        [g for g in groups if len(g["confusable_with"]) >= 2 and g["from_component"] <= MAX_MEMBERS],
        [g for g in groups if g["from_component"] > MAX_MEMBERS],
    ]
    chosen, used = [], set()
    r = 0
    while len(chosen) < n and any(buckets):
        b = buckets[r % len(buckets)]
        while b and key_of(b[0]) in used:
            b.pop(0)
        if b:
            g = b.pop(0)
            used.add(key_of(g))
            chosen.append(g)
        r += 1
        if r > 1000:
            break
    return chosen


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--groups", default="data/confusion_groups.json")
    ap.add_argument("--accepted", default="KARAKTER_MIRIP_FINAL_ACCEPTED.csv")
    ap.add_argument("--notes-override", default=None)
    ap.add_argument("--sample", type=int, default=0)
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--merge", action="store_true")
    ap.add_argument("--keluarga", default="keluarga_manual.json")
    ap.add_argument("--cap", type=int, default=6, help="ukuran maks grup; 0 = tanpa batas")
    ap.add_argument("--semua-tingkat", action="store_true", help="T1, T2, T3 boleh dicampur (grup bertingkat paling longgar)")
    ap.add_argument("--berbagi", choices=["hub", "bebas"], default="hub",
                    help="hub: gabung bila berbagi >=2 karakter atau 1 karakter yang jadi hub kedua grup; bebas: cukup berbagi 1 karakter")
    a = ap.parse_args()

    data = json.load(open(a.groups, encoding="utf-8"))
    old = data["groups"]
    pairs, order, dup = load_pairs(a.accepted)
    groups, redundant = build(pairs, order, old)

    if a.notes_override:
        ov = json.load(open(a.notes_override, encoding="utf-8"))
        n = 0
        for g in groups:
            if key_of(g) in ov:
                g["note"], g["note_src"] = ov[key_of(g)], "override"
                n += 1
        print(f"Catatan override dipakai: {n}")

    start_id = max(g["id"] for g in old) + 1
    if a.merge:
        if a.apply:
            sys.exit("BATAL: --apply belum tersedia untuk mode --merge (periksa usulan dulu).")
        run_merge(a, data, old, groups, order, start_id)
        return
    # ---- laporan
    print("=" * 60)
    print(f"Grup lama: {len(old)} | pasangan di ACCEPTED: {len(pairs)} (duplikat dibuang: {dup})")
    print(f"Pasangan redundan (sudah satu grup lama, diabaikan): {len(redundant)}")
    print(f"Pasangan yang dipakai: {len(pairs) - len(redundant)}")
    print(f"GRUP BARU: {len(groups)}  (id {start_id}..{start_id + len(groups) - 1})")
    print("  per tingkat:", dict(sorted(Counter(g['tier'] for g in groups).items())))
    print("  per jumlah anggota:", dict(sorted(Counter(1 + len(g['confusable_with']) for g in groups).items())))
    print(f"  hasil pemecahan komponen >{MAX_MEMBERS}: {sum(1 for g in groups if g['from_component'] > MAX_MEMBERS)}")
    print(f"  komponen <=4 yang bukan klik lengkap: "
          f"{sum(1 for g in groups if g['from_component'] <= MAX_MEMBERS and not g['complete'])}")
    print(f"  tingkat campuran: {sum(1 for g in groups if g['tier_mixed'])}")
    print(f"  tingkat tanpa sumber (default T3): {sum(1 for g in groups if 'DEFAULT' in g['tier_src'])}")
    print(f"  catatan dari GPT/kosong: {sum(1 for g in groups if 'gpt' in g['note_src'] or 'KOSONG' in g['note_src'])}")
    print(f"  menyentuh grup lama: {sum(1 for g in groups if g['touch_old'])}")
    print(f"  perlu catatan gabungan (2+ pasangan): {sum(1 for g in groups if g['n_pairs'] > 1)}")
    bad = [g for g in groups if any(len(c) != 1 for c in [g['character']] + g['confusable_with'])]
    print(f"  anggota bukan 1 karakter: {len(bad)}")
    total_chars = len({c for g in old for c in [g['character']] + g['confusable_with']} |
                      {c for g in groups for c in [g['character']] + g['confusable_with']})
    print(f"Karakter unik setelah digabung: {total_chars}")

    OUT_DIR.mkdir(exist_ok=True)
    prev = OUT_DIR / "preview_grup_baru.csv"
    write_preview(groups, start_id, prev)
    print(f"Pratinjau: {prev}")

    if a.sample:
        smp = pick_sample(list(groups), a.sample)
        ids = {id(g): start_id + i for i, g in enumerate(groups)}
        test = {"groups": old + [to_json_group(ids[id(g)], g) for g in smp], "metadata": dict(data["metadata"])}
        test["metadata"]["notes"] += f" | SAMPEL UJI {datetime.now():%Y-%m-%d}: +{len(smp)} grup (belum resmi)."
        test["metadata"]["total_groups"] = len(test["groups"])
        tp = OUT_DIR / "confusion_groups_TEST.json"
        json.dump(test, open(tp, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
        print(f"Sampel uji ditulis: {tp} (+{len(smp)} grup)")
        for g in smp:
            print(f"  id {ids[id(g)]}: T{g['tier']} {g['character']} <- {''.join(g['confusable_with'])}"
                  f"{'  [sentuh grup lama ' + ','.join(map(str, g['touch_old'])) + ']' if g['touch_old'] else ''}")

    if a.apply:
        if bad:
            sys.exit("BATAL: ada anggota yang bukan 1 karakter.")
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        bak = f"{a.groups}.bak_before_apply_{stamp}"
        shutil.copy2(a.groups, bak)
        print(f"Backup: {bak}")
        if Path("checkpoint.py").exists():
            subprocess.run([sys.executable, "checkpoint.py", "save"], check=False)
        data["groups"] = old + [to_json_group(start_id + i, g) for i, g in enumerate(groups)]
        data["metadata"]["total_groups"] = len(data["groups"])
        data["metadata"]["total_characters"] = total_chars
        data["metadata"]["notes"] += (f" | Ekspansi {datetime.now():%Y-%m-%d} (P1-P4 gelombang 1, FINAL_ACCEPTED): "
                                       f"+{len(groups)} grup (id {start_id}-{start_id + len(groups) - 1}), field tier ditambahkan.")
        json.dump(data, open(a.groups, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
        print(f"APPLY selesai: {len(data['groups'])} grup.")
    else:
        print("\n(dry-run: confusion_groups.json TIDAK diubah)")


if __name__ == "__main__":
    main()

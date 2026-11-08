# -*- coding: utf-8 -*-
r"""
scan_kamus.py -- PEMINDAI BACA-SAJA untuk proyek Mandarin Interaktif.

Tugas: menelusuri file apa saja yang dipakai langsung oleh kamus.html
(<script src>, <link href>, fetch('data/...'), url(...), dst., secara
berantai/rekursif), lalu mengelompokkan sisanya, supaya Anda tahu persis
file mana yang perlu diunggah ke repo GitHub.

TIDAK mengubah, memindah, atau menghapus file asli. Satu-satunya yang
ditulis: laporan_scan_kamus.txt, daftar_upload_WAJIB.txt,
daftar_upload_TERKAIT.txt, gitignore_usulan.txt (di folder tempat skrip
dijalankan), dan -- hanya kalau Anda minta lewat --stage -- SALINAN file
ke folder staging.

Cara pakai (dari folder C:\mandarin_app):
    python scan_kamus.py
    python scan_kamus.py --root C:\mandarin_app --entry kamus.html
    python scan_kamus.py --stage C:\mandarin_repo_staging          (salin WAJIB)
    python scan_kamus.py --stage C:\mandarin_repo_staging --termasuk-terkait

Kirim isi laporan_scan_kamus.txt ke Claude.
"""
import argparse
import collections
import fnmatch
import glob
import gzip
import io
import os
import re
import shutil
import sys
from pathlib import Path

REF_EXT = ("json", "js", "mjs", "css", "html", "htm", "txt", "csv", "tsv", "png",
           "jpg", "jpeg", "gif", "svg", "webp", "ico", "woff", "woff2", "ttf",
           "otf", "mp3", "wav", "ogg", "m4a", "mp4", "webm", "md", "wasm")
QUOTED = re.compile(
    r"""['"`]([^'"`\s<>()]{1,240}\.(?:%s))(?:[?#][^'"`]*)?['"`]""" % "|".join(REF_EXT),
    re.I)
CSSURL = re.compile(r"""url\(\s*['"]?([^'")\s]+)['"]?\s*\)""", re.I)
ATTR = re.compile(r"""(?:src|href)\s*=\s*['"]([^'"]+)['"]""", re.I)
FETCH_DYN = re.compile(r"""(?:fetch|import|loadJSON|getJSON)\s*\(\s*([^'"`)\s][^)]*|`[^`]*\$\{[^`]*`|['"][^'"]*['"]\s*\+[^)]*)\)""")
TEMPL = re.compile(r"\$\{[^}]*\}")
CONCAT = re.compile(
    r"""['"]([^'"\n]*)['"]\s*\+\s*[A-Za-z_$][\w$.\[\]()]*\s*\+\s*['"]([^'"\n]*\.(?:%s))['"]""" % "|".join(REF_EXT),
    re.I)
TEXT_EXT = {".html", ".htm", ".js", ".mjs", ".css"}
MAX_POLA = 80  # pola yang cocok >80 file dianggap terlalu luas -> tidak dimasukkan otomatis

SKIP_DIR = re.compile(r"(^|/)(\.git|node_modules|__pycache__|\.venv|venv|\.idea|\.vscode)(/|$)", re.I)
SKIP_PAT = [
    (re.compile(r"checkpoint", re.I), "checkpoint"),
    (re.compile(r"\.bak|_bak|backup", re.I), "backup"),
    (re.compile(r"\.(zip|7z|rar|tar|gz|exe|dll|pyc|tmp|log|bak)$", re.I), "arsip/biner/sementara"),
    (re.compile(r"(~|\.swp)$"), "sementara"),
]

out = io.StringIO()


def p(*a):
    s = " ".join(str(x) for x in a)
    print(s)
    out.write(s + "\n")


def mb(n):
    return "%.2f MB" % (n / 1048576.0)


def rel(root, path):
    return Path(os.path.relpath(path, root)).as_posix()


def skip_reason(relpath):
    if SKIP_DIR.search(relpath):
        return "folder sistem/lingkungan"
    for rx, why in SKIP_PAT:
        if rx.search(relpath):
            return why
    return None


def read_text(path):
    try:
        return Path(path).read_text(encoding="utf-8-sig", errors="ignore")
    except Exception:
        return ""


def resolve(root, from_file, ref):
    ref = ref.strip()
    if not ref or ref.startswith(("http:", "https:", "//", "data:", "mailto:", "#", "javascript:")):
        return None
    ref = re.split(r"[?#]", ref)[0]
    if not ref:
        return None
    cands = []
    if ref.startswith("/"):
        cands.append(Path(root) / ref.lstrip("/"))
    else:
        cands.append(Path(from_file).parent / ref)
        cands.append(Path(root) / ref)
    for c in cands:
        try:
            c = c.resolve()
            if c.is_file() and Path(root).resolve() in c.parents:
                return c
        except Exception:
            pass
    return None


def expand_pattern(root, from_file, pat):
    """Perluas pola dinamis (mis. data/pelajaran/pilar_*.json) menjadi file nyata."""
    pat = re.split(r"[?#]", pat)[0]
    if pat.startswith(("http:", "https:", "//", "data:")):
        return []
    if len(re.sub(r"[*/.]", "", pat)) < 6:
        return []  # terlalu umum
    bases = [Path(root)] if pat.startswith("/") else [Path(from_file).parent, Path(root)]
    hits = []
    for b in bases:
        full = glob.escape(str(b)) + os.sep + pat.lstrip("/").replace("/", os.sep)
        for h in glob.glob(full):
            hp = Path(h).resolve()
            if hp.is_file() and Path(root).resolve() in hp.parents and not skip_reason(rel(root, hp)):
                if hp not in hits:
                    hits.append(hp)
        if hits:
            break
    return hits


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".")
    ap.add_argument("--entry", action="append", default=None,
                    help="file masuk (default: kamus.html). Boleh diulang.")
    ap.add_argument("--stage", default=None, help="folder tujuan salinan (opsional)")
    ap.add_argument("--abaikan", action="append", default=[],
                    help="pola jalur (mis. \"cidict_split/*\") yang dikeluarkan dari kelompok TERKAIT. Boleh diulang.")
    ap.add_argument("--termasuk-terkait", action="store_true",
                    help="ikut salin kelompok TERKAIT ke folder staging")
    args = ap.parse_args()

    root = Path(args.root).resolve()
    entries = args.entry or ["kamus.html"]
    p("=" * 72)
    p("Root:", root)

    # ---- 1. Telusuri dependensi dari file masuk ---------------------------
    used_by = collections.defaultdict(set)   # file -> {perujuk}
    missing = collections.defaultdict(set)   # ref tidak ketemu -> {perujuk}
    external = collections.defaultdict(set)
    dynamic = []
    dyn_patterns = {}   # pola -> (set perujuk, [file cocok] atau 'terlalu luas')
    queue = []
    seen = set()
    for e in entries:
        ep = resolve(root, root / "x", e) or (root / e)
        if ep.is_file():
            queue.append(ep.resolve())
            seen.add(ep.resolve())
            used_by[ep.resolve()].add("(file masuk)")
        else:
            p("!! File masuk tidak ditemukan:", e)

    while queue:
        cur = queue.pop()
        if cur.suffix.lower() not in TEXT_EXT:
            continue
        txt = read_text(cur)
        refs = set(QUOTED.findall(txt)) | set(CSSURL.findall(txt))
        if cur.suffix.lower() in (".html", ".htm"):
            refs |= set(ATTR.findall(txt))
        pats = set()
        for r in list(refs):
            if "${" in r:
                refs.discard(r)
                pats.add(TEMPL.sub("*", r))
        for pre, suf in CONCAT.findall(txt):
            pats.add(pre + "*" + suf)
        for pt in pats:
            hits = expand_pattern(root, cur, pt)
            ent = dyn_patterns.setdefault(pt, [set(), []])
            ent[0].add(rel(root, cur))
            if len(hits) > MAX_POLA:
                ent[1] = "terlalu luas (%d file)" % len(hits)
                continue
            if isinstance(ent[1], list):
                for hp in hits:
                    if hp not in ent[1]:
                        ent[1].append(hp)
                    used_by[hp].add(rel(root, cur) + " [pola]")
                    if hp not in seen:
                        seen.add(hp)
                        queue.append(hp)
        for r in refs:
            if r.startswith(("http:", "https:", "//")):
                external[r].add(rel(root, cur))
                continue
            if "," in r or r.lower().startswith("application/"):
                continue  # atribut accept / tipe MIME, bukan file
            if re.split(r"[?#]", r)[0].lower().endswith((".html", ".htm")):
                continue  # tautan navigasi ke halaman lain: bukan dependensi kamus
            tgt = resolve(root, cur, r)
            if tgt is None:
                # hanya laporkan yang mirip path file lokal
                if re.search(r"\.(%s)$" % "|".join(REF_EXT), re.split(r"[?#]", r)[0], re.I):
                    missing[r].add(rel(root, cur))
                continue
            used_by[tgt].add(rel(root, cur))
            if tgt not in seen:
                seen.add(tgt)
                queue.append(tgt)
        for ln_no, ln in enumerate(txt.splitlines(), 1):
            if TEMPL.search(ln) or CONCAT.search(ln):
                continue  # sudah ditangani sebagai pola dinamis
            if re.search(r"fetch\s*\(", ln) and (("+" in ln) or ("${" in ln)) and "'" not in ln.split("fetch(")[1][:1]:
                dynamic.append("%s:%d: %s" % (rel(root, cur), ln_no, ln.strip()[:140]))
            elif re.search(r"""['"`]data/['"`]\s*\+|data/\$\{""", ln):
                dynamic.append("%s:%d: %s" % (rel(root, cur), ln_no, ln.strip()[:140]))

    wajib = sorted(used_by.keys(), key=lambda x: rel(root, x))

    # ---- 2. Pindai seluruh folder -----------------------------------------
    all_files = []
    skipped = collections.defaultdict(list)
    stage_abs = Path(args.stage).resolve() if args.stage else None
    for dp, dn, fn in os.walk(root):
        dpath = Path(dp)
        if stage_abs and (dpath == stage_abs or stage_abs in dpath.parents):
            dn[:] = []
            continue
        relp = rel(root, dpath)
        if relp != "." and skip_reason(relp + "/"):
            skipped[skip_reason(relp + "/")].append((relp + "/ (folder)", 0))
            dn[:] = []
            continue
        for f in fn:
            if relp == "." and f in ("laporan_scan_kamus.txt", "daftar_upload_WAJIB.txt",
                                     "daftar_upload_TERKAIT.txt", "gitignore_usulan.txt"):
                continue  # keluaran skrip ini sendiri
            fp = dpath / f
            rp = rel(root, fp)
            try:
                size = fp.stat().st_size
            except OSError:
                continue
            why = skip_reason(rp)
            if why:
                skipped[why].append((rp, size))
            else:
                all_files.append((fp.resolve(), rp, size))

    wajib_set = set(wajib)
    terkait = collections.defaultdict(list)
    for fp, rp, size in all_files:
        if fp in wajib_set:
            continue
        if any(fnmatch.fnmatch(rp, pat) for pat in args.abaikan):
            skipped["diabaikan (--abaikan)"].append((rp, size))
            continue
        ext = fp.suffix.lower()
        top = rp.split("/")[0] if "/" in rp else "(root)"
        if ext == ".py":
            cat = "Skrip Python (*.py)"
        elif ext == ".md":
            cat = "Dokumen (*.md, BLUEPRINT dll.)"
        elif ext in (".csv", ".tsv"):
            cat = "CSV (kurasi/arsip)"
        elif rp.lower().startswith("data/") and ext in (".json", ".txt"):
            cat = "data/ -- tidak terlacak dari kamus.html"
        elif ext in (".html", ".htm"):
            cat = "Halaman HTML lain"
        elif ext in (".js", ".css"):
            cat = "JS/CSS tidak terlacak dari kamus.html"
        else:
            cat = "Lain-lain (%s)" % (ext or "tanpa ekstensi")
        terkait[cat].append((rp, size))

    # ---- 3. Laporan -------------------------------------------------------
    p("\n" + "=" * 72)
    p("A. WAJIB -- dipakai langsung/berantai oleh %s (%d file)" % (", ".join(entries), len(wajib)))
    tot_a = 0
    for fp in wajib:
        rp = rel(root, fp)
        s = fp.stat().st_size
        tot_a += s
        p("   %-48s %10s   <- %s" % (rp, mb(s), ", ".join(sorted(used_by[fp]))[:60]))
    p("   TOTAL WAJIB:", mb(tot_a))

    p("\n" + "=" * 72)
    p("B. TERKAIT -- ada di folder, tidak terlacak dari kamus.html (tentukan sendiri)")
    tot_b = 0
    for cat in sorted(terkait):
        items = sorted(terkait[cat])
        sub = sum(s for _, s in items)
        tot_b += sub
        p("\n   [%s] %d file, %s" % (cat, len(items), mb(sub)))
        for rp, s in items[:25]:
            p("     %-60s %10s" % (rp, mb(s)))
        if len(items) > 25:
            p("     ... dan %d file lagi (lihat daftar_upload_TERKAIT.txt)" % (len(items) - 25))
    p("\n   TOTAL TERKAIT:", mb(tot_b))

    p("\n" + "=" * 72)
    p("C. DIKECUALIKAN (usul: jangan diunggah)")
    tot_c = 0
    for why in sorted(skipped):
        items = skipped[why]
        sub = sum(s for _, s in items)
        tot_c += sub
        p("\n   [%s] %d entri, %s" % (why, len(items), mb(sub)))
        for rp, s in sorted(items, key=lambda x: -x[1])[:8]:
            p("     %-60s %10s" % (rp, mb(s)))
        if len(items) > 8:
            p("     ... dan %d lagi" % (len(items) - 8))
    p("\n   TOTAL DIKECUALIKAN:", mb(tot_c))

    p("\n" + "=" * 72)
    p("D. PERINGATAN")
    big = [(rel(root, fp), fp.stat().st_size) for fp in wajib] + \
          [(rp, s) for cat in terkait for rp, s in terkait[cat]]
    b25 = [(r, s) for r, s in big if 25 * 1048576 <= s < 100 * 1048576]
    b100 = [(r, s) for r, s in big if s >= 100 * 1048576]
    p("   File 25-100 MB (tidak bisa lewat unggah web GitHub; bisa lewat API/git):", len(b25))
    for r, s in b25:
        p("     ", r, mb(s))
    p("   File >=100 MB (DITOLAK GitHub; kecualikan atau pakai Git LFS):", len(b100))
    for r, s in b100:
        p("     ", r, mb(s))
    p("   Rujukan ke file yang TIDAK ditemukan di disk (%d):" % len(missing))
    for r in sorted(missing):
        p("     %-50s <- %s" % (r, ", ".join(sorted(missing[r]))[:60]))
    p("   Rujukan eksternal/CDN (aplikasi butuh internet untuk ini) (%d):" % len(external))
    for r in sorted(external):
        p("     %-60s <- %s" % (r[:60], ", ".join(sorted(external[r]))[:40]))
    p("   Pola pemuatan dinamis, DIPERLUAS OTOMATIS dan sudah masuk bagian A (%d):" % len(dyn_patterns))
    for pt in sorted(dyn_patterns):
        perujuk, hasil = dyn_patterns[pt]
        if isinstance(hasil, str):
            ket = hasil + " -> TIDAK dimasukkan, tentukan manual"
        elif not hasil:
            ket = "0 file cocok (mungkin nama unduhan/ekspor, bukan file yang dimuat)"
        else:
            ket = "%d file cocok" % len(hasil)
        p("     %-52s %s  <- %s" % (pt[:52], ket, ", ".join(sorted(perujuk))[:40]))
    p("   Baris fetch dinamis lain yang mungkin perlu dicek manual (%d):" % len(dynamic))
    for d in dynamic[:20]:
        p("     ", d)

    # ---- 4. File keluaran --------------------------------------------------
    Path("daftar_upload_WAJIB.txt").write_text(
        "\n".join(rel(root, fp) for fp in wajib) + "\n", encoding="utf-8")
    Path("daftar_upload_TERKAIT.txt").write_text(
        "\n".join("%s\t%s" % (rp, cat) for cat in sorted(terkait) for rp, _ in sorted(terkait[cat])) + "\n",
        encoding="utf-8")
    gi = ["# usulan .gitignore", "*.bak*", "*_bak*", "*checkpoint*", "*.zip", "*.7z", "*.rar",
          "__pycache__/", "*.pyc", "*.log", "*.tmp", "node_modules/", ".venv/"]
    Path("gitignore_usulan.txt").write_text("\n".join(gi) + "\n", encoding="utf-8")

    # ---- 5. Staging (salinan, opsional) -------------------------------------
    if args.stage:
        n = 0
        todo = [(fp, rel(root, fp)) for fp in wajib]
        if args.termasuk_terkait:
            todo += [(root / rp, rp) for cat in terkait for rp, _ in terkait[cat]]
        for src, rp in todo:
            dst = stage_abs / rp
            dst.parent.mkdir(parents=True, exist_ok=True)
            if Path(src).stat().st_size >= 24 * 1048576:
                # >=24 MB: dikompres .gz supaya lolos batas unggah web GitHub (25 MB)
                with open(src, "rb") as fi, gzip.open(str(dst) + ".gz", "wb", 6) as fo:
                    shutil.copyfileobj(fi, fo)
                p("   dikompres .gz (terlalu besar untuk unggah web):", rp)
            else:
                shutil.copy2(src, dst)
            n += 1
        shutil.copy2("gitignore_usulan.txt", stage_abs / ".gitignore")
        p("\nSalinan staging dibuat: %d file di %s (file asli tidak disentuh)" % (n, stage_abs))

    Path("laporan_scan_kamus.txt").write_text(out.getvalue(), encoding="utf-8")
    p("\nTersimpan: laporan_scan_kamus.txt, daftar_upload_WAJIB.txt, daftar_upload_TERKAIT.txt, gitignore_usulan.txt")


if __name__ == "__main__":
    sys.exit(main())

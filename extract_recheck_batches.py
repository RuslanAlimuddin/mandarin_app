"""
extract_recheck_batches.py
=============================
Siapkan 3 jenis batch untuk perbaikan kualitas kata_majemuk_pola.json,
berdasarkan temuan audit_kata_majemuk_pola.py + tinjauan manual Claude.

Cara pakai:
    python extract_recheck_batches.py keterangan
        -> kata dengan keterangan_id generik (dipakai identik >=10x),
           kirim ke AI untuk ditulis ulang PENJELASANNYA saja (pola tetap).

    python extract_recheck_batches.py subjek-predikat
        -> SEMUA kata berkategori 主谓式 (106 kata), kirim ke AI untuk
           diklasifikasi ULANG dari nol dengan aturan lebih ketat.

    python extract_recheck_batches.py verifikasi [batch_size]
        -> kata berkategori 动宾式 atau 补充式, kirim ke AI untuk
           DIPERIKSA apakah sebenarnya 联合式 (dua kata nyaris sinonim).
           AI hanya melapor yang perlu dikoreksi. Ada tracking progress
           (default batch_size 500), jalankan berulang sampai habis.

Semua mode READ-ONLY terhadap kata_majemuk_pola.json -- hanya menulis
file .txt batch dan (utk mode verifikasi) file tracking progress.
"""

import json
import os
import sys
from collections import Counter

CLASSIFIED_PATH = "kata_majemuk_pola.json"
CANDIDATES_PATH = "kata_majemuk_candidates_2char_ALL.json"
VERIFIKASI_REVIEWED_PATH = "verifikasi_reviewed_words.json"

OVERUSED_THRESHOLD = 10
DEFAULT_VERIFIKASI_BATCH = 500


def load_json(path, default):
    if not os.path.exists(path):
        return default
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def pinyin_lookup():
    candidates = load_json(CANDIDATES_PATH, [])
    return {c["word"]: c.get("pinyin", "") for c in candidates}


def write_chunk(filename, lines, header_note=""):
    with open(filename, "w", encoding="utf-8") as f:
        if header_note:
            f.write(header_note + "\n\n")
        f.write("\n".join(lines))
    print(f"Disimpan: {filename}  ({len(lines)} baris)")


def mode_keterangan(classified):
    counts = Counter(item.get("keterangan_id", "").strip() for item in classified)
    overused = {k for k, c in counts.items() if c >= OVERUSED_THRESHOLD and k}

    if not overused:
        print(f"Tidak ada keterangan_id yang dipakai >= {OVERUSED_THRESHOLD}x. Tidak ada yang perlu diperbaiki.")
        return

    targets = [item for item in classified if item.get("keterangan_id", "").strip() in overused]
    print(f"{len(overused)} kalimat generik ditemukan, total {len(targets)} kata terdampak.")

    lines = []
    for item in targets:
        lines.append(f"{item['word']} | pola: {item['pola']} | keterangan_lama: {item['keterangan_id']}")

    write_chunk(
        "chunk_keterangan_to_send.txt",
        lines,
        "# Kata dengan keterangan_id generik/copy-paste -- pola JANGAN diubah, hanya tulis ulang keterangan_id"
    )
    print("\nLangkah berikutnya:")
    print("  1. Salin PROMPT_perbaiki_keterangan.md + tempel isi chunk_keterangan_to_send.txt di bawahnya")
    print("  2. Kirim ke AI eksternal, simpan balasan NDJSON")
    print("  3. python import_corrections.py <balasan.txt> --dry-run   (cek dulu)")
    print("  4. python import_corrections.py <balasan.txt>             (terapkan)")


def mode_subjek_predikat(classified):
    targets = [item for item in classified if item["pola"] == "主谓式"]
    if not targets:
        print("Tidak ada kata berkategori 主谓式.")
        return

    pinyin_map = pinyin_lookup()
    print(f"{len(targets)} kata berkategori 主谓式 ditemukan -- akan diklasifikasi ULANG dari nol.")

    lines = []
    for item in targets:
        py = pinyin_map.get(item["word"], "")
        lines.append(f"{item['word']} ({py})")

    write_chunk(
        "chunk_subjek_predikat_to_send.txt",
        lines,
        "# Kata berkategori 主谓式 -- klasifikasi ULANG dari nol (abaikan kategori lama)"
    )
    print("\nLangkah berikutnya:")
    print("  1. Salin PROMPT_reklasifikasi_subjek_predikat.md + tempel isi chunk_subjek_predikat_to_send.txt")
    print("  2. Kirim ke AI eksternal, simpan balasan NDJSON")
    print("  3. python import_corrections.py <balasan.txt> --dry-run")
    print("  4. python import_corrections.py <balasan.txt>")


def mode_verifikasi(classified, batch_size):
    targets_all = [item for item in classified if item["pola"] in ("动宾式", "补充式")]
    reviewed = load_json(VERIFIKASI_REVIEWED_PATH, [])
    reviewed_set = set(reviewed)

    remaining = [item for item in targets_all if item["word"] not in reviewed_set]

    print(f"Total kata 动宾式+补充式 : {len(targets_all)}")
    print(f"Sudah dikirim utk verifikasi: {len(reviewed_set)}")
    print(f"Sisa belum diverifikasi     : {len(remaining)}")

    if not remaining:
        print("\n=== SELESAI: semua kata 动宾式/补充式 sudah dikirim untuk verifikasi. ===")
        return

    chunk = remaining[:batch_size]
    pinyin_map = pinyin_lookup()

    lines = []
    for item in chunk:
        py = pinyin_map.get(item["word"], "")
        lines.append(f"{item['word']} ({py}) [pola saat ini: {item['pola']}]")

    write_chunk(
        "chunk_verifikasi_to_send.txt",
        lines,
        "# Verifikasi 动宾式/补充式 -- AI hanya lapor yang PERLU DIKOREKSI, skip yang sudah benar"
    )

    # Tandai batch ini sebagai "sudah dikirim" begitu chunk dibuat (bukan
    # menunggu hasil koreksi kembali), karena tujuannya cukup 1x lewat per kata.
    reviewed_set.update(item["word"] for item in chunk)
    with open(VERIFIKASI_REVIEWED_PATH, "w", encoding="utf-8") as f:
        json.dump(sorted(reviewed_set), f, ensure_ascii=False, indent=2)

    print(f"\n{len(chunk)} kata ditandai 'sudah dikirim' di {VERIFIKASI_REVIEWED_PATH}")
    print("\nLangkah berikutnya:")
    print("  1. Salin PROMPT_verifikasi_dongbin_buchong.md + tempel isi chunk_verifikasi_to_send.txt")
    print("  2. Kirim ke AI eksternal, simpan balasan NDJSON (bisa KOSONG kalau semua sudah benar)")
    print("  3. python import_corrections.py <balasan.txt> --dry-run")
    print("  4. python import_corrections.py <balasan.txt>")

    sisa = len(remaining) - len(chunk)
    if sisa > 0:
        print(f"\n(Masih ada {sisa} kata lagi untuk diverifikasi, jalankan mode ini lagi nanti)")


def main():
    if len(sys.argv) < 2:
        print("Cara pakai: python extract_recheck_batches.py <keterangan|subjek-predikat|verifikasi> [batch_size]")
        sys.exit(1)

    mode = sys.argv[1]
    classified = load_json(CLASSIFIED_PATH, [])
    if not classified:
        print(f"[ERROR] {CLASSIFIED_PATH} tidak ditemukan/kosong.")
        sys.exit(1)

    if mode == "keterangan":
        mode_keterangan(classified)
    elif mode == "subjek-predikat":
        mode_subjek_predikat(classified)
    elif mode == "verifikasi":
        batch_size = DEFAULT_VERIFIKASI_BATCH
        if len(sys.argv) > 2:
            try:
                batch_size = int(sys.argv[2])
            except ValueError:
                print(f"[WARN] batch_size tidak valid, pakai default {DEFAULT_VERIFIKASI_BATCH}")
        mode_verifikasi(classified, batch_size)
    else:
        print(f"[ERROR] Mode tidak dikenal: '{mode}'")
        print("        Pilihan: keterangan | subjek-predikat | verifikasi")
        sys.exit(1)


if __name__ == "__main__":
    main()

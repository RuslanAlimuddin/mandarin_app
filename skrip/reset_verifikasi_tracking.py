"""
reset_verifikasi_tracking.py
===============================
Hapus daftar kata dari verifikasi_reviewed_words.json supaya kata-kata
itu dianggap 'belum diverifikasi' lagi dan akan ikut kepilih ulang oleh
extract_recheck_batches.py verifikasi (dengan prompt yang sudah diperbaiki).

Dipakai setelah revert_batch.py, untuk 1 batch yang ternyata bermasalah
dan perlu diverifikasi ULANG dari awal.

Cara pakai:
    python reset_verifikasi_tracking.py balasan40.txt
        (baca semua 'word' dari file balasan, hapus dari tracking)
"""

import json
import os
import sys

TRACKING_PATH = "verifikasi_reviewed_words.json"


def load_json(path, default):
    if not os.path.exists(path):
        return default
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def main():
    if len(sys.argv) < 2:
        print("Cara pakai: python reset_verifikasi_tracking.py <file_balasan_ai.txt>")
        sys.exit(1)

    input_path = sys.argv[1]
    if not os.path.exists(input_path):
        print(f"[ERROR] File tidak ditemukan: {input_path}")
        sys.exit(1)

    words_to_reset = set()
    with open(input_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("```"):
                continue
            try:
                obj = json.loads(line)
                w = obj.get("word", "").strip()
                if w:
                    words_to_reset.add(w)
            except json.JSONDecodeError:
                continue

    if not words_to_reset:
        print("[WARN] Tidak ada 'word' yang terbaca dari file ini.")
        print("       Kalau file ini isinya cuma kata yang DIKOREKSI (bukan semua kata")
        print("       yang dikirim di batch), tracking utk kata yang TIDAK dikoreksi")
        print("       (dianggap sudah benar) TIDAK akan direset -- itu normal & aman,")
        print("       tidak perlu direset karena memang sudah correct.")
        return

    reviewed = load_json(TRACKING_PATH, [])
    reviewed_set = set(reviewed)

    before = len(reviewed_set)
    reviewed_set -= words_to_reset
    after = len(reviewed_set)

    with open(TRACKING_PATH, "w", encoding="utf-8") as f:
        json.dump(sorted(reviewed_set), f, ensure_ascii=False, indent=2)

    print(f"Kata dibaca dari file  : {len(words_to_reset)}")
    print(f"Tracking sebelum       : {before}")
    print(f"Tracking sesudah       : {after}")
    print(f"Dihapus dari tracking  : {before - after}")
    print(f"\n{TRACKING_PATH} sudah diperbarui.")
    print("Kata-kata ini akan ikut kepilih lagi saat 'extract_recheck_batches.py verifikasi' dijalankan.")


if __name__ == "__main__":
    main()

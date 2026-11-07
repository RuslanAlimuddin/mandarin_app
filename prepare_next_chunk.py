"""
prepare_next_chunk.py
=======================
Siapkan chunk kata berikutnya (belum diklasifikasi) untuk dikirim ke AI
eksternal, sebagai lanjutan dari PROMPT_untuk_AI_pola_majemuk.md.

READ-ONLY terhadap data sumber -- hanya menulis file
`next_chunk_to_send.txt` (ditimpa tiap dijalankan).

Cara pakai:
    python prepare_next_chunk.py           (default 250 kata)
    python prepare_next_chunk.py 150       (custom ukuran batch)

Alur kerja:
1. Jalankan script ini -> hasilkan next_chunk_to_send.txt
2. Buka PROMPT_untuk_AI_pola_majemuk.md, salin isinya
3. Tempel isi next_chunk_to_send.txt di bawahnya
4. Kirim ke AI eksternal (ChatGPT/Gemini/dst)
5. Simpan balasan NDJSON-nya ke file .txt/.jsonl
6. Jalankan import_kata_majemuk_batch.py untuk validasi & impor
7. Ulangi dari langkah 1 sampai "Tidak ada kandidat baru yang tersisa"
"""

import json
import os
import sys

CANDIDATES_PATH = "kata_majemuk_candidates_2char_ALL.json"
CLASSIFIED_PATH = "kata_majemuk_pola.json"  # hasil akumulasi dari import script
CHUNK_OUTPUT_PATH = "next_chunk_to_send.txt"

DEFAULT_BATCH_SIZE = 250


def load_json(path, default):
    if not os.path.exists(path):
        return default
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def main():
    batch_size = DEFAULT_BATCH_SIZE
    if len(sys.argv) > 1:
        try:
            batch_size = int(sys.argv[1])
        except ValueError:
            print(f"[WARN] Argumen '{sys.argv[1]}' bukan angka, pakai default {DEFAULT_BATCH_SIZE}")

    candidates = load_json(CANDIDATES_PATH, [])
    if not candidates:
        print(f"[ERROR] {CANDIDATES_PATH} tidak ditemukan atau kosong.")
        print("        Pastikan file ini ada di folder yang sama (hasil dari scope_kata_majemuk_full.py).")
        sys.exit(1)

    classified = load_json(CLASSIFIED_PATH, [])
    already_done = set(item["word"] for item in classified)

    remaining = [c for c in candidates if c["word"] not in already_done]

    total = len(candidates)
    done_count = len(already_done)
    remaining_count = len(remaining)

    print(f"Total kandidat        : {total}")
    print(f"Sudah diklasifikasi    : {done_count}")
    print(f"Sisa belum diklasifikasi: {remaining_count}")

    if remaining_count == 0:
        print("\n=== SELESAI: Tidak ada kandidat baru yang tersisa. ===")
        if os.path.exists(CHUNK_OUTPUT_PATH):
            os.remove(CHUNK_OUTPUT_PATH)
        return

    chunk = remaining[:batch_size]

    lines = []
    for item in chunk:
        hsk_label = item["hsk"] if item.get("hsk") is not None else "-"
        lines.append(f"{item['word']} ({item.get('pinyin', '')}) [HSK {hsk_label}]")

    with open(CHUNK_OUTPUT_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"\nChunk berikutnya: {len(chunk)} kata")
    print(f"Disimpan ke: {CHUNK_OUTPUT_PATH}")
    print("\nLangkah berikutnya:")
    print("  1. Buka PROMPT_untuk_AI_pola_majemuk.md, salin seluruh isinya")
    print(f"  2. Tempel isi {CHUNK_OUTPUT_PATH} di bawah prompt itu")
    print("  3. Kirim ke AI eksternal, simpan balasan NDJSON ke file baru")
    print("  4. Jalankan import_kata_majemuk_batch.py <file_balasan_AI>")

    sisa_setelah_chunk_ini = remaining_count - len(chunk)
    if sisa_setelah_chunk_ini > 0:
        estimasi_batch_lagi = -(-sisa_setelah_chunk_ini // batch_size)  # ceil
        print(f"\n(Setelah batch ini, masih ada {sisa_setelah_chunk_ini} kata lagi, "
              f"~{estimasi_batch_lagi} batch lagi dengan ukuran {batch_size})")


if __name__ == "__main__":
    main()

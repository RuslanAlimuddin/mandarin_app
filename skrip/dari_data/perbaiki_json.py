#!/usr/bin/env python3
"""
perbaiki_json.py
=================
Memperbaiki file JSON pelajaran (pilar_N.json) yang ditolak aplikasi karena
mengandung tanda kutip ganda (") yang TIDAK di-escape di dalam nilai string
-- biasanya muncul dari atribut HTML seperti <span class="hz">...</span>
yang seharusnya ditulis <span class=\"hz\">...</span>.

CARA KERJA
----------
Script ini membaca file sebagai teks mentah (bukan json.load, karena file
sumber memang tidak valid) lalu berjalan karakter-per-karakter sambil
melacak apakah posisi saat ini sedang "di dalam" sebuah string JSON.

Setiap kali menemukan tanda kutip (") saat berada di dalam string, script
akan melihat karakter non-spasi berikutnya:
  - Jika karakter berikutnya adalah salah satu dari  ,  }  ]  :
    -> ini dianggap kutip PENUTUP string yang sah (JSON asli), dibiarkan.
  - Selain itu (huruf, angka, spasi diikuti huruf, dll)
    -> ini dianggap kutip LITERAL di dalam kalimat/HTML yang lupa di-escape,
       maka akan diubah menjadi \" secara otomatis.

Backslash escape yang sudah ada (\", \\, \n, dst) tidak diutak-atik.

Setelah perbaikan, hasil divalidasi dengan json.loads(). Jika masih gagal,
posisi error akan ditampilkan supaya bisa diperbaiki manual.

PENGGUNAAN
----------
    python3 perbaiki_json.py pilar_7.json
    -> menghasilkan pilar_7.fixed.json (jika valid)

    python3 perbaiki_json.py pilar_7.json -o hasil.json
    -> menyimpan ke nama file custom

    python3 perbaiki_json.py pilar_7.json --overwrite
    -> menimpa langsung file aslinya (setelah backup .bak dibuat)
"""

import sys
import json
import argparse
import shutil


def _kutip_penutup_asli_pretty(teks: str, pos: int) -> bool:
    """Versi heuristik untuk file PRETTY-PRINTED (satu token struktural per
    baris). Kutip penutup asli selalu diikuti (setelah spasi/tab) oleh:
        - } ] : langsung, ATAU
        - , yang lalu diikuti baris baru (koma di dalam kalimat pada baris
          yang sama TIDAK dianggap penutup), ATAU
        - baris baru langsung, asalkan setelah baris baru itu (dan spasi/
          indentasi) muncul token struktural (}, ], {, [, atau kutip kunci
          berikutnya) -- bukan lanjutan kalimat.
    """
    n = len(teks)
    j = pos + 1

    while j < n and teks[j] in " \t":
        j += 1

    if j < n and teks[j] in "}]:":
        return True

    if j < n and teks[j] == ",":
        k = j + 1
        while k < n and teks[k] in " \t":
            k += 1
        return k < n and teks[k] in "\r\n"

    if j < n and teks[j] in "\r\n":
        k = j
        while k < n and teks[k] in " \t\r\n":
            k += 1
        return k < n and teks[k] in "}]\"{["

    return False


def _kutip_penutup_asli_minified(teks: str, pos: int) -> bool:
    """Versi heuristik untuk file MINIFIED (tanpa baris baru sama sekali).
    Tidak ada penanda newline yang bisa dipakai, jadi dipakai aturan
    sederhana: kutip penutup asli adalah yang diikuti langsung (setelah
    spasi) oleh salah satu dari , } ] :
    """
    n = len(teks)
    j = pos + 1
    while j < n and teks[j] in " \t\r\n":
        j += 1
    next_ch = teks[j] if j < n else ""
    return next_ch in (",", "}", "]", ":")


def perbaiki_kutip(teks: str) -> str:
    """Escape tanda kutip literal di dalam string JSON, biarkan kutip
    pembuka/penutup string JSON yang sah tidak berubah.

    Otomatis mendeteksi apakah file pretty-printed (banyak baris baru,
    satu token per baris) atau minified (satu baris panjang), lalu memakai
    heuristik yang sesuai untuk membedakan kutip literal vs kutip penutup
    JSON yang sah.
    """
    pretty = teks.count("\n") > 10
    cek_penutup = _kutip_penutup_asli_pretty if pretty else _kutip_penutup_asli_minified

    hasil = []
    n = len(teks)
    i = 0
    in_string = False

    while i < n:
        ch = teks[i]

        # Backslash escape: salin apa adanya (backslash + 1 karakter berikutnya)
        if in_string and ch == "\\" and i + 1 < n:
            hasil.append(ch)
            hasil.append(teks[i + 1])
            i += 2
            continue

        if ch == '"':
            if not in_string:
                # Kutip pembuka string baru
                in_string = True
                hasil.append(ch)
                i += 1
                continue
            else:
                if cek_penutup(teks, i):
                    # Kutip penutup string yang sah
                    in_string = False
                    hasil.append(ch)
                    i += 1
                    continue
                else:
                    # Kutip literal di dalam teks -> escape
                    hasil.append('\\"')
                    i += 1
                    continue

        hasil.append(ch)
        i += 1

    return "".join(hasil)


def hapus_koma_trailing(teks: str) -> tuple[str, int]:
    """Menghapus koma yang menggantung sebelum } atau ] (trailing comma),
    mis. `"teks": "..."  ,  }` -- valid di JS/Python dict literal tapi TIDAK
    valid di JSON. Hanya menghapus koma yang berada DI LUAR string.

    Mengembalikan (teks_baru, jumlah_koma_yang_dihapus).
    """
    hasil = []
    n = len(teks)
    i = 0
    in_string = False
    jumlah = 0

    while i < n:
        ch = teks[i]

        if in_string and ch == "\\" and i + 1 < n:
            hasil.append(ch)
            hasil.append(teks[i + 1])
            i += 2
            continue

        if ch == '"':
            in_string = not in_string
            hasil.append(ch)
            i += 1
            continue

        if not in_string and ch == ",":
            # Lihat ke depan (lewati spasi/baris baru) apakah karakter
            # berikutnya adalah } atau ] -> berarti koma ini trailing, buang
            j = i + 1
            while j < n and teks[j] in " \t\r\n":
                j += 1
            next_ch = teks[j] if j < n else ""
            if next_ch in ("}", "]"):
                jumlah += 1
                i += 1  # skip koma ini, tidak ditambahkan ke hasil
                continue

        hasil.append(ch)
        i += 1

    return "".join(hasil), jumlah


def tutup_kurung_yang_hilang(teks: str) -> tuple[str, int]:
    """Jika file terpotong di akhir (kurung penutup { } [ ] hilang, biasanya
    karena output AI kepotong), fungsi ini melacak stack kurung yang masih
    terbuka lalu menutupnya secara otomatis di akhir teks, dengan urutan
    yang benar (kurung yang paling akhir dibuka, ditutup paling dulu).

    Mengembalikan (teks_baru, jumlah_kurung_yang_ditambahkan).
    """
    stack = []
    in_string = False
    i = 0
    n = len(teks)
    while i < n:
        ch = teks[i]
        if in_string and ch == "\\" and i + 1 < n:
            i += 2
            continue
        if ch == '"':
            in_string = not in_string
            i += 1
            continue
        if not in_string:
            if ch in "{[":
                stack.append(ch)
            elif ch in "}]":
                if stack:
                    stack.pop()
        i += 1

    if not stack:
        return teks, 0

    penutup = {"{": "}", "[": "]"}
    tambahan = "".join(penutup[c] for c in reversed(stack))
    return teks + tambahan, len(stack)


def main():
    ap = argparse.ArgumentParser(description="Perbaiki JSON dengan kutip tak ter-escape")
    ap.add_argument("file_input", help="Path file JSON yang rusak (mis. pilar_7.json)")
    ap.add_argument("-o", "--output", help="Path file output (default: <nama>.fixed.json)")
    ap.add_argument("--overwrite", action="store_true",
                     help="Timpa file asli langsung (backup .bak otomatis dibuat)")
    args = ap.parse_args()

    with open(args.file_input, encoding="utf-8") as f:
        mentah = f.read()

    # Jika sudah valid, tidak perlu diapa-apakan
    try:
        json.loads(mentah)
        print(f"[INFO] '{args.file_input}' sudah berupa JSON valid. Tidak ada yang diubah.")
        return
    except json.JSONDecodeError as e_awal:
        print(f"[INFO] JSON asli tidak valid: {e_awal}")
        print("[INFO] Mencoba memperbaiki tanda kutip yang tidak ter-escape...")

    teks = perbaiki_kutip(mentah)
    langkah = ["escape tanda kutip"]

    def coba_parse(t):
        try:
            return json.loads(t), None
        except json.JSONDecodeError as e:
            return None, e

    data, err = coba_parse(teks)

    if err is not None:
        # Langkah 2: hapus trailing comma
        teks_baru, jumlah = hapus_koma_trailing(teks)
        if jumlah > 0:
            print(f"[INFO] Terdeteksi {jumlah} koma menggantung (trailing comma) "
                  f"sebelum }} atau ]. Menghapus otomatis...")
            teks = teks_baru
            langkah.append("hapus trailing comma")
        data, err = coba_parse(teks)

    if err is not None:
        # Langkah 3: mungkin file terpotong (kurung penutup hilang)
        teks_baru, jumlah = tutup_kurung_yang_hilang(teks)
        if jumlah > 0:
            print(f"[INFO] Terdeteksi {jumlah} kurung pembuka yang belum ditutup "
                  f"(kemungkinan file terpotong). Menutup otomatis...")
            teks = teks_baru
            langkah.append("tutup kurung yang hilang")
        data, err = coba_parse(teks)

    if err is not None:
        pos = err.pos
        awal = max(0, pos - 120)
        akhir = min(len(teks), pos + 120)
        print("\n[GAGAL] Masih ada error setelah semua perbaikan otomatis:")
        print(f"        {err}")
        print("\n--- Konteks di sekitar error ---")
        print(teks[awal:pos] + " <<<--- DI SINI --->>> " + teks[pos:akhir])
        print("---------------------------------\n")
        partial_path = args.file_input.rsplit(".", 1)[0] + ".partial.json"
        with open(partial_path, "w", encoding="utf-8") as f:
            f.write(teks)
        print(f"[INFO] Hasil perbaikan parsial disimpan ke: {partial_path}")
        print("       Silakan telusuri manual di sekitar posisi error di atas.")
        sys.exit(1)

    diperbaiki = teks

    # Validasi lolos -> tulis ulang dengan json.dump supaya escaping selalu benar
    if args.overwrite:
        backup_path = args.file_input + ".bak"
        shutil.copy2(args.file_input, backup_path)
        output_path = args.file_input
        print(f"[INFO] Backup file asli disimpan ke: {backup_path}")
    else:
        output_path = args.output or args.file_input.rsplit(".", 1)[0] + ".fixed.json"

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=None, separators=(",", ":"))

    print(f"[SUKSES] JSON valid ditulis ke: {output_path}")

    # Info ringkas
    jumlah_bagian = len(data.get("bagian", []))
    print(f"[INFO] Pilar {data.get('pilar')}: '{data.get('judul')}' -- {jumlah_bagian} bagian.")


if __name__ == "__main__":
    main()

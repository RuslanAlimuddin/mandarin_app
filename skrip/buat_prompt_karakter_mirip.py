"""
buat_prompt_karakter_mirip.py -- pembuat prompt untuk AI eksternal (self-updating).

Prompt TAHAP 1 (cari kandidat) otomatis memuat daftar grup yang SUDAH ADA di
data/confusion_groups.json sebagai daftar "jangan diulang", jadi tiap kali
dijalankan setelah --apply, prompt-nya ikut mutakhir.

Cara pakai (dari C:\\mandarin_app, satu folder dgn gabungkan_karakter_mirip.py):

  TAHAP 1 -- cari kandidat:
      python buat_prompt_karakter_mirip.py
      -> prompt_karakter_mirip_1_cari.txt   (tempel ke AI eksternal)
      Simpan jawaban AI sebagai:  kandidat_karakter_mirip.txt

  TAHAP 2 -- verifikasi (pakai AI LAIN dari tahap 1, kalau bisa):
      python buat_prompt_karakter_mirip.py kandidat_karakter_mirip.txt
      -> prompt_karakter_mirip_2_verifikasi.txt   (tempel ke AI kedua)
      Simpan jawaban AI sebagai:  verifikasi_karakter_mirip.txt

  TAHAP 3 -- cek & gabung:
      python gabungkan_karakter_mirip.py verifikasi_karakter_mirip.txt            (dry-run)
      -> kirim hasil dry-run ke Claude untuk tinjauan manual SEBELUM --apply
      python gabungkan_karakter_mirip.py verifikasi_karakter_mirip.txt --apply

PENTING -- URUTAN ANTAR BATCH:
  Selesaikan satu batch SAMPAI --apply, BARU buat prompt tahap 1 untuk batch berikutnya.
  (Daftar "jangan diulang" di prompt dibaca dari confusion_groups.json saat prompt
  dibuat; kalau batch sebelumnya belum di-apply, AI akan mengusulkan hal yang sama.)
  Setelah apply, file batch otomatis disalin ke arsip_karakter_mirip\\batch_<waktu>\\ oleh
  gabungkan_karakter_mirip.py. File asli BOLEH tetap di tempatnya (dan tetap terbuka di
  Notepad++): isinya tinggal ditimpa dgn hasil AI batch berikutnya lalu disimpan.

Opsi:  --n=30   jumlah kelompok yang diminta per batch tahap 1 (default 30)
"""

import json
import os
import sys

from gabungkan_karakter_mirip import (PATH_GROUPS, group_chars,
                                      iter_json_objects, validate_schema)

OUT1 = "prompt_karakter_mirip_1_cari.txt"
OUT2 = "prompt_karakter_mirip_2_verifikasi.txt"

DEFINISI = """\
APA ITU "KARAKTER MIRIP" (baca dengan teliti):
- Yang dicari: karakter Hanzi yang BENTUK TULISANNYA mirip sehingga pelajar sering
  tertukar saat membaca cepat atau menulis.
- BUKAN mirip bunyi (homofon, mis. 他/她/它), BUKAN mirip makna (sinonim), BUKAN pasangan
  aksara tradisional vs sederhana (mis. 见/見).
- FOKUS BATCH INI = JENIS A: selisih KECIL pada bentuk -- ada/tidaknya satu goresan atau
  titik, panjang atau arah garis, kait/tekukan yang berbeda, atau satu komponen kecil di
  dalam/luar bingkai yang sama. Contoh GAYA yang dicari (semuanya SUDAH ADA, jangan
  diulang): 己/已/巳, 末/未, 土/士, 戊/戌/戍/戎, 干/于, 厂/广.
- JANGAN buat JENIS B, yaitu keluarga komponen (komponen kanan sama tetapi radikal kiri
  berbeda, mis. 他/她/地/池, 妈/吗/码/蚂, 海/悔/梅). Jenis itu sudah banyak sekali di
  database. Kalau kamu ragu sebuah kelompok jenis A atau B, anggap B dan JANGAN sertakan.
- Semua karakter WAJIB Hanzi SEDERHANA (bukan tradisional) dan dipakai dalam kosakata
  HSK 1-9. Prioritaskan karakter HSK 1-6."""

FORMAT = """\
FORMAT KELUARAN (WAJIB, ketat):
- NDJSON: SATU objek JSON per baris. Tanpa markdown, tanpa ```, tanpa nomor, tanpa teks
  pengantar/penutup, tanpa field "id".
- Setiap objek persis berisi 3 field:
  {"character":"<1 hanzi utama>","confusable_with":["<1-4 hanzi lain>"],"note":"<catatan>"}
- "character" = 1 karakter. "confusable_with" = 1 sampai 4 karakter tunggal (bukan kata),
  tanpa mengulang "character".
- "note" = Bahasa Indonesia, 1-2 kalimat pendek, menyebut PERSIS bagian mana yang berbeda
  (goresan/titik/komponen mana) dan menyebut karakternya. Contoh gaya yang baik:
  "Perbedaan pada titik di bawah — 玉 = 王 + titik" atau
  "Radikal kiri berbeda — 清 (氵 air) vs 晴 (日 matahari)".
  DILARANG menulis note dalam bahasa Mandarin atau Inggris.
- AKURASI NOTE: sebut komponen dalam bentuk SEDERHANA (mis. 练/炼 memakai 东, bukan 柬).
  Sebut posisi (kiri/kanan/atas/bawah) HANYA kalau kamu yakin; kalau ragu, jelaskan
  perbedaannya tanpa menyebut posisi. Jangan mengarang goresan atau komponen."""


def load_existing_lines():
    with open(PATH_GROUPS, "r", encoding="utf-8") as f:
        data = json.load(f)
    lines = ["".join(group_chars(g)) for g in data["groups"]]
    return data, lines


def prompt_cari(n, lines):
    return f"""\
Kamu membantu menyusun database "Karakter Mirip" untuk aplikasi belajar Mandarin
(pengguna berbahasa Indonesia).

TUGAS: cari sampai {n} kelompok karakter Hanzi yang mirip BENTUK TULISANNYA, yang BELUM ada
di daftar "SUDAH ADA" di bawah.

{DEFINISI}

AREA YANG BOLEH DIJELAJAHI (cari yang BELUM ada di daftar "SUDAH ADA"):
1. Ada/tidaknya satu goresan atau satu titik.
2. Panjang garis berbeda (garis atas lebih pendek/panjang) atau arah garis berbeda.
3. Kait, tekukan, atau tarikan kecil yang berbeda pada kerangka yang sama.
4. Satu komponen kecil berbeda di dalam, di atas, atau di bawah bingkai yang sama.
5. Komponen yang SAMA tetapi posisinya ditukar (kiri-kanan atau atas-bawah).
6. Karakter kompleks (lebih dari 10 goresan) yang hanya berbeda satu coretan atau satu
   komponen kecil.

ATURAN KEJUJURAN (penting):
- Kalau kamu TIDAK YAKIN dua karakter benar-benar mirip bentuk, JANGAN sertakan. Lebih baik
  memberi 15 kelompok yang pasti benar daripada {n} kelompok yang dipaksakan.
- Jangan mengarang karakter. Jangan mencampur homofon atau sinonim ke dalam kelompok.
- Satu karakter boleh muncul di beberapa kelompok, asalkan PASANGAN-nya baru.
- Jangan mengulang kelompok di daftar "SUDAH ADA" (urutan karakter di dalam kelompok tidak
  penting: 己已巳 sama dengan 已己巳).

{FORMAT}

SUDAH ADA ({len(lines)} kelompok -- jangan diulang; tiap baris = 1 kelompok):
{chr(10).join(lines)}

Mulai sekarang. Keluarkan HANYA baris-baris NDJSON.
"""


def prompt_verifikasi(cands):
    body = "\n".join(json.dumps(c, ensure_ascii=False) for c in cands)
    return f"""\
Kamu adalah PEMERIKSA untuk database "Karakter Mirip" aplikasi belajar Mandarin
(pengguna berbahasa Indonesia). Di bawah ini ada {len(cands)} kelompok kandidat hasil AI lain.
Tugasmu memeriksa satu per satu dengan skeptis; kandidat sering salah.

{DEFINISI}

CATATAN: "note" awal pada sebagian kandidat dibuat otomatis dari data dekomposisi dan hanya
menyebut goresan/komponen tambahan (kadang tidak lengkap). Perbaiki dengan perbedaan yang
benar dan konkret; sebut POSISI goresan hanya kalau kamu yakin.

UNTUK SETIAP KANDIDAT, periksa:
1. Apakah SEMUA karakter adalah Hanzi sederhana yang NYATA (bukan karangan)? Kamu TIDAK perlu
   menilai apakah karakternya termasuk HSK atau umum: itu sudah disaring sebelumnya. JANGAN
   men-drop kandidat dengan alasan "bukan kosakata HSK" atau "jarang dipakai".
2. Apakah karakter-karakternya benar-benar mirip BENTUK (bukan sekadar bunyi/makna sama)?
3. Apakah "note" benar secara faktual: bagian yang disebut berbeda memang berbeda, dan
   ditulis dalam Bahasa Indonesia yang jelas?
4. Apakah ada anggota confusable_with yang sebenarnya tidak mirip? Kalau ada, buang anggota itu.
5. Periksa SETIAP klaim posisi komponen (kiri/kanan/atas/bawah) dan SETIAP komponen yang
   disebut, karakter demi karakter, dalam bentuk sederhana (mis. 练/炼 memakai 东, bukan
   柬). Kesalahan posisi/komponen sering terjadi -- jangan menganggap note sudah benar.
6. Kalau kelompok itu JENIS B (keluarga komponen: komponen sama, hanya radikal samping
   berbeda), DROP dengan alasan "jenis B".

HASIL PER KANDIDAT (satu baris NDJSON per kandidat, URUTAN SAMA seperti input):
- Layak (boleh dengan perbaikan): kembalikan objek skema yang sama
  {{"character":"...","confusable_with":["..."],"note":"..."}}
  Perbaikan yang diperbolehkan: membuang anggota yang tidak mirip, memperbaiki "note".
  Dilarang: mengganti "character" utama atau menambah karakter baru.
- Tidak layak: {{"character":"<karakter utama kandidat itu>","drop":"<alasan singkat>"}}

ATURAN:
- Kalau ragu, DROP. Jangan menebak.
- Jangan menambah kelompok baru yang tidak ada di input.
- Keluaran HANYA baris NDJSON: tanpa markdown, tanpa ```, tanpa teks lain.
- "note" wajib Bahasa Indonesia, menyebut persis bagian yang berbeda.

KANDIDAT:
{body}
"""


def peringatan_pending(data):
    """Tahap 1: peringatkan HANYA kalau ada file batch yang disimpan SETELAH terakhir kali
    confusion_groups.json berubah dan masih berisi kelompok yang belum masuk database
    (= tanda batch itu lupa di-apply). File lama yang tetap berada di tempatnya
    sesudah apply tidak memicu peringatan."""
    import glob
    sets = [frozenset(group_chars(g)) for g in data["groups"]]
    db_mtime = os.path.getmtime(PATH_GROUPS)
    ada = []
    for pat in ("verifikasi_karakter_mirip*.txt", "kandidat_karakter_mirip*.txt"):
        for fn in sorted(glob.glob(pat)):
            try:
                # file yang TIDAK lebih baru dari database = sudah lewat masa apply -> abaikan
                if os.path.getmtime(fn) <= db_mtime:
                    continue
                raw = open(fn, "r", encoding="utf-8", errors="replace").read()
            except OSError:
                continue
            n = 0
            for obj in iter_json_objects(raw):
                if "drop" in obj or validate_schema(obj):
                    continue
                cs = frozenset(group_chars(obj))
                if not any(cs <= s for s in sets):
                    n += 1
            if n:
                ada.append((fn, n))
    if ada:
        print("=" * 70)
        print("[PERINGATAN] Ada file batch yang disimpan SETELAH apply terakhir dan kelompoknya BELUM masuk database:")
        for fn, n in ada:
            print(f"   - {fn}: {n} kelompok")
        print("   Kalau itu batch yang masih mau dipakai -> jalankan gabungkan_karakter_mirip.py"
              " --apply DULU, lalu buat prompt ini lagi.")
        print("   Kalau itu cuma sisa/tidak dipakai -> abaikan saja (prompt tetap dibuat), atau"
              " kosongkan isi file itu.")
        print("=" * 70)


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    n = 30
    for a in sys.argv[1:]:
        if a.startswith("--n="):
            n = int(a.split("=", 1)[1])

    data, lines = load_existing_lines()

    if not args:
        peringatan_pending(data)
        with open(OUT1, "w", encoding="utf-8") as f:
            f.write(prompt_cari(n, lines))
        print(f"[OK] {OUT1} dibuat ({len(lines)} grup lama dimasukkan sbg daftar 'jangan diulang'; "
              f"meminta {n} kelompok).")
        print("     Tempel ke AI eksternal, simpan jawabannya sbg kandidat_karakter_mirip.txt")
        return

    src = args[0]
    with open(src, "r", encoding="utf-8", errors="replace") as f:
        raw = f.read()
    cands, buruk = [], 0
    for obj in iter_json_objects(raw):
        if "drop" in obj or validate_schema(obj):
            buruk += 1
            continue
        cands.append({"character": obj["character"],
                      "confusable_with": obj["confusable_with"], "note": obj["note"]})
    if not cands:
        print("[BERHENTI] Tidak ada kandidat valid di", src)
        sys.exit(1)
    with open(OUT2, "w", encoding="utf-8") as f:
        f.write(prompt_verifikasi(cands))
    print(f"[OK] {OUT2} dibuat: {len(cands)} kandidat masuk, {buruk} baris rusak/tak valid dilewati.")
    if len(cands) > 60:
        print("     Catatan: >60 kandidat sekaligus cenderung menurunkan ketelitian AI pemeriksa;"
              " pertimbangkan dipecah.")
    print("     Tempel ke AI KEDUA (beda dari tahap 1 kalau bisa), simpan jawabannya sbg"
          " verifikasi_karakter_mirip.txt")


if __name__ == "__main__":
    main()

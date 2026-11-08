# -*- coding: utf-8 -*-
"""
Bandingkan grammar_hsk1.json - grammar_hsk9.json di 2 folder berbeda
(mis. C:\\mandarin_app\\data\\ vs C:\\mandarin_app\\grammar\\) untuk cari
mana yang KUALITASNYA lebih baik, head-to-head per level.

JAWABAN PERTANYAAN #1 (folder mana yang dipakai app) SUDAH PASTI:
  Satu-satunya baris fetch() ke grammar_hsk*.json di SELURUH app ada di
  tatabahasa.html:
      const res = await fetch(`data/grammar_hsk${level}.json`);
  Jadi app SELALU baca dari folder 'data/' (relatif ke tempat server
  dijalankan, yaitu C:\\mandarin_app\\). Folder 'grammar/' TIDAK PERNAH
  dirujuk kode manapun -- kemungkinan sisa folder lama.
  Script ini fokus ke pertanyaan #2: kualitas head-to-head.

Cara pakai:
    python compare_grammar_folders.py "C:\\mandarin_app\\data" "C:\\mandarin_app\\grammar"
"""
import json
import sys
from pathlib import Path

def load_json(path):
    try:
        return json.loads(path.read_text(encoding="utf-8")), None
    except Exception as e:
        return None, str(e)

def flatten_strings(obj, acc):
    """Kumpulkan semua nilai string di dalam struktur (list/dict bersarang)
    utk mengukur 'kekayaan konten' -- lebih adil drpd cuma bandingkan ukuran
    file mentah (yg bisa beda krn indentasi/spasi, bukan isi)."""
    if isinstance(obj, str):
        acc.append(obj)
    elif isinstance(obj, dict):
        for v in obj.values():
            flatten_strings(v, acc)
    elif isinstance(obj, list):
        for v in obj:
            flatten_strings(v, acc)

def count_records(data):
    """Coba deteksi otomatis: list of records, atau dict of records."""
    if isinstance(data, list):
        return len(data)
    if isinstance(data, dict):
        return len(data)
    return None

def field_completeness(data):
    """Hitung, per field yang ADA di skema, berapa % entri yang field-nya
    terisi (bukan null/''/[])."""
    records = data if isinstance(data, list) else (list(data.values()) if isinstance(data, dict) else [])
    records = [r for r in records if isinstance(r, dict)]
    if not records:
        return {}
    all_fields = set()
    for r in records:
        all_fields |= set(r.keys())
    result = {}
    for f in sorted(all_fields):
        filled = sum(1 for r in records if r.get(f) not in (None, '', [], {}))
        result[f] = round(100 * filled / len(records), 1)
    return result

def compare_level(level, path_a, path_b, label_a, label_b):
    file_a = path_a / f"grammar_hsk{level}.json"
    file_b = path_b / f"grammar_hsk{level}.json"

    print(f"\n{'='*70}\nLEVEL HSK{level}\n{'='*70}")

    if not file_a.exists() and not file_b.exists():
        print(f"  Tidak ada di kedua folder, skip.")
        return None
    if not file_a.exists():
        print(f"  Hanya ada di {label_b} -- otomatis itu yang dipakai.")
        return label_b
    if not file_b.exists():
        print(f"  Hanya ada di {label_a} -- otomatis itu yang dipakai.")
        return label_a

    data_a, err_a = load_json(file_a)
    data_b, err_b = load_json(file_b)

    size_a = file_a.stat().st_size
    size_b = file_b.stat().st_size
    print(f"  Ukuran file : {label_a}={size_a:,} bytes | {label_b}={size_b:,} bytes")

    if err_a:
        print(f"  ⚠ {label_a} GAGAL PARSE JSON: {err_a} -> otomatis {label_b} menang (file rusak).")
        return label_b
    if err_b:
        print(f"  ⚠ {label_b} GAGAL PARSE JSON: {err_b} -> otomatis {label_a} menang (file rusak).")
        return label_a

    n_a = count_records(data_a)
    n_b = count_records(data_b)
    print(f"  Jumlah entri: {label_a}={n_a} | {label_b}={n_b}")

    strs_a, strs_b = [], []
    flatten_strings(data_a, strs_a)
    flatten_strings(data_b, strs_b)
    chars_a = sum(len(s) for s in strs_a)
    chars_b = sum(len(s) for s in strs_b)
    print(f"  Total karakter teks (semua field string, cara lebih adil drpd ukuran file mentah):")
    print(f"    {label_a}={chars_a:,} karakter | {label_b}={chars_b:,} karakter")

    comp_a = field_completeness(data_a)
    comp_b = field_completeness(data_b)
    all_fields = sorted(set(comp_a) | set(comp_b))
    if all_fields:
        print(f"  Kelengkapan field (% entri terisi, bukan kosong/null):")
        for f in all_fields:
            va = comp_a.get(f, '—')
            vb = comp_b.get(f, '—')
            flag = ''
            if isinstance(va, float) and isinstance(vb, float) and abs(va - vb) >= 1:
                flag = '  <-- BEDA' 
            print(f"    {f:30s} {label_a}={va!s:>6}%  {label_b}={vb!s:>6}%{flag}")

    # Skor sederhana: lebih banyak entri menang telak; kalau entri sama,
    # lebih banyak konten teks & field lebih lengkap yang menang.
    score_a = (n_a or 0) * 1000 + chars_a + sum(v for v in comp_a.values() if isinstance(v, (int, float)))
    score_b = (n_b or 0) * 1000 + chars_b + sum(v for v in comp_b.values() if isinstance(v, (int, float)))
    winner = label_a if score_a >= score_b else label_b
    print(f"  >>> Kesimpulan level ini: {winner} tampak lebih lengkap/kaya.")
    return winner

def main():
    if len(sys.argv) != 3:
        print("Cara pakai: python compare_grammar_folders.py <folder_A> <folder_B>")
        print(r'Contoh    : python compare_grammar_folders.py "C:\mandarin_app\data" "C:\mandarin_app\grammar"')
        sys.exit(1)

    path_a = Path(sys.argv[1])
    path_b = Path(sys.argv[2])
    label_a = f"A({path_a.name})"
    label_b = f"B({path_b.name})"

    if not path_a.exists():
        print(f"Folder A tidak ditemukan: {path_a}")
        sys.exit(1)
    if not path_b.exists():
        print(f"Folder B tidak ditemukan: {path_b}")
        sys.exit(1)

    print(f"Membandingkan grammar_hsk1-9.json:")
    print(f"  A = {path_a}")
    print(f"  B = {path_b}")

    winners = []
    for level in range(1, 10):
        w = compare_level(level, path_a, path_b, label_a, label_b)
        if w:
            winners.append(w)

    print(f"\n{'='*70}\nRINGKASAN AKHIR\n{'='*70}")
    from collections import Counter
    c = Counter(winners)
    for label, n in c.most_common():
        print(f"  {label} menang di {n}/9 level")

    print(f"""
CATATAN PENTING:
- Skor di atas HEURISTIK (jumlah entri + kekayaan teks + kelengkapan field),
  bukan penilaian linguistik. Kalau 2 folder skornya dekat/campur menang
  di level berbeda, sebaiknya رسلان intip manual 1-2 entri yang beda
  paling mencolok (lihat baris "<-- BEDA" di kelengkapan field) sebelum
  memutuskan mana yang jadi sumber final.
- File yang TERPAKAI aplikasi (dari kode, bukan tebakan) adalah folder
  'data/' -- lihat penjelasan di komentar atas file ini. Kalau ternyata
  folder 'grammar/' isinya lebih baik, رسلان perlu SALIN isinya ke
  'data/' (bukan ubah kode aplikasi) supaya tetap konsisten dgn arsitektur
  proyek (semua sumber data utama di 'data/').
""")

if __name__ == "__main__":
    main()

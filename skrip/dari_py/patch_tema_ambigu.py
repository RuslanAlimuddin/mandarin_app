#!/usr/bin/env python3
# patch_tema_ambigu.py
# Hapus beberapa kata yang masih ambigu dari tema tertentu
# Jalankan: python patch_tema_ambigu.py

import json, os
from collections import defaultdict

DATA_DIR   = r"C:\mandarin_app\data"
IN_WORDS   = os.path.join(DATA_DIR, "app_words.json")
OUT_WORDS  = os.path.join(DATA_DIR, "app_words.json")
OUT_THEME  = os.path.join(DATA_DIR, "index_theme.json")

# Kata yang harus DIHAPUS dari tema tertentu
# Format: { 'hanzi': ['tema1', 'tema2'] }
REMOVE_FROM_TEMA = {
    '公':   ['keluarga'],      # publik, bukan anggota keluarga
    '女':   ['keluarga'],      # perempuan (umum), bukan kata keluarga
    '子':   ['keluarga'],      # putra/anak (umum), terlalu ambigu
    '母':   ['keluarga'],      # ibu (terlalu umum sebagai prefix)
    '父':   ['keluarga'],      # ayah (terlalu umum sebagai prefix)
    '祖':   ['keluarga'],      # kakek/nenek (hanya prefix)
    '孙':   ['keluarga'],      # cucu (hanya prefix)
    '夫':   ['keluarga'],      # suami (hanya prefix)
    '婆':   ['keluarga'],      # mertua (hanya prefix)
    '婶':   ['keluarga'],      # bibi (hanya prefix)
    '侄':   ['keluarga'],      # keponakan (hanya prefix)
    '兄':   ['keluarga'],      # kakak (hanya prefix)
    '弟':   ['keluarga'],      # adik (hanya prefix)
    '姐':   ['keluarga'],      # kakak perempuan (hanya prefix)
    '妹':   ['keluarga'],      # adik perempuan (hanya prefix)
    '粉':   ['warna'],         # tepung/serbuk, bukan warna per se (粉色 sudah ada)
    '青':   ['warna'],         # ambigu (hijau/muda/dsb), 青色 sudah ada
    '金':   ['warna'],         # marga / emas (emas sebagai warna sudah ada di 金色)
    '银':   ['warna'],         # perak sebagai logam, bukan warna (银色 sudah ada)
    '玄':   ['warna'],         # hitam kuno, jarang dipakai
    '橙':   ['warna'],         # pohon jeruk — arti warna pakai 橙色
    '马':   ['hewan'],         # marga Ma — kartu harus cek apakah punya arti kuda
    '牛':   ['hewan'],         # marga Niu
    '鱼':   ['hewan'],         # marga Yu
    '龙':   ['hewan'],         # marga Long (naga = mitologis)
    '羊':   ['hewan'],         # marga Yang
    '熊':   ['hewan'],         # marga Xiong
    '鸟':   ['hewan'],         # varian vulgar (diao3)
    '兔':   ['hewan'],         # variasi karakter
    '鼠':   ['hewan'],         # bentuk terikat
    '鹰':   ['hewan'],         # cek apakah ada di HSK
}

print("Memuat data...")
with open(IN_WORDS, "r", encoding="utf-8") as f:
    words = json.load(f)

patched = 0
for w in words:
    simp = w.get('simplified', '')
    if simp in REMOVE_FROM_TEMA:
        temas_to_remove = REMOVE_FROM_TEMA[simp]
        old = w.get('themes', [])
        new = [t for t in old if t not in temas_to_remove]
        if new != old:
            w['themes'] = new
            print(f"  {simp}: {old} → {new}")
            patched += 1

print(f"\n✓ {patched} kata di-patch")

# Rebuild index_theme.json
print("\nRebuild index_theme.json...")
with open(OUT_THEME, "r", encoding="utf-8") as f:
    idx = json.load(f)

freq_map = {w.get('simplified',''): w.get('frequency', 99999) for w in words}

for tema_key in idx:
    kata = [w.get('simplified','') for w in words
            if tema_key in w.get('themes', [])]
    kata.sort(key=lambda x: freq_map.get(x, 99999))
    idx[tema_key]['words'] = kata
    idx[tema_key]['count'] = len(kata)

# Simpan
with open(OUT_WORDS, "w", encoding="utf-8") as f:
    json.dump(words, f, ensure_ascii=False)
print(f"✓ app_words.json disimpan")

with open(OUT_THEME, "w", encoding="utf-8") as f:
    json.dump(idx, f, ensure_ascii=False)
print(f"✓ index_theme.json disimpan")

# Tampilkan ringkasan akhir
print("\n── Jumlah kata per tema (final) ──")
for tema_key, v in sorted(idx.items(), key=lambda x: x[1]['label_id']):
    print(f"  {v['label_id']:<35} {v['count']:>4} kata")

print("\n✅ Patch selesai!")

"""
filter_balasan41.py
=====================
Saring balasan41.txt: buang baris untuk kata-kata yang teridentifikasi
SALAH klasifikasi dari tinjauan manual Claude (pola 于/为 sebagai
partikel gramatikal, dan pola verba+objek konkret yang salah ditandai
sinonim). Sisanya (yang sudah ditinjau dan benar) ditulis ke file baru.

Cara pakai:
    python filter_balasan41.py balasan41.txt balasan41_FILTERED.txt

Setelah itu jalankan seperti biasa:
    python import_corrections.py balasan41_FILTERED.txt --dry-run
    python import_corrections.py balasan41_FILTERED.txt
"""

import json
import sys

# Kata yang DIKECUALIKAN (tetap di pola lama / 动宾式-補充式, TIDAK direklasifikasi
# ke 联合式) -- hasil tinjauan manual Claude terhadap balasan41.txt
EXCLUDE_WORDS = {
    # Pola 1: karakter kedua 于/为 = partikel gramatikal, bukan sinonim
    "属于", "位于", "用于", "出于", "基于", "等于", "称为",
    # Pola 2: verba + objek konkret, bukan pasangan sinonim
    "生病", "放手", "开会", "收费", "购物", "违法", "得分", "救命",
    "上网", "惊人", "参赛", "住院", "迷人", "出场", "拍卖", "排队",
    "借口", "爱人", "知名", "绝望", "冒险", "转身", "自杀", "消费",
    "下载", "向前",
}


def main():
    if len(sys.argv) < 3:
        print("Cara pakai: python filter_balasan41.py <input.txt> <output.txt>")
        sys.exit(1)

    input_path = sys.argv[1]
    output_path = sys.argv[2]

    kept = []
    excluded = []

    with open(input_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                kept.append(line)  # biarkan baris aneh lolos, import_corrections yg akan tolak
                continue

            word = obj.get("word", "").strip()
            if word in EXCLUDE_WORDS:
                excluded.append(word)
            else:
                kept.append(line)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(kept))

    print(f"Total baris asli   : {len(kept) + len(excluded)}")
    print(f"Disimpan (aman)    : {len(kept)}  -> {output_path}")
    print(f"Dikecualikan       : {len(excluded)}")
    if excluded:
        print("  " + ", ".join(sorted(set(excluded))))
    print("\nKata yang dikecualikan TIDAK diubah -- tetap di pola lamanya (动宾式/补充式).")
    print("Lanjutkan dengan: python import_corrections.py " + output_path + " --dry-run")


if __name__ == "__main__":
    main()

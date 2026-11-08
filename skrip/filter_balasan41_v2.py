"""
filter_balasan41_v2.py
=========================
Versi ke-2 dari filter_balasan41.py -- daftar pengecualian diperluas
setelah tinjauan lanjutan menemukan lebih banyak kata dengan pola
kesalahan yang sama (objek konkret / partikel gramatikal disalahartikan
sebagai morfem sinonim).

Jalankan pada file ASLI balasan41.txt (bukan hasil filter v1), supaya
tidak bingung tumpang-tindih.

Cara pakai:
    python filter_balasan41_v2.py balasan41.txt balasan41_FILTERED_v2.txt

Setelah itu:
    python import_corrections.py balasan41_FILTERED_v2.txt --dry-run
"""

import json
import sys

EXCLUDE_WORDS = {
    # --- dari saringan babak 1 ---
    "上网", "下载", "位于", "住院", "借口", "冒险", "出于", "出场",
    "参赛", "向前", "基于", "属于", "开会", "得分", "惊人", "拍卖",
    "排队", "收费", "放手", "救命", "消费", "爱人", "生病", "用于",
    "知名", "称为", "等于", "绝望", "自杀", "购物", "转身", "违法",
    "迷人",
    # --- tambahan dari saringan babak 2 ---
    "说话", "对话", "签名", "拍照", "摄影", "录像", "跳舞",
    "升级", "加速", "赚钱", "辞职", "出席", "约会", "跟踪",
    "失踪", "在场", "在意", "移民", "化妆", "决心", "尽力",
    "收回", "深入", "陷入", "相比", "相处", "造型", "面试", "吵架",
}


def main():
    if len(sys.argv) < 3:
        print("Cara pakai: python filter_balasan41_v2.py <input.txt> <output.txt>")
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
                kept.append(line)
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
    print("\nLanjutkan dengan: python import_corrections.py " + output_path + " --dry-run")


if __name__ == "__main__":
    main()

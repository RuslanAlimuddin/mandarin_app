#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
fix_15_words_round2.py

Perbaikan untuk 15 kata dari putaran audit kedua (BLUEPRINT v18 Bagian E
poin 2), ditemukan via audit_known_polyphones.py + audit_brand_first_meaning.py:

KELOMPOK A — bacaan langka/sastra dipromosikan jadi field pinyin utama
(pola sama dgn 上/单 sesi sebelumnya). Isi meanings_id/en didominasi arti
utk bacaan umum, tapi field pinyin menyimpan bacaan langka:
    号 (háo->hào), 看 (kān->kàn), 说 (shuì->shuō),
    落 (là->luò), 圈 (juān->quān), 藏 (zàng->cáng), 结 (jiē->jié)

KELOMPOK B — nama merek dagang jadi arti pertama (pola sama dgn
老板/现代/大众/加/头条 sesi sebelumnya), kata majemuk:
    苹果 (Apple->apel), 吉利 (Geely->baik/beruntung),
    标致 (Peugeot->cantik), 全家 (FamilyMart->seluruh keluarga),
    老板 (Robam->bos/pemilik bisnis)

KELOMPOK C — bug field lain (bukan pinyin/urutan arti):
    假  : field `pinyin`("gēi") DAN `traditional`("叚") salah total --
          harusnya pinyin "jiǎ", traditional "假" (tak berubah dari simplified)
    血  : baris arti pertama "lihat 血[xue4]" adalah referensi ke diri
          sendiri (sampah data) -- dihapus
    严寒: typo spasi hilang "dingin yangMenusuk" -> "dingin yang menusuk"

CATATAN TAMBAHAN: beberapa entri (假, 老板, 说) punya baris "varian dari
X[...]" yang ternyata merujuk ke DIRINYA SENDIRI (mis. entri 假 bilang
"varian dari 假[jia3]") -- ini sampah data/artefak, ikut dihapus di
perbaikan ini karena tidak informatif dan membingungkan.

WAJIB jalankan --dry-run dulu. Backup otomatis dibuat sebelum --apply.

Penggunaan:
    python fix_15_words_round2.py --dry-run
    python fix_15_words_round2.py --apply
"""
import json
import argparse
import shutil
import datetime
import sys
from pathlib import Path

DATA_PATH = Path("data/app_words.json")

FIXES = {
    # ------------------------- KELOMPOK A -------------------------
    "号": {
        "pinyin": "hào",
        "pinyin_numeric": "hao4",
        "bopomofo": "ㄏㄠˋ",
        "meanings_id": [
            "nomor urut",
            "KP:個|个[ge4]",
            "tanggal dalam sebulan",
            "tanda",
            "nama perusahaan",
            "ukuran",
            "akhiran kapal",
            "terompet (instrumen tiup)",
            "komando terompet",
            "nama samaran",
            "mengambil denyut nadi",
            "klasifier yang digunakan untuk menunjukkan jumlah orang",
            "(bacaan khusus háo) auman",
            "(bacaan khusus háo) teriakan",
        ],
        "meanings_en": [
            "ordinal number",
            "day of a month",
            "mark",
            "sign",
            "business establishment",
            "size",
            "ship suffix",
            "horn (wind instrument)",
            "bugle call",
            "assumed name",
            "to take a pulse",
            "classifier used to indicate number of people",
            "(pr. háo) roar",
            "(pr. háo) cry",
        ],
    },
    "看": {
        "pinyin": "kàn",
        "pinyin_numeric": "kan4",
        "bopomofo": "ㄎㄢˋ",
        "meanings_id": [
            "menonton",
            "melihat; memandang",
            "membaca",
            "mengunjungi; bertamu",
            "mempertimbangkan; menganggap",
            "mengobati (pasien atau penyakit)",
            "bergantung pada",
            "merasa (bahwa)",
            "(setelah kata kerja) mencoba",
            "hati-hati",
            "(bacaan khusus kān) menjaga",
            "(bacaan khusus kān) mengurus",
            "(bacaan khusus kān) mengawasi",
        ],
        "meanings_en": [
            "to watch",
            "to see; to look at",
            "to read",
            "to visit; to call on",
            "to consider; to regard as",
            "to treat (a patient or illness)",
            "to depend on",
            "to feel (that)",
            "(after a verb) to give it a try",
            "to watch out for",
            "(pr. kān) to look after",
            "(pr. kān) to take care of",
            "(pr. kān) to guard",
        ],
    },
    "说": {
        "pinyin": "shuō",
        "pinyin_numeric": "shuo1",
        "bopomofo": "ㄕㄨㄛ",
        "meanings_id": [
            "berbicara; berkata",
            "menjelaskan; berkomentar",
            "memarahi; memberhentikan",
            "(bentuk terikat) teori; doktrin",
            "(bacaan khusus shuì) membujuk",
        ],
        "meanings_en": [
            "to speak; to talk; to say",
            "to explain; to comment",
            "to scold; to tell off",
            "(bound form) theory; doctrine",
            "(pr. shuì) to persuade",
        ],
    },
    "落": {
        "pinyin": "luò",
        "pinyin_numeric": "luo4",
        "bopomofo": "ㄌㄨㄛˋ",
        "meanings_id": [
            "jatuh atau merosot",
            "(matahari) terbenam",
            "(pasang surut) surut",
            "menurunkan",
            "menurun atau tenggelam",
            "jatuh ke",
            "beristirahat dengan",
            "mendapatkan atau menerima",
            "menuliskan",
            "keberadaan",
            "penyelesaian",
            "(bacaan khusus là, bacaan sehari-hari dalam beberapa gabungan kata) meninggalkan",
            "(bacaan khusus là) hilang",
            "(bacaan khusus là) lupa membawa",
            "(bacaan khusus là) tertinggal",
        ],
        "meanings_en": [
            "to fall or drop",
            "(of the sun) to set",
            "(of a tide) to go out",
            "to lower",
            "to decline or sink",
            "to fall onto",
            "to rest with",
            "to get or receive",
            "to write down",
            "whereabouts",
            "settlement",
            "(pr. là, colloquial reading in certain compounds) to leave out",
            "(pr. là) to be missing",
            "(pr. là) to leave behind or forget to bring",
            "(pr. là) to lag or fall behind",
        ],
    },
    "圈": {
        "pinyin": "quān",
        "pinyin_numeric": "quan1",
        "bopomofo": "ㄑㄩㄢ",
        "meanings_id": [
            "lingkaran; cincin; putaran",
            "KP:個|个[ge4]",
            "kata penggolong untuk putaran, orbit, putaran balapan dll",
            "mengelilingi; melingkari",
            "(bacaan khusus juān) membatasi",
            "(bacaan khusus juān) mengunci",
            "(bacaan khusus juān) memasukkan ke dalam kandang",
            "(bacaan khusus juàn) kandang ternak; kandang; lipatan; kandang babi",
        ],
        "meanings_en": [
            "circle; ring; loop",
            "classifier for loops, orbits, laps of race etc",
            "to surround; to circle",
            "(pr. juān) to confine",
            "(pr. juān) to lock up",
            "(pr. juān) to pen in",
            "(pr. juàn) livestock enclosure; pen; fold; sty",
        ],
    },
    "藏": {
        "pinyin": "cáng",
        "pinyin_numeric": "cang2",
        "bopomofo": "ㄘㄤˊ",
        "meanings_id": [
            "menyembunyikan",
            "menyimpan jauh-jauh",
            "menyimpan",
            "mengumpulkan",
            "gudang",
            "depot",
            "(bacaan khusus zàng) Tibet",
            "(bacaan khusus zàng) singkatan dari Wilayah Otonomi Xizang atau Tibet 西藏[Xi1 zang4]",
            "(bacaan khusus zàng) kitab suci Buddha atau Tao",
        ],
        "meanings_en": [
            "to conceal",
            "to hide away",
            "to harbor",
            "to store",
            "to collect",
            "storehouse",
            "depository",
            "(pr. zàng) Tibet",
            "(pr. zàng) abbr. for Xizang or Tibet Autonomous Region 藏",
            "(pr. zàng) Buddhist or Taoist scripture",
        ],
    },
    "结": {
        "pinyin": "jié",
        "pinyin_numeric": "jie2",
        "bopomofo": "ㄐㄧㄝˊ",
        "meanings_id": [
            "simpul",
            "kokoh",
            "ikatan",
            "mengikat",
            "memesan (checkout dari hotel)",
            "(bacaan khusus jiē) (tumbuhan) menghasilkan (buah atau biji) — di Taiwan dibaca [jié]",
        ],
        "meanings_en": [
            "knot",
            "sturdy",
            "bond",
            "to tie",
            "to bind",
            "to check out (of a hotel)",
            "(pr. jiē) (of a plant) to produce (fruit or seeds) — Taiwan pr. [jié]",
        ],
    },
    # ------------------------- KELOMPOK B -------------------------
    "苹果": {
        "meanings_id": [
            "apel",
            "KP:個|个[ge4],顆|颗[ke1]",
            "Apple (perusahaan teknologi Amerika)",
        ],
        # meanings_en sudah benar (hanya ["apple"]), tidak disentuh
    },
    "吉利": {
        "meanings_id": [
            "baik",
            "beruntung",
            "menguntungkan",
            "Geely, merek mobil Tiongkok",
        ],
        "meanings_en": [
            "auspicious",
            "lucky",
            "propitious",
            "Geely, Chinese car make",
        ],
    },
    "标致": {
        "meanings_id": [
            "(wanita) cantik; elok",
            "Peugeot (merek mobil)",
        ],
        "meanings_en": [
            "beautiful (of woman)",
            "pretty",
            "Peugeot",
        ],
    },
    "全家": {
        "meanings_id": [
            "seluruh keluarga",
            "FamilyMart (jaringan toko serba ada)",
        ],
        # meanings_en sudah benar (hanya ["whole family"]), tidak disentuh
    },
    "老板": {
        "meanings_id": [
            "bos",
            "pemilik bisnis",
            "KP:個|个[ge4]",
            "Robam (merek)",
        ],
        "meanings_en": [
            "boss",
            "business proprietor",
            "Robam (brand)",
        ],
    },
    # ------------------------- KELOMPOK C -------------------------
    "假": {
        "pinyin": "jiǎ",
        "pinyin_numeric": "jia3",
        "bopomofo": "ㄐㄧㄚˇ",
        "traditional": "假",
        "meanings_id": [
            "palsu",
            "tiruan",
            "buatan",
            "meminjam",
            "jika",
            "seandainya",
            "liburan",
            "(bacaan khusus gēi) digunakan dalam 假掰[gei1 bai1]",
        ],
        "meanings_en": [
            "fake",
            "false",
            "artificial",
            "to borrow",
            "if",
            "suppose",
            "vacation",
            "(pr. gēi) used in 掰",
        ],
    },
    "血": {
        "meanings_id": [
            "darah",
            "pelafalan sehari-hari [xie3]",
            "KP:滴[di1],片[pian4]",
        ],
        "meanings_en": [
            "blood",
            "colloquial pr. [xiě]",
        ],
    },
    "严寒": {
        "meanings_id": [
            "dingin yang menusuk",
            "musim dingin yang parah",
        ],
        # meanings_en sudah benar, tidak disentuh
    },
}


def load_json(path: Path):
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def find_entry(data, word):
    if isinstance(data, dict):
        candidates = data.get(word)
        if candidates is not None:
            return [candidates]
        return []
    return [e for e in data if e.get("id") == word or e.get("simplified") == word]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--path", default=str(DATA_PATH))
    args = ap.parse_args()

    if not args.dry_run and not args.apply:
        print("Pilih --dry-run atau --apply.")
        sys.exit(1)

    path = Path(args.path)
    if not path.exists():
        print(f"File tidak ditemukan: {path}")
        sys.exit(1)

    data = load_json(path)

    not_found = []
    changed_count = 0

    for word, updates in FIXES.items():
        matches = find_entry(data, word)
        if not matches:
            not_found.append(word)
            continue
        for entry in matches:
            print(f"=== {word} ===")
            for field, new_val in updates.items():
                old_val = entry.get(field)
                if old_val != new_val:
                    print(f"  [{field}]")
                    print(f"    LAMA: {old_val}")
                    print(f"    BARU: {new_val}")
                    if args.apply:
                        entry[field] = new_val
            print()
            changed_count += 1

    if not_found:
        print("PERINGATAN — kata tidak ditemukan di file:", ", ".join(not_found))
        print()

    print(f"Total entri diproses: {changed_count} / {len(FIXES)} kata")

    if args.apply:
        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = path.with_name(f"{path.stem}.bak_round2_{ts}{path.suffix}")
        shutil.copy2(path, backup_path)
        print(f"Backup dibuat: {backup_path}")

        with path.open("w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"Tersimpan: {path}")
    else:
        print("\n(Ini --dry-run, tidak ada file yang diubah. Jalankan --apply setelah dicek.)")


if __name__ == "__main__":
    main()

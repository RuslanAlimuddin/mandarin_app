#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
fix_18_words_manual.py

Perbaikan manual untuk 18 kata dari BLUEPRINT v18 Bagian B/E:
  - 8 kata "exclude": 以, 现代, 大众, 大学, 美德, 比, 率, 红
  - 10 kata "mencurigakan": 上, 新, 加, 哈, 单, 保, 签, 佛, 扬, 头条

Ditemukan 4 bug TAMBAHAN saat review manual (di luar sekadar urutan arti):
  1. 上  : field pinyin utama salah -> "shǎng" (bacaan khusus 上声) padahal
           seharusnya "shàng" (bacaan umum: atas/naik/menghadiri kelas).
  2. 单  : field pinyin utama salah -> "chán" (bacaan khusus 單于) padahal
           seharusnya "dān" (bacaan umum: tunggal/hanya/formulir).
  3. 率  : pinyin ("shuài") tidak konsisten dengan bopomofo ("ㄌㄩˋ" = lǜ).
           Diputuskan pinyin ikut bopomofo -> "lǜ" (tingkat/rasio),
           karena itu pemakaian dominan kata ini berdiri sendiri.
  4. 红  : meanings_id (6 item) dan meanings_en (5 item) TIDAK sinkron;
           arti paling dasar "merah" (red) hilang total dari meanings_id.
           Direkonstruksi ulang.
  5. 佛  : field `traditional` salah -> "彿" (karakter varian lain),
           seharusnya "佛" (tidak berubah dari simplified).

CATATAN KHUSUS - 签:
  Data aslinya TIDAK sekadar butuh reorder — tampak tercampur dari dua
  entri berbeda (签 dan varian karakter 籤), field meanings_id (5 item)
  vs meanings_en (9 item) sangat tidak seimbang. Versi di bawah adalah
  REKONSTRUKSI, bukan cuma reorder. MOHON DICEK EKSTRA HATI-HATI oleh
  رسلان sebelum apply, atau jalankan --skip-qian untuk melewati kata
  ini dulu dan tangani terpisah.

WAJIB jalankan --dry-run dulu. Backup otomatis dibuat sebelum --apply.

Penggunaan:
    python fix_18_words_manual.py --dry-run
    python fix_18_words_manual.py --dry-run --skip-qian
    python fix_18_words_manual.py --apply
    python fix_18_words_manual.py --apply --skip-qian
"""
import json
import argparse
import shutil
import datetime
import sys
from pathlib import Path

DATA_PATH = Path("data/app_words.json")

# ---------------------------------------------------------------------------
# Definisi perbaikan per kata.
# Field selain "meanings_id"/"meanings_en"/"pinyin"/"pinyin_numeric"/
# "bopomofo"/"traditional" TIDAK disentuh sama sekali.
# ---------------------------------------------------------------------------

FIXES = {
    "上": {
        "pinyin": "shàng",
        "pinyin_numeric": "shang4",
        "bopomofo": "ㄕㄤˋ",
        "meanings_id": [
            "atas; bagian atas; di atas; sebelumnya",
            "menghadiri (kelas atau universitas)",
            "memanjat; naik ke; naik",
            "(pelengkap pengarah) ke atas",
            "(akhiran kata benda) di",
            "pertama (dari beberapa bagian)",
            "(bacaan khusus shǎng) digunakan dalam 上聲|上声[shang3 sheng1]",
        ],
        "meanings_en": [
            "up; upper; above; previous",
            "to attend (class or university)",
            "to climb; to get onto; to go up",
            "(directional complement) up",
            "(noun suffix) on; above",
            "first (of multiple parts)",
            "(pr. shǎng) used in 上声",
        ],
    },
    "新": {
        "meanings_id": [
            "baru",
            "baru saja",
            "meso-(kimia)",
            "singkatan dari Xinjiang 新疆[Xin1 jiang1]",
            "singkatan dari Singapura 新加坡[Xin1 jia1 po1]",
            "marga Xin",
        ],
        "meanings_en": [
            "new",
            "newly",
            "meso- (chemistry)",
            "abbr. for Xinjiang 疆",
            "abbr. for Singapore 坡",
            "surname Xin",
        ],
    },
    "比": {
        "meanings_id": [
            "membandingkan",
            "(diikuti oleh kata benda dan kata sifat) lebih {kata sifat} daripada {kata benda}",
            "rasio",
            "memberi isyarat",
            "(Taiwan dibaca [bi4] dalam beberapa senyawa yang berasal dari Bahasa Tionghoa Klasik)",
            "Belgia",
            "singkatan dari 比利時|比利时[Bi3 li4 shi2]",
            "varian eupemistik dari 屄[bi1]",
        ],
        "meanings_en": [
            "to compare",
            "(followed by a noun and adjective) more {adj.} than {noun}",
            "ratio",
            "to gesture",
            "(Taiwan pr. [bì] in some compounds derived from Classical Chinese)",
            "Belgium",
            "Belgian",
            "abbr. for 比利时",
            "euphemistic variant of 屄",
        ],
    },
    "以": {
        "meanings_id": [
            "menggunakan",
            "dengan cara",
            "menurut",
            "agar",
            "karena",
            "pada (tanggal atau tempat tertentu)",
            "singkatan dari Israel 以色列[Yi3 se4 lie4]",
            "varian lama dari 以[yi3]",
        ],
        "meanings_en": [
            "to use",
            "by means of",
            "according to",
            "in order to",
            "because of",
            "at (a certain date or place)",
            "abbr. for Israel 列",
            "old variant of 以",
        ],
    },
    "加": {
        "meanings_id": [
            "menambah",
            "(matematika) ditambah",
            "untuk meningkatkan; untuk menambah",
            "(digunakan sebelum kata kerja dua suku kata, seringkali setelah kata "
            "keterangan seperti 不[bu4], 大[da4], 稍[shao1] dll, untuk menunjukkan "
            "bahwa tindakan tersebut berlaku untuk sesuatu yang disebutkan "
            "sebelumnya, seperti dalam 稍加改良[shao1 jia1 gai3 liang2] \"membuat "
            "beberapa perbaikan kecil pada (itu)\")",
            "menerapkan (batasan dll) kepada (seseorang)",
            "memberikan (dukungan, pertimbangan dll) kepada (sesuatu)",
            "Kanada (singkatan dari 加拿大[Jia1 na2 da4])",
            "marga Jia",
        ],
        "meanings_en": [
            "to add",
            "plus",
            "(used after an adverb such as 不, 大, 稍 etc, and before a disyllabic "
            "verb, to indicate that the action of the verb is applied to sth or "
            "sb previously mentioned)",
            "to apply (restrictions etc) to (sb)",
            "to give (support, consideration etc) to (sth)",
            "Canada (abbr. for 大)",
            "surname Jia",
        ],
    },
    "哈": {
        "meanings_id": [
            "(kata seru) ha!",
            "(tiruan bunyi untuk tertawa)",
            "(slang) tergila-gila dengan; memuja",
            "(bentuk terikat) husky (anjing) (singkatan dari 哈士奇[ha1 shi4 qi2])",
            "anjing Peking; anjing pesek",
            "(dialek) memarahi",
            "singkatan dari 哈薩克斯坦|哈萨克斯坦[Ha1 sa4 ke4 si1 tan3], Kazakhstan",
            "singkatan dari 哈爾濱|哈尔滨[Ha1 er3 bin1], Harbin",
        ],
        "meanings_en": [
            "(interj.) ha!",
            "(onom. for laughter)",
            "(slang) to be infatuated with",
            "to adore",
            "abbr. for 奇, husky (dog)",
            "a Pekinese",
            "a pug",
            "(dialect) to scold",
            "abbr. for 哈萨克斯坦, Kazakhstan",
            "abbr. for 哈尔滨, Harbin",
        ],
    },
    "红": {
        "meanings_id": [
            "merah",
            "populer",
            "bonus",
            "revolusioner",
            "marga Hong",
            "digunakan dalam 女紅|女红 (pekerjaan tangan/jahitan wanita)",
        ],
        "meanings_en": [
            "red",
            "popular",
            "bonus",
            "revolutionary",
            "surname Hong",
            "used in 女红 (women's needlework)",
        ],
    },
    "大学": {
        "meanings_id": [
            "universitas",
            "akademi",
            "KP:所[suo3]",
            "The Great Learning, salah satu dari Empat Buku 四書|四书[Si4 shu1] dalam Konfusianisme",
        ],
        "meanings_en": [
            "university",
            "college",
            "the Great Learning, one of the Four Books 四书 in Confucianism",
        ],
    },
    "单": {
        "pinyin": "dān",
        "pinyin_numeric": "dan1",
        "bopomofo": "ㄉㄢ",
        "meanings_id": [
            "tunggal",
            "hanya",
            "satu-satunya",
            "nomor ganjil",
            "tagihan",
            "daftar",
            "formulir",
            "KP:個|个[ge4]",
            "(bacaan khusus chán) digunakan dalam 單于|单于[chan2 yu2]",
            "(bacaan khusus shàn) marga Shan",
        ],
        "meanings_en": [
            "single",
            "only",
            "sole",
            "odd number",
            "bill",
            "list",
            "form",
            "(pr. chán) used in 單于",
            "(pr. shàn) surname Shan",
        ],
    },
    "保": {
        "meanings_id": [
            "membela; melindungi; menjaga",
            "menjamin; memastikan",
            "(kuno) unit administrasi sipil dalam sistem baojia 保甲[bao3 jia3]",
            "Bulgaria (singkatan dari 保加利亞|保加利亚[Bao3 jia1 li4 ya4])",
        ],
        "meanings_en": [
            "to defend; to protect; to keep",
            "to guarantee; to ensure",
            "civil administration unit in the baojia 甲 system (old)",
            "Bulgaria",
            "Bulgarian",
            "abbr. for 保加利亚",
        ],
    },
    # --- 签: REKONSTRUKSI, bukan sekadar reorder. Lihat catatan di header. ---
    "签": {
        "meanings_id": [
            "menandatangani nama; membubuhkan tanda tangan",
            "menulis komentar singkat pada dokumen",
            "visa",
            "tongkat bambu bertuliskan (digunakan dalam ramalan, perjudian, undian dll)",
            "serpihan kayu kecil",
            "label",
            "tag",
        ],
        "meanings_en": [
            "to sign one's name",
            "to write brief comments on a document",
            "visa",
            "inscribed bamboo stick (used in divination, gambling, drawing lots etc)",
            "small wood sliver",
            "label",
            "tag",
        ],
    },
    "现代": {
        "meanings_id": [
            "zaman modern",
            "era modern",
            "Hyundai, perusahaan Korea Selatan",
        ],
        "meanings_en": [
            "modern times",
            "modern age",
            "modern era",
            "Hyundai, South Korean company",
        ],
    },
    "率": {
        "pinyin": "lǜ",
        "pinyin_numeric": "lü4",
        "meanings_id": [
            "rasio; tingkat; proporsi",
            "umumnya",
            "biasanya",
            "jujur",
            "terus terang",
            "(bacaan khusus shuài) memimpin",
            "(bacaan khusus shuài) memerintah",
            "(bacaan khusus shuài) ceroboh",
            "(bacaan khusus shuài) terburu-buru",
        ],
        "meanings_en": [
            "rate; ratio; proportion",
            "generally",
            "usually",
            "frank",
            "straightforward",
            "(pr. shuài) to lead",
            "(pr. shuài) to command",
            "(pr. shuài) rash",
            "(pr. shuài) hasty",
        ],
    },
    "大众": {
        "meanings_id": [
            "massa",
            "mayoritas populasi",
            "populer (musik, sains, dll)",
            "Volkswagen (produsen mobil)",
        ],
        "meanings_en": [
            "the masses",
            "the great bulk of the population",
            "popular (of music, science etc)",
            "Volkswagen (automobile manufacturer)",
        ],
    },
    "佛": {
        "traditional": "佛",
        # urutan meanings sudah cukup baik (Buddha di posisi pertama), tidak diubah
    },
    "扬": {
        "meanings_id": [
            "mengangkat",
            "mengibarkan",
            "menaburkan (tertiup angin)",
            "mengepak",
            "menyebarkan",
            "singkatan dari Yangzhou 揚州|扬州[Yang2 zhou1] di Jiangsu",
            "marga Yang",
            "varian dari 揚|扬[yang2]",
        ],
        "meanings_en": [
            "to raise",
            "to hoist",
            "the action of tossing or winnowing",
            "scattering (in the wind)",
            "to flutter",
            "to propagate",
            "abbr. for 扬州",
            "surname Yang",
            "variant of 扬",
        ],
    },
    "美德": {
        "meanings_id": ["kebajikan", "Amerika Serikat dan Jerman"],
        "meanings_en": ["virtue", "USA and Germany"],
    },
    "头条": {
        "meanings_id": [
            "berita utama (di berita)",
            "Toutiao, aplikasi rekomendasi konten yang dipersonalisasi "
            "(singkatan dari 今日頭條|今日头条[Jin1 ri4 Tou2 tiao2])",
        ],
        "meanings_en": [
            "lead story (on the news)",
            "Toutiao, personalized content recommendation app (abbr. for 今日头条)",
        ],
    },
}


def load_json(path: Path):
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def find_entry(data, word):
    """Cocokkan berdasar field id ATAU simplified (jaga-jaga beda struktur)."""
    if isinstance(data, dict):
        candidates = data.get(word)
        if candidates is not None:
            return [candidates], "dict"
        return [], "dict"
    matches = [e for e in data if e.get("id") == word or e.get("simplified") == word]
    return matches, "list"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--skip-qian", action="store_true",
                     help="Lewati 签 (masih perlu review manual terpisah)")
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

    fixes = dict(FIXES)
    if args.skip_qian:
        fixes.pop("签", None)
        print("(--skip-qian aktif: 签 dilewati)\n")

    not_found = []
    changed_count = 0

    for word, updates in fixes.items():
        matches, _ = find_entry(data, word)
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

    print(f"Total entri diproses: {changed_count} / {len(fixes)} kata")

    if args.apply:
        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = path.with_name(f"{path.stem}.bak_manual18_{ts}{path.suffix}")
        shutil.copy2(path, backup_path)
        print(f"Backup dibuat: {backup_path}")

        with path.open("w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"Tersimpan: {path}")
    else:
        print("\n(Ini --dry-run, tidak ada file yang diubah. Jalankan --apply setelah dicek.)")


if __name__ == "__main__":
    main()

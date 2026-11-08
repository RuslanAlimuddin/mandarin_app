# scrape_allset_themes.py
# Mengambil daftar kosakata bertema dari AllSet Learning Vocabulary Wiki
# (https://resources.allsetlearning.com/chinese/vocabulary/Category:HSK_Themed_Vocabulary_Lists)
#
# CATATAN LISENSI:
#   Konten wiki ini berlisensi Creative Commons (CC) — gratis dipakai untuk NON-KOMERSIAL
#   dengan syarat mencantumkan atribusi. Karena aplikasi Mandarin Interaktif untuk
#   penggunaan pribadi (bukan dijual/komersial), ini aman dipakai. Atribusi sudah
#   disertakan otomatis di field "source" pada tiap tema hasil scrape.
#
# CARA PAKAI:
#   1. pip install requests beautifulsoup4 --break-system-packages
#   2. Taruh script ini di folder mana saja (tidak perlu di C:\mandarin_app\)
#   3. Jalankan: python scrape_allset_themes.py
#   4. Hasil: themes_external_raw.json (daftar tema mentah hasil scrape, BELUM
#      dicocokkan dengan app_words.json — lihat langkah lanjutan di bawah)
#
# LANGKAH LANJUTAN (dilakukan terpisah, sesi berikutnya):
#   File themes_external_raw.json ini perlu di-MATCH dengan id/simplified yang sudah
#   ada di app_words.json supaya bisa dipakai sebagai deck flashcard (karena flashcard
#   butuh wordId yang valid, bukan kata sembarang). Proses matching ini akan dibuatkan
#   script terpisah ('merge_themes.py') setelah رسلان konfirmasi hasil scrape ini sudah
#   sesuai harapan.

import json
import os
import re
import sys
import time

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    print("[ERROR] Paket 'requests' dan/atau 'beautifulsoup4' belum terinstall.")
    print("        Jalankan dulu: pip install requests beautifulsoup4 --break-system-packages")
    sys.exit(1)

BASE_URL     = 'https://resources.allsetlearning.com'
CATEGORY_URL = BASE_URL + '/chinese/vocabulary/Category:HSK_Themed_Vocabulary_Lists'
OUTPUT_FILE  = 'themes_external_raw.json'

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (compatible; MandarinInteraktifBot/1.0; personal-use-scraper)'
}

# Jeda antar request supaya tidak membebani server (sopan ke pihak wiki)
REQUEST_DELAY_SEC = 1.0


def slugify(title):
    """'HSK Animals Vocabulary List' -> 'animals' (untuk dipakai sebagai key tema)."""
    s = title.lower()
    s = re.sub(r'^hsk\s+', '', s)
    s = re.sub(r'\s+vocabulary\s+list.*$', '', s)
    s = re.sub(r'[^a-z0-9]+', '_', s).strip('_')
    return s or title.lower().replace(' ', '_')


def get_all_page_links():
    """Ambil semua link halaman tema dari halaman kategori."""
    print(f"[INFO] Mengambil daftar halaman dari kategori ...")
    resp = requests.get(CATEGORY_URL, headers=HEADERS, timeout=20)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, 'html.parser')

    # Halaman kategori MediaWiki: link ada di dalam <div id="mw-pages"> atau mw-category
    links = []
    container = soup.find(id='mw-pages') or soup.find(class_='mw-category-group') or soup
    for a in container.find_all('a', href=True):
        href = a['href']
        title = a.get_text(strip=True)
        if '/chinese/vocabulary/' in href and 'Category:' not in href and 'Special:' not in href:
            full_url = href if href.startswith('http') else BASE_URL + href
            links.append((title, full_url))

    # Buang duplikat sambil pertahankan urutan
    seen = set()
    unique_links = []
    for title, url in links:
        if url not in seen:
            seen.add(url)
            unique_links.append((title, url))

    print(f"[INFO] Ditemukan {len(unique_links)} halaman tema.")
    return unique_links


def parse_vocab_table(soup):
    """
    Ambil tabel kosakata dari halaman tema. Mendukung kolom:
    Chinese | Pinyin | English | (HSK Level opsional, urutan kolom bisa beda)
    Mengembalikan list of dict: {hanzi, pinyin, meaning_en, hsk_level}
    """
    words = []
    tables = soup.find_all('table')

    for table in tables:
        rows = table.find_all('tr')
        if not rows:
            continue

        header_cells = [c.get_text(strip=True).lower() for c in rows[0].find_all(['th', 'td'])]
        if not header_cells:
            continue

        # Cari index kolom berdasarkan nama header (fleksibel urutan)
        col_idx = {}
        for i, h in enumerate(header_cells):
            if 'chinese' in h or 'hanzi' in h:
                col_idx['hanzi'] = i
            elif 'pinyin' in h:
                col_idx['pinyin'] = i
            elif 'english' in h:
                col_idx['meaning_en'] = i
            elif 'hsk' in h or 'level' in h:
                col_idx['hsk_level'] = i

        if 'hanzi' not in col_idx:
            continue  # bukan tabel kosakata yang kita cari

        for row in rows[1:]:
            cells = row.find_all(['td', 'th'])
            if len(cells) <= col_idx['hanzi']:
                continue
            cell_texts = [c.get_text(strip=True) for c in cells]

            hanzi = cell_texts[col_idx['hanzi']] if col_idx.get('hanzi', -1) < len(cell_texts) else ''
            if not hanzi or not any('\u4e00' <= ch <= '\u9fff' for ch in hanzi):
                continue

            entry = {
                'hanzi': hanzi,
                'pinyin': cell_texts[col_idx['pinyin']] if col_idx.get('pinyin', -1) < len(cell_texts) and 'pinyin' in col_idx else '',
                'meaning_en': cell_texts[col_idx['meaning_en']] if col_idx.get('meaning_en', -1) < len(cell_texts) and 'meaning_en' in col_idx else '',
                'hsk_level': cell_texts[col_idx['hsk_level']] if col_idx.get('hsk_level', -1) < len(cell_texts) and 'hsk_level' in col_idx else '',
            }
            words.append(entry)

    return words


def scrape_theme_page(title, url):
    try:
        resp = requests.get(url, headers=HEADERS, timeout=20)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, 'html.parser')
        words = parse_vocab_table(soup)
        return words
    except Exception as e:
        print(f"  [WARNING] Gagal mengambil '{title}': {e}")
        return []


def main():
    pages = get_all_page_links()
    if not pages:
        print("[ERROR] Tidak ada halaman ditemukan. Cek koneksi internet atau struktur situs berubah.")
        sys.exit(1)

    result = {}
    total = len(pages)

    for i, (title, url) in enumerate(pages):
        slug = slugify(title)
        print(f"[{i+1}/{total}] Mengambil '{title}' -> tema '{slug}' ...")

        words = scrape_theme_page(title, url)

        if words:
            # Jika slug sudah ada (duplikat tema dari judul mirip), gabungkan
            if slug in result:
                existing_hanzi = {w['hanzi'] for w in result[slug]['words']}
                new_words = [w for w in words if w['hanzi'] not in existing_hanzi]
                result[slug]['words'].extend(new_words)
            else:
                result[slug] = {
                    'label_en': title,
                    'source_url': url,
                    'words': words,
                    'attribution': 'AllSet Learning Vocabulary Wiki (CC BY-NC), '
                                    'https://resources.allsetlearning.com/',
                }
            print(f"    -> {len(words)} kata ditemukan.")
        else:
            print(f"    -> tidak ada tabel kosakata, dilewati.")

        time.sleep(REQUEST_DELAY_SEC)

        # Simpan progres tiap 20 halaman supaya tidak hilang jika terputus di tengah
        if (i + 1) % 20 == 0:
            with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            print(f"    [progres disimpan sementara ke {OUTPUT_FILE}]")

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    total_words = sum(len(t['words']) for t in result.values())
    print()
    print(f"[SELESAI] {OUTPUT_FILE} berhasil dibuat.")
    print(f"          Tema berhasil di-scrape : {len(result)}")
    print(f"          Total entri kata        : {total_words}")
    print()
    print("[LANGKAH SELANJUTNYA]")
    print("  File ini berisi kata MENTAH hasil scrape, BELUM dicocokkan dengan")
    print("  app_words.json. Upload file 'themes_external_raw.json' ini ke percakapan")
    print("  Claude untuk dibuatkan script pencocokan (merge_themes.py) yang akan:")
    print("    - mencocokkan tiap kata dengan entry app_words.json (by simplified)")
    print("    - kata yang TIDAK ditemukan akan dilaporkan terpisah (opsional ditambah manual)")
    print("    - hasil akhir digabung ke index_theme.json dengan tema baru")


if __name__ == '__main__':
    main()

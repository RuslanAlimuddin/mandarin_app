# -*- coding: utf-8 -*-
"""
build_theme_entries.py
Bangun entri app_words.json baru untuk 15 tema kecil, dari unmatched_theme_words.json
(sumber AllSet Learning, CC BY-NC) + Make Me a Hanzi (radikal/goresan/struktur) +
cidict_index.json (traditional/pinyin_numeric cross-check) + bopomofo hasil konversi.
"""
import json
import re

# ── 1. Load semua sumber ──────────────────────────────────────
unmatched = json.load(open('unmatched_theme_words.json', encoding='utf-8'))
cidict    = json.load(open('cidict_index.json', encoding='utf-8'))
app_words = json.load(open('app_words.json', encoding='utf-8'))

by_s_cidict = {}
for w in cidict:
    by_s_cidict.setdefault(w['simplified'], w)  # ambil yang pertama saja

by_id_app = {w.get('id') or w.get('simplified'): w for w in app_words}

mmh_dict = {}
with open('makemeahanzi_dict.txt', encoding='utf-8') as f:
    for line in f:
        d = json.loads(line)
        mmh_dict[d['character']] = d

mmh_strokes = {}
with open('makemeahanzi_graphics.txt', encoding='utf-8') as f:
    for line in f:
        d = json.loads(line)
        mmh_strokes[d['character']] = len(d.get('strokes', []))

STRUCT_MAP = {
    '⿰': 'left-right', '⿱': 'top-bottom', '⿲': 'left-middle-right',
    '⿳': 'top-middle-bottom', '⿴': 'enclosed-full', '⿵': 'enclosed-top',
    '⿶': 'enclosed-bottom', '⿷': 'enclosed-left', '⿸': 'enclosed-topleft',
    '⿹': 'enclosed-topright', '⿺': 'enclosed-botleft', '⿻': 'overlaid',
}

# ── 2. Pinyin diacritic -> numeric (mekanis, bukan tebakan) ──
TONE_MARKS = {
    'ā':('a',1),'á':('a',2),'ǎ':('a',3),'à':('a',4),
    'ē':('e',1),'é':('e',2),'ě':('e',3),'è':('e',4),
    'ī':('i',1),'í':('i',2),'ǐ':('i',3),'ì':('i',4),
    'ō':('o',1),'ó':('o',2),'ǒ':('o',3),'ò':('o',4),
    'ū':('u',1),'ú':('u',2),'ǔ':('u',3),'ù':('u',4),
    'ǖ':('v',1),'ǘ':('v',2),'ǚ':('v',3),'ǜ':('v',4),
    'ü':('v',0),'ń':('n',2),'ň':('n',3),'ǹ':('n',4),
}

def syllable_to_numeric(syl):
    tone = 5  # netral kalau tidak ada tanda nada
    out = []
    for ch in syl:
        low = ch.lower()
        if low in TONE_MARKS:
            base, t = TONE_MARKS[low]
            if t != 0:
                tone = t
            out.append(base.upper() if ch.isupper() else base)
        else:
            out.append(ch)
    return ''.join(out) + (str(tone) if any(c.isalpha() for c in syl) else '')

def pinyin_to_numeric(pinyin_diacritic):
    # pisah per suku kata berdasar spasi/apostrof, biarkan tanda baca lain apa adanya
    tokens = re.split(r'(\s+)', pinyin_diacritic.strip())
    return ''.join(syllable_to_numeric(t) if t.strip() else t for t in tokens)

# ── 3. Pinyin numeric -> Bopomofo (tabel standar, mekanis) ───
INITIALS = ['zh','ch','sh','b','p','m','f','d','t','n','l','g','k','h','j','q','x','r','z','c','s']
# CATATAN: 'y' dan 'w' SENGAJA tidak dimasukkan -- keduanya bukan inisial zhuyin
# sungguhan, cuma konvensi ejaan pinyin untuk suku kata tanpa inisial (yu=ü,
# ya=ia, wu=u, wa=ua, dst). Kalau dimasukkan ke sini, cabang "if not initial"
# di bawah (yang sudah benar menanganinya) tidak akan pernah kepakai.
INITIAL_MAP = {
    'b':'ㄅ','p':'ㄆ','m':'ㄇ','f':'ㄈ','d':'ㄉ','t':'ㄊ','n':'ㄋ','l':'ㄌ',
    'g':'ㄍ','k':'ㄎ','h':'ㄏ','j':'ㄐ','q':'ㄑ','x':'ㄒ',
    'zh':'ㄓ','ch':'ㄔ','sh':'ㄕ','r':'ㄖ','z':'ㄗ','c':'ㄘ','s':'ㄙ',
}
FINAL_MAP = {
    'a':'ㄚ','o':'ㄛ','e':'ㄜ','ê':'ㄝ','ai':'ㄞ','ei':'ㄟ','ao':'ㄠ','ou':'ㄡ',
    'an':'ㄢ','en':'ㄣ','ang':'ㄤ','eng':'ㄥ','er':'ㄦ',
    'i':'ㄧ','ia':'ㄧㄚ','ie':'ㄧㄝ','iao':'ㄧㄠ','iu':'ㄧㄡ','iou':'ㄧㄡ',
    'ian':'ㄧㄢ','in':'ㄧㄣ','iang':'ㄧㄤ','ing':'ㄧㄥ','iong':'ㄩㄥ',
    'u':'ㄨ','ua':'ㄨㄚ','uo':'ㄨㄛ','uai':'ㄨㄞ','ui':'ㄨㄟ','uei':'ㄨㄟ',
    'uan':'ㄨㄢ','un':'ㄨㄣ','uen':'ㄨㄣ','uang':'ㄨㄤ','ueng':'ㄨㄥ',
    'v':'ㄩ','ve':'ㄩㄝ','van':'ㄩㄢ','vn':'ㄩㄣ',
    'ong':'ㄨㄥ',
}
TONE_CHAR = {1:'', 2:'ˊ', 3:'ˇ', 4:'ˋ', 5:'˙'}

# suku kata "berdiri sendiri" (zh/ch/sh/r/z/c/s + i) -> tanpa simbol vokal ㄧ
BUZZ_INITIALS = {'zh','ch','sh','r','z','c','s'}

def syllable_numeric_to_bopomofo(syl):
    m = re.match(r'^([a-zA-Z]+)([1-5]?)$', syl)
    if not m:
        return syl  # bukan suku kata biasa (angka, huruf asing, dsb) -> biarkan apa adanya
    body, tone = m.group(1).lower(), m.group(2)
    tone = int(tone) if tone else 5

    # kasus khusus: 'r' berdiri sendiri = akhiran erhua 儿 (mis. 馅儿 -> xiàn + r),
    # BUKAN konsonan "r" seperti di 人 (rén). Harus dicek SEBELUM pencocokan
    # inisial umum, karena kalau tidak, 'r' akan tertangkap sbg inisial dgn
    # final kosong -> salah jadi 'ㄖ' polos, padahal seharusnya 'ㄦ'.
    if body == 'r':
        return 'ㄦ' + TONE_CHAR.get(tone, '')

    initial = ''
    for cand in sorted(INITIALS, key=len, reverse=True):
        if body.startswith(cand):
            initial = cand
            break
    final = body[len(initial):]

    # kasus khusus: -i setelah zh/ch/sh/r/z/c/s adalah "buzzing vowel", tidak ditulis
    if initial in BUZZ_INITIALS and final == 'i':
        final = ''

    # yi/wu/yu/yin/ying/ya/wa/dst berdiri sendiri tanpa inisial -> final ditulis sbg suku penuh
    if not initial:
        if body == 'yi':
            final = 'i'
        elif body == 'yin':
            final = 'in'
        elif body == 'ying':
            final = 'ing'
        elif body == 'wu':
            final = 'u'
        elif body == 'yu':
            final = 'v'
        elif body.startswith('yu'):
            final = 'v' + body[2:]
        elif body.startswith('y'):
            final = 'i' + body[1:]
        elif body.startswith('w'):
            final = 'u' + body[1:]
        else:
            final = body

    # kasus khusus: 'u' setelah j/q/x SELALU sebenarnya ü (dieja tanpa titik
    # krn j/q/x tidak pernah digabung dgn bunyi 'u' asli, jadi tidak ambigu)
    if initial in ('j', 'q', 'x'):
        JQX_U_TO_V = {'u': 'v', 'ue': 've', 'uan': 'van', 'un': 'vn'}
        final = JQX_U_TO_V.get(final, final)

    bopomofo_initial = INITIAL_MAP.get(initial, '')
    bopomofo_final = FINAL_MAP.get(final, final if final else '')
    tone_mark = TONE_CHAR.get(tone, '')
    return bopomofo_initial + bopomofo_final + tone_mark

def pinyin_to_bopomofo(pinyin_diacritic):
    numeric = pinyin_to_numeric(pinyin_diacritic)
    tokens = numeric.split(' ')
    return ' '.join(syllable_numeric_to_bopomofo(t) for t in tokens if t)


# ── 4. Radikal/goresan/struktur/komponen per kata (multi-karakter) ──
def char_info(ch):
    d = mmh_dict.get(ch, {})
    decomp = d.get('decomposition', '')
    structure = STRUCT_MAP.get(decomp[0]) if decomp and decomp[0] in STRUCT_MAP else 'single'
    # komponen: ambil karakter di decomposition selain simbol IDC & '？'
    components = [c for c in decomp if c not in STRUCT_MAP and c != '？'] if decomp else []
    return {
        'radical': d.get('radical', ch),
        'stroke_count': mmh_strokes.get(ch, 0),
        'structure': structure,
        'components': components,
    }

def word_derived_fields(hanzi):
    infos = [char_info(c) for c in hanzi]
    radical = infos[0]['radical'] if infos else ''
    stroke_count = sum(i['stroke_count'] for i in infos)
    structure = infos[0]['structure'] if infos else 'single'
    components = []
    for i in infos:
        components.extend(i['components'])
    return radical, stroke_count, structure, components


# ── 5. Terjemahan Indonesia manual (dari meaning_en AllSet) ──
# Disusun manual satu-satu, bukan mesin -- supaya akurat & natural.
TRANSLATIONS = {
 '淘宝':'Taobao (aplikasi belanja online)', '京东':'JD.com (aplikasi belanja online)',
 '美团':'Meituan (aplikasi layanan hidup sehari-hari)', '盒马':'Freshippo/Hema (aplikasi belanja bahan segar)',
 '滴滴':'Didi (aplikasi ojek/taksi online)', '支付宝':'Alipay (aplikasi pembayaran digital)',
 '饿了么':'Eleme (aplikasi pesan-antar makanan)', '小红书':'Xiaohongshu/Little Red Book (aplikasi media sosial)',
 '共享单车':'sepeda sewa/berbagi', '大众点评':'Dianping (aplikasi ulasan restoran & diskon)',
 '抖音':'Douyin/TikTok versi Tiongkok',
 '上海':'Shanghai', '深圳':'Shenzhen', '三亚':'Sanya', '天津':'Tianjin', '青岛':'Qingdao',
 '大连':'Dalian', '杭州':'Hangzhou', '苏州':'Suzhou', '成都':'Chengdu', '广州':'Guangzhou',
 '阳朔':'Yangshuo', '武汉':'Wuhan', '南京':'Nanjing', '哈尔滨':'Harbin', '厦门':'Xiamen',
 '圣诞老人':'Sinterklas/Santa Claus', '圣诞树':'pohon Natal', '圣诞歌':'lagu Natal',
 '圣诞卡':'kartu Natal', '圣诞晚餐':'makan malam Natal', '圣诞帽':'topi Sinterklas',
 '圣诞袜':'kaus kaki Natal', '圣诞市场':'pasar Natal', '雪花':'kepingan salju',
 '驯鹿':'rusa kutub/rusa kereta Sinterklas', '雪橇':'kereta luncur salju', '铃铛':'lonceng kecil',
 '平安夜':'Malam Natal', '热红酒':'anggur panas rempah (mulled wine)',
 '欧元':'euro', '港币':'dolar Hong Kong', '台币':'dolar Taiwan Baru', '日元':'yen Jepang',
 '韩元':'won Korea', '卢布':'rubel (mata uang Rusia)', '克朗':'krona/krone (mata uang Skandinavia)',
 '卢比':'rupee (mata uang India)', '里拉':'lira (mata uang lama Italia)', '泰铢':'baht Thailand',
 '澳大利亚元':'dolar Australia', '俄罗斯卢布':'rubel Rusia', '加拿大元':'dolar Kanada',
 '纸币':'uang kertas', '巴西雷亚尔':'real Brasil', '南非兰特':'rand Afrika Selatan',
 '瑞士法郎':'franc Swiss', '沙特里亚尔':'riyal Arab Saudi', '新加坡元':'dolar Singapura',
 '新西兰元':'dolar Selandia Baru', '印度卢比':'rupee India', '越南盾':'dong Vietnam',
 '汉堡':'hamburger', '热狗':'hot dog', '炸鸡':'ayam goreng', '披萨':'piza', '沙拉':'salad',
 '肉串':'sate/tusukan daging', '意面':'pasta', '烤鸡':'ayam panggang', '炸鱼薯条':'ikan & kentang goreng',
 '墨西哥卷':'taco', '炒饭':'nasi goreng', '炒面':'mi goreng', '煎饺':'pangsit goreng', '咖喱':'kari',
 '猪肉':'daging babi', '牛肉':'daging sapi', '鸡肉':'daging ayam', '鱼肉':'daging ikan',
 '熟肉':'daging matang', '狗肉':'daging anjing', '生肉':'daging mentah', '瘦肉':'daging tanpa lemak',
 '肥肉':'daging berlemak', '鸭肉':'daging bebek', '兔肉':'daging kelinci', '火鸡肉':'daging kalkun',
 '驴肉':'daging keledai', '冻肉':'daging beku', '红肉':'daging merah', '白肉':'daging putih',
 '卤肉':'daging semur/kuah rempah', '咸肉':'daging asin', '腊肉':'daging asap khas Tiongkok',
 '一次':'satu kali', '极少':'sangat jarang/sangat sedikit', '不常':'tidak sering',
 '尤克里里':'ukulele', '笛':'suling', '长号':'trombon', '口琴':'harmonika', '手风琴':'akordeon',
 '萨克斯':'saksofon', '琵琶':'pipa (alat musik petik Tionghoa)', '二胡':'erhu (rebab dua senar Tionghoa)',
 '唢呐':'suona (alat musik tiup Tionghoa)', '古筝':'guzheng (kecapi Tionghoa)',
 '冰球':'hoki es', '冬泳':'berenang musim dingin', '铲雪':'menyekop salju',
 '打雪仗':'perang bola salju', '堆雪人':'membuat manusia salju', '滑雪橇':'meluncur kereta salju',
 '冰钓':'memancing di es', '泡温泉':'berendam air panas (onsen)',
 '女性教育':'pendidikan perempuan', '女性独立':'kemandirian perempuan',
 '社会进步':'kemajuan sosial', '女性权利':'hak-hak perempuan', '性别平等':'kesetaraan gender',
 '女性地位':'status perempuan', '女性贡献':'kontribusi perempuan', '杰出女性':'perempuan luar biasa/berprestasi',
 '女性领导者':'pemimpin perempuan', '女性历史':'sejarah perempuan', '平权运动':'gerakan kesetaraan hak',
 '女权':'feminisme/hak-hak perempuan',
 '酒杯':'gelas anggur/minuman keras', '喝醉':'mabuk', '宿醉':'sakit kepala setelah mabuk (hangover)',
 '香槟':'sampanye', '白兰地':'brendi', '威士忌':'wiski', '伏特加':'vodka', '马提尼':'martini',
 '鸡尾酒':'koktail',
 '美式':'gaya Amerika (kopi Americano)', '拿铁':'kopi latte', '黑咖啡':'kopi hitam',
 '白咖啡':'kopi susu putih', '中杯':'ukuran sedang', '大杯':'ukuran besar',
 '少冰':'sedikit es', '去冰':'tanpa es', '低因':'rendah kafein', '燕麦':'oat/gandum',
 '馥芮白':'flat white', '卡布奇诺':'kapucino', '焦糖玛奇果':'karamel machiato', '摩卡':'moka',
 '冷萃':'kopi seduh dingin (cold brew)',
 '犹太人':'orang Yahudi', '土豆饼':'kue kentang (latke)', '金币巧克力':'cokelat koin (gelt)',
 '家庭聚会':'kumpul keluarga', '点燃蜡烛':'menyalakan lilin', '光明节':'Hanukkah',
 '犹太节日':'hari raya Yahudi', '希伯来文':'bahasa Ibrani', '烛台':'tempat lilin',
 '八臂烛台':'menorah Hanukkah (8 lengan)', '油灯':'lampu minyak', '旋转陀螺':'gasing (dreidel)',
 '圣殿':'kuil suci', '宗教仪式':'upacara keagamaan', '玛卡比':'Makabe (tokoh sejarah Yahudi)',
 '印度教':'agama Hindu', '东正教':'Kristen Ortodoks', '犹太教':'agama Yahudi',
 '晒伤':'kulit terbakar matahari', '咬伤':'gigitan (luka)', '扭伤':'keseleo', '割伤':'luka sayat',
 '烧伤':'luka bakar', '擦伤':'lecet', '瘀伤':'memar', '蜇伤':'sengatan (luka)',
}

for k, v in TRANSLATIONS.items():
    if not v:
        print('!! terjemahan kosong:', k)

print(f'Total terjemahan disiapkan: {len(TRANSLATIONS)}')

# ── 6. Override pinyin manual (24 kata dgn karakter multi-bacaan yang
#      rekonstruksi otomatisnya salah -- app_words.json & cidict_index.json
#      SAMA-SAMA salah pilih bacaan langka utk karakter ini kalau berdiri
#      sendiri, mis. 广 auto jadi 'yǎn' padahal harusnya 'guǎng'. Diperbaiki
#      manual satu-satu berdasar pengetahuan Mandarin, bukan lookup lagi) ──
PINYIN_OVERRIDE = {
    '饿了么': 'è le me',
    '共享单车': 'gòng xiǎng dān chē',
    '广州': 'Guǎng zhōu',
    '圣诞老人': 'Shèng dàn lǎo rén',
    '圣诞树': 'Shèng dàn shù',
    '圣诞歌': 'Shèng dàn gē',
    '圣诞卡': 'Shèng dàn kǎ',
    '圣诞晚餐': 'Shèng dàn wǎn cān',
    '圣诞帽': 'Shèng dàn mào',
    '圣诞袜': 'Shèng dàn wà',
    '圣诞市场': 'Shèng dàn shì chǎng',
    '铃铛': 'líng dang',
    '腊肉': 'là ròu',
    '女性地位': 'nǚ xìng dì wèi',
    '白兰地': 'bái lán dì',
    '马提尼': 'mǎ tí ní',
    '黑咖啡': 'hēi kā fēi',
    '白咖啡': 'bái kā fēi',
    '卡布奇诺': 'kǎ bù qí nuò',
    '焦糖玛奇果': 'jiāo táng mǎ qí guǒ',
    '摩卡': 'mó kǎ',
    '希伯来文': 'Xī bó lái wén',
    '旋转陀螺': 'xuán zhuǎn tuó luó',
    '圣殿': 'shèng diàn',
}

# ── 7. Bangun pinyin per-karakter (utk 154 kata yg auto-rekonstruksi cocok) ──
def get_char_pinyin(c):
    if c in char_pinyin_lookup:
        return char_pinyin_lookup[c]
    mp = mmh_dict.get(c, {}).get('pinyin', [])
    return mp[0] if mp else c

char_pinyin_lookup = {}
for w in cidict:
    if len(w['simplified']) == 1 and w['simplified'] not in char_pinyin_lookup:
        char_pinyin_lookup[w['simplified']] = w['pinyin']

KEYS_MAP = {
 'chinese_apps': 'ext_chinese_apps', 'china_cities': 'ext_china_cities', 'christmas': 'ext_christmas',
 'currency': 'ext_currency', 'names_of_the_currency': 'ext_currency', 'fast_food': 'ext_fast_food',
 'meat': 'ext_meat', 'frequency_of_occurrence': 'ext_frequency_of_occurrence',
 'musical_instrument': 'ext_musical_instrument', 'winter_activities': 'ext_winter_activities',
 'women_s_history_month': 'ext_women_s_history_month', 'alcohol': 'ext_alcohol', 'coffee': 'ext_coffee',
 'hanukkah': 'ext_hanukkah', 'religion': 'ext_religion', 'injure': 'ext_injure',
}
THEME_LABELS = {
 'ext_chinese_apps': 'Aplikasi Mandarin', 'ext_china_cities': 'Kota-kota di Tiongkok',
 'ext_christmas': 'Natal', 'ext_currency': 'Mata Uang', 'ext_fast_food': 'Makanan Cepat Saji',
 'ext_meat': 'Daging', 'ext_frequency_of_occurrence': 'Frekuensi Kejadian',
 'ext_musical_instrument': 'Alat Musik', 'ext_winter_activities': 'Aktivitas Musim Dingin',
 'ext_women_s_history_month': "Bulan Sejarah Wanita", 'ext_alcohol': 'Minuman Keras & Alkohol',
 'ext_coffee': 'Kopi', 'ext_hanukkah': 'Hanukkah', 'ext_religion': 'Agama & Kepercayaan',
 'ext_injure': 'Cedera & Luka',
}

# kumpulkan per-kata (dedupe -- kata sama bisa muncul di >1 sub-list AllSet)
word_themes = {}  # hanzi -> set(theme_key)
word_meta   = {}  # hanzi -> {pinyin(AllSet asli), meaning_en}
for src_key, theme_key in KEYS_MAP.items():
    for it in unmatched.get(src_key, []):
        h = it['hanzi']
        word_themes.setdefault(h, set()).add(theme_key)
        if h not in word_meta:
            word_meta[h] = it

print(f'\nTotal kata unik final: {len(word_themes)}')

new_entries = []
skipped_no_translation = []
for hanzi, it in word_meta.items():
    if hanzi in PINYIN_OVERRIDE:
        pinyin = PINYIN_OVERRIDE[hanzi]
    else:
        pinyin = ' '.join(get_char_pinyin(c) for c in hanzi)

    meaning_id = TRANSLATIONS.get(hanzi)
    if not meaning_id:
        skipped_no_translation.append(hanzi)
        continue

    cidict_hit = by_s_cidict.get(hanzi)
    traditional = cidict_hit['traditional'] if cidict_hit else hanzi  # fallback: asumsikan sama (ditandai di log)
    pinyin_numeric = pinyin_to_numeric(pinyin)
    bopomofo = pinyin_to_bopomofo(pinyin)
    radical, stroke_count, structure, components = word_derived_fields(hanzi)

    entry = {
        'id': hanzi,
        'simplified': hanzi,
        'traditional': traditional,
        'pinyin': pinyin,
        'pinyin_numeric': pinyin_numeric,
        'bopomofo': bopomofo,
        'hsk': None,
        'hsk2': None,
        'frequency': None,
        'pos': ['n'],
        'pos_id': ['kata benda'],
        'meanings_id': [meaning_id],
        'meanings_en': [it.get('meaning_en', '')],
        'radical': radical,
        'radical_number': None,
        'stroke_count': stroke_count,
        'structure': structure,
        'components': components,
        'char_type': 'compound' if len(hanzi) > 1 else 'simple',
        'themes': sorted(word_themes[hanzi]),
        'synonyms': [],
        'antonyms': [],
        '_source_note': 'AllSet Learning Vocabulary Wiki (CC BY-NC), https://resources.allsetlearning.com/ -- traditional diasumsikan sama dgn simplified' + ('' if cidict_hit else ' (TIDAK divalidasi cidict)'),
    }
    new_entries.append(entry)

print(f'Entri berhasil dibangun: {len(new_entries)}')
print(f'Dilewati (tidak ada terjemahan): {skipped_no_translation}')

# ── 8. Gabung ke app_words.json ──
app_words.extend(new_entries)
json.dump(app_words, open('app_words.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(f'\napp_words.json diperbarui: {len(app_words)} entri total (+{len(new_entries)})')

# ── 9. Update index_theme.json ──
index_theme = json.load(open('index_theme.json', encoding='utf-8'))
theme_additions = {}
for entry in new_entries:
    for theme_key in entry['themes']:
        theme_additions.setdefault(theme_key, []).append(entry['simplified'])

for theme_key, words_to_add in theme_additions.items():
    if theme_key not in index_theme:
        index_theme[theme_key] = {
            'label_id': THEME_LABELS.get(theme_key, theme_key),
            'label_zh': '', 'words': [], 'count': 0,
        }
    existing = set(index_theme[theme_key]['words'])
    for w in words_to_add:
        if w not in existing:
            index_theme[theme_key]['words'].append(w)
            existing.add(w)
    index_theme[theme_key]['count'] = len(index_theme[theme_key]['words'])

json.dump(index_theme, open('index_theme.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

print('\n--- Ringkasan jumlah kartu tiap tema kecil SEKARANG ---')
for theme_key in sorted(set(KEYS_MAP.values())):
    print(f"  {THEME_LABELS.get(theme_key, theme_key):30s} {index_theme[theme_key]['count']} kartu")


#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
terapkan_koreksi_bacaan.py -- memperbaiki bacaan (pinyin, pinyin angka, zhuyin) dan arti kata berbacaan ganda
yang salah di data aplikasi, sesuai Daftar Tinjau Koreksi Bacaan yang sudah Anda setujui.

Yang diubah:
  A. 118 kata yang pasti salah        -> bacaan + zhuyin + arti (Indonesia dan Inggris) diperbaiki
  B. 22 kata dua-bacaan               -> bacaan lazim di depan; bacaan lainnya jadi keterangan "[bacaan] arti"
  C. 5 kata bacaan benar, arti salah  -> hanya urutan arti diperbaiki (arti jarang dipakai dipindah ke belakang)
  D. tulisan "u:" di kolom pinyin     -> menjadi ü
  E. zhuyin yang tidak cocok dengan pinyin angka -> dibuat ulang dari pinyin angka
  Berkas turunan yang ikut dikoreksi: tone_drills, wb_pools, nuance_pairs, graded_readers, produktif_karakter.
  Berkas utama: app_words.json. Format berkas (indentasi, akhir baris) dipertahankan persis.

Cara pakai (jalankan dari folder C:\\mandarin_app):
  python terapkan_koreksi_bacaan.py            -> hanya MELIHAT (tidak mengubah apa pun)
  python terapkan_koreksi_bacaan.py --apply    -> menerapkan (cadangan tiap berkas dibuat otomatis)

Cadangan: data\\<berkas>.json.bak_bacaan_<tanggal-jam>. Untuk membatalkan, salin kembali tiap cadangan ke nama aslinya.
Skrip menolak menulis bila ada bacaan lama yang tersisa di berkas turunan atau pemeriksaan akhir gagal.
"""
import re


# Keputusan peninjauan Claude: kata -> bacaan (angka nada, v = ü, 5 = netral) yang benar menurut standar HSK
FIX = {
 '个':'ge4','打':'da3','几':'ji3','哦':'o4','听':'ting1','东西':'dong1 xi5','啦':'la5','地方':'di4 fang5','场':'chang3',
 '正':'zheng4','结果':'jie2 guo3','转':'zhuan3','多少':'duo1 shao5','跑':'pao3','万':'wan4','片':'pian4','嘛':'ma5',
 '故事':'gu4 shi5','令':'ling4','约':'yue1','底':'di3','离':'li2','提':'ti2','弄':'nong4','读':'du2','节':'jie2',
 '追':'zhui1','喂':'wei4','重点':'zhong4 dian3','合':'he2','解':'jie3','觉':'jue2','骑':'qi2','泡':'pao4',
 '说法':'shuo1 fa5','页':'ye4','足':'zu2','弹':'tan2','好处':'hao3 chu5','刺':'ci4','便宜':'pian2 yi5','档':'dang4',
 '趟':'tang4','折':'zhe2','踏':'ta4','恶':'e4','当天':'dang4 tian1','当晚':'dang4 wan3','当日':'dang4 ri4','尺':'chi3',
 '汗':'han4','熬':'ao2','挣':'zheng4','抹':'mo3','脏':'zang1','看好':'kan4 hao3','幢':'zhuang4','炮':'pao4','番':'fan1',
 '鲜':'xian1','拽':'zhuai4','拾':'shi2','仇':'chou2','大方':'da4 fang5','琢磨':'zuo2 mo5','转动':'zhuan4 dong4',
 '大爷':'da4 ye5','结实':'jie1 shi5','工夫':'gong1 fu5','攒':'zan3','分量':'fen4 liang5','空地':'kong4 di4','撇':'pie3',
 '哑':'ya3','下调':'xia4 tiao2','好学':'hao4 xue2','吧':'ba5','吗':'ma5','告诉':'gao4 su5','称':'cheng1','妻子':'qi1 zi5',
 '累':'lei4','人家':'ren2 jia5','吓':'xia4','生意':'sheng1 yi5','厂':'chang3','角':'jiao3','胖':'pang4','答':'da2',
 '斗':'dou4','广':'guang3','狮子':'shi1 zi5','教学':'jiao4 xue2','浅':'qian3','本事':'ben3 shi5','虾':'xia1',
 '孙子':'sun1 zi5','地道':'di4 dao5','大夫':'dai4 fu5','哄':'hong3','谜':'mi2','粥':'zhou1','咳':'ke2','涌':'yong3',
 '扛':'kang2','大都':'da4 dou1','管子':'guan3 zi5','所长':'suo3 zhang3','上头':'shang4 tou5','倒车':'dao4 che1',
 '卷子':'juan4 zi5','匹':'pi3','打雪仗':'da3 xue3 zhang4','泡温泉':'pao4 wen1 quan2','燕麦':'yan4 mai4',
 '光明节':'guang1 ming2 jie2','东正教':'dong1 zheng4 jiao4','长号':'chang2 hao4',
}
# Perlu keputusan (dua bacaan sama-sama dipakai; standar HSK tidak tegas atau saya tidak yakin)
DECIDE = {
 '啊':('a5','a1 (seruan) dan a (partikel) sama-sama dipakai'),
 '处':('chu4','chǔ (berada/menangani) dan chù (tempat) sama-sama HSK'),
 '待':('dai4','dāi (tinggal) dan dài (menunggu; memperlakukan)'),
 '背':('bei4','bēi (memikul) dan bèi (punggung)'),
 '量':('liang4','liáng (mengukur) dan liàng (jumlah)'),
 '炸':('zha4','zhá (menggoreng) dan zhà (meledak)'),
 '钻':('zuan1','zuān (mengebor, kata kerja) dan zuàn (bor, kata benda)'),
 '扇':('shan4','shān (mengipasi) dan shàn (kipas; penggolong)'),
 '差':('cha4','chā (selisih) dan chà (kurang; buruk, dipakai di HSK 1)'),
 '薄':('bao2','bó (formal) dan báo (tipis, percakapan)'),
 '晃':('huang4','huǎng (berkilat) dan huàng (bergoyang)'),
 '大意':('da4 yi5','dàyì (garis besar) dan dàyi (ceroboh)'),
 '翘':('qiao4','qiáo dan qiào sama-sama dipakai'),
 '呛':('qiang4','qiāng (tersedak) dan qiàng (menyengat)'),
 '把手':('ba3 shou5','bǎshǒu (berjabat tangan) dan bǎshou (pegangan)'),
 '豁':('huo4','huō (membelah) dan huò (terbuka; jelas)'),
 '照应':('zhao4 ying5','zhàoyìng (berkorelasi) dan zhàoying (merawat)'),
 '裁缝':('cai2 feng5','cáiféng (menjahit) dan cáifeng (penjahit)'),
 '买卖':('mai3 mai5','mǎimài dan mǎimai (transaksi; toko)'),
 '闷':('men4','mēn (pengap) dan mèn (bosan)'),
 '为':('wei4','wéi (sebagai) dan wèi (untuk)'),
 '呵':('he1','hē (menghembus) dan ā (seruan); bukan kata HSK'),
}


TONE_MARKS={'a':'āáǎà','e':'ēéěè','i':'īíǐì','o':'ōóǒò','u':'ūúǔù','ü':'ǖǘǚǜ'}
def syl_marked(s):
    s=s.replace('v','ü')
    m=re.fullmatch(r'([a-zü]+)([1-5])',s)
    if not m: return s
    body,t=m.group(1),int(m.group(2))
    if t==5: return body
    idx=None
    for v in 'ae':
        if v in body: idx=body.index(v); break
    if idx is None:
        if 'ou' in body: idx=body.index('o')
        else:
            vs=[i for i,c in enumerate(body) if c in 'aeiouü']
            idx=vs[-1] if vs else 0
    c=body[idx]; return body[:idx]+TONE_MARKS[c][t-1]+body[idx+1:]
def marked(num): return ' '.join(syl_marked(x) for x in num.split())
INIT=['zh','ch','sh','b','p','m','f','d','t','n','l','g','k','h','j','q','x','r','z','c','s']
INITZY={'b':'ㄅ','p':'ㄆ','m':'ㄇ','f':'ㄈ','d':'ㄉ','t':'ㄊ','n':'ㄋ','l':'ㄌ','g':'ㄍ','k':'ㄎ','h':'ㄏ','j':'ㄐ','q':'ㄑ','x':'ㄒ','zh':'ㄓ','ch':'ㄔ','sh':'ㄕ','r':'ㄖ','z':'ㄗ','c':'ㄘ','s':'ㄙ'}
FIN={'a':'ㄚ','o':'ㄛ','e':'ㄜ','ê':'ㄝ','ai':'ㄞ','ei':'ㄟ','ao':'ㄠ','ou':'ㄡ','an':'ㄢ','en':'ㄣ','ang':'ㄤ','eng':'ㄥ','er':'ㄦ',
 'i':'ㄧ','ia':'ㄧㄚ','ie':'ㄧㄝ','iao':'ㄧㄠ','iu':'ㄧㄡ','ian':'ㄧㄢ','in':'ㄧㄣ','iang':'ㄧㄤ','ing':'ㄧㄥ','iong':'ㄩㄥ',
 'u':'ㄨ','ua':'ㄨㄚ','uo':'ㄨㄛ','uai':'ㄨㄞ','ui':'ㄨㄟ','uan':'ㄨㄢ','un':'ㄨㄣ','uang':'ㄨㄤ','ong':'ㄨㄥ',
 'ü':'ㄩ','üe':'ㄩㄝ','üan':'ㄩㄢ','ün':'ㄩㄣ'}
ZEROINIT={'yi':'ㄧ','ya':'ㄧㄚ','ye':'ㄧㄝ','yao':'ㄧㄠ','you':'ㄧㄡ','yan':'ㄧㄢ','yin':'ㄧㄣ','yang':'ㄧㄤ','ying':'ㄧㄥ','wu':'ㄨ','wa':'ㄨㄚ','wo':'ㄨㄛ','wai':'ㄨㄞ','wei':'ㄨㄟ','wan':'ㄨㄢ','wen':'ㄨㄣ','wang':'ㄨㄤ','weng':'ㄨㄥ','yu':'ㄩ','yue':'ㄩㄝ','yuan':'ㄩㄢ','yun':'ㄩㄣ','yong':'ㄩㄥ'}
TZY={1:'',2:'ˊ',3:'ˇ',4:'ˋ',5:'˙'}
def syl_zy(s):
    m=re.fullmatch(r'([a-zü]+)([1-5])',s.replace('v','ü'))
    if not m: return s
    body,t=m.group(1),int(m.group(2))
    if body in ZEROINIT: return ZEROINIT[body]+TZY[t]
    ini=''
    for i in INIT:
        if body.startswith(i): ini=i; break
    fin=body[len(ini):]
    if ini in ('zh','ch','sh','r','z','c','s') and fin=='i': return INITZY[ini]+TZY[t]
    if ini in ('j','q','x') and fin.startswith('u'): fin='ü'+fin[1:]
    if fin=='iou': fin='iu'
    if fin=='uei': fin='ui'
    if fin=='uen': fin='un'
    return (INITZY.get(ini,'')+FIN.get(fin,'?'))+TZY[t]
def zhuyin(num): return ' '.join(syl_zy(x) for x in num.split())


# Arti Inggris untuk bacaan baru (ditulis Claude, glos kamus baku). Format: kata -> (arti bacaan utama, [arti bacaan lain dengan tanda])
EN = {
 '个':(['classifier for people or objects in general','individual'],[]),
 '打':(['to hit; to strike; to beat','to play (a game)','to make (a phone call)'],[]),
 '几':(['how many','several; a few'],[]),
 '哦':(['oh (interjection indicating understanding)'],[]),
 '听':(['to listen to; to hear','to heed; to obey'],[]),
 '东西':(['thing; stuff; object','(derog.) creature'],[]),
 '啦':(['particle combining 了 and 啊 (exclamation or statement)'],[]),
 '地方':(['place; location','room (for sth)'],[]),
 '场':(['place; venue; field','classifier for events (spell, episode, bout)'],[]),
 '正':(['straight; upright','correct; main','just; precisely'],[]),
 '结果':(['result; outcome','in the end; finally'],[]),
 '转':(['to turn; to change direction','to transfer; to forward'],[]),
 '多少':(['how many; how much','number; amount'],[]),
 '跑':(['to run','to flee; to leak'],[]),
 '万':(['ten thousand'],[]),
 '片':(['slice; flake; thin piece','classifier for flat, thin things'],[]),
 '嘛':(['particle expressing obviousness or persuasion'],[]),
 '故事':(['story; tale; narrative'],[]),
 '令':(['to order; to command','to cause; to make'],[]),
 '约':(['to make an appointment','about; approximately','to restrict'],[]),
 '底':(['bottom; base','background','end (of a period)'],[]),
 '离':(['to leave; to part from','to be away from (in distance or time)'],[]),
 '提':(['to carry (hanging down from the hand)','to lift; to raise','to bring up; to mention'],[]),
 '弄':(['to do; to make; to get','to handle; to play with'],[]),
 '读':(['to read; to study','to pronounce'],[]),
 '节':(['festival; holiday','joint; section; segment','classifier for segments (class, battery)'],[]),
 '追':(['to chase; to pursue','to trace; to investigate','to court'],[]),
 '喂':(['hello; hey','to feed'],[]),
 '重点':(['key point; emphasis','focus'],[]),
 '合':(['to close; to shut','to combine; to join','to suit'],[]),
 '解':(['to divide; to separate','to untie; to solve','to understand'],[]),
 '觉':(['to feel; to find that','to be aware of'],[]),
 '骑':(['to ride (a horse, bicycle)','to sit astride'],[]),
 '泡':(['to soak; to steep','bubble; foam'],[]),
 '说法':(['way of saying; statement','version; theory'],[]),
 '页':(['page','leaf (of paper)'],[]),
 '足':(['foot; leg','sufficient; ample','fully; as much as'],[]),
 '弹':(['to pluck; to play (a string instrument)','to bounce; to spring','elastic'],[]),
 '好处':(['benefit; advantage','merit'],[]),
 '刺':(['thorn; splinter','to prick; to stab','to irritate'],[]),
 '便宜':(['cheap; inexpensive','small advantages','to let sb off lightly'],[]),
 '档':(['file; archive; shelf','grade; level','gear (of a vehicle)'],[]),
 '趟':(['classifier for trips; round trip','time (for a visit)'],[]),
 '折':(['to fold','to break; to snap','discount'],[]),
 '踏':(['to step on; to tread','to trample'],[]),
 '恶':(['evil; vicious','fierce'],[]),
 '当天':(['on that day; the same day'],[]),
 '当晚':(['on that evening; the same evening'],[]),
 '当日':(['on that day; the same day'],[]),
 '尺':(['Chinese foot (1/3 meter)','ruler'],[]),
 '汗':(['sweat; perspiration'],[]),
 '熬':(['to simmer; to cook slowly','to endure; to hold out'],[]),
 '挣':(['to earn (money)','to struggle free'],[]),
 '抹':(['to smear; to apply','to wipe','to erase'],[]),
 '脏':(['dirty; filthy'],[]),
 '看好':(['to regard as promising','to keep an eye on'],[]),
 '幢':(['classifier for buildings'],[]),
 '炮':(['cannon; gun','firecracker'],[]),
 '番':(['foreign (non-Chinese)','classifier for occurrences or kinds','to take turns'],[]),
 '鲜':(['fresh','delicious; tasty','bright'],[]),
 '拽':(['to pull; to drag; to tug'],[]),
 '拾':(['to pick up; to collect'],[]),
 '仇':(['hatred; enmity','revenge'],[]),
 '大方':(['generous; magnanimous','natural and relaxed','tasteful'],[]),
 '琢磨':(['to ponder; to think over'],[]),
 '转动':(['to turn; to rotate; to revolve'],[]),
 '大爷':(['uncle (respectful address for an older man)','master'],[]),
 '结实':(['sturdy; solid','strong; robust'],[]),
 '工夫':(['time; free time','skill (kung fu)'],[]),
 '攒':(['to save; to accumulate','to collect'],[]),
 '分量':(['weight','significance; importance'],[]),
 '空地':(['vacant land; clearing'],[]),
 '撇':(['to throw; to cast','to skim off','left-falling stroke (丿)'],[]),
 '哑':(['mute; dumb','hoarse'],[]),
 '下调':(['to adjust downward; to lower (prices etc.)'],[]),
 '好学':(['eager to learn; studious'],[]),
 '吧':(['particle for suggestions or requests','particle for assumptions'],[]),
 '吗':(['question particle for yes/no questions'],[]),
 '告诉':(['to tell; to inform'],[]),
 '称':(['to call; to name','to say','to weigh','to praise'],[]),
 '妻子':(['wife'],[]),
 '累':(['tired; weary','to strain; to tire out'],[]),
 '人家':(['other people','he/she/they','I; me (playful or coy)'],[]),
 '吓':(['to frighten; to scare'],[]),
 '生意':(['business; trade','deal'],[]),
 '厂':(['factory; plant; works'],[]),
 '角':(['angle; corner','horn','unit of money (0.1 yuan)'],[]),
 '胖':(['fat; plump'],[]),
 '答':(['to answer; to reply'],[]),
 '斗':(['to fight; to struggle','to contend with'],[]),
 '广':(['wide; extensive','to spread'],[]),
 '狮子':(['lion'],[]),
 '教学':(['teaching; instruction'],[]),
 '浅':(['shallow','simple; easy','light (color)'],[]),
 '本事':(['ability; skill'],[]),
 '虾':(['shrimp; prawn'],[]),
 '孙子':(["grandson (son's son)"],[]),
 '地道':(['authentic; genuine','thorough'],[]),
 '大夫':(['doctor; physician'],[]),
 '哄':(['to coax; to humor','to deceive'],[]),
 '谜':(['riddle; mystery'],[]),
 '粥':(['porridge; congee'],[]),
 '咳':(['to cough'],[]),
 '涌':(['to gush; to surge','to emerge'],[]),
 '扛':(['to carry on the shoulder','to bear (responsibility)'],[]),
 '大都':(['for the most part; mostly'],[]),
 '管子':(['tube; pipe'],[]),
 '所长':(['head of an institute or office'],[]),
 '上头':(['top; above; on top','superior; authority'],[]),
 '倒车':(['to reverse (a vehicle)'],[]),
 '卷子':(['test paper; exam paper'],[]),
 '匹':(['classifier for horses, mules (and bolts of cloth)'],[]),
 '打雪仗':(['to have a snowball fight'],[]),
 '泡温泉':(['to soak in a hot spring'],[]),
 '燕麦':(['oats'],[]),
 '光明节':(['Hanukkah (Festival of Lights)'],[]),
 '东正教':(['Eastern Orthodox Church'],[]),
 '长号':(['trombone'],[]),
 # B: bacaan utama + bacaan lain
 '啊':(['particle that softens statements, questions or exclamations'],['[ā] interjection of surprise or admiration']),
 '处':(['place; location','department; office'],['[chǔ] to reside; to handle; to be in a position']),
 '待':(['to treat; to wait for'],['[dāi] to stay; to remain']),
 '背':(['back (of the body)','to turn away from'],['[bēi] to carry on the back; to bear (a burden)']),
 '量':(['quantity; amount','capacity'],['[liáng] to measure']),
 '炸':(['to explode; to blow up'],['[zhá] to deep-fry']),
 '钻':(['to drill; to bore','to get into'],['[zuàn] a drill; diamond']),
 '扇':(['fan','classifier for doors and windows'],['[shān] to fan; to flap']),
 '差':(['to be lacking; to fall short','poor; bad'],['[chā] difference; discrepancy']),
 '薄':(['thin; flimsy','light (not rich)'],['[bó] thin; meager; to despise']),
 '晃':(['to shake; to sway'],['[huǎng] to dazzle; to flash']),
 '大意':(['careless; negligent'],['[dàyì] general idea; gist']),
 '翘':(['to stick up','to lift'],['[qiáo] to raise; to lift (the head)']),
 '呛':(['to irritate (nose or throat)','pungent'],['[qiāng] to choke']),
 '把手':(['handle; knob'],['[bǎshǒu] to shake hands; to hold hands']),
 '豁':(['open; clear','generous'],['[huō] to split; to sacrifice']),
 '照应':(['to take care of; to look after'],['[zhàoyìng] to correlate; to coordinate']),
 '裁缝':(['tailor; dressmaker'],['[cáiféng] to cut and sew']),
 '买卖':(['business; deal','shop'],['[mǎimài] to buy and sell']),
 '闷':(['bored; depressed','sealed; unclear'],['[mēn] stuffy; to cover tightly']),
 '为':(['for; for the sake of','because of'],['[wéi] to act as; to be; to do']),
 '呵':(['to exhale; to breathe out','to scold'],[]),
 # C: bacaan benar, arti diperbaiki
 '蹲':(['to crouch; to squat','to stay (somewhere)'],['[cún] (dialect) to sprain (the leg)']),
 '当':(['to be; to act as','to manage; to be in charge of','ought to; should','when; at the time of','to withstand'],[]),
 '若':(['if; supposing','like; as','to seem'],[]),
 '格':(['square; grid; frame','rule; standard','style; pattern','(grammar) case'],[]),
 '疏散':(['to scatter; to disperse','to evacuate','scattered; sparse'],[]),
}


# ───────────────────────── logika utama ─────────────────────────
import collections
import glob
import gzip
import io
import json
import os
import shutil
import sys
import time
import unicodedata

TS = time.strftime('%Y%m%d_%H%M%S')
FILES = ['app_words', 'tone_drills', 'wb_pools', 'nuance_pairs', 'graded_readers', 'produktif_karakter']
ARTI = {'蹲': 'dun1', '当': 'dang1', '若': 'ruo4', '格': 'ge2', '疏散': 'shu1 san4'}


def fail(msg):
    print('GAGAL: ' + msg)
    sys.exit(1)


def n_(p):
    p = (p or '').lower().replace('u:', 'v').replace('ü', 'v')
    return re.sub(r'\s+', ' ', p.strip())


def base_(p):
    return re.sub(r'5\b', '', p)


def fl(s):
    return re.sub(r"[\s'’·]", '', unicodedata.normalize('NFC', (s or '').lower().replace('u:', 'ü')))


def strip_tone(p):
    p = unicodedata.normalize('NFD', (p or '').lower())
    p = ''.join(c for c in p if unicodedata.category(c) != 'Mn' or c == '\u0308')
    return re.sub(r'\s+', ' ', unicodedata.normalize('NFC', p).replace('u:', 'ü').strip())


def style_like(old, new):
    if ' ' not in (old or '').strip():
        new = new.replace(' ', '')
    return new


def primary_meaning(word):
    """sama dengan primary_meaning di generate_tone_drills.py / generate_wordbuilder_pools.py:
    lewati catatan "varian dari ..." dan buang awalan "(bentuk terikat)"."""
    meanings = word.get('meanings_id') or []
    if isinstance(meanings, str):
        meanings = [meanings]
    if not meanings:
        return ''
    for m in meanings:
        low = m.lower()
        if not (low.startswith('varian dari') or low.startswith('varian lama dari')):
            prefix = '(bentuk terikat)'
            return m[len(prefix):].strip() if low.startswith(prefix) else m
    return meanings[0]


def as_hsk_int(val):
    if val is None or isinstance(val, bool):
        return None
    if isinstance(val, int):
        return val
    if isinstance(val, float):
        return int(val)
    if isinstance(val, str):
        digits = ''.join(ch for ch in val if ch.isdigit())
        return int(digits) if digits else None
    return None


def load(name):
    path = os.path.join('data', name + '.json')
    with io.open(path, encoding='utf-8', newline='') as f:
        raw = f.read()
    nl = '\r\n' if '\r\n' in raw else '\n'
    obj = json.loads(raw.replace('\r\n', '\n'))
    return obj, nl, raw


def dump(obj, nl):
    s = json.dumps(obj, ensure_ascii=False, indent=2, separators=(',', ': '))
    return s.replace('\n', nl) if nl != '\n' else s


DEMOTE = re.compile(r'^(digunakan dalam|\(tiruan bunyi\)|ding dong|\(dialek\)|lihat |Taiwan dibaca|marga |varian dari|KP:|kata kerja transitif ringan)')
PROMOTE_ID = {'地方': 'tempat'}   # arti yang harus berada paling depan


def reorder_meanings(e, target_num, cd_by_word):
    """arti Indonesia bacaan target dipindah ke depan (arti yang hanya dipakai dalam kata tertentu ke belakangnya);
    arti bacaan lain diberi tanda [bacaan]. Mengembalikan (berubah, catatan)."""
    ids = list(e.get('meanings_id') or [])
    if not ids:
        return False, 'tidak ada arti'
    rd = collections.defaultdict(set)
    for ce in cd_by_word.get(e['simplified'], []):
        r = base_(n_(ce.get('pinyin_numeric')))
        for m in ce.get('meanings_id') or []:
            rd[m].add(r)
    target = base_(n_(target_num))
    prim, oth = [], []
    for i, m in enumerate(ids):
        (prim if target in rd.get(m, set()) else oth).append(i)
    if not prim:
        if len(ids) == 1:
            return False, ''          # satu arti saja dan tidak bertentangan: dibiarkan
        return False, 'arti bacaan target tidak ditemukan'
    prim = [i for i in prim if not DEMOTE.match(ids[i])] + [i for i in prim if DEMOTE.match(ids[i])]
    want = PROMOTE_ID.get(e['simplified'])
    if want and want in [ids[i] for i in prim]:
        j = [ids[i] for i in prim].index(want)
        prim.insert(0, prim.pop(j))

    def tag(i):
        rs = sorted(rd.get(ids[i], set()))
        return '[' + ' / '.join(marked(r) for r in rs[:2]) + '] ' if rs else ''
    new_ids = [ids[i] for i in prim] + [tag(i) + ids[i] for i in oth]
    changed = (new_ids != ids)
    e['meanings_id'] = new_ids
    return changed, ''


def main():
    apply = '--apply' in sys.argv
    print('Mode: ' + ('TERAPKAN (--apply)' if apply else 'LIHAT-DULU (tidak mengubah apa pun)'))
    for nm in FILES + ['cidict_index']:
        p = os.path.join('data', nm + ('.json.gz' if nm == 'cidict_index' else '.json'))
        if not os.path.isfile(p):
            fail('berkas tidak ditemukan: %s (jalankan dari folder C:\\mandarin_app)' % p)
    with gzip.open(os.path.join('data', 'cidict_index.json.gz'), 'rt', encoding='utf-8') as f:
        cdl = json.load(f)
    cd = collections.defaultdict(list)
    for e in cdl:
        cd[e['simplified']].append(e)

    loaded = {nm: load(nm) for nm in FILES}
    words = loaded['app_words'][0]
    W = {}
    for w in words:
        if w['simplified'] in W:
            fail('kata ganda di app_words.json: ' + w['simplified'])
        W[w['simplified']] = w

    ORIG_FIRST = {k: ((W[k].get('meanings_id') or [''])[0]) for k in W}
    # daftar koreksi: A (pasti), B (usulan saya), C (arti saja)
    spec = []
    for k, num in FIX.items():
        spec.append((k, num, 'A'))
    for k, (num, _why) in DECIDE.items():
        spec.append((k, num, 'B'))
    for k, num in ARTI.items():
        spec.append((k, num, 'C'))
    missing = [k for k, _, _ in spec if k not in W]
    if missing:
        fail('kata tidak ada di app_words.json: %s' % missing)

    # ── 1. app_words.json ──
    NEW = {}          # kata -> info untuk berkas turunan
    manual = []
    notes = []
    cnt = collections.Counter()
    samples = []
    for k, num, grp in spec:
        e = W[k]
        old_py, old_num = e['pinyin'], e.get('pinyin_numeric') or ''
        old_first = (e.get('meanings_id') or [''])[0]
        old_reading_same = base_(n_(old_num)) == base_(n_(num))
        if grp != 'C' and old_reading_same:
            # bacaan sudah benar; hanya pastikan urutan arti
            pass
        new_py, new_zy = marked(num), zhuyin(num)
        chg_m, note = reorder_meanings(e, num, cd)
        en_new = EN[k][0] + EN[k][1]
        if (e.get('meanings_en') or []) != en_new:
            e['meanings_en'] = en_new
            chg_m = True
            cnt['arti Inggris diganti'] += 1
        if note and 'target tidak ditemukan' in note:
            manual.append((k, grp, num))
        elif note:
            notes.append((k, note))
        reading_changed = not old_reading_same
        if reading_changed:
            e['pinyin'], e['pinyin_numeric'], e['bopomofo'] = new_py, num, new_zy
            cnt['bacaan diganti ' + grp] += 1
        if chg_m:
            cnt['arti diurutkan ' + grp] += 1
        if reading_changed or chg_m:
            if len(samples) < 12 and grp == 'A':
                samples.append((k, old_py, new_py, old_first[:34], (e['meanings_id'] or [''])[0][:34]))
        if reading_changed:
            NEW[k] = {'old_fl': fl(old_py), 'old_py': old_py, 'new_py': new_py, 'num': num,
                      'old_first': old_first, 'new_first': (e.get('meanings_id') or [''])[0],
                      'new_pm': primary_meaning(e)}
    # tulisan "u:" pada pinyin
    for w in words:
        if 'u:' in (w.get('pinyin') or ''):
            w['pinyin'] = w['pinyin'].replace('u:', 'ü')
            cnt['tulisan u: -> ü'] += 1
    # zhuyin tidak cocok dengan pinyin angka
    for w in words:
        num = (w.get('pinyin_numeric') or '').strip()
        if not num or 'r5' in num or ':' in num or not re.fullmatch(r'[a-zü0-9 ]+', num.replace('v', 'ü')):
            continue
        zy = zhuyin(num)
        if '?' in zy:
            continue
        if zy.replace(' ', '') != (w.get('bopomofo') or '').replace(' ', ''):
            w['bopomofo'] = zy
            cnt['zhuyin dibuat ulang'] += 1

    print('\n── app_words.json ──')
    for k in sorted(cnt):
        print('  %-28s %4d' % (k, cnt[k]))
    for s in samples:
        print('    contoh: %s  %s -> %s | arti: "%s" -> "%s"' % s)
    if manual:
        print('  PERLU DIISI MANUAL (arti bacaan baru tidak ada di CC-CEDICT): ' + ', '.join('%s(%s)' % (k, g) for k, g, _ in manual))
    for k, nt in notes:
        print('  catatan %s: %s' % (k, nt))

    # ── 2. berkas turunan ──
    # INFO: semua kata yang dikoreksi (bacaan dan/atau urutan arti); NEW: yang bacaannya berganti
    INFO = {}
    for k, num, grp in spec:
        e = W[k]
        INFO[k] = dict(NEW.get(k) or {})
        INFO[k].update({'new_py': e['pinyin'], 'num': e['pinyin_numeric'], 'new_first': (e.get('meanings_id') or [''])[0],
                        'new_pm': primary_meaning(e), 'changed_reading': k in NEW})
        if k not in NEW:
            INFO[k]['old_first'] = ORIG_FIRST[k]
            INFO[k]['old_fl'] = None

    def match(hz, py):
        i = NEW.get(hz)
        return i if i and fl(py) == i['old_fl'] else None

    stats = collections.defaultdict(collections.Counter)
    order = {w['simplified']: n for n, w in enumerate(words)}

    # tone_drills: dibentuk ulang dari app_words yang sudah benar (seperti generate_tone_drills.py)
    td = loaded['tone_drills'][0]

    def qualifies_single(e):
        py = e.get('pinyin') or ''
        if len(e['simplified']) != 1 or as_hsk_int(e.get('hsk')) not in (1, 2, 3, 4, 5, 6, 7):
            return None
        marks = {'ā': 1, 'ē': 1, 'ī': 1, 'ō': 1, 'ū': 1, 'ǖ': 1, 'á': 2, 'é': 2, 'í': 2, 'ó': 2, 'ú': 2, 'ǘ': 2,
                 'ǎ': 3, 'ě': 3, 'ǐ': 3, 'ǒ': 3, 'ǔ': 3, 'ǚ': 3, 'à': 4, 'è': 4, 'ì': 4, 'ò': 4, 'ù': 4, 'ǜ': 4}
        for ch in py:
            if ch in marks:
                return marks[ch]
        return None
    singles_new = []
    seen = set()
    for s_ in td['singles']:
        k = s_['cn']
        if k in INFO:
            e = W[k]
            t = qualifies_single(e)
            if t is None:
                stats['tone_drills']['singles dihapus (kini nada netral)'] += 1
                continue
            s_.update({'py': e['pinyin'], 'id': primary_meaning(e), 'hsk': as_hsk_int(e.get('hsk')), 'tone': t,
                       'base': strip_tone(e['pinyin'])})
            stats['tone_drills']['singles diubah'] += 1
        seen.add(k)
        singles_new.append(s_)
    for k in INFO:
        e = W[k]
        t = qualifies_single(e)
        if k not in seen and t is not None:
            ent = {'cn': k, 'py': e['pinyin'], 'id': primary_meaning(e), 'hsk': as_hsk_int(e.get('hsk')),
                   'tone': t, 'base': strip_tone(e['pinyin'])}
            pos = next((j for j, s2 in enumerate(singles_new) if order.get(s2['cn'], 10 ** 9) > order[k]), len(singles_new))
            singles_new.insert(pos, ent)
            stats['tone_drills']['singles ditambah (kini bernada jelas)'] += 1
    td['singles'] = singles_new

    groups = td['groups']
    removed = 0
    for key in list(groups.keys()):
        keep = [it for it in groups[key] if it['cn'] not in INFO]
        removed += len(groups[key]) - len(keep)
        if len(keep) >= 2:
            groups[key] = keep
        else:
            if keep:
                stats['tone_drills']['grup dibubarkan (sisa 1 anggota)'] += 1
            del groups[key]
    homo = collections.defaultdict(list)
    for w in words:
        if as_hsk_int(w.get('hsk')) not in (1, 2, 3, 4, 5, 6, 7):
            continue
        homo[strip_tone(w['pinyin'])].append(w)
    seen_cn = collections.defaultdict(set)
    for k in INFO:
        e = W[k]
        if as_hsk_int(e.get('hsk')) not in (1, 2, 3, 4, 5, 6, 7) or not e.get('pinyin'):
            continue
        key = strip_tone(e['pinyin'])
        item = {'cn': k, 'py': e['pinyin'], 'id': primary_meaning(e), 'hsk': as_hsk_int(e.get('hsk'))}
        if key in groups:
            if not any(x['cn'] == k for x in groups[key]):
                groups[key].append(item)
            stats['tone_drills']['item masuk grup yang ada'] += 1
        elif len({w['simplified'] for w in homo.get(key, [])}) >= 2:
            grp, seen_k = [], set()
            for w in homo[key]:
                if w['simplified'] in seen_k:
                    continue
                seen_k.add(w['simplified'])
                grp.append({'cn': w['simplified'], 'py': w['pinyin'], 'id': primary_meaning(w), 'hsk': as_hsk_int(w.get('hsk'))})
            groups[key] = grp
            stats['tone_drills']['grup baru dibuat'] += 1
        else:
            stats['tone_drills']['item tanpa pasangan (tidak masuk grup mana pun)'] += 1
    for key in groups:
        groups[key].sort(key=lambda x: order.get(x['cn'], 10 ** 9))

    # wb_pools: item kata yang dikoreksi disamakan dengan app_words (seperti generate_wordbuilder_pools.py)
    def walk(o, fn):
        if isinstance(o, dict):
            fn(o)
            for v in o.values():
                walk(v, fn)
        elif isinstance(o, list):
            for v in o:
                walk(v, fn)

    def fn_wb(d):
        if isinstance(d.get('cn'), str) and isinstance(d.get('py'), str) and d['cn'] in INFO:
            e = W[d['cn']]
            d['py'] = e['pinyin']
            if 'id' in d:
                d['id'] = primary_meaning(e)
            stats['wb_pools']['item disamakan dengan app_words'] += 1
    walk(loaded['wb_pools'][0], fn_wb)

    # graded_readers: pinyin glosarium (jika cocok bacaan lama) dan arti (jika masih arti lama)
    def fn_gr(d):
        if isinstance(d.get('cn'), str) and isinstance(d.get('py'), str) and d['cn'] in INFO:
            i = INFO[d['cn']]
            if d['cn'] in NEW and fl(d['py']) == NEW[d['cn']]['old_fl']:
                d['py'] = style_like(d['py'], i['new_py'])
                stats['graded_readers']['pinyin diubah'] += 1
            if 'id' in d and d['id'] == i['old_first'] and i['old_first'] != i['new_first']:
                d['id'] = i['new_first']
                stats['graded_readers']['arti diubah'] += 1
    walk(loaded['graded_readers'][0], fn_gr)

    def fn_nuance(d):
        if isinstance(d.get('word'), str) and isinstance(d.get('pinyin'), str):
            i = match(d['word'], d['pinyin'])
            if i:
                d['pinyin'] = style_like(d['pinyin'], i['new_py'])
                stats['nuance_pairs']['pinyin diubah'] += 1
    walk(loaded['nuance_pairs'][0], fn_nuance)

    # produktif_karakter
    pk = loaded['produktif_karakter'][0]
    for root, v in pk.items():
        if root in INFO:
            i = INFO[root]
            if root in NEW and fl(v.get('pinyin')) == NEW[root]['old_fl']:
                v['pinyin'] = style_like(v['pinyin'], i['new_py'])
                stats['produktif_karakter']['akar: pinyin diubah'] += 1
            if v.get('arti') == i['old_first'] and i['old_first'] != i['new_first']:
                v['arti'] = i['new_first']
                stats['produktif_karakter']['akar: arti diubah'] += 1
        for d in v.get('kata_turunan', []):
            k = d.get('kata')
            if k in INFO:
                i = INFO[k]
                if k in NEW and fl(d.get('pinyin')) == NEW[k]['old_fl']:
                    d['pinyin'] = style_like(d['pinyin'], i['new_py'])
                    stats['produktif_karakter']['kata turunan: pinyin diubah'] += 1
                if d.get('arti') == i['old_first'] and i['old_first'] != i['new_first']:
                    d['arti'] = i['new_first']
                    stats['produktif_karakter']['kata turunan: arti diubah'] += 1

    print('\n── berkas turunan ──')
    for fname in FILES[1:]:
        s = stats.get(fname, {})
        print('  %-20s %s' % (fname + '.json', ', '.join('%s: %d' % (k, v) for k, v in s.items()) or 'tidak ada perubahan'))

    # ── 3. periksa sisa bacaan lama di berkas turunan ──
    left = collections.Counter()

    def scan_left(fname):
        def fn(d):
            for hk, pk_ in (('cn', 'py'), ('word', 'pinyin'), ('kata', 'pinyin')):
                if isinstance(d.get(hk), str) and isinstance(d.get(pk_), str) and match(d[hk], d[pk_]):
                    left[fname] += 1
        walk(loaded[fname][0], fn)
    for fname in FILES[1:]:
        scan_left(fname)
    for root, v in pk.items():
        if match(root, v.get('pinyin')):
            left['produktif_karakter'] += 1
    print('  sisa bacaan lama setelah koreksi: %s' % (dict(left) or '0'))
    if left:
        fail('masih ada bacaan lama di berkas turunan; tidak ada yang ditulis')

    total_nw = len(NEW)
    print('\nRingkasan: %d kata diganti bacaannya di app_words.json.' % total_nw)
    if not apply:
        print('\nBelum ada yang diubah. Jika sudah sesuai, jalankan:  python terapkan_koreksi_bacaan.py --apply')
        return

    # ── 4. tulis (dengan cadangan dan pemeriksaan) ──
    for nm in FILES:
        obj, nl, raw = loaded[nm]
        new_raw = dump(obj, nl)
        if new_raw == raw:
            print('--  %s.json: tidak berubah' % nm)
            continue
        path = os.path.join('data', nm + '.json')
        bak = path + '.bak_bacaan_' + TS
        shutil.copy2(path, bak)
        with io.open(path, 'w', encoding='utf-8', newline='') as f:
            f.write(new_raw)
        with io.open(path, encoding='utf-8', newline='') as f:
            chk = f.read()
        try:
            ok = (chk == new_raw) and json.loads(chk.replace('\r\n', '\n')) == obj
        except ValueError:
            ok = False
        if not ok:
            shutil.copy2(bak, path)
            fail('%s: pemeriksaan akhir gagal; dikembalikan dari cadangan' % path)
        print('OK  %s.json ditulis (cadangan: %s)' % (nm, os.path.basename(bak)))
    print('SELESAI. Muat ulang aplikasi dengan Ctrl+F5.')


if __name__ == '__main__':
    main()

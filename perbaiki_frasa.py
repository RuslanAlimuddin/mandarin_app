#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
perbaiki_frasa.py -- memperbaiki pinyin angka dan zhuyin 44 frasa sesuai Daftar Tinjau Frasa yang sudah disetujui.

Yang diubah (hanya data\\app_words.json, dan 4 baris pinyin di data\\produktif_karakter.json):
  - 23 frasa wisata: pinyin angka dan zhuyin dibuat ulang dari pinyin yang tampil
  - 21 frasa lain: pinyin angka dibuat ulang; zhuyin diperbaiki pada 真的, 纽扣儿, 城里
  - 这时候 dan 见过: pinyin tampil ikut diubah menjadi "zhè shíhou" dan "jiànguo" (nada netral)
Skrip menolak bekerja bila nilai lama di data tidak sama dengan yang tercatat di daftar (artinya data sudah berubah).

Cara pakai (jalankan dari folder C:\\mandarin_app):
  python perbaiki_frasa.py            -> hanya MELIHAT (tidak mengubah apa pun)
  python perbaiki_frasa.py --apply    -> menerapkan (cadangan dibuat otomatis)

Cadangan: data\\<berkas>.json.bak_frasa_<tanggal-jam>. Untuk membatalkan, salin kembali ke nama aslinya. Aman dijalankan ulang.
"""
import io
import json
import os
import re
import shutil
import sys
import time
import unicodedata

TS = time.strftime('%Y%m%d_%H%M%S')
# (kata, kelompok, pinyin_lama, pinyin_baru, angka_lama, angka_baru, zhuyin_lama, zhuyin_baru)
TABEL = [
    ('真的', 'C', 'zhēn de', 'zhēn de', 'zhen1 de', 'zhen1 de5', 'ㄓㄣ de', 'ㄓㄣ ㄉㄜ˙'),
    ('能不能', 'B', 'néng bùnéng', 'néng bùnéng', 'neng2 bùnéng', 'neng2 bu4 neng2', 'ㄋㄥˊ ㄅㄨˋ ㄋㄥˊ', 'ㄋㄥˊ ㄅㄨˋ ㄋㄥˊ'),
    ('眼里', 'B', 'yǎnli', 'yǎnli', 'yǎnli', 'yan3 li5', 'ㄧㄢˇ ㄌㄧ˙', 'ㄧㄢˇ ㄌㄧ˙'),
    ('这时候', 'B', 'zhè shíhòu', 'zhè shíhou', 'zhe4 shíhòu', 'zhe4 shi2 hou5', 'ㄓㄜˋ ㄕˊ ㄏㄡ˙', 'ㄓㄜˋ ㄕˊ ㄏㄡ˙'),
    ('城里', 'B', 'chénglǐ', 'chénglǐ', 'chénglǐ', 'cheng2 li3', 'ㄔㄥˊ ㄌㄧ˙', 'ㄔㄥˊ ㄌㄧˇ'),
    ('致力于', 'B', 'zhìlìyú', 'zhìlìyú', 'zhìlìyú', 'zhi4 li4 yu2', 'ㄓˋ ㄌㄧˋ ㄩˊ', 'ㄓˋ ㄌㄧˋ ㄩˊ'),
    ('怀着', 'B', 'huáizhe', 'huáizhe', 'huáizhe', 'huai2 zhe5', 'ㄏㄨㄞˊ ㄓㄜ˙', 'ㄏㄨㄞˊ ㄓㄜ˙'),
    ('不如说', 'B', 'bùrú shuō', 'bùrú shuō', 'bùrú shuo1', 'bu4 ru2 shuo1', 'ㄅㄨˋ ㄖㄨˊ ㄕㄨㄛ', 'ㄅㄨˋ ㄖㄨˊ ㄕㄨㄛ'),
    ('很难说', 'B', 'hěn nánshuō', 'hěn nánshuō', 'hen3 nánshuō', 'hen3 nan2 shuo1', 'ㄏㄣˇ ㄋㄢˊ ㄕㄨㄛ', 'ㄏㄣˇ ㄋㄢˊ ㄕㄨㄛ'),
    ('趁着', 'B', 'chènzhe', 'chènzhe', 'chènzhe', 'chen4 zhe5', 'ㄔㄣˋ ㄓㄜ˙', 'ㄔㄣˋ ㄓㄜ˙'),
    ('不予', 'B', 'bùyǔ', 'bùyǔ', 'bùyǔ', 'bu4 yu3', 'ㄅㄨˋ ㄩˇ', 'ㄅㄨˋ ㄩˇ'),
    ('公益性', 'B', 'gōngyì xìng', 'gōngyì xìng', 'gōngyì xing4', 'gong1 yi4 xing4', 'ㄍㄨㄥ ㄧˋ ㄒㄧㄥˋ', 'ㄍㄨㄥ ㄧˋ ㄒㄧㄥˋ'),
    ('大笔', 'B', 'dàbǐ', 'dàbǐ', 'dàbǐ', 'da4 bi3', 'ㄉㄚˋ ㄅㄧˇ', 'ㄉㄚˋ ㄅㄧˇ'),
    ('电动车', 'B', 'diàndòngchē', 'diàndòngchē', 'diàndòngchē', 'dian4 dong4 che1', 'ㄉㄧㄢˋ ㄉㄨㄥˋ ㄔㄜ', 'ㄉㄧㄢˋ ㄉㄨㄥˋ ㄔㄜ'),
    ('不利于', 'B', 'bù lìyú', 'bù lìyú', 'bu4 lìyú', 'bu4 li4 yu2', 'ㄅㄨˋ ㄌㄧˋ ㄩˊ', 'ㄅㄨˋ ㄌㄧˋ ㄩˊ'),
    ('指着', 'B', 'zhǐzhe', 'zhǐzhe', 'zhǐzhe', 'zhi3 zhe5', 'ㄓˇ ㄓㄜ˙', 'ㄓˇ ㄓㄜ˙'),
    ('着眼于', 'B', 'zhuóyǎn yú', 'zhuóyǎn yú', 'zhuóyǎn yu2', 'zhuo2 yan3 yu2', 'ㄓㄨㄛˊ ㄧㄢˇ ㄩˊ', 'ㄓㄨㄛˊ ㄧㄢˇ ㄩˊ'),
    ('纽扣儿', 'C', 'niǔ kòu er', 'niǔ kòu er', 'niu3 kou4 er', 'niu3 kou4 er5', 'ㄋㄧㄡˇ ㄎㄡˋ er', 'ㄋㄧㄡˇ ㄎㄡˋ ㄦ˙'),
    ('见过', 'B', 'jiànguò', 'jiànguo', 'jiànguò', 'jian4 guo5', 'ㄐㄧㄢˋ ㄍㄨㄛ˙', 'ㄐㄧㄢˋ ㄍㄨㄛ˙'),
    ('说起来', 'B', 'shuō qǐlái', 'shuō qǐlái', 'shuo1 qǐlái', 'shuo1 qi3 lai2', 'ㄕㄨㄛ ㄑㄧˇ ㄌㄞˊ', 'ㄕㄨㄛ ㄑㄧˇ ㄌㄞˊ'),
    ('难以想象', 'B', 'nányǐxiǎngxiàng', 'nányǐxiǎngxiàng', 'nányǐxiǎngxiàng', 'nan2 yi3 xiang3 xiang4', 'ㄋㄢˊ ㄧˇ ㄒㄧㄤˇ ㄒㄧㄤˋ', 'ㄋㄢˊ ㄧˇ ㄒㄧㄤˇ ㄒㄧㄤˋ'),
    ('免税店', 'A', 'miǎnshuìdiàn', 'miǎnshuìdiàn', 'mianshuidian4', 'mian3 shui4 dian4', 'ㄇianshuidianˋ', 'ㄇㄧㄢˇ ㄕㄨㄟˋ ㄉㄧㄢˋ'),
    ('候机室', 'A', 'hòujīshì', 'hòujīshì', 'houjishi4', 'hou4 ji1 shi4', 'ㄏoujishiˋ', 'ㄏㄡˋ ㄐㄧ ㄕˋ'),
    ('青年旅社', 'A', 'qīngnián lǚshè', 'qīngnián lǚshè', 'qingnian2 lvshe4', 'qing1 nian2 lv3 she4', 'ㄑingnianˊ ㄌvsheˋ', 'ㄑㄧㄥ ㄋㄧㄢˊ ㄌㄩˇ ㄕㄜˋ'),
    ('风景区', 'A', 'fēngjǐngqū', 'fēngjǐngqū', 'fengjingqu1', 'feng1 jing3 qu1', 'ㄈengjingqu', 'ㄈㄥ ㄐㄧㄥˇ ㄑㄩ'),
    ('古镇', 'A', 'gǔzhèn', 'gǔzhèn', 'guzhen4', 'gu3 zhen4', 'ㄍuzhenˋ', 'ㄍㄨˇ ㄓㄣˋ'),
    ('团费', 'A', 'tuánfèi', 'tuánfèi', 'tuanfei4', 'tuan2 fei4', 'ㄊuanfeiˋ', 'ㄊㄨㄢˊ ㄈㄟˋ'),
    ('学生票', 'A', 'xuéshēngpiào', 'xuéshēngpiào', 'xueshengpiao4', 'xue2 sheng1 piao4', 'ㄒueshengpiaoˋ', 'ㄒㄩㄝˊ ㄕㄥ ㄆㄧㄠˋ'),
    ('老人票', 'A', 'lǎorénpiào', 'lǎorénpiào', 'laorenpiao4', 'lao3 ren2 piao4', 'ㄌaorenpiaoˋ', 'ㄌㄠˇ ㄖㄣˊ ㄆㄧㄠˋ'),
    ('免费入场', 'A', 'miǎnfèi rùchǎng', 'miǎnfèi rùchǎng', 'mianfei4 ruchang3', 'mian3 fei4 ru4 chang3', 'ㄇianfeiˋ ㄖuchangˇ', 'ㄇㄧㄢˇ ㄈㄟˋ ㄖㄨˋ ㄔㄤˇ'),
    ('开放时间', 'A', 'kāifàng shíjiān', 'kāifàng shíjiān', 'kaifang4 shijian1', 'kai1 fang4 shi2 jian1', 'ㄎaifangˋ ㄕijian', 'ㄎㄞ ㄈㄤˋ ㄕˊ ㄐㄧㄢ'),
    ('闭馆时间', 'A', 'bìguǎn shíjiān', 'bìguǎn shíjiān', 'biguan3 shijian1', 'bi4 guan3 shi2 jian1', 'ㄅiguanˇ ㄕijian', 'ㄅㄧˋ ㄍㄨㄢˇ ㄕˊ ㄐㄧㄢ'),
    ('游客中心', 'A', 'yóukè zhōngxīn', 'yóukè zhōngxīn', 'youke4 zhongxin1', 'you2 ke4 zhong1 xin1', 'ioukeˋ ㄓongxin', 'ㄧㄡˊ ㄎㄜˋ ㄓㄨㄥ ㄒㄧㄣ'),
    ('语音导览', 'A', 'yǔyīn dǎolǎn', 'yǔyīn dǎolǎn', 'yuyin1 daolan3', 'yu3 yin1 dao3 lan3', 'vyin ㄉaolanˇ', 'ㄩˇ ㄧㄣ ㄉㄠˇ ㄌㄢˇ'),
    ('观光车', 'A', 'guānguāngchē', 'guānguāngchē', 'guanguangche1', 'guan1 guang1 che1', 'ㄍuanguangche', 'ㄍㄨㄢ ㄍㄨㄤ ㄔㄜ'),
    ('转换插头', 'A', 'zhuǎnhuàn chātóu', 'zhuǎnhuàn chātóu', 'zhuanhuan4 chatou2', 'zhuan3 huan4 cha1 tou2', 'ㄓuanhuanˋ ㄔatouˊ', 'ㄓㄨㄢˇ ㄏㄨㄢˋ ㄔㄚ ㄊㄡˊ'),
    ('常用药', 'A', 'chángyòngyào', 'chángyòngyào', 'changyongyao4', 'chang2 yong4 yao4', 'ㄔangyongyaoˋ', 'ㄔㄤˊ ㄩㄥˋ ㄧㄠˋ'),
    ('晕车药', 'A', 'yùnchēyào', 'yùnchēyào', 'yuncheyao4', 'yun4 che1 yao4', 'vncheyaoˋ', 'ㄩㄣˋ ㄔㄜ ㄧㄠˋ'),
    ('签证到期', 'A', 'qiānzhèng dàoqī', 'qiānzhèng dàoqī', 'qianzheng4 daoqi1', 'qian1 zheng4 dao4 qi1', 'ㄑianzhengˋ ㄉaoqi', 'ㄑㄧㄢ ㄓㄥˋ ㄉㄠˋ ㄑㄧ'),
    ('护照有效期', 'A', 'hùzhào yǒuxiàoqī', 'hùzhào yǒuxiàoqī', 'huzhao4 youxiaoqi1', 'hu4 zhao4 you3 xiao4 qi1', 'ㄏuzhaoˋ iouxiaoqi', 'ㄏㄨˋ ㄓㄠˋ ㄧㄡˇ ㄒㄧㄠˋ ㄑㄧ'),
    ('随身携带', 'A', 'suíshēn xiédài', 'suíshēn xiédài', 'suishen1 xiedai4', 'sui2 shen1 xie2 dai4', 'ㄙuishen ㄒiedaiˋ', 'ㄙㄨㄟˊ ㄕㄣ ㄒㄧㄝˊ ㄉㄞˋ'),
    ('行李提取处', 'A', 'xíngli tíqǔchù', 'xíngli tíqǔchù', 'xingli2 tiquchu4', 'xing2 li5 ti2 qu3 chu4', 'ㄒingliˊ ㄊiquchuˋ', 'ㄒㄧㄥˊ ㄌㄧ˙ ㄊㄧˊ ㄑㄩˇ ㄔㄨˋ'),
    ('出境卡', 'A', 'chūjìngkǎ', 'chūjìngkǎ', 'chujingka3', 'chu1 jing4 ka3', 'ㄔujingkaˇ', 'ㄔㄨ ㄐㄧㄥˋ ㄎㄚˇ'),
    ('入境卡', 'A', 'rùjìngkǎ', 'rùjìngkǎ', 'rujingka3', 'ru4 jing4 ka3', 'ㄖujingkaˇ', 'ㄖㄨˋ ㄐㄧㄥˋ ㄎㄚˇ'),
]


def fail(msg):
    print('GAGAL: ' + msg)
    sys.exit(1)


def fl(s):
    return re.sub(r"[\s'’·]", '', unicodedata.normalize('NFC', (s or '').lower()))


def load(name):
    path = os.path.join('data', name + '.json')
    with io.open(path, encoding='utf-8', newline='') as f:
        raw = f.read()
    nl = '\r\n' if '\r\n' in raw else '\n'
    return json.loads(raw.replace('\r\n', '\n')), nl, raw


def dump(obj, nl):
    s = json.dumps(obj, ensure_ascii=False, indent=2, separators=(',', ': '))
    return s.replace('\n', nl) if nl != '\n' else s


def main():
    apply = '--apply' in sys.argv
    print('Mode: ' + ('TERAPKAN (--apply)' if apply else 'LIHAT-DULU (tidak mengubah apa pun)'))
    for nm in ('app_words', 'produktif_karakter'):
        if not os.path.isfile(os.path.join('data', nm + '.json')):
            fail('berkas tidak ditemukan: data\\%s.json (jalankan dari folder C:\\mandarin_app)' % nm)
    words, nl_w, raw_w = load('app_words')
    prod, nl_p, raw_p = load('produktif_karakter')
    W = {w['simplified']: w for w in words}
    done, todo, bad = [], [], []
    for kata, grp, py0, py1, n0, n1, z0, z1 in TABEL:
        e = W.get(kata)
        if e is None:
            fail('kata tidak ada di app_words.json: ' + kata)
        cur = (e['pinyin'], e.get('pinyin_numeric'), e.get('bopomofo'))
        if cur == (py1, n1, z1):
            done.append(kata)
        elif cur == (py0, n0, z0):
            todo.append((kata, grp, py0, py1, n0, n1, z0, z1))
        else:
            bad.append((kata, cur))
    if bad:
        for k, c in bad:
            print('  tidak sesuai daftar: %s -> %s' % (k, c))
        fail('%d kata berbeda dari nilai yang tercatat di daftar; tidak ada yang diubah' % len(bad))
    print('Sudah benar: %d | akan diperbaiki: %d (A wisata: %d, B lain: %d)' % (
        len(done), len(todo), sum(1 for t in todo if t[1] == 'A'), sum(1 for t in todo if t[1] != 'A')))
    for kata, grp, py0, py1, n0, n1, z0, z1 in todo[:8]:
        print('    %s | angka: %s -> %s | zhuyin: %s -> %s%s' % (kata, n0, n1, z0, z1, (' | pinyin: %s -> %s' % (py0, py1)) if py0 != py1 else ''))
    if len(todo) > 8:
        print('    ... dan %d kata lain' % (len(todo) - 8))
    for kata, grp, py0, py1, n0, n1, z0, z1 in todo:
        e = W[kata]
        e['pinyin'], e['pinyin_numeric'], e['bopomofo'] = py1, n1, z1
    # pinyin tampil yang berubah juga di produktif_karakter (kata turunan)
    changed_py = {t[0]: (t[2], t[3]) for t in TABEL if t[2] != t[3]}
    nprod = 0
    for root, v in prod.items():
        for d in v.get('kata_turunan', []):
            k = d.get('kata')
            if k in changed_py and fl(d.get('pinyin')) == fl(changed_py[k][0]):
                d['pinyin'] = changed_py[k][1]
                nprod += 1
    print('produktif_karakter.json: %d baris pinyin kata turunan diubah' % nprod)
    if not todo and not nprod:
        print('Tidak ada yang perlu diubah: semuanya sudah benar.')
        return
    if not apply:
        print('\nBelum ada yang diubah. Jika sudah sesuai, jalankan:  python perbaiki_frasa.py --apply')
        return
    for nm, obj, nl, raw in (('app_words', words, nl_w, raw_w), ('produktif_karakter', prod, nl_p, raw_p)):
        new_raw = dump(obj, nl)
        if new_raw == raw:
            print('--  %s.json: tidak berubah' % nm)
            continue
        path = os.path.join('data', nm + '.json')
        bak = path + '.bak_frasa_' + TS
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

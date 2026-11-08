#!/usr/bin/env python3
# rebuild_tema.py
# Rebuild field 'themes' di app_words.json dari nol
# Aturan: kata masuk tema HANYA jika maknanya relevan secara semantik
# Jalankan: python rebuild_tema.py
# Output  : C:\mandarin_app\data\app_words.json (overwrite)
#           C:\mandarin_app\data\index_theme.json (rebuild)
#           C:\mandarin_app\data\LAPORAN_REBUILD_TEMA.txt

import json, os, re
from collections import defaultdict

DATA_DIR    = r"C:\mandarin_app\data"
IN_WORDS    = os.path.join(DATA_DIR, "app_words.json")
OUT_WORDS   = os.path.join(DATA_DIR, "app_words.json")
OUT_THEME   = os.path.join(DATA_DIR, "index_theme.json")
OUT_REPORT  = os.path.join(DATA_DIR, "LAPORAN_REBUILD_TEMA.txt")

lines = []
def log(s=""):
    print(s)
    lines.append(str(s))

def sep(title=""):
    log("\n" + "═"*60)
    log(f"  {title}")
    log("═"*60)

# ════════════════════════════════════════════════════════════
# DEFINISI TEMA — kata masuk jika:
#   'hanzi'    : karakter hanzi-nya cocok dengan daftar ini
#   'meanings' : arti ID-nya mengandung salah satu kata kunci ini
#   'pos_excl' : POS yang DILARANG masuk tema ini
#   'min_match': berapa kata kunci minimum harus cocok (default 1)
#
# Strategi: kombinasi whitelist hanzi + keyword arti
# Ini memastikan kata fungsi tidak masuk tema konkret
# ════════════════════════════════════════════════════════════

TEMA_RULES = {

    'warna': {
        'label_id': 'Warna',
        'label_zh': '颜色',
        'hanzi': [
            '红','橙','黄','绿','蓝','紫','黑','白','灰','粉',
            '棕','褐','金','银','青','靛','朱','赤','绛','碧',
            '翠','茜','红色','橙色','黄色','绿色','蓝色','紫色',
            '黑色','白色','灰色','粉色','粉红','棕色','金色','银色',
            '青色','彩色','颜色','色彩','色','五彩','彩虹',
            '深红','浅蓝','墨绿','米色','卡其','深蓝','淡黄',
            '红扑扑','翠绿','碧绿','朱红','深色','浅色','蓝领',
        ],
        'meanings': [
            'merah','orange','kuning','hijau','biru','ungu','hitam',
            'putih','abu','abu-abu','merah muda','pink','coklat','emas',
            'perak','warna','berwarna','bewarna','kebiruan','kehijauan',
            'kemerahan','kekuningan','hitam pekat','putih bersih',
        ],
        'pos_excl': ['u','p','c','d','e','r'],
    },

    'keluarga': {
        'label_id': 'Keluarga',
        'label_zh': '家庭',
        'hanzi': [
            '家','父','母','爸','妈','儿','女','子','兄','弟','姐','妹',
            '祖','孙','夫','妻','婆','公','舅','姑','叔','伯','婶','侄',
            '爸爸','妈妈','父亲','母亲','儿子','女儿','兄弟','姐妹',
            '祖父','祖母','爷爷','奶奶','外公','外婆','孙子','孙女',
            '丈夫','妻子','老公','老婆','夫妻','夫妇','婆婆','公公',
            '舅舅','舅妈','姑姑','姑父','叔叔','阿姨','伯伯','伯母',
            '侄子','侄女','外甥','亲戚','家人','家庭','家属','子女',
            '双亲','独生子','儿媳','女婿','继父','继母','养父','养母',
            '家长','户主','户口','孤儿','遗孀','寡妇',
        ],
        'meanings': [
            'ayah','ibu','anak','bapak','mama','papa','kakak','adik',
            'kakek','nenek','cucu','suami','istri','saudara','keluarga',
            'paman','bibi','keponakan','menantu','mertua','sanak','famili',
        ],
        'pos_excl': ['u','p','c','d','e'],
    },

    'hewan': {
        'label_id': 'Hewan & Binatang',
        'label_zh': '动物',
        'hanzi': [
            '狗','猫','鸟','鱼','马','牛','羊','猪','鸡','鸭','鹅',
            '兔','鼠','虎','狮','象','熊','猴','蛇','龙','凤','鹤',
            '鹰','燕','蝶','蜂','虫','蚊','蝇','蚂蚁','蟑螂',
            '狼','狐','鹿','豹','豹子','熊猫','大熊猫','老虎','狮子',
            '大象','长颈鹿','河马','犀牛','斑马','猩猩','海豚','鲸鱼',
            '鲨鱼','章鱼','螃蟹','龙虾','贝壳','蜗牛','青蛙','乌龟',
            '蜥蜴','壁虎','蝙蝠','松鼠','刺猬','穿山甲','仙鹤',
            '金鱼','热带鱼','鹦鹉','孔雀','企鹅','鸵鸟','猫头鹰',
            '动物','野生动物','宠物','家禽','家畜','昆虫','爬虫',
            '哺乳动物','鸟类','鱼类','两栖动物',
        ],
        'meanings': [
            'anjing','kucing','burung','ikan','kuda','sapi','kambing',
            'babi','ayam','bebek','kelinci','tikus','harimau','singa',
            'gajah','beruang','monyet','ular','serigala','rubah','rusa',
            'macan tutul','panda','lumba-lumba','paus','hiu','kepiting',
            'udang','katak','kura-kura','lebah','kupu-kupu','semut',
            'nyamuk','hewan','binatang','satwa','ternak','unggas',
            'serangga','reptil','mamalia',
        ],
        'pos_excl': ['u','p','c','d','e'],
    },

    'makanan_minuman': {
        'label_id': 'Makanan & Minuman',
        'label_zh': '食物饮料',
        'hanzi': [
            '饭','米','面','包','肉','鱼','菜','汤','粥','饺','饼',
            '水','茶','酒','奶','汁','饮料','咖啡','可乐','啤酒',
            '白酒','红酒','矿泉水','牛奶','豆浆','果汁','酸奶',
            '米饭','面条','面包','蛋糕','饼干','点心','小吃','零食',
            '早饭','午饭','晚饭','早餐','午餐','晚餐','宵夜',
            '牛肉','猪肉','鸡肉','鸭肉','羊肉','海鲜','虾','蟹',
            '豆腐','鸡蛋','火锅','炒饭','炒菜','烧烤','烤鸭',
            '饿','渴','吃','喝','味道','口味','美食','食物','食品',
            '调料','酱油','醋','盐','糖','辣椒','大蒜','姜',
            '营养','热量','卡路里','节食','减肥餐',
        ],
        'meanings': [
            'nasi','mie','roti','daging','ikan','sayur','sup','bubur',
            'pangsit','kue','air','teh','alkohol','susu','jus','minuman',
            'kopi','bir','anggur','makan','minum','lapar','haus',
            'rasa','makanan','minuman','masakan','santapan','kudapan',
            'sarapan','makan siang','makan malam','bumbu','garam',
            'gula','cuka','saus','kalori','nutrisi','diet',
        ],
        'pos_excl': ['u','p','c','e'],
    },

    'buah': {
        'label_id': 'Buah-buahan',
        'label_zh': '水果',
        'hanzi': [
            '苹果','香蕉','橙','橙子','桔子','橘子','葡萄','草莓',
            '西瓜','哈密瓜','芒果','菠萝','柠檬','桃','桃子','梨',
            '李子','杏','杏子','樱桃','荔枝','龙眼','椰子','榴莲',
            '木瓜','火龙果','猕猴桃','蓝莓','石榴','柚子','柿子',
            '枣','枇杷','山楂','无花果','杨梅','桑葚','水果',
        ],
        'meanings': [
            'apel','pisang','jeruk','anggur','stroberi','semangka',
            'melon','mangga','nanas','lemon','persik','pir','plum',
            'ceri','leci','kelapa','durian','pepaya','naga','kiwi',
            'blueberry','delima','buah',
        ],
        'pos_excl': ['u','p','c','d','e'],
    },

    'sayuran': {
        'label_id': 'Sayuran',
        'label_zh': '蔬菜',
        'hanzi': [
            '菜','蔬菜','白菜','青菜','菠菜','芹菜','韭菜','生菜',
            '卷心菜','花椰菜','西兰花','萝卜','胡萝卜','土豆','马铃薯',
            '红薯','地瓜','洋葱','大葱','蒜','大蒜','姜','辣椒',
            '西红柿','番茄','黄瓜','茄子','南瓜','苦瓜','冬瓜',
            '豆角','四季豆','豌豆','蘑菇','香菇','木耳','海带',
            '豆芽','竹笋','莲藕','百合','山药',
        ],
        'meanings': [
            'sayur','bayam','seledri','wortel','kentang','ubi','bawang',
            'bawang putih','jahe','cabai','tomat','mentimun','terong',
            'labu','jamur','kubis','brokoli','kacang','tauge','sayuran',
        ],
        'pos_excl': ['u','p','c','d','e'],
    },

    'angka': {
        'label_id': 'Angka & Bilangan',
        'label_zh': '数字',
        'hanzi': [
            '零','一','二','三','四','五','六','七','八','九','十',
            '百','千','万','亿','两','半','第','几','多少','数',
            '数字','数量','数目','号','码','编号','序号','奇数','偶数',
            '分之','百分','百分之','千分','倍','双','单','对','副',
            '共','合计','总共','共计','总数','小数','分数','整数',
        ],
        'meanings': [
            'nol','satu','dua','tiga','empat','lima','enam','tujuh',
            'delapan','sembilan','sepuluh','ratus','ribu','juta','miliar',
            'setengah','angka','bilangan','nomor','jumlah','hitungan',
            'digit','persen','kelipatan','genap','ganjil',
        ],
        'pos_excl': ['u','p','c','e'],
    },

    'waktu': {
        'label_id': 'Waktu & Jam',
        'label_zh': '时间',
        'hanzi': [
            '时','分','秒','钟','点','刻','时间','时刻','时候','时期',
            '早','晚','上午','下午','中午','午','凌晨','早上','晚上',
            '小时','半小时','一刻钟','整点',
        ],
        'meanings': [
            'jam','menit','detik','waktu','saat','pukul','dini hari',
            'pagi','siang','sore','malam','tengah malam','durasi',
        ],
        'pos_excl': ['u','p','c','e'],
    },

    'hari_tanggal': {
        'label_id': 'Hari, Bulan & Tanggal',
        'label_zh': '日期',
        'hanzi': [
            '今','昨','明','后','前','天','日','月','年','周','星期',
            '今天','昨天','明天','后天','前天','今年','去年','明年',
            '上周','下周','本周','这周','月份','季节','季度',
            '星期一','星期二','星期三','星期四','星期五','星期六','星期日','星期天',
            '周一','周二','周三','周四','周五','周六','周日',
            '一月','二月','三月','四月','五月','六月',
            '七月','八月','九月','十月','十一月','十二月',
            '元旦','春节','清明','端午','中秋','国庆','元宵',
            '节日','假日','假期','节假日','日期','年份','年代','世纪',
        ],
        'meanings': [
            'hari ini','kemarin','besok','lusa','hari','bulan','tahun',
            'minggu','senin','selasa','rabu','kamis','jumat','sabtu','minggu',
            'januari','februari','maret','april','mei','juni',
            'juli','agustus','september','oktober','november','desember',
            'musim','tanggal','penanggalan','liburan','hari raya',
        ],
        'pos_excl': ['u','p','c','e'],
    },

    'tubuh': {
        'label_id': 'Tubuh Manusia',
        'label_zh': '身体',
        'hanzi': [
            '头','脸','眼','耳','鼻','口','嘴','牙','舌','脖','颈',
            '肩','臂','手','指','胸','腹','肚','背','腰','臀','腿',
            '膝','脚','趾','发','皮','骨','肌','肉','血','心','肺',
            '肝','肾','胃','肠','脑','神经','头发','眉毛','睫毛',
            '嘴唇','下巴','额头','太阳穴','喉咙','食道','气管',
            '肌肉','关节','脊椎','肋骨','手腕','脚踝','膝盖',
            '身体','体','体重','身高','体温','血压','血型',
        ],
        'meanings': [
            'kepala','wajah','mata','telinga','hidung','mulut','gigi',
            'lidah','leher','bahu','lengan','tangan','jari','dada',
            'perut','punggung','pinggang','kaki','rambut','kulit',
            'tulang','otot','darah','jantung','paru','hati','ginjal',
            'otak','tubuh','badan','tinggi','berat badan','suhu',
        ],
        'pos_excl': ['u','p','c','d','e'],
    },

    'pakaian': {
        'label_id': 'Pakaian & Aksesori',
        'label_zh': '服装',
        'hanzi': [
            '衣','服','裤','裙','袜','鞋','帽','带','扣','领','袖',
            '衣服','上衣','外套','毛衣','衬衫','T恤','裤子','牛仔裤',
            '短裤','裙子','连衣裙','大衣','风衣','羽绒服','皮衣',
            '袜子','鞋子','皮鞋','运动鞋','高跟鞋','拖鞋','靴子',
            '帽子','围巾','手套','领带','皮带','腰带','包','手提包',
            '背包','钱包','眼镜','手表','项链','耳环','戒指','手镯',
            '内衣','睡衣','西装','礼服','制服','校服','运动服',
            '时装','时尚','品牌','尺码','号码','穿','戴','换',
        ],
        'meanings': [
            'baju','celana','rok','kaos kaki','sepatu','topi','ikat pinggang',
            'jaket','mantel','kemeja','kaos','jeans','gaun','pakaian',
            'busana','fashion','aksesori','jam tangan','kacamata',
            'kalung','anting','cincin','gelang','tas','dompet',
            'ukuran','memakai','mengenakan',
        ],
        'pos_excl': ['u','p','c','d','e'],
    },

    'kesehatan': {
        'label_id': 'Kesehatan & Medis',
        'label_zh': '健康医疗',
        'hanzi': [
            '病','药','医','院','症','健康','疾病','治疗','手术','检查',
            '医生','护士','医院','诊所','药房','药店','急救',
            '感冒','发烧','头痛','肚子痛','咳嗽','过敏','糖尿病',
            '高血压','心脏病','癌症','骨折','受伤','伤口','出血',
            '血压','血糖','体温','心率','呼吸','脉搏',
            '维生素','抗生素','止痛药','消炎药','疫苗','注射',
            '挂号','就诊','住院','手术室','急诊','救护车',
            '营养','蛋白质','脂肪','碳水','卡路里','保健',
        ],
        'meanings': [
            'sakit','obat','dokter','rumah sakit','perawat','kesehatan',
            'penyakit','pengobatan','operasi','pemeriksaan','demam',
            'flu','batuk','alergi','diabetes','kanker','tekanan darah',
            'luka','pendarahan','vitamin','antibiotik','vaksin',
            'rawat inap','ambulans','nutrisi','sehat','sembuh',
        ],
        'pos_excl': ['u','p','c','e'],
    },

    'pendidikan': {
        'label_id': 'Pendidikan & Sekolah',
        'label_zh': '教育',
        'hanzi': [
            '学','教','校','课','书','考','试','题','作业','成绩',
            '学生','老师','教师','教授','同学','班','年级','学期',
            '学校','幼儿园','小学','中学','高中','大学','研究生',
            '课本','教材','教室','图书馆','实验室','操场',
            '语文','数学','英语','物理','化学','生物','历史','地理',
            '上课','下课','听课','讲课','备课','复习','预习',
            '考试','考查','测验','期中考','期末考','高考','成绩',
            '毕业','入学','招生','报名','奖学金','助学金',
            '学费','校服','校规','班级','班主任','辅导',
        ],
        'meanings': [
            'belajar','mengajar','sekolah','guru','murid','pelajaran',
            'buku','ujian','tugas','nilai','kelas','semester',
            'taman kanak','sd','smp','sma','universitas','kuliah',
            'perpustakaan','laboratorium','kurikulum','mata pelajaran',
            'wisuda','beasiswa','biaya sekolah','pendidikan',
        ],
        'pos_excl': ['u','p','c','e'],
    },

    'pekerjaan': {
        'label_id': 'Pekerjaan & Profesi',
        'label_zh': '职业工作',
        'hanzi': [
            '工作','职业','职务','职位','岗位','上班','下班','加班',
            '医生','护士','老师','教师','工程师','律师','会计','程序员',
            '警察','消防员','军人','公务员','经理','总裁','总经理',
            '员工','职员','工人','农民','商人','服务员','司机',
            '厨师','厨子','设计师','建筑师','记者','编辑','作家',
            '艺术家','歌手','演员','运动员','裁判','教练',
            '工资','薪水','奖金','福利','合同','简历','面试','招聘',
            '辞职','解雇','退休','请假','出差','出勤',
        ],
        'meanings': [
            'pekerjaan','profesi','kerja','kantor','karyawan','pegawai',
            'dokter','perawat','guru','insinyur','pengacara','akuntan',
            'programmer','polisi','tentara','manajer','direktur',
            'petani','pedagang','sopir','koki','desainer','jurnalis',
            'seniman','penyanyi','aktor','atlet','gaji','upah','bonus',
            'kontrak','wawancara','rekrutmen','pensiun','cuti',
        ],
        'pos_excl': ['u','p','c','e'],
    },

    'transportasi': {
        'label_id': 'Transportasi',
        'label_zh': '交通运输',
        'hanzi': [
            '车','船','机','路','站','港','场','交通','运输','出行',
            '汽车','火车','地铁','公交','巴士','出租车','打车',
            '飞机','飞船','直升机','轮船','邮轮','渡船',
            '自行车','摩托车','电动车','滑板车','踏板车',
            '高铁','动车','城铁','轻轨','有轨电车',
            '车站','机场','港口','码头','停车场','加油站',
            '公路','高速','高速公路','铁路','航线','航班',
            '驾驶','开车','骑车','乘坐','搭','转乘','换乘',
            '堵车','塞车','超速','违章','事故','交通灯','红绿灯',
        ],
        'meanings': [
            'mobil','kereta','pesawat','kapal','sepeda','motor','bis',
            'taksi','subway','metro','transportasi','kendaraan',
            'stasiun','bandara','pelabuhan','terminal','lalu lintas',
            'berkendara','mengendarai','terbang','berlayar','mengemudi',
            'kemacetan','kecelakaan','rambu','tiket',
        ],
        'pos_excl': ['u','p','c','e'],
    },

    'olahraga': {
        'label_id': 'Olahraga & Kebugaran',
        'label_zh': '体育运动',
        'hanzi': [
            '运动','体育','锻炼','健身','比赛','竞赛','训练',
            '足球','篮球','排球','网球','乒乓球','羽毛球','棒球',
            '游泳','跑步','跳','骑','滑','举重','摔跤','拳击',
            '体操','瑜伽','武术','太极','跆拳道','功夫',
            '球','队','选手','运动员','教练','裁判','守门员',
            '赢','输','平','得分','进球','冠军','金牌','银牌','铜牌',
            '奥运','世界杯','联赛','马拉松','铁人三项',
        ],
        'meanings': [
            'olahraga','sepak bola','basket','voli','tenis','renang',
            'lari','loncat','angkat besi','senam','yoga','bela diri',
            'tinju','atlet','pelatih','wasit','juara','medali',
            'olimpiade','piala dunia','liga','maraton','fitness',
            'latihan','pertandingan','kompetisi',
        ],
        'pos_excl': ['u','p','c','e'],
    },

    'belanja': {
        'label_id': 'Belanja & Perdagangan',
        'label_zh': '购物',
        'hanzi': [
            '买','卖','购','价','钱','付','收','折','优惠','促销',
            '商店','超市','百货','商场','市场','专卖店','网店',
            '价格','价钱','定价','标价','售价','优惠价','特价',
            '打折','折扣','优惠券','满减','返现','积分',
            '收银台','购物车','购物袋','小票','发票','收据',
            '现金','信用卡','支付宝','微信支付','刷卡',
            '退货','换货','投诉','保修','售后','质量','品质',
        ],
        'meanings': [
            'membeli','menjual','belanja','harga','uang','bayar','diskon',
            'toko','supermarket','pasar','mal','promosi','murah','mahal',
            'kasir','keranjang','struk','invoice','kartu kredit','tunai',
            'refund','garansi','kualitas','belanja online',
        ],
        'pos_excl': ['u','p','c','e'],
    },

    'komunikasi': {
        'label_id': 'Komunikasi & Teknologi',
        'label_zh': '通讯技术',
        'hanzi': [
            '电话','手机','电脑','网络','网','信','消息','通话',
            '打电话','发短信','发消息','视频','语音','微信','电邮',
            '邮件','信件','信封','邮票','快递','包裹',
            '电视','广播','新闻','媒体','社交','网站','App','软件',
            '充电','信号','wifi','蓝牙','数据','流量','下载','上传',
            '密码','账号','注册','登录','搜索','浏览',
        ],
        'meanings': [
            'telepon','ponsel','komputer','internet','pesan','menelepon',
            'sms','video','email','surat','paket','pos','televisi',
            'siaran','berita','media','sosial','website','aplikasi',
            'baterai','sinyal','wifi','bluetooth','data','unduh','unggah',
            'kata sandi','akun','daftar','masuk','mencari','menjelajah',
        ],
        'pos_excl': ['u','p','c','e'],
    },

    'rumah_ruangan': {
        'label_id': 'Rumah & Ruangan',
        'label_zh': '家居',
        'hanzi': [
            '家','房','屋','室','厅','厨','卫','楼','门','窗','墙',
            '床','桌','椅','沙发','柜','灯','空调','冰箱','洗衣机',
            '电视','书架','衣柜','鞋柜','茶几','餐桌','书桌',
            '卧室','客厅','厨房','卫生间','浴室','阳台','走廊',
            '大厅','车库','地下室','阁楼','楼梯','电梯',
            '公寓','别墅','小区','楼房','平房','宿舍',
            '房租','物业','装修','家具','家电','家居',
        ],
        'meanings': [
            'rumah','kamar','ruang tamu','dapur','kamar mandi','kamar tidur',
            'balkon','koridor','apartemen','vila','asrama','lantai',
            'pintu','jendela','dinding','tempat tidur','meja','kursi',
            'sofa','lemari','lampu','AC','kulkas','mesin cuci','furnitur',
            'sewa','renovasi','dekorasi','properti',
        ],
        'pos_excl': ['u','p','c','e'],
    },

    'alam_lingkungan': {
        'label_id': 'Alam & Lingkungan',
        'label_zh': '自然环境',
        'hanzi': [
            '山','水','河','海','湖','树','花','草','石','土','风','雨',
            '太阳','月亮','星星','天空','云','闪电','彩虹',
            '森林','丛林','草原','沙漠','平原','高原','盆地',
            '大海','大洋','海湾','海峡','半岛','岛屿','礁石',
            '大山','山峰','山谷','山坡','悬崖','瀑布','泉水',
            '植物','动物','生态','自然','环境','地球','生物',
            '污染','保护','绿化','绿色','可持续','节能','减排',
        ],
        'meanings': [
            'gunung','sungai','laut','danau','pohon','bunga','rumput',
            'batu','tanah','angin','hujan','matahari','bulan','bintang',
            'langit','awan','petir','pelangi','hutan','padang rumput',
            'gurun','pulau','alam','lingkungan','bumi','ekologi',
            'polusi','perlindungan','penghijauan','berkelanjutan',
        ],
        'pos_excl': ['u','p','c','e'],
    },

    'cuaca': {
        'label_id': 'Cuaca & Musim',
        'label_zh': '天气季节',
        'hanzi': [
            '天气','气候','季节','温度','湿度','气压','风速',
            '晴','阴','雨','雪','雾','霜','冰','风',
            '春','夏','秋','冬','春天','夏天','秋天','冬天',
            '春季','夏季','秋季','冬季','梅雨','台风','暴雨',
            '大雨','小雨','中雨','阵雨','雷雨','冰雹','沙尘暴',
            '高温','低温','零下','结冰','解冻','回暖','降温',
        ],
        'meanings': [
            'cuaca','iklim','musim','suhu','kelembaban','angin','hujan',
            'salju','kabut','es','cerah','mendung','berawan','badai',
            'musim semi','musim panas','musim gugur','musim dingin',
            'topan','banjir','kekeringan','pemanasan','prakiraan',
        ],
        'pos_excl': ['u','p','c','e'],
    },

    'perjalanan_wisata': {
        'label_id': 'Perjalanan & Wisata',
        'label_zh': '旅游出行',
        'hanzi': [
            '旅游','旅行','出游','出发','到达','景点','景区','名胜',
            '酒店','宾馆','旅馆','客栈','青旅','民宿','帐篷',
            '签证','护照','机票','火车票','订票','订房',
            '导游','旅行社','团队游','自驾游','背包游',
            '海外','国外','境外','出国','入境','海关','边检',
            '行李','背包','行李箱','登机牌','安检','候机',
            '纪念品','特产','拍照','打卡','景色','风景','游览',
        ],
        'meanings': [
            'wisata','perjalanan','liburan','hotel','penginapan','hostel',
            'visa','paspor','tiket pesawat','tiket kereta','memesan',
            'pemandu wisata','agen perjalanan','luar negeri','imigrasi',
            'koper','tas punggung','boarding pass','pemeriksaan keamanan',
            'oleh-oleh','foto','pemandangan','tur','jalan-jalan',
        ],
        'pos_excl': ['u','p','c','e'],
    },

    'teknologi': {
        'label_id': 'Teknologi & Sains',
        'label_zh': '科技',
        'hanzi': [
            '科技','技术','科学','研究','发明','创新','数字','智能',
            '电脑','程序','软件','硬件','系统','平台','算法','数据',
            '人工智能','机器人','自动化','互联网','云计算','大数据',
            '芯片','处理器','内存','存储','电池','太阳能','核能',
            '实验室','研发','专利','科研','航天','卫星','探测器',
        ],
        'meanings': [
            'teknologi','sains','ilmu','penelitian','penemuan','inovasi',
            'digital','cerdas','komputer','program','software','hardware',
            'sistem','algoritma','data','kecerdasan buatan','robot',
            'otomasi','internet','cloud','chip','baterai','energi surya',
            'laboratorium','paten','satelit','luar angkasa',
        ],
        'pos_excl': ['u','p','c','e'],
    },

    'seni_budaya': {
        'label_id': 'Seni & Budaya',
        'label_zh': '艺术文化',
        'hanzi': [
            '艺术','文化','音乐','绘画','书法','雕塑','建筑','文学',
            '小说','诗歌','散文','戏剧','电影','动画','漫画',
            '唱歌','跳舞','演奏','表演','展览','博物馆','美术馆',
            '钢琴','小提琴','吉他','二胡','笛子','古筝','鼓',
            '传统文化','民俗','风俗','习俗','节日','礼仪',
            '历史','古代','现代','当代','民族','文明','遗产',
        ],
        'meanings': [
            'seni','budaya','musik','lukisan','kaligrafi','patung',
            'sastra','novel','puisi','drama','film','animasi','komik',
            'menyanyi','menari','bermain musik','pertunjukan','pameran',
            'museum','galeri','piano','biola','gitar','tradisional',
            'adat','istiadat','sejarah','peradaban','warisan',
        ],
        'pos_excl': ['u','p','c','e'],
    },

    'hobi_hiburan': {
        'label_id': 'Hobi & Hiburan',
        'label_zh': '爱好娱乐',
        'hanzi': [
            '爱好','兴趣','娱乐','游戏','玩','看','听','读','写','画',
            '电影','电视剧','综艺','动漫','游戏','棋','牌',
            '旅游','摄影','烹饪','园艺','钓鱼','登山','跑步',
            '阅读','书','杂志','漫画','音乐','歌','舞','跳舞',
            '网购','逛街','聚会','聊天','社交','直播','短视频',
        ],
        'meanings': [
            'hobi','minat','hiburan','permainan','bermain','menonton',
            'mendengarkan','membaca','menulis','menggambar','film',
            'sinetron','anime','catur','kartu','fotografi','memasak',
            'berkebun','memancing','pendakian','musik','tari',
            'belanja online','hangout','pesta','ngobrol','livestream',
        ],
        'pos_excl': ['u','p','c','e'],
    },

    'perasaan_emosi': {
        'label_id': 'Perasaan & Emosi',
        'label_zh': '情感',
        'hanzi': [
            '心情','情绪','感情','感觉','情感','心理',
            '高兴','快乐','开心','幸福','满意','骄傲','自豪',
            '伤心','难过','悲伤','哭','痛苦','绝望','沮丧',
            '生气','愤怒','不满','委屈','怨恨','恼火',
            '害怕','恐惧','担心','焦虑','紧张','不安',
            '惊喜','惊讶','好奇','兴奋','激动','感动',
            '孤独','寂寞','思念','想念','爱','恨','喜欢','讨厌',
            '同情','羡慕','嫉妒','感谢','感激','抱歉','后悔',
        ],
        'meanings': [
            'senang','bahagia','gembira','puas','bangga','sedih','menangis',
            'menderita','putus asa','marah','kesal','benci','takut',
            'cemas','khawatir','terkejut','penasaran','rindu','cinta',
            'benci','suka','tidak suka','simpati','iri','cemburu',
            'terima kasih','menyesal','perasaan','emosi','suasana hati',
        ],
        'pos_excl': ['u','p','c','d','e'],
    },

    'pendidikan_tinggi': {
        'label_id': 'Pendidikan Tinggi & Akademis',
        'label_zh': '高等教育',
        'hanzi': [
            '大学','学院','研究生','博士','硕士','本科','专科',
            '教授','副教授','讲师','导师','学者','院士',
            '论文','毕业论文','毕业设计','答辩','开题',
            '专业','学科','课程','学分','成绩单','学位','文凭',
            '奖学金','助学金','学费','宿舍','食堂','图书馆',
            '学术','科研','课题','项目','实验','报告','发表',
            '院系','系','学院','院长','系主任','班长','学生会',
        ],
        'meanings': [
            'universitas','perguruan tinggi','magister','doktor','sarjana',
            'profesor','dosen','peneliti','akademisi','skripsi','tesis',
            'disertasi','sidang','jurusan','mata kuliah','sks','ipk',
            'beasiswa','biaya kuliah','asrama','kantin','akademik',
            'riset','proyek','laporan','publikasi','gelar','diploma',
        ],
        'pos_excl': ['u','p','c','e'],
    },

    'pemerintahan_hukum': {
        'label_id': 'Pemerintahan & Hukum',
        'label_zh': '政府法律',
        'hanzi': [
            '政府','国家','法律','法规','制度','政策','规定','条例',
            '总统','主席','总理','部长','省长','市长','区长',
            '法院','检察院','公安局','警察局','监狱','法官','律师',
            '宪法','法典','刑法','民法','合同法','劳动法',
            '选举','投票','议会','人大','政协','党','民主',
            '税收','财政','预算','外交','条约','协议','协定',
            '公民','权利','义务','户籍','身份证','护照',
        ],
        'meanings': [
            'pemerintah','negara','hukum','peraturan','kebijakan',
            'presiden','perdana menteri','menteri','gubernur','walikota',
            'pengadilan','polisi','penjara','hakim','pengacara',
            'konstitusi','undang-undang','pemilu','parlemen','demokrasi',
            'pajak','anggaran','diplomasi','perjanjian','warga negara',
            'hak','kewajiban','ktp','paspor',
        ],
        'pos_excl': ['u','p','c','e'],
    },

    'bisnis_perdagangan': {
        'label_id': 'Bisnis & Perdagangan',
        'label_zh': '商业贸易',
        'hanzi': [
            '商业','贸易','企业','公司','集团','品牌','产品','服务',
            '市场','竞争','合作','合同','谈判','签约','成交',
            '利润','亏损','收入','支出','投资','融资','上市',
            '进口','出口','贸易顺差','贸易逆差','关税','配额',
            '销售','营销','推广','广告','代理','经销商',
            '客户','顾客','消费者','供应商','合作伙伴',
        ],
        'meanings': [
            'bisnis','perdagangan','perusahaan','korporasi','merek',
            'produk','layanan','pasar','persaingan','kerja sama',
            'kontrak','negosiasi','transaksi','laba','rugi','pendapatan',
            'investasi','saham','ekspor','impor','bea cukai','tarif',
            'penjualan','pemasaran','iklan','pelanggan','konsumen',
            'pemasok','mitra bisnis',
        ],
        'pos_excl': ['u','p','c','e'],
    },

    'keuangan': {
        'label_id': 'Keuangan & Perbankan',
        'label_zh': '金融银行',
        'hanzi': [
            '钱','银行','存款','取款','汇款','贷款','借款','还款',
            '账户','开户','信用卡','借记卡','银行卡','ATM',
            '利率','利息','本金','汇率','汇兑','外汇',
            '股票','基金','债券','期货','证券','投资','理财',
            '保险','医保','社保','养老金','公积金',
            '通货膨胀','通缩','GDP','财政','税','纳税',
            '收入','支出','预算','储蓄','花钱','节约',
        ],
        'meanings': [
            'uang','bank','tabungan','penarikan','transfer','pinjaman',
            'kredit','rekening','kartu kredit','debit','atm',
            'suku bunga','bunga','nilai tukar','valuta asing',
            'saham','reksa dana','obligasi','investasi','asuransi',
            'bpjs','pensiun','inflasi','deflasi','pajak','anggaran',
            'menabung','pengeluaran','hemat','keuangan',
        ],
        'pos_excl': ['u','p','c','e'],
    },

    'negara_budaya': {
        'label_id': 'Negara & Kebudayaan',
        'label_zh': '国家文化',
        'hanzi': [
            '中国','美国','日本','韩国','英国','法国','德国','俄国',
            '印度','印尼','泰国','越南','马来西亚','新加坡','澳大利亚',
            '非洲','欧洲','亚洲','美洲','大洋洲','北极','南极',
            '民族','国籍','文化','语言','宗教','传统','习俗',
            '华人','华侨','移民','留学生','外国人','外籍',
        ],
        'meanings': [
            'tiongkok','china','amerika','jepang','korea','inggris',
            'prancis','jerman','rusia','india','indonesia','thailand',
            'vietnam','singapura','australia','eropa','asia','afrika',
            'bangsa','kebangsaan','budaya','bahasa','agama','tradisi',
            'diaspora','imigran','pelajar asing','warga asing',
        ],
        'pos_excl': ['u','p','c','e'],
    },

    'arah_lokasi': {
        'label_id': 'Arah & Lokasi',
        'label_zh': '方位',
        'hanzi': [
            '东','西','南','北','上','下','左','右','前','后','中',
            '里','外','内','旁','边','角','端','侧','方','向',
            '东边','西边','南边','北边','左边','右边','前面','后面',
            '中间','附近','周围','旁边','对面','斜对面',
            '东方','西方','南方','北方','东南','东北','西南','西北',
            '正东','正西','正南','正北','中央','中心','中部',
            '上方','下方','左方','右方','顶部','底部','侧面',
        ],
        'meanings': [
            'timur','barat','selatan','utara','atas','bawah','kiri','kanan',
            'depan','belakang','tengah','dalam','luar','samping','sudut',
            'arah','lokasi','posisi','sekitar','dekat','berhadapan',
        ],
        'pos_excl': ['u','p','c','e'],
    },

    'sifat_deskripsi': {
        'label_id': 'Sifat & Deskripsi',
        'label_zh': '性质描述',
        'hanzi': [
            '大','小','多','少','高','低','长','短','宽','窄','粗','细',
            '厚','薄','重','轻','快','慢','新','旧','好','坏','美','丑',
            '强','弱','聪明','笨','勤劳','懒','认真','马虎','诚实','虚伪',
            '热情','冷漠','友好','善良','凶狠','温柔','粗鲁','文明',
            '干净','脏','整齐','乱','准时','迟到','积极','消极',
            '复杂','简单','难','容易','清楚','模糊','正确','错误',
            '重要','次要','普通','特殊','一般','常见','罕见','奇怪',
        ],
        'meanings': [
            'besar','kecil','banyak','sedikit','tinggi','rendah','panjang',
            'pendek','lebar','sempit','tebal','tipis','berat','ringan',
            'cepat','lambat','baru','lama','bagus','buruk','indah','jelek',
            'kuat','lemah','cerdas','bodoh','rajin','malas','jujur','bohong',
            'ramah','baik hati','jahat','lembut','kasar','bersih','kotor',
            'rapi','berantakan','tepat waktu','penting','biasa','aneh',
            'kompleks','sederhana','sulit','mudah','jelas','benar','salah',
        ],
        'pos_excl': ['u','p','c','e'],
    },

    'kata_fungsi': {
        'label_id': 'Kata Fungsi & Partikel',
        'label_zh': '功能词',
        'hanzi': [
            '的','了','着','过','吗','呢','吧','啊','哦','哇','喔',
            '是','不','没','也','都','很','非常','太','更','最',
            '和','跟','与','及','或','但','可是','然而','所以','因为',
            '如果','虽然','即使','只要','只有','除非','只是',
            '把','被','让','使','叫','请','对','向','从','到','在',
            '比','跟','像','为','给','替','按照','根据','通过',
            '已经','正在','将','曾经','刚','才','就','还','再','又',
            '一','每','各','该','这','那','哪','什么','谁','怎么',
        ],
        'meanings': [
            'partikel','kata sambung','preposisi','adverbia','konjungsi',
            'adalah','tidak','juga','dan','atau','tetapi','karena','jika',
            'meskipun','sudah','sedang','akan','pernah','baru saja',
        ],
        'pos_allow': ['u','p','c','d','e','r'],  # hanya POS ini yang boleh
    },

    'kata_tanya': {
        'label_id': 'Kata Tanya & Interogatif',
        'label_zh': '疑问词',
        'hanzi': [
            '什么','谁','哪','哪里','哪儿','哪个','哪些','几','多少',
            '怎么','怎样','怎么样','为什么','何时','何地','何人','何物',
            '多久','多长','多高','多重','多大','多远',
            '吗','呢','吧','是吗','对吗','好吗','可以吗',
        ],
        'meanings': [
            'apa','siapa','di mana','mana','yang mana','berapa','bagaimana',
            'mengapa','kapan','seberapa','apakah','betul',
        ],
        'pos_excl': [],
    },

    'konstruksi_teknik': {
        'label_id': 'Konstruksi & Teknik',
        'label_zh': '建筑工程',
        'hanzi': [
            '建筑','建设','施工','工程','结构','设计','规划','图纸',
            '砖','混凝土','钢铁','木材','玻璃','塑料','石材',
            '墙','柱','梁','板','基础','地基','屋顶','楼板',
            '道路','桥梁','隧道','地铁','水坝','电站',
            '工厂','车间','仓库','厂房','办公楼','写字楼',
        ],
        'meanings': [
            'konstruksi','bangunan','gedung','teknik','struktur','desain',
            'bata','beton','baja','kayu','kaca','plastik','batu',
            'dinding','kolom','balok','fondasi','atap','jalan','jembatan',
            'terowongan','bendungan','pabrik','gudang','kantor',
        ],
        'pos_excl': ['u','p','c','e'],
    },

    'tekstil_fashion': {
        'label_id': 'Tekstil & Mode',
        'label_zh': '纺织时尚',
        'hanzi': [
            '布','丝','棉','麻','毛','革','皮','绸','缎','绒','纱',
            '纺织','织物','面料','材质','质地','花纹','图案',
            '时尚','流行','潮流','款式','设计','品牌','奢侈',
            '裁缝','剪裁','缝纫','刺绣','印染','纺纱','编织',
        ],
        'meanings': [
            'kain','sutra','katun','linen','wol','kulit','satin','velvet',
            'tekstil','bahan','motif','pola','mode','tren','gaya',
            'merek','mewah','penjahit','jahitan','sulam','tenun',
        ],
        'pos_excl': ['u','p','c','e'],
    },

    'pertanian_pangan': {
        'label_id': 'Pertanian & Pangan',
        'label_zh': '农业粮食',
        'hanzi': [
            '农业','农村','农民','农田','耕地','土地','播种','种植',
            '水稻','小麦','玉米','大豆','棉花','茶叶','甘蔗',
            '收获','丰收','粮食','粮仓','农产品','蔬菜','水果',
            '化肥','农药','灌溉','施肥','除草','除虫',
            '牧场','畜牧','养殖','渔业','捕鱼','水产',
        ],
        'meanings': [
            'pertanian','desa','petani','sawah','ladang','menanam','panen',
            'padi','gandum','jagung','kedelai','teh','gula','beras',
            'pupuk','pestisida','irigasi','ternak','peternakan','perikanan',
            'hasil bumi','pangan','ketahanan pangan',
        ],
        'pos_excl': ['u','p','c','e'],
    },

    'lingkungan_hidup': {
        'label_id': 'Lingkungan Hidup',
        'label_zh': '环境保护',
        'hanzi': [
            '环境','生态','自然','污染','排放','废气','废水','垃圾',
            '回收','节能','减排','碳排放','温室气体','全球变暖',
            '可持续','绿色','清洁','保护','濒危','灭绝','生物多样性',
            '太阳能','风能','水能','核能','新能源','电动车',
        ],
        'meanings': [
            'lingkungan','ekologi','alam','polusi','emisi','limbah','sampah',
            'daur ulang','hemat energi','karbon','pemanasan global',
            'berkelanjutan','hijau','bersih','perlindungan','punah',
            'keanekaragaman hayati','energi surya','angin','nuklir',
        ],
        'pos_excl': ['u','p','c','e'],
    },

    'agama_kepercayaan': {
        'label_id': 'Agama & Kepercayaan',
        'label_zh': '宗教信仰',
        'hanzi': [
            '宗教','信仰','佛教','道教','儒教','基督教','伊斯兰教',
            '寺庙','庙宇','教堂','清真寺','神社',
            '神','佛','菩萨','上帝','真主','耶稣','孔子',
            '信徒','教徒','僧侣','和尚','尼姑','牧师','神父','阿訇',
            '祈祷','礼拜','冥想','打坐','斋戒','献祭',
            '天堂','地狱','灵魂','轮回','因果','缘分','命运',
        ],
        'meanings': [
            'agama','kepercayaan','buddha','taoisme','konfusianisme',
            'kristen','islam','kuil','masjid','gereja',
            'tuhan','allah','yesus','konfusius','biksu','pendeta','imam',
            'berdoa','ibadah','meditasi','puasa','surga','neraka',
            'jiwa','reinkarnasi','karma','takdir','nasib',
        ],
        'pos_excl': ['u','p','c','e'],
    },
}

# ════════════════════════════════════════════════════════════
# FUNGSI MATCHING
# ════════════════════════════════════════════════════════════

def get_meanings_text(word):
    """Gabungkan semua arti Indonesia menjadi satu string lower."""
    parts = []
    m = word.get('meanings_id') or []
    if isinstance(m, list):
        parts.extend(m)
    elif m:
        parts.append(str(m))
    return ' '.join(str(p) for p in parts).lower()

def word_matches_tema(word, tema_key, rule):
    simp    = word.get('simplified', '')
    pos_list = word.get('pos', []) or []
    meaning_text = get_meanings_text(word)

    # Cek POS exclusion
    if 'pos_excl' in rule:
        if any(p in pos_list for p in rule['pos_excl']):
            # Untuk kata_fungsi: hanya allow POS tertentu
            if tema_key == 'kata_fungsi':
                pass  # kata_fungsi ditangani tersendiri
            elif tema_key == 'kata_tanya':
                pass  # kata_tanya juga ditangani tersendiri
            else:
                return False

    # Untuk kata_fungsi: cek berdasarkan pos_allow
    if tema_key == 'kata_fungsi':
        if 'pos_allow' in rule:
            if any(p in pos_list for p in rule['pos_allow']):
                return True
        # Juga cek hanzi whitelist
        if simp in rule.get('hanzi', []):
            return True
        return False

    # Cek hanzi whitelist (cocok persis)
    if simp in rule.get('hanzi', []):
        return True

    # Cek keyword meanings
    for kw in rule.get('meanings', []):
        if kw.lower() in meaning_text:
            return True

    return False

# ════════════════════════════════════════════════════════════
# PROSES UTAMA
# ════════════════════════════════════════════════════════════

sep("Memuat app_words.json")
with open(IN_WORDS, "r", encoding="utf-8") as f:
    words = json.load(f)
log(f"  ✓ {len(words):,} kata dimuat")

sep("Rebuild tema untuk setiap kata")

tema_counts_before = defaultdict(int)
tema_counts_after  = defaultdict(int)

for w in words:
    old_themes = w.get('themes') or []
    for t in old_themes:
        tema_counts_before[t] += 1

# Rebuild
for w in words:
    new_themes = []
    for tema_key, rule in TEMA_RULES.items():
        if word_matches_tema(w, tema_key, rule):
            new_themes.append(tema_key)
    w['themes'] = new_themes
    for t in new_themes:
        tema_counts_after[t] += 1

# ════════════════════════════════════════════════════════════
# LAPORAN PERBANDINGAN
# ════════════════════════════════════════════════════════════

sep("Perbandingan jumlah kata per tema (sebelum vs sesudah)")
log(f"  {'Tema':<30} {'Sebelum':>8} {'Sesudah':>8}  {'Δ':>7}")
log(f"  {'-'*30} {'-'*8} {'-'*8}  {'-'*7}")
for tema in sorted(TEMA_RULES.keys()):
    before = tema_counts_before.get(tema, 0)
    after  = tema_counts_after.get(tema, 0)
    delta  = after - before
    sign   = '+' if delta >= 0 else ''
    log(f"  {tema:<30} {before:>8,} {after:>8,}  {sign}{delta:>6,}")

sep("Verifikasi: kata-kata dasar sekarang temanya apa")
kata_dasar = ['的','了','我','是','你','他','和','在','不','有']
for w in words:
    if w.get('simplified') in kata_dasar:
        log(f"  {w['simplified']:<4}  {len(w['themes'])} tema: {w['themes']}")

sep("Verifikasi tema 'warna' — 20 kata pertama")
warna = [w for w in words if 'warna' in w.get('themes', [])]
log(f"  Total kata tema warna: {len(warna)}")
for w in sorted(warna, key=lambda x: x.get('frequency', 99999))[:20]:
    log(f"  {w['simplified']:<8} {w.get('pinyin',''):<15} {(w.get('meanings_id') or [''])[0][:40]}")

sep("Verifikasi tema 'keluarga' — 20 kata pertama")
kel = [w for w in words if 'keluarga' in w.get('themes', [])]
log(f"  Total kata tema keluarga: {len(kel)}")
for w in sorted(kel, key=lambda x: x.get('frequency', 99999))[:20]:
    log(f"  {w['simplified']:<8} {w.get('pinyin',''):<15} {(w.get('meanings_id') or [''])[0][:40]}")

sep("Verifikasi tema 'hewan' — 20 kata pertama")
hewan = [w for w in words if 'hewan' in w.get('themes', [])]
log(f"  Total kata tema hewan: {len(hewan)}")
for w in sorted(hewan, key=lambda x: x.get('frequency', 99999))[:20]:
    log(f"  {w['simplified']:<8} {w.get('pinyin',''):<15} {(w.get('meanings_id') or [''])[0][:40]}")

sep("Kata tanpa tema sama sekali")
tanpa_tema = [w for w in words if not w.get('themes')]
log(f"  Total: {len(tanpa_tema)}")
log(f"  Contoh 10: {[w['simplified'] for w in tanpa_tema[:10]]}")

# ════════════════════════════════════════════════════════════
# SIMPAN
# ════════════════════════════════════════════════════════════

sep("Menyimpan app_words.json")
with open(OUT_WORDS, "w", encoding="utf-8") as f:
    json.dump(words, f, ensure_ascii=False)
log(f"  ✓ app_words.json disimpan")

sep("Menyimpan index_theme.json")
freq_map = {w.get('simplified',''): w.get('frequency', 99999) for w in words}
idx_theme = defaultdict(list)
for w in words:
    simp = w.get('simplified', '')
    for t in (w.get('themes') or []):
        idx_theme[t].append(simp)
for t in idx_theme:
    idx_theme[t].sort(key=lambda x: freq_map.get(x, 99999))

# Tambah metadata label
idx_theme_out = {}
for tema_key, rule in TEMA_RULES.items():
    idx_theme_out[tema_key] = {
        'label_id': rule.get('label_id', tema_key),
        'label_zh': rule.get('label_zh', ''),
        'words': idx_theme.get(tema_key, []),
    }

with open(OUT_THEME, "w", encoding="utf-8") as f:
    json.dump(idx_theme_out, f, ensure_ascii=False)
log(f"  ✓ index_theme.json disimpan")

# Simpan laporan
with open(OUT_REPORT, "w", encoding="utf-8") as f:
    f.write("\n".join(lines))
log(f"  ✓ Laporan: {OUT_REPORT}")
print("\n✅ Rebuild tema selesai!")
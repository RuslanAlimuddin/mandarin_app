#!/usr/bin/env python3
# ekstrak_kandidat_tema.py
# Ekstrak kandidat kata per tema berdasarkan HANZI dan PINYIN saja
# Output untuk dikurasi: C:\mandarin_app\data\KANDIDAT_TEMA.txt
# Jalankan: python ekstrak_kandidat_tema.py

import json, os, re
from collections import defaultdict

DATA_DIR   = r"C:\mandarin_app\data"
IN_WORDS   = os.path.join(DATA_DIR, "app_words.json")
OUT_REPORT = os.path.join(DATA_DIR, "KANDIDAT_TEMA.txt")

lines = []
def log(s=""):
    print(s)
    lines.append(str(s))

def sep(title=""):
    log("\n" + "═"*60)
    log(f"  {title}")
    log("═"*60)

with open(IN_WORDS, "r", encoding="utf-8") as f:
    words = json.load(f)

# Buat lookup: simplified → word object
lookup = {w.get('simplified',''): w for w in words}

log(f"Total kata: {len(words):,}")

# ════════════════════════════════════════════════════════════
# Untuk setiap tema, kita filter kata berdasarkan:
# 1. Kata dalam SEED LIST (hanzi yang pasti relevan)
# 2. Tambahan: radical matching
# 3. Kata yang meanings_id-nya DIMULAI dengan kata kunci
#    (bukan contains, tapi startswith — lebih ketat)
# ════════════════════════════════════════════════════════════

def get_first_meaning(word):
    m = word.get('meanings_id') or []
    if isinstance(m, list) and m:
        return str(m[0]).lower().strip()
    elif isinstance(m, str):
        return m.lower().strip()
    return ''

def starts_with_any(text, keywords):
    """True jika text DIMULAI dengan salah satu keyword."""
    for kw in keywords:
        if text.startswith(kw.lower()):
            return True
    return False

def contains_exact(text, keywords):
    """True jika keyword cocok sebagai kata utuh di awal arti."""
    for kw in keywords:
        # Harus di awal atau setelah tanda baca
        pattern = r'(^|[;,/(])' + re.escape(kw.lower())
        if re.search(pattern, text):
            return True
    return False

# ════════════════════════════════════════════════════════════
# DEFINISI TEMA — hanya hanzi seed + radical filter
# Meanings keyword HANYA dipakai jika SANGAT spesifik
# ════════════════════════════════════════════════════════════

TEMA_SEEDS = {

    'warna': {
        'label': 'Warna',
        # Kata yang PASTI warna atau sangat terkait warna
        'exact_hanzi': [
            '红','橙','黄','绿','蓝','紫','黑','白','灰','粉',
            '棕','褐','金','银','青','靛','朱','赤','绛','碧',
            '翠','茜','红色','橙色','黄色','绿色','蓝色','紫色',
            '黑色','白色','灰色','粉色','粉红','棕色','金色','银色',
            '青色','彩色','颜色','色彩','五彩','彩虹','深红','浅蓝',
            '墨绿','米色','深蓝','淡黄','碧绿','朱红','深色','浅色',
        ],
        # Kata yang artinya DIMULAI persis dengan nama warna
        'meaning_starts': [
            'merah','oranye','kuning','hijau','biru','ungu','hitam',
            'putih','abu-abu','abu','merah muda','pink','coklat',
            'emas','perak','warna','berwarna',
        ],
    },

    'keluarga': {
        'label': 'Keluarga',
        'exact_hanzi': [
            '爸','妈','父','母','兄','弟','姐','妹','子','女',
            '祖','孙','夫','妻','婆','公','舅','姑','叔','伯','婶','侄',
            '爸爸','妈妈','父亲','母亲','儿子','女儿','兄弟','姐妹',
            '祖父','祖母','爷爷','奶奶','外公','外婆','孙子','孙女',
            '丈夫','妻子','老公','老婆','夫妻','夫妇','婆婆','公公',
            '舅舅','舅妈','姑姑','姑父','叔叔','阿姨','伯伯','伯母',
            '侄子','侄女','外甥','亲戚','家人','家庭','家属','子女',
            '双亲','儿媳','女婿','继父','继母','养父','养母','家长',
            '孤儿','寡妇','家族','亲人','长辈','晚辈',
        ],
        'meaning_starts': [
            'ayah','ibu','bapak','anak laki','anak perempuan','kakak',
            'adik','kakek','nenek','cucu','suami','istri','paman',
            'bibi','keponakan','mertua','menantu','saudara','keluarga',
        ],
    },

    'hewan': {
        'label': 'Hewan',
        'exact_hanzi': [
            '狗','猫','鸟','马','牛','羊','猪','鸡','鸭','鹅','兔',
            '鼠','虎','狮','象','熊','猴','蛇','龙','凤','鹤','鹰',
            '燕','蝶','蜂','虫','蚊','蝇','蚂蚁','蟑螂','狼','狐',
            '鹿','豹','豹子','熊猫','大熊猫','老虎','狮子','大象',
            '长颈鹿','河马','犀牛','斑马','猩猩','海豚','鲸鱼','鲨鱼',
            '章鱼','螃蟹','龙虾','蜗牛','青蛙','乌龟','蜥蜴','壁虎',
            '蝙蝠','松鼠','刺猬','仙鹤','金鱼','鹦鹉','孔雀','企鹅',
            '鸵鸟','猫头鹰','动物','野生动物','宠物','家禽','家畜',
            '昆虫','爬虫','哺乳动物','鸟类','两栖动物',
            # Ikan
            '鱼','鲤鱼','草鱼','鲫鱼','带鱼','黄鱼','鳊鱼',
        ],
        'meaning_starts': [
            'anjing','kucing','burung','kuda','sapi','kambing','babi',
            'ayam','bebek','kelinci','tikus','harimau','singa','gajah',
            'beruang','monyet','ular','naga','bangau','elang','lebah',
            'kupu-kupu','semut','nyamuk','serigala','rusa','panda',
            'lumba-lumba','paus','hiu','kepiting','katak','kura-kura',
            'anjing laut','burung hantu','hewan','binatang','satwa',
        ],
    },

    'buah': {
        'label': 'Buah-buahan',
        'exact_hanzi': [
            '苹果','香蕉','橙','橙子','桔子','橘子','葡萄','草莓',
            '西瓜','哈密瓜','芒果','菠萝','柠檬','桃','桃子','梨',
            '李子','杏','杏子','樱桃','荔枝','龙眼','椰子','榴莲',
            '木瓜','火龙果','猕猴桃','蓝莓','石榴','柚子','柿子',
            '枣','枇杷','山楂','无花果','杨梅','桑葚','水果',
            '果汁','果肉','果皮','果核',
        ],
        'meaning_starts': [
            'apel','pisang','jeruk','anggur','stroberi','semangka',
            'melon','mangga','nanas','lemon','persik','pir','plum',
            'ceri','leci','kelapa','durian','pepaya','buah naga',
            'kiwi','blueberry','delima','buah',
        ],
    },

    'sayuran': {
        'label': 'Sayuran',
        'exact_hanzi': [
            '菜','蔬菜','白菜','青菜','菠菜','芹菜','韭菜','生菜',
            '卷心菜','花椰菜','西兰花','萝卜','胡萝卜','土豆','马铃薯',
            '红薯','地瓜','洋葱','大葱','葱','蒜','大蒜','姜','辣椒',
            '西红柿','番茄','黄瓜','茄子','南瓜','苦瓜','冬瓜',
            '豆角','四季豆','豌豆','蘑菇','香菇','木耳','海带',
            '豆芽','竹笋','莲藕','百合','山药',
        ],
        'meaning_starts': [
            'bayam','seledri','wortel','kentang','ubi','bawang',
            'bawang putih','bawang bombay','jahe','cabai','tomat',
            'mentimun','terong','labu','jamur','kubis','brokoli',
            'kacang panjang','tauge','bambu','teratai','sayuran','sayur',
        ],
    },

    'makanan_minuman': {
        'label': 'Makanan & Minuman',
        'exact_hanzi': [
            '饭','米','面','包','肉','汤','粥','饺','饼','面条',
            '米饭','面包','蛋糕','饼干','点心','小吃','零食',
            '早饭','午饭','晚饭','早餐','午餐','晚餐','宵夜',
            '牛肉','猪肉','鸡肉','鸭肉','羊肉','海鲜','虾','蟹',
            '豆腐','鸡蛋','火锅','炒饭','炒菜','烧烤','烤鸭',
            '水','茶','酒','奶','汁','饮料','咖啡','可乐','啤酒',
            '白酒','红酒','矿泉水','牛奶','豆浆','果汁','酸奶',
            '食物','食品','美食','调料','酱油','醋','盐','糖',
            '营养','热量','卡路里','菜单','套餐','外卖',
        ],
        'meaning_starts': [
            'nasi','mie','roti','daging','sup','bubur','pangsit',
            'kue','camilan','makanan ringan','sarapan','makan siang',
            'makan malam','sate','barbeque','teh','kopi','bir','susu',
            'jus','minuman','makanan','masakan','bumbu','garam','gula',
            'cuka','saus','kalori','nutrisi','menu','pesanan',
        ],
    },

    'tubuh': {
        'label': 'Tubuh Manusia',
        'exact_hanzi': [
            '头','脸','眼','眼睛','耳','耳朵','鼻','鼻子','口','嘴',
            '嘴巴','牙','牙齿','舌','舌头','脖','颈','脖子','肩',
            '肩膀','臂','手臂','手','手指','胸','腹','肚子','背',
            '腰','臀','腿','膝','膝盖','脚','脚趾','发','头发',
            '皮肤','骨头','肌肉','血','心脏','肺','肝','肾','胃',
            '肠','大脑','脑','神经','喉咙','眉毛','睫毛','嘴唇',
            '下巴','额头','太阳穴','食道','气管','关节','脊椎',
            '肋骨','手腕','脚踝','身体','体重','身高','体温','血压',
        ],
        'meaning_starts': [
            'kepala','wajah','mata','telinga','hidung','mulut','gigi',
            'lidah','leher','bahu','lengan','tangan','jari','dada',
            'perut','punggung','pinggang','panggul','kaki','rambut',
            'kulit','tulang','otot','darah','jantung','paru-paru',
            'hati','ginjal','lambung','otak','saraf','tenggorokan',
            'alis','bulu mata','bibir','dagu','dahi',
        ],
    },

    'pakaian': {
        'label': 'Pakaian & Aksesori',
        'exact_hanzi': [
            '衣服','上衣','外套','毛衣','衬衫','裤子','牛仔裤',
            '短裤','裙子','连衣裙','大衣','风衣','羽绒服','皮衣',
            '袜子','鞋子','皮鞋','运动鞋','高跟鞋','拖鞋','靴子',
            '帽子','围巾','手套','领带','皮带','腰带',
            '手提包','背包','钱包','眼镜','手表','项链','耳环',
            '戒指','手镯','内衣','睡衣','西装','礼服','制服','校服',
            '运动服','时装','尺码','T恤','夹克',
        ],
        'meaning_starts': [
            'baju','celana','rok','kaos kaki','sepatu','topi',
            'ikat pinggang','jaket','mantel','kemeja','kaos','jeans',
            'gaun','pakaian','busana','syal','sarung tangan','dasi',
            'tas tangan','ransel','dompet','kacamata','jam tangan',
            'kalung','anting','cincin','gelang','piyama','jas',
            'seragam','baju olahraga','ukuran baju',
        ],
    },

    'angka': {
        'label': 'Angka & Bilangan',
        'exact_hanzi': [
            '零','一','二','三','四','五','六','七','八','九','十',
            '百','千','万','亿','两','半','第','数','数字','数量',
            '数目','号','码','编号','序号','奇数','偶数','整数',
            '小数','分数','百分','倍','双','单','总数','合计',
        ],
        'meaning_starts': [
            'nol','satu','dua','tiga','empat','lima','enam','tujuh',
            'delapan','sembilan','sepuluh','ratus','ribu','juta',
            'miliar','setengah','angka','bilangan','nomor','jumlah',
            'hitungan','digit','persen','kelipatan','genap','ganjil',
        ],
    },

    'waktu': {
        'label': 'Waktu & Jam',
        'exact_hanzi': [
            '小时','分钟','秒','时间','时刻','时候','上午','下午',
            '中午','凌晨','早上','晚上','傍晚','黄昏','午夜','半夜',
            '清晨','正午','时','分','秒','钟','点','刻',
            '整点','报时','时区','当地时间',
        ],
        'meaning_starts': [
            'jam','menit','detik','waktu','saat','pukul','dini hari',
            'pagi','siang','sore','malam','tengah malam','fajar',
            'senja','zona waktu',
        ],
    },

    'hari_tanggal': {
        'label': 'Hari, Bulan & Tanggal',
        'exact_hanzi': [
            '今天','昨天','明天','后天','前天','今年','去年','明年',
            '上周','下周','本周','这周','上个月','下个月','本月',
            '星期一','星期二','星期三','星期四','星期五','星期六',
            '星期日','星期天','周一','周二','周三','周四','周五',
            '周六','周日','一月','二月','三月','四月','五月','六月',
            '七月','八月','九月','十月','十一月','十二月',
            '元旦','春节','清明','端午','中秋','国庆','元宵',
            '节日','假日','假期','节假日','日期','年份','年代','世纪',
            '季节','月份','周末','工作日',
        ],
        'meaning_starts': [
            'hari ini','kemarin','besok','lusa','tahun ini','tahun lalu',
            'tahun depan','minggu lalu','minggu depan','bulan lalu',
            'bulan depan','senin','selasa','rabu','kamis','jumat',
            'sabtu','minggu','januari','februari','maret','april',
            'mei','juni','juli','agustus','september','oktober',
            'november','desember','tahun baru','imlek','lebaran',
            'hari raya','tanggal','abad','musim','akhir pekan',
        ],
    },

    'kesehatan': {
        'label': 'Kesehatan & Medis',
        'exact_hanzi': [
            '医生','护士','医院','诊所','药房','药店','急救',
            '感冒','发烧','头痛','肚子痛','咳嗽','过敏','糖尿病',
            '高血压','心脏病','癌症','骨折','受伤','伤口','出血',
            '血压','血糖','体温','心率','呼吸','脉搏',
            '维生素','抗生素','止痛药','消炎药','疫苗','注射',
            '挂号','就诊','住院','急诊','救护车','手术',
            '健康','疾病','治疗','药','病','检查','诊断',
            '处方','药片','胶囊','针','输液','手术室',
        ],
        'meaning_starts': [
            'dokter','perawat','rumah sakit','klinik','apotek',
            'demam','flu','batuk','alergi','diabetes','kanker',
            'patah tulang','luka','pendarahan','tekanan darah',
            'vitamin','antibiotik','vaksin','rawat inap','ambulans',
            'operasi','kesehatan','penyakit','pengobatan','obat',
            'pemeriksaan','diagnosa','resep','suntikan','infus',
        ],
    },

    'pendidikan': {
        'label': 'Pendidikan & Sekolah',
        'exact_hanzi': [
            '学生','老师','教师','教授','同学','班','年级','学期',
            '学校','幼儿园','小学','中学','高中','大学','课本',
            '教材','教室','图书馆','实验室','操场','课','作业',
            '考试','成绩','毕业','入学','招生','报名','奖学金',
            '助学金','学费','班级','班主任','辅导','语文','数学',
            '英语','物理','化学','生物','历史','地理','体育',
            '上课','下课','复习','预习','期中考','期末考','高考',
        ],
        'meaning_starts': [
            'murid','siswa','guru','pengajar','profesor','teman sekelas',
            'kelas','semester','sekolah','taman kanak','sd','smp',
            'sma','universitas','buku teks','ruang kelas','perpustakaan',
            'laboratorium','lapangan','tugas','ujian','nilai','wisuda',
            'pendaftaran','beasiswa','biaya sekolah','matematika',
            'bahasa','fisika','kimia','biologi','sejarah','geografi',
        ],
    },

    'olahraga': {
        'label': 'Olahraga & Kebugaran',
        'exact_hanzi': [
            '运动','体育','锻炼','健身','比赛','竞赛','训练',
            '足球','篮球','排球','网球','乒乓球','羽毛球','棒球',
            '游泳','跑步','体操','瑜伽','武术','太极','跆拳道',
            '球','队','运动员','教练','裁判','守门员',
            '赢','输','得分','进球','冠军','金牌','银牌','铜牌',
            '奥运','世界杯','联赛','马拉松','举重','摔跤','拳击',
        ],
        'meaning_starts': [
            'olahraga','sepak bola','basket','voli','tenis','pingpong',
            'badminton','bisbol','renang','lari','senam','yoga',
            'bela diri','tai chi','taekwondo','tinju','angkat besi',
            'gulat','atlet','pelatih','wasit','juara','medali emas',
            'medali perak','medali perunggu','olimpiade','piala dunia',
            'liga','maraton','fitness','latihan','pertandingan',
        ],
    },

    'transportasi': {
        'label': 'Transportasi',
        'exact_hanzi': [
            '汽车','火车','地铁','公交','巴士','出租车','飞机',
            '轮船','自行车','摩托车','电动车','高铁','动车',
            '车站','机场','港口','码头','停车场','加油站',
            '公路','高速公路','铁路','驾驶','开车','骑车',
            '交通','运输','堵车','超速','事故','交通灯','红绿灯',
            '司机','乘客','车票','机票','船票','换乘','转乘',
        ],
        'meaning_starts': [
            'mobil','kereta','pesawat','kapal','sepeda','motor','bus',
            'taksi','subway','metro','stasiun','bandara','pelabuhan',
            'terminal','lalu lintas','mengemudi','berkendara','terbang',
            'berlayar','kemacetan','kecelakaan','lampu merah','sopir',
            'penumpang','tiket','transportasi','kendaraan',
        ],
    },

    'teknologi': {
        'label': 'Teknologi & Sains',
        'exact_hanzi': [
            '电脑','手机','网络','网','互联网','软件','硬件','系统',
            '程序','算法','数据','人工智能','机器人','自动化',
            '云计算','大数据','芯片','处理器','内存','存储','电池',
            '太阳能','核能','实验室','研发','专利','卫星',
            '科技','技术','科学','研究','发明','创新','数字','智能',
        ],
        'meaning_starts': [
            'komputer','ponsel','internet','jaringan','perangkat lunak',
            'perangkat keras','sistem','program','algoritma','data',
            'kecerdasan buatan','robot','otomasi','cloud','chip',
            'prosesor','memori','penyimpanan','baterai','energi surya',
            'nuklir','laboratorium','paten','satelit','teknologi',
            'sains','penelitian','penemuan','inovasi','digital',
        ],
    },

    'alam_lingkungan': {
        'label': 'Alam & Lingkungan',
        'exact_hanzi': [
            '山','河','海','湖','树','花','草','石','土地','森林',
            '丛林','草原','沙漠','平原','高原','大海','大洋','海湾',
            '岛屿','山峰','山谷','瀑布','泉水','植物','生态','自然',
            '地球','污染','保护','绿化','可持续','太阳','月亮',
            '星星','天空','云','闪电','彩虹','风','雨','雪','雾',
            '冰','岩石','土壤','空气','大气','臭氧','生物','物种',
        ],
        'meaning_starts': [
            'gunung','sungai','laut','danau','pohon','bunga','rumput',
            'batu','tanah','hutan','padang rumput','gurun','pulau',
            'puncak','lembah','air terjun','mata air','ekologi',
            'alam','bumi','polusi','perlindungan','penghijauan',
            'matahari','bulan','bintang','langit','awan','petir',
            'pelangi','angin','hujan','salju','kabut','es','udara',
        ],
    },

    'cuaca': {
        'label': 'Cuaca & Musim',
        'exact_hanzi': [
            '天气','气候','温度','湿度','风速','晴天','阴天','下雨',
            '下雪','起雾','结冰','春天','夏天','秋天','冬天',
            '春季','夏季','秋季','冬季','梅雨季','台风','暴雨',
            '大雨','小雨','阵雨','雷雨','冰雹','沙尘暴','高温',
            '低温','零度','寒冷','炎热','凉爽','温暖','干燥','潮湿',
            '天气预报','气象','气温','最高气温','最低气温',
        ],
        'meaning_starts': [
            'cuaca','iklim','suhu','kelembaban','kecepatan angin',
            'cerah','mendung','hujan','salju','kabut','beku',
            'musim semi','musim panas','musim gugur','musim dingin',
            'topan','badai','hujan lebat','hujan ringan','petir',
            'hail','badai pasir','panas','dingin','sejuk','hangat',
            'kering','lembab','prakiraan cuaca','meteorologi',
        ],
    },

    'perjalanan_wisata': {
        'label': 'Perjalanan & Wisata',
        'exact_hanzi': [
            '旅游','旅行','出游','景点','景区','名胜','酒店','宾馆',
            '旅馆','客栈','民宿','签证','护照','机票','火车票',
            '导游','旅行社','海外','出国','入境','海关','边检',
            '行李','行李箱','登机牌','安检','候机','纪念品','特产',
        ],
        'meaning_starts': [
            'wisata','perjalanan liburan','hotel','penginapan','hostel',
            'visa','paspor','tiket pesawat','tiket kereta',
            'pemandu wisata','agen perjalanan','luar negeri','imigrasi',
            'koper','boarding pass','pemeriksaan keamanan','oleh-oleh',
        ],
    },

    'komunikasi': {
        'label': 'Komunikasi & Media',
        'exact_hanzi': [
            '电话','手机','电脑','信','消息','通话','打电话','发短信',
            '视频','语音','微信','电邮','邮件','信件','信封','邮票',
            '快递','包裹','电视','广播','新闻','媒体','社交','网站',
            '充电','信号','下载','上传','密码','账号','注册','登录',
        ],
        'meaning_starts': [
            'telepon','ponsel','komputer','pesan','menelepon','sms',
            'video call','suara','email','surat','amplop','paket',
            'kurir','televisi','siaran','berita','media','sosial',
            'website','baterai','sinyal','unduh','unggah','kata sandi',
            'akun','daftar','masuk','aplikasi',
        ],
    },

    'rumah_ruangan': {
        'label': 'Rumah & Ruangan',
        'exact_hanzi': [
            '房间','卧室','客厅','厨房','卫生间','浴室','阳台',
            '走廊','大厅','车库','楼梯','电梯','公寓','别墅','宿舍',
            '床','桌子','椅子','沙发','柜子','灯','空调','冰箱',
            '洗衣机','电视','书架','衣柜','茶几','餐桌','书桌',
            '门','窗','墙','地板','天花板','屋顶','楼层',
            '房租','物业','装修','家具','家电','家居',
        ],
        'meaning_starts': [
            'kamar','ruang tamu','dapur','kamar mandi','kamar tidur',
            'balkon','koridor','aula','garasi','tangga','lift',
            'apartemen','vila','asrama','tempat tidur','meja','kursi',
            'sofa','lemari','lampu','ac','kulkas','mesin cuci',
            'pintu','jendela','dinding','lantai','atap','furnitur',
            'sewa','renovasi','dekorasi',
        ],
    },

    'pekerjaan': {
        'label': 'Pekerjaan & Profesi',
        'exact_hanzi': [
            '工作','职业','上班','下班','加班','工资','薪水','奖金',
            '合同','简历','面试','招聘','辞职','解雇','退休','出差',
            '医生','护士','老师','工程师','律师','会计','程序员',
            '警察','消防员','军人','公务员','经理','总裁','员工',
            '职员','工人','农民','商人','服务员','司机','厨师',
            '设计师','建筑师','记者','编辑','作家','艺术家','歌手',
            '演员','运动员','裁判','教练','职位','岗位','部门',
        ],
        'meaning_starts': [
            'pekerjaan','profesi','kerja','kantor','gaji','upah','bonus',
            'kontrak','lamaran','wawancara','rekrutmen','pensiun',
            'dokter','perawat','guru','insinyur','pengacara','akuntan',
            'programmer','polisi','pemadam','tentara','pegawai negeri',
            'manajer','direktur','karyawan','pegawai','pekerja','petani',
            'pedagang','sopir','koki','desainer','arsitek','jurnalis',
            'penulis','seniman','penyanyi','aktor','atlet','jabatan',
        ],
    },

    'belanja': {
        'label': 'Belanja & Perdagangan',
        'exact_hanzi': [
            '商店','超市','百货','商场','市场','专卖店','网店',
            '价格','定价','优惠价','特价','打折','折扣','优惠券',
            '收银台','购物车','购物袋','小票','发票','收据',
            '现金','信用卡','支付宝','微信支付','刷卡',
            '退货','换货','保修','售后','品质',
        ],
        'meaning_starts': [
            'toko','supermarket','pasar','mal','department store',
            'toko online','harga','diskon','kupon','kasir',
            'keranjang belanja','struk','faktur','kuitansi',
            'tunai','kartu kredit','dompet digital','gesek kartu',
            'refund','garansi','kualitas','layanan purna jual',
        ],
    },

    'seni_budaya': {
        'label': 'Seni & Budaya',
        'exact_hanzi': [
            '艺术','文化','音乐','绘画','书法','雕塑','建筑','文学',
            '小说','诗歌','散文','戏剧','电影','动画','漫画',
            '唱歌','跳舞','演奏','表演','展览','博物馆','美术馆',
            '钢琴','小提琴','吉他','二胡','笛子','古筝','鼓',
            '传统文化','民俗','风俗','习俗','礼仪','历史','遗产',
        ],
        'meaning_starts': [
            'seni','budaya','musik','lukisan','kaligrafi','patung',
            'sastra','novel','puisi','prosa','drama','film','animasi',
            'komik','menyanyi','menari','bermain musik','pertunjukan',
            'pameran','museum','galeri seni','piano','biola','gitar',
            'tradisional','adat','kebiasaan','sejarah','warisan budaya',
        ],
    },

    'hobi_hiburan': {
        'label': 'Hobi & Hiburan',
        'exact_hanzi': [
            '爱好','兴趣','娱乐','游戏','棋','牌','摄影','烹饪',
            '园艺','钓鱼','登山','阅读','漫画','直播','短视频',
        ],
        'meaning_starts': [
            'hobi','minat','hiburan','permainan','bermain game','catur',
            'kartu','fotografi','memasak','berkebun','memancing',
            'pendakian gunung','membaca buku','komik','livestream',
        ],
    },

    'perasaan_emosi': {
        'label': 'Perasaan & Emosi',
        'exact_hanzi': [
            '高兴','快乐','开心','幸福','满意','骄傲','自豪',
            '伤心','难过','悲伤','痛苦','绝望','沮丧','失望',
            '生气','愤怒','委屈','怨恨','恼火','愤慨',
            '害怕','恐惧','担心','焦虑','紧张','不安','恐慌',
            '惊喜','惊讶','好奇','兴奋','激动','感动',
            '孤独','寂寞','思念','想念','爱','恨','喜欢','讨厌',
            '同情','羡慕','嫉妒','感谢','感激','抱歉','后悔',
            '心情','情绪','感情','感觉','情感','心理',
        ],
        'meaning_starts': [
            'senang','bahagia','gembira','puas','bangga','sedih',
            'menangis','menderita','putus asa','kecewa','marah',
            'kesal','benci','dendam','takut','panik','cemas','khawatir',
            'gelisah','terkejut','penasaran','bersemangat','terharu',
            'kesepian','rindu','cinta','suka','tidak suka','iri',
            'cemburu','berterima kasih','menyesal','perasaan','emosi',
        ],
    },

    'keuangan': {
        'label': 'Keuangan & Perbankan',
        'exact_hanzi': [
            '银行','存款','取款','汇款','贷款','借款','还款',
            '账户','信用卡','借记卡','银行卡','利率','利息',
            '汇率','外汇','股票','基金','债券','证券','理财',
            '保险','医保','社保','养老金','公积金',
            '税','纳税','通货膨胀','储蓄','预算','财务','收支',
        ],
        'meaning_starts': [
            'bank','tabungan','penarikan','transfer','pinjaman','kredit',
            'rekening','kartu kredit','kartu debit','suku bunga',
            'bunga','nilai tukar','valuta asing','saham','reksa dana',
            'obligasi','investasi','asuransi','bpjs','pensiun',
            'pajak','inflasi','anggaran','keuangan','menabung',
        ],
    },

    'negara_budaya': {
        'label': 'Negara & Kebudayaan',
        'exact_hanzi': [
            '中国','美国','日本','韩国','英国','法国','德国','俄国',
            '印度','印尼','泰国','越南','马来西亚','新加坡','澳大利亚',
            '非洲','欧洲','亚洲','美洲','大洋洲',
            '民族','国籍','文化','语言','宗教','传统','习俗',
            '华人','华侨','移民','留学生','外国人','外籍','国旗',
        ],
        'meaning_starts': [
            'tiongkok','china','amerika serikat','jepang','korea',
            'inggris','prancis','jerman','rusia','india','indonesia',
            'thailand','vietnam','singapura','australia','eropa','asia',
            'afrika','bangsa','kebangsaan','budaya','bahasa','agama',
            'tradisi','diaspora','imigran','pelajar asing',
        ],
    },

    'arah_lokasi': {
        'label': 'Arah & Lokasi',
        'exact_hanzi': [
            '东','西','南','北','东边','西边','南边','北边',
            '左边','右边','前面','后面','上面','下面','中间',
            '附近','周围','旁边','对面','斜对面','中央','中心',
            '东方','西方','南方','北方','东南','东北','西南','西北',
            '顶部','底部','上方','下方','左方','右方','侧面',
        ],
        'meaning_starts': [
            'timur','barat','selatan','utara','kiri','kanan',
            'depan','belakang','atas','bawah','tengah','di dekat',
            'sekitar','di samping','berseberangan','pusat',
            'tenggara','timur laut','barat daya','barat laut',
        ],
    },

    'pemerintahan_hukum': {
        'label': 'Pemerintahan & Hukum',
        'exact_hanzi': [
            '政府','法律','法规','政策','宪法','刑法','民法',
            '法院','检察院','公安局','警察局','监狱','法官','律师',
            '总统','主席','总理','部长','省长','市长','议会',
            '选举','投票','民主','税收','外交','条约','协议',
            '公民','权利','义务','户籍','身份证','宪政',
        ],
        'meaning_starts': [
            'pemerintah','hukum','peraturan','kebijakan','konstitusi',
            'pengadilan','jaksa','kepolisian','penjara','hakim',
            'pengacara','presiden','perdana menteri','menteri',
            'gubernur','walikota','parlemen','pemilu','demokrasi',
            'pajak','diplomasi','perjanjian','warga negara',
            'hak','kewajiban','ktp',
        ],
    },

    'bisnis_perdagangan': {
        'label': 'Bisnis & Perdagangan',
        'exact_hanzi': [
            '公司','集团','品牌','产品','服务','市场','竞争',
            '合同','谈判','签约','利润','亏损','收入','支出',
            '投资','融资','上市','进口','出口','关税','配额',
            '销售','营销','推广','广告','代理','经销商',
            '客户','顾客','消费者','供应商','合作伙伴',
        ],
        'meaning_starts': [
            'perusahaan','korporasi','konglomerat','merek','produk',
            'layanan','pasar','persaingan','kontrak','negosiasi',
            'transaksi','laba','rugi','pendapatan','pengeluaran',
            'investasi','saham','go public','ekspor','impor',
            'bea cukai','penjualan','pemasaran','iklan','agen',
            'pelanggan','konsumen','pemasok','mitra bisnis',
        ],
    },

    'sifat_deskripsi': {
        'label': 'Sifat & Deskripsi Umum',
        'exact_hanzi': [
            '大','小','高','低','长','短','宽','窄','粗','细',
            '厚','薄','重','轻','快','慢','新','旧','好','坏',
            '美','丑','强','弱','聪明','笨','勤劳','懒','认真',
            '诚实','热情','冷漠','友好','善良','凶狠','温柔','粗鲁',
            '干净','脏','整齐','乱','积极','消极','复杂','简单',
            '重要','普通','特殊','一般','常见','罕见','奇怪',
            '清楚','模糊','正确','错误','准确','精确',
        ],
        'meaning_starts': [
            'besar','kecil','tinggi','rendah','panjang','pendek',
            'lebar','sempit','tebal','tipis','berat','ringan',
            'cepat','lambat','baru','lama','bagus','buruk','indah',
            'jelek','kuat','lemah','cerdas','bodoh','rajin','malas',
            'jujur','ramah','baik hati','jahat','lembut','kasar',
            'bersih','kotor','rapi','berantakan','positif','negatif',
            'kompleks','sederhana','sulit','mudah','penting','umum',
            'khusus','aneh','jelas','benar','salah','akurat',
        ],
    },

    'pertanian_pangan': {
        'label': 'Pertanian & Pangan',
        'exact_hanzi': [
            '农业','农村','农民','农田','耕地','播种','种植',
            '水稻','小麦','玉米','大豆','棉花','茶叶','甘蔗',
            '收获','丰收','粮食','农产品','化肥','农药','灌溉',
            '牧场','畜牧','养殖','渔业','捕鱼','水产','农场',
        ],
        'meaning_starts': [
            'pertanian','pedesaan','petani','sawah','ladang',
            'menanam','memanen','padi','gandum','jagung','kedelai',
            'kapas','teh','gula tebu','panen raya','beras','pupuk',
            'pestisida','irigasi','peternakan','perikanan',
            'ketahanan pangan','ladang','kebun',
        ],
    },

    'lingkungan_hidup': {
        'label': 'Lingkungan Hidup',
        'exact_hanzi': [
            '污染','排放','废气','废水','垃圾','回收','节能','减排',
            '碳排放','温室气体','全球变暖','可持续','绿色能源',
            '太阳能','风能','水能','核能','新能源','电动车',
            '濒危','灭绝','生物多样性','生态系统','保护区',
        ],
        'meaning_starts': [
            'polusi','emisi','gas buang','limbah cair','sampah',
            'daur ulang','hemat energi','pengurangan emisi',
            'karbon','gas rumah kaca','pemanasan global',
            'berkelanjutan','energi terbarukan','energi surya',
            'energi angin','nuklir','kendaraan listrik',
            'terancam punah','punah','keanekaragaman hayati',
        ],
    },

    'agama_kepercayaan': {
        'label': 'Agama & Kepercayaan',
        'exact_hanzi': [
            '宗教','信仰','佛教','道教','儒教','基督教','伊斯兰教',
            '寺庙','庙宇','教堂','清真寺','神社',
            '神','佛','菩萨','上帝','真主','耶稣','孔子',
            '信徒','教徒','僧侣','和尚','尼姑','牧师','神父','阿訇',
            '祈祷','礼拜','冥想','打坐','斋戒',
            '天堂','地狱','灵魂','轮回','因果','缘分','命运',
        ],
        'meaning_starts': [
            'agama','kepercayaan','buddha','buddhisme','taoisme',
            'konfusianisme','kristen','islam','kuil','masjid','gereja',
            'tuhan','allah','yesus','konfusius','biksu','biksuni',
            'pendeta','imam','berdoa','ibadah','meditasi','puasa',
            'surga','neraka','jiwa','reinkarnasi','karma','takdir',
        ],
    },

    'konstruksi_teknik': {
        'label': 'Konstruksi & Teknik',
        'exact_hanzi': [
            '建筑','建设','施工','工程','结构','设计','规划',
            '砖','混凝土','钢铁','木材','玻璃','塑料',
            '道路','桥梁','隧道','水坝','工厂','仓库',
        ],
        'meaning_starts': [
            'konstruksi','bangunan','pembangunan','teknik','struktur',
            'desain arsitektur','perencanaan','bata','beton','baja',
            'kayu bangunan','kaca','plastik','jalan raya','jembatan',
            'terowongan','bendungan','pabrik','gudang',
        ],
    },

    'tekstil_fashion': {
        'label': 'Tekstil & Mode',
        'exact_hanzi': [
            '布','丝','棉','麻','毛','皮','绸','缎','绒','纱',
            '纺织','面料','材质','质地','花纹','图案','时尚','流行',
            '裁缝','缝纫','刺绣','印染','纺纱','编织',
        ],
        'meaning_starts': [
            'kain','sutra','katun','linen','wol','kulit binatang',
            'satin','beludru','tekstil','bahan kain','motif','pola',
            'mode','tren fashion','penjahit','jahitan','sulam','tenun',
        ],
    },

    'pendidikan_tinggi': {
        'label': 'Pendidikan Tinggi',
        'exact_hanzi': [
            '大学','学院','研究生','博士','硕士','本科','专科',
            '教授','副教授','讲师','导师','论文','毕业论文',
            '答辩','专业','学分','成绩单','学位','文凭',
            '奖学金','助学金','学费','食堂','学术','科研',
            '院系','系','院长','系主任','学生会',
        ],
        'meaning_starts': [
            'universitas','perguruan tinggi','pascasarjana',
            'program doktor','program magister','sarjana','diploma',
            'profesor','dosen senior','dosen','pembimbing',
            'skripsi','tesis','disertasi','sidang','jurusan','sks',
            'transkrip','gelar','beasiswa','biaya kuliah','kantin',
            'akademis','riset','departemen','dekan','ketua jurusan',
        ],
    },
}

# ════════════════════════════════════════════════════════════
# PROSES: Cari kata kandidat dari app_words.json
# ════════════════════════════════════════════════════════════

sep("Mencari kandidat kata per tema")

for tema_key, rule in TEMA_SEEDS.items():
    exact_set = set(rule.get('exact_hanzi', []))
    meaning_starts_kw = rule.get('meaning_starts', [])

    candidates = []
    for w in words:
        simp = w.get('simplified', '')
        first_meaning = get_first_meaning(w)

        # Cek 1: exact hanzi match
        if simp in exact_set:
            candidates.append((simp, 'hanzi', first_meaning[:50]))
            continue

        # Cek 2: arti DIMULAI dengan keyword (sangat ketat)
        if starts_with_any(first_meaning, meaning_starts_kw):
            candidates.append((simp, 'meaning', first_meaning[:50]))

    sep(f"  TEMA: {rule['label']} — {len(candidates)} kandidat")
    for simp, src, meaning in candidates:
        log(f"    [{src}]  {simp:<10} {meaning}")

# Simpan
with open(OUT_REPORT, "w", encoding="utf-8") as f:
    f.write("\n".join(lines))
print(f"\n✅ Selesai! Buka: {OUT_REPORT}")

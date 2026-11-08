#!/usr/bin/env python3
# fix_tema_final.py
# Rebuild field 'themes' menggunakan PURE HANZI WHITELIST
# Tidak ada keyword/meaning matching — 100% akurat dan terkontrol
# Jalankan: python fix_tema_final.py

import json, os
from collections import defaultdict

DATA_DIR   = r"C:\mandarin_app\data"
IN_WORDS   = os.path.join(DATA_DIR, "app_words.json")
OUT_WORDS  = os.path.join(DATA_DIR, "app_words.json")
OUT_THEME  = os.path.join(DATA_DIR, "index_theme.json")
OUT_REPORT = os.path.join(DATA_DIR, "LAPORAN_FIX_TEMA_FINAL.txt")

lines = []
def log(s=""):
    print(s)
    lines.append(str(s))

def sep(title=""):
    log("\n" + "═"*60)
    log(f"  {title}")
    log("═"*60)

# ════════════════════════════════════════════════════════════
# PURE WHITELIST — setiap hanzi dikurasi manual
# Sumber: KANDIDAT_TEMA.txt (filtered noise)
# ════════════════════════════════════════════════════════════

TEMA_WHITELIST = {

    'warna': {
        'label_id': 'Warna',
        'label_zh': '颜色',
        'words': [
            # Warna dasar
            '红','橙','黄','绿','蓝','紫','黑','白','灰','粉',
            '棕','褐','金','银','青','靛','朱','赤','绛','碧',
            '翠','茜',
            # Warna + 色
            '红色','橙色','黄色','绿色','蓝色','紫色','黑色','白色',
            '灰色','粉色','粉红','棕色','金色','银色','青色','彩色',
            # Kata terkait warna
            '颜色','色彩','色','五彩','彩虹','五颜六色','翠绿','碧绿',
            '朱红','乌黑','黑白','红扑扑','气色','玄',
            # Warna gabungan yang ada di HSK
            '深红','浅蓝','墨绿','米色','深蓝','淡黄','深色','浅色',
            '黄金',
        ],
    },

    'keluarga': {
        'label_id': 'Keluarga',
        'label_zh': '家庭',
        'words': [
            # Anggota keluarga inti
            '爸','妈','父','母','兄','弟','姐','妹','子','女',
            '祖','孙','夫','妻','婆','公','舅','姑','叔','伯','婶','侄',
            '爸爸','妈妈','父亲','母亲','儿子','女儿','兄弟','姐妹',
            '祖父','祖母','爷爷','奶奶','外公','外婆','孙子','孙女',
            '丈夫','妻子','老公','老婆','夫妻','夫妇','婆婆','公公',
            # Kerabat lebih jauh
            '舅舅','舅妈','姑姑','姑父','叔叔','阿姨','伯伯','伯母',
            '侄子','侄女','外甥','亲戚','家人','家庭','家属','子女',
            '双亲','儿媳','女婿','继父','继母','养父','养母','家长',
            '孤儿','寡妇','家族','亲人','长辈','晚辈',
            # Dari kandidat
            '哥','姐姐','哥哥','妹妹','弟弟','父母','父子','大哥',
            '大姐','大妈','母女','母子','父女','岳父','岳母','两口子',
            '媳妇','主妇','门当户对','大家庭','姨','爹','娘',
            '伯父','姥爷',
        ],
    },

    'hewan': {
        'label_id': 'Hewan & Binatang',
        'label_zh': '动物',
        'words': [
            # Hewan umum
            '狗','猫','鸟','鱼','马','牛','羊','猪','鸡','鸭','鹅',
            '兔','鼠','虎','狮','象','熊','猴','蛇','龙','凤','鹤',
            '鹰','燕','蝶','蜂','虫','蚊','蝇','蚂蚁','蟑螂',
            '狼','狐','鹿','豹','豹子','熊猫','大熊猫','老虎','狮子',
            '大象','长颈鹿','河马','犀牛','斑马','猩猩','海豚','鲸鱼',
            '鲨鱼','章鱼','螃蟹','龙虾','蜗牛','青蛙','乌龟','蜥蜴',
            '壁虎','蝙蝠','松鼠','刺猬','仙鹤','金鱼','鹦鹉','孔雀',
            '企鹅','鸵鸟','猫头鹰',
            # Kategori hewan
            '动物','野生动物','宠物','家禽','家畜','昆虫','爬虫',
            '哺乳动物','鸟类','两栖动物',
            # Dari kandidat (bersih)
            '老鼠','犬','兔子','猴子','蝴蝶','蜜蜂','鸭子','龟',
            '野兽','奶牛','蚊子','牲畜','公鸡','母鸡','黑马',
            '鲤鱼','草鱼','鲫鱼','带鱼','黄鱼',
        ],
    },

    'buah': {
        'label_id': 'Buah-buahan',
        'label_zh': '水果',
        'words': [
            '苹果','香蕉','橙','橙子','桔子','橘子','葡萄','草莓',
            '西瓜','哈密瓜','芒果','菠萝','柠檬','桃','桃子','梨',
            '李子','杏','杏子','樱桃','荔枝','龙眼','椰子','榴莲',
            '木瓜','火龙果','猕猴桃','蓝莓','石榴','柚子','柿子',
            '枣','枇杷','山楂','无花果','杨梅','桑葚','水果',
            '果汁','果肉','果皮','果核',
        ],
    },

    'sayuran': {
        'label_id': 'Sayuran',
        'label_zh': '蔬菜',
        'words': [
            '蔬菜','白菜','青菜','菠菜','芹菜','韭菜','生菜',
            '卷心菜','花椰菜','西兰花','萝卜','胡萝卜','土豆','马铃薯',
            '红薯','地瓜','洋葱','大葱','葱','蒜','大蒜','姜','辣椒',
            '西红柿','番茄','黄瓜','茄子','南瓜','苦瓜','冬瓜',
            '豆角','四季豆','豌豆','蘑菇','香菇','木耳','海带',
            '豆芽','竹笋','莲藕','百合','山药',
            # catatan: 菜 sendiri terlalu umum, skip
        ],
    },

    'makanan_minuman': {
        'label_id': 'Makanan & Minuman',
        'label_zh': '食物饮料',
        'words': [
            # Makanan pokok
            '米饭','面条','面包','蛋糕','饼干','点心','小吃','零食',
            '早饭','午饭','晚饭','早餐','午餐','晚餐','宵夜',
            '饺子','包子','馒头','汤圆','粽子','月饼','烤鸭','火锅',
            '炒饭','炒菜','烧烤','麻辣烫','面','粥','汤','饭',
            # Protein
            '牛肉','猪肉','鸡肉','鸭肉','羊肉','海鲜','虾','蟹',
            '豆腐','鸡蛋','咸鱼','香肠','火腿','腊肉',
            # Minuman
            '水','茶','酒','牛奶','果汁','咖啡','可乐','啤酒',
            '白酒','红酒','矿泉水','豆浆','酸奶','奶茶','饮料',
            # Bumbu & lainnya
            '酱油','醋','盐','糖','辣椒','大蒜','姜','调料','香料',
            # Kata umum
            '食物','食品','美食','菜单','套餐','外卖','营养','热量',
        ],
    },

    'tubuh': {
        'label_id': 'Tubuh Manusia',
        'label_zh': '身体',
        'words': [
            # Bagian kepala
            '头','脸','眼','眼睛','耳','耳朵','鼻','鼻子','口','嘴',
            '嘴巴','牙','牙齿','舌','舌头','脖','颈','脖子',
            '头发','眉毛','睫毛','嘴唇','下巴','额头','太阳穴',
            # Badan
            '肩','肩膀','臂','手臂','手','手指','胸','腹','肚子',
            '背','腰','臀','腿','膝','膝盖','脚','脚趾',
            # Organ dalam
            '皮肤','骨头','肌肉','血','心脏','肺','肝','肾','胃',
            '肠','大脑','脑','神经','喉咙','食道','气管',
            '关节','脊椎','肋骨','手腕','脚踝',
            # Konsep tubuh
            '身体','体重','身高','体温','血压','血型','血糖',
        ],
    },

    'pakaian': {
        'label_id': 'Pakaian & Aksesori',
        'label_zh': '服装',
        'words': [
            # Pakaian atas
            '衬衫','上衣','毛衣','T恤','外套','大衣','风衣','羽绒服',
            '皮衣','夹克','西装','礼服','制服','校服','运动服','睡衣',
            # Bawahan & gaun
            '裤子','牛仔裤','短裤','裙子','连衣裙','内衣',
            # Alas kaki
            '鞋子','皮鞋','运动鞋','高跟鞋','拖鞋','靴子','袜子',
            # Aksesori
            '帽子','围巾','手套','领带','皮带','腰带',
            '手提包','背包','钱包','眼镜','手表','项链','耳环',
            '戒指','手镯',
            # Kata umum
            '衣服','时装','尺码','服装','穿着','着装',
        ],
    },

    'angka': {
        'label_id': 'Angka & Bilangan',
        'label_zh': '数字',
        'words': [
            '零','一','二','三','四','五','六','七','八','九','十',
            '百','千','万','亿','两','半',
            # Urutan & konsep angka
            '第','数','数字','数量','数目','号','码','编号','序号',
            '奇数','偶数','整数','小数','分数','百分','百分之',
            '倍','双','单','总数','合计','总共',
        ],
    },

    'waktu': {
        'label_id': 'Waktu & Jam',
        'label_zh': '时间',
        'words': [
            '小时','分钟','秒','时间','时刻','时候',
            '上午','下午','中午','凌晨','早上','晚上','傍晚','黄昏',
            '午夜','半夜','清晨','正午',
            '整点','时区','当地时间',
            # Karakter tunggal yang ambigu dihilangkan (时,分,秒,钟,点,刻)
            # karena bisa berarti banyak hal
        ],
    },

    'hari_tanggal': {
        'label_id': 'Hari, Bulan & Tanggal',
        'label_zh': '日期',
        'words': [
            # Hari relatif
            '今天','昨天','明天','后天','前天',
            '今年','去年','明年','上周','下周','本周','这周',
            '上个月','下个月','本月',
            # Hari dalam seminggu
            '星期一','星期二','星期三','星期四','星期五','星期六',
            '星期日','星期天','周一','周二','周三','周四','周五',
            '周六','周日','周末','工作日',
            # Bulan
            '一月','二月','三月','四月','五月','六月',
            '七月','八月','九月','十月','十一月','十二月',
            # Hari besar
            '元旦','春节','清明','端午','中秋','国庆','元宵',
            '节日','假日','假期','节假日',
            # Konsep waktu
            '日期','年份','年代','世纪','季节','月份',
        ],
    },

    'kesehatan': {
        'label_id': 'Kesehatan & Medis',
        'label_zh': '健康医疗',
        'words': [
            # Tenaga medis & fasilitas
            '医生','护士','医院','诊所','药房','药店','急诊室',
            # Gejala & penyakit
            '感冒','发烧','头痛','肚子痛','咳嗽','过敏','糖尿病',
            '高血压','心脏病','癌症','骨折','受伤','伤口','出血',
            '失眠','近视','发炎','中毒','晕倒','昏迷',
            # Pengukuran kesehatan
            '血压','血糖','体温','心率','呼吸','脉搏',
            # Obat & tindakan medis
            '药','维生素','抗生素','止痛药','消炎药','疫苗','注射',
            '手术','住院','急救','救护车','挂号','就诊','处方',
            # Kata umum
            '健康','疾病','治疗','检查','诊断','康复','保健',
        ],
    },

    'pendidikan': {
        'label_id': 'Pendidikan & Sekolah',
        'label_zh': '教育',
        'words': [
            # Orang
            '学生','老师','教师','教授','同学','班主任',
            # Tingkat sekolah
            '学校','幼儿园','小学','中学','高中','大学',
            # Fasilitas
            '教室','图书馆','实验室','操场','食堂',
            # Kegiatan belajar
            '课','上课','下课','作业','复习','预习','辅导',
            '课本','教材',
            # Penilaian
            '考试','成绩','考查','测验','期中考','期末考','高考',
            # Mata pelajaran
            '语文','数学','英语','物理','化学','生物','历史','地理',
            # Lainnya
            '毕业','入学','招生','报名','奖学金','助学金','学费',
            '班级','年级','学期',
        ],
    },

    'pekerjaan': {
        'label_id': 'Pekerjaan & Profesi',
        'label_zh': '职业工作',
        'words': [
            # Aktivitas kerja
            '工作','上班','下班','加班','出差','请假',
            # Kompensasi
            '工资','薪水','奖金','福利',
            # Proses kerja
            '合同','简历','面试','招聘','辞职','解雇','退休',
            # Profesi
            '医生','护士','老师','工程师','律师','会计','程序员',
            '警察','消防员','军人','公务员','经理','总裁','总经理',
            '员工','职员','工人','农民','商人','服务员','司机',
            '厨师','设计师','建筑师','记者','编辑','作家',
            '艺术家','歌手','演员','运动员','裁判','教练',
            # Konsep pekerjaan
            '职业','职位','岗位','部门','职务',
        ],
    },

    'transportasi': {
        'label_id': 'Transportasi',
        'label_zh': '交通运输',
        'words': [
            # Kendaraan darat
            '汽车','火车','地铁','公交','巴士','出租车','高铁','动车',
            '城铁','轻轨','自行车','摩托车','电动车','滑板车',
            # Kendaraan udara & air
            '飞机','直升机','轮船','邮轮','渡船',
            # Fasilitas transportasi
            '车站','机场','港口','码头','停车场','加油站',
            # Infrastruktur
            '公路','高速公路','铁路',
            # Aktivitas
            '驾驶','开车','骑车','乘坐','搭车','换乘','转乘',
            # Masalah & lainnya
            '堵车','塞车','超速','事故','交通灯','红绿灯',
            '司机','乘客','车票','机票','船票',
            # Kata umum
            '交通','运输',
        ],
    },

    'olahraga': {
        'label_id': 'Olahraga & Kebugaran',
        'label_zh': '体育运动',
        'words': [
            # Cabang olahraga
            '足球','篮球','排球','网球','乒乓球','羽毛球','棒球',
            '游泳','跑步','体操','瑜伽','武术','太极','跆拳道',
            '功夫','举重','摔跤','拳击','马拉松','铁人三项',
            # Kompetisi & hasil
            '比赛','竞赛','训练','锻炼','健身',
            '赢','输','得分','进球','冠军','金牌','银牌','铜牌',
            # Orang & institusi
            '运动员','教练','裁判','守门员','队',
            '奥运','世界杯','联赛',
            # Kata umum
            '运动','体育',
        ],
    },

    'belanja': {
        'label_id': 'Belanja & Perdagangan',
        'label_zh': '购物',
        'words': [
            # Tempat belanja
            '商店','超市','百货','商场','市场','专卖店','网店',
            # Harga & promosi
            '价格','价钱','定价','标价','售价','优惠价','特价',
            '打折','折扣','优惠券','满减','返现','积分','促销',
            # Proses transaksi
            '收银台','购物车','购物袋','小票','发票','收据',
            '现金','信用卡','支付宝','微信支付','刷卡',
            # Purna jual
            '退货','换货','保修','售后','质量','品质',
        ],
    },

    'komunikasi': {
        'label_id': 'Komunikasi & Media',
        'label_zh': '通讯媒体',
        'words': [
            # Alat komunikasi
            '电话','手机','电脑',
            # Aktivitas komunikasi
            '打电话','发短信','发消息','通话','视频','语音',
            # Platform & aplikasi
            '微信','电邮','网站',
            # Surat fisik
            '邮件','信件','信封','邮票','快递','包裹',
            # Media
            '电视','广播','新闻','媒体','社交',
            # Internet
            '网络','网','互联网','充电','信号','下载','上传',
            'wifi','蓝牙','数据','流量',
            # Akun
            '密码','账号','注册','登录','搜索','浏览',
            # Kata umum
            '消息','通讯','信息',
        ],
    },

    'rumah_ruangan': {
        'label_id': 'Rumah & Ruangan',
        'label_zh': '家居',
        'words': [
            # Ruangan
            '卧室','客厅','厨房','卫生间','浴室','阳台',
            '走廊','大厅','车库','地下室','阁楼','楼梯',
            # Jenis hunian
            '公寓','别墅','宿舍','楼房','平房',
            # Perabot
            '床','桌子','椅子','沙发','柜子','灯','书架',
            '衣柜','鞋柜','茶几','餐桌','书桌',
            # Peralatan rumah
            '空调','冰箱','洗衣机','电视','洗碗机','微波炉',
            # Bagian bangunan
            '门','窗','墙','地板','天花板','屋顶','楼层','电梯',
            # Konsep
            '房租','物业','装修','家具','家电','家居','房间',
        ],
    },

    'alam_lingkungan': {
        'label_id': 'Alam & Lingkungan',
        'label_zh': '自然环境',
        'words': [
            # Bentang alam
            '山','河','海','湖','森林','丛林','草原','沙漠',
            '平原','高原','盆地','大海','大洋','海湾','海峡',
            '半岛','岛屿','礁石','山峰','山谷','山坡','悬崖',
            '瀑布','泉水',
            # Tumbuhan
            '树','花','草','植物',
            # Bumi & langit
            '石','土地','太阳','月亮','星星','天空','云',
            '闪电','彩虹','土壤','空气','大气','臭氧',
            # Makhluk hidup
            '生态','自然','地球','生物','物种','生物多样性',
            # Perlindungan
            '污染','保护','绿化',
        ],
    },

    'cuaca': {
        'label_id': 'Cuaca & Musim',
        'label_zh': '天气季节',
        'words': [
            # Kata cuaca
            '天气','气候','温度','湿度','气压','风速',
            '天气预报','气象','气温','最高气温','最低气温',
            # Kondisi cuaca
            '晴天','阴天','下雨','下雪','起雾','结冰',
            '台风','暴雨','大雨','小雨','中雨','阵雨','雷雨',
            '冰雹','沙尘暴','高温','低温',
            # Musim
            '春天','夏天','秋天','冬天','春季','夏季','秋季','冬季',
            '梅雨季',
            # Deskripsi cuaca
            '寒冷','炎热','凉爽','温暖','干燥','潮湿',
            '晴','阴',
        ],
    },

    'perjalanan_wisata': {
        'label_id': 'Perjalanan & Wisata',
        'label_zh': '旅游出行',
        'words': [
            # Aktivitas wisata
            '旅游','旅行','出游','出发','到达','游览',
            # Destinasi
            '景点','景区','名胜','景色','风景',
            # Akomodasi
            '酒店','宾馆','旅馆','客栈','民宿','帐篷',
            # Dokumen perjalanan
            '签证','护照','登机牌',
            # Transportasi wisata
            '机票','火车票','订票','订房',
            # Layanan wisata
            '导游','旅行社','团队游','自驾游',
            # Keimigrasian
            '出国','入境','海关','边检','行李','行李箱','安检',
            # Oleh-oleh
            '纪念品','特产',
            # Konsep
            '海外','国外','旅途',
        ],
    },

    'teknologi': {
        'label_id': 'Teknologi & Sains',
        'label_zh': '科技',
        'words': [
            # Perangkat
            '电脑','手机','平板','打印机','路由器',
            # Software & sistem
            '程序','软件','硬件','系统','平台','算法','数据',
            # Teknologi canggih
            '人工智能','机器人','自动化','互联网','云计算','大数据',
            '芯片','处理器','内存','存储',
            # Energi & inovasi
            '电池','太阳能','核能','新能源','电动车',
            # Penelitian
            '实验室','研发','专利','科研','航天','卫星','探测器',
            # Kata umum
            '科技','技术','科学','研究','发明','创新','数字','智能',
        ],
    },

    'seni_budaya': {
        'label_id': 'Seni & Budaya',
        'label_zh': '艺术文化',
        'words': [
            # Jenis seni
            '音乐','绘画','书法','雕塑','文学',
            '小说','诗歌','散文','戏剧','电影','动画','漫画',
            # Aktivitas seni
            '唱歌','跳舞','演奏','表演','展览',
            # Alat musik
            '钢琴','小提琴','吉他','二胡','笛子','古筝','鼓',
            # Tempat seni
            '博物馆','美术馆','剧院','音乐厅',
            # Budaya & tradisi
            '传统文化','民俗','风俗','习俗','礼仪',
            '历史','古代','现代','当代','民族','文明','遗产',
            # Kata umum
            '艺术','文化',
        ],
    },

    'hobi_hiburan': {
        'label_id': 'Hobi & Hiburan',
        'label_zh': '爱好娱乐',
        'words': [
            # Hobi
            '摄影','烹饪','园艺','钓鱼','登山','阅读',
            '收藏','手工','绘画','书法',
            # Hiburan
            '游戏','棋','象棋','围棋','扑克','麻将',
            '电影','电视剧','综艺','动漫','直播','短视频',
            # Kata umum
            '爱好','兴趣','娱乐','休闲',
        ],
    },

    'perasaan_emosi': {
        'label_id': 'Perasaan & Emosi',
        'label_zh': '情感',
        'words': [
            # Positif
            '高兴','快乐','开心','幸福','满意','骄傲','自豪',
            '兴奋','激动','感动','感激','感谢',
            # Negatif
            '伤心','难过','悲伤','痛苦','绝望','沮丧','失望',
            '生气','愤怒','委屈','怨恨','恼火','愤慨',
            '害怕','恐惧','担心','焦虑','紧张','不安','恐慌',
            '孤独','寂寞','思念','想念','后悔','抱歉',
            # Netral
            '惊喜','惊讶','好奇','同情','羡慕','嫉妒',
            '喜欢','讨厌','爱','恨',
            # Konsep
            '心情','情绪','感情','感觉','情感','心理',
        ],
    },

    'keuangan': {
        'label_id': 'Keuangan & Perbankan',
        'label_zh': '金融银行',
        'words': [
            # Perbankan
            '银行','存款','取款','汇款','贷款','借款','还款',
            '账户','银行卡','ATM','信用卡','借记卡',
            # Konsep keuangan
            '利率','利息','本金','汇率','汇兑','外汇',
            # Investasi
            '股票','基金','债券','期货','证券','投资','理财',
            # Asuransi & jaminan sosial
            '保险','医保','社保','养老金','公积金',
            # Perpajakan & makroekonomi
            '税','纳税','通货膨胀','GDP','财政',
            # Pengeluaran & tabungan
            '储蓄','预算','收入','支出','花钱','节约','财务',
        ],
    },

    'negara_budaya': {
        'label_id': 'Negara & Kebangsaan',
        'label_zh': '国家地区',
        'words': [
            # Negara
            '中国','美国','日本','韩国','英国','法国','德国','俄国',
            '印度','印尼','泰国','越南','马来西亚','新加坡','澳大利亚',
            '加拿大','巴西','墨西哥','意大利','西班牙','荷兰',
            # Wilayah & benua
            '非洲','欧洲','亚洲','美洲','大洋洲','北极','南极',
            '东南亚','中东','拉丁美洲',
            # Identitas & kewarganegaraan
            '民族','国籍','华人','华侨','移民','留学生','外国人',
            '国旗','国歌','首都','首府','省会',
        ],
    },

    'arah_lokasi': {
        'label_id': 'Arah & Posisi',
        'label_zh': '方位',
        'words': [
            # Arah kardinal
            '东','西','南','北','东方','西方','南方','北方',
            '东南','东北','西南','西北','正东','正西','正南','正北',
            # Posisi relatif
            '上面','下面','左边','右边','前面','后面','中间',
            '左方','右方','上方','下方','顶部','底部','侧面',
            '旁边','附近','周围','对面','斜对面',
            # Kata umum
            '中央','中心','中部',
        ],
    },

    'pemerintahan_hukum': {
        'label_id': 'Pemerintahan & Hukum',
        'label_zh': '政府法律',
        'words': [
            # Hukum & peraturan
            '法律','法规','制度','政策','规定','条例','宪法',
            '刑法','民法','合同法','劳动法','法典',
            # Lembaga
            '政府','法院','检察院','公安局','警察局','监狱','议会',
            # Jabatan
            '总统','主席','总理','部长','省长','市长','区长',
            '法官','律师',
            # Proses hukum & politik
            '选举','投票','民主','外交','条约','协议','协定',
            # Administrasi kependudukan
            '税收','财政','公民','权利','义务','户籍','身份证','护照',
            # Kata umum
            '国家','政治',
        ],
    },

    'bisnis_perdagangan': {
        'label_id': 'Bisnis & Perdagangan',
        'label_zh': '商业贸易',
        'words': [
            # Entitas bisnis
            '公司','集团','企业','品牌',
            # Produk & layanan
            '产品','服务','商品',
            # Pasar & persaingan
            '市场','竞争','合作','谈判','签约','成交',
            # Finansial bisnis
            '利润','亏损','收入','支出','投资','融资','上市',
            # Perdagangan internasional
            '进口','出口','贸易','关税','配额',
            # Pemasaran
            '销售','营销','推广','广告','代理','经销商',
            # Pihak terkait
            '客户','顾客','消费者','供应商','合作伙伴',
            # Kontrak
            '合同',
        ],
    },

    'sifat_deskripsi': {
        'label_id': 'Sifat & Deskripsi',
        'label_zh': '性质描述',
        'words': [
            # Ukuran & dimensi
            '大','小','高','低','长','短','宽','窄','粗','细',
            '厚','薄','重','轻','深','浅','远','近',
            # Kecepatan & kondisi
            '快','慢','新','旧','热','冷','干','湿',
            # Kualitas
            '好','坏','美','丑','强','弱','硬','软',
            # Karakter
            '聪明','笨','勤劳','懒','认真','马虎','诚实','虚伪',
            '热情','冷漠','友好','善良','凶狠','温柔','粗鲁',
            # Keadaan
            '干净','脏','整齐','乱','准时','积极','消极',
            '复杂','简单','重要','普通','特殊','一般','奇怪',
            '清楚','模糊','正确','错误','准确','精确',
            '危险','安全','方便','麻烦','有趣','无聊',
        ],
    },

    'pertanian_pangan': {
        'label_id': 'Pertanian & Pangan',
        'label_zh': '农业粮食',
        'words': [
            # Orang & tempat
            '农民','农村','农田','耕地','土地','牧场','农场',
            # Tanaman komoditas
            '水稻','小麦','玉米','大豆','棉花','茶叶','甘蔗',
            # Aktivitas pertanian
            '播种','种植','收获','灌溉','施肥','除草','除虫',
            # Produk pertanian
            '粮食','农产品',
            # Input pertanian
            '化肥','农药',
            # Peternakan & perikanan
            '畜牧','养殖','渔业','捕鱼','水产',
            # Kata umum
            '农业','丰收',
        ],
    },

    'lingkungan_hidup': {
        'label_id': 'Lingkungan Hidup',
        'label_zh': '环境保护',
        'words': [
            # Masalah lingkungan
            '污染','排放','废气','废水','垃圾','温室气体',
            '全球变暖','碳排放',
            # Solusi
            '回收','节能','减排','可持续','绿色','清洁能源',
            '太阳能','风能','水能','核能','新能源','电动车',
            # Keanekaragaman hayati
            '濒危','灭绝','生物多样性','生态系统','保护区',
            # Kimia
            '碳','二氧化碳','尾气','废物',
            # Kata umum
            '环境保护','节能减排',
        ],
    },

    'agama_kepercayaan': {
        'label_id': 'Agama & Kepercayaan',
        'label_zh': '宗教信仰',
        'words': [
            # Agama
            '宗教','信仰','佛教','道教','儒教','基督教','伊斯兰教',
            '儒学','清真',
            # Tempat ibadah
            '寺庙','庙宇','教堂','清真寺','神社','寺',
            # Figur keagamaan
            '神','佛','菩萨','上帝','真主','耶稣','孔子',
            # Tokoh agama
            '信徒','教徒','僧侣','和尚','尼姑','牧师','神父','阿訇',
            '僧人',
            # Praktik keagamaan
            '祈祷','礼拜','冥想','打坐','斋戒',
            # Konsep spiritual
            '天堂','地狱','灵魂','轮回','因果','缘分','命运',
            '乐园','少林寺',
        ],
    },

    'konstruksi_teknik': {
        'label_id': 'Konstruksi & Teknik',
        'label_zh': '建筑工程',
        'words': [
            # Kegiatan konstruksi
            '建筑','建设','施工','规划','设计',
            # Material
            '砖','混凝土','钢铁','钢','木材','玻璃','塑料',
            # Infrastruktur
            '道路','桥梁','桥','隧道','地道','水坝','堤坝',
            # Bangunan
            '工厂','厂家','仓库','楼房','建筑物','高层',
            # Konsep teknik
            '工程','结构','构造',
        ],
    },

    'tekstil_fashion': {
        'label_id': 'Tekstil & Mode',
        'label_zh': '纺织时尚',
        'words': [
            # Material tekstil
            '布','丝','棉','麻','毛皮','绸','缎','绒','纱','素',
            # Industri tekstil
            '纺织','面料','质地',
            # Mode & desain
            '时尚','流行','时装','图案','花纹','花样','款式',
            # Proses
            '裁缝','缝纫','刺绣','印染','纺纱','编织',
            # Mode kontemporer
            '新潮','新款','模特儿',
        ],
    },

    'pendidikan_tinggi': {
        'label_id': 'Pendidikan Tinggi',
        'label_zh': '高等教育',
        'words': [
            # Institusi
            '大学','学院',
            # Jenjang
            '研究生','博士','硕士','本科','专科',
            # Akademisi
            '教授','副教授','讲师','导师','学者','院士',
            # Karya akademik
            '论文','毕业论文','答辩','开题',
            # Administrasi
            '专业','学分','成绩单','学位','文凭','奖学金',
            '助学金','学费','食堂','学术','科研',
            '院系','系','院长','系主任','学生会','学士',
            '部门','学堂',
        ],
    },
}

# ════════════════════════════════════════════════════════════
# PROSES: Assign tema ke setiap kata
# ════════════════════════════════════════════════════════════

sep("Memuat data")
with open(IN_WORDS, "r", encoding="utf-8") as f:
    words = json.load(f)
log(f"  ✓ {len(words):,} kata")

# Buat reverse lookup: simplified → list tema
tema_lookup = defaultdict(list)
for tema_key, rule in TEMA_WHITELIST.items():
    for hanzi in rule['words']:
        tema_lookup[hanzi].append(tema_key)

# Assign tema ke setiap kata
sep("Assign tema")
total_assigned = 0
for w in words:
    simp   = w.get('simplified', '')
    temas  = tema_lookup.get(simp, [])
    w['themes'] = temas
    if temas:
        total_assigned += 1

log(f"  Kata dengan minimal 1 tema : {total_assigned:,}")
log(f"  Kata tanpa tema            : {len(words) - total_assigned:,}")

# ════════════════════════════════════════════════════════════
# LAPORAN VERIFIKASI
# ════════════════════════════════════════════════════════════

sep("Jumlah kata per tema")
for tema_key, rule in sorted(TEMA_WHITELIST.items()):
    cnt = sum(1 for w in words if tema_key in w.get('themes', []))
    log(f"  {rule['label_id']:<35} {cnt:>5} kata")

sep("Verifikasi kata dasar tidak masuk tema konkret")
kata_dasar = ['的','了','我','是','你','他','和','在','不','有',
              '这','那','都','也','把','被','让','给']
for w in words:
    if w.get('simplified') in kata_dasar:
        temas = w.get('themes', [])
        status = "✓ bersih" if not temas or temas == ['kata_fungsi'] else f"⚠ {temas}"
        log(f"  {w['simplified']:<4}  {status}")

sep("Verifikasi tema 'warna'")
warna = [w for w in words if 'warna' in w.get('themes', [])]
log(f"  Total: {len(warna)}")
for w in sorted(warna, key=lambda x: x.get('frequency', 99999)):
    log(f"  {w['simplified']:<8} {w.get('pinyin',''):<15} {(w.get('meanings_id') or [''])[0][:50]}")

sep("Verifikasi tema 'hewan'")
hewan = [w for w in words if 'hewan' in w.get('themes', [])]
log(f"  Total: {len(hewan)}")
for w in sorted(hewan, key=lambda x: x.get('frequency', 99999))[:30]:
    log(f"  {w['simplified']:<8} {w.get('pinyin',''):<15} {(w.get('meanings_id') or [''])[0][:50]}")

sep("Verifikasi tema 'keluarga'")
kel = [w for w in words if 'keluarga' in w.get('themes', [])]
log(f"  Total: {len(kel)}")
for w in sorted(kel, key=lambda x: x.get('frequency', 99999))[:30]:
    log(f"  {w['simplified']:<8} {w.get('pinyin',''):<15} {(w.get('meanings_id') or [''])[0][:50]}")

# ════════════════════════════════════════════════════════════
# SIMPAN
# ════════════════════════════════════════════════════════════

sep("Simpan app_words.json")
with open(OUT_WORDS, "w", encoding="utf-8") as f:
    json.dump(words, f, ensure_ascii=False)
log(f"  ✓ app_words.json disimpan")

sep("Simpan index_theme.json")
freq_map = {w.get('simplified',''): w.get('frequency', 99999) for w in words}
idx_out  = {}
for tema_key, rule in TEMA_WHITELIST.items():
    kata_tema = [w.get('simplified','') for w in words
                 if tema_key in w.get('themes', [])]
    kata_tema.sort(key=lambda x: freq_map.get(x, 99999))
    idx_out[tema_key] = {
        'label_id': rule['label_id'],
        'label_zh': rule.get('label_zh', ''),
        'words': kata_tema,
        'count': len(kata_tema),
    }

with open(OUT_THEME, "w", encoding="utf-8") as f:
    json.dump(idx_out, f, ensure_ascii=False)
log(f"  ✓ index_theme.json disimpan")

with open(OUT_REPORT, "w", encoding="utf-8") as f:
    f.write("\n".join(lines))
log(f"  ✓ Laporan: {OUT_REPORT}")
print("\n✅ Fix tema final selesai!")

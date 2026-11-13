# PROMPT UNTUK GPT: Proyek "Pembentukan Kata (构词法)" di aplikasi Mandarin Interaktif

Salin seluruh isi berkas ini ke GPT. Mulai dari TAHAP 0 saja (lihat bagian 6).

---

## 1. Peran dan pembagian kerja

- **Pemilik proyek:** Ruslan (pengguna tunggal aplikasi, berbahasa Indonesia).
- **Kamu (GPT) = pengisi data.** Tugasmu menyusun dan melengkapi data pelajaran, dengan lengkap dan benar.
- **Claude = pengatur aplikasi dan pemeriksa mutu.** Claude menulis semua kode (HTML, menu, tombol, pemuat data) dan akan memeriksa hasil kerjamu dengan skrip otomatis sebelum apa pun dipakai.
- Repo: https://github.com/RuslanAlimuddin/mandarin_app (kamu punya akses baca-tulis).
- Bahasa pengantar semua teks: **Bahasa Indonesia yang mudah dipahami**. Hindari istilah teknis atau jelaskan dengan kata sehari-hari.
- "Semaksimal mungkin" berarti **lengkap dan benar sesuai batas di bawah**, bukan sebanyak mungkin. Jangan menambah apa pun di luar batas.

## 2. Aturan keselamatan (WAJIB, tidak boleh dilanggar)

1. Buat satu folder baru di akar repo bernama **`kerja_gpt_afiks/`**. Di dalamnya hanya ada tiga subfolder: `acuan/` (salinan berkas relevan yang perlu kamu otak-atik), `hasil/` (hasil akhir), dan `laporan/` (laporan tiap tahap).
2. **Menulis hanya boleh di dalam `kerja_gpt_afiks/`.** Jangan mengubah, menghapus, mengganti nama, atau memindahkan berkas di luar folder itu.
3. Membaca berkas asli di repo boleh. **Menyalin ke `acuan/` hanya berkas yang relevan**, dan catat daftar salinan itu di laporan. Jangan menyalin berkas yang tidak relevan.
4. Satu commit per tahap, pesan commit dalam Bahasa Indonesia.
5. Jangan membuat atau mengubah kode (HTML, JS, CSS). Itu bagian Claude.

## 3. Latar singkat aplikasi (hanya yang relevan)

Mandarin Interaktif adalah aplikasi belajar Mandarin offline (HTML/CSS/JS biasa, data berupa berkas JSON di `data/`). Berkas yang relevan (periksa sendiri struktur isinya sebelum bekerja):

- `data/app_words.json`: kamus kata (ada kolom antara lain `simplified`, `pinyin`, `hsk`, dan arti Bahasa Indonesia; periksa nama kolom persisnya).
- `data/grammar_hsk1.json` sampai `grammar_hsk9.json`: Tata Bahasa per tingkat HSK (kategori berisi poin; poin punya nomor, judul, fungsi, tabel pola/contoh/terjemahan, dan ada yang berupa tabel referensi). Halaman Tata Bahasa menggabungkan kategori sejenis dari berbagai tingkat menjadi satu topik. Topik yang sudah ada: **"Prefix & Suffix (Imbuhan)"**, berisi HSK 1 kategori "AWALAN & AKHIRAN" (poin 56 untuk 小— dan 第—, poin 57 untuk —们 dan —边), HSK 3 poin 16.3 (—子), dan HSK 9 kategori "准词缀" (awalan/akhiran semu seperti 后—, 亲—, —观, —界, —然, —坛, —制).
- `data/pelajaran/pilar_1.json` sampai `pilar_11.json`: Pelajaran Lengkap (11 pilar). Tiap berkas punya daftar `bagian`, tiap bagian punya `judul` dan blok isi (paragraf, poin, tabel, contoh, peringatan). Pilar 4 (partikel & aspek) dan Pilar 9 (kata sifat & reduplikasi) sudah sangat lengkap.
- `data/produktif_karakter.json`: fitur "Akar Kosakata" (±1.389 karakter akar beserta kata turunannya).
- Berkas data fitur "Pola Pembentukan Kata Majemuk" (cari sendiri namanya di `data/`).
- `peta-bahasa.html`, `tatabahasa.html`, `kamus.html`: halaman terkait (hanya dibaca, jangan diubah).

## 4. Keputusan yang SUDAH FINAL (jangan diubah, jangan diperdebatkan)

**Tujuan:** menambah pelajaran pembentukan kata Mandarin dengan tiga lapis yang saling terhubung: Kamus (daftar entri dan kata contoh), Tata Bahasa (penjelasan per entri dan kalimat), dan Pelajaran Pilar 12 (konsep dan pengantar).

**Cakupan: 60 entri ("Tingkat 2")**, satu entri per karakter. Format tiap baris: karakter: kata contoh yang sudah disetujui | bukan (mirip tetapi bukan).

AKHIRAN
- A. Orang/pelaku (7)
  - 者: 记者, 作者, 读者, 学者, 消费者 | bukan: 或者, 前者, 后者
  - 家: 作家, 画家, 科学家, 专家, 行家 | bukan: 国家, 回家, 大家, 全家 (di sini 家 = rumah/keluarga)
  - 员: 演员, 服务员, 公务员, 运动员, 成员 | bukan: 动员 (kata kerja)
  - 师: 老师, 工程师, 律师, 厨师, 设计师 | bukan: 师生
  - 生: 学生, 大学生, 留学生, 毕业生, 医生 | bukan: 发生, 出生, 产生, 人生, 陌生, 花生
  - 手: 歌手, 选手, 助手, 高手, 新手 | catatan: di depan (手机, 手套) 手 hanya "tangan"
  - 长: 校长, 市长, 班长, 部长, 船长 | bukan: 成长, 增长, 擅长, 漫长 (dibaca zhǎng/cháng menurut arti)
- B. Sifat dan konsep abstrak (10)
  - 化: 现代化, 绿化, 美化, 简化, 老化 | bukan: 文化, 变化 (kata utuh)
  - 性: 个性, 积极性, 弹性, 慢性, 女性
  - 度: 温度, 速度, 难度, 角度, 程度
  - 率: 效率, 汇率, 频率, 概率, 利率 | bukan: 坦率, 草率 (dibaca shuài)
  - 感: 情感, 灵感, 好感, 责任感, 口感
  - 力: 能力, 压力, 听力, 体力, 活力 | bukan: 力量 (kata utuh)
  - 量: 数量, 质量, 重量, 能量, 音量 | bukan: 商量, 测量
  - 法: 方法, 办法, 想法, 看法, 做法 | arti lain "hukum": 合法, 违法
  - 观: 乐观, 悲观, 客观, 主观, 价值观
  - 点: 优点, 缺点, 特点, 观点, 地点
- C. Jenis dan gaya (3)
  - 型: 大型, 小型, 新型, 发型, 转型
  - 式: 方式, 正式, 公式, 仪式, 美式
  - 类: 人类, 种类, 分类, 之类, 同类
- D. Bidang dan ilmu (5)
  - 学: 科学, 文学, 医学, 哲学, 大学 | catatan: di depan (学生, 学校) 学 = belajar
  - 论: 理论, 结论, 讨论, 评论, 辩论 | bukan: 无论, 不论
  - 主义: 社会主义, 资本主义, 帝国主义, 官僚主义 (hanya 4 contoh di kamus)
  - 业: 专业, 职业, 工业, 农业, 企业 | bukan: 毕业, 失业, 创业 (kata kerja)
  - 界: 外界, 自然界, 工商界, 边界, 眼界
- E. Tempat dan lembaga (9)
  - 馆: 图书馆, 博物馆, 饭馆, 旅馆, 大使馆
  - 室: 办公室, 教室, 实验室, 卧室, 浴室
  - 站: 车站, 地铁站, 加油站, 网站, 核电站
  - 场: 机场, 商场, 广场, 球场, 停车场
  - 院: 医院, 学院, 电影院, 法院, 剧院 | bukan: 住院 (kata kerja)
  - 店: 商店, 书店, 药店, 酒店, 便利店
  - 所: 场所, 研究所, 厕所, 诊所, 事务所
  - 区: 地区, 社区, 郊区, 小区, 景区
  - 部: 东部, 内部, 总部, 俱乐部, 头部
- F. Alat, barang, biaya (5)
  - 器: 机器, 武器, 电器, 乐器, 浏览器
  - 机: 手机, 飞机, 相机, 电视机, 洗衣机 | catatan: di depan (机场, 机器) dan arti "kesempatan" (时机, 危机)
  - 品: 食品, 商品, 产品, 作品, 用品
  - 物: 动物, 植物, 食物, 礼物, 宠物 | bukan: 购物 (kata kerja)
  - 费: 学费, 消费, 免费, 小费, 生活费 | bukan: 浪费
- G. Pelengkap kata benda (4)
  - 们: 我们, 你们, 他们, 人们, 咱们 | catatan: tidak dipakai bersama bilangan
  - 子: 桌子, 椅子, 房子, 杯子, 筷子
  - 儿: 这儿, 哪儿, 玩儿, 一会儿, 一点儿 | bukan: 女儿 (儿 = anak)
  - 头: 石头, 木头, 骨头, 里头, 舌头 | bukan: 点头, 回头 (头 = kepala)

AWALAN
- H. Penanda awal kata (4)
  - 老: 老师, 老板, 老乡, 老公, 老百姓
  - 第: 第一, 第二, 第一手, 第一线 (hanya 4 contoh di kamus)
  - 初: 初中, 初级, 初步, 初期, 初次
  - 可: 可爱, 可怕, 可靠, 可惜, 可笑 | bukan: 可以, 可能, 可是 (kata utuh)
- I. Menolak/meniadakan (5)
  - 不: 不同, 不错, 不少, 不够, 不如
  - 无: 无法, 无聊, 无限, 无奈, 无效
  - 非: 非常, 非法, 非凡, 非得, 非金属
  - 未: 未来, 未必, 未经, 未免, 未成年人
  - 反: 反对, 反应, 反问, 反感, 反馈
- J. Tingkat dan keseluruhan (8)
  - 超: 超过, 超级, 超市, 超速, 超标
  - 准: 准备, 准确, 准时, 准则, 准许 | catatan: awalan paling lemah; di kamus berarti "tepat/boleh", bukan "calon" (seperti 准妈妈)
  - 总: 总是, 总共, 总结, 总部, 总经理
  - 半: 半天, 半年, 半夜, 半路, 半岛
  - 自: 自己, 自由, 自然, 自动, 自信
  - 全: 全国, 全家, 全球, 全面, 全新
  - 同: 同学, 同事, 同意, 同时, 同样
  - 共: 共同, 共有, 共享, 共计, 共识

Total: akhiran 43 + awalan 17 = **60 entri**. Entri **副 sengaja dikeluarkan** (hanya 1 kata di kamus).

**Aturan kata contoh:** semua kata contoh harus **benar-benar ada di `app_words.json`** (cocokkan kolom `simplified`). Setiap entri punya 3 sampai 5 contoh. Kata yang menyesatkan masuk daftar "bukan" (mirip tetapi bukan), dengan alasan satu kalimat. Daftar di atas sudah disetujui Ruslan; kalau ada kata yang ternyata tidak ada di `app_words.json`, **laporkan, jangan menggantinya sendiri**.

**Karakter yang berperan di dua posisi** (mis. 手, 家, 力, 机, 场, 学, 同, 总, 部, 院, 站, 物, 观, 法, 业): tetap **satu entri per karakter**, dengan bagian "sebagai akhiran" dan "sebagai awalan" yang masing-masing punya arti dan contoh sendiri. Posisi depan yang hanya berupa kata biasa (mis. 家 di 家庭) tidak dijadikan "awalan"; tulis sebagai catatan "mirip tetapi bukan". Kamu yang memastikan karakter mana yang benar-benar dua posisi, berdasarkan data.

**Tata Bahasa:** entri baru **memperluas topik yang sudah ada** lewat berkas data baru. Poin lama tidak diubah. Untuk 第, 们, dan 子 (sudah ada di poin lama), entri baru ditandai sebagai "pendalaman" dan menyebut nomor poin lamanya.

**Jangan dikerjakan sekarang (Tingkat 3 dan lainnya):** 族, 迷, 热, 控, 症, 剂, 炎, 盲, kata penunjuk posisi (上, 下, 里, 外, 中, 间), 客, 友, 体, 心, 气, 阿/小/大 sebagai awalan, serta modul kata majemuk, kata berulang, perubahan kelas kata, dan partikel dari dokumen kurikulum 汉语构词法 (itu rencana lanjutan, atau sudah ada di aplikasi).

**Belum diputuskan (jangan dikerjakan sampai ada instruksi):** apakah 小 dan 边 (yang sudah ada di Tata Bahasa HSK 1) ikut menjadi entri baru (jumlah menjadi 62). Catat saja di laporan Tahap 0.

## 5. Bahan yang harus dibuat

**(a) Data Kamus**, berkas baru `hasil/afiks_kamus.json`. Tiap entri minimal berisi: `id`, `karakter`, `pinyin` (dengan tanda nada), `kelompok` (A sampai J) dan `kelompok_nama`, `posisi` ("akhiran", "awalan", atau "keduanya"), `arti_dasar`, `bagian` (per posisi: `sebagai`, `fungsi`, `arti`, daftar `contoh` dengan `kata`), `bukan` (daftar `kata` dan `alasan`), dan `catatan`. Boleh menambah kolom, tidak boleh mengurangi. **Jangan menyimpan tingkat HSK per contoh**; aplikasi mengambilnya dari `app_words.json`. Buat juga `hasil/afiks_kamus_SKEMA.md` yang menjelaskan setiap kolom.

**(b) Poin Tata Bahasa**, berkas baru `hasil/grammar_afiks.json`. Ikuti **persis skema poin di `grammar_hsk*.json`** (periksa dulu dan tiru kolomnya). Tiap entri: penjelasan singkat dalam Bahasa Indonesia sederhana, **2 kalimat contoh** (Mandarin, pinyin dengan tanda nada, terjemahan Indonesia; usahakan memakai kata yang ada di `app_words.json`), tingkat HSK terendah dari contoh utamanya (sebagai keterangan), dan tautan nama ke entri Kamus yang sesuai. Gunakan penomoran dengan awalan `AFX.` (mis. `AFX.01`) agar tidak bentrok dengan nomor lama.

**(c) Pelajaran Pilar 12**, berkas baru `hasil/pilar_12.json`, mengikuti skema `data/pelajaran/pilar_N.json`. Judul pilar: **"Pembentukan Kata (构词法)"**. Enam bagian:
1. Apa itu awalan dan akhiran dalam Mandarin (dan bedanya dengan imbuhan bahasa Indonesia seperti me-, -kan).
2. Cara membaca kartu entri.
3. Karakter bermakna ganda (家, 生, 长, 率, 手, 点, 化, 头, dan sejenisnya).
4. Tabel perbandingan akhiran pelaku: 者, 家, 员, 师, 生, 手, 长.
5. Awalan penolak: 不, 无, 非, 未, 反.
6. Peta cepat 60 entri, dan apa yang menyusul kelak.

## 6. Tahap kerja (berhenti dan lapor di akhir tiap tahap)

- **TAHAP 0, audit (hanya membaca dan membuat folder + laporan).** Telusuri seluruh repo untuk semua yang berkaitan dengan pembentukan kata: topik "Prefix & Suffix (Imbuhan)" di Tata Bahasa, bagian terkait di Pilar 4/9, Akar Kosakata, Pola Pembentukan Kata Majemuk, dan hal serupa. Buat `laporan/tahap0_audit.md` berisi: (1) inventaris apa yang sudah ada beserta jumlahnya, (2) tumpang tindih dengan 60 entri kita, (3) celah yang kamu temukan pada bagian yang sudah ada dan **usulan** cara melengkapinya (hanya usulan, jangan ditulis kontennya), (4) hasil pencocokan semua kata contoh di bagian 4 dengan `app_words.json` (daftar yang tidak ditemukan), (5) pendapatmu tentang 小 dan 边. **Berhenti, tunggu perintah "LANJUT TAHAP 1".**
- **TAHAP 1:** data Kamus (a). **TAHAP 2:** poin Tata Bahasa (b). **TAHAP 3:** Pelajaran Pilar 12 (c). Setiap tahap diakhiri laporan dan berhenti.
- **TAHAP 4 (hanya jika Ruslan menyetujui usulan di Tahap 0):** melengkapi bagian yang sudah ada sesuai usulan yang disetujui, tetap sebagai berkas baru di `hasil/`.
- **Kapan berhenti:** setelah daftar bahan di bagian 5 selesai dan laporan terakhir dikirim. Jangan menambah pekerjaan lain.

## 7. Aturan mutu

- Pinyin selalu dengan tanda nada; untuk kata yang ada di `app_words.json`, ikuti pinyin di sana.
- **Jangan mengarang** kata, arti, atau pinyin. Ragu: tandai `⚠️ perlu dicek` dan lanjutkan.
- Tidak boleh ada sisa penanda tak berguna seperti `[citation:1]` atau teks salinan lain di dalam isi.
- Semua berkas JSON harus valid (UTF-8, tanpa koma berlebih), dan **kamu sendiri menjalankan pengecekan** (parse JSON, cocokkan kata contoh dengan `app_words.json`) sebelum melapor.
- Bahasa penjelasan sederhana; istilah teknis harus dijelaskan dengan kata sehari-hari.

## 8. Temuan yang sudah diketahui (cukup LAPORKAN, jangan diperbaiki)

- `pilar_3.json` isinya salinan pelajaran Kata Kerja Modal (sama dengan `pilar_5.json`); pelajaran 量词 sebenarnya belum ada.
- Di `app_words.json`, 重点 tercatat dibaca *chóngdiǎn*, seharusnya *zhòngdiǎn*.
- Poin HSK 9 kategori "准词缀" masih memuat sisa penanda `[citation:1]`.
- Karakter 师 tidak ada di daftar Akar Kosakata.
- Kalau kamu menemukan masalah serupa, tambahkan ke laporan.

## 9. Format laporan tiap tahap

Singkat dan padat: (1) apa yang dibuat dan jumlahnya, (2) pengecekan yang dijalankan dan hasilnya, (3) daftar keraguan atau temuan, (4) daftar berkas yang dibuat atau disalin (dengan jalurnya), (5) kalimat penutup: "Menunggu perintah LANJUT dari Ruslan."

Setelah tiap tahap, Ruslan akan meminta Claude memeriksa isi folder `kerja_gpt_afiks/` dengan skrip otomatis; perbaikan yang diminta kembali kepadamu.

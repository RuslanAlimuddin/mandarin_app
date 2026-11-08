/* ═══════════════════════════════════════════════════════════════
   wordbuilder-data.js — Data statis: definisi pola kalimat (PATTERNS)
   dan state kuis pola (QUIZ_POLA)
═══════════════════════════════════════════════════════════════ */
'use strict';


/* ── BANK KATA PER KATEGORI ────────────────────────────────────
   WORD_POOLS TIDAK LAGI di-hardcode di sini.
   Sekarang dimuat secara dinamis dari data/wb_pools.json (11.470 kata
   app_words.json, difilter per pos/theme, dikoreksi via wb_overrides.json)
   lewat fetch() di wordbuilder_PART_4.txt -> lihat fungsi loadWordPools().
   Variabel global `let WORD_POOLS = {}` dideklarasikan di PART_4.
═══════════════════════════════════════════════════════════════ */


/* ══════════════════════════════════════════════════════════════
   DEFINISI POLA
══════════════════════════════════════════════════════════════ */
const PATTERNS = {

  'S-V': {
    name: 'Subjek + Kata Kerja', formula: 'S + V',
    tip: '<strong>S + V</strong> — Kalimat paling dasar. Tidak perlu objek jika KK intransitif. Contoh: 我来 (Saya datang).',
    slots: [
      { id:'s', label:'Subjek',     required:true, pool:'subyek' },
      { id:'v', label:'Kata Kerja', required:true, pool:'kata_kerja' },
    ],
    examples: [
      { cn:'我来。',     py:'Wǒ lái.',       id:'Saya datang.' },
      { cn:'他走了。',   py:'Tā zǒu le.',    id:'Dia sudah pergi.' },
      { cn:'我们吃吧。', py:'Wǒmen chī ba.', id:'Yuk kita makan.' },
    ],
    build: (v) => {
      if (!v.s || !v.v) return null;
      return { cn: v.s.cn+v.v.cn+'。', py: v.s.py+' '+v.v.py+'.', id: v.s.id+' '+v.v.id+'.' };
    },
  },

  'S-V-O': {
    name: 'Subjek + Kata Kerja + Objek', formula: 'S + V + O',
    tip: '<strong>S + V + O</strong> — Struktur inti bahasa Mandarin. Urutan ini tidak berubah.',
    slots: [
      { id:'s', label:'Subjek',     required:true, pool:'subyek' },
      { id:'v', label:'Kata Kerja', required:true, pool:'kata_kerja' },
      { id:'o', label:'Objek',      required:true, pool:'objek_umum' },
    ],
    examples: [
      { cn:'我吃饭。',     py:'Wǒ chī fàn.',         id:'Saya makan.' },
      { cn:'她喜欢音乐。', py:'Tā xǐhuan yīnyuè.',   id:'Dia suka musik.' },
      { cn:'我们学中文。', py:'Wǒmen xué Zhōngwén.', id:'Kami belajar bahasa Mandarin.' },
    ],
    build: (v) => {
      if (!v.s || !v.v || !v.o) return null;
      return { cn: v.s.cn+v.v.cn+v.o.cn+'。', py: v.s.py+' '+v.v.py+' '+v.o.py+'.', id: v.s.id+' '+v.v.id+' '+v.o.id+'.' };
    },
  },

  'S-shi-O': {
    name: 'S + 是 + O (adalah)', formula: 'S + 是 + O',
    tip: '<strong>是 (shì)</strong> = "adalah". Dipakai untuk identitas, bukan deskripsi sifat. Salah: <em>他是高</em>. Benar: <em>他很高</em>.',
    slots: [
      { id:'s',   label:'Subjek',    required:true, pool:'subyek' },
      { id:'shi', label:'',          required:true, fixed:{ cn:'是', py:'shì', id:'adalah' } },
      { id:'o',   label:'Identitas', required:true, pool:'identitas' },
    ],
    examples: [
      { cn:'我是学生。',   py:'Wǒ shì xuésheng.', id:'Saya adalah murid.' },
      { cn:'他是老师。',   py:'Tā shì lǎoshī.',   id:'Dia adalah guru.' },
      { cn:'这是我的书。', py:'Zhè shì wǒ de shū.', id:'Ini adalah buku saya.' },
    ],
    build: (v) => {
      if (!v.s || !v.o) return null;
      return { cn: v.s.cn+'是'+v.o.cn+'。', py: v.s.py+' shì '+v.o.py+'.', id: v.s.id+' adalah '+v.o.id+'.' };
    },
  },

  'S-you-O': {
    name: 'S + 有 + O (mempunyai)', formula: 'S + 有 + O',
    tip: '<strong>有 (yǒu)</strong> = "memiliki". Negatifnya adalah <strong>没有 (méiyǒu)</strong>, BUKAN 不有.',
    slots: [
      { id:'s',   label:'Subjek', required:true, pool:'subyek' },
      { id:'you', label:'',       required:true, fixed:{ cn:'有', py:'yǒu', id:'punya' } },
      { id:'o',   label:'Objek',  required:true, pool:'objek_umum' },
    ],
    examples: [
      { cn:'我有书。',   py:'Wǒ yǒu shū.',     id:'Saya punya buku.' },
      { cn:'他没有钱。', py:'Tā méiyǒu qián.', id:'Dia tidak punya uang.' },
      { cn:'我有问题。', py:'Wǒ yǒu wèntí.',   id:'Saya punya pertanyaan.' },
    ],
    build: (v) => {
      if (!v.s || !v.o) return null;
      return { cn: v.s.cn+'有'+v.o.cn+'。', py: v.s.py+' yǒu '+v.o.py+'.', id: v.s.id+' punya '+v.o.id+'.' };
    },
  },

  'S-zai-L': {
    name: 'S + 在 + Tempat (berada di)', formula: 'S + 在 + Tempat',
    tip: '<strong>在 (zài)</strong> = "berada di". Tempat selalu di belakang 在.',
    slots: [
      { id:'s',   label:'Subjek', required:true, pool:'subyek' },
      { id:'zai', label:'',       required:true, fixed:{ cn:'在', py:'zài', id:'berada di' } },
      { id:'l',   label:'Tempat', required:true, pool:'tempat' },
    ],
    examples: [
      { cn:'我在家。',     py:'Wǒ zài jiā.',         id:'Saya di rumah.' },
      { cn:'老师在学校。', py:'Lǎoshī zài xuéxiào.', id:'Guru berada di sekolah.' },
      { cn:'他们在餐厅。', py:'Tāmen zài cāntīng.',  id:'Mereka di restoran.' },
    ],
    build: (v) => {
      if (!v.s || !v.l) return null;
      return { cn: v.s.cn+'在'+v.l.cn+'。', py: v.s.py+' zài '+v.l.py+'.', id: v.s.id+' berada di '+v.l.id+'.' };
    },
  },

  'S-hen-Adj': {
    name: 'S + 很 + Kata Sifat', formula: 'S + 很 + Adj',
    tip: '<strong>很 (hěn)</strong> sering dipakai sebagai penghubung netral sebelum kata sifat. Tanpa 很, kalimat terasa seperti perbandingan.',
    slots: [
      { id:'s',   label:'Subjek',     required:true, pool:'subyek' },
      { id:'hen', label:'',           required:true, fixed:{ cn:'很', py:'hěn', id:'sangat' } },
      { id:'adj', label:'Kata Sifat', required:true, pool:'kata_sifat' },
    ],
    examples: [
      { cn:'我很好。',   py:'Wǒ hěn hǎo.',      id:'Saya (sangat) baik.' },
      { cn:'这个很贵。', py:'Zhège hěn guì.',    id:'Ini sangat mahal.' },
      { cn:'他很聪明。', py:'Tā hěn cōngming.', id:'Dia sangat cerdas.' },
    ],
    build: (v) => {
      if (!v.s || !v.adj) return null;
      return { cn: v.s.cn+'很'+v.adj.cn+'。', py: v.s.py+' hěn '+v.adj.py+'.', id: v.s.id+' sangat '+v.adj.id+'.' };
    },
  },

  'S-bu-Adj': {
    name: 'S + 不 + Sifat/KK (negatif)', formula: 'S + 不 + Adj/V',
    tip: '<strong>不 (bù)</strong> menegasikan kata sifat dan kata kerja. Untuk 有, gunakan <strong>没有</strong>, bukan 不有.',
    slots: [
      { id:'s',   label:'Subjek',           required:true, pool:'subyek' },
      { id:'bu',  label:'',                 required:true, fixed:{ cn:'不', py:'bù', id:'tidak' } },
      { id:'adj', label:'Sifat/Kata Kerja', required:true, pool:'kata_sifat' },
    ],
    examples: [
      { cn:'我不忙。', py:'Wǒ bù máng.', id:'Saya tidak sibuk.' },
      { cn:'他不去。', py:'Tā bù qù.',   id:'Dia tidak pergi.' },
      { cn:'这不贵。', py:'Zhè bù guì.', id:'Ini tidak mahal.' },
    ],
    build: (v) => {
      if (!v.s || !v.adj) return null;
      return { cn: v.s.cn+'不'+v.adj.cn+'。', py: v.s.py+' bù '+v.adj.py+'.', id: v.s.id+' tidak '+v.adj.id+'.' };
    },
  },

  'S-tai-Adj-le': {
    name: 'S + 太…了 (terlalu)', formula: 'S + 太 + Adj + 了',
    tip: '<strong>太…了 (tài…le)</strong> = "terlalu…". Pola ini selalu mengapit kata sifat.',
    slots: [
      { id:'s',   label:'Subjek',     required:true, pool:'subyek' },
      { id:'tai', label:'',           required:true, fixed:{ cn:'太', py:'tài', id:'terlalu' } },
      { id:'adj', label:'Kata Sifat', required:true, pool:'kata_sifat' },
      { id:'le',  label:'',           required:true, fixed:{ cn:'了', py:'le', id:'(penegas)' } },
    ],
    examples: [
      { cn:'这太贵了！', py:'Zhè tài guì le!', id:'Ini terlalu mahal!' },
      { cn:'我太忙了。', py:'Wǒ tài máng le.', id:'Saya terlalu sibuk.' },
      { cn:'太好了！',   py:'Tài hǎo le!',     id:'Bagus sekali!' },
    ],
    build: (v) => {
      if (!v.s || !v.adj) return null;
      return { cn: v.s.cn+'太'+v.adj.cn+'了！', py: v.s.py+' tài '+v.adj.py+' le!', id: v.s.id+' terlalu '+v.adj.id+'!' };
    },
  },

  'S-Num-M-N': {
    name: 'Angka + Satuan + Nomina', formula: 'Num + 量词 + N',
    tip: '<strong>量词 (liàngcí)</strong> = kata satuan/penjodoh bilangan. Wajib dipakai antara angka dan nomina.',
    slots: [
      { id:'num', label:'Angka',  required:true, pool:'angka' },
      { id:'m',   label:'Satuan', required:true, pool:'satuan' },
      { id:'n',   label:'Benda',  required:true, pool:'objek_umum' },
    ],
    examples: [
      { cn:'一本书',   py:'yī běn shū',     id:'satu buah buku' },
      { cn:'两杯茶',   py:'liǎng bēi chá',  id:'dua cangkir teh' },
      { cn:'三个朋友', py:'sān gè péngyou', id:'tiga orang teman' },
    ],
    build: (v) => {
      if (!v.num || !v.m || !v.n) return null;
      return { cn: v.num.cn+v.m.cn+v.n.cn, py: v.num.py+' '+v.m.py+' '+v.n.py, id: v.num.id+' '+v.m.id+' '+v.n.id };
    },
  },

  'S-T-V-O': {
    name: 'S + Waktu + V + O', formula: 'S + 时间 + V + O',
    tip: 'Keterangan waktu bisa diletakkan di awal kalimat atau setelah subjek — TIDAK di akhir seperti bahasa Indonesia.',
    slots: [
      { id:'s', label:'Subjek',  required:true,  pool:'subyek' },
      { id:'t', label:'Waktu',   required:true,  pool:'waktu' },
      { id:'v', label:'KK',      required:true,  pool:'kata_kerja' },
      { id:'o', label:'Objek',   required:false, pool:'objek_umum' },
    ],
    examples: [
      { cn:'我今天学中文。', py:'Wǒ jīntiān xué Zhōngwén.', id:'Saya hari ini belajar bahasa Mandarin.' },
      { cn:'他明天去学校。', py:'Tā míngtiān qù xuéxiào.',  id:'Dia besok pergi ke sekolah.' },
      { cn:'我们每天吃饭。', py:'Wǒmen měitiān chī fàn.',   id:'Kami makan setiap hari.' },
    ],
    build: (v) => {
      if (!v.s || !v.t || !v.v) return null;
      const o = v.o ? v.o.cn : ''; const opy = v.o ? ' '+v.o.py : ''; const oid = v.o ? ' '+v.o.id : '';
      return { cn: v.s.cn+v.t.cn+v.v.cn+o+'。', py: v.s.py+' '+v.t.py+' '+v.v.py+opy+'.', id: v.s.id+' '+v.t.id+' '+v.v.id+oid+'.' };
    },
  },

  'S-V-guo': {
    name: 'S + V + 过 (pernah)', formula: 'S + V + 过',
    tip: '<strong>过 (guò)</strong> setelah kata kerja = menyatakan pengalaman di masa lalu.',
    slots: [
      { id:'s',   label:'Subjek',     required:true,  pool:'subyek' },
      { id:'v',   label:'Kata Kerja', required:true,  pool:'kata_kerja' },
      { id:'guo', label:'',           required:true,  fixed:{ cn:'过', py:'guò', id:'(pernah)' } },
      { id:'o',   label:'Objek',      required:false, pool:'objek_umum' },
    ],
    examples: [
      { cn:'他去过中国。',     py:'Tā qù guò Zhōngguó.',       id:'Dia pernah pergi ke Tiongkok.' },
      { cn:'你看过这本书吗？', py:'Nǐ kàn guò zhè běn shū ma?', id:'Kamu pernah membaca buku ini?' },
    ],
    build: (v) => {
      if (!v.s || !v.v) return null;
      const o = v.o ? v.o.cn : ''; const opy = v.o ? ' '+v.o.py : ''; const oid = v.o ? ' '+v.o.id : '';
      return { cn: v.s.cn+v.v.cn+'过'+o+'。', py: v.s.py+' '+v.v.py+'guò'+opy+'.', id: v.s.id+' pernah '+v.v.id+oid+'.' };
    },
  },

  'S-V-le': {
    name: 'S + V + 了 (sudah selesai)', formula: 'S + V + 了',
    tip: '<strong>了 (le)</strong> setelah kata kerja menandai tindakan yang telah selesai.',
    slots: [
      { id:'s',  label:'Subjek',     required:true,  pool:'subyek' },
      { id:'v',  label:'Kata Kerja', required:true,  pool:'kata_kerja' },
      { id:'le', label:'',           required:true,  fixed:{ cn:'了', py:'le', id:'(sudah)' } },
      { id:'o',  label:'Objek',      required:false, pool:'objek_umum' },
    ],
    examples: [
      { cn:'我吃了饭。', py:'Wǒ chī le fàn.', id:'Saya sudah makan.' },
      { cn:'他买了书。', py:'Tā mǎi le shū.', id:'Dia sudah membeli buku.' },
      { cn:'我们来了。', py:'Wǒmen lái le.',  id:'Kami sudah datang.' },
    ],
    build: (v) => {
      if (!v.s || !v.v) return null;
      const o = v.o ? v.o.cn : ''; const opy = v.o ? ' '+v.o.py : ''; const oid = v.o ? ' '+v.o.id : '';
      return { cn: v.s.cn+v.v.cn+'了'+o+'。', py: v.s.py+' '+v.v.py+'le'+opy+'.', id: v.s.id+' sudah '+v.v.id+oid+'.' };
    },
  },

  'S-zai-V': {
    name: 'S + 在 + V (sedang)', formula: 'S + 在 + V',
    tip: '<strong>在 (zài) + V</strong> menyatakan aksi yang sedang berlangsung (aspek progresif).',
    slots: [
      { id:'s',   label:'Subjek',     required:true,  pool:'subyek' },
      { id:'zai', label:'',           required:true,  fixed:{ cn:'在', py:'zài', id:'sedang' } },
      { id:'v',   label:'Kata Kerja', required:true,  pool:'kata_kerja' },
      { id:'o',   label:'Objek',      required:false, pool:'objek_umum' },
    ],
    examples: [
      { cn:'我在吃饭。',     py:'Wǒ zài chī fàn.',         id:'Saya sedang makan.' },
      { cn:'他在看电视。',   py:'Tā zài kàn diànshì.',     id:'Dia sedang menonton TV.' },
      { cn:'我们在学中文。', py:'Wǒmen zài xué Zhōngwén.', id:'Kami sedang belajar Mandarin.' },
    ],
    build: (v) => {
      if (!v.s || !v.v) return null;
      const o = v.o ? v.o.cn : ''; const opy = v.o ? ' '+v.o.py : ''; const oid = v.o ? ' '+v.o.id : '';
      return { cn: v.s.cn+'在'+v.v.cn+o+'。', py: v.s.py+' zài '+v.v.py+opy+'.', id: v.s.id+' sedang '+v.v.id+oid+'.' };
    },
  },

  'Q-ma': {
    name: 'Pertanyaan Ya/Tidak + 吗', formula: 'Kalimat + 吗？',
    tip: '<strong>吗 (ma)</strong> mengubah kalimat pernyataan menjadi pertanyaan yes/no — tambahkan di akhir saja.',
    slots: [
      { id:'s',  label:'Subjek',     required:true,  pool:'subyek' },
      { id:'v',  label:'Kata Kerja', required:true,  pool:'kata_kerja' },
      { id:'o',  label:'Objek',      required:false, pool:'objek_umum' },
      { id:'ma', label:'',           required:true,  fixed:{ cn:'吗？', py:'ma?', id:'(tanya)' } },
    ],
    examples: [
      { cn:'你吃饭吗？',   py:'Nǐ chī fàn ma?',      id:'Kamu makan?' },
      { cn:'他是学生吗？', py:'Tā shì xuésheng ma?',  id:'Dia murid?' },
      { cn:'你喜欢吗？',   py:'Nǐ xǐhuan ma?',        id:'Kamu suka?' },
    ],
    build: (v) => {
      if (!v.s || !v.v) return null;
      const o = v.o ? v.o.cn : ''; const opy = v.o ? ' '+v.o.py : ''; const oid = v.o ? ' '+v.o.id : '';
      return { cn: v.s.cn+v.v.cn+o+'吗？', py: v.s.py+' '+v.v.py+opy+' ma?', id: 'Apakah '+v.s.id+' '+v.v.id+oid+'?' };
    },
  },

  'Q-ne': {
    name: 'Pertanyaan balik + 呢', formula: 'Topik + 呢？',
    tip: '<strong>呢 (ne)</strong> dipakai untuk pertanyaan "bagaimana dengan…?" tanpa mengulang kata kerja.',
    slots: [
      { id:'s',  label:'Topik', required:true, pool:'subyek' },
      { id:'ne', label:'',      required:true, fixed:{ cn:'呢？', py:'ne?', id:'(bagaimana?)' } },
    ],
    examples: [
      { cn:'我很好，你呢？', py:'Wǒ hěn hǎo, nǐ ne?', id:'Saya baik-baik, bagaimana kamu?' },
    ],
    build: (v) => {
      if (!v.s) return null;
      return { cn: v.s.cn+'呢？', py: v.s.py+' ne?', id: 'Bagaimana dengan '+v.s.id+'?' };
    },
  },

  'Q-shenme': {
    name: 'S + V + 什么 (apa)', formula: 'S + V + 什么',
    tip: '<strong>什么 (shénme)</strong> = "apa". Posisinya tetap di tempat objek.',
    slots: [
      { id:'s',      label:'Subjek',     required:true, pool:'subyek' },
      { id:'v',      label:'Kata Kerja', required:true, pool:'kata_kerja' },
      { id:'shenme', label:'',           required:true, fixed:{ cn:'什么？', py:'shénme?', id:'apa?' } },
    ],
    examples: [
      { cn:'你吃什么？',   py:'Nǐ chī shénme?',    id:'Kamu makan apa?' },
      { cn:'你喜欢什么？', py:'Nǐ xǐhuan shénme?', id:'Kamu suka apa?' },
    ],
    build: (v) => {
      if (!v.s || !v.v) return null;
      return { cn: v.s.cn+v.v.cn+'什么？', py: v.s.py+' '+v.v.py+' shénme?', id: v.s.id+' '+v.v.id+' apa?' };
    },
  },

  'Q-zenme': {
    name: '怎么 + V (bagaimana caranya)', formula: 'S + 怎么 + V',
    tip: '<strong>怎么 (zěnme)</strong> = "bagaimana (caranya)". Diletakkan sebelum kata kerja.',
    slots: [
      { id:'s',     label:'Subjek',     required:true,  pool:'subyek' },
      { id:'zenme', label:'',           required:true,  fixed:{ cn:'怎么', py:'zěnme', id:'bagaimana' } },
      { id:'v',     label:'Kata Kerja', required:true,  pool:'kata_kerja' },
      { id:'o',     label:'Objek',      required:false, pool:'objek_umum' },
    ],
    examples: [
      { cn:'你怎么去？', py:'Nǐ zěnme qù?',   id:'Kamu pergi dengan cara apa?' },
      { cn:'这怎么说？', py:'Zhè zěnme shuō?', id:'Ini bagaimana mengatakannya?' },
    ],
    build: (v) => {
      if (!v.s || !v.v) return null;
      const o = v.o ? v.o.cn : ''; const opy = v.o ? ' '+v.o.py : ''; const oid = v.o ? ' '+v.o.id : '';
      return { cn: v.s.cn+'怎么'+v.v.cn+o+'？', py: v.s.py+' zěnme '+v.v.py+opy+'?', id: 'Bagaimana cara '+v.s.id+' '+v.v.id+oid+'?' };
    },
  },

  'Q-duoshao': {
    name: '多少 / 几 (berapa)', formula: 'S + V + 多少',
    tip: '<strong>多少 (duōshao)</strong> untuk angka besar. <strong>几 (jǐ)</strong> untuk angka kecil (harus diikuti satuan).',
    slots: [
      { id:'s',       label:'Subjek',     required:true,  pool:'subyek' },
      { id:'v',       label:'Kata Kerja', required:true,  pool:'kata_kerja' },
      { id:'duoshao', label:'',           required:true,  fixed:{ cn:'多少', py:'duōshao', id:'berapa' } },
      { id:'m',       label:'Satuan',     required:false, pool:'satuan' },
    ],
    examples: [
      { cn:'这个多少钱？', py:'Zhège duōshao qián?',  id:'Ini berapa harganya?' },
      { cn:'你有多少书？', py:'Nǐ yǒu duōshao shū?', id:'Kamu punya berapa buku?' },
    ],
    build: (v) => {
      if (!v.s || !v.v) return null;
      const m = v.m ? v.m.cn : ''; const mpy = v.m ? ' '+v.m.py : '';
      return { cn: v.s.cn+v.v.cn+'多少'+m+'？', py: v.s.py+' '+v.v.py+' duōshao'+mpy+'?', id: v.s.id+' '+v.v.id+' berapa?' };
    },
  },

  /* ── MAJEMUK ── */

  'C-yinwei-suoyi': {
    name: '因为…所以 (sebab-akibat)', formula: '因为+S₁V₁+所以+S₂V₂',
    tip: '<strong>因为</strong> = "karena", <strong>所以</strong> = "maka". Keduanya sering dipakai bersama.',
    slots: [
      { id:'s1', label:'Subjek 1', required:true, pool:'subyek' },
      { id:'v1', label:'KK 1',     required:true, pool:'kata_kerja' },
      { id:'s2', label:'Subjek 2', required:true, pool:'subyek' },
      { id:'v2', label:'KK 2',     required:true, pool:'kata_kerja' },
    ],
    connector: { cn:'因为…所以', py:'yīnwèi…suǒyǐ' },
    examples: [
      { cn:'因为下雨，所以我不去了。', py:'Yīnwèi xià yǔ, suǒyǐ wǒ bù qù le.', id:'Karena hujan, maka saya tidak jadi pergi.' },
    ],
    build: (v) => {
      if (!v.s1||!v.v1||!v.s2||!v.v2) return null;
      return { cn:'因为'+v.s1.cn+v.v1.cn+'，所以'+v.s2.cn+v.v2.cn+'。', py:'Yīnwèi '+v.s1.py+' '+v.v1.py+', suǒyǐ '+v.s2.py+' '+v.v2.py+'.', id:'Karena '+v.s1.id+' '+v.v1.id+', maka '+v.s2.id+' '+v.v2.id+'.' };
    },
  },

  'C-suiran-danshi': {
    name: '虽然…但是 (meski-tapi)', formula: '虽然+S₁Adj₁+但是+S₂Adj₂',
    tip: '<strong>虽然</strong> = "meskipun", <strong>但是</strong> = "tetapi". Hampir selalu berpasangan.',
    slots: [
      { id:'s1',  label:'Subjek 1',   required:true, pool:'subyek' },
      { id:'adj1',label:'Sifat/KK 1', required:true, pool:'kata_sifat' },
      { id:'s2',  label:'Subjek 2',   required:true, pool:'subyek' },
      { id:'adj2',label:'Sifat/KK 2', required:true, pool:'kata_sifat' },
    ],
    connector: { cn:'虽然…但是', py:'suīrán…dànshì' },
    examples: [
      { cn:'虽然他忙，但是很高兴。', py:'Suīrán tā máng, dànshì hěn gāoxìng.', id:'Meskipun dia sibuk, tapi sangat senang.' },
    ],
    build: (v) => {
      if (!v.s1||!v.adj1||!v.s2||!v.adj2) return null;
      return { cn:'虽然'+v.s1.cn+'很'+v.adj1.cn+'，但是'+v.s2.cn+'很'+v.adj2.cn+'。', py:'Suīrán '+v.s1.py+' hěn '+v.adj1.py+', dànshì '+v.s2.py+' hěn '+v.adj2.py+'.', id:'Meskipun '+v.s1.id+' '+v.adj1.id+', tapi '+v.s2.id+' '+v.adj2.id+'.' };
    },
  },

  'C-ruguo-jiu': {
    name: '如果…就 (jika-maka)', formula: '如果+kondisi+就+hasil',
    tip: '<strong>如果</strong> = "jika", <strong>就</strong> = "maka". 就 selalu ada di klausa hasil sebelum kata kerja.',
    slots: [
      { id:'s1',  label:'Subjek 1', required:true, pool:'subyek' },
      { id:'adj1',label:'Kondisi',  required:true, pool:'kata_sifat' },
      { id:'s2',  label:'Subjek 2', required:true, pool:'subyek' },
      { id:'v2',  label:'Hasil KK', required:true, pool:'kata_kerja' },
    ],
    connector: { cn:'如果…就', py:'rúguǒ…jiù' },
    examples: [
      { cn:'如果你来，我就高兴。', py:'Rúguǒ nǐ lái, wǒ jiù gāoxìng.', id:'Jika kamu datang, saya akan senang.' },
    ],
    build: (v) => {
      if (!v.s1||!v.adj1||!v.s2||!v.v2) return null;
      return { cn:'如果'+v.s1.cn+'很'+v.adj1.cn+'，'+v.s2.cn+'就'+v.v2.cn+'。', py:'Rúguǒ '+v.s1.py+' hěn '+v.adj1.py+', '+v.s2.py+' jiù '+v.v2.py+'.', id:'Jika '+v.s1.id+' '+v.adj1.id+', maka '+v.s2.id+' akan '+v.v2.id+'.' };
    },
  },

  'C-bujin-erqie': {
    name: '不仅…而且 (tidak hanya…bahkan)', formula: 'S+不仅Adj₁+而且Adj₂',
    tip: '<strong>不仅</strong> = "tidak hanya", <strong>而且</strong> = "bahkan juga".',
    slots: [
      { id:'s',    label:'Subjek',  required:true, pool:'subyek' },
      { id:'adj1', label:'Sifat 1', required:true, pool:'kata_sifat' },
      { id:'adj2', label:'Sifat 2', required:true, pool:'kata_sifat' },
    ],
    connector: { cn:'不仅…而且', py:'bùjǐn…érqiě' },
    examples: [
      { cn:'他不仅聪明，而且努力。', py:'Tā bùjǐn cōngming, érqiě nǔlì.', id:'Dia tidak hanya cerdas, bahkan juga rajin.' },
    ],
    build: (v) => {
      if (!v.s||!v.adj1||!v.adj2) return null;
      return { cn: v.s.cn+'不仅很'+v.adj1.cn+'，而且很'+v.adj2.cn+'。', py: v.s.py+' bùjǐn hěn '+v.adj1.py+', érqiě hěn '+v.adj2.py+'.', id: v.s.id+' tidak hanya '+v.adj1.id+', bahkan juga '+v.adj2.id+'.' };
    },
  },

  'C-yibian-yibian': {
    name: '一边…一边 (sambil)', formula: 'S+一边V₁+一边V₂',
    tip: '<strong>一边…一边</strong> = "sambil melakukan A, juga melakukan B". Kedua aksi berlangsung bersamaan.',
    slots: [
      { id:'s',  label:'Subjek', required:true, pool:'subyek' },
      { id:'v1', label:'KK 1',   required:true, pool:'kata_kerja' },
      { id:'v2', label:'KK 2',   required:true, pool:'kata_kerja' },
    ],
    connector: { cn:'一边…一边', py:'yībiān…yībiān' },
    examples: [
      { cn:'他一边吃饭，一边看电视。', py:'Tā yībiān chī fàn, yībiān kàn diànshì.', id:'Dia sambil makan, juga menonton TV.' },
    ],
    build: (v) => {
      if (!v.s||!v.v1||!v.v2) return null;
      return { cn: v.s.cn+'一边'+v.v1.cn+'，一边'+v.v2.cn+'。', py: v.s.py+' yībiān '+v.v1.py+', yībiān '+v.v2.py+'.', id: v.s.id+' sambil '+v.v1.id+', juga '+v.v2.id+'.' };
    },
  },

  'C-bi': {
    name: 'A + 比 + B + Adj', formula: 'A + 比 + B + Adj',
    tip: '<strong>比 (bǐ)</strong> = "lebih dari". Urutan: A + 比 + B + sifat. JANGAN tambahkan 更 langsung setelah 比.',
    slots: [
      { id:'a',   label:'A (Subjek)',      required:true, pool:'subyek' },
      { id:'bi',  label:'',               required:true, fixed:{ cn:'比', py:'bǐ', id:'lebih dari' } },
      { id:'b',   label:'B (Pembanding)', required:true, pool:'subyek' },
      { id:'adj', label:'Kata Sifat',     required:true, pool:'kata_sifat' },
    ],
    examples: [
      { cn:'我比他忙。',   py:'Wǒ bǐ tā máng.',   id:'Saya lebih sibuk dari dia.' },
      { cn:'今天比昨天冷。', py:'Jīntiān bǐ zuótiān lěng.', id:'Hari ini lebih dingin dari kemarin.' },
    ],
    build: (v) => {
      if (!v.a||!v.b||!v.adj) return null;
      return { cn: v.a.cn+'比'+v.b.cn+'更'+v.adj.cn+'。', py: v.a.py+' bǐ '+v.b.py+' gèng '+v.adj.py+'.', id: v.a.id+' lebih '+v.adj.id+' dari '+v.b.id+'.' };
    },
  },

  'C-meiyou': {
    name: 'A + 没有 + B + Adj', formula: 'A + 没有 + B + Adj',
    tip: '<strong>没有</strong> dalam perbandingan = "tidak se-". Kebalikan dari 比.',
    slots: [
      { id:'a',      label:'A',           required:true, pool:'subyek' },
      { id:'meiyou', label:'',            required:true, fixed:{ cn:'没有', py:'méiyǒu', id:'tidak se-' } },
      { id:'b',      label:'B',           required:true, pool:'subyek' },
      { id:'adj',    label:'Kata Sifat',  required:true, pool:'kata_sifat' },
    ],
    examples: [
      { cn:'我没有他忙。',     py:'Wǒ méiyǒu tā máng.',   id:'Saya tidak sesibuk dia.' },
      { cn:'这个没有那个贵。', py:'Zhège méiyǒu nàge guì.', id:'Ini tidak semahal itu.' },
    ],
    build: (v) => {
      if (!v.a||!v.b||!v.adj) return null;
      return { cn: v.a.cn+'没有'+v.b.cn+'那么'+v.adj.cn+'。', py: v.a.py+' méiyǒu '+v.b.py+' nàme '+v.adj.py+'.', id: v.a.id+' tidak se'+v.adj.id+' '+v.b.id+'.' };
    },
  },

  'C-yiyang': {
    name: 'A + 跟 B + 一样 + Adj', formula: 'A + 跟 + B + 一样 + Adj',
    tip: '<strong>一样 (yīyàng)</strong> = "sama". Pola: A + 跟 + B + 一样 + sifat.',
    slots: [
      { id:'a',   label:'A',           required:true,  pool:'subyek' },
      { id:'gen', label:'',            required:true,  fixed:{ cn:'跟', py:'gēn', id:'dengan' } },
      { id:'b',   label:'B',           required:true,  pool:'subyek' },
      { id:'yy',  label:'',            required:true,  fixed:{ cn:'一样', py:'yīyàng', id:'sama' } },
      { id:'adj', label:'Kata Sifat',  required:false, pool:'kata_sifat' },
    ],
    examples: [
      { cn:'我跟他一样忙。', py:'Wǒ gēn tā yīyàng máng.', id:'Saya sama sibuknya dengan dia.' },
    ],
    build: (v) => {
      if (!v.a||!v.b) return null;
      const adj = v.adj ? v.adj.cn : ''; const adjpy = v.adj ? ' '+v.adj.py : ''; const adjid = v.adj ? ' '+v.adj.id : '';
      return { cn: v.a.cn+'跟'+v.b.cn+'一样'+adj+'。', py: v.a.py+' gēn '+v.b.py+' yīyàng'+adjpy+'.', id: v.a.id+' sama'+adjid+' dengan '+v.b.id+'.' };
    },
  },

  /* ── FUNGSI ── */

  'F-keyi': {
    name: '可以 (boleh/bisa)', formula: 'S + 可以 + V + O',
    tip: '<strong>可以 (kěyǐ)</strong> menyatakan izin atau kemampuan. Negatif: <strong>不可以</strong> atau <strong>不能</strong>.',
    slots: [
      { id:'s',    label:'Subjek',     required:true,  pool:'subyek' },
      { id:'keyi', label:'',           required:true,  fixed:{ cn:'可以', py:'kěyǐ', id:'boleh/bisa' } },
      { id:'v',    label:'Kata Kerja', required:true,  pool:'kata_kerja' },
      { id:'o',    label:'Objek',      required:false, pool:'objek_umum' },
    ],
    examples: [
      { cn:'你可以吃。',     py:'Nǐ kěyǐ chī.',       id:'Kamu boleh makan.' },
      { cn:'我可以用吗？',   py:'Wǒ kěyǐ yòng ma?',   id:'Boleh saya pakai?' },
    ],
    build: (v) => {
      if (!v.s||!v.v) return null;
      const o = v.o ? v.o.cn : ''; const opy = v.o ? ' '+v.o.py : ''; const oid = v.o ? ' '+v.o.id : '';
      return { cn: v.s.cn+'可以'+v.v.cn+o+'。', py: v.s.py+' kěyǐ '+v.v.py+opy+'.', id: v.s.id+' boleh '+v.v.id+oid+'.' };
    },
  },

  'F-yao': {
    name: '要 (ingin/harus)', formula: 'S + 要 + V + O',
    tip: '<strong>要 (yào)</strong> bisa "ingin", "akan", atau "harus". Negatif "tidak ingin" = <strong>不想</strong>; "tidak harus" = <strong>不用</strong>.',
    slots: [
      { id:'s',   label:'Subjek',     required:true,  pool:'subyek' },
      { id:'yao', label:'',           required:true,  fixed:{ cn:'要', py:'yào', id:'ingin/harus' } },
      { id:'v',   label:'Kata Kerja', required:true,  pool:'kata_kerja' },
      { id:'o',   label:'Objek',      required:false, pool:'objek_umum' },
    ],
    examples: [
      { cn:'我要喝水。', py:'Wǒ yào hē shuǐ.', id:'Saya ingin minum air.' },
      { cn:'你要去吗？', py:'Nǐ yào qù ma?',   id:'Kamu mau pergi?' },
    ],
    build: (v) => {
      if (!v.s||!v.v) return null;
      const o = v.o ? v.o.cn : ''; const opy = v.o ? ' '+v.o.py : ''; const oid = v.o ? ' '+v.o.id : '';
      return { cn: v.s.cn+'要'+v.v.cn+o+'。', py: v.s.py+' yào '+v.v.py+opy+'.', id: v.s.id+' ingin '+v.v.id+oid+'.' };
    },
  },

  'F-xiang': {
    name: '想 (ingin/hendak)', formula: 'S + 想 + V + O',
    tip: '<strong>想 (xiǎng)</strong> = "ingin/hendak" (lebih ringan dari 要). Juga berarti "memikirkan/merindukan" jika diikuti benda.',
    slots: [
      { id:'s',     label:'Subjek',     required:true,  pool:'subyek' },
      { id:'xiang', label:'',           required:true,  fixed:{ cn:'想', py:'xiǎng', id:'ingin' } },
      { id:'v',     label:'Kata Kerja', required:true,  pool:'kata_kerja' },
      { id:'o',     label:'Objek',      required:false, pool:'objek_umum' },
    ],
    examples: [
      { cn:'我想吃饭。',   py:'Wǒ xiǎng chī fàn.',     id:'Saya ingin makan.' },
      { cn:'她想学中文。', py:'Tā xiǎng xué Zhōngwén.', id:'Dia ingin belajar Mandarin.' },
    ],
    build: (v) => {
      if (!v.s||!v.v) return null;
      const o = v.o ? v.o.cn : ''; const opy = v.o ? ' '+v.o.py : ''; const oid = v.o ? ' '+v.o.id : '';
      return { cn: v.s.cn+'想'+v.v.cn+o+'。', py: v.s.py+' xiǎng '+v.v.py+opy+'.', id: v.s.id+' ingin '+v.v.id+oid+'.' };
    },
  },

  'F-qing': {
    name: '请 (mohon/tolong)', formula: '请 + V + O',
    tip: '<strong>请 (qǐng)</strong> = "tolong/mohon". Biasanya tanpa subjek eksplisit.',
    slots: [
      { id:'qing', label:'',           required:true,  fixed:{ cn:'请', py:'qǐng', id:'tolong' } },
      { id:'v',    label:'Kata Kerja', required:true,  pool:'kata_kerja' },
      { id:'o',    label:'Objek',      required:false, pool:'objek_umum' },
    ],
    examples: [
      { cn:'请坐。',       py:'Qǐng zuò.',          id:'Silakan duduk.' },
      { cn:'请告诉我。',   py:'Qǐng gàosu wǒ.',     id:'Tolong beritahu saya.' },
    ],
    build: (v) => {
      if (!v.v) return null;
      const o = v.o ? v.o.cn : ''; const opy = v.o ? ' '+v.o.py : ''; const oid = v.o ? ' '+v.o.id : '';
      return { cn: '请'+v.v.cn+o+'。', py: 'Qǐng '+v.v.py+opy+'.', id: 'Tolong '+v.v.id+oid+'.' };
    },
  },

  'F-ba': {
    name: '把 (konstruksi BA)', formula: 'S + 把 + O + V',
    tip: '<strong>把 (bǎ)</strong> memindahkan objek ke depan KK untuk menekankan "apa yang diperlakukan". KK setelah 把 harus punya komplemen hasil.',
    slots: [
      { id:'s',  label:'Subjek',     required:true, pool:'subyek' },
      { id:'ba', label:'',           required:true, fixed:{ cn:'把', py:'bǎ', id:'(obj)' } },
      { id:'o',  label:'Objek',      required:true, pool:'objek_umum' },
      { id:'v',  label:'Kata Kerja', required:true, pool:'kata_kerja' },
    ],
    examples: [
      { cn:'我把书看完了。', py:'Wǒ bǎ shū kàn wán le.',  id:'Saya sudah selesai membaca buku itu.' },
      { cn:'他把饭吃完了。', py:'Tā bǎ fàn chī wán le.',  id:'Dia sudah menghabiskan nasinya.' },
    ],
    build: (v) => {
      if (!v.s||!v.o||!v.v) return null;
      return { cn: v.s.cn+'把'+v.o.cn+v.v.cn+'了。', py: v.s.py+' bǎ '+v.o.py+' '+v.v.py+'le.', id: v.s.id+' sudah '+v.v.id+' '+v.o.id+'.' };
    },
  },

  'F-bei': {
    name: '被 (kalimat pasif)', formula: 'S + 被 + Agen + V',
    tip: '<strong>被 (bèi)</strong> membentuk kalimat pasif. Biasanya dipakai untuk situasi negatif/tidak menyenangkan.',
    slots: [
      { id:'s',   label:'Penderita',  required:true, pool:'objek_umum' },
      { id:'bei', label:'',           required:true, fixed:{ cn:'被', py:'bèi', id:'di- (pasif)' } },
      { id:'ag',  label:'Pelaku',     required:true, pool:'subyek' },
      { id:'v',   label:'Kata Kerja', required:true, pool:'kata_kerja' },
    ],
    examples: [
      { cn:'书被他拿走了。', py:'Shū bèi tā ná zǒu le.', id:'Buku itu dibawa pergi olehnya.' },
    ],
    build: (v) => {
      if (!v.s||!v.ag||!v.v) return null;
      return { cn: v.s.cn+'被'+v.ag.cn+v.v.cn+'了。', py: v.s.py+' bèi '+v.ag.py+' '+v.v.py+'le.', id: v.s.id+' di-'+v.v.id+' oleh '+v.ag.id+'.' };
    },
  },

  'F-gei': {
    name: '给 (memberi kepada)', formula: 'S + 给 + Penerima + O',
    tip: '<strong>给 (gěi)</strong> = "memberi" atau penanda penerima. Bisa sebagai kata kerja atau preposisi.',
    slots: [
      { id:'s',    label:'Subjek',   required:true,  pool:'subyek' },
      { id:'gei',  label:'',         required:true,  fixed:{ cn:'给', py:'gěi', id:'memberi kepada' } },
      { id:'recv', label:'Penerima', required:true,  pool:'subyek' },
      { id:'o',    label:'Objek',    required:false, pool:'objek_umum' },
    ],
    examples: [
      { cn:'我给你书。',   py:'Wǒ gěi nǐ shū.',      id:'Saya memberi kamu buku.' },
      { cn:'妈妈给我钱。', py:'Māma gěi wǒ qián.',    id:'Ibu memberi saya uang.' },
    ],
    build: (v) => {
      if (!v.s||!v.recv) return null;
      const o = v.o ? v.o.cn : ''; const opy = v.o ? ' '+v.o.py : ''; const oid = v.o ? ' '+v.o.id : '';
      return { cn: v.s.cn+'给'+v.recv.cn+o+'。', py: v.s.py+' gěi '+v.recv.py+opy+'.', id: v.s.id+' memberi '+v.recv.id+oid+'.' };
    },
  },

  'F-cong-dao': {
    name: '从…到 (dari…ke)', formula: 'S + 从 + A + 到 + B',
    tip: '<strong>从 (cóng)</strong> = "dari", <strong>到 (dào)</strong> = "ke/sampai". Bisa untuk tempat maupun waktu.',
    slots: [
      { id:'s',    label:'Subjek', required:true,  pool:'subyek' },
      { id:'cong', label:'',       required:true,  fixed:{ cn:'从', py:'cóng', id:'dari' } },
      { id:'a',    label:'Asal',   required:true,  pool:'tempat' },
      { id:'dao',  label:'',       required:true,  fixed:{ cn:'到', py:'dào', id:'ke' } },
      { id:'b',    label:'Tujuan', required:true,  pool:'tempat' },
      { id:'v',    label:'KK',     required:false, pool:'kata_kerja' },
    ],
    examples: [
      { cn:'我从家到学校。', py:'Wǒ cóng jiā dào xuéxiào.', id:'Saya dari rumah ke sekolah.' },
    ],
    build: (v) => {
      if (!v.s||!v.a||!v.b) return null;
      const vv = v.v ? v.v.cn : '走'; const vpy = v.v ? ' '+v.v.py : ' zǒu'; const vid = v.v ? ' '+v.v.id : ' pergi';
      return { cn: v.s.cn+'从'+v.a.cn+'到'+v.b.cn+vv+'。', py: v.s.py+' cóng '+v.a.py+' dào '+v.b.py+vpy+'.', id: v.s.id+vid+' dari '+v.a.id+' ke '+v.b.id+'.' };
    },
  },

};




/* ═══════════════════════════════════════════════════════════════
   wordbuilder.html — PART 4: Engine render slot, event handler,
   output builder, aksi, init + gabung_wordbuilder.py
═══════════════════════════════════════════════════════════════ */

/* ── STATE ─────────────────────────────────────────────────── */

// -*- coding: utf-8 -*-
// Beautified 2026-07-07 World Cup Predictions DOCX
// All data from player_database_0707.md + corrected lineups
const fs = require('fs');
const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
  Header, Footer, AlignmentType, PageOrientation, HeadingLevel,
  BorderStyle, WidthType, ShadingType, PageNumber, PageBreak,
  LevelFormat, TabStopType, TabStopPosition,
} = require('docx');

// ── Colors ──
const NAVY   = "1A2E3D";
const DARK   = "1A1A2E";
const RED    = "C0392B";
const BLUE   = "2E75B6";
const GRAY   = "7F8C8D";
const LGRAY  = "95A5A6";
const WHITE  = "FFFFFF";
const BG_ALT = "F5F7FA";
const BG_HDR = "1A1A2E";
const BG_PREF = "E8F5E9";
const BG_WARN = "FFF3E0";
const ORANGE = "F39C12";
const FONT = "Arial";

// ── Helpers ──
const border = (color="D0D5DD") => ({ style: BorderStyle.SINGLE, size: 1, color });
const borders = (c) => ({ top: border(c), bottom: border(c), left: border(c), right: border(c) });
const cellMargins = { top: 60, bottom: 60, left: 100, right: 100 };

function txt(text, opts={}) {
  return new TextRun({ text, font: FONT, size: opts.size || 21, bold: opts.bold, color: opts.color || DARK, ...(opts.font ? { font: opts.font } : {}) });
}

function hdrCell(text, width, opts={}) {
  return new TableCell({
    width: { size: width, type: WidthType.DXA }, borders: borders("152938"), shading: { fill: BG_HDR, type: ShadingType.CLEAR },
    margins: cellMargins,
    verticalAlign: "center",
    children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [txt(text, { size: 16, bold: true, color: WHITE })] })]
  });
}

function cell(text, width, opts={}) {
  const bg = opts.bg;
  const clr = opts.color;
  const children = [new Paragraph({
    alignment: opts.align === 'left' ? AlignmentType.LEFT : AlignmentType.CENTER,
    children: [txt(text, { size: opts.size || 16, bold: opts.bold, color: clr || DARK })]
  })];
  return new TableCell({
    width: { size: width, type: WidthType.DXA }, borders: borders("D0D5DD"), margins: cellMargins,
    shading: bg ? { fill: bg, type: ShadingType.CLEAR } : undefined,
    verticalAlign: "center",
    children,
  });
}

function emptyRow(widths, count = 1) {
  return Array.from({ length: count }, () =>
    new TableRow({ children: widths.map(w => cell("", w)) })
  );
}

function heading(title, level=1) {
  const sizes = { 1: 32, 2: 26, 3: 22 };
  return new Paragraph({
    spacing: { before: level === 1 ? 280 : 200, after: level === 1 ? 120 : 80 },
    children: [txt(title, { size: sizes[level] || 22, bold: true, color: level === 1 ? RED : DARK })]
  });
}

function para(text, opts={}) {
  return new Paragraph({
    spacing: { before: opts.before || 40, after: opts.after || 80 },
    alignment: opts.center ? AlignmentType.CENTER : AlignmentType.LEFT,
    children: [txt(text, { size: opts.size || 20, bold: opts.bold, color: opts.color || (opts.dim ? GRAY : DARK) })]
  });
}

function meta(text) {
  return new Paragraph({
    spacing: { before: 0, after: 60 },
    children: [txt(text, { size: 14, color: LGRAY })]
  });
}

function spacer() { return new Paragraph({ spacing: { before: 80, after: 80 }, children: [] }); }

// ── CONTENT ──

const children = [];

// Title Page
children.push(new Paragraph({ spacing: { before: 600 }, children: [] }));
children.push(new Paragraph({
  alignment: AlignmentType.CENTER, spacing: { after: 60 },
  children: [txt("2026 FIFA 世界杯", { size: 52, bold: true, color: RED })]
}));
children.push(new Paragraph({
  alignment: AlignmentType.CENTER, spacing: { after: 80 },
  children: [txt("7月7日  16强淘汰赛  预测报告", { size: 34, bold: true, color: DARK })]
}));
children.push(new Paragraph({
  alignment: AlignmentType.CENTER, spacing: { after: 120 },
  children: [txt("葡萄牙 vs 西班牙         美国 vs 比利时", { size: 22, color: GRAY })]
}));
children.push(new Paragraph({
  alignment: AlignmentType.CENTER, spacing: { after: 40 },
  children: [txt("Round of 16  ·  AT&T Stadium (达拉斯) / Lumen Field (西雅图)", { size: 20, color: GRAY })]
}));
children.push(spacer());
children.push(meta("生成时间: 2026年7月7日 北京时间  |  数据来源: player_database_0707.md + Sporting News + Fox Sports"));
children.push(meta("分析框架: CLAUDE.md v18 (铁律10-14全系生效)  |  Illmer & Daumann (2022) 系统综述交叉验证"));
children.push(new Paragraph({
  alignment: AlignmentType.CENTER, spacing: { before: 200, after: 80 },
  children: [txt("[修正] C罗评分 8.0 → 7.0 (€8M, 对强队0运动战进球)  |  ESP首发修正 (波罗+奥尔莫)  |  BEL首发修正 (梅赫勒+瓦纳肯+德克特拉雷)", { size: 16, color: RED })]
}));
children.push(new Paragraph({ children: [new PageBreak()] }));

// ── 1. SUMMARY ──
children.push(heading("一、预测汇总"));
children.push(meta("所有时间均为北京时间 (UTC+8)  |  数据截至 7月7日 00:30 BJT"));

const sumWidths = [600, 2300, 900, 1200, 2000, 800, 2400, 900];
children.push(new Table({
  width: { size: 11600, type: WidthType.DXA },
  columnWidths: sumWidths,
  rows: [
    new TableRow({ children: ["#,比赛 (BJT),身价比,强队分类,首选比分,半场,备选比分,冷门风险".split(",").map((t,i) => hdrCell(t, sumWidths[i]))] }),
    new TableRow({ children: [
      cell("93", sumWidths[0]), cell("POR vs ESP\n(03:00)", sumWidths[1], {align:'left'}),
      cell("1:1.32", sumWidths[2]), cell("双方均\n超巨型", sumWidths[3]),
      cell("西班牙 2-1\n葡萄牙", sumWidths[4], {bold:true, bg:BG_PREF}),
      cell("1-0", sumWidths[5], {bg:BG_PREF}),
      cell("1-1(加时/点球)  / 2-0  / 葡萄牙2-1", sumWidths[6], {align:'left', bg:BG_PREF}),
      cell("中高", sumWidths[7], {bold:true, color:WHITE, bg:ORANGE}),
    ]}),
    new TableRow({ children: [
      cell("94", sumWidths[0]),
      cell("USA vs BEL\n(08:00)", sumWidths[1], {align:'left'}),
      cell("1:1.54", sumWidths[2]),
      cell("BEL:\n体系型", sumWidths[3]),
      cell("美国 2-1\n比利时", sumWidths[4], {bold:true, bg:BG_PREF}),
      cell("1-0", sumWidths[5], {bg:BG_PREF}),
      cell("1-1(加时)  / 2-0  / 比利时2-1", sumWidths[6], {align:'left', bg:BG_PREF}),
      cell("中", sumWidths[7], {bold:true, color:WHITE, bg:ORANGE}),
    ]}),
  ]
}));
children.push(spacer());

// ── 2. MATCH 93: POR vs ESP ──
children.push(heading("二、比赛93: 葡萄牙 vs 西班牙"));
children.push(meta("7月7日 03:00 BJT  |  AT&T Stadium, 达拉斯  |  室内球场, 气候受控  |  FIFA #7 vs #3  |  身价比: €957M vs €1.267B (1:1.32)"));
children.push(para("西班牙4场零封(12-0) · 葡萄牙4场失4球 · 威廉斯缺阵 · C罗对强队0运动战进球", { dim: true, size: 18 }));

children.push(para("预测首发 (player_database_0707.md + 媒体交叉验证)", { bold: true, size: 20 }));
children.push(para("POR (4-2-3-1): 迪奥戈·科斯塔 | 坎塞洛  鲁本·迪亚斯[黄]  雷纳托·韦加  努诺·门德斯 | 维蒂尼亚  若昂·内维斯 | 佩德罗·内托  B费  拉斐尔·莱昂 | C罗", { size: 18, color: DARK }));
children.push(para("ESP (4-3-3): 乌奈·西蒙 | 佩德罗·波罗  库巴西  拉波尔特  库库雷利亚 | 罗德里  佩德里  奥尔莫 | 亚马尔  奥亚萨瓦尔  巴埃纳", { size: 18, color: DARK }));
children.push(para("[修正] ESP RB波罗(热刺€50M, 对奥地利进球!) | AM奥尔莫(巴萨€50M) | POR LW莱昂(€90M, 对克罗地亚助攻)", { size: 14, color: RED }));
children.push(spacer());

// Player ratings table
children.push(para("核心球员评分", { bold: true, size: 20, color: BLUE }));
const prw = [700, 2500, 600, 1000, 5800]; // total 10600
const prData = [
  ["#", "球员", "评分", "位置", "关键信息"],
  ["16", "罗德里 (ESP)", "9.0", "DM", "[MOTM候选] 金球奖得主 · 曼城 · €130M"],
  ["19", "拉明·亚马尔 (ESP)", "9.0", "RW", "[MOTM候选] 18岁 · €200M · 本届最佳边锋"],
  ["21", "奥亚萨瓦尔 (ESP)", "8.5", "ST", "4球 · 近16场首发17球 · 皇社€45M"],
  ["20", "佩德里 (ESP)", "8.5", "CM", "巴萨核心 · €80M"],
  ["8", "B费 (POR)", "8.5", "AM", "[关键] 曼联 · €85M · 创造力中枢"],
  ["4", "鲁本·迪亚斯 (POR)", "8.5", "CB", "[黄牌] 曼城 · €80M · 背牌收敛30%"],
  ["2", "佩德罗·波罗 (ESP)", "8.0", "RB", "[修正] 热刺€50M · 对奥地利头球破门"],
  ["23", "乌奈·西蒙 (ESP)", "8.0", "GK", "519分钟不失球纪录 · 毕尔巴鄂€25M"],
  ["17", "拉斐尔·莱昂 (POR)", "8.0", "LW", "[修正] AC米兰€90M · 对克罗地亚助攻"],
  ["10", "达尼·奥尔莫 (ESP)", "8.0", "AM", "[修正] 巴萨€50M · 7/4训练减量但可出战"],
  ["7", "C罗 (POR/C)", "7.0", "ST", "[修正] 41岁 · €8M · 对强队0运动战进球 · 仅点球+定位球威胁"],
  ["9", "贡萨洛·拉莫斯 (POR)", "7.5", "ST", "[超级替补] PSG€50M · 90+4绝杀克罗地亚"],
  ["—", "尼科·威廉斯 (ESP)", "—", "LW", "[缺席] 内收肌伤 · 左路爆破减半"],
];
children.push(new Table({
  width: { size: 10600, type: WidthType.DXA },
  columnWidths: prw,
  rows: prData.map((row, ri) => {
    const isHdr = ri === 0;
    const isMotm = row[4] && row[4].includes('MOTM候选');
    const bg = isHdr ? BG_HDR : (isMotm ? BG_PREF : (ri % 2 === 0 ? BG_ALT : undefined));
    return new TableRow({ children: row.map((t, ci) => {
      const isWarn = t.includes('[修正]') || t.includes('[黄牌]') || t.includes('[缺席]');
      return new TableCell({
        width: { size: prw[ci], type: WidthType.DXA }, borders: borders(isHdr ? "152938" : "D0D5DD"), margins: cellMargins,
        shading: bg ? { fill: bg, type: ShadingType.CLEAR } : undefined,
        verticalAlign: "center",
        children: [new Paragraph({
          alignment: ci === 1 || ci === 4 ? AlignmentType.LEFT : AlignmentType.CENTER,
          children: [txt(t, { size: 15, bold: isHdr, color: isHdr ? WHITE : (isWarn ? RED : DARK) })]
        })]
      });
    })});
  })
}));
children.push(spacer());

// Factors table
children.push(para("因素导向表", { bold: true, size: 20, color: BLUE }));
const fw = [5200, 1400, 4000];
const ftData = [
  ["因素", "有利", "理由"],
  ["西班牙体系完整: 4场12-0(零封)", "ESP ★★", "铁律12降级: 零封对手均非超巨型 · 从未面对C罗+B费+莱昂级攻击线"],
  ["尼科·威廉斯缺阵: 左路爆破减半", "POR ★★", "巴埃纳(€50M)远不如威廉斯(€60M) · 坎塞洛防守压力大减"],
  ["C罗+B费+莱昂: 3核心攻击线", "POR ★★★", "莱昂€90M + B费€85M · C罗€8M对强队0运动战进球—非超巨"],
  ["C罗对强队0运动战进球", "ESP ★★", "[修正] 对乌兹别克外仅点球 · 面对4场零封防线运动战破门概率极低"],
  ["葡萄牙防守不稳: 4场失4球", "ESP ★★", "对刚果金+哥伦比亚均失球 · 面对西班牙12-0控制力=最大考验"],
  ["亚马尔 vs 门德斯: €200M vs PSG", "ESP ★★", "西班牙最强对位 · 亚马尔可内切可传中"],
  ["罗德里 vs 维蒂尼亚: 金球奖vs欧冠冠军", "ESP ★★", "罗德里世界第一 · 维蒂尼亚+内维斯=PSG欧冠级不弱"],
  ["室内球场: 气候受控", "均势", "纯实力对决 · 西班牙体系优势被放大"],
  ["2025欧国联决赛: 葡萄牙点球胜", "POR ★", "最近交手心理优势 · 但世界杯≠欧国联"],
];
children.push(new Table({
  width: { size: 10600, type: WidthType.DXA },
  columnWidths: fw,
  rows: ftData.map((row, ri) => {
    const isHdr = ri === 0;
    const isPor = row[1] && row[1].includes('POR');
    const isEsp = row[1] && row[1].includes('ESP');
    const clr = row[1] === '均势' ? undefined : (isPor ? RED : BLUE);
    return new TableRow({ children: row.map((t, ci) => {
      return new TableCell({
        width: { size: fw[ci], type: WidthType.DXA }, borders: borders(isHdr ? "152938" : "D0D5DD"), margins: cellMargins,
        shading: isHdr ? { fill: BG_HDR, type: ShadingType.CLEAR } : undefined,
        verticalAlign: "center",
        children: [new Paragraph({
          alignment: ci < 2 ? AlignmentType.CENTER : AlignmentType.LEFT,
          children: [txt(t, { size: 16, bold: isHdr || ci === 1, color: isHdr ? WHITE : (ci === 1 ? clr : DARK) })]
        })]
      });
    })});
  })
}));
children.push(spacer());

children.push(para("强队分类: 葡萄牙(超级巨星型, €957M: B费€85M+莱昂€90M+迪亚斯€80M) vs 西班牙(超级巨星型, €1.267B: 亚马尔€200M+罗德里€130M+佩德里€80M)", { size: 18, dim: true }));
children.push(para("冷门风险: 中高 — 西班牙4场零封含金量待检验(铁律12) | 葡萄牙超巨破局能力不可低估 | 威廉斯缺阵=左路降半级", { size: 18, bold: true, color: ORANGE }));
children.push(spacer());

// Prediction table
children.push(para("比分预测", { bold: true, size: 20, color: BLUE }));
const predw = [1200, 2400, 800, 6200];
const predData = [
  ["类型", "比分", "半场", "进球者与逻辑"],
  ["[首选]", "西班牙 2-1 葡萄牙", "1-0", "奥亚萨瓦尔31'(亚马尔传中) / C罗58'(点球—唯一得分路径) / 佩德里73'(远射)"],
  ["备选1", "1-1 (葡萄牙加时/点球)", "0-0", "C罗67'(点) / 亚马尔82'. 双方谨慎→葡萄牙加时深度(莱昂+拉莫斯+B席)优势"],
  ["备选2", "西班牙 2-0 葡萄牙", "1-0", "亚马尔24' / 奥亚萨瓦尔55'. 零封延续至6场 · 威廉斯缺阵不影响体系"],
  ["冷门", "葡萄牙 2-1 西班牙", "0-1", "亚马尔18' / C罗44'(点) / 莱昂79'(替补爆波罗). C罗禁区经验制造点球+莱昂速度绝杀"],
];
children.push(new Table({
  width: { size: 10600, type: WidthType.DXA },
  columnWidths: predw,
  rows: predData.map((row, ri) => {
    const isHdr = ri === 0;
    const isPref = ri === 1;
    const isUpset = ri === 4;
    const bg = isHdr ? BG_HDR : (isPref ? BG_PREF : (isUpset ? BG_WARN : undefined));
    const clr = isHdr ? WHITE : (isUpset ? RED : DARK);
    return new TableRow({ children: row.map((t, ci) => {
      return new TableCell({
        width: { size: predw[ci], type: WidthType.DXA }, borders: borders(isHdr ? "152938" : "D0D5DD"), margins: cellMargins,
        shading: bg ? { fill: bg, type: ShadingType.CLEAR } : undefined,
        verticalAlign: "center",
        children: [new Paragraph({
          alignment: ci === 3 ? AlignmentType.LEFT : AlignmentType.CENTER,
          children: [txt(t, { size: 16, bold: isHdr || ci <= 1, color: clr })]
        })]
      });
    })});
  })
}));
children.push(spacer());

// Key battles
children.push(para("关键对位", { bold: true, size: 20, color: BLUE }));
const bw = [2400, 4400, 3800];
const btData = [
  ["对位", "详情", "预判"],
  ["库巴西(18) vs C罗(41)", "巴萨18岁天才 vs 41岁6届传奇 · 经验差23年", "C罗运动战难破门 · 禁区经验可制造点球"],
  ["亚马尔 vs 努诺·门德斯", "€200M超巨 vs PSG左后卫€65M · 西班牙最强对位", "亚马尔传中→奥亚萨瓦尔终结 · 西班牙最大优势"],
  ["罗德里 vs B费", "金球奖后腰 vs 创造力核心 · 若B费被锁=POR攻击瘫痪", "罗德里大概率限制B费 · 葡萄牙需第二方案"],
  ["波罗 vs 莱昂", "热刺RB€50M(对奥地利进球) vs AC米兰€90M", "莱昂速度占优 · 波罗进攻强于防守"],
];
children.push(new Table({
  width: { size: 10600, type: WidthType.DXA },
  columnWidths: bw,
  rows: btData.map((row, ri) => {
    return new TableRow({ children: row.map((t, ci) => {
      return new TableCell({
        width: { size: bw[ci], type: WidthType.DXA }, borders: borders(ri === 0 ? "152938" : "D0D5DD"), margins: cellMargins,
        shading: ri === 0 ? { fill: BG_HDR, type: ShadingType.CLEAR } : undefined,
        verticalAlign: "center",
        children: [new Paragraph({
          alignment: ci === 0 ? AlignmentType.CENTER : AlignmentType.LEFT,
          children: [txt(t, { size: 16, bold: ri === 0 || ci === 0, color: ri === 0 ? WHITE : DARK })]
        })]
      });
    })});
  })
}));

children.push(new Paragraph({ children: [new PageBreak()] }));

// ── 3. MATCH 94: USA vs BEL ──
children.push(heading("三、比赛94: 美国 vs 比利时"));
children.push(meta("7月7日 08:00 BJT  |  Lumen Field, 西雅图  |  68,740人满座  |  FIFA #11 vs #5  |  身价比: ~€345M vs €530M (1:1.54)"));
children.push(para("巴洛贡红牌撤销确认复出 · 多库 vs 里姆(37岁)致命对位 · 德布劳内本届0助攻 · 比利时防线老龄化", { dim: true, size: 18 }));

children.push(para("预测首发 (player_database_0707.md + 媒体交叉验证)", { bold: true, size: 20 }));
children.push(para("USA (4-2-3-1): 弗里兹 | 弗里曼  理查兹  里姆(37)  罗宾逊 | 亚当斯  蒂尔曼 | 德斯特  麦肯尼  普利西奇(C) | 巴洛贡", { size: 18, color: DARK }));
children.push(para("BEL (4-2-3-1): 库尔图瓦 | 卡斯塔涅  梅赫勒  泰特  德克伊珀 | 蒂勒曼斯(C)  瓦纳肯 | 多库  德布劳内(C)  特罗萨尔 | 德克特拉雷", { size: 18, color: DARK }));
children.push(para("[修正] BEL: CB梅赫勒(€5M)替代法斯 | CM瓦纳肯(€6M工兵)替代奥纳纳 | CF德克特拉雷€40M(卢卡库=超级替补) | 德布劳内=那不勒斯/0助攻/未踢满90' | 多库本届0球0助", { size: 14, color: RED }));
children.push(spacer());

// USA/BEL Player ratings
children.push(para("核心球员评分", { bold: true, size: 20, color: BLUE }));
const pr2w = [700, 2500, 600, 1000, 5800];
const pr2Data = [
  ["#", "球员", "评分", "位置", "关键信息"],
  ["1", "库尔图瓦 (BEL)", "9.0", "GK", "[MOTM候选] 皇马€25M · 2014在此对美国15扑"],
  ["10", "普利西奇 (USA/C)", "8.5", "LW", "[关键] AC米兰€50M · 美国队长"],
  ["9", "巴洛贡 (USA)", "8.5", "ST", "[注意] 3球/4场 · 红牌撤销复出! · 状态待验证(铁律11)"],
  ["8", "蒂勒曼斯 (BEL/C)", "8.5", "CM", "[MOTM候选] 维拉€35M · 89'扳平+120+5'点球 · 本届英雄"],
  ["10", "多库 (BEL)", "8.5", "RW", "[MOTM候选] 曼城€60M · 本届0球0助 · 但对37岁里姆速度碾压"],
  ["5", "罗宾逊 (USA)", "8.0", "LB", "富勒姆€30M · 本届最佳左后卫之一"],
  ["6", "麦肯尼 (USA)", "8.0", "AM", "尤文€25M · 对抗+跑动覆盖巨大"],
  ["11", "特罗萨尔 (BEL)", "8.0", "LW", "[关键] 阿森纳€45M · 2球1助—常规攻击最强点"],
  ["7", "德布劳内 (BEL/C)", "7.5", "AM", "[修正] 那不勒斯€55M · 35岁/0助攻/未踢满90'/R32被56'换下"],
  ["9", "卢卡库 (BEL)", "7.5", "ST", "[超级替补] 罗马€20M · 86'救命球 · 仅适合30分钟冲刺"],
  ["4", "梅赫勒 (BEL)", "6.5", "CB", "[弱点/修正] 布鲁日€5M · 对塞内加尔被打穿—速度不足"],
  ["13", "蒂姆·里姆 (USA)", "7.0", "CB", "[注意] 37岁€1M · 速度vs多库=致命对位 · 亚当斯须协防"],
  ["17", "德克特拉雷 (BEL)", "7.0", "ST", "[修正] 亚特兰大€40M · 首发CF—R32无进球被换下"],
];
children.push(new Table({
  width: { size: 10600, type: WidthType.DXA },
  columnWidths: pr2w,
  rows: pr2Data.map((row, ri) => {
    const isHdr = ri === 0;
    const isMotm = row[4] && row[4].includes('MOTM候选');
    const isWarn = row[4] && (row[4].includes('[注意]') || row[4].includes('[弱点') || row[4].includes('[修正]'));
    const bg = isHdr ? BG_HDR : (isMotm ? BG_PREF : (ri % 2 === 0 ? BG_ALT : undefined));
    return new TableRow({ children: row.map((t, ci) => {
      return new TableCell({
        width: { size: pr2w[ci], type: WidthType.DXA }, borders: borders(isHdr ? "152938" : "D0D5DD"), margins: cellMargins,
        shading: bg ? { fill: bg, type: ShadingType.CLEAR } : undefined,
        verticalAlign: "center",
        children: [new Paragraph({
          alignment: ci === 1 || ci === 4 ? AlignmentType.LEFT : AlignmentType.CENTER,
          children: [txt(t, { size: 15, bold: isHdr, color: isHdr ? WHITE : (isWarn ? RED : DARK) })]
        })]
      });
    })});
  })
}));
children.push(spacer());

// USA/BEL Factors
children.push(para("因素导向表", { bold: true, size: 20, color: BLUE }));
const ft2Data = [
  ["因素", "有利", "理由"],
  ["美国主场: 68,740人满座", "USA ★★★", "本届主场全胜 · 波切蒂诺称'美国足球史上最大比赛'"],
  ["巴洛贡复出: 红牌撤销, 3球射手回归", "USA ★★★", "[注意] 攻击力恢复双核 · 但停赛期训练状态待验证(铁律11)"],
  ["多库 vs 里姆(37): 速度碾压", "BEL ★★★", "最致命对位 · 多库本届0球0助但速度威胁真实 · 亚当斯须协防"],
  ["库尔图瓦: 世界前三门将", "BEL ★★★", "淘汰赛门将模式 · 但对塞内加尔失2球"],
  ["德布劳内低迷: 35岁/0助攻/未踢满90'", "USA ★★", "R32被56'换下后球队反而逆转 · 亚当斯可针对性锁死"],
  ["比利时防线速度慢: 梅赫勒被打穿", "USA ★★", "梅赫勒(€5M)对塞内加尔被爆 · 巴洛贡+普利西奇速度可碾压"],
  ["美国Pochettino高位逼抢", "USA ★★", "对比利时老龄后场出球=噩梦 · 逼抢→失误→反击得分"],
  ["比利时攻击便秘: R32前86分钟0射正", "USA ★★", "对伊朗10人0-0 · 对埃及1-1 · 有组织防守时进攻乏力"],
];
children.push(new Table({
  width: { size: 10600, type: WidthType.DXA },
  columnWidths: fw,
  rows: ft2Data.map((row, ri) => {
    const isHdr = ri === 0;
    const isUsa = row[1] && row[1].includes('USA');
    const clr = row[1] === '均势' ? undefined : (isUsa ? BLUE : RED);
    return new TableRow({ children: row.map((t, ci) => {
      return new TableCell({
        width: { size: fw[ci], type: WidthType.DXA }, borders: borders(isHdr ? "152938" : "D0D5DD"), margins: cellMargins,
        shading: isHdr ? { fill: BG_HDR, type: ShadingType.CLEAR } : undefined,
        verticalAlign: "center",
        children: [new Paragraph({
          alignment: ci < 2 ? AlignmentType.CENTER : AlignmentType.LEFT,
          children: [txt(t, { size: 16, bold: isHdr || ci === 1, color: isHdr ? WHITE : (ci === 1 ? clr : DARK) })]
        })]
      });
    })});
  })
}));
children.push(spacer());

children.push(para("强队分类: 比利时=体系型(德布劳内€55M未达超巨阈值+0助攻 · 多库€60M核心级0球0助 · 对塞内加尔86分钟0射正验证). 美国=非强队方(主场等效~€345M, 无超巨)", { size: 18, dim: true }));
children.push(para("冷门风险: 中 — 身价比1:1.54五五开 | 比利时老龄防线vs美国年轻锋线 | 库尔图瓦+多库可单场决定 | 多库vs里姆致命", { size: 18, bold: true, color: ORANGE }));
children.push(spacer());

// USA/BEL Predictions
children.push(para("比分预测", { bold: true, size: 20, color: BLUE }));
const pd2Data = [
  ["类型", "比分", "半场", "进球者与逻辑"],
  ["[首选]", "美国 2-1 比利时", "1-0", "巴洛贡27'(普利西奇助攻) / 多库52'(单人突破里姆) / 麦肯尼68'(角球混战). 主场+高位逼抢vs老龄防线"],
  ["备选1", "1-1 (加时/点球)", "0-0", "卢卡库72'(替补头球) / 巴洛贡85'. 双方谨慎→加时美国深度稍优"],
  ["备选2", "美国 2-0 比利时", "1-0", "普利西奇34' / 巴洛贡61'. 比利时防线被逼抢撕碎 · 库尔图瓦无力回天"],
  ["冷门", "比利时 2-1 美国", "0-1", "德布劳内38'(直塞) / 卢卡库55' / 雷纳90+2'. 库尔图瓦5+神扑模式 · 多库爆里姆"],
];
children.push(new Table({
  width: { size: 10600, type: WidthType.DXA },
  columnWidths: predw,
  rows: pd2Data.map((row, ri) => {
    const isHdr = ri === 0;
    const isPref = ri === 1;
    const isUpset = ri === 4;
    const bg = isHdr ? BG_HDR : (isPref ? BG_PREF : (isUpset ? BG_WARN : undefined));
    const clr = isHdr ? WHITE : (isUpset ? RED : DARK);
    return new TableRow({ children: row.map((t, ci) => {
      return new TableCell({
        width: { size: predw[ci], type: WidthType.DXA }, borders: borders(isHdr ? "152938" : "D0D5DD"), margins: cellMargins,
        shading: bg ? { fill: bg, type: ShadingType.CLEAR } : undefined,
        verticalAlign: "center",
        children: [new Paragraph({
          alignment: ci === 3 ? AlignmentType.LEFT : AlignmentType.CENTER,
          children: [txt(t, { size: 16, bold: isHdr || ci <= 1, color: clr })]
        })]
      });
    })});
  })
}));
children.push(spacer());

// USA/BEL Key battles
children.push(para("关键对位", { bold: true, size: 20, color: BLUE }));
const bt2Data = [
  ["对位", "详情", "预判"],
  ["多库 vs 里姆(37)", "曼城速度爆点 vs 37岁老将 · BEL最强对位", "多库大概率爆点 · 美国需双人包夹 · 若里姆被罚下=比赛转折"],
  ["巴洛贡 vs 梅赫勒", "3球射手刚复出 vs €5M被打穿过中卫", "高位逼抢下梅赫勒出球失误率高 · 美国得分窗口"],
  ["亚当斯 vs 德布劳内", "伯恩茅斯DM vs 35岁那不勒斯0助攻中场", "德布劳内本届低迷但一脚传球仍可致命"],
  ["库尔图瓦 vs 美国攻击群", "世界级门将 vs 巴洛贡+普利西奇+麦肯尼", "库尔图瓦会神扑 · 但无法阻止所有射门"],
];
children.push(new Table({
  width: { size: 10600, type: WidthType.DXA },
  columnWidths: bw,
  rows: bt2Data.map((row, ri) => {
    return new TableRow({ children: row.map((t, ci) => {
      return new TableCell({
        width: { size: bw[ci], type: WidthType.DXA }, borders: borders(ri === 0 ? "152938" : "D0D5DD"), margins: cellMargins,
        shading: ri === 0 ? { fill: BG_HDR, type: ShadingType.CLEAR } : undefined,
        verticalAlign: "center",
        children: [new Paragraph({
          alignment: ci === 0 ? AlignmentType.CENTER : AlignmentType.LEFT,
          children: [txt(t, { size: 16, bold: ri === 0 || ci === 0, color: ri === 0 ? WHITE : DARK })]
        })]
      });
    })});
  })
}));
children.push(spacer());
children.push(spacer());

// ── 4. NOTES ──
children.push(heading("四、修正说明与分析框架"));
children.push(para("C罗评分修正: C罗41岁, €8M身价(沙特联赛). 本届: 5-0乌兹别克斯坦2球(运动战/弱队) + 对克罗地亚点球. 对强队0运动战进球. 评分8.0/MOTM候选→7.0. 主要威胁仅限点球+定位球头球, 非运动战破局者.", { size: 18, color: RED }));
children.push(para("西班牙首发修正: RB波罗(€50M热刺, 对奥地利进球)替代略伦特. AM奥尔莫(€50M巴萨)替代梅里诺. 来源: player_database_0707.md R32实际首发.", { size: 18, color: RED }));
children.push(para("比利时首发修正: CB梅赫勒(€5M)替代法斯. CM瓦纳肯(€6M)替代奥纳纳. CF德克特拉雷(€40M)替代卢卡库. 卢卡库=超级替补(86'救命球). 德布劳内=那不勒斯/0助攻. 多库=本届0球0助.", { size: 18, color: RED }));
children.push(para("系统综述交叉验证 (Illmer & Daumann 2022, 21篇研究): 降雨无效应 [已确认] | 海拔降身体不降技术 [已确认] | 温度需条件分支 [已确认] | 风影响进攻 [待纳入]", { size: 18, dim: true }));
children.push(para(""));
children.push(meta("───"));
children.push(meta("数据源: player_database_0707.md + Sporting News + Fox Sports + RotoWire + Illmer & Daumann (2022)"));
children.push(meta("框架: CLAUDE.md v18 (铁律10-14全系生效) | 生成工具: docx-js"));

// ── BUILD ──
const doc = new Document({
  styles: {
    default: { document: { run: { font: "Arial", size: 21 } } },
  },
  sections: [{
    properties: {
      page: {
        size: { width: 12240, height: 15840, orientation: PageOrientation.LANDSCAPE },
        margin: { top: 900, right: 900, bottom: 900, left: 900 },
      },
    },
    headers: {
      default: new Header({
        children: [new Paragraph({
          alignment: AlignmentType.RIGHT,
          border: { bottom: { style: BorderStyle.SINGLE, size: 4, color: LGRAY, space: 4 } },
          children: [txt("2026 FIFA World Cup  ·  7月7日 预测报告", { size: 14, color: LGRAY })],
        })]
      }),
    },
    footers: {
      default: new Footer({
        children: [new Paragraph({
          alignment: AlignmentType.CENTER,
          border: { top: { style: BorderStyle.SINGLE, size: 4, color: LGRAY, space: 4 } },
          children: [txt("Page ", { size: 14, color: LGRAY }), new TextRun({ children: [PageNumber.CURRENT], font: FONT, size: 14, color: LGRAY })],
        })]
      }),
    },
    children,
  }],
});

const OUT = __dirname + "\\2026年7月7日_两场预测_beautified.docx";
Packer.toBuffer(doc).then(buf => {
  fs.writeFileSync(OUT, buf);
  console.log(`Saved to ${OUT}`);
  console.log(`  File size: ${buf.length.toLocaleString()} bytes`);
});

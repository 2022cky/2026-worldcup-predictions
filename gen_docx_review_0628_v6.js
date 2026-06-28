// DOCX v6 美化 — 2026年6月28日 六场复盘
// 基于 gen_docx_template.js v6 横向尺寸 + 完整组件
const fs = require("fs");
const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
  Header, Footer, AlignmentType, PageOrientation, BorderStyle, WidthType,
  ShadingType, PageNumber, PageBreak
} = require("docx");

// ═══ 版面 ═══
const FONT = "微软雅黑";
const PAGE_W = 11906, PAGE_H = 16838, MARGIN = 850, CW = PAGE_H - MARGIN * 2;

// ═══ 色板 ═══
const C = {
  HEADER_BG: "1A2E3D", HEADER_TEXT: "FFFFFF", ALT_ROW: "F5F7FA", PREF_ROW: "E8F5E9",
  BORDER: "D0D5DD", TITLE_RED: "C0392B", SUBTITLE: "1A1A2E", META: "7F8C8D",
  META_LIGHT: "95A5A6", ACCENT: "2E75B6", HIGH_RISK: "C0392B", GREEN: "27AE60",
};

const thinBorder = { style: BorderStyle.SINGLE, size: 1, color: C.BORDER };
const BORDERS = { top: thinBorder, bottom: thinBorder, left: thinBorder, right: thinBorder };

function tr(text, size, opts) {
  if (!opts) opts = {};
  return new TextRun({ text, font: FONT, size: (size || 10) * 2, bold: !!opts.bold, color: opts.color });
}
function para(text, size, opts) {
  if (!opts) opts = {};
  return new Paragraph({
    spacing: { after: opts.after !== undefined ? opts.after : 80, before: opts.before || 0 },
    alignment: opts.align || AlignmentType.LEFT,
    children: [tr(text, size || 10, opts)],
  });
}
function empty() { return new Paragraph({ spacing: { after: 40 }, children: [] }); }
function sep() {
  return new Paragraph({
    spacing: { before: 200, after: 200 },
    border: { bottom: { style: BorderStyle.SINGLE, size: 4, color: C.ACCENT, space: 1 } },
    children: [],
  });
}

function hdrCell(text, colW) {
  return new TableCell({
    borders: BORDERS, width: { size: colW, type: WidthType.DXA },
    shading: { fill: C.HEADER_BG, type: ShadingType.CLEAR }, verticalAlign: "center",
    margins: { top: 50, bottom: 50, left: 60, right: 60 },
    children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [tr(text, 9, { bold: true, color: C.HEADER_TEXT })] })],
  });
}
function datCell(text, colW, opts) {
  const o = opts || {};
  return new TableCell({
    borders: BORDERS, width: { size: colW, type: WidthType.DXA },
    shading: o.shading ? { fill: o.shading, type: ShadingType.CLEAR } : undefined, verticalAlign: "center",
    margins: { top: 40, bottom: 40, left: 60, right: 60 },
    children: [new Paragraph({ alignment: o.align || AlignmentType.CENTER, children: [tr(text, o.size || 9, { bold: !!o.bold, color: o.color })] })],
  });
}
function tblRow(cells) { return new TableRow({ children: cells }); }
function makeTable(colW, rows) {
  return new Table({ width: { size: CW, type: WidthType.DXA }, columnWidths: colW, rows });
}

// ── 汇总表 ──
const SW = [400, 720, 4200, 1200, 1100, 600, 700, 6218]; // sum = 15138 = CW
function buildSummary(rows) {
  const hdr = tblRow([
    hdrCell("#", SW[0]), hdrCell("时间", SW[1]), hdrCell("比赛", SW[2]),
    hdrCell("预测首选", SW[3]), hdrCell("实际比分", SW[4]), hdrCell("方向", SW[5]),
    hdrCell("比分", SW[6]), hdrCell("复盘", SW[7]),
  ]);
  const data = rows.map((r, i) => {
    const sh = i % 2 === 0 ? C.ALT_ROW : undefined;
    return tblRow(r.map((t, j) =>
      datCell(t, SW[j], { size: 8, bold: j === 4, align: j === 7 || j === 2 ? AlignmentType.LEFT : AlignmentType.CENTER, shading: sh })
    ));
  });
  return makeTable(SW, [hdr, ...data]);
}

// ── 3-column table ──
function threeColTbl(headers, rows) {
  const W = [3500, 3500, CW - 7000];
  const hdr = tblRow(headers.map((h, i) => hdrCell(h, W[i])));
  const data = rows.map((r, i) => tblRow(r.map((t, j) =>
    datCell(t, W[j], { size: 8, align: j === 2 ? AlignmentType.LEFT : AlignmentType.LEFT, shading: i % 2 === 0 ? C.ALT_ROW : undefined })
  )));
  return makeTable(W, [hdr, ...data]);
}

// ── 4-column pred vs actual ──
function predTbl(rows) {
  const W = [1500, 2000, 2000, CW - 5500];
  const hdr = tblRow([hdrCell("维度", W[0]), hdrCell("预测", W[1]), hdrCell("实际", W[2]), hdrCell("评估", W[3])]);
  const data = rows.map((r, i) => tblRow(r.map((t, j) =>
    datCell(t, W[j], { size: 8, bold: j === 0, align: j === 3 ? AlignmentType.LEFT : AlignmentType.CENTER, shading: i % 2 === 0 ? C.ALT_ROW : undefined })
  )));
  return makeTable(W, [hdr, ...data]);
}

// ── Goals table ──
function goalsTbl(rows) {
  const W = [800, 2800, 1200, CW - 4800];
  const hdr = tblRow([hdrCell("时间", W[0]), hdrCell("球员", W[1]), hdrCell("进球方", W[2]), hdrCell("备注", W[3])]);
  const data = rows.map((r, i) => tblRow(r.map((t, j) =>
    datCell(t, W[j], { size: 8, align: j === 3 || j === 1 ? AlignmentType.LEFT : AlignmentType.CENTER, shading: i % 2 === 0 ? C.ALT_ROW : undefined })
  )));
  return makeTable(W, [hdr, ...data]);
}

// ═══ Match data ═══
const matches = [
  {
    num: 1, title: "克罗地亚 2-1 加纳 (L组)",
    goals: [["31'", "苏契奇 (Petar SUCIC)", "克罗地亚", "#17首发中场"], ["73'", "卢卡森 (Derrick LUCKASSEN)", "加纳", "#23后卫定位球扳平"], ["83'", "弗拉希奇 (Nikola VLASIC)", "克罗地亚", "#13绝杀! 预测仅标注为\"中场\""]],
    events: "半场 克罗地亚 1-0 加纳 | 黄牌: 佩里希奇 68'(克), 奥庞 90+4'(加) | 换人: 克罗地亚4换(格瓦迪奥尔88'上), 加纳5换",
    pred: [["首选比分", "1-1", "2-1", "[错]"], ["方向", "平局", "克罗地亚赢", "[错]"], ["半场", "0-0", "1-0", "[错]"]],
    factors: [["格瓦迪奥尔替补→防守削弱", "仅丢1球,三后卫未崩溃", "[半对]"], ["加纳威廉姆斯+耶伦基替补→反击减半", "加纳仅1球(后卫定位球),无反击进球", "[对]"], ["莫德里奇定位球是唯一破局手段", "两球均来自中前场运动战配合", "[半对]"], ["1-1首选逻辑:核心缺席互相抵消", "结果偏克罗地亚—替补深度差异更大", "[错]"]],
    lessons: ["核心缺席不对称: 克罗地亚替代者(苏契奇/弗拉希奇)是首发级别,加纳替代者不是。替补深度差 > 缺席人数对称。", "弗拉希奇隐藏胜负手: 赛前仅标注\"中场\"的#13球员,83'绝杀。首发中靠前的中场值得专门评估。", "大巴持久力看替补防守深度: 首发大巴撑70分钟,替补防守下降导致最后阶段丢球。"],
  },
  {
    num: 2, title: "巴拿马 0-2 英格兰 (L组)",
    goals: [["62'", "贝林厄姆 (Jude BELLINGHAM)", "英格兰", "打破僵局!"], ["67'", "凯恩 (Harry KANE)", "英格兰", "5分钟后扩大比分!"]],
    events: "半场 巴拿马 0-0 英格兰 | 黄牌: 法哈多 53'(巴), 昆沙 60'(英), 安德拉德 83'(巴) | 换人: 英格兰5换(凯恩84'下), 巴拿马5换",
    pred: [["首选比分", "0-3", "0-2", "[错]"], ["备选比分", "0-2", "0-2", "[对] 命中!"], ["方向", "英格兰赢", "英格兰赢", "[对]"], ["半场", "0-1", "0-0", "[错]"]],
    factors: [["凯恩+萨卡+拉什福德→要进球", "贝林厄姆先破僵,凯恩跟进", "[对]"], ["轮换配合生疏→预测半场0-1", "上半场0-0!轮换影响大于预期", "[错]"], ["身价比碾压→英格兰必赢", "方向正确,赢球幅度低于预期", "[对]"]],
    lessons: ["轮换中场控制力下降真实: 安德森+罗杰斯上半场无法穿透巴拿马大巴。换上斯彭斯/马杜埃克后才打开。", "贝林厄姆中场定海神针: 轮换阵容中不可替代,62'打破僵局。", "大幅轮换→上半场0-0: 不管对手多弱,全新中场+防线必然生涩。以后默认上半场进球困难。"],
  },
  {
    num: 3, title: "哥伦比亚 0-0 葡萄牙 (K组)",
    goals: [],
    events: "比分 哥伦比亚 0-0 葡萄牙 | 半场 0-0 | 黄牌: 普埃尔塔 86'(哥) | 换人: 哥伦比亚5换(哈梅斯76'下),葡萄牙5换(莱昂70'上)",
    pred: [["首选比分", "1-1", "0-0", "[错]"], ["方向", "平局", "平局", "[对]"], ["半场", "0-0", "0-0", "[对]"]],
    factors: [["哥伦比亚打平即头名→不冒险", "全场0-0,射门均不多", "[对]"], ["双方均已出线→平局双赢", "完全验证——典型默契平局", "[对]"], ["C罗可能被保护性使用", "打满全场但未进球,强度不足", "[半对]"]],
    lessons: ["\"双方均可接受平局\"判断准确: 但高估了进攻意愿——1-1非0-0。", "第3轮\"已出线\"比赛0-0概率翻倍: 历史基线9.4%在此类比赛可能x2。", "超巨星在\"无所谓\"的比赛中不会强行破局: 比赛强度不够。"],
  },
  {
    num: 4, title: "刚果金 3-1 乌兹别克斯坦 (K组)",
    goals: [["10'", "绍穆罗多夫 (SHOMURODOV)", "乌兹别克斯坦", "刚果金先丢球!"], ["68'", "维萨 (Yoane WISSA)", "刚果金", "扳平!"], ["78'", "马耶莱 (Fiston MAYELE)", "刚果金", "反超! 替补奇兵(51'换入)!"], ["90+1'", "维萨 (Yoane WISSA)", "刚果金", "梅开二度锁定胜局"]],
    events: "半场 刚果金 0-1 乌兹别克斯坦 | 黄牌: 萨迪基21'/姆布库45+4'/穆图萨米62'(刚) | 换人: 马耶莱51'换入→78'反超!",
    pred: [["首选比分", "刚果金 2-0", "3-1", "[错]"], ["方向", "刚果金赢", "刚果金赢", "[对]"], ["零封预测", "预测零封", "10'即丢球!", "[错]"]],
    factors: [["刚果金防守已验证", "10'先丢球!开场松懈", "[错]"], ["乌兹别克斯坦已淘汰无威胁", "10'先拔头筹!无压力反而放开", "[错]"], ["刚果金赢球动力明确", "下半场连进3球逆转——动力兑现", "[对]"]],
    lessons: ["\"已淘汰球队\"≠\"无威胁\": 乌兹别克斯坦10'进球是响亮警告。", "无淘汰球队下半场崩盘真实: 60'后体能/专注度下降——刚果金逆转窗口(68'/78'/90+1')。", "上半场全错,全场正确: 足球逻辑有时延迟兑现。马耶莱替补奇兵(51'→78')。"],
  },
  {
    num: 5, title: "阿尔及利亚 3-3 奥地利 (J组) ※ 本日最具戏剧性",
    goals: [["28'", "阿瑙托维奇 (ARNAUTOVIC)", "奥地利", "先拔头筹! 第49粒国家队进球"], ["45'", "贝尔加利 (BELGHALI)", "阿尔及利亚", "半场前扳平!"], ["55'", "萨比策 (SABITZER)", "奥地利", "再次领先!"], ["60'", "马赫雷斯 (MAHREZ)", "阿尔及利亚", "5分钟后再次扳平!"], ["90+3'", "马赫雷斯 (MAHREZ)", "阿尔及利亚", "※ 看似绝杀!"], ["90+6'", "卡拉季奇 (KALAJDZIC)", "奥地利", "※ 真正绝平! 替补奇兵"]],
    events: "半场 1-1 | 黄牌: 阿瑙托维奇 11'(奥) | 换人: 卡拉季奇90+5'入→90+6'头球绝平!",
    pred: [["首选比分", "0-0", "3-3", "[错][错][错]"], ["方向", "平局(默契球)", "平局(生死战)", "巧合!逻辑全错"], ["核心逻辑", "J2=西班牙→都不想赢", "3分不够→必须争胜", "[错][错][错]"]],
    factors: [["J2=西班牙→双方都不想第2", "双方全力争胜!奥地利赢仍对西班牙", "[错]"], ["0-0默契球预判", "28'即破僵,全场6球", "[错]"], ["阿瑙托维奇首发", "28'进球!关键球员", "[对]"], ["马赫雷斯能力", "梅开二度!含90+3'看似绝杀", "[对]"]],
    lessons: ["[致命]出线数学必须精确: \"都不想赢\"前提=输球J3=4分——但输球=3分!3分大概率淘汰。", "3分≠安全、4分≠保险: 48队取8个第3名,第3轮底线是4分。", "预测0-0→实际3-3=本日最大失准: 生存本能压倒选对手算计。"],
  },
  {
    num: 6, title: "约旦 1-3 阿根廷 (J组)",
    goals: [["19'", "洛塞尔索 (LO CELSO)", "阿根廷", "任意球破门!"], ["31'", "劳塔罗·马丁内斯 (Lautaro MARTINEZ)", "阿根廷", "点球扩大比分"], ["55'", "阿尔塔马里 (AL-TAMARI)", "约旦", "扳回一球!"], ["80'", "梅西 (Lionel MESSI)", "阿根廷", "※ 替补任意球破门! 第6球!"]],
    events: "半场 约旦 0-2 阿根廷 | 黄牌: 约旦17'/64'/90+4' | 换人: 梅西60'入→80'任意球破门=第6球!",
    pred: [["首选比分", "0-3", "1-3", "[错]差1球"], ["方向", "阿根廷赢", "阿根廷赢", "[对]"], ["半场", "0-2", "0-2", "[对]"]],
    factors: [["身价比41:1→碾压", "1-3全程控制", "[对]"], ["阿根廷可能大幅轮换", "9人轮换!梅西替补", "[对]"], ["梅西替补出场刷1球", "60'上场→80'任意球=第6球!", "[对][对]"]],
    lessons: ["约旦韧性被低估: 0-2落后仍扳回1球。小组赛3场全部进球。", "梅西替补=阿根廷奢侈: 60'出场80'破门。第6球领跑金靴。", "阿根廷9人轮换仍19'破僵: 阵容深度世界顶级。"],
  },
];

// ═══ Build document ═══
const cover = [
  empty(),
  para("2026 FIFA 世界杯", 28, { bold: true, color: C.TITLE_RED, align: AlignmentType.CENTER }),
  para("6月28日 六场全复盘", 20, { bold: true, color: C.SUBTITLE, align: AlignmentType.CENTER, after: 120 }),
  para("小组赛收官日  ·  L / K / J 组  ·  第3轮", 12, { color: C.META, align: AlignmentType.CENTER, after: 360 }),
  para("生成时间: 2026年6月29日 北京时间  |  数据源: FIFA API + ESPN API  |  框架: CLAUDE.md v17", 8, { color: C.META_LIGHT, align: AlignmentType.CENTER, after: 400 }),
  sep(),
];

// Summary
const summarySection = [
  para("一、复盘成绩总览", 14, { bold: true, color: C.ACCENT, before: 100, after: 120 }),
  buildSummary([
    ["1", "05:00", "克罗地亚 vs 加纳", "1-1", "2-1", "[错]", "[错]", "首选平局→克罗地亚赢"],
    ["2", "05:00", "巴拿马 vs 英格兰", "0-3", "0-2", "[对]", "[对]备选", "备选2-0命中!"],
    ["3", "07:30", "哥伦比亚 vs 葡萄牙", "1-1", "0-0", "[对]", "[错]", "方向对(平局),比分0-0非首选"],
    ["4", "07:30", "刚果金 vs 乌兹别克斯坦", "刚果金 2-0", "3-1", "[对]", "[错]", "方向对,过程全反"],
    ["5", "10:00", "阿尔及利亚 vs 奥地利", "0-0", "3-3", "[错]", "[错]", "※默契球预判全错!"],
    ["6", "10:00", "约旦 vs 阿根廷", "0-3", "1-3", "[对]", "[错]", "方向对,约旦进球意外"],
  ]),
  empty(),
  para("汇总: 方向 4/6 (67%)  |  精确比分 1/6 (17%, 含备选)  |  半场正确 2/6 (33%)", 10, { bold: true, color: C.SUBTITLE, align: AlignmentType.CENTER }),
  empty(),
];

// Match sections
function buildMatchSection(m) {
  const parts = [];
  parts.push(para(`比赛${m.num}: ${m.title}`, 12, { bold: true, color: C.ACCENT, before: 160, after: 100 }));

  // Goals
  if (m.goals.length > 0) {
    parts.push(para("进球记录", 10, { bold: true, color: C.SUBTITLE }));
    parts.push(goalsTbl(m.goals.map(g => [g[0], g[1], g[2], g[3]])));
    parts.push(empty());
  }

  // Events
  parts.push(para(m.events, 8, { color: C.META }));
  parts.push(empty());

  // Pred vs Actual
  parts.push(para("原始预测 vs 实际", 10, { bold: true, color: C.SUBTITLE }));
  parts.push(predTbl(m.pred));
  parts.push(empty());

  // Factors
  parts.push(para("赛前因素验证", 10, { bold: true, color: C.SUBTITLE }));
  parts.push(threeColTbl(["预测因素", "实际结果", "验证"], m.factors));
  parts.push(empty());

  // Lessons
  parts.push(para("关键教训", 10, { bold: true, color: C.HIGH_RISK }));
  m.lessons.forEach((l, i) => {
    parts.push(para(`${i + 1}. ${l}`, 9, { color: C.META }));
  });
  parts.push(empty());

  return parts;
}

// Insights section
const insightsSection = [
  para("二、六场汇总洞察", 14, { bold: true, color: C.ACCENT, before: 200, after: 120 }),
  para("被高估/低估的维度", 11, { bold: true, color: C.SUBTITLE }),
  threeColTbl(["维度", "趋势", "典型案例"], [
    ["第3轮出线数学", "[致命]错误", "比赛5: 3分≠安全,\"双方都不想赢\"逻辑完全错误"],
    ["已淘汰球队威胁", "被低估", "比赛4/6: 乌兹别克斯坦10'进球 + 约旦回敬1球"],
    ["轮换影响", "被低估", "比赛2: 英格兰上半场0-0"],
    ["\"双方都可接受平局\"", "判断准确", "比赛3: 哥伦比亚0-0葡萄牙完全验证"],
    ["大巴持久力", "被高估", "比赛1: 加纳73'扳平→83'被绝杀"],
    ["核心缺席对称性", "被高估", "比赛1: 克罗地亚替代者 > 加纳替代者"],
    ["无淘汰球队下半场崩盘", "新发现", "比赛4: 乌兹别克斯坦上半场1-0→下半场连丢3球"],
  ]),
  empty(),
  para("值得记录的新规律", 11, { bold: true, color: C.SUBTITLE }),
  ...[
    "1. 第3轮\"双方已出线+打平双赢\"=0-0概率极高 — 哥伦比亚0-0葡萄牙 [对]",
    "2. 大幅轮换→上半场大概率0-0 — 巴拿马0-0英格兰(半场) [对]",
    "3. 已淘汰球队→上半场可能制造惊喜→下半场崩盘 [对]",
    "4. 大巴持久力≠全场→70'后疲劳导致防守失误增加 [对]",
    "5. [新] 第3轮出线数学必须逐组精确计算,不能凭感觉 — 3分=大概率淘汰",
    "6. [新] \"不想对强队\" < \"不能小组淘汰\" — 生存本能压倒选对手算计",
  ].map(r => para(r, 9, { color: r.includes("[新]") ? C.HIGH_RISK : C.META })),
  empty(),
];

const bestSection = [
  para("本日最佳/最差", 11, { bold: true, color: C.SUBTITLE }),
  threeColTbl(["奖项", "得主", "理由"], [
    ["最佳预测", "巴拿马 0-2 英格兰", "备选比分完全命中,方向+走势正确"],
    ["最差预测", "阿尔及利亚 0-0 奥地利", "逻辑全错(0-0→3-3),出线数学算错"],
    ["最佳比赛", "阿尔及利亚 3-3 奥地利", "90+3'→90+6'绝平,本日最具戏剧性"],
    ["最佳球员", "马赫雷斯(阿尔及利亚)", "梅开二度,含90+3'看似绝杀"],
    ["最佳换人", "卡拉季奇(奥地利)", "90+5'换入→90+6'头球绝平"],
    ["最大惊喜", "梅西替补任意球", "连续7场世界杯进球,第6球领跑金靴"],
  ]),
];

// Assemble all match sections
const allMatchSections = matches.flatMap(m => buildMatchSection(m));

const children = [
  ...cover,
  ...summarySection,
  ...allMatchSections,
  ...insightsSection,
  ...bestSection,
  sep(),
  para("数据源: FIFA Official API + ESPN API", 7, { color: C.META_LIGHT }),
  para("原始预测: 2026年6月28日_6场预测.md (v7, FIFA首发确认版)", 7, { color: C.META_LIGHT }),
  para("分析框架: CLAUDE.md v17 复盘规范  |  生成工具: docx-js  |  [对]=正确 [错]=错误 [半对]=部分正确", 7, { color: C.META_LIGHT }),
];

const doc = new Document({
  styles: { default: { document: { run: { font: FONT, size: 20 } } } },
  sections: [{
    properties: {
      page: {
        size: { width: PAGE_W, height: PAGE_H, orientation: PageOrientation.LANDSCAPE },
        margin: { top: 720, right: MARGIN, bottom: 720, left: MARGIN },
      },
    },
    headers: {
      default: new Header({
        children: [new Paragraph({
          alignment: AlignmentType.RIGHT, spacing: { after: 0 },
          border: { bottom: { style: BorderStyle.SINGLE, size: 4, color: C.ACCENT, space: 4 } },
          children: [tr("2026 FIFA 世界杯  ·  6月28日 六场全复盘", 8, { color: C.META })],
        })],
      }),
    },
    footers: {
      default: new Footer({
        children: [new Paragraph({
          alignment: AlignmentType.CENTER,
          children: [
            tr("— ", 8, { color: C.META }),
            tr("Page ", 8, { color: C.META }),
            new TextRun({ children: [PageNumber.CURRENT], font: FONT, size: 16, color: C.META }),
            tr(" —", 8, { color: C.META }),
          ],
        })],
      }),
    },
    children,
  }],
});

const OUT = __dirname + "/2026年6月28日_6场复盘_v6.docx";
Packer.toBuffer(doc).then(buffer => {
  fs.writeFileSync(OUT, buffer);
  console.log(`Saved to ${OUT}`);
  console.log(`   File size: ${fs.statSync(OUT).size.toLocaleString()} bytes`);
});

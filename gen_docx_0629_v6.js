// DOCX v6 美化 — 2026年6月29日 1场预测 (南非 vs 加拿大 — Round of 32)
// 基于 gen_docx_template.js v6 横向尺寸 + 完整组件
const fs = require("fs");
const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
  Header, Footer, AlignmentType, PageOrientation, BorderStyle, WidthType,
  ShadingType, PageNumber, PageBreak
} = require("docx");

// ═══ 版面配置 (v6正确横向) ═══
const FONT = "微软雅黑";
const PAGE_W = 11906; // 短边 → swap后变 landscape height
const PAGE_H = 16838; // 长边 → swap后变 landscape width
const MARGIN = 850;
const CW = PAGE_H - MARGIN * 2; // 16838 - 1700 = 15138

// ═══ 色板 (与模板一致) ═══
const C = {
  HEADER_BG:   "1A2E3D",
  HEADER_TEXT: "FFFFFF",
  ALT_ROW:     "F5F7FA",
  PREF_ROW:    "E8F5E9",
  BORDER:      "D0D5DD",
  TITLE_RED:   "C0392B",
  SUBTITLE:    "1A1A2E",
  META:        "7F8C8D",
  META_LIGHT:  "95A5A6",
  ACCENT:      "2E75B6",
  HIGH_RISK:   "C0392B",
  GREEN:       "27AE60",
};

// ═══ 组件 ═══
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

// ═══ 表格组件 ═══
function hdrCell(text, colW, size) {
  return new TableCell({
    borders: BORDERS, width: { size: colW, type: WidthType.DXA },
    shading: { fill: C.HEADER_BG, type: ShadingType.CLEAR },
    verticalAlign: "center",
    margins: { top: 50, bottom: 50, left: 60, right: 60 },
    children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [tr(text, size || 9, { bold: true, color: C.HEADER_TEXT })] })],
  });
}
function datCell(text, colW, opts) {
  const o = opts || {};
  return new TableCell({
    borders: BORDERS, width: { size: colW, type: WidthType.DXA },
    shading: o.shading ? { fill: o.shading, type: ShadingType.CLEAR } : undefined,
    verticalAlign: "center",
    margins: { top: 40, bottom: 40, left: 60, right: 60 },
    children: [new Paragraph({ alignment: o.align || AlignmentType.CENTER, children: [tr(text, o.size || 9, { bold: !!o.bold, color: o.color })] })],
  });
}
function tblRow(cells) { return new TableRow({ children: cells }); }
function makeTable(colW, rows) {
  return new Table({ width: { size: CW, type: WidthType.DXA }, columnWidths: colW, rows });
}

// ── 汇总表 (8列, 无半场) ──
const SW = [400, 720, 420, 5900, 3200, 1280, 2158, 1060];
function buildSummary(rows) {
  const hdr = tblRow([
    hdrCell("#", SW[0]), hdrCell("时间", SW[1]), hdrCell("组", SW[2]),
    hdrCell("比赛", SW[3]), hdrCell("形势", SW[4]), hdrCell("首选比分", SW[5]),
    hdrCell("备选比分", SW[6]), hdrCell("冷门风险", SW[7]),
  ]);
  const data = rows.map((r, i) => {
    const sh = i % 2 === 0 ? C.PREF_ROW : undefined;
    return tblRow(r.map((t, j) =>
      datCell(t, SW[j], { bold: j === 5, size: 8, align: j <= 2 || j >= 5 ? AlignmentType.CENTER : AlignmentType.LEFT, shading: sh })
    ));
  });
  return makeTable(SW, [hdr, ...data]);
}

// ── 因素导向表 ──
function factorTbl(rows) {
  const W = [4800, 2200, CW - 7000]; // 4800 + 2200 + 8138 = 15138
  const hdr = tblRow([hdrCell("因素", W[0]), hdrCell("对哪边有利", W[1]), hdrCell("理由", W[2])]);
  const data = rows.map((r, i) => tblRow(r.map((t, j) =>
    datCell(t, W[j], { size: 8, align: j === 2 ? AlignmentType.LEFT : (j === 1 ? AlignmentType.CENTER : AlignmentType.LEFT), shading: i % 2 === 0 ? C.ALT_ROW : undefined })
  )));
  return makeTable(W, [hdr, ...data]);
}

// ── 比分预测表 ──
function scoreTbl(rows) {
  const W = [1200, 1800, 1200, CW - 4200];
  const hdr = tblRow([hdrCell("类型", W[0]), hdrCell("比分", W[1]), hdrCell("半场", W[2]), hdrCell("说明", W[3])]);
  const data = rows.map((r, i) => tblRow(r.map((t, j) =>
    datCell(t, W[j], { size: 8, bold: i === 0 && j === 1, align: j === 3 ? AlignmentType.LEFT : AlignmentType.CENTER, shading: i === 0 ? C.PREF_ROW : (i % 2 === 0 ? C.ALT_ROW : undefined) })
  )));
  return makeTable(W, [hdr, ...data]);
}

// ── 韧性评估表 ──
function resilienceTbl(items) {
  const W = [2800, 1200, CW - 4000];
  const hdr = tblRow([hdrCell("韧性维度", W[0]), hdrCell("评分", W[1]), hdrCell("说明", W[2])]);
  const data = items.map((r, i) => tblRow(r.map((t, j) =>
    datCell(t, W[j], { size: 8, align: j === 2 ? AlignmentType.LEFT : (j === 1 ? AlignmentType.CENTER : AlignmentType.LEFT), shading: i % 2 === 0 ? C.ALT_ROW : undefined })
  )));
  return makeTable(W, [hdr, ...data]);
}

// ── 信息表 (2列) ──
function infoTbl(rows) {
  const W = [1800, CW - 1800];
  return makeTable(W, rows.map(([k, v]) => tblRow([
    datCell(k, W[0], { bold: true, shading: C.ALT_ROW, align: AlignmentType.LEFT }),
    datCell(v, W[1], { align: AlignmentType.LEFT }),
  ])));
}

// ── 伤病表 ──
function injuryTbl(rows) {
  const W = [800, 2400, 1200, CW - 4400];
  const hdr = tblRow([hdrCell("球队", W[0]), hdrCell("球员", W[1]), hdrCell("状态", W[2]), hdrCell("影响", W[3])]);
  const data = rows.map((r, i) => tblRow(r.map((t, j) =>
    datCell(t, W[j], { size: 8, align: j === 3 ? AlignmentType.LEFT : (j <= 2 ? AlignmentType.CENTER : AlignmentType.CENTER), shading: i % 2 === 0 ? C.ALT_ROW : undefined })
  )));
  return makeTable(W, [hdr, ...data]);
}

// ── 晋级预测表 ──
function advanceTbl(rows) {
  const W = [1200, 2400, CW - 3600];
  const hdr = tblRow([hdrCell("类型", W[0]), hdrCell("晋级方", W[1]), hdrCell("方式", W[2])]);
  const data = rows.map((r, i) => tblRow(r.map((t, j) =>
    datCell(t, W[j], { size: 9, bold: i === 0 && j <= 1, align: j === 2 ? AlignmentType.LEFT : AlignmentType.CENTER, shading: i === 0 ? C.PREF_ROW : (i % 2 === 0 ? C.ALT_ROW : undefined) })
  )));
  return makeTable(W, [hdr, ...data]);
}

// ═══════════════════════════
// 文档内容
// ═══════════════════════════
const cover = [
  empty(),
  para("2026 FIFA 世界杯", 28, { bold: true, color: C.TITLE_RED, align: AlignmentType.CENTER }),
  para("6月29日 一场预测报告", 20, { bold: true, color: C.SUBTITLE, align: AlignmentType.CENTER, after: 120 }),
  para("淘汰赛32强开幕  ·  南非 vs 加拿大  ·  Round of 32", 12, { color: C.META, align: AlignmentType.CENTER, after: 360 }),
  para("生成时间: 2026年6月29日 北京时间  |  数据源: FIFA API + ESPN API + 多源赛前分析  |  框架: CLAUDE.md v17", 8, { color: C.META_LIGHT, align: AlignmentType.CENTER, after: 400 }),
  sep(),
];

// ── 一、预测汇总 ──
const summarySection = [
  para("一、预测汇总", 14, { bold: true, color: C.ACCENT, before: 100, after: 120 }),
  buildSummary([
    ["1", "03:00", "R32", "南非 vs 加拿大", "两队首次淘汰赛\n加拿大€280M vs 南非€45M ≈ 6:1", "1-1\n(加时加拿大晋级)", "0-1 / 南非1-0\n0-2", "中高"],
  ]),
  empty(),
  para("6月29日仅1场 — Round of 32淘汰赛开幕战。两队均为队史首次世界杯淘汰赛。胜者16强对阵荷兰 vs 摩洛哥的胜者。", 9, { color: C.META }),
  empty(),
];

// ── 二、小组赛回顾 ──
const groupSection = [
  para("二、小组赛回顾", 14, { bold: true, color: C.ACCENT, before: 100, after: 120 }),
];

// 小组回顾表
const GR_WIDTHS = [600, 3600, 3600, 3200, 3200]; // sum = 14100
function groupReviewTbl() {
  const hdr = tblRow([
    hdrCell("", GR_WIDTHS[0]), hdrCell("南非 (A组第2, 4分)", GR_WIDTHS[1]),
    hdrCell("加拿大 (B组第2, 4分)", GR_WIDTHS[2]),
    hdrCell("南非详情", GR_WIDTHS[3]),
    hdrCell("加拿大详情", GR_WIDTHS[4]),
  ]);
  const rows = [
    ["G1", "墨西哥", "波黑", "0-2 负", "1-1 平"],
    ["G2", "捷克", "卡塔尔", "1-1 平 (莫科纳83'点球)", "6-0 胜 (戴维帽子戏法!)"],
    ["G3", "韩国", "瑞士", "1-0 胜 (马塞科63')", "1-2 负"],
    ["进/失", "2球 / 3球", "8球 / 3球", "防守大巴已验证", "攻击力4倍于对手"],
    ["排名", "#60", "#31", "首进淘汰赛", "首进淘汰赛"],
  ].map((r, i) => tblRow(r.map((t, j) =>
    datCell(t, GR_WIDTHS[j], { size: 8, align: j >= 1 ? AlignmentType.LEFT : AlignmentType.CENTER, shading: i % 2 === 0 ? C.ALT_ROW : undefined })
  )));
  return new Table({ width: { size: 14100, type: WidthType.DXA }, columnWidths: GR_WIDTHS, rows: [hdr, ...rows] });
}

// ── 三、比赛详细分析 ──
const matchSections = [
  para("三、比赛详细分析", 14, { bold: true, color: C.ACCENT, before: 200, after: 120 }),

  // 3.1 基本信息
  para("3.1 基本信息", 11, { bold: true, color: C.SUBTITLE }),
  infoTbl([
    ["比赛时间", "6月29日 03:00 北京时间"],
    ["比赛地点", "SoFi体育场, 洛杉矶, 美国"],
    ["比赛阶段", "Round of 32 (1/16决赛)"],
    ["FIFA排名", "加拿大 #31  vs  南非 #60"],
    ["身价比", "加拿大~€280M  vs  南非~€45M  ≈  6:1"],
    ["历史交锋", "仅1次友谊赛 (2007年), 南非2-0获胜"],
    ["晋级奖励", "16强对阵 荷兰 vs 摩洛哥 的胜者"],
    ["主裁判", "若昂·皮涅罗 (葡萄牙)"],
  ]),
  empty(),

  // 3.2 伤病/停赛
  para("3.2 伤病与停赛", 11, { bold: true, color: C.SUBTITLE }),
  injuryTbl([
    ["南非", "兹瓦内 (Themba Zwane)", "停赛", "进攻组织核心缺阵 — 唯一10号被移除"],
    ["南非", "莫科纳 (Teboho Mokoena)", "复出", "中场核心回归! 弥补兹瓦内部分损失"],
    ["加拿大", "科内 (Ismaël Koné)", "报销", "中场核心腿骨折 — 缺席整届"],
    ["加拿大", "阿方索·戴维斯 (Alphonso Davies)", "疑似", "拜仁左边锋可出场 — 球队最高身价"],
    ["加拿大", "欧斯塔基奥 (Stephen Eustáquio)", "疑似", "肌肉问题 — 若缺阵中场硬度进一步下降"],
  ]),
  empty(),

  // 3.3 因素导向
  para("3.3 因素导向表", 11, { bold: true, color: C.SUBTITLE }),
  factorTbl([
    ["身价比6:1 (加拿大~€280M)", "加拿大 ★★★", "阵容深度碾压 — 淘汰赛阵容厚度更重要"],
    ["★ 乔纳森·戴维状态 (小组赛3球)", "加拿大 ★★★", "32强中状态最火前锋 — 单兵可破大巴"],
    ["★ 南非大巴已验证 (1-0韩国零封)", "南非 ★★", "32强中最可能拖入加时的防守体系"],
    ["★ 兹瓦内停赛 → 创造力消失", "加拿大 ★★", "南非唯一10号被移除 — 反击发起能力下降"],
    ["★ 阿方索·戴维斯可能复出", "加拿大 ★★", "左边路升级一档 — 对南非右路施压"],
    ["★ 科内报销 → 加拿大中场硬度下降", "南非 ★", "对阵波黑/瑞士时已暴露中场问题"],
    ["南非速度反击 (马塞科速度32强顶级)", "南非 ★★", "加拿大压上 → 身后空间大 → 反击机会多"],
    ["淘汰赛经验: 双方均为零", "双方", "均首次淘汰赛 — 上半场试探为主, 都可能紧张"],
    ["南非门将威廉姆斯 = 扑点专家", "南非 ★", "点球大战对南非有利! 曾AFCON单场扑4点"],
    ["加拿大东道主 + 洛杉矶半个主场", "加拿大 ★", "SoFi球场氛围有利 — 但不是决定性"],
  ]),
  empty(),

  // 3.4 强队分类
  para("3.4 强队分类", 11, { bold: true, color: C.SUBTITLE }),
  para("加拿大: 体系型 — 戴维 (超巨, €50M+) 是唯一具备单兵破局能力的球员。戴维斯伤疑 + 科内报销 → 缺少第二进攻维度。进攻依赖戴维终结 + 双翼传中。", 9, { color: C.META }),
  para("南非: 大巴型 — 防守体系稳固, 进攻创造力完全依赖反击速度 (马塞科/莫福肯)。兹瓦内停赛 = 唯一10号被移除, 反击发起进一步受限。", 9, { color: C.META }),
  empty(),

  // 3.5 非洲韧性评估 (南非)
  para("3.5 非洲韧性评估 (南非)", 11, { bold: true, color: C.SUBTITLE }),
  resilienceTbl([
    ["低位防守", "★★★", "对韩国零封 = 大巴满分。对捷克仅丢1球 (非大巴阵型)。"],
    ["速度反击", "★★★", "马塞科速度32强顶级, 莫福肯 + 阿波利斯双翼齐飞。"],
    ["定位球高点", "★★", "姆博卡齐 + 奥孔双塔, 莫科纳回归增加定位球威胁。"],
    ["前30分钟专注度", "★★★", "3场均未在前30分钟丢球 — 开场纪律满分。"],
    ["被压制不崩盘", "★★★", "对韩国68%控球围攻不崩盘。少2人打墨西哥例外。"],
  ]),
  para("南非韧性 5/5 — 除少2人打墨西哥外, 防守体系完整且已验证。", 10, { bold: true, color: C.GREEN }),
  empty(),

  // 3.6 教练博弈
  para("3.6 教练博弈", 11, { bold: true, color: C.SUBTITLE }),
  para("南非 (布鲁斯, 67岁, 本届后退休): 低位防守 + 反击, 少输当赢。落后策略 → 60'上莫福肯/雷纳斯搏命。关键: 布鲁斯对非洲球队淘汰赛经验丰富。", 9, { color: C.META }),
  para("加拿大 (科克伦, 年轻教练): 高位压迫 + 两翼齐飞。领先 → 控制节奏消耗; 落后 → 堆前锋搏命。关键换人: 戴维斯是否出场。若65'后仍是0-0 → 戴维斯替补登场 = 比赛转折点。", 9, { color: C.META }),
  para("替补改变比赛能力: 加拿大的戴维斯/马杜埃克 > 南非的莫福肯/雷纳斯。", 9, { bold: true }),
  empty(),

  // 3.7 定位球攻防
  para("3.7 定位球攻防", 11, { bold: true, color: C.SUBTITLE }),
  para("南非进攻定位球: 莫科纳回归 (对捷克点球得分), 姆博卡齐 + 奥孔双塔高点 — 这是南非最可能破门的方式。", 9, { color: C.META }),
  para("加拿大进攻定位球: 科内报销后失去最佳头球点, 戴维/科尼利厄斯仍有威胁。对瑞士丢过定位球 — 防守端有漏洞。", 9, { color: C.META }),
  para("总结: 定位球攻防双方基本均衡, 但南非高点优势稍占优。", 9, { bold: true }),
  empty(),

  // 3.8 冷门风险评估
  para("3.8 冷门风险评估: 中高", 11, { bold: true, color: C.HIGH_RISK }),
  para("南非大巴已验证 (1-0韩国), 加拿大缺少科内 → 中场控制下降。核心变量: (1) 南非撑60分钟不丢球 → 拖入加时; (2) 威廉姆斯扑点专家 → 点球对南非有利; (3) 兹瓦内停赛 → 南非反击创造力下降。", 9, { color: C.META }),
  empty(),

  // 3.9 冷门路径
  para("3.9 冷门路径", 11, { bold: true, color: C.HIGH_RISK }),
  para("路径1: 南非大巴守75分钟 → 加拿大急躁压上 → 马塞科反击偷一个 → 1-0。", 9, { color: C.META }),
  para("路径2: 0-0拖入加时 → 双方体力耗尽 → 点球大战 → 威廉姆斯 (AFCON扑4点) 决胜 → 南非晋级。", 9, { color: C.META }),
  para("概率评估: 路径1约15% / 路径2约10% / 合计冷门概率约25%。", 9, { bold: true }),
  empty(),

  // 3.10 比分预测
  para("3.10 比分预测", 11, { bold: true, color: C.SUBTITLE }),
  scoreTbl([
    ["首选", "1-1", "0-0", "南非大巴撑70分钟 → 戴维破僵 → 马塞科反击扳平 → 加时加拿大胜"],
    ["备选", "0-1", "0-0", "戴维个人能力破大巴 → 南非反击无果 → 加拿大常规时间小胜"],
    ["备选", "南非 1-0", "0-0", "马塞科反击偷一个 → 大巴死守85分钟 → 冷门!"],
    ["备选", "0-2", "0-1", "戴维斯复出即助攻 → 加拿大早破僵 → 南非被迫压出 → 再丢一球"],
  ]),
  empty(),

  // 晋级预测
  para("晋级预测", 11, { bold: true, color: C.SUBTITLE }),
  advanceTbl([
    ["首选", "加拿大", "加时赛后晋级"],
    ["备选", "加拿大", "常规时间 0-1"],
    ["冷门", "南非", "常规时间 1-0 或 点球决胜"],
  ]),
  empty(),

  // 淘汰赛路径
  para("四、淘汰赛路径", 14, { bold: true, color: C.ACCENT, before: 200, after: 120 }),
  para("本场胜者 → Round of 16 → 对阵 荷兰 vs 摩洛哥 的胜者", 11, { bold: true, color: C.SUBTITLE }),
  para("如果加拿大晋级: 大概率面对荷兰 (€837M) — 晋级希望极低。", 9, { color: C.META }),
  para("如果南非晋级: 若摩洛哥爆冷胜荷兰 → 非洲内战晋级机会增大 → 历史性八强!", 9, { color: C.META }),
];

// ═══════════════════════════
// 组装文档
// ═══════════════════════════
const children = [
  ...cover,
  ...summarySection,
  ...groupSection,
  groupReviewTbl(),
  empty(),
  ...matchSections,
  sep(),
  para("数据来源: FIFA API + ESPN API + Sporting News + Sports Illustrated + OneSoccer + 澎湃新闻", 7, { color: C.META_LIGHT }),
  para("身价数据: Transfermarkt 估算 (加拿大~€280M / 南非~€45M)", 7, { color: C.META_LIGHT }),
  para("分析框架: CLAUDE.md v17 (身价量化 + 强队三类分法 + 淘汰赛路径分析 + 10项必填清单)", 7, { color: C.META_LIGHT }),
  para("生成时间: 2026年6月29日 北京时间  |  生成工具: docx-js  |  [注意] 淘汰赛无平局 — 可能进入加时+点球", 7, { color: C.META_LIGHT }),
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
          children: [tr("2026 FIFA 世界杯  ·  6月29日 一场预测  ·  南非 vs 加拿大", 8, { color: C.META })],
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

const OUT = __dirname + "/2026年6月29日_1场预测_v6.docx";
Packer.toBuffer(doc).then(buffer => {
  fs.writeFileSync(OUT, buffer);
  console.log(`Saved to ${OUT}`);
  console.log(`   File size: ${fs.statSync(OUT).size.toLocaleString()} bytes`);
});

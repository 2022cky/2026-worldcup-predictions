// DOCX 美化模板 — 2026世界杯预测报告
// 用法: 复制此文件 → 修改 MATCHES 数据 → node gen_xxx.js
// 规范: CLAUDE.md v17 — 横向A4, 微软雅黑, 深蓝表头白字, 隔行灰底, 首选浅绿
//       🚨 国家名全称 (禁止缩写/禁止3字母代码)
//       🚨 汇总表8列 (无半场列), 表格宽度不溢出

const fs = require("fs");
const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
  Header, Footer, AlignmentType, PageOrientation, BorderStyle, WidthType,
  ShadingType, PageNumber, PageBreak
} = require("docx");

// ═══ 版面配置 ═══
// 🚨 关键: docx-js landscape 需传入 PORTRAIT 尺寸, 内部自动交换
// A4 portrait = 11906×16838, 传参后 swap → XML w=16838 h=11906 (正确横向)
const FONT = "微软雅黑";
const PAGE_W = 11906; // 短边 (portrait width, swap后变 landscape height)
const PAGE_H = 16838; // 长边 (portrait height, swap后变 landscape width)
const MARGIN = 850;
const CONTENT_W = PAGE_H - MARGIN * 2; // 16838 - 1700 = 15138 (真正可打印宽度)

// ═══ 色板 ═══
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
};

// ═══ 基础组件 ═══
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
    border: opts.border,
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
function pageBr() { return new Paragraph({ children: [new PageBreak()] }); }

// ═══ 表格组件 ═══
function hdrCell(text, colW) {
  return new TableCell({
    borders: BORDERS, width: { size: colW, type: WidthType.DXA },
    shading: { fill: C.HEADER_BG, type: ShadingType.CLEAR },
    verticalAlign: "center",
    margins: { top: 50, bottom: 50, left: 60, right: 60 },
    children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [tr(text, 9, { bold: true, color: C.HEADER_TEXT })] })],
  });
}
function datCell(text, colW, opts) {
  const o = opts || {};
  const runs = Array.isArray(text) ? text : [tr(text, 9, o)];
  return new TableCell({
    borders: BORDERS, width: { size: colW, type: WidthType.DXA },
    shading: o.shading ? { fill: o.shading, type: ShadingType.CLEAR } : undefined,
    verticalAlign: "center",
    margins: { top: 40, bottom: 40, left: 60, right: 60 },
    children: [new Paragraph({ alignment: o.align || AlignmentType.CENTER, children: runs })],
  });
}
function tblRow(cells) { return new TableRow({ children: cells }); }
function makeTable(colW, rows) {
  return new Table({ width: { size: CONTENT_W, type: WidthType.DXA }, columnWidths: colW, rows });
}

// ═══ 固定模板表格 ═══
// 汇总表 — 8列: #,时间,组,比赛,形势,首选比分,备选比分,冷门风险
// 列宽和 = 15038 = CONTENT_W (不溢出)
const SW = [400, 720, 420, 5900, 3200, 1280, 2158, 1060]; // sum = 15138

function buildSummary(rows) {
  const hdr = tblRow([
    hdrCell("#", SW[0]), hdrCell("时间", SW[1]), hdrCell("组", SW[2]),
    hdrCell("比赛", SW[3]), hdrCell("形势", SW[4]), hdrCell("首选比分", SW[5]),
    hdrCell("备选比分", SW[6]), hdrCell("冷门风险", SW[7]),
  ]);
  const data = rows.map((r, i) => {
    const sh = i % 2 === 0 ? C.PREF_ROW : undefined;
    return tblRow(r.map((t, j) =>
      datCell(t, SW[j], { bold: j === 5, align: j <= 2 || j >= 5 ? AlignmentType.CENTER : AlignmentType.LEFT, shading: sh })
    ));
  });
  return makeTable(SW, [hdr, ...data]);
}

// 因素导向表 — 3列: 因素, 对哪边有利, 理由
function factorTbl(rows) {
  const W = [4800, 2200, CONTENT_W - 7000];
  const hdr = tblRow([hdrCell("因素", W[0]), hdrCell("对哪边有利", W[1]), hdrCell("理由", W[2])]);
  const data = rows.map((r, i) => tblRow(r.map((t, j) =>
    datCell(t, W[j], { align: j === 2 ? AlignmentType.LEFT : (j === 1 ? AlignmentType.CENTER : AlignmentType.LEFT), shading: i % 2 === 0 ? C.ALT_ROW : undefined })
  )));
  return makeTable(W, [hdr, ...data]);
}

// 比分预测表 — 4列: 类型, 比分, 半场, 说明
function scoreTbl(rows) {
  const W = [1200, 1800, 1200, CONTENT_W - 4200];
  const hdr = tblRow([hdrCell("类型", W[0]), hdrCell("比分", W[1]), hdrCell("半场", W[2]), hdrCell("说明", W[3])]);
  const data = rows.map((r, i) => tblRow(r.map((t, j) =>
    datCell(t, W[j], { bold: i === 0 && j === 1, align: j === 3 ? AlignmentType.LEFT : AlignmentType.CENTER, shading: i === 0 ? C.PREF_ROW : (i % 2 === 0 ? C.ALT_ROW : undefined) })
  )));
  return makeTable(W, [hdr, ...data]);
}

// 韧性评估表 — 3列
function resilienceTbl(items) {
  const W = [2800, 1200, CONTENT_W - 4000];
  const hdr = tblRow([hdrCell("韧性维度", W[0]), hdrCell("评分", W[1]), hdrCell("说明", W[2])]);
  const data = items.map((r, i) => tblRow(r.map((t, j) =>
    datCell(t, W[j], { align: j === 2 ? AlignmentType.LEFT : (j === 1 ? AlignmentType.CENTER : AlignmentType.LEFT), shading: i % 2 === 0 ? C.ALT_ROW : undefined })
  )));
  return makeTable(W, [hdr, ...data]);
}

// 信息表 — 2列
function infoTbl(rows) {
  const W = [1800, CONTENT_W - 1800];
  return makeTable(W, rows.map(([k, v]) => tblRow([
    datCell(k, W[0], { bold: true, shading: C.ALT_ROW, align: AlignmentType.LEFT }),
    datCell(v, W[1], { align: AlignmentType.LEFT }),
  ])));
}

// 小组积分表 (独立宽度)
const GW = [600, 2400, 500, 500, 500, 500, 1300, 800, 800]; // sum = 7800
function groupTbl(rows) {
  const hdr = tblRow(["#","球队","场","胜","平","负","进/失","净胜","积分"].map((h, i) => hdrCell(h, GW[i])));
  const data = rows.map((r, ri) => tblRow(r.map((t, ci) =>
    datCell(t, GW[ci], { bold: ri === 0, align: ci >= 2 ? AlignmentType.CENTER : AlignmentType.LEFT, shading: ri === 0 ? C.PREF_ROW : (ri % 2 === 0 ? C.ALT_ROW : undefined) })
  )));
  return new Table({ width: { size: 7800, type: WidthType.DXA }, columnWidths: GW, rows: [hdr, ...data] });
}

// 淘汰赛路径表
const PATH_W = [1200, 2400, 2400, 4569, 4569]; // sum = 15138
function pathTbl(rows) {
  const hdr = tblRow([
    hdrCell("小组", PATH_W[0]), hdrCell("第1名", PATH_W[1]), hdrCell("第2名", PATH_W[2]),
    hdrCell("第1名淘汰赛路径", PATH_W[3]), hdrCell("第2名淘汰赛路径", PATH_W[4]),
  ]);
  const data = rows.map(r => tblRow(r.map((t, j) =>
    datCell(t, PW[j], { align: j >= 3 ? AlignmentType.LEFT : AlignmentType.CENTER })
  )));
  return makeTable(PW, [hdr, ...data]);
}

// ═══ 文档结构 ═══
function buildDoc({ date, title, subtitle, summaryRows, groupData, pathData, matchSections }) {
  const cover = [
    empty(),
    para("2026 FIFA 世界杯", 28, { bold: true, color: C.TITLE_RED, align: AlignmentType.CENTER }),
    para(title, 20, { bold: true, color: C.SUBTITLE, align: AlignmentType.CENTER, after: 120 }),
    para(subtitle, 12, { color: C.META, align: AlignmentType.CENTER, after: 360 }),
    para(`生成时间: ${date} 北京时间  |  数据源: FIFA API + ESPN API  |  框架: CLAUDE.md v17`, 8, { color: C.META_LIGHT, align: AlignmentType.CENTER, after: 400 }),
    sep(),
  ];

  // Group standings
  const groupSection = [];
  for (const g of groupData) {
    groupSection.push(para(g.label, 11, { bold: true, color: C.SUBTITLE }));
    groupSection.push(groupTbl(g.rows));
    groupSection.push(empty());
  }

  const children = [
    ...cover,
    para("一、预测汇总", 14, { bold: true, color: C.ACCENT, before: 100, after: 120 }),
    buildSummary(summaryRows),
    empty(),
    para("二、小组积分形势", 14, { bold: true, color: C.ACCENT, before: 100, after: 120 }),
    ...groupSection,
    para("三、淘汰赛路径分析", 14, { bold: true, color: C.ACCENT, before: 100, after: 120 }),
    pathTbl(pathData),
    pageBr(),
    para("四、分场比赛详细分析", 14, { bold: true, color: C.ACCENT, before: 100, after: 120 }),
    ...matchSections.flat(),
    empty(), sep(),
    para("数据来源: FIFA API + ESPN API + Sporting News + Sports Mole + FIFA官网", 7, { color: C.META_LIGHT }),
    para("身价数据: Transfermarkt via Mundo Deportivo + memory/team-market-values.md", 7, { color: C.META_LIGHT }),
    para("分析框架: CLAUDE.md v17 (身价量化 + 强队三类分法 + 淘汰赛路径分析 + 10项必填清单)", 7, { color: C.META_LIGHT }),
    para(`生成时间: ${date} 北京时间`, 7, { color: C.META_LIGHT }),
  ];

  return new Document({
    styles: { default: { document: { run: { font: FONT, size: 20 } } } },
    sections: [{
      properties: {
        page: { size: { width: PAGE_W, height: PAGE_H, orientation: PageOrientation.LANDSCAPE }, margin: { top: 720, right: MARGIN, bottom: 720, left: MARGIN } },
      },
      headers: {
        default: new Header({
          children: [new Paragraph({
            alignment: AlignmentType.RIGHT, spacing: { after: 0 },
            border: { bottom: { style: BorderStyle.SINGLE, size: 4, color: C.ACCENT, space: 4 } },
            children: [tr(`2026 FIFA 世界杯  ·  ${title}`, 8, { color: C.META })],
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
}

// ═══ 导出 ═══
module.exports = { buildDoc, tr, para, empty, sep, pageBr, factorTbl, scoreTbl, resilienceTbl, infoTbl, sep as separator };

// ═══ 直接运行时生成示例文件 ═══
if (require.main === module) {
  console.log("模板已加载。请创建独立脚本，调用 buildDoc() 生成具体日期的文档。");
  console.log("参考: gen_docx_0628_v4.js 中的数据结构。");
}

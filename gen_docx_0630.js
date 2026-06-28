// gen_docx_0630.js — 6月30日 3场预测 DOCX v3 (docx-js, 表格宽度精确控制)
const fs = require('fs');
const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
  Header, AlignmentType, PageOrientation, HeadingLevel, BorderStyle,
  WidthType, ShadingType, PageBreak, PageNumber, Footer, ExternalHyperlink
} = require('docx');

// ── Colors & constants ──
const DARK   = "1A1A2E";
const RED    = "C0392B";
const WHITE  = "FFFFFF";
const GRAY   = "F2F2F2";
const GREEN  = "D5F5D0";
const BLUE_HEADER = "1A1A2E";

// Page: US Letter Landscape (pass portrait dims, docx-js swaps)
const PAGE_W = 12240; // short edge
const PAGE_H = 15840; // long edge
const MARGIN = 1440;  // 1 inch
const CONTENT_W = PAGE_H - 2 * MARGIN; // 12960 DXA — usable table width

// Shared border
const border = { style: BorderStyle.SINGLE, size: 1, color: "BBBBBB" };
const borders = { top: border, bottom: border, left: border, right: border };
const noBorders = {
  top: { style: BorderStyle.NONE, size: 0 },
  bottom: { style: BorderStyle.NONE, size: 0 },
  left: { style: BorderStyle.NONE, size: 0 },
  right: { style: BorderStyle.NONE, size: 0 },
};
const cellMargins = { top: 60, bottom: 60, left: 100, right: 100 };

// ── Helpers ──
function hdrCell(text, width) {
  return new TableCell({
    borders, width: { size: width, type: WidthType.DXA },
    shading: { fill: BLUE_HEADER, type: ShadingType.CLEAR },
    margins: cellMargins,
    verticalAlign: "center",
    children: [new Paragraph({
      alignment: AlignmentType.CENTER,
      children: [new TextRun({ text, bold: true, font: "Arial", size: 18, color: WHITE })],
    })]
  });
}

function dataCell(text, width, opts = {}) {
  const { bold, color, bg, align } = opts;
  return new TableCell({
    borders, width: { size: width, type: WidthType.DXA },
    shading: bg ? { fill: bg, type: ShadingType.CLEAR } : undefined,
    margins: cellMargins,
    verticalAlign: "center",
    children: [new Paragraph({
      alignment: align || AlignmentType.CENTER,
      children: [new TextRun({ text: String(text), bold: !!bold, font: "Arial", size: 17, color: color || "333333" })],
    })]
  });
}

function makeRow(cells) { return new TableRow({ children: cells }); }

function heading(text, level, color) {
  return new Paragraph({
    spacing: { before: 200, after: 100 },
    children: [new TextRun({ text, bold: true, font: "Arial", size: level === 1 ? 36 : level === 2 ? 28 : 24, color: color || DARK })]
  });
}

function bodyText(text, opts = {}) {
  return new Paragraph({
    spacing: { before: 40, after: 40 },
    children: [new TextRun({ text, font: "Arial", size: 18, color: opts.color || "333333", bold: !!opts.bold })]
  });
}

// ── Match detail table builder ──
function buildInfoTable(infoRows, col1w, col2w) {
  const rows = [
    makeRow([hdrCell("项目", col1w), hdrCell("内容", col2w)]),
  ];
  infoRows.forEach(([k, v], i) => {
    rows.push(makeRow([
      dataCell(k, col1w, { bold: true, bg: i % 2 === 0 ? GRAY : undefined, align: AlignmentType.LEFT }),
      dataCell(v, col2w, { bg: i % 2 === 0 ? GRAY : undefined, align: AlignmentType.LEFT }),
    ]));
  });
  return new Table({ width: { size: CONTENT_W, type: WidthType.DXA }, columnWidths: [col1w, col2w], rows });
}

function buildScoreTable(headers, data, colWidths) {
  const totalW = colWidths.reduce((a, b) => a + b, 0);
  const rows = [makeRow(headers.map((h, i) => hdrCell(h, colWidths[i])))];
  data.forEach((row, ri) => {
    const isFirst = row[0] === "首选";
    const bg = isFirst ? GREEN : (ri % 2 === 1 ? GRAY : undefined);
    rows.push(makeRow(row.map((t, ci) =>
      dataCell(t, colWidths[ci], { bold: isFirst, bg })
    )));
  });
  return new Table({ width: { size: totalW, type: WidthType.DXA }, columnWidths: colWidths, rows });
}

// ═══════════════════════════════════════
// DOCUMENT
// ═══════════════════════════════════════
const doc = new Document({
  styles: {
    default: { document: { run: { font: "Arial", size: 20 } } },
  },
  sections: [
    // ── SECTION 1: Cover + Summary ──
    {
      properties: {
        page: {
          size: { width: PAGE_W, height: PAGE_H, orientation: PageOrientation.LANDSCAPE },
          margin: { top: MARGIN, bottom: MARGIN, left: MARGIN, right: MARGIN },
        },
      },
      headers: {
        default: new Header({
          children: [new Paragraph({
            alignment: AlignmentType.RIGHT,
            children: [new TextRun({ text: "2026世界杯 · 6月30日淘汰赛R32预测", font: "Arial", size: 16, color: "999999", italics: true })],
          })]
        }),
      },
      footers: {
        default: new Footer({
          children: [new Paragraph({
            alignment: AlignmentType.CENTER,
            children: [new TextRun({ text: "第 ", font: "Arial", size: 14, color: "999999" }),
                       new TextRun({ children: [PageNumber.CURRENT], font: "Arial", size: 14, color: "999999" }),
                       new TextRun({ text: " 页", font: "Arial", size: 14, color: "999999" })],
          })]
        }),
      },
      children: [
        // Title
        new Paragraph({
          alignment: AlignmentType.CENTER,
          spacing: { after: 60 },
          children: [new TextRun({ text: "2026世界杯 6月30日淘汰赛R32三场预测", bold: true, font: "Arial", size: 40, color: DARK })],
        }),
        new Paragraph({
          alignment: AlignmentType.CENTER,
          spacing: { after: 40 },
          children: [new TextRun({ text: "生成: 2026年6月29日 北京时间 | 数据: ESPN API + FIFA API + Transfermarkt | 框架: CLAUDE.md v17", font: "Arial", size: 16, color: "888888" })],
        }),

        // ── SUMMARY TABLE ──
        heading("预测汇总", 2, DARK),
        buildScoreTable(
          ["#", "时间", "阶段", "比赛", "身价比", "首选比分", "半场", "冷门"],
          [
            ["1", "01:00", "R32", "巴西 vs 日本", "3.4:1", "巴西 2-0", "1-0", "中"],
            ["2", "04:30", "R32", "德国 vs 巴拉圭", "6.2:1", "德国 3-0", "1-0", "低中"],
            ["3", "09:00", "R32", "荷兰 vs 摩洛哥", "1.7:1", "1-1 (荷加时晋级)", "0-0", "中高"],
          ],
          [600, 800, 800, 1800, 1200, 2400, 1000, 1000]
        ),

        new Paragraph({ children: [new PageBreak()] }),

        // ═══════════════════ MATCH 1: BRA vs JPN ═══════════════════
        heading("比赛1: 巴西 vs 日本  (01:00 BJT, NRG体育场, 休斯顿)", 2, RED),

        bodyText("基本信息", { bold: true }),
        buildInfoTable([
          ["FIFA排名", "巴西 #6 vs 日本 #18"],
          ["身价比", "巴西 €928M vs 日本 €271M ≈ 3.4:1"],
          ["晋级奖励", "16强对阵 科特迪瓦 vs 挪威 的胜者"],
          ["强队分类", "巴西 超级巨星型 | 日本 大巴+反击型"],
          ["冷门风险", "中 — 日本2026年已击败巴西+英格兰+战平荷兰"],
        ], 2000, CONTENT_W - 2000),

        bodyText(""),
        bodyText("小组赛回顾", { bold: true }),
        bodyText("巴西 (C组第1, 7分): 摩洛哥 1-1 / 海地 3-0 / 苏格兰 3-0 — 维尼修斯三场全部进球, 最后两场零封", { color: "555555" }),
        bodyText("日本 (F组第2, 5分): 荷兰 2-2 / 突尼斯 胜 / 瑞典 1-1 — 540分钟仅丢3球, 3-4-2-1大巴运转流畅", { color: "555555" }),

        bodyText("因素导向表", { bold: true }),
        buildScoreTable(
          ["因素", "有利方", "理由"],
          [
            ["维尼修斯状态(3场全进球+历史级xG)", "巴西 ★★★", "日本尚未面对过此级别单兵破局者"],
            ["日本3-4-2-1大巴已验证(540分钟仅丢3球)", "日本 ★★★", "已对荷兰+英格兰+巴西验证"],
            ["日本2025年10月3-2击败巴西", "日本 ★★★", "但不是同一防线(当时无马基+加布里埃尔)"],
            ["巴西对摩洛哥大巴1-1", "日本 ★★", "巴西对5后卫大巴仍有破局困难"],
            ["拉菲尼亚伤疑", "日本 ★", "巴西右路攻击力下降"],
            ["巴西防线vs10月完全不同", "巴西 ★★", "马尔基尼奥斯+加布里埃尔=更稳固"],
          ],
          [3600, 1600, 7760]
        ),

        bodyText(""),
        bodyText("亚非韧性评估(日本): 5/5 — 低位防守特优 | 速度反击特优 | 定位球高点良好 | 前30分钟特优 | 被压制不崩盘特优。本届世界杯防守纪律最好的非欧洲球队之一。", { color: "555555" }),
        bodyText("定位球攻防: 巴西 — 加布里埃尔+马尔基尼奥斯双塔头球 + 维尼修斯罚球。日本 — 板仓滉+富安健洋高点, 久保建英任意球。定位球是巴西对日本最可能得分路径。", { color: "555555" }),
        bodyText("冷门路径: 日本3-4-2-1大巴守住前70分钟→巴西急躁压上→伊东纯也反击1v1过掉丹尼洛→铃木彩艳连续扑救→1-0或1-1(加时/点球)", { color: "555555" }),

        bodyText("伤病/停赛", { bold: true }),
        buildScoreTable(
          ["球队", "球员", "状态", "影响"],
          [
            ["巴西", "拉菲尼亚(Raphinha)", "伤疑", "腿筋问题, 大概率替补"],
            ["巴西", "内马尔(Neymar)", "可替补", "对苏格兰20分钟替补登场"],
            ["日本", "—", "全员可用", "无伤停"],
          ],
          [1200, 2600, 1600, 7560]
        ),

        bodyText(""),
        bodyText("比分预测", { bold: true }),
        buildScoreTable(
          ["类型", "比分", "半场", "说明"],
          [
            ["首选", "巴西 2-0", "1-0", "维尼修斯个人破局→库尼亚锁定"],
            ["备选", "巴西 1-0", "0-0", "定位球或维尼修斯晚破门"],
            ["备选", "巴西 2-1", "1-1", "日本反击偷一球→巴西逆转"],
            ["备选", "1-1", "0-0", "日本大巴满分→加时决胜"],
          ],
          [1000, 1600, 1000, 9360]
        ),

        new Paragraph({ children: [new PageBreak()] }),

        // ═══════════════════ MATCH 2: GER vs PAR ═══════════════════
        heading("比赛2: 德国 vs 巴拉圭  (04:30 BJT, 吉列体育场, 福克斯堡)", 2, RED),

        bodyText("基本信息", { bold: true }),
        buildInfoTable([
          ["FIFA排名", "德国 #10 vs 巴拉圭 #48(估)"],
          ["身价比", "德国 €947M vs 巴拉圭 €154M ≈ 6.2:1"],
          ["晋级奖励", "16强对阵 法国 vs 瑞典 的胜者 (大概率法国, €1.52B!)"],
          ["强队分类", "德国 超级巨星型 | 巴拉圭 大巴+阿尔米隆反击型"],
          ["冷门风险", "低中 — 德国防线有速度短板但巴拉圭3场仅1球"],
        ], 2000, CONTENT_W - 2000),

        bodyText(""),
        bodyText("小组赛回顾", { bold: true }),
        bodyText("德国 (E组第1, 6分): 库拉索 7-1 / 科特迪瓦 2-1 / 厄瓜多尔 1-2 — 对厄瓜多尔失利暴露防线速度短板", { color: "555555" }),
        bodyText("巴拉圭 (D组第3, 4分): 美国 负 / 土耳其 1-0 / 澳大利亚 0-0 — 3场仅1球但仅丢2球, 大巴已验证", { color: "555555" }),

        bodyText("因素导向表", { bold: true }),
        buildScoreTable(
          ["因素", "有利方", "理由"],
          [
            ["身价比6.2:1", "德国 ★★★", "大差距, 德国正常发挥=稳胜"],
            ["德国对厄瓜多尔1-2失利→状态存疑", "巴拉圭 ★★", "防线被速度反击惩罚→巴拉圭有阿尔米隆"],
            ["穆西亚拉+维尔茨双核(€200M)", "德国 ★★★", "破大巴能力在纸面上极强"],
            ["巴拉圭3场仅进1球", "德国 ★★★", "攻击力极弱, 即使德国犯错也难惩罚"],
            ["巴拉圭大巴已验证(仅丢2球)", "巴拉圭 ★★", "零封土耳其+澳大利亚"],
            ["施洛特贝克伤缺+布朗肌肉问题", "巴拉圭 ★", "德国防线深度减弱"],
          ],
          [3800, 1600, 7560]
        ),

        bodyText(""),
        bodyText("防守韧性(巴拉圭): 4/5 — 低位防守特优 | 速度反击良好(仅阿尔米隆一人) | 定位球良好 | 前30分钟良好 | 被压制不崩盘良好。防守纪律好但攻击力太弱是致命短板。", { color: "555555" }),
        bodyText("定位球攻防: 德国 — 吕迪格+哈弗茨高点, 穆西亚拉/维尔茨罚球。巴拉圭 — 南美传统定位球威胁, 阿尔米隆任意球。德国对厄瓜多尔定位球防守存疑。", { color: "555555" }),
        bodyText("冷门路径: 德国久攻不下→纳格尔斯曼过度压上→阿尔米隆反击1v1吕迪格→1-0。或0-0加时点球。但巴拉圭攻击力太弱, 即使德国犯错也很难只靠1球守住。", { color: "555555" }),

        bodyText("比分预测", { bold: true }),
        buildScoreTable(
          ["类型", "比分", "半场", "说明"],
          [
            ["首选", "德国 3-0", "1-0", "上半场破大巴→下半场双核收割"],
            ["备选", "德国 2-0", "1-0", "标准比分, 德国控制全场"],
            ["备选", "德国 3-1", "2-0", "阿尔米隆反击→德国仍稳赢"],
            ["备选", "德国 2-1", "1-1", "巴拉圭先偷一个→德国逆转"],
          ],
          [1000, 1600, 1000, 9360]
        ),

        new Paragraph({ children: [new PageBreak()] }),

        // ═══════════════════ MATCH 3: NED vs MAR ═══════════════════
        heading("比赛3: 荷兰 vs 摩洛哥  (09:00 BJT, 西班牙对外银行体育场, 蒙特雷)", 2, RED),

        bodyText("基本信息", { bold: true }),
        buildInfoTable([
          ["FIFA排名", "荷兰 #8 vs 摩洛哥 #7"],
          ["身价比", "荷兰 €754M vs 摩洛哥 €448M ≈ 1.7:1"],
          ["晋级奖励", "16强对阵 加拿大"],
          ["强队分类", "荷兰 体系型倾向 | 摩洛哥 大巴+高质量反击型"],
          ["冷门风险", "中高 — 本日最难预测。博彩市场摩洛哥略热(+130赔率)"],
        ], 2000, CONTENT_W - 2000),

        bodyText(""),
        bodyText("小组赛回顾", { bold: true }),
        bodyText("荷兰 (F组第1, 7分): 日本 2-2 / 瑞典 胜 / 突尼斯 胜 — 3场10球攻击力强, 但防守对日本丢2球", { color: "555555" }),
        bodyText("摩洛哥 (C组第2, 7分): 巴西 1-1 / 苏格兰 1-0 / 海地 4-2 — 大巴逼平巴西, 赛巴里3场3球", { color: "555555" }),

        bodyText("因素导向表", { bold: true }),
        buildScoreTable(
          ["因素", "有利方", "理由"],
          [
            ["摩洛哥1-1逼平巴西(已验证大巴对超巨级)", "摩洛哥 ★★★", "巴西级别攻击力也被摩洛哥大巴压制"],
            ["赛巴里状态(3场3球, 即将加盟拜仁)", "摩洛哥 ★★", "攻击线有破局者"],
            ["荷兰10球攻击力", "荷兰 ★★", "但仅面对一个强队(日本)"],
            ["荷兰对日本2-2防守不稳", "摩洛哥 ★★", "摩洛哥反击质量高于日本"],
            ["摩洛哥2022四强+跨届经验", "摩洛哥 ★★", "淘汰赛经验远超普通球队"],
            ["身价比1.7:1 < 3:1 → 任何结果都可能", "双方", "不做强队方向强硬断言"],
          ],
          [4000, 1600, 7360]
        ),

        bodyText(""),
        bodyText("非洲韧性评估(摩洛哥): 5/5 — 低位防守特优 | 速度反击特优 | 定位球高点特优 | 前30分钟特优 | 被压制不崩盘特优。2022四强非偶然, 本届最强非洲防线。", { color: "555555" }),
        bodyText("定位球攻防: 荷兰 — 范戴克+布罗比高点, 哈克波/德容罚球。摩洛哥 — 迪奥普+赛巴里高点, 阿什拉夫任意球。关键: 范戴克防空 vs 赛巴里(186cm)头球。", { color: "555555" }),
        bodyText("冷门路径: 荷兰控球不进球→摩洛哥60-70分反击(阿什拉夫传中/赛巴里头球)→1-0→大巴升级→荷兰全线压上无果→常规时间摩洛哥胜。或0-0→加时→点球→布努扑点。最可能冷门: 摩洛哥1-0(常规时间)", { color: "555555" }),

        bodyText("比分 + 晋级预测", { bold: true }),
        buildScoreTable(
          ["类型", "比分(常规)", "半场", "说明"],
          [
            ["首选", "1-1 (荷兰加时晋级)", "0-0", "互有进球→加时荷兰深度优势胜"],
            ["备选", "荷兰 1-0", "0-0", "哈克波个人能力破大巴"],
            ["备选", "0-0 (点球)", "0-0", "双方保守→点球决胜"],
            ["备选", "摩洛哥 1-0", "0-0", "赛巴里反击/定位球→大巴死守"],
          ],
          [1200, 2600, 1000, 8160]
        ),

        bodyText(""),
        bodyText("伤病/停赛: 荷兰 — 邓弗里斯/布罗比确认可用, 范德芬左后卫回归首发。摩洛哥 — 马兹拉维/迪奥普/布阿迪/乌纳希全部回归首发。双方主力基本齐整。", { color: "555555" }),

        // ── Knockout path ──
        new Paragraph({ children: [new PageBreak()] }),
        heading("淘汰赛路径总览", 2, DARK),
        bodyText("巴西/日本胜者 → R16 → 科特迪瓦 vs 挪威 的胜者 → QF碰德国区 [难度: 中]"),
        bodyText("德国/巴拉圭胜者 → R16 → 法国 vs 瑞典 的胜者 (大概率法国 €1.52B!) [难度: 极高!]", { bold: true, color: RED }),
        bodyText("荷兰/摩洛哥胜者 → R16 → 加拿大 → QF碰阿根廷区 [难度: 中高]"),

        bodyText(""),
        bodyText("风险提示", { bold: true }),
        bodyText("1. 巴西vs日本: 日本已在2026年击败巴西+英格兰+战平荷兰——大巴对强队克制力已验证。如果巴西前30分钟不进球, 比赛可能苦战。"),
        bodyText("2. 德国vs巴拉圭: 德国对厄瓜多尔1-2失利是警报——高位防线对速度反击脆弱。但巴拉圭3场仅1球攻击力是致命短板。"),
        bodyText("3. 荷兰vs摩洛哥: 身价比仅1.7:1, 双方均是2022四强/八强级别。摩洛哥大巴已验证(对巴西1-1)。市场定价摩洛哥略优需认真对待。", { bold: true }),

        bodyText(""),
        bodyText("数据: ESPN API + FIFA API + Sports Mole + SI + Planet Football + Transfermarkt | 身价: Transfermarkt via Planet Football (2026年6月) | 分析框架: CLAUDE.md v17", { color: "999999" }),
      ],
    },
  ],
});

// ── Save ──
const outPath = __dirname + "/2026年6月30日_3场预测.docx";
Packer.toBuffer(doc).then(buf => {
  fs.writeFileSync(outPath, buf);
  console.log("DOCX saved: " + outPath);
});

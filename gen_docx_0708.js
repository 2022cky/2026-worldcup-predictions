// gen_docx_0708_v7.js — 7月8日预测报告
// [v7] 盘口换行修复: clm() 函数+ml:true 使\n真实换行 | 隐含概率 | 比分加概率%
const fs = require("fs");
const { Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell, Header, Footer, AlignmentType, PageOrientation, BorderStyle, WidthType, ShadingType, PageNumber, PageBreak, HeadingLevel } = require("docx");
const F = "Microsoft YaHei";
const D = "1A1A2E", R = "C0392B", W = "FFFFFF", GY = "F2F2F2", HB = "1A1A2E", GR = "27AE60", OR = "F39C12", LG = "E8F8F5";
const thin = { style: BorderStyle.SINGLE, size: 1, color: "DDDDDD" };
const bd = { top: thin, bottom: thin, left: thin, right: thin };

function pp(c, o = {}) { return new Paragraph({ alignment: o.al || AlignmentType.LEFT, spacing: { after: o.a != null ? o.a : 80, before: o.b || 20 }, children: Array.isArray(c) ? c : [c] }); }
function tx(text, o = {}) { return new TextRun({ text: String(text), font: F, size: o.s || 18, bold: o.b || false, color: o.c || D }); }
function hd(text, level) { const sz = { 1: 32, 2: 28, 3: 24 }; return new Paragraph({ heading: level === 1 ? HeadingLevel.HEADING_1 : HeadingLevel.HEADING_2, spacing: { before: level === 1 ? 300 : 200, after: 120 }, children: [new TextRun({ text, font: F, size: sz[level] || 24, bold: true, color: D })] }); }

function cl(text, opts = {}) {
  const runs = Array.isArray(text) ? text.map(r => typeof r === "string" ? tx(r, opts) : new TextRun({ ...{ font: F, size: opts.s || 16, color: opts.c || D }, ...r })) : [new TextRun({ text: String(text), font: F, size: opts.s || 16, bold: opts.b || false, color: opts.c || D })];
  return new TableCell({ borders: bd, width: opts.w ? { size: opts.w, type: WidthType.DXA } : undefined, shading: opts.bg ? { fill: opts.bg, type: ShadingType.CLEAR } : undefined, verticalAlign: "center", margins: { top: 60, bottom: 60, left: 100, right: 100 }, children: [new Paragraph({ alignment: opts.al === "L" ? AlignmentType.LEFT : AlignmentType.CENTER, children: runs })] });
}

// Multi-paragraph cell: \n → real line breaks (one Paragraph per line)
function clm(text, opts = {}) {
  const lines = String(text).split("\n");
  const paras = lines.map(line => new Paragraph({
    alignment: opts.al === "L" ? AlignmentType.LEFT : AlignmentType.CENTER,
    spacing: { after: 40, before: 0 },
    children: [new TextRun({ text: line, font: F, size: opts.s || 16, bold: opts.b || false, color: opts.c || D })],
  }));
  return new TableCell({ borders: bd, width: opts.w ? { size: opts.w, type: WidthType.DXA } : undefined, shading: opts.bg ? { fill: opts.bg, type: ShadingType.CLEAR } : undefined, verticalAlign: "top", margins: { top: 60, bottom: 60, left: 100, right: 100 }, children: paras });
}

function rw(data, opts = {}) {
  return new TableRow({ children: data.map((d, i) => {
    const co = { ...opts, w: opts.ws ? opts.ws[i] : undefined, al: opts.as ? opts.as[i] : "center" };
    if (typeof d === "object" && !Array.isArray(d)) {
      return d.ml ? clm(d.text, { ...co, ...d }) : cl(d.text, { ...co, ...d });
    }
    return cl(d, co);
  })});
}

function groupReviewTable(teamName, groupInfo, rows_data) {
  const parts = [];
  parts.push(pp([tx(teamName + " (" + groupInfo + ")", { s: 16, b: true })], { b: 60, a: 20 }));
  parts.push(new Table({
    width: { size: 13800, type: WidthType.DXA }, columnWidths: [3000, 1500, 9300],
    rows: [
      rw(["对手","比分","关键"], { ws:[3000,1500,9300], bg:HB, c:W, b:true, s:15 }),
      ...rows_data.map((rd, idx) => rw(rd, { ws:[3000,1500,9300], bg: idx%2===0?GY:undefined, s:14, al:"L" })),
    ],
  }));
  parts.push(pp([], { a: 40 }));
  return parts;
}

// ═══════════════════════════════════════════
// DOCUMENT
// ═══════════════════════════════════════════
const doc = new Document({
  styles: {
    default: { document: { run: { font: F, size: 18 } } },
    paragraphStyles: [
      { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true, run: { size: 32, bold: true, font: F, color: D }, paragraph: { spacing: { before: 300, after: 120 }, outlineLevel: 0 } },
      { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true, run: { size: 26, bold: true, font: F, color: D }, paragraph: { spacing: { before: 200, after: 100 }, outlineLevel: 1 } },
      { id: "Heading3", name: "Heading 3", basedOn: "Normal", next: "Normal", quickFormat: true, run: { size: 22, bold: true, font: F, color: D }, paragraph: { spacing: { before: 140, after: 60 }, outlineLevel: 2 } },
    ]
  },
  sections: [{
    properties: { page: { size: { width: 11906, height: 16838, orientation: PageOrientation.LANDSCAPE }, margin: { top: 1220, right: 1300, bottom: 1220, left: 1300 } } },
    headers: { default: new Header({ children: [new Paragraph({ alignment: AlignmentType.RIGHT, children: [new TextRun({ text: "2026 FIFA 世界杯  |  16强淘汰赛  |  7月8日预测报告", font: F, size: 14, color: "999999", italics: true })] })] }) },
    footers: { default: new Footer({ children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "页 ", font: F, size: 14, color: "999999" }), new TextRun({ children: [PageNumber.CURRENT], font: F, size: 14, color: "999999" }), new TextRun({ text: "  |  CLAUDE.md v20  |  docx skill", font: F, size: 14, color: "999999" })] })] }) },
    children: [

      // ═══════ TITLE ═══════
      pp([], { a: 40 }),
      new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 0 }, children: [tx("2026 FIFA 世界杯", { s: 48, b: true, c: R })] }),
      new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 40 }, children: [tx("7月8日 16强淘汰赛 预测报告", { s: 32, b: true })] }),
      new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 0 }, children: [tx("阿根廷 vs 埃及  |  瑞士 vs 哥伦比亚", { s: 20, c: "7F8C8D" })] }),
      new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 20 }, children: [tx("Mercedes-Benz 体育场 (亚特兰大)  /  BC Place 体育场 (温哥华)", { s: 18, c: "7F8C8D" })] }),
      new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 30 }, children: [tx("[v7] 盘口换行修复 | 隐含概率替换\"押X赢X\" | 比分加概率% | 小组回顾=表格 | 迪马利亚退役修正", { s: 14, c: R, b: true })] }),

      // ═══════ SUMMARY ═══════
      hd("预测汇总", 2),
      new Table({
        width: { size: 13800, type: WidthType.DXA }, columnWidths: [500, 3200, 1000, 1200, 2000, 700, 2500, 700],
        rows: [
          rw(["#","比赛 (北京时间)","身价比","强队分类","首选比分","半场","备选比分(按概率)","冷门风险"], { ws:[500,3200,1000,1200,2000,700,2500,700], bg:HB, c:W, b:true, s:16 }),
          rw(["95","阿根廷 vs 埃及 (00:00)","6.9 : 1","阿根廷: 超级巨星型", { text: "阿根廷 3-1 埃及", b: true, c: R }, "1-0", "2-0 / 2-1 / 1-0 / 3-0 / 1-1(加时)", { text: "中低", b: true, c: W, bg: OR }], { ws:[500,3200,1000,1200,2000,700,2500,700], s:16 }),
          rw(["96","瑞士 vs 哥伦比亚 (04:00)","1.33 : 1","平衡型 vs 低效热门", { text: "瑞士 2-1 哥伦比亚", b: true, c: R }, "1-0", "1-1(加时) / 2-0 / 1-0 / 哥伦比亚2-1 / 0-0(加时)", { text: "中高", b: true, c: W, bg: OR }], { ws:[500,3200,1000,1200,2000,700,2500,700], bg:GY, s:16 }),
        ],
      }),

      // ══════════════════════  比赛95: 阿根廷 vs 埃及  ══════════════════════
      hd("比赛95: 阿根廷 vs 埃及  (北京时间 00:00)", 2),
      pp([tx("16强淘汰赛  |  四分之一决赛对手: 瑞士/哥伦比亚胜者  |  国际足联排名 #2 vs #30  |  总身价 8.075亿欧元 vs 1.165亿欧元 (约7:1)  |  Mercedes-Benz 体育场, 亚特兰大", { s: 16, c: "7F8C8D" })]),

      hd("小组赛回顾", 3),
      ...groupReviewTable("阿根廷", "J组第1名 · 9分 · 进8球失1球 · 小组全胜", [
        ["阿尔及利亚","3-0","小组赛首战大胜"],
        ["奥地利","2-0","小组赛次战稳健取胜"],
        ["约旦","3-1","小组赛末战锁定头名"],
        ["佛得角 (32强赛)","3-2 (加时)","梅西29' / 德里·杜阿尔特59' / 利桑德罗92' / 卡布拉尔103'世界波 / 乌龙111'制胜"],
      ]),
      pp([tx("[注意] 上一场120分钟, 恢复仅4天. 梅西(38岁)/德保罗(31岁)/奥塔门迪(37岁)体能是最大变数.", { s: 14, c: R, b: true })]),

      ...groupReviewTable("埃及", "G组第2名 · 5分 · 进5球失3球 · 小组不败", [
        ["比利时","1-1","阿舒尔进球——逼平身价5倍对手"],
        ["新西兰","3-1","萨拉赫进球——攻击力全开"],
        ["伊朗","1-1","萨拉赫57'伤退→随后被追平"],
        ["澳大利亚 (32强赛)","1-1 (点球4-2)","阿舒尔13' / 哈尼55'乌龙 / 加时0-0 / 点球4-2胜. 首支赢得WC点球大战的非洲球队"],
      ]),
      pp([tx("[注意] 萨拉赫带伤打满120'——淘汰赛\"保守声明\"=烟雾弹. 非洲杯冠军(2024)心理素质已验证.", { s: 14, c: R, b: true })]),

      // ═══════ ODDS ═══════
      hd("盘口分析 (OddsShark / DraftKings / Kalshi / football-predictions.ai)", 3),
      new Table({
        width: { size: 13800, type: WidthType.DXA }, columnWidths: [4000, 9800],
        rows: [
          rw([{text:"盘口类型",b:true,c:W},{text:"赔率数据与分析解读",b:true,c:W}], { ws:[4000,9800], bg:HB, s:15 }),
          rw([{text:"胜平负\n(90分钟)",b:true,ml:true},{text:"阿根廷胜: 1.36 ~ 1.40  → 隐含概率约 71%\n平局: 4.70 ~ 5.25  → 隐含概率约 19%\n埃及胜: 8.00 ~ 10.50  → 隐含概率约 9%\n→ 市场强烈倾向阿根廷90分钟内取胜, 与我们的方向一致",ml:true,al:"L"}], { ws:[4000,9800], s:14 }),
          rw([{text:"让球盘\n(亚洲盘)",b:true,ml:true},{text:"阿根廷让 1.5 球: 赔率约 2.00  → 隐含概率约 50%\n阿根廷需净胜 ≥2球(如2-0、3-1)才算赢盘\n净胜1球(如2-1、1-0)均输盘\n→ 市场对阿根廷大胜信心有限, 佛得角恐慌后遗症",ml:true,al:"L"}], { ws:[4000,9800], bg:GY, s:14 }),
          rw([{text:"大小球\n(总进球数)",b:true,ml:true},{text:"大 2.5 球: +101 ~ +105  → 隐含概率约 50%\n小 2.5 球: -129 ~ -135  → 隐含概率约 56%\n→ 市场倾向低比分. 我们判断双方防线均有漏洞, 大球概率高于市场定价",ml:true,al:"L"}], { ws:[4000,9800], s:14 }),
          rw([{text:"波胆\n(精确比分)",b:true,ml:true},{text:"阿根廷 1-0  @4.75 (21%)   ← 市场最高概率\n阿根廷 2-0  @5.25 (17%)\n阿根廷 2-1  @8.50 (12%)\n阿根廷 3-0  @9.00 (11%)\n1-1 平局  @8.00 (12%)\n0-0 平局  @11.00 (9%)\n→ 我们偏向双方都进球的场景(2-1/3-1), 被市场低估",ml:true,al:"L"}], { ws:[4000,9800], bg:GY, s:14 }),
          rw([{text:"双方都进球\n(BTTS)",b:true,ml:true},{text:"否 @1.54 (65%)  —— 市场认为至少一方被零封\n是 @2.30 (43%)  —— ★我们偏向\"是\": 阿根廷防线速度不足, 萨拉赫有能力破门",ml:true,al:"L"}], { ws:[4000,9800], s:14 }),
          rw([{text:"晋级赔率",b:true,ml:true},{text:"阿根廷晋级 @1.15 (87%)  |  埃及晋级 @5.50 (18%)\n→ 方向一致: 阿根廷晋级, 但埃及不是零概率",ml:true,al:"L"}], { ws:[4000,9800], bg:GY, s:14 }),
          rw([{text:"★ 我们的\n盘口判断",b:true,c:R,ml:true},{text:"市场方向与我们一致(阿根廷胜). 核心分歧有三:\n① 双方都进球(BTTS=是)概率高于市场——阿根廷对佛得角失2球非偶然\n② 大球(Over 2.5)价值优于市场——双方防线均有漏洞\n③ 波胆价值: 2-1(@8.50)和3-1被低估, 1-0(@4.75)被高估",ml:true,al:"L",c:R}], { ws:[4000,9800], s:14 }),
        ],
      }),
      pp([], { a: 20 }),

      // ═══════ LINEUP ═══════
      hd("预测首发阵容 (FIFA官方26人名单 + 媒体预测)", 3),
      pp([tx("阿根廷 (4-4-2): ", { s: 16, b: true }), tx("埃米利亚诺·马丁内斯(门将) | 莫利纳(右后卫) 罗梅罗(中后卫) 利桑德罗·马丁内斯(中后卫) 塔利亚菲科(左后卫) | 德保罗(右中场) 麦克阿利斯特(中前卫) 恩佐·费尔南德斯(中前卫) 阿尔马达(左中场) | 梅西(前锋)[队长] 劳塔罗·马丁内斯(前锋)", { s: 14 })], { a: 0 }),
      pp([tx("埃及 (4-4-2): ", { s: 16, b: true }), tx("舒贝尔(门将) | 哈尼(右后卫) 阿卜杜勒莫内姆(中后卫) 拉比亚(中后卫) 哈菲兹(左后卫) | 阿舒尔(右中场) 法蒂(中前卫) 阿提亚(中前卫) 泽科(左中场) | 马尔穆什(前锋) 萨拉赫(前锋)[队长]", { s: 14 })]),
      pp([tx("[核实] 无迪马利亚(已退役)/无迪巴拉 | 超级替补=阿尔瓦雷斯+尼古拉斯·冈萨雷斯(马竞) | 阿尔马达=马竞非ATL联 | 埃及伊布拉希姆停赛→阿卜杜勒莫内姆替代", { s: 12, c: R })]),

      hd("核心球员评分", 3),
      new Table({
        width: { size: 13800, type: WidthType.DXA }, columnWidths: [700, 2800, 800, 1300, 8200],
        rows: [
          rw(["号码","球员","评分","位置","表现点评"], { ws:[700,2800,800,1300,8200], bg:HB, c:W, b:true, s:15 }),
          rw(["10","利昂内尔·梅西 (阿根廷)[队长]","9.0","前锋","[核心] 世界杯20球历史纪录. 连续8场WC进球. 38岁但淘汰赛模式"], { ws:[700,2800,800,1300,8200], bg:LG, s:14 }),
          rw(["10","穆罕默德·萨拉赫 (埃及)[队长]","9.0","前锋","[核心] 本届16次创造机会=并列最高. 超巨——单兵可改变比赛"], { ws:[700,2800,800,1300,8200], s:14 }),
          rw(["23","埃米利亚诺·马丁内斯 (阿根廷)","8.5","门将","2022金手套. 但对佛得角失2球——防线保护已不如2022"], { ws:[700,2800,800,1300,8200], bg:GY, s:14 }),
          rw(["20","麦克阿利斯特 (阿根廷)","8.0","中前卫","利物浦核心. WC状态极佳. 梅西之外的第二进攻引擎"], { ws:[700,2800,800,1300,8200], s:14 }),
          rw(["22","劳塔罗·马丁内斯 (阿根廷)","8.0","前锋","国际米兰核心. 对佛得角0进球但防守压迫好"], { ws:[700,2800,800,1300,8200], bg:GY, s:14 }),
          rw(["7","奥马尔·马尔穆什 (埃及)","7.5","前锋","曼城前锋. 萨拉赫吸引防守→获更多空间. 本届0G0A"], { ws:[700,2800,800,1300,8200], s:14 }),
          rw(["22","艾哈迈德·泽科 (埃及)","7.0","左中场","边路突破手. 对莫利纳+塔利亚菲科的速度=埃及第二威胁点"], { ws:[700,2800,800,1300,8200], bg:GY, s:14 }),
          rw(["—","胡利安·阿尔瓦雷斯 (阿根廷)","—","前锋","[超级替补] 马竞前锋. 64'换人窗口. 禁区嗅觉+把握机会能力"], { ws:[700,2800,800,1300,8200], s:14 }),
        ],
      }),

      hd("因素导向表", 3),
      new Table({
        width: { size: 13800, type: WidthType.DXA }, columnWidths: [5800, 1800, 6200],
        rows: [
          rw(["因素","有利方","详细理由"], { ws:[5800,1800,6200], bg:HB, c:W, b:true, s:15 }),
          rw(["梅西破局能力: 20球纪录+连续8场进球","阿根廷 ★★★","超级巨星型——梅西一人可在任何时候打破僵局. 埃及4场0零封"], {ws:[5800,1800,6200],s:14}),
          rw(["萨拉赫创造能力: 16次机会=赛事最高","埃及 ★★★","超巨——即使埃及整体弱, 萨拉赫一人可改变比分. ARG中后卫转身慢"], {ws:[5800,1800,6200],bg:GY,s:14}),
          rw(["阿根廷防线不稳: 对佛得角失2球(7/4教训)","埃及 ★★","利桑德罗59'被穿裆+103'世界波——结构性问题非偶然. 佛得角5/5不崩盘"], {ws:[5800,1800,6200],s:14}),
          rw(["埃及终结效率低: 62%控球率120'仅1球","阿根廷 ★★","对澳大利亚仅从定位球二次进攻得分. 萨拉赫120'0G0A"], {ws:[5800,1800,6200],bg:GY,s:14}),
          rw(["埃及防线0零封: 4场场均预期失球1.48","阿根廷 ★★★","梅西+劳塔罗+麦克阿利斯特+阿尔马达应能在埃及防线上找到≥2球"], {ws:[5800,1800,6200],s:14}),
        ],
      }),
      pp([tx("冷门风险: 中低  |  ARG超巨可破局  |  埃及有萨拉赫+防线速度劣势  |  双方120'消耗=最大未知", { s: 16, b: true, c: OR })]),

      hd("比分预测", 3),
      new Table({
        width: { size: 13800, type: WidthType.DXA }, columnWidths: [1200, 1800, 800, 1000, 9000],
        rows: [
          rw(["类型","比分","半场","概率","进球者与比赛逻辑"], { ws:[1200,1800,800,1000,9000], bg:HB, c:W, b:true, s:15 }),
          rw(["[首选]","阿根廷 3-1 埃及","1-0","~35%","梅西23'突破 → 劳塔罗39'角球头球 → 萨拉赫55'反击单刀 → 梅西72'远射锁定. 阿根廷攻击力足够, 埃及反击必进1球"], { ws:[1200,1800,800,1000,9000], bg:LG, s:13 }),
          rw(["备选1","阿根廷 2-0 埃及","1-0","~22%","梅西31'破门 → 阿尔瓦雷斯76'替补锁定. ARG防线改善, 埃及进攻无力"], { ws:[1200,1800,800,1000,9000], s:13 }),
          rw(["备选2","阿根廷 2-1 埃及","0-0","~18%","萨拉赫65'先破 → 梅西68'点球扳平 → 劳塔罗79'绝杀. 惊魂剧本"], { ws:[1200,1800,800,1000,9000], bg:GY, s:13 }),
          rw(["[铁律15]","阿根廷 1-0 埃及","0-0","~10%","梅西58'任意球制胜. 淘汰赛最常见比分(历史约27%)"], { ws:[1200,1800,800,1000,9000], s:13 }),
          rw(["[冷门]","1-1(加时→埃及点球)","0-0","~7%","萨拉赫61'反击 → 梅西79'远射扳平 → 加时ARG老将体能崩溃 → EGY点球胜"], { ws:[1200,1800,800,1000,9000], bg:GY, c:R, s:13 }),
        ],
      }),

      // ═══ PAGE BREAK ═══
      new Paragraph({ children: [new PageBreak()] }),

      // ══════════════════════  比赛96: 瑞士 vs 哥伦比亚  ══════════════════════
      hd("比赛96: 瑞士 vs 哥伦比亚  (北京时间 04:00)", 2),
      pp([tx("16强淘汰赛  |  四分之一决赛对手: 阿根廷/埃及胜者  |  国际足联排名 #15 vs #10  |  总身价 3.325亿欧元 vs 约2.5亿欧元 (约1.33:1)  |  BC Place 体育场, 温哥华  |  室内球场", { s: 16, c: "7F8C8D" })]),

      hd("小组赛回顾", 3),
      ...groupReviewTable("瑞士", "B组第1名 · 7分 · 进7球失3球 · 近10场不败(7胜3平)", [
        ["卡塔尔","1-1","首战平局——瑞士慢热"],
        ["波黑","4-1","大胜——攻击力展现"],
        ["加拿大","2-1","巴尔加斯46' / 曼扎姆比57' / Promise David 76'(加). 顶住加拿大主场压力"],
        ["阿尔及利亚 (32强赛)","2-0","恩博洛10' / 恩多耶46'. 完全控制——从未受威胁"],
      ]),
      pp([tx("[注意] 10场不败(7胜3平)——对手平均排名40.6位(更强). 恩博洛6球为金靴竞争者.", { s: 14, c: R, b: true })]),

      ...groupReviewTable("哥伦比亚", "K组第1名 · 7分 · 进4球失1球 · 3场零封/4场", [
        ["葡萄牙","1-1","逼平葡萄牙——防守验证"],
        ["乌兹别克斯坦","3-1","迪亚斯1球1助(9.0 MOTM)——攻击力展现"],
        ["刚果民主共和国","胜","末战取胜——锁定头名"],
        ["加纳 (32强赛)","1-0","阿里亚斯14'(苏亚雷斯助攻). 加纳全场0射正——防守统治级. 但20+射门仅1球暴露攻击效率"],
      ]),
      pp([tx("[注意] 3场零封对手: 刚果(T3)/乌兹别克(T4)/加纳(T3)——均非顶级. 铁律12降级: ★★★→★★. 科尔多瓦(前锋)伤缺.", { s: 14, c: R, b: true })]),

      // ═══════ ODDS ═══════
      hd("盘口分析 (DraftKings / Kalshi / VSiN / Racing Post)  [注意] 我们与市场方向相反!", 3),
      new Table({
        width: { size: 13800, type: WidthType.DXA }, columnWidths: [4000, 9800],
        rows: [
          rw([{text:"盘口类型",b:true,c:W},{text:"赔率数据与分析解读",b:true,c:W}], { ws:[4000,9800], bg:HB, s:15 }),

          rw([{text:"胜平负\n(90分钟)",b:true,ml:true},{text:"哥伦比亚胜: 2.20 ~ 2.30  → 隐含概率约 43%  ← 市场热门方\n平局: 3.10 ~ 3.20  → 隐含概率约 30%\n瑞士胜: 3.40 ~ 3.70  → 隐含概率约 27%\n★ 我们逆向于市场——瑞士+270被低估. 证据: 10场不败+更强对手+恩博洛6球",ml:true,al:"L"}], { ws:[4000,9800], s:14 }),

          rw([{text:"让球盘\n(亚洲盘)",b:true,ml:true},{text:"哥伦比亚让 0.5 球: 赔率 +125 → 需赢球才算赢盘(打平也输盘)\n瑞士受让 0.5 球: 赔率 -155 → 不输(赢或平)即赢盘\n→ 瑞士+0.5有防守价值——打平也赢盘. 结合我们预测瑞士可能赢球, 价值更高",ml:true,al:"L"}], { ws:[4000,9800], bg:GY, s:14 }),

          rw([{text:"大小球\n(总进球数)",b:true,ml:true},{text:"大 2.5 球: +135 ~ +146  → 隐含概率约 40%\n小 2.5 球: -165 ~ -175  → 隐含概率约 63%\n→ 市场强烈倾向低比分. 合理但瑞士场均2.3球+迪亚斯单点爆破使大球有潜在价值",ml:true,al:"L"}], { ws:[4000,9800], s:14 }),

          rw([{text:"波胆\n(精确比分)",b:true,ml:true},{text:"1-0(任意方) @6.50 (15%)  ← 淘汰赛最常见比分\n1-1 @6.00 (17%)  ← 均势比赛最可能平局\n哥伦比亚 1-0 @8.00 (12%)  ← 市场首选\n瑞士 1-0 @9.50 (10%)\n哥伦比亚 2-1 @10.00 (10%)\n瑞士 2-1 @13.00 (8%)  ← ★我们的首选, 严重被低估!",ml:true,al:"L"}], { ws:[4000,9800], bg:GY, s:14 }),

          rw([{text:"双方都进球\n(BTTS)",b:true,ml:true},{text:"否 @1.67 (60%)  —— 市场认为至少一方被零封\n是 @2.10 (48%)  —— ★哥伦比亚3场零封但对手弱, 面对恩博洛6球难零封",ml:true,al:"L"}], { ws:[4000,9800], s:14 }),

          rw([{text:"晋级赔率",b:true,ml:true},{text:"哥伦比亚晋级 @1.63 (61%)  |  瑞士晋级 @2.30 (43%)\n★ 瑞士晋级概率应接近50%——市场高估了哥伦比亚约11个百分点. 最大偏差!",ml:true,al:"L"}], { ws:[4000,9800], bg:GY, s:14 }),

          rw([{text:"★ 我们的\n盘口判断",b:true,c:R,ml:true},{text:"逆向于市场的核心逻辑:\n① 瑞士10场不败(对手更强) > 哥伦比亚3场零封(含金量不足)\n② 恩博洛6球+曼扎姆比3球2助=攻击力被严重低估\n③ 瑞士中场(扎卡+弗罗伊勒+曼扎姆比) > 哥伦比亚(普埃尔塔22岁/经验不足)\n④ 晋级赔率瑞士+130是最大价值——市场高估哥伦比亚约11个百分点\n\nCovers分析师James Eastham(21年经验)与我们同向——也认为赔率差距\"没有任何形式依据\"",ml:true,al:"L",c:R}], { ws:[4000,9800], s:14 }),
        ],
      }),
      pp([], { a: 20 }),

      // ═══════ LINEUP ═══════
      hd("预测首发阵容 (FIFA官方26人名单 + 媒体预测)", 3),
      pp([tx("瑞士 (4-2-3-1): ", { s: 16, b: true }), tx("科贝尔(门将) | 扎卡里亚(右后卫/FIFA列中场→本届打RB) 阿坎吉(中后卫) 埃尔韦迪(中后卫) R.罗德里格斯(左后卫) | 弗罗伊勒(防守中场) 扎卡(防守中场)[队长] | 恩多耶(右边锋) 曼扎姆比(攻击中场) 巴尔加斯(左边锋) | 恩博洛(前锋)", { s: 14 })], { a: 0 }),
      pp([tx("哥伦比亚 (4-2-3-1): ", { s: 16, b: true }), tx("巴尔加斯(门将) | 穆尼奥斯(右后卫) 达.桑切斯(中后卫) 卢库米(中后卫) 莫希卡(左后卫) | 普埃尔塔(防守中场) 莱尔马(防守中场) | 阿里亚斯(右边锋) 哈梅斯(攻击中场) 迪亚斯(左边锋) | 苏亚雷斯(前锋)", { s: 14 })]),
      pp([tx("[核实] 扎卡里亚=FIFA名单中场, 本届打RB→\"非本职\" | 恩多耶/曼扎姆比/恩博洛均在26人名单 | 科尔多瓦伤缺→苏亚雷斯首发", { s: 12, c: R })]),

      hd("核心球员评分", 3),
      new Table({
        width: { size: 13800, type: WidthType.DXA }, columnWidths: [700, 2800, 800, 1500, 8000],
        rows: [
          rw(["号码","球员","评分","位置","表现点评"], { ws:[700,2800,800,1500,8000], bg:HB, c:W, b:true, s:15 }),
          rw(["7","布雷尔·恩博洛 (瑞士)","8.5","前锋","[核心] 本届6球!! 金靴竞争者. 身体对抗顶级+头球威胁"], { ws:[700,2800,800,1500,8000], bg:LG, s:13 }),
          rw(["7","路易斯·迪亚斯 (哥伦比亚)","8.5","左边锋","[MOTM候选] 拜仁·国家队76场23球. 对位扎卡里亚(=非本职RB)——全场最致命对位"], { ws:[700,2800,800,1500,8000], s:13 }),
          rw(["5","曼努埃尔·阿坎吉 (瑞士)","8.5","中后卫","曼城·英超三冠王. 对迪亚斯有直接交锋经验——防守迪亚斯的关键人物"], { ws:[700,2800,800,1500,8000], bg:GY, s:13 }),
          rw(["10","格拉尼特·扎卡 (瑞士)[队长]","8.5","防守中场","勒沃库森·攻防转换核心. 10场不败场均90+传球——控制节奏的大脑"], { ws:[700,2800,800,1500,8000], s:13 }),
          rw(["1","格雷戈尔·科贝尔 (瑞士)","8.5","门将","多特蒙德·10场5次零封. 防线基石. 若进点球大战——优于对方门将"], { ws:[700,2800,800,1500,8000], bg:GY, s:13 }),
          rw(["9","约翰·曼扎姆比 (瑞士)","8.0","攻击中场","[突破之星] 20岁! 本届3球2助攻. 哥伦比亚后腰(22岁)从未面对"], { ws:[700,2800,800,1500,8000], s:13 }),
          rw(["10","哈梅斯·罗德里格斯 (哥伦比亚)","7.5","攻击中场","34岁·2014金靴6球. WC模式>俱乐部. 任意球+角球传中=致命"], { ws:[700,2800,800,1500,8000], bg:GY, s:13 }),
          rw(["9","路易斯·苏亚雷斯 (哥伦比亚)","7.5","前锋","葡萄牙体育·14场4球. 32强制胜助攻. 对埃尔韦迪=第二攻击点"], { ws:[700,2800,800,1500,8000], s:13 }),
        ],
      }),

      hd("因素导向表", 3),
      new Table({
        width: { size: 13800, type: WidthType.DXA }, columnWidths: [5800, 1800, 6200],
        rows: [
          rw(["因素","有利方","详细理由"], { ws:[5800,1800,6200], bg:HB, c:W, b:true, s:15 }),
          rw(["瑞士10场不败(7胜3平): 对更强对手场均2.3球","瑞士 ★★★","对手平均排名40.6 vs 哥伦比亚对手56.3. 瑞士进攻已充分验证"], {ws:[5800,1800,6200],s:14}),
          rw(["哥伦比亚3场零封: 4场仅失1球","哥伦比亚 ★★","[铁律12降级: ★★★→★★] 零封对手均非顶级. 从未面对瑞士(恩博洛6球)"], {ws:[5800,1800,6200],bg:GY,s:14}),
          rw(["迪亚斯(7000万) vs 扎卡里亚(非本职右后卫)","哥伦比亚 ★★★","[本场#1对位!] 迪亚斯=拜仁顶级左边锋 vs 扎卡里亚=防守中场临时打RB"], {ws:[5800,1800,6200],s:14}),
          rw(["恩博洛6球(金靴级别) vs 哥伦比亚防线","瑞士 ★★","桑切斯+卢库米从未面对如此火热中锋. 6球不是偶然"], {ws:[5800,1800,6200],bg:GY,s:14}),
          rw(["盘口低估瑞士: +270(27%) vs 哥伦比亚+131(43%)","瑞士 ★","[新纳入] 市场可能因排名+名气溢价高估哥伦比亚. Covers分析师同向"], {ws:[5800,1800,6200],s:14}),
        ],
      }),
      pp([tx("冷门风险: 中高  |  均势比赛(1.33:1)  |  迪亚斯vs扎卡里亚=COL最明确制胜路径  |  恩博洛6球+瑞士中场=对抗", { s: 16, b: true, c: OR })]),

      hd("比分预测  [注意] 我们逆向于市场——市场以哥伦比亚为热门, 我们认为瑞士被低估", 3),
      new Table({
        width: { size: 13800, type: WidthType.DXA }, columnWidths: [1200, 1800, 800, 1000, 9000],
        rows: [
          rw(["类型","比分","半场","概率","进球者与比赛逻辑"], { ws:[1200,1800,800,1000,9000], bg:HB, c:W, b:true, s:15 }),
          rw(["[首选]","瑞士 2-1 哥伦比亚","1-0","~28%","恩博洛31'传中头球 → 迪亚斯58'突破远射扳平 → 曼扎姆比74'禁区混战制胜. 瑞士中场+恩博洛更强"], { ws:[1200,1800,800,1000,9000], bg:LG, s:13 }),
          rw(["备选1","1-1(加时→瑞士点球)","0-0","~22%","桑切斯61'哈梅斯角球头球 → 恩博洛78'头球扳平. 加时0-0→点球科贝尔占优"], { ws:[1200,1800,800,1000,9000], s:13 }),
          rw(["备选2","瑞士 2-0 哥伦比亚","1-0","~15%","恩博洛23'+曼扎姆比55'. COL攻击低效暴露——Diaz被Akanji限制"], { ws:[1200,1800,800,1000,9000], bg:GY, s:13 }),
          rw(["[铁律15]","瑞士 1-0 哥伦比亚","0-0","~13%","恩博洛42'角球头球制胜. 淘汰赛最常见比分(历史约27%)"], { ws:[1200,1800,800,1000,9000], s:13 }),
          rw(["[冷门]","哥伦比亚 2-1 瑞士","0-1","~12%","迪亚斯32'突破 → 苏亚雷斯67' → 恩博洛82'追回. 市场方向. Diaz爆点制胜"], { ws:[1200,1800,800,1000,9000], bg:GY, c:R, s:13 }),
        ],
      }),

      pp([], { a: 20 }),
      pp([tx("数据源与参考文献", { s: 18, b: true })], { b: 100 }),
      pp([tx("FIFA官方名单: 阿根廷(Al Jazeera) + 瑞士(FIFA.com) + 埃及(KingFut) + 哥伦比亚(beIN SPORTS) | 盘口: OddsShark / DraftKings / Kalshi / VSiN / football-predictions.ai / Racing Post | 身价: Transfermarkt | 积分榜: FOX Sports / Wikipedia | 阵容: RotoWire / Covers | 战术: SI.com | 战报: Sky Sports / BBC | 项目文件: 7月4日_3场预测.md + 7月4日_三场复盘.md + 7月4日_澳大利亚vs埃及_复盘.md | memory/: v20教训x5 | CLAUDE.md v20", { s: 13, c: "95A5A6" })], { a: 0 }),
      pp([tx("生成: 2026年7月8日 北京时间  |  v20 框架  |  通过 docx skill (docx-js) 生成  |  [v7] 盘口换行修复", { s: 13, c: "95A5A6" })]),
    ],
  }],
});

Packer.toBuffer(doc).then(buf => {
  fs.writeFileSync("E:/ai/世界杯/2026年7月8日_两场预测_v7.docx", buf);
  console.log("Saved: 2026年7月8日_两场预测_v7.docx (" + (buf.length / 1024).toFixed(0) + " KB)");
});

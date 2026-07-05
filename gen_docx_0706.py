# -*- coding: utf-8 -*-
"""Generate 2026-07-06 predictions DOCX — Brazil vs Norway + Mexico vs England."""

from docx import Document
from docx.shared import Inches, Pt, Cm, RGBColor, Emu
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.section import WD_ORIENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
import os

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "2026年7月6日_两场预测_v2.docx")

doc = Document()

# ── Colours ──
NAVY   = RGBColor(0x1A, 0x2E, 0x3D)
WHITE   = RGBColor(0xFF, 0xFF, 0xFF)
ALT_ROW = RGBColor(0xF5, 0xF7, 0xFA)
PREF_ROW= RGBColor(0xE8, 0xF5, 0xE9)
BORDER  = RGBColor(0xD0, 0xD5, 0xDD)
RED_T   = RGBColor(0xC0, 0x39, 0x2B)
DARK    = RGBColor(0x1A, 0x1A, 0x2E)
META    = RGBColor(0x7F, 0x8C, 0x8D)
META_L  = RGBColor(0x95, 0xA5, 0xA6)
BLUE_T  = RGBColor(0x2E, 0x75, 0xB6)
ORANGE  = RGBColor(0xE6, 0x7E, 0x22)
GREEN_T = RGBColor(0x27, 0xAE, 0x60)

FONT = '微软雅黑'

for sec in doc.sections:
    sec.orientation = WD_ORIENT.LANDSCAPE
    sec.page_width = Cm(29.7); sec.page_height = Cm(21.0)
    sec.left_margin = Cm(1.2); sec.right_margin = Cm(1.2)
    sec.top_margin = Cm(1.0); sec.bottom_margin = Cm(1.0)

CONTENT_W = 27.3

def sf(run, size=None, color=None, bold=False, font=FONT):
    run.font.name = font; run._element.rPr.rFonts.set(qn('w:eastAsia'), font)
    if size: run.font.size = Pt(size)
    if color: run.font.color.rgb = color
    run.bold = bold

def arun(p, text, **kw):
    r = p.add_run(text); sf(r, **kw)
    return r

def mp(before=0, after=0, align=None, border=False, bc='2E75B6'):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(before); p.paragraph_format.space_after = Pt(after)
    if align is not None: p.alignment = align
    if border:
        pPr = p._p.get_or_add_pPr(); pBdr = OxmlElement('w:pBdr')
        bot = OxmlElement('w:bottom')
        for a, v in [('w:val','single'),('w:sz','4'),('w:space','4'),('w:color',bc)]:
            bot.set(qn(a), v)
        pBdr.append(bot)
        for tag in ['w:spacing','w:ind','w:jc','w:rPr']:
            el = pPr.find(qn(tag))
            if el is not None: pPr.insert(list(pPr).index(el), pBdr); break
        else: pPr.append(pBdr)
    return p

def h1(t): return arun(mp(before=16,after=4,border=True,bc='C0392B'), t, size=16, bold=True, color=RED_T)
def h2(t): return arun(mp(before=12,after=3), t, size=12, bold=True, color=DARK)
def body(t, size=8.5, color=None):
    p = mp(before=1,after=2)
    arun(p, t, size=size, color=color or DARK)
    return p
def meta(t): return arun(mp(before=2,after=2), t, size=7, color=META)

def _shade(cell, clr):
    shading = OxmlElement('w:shd')
    shading.set(qn('w:fill'), str(clr)); shading.set(qn('w:val'), 'clear')
    cell._tc.get_or_add_tcPr().append(shading)

def _cb(cell, clr=BORDER, sz='4'):
    tcPr = cell._tc.get_or_add_tcPr()
    borders = OxmlElement('w:tcBorders')
    for edge in ['top','bottom','left','right']:
        b = OxmlElement(f'w:{edge}')
        for a, v in [('w:val','single'),('w:sz',sz),('w:color',str(clr)),('w:space','0')]:
            b.set(qn(a), v)
        borders.append(b)
    tcPr.append(borders)

def cpara(cell, text, size=8, bold=False, color=None, align=None):
    for pp in cell.paragraphs: pp.clear()
    p = cell.paragraphs[0]
    p.paragraph_format.space_before = Pt(1); p.paragraph_format.space_after = Pt(1)
    if align is not None: p.alignment = align
    r = p.add_run(str(text)); sf(r, size=size, bold=bold, color=color or DARK)
    return p

def make_table(headers, rows, widths, pref=None):
    tbl = doc.add_table(rows=1+len(rows), cols=len(headers))
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl.autofit = False
    for i, h in enumerate(headers):
        c = tbl.rows[0].cells[i]; _shade(c, NAVY)
        cpara(c, h, size=7.5, bold=True, color=WHITE, align=WD_ALIGN_PARAGRAPH.CENTER); _cb(c, clr=RGBColor(0x15,0x29,0x38))
    for ri, row in enumerate(rows):
        for ci, val in enumerate(row):
            c = tbl.rows[ri+1].cells[ci]
            if pref is not None and ri == pref: _shade(c, PREF_ROW)
            elif ri % 2 == 0: _shade(c, ALT_ROW)
            al = WD_ALIGN_PARAGRAPH.CENTER if ci < 2 else None
            cpara(c, val, size=7.5, align=al); _cb(c)
    for row in tbl.rows:
        for i, w in enumerate(widths):
            row.cells[i].width = Cm(w)
    return tbl

# ── header / footer ──
for sec in doc.sections:
    h = sec.header; h.is_linked_to_previous = False
    hp0 = h.paragraphs[0]; hp0.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    hp0.paragraph_format.space_after = Pt(2)
    r = hp0.add_run('2026 FIFA 世界杯 · 7月6日 两场预测报告')
    sf(r, size=7, color=META_L, font='Arial'); r._element.rPr.rFonts.set(qn('w:eastAsia'), FONT)
    pPr = hp0._p.get_or_add_pPr(); pBdr = OxmlElement('w:pBdr')
    bot = OxmlElement('w:bottom')
    for a, v in [('w:val','single'),('w:sz','4'),('w:space','4'),('w:color','95A5A6')]:
        bot.set(qn(a), v)
    pBdr.append(bot); pPr.insert(0, pBdr)

    f = sec.footer; f.is_linked_to_previous = False
    fp = f.paragraphs[0]; fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
    fp.paragraph_format.space_before = Pt(2)
    rp = fp.add_run(); sf(rp, size=7, color=META_L, font='Arial'); rp._element.rPr.rFonts.set(qn('w:eastAsia'), FONT)
    fc1 = OxmlElement('w:fldChar'); fc1.set(qn('w:fldCharType'), 'begin'); rp._r.append(fc1)
    it = OxmlElement('w:instrText'); it.set(qn('xml:space'), 'preserve'); it.text = ' PAGE '; rp._r.append(it)
    fc2 = OxmlElement('w:fldChar'); fc2.set(qn('w:fldCharType'), 'end'); rp._r.append(fc2)

# ═══════════ COVER ═══════════
p = mp(before=60, after=4, align=WD_ALIGN_PARAGRAPH.CENTER)
arun(p, '2026 FIFA 世界杯', size=26, bold=True, color=RED_T)
p = mp(before=2, after=6, align=WD_ALIGN_PARAGRAPH.CENTER)
arun(p, '淘汰赛十六强 · 7月6日 两场预测报告', size=15, bold=True, color=DARK)
p = mp(before=2, after=2, align=WD_ALIGN_PARAGRAPH.CENTER)
arun(p, '巴西 vs 挪威  |  墨西哥 vs 英格兰', size=12, bold=True, color=BLUE_T)
p = mp(before=16, after=0, align=WD_ALIGN_PARAGRAPH.CENTER)
arun(p, '预测时间: 2026年7月5日 10:00 北京时间', size=8.5, color=META)
p = mp(before=2, after=2, align=WD_ALIGN_PARAGRAPH.CENTER)
arun(p, '数据来源: FIFA API + ESPN API + Sports Mole + RotoWire + SI + Goal.com + Yahoo Sports', size=7, color=META_L)
p = mp(before=8, after=10, align=WD_ALIGN_PARAGRAPH.CENTER)
arun(p, '[注意] 官方首发尚未公布(ESPN roster空) — 阵容基于R32实际+媒体预测 — 赛前1小时拉roster更新', size=7, color=RED_T)

# ═══════════ SUMMARY ═══════════
h1('一、预测汇总')
meta('数据截至: 2026-07-05 10:00 CST | 淘汰赛十六强 | 所有时间均为北京时间 (UTC+8)')
make_table(
    ['#', '时间(BJT)', '阶段', '比赛', '身价比', '首选', '概率', '备选', '冷门风险'],
    [
        ['91', '04:00', '十六强', '巴西 vs 挪威', '1.51:1', '巴西 2-1', '~38%', '2-2(加时) / 巴西 3-1 / 1-1', '中高'],
        ['92', '08:00', '十六强', '墨西哥 vs 英格兰', '1:6.8', '英格兰 2-0', '~45%', '英格兰 1-0 / 2-1 / 1-1(加时)', '中'],
    ],
    widths=[0.5, 1.3, 1.0, 2.8, 1.1, 2.0, 1.0, 4.5, 1.2],
)

# ═══════════ BRACKET ═══════════
h1('二、淘汰赛路径')
make_table(
    ['日期(北京时间)', '阶段', '对阵', '场地'],
    [
        ['7/6 04:00', '十六强', '巴西 vs 挪威', 'MetLife球场, 东卢瑟福, 新泽西'],
        ['7/6 08:00', '十六强', '墨西哥 vs 英格兰', '阿兹特克球场, 墨西哥城(2240m)'],
        ['7/7 03:00', '十六强', '葡萄牙 vs 西班牙', 'AT&T球场, 阿灵顿'],
        ['7/7 08:00', '十六强', '美国 vs 比利时', '流明球场, 西雅图'],
        ['7/11', '四分之一决赛', 'BRA/NOR胜者 vs MEX/ENG胜者', '硬石球场, 迈阿密'],
        ['7/14', '半决赛', 'QF3胜者 vs 阿根廷/埃及/瑞士/哥伦比亚胜者', 'AT&T球场, 阿灵顿'],
    ],
    widths=[3.0, 1.5, 4.5, 4.3],
)

# ═══════════ MATCH 1: BRA vs NOR ═══════════
h1('三、比赛1: 巴西 vs 挪威')
meta('7月6日 04:00 北京时间 (7/5 16:00 ET) | MetLife球场, 新泽西 | FIFA #6 vs #9 | 历史: 挪威2胜2平 — 巴西从未赢过挪威')

h2('3.1 基本信息')
make_table(
    ['项目', '内容'],
    [['时间', '7月6日 04:00 北京时间 (UTC 7/5 20:00)'],
     ['场地', 'MetLife Stadium, 东卢瑟福, 新泽西, 美国'],
     ['FIFA排名', '巴西 #6 vs 挪威 #9'],
     ['阵容身价', '巴西 9.09亿欧元 vs 挪威 6.01亿欧元 (约1:1.51)'],
     ['历史交锋', '4次: 挪威2胜2平 — 含1998世界杯挪威2-1巴西 — 巴西从未赢过挪威'],
     ['巴西纪录', '自2002决赛后 — 淘汰赛对欧洲球队零胜(22年)'],
     ['晋级奖励', '四分之一决赛 vs 墨西哥/英格兰胜者 (7/11 迈阿密)']],
    widths=[2.5, 10.8],
)

h2('3.2 小组赛及淘汰赛回顾')
make_table(
    ['球队', '对手', '比分', '关键'],
    [['巴西', '摩洛哥 (G1)', '1-1', '大巴逼平 — 攻坚问题首现'],
     ['巴西', '海地 (G2)', '3-0', '稳定取胜'],
     ['巴西', '苏格兰 (G3)', '3-0', '小组头名出线'],
     ['巴西', '日本 (R32)', '2-1', '马丁内利制胜球 — 帕奎塔半场伤退'],
     ['挪威', '伊拉克 (G1)', '4-1', '攻击力爆表'],
     ['挪威', '塞内加尔 (G2)', '3-2', '哈兰德继续屠杀'],
     ['挪威', '法国 (G3)', '1-4', '面对顶级攻击力防线崩溃'],
     ['挪威', '科特迪瓦 (R32)', '2-1', '哈兰德制胜球']],
    widths=[1.2, 2.4, 2.2, 5.4],
)
p = mp(before=4, after=0); arun(p, '[关键] 挪威: 哈兰德5球/4场=最致命前锋。但防线7失球/4场=面对巴西攻击力将承受最大压力。巴西双核(帕奎塔+拉菲尼亚)缺阵=创造力大幅下降。', size=8, bold=True, color=RED_T)

h2('3.3 核心球员评分')
make_table(
    ['球队', '球员', '评分', '位置/俱乐部', '关键信息'],
    [['巴西', '阿利松', '8.0', '门将 / 利物浦', '世界前三门将 — 本届稳定'],
     ['巴西', '马尔基尼奥斯', '7.8', '中卫 / 巴黎圣日耳曼', '防线领袖 — 对日本多次关键解围'],
     ['巴西', '加布里埃尔', '7.5', '中卫 / 阿森纳', '英超经验 — 面对哈兰德——联赛对手重逢'],
     ['巴西', '布鲁诺·吉马良斯', '7.8', '中场 / 纽卡斯尔', '中场发动机 — 身价€85M'],
     ['巴西', '加布里埃尔·马丁内利', '7.5 [关键]', '攻击中场 / 阿森纳', '对日本制胜球 — 顶替受伤帕奎塔首发'],
     ['巴西', '维尼修斯', '9.0 [MOTM候选]', '左边锋 / 皇家马德里', '4球+1助 — 身价€180M — 对挪威右路佩德森降维打击'],
     ['巴西', '马特乌斯·库尼亚', '7.5', '中锋 / 狼队', '支点 — 本届进球稳定'],
     ['巴西缺阵', '卢卡斯·帕奎塔', '—', '中场 / 西汉姆', '[缺席] 大腿二级拉伤 — 缺3周'],
     ['巴西缺阵', '拉菲尼亚', '—', '右边锋 / 巴塞罗那', '[缺席] 腿筋'],
     ['巴西', '内马尔', '6.5 [注意]', '前锋 / —', '仅14分钟出场 — 状态未知 — 超级替补或零影响'],
     ['挪威', '厄德高 [C]', '8.5', '攻击中场 / 阿森纳', '创造力核心 — 队长'],
     ['挪威', '哈兰德', '9.5 [MOTM]', '中锋 / 曼城', '5球/3场 — 世界最佳中锋 — 仅需一次机会'],
     ['挪威', '桑德尔·贝格', '7.5', '中场 / —', '中场屏障 — 身体对抗'],
     ['挪威', '安东尼奥·努萨', '7.5', '左边锋 / —', '速度+盘带 — 对达尼洛的考验'],
     ['挪威', '索尔洛特', '7.5', '右边锋 / 马德里竞技', '右路支点'],
     ['挪威弱点', '佩德森', '6.5', '右后卫', '[弱点] 面对维尼修斯——本届最大错位'],
     ['挪威', '尼兰', '6.8', '门将 / 塞维利亚', '本届7失球']],
    widths=[1.2, 3.2, 1.6, 2.5, 4.8],
)

h2('3.4 因素导向')
make_table(
    ['因素', '有利', '理由'],
    [['哈兰德状态: 5球/3场', '挪威 ★★★', '仅需一次机会 — 加布里埃尔+马尔基尼奥斯有英超经验但未曾面对此状态的哈兰德'],
     ['巴西伤病: 帕奎塔+拉菲尼亚缺阵', '挪威 ★★★', '失去两大中场创造力来源 — 马丁内利被迫打更深 — 攻击维度从4降为2'],
     ['历史交锋: 挪威2胜2平', '挪威 ★★', '巴西从未赢过挪威 — 含1998世界杯2-1 — 心理枷锁'],
     ['维尼修斯 vs 佩德森: €180M vs ~€8M', '巴西 ★★★', '最大错位 — 若有空间维尼修斯可单兵解决比赛'],
     ['巴西中场实力: 吉马良斯+卡塞米罗', '巴西 ★★', '若卡塞米罗健康 — 中场控制力远超挪威 — 可限制厄德高触球'],
     ['挪威防线: 7失球/4场', '巴西 ★★', '对法国1-4暴露 — 从未面对巴西级别攻击力'],
     ['内马尔仅14分钟: 替补席最强牌受限', '挪威 ★', '若需逆转缺少王牌替补'],
     ['巴西对欧洲淘汰赛22年零胜', '挪威 ★', '不容忽视的心理障碍'],
     ['身价比 1:1.51 (<3:1)', '均势', '任何结果都可能'],
     ['中立场地(新泽西)', '均势', '无地理优势']],
    widths=[5.0, 1.8, 6.5],
)

h2('3.5 强队分类')
make_table(
    ['球队', '总身价', '超巨(>=€80M)', '分型', '破大巴能力'],
    [['巴西', '€909M (T1)', '维尼修斯(€180M)+吉马良斯(€85M)', '超级巨星型', '强 — 但帕奎塔+拉菲尼亚缺阵后降至中等'],
     ['挪威', '€601M (T2)', '哈兰德(€200M)+厄德高(~€80M)', '超级巨星型', '强 — 哈兰德单兵+厄德高传球双人组合']],
    widths=[1.2, 1.8, 3.0, 1.8, 3.5],
)
p = mp(before=4, after=0); arun(p, '双方均为超级巨星型 — 罕见淘汰赛配置。区别: 巴西依赖维尼修斯单点爆破, 挪威依赖哈兰德+厄德高双人组合。巴西伤病后超巨数量相当(2 vs 2)。', size=8, bold=True, color=BLUE_T)

h2('3.6 比分预测')
make_table(
    ['首选', '概率', '半场', '逻辑'],
    [['巴西 2-1 挪威', '~38%', '1-0', '维尼修斯28\'先破 — 哈兰德62\'扳平 — 库尼亚76\'锁定'],
     ['2-2 (挪威加时/点球)', '~18%', '1-1', '维尼修斯15\'/哈兰德38\'/努萨55\'/马丁内利78\' — 加时挪威替补弱'],
     ['巴西 3-1 挪威', '~17%', '2-0', '维尼修斯12\'52\'+库尼亚33\' — 哈兰德81\'(点)'],
     ['挪威 2-1 巴西', '~15%', '1-1', '哈兰德24\'/马丁内利41\'/索尔洛特83\' — 1998重演'],
     ['1-1 (巴西点球/加时)', '~12%', '—', '双方谨慎 — 巴西替补深度优势']],
    widths=[2.8, 1.0, 0.8, 7.7],
    pref=0,
)
p = mp(before=4, after=0); arun(p, '冷门风险: 中高 | 平局概率约30% | 挪威赢约15% | 哈兰德状态+巴西伤病+历史=罕见的高冷门潜力', size=8, bold=True, color=RED_T)

h2('3.7 伤停与定位球')
make_table(
    ['球队', '球员', '状态', '影响'],
    [['巴西', '拉菲尼亚 (右边锋)', '[缺席] 腿筋', '重大 — 右路攻击力缺失'],
     ['巴西', '卢卡斯·帕奎塔 (中场)', '[缺席] 大腿二级拉伤', '重大 — 创造力核心缺失 — 缺3周'],
     ['巴西', '卡塞米罗 (后腰)', '[疑] 肌肉问题', '若缺阵→法比尼奥顶替 — 防守硬度下降'],
     ['挪威', '尤利安·吕尔松 (右后卫)', '[疑] 大腿', '佩德森替代表现良好 — 但面对维尼修斯']],
    widths=[1.2, 3.5, 2.5, 5.1],
)
p = mp(before=2, after=0); arun(p, '定位球: 巴西略优(加布里埃尔+马尔基尼奥斯双中卫头球) — 挪威定位球防守7失球是大问题', size=8, bold=True)

h2('3.8 冷门路径')
body('挪威赢需同时: (1)哈兰德上半场厄德高直塞先破门 (2)卡塞米罗缺阵或状态差→吉马良斯单后腰被打穿 (3)佩德森奇迹限制维尼修斯 (4)索尔洛特/努萨反击第二球 (5)延续巴西对欧洲淘汰赛22年不胜', size=8)
body('最大不确定性: 巴西双核伤缺后创造力还剩多少? 若维尼修斯被双人包夹, 巴西是否有第二进攻方案?', size=8, color=RED_T)

# ═══════════ MATCH 2: MEX vs ENG ═══════════
h1('四、比赛2: 墨西哥 vs 英格兰')
meta('7月6日 08:00 北京时间 (7/5 19:00 CT) | 阿兹特克球场, 墨西哥城(2240m) | FIFA #15 vs #4 | 正式比赛: 英格兰6胜2负')

h2('4.1 基本信息')
make_table(
    ['项目', '内容'],
    [['时间', '7月6日 08:00 北京时间 (7/5 19:00 当地时间)'],
     ['场地', '阿兹特克球场 (Estadio Azteca), 墨西哥城 — 海拔2,240米'],
     ['FIFA排名', '墨西哥 #15 vs 英格兰 #4'],
     ['阵容身价', '墨西哥 ~1.92亿欧元 vs 英格兰 13.10亿欧元 (约1:6.8)'],
     ['历史交锋(正式)', '英格兰6胜 墨西哥2胜'],
     ['墨西哥纪录', '4场零封(360+分钟) — 2013年以来主场正式比赛不败'],
     ['英格兰高原', '历史2-2-2在高原球场 — 从未在墨西哥城赢过'],
     ['晋级奖励', '四分之一决赛 vs 巴西/挪威胜者 (7/11 迈阿密)'],
     ['关键缺席', '英格兰: 里斯·詹姆斯+贾雷尔·匡萨(右后卫双双缺席)']],
    widths=[2.5, 10.8],
)

h2('4.2 小组赛及淘汰赛回顾')
make_table(
    ['球队', '对手', '比分', '关键'],
    [['墨西哥', '南非 (G1)', '2-0', '零封开门红'],
     ['墨西哥', '韩国 (G2)', '1-0', '零封稳守'],
     ['墨西哥', '捷克 (G3)', '3-0', '零封大胜 — 360分钟不失球'],
     ['墨西哥', '厄瓜多尔 (R32)', '2-0', '零封延续至4场 — 奎尼奥内斯3球领跑'],
     ['英格兰', '克罗地亚 (G1)', '4-2', '凯恩2球 — 开门红'],
     ['英格兰', '加纳 (G2)', '0-0', '第二场综合征 — 对大巴攻坚弱'],
     ['英格兰', '巴拿马 (G3)', '2-0', '卡塔尔稳胜'],
     ['英格兰', '刚果民主共和国 (R32)', '2-1', '凯恩双响逆转']],
    widths=[1.2, 2.4, 2.2, 5.4],
)
p = mp(before=4, after=0); arun(p, '[关键] 墨西哥: 4场零封=本届最佳防守之一 — 但对手(南非/韩国/捷克/厄瓜多尔)无一是顶级攻击力。英格兰: 凯恩4球+贝林厄姆超级巨星 — 对高原适应是最大变量。', size=8, bold=True, color=RED_T)

h2('4.3 核心球员评分')
make_table(
    ['球队', '球员', '评分', '位置/俱乐部', '关键信息'],
    [['墨西哥', '劳尔·兰赫尔', '8.2', '门将', '4场零封 — 本届最佳门将之一'],
     ['墨西哥', '约翰·巴斯克斯', '7.8 [关键]', '中卫', '盯防凯恩 — 本届最大考验'],
     ['墨西哥', '塞萨尔·蒙特斯', '7.5', '中卫', '防线领袖 — 防空核心'],
     ['墨西哥', '埃里克·利拉', '7.5', '防守中场', '屏障 — 对抗贝林厄姆+赖斯'],
     ['墨西哥', '吉尔伯托·莫拉', '7.5', '中场', '17岁神童 — 创造力爆点'],
     ['墨西哥', '胡利安·奎尼奥内斯', '8.0 [关键]', '左边锋 / —', '3球 — 对英格兰残破右路(斯彭斯首秀)'],
     ['墨西哥', '罗伯托·阿尔瓦拉多', '7.5', '右边锋', '3助攻'],
     ['英格兰', '乔丹·皮克福德', '7.5', '门将 / 埃弗顿', '稳定'],
     ['英格兰', '杰德·斯彭斯', '6.8 [弱点]', '右后卫 / 热刺', '顶替受伤詹姆斯+匡萨 — 淘汰赛首秀'],
     ['英格兰', '马克·格希', '7.5', '中卫 / 水晶宫', '防线组织者'],
     ['英格兰', '德克兰·赖斯', '8.0 [疑]', '后腰 / 阿森纳', '腿筋紧 — 若缺阵中场控制力大降'],
     ['英格兰', '裘德·贝林厄姆', '8.8 [关键]', '攻击中场 / 皇家马德里', '身价€130M>墨西哥全队 — 英格兰最强单点'],
     ['英格兰', '安东尼·戈登', '7.5', '左边锋 / 纽卡斯尔', '对刚果2助攻'],
     ['英格兰', '哈里·凯恩 [C]', '8.5 [关键]', '中锋 / 拜仁慕尼黑', '4球 — 对刚果双响 — 高原影响待验证'],
     ['英格兰', '诺尼·马杜埃克', '7.5', '右边锋 / 切尔西', '速度'],
     ['英格兰缺阵', '里斯·詹姆斯', '—', '右后卫 / 切尔西', '[缺席] 小组赛以来一直缺阵'],
     ['英格兰缺阵', '贾雷尔·匡萨', '—', '中卫/右后卫 / 利物浦', '[缺席] 对巴拿马脚踝伤']],
    widths=[1.2, 3.2, 1.6, 2.3, 5.0],
)

h2('4.4 因素导向')
make_table(
    ['因素', '有利', '理由'],
    [['高原主场(2240m): 球飞行+6%更远 — 60分钟后体能断崖', '墨西哥 ★★★', '英格兰仅4天适应 — 墨西哥球员在此出生/训练 — 最大战术武器'],
     ['墨西哥4场零封: 本届仅两支零失球球队之一', '墨西哥 ★★★', '防守组织世界级 — 但对手均非顶级(南非/韩国/捷克/厄瓜多尔)'],
     ['英格兰伤病: 詹姆斯+匡萨缺右后卫', '墨西哥 ★★', '斯彭斯淘汰赛首秀 — 奎尼奥内斯(3球)对残破右路'],
     ['凯恩状态: 4球 — 对刚果双响', '英格兰 ★★★', '无论高原如何 — 凯恩总能进球'],
     ['身价比 1:6.8 (3:1-10:1明显差距)', '英格兰 ★★★', '正常发挥英格兰显著占优 — 不做平局首选'],
     ['贝林厄姆(€130M): 身价超过墨西哥全队(€192M)', '英格兰 ★★', '单兵能力在任何防守中找到空间 — 超级巨星型核心'],
     ['英格兰高原历史: 2-2-2 — 从未在墨西哥城赢过', '墨西哥 ★', '高原难适应 — 但样本量小'],
     ['赖斯若缺阵: 腿筋紧', '墨西哥 ★★', '最关键的防守中场 — 若缺阵安德森无法填坑'],
     ['英格兰对大巴攻坚弱(G2加纳0-0)', '墨西哥 ★', '特质仍在 — 但淘汰赛不同于小组赛第二轮']],
    widths=[5.0, 1.8, 6.5],
)

h2('4.5 强队分类')
make_table(
    ['球队', '总身价', '超巨(>=€80M)', '分型', '破大巴能力'],
    [['墨西哥', '~€192M (T3)', '无 (最高金梅内斯€18M)', '非强队方 — 高原=额外球员', '弱 — 主要靠防守反击'],
     ['英格兰', '€1,310M (T0)', '贝林厄姆(€130M)+凯恩+赖斯+萨卡', '超级巨星型', '强 — 凯恩+贝林厄姆+戈登多点破局']],
    widths=[1.2, 1.8, 3.0, 2.3, 3.0],
)
p = mp(before=4, after=0); arun(p, '身价比1:6.8 — 属于3:1-10:1"明显差距"。规则: 英格兰不做平局首选。但高原因子是罕见的"场地等效因子"——部分抵消身价差。', size=8, bold=True, color=BLUE_T)

h2('4.6 比分预测')
make_table(
    ['首选', '概率', '半场', '逻辑'],
    [['英格兰 2-0 墨西哥', '~45%', '1-0', '高原上半场慢节奏 — 凯恩38\'(点)先破 — 贝林厄姆67\'锁定'],
     ['英格兰 1-0 墨西哥', '~22%', '0-0', '墨西哥大巴守住半场 — 凯恩72\'才破门 — 高原影响双方'],
     ['英格兰 2-1 墨西哥', '~15%', '0-1', '奎尼奥内斯22\'先破 — 凯恩58\'81\'逆转'],
     ['1-1 (墨西哥点球/加时)', '~12%', '0-0', '高原致英格兰体能崩 — 阿尔瓦拉多77\' — 萨卡90+3\'扳平 — 加时墨西哥'],
     ['墨西哥 1-0 英格兰', '~6%', '0-0', '奎尼奥内斯55\'反击 — 4场零封延续至5场 — 但概率极低']],
    widths=[2.8, 1.0, 0.8, 7.7],
    pref=0,
)
p = mp(before=4, after=0); arun(p, '冷门风险: 中 | 平局概率约12% | 墨西哥赢约6% | 高原是最大变量 — 但英格兰攻击力足以克服', size=8, bold=True, color=BLUE_T)

h2('4.7 伤停与定位球')
make_table(
    ['球队', '球员', '状态', '影响'],
    [['英格兰', '里斯·詹姆斯 (右后卫)', '[缺席]', '重大 — 右路防守被迫用斯彭斯(淘汰赛首秀)'],
     ['英格兰', '贾雷尔·匡萨 (中卫/右后卫)', '[缺席] 脚踝', '轮换深度受损'],
     ['英格兰', '德克兰·赖斯 (后腰)', '[疑] 腿筋紧', '若缺阵 — 中场防守从世界级降至中游'],
     ['英格兰', '布卡约·萨卡 (右边锋)', '[疑] 恢复中', '可能替补 — 超级替补选项'],
     ['墨西哥', '全队健康 无停赛', '[可]', '利好 — 完整阵容']],
    widths=[1.2, 3.5, 2.5, 5.1],
)
p = mp(before=2, after=0); arun(p, '定位球: 墨西哥略优(蒙特斯188cm头球+阿尔瓦拉多传中) — 英格兰对克罗地亚失2球暴露防守漏洞', size=8, bold=True)

h2('4.8 冷门路径')
body('墨西哥赢需同时: (1)高原让英格兰60分钟后体能崩溃→传控断崖下降 (2)大巴守住上半场(4场零封已验证) (3)奎尼奥内斯60-75分钟打爆斯彭斯(淘汰赛首秀) (4)凯恩高原表现低于预期(32岁/体能消耗大) (5)比赛拖入加时→高原影响指数级放大→墨西哥点球', size=8)
body('最大不确定性: 4场零封对手(南非/韩国/捷克/厄瓜多尔)无一是顶级攻击力。贝林厄姆+凯恩是墨西哥从未面对过的级别。', size=8, color=RED_T)

# ═══════════ RISK ═══════════
h1('五、风险提示')
make_table(
    ['#', '场景', '风险', '应用'],
    [['1', '双方首发未确认: ESPN roster返回0', '阵容基于R32实际+媒体预测 — 可能偏差', '赛前1小时拉roster对照更新'],
     ['2', '巴西伤病严重: 帕奎塔+拉菲尼亚缺阵', '巴西创造力从4维度降至2维度 — 哈兰德有机会', '关注卡塞米罗能否首发——决定中场控制权'],
     ['3', '墨西哥高原: 2240m——英格兰仅4天适应', '60分钟后体能断崖可能性 — 球飞行+6%', '观察英格兰上半场节奏——若慢热则高原影响更大'],
     ['4', '挪威从未输给巴西: 4次2胜2平', '心理因素可能影响巴西淘汰赛决策', '若巴西上半场不进球→焦虑可能累积'],
     ['5', '赖斯若缺阵: 英格兰中场控制力降级', '安德森无法替代赖斯防守覆盖', '关注赛前1小时英格兰首发——赖斯是大关键']],
    widths=[0.8, 3.5, 4.5, 4.5],
)

# ═══════════ FOOTER ═══════════
p = mp(before=18, after=0); arun(p, '数据来源: FIFA API + ESPN API + Sports Mole + RotoWire + SI + Goal.com + Yahoo Sports + Fox Sports Mexico + TUDN', size=7, color=META_L)
p = mp(before=2, after=0); arun(p, '分析框架: CLAUDE.md v17 + match_analysis_template.md v2.0 + historical_upset_patterns.md + memory/team-market-values.md', size=7, color=META_L)
p = mp(before=2, after=0); arun(p, '生成时间: 2026年7月5日 10:00 CST | 引擎: python-docx v6 (横向A4) | 首发: 均未公布 — 赛前1小时拉ESPN roster更新', size=7, color=META_L)

doc.save(OUT)
print(f'OK: {OUT} ({os.path.getsize(OUT):,} bytes)')

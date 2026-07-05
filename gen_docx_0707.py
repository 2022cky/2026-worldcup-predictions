# -*- coding: utf-8 -*-
"""Generate 2026-07-07 predictions DOCX — Portugal vs Spain + USA vs Belgium."""

from docx import Document
from docx.shared import Inches, Pt, Cm, RGBColor, Emu
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.section import WD_ORIENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
import os

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "2026年7月7日_两场预测.docx")

doc = Document()
NAVY=RGBColor(0x1A,0x2E,0x3D); WHITE=RGBColor(0xFF,0xFF,0xFF); ALT_ROW=RGBColor(0xF5,0xF7,0xFA)
PREF_ROW=RGBColor(0xE8,0xF5,0xE9); BORDER=RGBColor(0xD0,0xD5,0xDD); RED_T=RGBColor(0xC0,0x39,0x2B)
DARK=RGBColor(0x1A,0x1A,0x2E); META=RGBColor(0x7F,0x8C,0x8D); META_L=RGBColor(0x95,0xA5,0xA6)
BLUE_T=RGBColor(0x2E,0x75,0xB6); FONT='微软雅黑'

for sec in doc.sections:
    sec.orientation = WD_ORIENT.LANDSCAPE
    sec.page_width=Cm(29.7); sec.page_height=Cm(21.0)
    sec.left_margin=Cm(1.2); sec.right_margin=Cm(1.2); sec.top_margin=Cm(1.0); sec.bottom_margin=Cm(1.0)

def sf(run, size=None, color=None, bold=False, font=FONT):
    run.font.name=font; run._element.rPr.rFonts.set(qn('w:eastAsia'),font)
    if size: run.font.size=Pt(size)
    if color: run.font.color.rgb=color
    run.bold=bold

def arun(p,text,**kw):
    r=p.add_run(text); sf(r,**kw); return r

def mp(before=0,after=0,align=None,border=False,bc='2E75B6'):
    p=doc.add_paragraph()
    p.paragraph_format.space_before=Pt(before); p.paragraph_format.space_after=Pt(after)
    if align is not None: p.alignment=align
    if border:
        pPr=p._p.get_or_add_pPr(); pBdr=OxmlElement('w:pBdr')
        bot=OxmlElement('w:bottom')
        for a,v in [('w:val','single'),('w:sz','4'),('w:space','4'),('w:color',bc)]: bot.set(qn(a),v)
        pBdr.append(bot)
        for tag in ['w:spacing','w:ind','w:jc','w:rPr']:
            el=pPr.find(qn(tag))
            if el is not None: pPr.insert(list(pPr).index(el),pBdr); break
        else: pPr.append(pBdr)
    return p

def h1(t): return arun(mp(before=16,after=4,border=True,bc='C0392B'),t,size=16,bold=True,color=RED_T)
def h2(t): return arun(mp(before=12,after=3),t,size=12,bold=True,color=DARK)
def body(t,size=8.5,color=None):
    p=mp(before=1,after=2); arun(p,t,size=size,color=color or DARK); return p
def meta(t): return arun(mp(before=2,after=2),t,size=7,color=META)

def _shade(cell,clr):
    shading=OxmlElement('w:shd'); shading.set(qn('w:fill'),str(clr)); shading.set(qn('w:val'),'clear')
    cell._tc.get_or_add_tcPr().append(shading)

def _cb(cell,clr=BORDER,sz='4'):
    tcPr=cell._tc.get_or_add_tcPr(); borders=OxmlElement('w:tcBorders')
    for edge in ['top','bottom','left','right']:
        b=OxmlElement(f'w:{edge}')
        for a,v in [('w:val','single'),('w:sz',sz),('w:color',str(clr)),('w:space','0')]: b.set(qn(a),v)
        borders.append(b)
    tcPr.append(borders)

def cpara(cell,text,size=8,bold=False,color=None,align=None):
    for pp in cell.paragraphs: pp.clear()
    p=cell.paragraphs[0]
    p.paragraph_format.space_before=Pt(1); p.paragraph_format.space_after=Pt(1)
    if align is not None: p.alignment=align
    r=p.add_run(str(text)); sf(r,size=size,bold=bold,color=color or DARK); return p

def make_table(headers,rows,widths,pref=None):
    tbl=doc.add_table(rows=1+len(rows),cols=len(headers))
    tbl.alignment=WD_TABLE_ALIGNMENT.CENTER; tbl.autofit=False
    for i,h in enumerate(headers):
        c=tbl.rows[0].cells[i]; _shade(c,NAVY)
        cpara(c,h,size=7.5,bold=True,color=WHITE,align=WD_ALIGN_PARAGRAPH.CENTER)
        _cb(c,clr=RGBColor(0x15,0x29,0x38))
    for ri,row in enumerate(rows):
        for ci,val in enumerate(row):
            c=tbl.rows[ri+1].cells[ci]
            if pref is not None and ri==pref: _shade(c,PREF_ROW)
            elif ri%2==0: _shade(c,ALT_ROW)
            al=WD_ALIGN_PARAGRAPH.CENTER if ci<2 else None
            cpara(c,val,size=7.5,align=al); _cb(c)
    for row in tbl.rows:
        for i,w in enumerate(widths): row.cells[i].width=Cm(w)
    return tbl

# header/footer
for sec in doc.sections:
    h=sec.header; h.is_linked_to_previous=False
    hp0=h.paragraphs[0]; hp0.alignment=WD_ALIGN_PARAGRAPH.RIGHT; hp0.paragraph_format.space_after=Pt(2)
    r=hp0.add_run('2026 FIFA 世界杯 · 7月7日 两场预测报告')
    sf(r,size=7,color=META_L,font='Arial'); r._element.rPr.rFonts.set(qn('w:eastAsia'),FONT)
    pPr=hp0._p.get_or_add_pPr(); pBdr=OxmlElement('w:pBdr'); bot=OxmlElement('w:bottom')
    for a,v in [('w:val','single'),('w:sz','4'),('w:space','4'),('w:color','95A5A6')]: bot.set(qn(a),v)
    pBdr.append(bot); pPr.insert(0,pBdr)
    f=sec.footer; f.is_linked_to_previous=False
    fp=f.paragraphs[0]; fp.alignment=WD_ALIGN_PARAGRAPH.CENTER; fp.paragraph_format.space_before=Pt(2)
    rp=fp.add_run(); sf(rp,size=7,color=META_L,font='Arial'); rp._element.rPr.rFonts.set(qn('w:eastAsia'),FONT)
    fc1=OxmlElement('w:fldChar'); fc1.set(qn('w:fldCharType'),'begin'); rp._r.append(fc1)
    it=OxmlElement('w:instrText'); it.set(qn('xml:space'),'preserve'); it.text=' PAGE '; rp._r.append(it)
    fc2=OxmlElement('w:fldChar'); fc2.set(qn('w:fldCharType'),'end'); rp._r.append(fc2)

# COVER
p=mp(before=60,after=4,align=WD_ALIGN_PARAGRAPH.CENTER); arun(p,'2026 FIFA 世界杯',size=26,bold=True,color=RED_T)
p=mp(before=2,after=6,align=WD_ALIGN_PARAGRAPH.CENTER); arun(p,'淘汰赛十六强 · 7月7日 两场预测报告',size=15,bold=True,color=DARK)
p=mp(before=2,after=2,align=WD_ALIGN_PARAGRAPH.CENTER); arun(p,'葡萄牙 vs 西班牙  |  美国 vs 比利时',size=12,bold=True,color=BLUE_T)
p=mp(before=16,after=0,align=WD_ALIGN_PARAGRAPH.CENTER); arun(p,'预测时间: 2026年7月5日 08:00 北京时间',size=8.5,color=META)
p=mp(before=2,after=2,align=WD_ALIGN_PARAGRAPH.CENTER); arun(p,'数据来源: FIFA API + ESPN API + Sports Mole + Last Word On Football + Sky Sports + Yahoo Sports',size=7,color=META_L)
p=mp(before=8,after=10,align=WD_ALIGN_PARAGRAPH.CENTER); arun(p,'[注意] 官方首发尚未公布 — 阵容基于R32实际+媒体预测 — 赛前1小时拉ESPN roster更新',size=7,color=RED_T)

# SUMMARY
h1('一、预测汇总')
meta('数据截至: 2026-07-05 08:00 CST | 淘汰赛十六强 | 所有时间均为北京时间 (UTC+8)')
make_table(
    ['#','时间(BJT)','阶段','比赛','身价比','首选','概率','备选','冷门风险'],
    [['93','03:00','十六强','葡萄牙 vs 西班牙','1:1.32','西班牙 2-1','~38%','1-1(加时) / 西班牙 2-0 / 葡萄牙 2-1','中高'],
     ['94','08:00','十六强','美国 vs 比利时','1:1.54','美国 2-1','~40%','1-1(加时) / 美国 2-0 / 比利时 1-0','中']],
    widths=[0.5,1.3,1.0,2.8,1.1,2.0,1.0,4.2,1.2],
)

# BRACKET
h1('二、淘汰赛路径')
make_table(
    ['日期(北京时间)','阶段','对阵','场地'],
    [['7/6 04:00','十六强','巴西 vs 挪威','MetLife球场, 新泽西'],
     ['7/6 08:00','十六强','墨西哥 vs 英格兰','阿兹特克球场, 墨西哥城(2240m)'],
     ['7/7 03:00','十六强','葡萄牙 vs 西班牙','AT&T球场, 阿灵顿'],
     ['7/7 08:00','十六强','美国 vs 比利时','流明球场, 西雅图'],
     ['7/10','四分之一决赛','POR/ESP胜者 vs USA/BEL胜者','SoFi球场, 洛杉矶']],
    widths=[3.0,1.5,4.5,4.3],
)
p=mp(before=4,after=0); arun(p,'四分之一决赛路径: 葡萄牙/西班牙胜者 vs 美国/比利时胜者 → 半决赛 vs 巴拉圭/法国/加拿大/摩洛哥胜者 (7/14 阿灵顿)',size=8,bold=True,color=BLUE_T)

# MATCH 1: POR vs ESP
h1('三、比赛1: 葡萄牙 vs 西班牙')
meta('7月7日 03:00 北京时间 (7/6 14:00 ET) | AT&T球场, 阿灵顿 | FIFA #5 vs #2 | 历史: 西班牙18胜 葡萄牙7胜 16平')

h2('3.1 基本信息')
make_table(
    ['项目','内容'],
    [['时间','7月7日 03:00 北京时间'],
     ['场地','AT&T Stadium (Dallas Stadium), 阿灵顿, 美国'],
     ['FIFA排名','葡萄牙 #5 vs 西班牙 #2'],
     ['阵容身价','葡萄牙 9.57亿欧元 vs 西班牙 12.67亿欧元 (约1:1.32)'],
     ['历史交锋','41次: 葡萄牙7胜 西班牙18胜 16平 — 最近: 2025欧国联决赛葡萄牙点球胜'],
     ['世界杯交锋','2010 R16: 西班牙1-0 / 2018 小组赛: 3-3 (C罗帽子戏法)'],
     ['西班牙纪录','5场零封 / 519分钟不失球 — 世界杯历史纪录 (超越曾加1990)'],
     ['晋级奖励','四分之一决赛 vs 美国/比利时胜者 (7/10 洛杉矶)']],
    widths=[2.5,10.8],
)

h2('3.2 小组赛及淘汰赛回顾')
make_table(
    ['球队','对手','比分','关键'],
    [['葡萄牙','刚果民主共和国 (G1)','1-1','内维斯6\' — 非洲大巴逼平'],
     ['葡萄牙','乌兹别克斯坦 (G2)','5-0','进攻爆发'],
     ['葡萄牙','哥伦比亚 (G3)','0-0','暴露体系困境'],
     ['葡萄牙','克罗地亚 (R32)','2-1','C罗68\'(点)+拉莫斯90+4\' — VAR争议'],
     ['西班牙','佛得角 (G1)','0-0','大巴攻坚难题'],
     ['西班牙','沙特阿拉伯 (G2)','4-0','进攻全面开花'],
     ['西班牙','乌拉圭 (G3)','1-0','稳扎稳打'],
     ['西班牙','奥地利 (R32)','3-0','23射门/2.84xG — 奥亚萨瓦尔2球+波罗1球']],
    widths=[1.2,2.4,2.2,5.4],
)
p=mp(before=4,after=0); arun(p,'[关键] 西班牙: 5场零封=史上最佳防守。葡萄牙: 对克罗地亚逆转展现韧性但依赖VAR。小组赛均对大巴球队暴露攻坚问题。',size=8,bold=True,color=RED_T)

h2('3.3 核心球员评分')
make_table(
    ['球队','球员','评分','位置/俱乐部','关键信息'],
    [['葡萄牙','迪奥戈·科斯塔','7.0','门将 / 波尔图','对克罗地亚多次扑救'],
     ['葡萄牙','鲁本·迪亚斯','7.8','中卫 / 曼城','防线领袖 — 本届最佳CB之一'],
     ['葡萄牙','努诺·门德斯','7.5','左后卫 / 巴黎圣日耳曼','左路攻防俱佳'],
     ['葡萄牙','维蒂尼亚','7.8 [关键]','中场 / 巴黎圣日耳曼','本届葡萄牙最稳定球员'],
     ['葡萄牙','若昂·内维斯','7.5','中场 / 巴黎圣日耳曼','G1进球 — 21岁已是主力'],
     ['葡萄牙','布鲁诺·费尔南德斯','7.5','攻击中场 / 曼联','创造机会顶级 — 淘汰赛尚未直接破门'],
     ['葡萄牙','拉斐尔·莱昂','7.3','左边锋 / AC米兰','替补更危险 — 对克罗地亚助攻绝杀'],
     ['葡萄牙','C罗 [C]','7.0','中锋 / 利雅得胜利','处子淘汰赛进球(点) — 41岁体能60-70\''],
     ['葡萄牙','贡萨洛·拉莫斯','8.0 [超级替补]','中锋 / 巴黎圣日耳曼','场均37分钟1球/助'],
     ['西班牙','乌奈·西蒙','8.5 [MOTM]','门将 / 毕尔巴鄂竞技','519分钟不失球创历史纪录'],
     ['西班牙','保·库巴西','7.8','中卫 / 巴塞罗那','18岁 — 对抗奥地利高球全胜'],
     ['西班牙','马克·库库雷利亚','8.0','左后卫 / 切尔西','对奥地利2助攻'],
     ['西班牙','罗德里','8.5 [MOTM]','后腰 / 曼城','世界第一后腰'],
     ['西班牙','佩德里','7.8','中场 / 巴塞罗那','创造力核心'],
     ['西班牙','拉明·亚马尔','8.2 [关键]','右边锋 / 巴塞罗那','本届最火爆新星(€200M)'],
     ['西班牙','阿莱士·巴埃纳','7.8','左边锋 / 比利亚雷亚尔','对奥地利5次创造机会'],
     ['西班牙','米克尔·奥亚萨瓦尔','8.3 [关键]','中锋 / 皇家社会','近16场首发17球'],
     ['西班牙缺阵','尼科·威廉姆斯','—','左边锋 / 毕尔巴鄂竞技','[缺席] 内收肌']],
    widths=[1.2,3.2,1.6,2.5,4.8],
)

h2('3.4 因素导向')
make_table(
    ['因素','有利','理由'],
    [['西班牙防守: 5场零封 vs 葡萄牙4场3失球','西班牙 ★★★','历史级防线 vs 有漏洞防线'],
     ['西班牙进攻整体性: 奥亚萨瓦尔+亚马尔+巴埃纳+库库雷利亚','西班牙 ★★★','四维度攻击 — 葡萄牙右路坎塞洛防>攻'],
     ['威廉姆斯缺阵: 西班牙失去最快反击点','葡萄牙 ★★','努诺·门德斯可更专注锁亚马尔'],
     ['葡萄牙逆转能力: 对克罗地亚落后→逆转','葡萄牙 ★★','C罗+拉莫斯双重得分方式'],
     ['替补深度: 拉莫斯(超级替补)+B席+帕利尼亚','葡萄牙 ★★','拉莫斯场均37分钟1球/助 — 加时赛优势方'],
     ['C罗体能: 41岁仅60-70\'高强度','西班牙 ★','若70\'后仍胶着 — 葡萄牙中锋位置降级'],
     ['欧国联决赛心理: 葡萄牙点球胜','葡萄牙 ★','最近一次交手 — 但世界杯≠欧国联'],
     ['身价比 1:1.32 — 十六强最接近对决','均势','<3:1 = 任何结果都可能']],
    widths=[5.0,1.8,6.5],
)

h2('3.5 强队分类')
make_table(
    ['球队','总身价','超巨(>=€80M)','分型'],
    [['葡萄牙','€957M (T1)','B费(€85M)/莱昂(€90M)/迪亚斯(€80M)','超级巨星型'],
     ['西班牙','€1,267M (T0)','亚马尔(€200M)/罗德里(€130M)/佩德里(€80M)','超级巨星型']],
    widths=[1.5,2.0,4.0,3.0],
)
p=mp(before=4,after=0); arun(p,'双方均为超级巨星型 — 区别: 西班牙依赖体系+整体, 葡萄牙依赖个人灵光。若西班牙体系运转→大概率胜; 若C罗/莱昂/B费爆发→可翻盘。',size=8,bold=True,color=BLUE_T)

h2('3.6 比分预测')
make_table(
    ['首选','概率','半场','逻辑'],
    [['西班牙 2-1 葡萄牙','~38%','0-0','上半场试探(0-0) — 奥亚萨瓦尔58\'+亚马尔72\' — C罗82\'(点)追回'],
     ['1-1 (加时/点球)','~20%','0-1','莱昂34\' — 西班牙67\'追平 — 加时双方谨慎'],
     ['西班牙 2-0 葡萄牙','~17%','1-0','奥亚萨瓦尔41\'+佩德里78\' — 零封延续至6场'],
     ['葡萄牙 2-1 西班牙','~15%','0-1','亚马尔18\' — C罗55\'(点)+拉莫斯88\'绝杀'],
     ['1-1 (葡萄牙点球/加时)','~10%','—','双方谨慎 — 葡萄牙加时深度优势']],
    widths=[2.8,1.0,0.8,7.7],pref=0,
)
p=mp(before=4,after=0); arun(p,'冷门风险: 中高 | 平局概率约30% | 葡萄牙赢约25% | 十六强历史平局率32.5%',size=8,bold=True,color=RED_T)

h2('3.7 伤病与停赛')
make_table(
    ['球队','球员','状态','影响'],
    [['西班牙','尼科·威廉姆斯 (左边锋)','[缺席] 内收肌','重大 — 失去最快反击点'],
     ['西班牙','耶雷米·皮诺 (右边锋)','[缺席] 肩韧带','中等 — 右路深度受损'],
     ['西班牙','亚马尔/波罗/拉波尔特/奥尔莫','[可出战] 训练减量','负荷管理 — 预计全部首发'],
     ['葡萄牙','全队健康','[可]','利好 — 完整武器库']],
    widths=[1.2,3.5,2.5,5.1],
)

h2('3.8 冷门路径')
body('葡萄牙赢需同时: (1)C罗开场闪电进球(定位球/点球) (2)西班牙首次在本届落后→应变未知 (3)努诺·门德斯锁死亚马尔 (4)马丁内斯65\'上拉莫斯→反击锁定 (5)2018小组赛3-3式个人英雄主义',size=8)
body('最大不确定性: 西班牙5场零封从未测试过"先失球"场景',size=8,color=RED_T)

# MATCH 2: USA vs BEL
h1('四、比赛2: 美国 vs 比利时')
meta('7月7日 08:00 北京时间 (7/6 17:00 PT) | 流明球场, 西雅图 | FIFA #13 vs #4 | 历史: 比利时2-1美国 (2014 R16 AET)')

h2('4.1 基本信息')
make_table(
    ['项目','内容'],
    [['时间','7月7日 08:00 北京时间'],
     ['场地','流明球场 (Lumen Field), 西雅图, 美国'],
     ['FIFA排名','美国 #13 vs 比利时 #4'],
     ['阵容身价','美国 ~3.45亿欧元 vs 比利时 5.30亿欧元 (约1:1.54)'],
     ['历史交锋(世界杯)','2014 R16: 比利时 2-1 美国 (AET)'],
     ['最近交手','2026年3月友谊赛: 比利时 5-2 美国 — 但美国阵容大不同'],
     ['关键缺席','美国: 巴洛贡(3球/最佳射手)红牌停赛'],
     ['晋级奖励','四分之一决赛 vs 葡萄牙/西班牙胜者 (7/10 洛杉矶)']],
    widths=[2.5,10.8],
)

h2('4.2 小组赛及淘汰赛回顾')
make_table(
    ['球队','对手','比分','关键'],
    [['美国','巴拉圭 (G1)','4-1','攻击力爆表'],
     ['美国','澳大利亚 (G2)','2-0','提前出线'],
     ['美国','土耳其 (G3)','2-3','轮换阵容仍进2球'],
     ['美国','波黑 (R32)','2-0','巴洛贡45\'+蒂尔曼82\' — 10人扩大比分'],
     ['比利时','埃及 (G1)','1-1','勉强逼平'],
     ['比利时','伊朗 (G2)','0-0','对10人伊朗大巴0进球'],
     ['比利时','新西兰 (G3)','5-1','进攻爆发'],
     ['比利时','塞内加尔 (R32)','3-2 AET','0-2落后86\' → 卢卡库86\'+蒂勒曼斯89\'120+5\'(点) — 神级逆转']],
    widths=[1.2,2.4,2.2,5.4],
)
p=mp(before=4,after=0); arun(p,'[关键] 美国: 4场全部2+进球。比利时: 对塞内加尔86分钟前0射正 — 依赖个人英雄逆转 — 防线速度是致命弱点。',size=8,bold=True,color=RED_T)

h2('4.3 核心球员评分')
make_table(
    ['球队','球员','评分','位置/俱乐部','关键信息'],
    [['美国','马特·弗里兹','7.5','门将 / 纽约城','对波黑2次关键扑救'],
     ['美国','安东尼·罗宾逊','8.0 [关键]','左后卫 / 富勒姆','本届最佳左后卫之一'],
     ['美国','泰勒·亚当斯','7.8 [关键]','后腰 / 伯恩茅斯','锁死德布劳内的关键'],
     ['美国','韦斯顿·麦肯尼','7.5','前腰 / 尤文图斯','对抗+跑动覆盖巨大'],
     ['美国','马利克·蒂尔曼','7.8 [MOTM]','中场 / 埃因霍温','对波黑1球1助 — 任意球破门'],
     ['美国','克里斯蒂安·普利西奇','7.5 [关键]','左边锋 / AC米兰','队长 — 巴洛贡缺阵后攻击核心'],
     ['美国','里卡多·佩皮','6.5 [注意]','中锋 / PSV','13球/41场国队 — 本届0球 — 取代巴洛贡'],
     ['美国缺阵','福拉林·巴洛贡','—','中锋 / 摩纳哥','[停赛] 3球最佳射手'],
     ['比利时','蒂博·库尔图瓦','7.5','门将 / 皇家马德里','世界级 — 但对塞内加尔失2球'],
     ['比利时','尤里·蒂勒曼斯 [C]','8.5 [MOTM]','中场 / 阿斯顿维拉','89\'扳平+120+5\'点球 — 本届最关键球员'],
     ['比利时','凯文·德布劳内','7.2 [注意]','攻击中场 / 那不勒斯','35岁/0助攻/未踢满90\'/R32被56\'换下'],
     ['比利时','莱安德罗·特罗萨尔','7.5 [关键]','左边锋 / 阿森纳','2球1助 — 主要攻击威胁'],
     ['比利时','热雷米·多库','7.0','右边锋 / 曼城','0球0助/R32被56\'换下'],
     ['比利时','罗梅卢·卢卡库','7.5 [超级替补]','中锋 / 罗马','86\'救命进球 — 仅适合30分钟冲刺'],
     ['比利时弱点','布兰登·梅赫勒','6.5 [弱点]','中卫 / 布鲁日','对塞内加尔被打穿 — 速度不足']],
    widths=[1.2,3.2,1.6,2.3,5.0],
)

h2('4.4 因素导向')
make_table(
    ['因素','有利','理由'],
    [['巴洛贡停赛: 3球最佳射手缺阵','比利时 ★★★','美国失去战术支点+最佳终结者'],
     ['美国主场: 西雅图Lumen Field — 3300万人看R32','美国 ★★★','东道主主场优势 — 波切蒂诺"26人团队"信念'],
     ['比利时体能: R32打120分钟+仅休4天','美国 ★★★','德布劳内/库尔图瓦35岁恢复更慢'],
     ['美国攻击稳定性: 4场全部2+进球','美国 ★★','蒂尔曼/普利西奇/麦肯尼多点开花'],
     ['比利时逆转基因: 86\'起死回生','比利时 ★★','不能被提前杀死'],
     ['比利时防线速度: 梅赫勒被打穿','美国 ★★','普利西奇+德斯特反击速度可能致命'],
     ['德布劳内状态: 35岁/0助攻/无90分钟体能','美国 ★★','亚当斯可针对性锁死 — 完美验证体系型弱点'],
     ['身价比 1:1.54 (<3:1接近)','中立','任何结果都可能']],
    widths=[5.0,1.8,6.5],
)

h2('4.5 强队分类')
make_table(
    ['球队','总身价','超巨(>=€80M)','分型'],
    [['美国','~€345M (T2)','无','非强队方 — 主场优势拉至均势'],
     ['比利时','€530M (T2)','仅德布劳内(€55M—未达阈值)','体系型 — 对塞内加尔86分钟0射正验证']],
    widths=[1.5,2.0,4.0,3.0],
)
p=mp(before=4,after=0); arun(p,'比利时=体系型。一旦亚当斯锁死德布劳内→比利时创造力归零。对塞内加尔86分钟0射正完美验证。',size=8,bold=True,color=RED_T)

h2('4.6 比分预测')
make_table(
    ['首选','概率','半场','逻辑'],
    [['美国 2-1 比利时','~40%','1-0','普利西奇32\'+蒂尔曼67\' — 卢卡库78\'替补追回'],
     ['1-1 (加时/点球)','~22%','0-0','蒂勒曼斯85\' — 德斯特90+3\' — 加时双方体能崩'],
     ['美国 2-0 比利时','~18%','1-0','麦肯尼23\'+佩皮58\'首球 — 弗里兹零封'],
     ['比利时 1-0 美国','~12%','0-0','德布劳内找回60分钟巅峰直塞多库'],
     ['比利时 3-1 美国','~8%','0-2','德布劳内41\'82\'+多库55\' — 概率最低']],
    widths=[2.8,1.0,0.8,7.7],pref=0,
)
p=mp(before=4,after=0); arun(p,'冷门风险: 中 | 平局概率约22% | 比利时赢约20% | 美国主场+体能+攻击稳定性 > 比利时个人能力。但比利时不能被提前杀死。',size=8,bold=True,color=BLUE_T)

h2('4.7 伤病与停赛')
make_table(
    ['球队','球员','状态','影响'],
    [['美国','福拉林·巴洛贡 (中锋)','[停赛] 红牌1场','重大 — 3球/战术支点缺失'],
     ['美国','马克·麦肯齐 (中卫)','[疑] 脚伤','轻微'],
     ['比利时','泽诺·德巴斯特 (中卫)','[疑]','防线轮换受损']],
    widths=[1.2,3.5,2.5,5.1],
)

h2('4.8 冷门路径')
body('比利时赢需同时: (1)德布劳内找回巅峰(哪怕60分钟) (2)佩皮无法替代巴洛贡 (3)库尔图瓦世界级扑救 (4)比利时逆转基因80分钟后显现',size=8)
body('最大不确定性: 巴洛贡缺阵冲击多大? 佩皮风格不同(终结者非逼抢支点)可能改变整个前场压迫结构。',size=8,color=RED_T)

# RISK
h1('五、风险提示')
make_table(
    ['#','场景','风险','应用'],
    [['1','首发未确认: ESPN roster返回0','阵容基于R32+媒体预测','赛前1小时拉roster更新'],
     ['2','西班牙从未落后过: 5场零封=双刃剑','若葡萄牙先破门→西班牙应变未知','西班牙先失球时观察调整'],
     ['3','巴洛贡缺阵: 美国火力不确定','佩皮(0球) vs 赖特(1分钟)','若佩皮上半场无威胁→波切蒂诺会早换'],
     ['4','德布劳内状态: R32被换后球队逆转','加西亚敢再次换下德布劳内?','比利时落后时观察换人时机'],
     ['5','十六强平局率32.5%','两场均有可能加时/点球','备选方案均已包含加时路径']],
    widths=[0.8,3.5,4.5,4.5],
)

# FOOTER
p=mp(before=18,after=0); arun(p,'数据来源: FIFA API + ESPN API + Sports Mole + Last Word On Football + Sky Sports + Yahoo Sports + Goal.com',size=7,color=META_L)
p=mp(before=2,after=0); arun(p,'分析框架: CLAUDE.md v17 + match_analysis_template.md + historical_upset_patterns.md + memory/team-market-values.md',size=7,color=META_L)
p=mp(before=2,after=0); arun(p,'生成时间: 2026年7月5日 CST | 引擎: python-docx v6 (横向A4) | 首发: 均未公布 — 赛前1小时更新',size=7,color=META_L)

doc.save(OUT)
print(f'OK: {OUT} ({os.path.getsize(OUT):,} bytes)')

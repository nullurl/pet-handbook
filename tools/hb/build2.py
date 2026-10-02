# -*- coding: utf-8 -*-
"""重建两份手册（合并来源口径 + 来源入附录 + 角标 + 外链图片仓库版）。

用法：
    python build2.py            # 内联图版（单文件 HTML）+ 外链图版（GitHub 版）
    python build2.py report     # 只打印转换后的标题，用于人工复核
"""

import os
import re
import sys
import csv
import shutil
from urllib.parse import quote

REPO_URL = 'https://github.com/nullurl/pet-handbook'

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import gen                 # noqa: E402
import common              # noqa: E402
import cat as MOD_CAT      # noqa: E402
import dog as MOD_DOG      # noqa: E402
import provenance as PV    # noqa: E402
import neutralize as NZ    # noqa: E402

# 开发布局：<项目>/hb/*.py           → 产物 <项目>/手册、<项目>/github
# 仓库布局：<repo>/tools/hb/*.py     → 产物 <repo>/docs/单文件离线版、<repo>/docs
_REPO_LAYOUT = os.path.isdir(os.path.join(HERE, '..', '..', 'docs', 'assets'))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..')) if _REPO_LAYOUT \
    else os.path.abspath(os.path.join(HERE, '..'))
OUT_SINGLE = os.environ.get('HB_SINGLE', os.path.join(ROOT, 'docs', '单文件离线版')
                            if _REPO_LAYOUT else os.path.join(ROOT, '手册'))
OUT_REPO = os.environ.get('HB_REPO', ROOT if _REPO_LAYOUT else os.path.join(ROOT, 'github'))

gen.CITE_TERMS = PV.cite_terms()

# ── 需要整块删除的来源导语 ─────────────────────────────────────────────
DROP_NOTE_PREFIX = (
    '**以下为原书原文补录',
    '**本章新增原书口径',
    '**本节的由来',
    '**本章对标来源',
)

# ── 章末对照表所在的小节标题特征 ───────────────────────────────────────
DIFF_H4 = ('原书口径 vs 权威口径', '原书推荐 vs 本书补充', '犬 vs 猫', '犬猫逐项差异')

# ── 标题人工改写（中性化规则兜不住的） ─────────────────────────────────
H4_FIX = {
    # 猫篇
    '五、原书 30 问逐条（原文补录）': '五、30 问逐条速查',
    '五、原书原文补录（到家头 48 小时的正确顺序）': '五、头 48 小时的正确顺序',
    '四、原书《猫咪喂养之：猫粮》19 问（原文逐条还原）': '四、猫粮 19 问逐条详解',
    '四、原书《猫咪喂养之：生骨肉》12 问（原文逐条还原）': '四、生骨肉 12 问逐条详解',
    '五、原书配方表（原文数据）': '五、完整配方与用量',
    '三、原书《猫咪喂养之：零食》原文': '三、零食的取舍原则',
    '三、原书《猫咪喂养之：营养品》原文（只推荐三种）': '三、只推荐这三种营养品',
    '四、原书《猫咪健康之：绝育篇》原文': '四、绝育的时机与术前术后',
    '三、原书《猫咪健康之：驱虫篇》原文': '三、驱虫频率与选药',
    '四、原书《猫咪健康之：疫苗篇》原文': '四、疫苗程序与接种前后',
    '四、原书《家养猫咪的牙结石问题》原文（含核心立场）': '四、关于"到底要不要刷牙"',
    '六、原书《常见问题：呕吐、拉稀、挠伤》原文（含眼部问题）': '六、呕吐、拉稀、挠伤与眼部问题要点',
    '四、原书《铲屎官购物清单》原文': '四、七大类与八件必需品',
    '四、原书《橘南家长购物清单》原文': '四、只推荐 4 件',
    '三、原书《养猫进阶好物》原文': '三、非必需但能提升体验的好物',
    '五、原书《怎么给猫咪剪指甲》原文': '五、控猫之术全文',
    '三、原书《夏天要给猫咪开空调吗？》原文': '三、温度与猫咪状态对照',
    '五、原书《宠物托运的一点总结》原文': '五、四项费用与全流程',
    '四、原书《猫粮碗选购指南》原文': '四、八节要点',
    '五、原书《如何给猫咪拍出一张「人生照片」》原文': '五、拍出"人生照片"的关键',
    '四、原书《掉毛季来了，如何优雅地与猫毛共处？》原文': '四、与猫毛共处的具体做法',
    '四、原书《养猫家庭里，不能碰的美丽植物》原文': '四、完整植物清单',
    '四、原书《拓展阅读：行为学、病理学》书单': '四、值得读的六本',
    # 犬篇
    '四、原书对标：把《养猫手册》30 问逐条翻译成犬的答案': '四、30 问的犬版答案',
    '四、原书对标：犬与猫的七个根本差异': '四、犬与猫的七个根本差异',
    '五、原书对标：把猫的"头 48 小时"翻译给幼犬': '五、头 48 小时怎么做',
    '原书对标：抚摸、互动与训练的犬版': '五、抚摸、互动与训练',
    '四、原书《猫粮》19 问的犬版逐条翻译': '四、狗粮 19 问逐条详解',
    '四、原书《生骨肉》12 问的犬版翻译': '四、生骨肉 12 问逐条详解',
    '三、原书《零食》原则的犬版': '三、零食的取舍原则',
    '三、原书《营养品》的犬版（三种 + 犬特有的两种）': '三、三种通用补剂 + 犬特有的两种',
    '四、原书《绝育篇》的犬版（时机比猫复杂得多）': '四、术前术后的补充要点',
    '四、原书《驱虫篇》的犬版（⚠️ 心丝虫是核心议题）': '四、心丝虫：犬的核心议题 ⚠️',
    '四、原书《疫苗篇》的犬版（核心疫苗比猫多一针）': '四、犬核心疫苗比猫多一针',
    '四、原书《牙结石》的犬版（⚠️ 犬比猫更严重）': '四、犬的口腔问题比猫更严重 ⚠️',
    '六、原书《呕吐、拉稀、挠伤》的犬版（⚠️ 两个猫没有的致命急症）': '六、两个猫没有的致命急症 ⚠️',
    '四、原书（猫）清单的犬版对标': '四、装备清单里两件"猫没有"的',
    '四、原书（猫）家长清单的犬版对标': '四、清单里最容易漏的两项',
    '三、原书（猫）进阶好物的犬版对标': '三、值得添置的进阶装备',
    '五、原书（猫）剪指甲的犬版对标': '五、剪指甲与肛门腺的补充要点',
    '三、原书（猫）空调篇的犬版对标': '三、降温与中暑预防的补充要点',
    '五、原书（猫）托运篇的犬版对标': '五、托运的补充要点',
    '四、原书（猫）猫粮碗篇的犬版对标': '四、抬高食盆的风险 ⚠️',
    '五、原书（猫）拍猫篇的犬版对标': '五、给狗拍照的补充要点',
    '三、原书（猫）掉毛篇的犬版对标': '三、被毛管理的补充要点',
    '五、原书（猫）植物篇的犬版对标': '五、犬的毒物风险补充要点',
    '四、原书（猫）书单的犬版对标': '四、犬版书单的取舍',
    '五、犬的对应书单与免费资源（7 组）': '五、犬的对应书单与免费资源',
}

# ── 二级小标题人工改写 ─────────────────────────────────────────────────
SRC_FIX = {
    '生骨肉：制作流程与喂养方法（原书原文）': '生骨肉：制作流程与喂养方法',
}

# ── 对照表表头改写 ─────────────────────────────────────────────────────
HEADER_FIX = {
    'cat': {
        '原书口径': '手册口径', '权威口径': '权威口径', '权威口径 / 本书补充': '权威口径 / 补充',
        '怎么用': '差异说明与怎么用', '原书推荐': '手册推荐', '本书评价 / 补充': '补充评价',
    },
    'dog': {
        '维度': '维度', '猫（原书结论）': '猫的常见做法', '犬（本书结论）': '犬的做法',
        '原书口径（猫）': '猫的常见做法', '犬的修正': '犬的做法', '为什么': '为什么',
        '猫': '猫', '犬': '犬', '急症': '急症', '原书（猫）做法': '猫的常见做法',
        '犬的对应做法': '犬的做法', '差异关键点': '差异关键点',
        '原书推荐（猫）': '猫的推荐', '犬的对应书单': '犬的对应书单', '备注': '备注',
    },
}

# ── 附录 G 每条对照表的导语 ────────────────────────────────────────────
DIFF_LEAD = {
    'cat': '本手册口径与**权威来源**之间的差异，逐条列在下面；每条都说明了「为什么不一样」和「实际怎么做」。',
    'dog': '犬与猫在同一件事上的做法差异，逐条列在下面；⚠️ 标出的是**与猫相反、最容易照搬出错**的地方。',
}

IMG_RE = re.compile(r'\.(jpg|jpeg|png|gif|webp)$', re.I)


# ══════════════════════════════════════════════════════════════════════
def _deep(o):
    """递归中性化：图片文件名与 URL 原样保留。"""
    if isinstance(o, str):
        if IMG_RE.search(o) or o.startswith('http') or o.startswith('#'):
            return o
        return NZ.nz(o)
    if isinstance(o, list):
        return [_deep(x) for x in o]
    if isinstance(o, tuple):
        return tuple(_deep(x) for x in o)
    return o


def nz_block(b):
    """中性化一个块；同时把配图标签统一成「配图」。"""
    k = b[0]
    if k == 'fig':
        return ('fig', b[1], NZ.nz(b[2], title=True), '配图') + (tuple(b[4:]) if len(b) > 4 else ())
    if k == 'figs':
        return ('figs', [(it[0], NZ.nz(it[1], title=True), '配图') for it in b[1]])
    if k == 'src':
        items = []
        for it in b[2]:
            if it[0] == 'h6':
                items.append(('h6', NZ.nz(it[1], title=True, sub=True)))
            elif it[0] in ('ul', 'ol'):
                items.append((it[0], [_deep(x) for x in it[1]]))
            else:
                items.append(_deep(it))
        return ('src', NZ.nz(b[1], title=True, sub=True), items)
    parts = [k]
    for idx, x in enumerate(b[1:], 1):
        if k in ('h4', 'src', 'apph', 'apph5') and idx == 1 and isinstance(x, str):
            parts.append(NZ.nz(x, title=True, sub=(k == 'src')))
        else:
            parts.append(_deep(x))
    return tuple(parts)


def transform(mod, kind):
    """把一章章的块序列改造成「统一正文 + 来源入附录」。返回 (sections, diffs, nfig)。"""
    diffs = []
    nfig = 0
    for sec in mod.SECTIONS:
        for ch in sec['chapters']:
            B = list(ch['blocks'])
            nb = []
            prev = None
            pending = False       # 刚遇到小节标题，其后的第一个 src 标题视为重复
            i = 0
            while i < len(B):
                b = B[i]
                k = b[0]

                # 1) 丢掉来源导语
                if k == 'note' and str(b[1]).startswith(DROP_NOTE_PREFIX):
                    i += 1
                    continue

                # 2) 章末对照表 → 附录 G（该 h4 之后的内容整段搬走）
                if k == 'h4' and any(p in b[1] for p in DIFF_H4):
                    tail = [x for x in B[i + 1:]
                            if not (x[0] == 'note' and str(x[1]).startswith(DROP_NOTE_PREFIX))]
                    diffs.append({'no': ch['no'], 'title': ch['title'],
                                  'raw': b[1], 'blocks': tail})
                    break

                # 3) 对照表紧跟在小节标题后：连标题一起搬走
                if k == 'ftable':
                    sub = ''
                    if prev == 'h4' and nb:
                        hb = nb.pop()[1]
                        sub = H4_FIX.get(hb) or NZ.nz(hb, title=True)
                    diffs.append({'no': ch['no'], 'title': ch['title'],
                                  'sub': sub, 'blocks': [b]})
                    i += 1
                    prev = None
                    continue

                # 4) 「原书原文补录」包装标题：后面挂了多个 src 就丢掉它
                if k == 'h4' and '原书原文补录' in b[1]:
                    nsrc = 0
                    for x in B[i + 1:]:
                        if x[0] == 'note' and str(x[1]).startswith(DROP_NOTE_PREFIX):
                            continue
                        if x[0] == 'src':
                            nsrc += 1
                        else:
                            break
                    if nsrc > 1:
                        i += 1
                        prev = None
                        pending = False
                        continue

                # 5) src 块紧跟在小节标题后时，去掉它自己的重复标题
                if k == 'src':
                    if b[1] in SRC_FIX:
                        b = ('src', SRC_FIX[b[1]], b[2])
                    if pending:
                        b = ('src', '', b[2])
                        pending = False

                if k == 'h4':
                    if b[1] in H4_FIX:
                        b = ('h4', H4_FIX[b[1]])
                    pending = True

                if k == 'fig' or k == 'figs':
                    nfig += 1 if k == 'fig' else len(b[1])

                nb.append(b)
                prev = k
                i += 1

            if diffs and diffs[-1]['no'] == ch['no']:
                key = f'G{diffs[-1]["no"]}'
                nb.append(('xref', '本章的**对照与差异说明**已统一收进附录：', (f'附录G.{diffs[-1]["no"]}', f'appG-{diffs[-1]["no"]}')))
            ch['blocks'] = [nz_block(x) for x in nb]
    return diffs, nfig


# ══════════════════════════════════════════════════════════════════════
# 附录
# ══════════════════════════════════════════════════════════════════════
def appendix_diffs(kind, diffs):
    if not diffs:
        return []
    blocks = [('lead', '本附录把正文中所有**对照与差异说明**集中在一起，按章编号；'
                       '正文每章末尾都有指向这里的链接。')]
    for d in diffs:
        head = f'G.{d["no"]} · 第 {d["no"]} 章 {d["title"]}'
        if d.get('sub'):
            head += f'　{d["sub"]}'
        blocks.append(('apph', head, f'appG-{d["no"]}'))
        blocks.append(('lead', DIFF_LEAD[kind]))
        for b in d['blocks']:
            if b[0] == 'ftable':
                hd = [HEADER_FIX[kind].get(h, h) for h in b[1]]
                blocks.append(('ftable', hd, _deep(b[2])))
            else:
                blocks.append(nz_block(b))
    return blocks


def appendix_h(kind):
    return PV.appendix_refs(kind)


# ══════════════════════════════════════════════════════════════════════
# 封面
# ══════════════════════════════════════════════════════════════════════
def front_cat(nfig):
    return [
        ('h2', '关于这本手册'),
        ('p', '这本手册把 25 章内容写成**可以直接照着做**的条目：每一个数字、月龄、剂量，都能在附录里找到出处；'
              '凡是权威来源之间存在分歧的地方，都单独标出来，而不是揉成一句"看情况"。'),
        ('p', '全书分五个部分——**与猫共处、喂养、健康、购物清单、常见提问**，'
              '覆盖从「我是不是该养猫」到「猫半夜吐了要不要冲医院」。'),
        ('note', '**来源是怎么标**：正文不再分成"底本"和"补充"两轨，读下来就是一本完整的手册；'
                 '所有出处集中收进三个附录——**附录F** 逐章列出内容来源，'
                 '**附录G** 逐条列出与权威口径的差异说明，**附录H** 是完整的引用来源清单。'
                 '正文里凡出现 [n] 上标之处，点击即跳到附录H 对应条目。'),
        ('h2', '关于配图'),
        ('p', f'全书 **{nfig} 张配图**，分两类：一类来自内容底本公众号原文里的实拍与手绘插图，'
              '一类是本手册为无图章节补绘的示意图。两类图在版式上**不作区分**，统一以「配图」标注，'
              '图注里说明这张图想表达的那个判断。'),
        ('note', '**为什么会有两类图**：底本中有几篇（尤其购物清单类）通篇是电商商品截图，'
                 '直接放进手册会变成广告。因此原则是——原文有合适的实拍或插画就用原图，'
                 '只有商品截图的地方改用手绘示意。目的只有一个：让每一张图都对得起读者花的时间。'),
        ('h2', '使用前先看这三条'),
        ('danger', '**一、兽医面诊 > 指南共识 > 本手册。** 本手册不能替代诊断。文中给的剂量、月龄、频率都是'
                   '"人群层面的共识"，落到你家这只猫身上，请听主治兽医的。'),
        ('danger', '**二、急诊不等天亮。** 猫是"忍痛大师"，等它表现出明显痛苦时，往往已经病得不轻。'
                   '出现附录D 里列的任何一种情况，直接去医院。'),
        ('danger', '**三、别信偏方。** 人用药（尤其对乙酰氨基酚、布洛芬）、各种"网红神药"、'
                   '"纯天然精油"，对猫的伤害远大于好处。猫的肝脏代谢通路与人差异巨大。'),
        ('h2', '全书速览'),
        ('grid', [
            ['如果你刚接猫回家', '先读第 1、3 章，把家改造成"猫安全区"，再谈感情', '预约首次体检，带上免疫本'],
            ['如果你在纠结吃什么', '第 6 章定主食框架，第 7 章看生骨肉的风险，第 8、9 章管零食和营养品',
             '把钱花在主食上，别花在补剂上'],
            ['如果你怕它生病', '第 10–14 章是硬功夫：绝育、驱虫、疫苗、牙齿、日常症状', '重点背下附录D 的急诊红旗'],
            ['如果你只想抄清单', '直接跳第 15 章"铲屎官购物清单"', '避坑项都在表里标了出来'],
        ]),
    ]


def front_dog(nfig):
    return [
        ('h2', '关于这本手册'),
        ('p', '这本手册把犬的 25 个主题写成**可以直接照着做**的条目。犬的品种差异极大——'
              '体型能相差 60 倍，任何剂量与月龄都必须结合你家这只狗的具体情况。'),
        ('p', '全书分五个部分——**与狗共处、喂养、健康、购物清单、常见提问**，'
              '覆盖从选犬、行为训练、科学喂养，到急诊判断与日常照护。'),
        ('note', '**来源是怎么标**：正文不再分成"底本"和"补充"两轨，读下来就是一本完整的手册；'
                 '所有出处集中收进三个附录——**附录F** 逐章列出内容来源，'
                 '**附录G** 逐条列出犬与猫的做法差异（⚠️ 标出与猫相反的地方），'
                 '**附录H** 是完整的引用来源清单。正文里凡出现 [n] 上标之处，点击即跳到附录H 对应条目。'),
        ('h2', '关于配图'),
        ('p', f'全书 **{nfig} 张插图，全部为本手册原创绘制**（暖色扁平插画风）。理由很简单：'
              '市面上的宠物配图大多是猫的，直接搬来会误导。每一张图都对应本章要讲的那个关键判断，'
              '而不是泛泛的"可爱狗狗图"。'),
        ('h2', '犬与猫，最大的七个不同（先建立正确预期）'),
        ('table', ['维度', '猫', '犬'], [
            ['驯化史', '约 1 万年前自我驯化，独居猎手', '约 1.5 万年以上，群体协作狩猎，被真正驯化'],
            ['社交需求', '独居动物，社交容忍度有限', '**群居动物，社交需求强**，独处易分离焦虑'],
            ['活动需求', '短时爆发 + 高处观察', '**按品种差异极大**：边牧/pointer 需要的运动量是巴哥的十倍'],
            ['服从基础', '无（靠利益与安全感）', '**有（有等级与协作基础）**，可做系统训练'],
            ['口腔护理', '牙周病、牙吸收病变高发', '牙周病高发，但**咀嚼拖拽玩具能部分自洁**'],
            ['中暑风险', '较耐热但会张口呼吸预警', '**犬耐热差得多**，短头颅犬（巴哥、法斗、英斗）高危，'
             '犬主要靠喘气散热'],
            ['核心疫苗', '猫三联 + 狂犬', '犬瘟/细小/腺病毒/副流感 + 狂犬；**AAHA 2024 已将钩端螺旋体列为犬核心**'],
        ]),
        ('h2', '使用前先看这三条'),
        ('danger', '**一、兽医面诊 > 指南共识 > 本手册。** 本手册不能替代诊断。'
                   '犬的品种差异极大，任何剂量与月龄都必须结合你家这只狗的具体情况。'),
        ('danger', '**二、急诊不等天亮。** 犬的**胃扭转（GDV）、中暑、误食**都是分钟级的急症。'
                   '附录D 列了红旗信号，背下来。'),
        ('danger', '**三、别信偏方。** 人用药（尤其对乙酰氨基酚、布洛芬）、"网红驱虫法"、'
                   '大蒜驱虫、生鸡蛋"美毛"都是有害无益的。'),
        ('h2', '全书速览'),
        ('grid', [
            ['如果你刚接狗回家', '先读第 1、3 章，把家改成"幼犬安全区"，并抓紧 3–14 周龄社会化窗口',
             '预约首次体检，带上免疫本'],
            ['如果你在纠结吃什么', '第 6 章定主食框架，第 7 章看鲜食/生食的风险，第 8、9 章管零食与补剂',
             '把钱花在主食上'],
            ['如果你怕它生病', '第 10–14 章：绝育、驱虫、疫苗、牙齿、常见症状', '重点背下 GDV、中暑、误食的处置'],
            ['如果你只想抄清单', '直接跳第 15 章"新手狗家长购物清单"', '第 16 章是到家 30 天日程'],
        ]),
    ]


META_FIX = {
    'cat': dict(
        version='2026 增订版 · 25 章 + 8 附录 · 全文来源可追溯',
        subtitle='从「我是不是该养猫」到「猫半夜吐了要不要冲医院」。25 章覆盖与猫共处、喂养、健康、购物、'
                 '常见提问；所有出处集中收进附录F/G/H，正文以 [n] 上标逐条可追。',
        meta=['25 章 + 8 附录（知识库速查 / 宠物医院 / 毒物清单 / 急诊卡 / 勘误表 / 来源对照 / 差异说明 / 引用清单）',
              '引用来源：默沙东兽医手册、WSAVA 2024、AAHA 2024、ACVIM、CVMA 团标与指南、GB/T 与 NY/T 标准、ASPCA',
              '正文任何数字都可在附录H 找到出处；与权威口径不一致处，逐条列在附录G',
              '附录B：全国宠物医院 24h 急诊与价格参考',
              '权威数据已于 2026-10-01 逐条回查核对（见附录E）'],
    ),
    'dog': dict(
        version='2026 版 · 25 章 + 8 附录 · 全文来源可追溯',
        subtitle='与养猫手册同为五部分 25 章，为养狗场景重写。所有出处集中收进附录F/G/H，'
                 '正文以 [n] 上标逐条可追；⚠️ 标出犬与猫做法相反的关键处。',
        meta=['25 章 + 8 附录（知识库速查 / 宠物医院 / 毒物清单 / 急诊卡 / 勘误表 / 来源对照 / 差异说明 / 引用清单）',
              '引用来源：默沙东兽医手册、WSAVA 2024、AAHA 2024、ACVIM、CVMA 团标与指南、GB/T 与 NY/T 标准、ASPCA',
              '正文任何数字都可在附录H 找到出处；犬猫差异逐条列在附录G',
              '附录B：全国宠物医院 24h 急诊与价格参考',
              '权威数据已于 2026-10-01 逐条回查核对（见附录E）'],
    ),
}


def common_appendices(kind):
    intro = common.KB_INTRO + [
        ('refnote', '本附录只讲"怎么用"；每条依据的**完整出处与版本号**，统一列在 **附录H · 引用来源清单**，'
                    '正文中的 [n] 上标与之一一对应。'),
    ]
    return [
        {'id': 'apA', 'title': '附录A · 权威知识库速查（默沙东 / WSAVA / AAHA / CVMA / 国标）',
         'blocks': [nz_block(x) for x in intro + common.KB_REFS[2:]]},
        {'id': 'apB', 'title': '附录B · 全国宠物医院信息（24 小时急诊 · 价格 · 评价参考）',
         'blocks': [nz_block(x) for x in common.HOSP_INTRO + common.HOSP_STRUCTURE + common.HOSP_CHECKLIST]},
        {'id': 'apC', 'title': '附录C · 危险食物、毒物与植物清单（含中毒剂量）',
         'blocks': [nz_block(x) for x in common.TOX_TOXIC_FOOD + common.TOX_PLANTS + common.TOX_FIRST_AID]},
        {'id': 'apD', 'title': '附录D · 急诊速查卡（红旗信号 · 生命体征 · 出门清单）',
         'blocks': [nz_block(x) for x in common.EMERGENCY_CARD]},
        {'id': 'apE', 'title': '附录E · 核对与勘误表（2026-10-01 逐条回查）',
         'blocks': [nz_block(x) for x in common.VERIFY_INTRO + common.VERIFY_LOG + common.VERIFY_NEW]},
    ]


def build_one(mod, kind, out_path, img_mode, img_prefix, diffs, nfig):
    meta = dict(mod.META)
    meta.update(META_FIX[kind])
    front = front_cat(nfig) if kind == 'cat' else front_dog(nfig)

    # 仅 GitHub 版（图片外链）挂出外部入口：自包含的单文件版保持零依赖、零外链
    if img_mode == 'external':
        if kind == 'cat':
            meta['links'] = [
                ('另：养狗手册（2026 版）', 'dog.html'),
                ('下载单文件离线版（图片内联，可离线打开）',
                 '单文件离线版/' + quote('养猫手册-2026增订版.html'), ' download'),
                ('GitHub 仓库 · 勘误与反馈', REPO_URL),
            ]
        else:
            meta['links'] = [
                ('另：养猫手册（2026 增订版）', './'),
                ('下载单文件离线版（图片内联，可离线打开）',
                 '单文件离线版/' + quote('养狗手册-2026版.html'), ' download'),
                ('GitHub 仓库 · 勘误与反馈', REPO_URL),
            ]

    chapters = [(c['no'], c['title']) for s in mod.SECTIONS for c in s['chapters']]

    # 预渲染，收集每章实际命中哪些来源编号
    cited = {}
    for s in mod.SECTIONS:
        for c in s['chapters']:
            gen.render_blocks(c['blocks'])
            cited[c['no']] = set(gen._CITE_SEEN)

    apps = common_appendices(kind)
    apps.append({'id': 'apF', 'title': '附录F · 内容来源与出处对照',
                 'blocks': PV.appendix_sources(kind, chapters, cited)})
    apps.append({'id': 'apG', 'title': '附录G · 对照与差异说明',
                 'blocks': appendix_diffs(kind, diffs)})
    apps.append({'id': 'apH', 'title': '附录H · 引用来源清单（References）',
                 'blocks': appendix_h(kind)})

    gen.IMG_MODE = img_mode
    gen.IMG_PREFIX = img_prefix
    html = gen.build(meta, mod.SECTIONS, front, apps, os.path.basename(out_path))
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f'  {os.path.basename(out_path):34} {len(html)/1048576:6.2f} MB  '
          f'配图 {nfig}  差异表 {len(diffs)}  章 {len(chapters)}')
    return html


def build_repo_pages():
    """只生成 GitHub 版（图片外链）页面，供 mkrepo.py 在目录就绪后调用。"""
    prep = {k: transform(m, k) for m, k in ((MOD_CAT, 'cat'), (MOD_DOG, 'dog'))}
    build_one(MOD_CAT, 'cat', os.path.join(OUT_REPO, 'docs', 'index.html'),
              'external', 'assets', *prep['cat'])
    build_one(MOD_DOG, 'dog', os.path.join(OUT_REPO, 'docs', 'dog.html'),
              'external', 'assets', *prep['dog'])


def main():
    report = len(sys.argv) > 1 and sys.argv[1] == 'report'
    if report:
        for mod, kind in ((MOD_CAT, 'cat'), (MOD_DOG, 'dog')):
            diffs, nfig = transform(mod, kind)
            print('=' * 30, kind, f'（配图 {nfig}，差异表 {len(diffs)}）')
            for sec in mod.SECTIONS:
                for ch in sec['chapters']:
                    for b in ch['blocks']:
                        if b[0] in ('h4', 'src') and isinstance(b[1], str) and b[1]:
                            print(f'  ch{ch["no"]:>2} {b[0]:4} {b[1]}')
                    if ch['blocks'] and ch['blocks'][-1][0] == 'xref':
                        print(f'  ch{ch["no"]:>2} ---- 差异表 → 附录G.{ch["no"]}')
        return

    os.makedirs(OUT_SINGLE, exist_ok=True)
    # 管道只跑一次（transform 会就地改写 SECTIONS），两个版本共用结果
    prep = {}
    for mod, kind in ((MOD_CAT, 'cat'), (MOD_DOG, 'dog')):
        prep[kind] = transform(mod, kind)

    print('◇ 单文件版（图片内联）')
    build_one(MOD_CAT, 'cat', os.path.join(OUT_SINGLE, '养猫手册-2026增订版.html'),
              'inline', '', *prep['cat'])
    build_one(MOD_DOG, 'dog', os.path.join(OUT_SINGLE, '养狗手册-2026版.html'),
              'inline', '', *prep['dog'])

    print('◇ GitHub 版（图片外链）')
    build_one(MOD_CAT, 'cat', os.path.join(OUT_REPO, 'docs', 'index.html'),
              'external', 'assets', *prep['cat'])
    build_one(MOD_DOG, 'dog', os.path.join(OUT_REPO, 'docs', 'dog.html'),
              'external', 'assets', *prep['dog'])


if __name__ == '__main__':
    main()

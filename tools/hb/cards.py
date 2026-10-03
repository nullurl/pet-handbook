# -*- coding: utf-8 -*-
"""把手册里适合传播的内容做成自媒体图卡。

做法：从**转换后**的正文里按 (章号, 块序号) 取原样内容，
套统一版式渲染成 1080×1440 的 HTML，再由 cardshot.js 截成 PNG。
卡片里看到的每一句都是手册原文，不另写文案。

用法：
    python cards.py            # 生成卡片 HTML 到 /tmp/petcards，标签写入 PNG 输出目录
    node cardshot.js           # 截图到 手册/素材（再由 mkrepo.py 收进仓库）
"""

import io
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import gen          # noqa: E402
import build2       # noqa: E402
import cat as MOD_CAT   # noqa: E402
import dog as MOD_DOG   # noqa: E402

OUT = os.environ.get('HB_CARDS', '/tmp/petcards')
ROOT = build2.ROOT
PNG_DIR = os.environ.get('HB_PNG', os.path.join(ROOT, '手册', '素材'))

BOOK = {
    'cat': dict(name='养猫手册', ver='2026 增订版', accent='#b03a2e', accent2='#f6e4e0',
                slug='cat', hero=MOD_CAT.META.get('hero')),
    'dog': dict(name='养狗手册', ver='2026 版', accent='#1f5f8b', accent2='#e2edf5',
                slug='dog', hero=MOD_DOG.META.get('hero')),
}

# ── 选材：(章号, 块序号, 覆盖标题 or None) ──────────────────────────────
# 块序号对应 transform 之后的 blocks 下标；max_rows 只截断行数，不改文字。
MATERIALS = {
    'cat': [
        dict(id='cover', kind='cover',
             title='养猫手册', sub='从「我是不是该养猫」到「猫半夜吐了要不要冲医院」'),
        dict(id='qa', ch=1, bi=10, max_rows=6,
             title='新手最常问的问题，先看结论'),
        dict(id='body', ch=2, bi=2, max_rows=6,
             title='尾巴与耳朵：猫的情绪仪表盘'),
        dict(id='arrive', ch=3, bi=3,
             title='猫到家的第 1–14 天，每天做什么'),
        dict(id='worm', ch=11, bi=3,
             title='驱虫：多久一次，怎么选药'),
        dict(id='vaccine', ch=12, bi=3,
             title='猫的免疫程序（WSAVA 中文版）'),
        dict(id='vomit', ch=14, bi=1, max_rows=6,
             title='猫吐了：先分清要不要去医院'),
        dict(id='buyfirst', ch=15, bi=1, max_rows=8, cols=3,
             title='接猫前必买，缺一不可'),
        dict(id='plant', ch=24, bi=3,
             title='有猫家庭不能养的植物'),
        dict(id='teeth', ch=13, bi=4, max_rows=5,
             title='猫的牙出问题时，你先看到什么'),
        dict(id='after', ch=10, bi=5,
             title='绝育术后 48 小时，最关键'),
        dict(id='shed', ch=23, bi=1,
             title='正常掉毛，还是异常掉毛'),
    ],
    'dog': [
        dict(id='cover', kind='cover',
             title='养狗手册', sub='与养猫手册同为五部分 25 章，为养狗场景重写'),
        dict(id='qa', ch=1, bi=7, max_rows=6,
             title='新手最常问的问题，先看结论'),
        dict(id='body', ch=2, bi=3, max_rows=6,
             title='读懂狗的身体语言'),
        dict(id='vaccine', ch=12, bi=2, max_rows=7,
             title='犬的核心疫苗有哪些'),
        dict(id='heat', ch=14, bi=9,
             title='中暑：犬的夏季头号杀手'),
        dict(id='blacklist', ch=24, bi=4, max_rows=8,
             title='必须背下来的食物黑名单'),
        dict(id='worm', ch=11, bi=3,
             title='驱虫频率：幼犬和成年犬不一样'),
        dict(id='neuter', ch=10, bi=2, cols=3,
             title='不同体型的犬，绝育月龄差很多'),
        dict(id='cost', ch=15, bi=5,
             title='养一只狗，第一年要花多少'),
        dict(id='arrive', ch=16, bi=6,
             title='狗到家 30 天日程'),
        dict(id='cmd', ch=4, bi=5,
             title='必学的五个基础指令'),
        dict(id='vomit', ch=14, bi=1, max_rows=6,
             title='狗吐了：先分清要不要去医院'),
    ],
}

CARD_CSS = """
*{margin:0;padding:0;box-sizing:border-box}
html,body{width:1080px;height:1440px;overflow:hidden}
body{
  font-family:-apple-system,BlinkMacSystemFont,"PingFang SC","Hiragino Sans GB","Microsoft YaHei",sans-serif;
  background:#fffdfb; color:#1a1d21; -webkit-font-smoothing:antialiased;
}
.card{width:1080px;height:1440px;display:flex;flex-direction:column;position:relative;background:#fffdfb}
.bar{height:14px;background:var(--accent);flex:0 0 14px}
.wm{position:absolute;right:-90px;top:-70px;width:420px;height:420px;border-radius:50%;
    background:var(--accent2);opacity:.55;z-index:0}
.head{position:relative;z-index:1;padding:64px 78px 30px}
.kicker{display:flex;align-items:center;gap:14px;font-size:25px;color:var(--accent);
        letter-spacing:1px;font-weight:600}
.kicker .dot{width:11px;height:11px;border-radius:50%;background:var(--accent);flex:0 0 11px}
.kicker .ch{color:#8a929c;font-weight:400}
h1{font-size:66px;line-height:1.24;margin:22px 0 0;letter-spacing:.5px;font-weight:800}
h1.sm{font-size:52px}
.sub{margin-top:20px;font-size:28px;color:#5b636d;line-height:1.6}
.rule{margin:34px 78px 0;height:3px;background:var(--accent);opacity:.22;flex:0 0 3px}
.area{flex:1 1 auto;position:relative;z-index:1;padding:36px 78px 34px;overflow:hidden}
.fit{font-size:33px;line-height:1.62}
table{width:100%;border-collapse:separate;border-spacing:0}
th{font-size:.86em;color:#7a828c;font-weight:600;text-align:left;
   padding:0 .7em 14px;border-bottom:2px solid #e8e2dd;letter-spacing:.5px}
td{padding:.72em .7em;vertical-align:top;border-bottom:1px solid #f0eae5;font-size:1em;line-height:1.58}
tr:last-child td{border-bottom:0}
td.k{color:var(--accent);font-weight:700;white-space:nowrap}
td.k.wrap{white-space:normal}
tbody tr:nth-child(odd) td{background:#fdf8f5}
td.more{color:#98a0a8;font-style:normal;font-size:.86em;text-align:center}
ul,ol{list-style:none}
li{position:relative;padding-left:1.5em;margin-bottom:.72em;line-height:1.6}
li:before{content:"";position:absolute;left:.18em;top:.58em;width:.42em;height:.42em;
          border-radius:50%;background:var(--accent)}
ol{counter-reset:n}
ol li{padding-left:1.7em}
ol li:before{counter-increment:n;content:counter(n);background:none;color:var(--accent);
  font-weight:800;font-size:.92em;top:0;left:0;width:auto;height:auto;border-radius:0}
.chips{display:flex;flex-wrap:wrap;gap:16px}
.chips span{background:#fff;border:2px solid var(--accent2);color:#3d444c;border-radius:999px;
  padding:.34em .92em;font-size:.9em;line-height:1.5}
.callout{border-left:8px solid var(--accent);background:#fdf4f1;padding:.9em 1.1em;
  border-radius:0 14px 14px 0;line-height:1.68}
strong{color:#111418}
code{background:#f2f4f7;padding:.08em .34em;border-radius:5px;font-size:.92em}
.cover{flex:1 1 auto;display:flex;flex-direction:column;justify-content:center;
  padding:0 78px 40px;position:relative;z-index:1}
.cover h1{font-size:96px;line-height:1.15;margin:0}
.cover .sub{margin-top:26px;font-size:31px;max-width:820px}
.cover .chips{margin-top:44px}
.cover .chips span{background:#fff;border:2px solid var(--accent);color:var(--accent);font-weight:600}
.hero{margin-top:52px;border-radius:20px;overflow:hidden;border:1px solid #ead9d3;
  box-shadow:0 18px 44px rgba(80,40,30,.14);max-width:640px}
.hero img{display:block;width:100%}
.foot{flex:0 0 auto;padding:26px 78px 34px;display:flex;justify-content:space-between;
  align-items:center;font-size:23px;color:#9aa1a9;border-top:1px solid #f0eae5}
.foot b{color:#6b7480;font-weight:600}
.foot .repo{font-size:21px;color:#b3b9c0}
"""

FIT_JS = """
(function(){
  var fit=document.querySelector('.fit'), area=document.querySelector('.area');
  if(!fit||!area) return;
  var box=area.clientHeight, fs=parseFloat(getComputedStyle(fit).fontSize);
  while(fs>16 && fit.scrollHeight>box){ fs-=1; fit.style.fontSize=fs+'px'; }
  // 再压一次内边距，兜住极端长表
  var t=fit.querySelector('table');
  if(t && fit.scrollHeight>box){
    fit.querySelectorAll('td,th').forEach(function(c){ c.style.paddingTop='.4em'; c.style.paddingBottom='.4em'; });
  }
  window.__fit={fs:fs, need:fit.scrollHeight, box:box, ok:fit.scrollHeight<=box};
})();
"""


def _strip_no(t):
    """去掉小节标题开头的「一、」「十二、」「4. 」这类编号。"""
    t = re.sub(r'^[一二三四五六七八九十]+、\s*', '', str(t))
    return re.sub(r'^\d+\s*[.、)]\s*', '', t).strip()


def _same(a, b):
    """忽略标点与空白后比较，用来判断副标题是否只是标题的复述。"""
    n = lambda s: re.sub(r'[\s，,。.、：:；;（）()「」“”"\'\-—]', '', str(s))
    return n(a) == n(b) or n(a) in n(b) or n(b) in n(a)


def _blocks_of(mod, ch_no):
    for sec in mod.SECTIONS:
        for ch in sec['chapters']:
            if ch['no'] == ch_no:
                return ch
    raise KeyError(ch_no)


def _ctx(mod, ch_no, bi):
    """返回 (章标题, 块, 块之前的最近一个 h4 标题)。"""
    ch = _blocks_of(mod, ch_no)
    prev = ''
    for i, b in enumerate(ch['blocks']):
        if i == bi:
            return ch['title'], b, prev
        if b[0] == 'h4':
            prev = _strip_no(b[1])
    raise IndexError(f'ch{ch_no} 没有第 {bi} 个块')


def _render_block(b, max_rows=None, cols=None):
    k = b[0]
    if k in ('table', 'vtable'):
        head, rows = list(b[1]), [list(r) for r in b[2]]
        if cols:
            head, rows = head[:cols], [r[:cols] for r in rows]
        cut = 0
        if max_rows and len(rows) > max_rows:
            cut = len(rows) - max_rows
            rows = rows[:max_rows]
        th = ''.join(f'<th>{gen.inline(h, cite_ok=False)}</th>' for h in head)
        trs = []
        prev0 = None
        for ri, r in enumerate(rows):
            tds = []
            for ci, c in enumerate(r):
                if ci == 0 and ri > 0 and prev0 is not None and str(c) == prev0:
                    # 首列连续重复时只显示一次，避免整列都是同一个词
                    tds.append('<td></td>')
                    continue
                if ci == 0:
                    prev0 = str(c)
                cls = 'k wrap' if (ci == 0 and len(str(c)) > 12) else ('k' if ci == 0 else '')
                tds.append(f'<td class="{cls}">{gen.inline(str(c), cite_ok=False)}</td>')
            trs.append('<tr>' + ''.join(tds) + '</tr>')
        if cut:
            trs.append(f'<tr><td class="more" colspan="{len(head)}">'
                       f'另有 {cut} 条，见手册原文</td></tr>')
        return f'<table><thead><tr>{th}</tr></thead><tbody>{"".join(trs)}</tbody></table>'
    if k in ('ul', 'ol'):
        items = ''.join(f'<li>{gen.inline(x, cite_ok=False)}</li>' for x in b[1])
        return f'<{k}>{items}</{k}>'
    if k == 'chips':
        items = ''.join(f'<span>{gen.inline(x, cite_ok=False)}</span>' for x in b[1])
        return f'<div class="chips">{items}</div>'
    if k in ('note', 'tip', 'warn', 'danger'):
        return f'<div class="callout">{gen.inline(b[1], cite_ok=False)}</div>'
    if k == 'p':
        return f'<p>{gen.inline(b[1], cite_ok=False)}</p>'
    if k == 'grid':
        rows = ''.join(
            '<tr><td class="k">%s</td><td>%s</td></tr>' % (
                gen.inline(r[0], cite_ok=False),
                '、'.join(gen.inline(x, cite_ok=False) for x in r[1:]))
            for r in b[2] if len(r) > 1)
        return f'<table><tbody>{rows}</tbody></table>'
    return f'<p>{gen.inline(str(b[1]), cite_ok=False)}</p>'


def _card_html(bk, spec, idx, total):
    accent, accent2 = bk['accent'], bk['accent2']
    ch_title = kicker = ''
    body = ''

    if spec.get('kind') == 'cover':
        chips = ('<span>25 章</span><span>8 个附录</span><span>全文来源可追溯</span>'
                 '<span>离线 PDF · 可打印</span>')
        hero = ''
        if bk.get('hero'):
            hero = f'<div class="hero"><img src="{gen.img_uri(bk["hero"])}" alt=""></div>'
        body = (f'<div class="cover"><div class="kicker"><span class="dot"></span>'
                f'{bk["name"]} · {bk["ver"]}</div>'
                f'<h1>{gen.inline(spec["title"], cite_ok=False)}</h1>'
                f'<div class="sub">{gen.inline(spec["sub"], cite_ok=False)}</div>'
                f'<div class="chips">{chips}</div>{hero}</div>')
    else:
        mod = MOD_CAT if bk['slug'] == 'cat' else MOD_DOG
        ch_title, block, prev_h4 = _ctx(mod, spec['ch'], spec['bi'])
        kicker = (f'<div class="kicker"><span class="dot"></span>{bk["name"]}'
                  f'<span class="ch"> · 第 {spec["ch"]} 章 {ch_title}</span></div>')
        title = spec.get('title') or prev_h4
        sub = ''
        if prev_h4 and spec.get('title') and not _same(prev_h4, spec['title']):
            sub = f'<div class="sub">{gen.inline(prev_h4, cite_ok=False)}</div>'
        h1cls = ' class="sm"' if len(title) > 16 else ''
        head = f'{kicker}<h1{h1cls}>{gen.inline(title, cite_ok=False)}</h1>{sub}'
        inner = _render_block(block, spec.get('max_rows'), spec.get('cols'))
        body = (f'<div class="head">{head}</div><div class="rule"></div>'
                f'<div class="area"><div class="fit">{inner}</div></div>')

    return f'''<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="utf-8">
<title>{spec['id']}</title><style>
:root{{--accent:{accent};--accent2:{accent2}}}
{CARD_CSS}</style></head>
<body><div class="card"><div class="bar"></div><div class="wm"></div>
{body}
<div class="foot"><span><b>{bk['name']} · {bk['ver']}</b></span>
<span class="repo">第 {idx:02d} / {total:02d}　github.com/nullurl/pet-handbook</span></div>
</div><script>{FIT_JS}</script></body></html>'''


def build_gallery(out_path, labels, groups=None):
    """生成素材墙页面。labels：{png 文件名: 中文标题}。"""
    groups = groups or [('cat', '🐱 养猫手册'), ('dog', '🐶 养狗手册')]
    secs = []
    total = 0
    for prefix, title in groups:
        names = sorted(n for n in labels if n.startswith(prefix + '-'))
        if not names:
            continue
        total += len(names)
        cards = ''.join(
            f'<a class="c" href="assets/social/{n}" target="_blank">'
            f'<img src="assets/social/{n}" alt="{labels[n]}" loading="lazy">'
            f'<div class="t">{labels[n]}</div>'
            f'<div class="d">{n}<span>打开 / 下载</span></div></a>'
            for n in names)
        secs.append(f'<h2>{title}<span class="n">{len(names)} 张</span></h2>'
                    f'<div class="grid">{cards}</div>')
    html = f'''<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>自媒体图卡素材 · 宠物饲养手册</title>
<style>
:root{{--ink:#1a1d21;--ink3:#6b7480;--line:#e3e7ec}}
*{{box-sizing:border-box}}
body{{margin:0;background:#f7f8fa;color:var(--ink);
 font-family:-apple-system,BlinkMacSystemFont,"PingFang SC","Microsoft YaHei",sans-serif}}
header{{background:linear-gradient(135deg,#1f2328,#3a2f2c 55%,#5d2a24);color:#fff;padding:52px 40px 44px}}
header h1{{margin:0 0 12px;font-size:32px}}
header p{{margin:0;color:#d8cfcd;font-size:15px;line-height:1.85;max-width:800px}}
header a{{color:#fff}}
.wrap{{max-width:1180px;margin:0 auto;padding:8px 24px 60px}}
h2{{font-size:19px;margin:38px 0 16px;padding-left:12px;border-left:4px solid #c0392b;
 display:flex;align-items:baseline;gap:10px}}
h2 .n{{font-size:13px;font-weight:400;color:var(--ink3);border:0}}
.grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(228px,1fr));gap:20px}}
.c{{display:block;background:#fff;border:1px solid var(--line);border-radius:14px;overflow:hidden;
 text-decoration:none;color:inherit;transition:.15s}}
.c:hover{{box-shadow:0 10px 26px rgba(16,24,40,.13);transform:translateY(-2px)}}
.c img{{display:block;width:100%;height:auto;background:#fff}}
.c .t{{padding:11px 13px 4px;font-size:13.5px;font-weight:600;line-height:1.5}}
.c .d{{padding:0 13px 13px;font-size:11.5px;color:var(--ink3);display:flex;
 justify-content:space-between;gap:8px}}
.c .d span{{color:#c0392b;font-weight:600;flex:0 0 auto}}
footer{{border-top:1px solid var(--line);padding:26px 24px 60px;text-align:center;
 color:var(--ink3);font-size:13px}}
footer a{{color:var(--ink3)}}
</style></head><body>
<header>
  <h1>自媒体图卡素材</h1>
  <p>共 {total} 张，1080×1440（3:4）。内容全部取自《养猫手册》《养狗手册》正文，
  按原文引用、未另写文案；图上已带来源标注与仓库地址。可直接用于公众号 / 小红书 / 朋友圈，
  点开大图另存即可。</p>
</header>
<div class="wrap">
{''.join(secs)}
</div>
<footer>宠物饲养手册 2026 ·
  <a href="index.html">养猫手册</a> ·
  <a href="dog.html">养狗手册</a> ·
  <a href="https://github.com/nullurl/pet-handbook/tree/main/docs/单文件离线版">PDF 与单文件版</a></footer>
</body></html>'''
    with io.open(out_path, 'w', encoding='utf-8') as f:
        f.write(html)
    return total


def main():
    os.makedirs(OUT, exist_ok=True)
    gen.CITE_TERMS = []          # 卡片上不印角标，保持画面干净
    gen.IMG_MODE = 'external'    # 封面图走相对路径，截图时按目录就地解析
    gen.IMG_PREFIX = os.path.join(ROOT, 'github', 'docs', 'assets')

    # 先跑一次管线，拿到中性化后的正文
    for mod, kind in ((MOD_CAT, 'cat'), (MOD_DOG, 'dog')):
        build2.transform(mod, kind)

    labels, manifest = {}, []
    for kind in ('cat', 'dog'):
        bk = BOOK[kind]
        specs = MATERIALS[kind]
        for i, spec in enumerate(specs, 1):
            html = _card_html(bk, spec, i, len(specs))
            name = f'{kind}-{i:02d}-{spec["id"]}'
            with io.open(os.path.join(OUT, name + '.html'), 'w', encoding='utf-8') as f:
                f.write(html)
            manifest.append({'html': os.path.join(OUT, name + '.html'),
                             'png': name + '.png', 'label': spec.get('title', name)})
            labels[name + '.png'] = spec.get('title', name)

    with io.open(os.path.join(OUT, 'manifest.json'), 'w', encoding='utf-8') as f:
        json.dump(manifest, f, ensure_ascii=False, indent=1)

    os.makedirs(PNG_DIR, exist_ok=True)
    with io.open(os.path.join(PNG_DIR, 'labels.json'), 'w', encoding='utf-8') as f:
        json.dump(labels, f, ensure_ascii=False, indent=1)

    print(f'卡片 HTML {len(manifest)} 张 → {OUT}')
    print(f'  猫 {len(MATERIALS["cat"])} 张  犬 {len(MATERIALS["dog"])} 张')
    print(f'  标签 → {os.path.join(PNG_DIR, "labels.json")}')


if __name__ == '__main__':
    main()

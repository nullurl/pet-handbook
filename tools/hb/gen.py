# -*- coding: utf-8 -*-
"""手册渲染引擎：统一 CSS + 简易块 DSL -> 单文件 HTML

图片以 base64 内联，保证输出仍是「单文件 HTML」，可直接发送/打印。
"""

import base64
import os

_HERE = os.path.dirname(os.path.abspath(__file__))


def _pick(*cands):
    """返回第一个存在的候选路径；都不存在时返回第一个（便于报错时定位）。"""
    for c in cands:
        if os.path.isdir(c):
            return os.path.normpath(c)
    return os.path.normpath(cands[0])


# 开发目录（hb/img、hb/img2）与仓库目录（docs/assets/illus、docs/assets/orig）两种布局都支持
IMG_DIR = _pick(os.path.join(_HERE, 'img'),
                os.path.join(_HERE, '..', 'docs', 'assets', 'illus'),
                os.path.join(_HERE, '..', '..', 'docs', 'assets', 'illus'))
IMG_DIR2 = _pick(os.path.join(_HERE, 'img2'),
                 os.path.join(_HERE, '..', 'docs', 'assets', 'orig'),
                 os.path.join(_HERE, '..', '..', 'docs', 'assets', 'orig'))
_IMG_CACHE = {}
_MIME = {'jpg': 'jpeg', 'jpeg': 'jpeg', 'png': 'png', 'gif': 'gif', 'webp': 'webp'}

# 'inline'  -> 图片以 base64 内联，输出单文件 HTML（离线/发送用）
# 'external'-> 图片写成相对路径 assets/<子目录>/<name>（GitHub / 静态站点用）
IMG_MODE = 'inline'
IMG_PREFIX = 'assets'
_SUBDIR = {'img': 'illus', 'img2': 'orig'}


def img_path(name):
    """返回图片在磁盘上的绝对路径；两个目录都找不到则抛错。"""
    for d in (IMG_DIR, IMG_DIR2):
        p = os.path.join(d, name)
        if os.path.exists(p):
            return p
    raise FileNotFoundError(name)


def img_uri(name):
    """返回该图的引用地址：内联模式为 base64 data URI，外链模式为相对路径。"""
    if IMG_MODE == 'external':
        sub = 'illus' if os.path.exists(os.path.join(IMG_DIR, name)) else 'orig'
        return f'{IMG_PREFIX}/{sub}/{name}'
    if name not in _IMG_CACHE:
        ext = name.rsplit('.', 1)[-1].lower()
        mime = _MIME.get(ext, 'jpeg')
        with open(img_path(name), 'rb') as f:
            _IMG_CACHE[name] = f'data:image/{mime};base64,' + base64.b64encode(f.read()).decode()
    return _IMG_CACHE[name]


CSS = """
:root{
  --ink:#1a1d21; --ink2:#41474f; --ink3:#6b7480;
  --line:#e3e7ec; --line2:#eef1f5;
  --bg:#ffffff; --bg2:#f7f8fa; --bg3:#f1f3f7;
  --brand:#c0392b; --brand2:#a93226; --brandbg:#fdf2f0;
  --blue:#1d4ed8; --bluebg:#eff4ff;
  --green:#0f7b4f; --greenbg:#eefaf4;
  --amber:#a16207; --amberbg:#fff9e8;
  --purple:#6d28d9; --purplebg:#f4f0ff;
}
*{box-sizing:border-box}
html{scroll-behavior:smooth}
body{
  margin:0; background:var(--bg2); color:var(--ink);
  font-family:-apple-system,BlinkMacSystemFont,"PingFang SC","Hiragino Sans GB","Microsoft YaHei",sans-serif;
  font-size:15.5px; line-height:1.85; -webkit-font-smoothing:antialiased;
}
.wrap{display:flex; align-items:flex-start; max-width:1400px; margin:0 auto;}
/* ---------- 侧边目录 ---------- */
aside{
  width:300px; flex:0 0 300px; position:sticky; top:0; height:100vh; overflow-y:auto;
  background:#fff; border-right:1px solid var(--line); padding:22px 0 60px;
}
aside .brand{padding:0 22px 16px; border-bottom:1px solid var(--line2); margin-bottom:12px}
aside .brand b{display:block; font-size:16px; letter-spacing:.3px}
aside .brand span{font-size:12px; color:var(--ink3)}
aside a{display:block; padding:5px 22px; color:var(--ink2); text-decoration:none; font-size:13.5px; border-left:3px solid transparent;}
aside a:hover{background:var(--bg3); color:var(--brand)}
aside a.sec{font-weight:700; color:var(--ink); margin-top:10px; font-size:13px; padding-top:9px; border-top:1px solid var(--line2)}
aside a.sec:hover{border-left-color:var(--brand)}
aside a.ch{padding-left:34px; font-size:13px; color:var(--ink3)}
aside a.ch:hover{color:var(--brand)}
/* ---------- 正文 ---------- */
main{flex:1 1 auto; min-width:0; background:#fff; padding:0 0 80px;}
header.hero{
  background:linear-gradient(135deg,#1f2328 0%,#3a2f2c 55%,#5d2a24 100%);
  color:#fff; padding:56px 60px 48px; position:relative; overflow:hidden;
}
header.hero:after{content:""; position:absolute; right:-60px; top:-60px; width:280px; height:280px;
  border-radius:50%; background:rgba(255,255,255,.05)}
header.hero .kicker{font-size:12.5px; letter-spacing:2px; color:#e7b9b2; text-transform:uppercase}
header.hero h1{font-size:36px; margin:10px 0 6px; line-height:1.25; letter-spacing:.5px}
header.hero .sub{font-size:15px; color:#d8cfcd; max-width:760px}
header.hero .meta{margin-top:24px; display:flex; flex-wrap:wrap; gap:10px}
header.hero .meta span{
  background:rgba(255,255,255,.12); border:1px solid rgba(255,255,255,.18);
  padding:5px 12px; border-radius:20px; font-size:12.5px; color:#f0e6e4}
header.hero .hero-inner{display:flex; gap:34px; align-items:center; position:relative; z-index:2}
header.hero .hero-txt{flex:1 1 auto; min-width:0}
header.hero .hero-art{flex:0 0 330px; border-radius:16px; overflow:hidden;
  box-shadow:0 16px 40px rgba(0,0,0,.42); border:1px solid rgba(255,255,255,.16)}
header.hero .hero-art img{display:block; width:100%; height:auto}
/* ---------- 插图 ---------- */
figure{margin:22px 0; border:1px solid var(--line); border-radius:14px;
  overflow:hidden; background:#fff; box-shadow:0 2px 10px rgba(16,24,40,.05)}
figure img{display:block; width:100%; height:auto}
figure figcaption{padding:11px 18px; font-size:13.2px; color:var(--ink3);
  background:var(--bg2); border-top:1px solid var(--line2); line-height:1.75}
figure figcaption b{color:var(--ink2)}
figure figcaption em{font-style:normal; display:inline-block; background:var(--brand);
  color:#fff; border-radius:4px; padding:1px 7px; margin-right:8px; font-size:11.5px; letter-spacing:.6px}
figure.tall{max-width:520px; margin-left:auto; margin-right:auto}
sup.cite{font-size:.72em; line-height:0; vertical-align:super; margin-left:1px}
sup.cite a{color:var(--blue); text-decoration:none; font-weight:600;
  background:var(--bluebg); border:1px solid #d6e2ff; border-radius:4px; padding:0 3px}
sup.cite a:hover{background:var(--blue); color:#fff}
.figmix{margin:22px 0}
.figmix .cap{font-size:12.5px; color:#8a6320; background:#fbf9f4; border:1px solid #ecdfc9;
  border-bottom:0; border-radius:10px 10px 0 0; padding:8px 14px; font-weight:700; letter-spacing:.8px}
.figmix .figrow{margin-top:0}
.figmix .figrow figure{border-radius:0}
.vidbox{margin:22px 0; border:1px solid var(--line); border-radius:14px; overflow:hidden; background:#fff;
  box-shadow:0 2px 10px rgba(16,24,40,.05)}
.vidbox .vwrap{position:relative}
.vidbox img{display:block; width:100%; height:auto}
.vidbox .vplay{position:absolute; inset:0; display:flex; align-items:center; justify-content:center;
  background:rgba(0,0,0,.22); text-decoration:none}
.vidbox .vplay i{width:64px; height:64px; border-radius:50%; background:rgba(255,255,255,.92);
  display:flex; align-items:center; justify-content:center; font-style:normal; font-size:26px; color:#c0392b;
  box-shadow:0 6px 20px rgba(0,0,0,.3)}
.vidbox figcaption{padding:11px 18px; font-size:13.2px; color:var(--ink3);
  background:var(--bg2); border-top:1px solid var(--line2); line-height:1.75}
.vidbox figcaption em{font-style:normal; display:inline-block; background:#1d4ed8; color:#fff;
  border-radius:4px; padding:1px 7px; margin-right:8px; font-size:11.5px; letter-spacing:.6px}
.figrow{display:grid; grid-template-columns:1fr 1fr; gap:16px; margin:22px 0}
.figrow figure{margin:0}
@media (max-width:760px){.figrow{grid-template-columns:1fr}}
.body{padding:0 60px}
h2{
  font-size:23px; margin:52px 0 18px; padding:14px 0 12px 18px;
  border-left:5px solid var(--brand); background:linear-gradient(90deg,var(--brandbg),transparent 70%);
  border-radius:0 8px 8px 0;
}
h3{font-size:18px; margin:34px 0 12px; padding-left:12px; border-left:3px solid var(--line); color:var(--ink)}
h3 .no{color:var(--brand); font-weight:800; margin-right:8px}
h4{font-size:15.5px; margin:22px 0 8px; color:var(--ink2)}
p{margin:10px 0; color:var(--ink2)}
strong{color:var(--ink)}
ul,ol{margin:10px 0 14px; padding-left:22px; color:var(--ink2)}
li{margin:6px 0}
li::marker{color:var(--brand)}
hr{border:0; border-top:1px dashed var(--line); margin:36px 0}
a.ref{color:var(--blue); text-decoration:none; border-bottom:1px dotted var(--blue)}
table{width:100%; border-collapse:collapse; margin:14px 0 20px; font-size:14px;}
th,td{border:1px solid var(--line); padding:9px 12px; text-align:left; vertical-align:top}
th{background:var(--bg3); font-weight:700; color:var(--ink)}
tbody tr:nth-child(even){background:#fbfcfd}
.num{font-variant-numeric:tabular-nums}
table.vlog td:nth-child(3),table.vlog th:nth-child(3){white-space:nowrap;text-align:center;font-weight:600}
/* ---------- 二级小节（合并后的续写段落，不再标注来源） ---------- */
.subsec{margin:16px 0 4px}
.subsec .sub-h{font-size:15px; font-weight:800; color:var(--ink); margin:18px 0 6px;
  padding-left:10px; border-left:3px solid var(--brand); line-height:1.5}
.subsec .sub-h:first-child{margin-top:6px}
.subsec p{margin:8px 0}
blockquote.q{margin:10px 0; padding:2px 0 2px 15px; border-left:3px solid var(--line);
  color:var(--ink3); font-size:14.2px; line-height:1.82}
blockquote.q p{margin:0; color:var(--ink3)}
/* ---------- 交叉指引 ---------- */
.xref{margin:18px 0; padding:10px 16px; background:var(--bg3); border:1px dashed var(--line);
  border-radius:10px; font-size:13.8px; color:var(--ink2); line-height:1.8}
.xref a{color:var(--blue); text-decoration:none; font-weight:600; border-bottom:1px dotted var(--blue)}
.xref b{color:var(--ink)}
/* ---------- 附录：来源 / 差异 ---------- */
.app-lead{font-size:14px; color:var(--ink3); margin:6px 0 14px}
table.ftab th{background:var(--bg3)}
table.ftab td:nth-child(1){color:var(--ink2)}
table.ftab td:nth-child(3){font-weight:600}
table.refs{font-size:13.6px}
table.refs td:nth-child(1){white-space:nowrap; text-align:center; font-weight:700; color:var(--brand);
  font-variant-numeric:tabular-nums; width:52px}
table.refs td:nth-child(2){width:34%; color:var(--ink)}
.refnote{font-size:12.8px; color:var(--ink3); margin:-6px 0 16px}
h4.apph{font-size:16px; margin:30px 0 10px; padding:8px 14px; background:var(--bg3);
  border-radius:8px; color:var(--ink); border-left:4px solid var(--ink3)}
h5.apph5{font-size:14.5px; margin:20px 0 8px; color:var(--ink2)}
/* ---------- 卡片 / 提示 ---------- */
.note,.warn,.tip,.danger{
  border-radius:10px; padding:14px 18px; margin:16px 0; font-size:14.5px; line-height:1.8}
.note{background:var(--bluebg); border-left:4px solid var(--blue)}
.tip{background:var(--greenbg); border-left:4px solid var(--green)}
.warn{background:var(--amberbg); border-left:4px solid var(--amber)}
.danger{background:var(--brandbg); border-left:4px solid var(--brand)}
.note b,.tip b,.warn b,.danger b{display:inline-block; margin-right:6px}
.danger b{color:var(--brand2)}
.grid{display:grid; grid-template-columns:repeat(auto-fit,minmax(240px,1fr)); gap:14px; margin:18px 0}
.card{background:#fff; border:1px solid var(--line); border-radius:12px; padding:16px 18px; box-shadow:0 1px 2px rgba(16,24,40,.04)}
.card h5{margin:0 0 8px; font-size:15px; color:var(--brand)}
.card p{margin:6px 0; font-size:14px; color:var(--ink3)}
.chip{display:inline-block; background:var(--bg3); border:1px solid var(--line); color:var(--ink2);
  border-radius:999px; padding:2px 10px; font-size:12.5px; margin:2px 4px 2px 0}
.toc-grid{display:grid; grid-template-columns:repeat(auto-fit,minmax(280px,1fr)); gap:16px; margin:20px 0 10px}
.toc-grid .col{border:1px solid var(--line); border-radius:12px; padding:14px 18px; background:#fff}
.toc-grid .col h5{margin:0 0 8px; color:var(--brand); font-size:14.5px; letter-spacing:.5px}
.toc-grid .col a{display:block; color:var(--ink2); text-decoration:none; font-size:13.5px; padding:3px 0; line-height:1.7}
.toc-grid .col a:hover{color:var(--brand)}
.toc-grid .col a i{color:var(--ink3); font-style:normal; margin-right:6px; font-variant-numeric:tabular-nums}
footer{padding:36px 60px; color:var(--ink3); font-size:12.5px; border-top:1px solid var(--line); line-height:1.9}
.backtop{position:fixed; right:26px; bottom:26px; background:var(--brand); color:#fff; width:44px; height:44px;
  border-radius:50%; display:flex; align-items:center; justify-content:center; text-decoration:none;
  box-shadow:0 6px 18px rgba(192,57,43,.35); font-size:18px}
@media print{
  aside,.backtop{display:none} body{background:#fff}
  .wrap{display:block; max-width:none} main{padding:0}
  header.hero{padding:30px} .body,footer{padding:0 12px}
  h2{page-break-after:avoid} h3{page-break-after:avoid} table{page-break-inside:avoid}
  figure{page-break-inside:avoid; box-shadow:none}
}
@media (max-width:900px){
  aside{display:none} .body{padding:0 20px} header.hero{padding:34px 20px} footer{padding:24px 20px}
  header.hero .hero-art{display:none}
}
"""


def esc(s):
    return (s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;'))


# 角标：正文首次提到某权威来源处，插入上标 [n]，指向附录「引用来源清单」
CITE_TERMS = []      # [(关键词, 编号)]，由 provenance 注入，长词在前
_CITE_SEEN = set()
_SUP = '<sup class="cite"><a href="#ref-%s" title="见附录H · 引用来源清单">[%s]</a></sup>'


def _cite(s):
    """在一段 HTML 里，为每个来源编号插入最多一个 [n] 上标。

    从左到右单遍扫描，同一位置取最长匹配，因此「CVMA 团体标准」不会被拆成两个角标。
    """
    if not CITE_TERMS:
        return s
    out, i, n = [], 0, len(s)
    while i < n:
        hit = None
        for needle, rid in CITE_TERMS:
            if rid not in _CITE_SEEN and s.startswith(needle, i):
                hit = (needle, rid)
                break
        if hit:
            needle, rid = hit
            j = i + len(needle)
            out.append(s[i:j])
            out.append(_SUP % (rid, rid))
            _CITE_SEEN.add(rid)
            i = j
        else:
            out.append(s[i])
            i += 1
    return ''.join(out)


def inline(s, cite_ok=True):
    """支持 **粗体**、`代码`，把成对直角引号换成中文引号，并注入来源角标"""
    import re
    s = esc(s)
    s = s.replace('&lt;br&gt;', '<br>')     # 允许文本里用 <br> 换行
    s = re.sub(r'"([^"]*)"', lambda m: '\u201c' + m.group(1) + '\u201d', s)
    s = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', s)
    s = re.sub(r'`(.+?)`', r'<code>\1</code>', s)
    if cite_ok and CITE_TERMS:
        s = _cite(s)
    s = s.replace('\n', '<br>')
    return s


def _fig(name, cap, tag='配图', tall=False):
    c = ' class="tall"' if tall else ''
    return (f'<figure{c}><img src="{img_uri(name)}" alt="{esc(cap[:60])}" loading="lazy">'
            f'<figcaption><em>{tag}</em>{inline(cap)}</figcaption></figure>')


def render_blocks(blocks):
    global _CITE_SEEN
    _CITE_SEEN = set()
    out = []
    for b in blocks:
        k = b[0]
        if k == 'h3':
            out.append(f'<h3 id="{b[2] if len(b) > 2 else ""}">{b[1]}</h3>')
        elif k == 'h4':
            out.append(f'<h4>{inline(b[1], cite_ok=False)}</h4>')
        elif k == 'apph':
            out.append(f'<h4 class="apph" id="{b[2] if len(b) > 2 else ""}">{inline(b[1], cite_ok=False)}</h4>')
        elif k == 'apph5':
            out.append(f'<h5 class="apph5">{inline(b[1], cite_ok=False)}</h5>')
        elif k == 'lead':
            out.append(f'<p class="app-lead">{inline(b[1], cite_ok=False)}</p>')
        elif k == 'refnote':
            out.append(f'<p class="refnote">{inline(b[1], cite_ok=False)}</p>')
        elif k == 'p':
            out.append(f'<p>{inline(b[1])}</p>')
        elif k == 'ul':
            out.append('<ul>' + ''.join(f'<li>{inline(x)}</li>' for x in b[1]) + '</ul>')
        elif k == 'ol':
            out.append('<ol>' + ''.join(f'<li>{inline(x)}</li>' for x in b[1]) + '</ol>')
        elif k == 'q':
            out.append(f'<blockquote class="q"><p>{inline(b[1])}</p></blockquote>')
        elif k == 'note':
            out.append(f'<div class="note">💡 {inline(b[1])}</div>')
        elif k == 'tip':
            out.append(f'<div class="tip">✅ {inline(b[1])}</div>')
        elif k == 'warn':
            out.append(f'<div class="warn">⚠️ {inline(b[1])}</div>')
        elif k == 'danger':
            out.append(f'<div class="danger">🚨 {inline(b[1])}</div>')
        elif k == 'table':
            out.append(_table(b[1], b[2], ''))
        elif k == 'vtable':
            out.append(_table(b[1], b[2], 'vlog'))
        elif k == 'ftable':
            out.append(_table(b[1], b[2], 'ftab'))
        elif k == 'rtable':
            out.append(_table(b[1], b[2], 'refs'))
        elif k == 'src':
            # 与正文合并后的续写小节：不带任何来源标签
            inner = []
            for item in b[2]:
                if item[0] == 'h6':
                    inner.append(f'<div class="sub-h">{inline(item[1], cite_ok=False)}</div>')
                elif item[0] == 'p':
                    inner.append(f'<p>{inline(item[1])}</p>')
                elif item[0] == 'q':
                    inner.append(f'<blockquote class="q"><p>{inline(item[1])}</p></blockquote>')
                elif item[0] == 'ul':
                    inner.append('<ul>' + ''.join(f'<li>{inline(x)}</li>' for x in item[1]) + '</ul>')
                elif item[0] == 'ol':
                    inner.append('<ol>' + ''.join(f'<li>{inline(x)}</li>' for x in item[1]) + '</ol>')
            head = f'<div class="sub-h">{inline(b[1], cite_ok=False)}</div>' if b[1] else ''
            out.append('<div class="subsec">' + head + ''.join(inner) + '</div>')
        elif k == 'xref':
            # ('xref', '本章的对照与差异说明见', ('附录G.12', 'appG-12'))
            out.append(f'<div class="xref">{inline(b[1])} '
                       f'<a href="#{b[2][1]}">{b[2][0]}</a></div>')
        elif k == 'grid':
            cards = ''.join(
                f'<div class="card"><h5>{inline(c[0], cite_ok=False)}</h5>'
                + ''.join(f'<p>{inline(x)}</p>' for x in c[1:]) + '</div>'
                for c in b[1])
            out.append(f'<div class="grid">{cards}</div>')
        elif k == 'chips':
            out.append(''.join(f'<span class="chip">{inline(x, cite_ok=False)}</span>' for x in b[1]))
        elif k == 'fig':
            # ('fig', 'cat-cover.jpg', '图注') 或 ('fig', 'x.jpg', '图注', '标签'[, 'tall'])
            out.append(_fig(b[1], b[2],
                            b[3] if len(b) > 3 else '配图',
                            len(b) > 4 and b[4] == 'tall'))
        elif k == 'figs':
            # ('figs', [ (name, caption) | (name, caption, tag), ... ])
            cells = []
            for it in b[1]:
                cells.append(_fig(it[0], it[1], it[2] if len(it) > 2 else '配图'))
            out.append('<div class="figrow">' + ''.join(cells) + '</div>')
        elif k == 'vid':
            # ('vid', 'poster.jpg', '视频说明', '播放链接')
            out.append(f'<div class="vidbox"><div class="vwrap"><img src="{img_uri(b[1])}" alt="视频封面">'
                       f'<a class="vplay" href="{esc(b[3])}" target="_blank" rel="noopener"><i>▶</i></a></div>'
                       f'<figcaption><em>视频</em>{inline(b[2])}</figcaption></div>')
        elif k == 'hr':
            out.append('<hr>')
    return '\n'.join(out)


def _table(head, rows, cls):
    c = f' class="{cls}"' if cls else ''
    ok = cls != 'refs'          # 引用来源清单本身不再加角标
    t = f'<table{c}><thead><tr>' + ''.join(f'<th>{inline(h, cite_ok=False)}</th>' for h in head) + '</tr></thead><tbody>'
    for r in rows:
        cells = []
        for ci, x in enumerate(r):
            aid = f' id="ref-{x}"' if (cls == 'refs' and ci == 0) else ''
            cells.append(f'<td{aid}>{inline(x, cite_ok=ok)}</td>')
        t += '<tr>' + ''.join(cells) + '</tr>'
    return t + '</tbody></table>'


def build(meta, sections, front_extra, appendices, slug):
    # 侧边栏
    sb = ['<div class="brand"><b>%s</b><span>%s</span></div>' % (esc(meta['title']), esc(meta['version']))]
    sb.append('<a href="#top">封面与使用说明</a>')
    for si, sec in enumerate(sections):
        sb.append(f'<a class="sec" href="#sec{si}">{esc(sec["name"])}</a>')
        for ch in sec['chapters']:
            sb.append(f'<a class="ch" href="#{ch["id"]}">{ch["no"]}. {esc(ch["title"])}</a>')
    sb.append('<a class="sec" href="#app">附录</a>')
    for ap in appendices:
        sb.append(f'<a class="ch" href="#{ap["id"]}">{esc(ap["title"])}</a>')

    # 目录网格
    tg = ['<div class="toc-grid">']
    for si, sec in enumerate(sections):
        tg.append('<div class="col"><h5>%s</h5>' % esc(sec['name']))
        for ch in sec['chapters']:
            tg.append(f'<a href="#{ch["id"]}"><i>{ch["no"]}</i>{esc(ch["title"])}</a>')
        tg.append('</div>')
    tg.append('</div>')

    body = ['<header class="hero" id="top">']
    body.append('<div class="hero-inner"><div class="hero-txt">')
    body.append(f'<div class="kicker">{esc(meta["kicker"])}</div>')
    body.append(f'<h1>{esc(meta["title"])}</h1>')
    body.append(f'<div class="sub">{esc(meta["subtitle"])}</div>')
    body.append('<div class="meta">' + ''.join(f'<span>{esc(x)}</span>' for x in meta['meta']) + '</div>')
    body.append('</div>')
    if meta.get('hero'):
        body.append(f'<div class="hero-art"><img src="{img_uri(meta["hero"])}" alt="封面插图"></div>')
    body.append('</div></header><div class="body">')
    body.append(render_blocks(front_extra))
    body.append('<h2 id="toc">目录</h2>')
    body.append(''.join(tg))

    for si, sec in enumerate(sections):
        body.append(f'<h2 id="sec{si}">{esc(sec["name"])}</h2>')
        if sec.get('intro'):
            body.append(f'<p>{inline(sec["intro"])}</p>')
        for ch in sec['chapters']:
            body.append(f'<h3 id="{ch["id"]}"><span class="no">{ch["no"]}</span>{esc(ch["title"])}</h3>')
            body.append(render_blocks(ch['blocks']))

    body.append('<h2 id="app">附录</h2>')
    for ap in appendices:
        body.append(f'<h3 id="{ap["id"]}">{esc(ap["title"])}</h3>')
        body.append(render_blocks(ap['blocks']))
    body.append('</div>')

    html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(meta["title"])} · {esc(meta["version"])}</title>
<style>{CSS}</style>
</head>
<body>
<div class="wrap">
<aside>{''.join(sb)}</aside>
<main>{''.join(body)}
<footer>{esc(meta["footer"])}</footer>
</main>
</div>
<a class="backtop" href="#top">↑</a>
</body>
</html>'''
    return html

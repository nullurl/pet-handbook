# -*- coding: utf-8 -*-
"""把成品打包成 GitHub 仓库结构。

    github/
      README.md  LICENSE  .gitignore  .gitattributes
      docs/       index.html  dog.html  单文件离线版/    assets/{illus,orig}/
      data/       两份 CSV
      tools/      生成脚本（可复现）
"""

import os
import re
import sys
import shutil

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import gen  # noqa: E402
import cat as MOD_CAT  # noqa: E402
import dog as MOD_DOG  # noqa: E402

ROOT = os.path.abspath(os.path.join(HERE, '..'))
REPO = os.path.join(ROOT, 'github')
OWNER, NAME = 'nullurl', 'pet-handbook'
PAGES = f'https://{OWNER}.github.io/{NAME}'

IMG_RE = re.compile(r'\.(jpg|jpeg|png|gif|webp)$', re.I)


def used_images():
    names = set()

    def rec(o):
        if isinstance(o, str):
            if IMG_RE.search(o):
                names.add(o)
        elif isinstance(o, dict):
            for v in o.values():
                rec(v)
        elif isinstance(o, (list, tuple)):
            for x in o:
                rec(x)
    for m in (MOD_CAT, MOD_DOG):
        rec(m.SECTIONS)
        rec(m.META)
    # 封面图
    for m in (MOD_CAT, MOD_DOG):
        if m.META.get('hero'):
            names.add(m.META['hero'])
    return names


def write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(text)


README = f'''# 宠物饲养手册（2026）

两本写给中国养宠人的实用手册：**《养猫手册》** 与 **《养狗手册》**。
各 **25 章 + 8 个附录**，正文里每一个数字都能追到出处；凡是权威来源之间有分歧的地方，
都单独列出来，而不是揉成一句"看情况"。

## 在线阅读

| 手册 | 链接 |
|---|---|
| 🐱 养猫手册（2026 增订版） | <{PAGES}/> |
| 🐶 养狗手册（2026 版） | <{PAGES}/dog.html> |

也可以直接打开仓库里的 `docs/index.html` 与 `docs/dog.html`。

## 单文件离线版

`docs/单文件离线版/` 下是两份**把图片内联进去**的单文件 HTML（各约 4 MB），
不依赖任何外部资源，可直接下载、打印、发给朋友：

- [养猫手册-2026增订版.html]({PAGES}/单文件离线版/养猫手册-2026增订版.html)（4.8 MB）
- [养狗手册-2026版.html]({PAGES}/单文件离线版/养狗手册-2026版.html)（4.1 MB）

也可以从仓库里直接下载原始文件，或用 `curl -O` 抓取上面的直链。

## 内容结构

五个部分、25 章，另加 8 个附录。

| 部分 | 章节 | 养猫手册 | 养狗手册 |
|---|---|---|---|
| 一 · 相处 | 1–5 | 新手 30 问、行为心理、到家注意、互动建立感情、共生史 | 同结构，按犬重写 |
| 二 · 喂养 | 6–9 | 猫粮、生骨肉、零食、营养品 | 狗粮、生食鲜食、零食、补剂 |
| 三 · 健康 | 10–14 | 绝育、驱虫、疫苗、牙结石、呕吐拉稀挠伤 | 绝育、驱虫心丝虫、疫苗、口腔、急症（GDV / 中暑） |
| 四 · 清单 | 15–17 | 铲屎官购物清单、猫舍家长清单、进阶好物 | 新手狗家长清单、到家 30 天、进阶装备 |
| 五 · 备查 | 18–25 | 剪指甲、空调、托运、猫粮碗、拍照、掉毛、有毒植物、书单 | 同主题，按犬重写 |

### 附录

| | 内容 |
|---|---|
| A | 权威知识库速查（疫苗程序 / BCS 体况评分 / 驱虫 / 绝育 / 口腔） |
| B | 全国宠物医院信息（24 小时急诊 · 价格 · 评价参考） |
| C | 危险食物、毒物与植物清单（**含中毒剂量**） |
| D | 急诊速查卡（红旗信号 · 生命体征 · 出门清单） |
| E | 核对与勘误表（2026-10-01 逐条回查） |
| **F** | **内容来源与出处对照**（逐章列出内容底本与权威来源编号） |
| **G** | **对照与差异说明**（正文中所有对照表集中在此，按章编号） |
| **H** | **引用来源清单（References）** + 底本各篇原文链接 |

## 来源与引用怎么读

正文**不区分"底本"与"补充"**，读下来就是一本完整的手册；出处统一收进附录：

1. 正文里凡出现 `[n]` 上标，点击即跳到 **附录H** 的对应条目；
2. 每一章末尾有一行「本章的**对照与差异说明**已统一收进附录：附录G.n」，点进去就是那张表；
3. **附录F** 逐章说明"这一章的内容从哪来"。

`[n]` 的编号在全书中一致，同一编号在同一章里只标一次，避免刷屏。

## 仓库结构

```
.
├── docs/
│   ├── index.html            养猫手册（在线版，图片外链）
│   ├── dog.html              养狗手册（在线版，图片外链）
│   ├── 单文件离线版/           两份把图片内联进去的单文件 HTML
│   └── assets/
│       ├── illus/            本手册绘制的示意图
│       └── orig/             来自内容底本原文的实拍与插画
├── data/
│   ├── 宠物医院信息表.csv
│   └── 宠物医疗价格参考表.csv
└── tools/hb/                 生成脚本（内容模块 + 渲染引擎 + 构建管道）
```

## 重新生成

```bash
cd tools/hb
python build2.py            # 重新产出 docs/index.html 与 docs/dog.html
python build2.py report     # 只打印转换后的全部小节标题，用于人工复核
```

内容写在 `tools/hb/cat.py`（养猫）、`tools/hb/dog.py`（养狗）里，
是两个纯数据模块；`gen.py` 是渲染引擎，`provenance.py` 管来源与引用，
`neutralize.py` 负责把来源口径从正文里去掉。

## 免责声明

本手册内容基于公开权威资料整理（《默沙东兽医手册》、WSAVA 2024 疫苗指南、
AAHA 犬猫疫苗指南（2024 更新）、ACVIM 钩端螺旋体共识声明、中国兽医协会 CVMA 团体标准与指南、
GB/T 45295-2025 等国家标准、农业行业标准、ASPCA 及公开同行评议文献），
**仅作科普与决策辅助，不构成诊断或治疗建议**。任何健康问题请以执业兽医面诊结论为准。

医院地址、电话与价格随时变动，出行前请电话确认。

**兽医面诊 > 指南共识 > 本手册。**

## 贡献

发现数据错误、来源过时或表述有误，欢迎开 Issue。
本手册的核对原则是：**能溯源、可复核、分歧不隐瞒** —— 如果某一条与最新来源不一致，
请附上来源，我们会更新并记录进附录E。

## 许可

- 手册内容（`docs/`、`data/`）：**CC BY-NC-SA 4.0**
  —— 可自由转载、改编，需署名、非商业使用、以相同方式共享。
  完整法律文本见 <https://creativecommons.org/licenses/by-nc-sa/4.0/legalcode.zh-hans>。
- 生成脚本（`tools/`）：**MIT**。

部分插图源自内容底本公众号原文，版权归原作者所有，此处仅作科普引用；
如涉版权问题请联系删除。
'''

LICENSE = f'''本仓库采用双重许可：

1. 手册内容（docs/ 与 data/ 目录下的全部文件）
   —— 知识共享 署名-非商业性使用-相同方式共享 4.0 国际许可协议
      (Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International, CC BY-NC-SA 4.0)

   您可以自由地：
     · 共享 — 在任何媒介以任何形式复制、发行本作品
     · 演绎 — 修改、转换或以本作品为基础进行创作

   惟须遵守下列条件：
     · 署名 — 您必须给出适当的署名，提供指向本许可协议的链接，
              同时标明是否（对原始作品）作了修改。
     · 非商业性使用 — 您不得将本作品用于商业目的。
     · 相同方式共享 — 如果您再混合、转换或者基于本作品进行创作，
                    您必须基于与原先许可协议相同的许可协议分发您贡献的作品。

   完整法律文本：https://creativecommons.org/licenses/by-nc-sa/4.0/legalcode.zh-hans
   许可协议摘要：https://creativecommons.org/licenses/by-nc-sa/4.0/deed.zh-hans

2. 生成脚本（tools/ 目录下的全部文件）
   —— MIT License

   Permission is hereby granted, free of charge, to any person obtaining a copy
   of this software and associated documentation files (the "Software"), to deal
   in the Software without restriction, including without limitation the rights
   to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
   copies of the Software, and to permit persons to whom the Software is
   furnished to do so, subject to the following conditions:

   The above copyright notice and this permission notice shall be included in all
   copies or substantial portions of the Software.

   THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
   IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
   FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
   AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
   LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
   OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
   SOFTWARE.

3. 插图
   部分插图源自内容底本公众号原文，版权归原作者所有，此处仅作科普引用。
   如涉版权问题请联系删除。

Copyright (c) 2026 pet-handbook contributors
'''

GITIGNORE = '''.DS_Store
__pycache__/
*.pyc
.venv/
'''

GITATTR = '''* text=auto eol=lf
*.jpg binary
*.jpeg binary
*.png binary
*.gif binary
*.html -text
'''


def main():
    # 清理上次产物，但**绝不动 .git**（否则会把本地仓库连同未推送的提交一起删掉）
    if os.path.isdir(REPO):
        for name in os.listdir(REPO):
            if name == '.git':
                continue
            p = os.path.join(REPO, name)
            if os.path.isdir(p):
                shutil.rmtree(p)
            else:
                os.remove(p)
    os.makedirs(REPO, exist_ok=True)

    # 1) 图片
    imgs = used_images()
    n_illus = n_orig = 0
    for name in sorted(imgs):
        src = None
        if os.path.exists(os.path.join(gen.IMG_DIR, name)):
            src, sub = os.path.join(gen.IMG_DIR, name), 'illus'
        elif os.path.exists(os.path.join(gen.IMG_DIR2, name)):
            src, sub = os.path.join(gen.IMG_DIR2, name), 'orig'
        if not src:
            print('  !! 缺图', name)
            continue
        dst = os.path.join(REPO, 'docs', 'assets', sub, name)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copy2(src, dst)
        n_illus += sub == 'illus'
        n_orig += sub == 'orig'
    print(f'  图片 {len(imgs)} 个（示意图 {n_illus} / 原图 {n_orig}）')

    # 2) 单文件离线版
    for f in ('养猫手册-2026增订版.html', '养狗手册-2026版.html'):
        s = os.path.join(ROOT, '手册', f)
        if os.path.exists(s):
            d = os.path.join(REPO, 'docs', '单文件离线版', f)
            os.makedirs(os.path.dirname(d), exist_ok=True)
            shutil.copy2(s, d)
    print('  单文件离线版 2 份')

    # 3) 数据表
    for f in os.listdir(os.path.join(ROOT, '手册')):
        if f.endswith('.csv'):
            d = os.path.join(REPO, 'data', f)
            os.makedirs(os.path.dirname(d), exist_ok=True)
            shutil.copy2(os.path.join(ROOT, '手册', f), d)
    print('  CSV 数据表 2 份')

    # 4) 生成脚本
    tdst = os.path.join(REPO, 'tools', 'hb')
    os.makedirs(tdst, exist_ok=True)
    for f in sorted(os.listdir(HERE)):
        if f.endswith('.py'):
            shutil.copy2(os.path.join(HERE, f), os.path.join(tdst, f))
    print('  生成脚本', len([f for f in os.listdir(tdst) if f.endswith('.py')]), '个')

    # 5) 说明文件
    write(os.path.join(REPO, 'README.md'), README)
    write(os.path.join(REPO, 'LICENSE'), LICENSE)
    write(os.path.join(REPO, '.gitignore'), GITIGNORE)
    write(os.path.join(REPO, '.gitattributes'), GITATTR)
    write(os.path.join(REPO, 'docs', '.nojekyll'), '')
    print('  README / LICENSE / .gitignore / .gitattributes / docs/.nojekyll')

    # 6) 线上页：必须在 assets/ 与单文件离线版就绪之后再生成
    #    （build2 的外链版依赖这里的目录结构，所以由本脚本收尾，避免顺序踩坑）
    import build2
    print('◇ GitHub 版页面（图片外链）')
    build2.build_repo_pages()


if __name__ == '__main__':
    main()

# -*- coding: utf-8 -*-
"""补充原书配图：各章第二张图 + 第 1、25 章新增图组。"""
import re, os

BASE = os.path.dirname(os.path.abspath(__file__))
FP = os.path.join(BASE, 'cat.py')
s = open(FP, encoding='utf-8').read()

# A) 在指定已存在的 src 图之后，追加第二张
AFTER = {
 'src-raw.jpg': ('src-raw2.jpg',
   '**原书《生骨肉》篇实拍**：猫咪进食生肉。生骨肉的三大现实成本——'
   '**买肉、配比、更频繁驱虫**——原书讲得很直白：省事的是主食罐头与猫粮，不是生骨肉。'),
 'src-teeth.jpg': ('src-teeth2.jpg',
   '**同篇实拍**：猫咪口腔检查。原书提醒，牙结石高发于**后槽牙外侧**，'
   '主人自己在家很难看清，因此**每年一次的口腔检查**比"我觉得还行"可靠得多。'),
 'src-ac.jpg': ('src-ac2.jpg',
   '**同篇实拍**：猫咪蜷在金属盆里降温。猫靠**舔毛蒸发 + 寻找凉表面**散热，'
   '效率远低于犬的喘气散热。**短鼻猫（加菲等）、老龄猫、胖猫**是中暑高危群体。'),
 'src-bowl.jpg': ('src-bowl2.jpg',
   '**同篇实拍**：不同形态的猫碗陈列。原书对比了浅盘、深碗、抬高碗架的实际使用体验。'
   '本版据此给出结论：**猫更接受"浅、宽、稳"的碗**，抬高碗架对猫是加分项。'),
 'src-photo.jpg': ('src-photo2.jpg',
   '**同篇实拍**：户外环境下的猫。原书建议用**长焦 + 自然光 + 抓拍**，'
   '而不是把猫摆成固定姿势——猫一被摆弄就会失去"松弛感"，而这恰恰是好照片的关键。'),
 'src-shed.jpg': ('src-shed2.jpg',
   '**同篇实拍**：梳毛过程。原书建议**每天 5 分钟**胜过"掉毛了才猛梳一次"。'
   '工具上，**针梳去浮毛、排梳查毛结**，两把就够，不必买一整套。'),
 'src-plants.jpg': ('src-plants2.jpg',
   '**同篇实拍**：百合。这是**对猫毒性最强的常见观赏花之一**——'
   '全株有毒，**连花瓶里的水都含毒**。猫只要舔一口花粉或喝一口花瓶水，就可能急性肾衰。'
   '有猫家庭，**百合建议直接不买**。'),
}

for anchor, (fn, cap) in AFTER.items():
    pat = re.compile(r"\(\s*'fig',\s*'%s',.*?'原书配图'\),\n" % re.escape(anchor), re.S)
    m = pat.search(s)
    if not m:
        print('MISS after', anchor)
        continue
    ins = "('fig', '%s',\n                 '%s', '原书配图'),\n" % (fn, cap)
    s = s[:m.end()] + '                ' + ins + s[m.end():]
    print('AFTER', anchor, '->', fn)

# B) 第 1 章 / 第 25 章：新增图组
NEW = {
 'ch1': [("('fig', 'src-cat30.jpg',\n"
          "                 '**原书《新手养猫30问》篇插图**（Q16「出门几天，猫咪在家可不可以」与"
          "「要封窗吗」两问）。原书用的是统一的手绘猫形象，一问一图。'\n"
          "                 '这一篇的 30 问，本版在下面做了**权威口径校核**——"
          "凡是原书说得太绝对、或与兽医共识不一致的地方，都在对照表里标了出来。', '原书配图', 'tall'),"),
         ],
 'ch25': [("('figs', [('src-book.jpg', '《猫咪家庭医学大百科》', '原书推荐'),\n"
           "                          ('src-book2.jpg', '《猫病学》（Feline Patient 中文版）', '原书推荐')]),"),
          ],
}

for cid, blocks in NEW.items():
    pat = re.compile(r"('id': '%s', 'title': '[^']*', 'blocks': \[)\n" % cid)
    m = pat.search(s)
    if not m:
        print('MISS new', cid)
        continue
    ins = '\n                ' + blocks[0]
    s = s[:m.end()] + ins + s[m.end():]
    print('NEW', cid)

open(FP, 'w', encoding='utf-8').write(s)
print('done')

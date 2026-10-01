# -*- coding: utf-8 -*-
"""向 dog.py 的目标章节插入新生成的插图。"""
import re, os

BASE = os.path.dirname(os.path.abspath(__file__))
FP = os.path.join(BASE, 'dog.py')

FIGS = {
    'ch1':  ('dog-newbie.jpg',    '新手养狗：先把「体型、预算、时间」三笔账算清楚'),
    'ch2':  ('dog-behavior.jpg',  '犬的安定信号：读懂身体语言，比大声制止有效得多'),
    'ch3':  ('dog-puppy.jpg',     '幼犬到家：先给一个「小空间」，不要一上来就全屋放风'),
    'ch5':  ('dog-history.jpg',   '从篝火旁的狼，到沙发上的家人'),
    'ch7':  ('dog-raw.jpg',       '生骨肉与鲜食：配比对了才有意义，随便喂肉反而伤狗'),
    'ch8':  ('dog-treat.jpg',     '零食是训练货币，不是加餐'),
    'ch10': ('dog-neuter.jpg',    '绝育后的恢复期：防舔、限动、控体重，三件事都不能松'),
    'ch12': ('dog-vaccine.jpg',   '核心疫苗与非核心疫苗要分开算，狂犬在中国属强制免疫'),
    'ch13': ('dog-teeth.jpg',     '口腔护理：从每天一次刷牙开始，而不是等牙结石长满'),
    'ch16': ('dog-30days.jpg',    '幼犬到家 30 天：按周推进，别错过社会化窗口'),
    'ch22': ('dog-photo.jpg',     '给狗拍照：先让它放松，再按快门'),
    'ch23': ('dog-shedding.jpg',  '掉毛不是病，但梳毛的方式决定了你家的毛量'),
    'ch24': ('dog-toxic.jpg',     '这份黑名单，建议直接贴在冰箱门上'),
}

s = open(FP, encoding='utf-8').read()
n = 0
for cid, (fn, cap) in FIGS.items():
    pat = re.compile(r"('id': '%s', 'title': '[^']*', 'blocks': \[)" % cid)
    m = pat.search(s)
    if not m:
        print('MISS', cid)
        continue
    ins = m.group(1) + "\n                ('fig', '%s', '%s')," % (fn, cap)
    s = s[:m.start()] + ins + s[m.end():]
    n += 1
    print('OK', cid, fn)

open(FP, 'w', encoding='utf-8').write(s)
print('inserted', n)

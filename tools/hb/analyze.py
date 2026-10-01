# -*- coding: utf-8 -*-
"""分析两份手册的对照表 / 来源块结构。"""
import os, sys, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cat, dog

def walk(mod, label):
    print('=' * 70)
    print(label)
    print('=' * 70)
    for sec in mod.SECTIONS:
        for ch in sec['chapters']:
            B = ch['blocks']
            ft = [b for b in B if b[0] == 'ftable']
            src = [b for b in B if b[0] == 'src']
            notes = [b for b in B if b[0] == 'note' and '原书' in b[1]]
            h4s = [b[1] for b in B if b[0] == 'h4']
            last_h4 = h4s[-1] if h4s else ''
            print(f"\n--- ch{ch['no']} {ch['title']}")
            print(f"    h4 数 {len(h4s)} | 末位 h4: {last_h4}")
            print(f"    src 块 {len(src)} | ftable {len(ft)} | 原书note {len(notes)}")
            for b in ft:
                print(f"      ftable 表头: {b[1]}")
            for b in src:
                print(f"      src 标题: {b[1][:60]}")

walk(cat, 'CAT')
walk(dog, 'DOG')

# 统计所有含“原书”的文本片段
print('\n' + '=' * 70)
print('正文中含「原书」的文本片段（前 120 条）')
print('=' * 70)
cnt = 0
for mod, label in ((cat, 'CAT'), (dog, 'DOG')):
    def rec(o, path):
        global cnt
        if isinstance(o, str):
            if '原书' in o and cnt < 120:
                for m in re.finditer(r'.{0,18}原书.{0,18}', o):
                    print(f"[{label}] {m.group(0)}")
                    cnt += 1
        elif isinstance(o, (list, tuple)):
            for x in o:
                rec(x, path)
    rec(mod.SECTIONS, '')
print('总计片段:', cnt)

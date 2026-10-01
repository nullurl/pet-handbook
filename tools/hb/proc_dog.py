# -*- coding: utf-8 -*-
"""处理新生成的犬手册插图：裁掉右下角水印 + 统一尺寸 1200x731 + JPEG 压缩。"""
import os
from PIL import Image

BASE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(BASE, 'gen_raw')
DST = os.path.join(BASE, 'img')

MAP = {
    '07-55-18': 'dog-newbie',
    '07-55-39': 'dog-behavior',
    '07-55-59': 'dog-puppy',
    '07-56-18': 'dog-history',
    '07-56-38': 'dog-raw',
    '07-56-57': 'dog-treat',
    '07-57-14': 'dog-neuter',
    '07-57-32': 'dog-vaccine',
    '07-57-51': 'dog-teeth',
    '07-58-09': 'dog-30days',
    '07-58-26': 'dog-photo',
    '07-58-44': 'dog-shedding',
    '07-59-04': 'dog-toxic',
}

files = sorted(os.listdir(SRC))
for f in files:
    if not f.endswith('.png'):
        continue
    ts = f.split('T')[-1][:8].replace('-', '-')  # 07-55-18
    ts = ts[:8]
    key = None
    for k, v in MAP.items():
        if ts == k:
            key = v
            break
    if not key:
        print('skip', f)
        continue
    im = Image.open(os.path.join(SRC, f)).convert('RGB')
    w, h = im.size
    im = im.crop((0, 0, w, int(h * 0.915)))          # 去水印
    im = im.resize((1200, 731), Image.LANCZOS)
    out = os.path.join(DST, key + '.jpg')
    im.save(out, 'JPEG', quality=85, optimize=True)
    print(f'{f}  ->  {key}.jpg  {w}x{h} -> 1200x731  {os.path.getsize(out)//1024}KB')

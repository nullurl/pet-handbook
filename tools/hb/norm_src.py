# -*- coding: utf-8 -*-
"""把选中的原文图片标准化为 hb/img2/src-*.jpg（限宽、转 JPEG）。"""
import os
from PIL import Image

BASE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(BASE, 'img2')
OUT = os.path.join(BASE, 'img2')

# 原文文件 -> 规范名
PICK = {
    # 第 1 章 新手养猫30问
    'rQXoQUJJ0esfMZPx3X58qw-05.png': 'src-cat30.jpg',
    # 第 6 章 猫粮
    '_piVNX8GU9_UnOJkB4yRYg-08.png': 'src-food.jpg',
    # 第 7 章 生骨肉
    'NVgcMGWv9k63xiJYwbD1JA-04.png': 'src-raw.jpg',
    'NVgcMGWv9k63xiJYwbD1JA-00.png': 'src-raw2.jpg',
    # 第 13 章 牙结石
    'KxC5brtYpySiUwthPlWDUw-00.jpg': 'src-teeth.jpg',
    'KxC5brtYpySiUwthPlWDUw-01.jpg': 'src-teeth2.jpg',
    # 第 18 章 剪指甲
    'f2iU8w5mlY2SwVXYZIyhCw-00.png': 'src-nail.jpg',
    # 第 19 章 空调
    'qXnpk5pPhjB1UUYMQxtfdQ-00.png': 'src-ac.jpg',
    'qXnpk5pPhjB1UUYMQxtfdQ-01.jpg': 'src-ac2.jpg',
    # 第 20 章 托运
    'f4lgW_LBPehIeMF1u9zViA-00.png': 'src-express.jpg',
    # 第 21 章 猫粮碗
    'L5NR8EwY9tcrSVN1SXDmTQ-00.jpg': 'src-bowl.jpg',
    'L5NR8EwY9tcrSVN1SXDmTQ-09.jpg': 'src-bowl2.jpg',
    'L5NR8EwY9tcrSVN1SXDmTQ-08.png': 'src-bowl3.jpg',
    # 第 22 章 拍照
    'N1Yd97ffr8vuDeOUM1B2Qg-00.jpg': 'src-photo.jpg',
    'N1Yd97ffr8vuDeOUM1B2Qg-01.jpg': 'src-photo2.jpg',
    # 第 23 章 掉毛
    '4Bds60-nahOpmY4_iioKbw-00.png': 'src-shed.jpg',
    '4Bds60-nahOpmY4_iioKbw-01.jpg': 'src-shed2.jpg',
    # 第 24 章 植物
    'fBsbQmxnzql029-dYP70EA-00.jpg': 'src-plants.jpg',
    'fBsbQmxnzql029-dYP70EA-01.jpg': 'src-plants2.jpg',
    # 第 25 章 拓展阅读
    'NV-0bKp2k0isgBUiB91NcA-02.jpg': 'src-book.jpg',
    'NV-0bKp2k0isgBUiB91NcA-05.jpg': 'src-book2.jpg',
}

MAXW = 1100
for src_name, dst_name in PICK.items():
    p = os.path.join(SRC, src_name)
    if not os.path.exists(p):
        print('MISS', src_name)
        continue
    im = Image.open(p)
    if getattr(im, 'is_animated', False):
        im.seek(0)
    im = im.convert('RGB')
    w, h = im.size
    if w > MAXW:
        im = im.resize((MAXW, int(h * MAXW / w)), Image.LANCZOS)
    out = os.path.join(OUT, dst_name)
    im.save(out, 'JPEG', quality=86, optimize=True)
    print('%-34s -> %-20s %dx%d %dKB' % (src_name, dst_name, im.size[0], im.size[1],
                                         os.path.getsize(out) // 1024))

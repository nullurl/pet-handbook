# -*- coding: utf-8 -*-
"""等比缩放到固定画框内（不裁剪），生成 contact sheet。"""
import os, sys, glob
from PIL import Image, ImageDraw

BASE = os.path.dirname(os.path.abspath(__file__))
IMGDIR = os.path.join(BASE, 'img2')
OUT = os.path.join(BASE, 'contact')
os.makedirs(OUT, exist_ok=True)

BW, BH = 300, 460        # 每格画框
COLS = 6

keys = sys.argv[1:]
if not keys:
    print('need keys')
    sys.exit()

single = len(keys) == 1
for key in keys:
    files = sorted(glob.glob(os.path.join(IMGDIR, key + '-*')))
    if not files:
        print('no files', key)
        continue
    rows = (len(files) + COLS - 1) // COLS
    CW, CH = BW + 12, BH + 30
    sheet = Image.new('RGB', (min(COLS, len(files)) * CW, rows * CH), (243, 244, 246))
    d = ImageDraw.Draw(sheet, 'RGB')
    for i, f in enumerate(files):
        try:
            im = Image.open(f)
            if getattr(im, 'is_animated', False):
                im.seek(0)
            im = im.convert('RGB')
        except Exception:
            continue
        w, h = im.size
        s = min(BW / w, BH / h)
        im = im.resize((max(1, int(w * s)), max(1, int(h * s))), Image.LANCZOS)
        r, c = divmod(i, COLS)
        x, y = c * CW, r * CH
        sheet.paste(im, (x + (CW - im.size[0]) // 2, y + 24 + (BH - im.size[1]) // 2))
        d.text((x + 4, y + 6), os.path.basename(f).split('-')[-1] + '  %dx%d' % (w, h), fill=(15, 15, 15))
    outp = os.path.join(OUT, key + '.jpg')
    sheet.save(outp, 'JPEG', quality=80)
    print(outp, sheet.size, len(files))

# -*- coding: utf-8 -*-
"""驱动器：小批次串行抓取全部短链接，避免超时中断。"""
import subprocess, sys, os, time

BASE = os.path.dirname(os.path.abspath(__file__))
PY = '/Users/marvin/.workbuddy/binaries/python/versions/3.13.12/bin/python3'

URLS = [
    # 主合集
    'NSPuKqTRj9wMPq_9OWSGgw',
    # sup2 (第6~14章)
    '_piVNX8GU9_UnOJkB4yRYg', 'NVgcMGWv9k63xiJYwbD1JA', 'scoiglj7_e62w8FZ5og6qQ',
    'rq5jmd7JLKr-BoGz-q2Fig', 'YSro9Mp9bGhOexF8bS3O-Q', '_QfE0oT1bwF9jmLrtEPfjw',
    'Yw6we1yoGATUedcJOM0cqg', 'KxC5brtYpySiUwthPlWDUw', 'IuS7rOGdwLUBdmZMrgjErA',
    # sup4 (第15~25章)
    'GK32RZ_hgjIBIaf3maqMkA', 'YftlyP3X94jRBBfdb87Pcg', 'NZKgu6uv4onUuFZ4HhXZ9w',
    '5ag5JIe5diKAGFFlSIWEXQ', 'TBX1RoPPYJzZIWsnF0HXw', 'f2iU8w5mlY2SwVXYZIyhCw',
    'qXnpk5pPhjB1UUYMQxtfdQ', 'f4lgW_LBPehIeMF1u9zViA', 'L5NR8EwY9tcrSVN1SXDmTQ',
    'N1Yd97ffr8vuDeOUM1B2Qg', '4Bds60-nahOpmY4_iioKbw', 'fBsbQmxnzql029-dYP70EA',
    'NV-0bKp2k0isgBUiB91NcA',
    # 其他
    '_2kC-fXw7UjneZSrsC9CVQ', 'rQXoQUJJ0esfMZPx3X58qw',
]

B = 3  # 每批 3 篇
for i in range(0, len(URLS), B):
    batch = URLS[i:i + B]
    print(f"\n===== 批次 {i//B+1}: {i+1}~{i+len(batch)} =====", flush=True)
    subprocess.run([PY, os.path.join(BASE, 'harvest.py')] + batch,
                   cwd=BASE, timeout=600)
    time.sleep(1)
print("\n全部完成", flush=True)

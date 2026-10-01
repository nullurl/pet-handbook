# -*- coding: utf-8 -*-
"""批量抓取微信公众号文章：正文文本 + 原始图片 + 视频标记。
用法: python3 harvest.py <url1> <url2> ...
产出: raw/orig/{key}.html / raw/orig/{key}.json ; hb/img2/{key}-{i}.jpg
"""
import sys, os, re, json, subprocess, hashlib

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(BASE, 'raw', 'orig')
IMGDIR = os.path.join(BASE, 'hb', 'img2')
os.makedirs(RAW, exist_ok=True)
os.makedirs(IMGDIR, exist_ok=True)

UA = ("Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) "
      "AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 MicroMessenger/8.0.40")
REF = "https://mp.weixin.qq.com/"


def key_of(url):
    m = re.search(r'/s/([A-Za-z0-9_\-]+)', url)
    return m.group(1) if m else hashlib.md5(url.encode()).hexdigest()[:16]


def fetch(url):
    r = subprocess.run(['curl', '-sL', '-A', UA, url],
                       capture_output=True, timeout=90)
    return r.stdout.decode('utf-8', 'ignore')


def clean_img(u):
    u = u.replace('&amp;', '&')
    # 去掉尺寸后缀 /640 、/300 等，取原图尺寸 0
    u = re.sub(r'/640(\?|$)', '/640\\1', u)
    return u


def parse(html):
    title = ''
    m = re.search(r"var msg_title = '([^']*)'", html)
    if m:
        title = m.group(1)
    if not title:
        m = re.search(r'property="og:title" content="([^"]*)"', html)
        if m:
            title = m.group(1)

    # 定位正文容器
    body = html
    i = html.find('id="js_content"')
    if i < 0:
        i = html.find('id=js_content')
    if i >= 0:
        j = html.find('</div>', html.find('</div>', i))
        body = html[i:i + 900000]

    # 图片：data-src 优先
    imgs = re.findall(r'data-src="(https?://mmbiz\.qpic\.cn/[^"]+)"', body)
    if not imgs:
        imgs = re.findall(r'src="(https?://mmbiz\.qpic\.cn/[^"]+)"', body)
    seen, out = set(), []
    for u in imgs:
        u = clean_img(u)
        core = u.split('?')[0]
        if core in seen:
            continue
        seen.add(core)
        out.append(u)

    # 视频：video_iframe / mpvideo data-vid / wxv_
    vids = re.findall(r'data-vid="([^"]+)"', body)
    vids += re.findall(r'\b(wxv_[A-Za-z0-9]+)', body)
    vids = list(dict.fromkeys(vids))

    text = re.sub(r'<script[\s\S]*?</script>', '', body)
    text = re.sub(r'<style[\s\S]*?</style>', '', text)
    text = re.sub(r'<br\s*/?>', '\n', text)
    text = re.sub(r'</p>', '\n', text)
    text = re.sub(r'<[^>]+>', '', text)
    text = re.sub(r'&nbsp;', ' ', text)
    text = re.sub(r'&amp;', '&', text)
    text = re.sub(r'&quot;', '"', text)
    text = re.sub(r'\n{3,}', '\n\n', text).strip()
    return title, out, vids, text


def dl_img(url, path):
    r = subprocess.run(['curl', '-sL', '-A', UA, '-e', REF, url, '-o', path,
                        '-w', '%{http_code} %{size_download}'],
                       capture_output=True, timeout=60)
    try:
        code, size = r.stdout.decode().split()
        return int(code), int(size)
    except Exception:
        return 0, 0


def main(urls):
    report = []
    for url in urls:
        if not url.startswith('http'):
            url = 'https://mp.weixin.qq.com/s/' + url
        key = key_of(url)
        html = fetch(url)
        if len(html) < 5000:
            report.append({'key': key, 'url': url, 'err': 'fetch-too-small', 'n': len(html)})
            continue
        open(os.path.join(RAW, key + '.html'), 'w', encoding='utf-8').write(html)
        title, imgs, vids, text = parse(html)
        rec = {'key': key, 'url': url, 'title': title,
               'imgs': imgs, 'vids': vids, 'tlen': len(text)}
        # 下载图片
        saved = []
        for i, u in enumerate(imgs):
            ext = 'jpg'
            low = u.lower()
            if 'gif' in low:
                ext = 'gif'
            elif 'png' in low:
                ext = 'png'
            fn = f'{key}-{i:02d}.{ext}'
            fp = os.path.join(IMGDIR, fn)
            if not os.path.exists(fp):
                code, size = dl_img(u, fp)
                if code != 200 or size < 2000:
                    if os.path.exists(fp):
                        os.remove(fp)
                    continue
            saved.append(fn)
        rec['saved'] = saved
        open(os.path.join(RAW, key + '.json'), 'w', encoding='utf-8').write(
            json.dumps(rec, ensure_ascii=False, indent=1))
        report.append({'key': key, 'title': title, 'imgs': len(imgs),
                       'saved': len(saved), 'vids': len(vids), 'tlen': len(text)})
        print(f"  {key} | {title[:28]} | 图 {len(imgs)}→{len(saved)} | 视频 {len(vids)} | 文本 {len(text)}", flush=True)
    return report


if __name__ == '__main__':
    rep = main(sys.argv[1:])
    print(json.dumps(rep, ensure_ascii=False))

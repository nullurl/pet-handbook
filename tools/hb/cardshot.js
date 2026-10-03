// 把 cards.py 生成的卡片 HTML 批量截成 PNG。
//   node cardshot.js [indir] [outdir]
// 默认：/tmp/petcards → 手册/素材（源目录，由 mkrepo.py 收进仓库）
// 同时把每张卡的自适应结果打出来，字号压到下限仍溢出会标 OVERFLOW。

const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

(async () => {
  const inDir = process.argv[2] || '/tmp/petcards';
  const outDir = process.argv[3] ||
    path.resolve(__dirname, '..', '手册', '素材');
  fs.mkdirSync(outDir, { recursive: true });

  const list = JSON.parse(fs.readFileSync(path.join(inDir, 'manifest.json'), 'utf8'));
  const browser = await chromium.launch();
  const page = await browser.newPage({
    viewport: { width: 1080, height: 1440 },
    deviceScaleFactor: 2,
  });

  let bad = 0;
  for (const it of list) {
    await page.goto('file://' + it.html, { waitUntil: 'load' });
    await page.evaluate(async () => {
      await Promise.all([...document.images].map((im) =>
        im.complete ? null : new Promise((r) => { im.onload = im.onerror = r; })));
    });
    await page.waitForTimeout(220);
    const fit = await page.evaluate(() => window.__fit || null);
    await page.screenshot({ path: path.join(outDir, it.png) });
    const flag = !fit ? 'n/a' : (fit.ok ? 'ok' : 'OVERFLOW');
    if (flag === 'OVERFLOW') bad++;
    console.log(`${flag.padEnd(9)} ${it.png.padEnd(26)} 字号 ${fit ? fit.fs : '-'}` +
      (fit && !fit.ok ? `  需 ${fit.need}px / 可用 ${fit.box}px` : ''));
  }

  await browser.close();
  console.log(`\nPNG ${list.length} 张 → ${outDir}${bad ? `  溢出 ${bad} 张` : '  全部适配'}`);
  if (bad) process.exitCode = 2;
})();

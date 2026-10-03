const { chromium } = require('playwright');
const path = require('path');

(async () => {
  const file = process.argv[2];
  const targets = process.argv.slice(3);   // ch6 或 fig:血线
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
  await page.goto('file://' + path.resolve(file));
  await page.waitForTimeout(2500);
  await page.evaluate(() => { document.documentElement.style.scrollBehavior = 'auto'; });
  const base = path.basename(file, '.html');
  for (const t of targets) {
    let out = `/tmp/shot_${base}_${t.replace(/[:\u4e00-\u9fa5]/g, '_')}.png`;
    if (t.startsWith('sel:')) {
      const el = await page.$(t.slice(4));
      if (!el) { console.log('no selector', t); continue; }
      await el.scrollIntoViewIfNeeded();
      await page.waitForTimeout(1000);
      await page.screenshot({ path: out });
    } else if (t.startsWith('fig:')) {
      const txt = t.slice(4);
      const h = await page.evaluateHandle((txt) => {
        const caps = [...document.querySelectorAll('figcaption')];
        const c = caps.find(x => x.textContent.includes(txt));
        return c ? c.closest('figure') : null;
      }, txt);
      const el = h.asElement();
      if (!el) { console.log('no fig', txt); continue; }
      await el.scrollIntoViewIfNeeded();
      await page.waitForTimeout(1200);
      await el.screenshot({ path: out });
    } else {
      const el = await page.$('#' + t);
      if (!el) { console.log('no anchor', t); continue; }
      await el.scrollIntoViewIfNeeded();
      await page.evaluate(() => window.scrollBy(0, -40));
      await page.waitForTimeout(900);
      await page.screenshot({ path: out });
    }
    console.log(out);
  }
  await browser.close();
})();

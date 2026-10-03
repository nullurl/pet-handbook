// 把手册 HTML 打印成 A4 PDF。
//   node mkpdf.js <in.html> <out.pdf> [页脚文字]
// 说明：只认外链图版（docs/index.html、docs/dog.html），图片相对路径能就地解析。

const { chromium } = require('playwright');
const path = require('path');

(async () => {
  const [, , inFile, outFile, footerLabel = ''] = process.argv;
  if (!inFile || !outFile) {
    console.error('用法：node mkpdf.js <in.html> <out.pdf> [页脚文字]');
    process.exit(1);
  }

  const browser = await chromium.launch();
  const page = await browser.newPage();

  await page.goto('file://' + path.resolve(inFile), { waitUntil: 'load' });

  // 等图片就绪。正文里的图是 loading="lazy"，不先改成 eager 就永远不会触发 load，
  // 等待会一直挂着——这是首次尝试卡住的根因。
  await page.evaluate(async () => {
    document.querySelectorAll('img[loading="lazy"]').forEach((im) => { im.loading = 'eager'; });
    document.documentElement.style.scrollBehavior = 'auto';
    const all = Promise.all([...document.images].map((im) =>
      im.complete ? null : new Promise((r) => { im.onload = im.onerror = r; })));
    await Promise.race([all, new Promise((r) => setTimeout(r, 60000))]);   // 兜底：大不了不等待
  });
  await page.waitForTimeout(800);

  const footer = `
    <div style="width:100%; font-size:8px; color:#8a929c; padding:0 14mm;
                font-family:-apple-system,'PingFang SC',sans-serif;
                display:flex; justify-content:space-between;">
      <span>${footerLabel}</span>
      <span>第 <span class="pageNumber"></span> / <span class="totalPages"></span> 页</span>
    </div>`;

  // 左右留白交给 CSS 的 .body{padding:0 14mm}，这里只留页眉页脚高度
  await page.pdf({
    path: outFile,
    format: 'A4',
    printBackground: true,
    displayHeaderFooter: true,
    headerTemplate: '<span></span>',
    footerTemplate: footer,
    margin: { top: '14mm', bottom: '14mm', left: '0mm', right: '0mm' },
  });

  await browser.close();
  console.log(outFile);
})();

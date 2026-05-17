const { chromium } = require('playwright');
const fs = require('fs');

(async () => {
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext();
  const page = await context.newPage();

  try {
    console.log('Navigating to Taipei City Council schedule page...');
    await page.goto('https://www.tcc.gov.tw/DaySchedule.aspx?n=13516', { waitUntil: 'networkidle' });
    await page.waitForTimeout(2000);

    const youtubeUrl = await page.evaluate(() => {
      const anchors = Array.from(document.querySelectorAll('a[href]'));
      for (const a of anchors) {
        const href = a.href;
        if (href.includes('youtube.com/watch?v=') || href.includes('youtu.be/')) {
          return href;
        }
      }
      const iframes = Array.from(document.querySelectorAll('iframe[src]'));
      for (const iframe of iframes) {
        const src = iframe.src;
        if (src.includes('youtube.com/embed/') || src.includes('youtube.com/v/')) {
          return src;
        }
      }
      return null;
    });

    const outputPath = 'F:/2026/0514_AI_AGENT/youtube_url.txt';
    if (youtubeUrl) {
      fs.writeFileSync(outputPath, youtubeUrl.trim(), { encoding: 'utf8' });
      console.log(`YouTube URL written to ${outputPath}: ${youtubeUrl}`);
    } else {
      // Write empty string so downstream knows not found
      fs.writeFileSync(outputPath, '', { encoding: 'utf8' });
      console.log('No YouTube URL found on the page. youtube_url.txt set to empty.');
    }
  } catch (err) {
    console.error('Error during scraping:', err);
    fs.writeFileSync('F:/2026/0514_AI_AGENT/youtube_url.txt', '', { encoding: 'utf8' });
  } finally {
    await browser.close();
  }
})();
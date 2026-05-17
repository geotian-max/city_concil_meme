// fetch_youtube_id.js
// Uses Playwright to scrape the Taipei City Council schedule page for a YouTube URL
// Outputs the video ID to youtube_video_id.txt (or empty if not found)

const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext();
  const page = await context.newPage();

  try {
    console.log('Navigating to Taipei City Council schedule page...');
    await page.goto('https://www.tcc.gov.tw/DaySchedule.aspx?n=13516', { waitUntil: 'networkidle' });

    // Wait a bit for any dynamic content
    await page.waitForTimeout(2000);

    // Extract all anchors and iframes
    const youtubeUrl = await page.evaluate(() => {
      // Check anchors
      const anchors = Array.from(document.querySelectorAll('a[href]'));
      for (const a of anchors) {
        const href = a.href;
        if (href.includes('youtube.com/watch?v=') || href.includes('youtu.be/')) {
          return href;
        }
      }
      // Check iframes
      const iframes = Array.from(document.querySelectorAll('iframe[src]'));
      for (const iframe of iframes) {
        const src = iframe.src;
        if (src.includes('youtube.com/embed/') || src.includes('youtube.com/v/')) {
          return src;
        }
      }
      return null;
    });

    let videoId = '';
    if (youtubeUrl) {
      // Extract video ID
      if (youtubeUrl.includes('youtu.be/')) {
        videoId = youtubeUrl.split('youtu.be/')[1].split('?')[0];
      } else if (youtubeUrl.includes('youtube.com/watch?v=')) {
        videoId = youtubeUrl.split('youtube.com/watch?v=')[1].split('&')[0];
      } else if (youtubeUrl.includes('youtube.com/embed/')) {
        videoId = youtubeUrl.split('youtube.com/embed/')[1].split('?')[0];
      } else if (youtubeUrl.includes('youtube.com/v/')) {
        videoId = youtubeUrl.split('youtube.com/v/')[1].split('?')[0];
      }
      console.log(`Found YouTube URL: ${youtubeUrl}`);
      console.log(`Extracted video ID: ${videoId}`);
    } else {
      console.log('No YouTube URL found on the page.');
    }

    // Write video ID to file
    const fs = require('fs');
    const outputPath = 'F:/2026/0514_AI_AGENT/youtube_video_id.txt';
    fs.writeFileSync(outputPath, videoId, { encoding: 'utf8' });
    console.log(`Written video ID to ${outputPath}: "${videoId}"`);
  } catch (err) {
    console.error('Error during scraping:', err);
    // Write empty string on error so downstream knows
    const fs = require('fs');
    fs.writeFileSync('F:/2026/0514_AI_AGENT/youtube_video_id.txt', '', { encoding: 'utf8' });
  } finally {
    await browser.close();
  }
})();
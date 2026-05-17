from playwright.sync_api import sync_playwright
import re

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto("https://www.tcc.gov.tw/DaySchedule.aspx?n=13516", wait_until="networkidle")

    # Get all text content
    content = page.content()

    # Look for YouTube patterns
    youtube_patterns = [
        r'youtube\.com/watch\?v=([a-zA-Z0-9_-]+)',
        r'youtu\.be/([a-zA-Z0-9_-]+)',
        r'youtube\.com/embed/([a-zA-Z0-9_-]+)'
    ]

    found_urls = []
    for pattern in youtube_patterns:
        matches = re.findall(pattern, content)
        for match in matches:
            full_match = re.search(pattern, content)
            if full_match:
                found_urls.append(full_match.group(0))

    if found_urls:
        print("Found YouTube URLs:")
        for url in set(found_urls):  # deduplicate
            print(url)
    else:
        print("No YouTube URLs found in page content")

        # Let's also check for any iframe sources
        iframes = page.query_selector_all('iframe')
        print(f"\nFound {len(iframes)} iframes:")
        for iframe in iframes:
            src = iframe.get_attribute('src')
            if src:
                print(f"  iframe src: {src}")

        # Check for any links
        links = page.query_selector_all('a')
        print(f"\nFound {len(links)} links, checking first 10 for youtube:")
        for i, link in enumerate(links[:10]):
            href = link.get_attribute('href')
            if href and ('youtube' in href.lower() or 'yt' in href.lower()):
                print(f"  link {i}: {href}")

    browser.close()
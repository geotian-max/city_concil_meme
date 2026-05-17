#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Extract YouTube URLs from the Netscape bookmarks file and append to youtube_history.txt
with date (from ADD_DATE) and department inferred from title.
"""

import os
import re
from datetime import datetime

BOOKMARKS_FILE = r"/f/2026/0514_AI_AGENT/council_summaries/bookmarks_2026_5_15.html"
HISTORY_FILE = r"/f/2026/0514_AI_AGENT/youtube_history.txt"

def extract_from_line(line):
    # Find HREF
    href_match = re.search(r'HREF="([^"]+)"', line, re.IGNORECASE)
    if not href_match:
        return None, None, None
    url = href_match.group(1)
    # Check if it's a YouTube URL
    if 'youtube.com/watch?v=' not in url and 'youtu.be/' not in url:
        return None, None, None
    # Find ADD_DATE
    date_match = re.search(r'ADD_DATE="(\d+)"', line, re.IGNORECASE)
    if not date_match:
        timestamp = None
    else:
        timestamp = int(date_match.group(1))
    # Find title (between > and <)
    gt_pos = line.find('>')
    if gt_pos == -1:
        title = ''
    else:
        end_a = line.find('</A>', gt_pos)
        if end_a == -1:
            title = line[gt_pos+1:]
        else:
            title = line[gt_pos+1:end_a]
    return url, timestamp, title.strip()

def infer_department(title):
    title_lower = title.lower()
    # Look for keywords
    if '警政衛生' in title or '公安衛生' in title or '公共衛生' in title:
        return '警政衛生部門'
    if '議會' in title or '市議會' in title or '台北市議會' in title:
        # Try to find specific bureau
        bureaus = ['警察局', '衛生局', '消防局', '都市發展局', '財政局', '教育局', '交通局', '工務局', '地政局', '民政局', '社會局', '新聞局', '文化局', '觀光局', '體育局', '法務局', '研究發展考核委員會', '秘書處', '人事處', '會計處', '統計處']
        for bureau in bureaus:
            if bureau in title:
                return bureau + '部門' if not bureau.endswith('局') else bureau + '部門'
        return '台北市議會'
    return '未知部門'

def main():
    if not os.path.exists(BOOKMARKS_FILE):
        print(f"Bookmarks file not found: {BOOKMARKS_FILE}")
        return
    new_entries = []
    with open(BOOKMARKS_FILE, 'r', encoding='utf-8', errors='ignore') as f:
        for line in f:
            url, timestamp, title = extract_from_line(line)
            if url is None:
                continue
            if timestamp is None:
                date_str = datetime.now().strftime('%Y-%m-%d')
            else:
                try:
                    dt = datetime.fromtimestamp(timestamp)
                    date_str = dt.strftime('%Y-%m-%d')
                except Exception:
                    date_str = datetime.now().strftime('%Y-%m-%d')
            department = infer_department(title)
            new_entries.append((date_str, department, url))
    if not new_entries:
        print("No YouTube URLs found in bookmarks file.")
        return
    existing = set()
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    parts = line.split()
                    if len(parts) >= 3:
                        existing.add((parts[0], parts[1], ' '.join(parts[2:])))
    all_entries = list(existing) + new_entries
    seen = set()
    unique = []
    for date, dept, url in all_entries:
        key = (date, dept, url)
        if key not in seen:
            seen.add(key)
            unique.append((date, dept, url))
    unique.sort(key=lambda x: (x[0], x[1]))
    with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
        f.write('# YouTube URL History for Taipei City Council Meetings\n')
        f.write('# Format: DATE DEPARTMENT URL\n')
        f.write('# Sorted by date then department, duplicates removed\n')
        f.write('# Entries added automatically by extract_youtube_from_bookmarks.py\n')
        for date, dept, url in unique:
            f.write(f'{date} {dept} {url}\n')
    print(f'Added {len(new_entries)} new entries from bookmarks. Total unique entries: {len(unique)}')

if __name__ == '__main__':
    main()

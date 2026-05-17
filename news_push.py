#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys, os
os.environ['PYTHONIOENCODING'] = 'utf-8'
"""
每日抓取 松山信義 選舉相關新聞並透過 Telegram Bot 推播
使用方式：python news_push.py
排程：可使用 CronCreate 每日 08:00 執行
"""

import os
import json
import re
import time
from datetime import datetime, timezone, timedelta
import requests
import xml.etree.ElementTree as ET
from email.utils import parsedate_to_datetime

from dotenv import load_dotenv

# 載入環境變數
load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID   = os.getenv("TELEGRAM_CHAT_ID")

if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
    raise RuntimeError("請在 .env 中設定 TELEGRAM_BOT_TOKEN 與 TELEGRAM_CHAT_ID")

# Telegram Bot 相關函式（複用自 sync_calendar.py）
from telegram import Bot
from telegram.error import TelegramError
import asyncio

_telegram_bot = Bot(token=TELEGRAM_BOT_TOKEN)

async def _tg_notify_async(message: str) -> None:
    try:
        await _telegram_bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)
    except TelegramError as e:
        # 靜靜忽略，避免因通知失敗而中斷主流程
        pass

def tg_notify(message: str) -> None:
    try:
        asyncio.run(_tg_notify_async(message))
    except Exception:
        pass

def split_message(text: str, limit: int = 4090) -> list[str]:
    """簡單分段：不超過 limit，盡量在換行處斷斷"""
    if len(text) <= limit:
        return [text]
    parts = []
    start = 0
    while start < len(text):
        end = start + limit
        if end >= len(text):
            parts.append(text[start:])
            break
        # 盡量在最近的換行處斷斷
        newline = text.rfind('\n', start, end)
        if newline != -1 and newline > start:
            end = newline
        else:
            # 沒換行則在空白處斷斷
            space = text.rfind(' ', start, end)
            if space != -1 and space > start:
                end = space
        parts.append(text[start:end].strip())
        start = end
    return parts

def fetch_news_for_query(query: str, cutoff: datetime) -> list[dict]:
    """針對單一查詢透過 Google News RSS 抓取新聞，返回新聞項目列表，僅保留 cutoff 之後的新聞"""
    rss_url = f"https://news.google.com/rss/search?q={requests.utils.quote(query)}&hl=zh-TW&gl=TW&ceid=TW:zh-TW"
    try:
        resp = requests.get(rss_url, timeout=10)
        resp.raise_for_status()
    except Exception as e:
        print(f"[WARNING] 無法取得 RSS for '{query}': {e}")
        return []

    try:
        root = ET.fromstring(resp.content)
    except ET.ParseError as e:
        print(f"[WARNING] RSS 解析失敗 for '{query}': {e}")
        return []

    items = []
    for item in root.findall(".//item"):
        title_elem = item.find("title")
        link_elem  = item.find("link")
        pubdate_elem = item.find("pubDate")
        if title_elem is None or link_elem is None:
            continue
        title = title_elem.text.strip()
        link  = link_elem.text.strip()
        if not title:
            continue
        pub_date = None
        if pubdate_elem is not None and pubdate_elem.text:
            try:
                # parsedate_to_datetime returns a datetime with timezone if present
                pub_date = parsedate_to_datetime(pubdate_elem.text.strip())
                # Ensure it's timezone-aware UTC for comparison
                if pub_date.tzinfo is None:
                    pub_date = pub_date.replace(tzinfo=timezone.utc)
                else:
                    pub_date = pub_date.astimezone(timezone.utc)
            except Exception:
                # If parsing fails, we treat as unknown date and exclude to be safe
                pub_date = None
        # Include only if we have a valid date and it's within the last 3 months
        if pub_date is not None and pub_date >= cutoff:
            items.append({
                "title": title,
                "link": link
            })
    return items

def fetch_all_relevant_news() -> str:
    """抓取多種相關新聞：選舉、交通事故、一般新聞（松山信義區域），限制為最近三個月"""
    # 計算三個月前的截止時間（使用當前 UTC 時間）
    cutoff = datetime.now(timezone.utc) - timedelta(days=90)  # 約 3 個月
    # 定義要搜尋的查詢列表
    queries = [
        "松山信義 選舉",                           # 原有選舉新聞
        "松山區 交通事故",                         # 松山區交通事故
        "信義區 車禍",                             # 信義區車禍
        "松山區 新聞",                             # 松山區一般新聞
        "信義區 新聞"                              # 信義區一般新聞
    ]

    all_items = []
    seen_titles = set()

    for i, query in enumerate(queries):
        # 避免請求過於頻繁，加入小延遲（除了第一個查詢）
        if i > 0:
            time.sleep(0.5)

        items = fetch_news_for_query(query, cutoff)
        for item in items:
            # 以標題作為去重依據（連結有時可能會有參數差異但內容相同）
            if item["title"] not in seen_titles:
                seen_titles.add(item["title"])
                all_items.append(item)

    if not all_items:
        return "⚠️ 目前沒有找到相關新聞（最近三個月內）。"

    # 按照標題長度排序（較長的標題通常更具體），取前 10 條
    all_items.sort(key=lambda x: len(x["title"]), reverse=True)
    top_items = all_items[:10]

    today_str = datetime.now(timezone.utc).astimezone().strftime("%Y-%m-%d")
    lines = [f"松山信義區域相關新聞（選舉＋交通事故＋一般新聞）（{today_str}）\n"]

    for item in top_items:
        lines.append(f"- {item['title']}")
        lines.append(f"  {item['link']}")
        lines.append("")  # 空行

    return "\n".join(lines)

def main() -> None:
    print("[INFO] 開始抓取松山信義區域相關新聞（選舉＋交通事故＋一般新聞）...")
    news = fetch_all_relevant_news()
    print("[INFO] 抓取完成，準備推播...")
    chunks = split_message(news, limit=4090)
    for i, chunk in enumerate(chunks, start=1):
        header = f"（{i}/{len(chunks)}）\n" if len(chunks) > 1 else ""
        tg_notify(header + chunk)
    print("[INFO] 推播完成。")

if __name__ == '__main__':
    main()
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Google Calendar 同步腳本（每 3 小時執行一次增量同步）
使用方式：
    python sync_calendar.py
說明：
- 首次執行會進行完整同步並產生 token.json（請將此檔案加入 .gitignore）
- 後續執行會使用上次儲存的 syncToken 進行增量同步
- 若 syncToken 失效（410），腳本會自動回退到完整同步
- 同步結果會寫入 local_events.json（範例），您可自行替換為自己的資料庫或儲存方式
"""

import json
import os.path
import time
import uuid
from datetime import datetime, timezone
from dotenv import load_dotenv

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request

# Load environment variables from .env file
load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

from telegram import Bot
from telegram.error import TelegramError
import asyncio

_telegram_bot = Bot(token=TELEGRAM_BOT_TOKEN)

async def _tg_notify_async(message: str) -> None:
    """Send a notification via Telegram Bot (async version)."""
    try:
        await _telegram_bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)
    except TelegramError as e:
        # Silently ignore notification errors to avoid breaking the sync flow
        pass

def tg_notify(message: str) -> None:
    """Send a notification via Telegram Bot."""
    try:
        asyncio.run(_tg_notify_async(message))
    except Exception as e:
        # Silently ignore notification errors to avoid breaking the sync flow
        pass

# 若修改這些範圍，請刪除已儲存的 token.json
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']  # 僅讀取，若需寫入改為 .../calendar

# 儲存同步狀態的檔案（實際專案請改為資料庫）
STATE_FILE = 'calendar_sync_state.json'
LOCAL_EVENTS_FILE = 'local_events.json'  # 範例：將同步下來的事件寫入此檔案


def get_calendar_service():
    """取得已授權的 Google Calendar service 物件"""
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # 若沒有有效憑證或已過期，則進行 OAuth 流程
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'client_secret_91320162548-kqh5lguphct1q1dunp90viosppu5mk73.apps.googleusercontent.com.json',
                SCOPES)
            creds = flow.run_local_server(port=0)
        # 儲存下次使用的 token
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return build('calendar', 'v3', credentials=creds)


def load_state():
    """載入上次同步的 syncToken 與事件時間戳（若有）"""
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}


def save_state(state):
    """儲存同步狀態"""
    with open(STATE_FILE, 'w', encoding='utf-8') as f:
        json.dump(state, f, ensure_ascii=False, indent=2)


def load_local_events():
    """載入本地已儲存的事件（範例）"""
    if os.path.exists(LOCAL_EVENTS_FILE):
        with open(LOCAL_EVENTS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []


def save_local_events(events):
    """將事件寫入本地檔案（範例）"""
    with open(LOCAL_EVENTS_FILE, 'w', encoding='utf-8') as f:
        json.dump(events, f, ensure_ascii=False, indent=2)


def fetch_all_events(service, calendar_id='primary'):
    """取得全部事件（用於初次同步）"""
    events = []
    page_token = None
    while True:
        resp = service.events().list(
            calendarId=calendar_id,
            pageToken=page_token,
            showDeleted=False,
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        events.extend(resp.get('items', []))
        page_token = resp.get('nextPageToken')
        if not page_token:
            break
    return events


def fetch_incremental(service, sync_token, calendar_id='primary'):
    """使用 syncToken 取得變更的事件（增量同步）"""
    changed = []
    page_token = None
    while True:
        resp = service.events().list(
            calendarId=calendar_id,
            syncToken=sync_token,
            pageToken=page_token,
            showDeleted=True,   # 必须看删除的事件
            singleEvents=True
        ).execute()
        changed.extend(resp.get('items', []))
        page_token = resp.get('nextPageToken')
        if not page_token:
            break
    return changed, resp.get('nextSyncToken')


def sync_once():
    """執行一次同步（完整或增量）"""
    service = get_calendar_service()
    state = load_state()
    sync_token = state.get('syncToken')
    local_events = load_local_events()

    if not sync_token:
        print('[{}] 無同步紀錄，執行完整同步...'.format(datetime.now().isoformat()))
        events = fetch_all_events(service)
        # 取得此次完整同步後的 syncToken，以供下次增量使用
        resp = service.events().list(
            calendarId='primary',
            syncToken=None,
            showDeleted=False,
            singleEvents=True
        ).execute()
        new_sync_token = resp.get('nextSyncToken')
        print('[{}] 完成完整同步，取得 {} 筆事件。'.format(datetime.now().isoformat(), len(events)))
    else:
        print('[{}] 使用同步 token 進行增量同步...'.format(datetime.now().isoformat()))
        try:
            changed, new_sync_token = fetch_incremental(service, sync_token)
            # 这里简单示例：直接覆写本地事件（您可依据 event.status 或 'deleted' 自行做增删改）
            # 為了示範，我們重新取得全部事件再存檔（真實場景請自行實作增量合併）
            events = fetch_all_events(service)
            print('[{}] 增量同步取得變更 {} 筆，重新整理後共有 {} 筆事件。'
                  .format(datetime.now().isoformat(), len(changed), len(events)))
        except Exception as e:
            # 若 syncToken 失效（410），回到完整同步
            if 'syncToken' in str(e) or '410' in str(e):
                print('[{}] syncToken 失效 ({})，回退到完整同步。'.format(datetime.now().isoformat(), e))
                return sync_once()
            else:
                raise

    # 更新狀態與儲存事件
    state['syncToken'] = new_sync_token
    state['last_sync'] = datetime.now(timezone.utc).isoformat()
    save_state(state)
    save_local_events(events)
    print('[{}] 同步完成，事件已寫入 {}。'.format(datetime.now().isoformat(), LOCAL_EVENTS_FILE))
    # Send Telegram notification
    tg_notify('同步完成：{} 筆事件已儲存。'.format(len(events)))


def main():
    """主程式：無限循環，每 3 小時執行一次同步"""
    print('=== Google Calendar 同步腳本啟動 ===')
    while True:
        try:
            sync_once()
        except Exception as exc:
            print('[{}] 同步過程發生錯誤：{}'.format(datetime.now().isoformat(), exc))
        # 等待 3 小時 (3 * 60 * 60 秒)
        print('[{}] 等待 3 小時後進行下次同步...'.format(datetime.now().isoformat()))
        time.sleep(3 * 60 * 60)


if __name__ == '__main__':
    main()
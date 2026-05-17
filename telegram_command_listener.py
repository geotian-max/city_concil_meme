#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Telegram Command Listener for Claude Code
Listens for commands via Telegram and executes corresponding actions
"""

import os
import time
import json
import requests
from datetime import datetime

# Load environment variables from .env file
def load_env():
    env_path = r"F:\2026\0514_AI_AGENT\.env"
    if os.path.exists(env_path):
        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()

load_env()

# Telegram configuration
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
    raise ValueError("TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID must be set in .env")

# Import functions from existing scripts
import sys
sys.path.append(r'F:\2026\0514_AI_AGENT')

def send_telegram_message(chat_id, text):
    """Send message via Telegram Bot"""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        'chat_id': chat_id,
        'text': text,
        'parse_mode': 'HTML',
        'disable_web_page_preview': True
    }
    try:
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        result = response.json()
        if result.get('ok'):
            return True
        else:
            print(f"[ERROR] Telegram API returned error: {result}")
            return False
    except Exception as e:
        print(f"[ERROR] Failed to send Telegram message: {e}")
        return False

def get_telegram_updates(offset=None):
    """Get updates from Telegram Bot"""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getUpdates"
    params = {
        'timeout': 30,
        'offset': offset
    }
    try:
        response = requests.get(url, params=params, timeout=35)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"[ERROR] Failed to get Telegram updates: {e}")
        return {"ok": False, "result": []}

def run_stock_check_once():
    """Run a single stock check and return results"""
    try:
        # Import and run stock alert logic
        import stock_alert
        # We'll reuse the fetch_prices function but not the loop
        # For simplicity, let's just call the fetch and format
        import re

        STOCKS = ["2330.TW", "2308.TW", "2454.TW"]
        url = "https://mis.twse.com.tw/stock/api/getStockInfo.jsp"
        params = {"ex_ch": "|".join([s.replace(".TW", ".tw") for s in STOCKS])}
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        text = resp.text.strip()
        matches = re.findall(r'[\d]+\.[\d]+', text)

        prices = {}
        for i, sym in enumerate(STOCKS):
            if i < len(matches):
                prices[sym] = float(matches[i])

        if not prices:
            return "無法取得股價資料"

        result = "📈 股價檢查結果:\n"
        for sym, price in prices.items():
            result += f"{sym}: {price:.2f}\n"
        return result
    except Exception as e:
        return f"股價檢查失敗: {str(e)}"

def get_random_land_question():
    """Get a random land surveyor question"""
    try:
        from daily_land_surveyor import QUESTION_BANK, get_today_question, format_message
        import random
        # Get a random question (not necessarily today's)
        question_data = random.choice(QUESTION_BANK)
        return format_message(question_data)
    except Exception as e:
        return f"取得地政士題目失敗: {str(e)}"

def get_help_message():
    """Get help message with available commands"""
    return """🤖 可用指令列表:

/help - 顯示此說明
/stock - 立即檢查一次股票價格
/land - 發送一題隨機地政士考題
/status - 顯示系統狀態
/ping - 測試機器人是否在線

範例 usage:
傳送 /stock 來取得當前台股價格
傳送 /land 來取得一題地政士考題"""

def get_status_message():
    """Get system status message"""
    return f"""📊 系統狀態:
⏰ 時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
🤖 機器人: 正常運行
📡 聊天 ID: {TELEGRAM_CHAT_ID}
💼 服務: Telegram 指令監聽器運行中"""

def main():
    print("=" * 50)
    print("Telegram Command Listener for Claude Code")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)

    # Get the last update ID to avoid processing old messages
    updates = get_telegram_updates()
    if not updates.get("ok"):
        print("[ERROR] Failed to initialize Telegram connection")
        return 1

    # Get the latest update ID to start from
    last_update_id = 0
    if updates.get("result"):
        last_update_id = updates["result"][-1]["update_id"]

    print(f"[INFO] Starting from update ID: {last_update_id}")
    print("[INFO] Listening for Telegram commands... (Press Ctrl+C to stop)")

    try:
        while True:
            updates = get_telegram_updates(offset=last_update_id + 1)

            if updates.get("ok") and updates.get("result"):
                for update in updates["result"]:
                    last_update_id = update["update_id"]

                    if "message" in update and "text" in update["message"]:
                        message = update["message"]
                        chat_id = message["chat"]["id"]
                        text = message["text"].strip()

                        print(f"[INFO] Received message from {chat_id}: {text}")

                        # Process commands
                        if text.startswith('/'):
                            command = text.split()[0].lower()  # Get first word and make lowercase

                            response_text = ""
                            if command == '/help':
                                response_text = get_help_message()
                            elif command == '/stock':
                                response_text = "🔍 正在檢查股票價格...\n" + run_stock_check_once()
                            elif command == '/land':
                                response_text = get_random_land_question()
                            elif command == '/status':
                                response_text = get_status_message()
                            elif command == '/ping':
                                response_text = "🏓 Pong! 機器人正常運行中"
                            else:
                                response_text = f"❓ 未知指令: {command}\n輸入 /help 查看可用指令"

                            if response_text:
                                send_telegram_message(chat_id, response_text)
                                print(f"[INFO] Sent response to {chat_id}")

            # Sleep briefly to avoid excessive API calls
            time.sleep(1)

    except KeyboardInterrupt:
        print("\n[INFO] Stopping Telegram command listener...")
        return 0
    except Exception as e:
        print(f"[ERROR] Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit(main())

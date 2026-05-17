import requests
import time
import json
import os
import urllib.parse

# Configuration
TELEGRAM_TOKEN = "8459492130:AAGRuLttUM8-xqK2jX_7YAHl90pQ-VTMQNY"
TELEGRAM_CHAT_ID = "461158743"
STOCKS = ["2330.TW", "2308.TW", "2454.TW"]
LOW_THRESHOLD = 20.0   # price increase threshold for low alert (in same currency)
HIGH_THRESHOLD = 100.0 # price increase threshold for high alert (in same currency)
INTERVAL_SECONDS = 30 * 60  # 30 minutes
STATE_FILE = "stock_prices.json"

def fetch_prices():
    """Fetch latest prices from TWSE mis API."""
    url = "https://mis.twse.com.tw/stock/api/getStockInfo.jsp"
    params = {"ex_ch": "|".join([s.replace(".TW", ".tw") for s in STOCKS])}
    try:
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        text = resp.text.strip()
        # Expected format: "台積電 2330.tw – 2270.00 (6821 vol), 台達電 2308.tw – 2155.00 (624 vol), 聯發科 2454.tw – 3405.00 (584 vol)."
        # Extract numbers (float) after the dash and before space or parenthesis
        import re
        # Find all numbers with possible decimal
        matches = re.findall(r'[\d]+\.[\d]+', text)
        # The order should correspond to the order in ex_ch
        prices = {}
        for i, sym in enumerate(STOCKS):
            if i < len(matches):
                prices[sym] = float(matches[i])
            else:
                prices[sym] = None
        return prices
    except Exception as e:
        print(f"Error fetching prices: {e}")
        return {}

def load_state():
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_state(state):
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    params = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "HTML"
    }
    try:
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        print("Telegram message sent.")
    except Exception as e:
        print(f"Failed to send Telegram message: {e}")

def main():
    state = load_state()
    print("Starting stock price monitor...")
    while True:
        prices = fetch_prices()
        if not prices:
            print("No prices fetched, retrying after interval.")
            time.sleep(INTERVAL_SECONDS)
            continue
        for sym, price in prices.items():
            if price is None:
                continue
            prev_price = state.get(sym)
            if prev_price is not None:
                change = price - prev_price
                if change >= HIGH_THRESHOLD:
                    msg = f"<b>🔴 {sym} 價格大漲警訊 (高等級)</b>\n" \
                          f"目前價格: {price:.2f}\n" \
                          f"上次價格: {prev_price:.2f}\n" \
                          f"漲幅: {change:.2f} (≥ {HIGH_THRESHOLD})"
                    send_telegram(msg)
                    print(f"High alert sent for {sym}: change {change:.2f}")
                elif change >= LOW_THRESHOLD:
                    msg = f"<b>🟠 {sym} 價格上漲警訊 (低等級)</b>\n" \
                          f"目前價格: {price:.2f}\n" \
                          f"上次價格: {prev_price:.2f}\n" \
                          f"漲幅: {change:.2f} (≥ {LOW_THRESHOLD})"
                    send_telegram(msg)
                    print(f"Low alert sent for {sym}: change {change:.2f}")
            # update state
            state[sym] = price
        save_state(state)
        print(f"Checked prices at {time.strftime('%Y-%m-%d %H:%M:%S')}: {prices}")
        time.sleep(INTERVAL_SECONDS)

if __name__ == "__main__":
    main()
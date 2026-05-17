#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Daily Land Surveyor (地政士) Exam Question Push
Sends a question with explanation via Telegram Bot at noon daily
"""

import os
import random
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

# Question bank for land surveyor exam (台灣地政士考試)
QUESTION_BANK = [
    {
        "question": "根據土地法規定，土地所有權人對其所有之土地，有使用、收益及處分之權利，但應負擔什麼義務？",
        "explanation": "土地所有權人應負擔公共義務。根據土地法第25條規定：土地所有權人對其所有之土地，有使用、收益及處分之權利，但應負擔公共義務。這意味著土地使用必須符合公共利益，遵守都市計畫、建築法令等公共規範。"
    },
    {
        "question": "在土地登記事務中，何謂『標示變更登記』？其適用範圍為何？",
        "explanation": "標示變更登記係指土地之地目、等則或面積因自然力或人為力之變動而致其標示有變更時，所申請之登記。適用範圍包括：1. 地目變更（如田變為建築用地）2. 等則重編 3. 面積增加或減少（如河道變遷造成之嶁消或新生）4. 界限變更。依土地登記規則第76條規定辦理。"
    },
    {
        "question": "測量師執行基點測量時，應參考什麼標準來決定基點的等級與精度？",
        "explanation": "測量師執行基點測量時，應參考《基點測量規則》來決定基點的等級與精度。基點分為一、二、三、四等，一等基點精度最高，用作國家基礎測量之基礎；二等基點用於省（市）基礎測量；三等基點用於縣（市）基礎測量；四等基點用於鄉（鎮、市）基礎測量。精度標準包括平面位置誤差和高程誤差的容許值。"
    },
    {
        "question": "何謂『地役權』？其成立要件為何？",
        "explanation": "地役權是指為增強己。**之便利或利益，而在他人土地上設置之使用權或制約權。成立要件包括：1. 須有支配地與服務地之分離 2. 必须为了增强支配地的便利或利益 3. 必须以通常方法进行行使 4. 不得超过必要的程度 民法第834-844條有詳細規定。"
    },
    {
        "question": "執行土地分割測量時，應遵循何種原則來決定新界點的位置？",
        "explanation": "土地分割測量應遵循『原則上以原界點為基準』進行。具體來說：1. 優先使用原始界點（如石樁、鐵樁、混凝土樁等） 2. 若原界點消失或爭議，則應參照鄰近地積圖登記之界點 3. 必須確保分割後各宗土地之面積、形狀及使用符合都市計畫及相關法規 4. 新界點應設定於容易復測且不易損壞之處。依內政部土地測量規則相關規定辦理。"
    },
    {
        "question": "在都市計畫法規定中，何謂『特別專用區』？其設置目的為何？",
        "explanation": "特別專用區是都市計畫依土地使用性質之特別需要，而劃定之區域，以適合特定之土地使用。設置目的包括：1. 集中特定土地使用功能（如工業、倉儲、學術研究等） 2. 分離不相容之土地使用 3. 提高土地使用效率 4. 保護特定環境或資源。例如工業專用區、學術研究專用區、觀光專用區等。依都市計畫法第24條規定。"
    },
    {
        "question": "測量師在執行界線復測時，發現與鄰 neighbour 界線有爭議時，應如何處理？",
        "explanation": "界線復測時發生爭議時，測量師應：1. 先保持中立，不做利益判斷 2. 詳細復查地積圖、登記文件及歷史測量紀錄 3. 說明測量依據與可能誤差來源 4. 建議當事人進行協調或請求地政機構協調 5. 必要時可建議申請界線定標或訴訟解決 6. 在測量報告中明確註明爭議事項及處理建議。測量師職責是提供專業技術意見，而非裁決爭議。"
    },
    {
        "question": "何謂『地籍圖』？其製作依據與主要用途為何？",
        "explanation": "地籍圖是以土地為單位，以圖形方式表示土地之位置、界線、地號及其他相關資訊之圖表。製作依據包括：1. 地籍調查成果 2. 土地登記文件 3. 測量果效 4. 其他相關技術資料。主要用途：1. 作為土地權利關係之根據 2. 提供都市計畫及建築管理之依據 3. 協助土地開發與利用 4. 供徵稅、土地價格評估等行政作業使用 5. 為土地統計與研究之基礎資料。依土地法及地籍規則製作管理。"
    },
    {
        "question": "在使用全球定位系統（GPS）進行測量時，應注意哪些影響精度的因素？",
        "explanation": "GPS測量精度受多種因素影響：1. 衛星幾何強度（GDOP）：衛星分布越均勻，精度越高 2. 大氣層延進離子層與對流層 3. 多路徑效應：訊號反射後再接收 4. 衛星時鐘誤差 5. 接收器雜訊與天線特性 6. 遮蔽效應：建築物、樹木等阻擋衛星訊號 為提高精度，應選擇開闊視野良好之測站，使用差分GPS（DGPS）或實時運動學（RTK）技術，並觀測足夠期間進行靜態測量。"
    },
    {
        "question": "依不動產登記法規定，申請設定抵押權時，應檢附哪些主要文件？",
        "explanation": "申請設定抵押權時，應檢附以下文件：1. 不動產權利狀況證明書（最近三個月內核發） 2. 買賣契約或其他法律行為證明文件（如有必要） 3. 抵押權契約書（應載明債權額、利率、給付期限等重要事項） 4. 權利人身分證明文件 5. 其他依法令應檢附之文件（如公司設定則需董事會議議事錄）。抵押權契約應以公證書或私文書提出，並依不動產登記法第56條規定辦理登記。"
    }
]

def get_today_question():
    """Select a question for today based on date to ensure consistency"""
    today = datetime.now().date()
    # Use ordinal date to get a different question each day, cycling through the bank
    index = today.toordinal() % len(QUESTION_BANK)
    return QUESTION_BANK[index]

def format_message(question_data):
    """Format the question and explanation for Telegram message"""
    today_str = datetime.now().strftime("%Y-%m-%d (%A)")
    message = f"📚 每日地政士考題 ({today_str})\n"
    message += "=" * 30 + "\n\n"
    message += f"【題目】\n{question_data['question']}\n\n"
    message += f"【解答】\n{question_data['explanation']}\n\n"
    message += "=" * 30 + "\n"
    message += "💡 持續學習，逐日進步！"
    return message

def save_question_record(question_data, message):
    """Save the question to a daily record file"""
    output_dir = r"F:\2026\0514_AI_AGENT\daily_land_surveyor_records"
    os.makedirs(output_dir, exist_ok=True)
    today_str = datetime.now().strftime("%Y-%m-%d")
    filename = f"land_surveyor_question_{today_str}.txt"
    filepath = os.path.join(output_dir, filename)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(f"=== 土地政士考試每日一題 ===\n")
        f.write(f"日期：{datetime.now().strftime('%Y-%m-%d (%A)')}\n")
        f.write("=" * 50 + "\n\n")
        f.write(f"【題目】\n{question_data['question']}\n\n")
        f.write(f"【解答】\n{question_data['explanation']}\n\n")
        f.write("=" * 50 + "\n")
    return filepath

def send_telegram_message(message):
    """Send message via Telegram Bot"""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        'chat_id': TELEGRAM_CHAT_ID,
        'text': message,
        'parse_mode': 'HTML',  # Enable basic HTML formatting
        'disable_web_page_preview': True
    }
    try:
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        result = response.json()
        if result.get('ok'):
            print(f"[SUCCESS] Message sent to Telegram chat {TELEGRAM_CHAT_ID}")
            return True
        else:
            print(f"[ERROR] Telegram API returned error: {result}")
            return False
    except Exception as e:
        print(f"[ERROR] Failed to send Telegram message: {e}")
        return False

def main():
    print("=" * 50)
    print("Daily Land Surveyor Question Push")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)
    try:
        question_data = get_today_question()
        print(f"[INFO] Selected question: {question_data['question'][:50]}...")
        message = format_message(question_data)
        print(f"[INFO] Message formatted ({len(message)} characters)")
        record_file = save_question_record(question_data, message)
        print(f"[INFO] Record saved to: {record_file}")
        if send_telegram_message(message):
            print("[SUCCESS] Daily land surveyor question pushed via Telegram!")
        else:
            print("[ERROR] Failed to send Telegram message")
            return 1
    except Exception as e:
        print(f"[ERROR] Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    print("=" * 50)
    return 0

if __name__ == "__main__":
    exit(main())

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Combined daily push: 松山信義新聞 + 地政士每日一題
"""

import os
import sys
import traceback
from datetime import datetime

# Ensure UTF-8 output for Windows console
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

def run_news_push():
    """Run the news push script"""
    print("[INFO] Starting 松山信義新聞推播...")
    try:
        # Import and run news_push.main
        import news_push
        news_push.main()
        print("[INFO] 松山信義新聞推播完成")
        return True
    except Exception as e:
        print(f"[ERROR] 松山信義新聞推播失敗: {e}")
        traceback.print_exc()
        return False

def run_land_surveyor():
    """Run the land surveyor script"""
    print("[INFO] Starting 地政士每日一題推播...")
    try:
        # Import and run daily_land_surveyor.main
        import daily_land_surveyor
        daily_land_surveyor.main()
        print("[INFO] 地政士每日一題推播完成")
        return True
    except Exception as e:
        print(f"[ERROR] 地政士每日一題推播失敗: {e}")
        traceback.print_exc()
        return False

def main():
    print("=" * 60)
    print(f"Combined Daily Push - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    news_ok = run_news_push()
    print()
    land_ok = run_land_surveyor()

    print()
    print("=" * 60)
    if news_ok and land_ok:
        print("[INFO] All pushes completed successfully")
    else:
        print("[WARNING] Some pushes failed")
    print("=" * 60)

    return 0 if (news_ok and land_ok) else 1

if __name__ == "__main__":
    exit(main())

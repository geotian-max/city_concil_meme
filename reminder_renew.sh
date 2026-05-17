#!/bin/bash
LOG_FILE="F:/2026/0514_AI_AGENT/renew_reminder.log"
echo "[$(date)] REMINDER: The daily YouTube fetch and summary jobs will expire in 7 days. To renew them, please run the renewal commands or ask Claude to recreate the cron jobs." >> "$LOG_FILE"
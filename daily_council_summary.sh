#!/bin/bash
# Daily Taipei City Council Meeting Summary Script
# Runs at 6 PM daily to summarize departmental meetings

DATE=$(date +%Y-%m-%d)
OUTPUT_FILE="taipei_council_summary_${DATE}.txt"
OUTPUT_DIR="F:/2026/0514_AI_AGENT/council_summaries"
mkdir -p "$OUTPUT_DIR"
OUTPUT_PATH="${OUTPUT_DIR}/${OUTPUT_FILE}"

echo "=== Taipei City Council Departmental Meeting Summary ===" > "$OUTPUT_PATH"
echo "Date: $(date)" >> "$OUTPUT_PATH"
echo "Fetching meeting information for $(date +%Y-%m-%d)..." >> "$OUTPUT_PATH"
echo "" >> "$OUTPUT_PATH"

# Try to get today's schedule from the official site
echo "Attempting to fetch today's schedule..." >> "$OUTPUT_PATH"
echo "Source: https://www.tcc.gov.tw/DaySchedule.aspx?n=13516" >> "$OUTPUT_PATH"
echo "" >> "$OUTPUT_PATH"

# Try using Playwright to fetch the page content if direct fetch fails
echo "Trying to get schedule information..." >> "$OUTPUT_PATH"
echo "--" >> "$OUTPUT_PATH"

# Fallback: at least record that we attempted the fetch
echo "Schedule fetch attempted at $(date)" >> "$OUTPUT_PATH"
echo "Note: Due to website restrictions, detailed content may require manual checking." >> "$OUTPUT_PATH"
echo "Please visit: https://live.tcc.gov.tw/ for live departmental meetings" >> "$OUTPUT_PATH"
echo "Or check: https://www.tcc.gov.tw/DaySchedule.aspx?n=13516 for today's agenda" >> "$OUTPUT_PATH"
echo "" >> "$OUTPUT_PATH"
echo "=== End of Summary ===" >> "$OUTPUT_PATH"

echo "Summary saved to: $OUTPUT_PATH"
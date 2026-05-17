#!/bin/bash
# Daily Taipei City Council Meeting Summary Script - Version 2
# Runs at 6 PM daily to consolidate the YouTube transcript fetched at 2 PM

DATE=$(date +%Y-%m-%d)
OUTPUT_DIR="F:/2026/0514_AI_AGENT/council_summaries"
YOUTUBE_DIR="F:/2026/0514_AI_AGENT/youtube_transcripts"
mkdir -p "$OUTPUT_DIR"
mkdir -p "$YOUTUBE_DIR"

OUTPUT_FILE="taipei_council_transcript_${DATE}.txt"
OUTPUT_PATH="${OUTPUT_DIR}/${OUTPUT_FILE}"

echo "=== Taipei City Council Meeting Transcript (Date: $DATE) ===" > "$OUTPUT_PATH"

# Look for today's transcript file in youtube_transcripts/
# The fetch script names them: transcript_VIDEOID_YYYY-MM-DD.txt
TODAY_TRANSCRIPT=$(ls "$YOUTUBE_DIR"/transcript_*_${DATE}.txt 2>/dev/null | head -n 1)

if [ -n "$TODAY_TRANSCRIPT" ] && [ -f "$TODAY_TRANSCRIPT" ]; then
    echo "Found YouTube transcript for today. Copying content..." >> "$OUTPUT_PATH"
    echo "" >> "$OUTPUT_PATH"
    cat "$TODAY_TRANSCRIPT" >> "$OUTPUT_PATH"
    echo "" >> "$OUTPUT_PATH"
    echo "--- End of Transcript ---" >> "$OUTPUT_PATH"
else
    echo "No YouTube transcript found for today ($DATE)." >> "$OUTPUT_PATH"
    echo "" >> "$OUTPUT_PATH"
    echo "Fetch attempt was made at 2:00 PM. Possible reasons:" >> "$OUTPUT_PATH"
    echo "1. The YouTube URL was not provided in youtube_url.txt before 2 PM." >> "$OUTPUT_PATH"
    echo "2. The video does not have subtitles/transcript enabled." >> "$OUTPUT_PATH"
    echo "3. The video became private/hidden before the 2 PM fetch." >> "$OUTPUT_PATH"
    echo "" >> "$OUTPUT_PATH"
    echo "Please check:" >> "$OUTPUT_PATH"
    echo "- That youtube_url.txt contains the correct YouTube URL for today's meeting." >> "$OUTPUT_PATH"
    echo "- The youtube_transcripts/ directory for any error notes." >> "$OUTPUT_PATH"
    echo "" >> "$OUTPUT_PATH"
    echo "For reference, today's official schedule:" >> "$OUTPUT_PATH"
    echo "  Source: https://www.tcc.gov.tw/DaySchedule.aspx?n=13516" >> "$OUTPUT_PATH"
    echo "  Live stream: https://live.tcc.gov.tw/" >> "$OUTPUT_PATH"
    echo "" >> "$OUTPUT_PATH"
    echo "=== End of Summary ===" >> "$OUTPUT_PATH"
fi

echo "Summary saved to: $OUTPUT_PATH"
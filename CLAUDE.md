# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This repository is a personal automation and productivity toolkit containing:

- **Stock monitoring system** (`stock_alert.py`) - Tracks Taiwan stock prices and sends Telegram alerts for price movements
- **YouTube transcript tools** (`fetch_youtube_transcript.py`, `fetch_youtube_id.js`) - Extracts transcripts from YouTube videos
- **Council meeting processors** (`daily_council_summary.sh`, `council_summaries/`) - Processes Taipei City Council meeting transcripts and audio
- **Financial analysis plugins** - Claude Code plugins for financial services workflows
- **Utility scripts** - Various automation and information gathering tools

There is no unified build system or test framework as this is a collection of independent automation scripts.

## Key Components

### Stock Alert System
- `stock_alert.py` - Monitors Taiwan stocks (2330.TW, 2308.TW, 2454.TW) and sends Telegram alerts
- Configuration: Telegram bot token and chat ID stored in the script
- Alerts: Two-tier system (20??= low alert, 100??= high alert)
- Interval: Configurable checking interval (default 30 minutes)
- State tracking: Uses `stock_prices.json` to track previous prices

### YouTube Transcript Tools
- `fetch_youtube_transcript.py` - Python script to fetch YouTube transcripts
- `fetch_youtube_id.js` - Node.js script to extract YouTube video IDs
- Output: Transcripts saved to `youtube_transcripts/` directory with timestamps

### Council Meeting Processing
- `daily_council_summary.sh` / `daily_council_summary_v2.sh` - Scripts to process Taipei Council meetings
- Input: Audio files or transcripts
- Output: Summaries saved to `council_summaries/` directory
- Uses AI to generate concise meeting summaries

## Common Commands

Since this is a collection of independent scripts, there are no unified build/test commands. Common usage patterns include:

### Stock Monitoring
```bash
# Start the stock alert monitor
python stock_alert.py

# To run in background (Windows)
start /B pythonw stock_alert.py
```

### YouTube Transcripts
```bash
# Fetch transcript for a YouTube URL
python fetch_youtube_transcript.py "https://www.youtube.com/watch?v=VIDEO_ID"
```

### Council Meeting Processing
```bash
# Process council meeting audio/transcript
./daily_council_summary.sh [input_file]
```

### Financial Services Plugins
```bash
# List installed financial plugins
claude plugin list

# Get details on a specific plugin
claude plugin details financial-analysis
```

## Development Guidelines

### Adding New Scripts
1. Place new automation scripts in the repository root
2. Use descriptive names that indicate purpose
3. Include a brief comment header explaining the script's function
4. For Python scripts, consider adding a `requirements.txt` if dependencies are needed
5. For Node.js scripts, include a `package.json` if managing dependencies

### Configuration Management
- Avoid hardcoding sensitive information (API keys, tokens) in scripts
- Use environment variables or external configuration files when possible
- The `.claude` directory contains Claude Code configuration that should not be modified unless adjusting assistant behavior

### File Organization
- Transcripts and generated content go in appropriately named directories (`youtube_transcripts/`, `council_summaries/`)
- Temporary files should be cleaned up regularly
- Consider using `.gitignore` for sensitive or large generated files

## Plugin Ecosystem
This repository has the financial services plugin marketplace installed:
- Marketplace: `anthropics/financial-services-plugins` (available as `claude-for-financial-services`)
- Installed plugins: `financial-analysis`, `investment-banking`, `equity-research`, `private-equity`, `wealth-management`
- These plugins provide specialized skills for financial analysis workflows accessible via Claude Code commands
## Maintenance
- Scripts may require updates when external APIs change (e.g., YouTube, TWSE, Telegram)
- Monitor stock_alert.py for changes to the TWSE Mis API format
- YouTube tools may need updates if YouTube changes their page structure

## Language Preference
- Always respond in Chinese (Traditional) when interacting with the user
- All code comments, documentation, and output should be in Chinese


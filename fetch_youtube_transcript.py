#!/usr/bin/env python3
"""
Fetch YouTube transcript for a given URL provided in a file.
Usage: Place the YouTube URL in 'youtube_url.txt' in the same directory.
Run at 2 PM daily to get transcript before video becomes private/hidden.
"""

import os
import sys
from datetime import datetime
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter

def extract_video_id(url):
    """Extract YouTube video ID from various URL formats."""
    if not url:
        return None
    url = url.strip()
    if 'youtu.be/' in url:
        video_id = url.split('youtu.be/')[1].split('?')[0]
        return video_id
    if 'v=' in url:
        video_id = url.split('v=')[1].split('&')[0]
        return video_id
    if 'embed/' in url:
        video_id = url.split('embed/')[1].split('?')[0]
        return video_id
    if len(url) == 11 and all(c.isalnum() or c in ['-', '_'] for c in url):
        return url
    return None

def main():
    base_dir = r"F:\2026\0514_AI_AGENT"
    url_file = os.path.join(base_dir, "youtube_url.txt")
    output_dir = os.path.join(base_dir, "youtube_transcripts")
    os.makedirs(output_dir, exist_ok=True)

    if not os.path.exists(url_file):
        print(f"URL file not found: {url_file}")
        sys.exit(1)

    with open(url_file, 'r', encoding='utf-8') as f:
        url = f.read().strip()

    if not url:
        print("URL file is empty.")
        sys.exit(1)

    video_id = extract_video_id(url)
    if not video_id:
        print(f"Could not extract video ID from URL: {url}")
        sys.exit(1)

    print(f"Processing video ID: {video_id}")

    try:
        ytt_api = YouTubeTranscriptApi()
        # Try to get transcript; fetch can take language list
        transcript_data = ytt_api.fetch(video_id, languages=['en'])
    except Exception as e:
        print(f"Error fetching transcript: {e}")
        # Try without language
        try:
            ytt_api = YouTubeTranscriptApi()
            transcript_data = ytt_api.fetch(video_id)
        except Exception as e2:
            print(f"Failed again: {e2}")
            date_str = datetime.now().strftime("%Y-%m-%d")
            output_file = os.path.join(output_dir, f"transcript_{video_id}_{date_str}.txt")
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(f"No transcript available for YouTube video: {url}\n")
                f.write(f"Reason: {e2}\n")
            print(f"Created note file: {output_file}")
            return

    formatter = TextFormatter()
    text_formatted = formatter.format_transcript(transcript_data)

    date_str = datetime.now().strftime("%Y-%m-%d")
    output_file = os.path.join(output_dir, f"transcript_{video_id}_{date_str}.txt")
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(text_formatted)

    print(f"Transcript saved to: {output_file}")
    print(f"Length: {len(text_formatted)} characters")

if __name__ == "__main__":
    main()
import sqlite3, os, re, glob, json
from pathlib import Path

DB_PATH   = "data/council.db"
JSON_PATH = "data/index.json"
TRANS_DIR = "transcripts"  # folder where .vtt files will be placed

def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("DROP TABLE IF EXISTS fts_transcript")
    cur.execute("""
        CREATE VIRTUAL TABLE fts_transcript
        USING fts5(
            vid,
            start_time,
            end_time,
            text
        )
    """)
    conn.commit()
    return conn

def parse_vtt(vtt_path):
    """Very simple VTT parser -> list of (start, end, text)"""
    with open(vtt_path, encoding="utf-8-sig") as f:
        lines = f.readlines()
    i = 0
    results = []
    while i < len(lines):
        line = lines[i].strip()
        if re.match(r"\d{2}:\d{2}:\d{2}\.\d{3} --> \d{2}:\d{2}:\d{2}\.\d{3}", line):
            times = line.split(" --> ")
            # convert HH:MM:SS.mmm to seconds
            def to_sec(t):
                h, m, s = t.split(':')
                return int(h)*3600 + int(m)*60 + float(s)
            start = to_sec(times[0])
            end   = to_sec(times[1])
            i += 1
            text_lines = []
            while i < len(lines) and lines[i].strip() and not re.match(r"\d{2}:\d{2}:\d{2}\.\d{3}", lines[i]):
                text_lines.append(lines[i].strip())
                i += 1
            text = " ".join(text_lines)
            results.append((start, end, text))
        else:
            i += 1
    return results

def main():
    # ensure transcripts directory exists
    os.makedirs(TRANS_DIR, exist_ok=True)
    os.makedirs(os.path.dirname(JSON_PATH), exist_ok=True)
    conn = init_db()
    cur = conn.cursor()
    all_records = []  # for JSON export
    for vtt_file in glob.glob(os.path.join(TRANS_DIR, "*.vtt")):
        vid = Path(vtt_file).stem
        entries = parse_vtt(vtt_file)
        for st, et, txt in entries:
            cur.execute(
                "INSERT INTO fts_transcript(vid, start_time, end_time, text) VALUES (?,?,?,?)",
                (vid, st, et, txt)
            )
            all_records.append({
                "vid": vid,
                "start": st,
                "end":   et,
                "text":  txt
            })
    conn.commit()
    conn.close()
    # Write JSON
    with open(JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(all_records, f, ensure_ascii=False, indent=2)
    print(f"Index built: {len(all_records)} subtitle entries -> {JSON_PATH}")

if __name__ == "__main__":
    main()

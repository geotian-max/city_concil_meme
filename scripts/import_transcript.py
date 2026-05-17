import json, sqlite3, pathlib, os
AUDIO_ROOT = r"F:\2026\0517CITY_CONCIL_ME\audio"
DB_PATH    = r"F:\2026\0517CITY_CONCIL_ME\data\council.db"
def init_db(conn):
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS sentences (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        video_id TEXT NOT NULL,
        seq INTEGER NOT NULL,
        text TEXT NOT NULL,
        start_sec REAL NOT NULL,
        end_sec REAL NOT NULL,
        UNIQUE(video_id, seq)
    );
    """)
    cur.execute("""
    CREATE VIRTUAL TABLE IF NOT EXISTS sentences_fts USING fts5(
        text,
        content='sentences',
        content_rowid='id'
    );
    """)
    cur.execute("""CREATE TRIGGER IF NOT EXISTS sentences_ai AFTER INSERT ON sentences BEGIN
        INSERT INTO sentences_fts(rowid, text) VALUES (new.id, new.text);
    END;""")
    cur.execute("""CREATE TRIGGER IF NOT EXISTS sentences_ad AFTER DELETE ON sentences BEGIN
        INSERT INTO sentences_fts(sentences_fts, rowid, text) VALUES('delete', old.id, old.text);
    END;""")
    cur.execute("""CREATE TRIGGER IF NOT EXISTS sentences_au AFTER UPDATE ON sentences BEGIN
        INSERT INTO sentences_fts(sentences_fts, rowid, text) VALUES('delete', old.id, old.text);
        INSERT INTO sentences_fts(rowid, text) VALUES (new.id, new.text);
    END;""")
    conn.commit()
def import_json(json_path):
    video_id = json_path.stem
    with json_path.open(encoding="utf-8") as f:
        data = json.load(f)
    segments = data.get("segments", [])
    if not segments:
        print(f"[WARN] {json_path.name} no segments")
        return 0
    conn = sqlite3.connect(DB_PATH)
    init_db(conn)
    cur = conn.cursor()
    inserted = 0
    for i, seg in enumerate(segments):
        text = seg.get("text", "").strip()
        start = float(seg.get("start", 0))
        end   = float(seg.get("end", 0))
        cur.execute("""INSERT OR REPLACE INTO sentences
            (video_id, seq, text, start_sec, end_sec)
            VALUES (?, ?, ?, ?, ?)""", (video_id, i, text, start, end))
        inserted += 1
    conn.commit()
    conn.close()
    print(f"[OK] {json_path.name}: inserted {inserted} sentences")
    return inserted
def main():
    audio_dir = pathlib.Path(AUDIO_ROOT)
    json_files = list(audio_dir.glob("*.json"))
    if not json_files:
        print("[INFO] No JSON files to import")
        return
    total = 0
    for jf in json_files:
        total += import_json(jf)
    print(f"[DONE] Total inserted {total} sentences")
if __name__ == "__main__":
    main()

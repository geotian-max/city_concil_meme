import sqlite3, pathlib
DB = pathlib.Path("data/council.db")
conn = sqlite3.connect(DB)
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
conn.close()
print("Database and FTS5 index created")

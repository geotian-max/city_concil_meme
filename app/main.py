from fastapi import FastAPI, Query
from typing import List, Dict, Optional
import sqlite3

app = FastAPI(title="臺北市議會聲音影像搜尋 API")
DB_PATH = r"F:\2026\0517CITY_CONCIL_ME\data\council.db"

def get_conn():
    return sqlite3.connect(DB_PATH)

@app.get("/search")
def search(
    q: str = Query(..., description="中文關鍵字，可使用空格分隔多個詞，會被當作 AND 運算"),
    date: Optional[str] = Query(None, description="過濾日期 (YYYY-MM-DD)，例如 2026-05-14"),
    limit: int = Query(20, le=100, description="回傳筆數上限")
):
    conn = get_conn()
    cur = conn.cursor()
    fts_query = q.strip()
    if date:
        date_prefix = date.replace("-", "")
        sql = """
            SELECT s.video_id, s.text, s.start_sec, s.end_sec
            FROM sentences s
            JOIN sentences_fts f ON s.id = f.rowid
            WHERE f.text MATCH ?
              AND s.video_id LIKE ?
            ORDER BY s.rank
            LIMIT ?
        """
        params = [fts_query, f"council_{date_prefix}%", limit]
    else:
        sql = """
            SELECT s.video_id, s.text, s.start_sec, s.end_sec
            FROM sentences s
            JOIN sentences_fts f ON s.id = f.rowid
            WHERE f.text MATCH ?
            ORDER BY s.rank
            LIMIT ?
        """
        params = [fts_query, limit]
    cur.execute(sql, params)
    rows = cur.fetchall()
    conn.close()
    results = [
        {
            "video_id": r[0],
            "snippet": (r[1] or "").replace("\n", " ").strip()[:120],
            "start": round(float(r[2]), 2),
            "end": round(float(r[3]), 2),
        }
        for r in rows
    ]
    return {"query": q, "date": date, "count": len(results), "results": results}

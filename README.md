● 本專案是一個台北市議會聲音＋影像搜尋平台，利用 ffmpeg 抓取議會直播或 YouTube 影片、Whisper
  轉錄帶時間戳的逐字稿，將結果存入 SQLite + FTS5 全文索引，並透過 FastAPI 提供搜尋
  API。前端可關鍵字搜尋並點擊片段直接跳至對應時間播放，支援週一至週五自動排程抓取與更新。n
  Perfect for:
  - Public company valuation (M&A, investment analysis)
  - Benchmarking performance vs. industry peers
  - Pricing IPOs or funding rounds
  - Identifying valuation outliers (over/under-valued)
  - Supporting investment committee presentations
  - Creating sector overview reports

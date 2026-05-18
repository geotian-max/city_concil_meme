# 台北市議會 Meme 網站維護說明

## 目的
維護台北市議會 Meme 搜尋網站的內容更新流程，包括自動或手動抓取字幕、建立索引、更新 GitHub Pages。

## 更新頻率
- 每週一至週五 13:00~18:00（台北時間）自動執行字幕抓取（若使用 GitHub Actions）。
- 亦可手動執行以下步驟來更新內容。

## 步驟

### 1. 取得 YouTube 直播字幕
```bash
# 安裝 yt-dlp（若尚未安裝）
pip install yt-dlp

# 下載自動產生的中文字幕（若當時可用）
yt-dlp --skip-download --write-auto-sub --sub-lang zh-TW -o "transcripts/%(id)s.%(ext)s" "https://www.youtube.com/watch?v=ENXhEMk0504"
```
- 若當時無自動字幕，請改用已上傳之完整影片或改用市議會官網提供之逐字稿。
- 字幕檔將存放於 `transcripts/` 目錄，檔名格式為 `ENXhEMk0504.vtt`（或 `.srt`）。

### 2. 建立搜尋索引
```bash
# 確保 build_index.py 在專案根目錄
python build_index.py
```
- 此腳本會讀取 `transcripts/` 目錄下的所有 `.vtt` 檔，產生 SQLite FTS5 資料庫 (`data/council.db`) 與 JSON 索引 (`data/index.json`)。
- JSON 索引即為前端靜態模式使用的資料。

### 3. 更新 GitHub Pages (gh-pages 分支)
```bash
# 確認目前在 gh-pages 分支
git checkout gh-pages

# 添加或更新以下檔案：
#   - data/index.json (必要)
#   - (可選) transcripts/ 下的新字幕檔
git add data/index.json
# 若想同時保存字幕檔：
# git add transcripts/

# 提交變更
git commit -m "update: 重建字幕索引 $(date +%Y-%m-%d)"

# 推送至遠端
git push origin gh-pages
```

### 4. 驗證 GitHub Pages 設定
1. 前往 GitHub 倉庫的 **Settings** → **Pages**。
2. 確認 **Source** 設定為：
   - Branch: `gh-pages`
   - Folder: `/ (root)`
3. 若無法見到更新，請等待幾分鐘或強制刷新瀏覽器 cache。

### 5. 故障排除
- **字幕抓取失敗**：YouTube 直播進行中可能尚未產生自動字幕，請稍後再試或使用已上傳之重播。
- **索引建立失敗**：檢查 `transcripts/` 目錄是否有有效的 `.vtt` 檔，並確認 `build_index.py` 無語法錯誤。
- **Pages 未更新**：確認已推送至 `gh-pages` 分支且 Pages 來源正確設定。

## 自動化方案（可選）
可於 GitHub Actions 新增工作流程 `.github/workflows/subtitles.yml`，使用 `cron` trigger 每週一至週五 13:00 UTC（對應台北時間 21:00）執行上述步驟。

---  
維護人員請依照實際狀況調整步驟，並將重大變更記錄於此檔案。

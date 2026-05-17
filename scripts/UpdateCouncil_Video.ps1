# Updated UpdateCouncil_Video.ps1
# Tries to get Taipei Council live stream via schedule page, fallback to YouTube, then HLS.

# ---- 參數區 -------------------------------------------------
$scheduleUrl   = "https://www.tcc.gov.tw/DaySchedule.aspx?n=13516"
$hlsUrl        = "https://live.tcc.gov.tw/hls/channel1.m3u8"
$outputRoot    = "F:\2026\0517CITY_CONCIL_ME\media"
$audioRoot     = "F:\2026\0517CITY_CONCIL_ME\audio"
$segmentLen    = 300                                          # 每片長度秒 (5 分鐘)
$ffmpeg        = "F:\2026\0517CITY_CONCIL_ME\ffmpeg.exe"
$ytDlp         = "yt-dlp"                                     # assume in PATH
$whisperExe    = "python"                                     # calling python -m whisper
$whisperModel  = "base"
$logFile       = "F:\2026\0517CITY_CONCIL_ME\logs\update.log"
# ------------------------------------------------------------

function Write-Log($msg){
    $ts = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    "$ts $msg" | Out-File -FilePath $logFile -Append -Encoding utf8
}

function Get-YoutubeIdFromSchedule{
    param([string]$html)
    # Look for YouTube URL patterns
    if ($html -match 'https?:\/\/(www\.)?youtube\.com\/watch\?v=([^\s&\'"">]+)') {
        return $matches[2]
    }
    if ($html -match 'youtu\.be\/([^\s&\'"">]+)') {
        return $matches[1]
    }
    return $null
}

function Get-HlsUrlFromSchedule{
    param([string]$html)
    if ($html -match 'https?:\/\/[^\s&\'""]+\.m3u8') {
        return $matches[0]
    }
    return $null
}

# 1️⃣ 取得目前時間戳，用於命名檔案 (YYYYMMDD_HHMM)
$timestamp = Get-Date -Format "yyyyMMdd_HHmm"
$videoFile = Join-Path $outputRoot "council_${timestamp}.mp4"
$audioFile = Join-Path $audioRoot  "council_${timestamp}.mp3"

Write-Log "開始抓取會議內容..."

# 2️⃣ 嘗試取得排程頁面
try {
    $scheduleHtml = Invoke-WebRequest -Uri $scheduleUrl -UseBasicParsing -ErrorAction Stop
    $htmlContent = $scheduleHtml.Content
    Write-Log "成功取得排程頁面。"
}
catch {
    Write-Log "警告：無法取得排程頁面 ($_)"
    $htmlContent = $null
}

$videoSource = $null
$sourceType = $null

if ($htmlContent) {
    # 嘗試從排程頁面取得 YouTube 連結
    $ytId = Get-YoutubeIdFromSchedule -html $htmlContent
    if ($ytId) {
        $videoSource = "https://www.youtube.com/watch?v=$ytId"
        $sourceType = "youtube"
        Write-Log "在排程頁面偵測到 YouTube 影片：$videoSource"
    }
    else {
        # 嘗試取得 HLS 連結
        $m3u8 = Get-HlsUrlFromSchedule -html $htmlContent
        if ($m3u8) {
            $videoSource = $m3u8
            $sourceType = "hls"
            Write-Log "在排程頁面偵測到 HLS 串流：$videoSource"
        }
    }
}

# 若仍未取得來源，則依序嘗試備用來源
if (-not $videoSource) {
    Write-Log "排程頁面未提供可用連結，嘗試備用來源..."
    # 先試 YouTube 今日可能的直播 (假設有固定頻道名稱，此處暫時跳過)
    # 直接嘗試 HLS
    try {
        $test = Invoke-WebRequest -Uri $hlsUrl -Method Head -ErrorAction Stop -TimeoutSec 5
        if ($test.StatusCode -eq 200) {
            $videoSource = $hlsUrl
            $sourceType = "hls"
            Write-Log "直接 HLS 可用：$videoSource"
        }
    }
    catch {
        Write-Log "直接 HLS 也不可用。"
    }
}

if (-not $videoSource) {
    Write-Log "錯誤：找不到可用的影片來源（排程頁面、YouTube、HLS 均失敗）。"
    exit 1
}

# 3️⃣ 依來源類型處理
switch ($sourceType) {
    "youtube" {
        Write-Log "正在下載 YouTube 影片：$videoSource"
        & $ytDlp -f "bestvideo[height<=720]+bestaudio/best[height<=720]" --no-part -o "$videoFile" "$videoSource"
        if ($LASTEXITCODE -ne 0){
            Write-Log "錯誤：yt-dlp 下載失敗 (exit $LASTEXITCODE)"
            exit 1
        }
        Write-Log "YouTube 影片已下載：$videoFile"
        # 同時抽出音訊給 Whisper
        & $ffmpeg -hide_banner -loglevel error -i "$videoFile" -vn -acodec libmp3lame -b:a 128k "$audioFile"
        if ($LASTEXITCODE -ne 0){
            Write-Log "錯誤：萃取音訊失敗"
            exit 1
        }
        Write-Log "音訊已萃取：$audioFile"
    }
    "hls" {
        Write-Log "正在抓取 HLS 串流：$videoSource"
        & $ffmpeg -hide_banner -loglevel error -i "$videoSource" -t 01:00:00 `
            -vf "scale=-2:720" -c:v libx265 -preset veryfast -crf 28 `
            -c:a aac -b:a 128k -f mp4 "$videoFile"
        if ($LASTEXITCODE -ne 0){
            Write-Log "錯誤：ffmpeg 抓取/轉碼失敗 (exit $LASTEXITCODE)"
            exit 1
        }
        Write-Log "影片已儲存：$videoFile"
        & $ffmpeg -hide_banner -loglevel error -i "$videoFile" -vn -acodec libmp3lame -b:a 128k "$audioFile"
        if ($LASTEXITCODE -ne 0){
            Write-Log "錯誤：萃取音訊失敗"
            exit 1
        }
        Write-Log "音訊已萃取：$audioFile"
    }
}

# 4️⃣ 呼叫 Whisper 產出帶時間戳的 JSON（segment 輸出）
$transcriptJson = Join-Path $audioRoot "council_${timestamp}.json"
& $whisperExe -m whisper transcribe "$audioFile" --model $whisperModel --language zh --output_json "$transcriptJson"
if ($LASTEXITCODE -ne 0){
    Write-Log "錯誤：Whisper 轉錄失敗"
    exit 1
}
Write-Log "轉錄 JSON 已產出：$transcriptJson"

# 5️⃣ 切割影片為 5 分鐘片段 (方便後續依據關鍵詞保留/刪除)
$segmentFolder = Join-Path $outputRoot "segments_$timestamp"
New-Item -ItemType Directory -Force -Path $segmentFolder | Out-Null
& $ffmpeg -hide_banner -loglevel error -i "$videoFile" -c copy -map 0 -f segment -segment_time $segmentLen -reset_timestamps 1 "$segmentFolder\part_%03d.mp4"
if ($LASTEXITCODE -ne 0){
    Write-Log "錯誤：影片切片失敗"
    exit 1
}
Write-Log "影片已切片至資料夾：$segmentFolder"

# 6️⃣ 將轉錄結果寫入 SQLite (此段省略，請參考下一節的 Python 腳本)
Write-Log "後續將由寫入 DB 的腳本處理轉錄結果與片段對應"
Write-Log "============= 本次執行結束 ===============`n"

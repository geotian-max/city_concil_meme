const searchBox = document.getElementById('searchBox');
const resultsDiv = document.getElementById('results');
const hiddenVideo = document.getElementById('hiddenVideo');

function ytEmbedUrl(vid, start){
    // 如果vid看起来像YouTube ID（11位字母数字/-/_）
    if (/^[A-Za-z0-9_-]{11}$/.test(vid)){
        return `https://www.youtube.com/embed/${vid}?start=${Math.floor(start)}&autoplay=1`;
    }
    // 否则作为本地文件处理（例如：transcripts/xxx.vtt对应视频文件）
    // 假设您有与名称相同的mp4文件在videos/目录中
    return `videos/${vid}.mp4#t=${start}`;
}

async function doSearch(){
    const q = searchBox.value.trim();
    if (!q){ resultsDiv.innerHTML = ''; return; }
    const resp = await fetch(`/search?q=${encodeURIComponent(q)}`);
    const data = await resp.json();
    if(data.length===0){
        resultsDiv.innerHTML = '<p>找不到相符片段。</p>';
        return;
    }
    // 构建结果
    resultsDiv.innerHTML = await Promise.all(data.map(async r=>{
        const vid = r.vid;
        const start = r.start_time;
        const end   = r.end_time;
        // 确定缩略图
        const thumbUrl = /^[A-Za-z0-9_-]{11}$/.test(vid)
            ? `https://img.youtube.com/vi/${vid}/hqdefault.jpg`
            : `thumbnails/${vid}.jpg`;
        // 加载视频元数据以获取时长
        hiddenVideo.src = ytEmbedUrl(vid, start);
        await new Promise(res=>{ hiddenVideo.onloadedmetadata =()=>res(); });
        const duration = hiddenVideo.duration;
        const clipStart = Math.max(0, start-2);
        const clipEnd   = Math.min(duration, end+2);
        return `
            <div class="result-item" data-vid="${vid}" data-start="${clipStart}" data-end="${clipEnd}">
                <div class="thumb" style="background-image:url('${thumbUrl}');background-size:cover;"></div>
                <div>
                    <div class="text">${r.frag}</div>
                    <div class="timestamp">
                        ${new Date(clipStart*1000).toISOString().substr(11,8)} –
                        ${new Date(clipEnd*1000).toISOString().substr(11,8)}
                    </div>
                </div>
            </div>
        `;
    })).join('');

    // 为结果项附加点击处理程序以进行播放
    const resultItems = resultsDiv.querySelectorAll('.result-item');
    resultItems.forEach(item => {
        item.addEventListener('click', () => {
            // 移除任何现有的视频播放器
            document.querySelectorAll('.result-item video').forEach(v => v.remove());

            const vid = item.dataset.vid;
            const start = parseFloat(item.dataset.start);
            const end = parseFloat(item.dataset.end);

            const v = document.createElement('video');
            v.controls = true;
            v.src = ytEmbedUrl(vid, start);
            v.currentTime = 0;
            v.addEventListener('timeupdate',()=>{
                if(v.currentTime >= (end-start)+0.2){
                    v.pause();
                }
            });
            item.appendChild(v);
            v.play();
        });
    });

    // 自动播放第一个结果
    if (resultItems.length > 0) {
        resultItems[0].click();
    }
}

let timeoutId;
searchBox.addEventListener('input',()=>{
    clearTimeout(timeoutId);
    timeoutId = setTimeout(doSearch,300);
});
searchBox.addEventListener('keydown',e=>{
    if(e.key==='Enter'){
        e.preventDefault();
        doSearch();
    }
});
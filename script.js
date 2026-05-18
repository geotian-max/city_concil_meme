const searchBox = document.getElementById('searchBox');
const resultsDiv = document.getElementById('results');
const hiddenVideo = document.getElementById('hiddenVideo');

function ytEmbedUrl(vid, start){
    // If vid looks like a YouTube ID (11 chars alnum/-/_)
    if (/^[A-Za-z0-9_-]{11}$/.test(vid)){
        return `https://www.youtube.com/embed/${vid}?start=${Math.floor(start)}&autoplay=1`;
    }
    // Otherwise treat as local file (e.g., transcripts/xxx.vtt corresponds to video file)
    // Assuming you have mp4 files in videos/ with same name
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
    // Build results
    resultsDiv.innerHTML = await Promise.all(data.map(async r=>{
        const vid = r.vid;
        const start = r.start_time;
        const end   = r.end_time;
        // Determine thumbnail
        const thumbUrl = /^[A-Za-z0-9_-]{11}$/.test(vid)
            ? `https://img.youtube.com/vi/${vid}/hqdefault.jpg`
            : `thumbnails/${vid}.jpg`;
        // Load video metadata to get duration
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
                    <button class="play-btn">播放片段</button>
                </div>
            </div>
        `;
    })).join('');
    // Attach play button handlers
    document.querySelectorAll('.result-item .play-btn').forEach(btn=>{
        btn.addEventListener('click', e=>{
            const item = e.target.closest('.result-item');
            const vid   = item.dataset.vid;
            const start = parseFloat(item.dataset.start);
            const end   = parseFloat(item.dataset.end);
            const v = document.createElement('video');
            v.controls = true;
            v.src = ytEmbedUrl(vid, start);
            v.currentTime = 0;
            v.addEventListener('timeupdate',()=>{
                if(v.currentTime >= (end-start)+0.2){
                    v.pause();
                }
            });
            const playerDiv = document.createElement('div');
            playerDiv.style.marginTop='0.5rem';
            playerDiv.appendChild(v);
            item.appendChild(playerDiv);
            v.play();
        });
    });
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

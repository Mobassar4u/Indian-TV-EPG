async function initEPG() {
    try {
        // 1. Fetch both files simultaneously
        const [m3uRes, xmlRes] = await Promise.all([
            fetch('./channels.m3u'),
            fetch('./data.xml')
        ]);

        const m3uText = await m3uRes.text();
        const xmlText = await xmlRes.text();

        // 2. Parse XML EPG
        const parser = new DOMParser();
        const xmlDoc = parser.parseFromString(xmlText, "text/xml");
        const programmes = Array.from(xmlDoc.getElementsByTagName("programme"));

        // 3. Parse M3U and Match
        const lines = m3uText.split('\n');
        const container = document.getElementById("epg-grid");
        container.innerHTML = '';

        for (let i = 0; i < lines.length; i++) {
            if (lines[i].startsWith('#EXTINF')) {
                // Extract tvg-id and Logo
                const tvgIdMatch = lines[i].match(/tvg-id="([^"]+)"/);
                const logoMatch = lines[i].match(/tvg-logo="([^"]+)"/);
                const channelName = lines[i].split(',')[1];
                
                if (tvgIdMatch) {
                    const tvgId = tvgIdMatch[1];
                    const logo = logoMatch ? logoMatch[1] : 'https://via.placeholder.com/50';

                    // Find programs for this specific tvg-id
                    const channelProgs = programmes.filter(p => p.getAttribute("channel") === tvgId);

                    if (channelProgs.length > 0) {
                        renderChannelRow(container, channelName, logo, channelProgs);
                    }
                }
            }
        }
    } catch (err) {
        console.error("Initialization failed:", err);
    }
}

function renderChannelRow(container, name, logo, progs) {
    const row = document.createElement("div");
    row.className = "channel-row";

    row.innerHTML = `
        <div class="channel-info">
            <img src="${logo}" alt="${name}" onerror="this.src='https://via.placeholder.com/40'">
            <div>${name}</div>
        </div>
        <div class="program-list">
            ${progs.map(p => {
                const title = p.getElementsByTagName("title")[0].textContent;
                const start = p.getAttribute("start");
                return `
                    <div class="program-card">
                        <div class="program-time">${formatTime(start)}</div>
                        <strong>${title}</strong>
                    </div>
                `;
            }).join('')}
        </div>
    `;
    container.appendChild(row);
}

function formatTime(xmlTime) {
    // Converts 20260111183000 to 18:30
    return `${xmlTime.substring(8, 10)}:${xmlTime.substring(10, 12)}`;
}

initEPG();

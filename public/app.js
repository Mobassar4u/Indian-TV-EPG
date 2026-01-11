function renderRow(container, ch, progs) {
    const row = document.createElement("div");
    row.className = "channel-row";
    
    // Sort programs by time so history comes first
    const sortedProgs = progs.sort((a, b) => 
        a.getAttribute("start").localeCompare(b.getAttribute("start"))
    );

    row.innerHTML = `
        <div class="channel-info">
            <img src="${ch.logo}">
            <span>${ch.name}</span>
        </div>
        <div class="program-list">
            ${sortedProgs.map(p => {
                const startTime = p.getAttribute("start");
                const isPast = isProgramInPast(startTime);
                
                return `
                    <div class="program-card ${isPast ? 'catchup-available' : ''}">
                        <div class="time">${startTime.substring(8,12)}</div>
                        <div class="title">${p.getElementsByTagName("title")[0].textContent}</div>
                        ${isPast ? '<span class="badge">Catchup</span>' : ''}
                    </div>
                `;
            }).join('')}
        </div>`;
    container.appendChild(row);
}

// Helper to check if a program has already finished
function isProgramInPast(xmlTime) {
    // Format: YYYYMMDDHHMMSS
    const year = xmlTime.substring(0, 4);
    const month = xmlTime.substring(4, 6) - 1;
    const day = xmlTime.substring(6, 8);
    const hour = xmlTime.substring(8, 10);
    const min = xmlTime.substring(10, 12);
    
    const progDate = new Date(year, month, day, hour, min);
    return progDate < new Date();
}

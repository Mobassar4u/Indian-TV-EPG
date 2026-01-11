async function loadEPG() {
    try {
        const response = await fetch('./data.xml');
        const xmlText = await response.text();
        const parser = new DOMParser();
        const xmlDoc = parser.parseFromString(xmlText, "text/xml");

        const channels = Array.from(xmlDoc.getElementsByTagName("channel")).slice(0, 40);
        const programmes = Array.from(xmlDoc.getElementsByTagName("programme"));
        const container = document.getElementById("epg-grid");
        container.innerHTML = '';

        const now = new Date();

        channels.forEach(channel => {
            const id = channel.getAttribute("id");
            const name = channel.getElementsByTagName("display-name")[0].textContent;

            const row = document.createElement("div");
            row.className = "channel-row";
            row.innerHTML = `<div class="channel-info"><strong>${name}</strong></div>`;

            const progList = document.createElement("div");
            progList.className = "program-list";

            programmes.filter(p => p.getAttribute("channel") === id).forEach(p => {
                const title = p.getElementsByTagName("title")[0].textContent;
                const startStr = p.getAttribute("start");
                
                // Parse XML time: 20260111183000 +0530
                const hour = startStr.substring(8, 10);
                const min = startStr.substring(10, 12);

                const card = document.createElement("div");
                card.className = "program-card";
                card.innerHTML = `<span>${hour}:${min}</span><br><strong>${title}</strong>`;
                progList.appendChild(card);
            });

            row.appendChild(progList);
            container.appendChild(row);
        });
    } catch (err) {
        container.innerHTML = "Guide currently updating. Please check back in 5 minutes.";
    }
}
loadEPG();

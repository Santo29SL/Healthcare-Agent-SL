const API = "http://127.0.0.1:8000";
let user = null;

// Emergency Tips Data
const medicalTips = [
    "Stay Calm and Call for Help: Take a deep breath to think clearly, assess the situation, and immediately call emergency services (e.g., 108).",
    "Ensure Safety: Check for dangers like fire, electricity, or traffic before approaching the victim.",
    "Check Airway, Breathing, Circulation (ABC): Verify consciousness. If not breathing, start CPR immediately.",
    "Perform CPR: Push hard and fast (100–120 compressions per minute) in the center of the chest.",
    "Stop Severe Bleeding: Apply direct, firm pressure on the wound using a clean cloth or bandage.",
    "Manage Choking (Heimlich Maneuver): If a person cannot speak, perform abdominal thrusts.",
    "Heart Attack/Stroke: Keep them calm and seated; seek immediate professional help.",
    "Treat Burns Correctly: Run cool water over the burn for 10–20 minutes. Do not apply ice or ointments.",
    "Manage Fractures: Immobilize the area using a splint and avoid unnecessary movement.",
    "Control Shock: Keep the person warm, lying down, and provide constant reassurance."
];

document.addEventListener('DOMContentLoaded', () => {
    checkSession(); // Requirement: Persistent Session
    fetchWHORSSAuth();
    startTipRotation();
});

function checkSession() {
    const sessionData = JSON.parse(localStorage.getItem('agentic_session'));
    if (sessionData) {
        const now = new Date().getTime();
        // 15 minutes timeout logic
        if (now - sessionData.timestamp < 15 * 60 * 1000) {
            setupApp(sessionData.user);
        } else {
            logout();
        }
    }
}

async function handleLogin() {
    const email = document.getElementById('lEmail').value;
    const password = document.getElementById('lPass').value;
    const res = await fetch(`${API}/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: email, password: password })
    });
    if (res.ok) {
        const data = await res.json();
        // Save session locally
        localStorage.setItem('agentic_session', JSON.stringify({
            user: data,
            timestamp: new Date().getTime()
        }));
        triggerLoader(() => setupApp(data));
    } else { alert("Login failed"); }
}

async function handleSignup() {
    const payload = {
        name: document.getElementById('sName').value,
        email: document.getElementById('sEmail').value,
        password: document.getElementById('sPass').value,
        blood_group: document.getElementById('sBlood').value,
        allergies: document.getElementById('sAllergies').value
    };
    try {
        const response = await fetch(`${API}/signup`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        if (response.ok) {
            alert("Registration Successful!");
            toggleAuth('login');
        }
    } catch (error) { console.error("Signup error:", error); }
}

function triggerLoader(callback) {
    document.getElementById('lifelineLoader').classList.remove('hidden');
    setTimeout(() => {
        document.getElementById('lifelineLoader').classList.add('hidden');
        callback();
    }, 2000);
}

function startTipRotation() {
    let currentTip = 0;
    const tipEl = document.getElementById('tipText');
    if (!tipEl) return;
    setInterval(() => {
        tipEl.style.opacity = 0;
        setTimeout(() => {
            currentTip = (currentTip + 1) % medicalTips.length;
            tipEl.innerText = medicalTips[currentTip];
            tipEl.style.opacity = 1;
        }, 500);
    }, 8000);
}

async function runTriage() {
    const symptomText = document.getElementById('symptomText').value;
    if (!symptomText) return;
    const res = await fetch(`${API}/triage`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_id: user.id, query: symptomText })
    });
    const data = await res.json();
    document.getElementById('emergencyTips').classList.add('hidden'); // Hide tips on results
    const box = document.getElementById('triageResult');
    box.classList.remove('hidden');
    const isHigh = data.risk_level.toLowerCase().includes('high');
    box.className = `mt-8 p-8 rounded-[2rem] border-l-[15px] flex justify-between items-center ${isHigh ? 'bg-[#fce8e6] border-[#d32f2f]' : 'bg-[#e8f0fe] border-[#1a73e8]'}`;
    document.getElementById('riskTitle').innerHTML = `<span class="text-[10px] block opacity-50 uppercase tracking-widest">Clinical Risk Analysis:</span> ${data.risk_level.toUpperCase()}`;
    document.getElementById('riskAdvice').innerText = data.advice;
    document.getElementById('resultActions').innerHTML = `<button onclick="loadDoctors()" class="bg-[#202124] text-white px-8 py-3 rounded-xl font-black">CLINICS</button><button onclick="openPopup('chatPopup')" class="bg-[#0b57d0] text-white px-8 py-3 rounded-xl font-black">AI AGENT</button>`;
}

async function sendChat() {
    const q = chatInput.value; if (!q) return;
    const box = document.getElementById('chatMessages');
    box.innerHTML += `<div class="flex justify-end"><div class="bg-[#0b57d0] text-white p-4 rounded-2xl shadow-sm">${q}</div></div>`;
    const loadId = "load_" + Date.now();
    // Center-aligned Loading with Cyclic Dots
    box.innerHTML += `<div id="${loadId}" class="flex justify-center w-full py-6"><div class="bg-white border border-[#dfe1e5] px-6 py-3 rounded-full text-sm font-medium text-[#444746] flex items-center gap-2 shadow-sm">Gathering resources from PubMed MCP server<span class="cyclic-dots"></span></div></div>`;
    chatInput.value = ''; box.scrollTop = box.scrollHeight;
    const res = await fetch(`${API}/chat`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ user_id: user.id, query: q }) });
    const data = await res.json();
    document.getElementById(loadId).remove();
    const parts = data.response.split('\n\n');
    box.innerHTML += `<div class="space-y-4"><div class="pubmed-box"><b>VERIFIED LITERATURE:</b> ${parts[0]}</div><div class="ai-box"><b>CLINICAL INSIGHT:</b> <ul>${parts.slice(1).join('\n\n').split('\n').filter(p => p.trim()).map(p => `<li>• ${p.replace(/^[•\-\d.]+\s*/, '')}</li>`).join('')}</ul></div></div>`;
    box.scrollTop = box.scrollHeight;
}

async function fetchPubMedTrending() {
    const pubmedGrid = document.getElementById('pubmedGrid');
    try {
        const searchRes = await fetch("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term=trending&retmode=json&retmax=3");
        const searchData = await searchRes.json();
        const ids = searchData.esearchresult.idlist.join(',');

        if (!ids) throw new Error("No trending articles found");

        const summaryRes = await fetch(`https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed&id=${ids}&retmode=json`);
        const summaryData = await summaryRes.json();

        const items = searchData.esearchresult.idlist.map(id => {
            const article = summaryData.result[id];
            return {
                title: article.title,
                link: `https://pubmed.ncbi.nlm.nih.gov/${id}/`
            };
        });

        pubmedGrid.innerHTML = items.map(item => `
            <div class="p-6 bg-white rounded-3xl border border-[#dfe1e5] hover:border-[#0b57d0] transition-all flex flex-col h-full shadow-sm">
                <span class="text-[#0b57d0] font-black text-[10px] uppercase mb-2">TRENDING RESEARCH</span>
                <h4 class="font-bold text-sm line-clamp-2">${item.title}</h4>
                <a href="${item.link}" target="_blank" class="text-[10px] font-black text-[#0b57d0] uppercase mt-auto pt-4 hover:underline">Read Abstract</a>
            </div>`).join('');
    } catch (e) {
        console.warn("PubMed Sync Error.", e);
        pubmedGrid.innerHTML = '<p class="text-sm text-gray-500 p-4">Could not load trending research.</p>';
    }
}
async function fetchWHORSSAuth() {
    try {
        const res = await fetch("https://api.rss2json.com/v1/api.json?rss_url=https://www.who.int/rss-feeds/news-english.xml");
        const data = await res.json();
        const container = document.getElementById('whoRssAuth');
        let i = 0;
        const render = (idx) => {
            const item = data.items[idx];
            container.innerHTML = `<div class="p-10 bg-white rounded-[3.5rem] border border-[#dfe1e5] shadow-sm animate-in zoom-in duration-500">
                <span class="text-[10px] font-black text-[#0b57d0] uppercase tracking-widest">${new Date(item.pubDate).toLocaleDateString()}</span>
                <h4 class="font-bold text-[#1f1f1f] mt-4 text-xl leading-tight">${item.title}</h4>
                <p class="text-[#444746] mt-4 text-sm line-clamp-3">${item.description.replace(/<[^>]*>?/gm, '')}</p>
            </div>`;
        };
        render(0);
        setInterval(() => { i = (i + 1) % 5; render(i); }, 6000);
    } catch (e) { console.warn("WHO RSS Load error."); }
}
function setupApp(data) {
    user = data;
    document.getElementById('authContainer').classList.add('hidden');
    document.getElementById('navbar').classList.remove('hidden');
    document.getElementById('appViews').classList.remove('hidden');
    document.getElementById('navName').innerText = user.name;
    fetchPubMedTrending();
}

function logout() { localStorage.removeItem('agentic_session'); location.reload(); }
function openPopup(id) {
    document.getElementById(id).classList.remove('hidden');
    if (id === 'historyPopup') loadHistory();
    if (id === 'profilePopup' && user) {
        document.getElementById('pName').innerText = user.name || 'User';
        document.getElementById('pBlood').value = user.profile?.blood_group || '';
        document.getElementById('pAllergies').value = user.profile?.allergies || '';
    }
}
function closePopup(id) { document.getElementById(id).classList.add('hidden'); }
function toggleAuth(mode) {
    const isLogin = mode === 'login';
    document.getElementById('loginForm').classList.toggle('hidden', !isLogin);
    document.getElementById('signupForm').classList.toggle('hidden', isLogin);
    
    const tabLogin = document.getElementById('tabLogin');
    const tabSignup = document.getElementById('tabSignup');
    if (tabLogin && tabSignup) {
        if (isLogin) {
            tabLogin.classList.add('bg-white', 'shadow-sm');
            tabLogin.classList.remove('text-[#444746]');
            tabSignup.classList.remove('bg-white', 'shadow-sm');
            tabSignup.classList.add('text-[#444746]');
        } else {
            tabSignup.classList.add('bg-white', 'shadow-sm');
            tabSignup.classList.remove('text-[#444746]');
            tabLogin.classList.remove('bg-white', 'shadow-sm');
            tabLogin.classList.add('text-[#444746]');
        }
    }
}

async function handleUpdateProfile() {
    if (!user) return;
    const bg = document.getElementById('pBlood').value;
    const alg = document.getElementById('pAllergies').value;

    try {
        const res = await fetch(`${API}/update-profile`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ user_id: user.id, blood_group: bg, allergies: alg })
        });
        if (res.ok) {
            user.profile = { blood_group: bg, allergies: alg };
            localStorage.setItem('agentic_session', JSON.stringify({
                user: user,
                timestamp: new Date().getTime()
            }));
            alert("Profile updated successfully in database!");
            closePopup('profilePopup');
        } else {
            alert("Failed to update profile.");
        }
    } catch (e) {
        console.error("Update profile error", e);
        alert("An error occurred while updating the profile.");
    }
}

async function loadHistory() {
    if (!user) return;
    const historyContent = document.getElementById('historyContent');
    historyContent.innerHTML = '<div class="text-center py-10 text-gray-500">Loading history...</div>';

    try {
        const res = await fetch(`${API}/history/${user.id}`);
        if (res.ok) {
            const data = await res.json();
            if (data.length === 0) {
                historyContent.innerHTML = '<div class="text-center py-10 text-gray-500">No history found.</div>';
                return;
            }
            historyContent.innerHTML = data.map(item => `
                <div class="mb-4 p-4 bg-[#f8f9fa] rounded-2xl border border-[#dfe1e5]">
                    <div class="text-[10px] text-[#0b57d0] font-black uppercase mb-2">${item.time}</div>
                    <div class="text-sm font-medium text-[#1f1f1f]">${item.query}</div>
                </div>
            `).join('');
        } else {
            historyContent.innerHTML = '<div class="text-center py-10 text-red-500">Failed to load history.</div>';
        }
    } catch (e) {
        console.error("History load error", e);
        historyContent.innerHTML = '<div class="text-center py-10 text-red-500">Error loading history.</div>';
    }
}

async function loadDoctors() {
    openPopup('clinicsPopup');
    const clinicsContent = document.getElementById('clinicsContent');
    clinicsContent.innerHTML = '<div class="text-center py-10 text-gray-500">Getting your location...</div>';

    if (!navigator.geolocation) {
        clinicsContent.innerHTML = '<div class="text-center py-10 text-red-500">Geolocation is not supported by your browser.</div>';
        return;
    }

    navigator.geolocation.getCurrentPosition(async (position) => {
        const lat = position.coords.latitude;
        const lon = position.coords.longitude;
        clinicsContent.innerHTML = '<div class="text-center py-10 text-gray-500">Searching for nearby clinics...</div>';

        try {
            const res = await fetch(`${API}/doctors?lat=${lat}&lon=${lon}`);
            if (res.ok) {
                const data = await res.json();
                if (data.length === 0) {
                    clinicsContent.innerHTML = '<div class="text-center py-10 text-gray-500">No clinics found nearby.</div>';
                    return;
                }
                clinicsContent.innerHTML = data.map(doc => `
                    <div class="mb-4 p-5 bg-[#f8f9fa] rounded-2xl border border-[#dfe1e5] flex justify-between items-center">
                        <div>
                            <h4 class="font-bold text-[#1f1f1f] text-lg">${doc.name}</h4>
                            <div class="text-sm text-[#444746] mt-1">${doc.specialty}</div>
                            <div class="text-xs font-bold text-[#0b57d0] mt-2"><i class="fa-solid fa-location-dot mr-1"></i>${doc.dist.toFixed(2)} km away</div>
                        </div>
                        <a href="tel:${doc.phone}" class="bg-[#202124] text-white px-5 py-3 rounded-xl font-bold flex items-center justify-center gap-2 hover:bg-black transition-colors">
                            <i class="fa-solid fa-phone"></i> Call
                        </a>
                    </div>
                `).join('');
            } else {
                clinicsContent.innerHTML = '<div class="text-center py-10 text-red-500">Failed to reach clinic service.</div>';
            }
        } catch (e) {
            console.error(e);
            clinicsContent.innerHTML = '<div class="text-center py-10 text-red-500">Error loading clinics.</div>';
        }
    }, () => {
        clinicsContent.innerHTML = '<div class="text-center py-10 text-red-500">Unable to retrieve your location.</div>';
    });
}
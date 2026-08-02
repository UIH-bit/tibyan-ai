from flask import Flask, request, jsonify, render_template_string
import os
import requests

app = Flask(__name__)

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Tibyan AI</title>
    
    <link rel="manifest" href="/manifest.json">
    <meta name="theme-color" content="#ffffff">
    <meta name="mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-capable" content="yes">

    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; }
        
        body { background-color: #ffffff; color: #1f1f1f; display: flex; height: 100vh; overflow: hidden; }
        
        /* Sidebar / Left Drawer */
        .sidebar { width: 280px; background-color: #f9fbfd; border-right: 1px solid #e0e0e0; display: flex; flex-direction: column; height: 100vh; position: fixed; top: 0; left: -280px; transition: 0.3s ease; z-index: 1000; }
        .sidebar.open { left: 0; }
        
        .sidebar-header { padding: 16px; display: flex; align-items: center; justify-content: space-between; border-bottom: 1px solid #f0f0f0; }
        .new-chat-btn { display: flex; align-items: center; gap: 8px; background: #ffffff; border: 1px solid #dadce0; color: #1a73e8; padding: 8px 14px; border-radius: 16px; font-size: 14px; cursor: pointer; font-weight: 500; width: 100%; justify-content: center; transition: 0.2s; }
        .new-chat-btn:hover { background: #f1f3f4; }

        .sidebar-menu { flex: 1; overflow-y: auto; padding: 12px; display: flex; flex-direction: column; gap: 4px; }
        .menu-item { display: flex; align-items: center; gap: 12px; padding: 10px 14px; border-radius: 10px; color: #3c4043; font-size: 14px; cursor: pointer; text-decoration: none; transition: 0.2s; }
        .menu-item:hover { background: #f1f3f4; color: #202124; }
        .menu-item i { width: 20px; color: #5f6368; }

        .sidebar-footer { padding: 12px; border-top: 1px solid #f0f0f0; }

        /* Main Wrapper */
        .main-wrapper { flex: 1; display: flex; flex-direction: column; height: 100vh; margin-left: 0; transition: 0.3s ease; width: 100%; }
        
        header { display: flex; align-items: center; justify-content: space-between; padding: 14px 20px; background-color: #ffffff; border-bottom: 1px solid #f0f0f0; flex-shrink: 0; }
        .menu-toggle { background: transparent; border: none; font-size: 20px; cursor: pointer; color: #444746; padding: 6px; border-radius: 50%; }
        .menu-toggle:hover { background: #f1f3f4; }
        .logo-text { font-size: 18px; font-weight: 600; color: #1f1f1f; display: flex; align-items: center; gap: 8px; }
        .logo-text i { color: #1a73e8; }
        
        .content-area { flex: 1; overflow-y: auto; padding: 24px; display: flex; flex-direction: column; align-items: center; padding-bottom: 110px; }
        
        .view { width: 100%; max-width: 800px; display: none; flex-direction: column; }
        .view.active { display: flex; }

        .home-center { text-align: center; margin: auto 0; width: 100%; }
        .greeting { font-size: 36px; color: #1f1f1f; margin-bottom: 10px; font-weight: 500; font-family: serif; }
        .sub-greeting { font-size: 15px; color: #5f6368; margin-bottom: 30px; }
        
        .suggestions { display: flex; flex-wrap: wrap; gap: 10px; justify-content: center; margin-bottom: 20px; }
        .chip { background: #f8f9fa; border: 1px solid #dadce0; color: #3c4043; padding: 8px 14px; border-radius: 16px; font-size: 13px; cursor: pointer; transition: 0.2s; }
        .chip:hover { background: #f1f3f4; border-color: #bdc1c6; }
        
        #chat-box { width: 100%; text-align: left; display: none; flex-direction: column; gap: 20px; }
        .msg-container { width: 100%; margin-bottom: 15px; display: flex; flex-direction: column; gap: 8px; }
        
        .msg { font-size: 15px; line-height: 1.6; white-space: pre-wrap; width: 100%; }
        .user-msg { background: #f0f4f9; color: #1f1f1f; padding: 12px 18px; border-radius: 18px 18px 4px 18px; align-self: flex-end; max-width: 85%; margin-left: auto; }
        .bot-msg { color: #202124; padding: 4px 0; align-self: flex-start; width: 100%; }
        
        .action-bar { display: flex; gap: 12px; align-items: center; margin-top: 2px; }
        .action-btn { background: transparent; border: none; color: #5f6368; font-size: 13px; cursor: pointer; display: inline-flex; align-items: center; gap: 5px; padding: 4px 8px; border-radius: 6px; transition: 0.2s; }
        .action-btn:hover { background: #f1f3f4; color: #202124; }
        .action-btn.active-action { color: #1a73e8; font-weight: 500; }

        .lib-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: 14px; width: 100%; margin-top: 10px; }
        .lib-card { background: #f8f9fa; border: 1px solid #dadce0; padding: 16px; border-radius: 14px; cursor: pointer; transition: 0.2s; display: flex; flex-direction: column; gap: 6px; }
        .lib-card:hover { background: #f1f3f4; border-color: #bdc1c6; }
        .lib-card h3 { color: #1a73e8; font-size: 16px; font-weight: 500; display: flex; align-items: center; gap: 8px; }
        .lib-card p { color: #5f6368; font-size: 13px; line-height: 1.3; }

        .section-title { font-size: 22px; color: #1f1f1f; margin-bottom: 15px; font-weight: 500; width: 100%; display: flex; justify-content: space-between; align-items: center; }
        
        .bottom-panel { position: fixed; bottom: 15px; left: 0; width: 100%; background: transparent; padding: 0 20px; display: flex; justify-content: center; z-index: 10; }
        .input-box { display: flex; align-items: flex-end; background-color: #f0f4f9; border: 1px solid transparent; border-radius: 28px; padding: 10px 16px; width: 100%; max-width: 750px; transition: 0.2s; box-shadow: 0 2px 10px rgba(0,0,0,0.06); gap: 8px; }
        .input-box:focus-within { background: #ffffff; border-color: #d3e3fd; box-shadow: 0 4px 14px rgba(26,115,232,0.1); }
        .input-box textarea { flex: 1; background: transparent; border: none; outline: none; color: #1f1f1f; font-size: 15px; resize: none; max-height: 120px; min-height: 24px; line-height: 1.5; padding-top: 2px; }
        
        .tool-btn { background: transparent; border: none; color: #444746; font-size: 18px; cursor: pointer; padding: 6px; border-radius: 50%; width: 38px; height: 38px; display: flex; align-items: center; justify-content: center; }
        .tool-btn:hover { background: #e2e8f0; }
        .send-btn { background: #1a73e8; border: none; color: #ffffff; font-size: 14px; cursor: pointer; width: 38px; height: 38px; border-radius: 50%; display: flex; align-items: center; justify-content: center; transition: 0.2s; flex-shrink: 0; }
        .send-btn:hover { background: #1557b0; }

        /* Overlay for mobile drawer */
        .overlay { position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.3); display: none; z-index: 999; }
        .overlay.active { display: block; }
    </style>
</head>
<body>

    <!-- Left Drawer / Sidebar -->
    <div class="overlay" id="overlay" onclick="toggleSidebar()"></div>
    <div class="sidebar" id="sidebar">
        <div class="sidebar-header">
            <button class="new-chat-btn" onclick="startNewChat(); toggleSidebar();"><i class="fa-solid fa-plus"></i> New Chat</button>
        </div>
        <div class="sidebar-menu">
            <div class="menu-item" onclick="switchView('home')"><i class="fa-solid fa-house"></i> Home / Chat</div>
            <div class="menu-item" onclick="switchView('history')"><i class="fa-solid fa-clock-rotate-left"></i> History</div>
            <div class="menu-item" onclick="switchView('search')"><i class="fa-solid fa-magnifying-glass"></i> Search Chats</div>
            <div class="menu-item" onclick="switchView('library')"><i class="fa-solid fa-book-open"></i> Library</div>
            <div class="menu-item" onclick="switchView('bookmarks')"><i class="fa-solid fa-bookmark"></i> Bookmarks</div>
            <div class="menu-item" onclick="switchView('downloads')"><i class="fa-solid fa-download"></i> Downloads</div>
            <div class="menu-item" onclick="switchView('collection')"><i class="fa-solid fa-folder-open"></i> Collection</div>
            <div class="menu-item" onclick="switchView('settings')"><i class="fa-solid fa-gear"></i> Setting</div>
            <div class="menu-item" onclick="switchView('help')"><i class="fa-solid fa-circle-question"></i> Help</div>
            <div class="menu-item" onclick="switchView('about')"><i class="fa-solid fa-circle-info"></i> About</div>
        </div>
        <div class="sidebar-footer">
            <div class="menu-item" onclick="switchView('auth')" style="background: #f0f4f9; color: #1a73e8; font-weight: 500;"><i class="fa-solid fa-user"></i> Login / Signup</div>
        </div>
    </div>

    <!-- Main App UI -->
    <div class="main-wrapper">
        <header>
            <div style="display: flex; align-items: center; gap: 12px;">
                <button class="menu-toggle" onclick="toggleSidebar()"><i class="fa-solid fa-bars"></i></button>
                <div class="logo-text"><i class="fa-solid fa-sparkles"></i> Tibyan AI</div>
            </div>
            <button onclick="startNewChat()" style="background: #f0f4f9; border: 1px solid #dadce0; color: #1a73e8; padding: 6px 12px; border-radius: 14px; font-size: 13px; cursor: pointer; font-weight: 500;"><i class="fa-solid fa-plus"></i> New Chat</button>
        </header>

        <div class="content-area">
            <!-- HOME / CHAT VIEW -->
            <div id="view-home" class="view active">
                <div id="home-welcome" class="home-center">
                    <div class="greeting">السلام عليكم</div>
                    <div class="sub-greeting">Authentic Islamic Knowledge, Powered by Advanced Context AI</div>
                    <div class="suggestions">
                        <div class="chip" onclick="sendSuggestion('What breaks the fast in detail?')">What breaks the fast?</div>
                        <div class="chip" onclick="sendSuggestion('Explain the deep virtues of Ayat al-Kursi')">Virtues of Ayat al-Kursi</div>
                        <div class="chip" onclick="sendSuggestion('Step by step guide to Tahajjud prayer')">How to perform Tahajjud?</div>
                    </div>
                </div>
                <div id="chat-box"></div>
            </div>

            <!-- HISTORY VIEW -->
            <div id="view-history" class="view">
                <div class="section-title">Chat History <button onclick="clearHistory()" style="background:transparent; border:none; color:#ea4335; font-size:12px; cursor:pointer;"><i class="fa-solid fa-trash"></i> Clear</button></div>
                <div id="history-container" style="display: flex; flex-direction: column; gap: 12px; width: 100%;">
                    <div style="color: #5f6368; font-size: 14px; text-align: center; margin-top: 30px;">No past chats found.</div>
                </div>
            </div>

            <!-- SEARCH CHATS VIEW -->
            <div id="view-search" class="view">
                <div class="section-title">Search Chats</div>
                <input type="text" id="chat-search-input" placeholder="Type keyword to search in history..." oninput="searchChats(this.value)" style="width: 100%; padding: 12px 16px; border: 1px solid #dadce0; border-radius: 12px; font-size: 15px; outline: none; margin-bottom: 15px;">
                <div id="search-results-container" style="display: flex; flex-direction: column; gap: 10px; width: 100%;"></div>
            </div>

            <!-- LIBRARY VIEW -->
            <div id="view-library" class="view">
                <div class="section-title">Islamic Library</div>
                <div class="lib-grid">
                    <div class="lib-card" onclick="sendSuggestion('Explain the 5 Pillars of Islam with comprehensive proofs')">
                        <h3><i class="fa-solid fa-book"></i> Pillars of Islam</h3>
                        <p>Detailed study of Shahada, Salah, Zakat, Sawm, and Hajj.</p>
                    </div>
                    <div class="lib-card" onclick="sendSuggestion('Share 5 essential Daily Duas with Arabic text and meanings')">
                        <h3><i class="fa-solid fa-hands-praying"></i> Daily Duas</h3>
                        <p>Essential supplications for morning, evening, and protection.</p>
                    </div>
                    <div class="lib-card" onclick="sendSuggestion('Explain 3 authentic Hadiths from 40 Hadith Nawawi')">
                        <h3><i class="fa-solid fa-scroll"></i> 40 Hadith Nawawi</h3>
                        <p>Core sayings of Prophet Muhammad (PBUH) on Islamic morals.</p>
                    </div>
                    <div class="lib-card" onclick="sendSuggestion('Explain the meaning and beauty of 5 Names of Allah (Asma-ul-Husna)')">
                        <h3><i class="fa-solid fa-star-and-crescent"></i> Asma-ul-Husna</h3>
                        <p>Discover the profound meanings of the Beautiful Names of Allah.</p>
                    </div>
                </div>
            </div>

            <!-- BOOKMARKS VIEW -->
            <div id="view-bookmarks" class="view">
                <div class="section-title">Bookmarks <button onclick="clearSaved()" style="background:transparent; border:none; color:#ea4335; font-size:12px; cursor:pointer;"><i class="fa-solid fa-trash"></i> Clear</button></div>
                <div id="saved-container" style="display: flex; flex-direction: column; gap: 12px; width: 100%;">
                    <div style="color: #5f6368; font-size: 14px; text-align: center; margin-top: 30px;">No saved bookmarks yet.</div>
                </div>
            </div>

            <!-- DOWNLOADS VIEW -->
            <div id="view-downloads" class="view">
                <div class="section-title">Downloads</div>
                <p style="color: #5f6368; font-size: 14px; line-height: 1.5;">You can download offline scholarly articles or exported chat histories here. No offline items downloaded yet.</p>
            </div>

            <!-- COLLECTION VIEW -->
            <div id="view-collection" class="view">
                <div class="section-title">Collection</div>
                <p style="color: #5f6368; font-size: 14px; line-height: 1.5;">Manage your categorized notes, favorite verses, and saved topics into custom collections.</p>
            </div>

            <!-- SETTINGS VIEW -->
            <div id="view-settings" class="view">
                <div class="section-title">Settings</div>
                <div style="display: flex; flex-direction: column; gap: 15px; font-size: 15px;">
                    <label style="display: flex; justify-content: space-between; align-items: center; padding: 12px; background: #f8f9fa; border-radius: 10px;">
                        <span>Dark Theme Mode</span>
                        <input type="checkbox" onchange="alert('Dark mode toggle coming soon!')">
                    </label>
                    <label style="display: flex; justify-content: space-between; align-items: center; padding: 12px; background: #f8f9fa; border-radius: 10px;">
                        <span>Scholarly Detailed Responses</span>
                        <input type="checkbox" checked disabled>
                    </label>
                </div>
            </div>

            <!-- HELP VIEW -->
            <div id="view-help" class="view">
                <div class="section-title">Help & Support</div>
                <p style="color: #5f6368; font-size: 14px; line-height: 1.6;">Tibyan AI is designed to assist you with authentic Islamic knowledge. If you face any issues, make sure your internet connection is active and your API key is correctly configured.</p>
            </div>

            <!-- ABOUT VIEW -->
            <div id="view-about" class="view">
                <div class="section-title">About Tibyan AI</div>
                <p style="color: #5f6368; font-size: 14px; line-height: 1.6;"><strong>Tibyan AI v2.0</strong><br>An intelligent Islamic scholarly assistant built to provide grounded, authentic information from the Quran, Hadith, and Fiqh.</p>
            </div>

            <!-- LOGIN / SIGNUP VIEW -->
            <div id="view-auth" class="view">
                <div class="section-title">Login / Signup</div>
                <div style="background: #f8f9fa; border: 1px solid #dadce0; padding: 24px; border-radius: 16px; display: flex; flex-direction: column; gap: 15px; max-width: 400px; margin: 0 auto; width: 100%;">
                    <h3 style="font-size: 18px; color: #1a73e8; margin-bottom: 5px;">Welcome to Tibyan</h3>
                    <input type="email" placeholder="Email Address" style="padding: 12px; border: 1px solid #dadce0; border-radius: 10px; font-size: 14px; outline: none;">
                    <input type="password" placeholder="Password" style="padding: 12px; border: 1px solid #dadce0; border-radius: 10px; font-size: 14px; outline: none;">
                    <button onclick="alert('Authentication feature connected to local state!')" style="background: #1a73e8; color: white; border: none; padding: 12px; border-radius: 10px; font-size: 15px; cursor: pointer; font-weight: 500;">Continue</button>
                </div>
            </div>

        </div>
    </div>

    <!-- Bottom Input Bar (Only visible on Home) -->
    <div class="bottom-panel" id="input-container-wrapper">
        <div class="input-box">
            <button class="tool-btn" title="Voice Input" onclick="toggleVoiceInput()"><i class="fa-solid fa-microphone" id="mic-icon"></i></button>
            <textarea id="user-input" placeholder="Ask anything about Quran, Hadith, Fiqh..." rows="1" oninput="autoResize(this)" onkeydown="handleKey(event)"></textarea>
            <button class="send-btn" onclick="sendMessage()"><i class="fa-solid fa-arrow-up"></i></button>
        </div>
    </div>

    <script>
        let currentSessionChats = [];
        let allPastSessions = JSON.parse(localStorage.getItem('tibyan_past_sessions')) || [];
        let savedItems = JSON.parse(localStorage.getItem('tibyan_saved_items')) || [];

        window.addEventListener('DOMContentLoaded', () => {
            updateSavedUI();
            updateHistoryUI();
        });

        function toggleSidebar() {
            document.getElementById('sidebar').classList.toggle('open');
            document.getElementById('overlay').classList.toggle('active');
        }

        function switchView(viewName) {
            document.querySelectorAll('.view').forEach(v => v.classList.remove('active'));
            document.getElementById('view-' + viewName).classList.add('active');
            document.getElementById('input-container-wrapper').style.display = (viewName === 'home') ? 'flex' : 'none';
            toggleSidebar();
        }

        function autoResize(textarea) {
            textarea.style.height = 'auto';
            textarea.style.height = textarea.scrollHeight + 'px';
        }

        function startNewChat() {
            if (currentSessionChats.length > 0) {
                allPastSessions.unshift({
                    date: new Date().toLocaleDateString() + ' ' + new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
                    chats: [...currentSessionChats]
                });
                localStorage.setItem('tibyan_past_sessions', JSON.stringify(allPastSessions));
                currentSessionChats = [];
                updateHistoryUI();
            }
            document.getElementById('home-welcome').style.display = 'block';
            const chatBox = document.getElementById('chat-box');
            chatBox.style.display = 'none';
            chatBox.innerHTML = '';
            switchView('home');
        }

        function sendSuggestion(text) {
            switchView('home');
            const input = document.getElementById('user-input');
            input.value = text;
            autoResize(input);
            sendMessage();
        }

        function handleKey(e) {
            if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendMessage(); }
        }

        function copyText(btn) {
            navigator.clipboard.writeText(btn.getAttribute('data-content'));
            const orig = btn.innerHTML;
            btn.innerHTML = '<i class="fa-solid fa-check"></i> Copied';
            setTimeout(() => { btn.innerHTML = orig; }, 2000);
        }

        function saveAnswer(btn) {
            const text = btn.getAttribute('data-content');
            if (btn.classList.contains('active-action')) return;
            btn.classList.add('active-action');
            btn.innerHTML = '<i class="fa-solid fa-bookmark"></i> Saved';
            if (!savedItems.includes(text)) {
                savedItems.push(text);
                localStorage.setItem('tibyan_saved_items', JSON.stringify(savedItems));
                updateSavedUI();
            }
        }

        function clearSaved() {
            if (confirm("Clear all bookmarks?")) {
                savedItems = [];
                localStorage.removeItem('tibyan_saved_items');
                updateSavedUI();
            }
        }

        function clearHistory() {
            if (confirm("Clear all history?")) {
                allPastSessions = [];
                localStorage.removeItem('tibyan_past_sessions');
                updateHistoryUI();
            }
        }

        function updateSavedUI() {
            const container = document.getElementById('saved-container');
            if (savedItems.length === 0) {
                container.innerHTML = '<div style="color: #5f6368; font-size: 14px; text-align: center; margin-top: 30px;">No saved bookmarks yet.</div>';
                return;
            }
            container.innerHTML = '';
            savedItems.forEach((item, index) => {
                container.innerHTML += `<div style="background: #f8f9fa; border: 1px solid #dadce0; padding: 16px; border-radius: 12px; font-size: 14px; line-height: 1.5;"><div style="color: #1a73e8; font-weight: 500; margin-bottom: 6px;">Bookmark #${index + 1}</div>${item}</div>`;
            });
        }

        function updateHistoryUI() {
            const container = document.getElementById('history-container');
            if (allPastSessions.length === 0) {
                container.innerHTML = '<div style="color: #5f6368; font-size: 14px; text-align: center; margin-top: 30px;">No past chats found.</div>';
                return;
            }
            container.innerHTML = '';
            allPastSessions.forEach((session) => {
                let html = `<div style="background: #f8f9fa; border: 1px solid #dadce0; padding: 12px; border-radius: 12px;"><div style="color: #1a73e8; font-weight: 500; font-size: 12px; margin-bottom: 6px;">${session.date}</div>`;
                session.chats.forEach(c => {
                    html += `<div style="font-size: 13px; margin-bottom: 6px;"><strong>${c.user}</strong></div>`;
                });
                html += `</div>`;
                container.innerHTML += html;
            });
        }

        function searchChats(query) {
            const resContainer = document.getElementById('search-results-container');
            if (!query.trim()) { resContainer.innerHTML = ''; return; }
            let results = [];
            allPastSessions.forEach(s => {
                s.chats.forEach(c => {
                    if (c.user.toLowerCase().includes(query.toLowerCase()) || c.bot.toLowerCase().includes(query.toLowerCase())) {
                        results.push(c);
                    }
                });
            });
            if (results.length === 0) {
                resContainer.innerHTML = '<div style="color: #5f6368; font-size: 14px; text-align: center;">No matching chats found.</div>';
                return;
            }
            resContainer.innerHTML = '';
            results.forEach(r => {
                resContainer.innerHTML += `<div style="background: #f8f9fa; border: 1px solid #dadce0; padding: 14px; border-radius: 12px; font-size: 14px;"><strong>Q: ${r.user}</strong><br><span style="color: #5f6368;">${r.bot.substring(0, 100)}...</span></div>`;
            });
        }

        async function sendMessage() {
            const input = document.getElementById('user-input');
            const message = input.value.trim();
            if (!message) return;

            document.getElementById('home-welcome').style.display = 'none';
            const chatBox = document.getElementById('chat-box');
            chatBox.style.display = 'flex';

            chatBox.innerHTML += `<div class="msg-container"><div class="msg user-msg">${message}</div></div>`;
            input.value = '';
            input.style.height = '24px';
            window.scrollTo(0, document.body.scrollHeight);

            try {
                const response = await fetch('/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ message: message })
                });
                const data = await response.json();
                
                const tempDiv = document.createElement('div');
                tempDiv.textContent = data.response;
                const safeText = tempDiv.innerHTML;

                currentSessionChats.push({ user: message, bot: data.response });

                chatBox.innerHTML += `
                    <div class="msg-container">
                        <div class="msg bot-msg">${data.response}</div>
                        <div class="action-bar">
                            <button class="action-btn" data-content="${safeText.replace(/"/g, '&quot;')}" onclick="copyText(this)"><i class="fa-regular fa-copy"></i> Copy</button>
                            <button class="action-btn" data-content="${safeText.replace(/"/g, '&quot;')}" onclick="saveAnswer(this)"><i class="fa-regular fa-bookmark"></i> Save</button>
                        </div>
                    </div>`;
                window.scrollTo(0, document.body.scrollHeight);
            } catch (err) {
                chatBox.innerHTML += `<div class="msg-container"><div class="msg bot-msg">Error: Unable to fetch response.</div></div>`;
            }
        }
    </script>
</body>
</html>
'''

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/manifest.json')
def manifest():
    return jsonify({
        "name": "Tibyan AI",
        "short_name": "Tibyan",
        "start_url": "/",
        "display": "standalone",
        "background_color": "#ffffff",
        "theme_color": "#1a73e8",
        "icons": [{"src": "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/svgs/solid/sparkles.svg", "sizes": "512x512", "type": "image/svg+xml"}]
    })

@app.route('/chat', methods=['POST'])
def chat():
    user_msg = request.json.get('message', '')
    api_key = os.environ.get("GROQ_API_KEY")
    
    if not api_key:
        return jsonify({"response": "Error: GROQ_API_KEY is missing."})

    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    
    system_prompt = (
        "You are Tibyan AI, an elite, highly knowledgeable, and authentic Islamic scholar assistant. "
        "Your responses must be structured, deeply detailed, scholarly, and completely grounded in authentic Islamic sources. "
        "Strictly follow these rules for every answer:\n"
        "1. Always quote relevant Quranic verses with Surah name and Ayat number (in Arabic and translation if needed).\n"
        "2. Provide authentic Hadiths with proper references (Sahih al-Bukhari, Sahih Muslim, Sunan Abu Dawud, etc.).\n"
        "3. Explain the rulings according to recognized mainstream Fiqh schools (Hanafi, Shafi'i, Maliki, Hanbali) if there is a difference of opinion.\n"
        "4. Maintain an empathetic, respectful, wise, and dignified scholarly tone. Avoid vague or unsupported opinions."
    )

    data = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_msg}
        ]
    }
    try:
        res = requests.post(url, json=data, headers=headers)
        res_json = res.json()
        if 'choices' in res_json:
            return jsonify({"response": res_json['choices'][0]['message']['content']})
        else:
            return jsonify({"response": f"API Error: {res_json.get('error', {}).get('message', 'Invalid Key')}"})
    except Exception as e:
        return jsonify({"response": f"Connection Error: {str(e)}"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

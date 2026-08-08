from flask import Flask, request, jsonify, render_template_string
import os
import requests

app = Flask(__name__)
api_key = os.environ.get("GROQ_API_KEY") or os.environ.get("GEMINI_API_KEY")

def call_groq_api(prompt_text):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {
                "role": "system", 
                "content": "You are Tibyan AI, a knowledgeable and respectful Muslim scholar assistant adhering to Hanafi Fiqh (Deoband/Banuri Town manhaj). Structure responses cleanly."
            },
            {"role": "user", "content": prompt_text}
        ],
        "temperature": 0.7
    }
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=25)
        if response.status_code == 200:
            return response.json()['choices'][0]['message']['content']
        else:
            return f"Error: {response.text}"
    except Exception as e:
        return f"Exception: {str(e)}"

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Tibyan AI - Authentic Islamic Knowledge</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }
        body { background-color: #ffffff; color: #111; display: flex; flex-direction: column; height: 100vh; overflow: hidden; font-size: 17px; }
        header { display: flex; align-items: center; justify-content: space-between; padding: 15px 20px; border-bottom: 1px solid #eaeaea; background: #fff; z-index: 10; flex-shrink: 0; }
        .header-left { display: flex; align-items: center; gap: 15px; }
        .menu-btn { background: none; border: none; font-size: 24px; cursor: pointer; color: #1e3d2f; }
        .logo { font-size: 22px; font-weight: bold; color: #1e3d2f; }
        
        .sidebar { position: fixed; top: 0; left: -280px; width: 280px; height: 100%; background: #fff; box-shadow: 2px 0 10px rgba(0,0,0,0.1); transition: 0.3s ease; z-index: 100; display: flex; flex-direction: column; }
        .sidebar.open { left: 0; }
        .sidebar-header { padding: 20px; font-size: 20px; font-weight: bold; color: #1e3d2f; border-bottom: 1px solid #eaeaea; display: flex; justify-content: space-between; align-items: center; }
        .close-sidebar { background: none; border: none; font-size: 20px; cursor: pointer; color: #555; }
        .sidebar-search-box { padding: 12px 16px; border-bottom: 1px solid #eaeaea; }
        .sidebar-search { width: 100%; padding: 10px 14px; border: 1px solid #ddd; border-radius: 8px; font-size: 15px; outline: none; background: #f9f9f9; }
        .sidebar-menu { list-style: none; padding: 10px 0; overflow-y: auto; flex: 1; }
        .sidebar-menu li { padding: 14px 20px; font-size: 17px; color: #333; cursor: pointer; display: flex; align-items: center; gap: 14px; transition: 0.2s; border-bottom: 1px solid #f7f7f7; }
        .sidebar-menu li:hover { background: #f0f4f1; color: #1e3d2f; font-weight: 500; }
        
        .overlay { position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.4); display: none; z-index: 90; }
        .overlay.active { display: block; }

        .main-content { flex: 1; display: flex; flex-direction: column; overflow: hidden; position: relative; }
        .view-section { display: none; flex: 1; overflow-y: auto; padding: 20px; max-width: 800px; width: 100%; margin: 0 auto; scroll-behavior: smooth; }
        .view-section.active-view { display: flex; flex-direction: column; }

        .chat-container { justify-content: space-between; }
        .welcome-section { display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center; margin: auto 0; width: 100%; padding: 20px 0; }
        .arabic-greeting { font-size: 40px; color: #1e3d2f; font-weight: bold; margin-bottom: 15px; font-family: serif; }
        .sub-text { font-size: 18px; color: #555; margin-bottom: 30px; line-height: 1.5; }
        
        .suggestions { width: 100%; display: flex; flex-direction: column; align-items: center; gap: 14px; max-width: 550px; margin: 0 auto; }
        .suggestions-row { display: flex; justify-content: center; gap: 14px; width: 100%; }
        .suggestion-chip { background: #fff; border: 1px solid #e0e0e0; border-radius: 30px; padding: 14px 20px; font-size: 16px; color: #333; cursor: pointer; text-align: center; box-shadow: 0 2px 5px rgba(0,0,0,0.02); transition: 0.2s; flex: 1; }
        .suggestion-chip:hover { border-color: #1e3d2f; background: #f9fbf9; }
        .suggestion-center { max-width: 280px; width: 100%; }

        #chat-history { width: 100%; display: flex; flex-direction: column; gap: 18px; padding-bottom: 20px; }
        .message-wrapper { display: flex; flex-direction: column; width: 100%; margin-bottom: 12px; }
        .message { padding: 16px 20px; border-radius: 14px; max-width: 85%; line-height: 1.6; font-size: 17px; white-space: pre-wrap; }
        .user-msg { background: #f0f4f1; color: #1e3d2f; align-self: flex-end; margin-left: auto; }
        .ai-msg { background: #ffffff; border: 1px solid #e0e0e0; color: #222; align-self: flex-start; width: 100%; max-width: 100%; }
        
        .library-grid { display: grid; grid-template-columns: 1fr; gap: 12px; padding-bottom: 20px; }
        .library-card { background: #fff; border: 1px solid #e0e0e0; border-radius: 10px; padding: 16px 20px; font-size: 18px; font-weight: 500; color: #1e3d2f; cursor: pointer; box-shadow: 0 2px 4px rgba(0,0,0,0.02); transition: 0.2s; display: flex; align-items: center; justify-content: space-between; }
        .library-card:hover { background: #f0f4f1; border-color: #1e3d2f; }

        .input-area { display: flex; align-items: flex-end; padding: 14px 18px; border-top: 1px solid #eaeaea; background: #fff; gap: 12px; max-width: 800px; width: 100%; margin: 0 auto; flex-shrink: 0; }
        .text-input { flex: 1; border: 1px solid #e0e0e0; border-radius: 24px; padding: 14px 20px; font-size: 17px; outline: none; background: #f9f9f9; resize: none; max-height: 180px; overflow-y: auto; line-height: 1.5; }
        .send-btn { background: #1e3d2f; border: none; border-radius: 50%; width: 48px; height: 48px; min-width: 48px; display: flex; align-items: center; justify-content: center; cursor: pointer; color: white; position: relative; margin-bottom: 3px; }
        .send-btn svg { width: 20px; height: 20px; fill: white; }
    </style>
</head>
<body>
    <header>
        <div class="header-left">
            <button class="menu-btn" onclick="toggleSidebar()">☰</button>
            <div class="logo">Tibyan AI</div>
        </div>
    </header>

    <div class="overlay" id="overlay" onclick="toggleSidebar()"></div>
    <div class="sidebar" id="sidebar">
        <div class="sidebar-header">
            <span>Tibyan Menu</span>
            <button class="close-sidebar" onclick="toggleSidebar()">✕</button>
        </div>
        
        <div class="sidebar-search-box">
            <input type="text" id="chatSearchInput" class="sidebar-search" placeholder="Search Chats..." oninput="filterChats(this.value)">
        </div>

        <ul class="sidebar-menu">
            <li onclick="startNewChat()">➕️ New Chat</li>
            <li onclick="switchView('home')">🏡 Home</li>
            <li onclick="switchView('library')">📚 Library</li>
            <li onclick="switchView('saved')">📜 Saved</li>
            <li onclick="switchView('profile')">👤 Profile</li>
            <li onclick="switchView('about')">❕️ About</li>
        </ul>
    </div>

    <div class="main-content">
        <div id="home-view" class="view-section active-view chat-container">
            <div id="chat-box" style="width: 100%;">
                <div class="welcome-section" id="welcome-screen">
                    <div class="arabic-greeting">بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ</div>
                    <div class="sub-text">Authentic Islamic Knowledge backed by Deoband & Banuri Town manhaj</div>
                    <div class="suggestions">
                        <div class="suggestions-row">
                            <div class="suggestion-chip" onclick="sendPrompt('What does the Quran say about patience (Sabr)?')">What does the Quran say about patience (Sabr)?</div>
                            <div class="suggestion-chip" onclick="sendPrompt('Roza kaise toot jata hai')">Roza kaise toot jata hai</div>
                        </div>
                    </div>
                </div>
                <div id="chat-history"></div>
            </div>
        </div>

        <div id="library-view" class="view-section">
            <div class="view-title" style="font-size:28px; color:#1e3d2f; margin-bottom:20px; font-weight:bold;">Islamic Library 📚</div>
            <div class="library-grid">
                <div class="library-card" onclick="sendPrompt('Tell me about Qur\'an sciences.')">📖 Qur'an</div>
                <div class="library-card" onclick="sendPrompt('Explain Tafsir methodologies.')">📜 Tafsir</div>
                <div class="library-card" onclick="sendPrompt('Explain Hadith collections.')">🏷️ Hadith</div>
                <div class="library-card" onclick="sendPrompt('Explain Fiqh according to Hanafi school.')">⚖️ Fiqh</div>
                <div class="library-card" onclick="sendPrompt('Principles of Usul al-Fiqh.')">📋 Usul al-Fiqh</div>
                <div class="library-card" onclick="sendPrompt('Explain Islamic Aqeedah.')">💡 Aqeedah</div>
                <div class="library-card" onclick="sendPrompt('Arabic Fatawa insights.')">📜 Arabic Fatwa</div>
                <div class="library-card" onclick="sendPrompt('Overview of Islamic History.')">🏛️ History</div>
                <div class="library-card" onclick="sendPrompt('Seerah of Prophet Muhammad (PBUH).')">⭐ Seerah</div>
                <div class="library-card" onclick="sendPrompt('Islamic Biographies.')">👥 Biography</div>
                <div class="library-card" onclick="sendPrompt('Islamic Finance and Banking.')">🪙 Islamic Finance</div>
                <div class="library-card" onclick="sendPrompt('Comparative religion.')">🌐 Comparative religion</div>
            </div>
        </div>

        <div id="saved-view" class="view-section"><div style="font-size:28px; color:#1e3d2f; margin-bottom:20px; font-weight:bold;">Saved Chats 📜</div><p>No saved responses yet.</p></div>
        <div id="profile-view" class="view-section"><div style="font-size:28px; color:#1e3d2f; margin-bottom:20px; font-weight:bold;">Profile 👤</div><p>Active Developer Mode</p></div>
        <div id="about-view" class="view-section"><div style="font-size:28px; color:#1e3d2f; margin-bottom:20px; font-weight:bold;">About ❕️</div><p>Tibyan AI authentic scholar assistant.</p></div>
    </div>

    <div class="input-area">
        <textarea id="userInput" class="text-input" rows="1" placeholder="Ask a question..." oninput="this.style.height='inherit';this.style.height=this.scrollHeight+'px';"></textarea>
        <button class="send-btn" id="sendBtn" onclick="submitQuery()">
            <svg viewBox="0 0 24 24"><path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"></path></svg>
        </button>
    </div>

    <script>
        function toggleSidebar() {
            document.getElementById('sidebar').classList.toggle('open');
            document.getElementById('overlay').classList.toggle('active');
        }
        function switchView(viewName) {
            document.querySelectorAll('.view-section').forEach(el => el.classList.remove('active-view'));
            document.getElementById(viewName + '-view').classList.add('active-view');
            toggleSidebar();
        }
        function startNewChat() {
            document.getElementById('chat-history').innerHTML = '';
            const ws = document.getElementById('welcome-screen');
            if(ws) ws.style.display = 'flex';
            switchView('home');
        }
        function filterChats(q) { console.log(q); }
        async function submitQuery() {
            const inputField = document.getElementById('userInput');
            const query = inputField.value.trim();
            if(!query) return;
            document.querySelectorAll('.view-section').forEach(el => el.classList.remove('active-view'));
            document.getElementById('home-view').classList.add('active-view');
            const ws = document.getElementById('welcome-screen');
            if(ws) ws.style.display = 'none';
            const historyBox = document.getElementById('chat-history');
            historyBox.innerHTML += `<div class="message-wrapper"><div class="message user-msg">${query}</div></div>`;
            inputField.value = '';
            
            const uniqueId = 'msg-' + Date.now();
            historyBox.innerHTML += `<div class="message-wrapper"><div class="message ai-msg" id="${uniqueId}">Bismillah, searching...</div></div>`;
            
            try {
                const res = await fetch('/generate', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ prompt: query })
                });
                const data = await res.json();
                document.getElementById(uniqueId).innerText = data.response || "Error";
            } catch(e) {
                document.getElementById(uniqueId).innerText = "Network error.";
            }
        }
        function sendPrompt(text) {
            document.getElementById('userInput').value = text;
            submitQuery();
        }
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/generate', methods=['POST'])
def generate():
    data = request.json
    user_prompt = data.get('prompt', '')
    ai_response = call_groq_api(user_prompt)
    return jsonify({'response': ai_response})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

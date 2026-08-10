from flask import Flask, request, jsonify, render_template_string, url_for, redirect, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import os
import requests
import re
import time
import traceback

app = Flask(__name__)
app.config['SECRET_KEY'] = 'tibyan_secure_secret_key_2026'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tibyan.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

api_key = os.environ.get("GROQ_API_KEY") or os.environ.get("GEMINI_API_KEY")

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    surname = db.Column(db.String(100), nullable=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    dob = db.Column(db.String(20), nullable=True)
    pic = db.Column(db.Text, nullable=True)

class ChatHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    chat_id = db.Column(db.String(100), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    html_content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.Float, nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

# Har request se pehle ensure karein ki tables bani hui hain
@app.before_request
def ensure_tables():
    if not getattr(app, '_database_checked', False):
        db.create_all()
        app._database_checked = True

@app.errorhandler(Exception)
def handle_exception(e):
    tb = traceback.format_exc()
    return f"""
    <div style="font-family: monospace; padding: 20px; background: #ffe6e6; color: #900; border: 2px solid #red; margin: 20px; border-radius: 8px;">
        <h2>⚠️ Application Error Caught:</h2>
        <pre>{tb}</pre>
    </div>
    """, 500

def call_groq_api(prompt_text, image_data=None):
    if not api_key:
        return "Error: API Key is missing. Please set GROQ_API_KEY in Render environment variables."
        
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    
    messages = [
        {
            "role": "system", 
            "content": "You are Tibyan AI, a knowledgeable and respectful Muslim scholar assistant adhering to Hanafi Fiqh. Use clear markdown headings with double asterisks like **Heading** for main sections."
        }
    ]
    
    if image_data:
        messages.append({
            "role": "user",
            "content": [
                {"type": "text", "text": prompt_text if prompt_text else "Explain this image from an Islamic perspective."},
                {"type": "image_url", "image_url": {"url": image_data}}
            ]
        })
        model_name = "llama-3.2-11b-vision-preview"
    else:
        messages.append({"role": "user", "content": prompt_text})
        model_name = "llama-3.3-70b-versatile"

    payload = {
        "model": model_name,
        "messages": messages,
        "temperature": 0.7
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        if response.status_code == 200:
            return response.json()['choices'][0]['message']['content']
        else:
            return f"API Error ({response.status_code}): {response.text}"
    except Exception as e:
        return f"Exception occurred while contacting API: {str(e)}"

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Tibyan AI - Authentic Islamic Knowledge</title>
    <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }
        body { background-color: #ffffff; color: #111; display: flex; flex-direction: column; height: 100vh; overflow: hidden; font-size: 17px; }
        header { display: flex; align-items: center; justify-content: space-between; padding: 12px 20px; border-bottom: 1px solid #eaeaea; background: #fff; z-index: 1000; flex-shrink: 0; position: fixed; top: 0; left: 0; width: 100%; }
        .header-left { display: flex; align-items: center; gap: 15px; }
        .menu-btn { background: none; border: none; font-size: 26px; cursor: pointer; color: #1e3d2f; z-index: 1001; padding: 4px 8px; }
        .logo-img { height: 35px; width: auto; display: block; mix-blend-mode: multiply; }
        .sidebar { position: fixed; top: 0; left: -280px; width: 280px; height: 100%; background: #fff; box-shadow: 2px 0 10px rgba(0,0,0,0.1); transition: 0.3s ease; z-index: 9999; display: flex; flex-direction: column; }
        .sidebar.open { left: 0; }
        .sidebar-header { padding: 20px; font-size: 20px; font-weight: bold; color: #1e3d2f; border-bottom: 1px solid #eaeaea; display: flex; justify-content: space-between; align-items: center; }
        .close-sidebar { background: none; border: none; font-size: 20px; cursor: pointer; color: #555; }
        .sidebar-search-box { padding: 12px 16px; border-bottom: 1px solid #eaeaea; }
        .sidebar-search { width: 100%; padding: 10px 14px; border: 1px solid #ddd; border-radius: 8px; font-size: 15px; outline: none; background: #f9f9f9; }
        .sidebar-menu { list-style: none; padding: 10px 0; overflow-y: auto; flex: 1; border-bottom: 1px solid #eaeaea; }
        .sidebar-menu li { padding: 14px 20px; font-size: 17px; color: #333; cursor: pointer; display: flex; align-items: center; gap: 14px; transition: 0.2s; border-bottom: 1px solid #f7f7f7; }
        .sidebar-menu li:hover { background: #f0f4f1; color: #1e3d2f; font-weight: 500; }
        .sidebar-menu li a { text-decoration: none; color: inherit; width: 100%; display: flex; align-items: center; gap: 14px; }
        .chat-history-section { padding: 15px; overflow-y: auto; flex: 1; max-height: 40vh; }
        .history-title { font-size: 13px; text-transform: uppercase; color: #777; font-weight: bold; margin-bottom: 10px; letter-spacing: 0.5px; }
        .history-item { padding: 10px 12px; font-size: 15px; font-weight: 600; color: #222; background: #f9f9f9; border-radius: 8px; margin-bottom: 8px; cursor: pointer; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; border: 1px solid #eee; transition: 0.2s; position: relative; user-select: none; }
        .history-item:hover { background: #f0f4f1; border-color: #d0ded4; color: #1e3d2f; }
        .overlay { position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.4); display: none; z-index: 998; }
        .overlay.active { display: block; }
        .main-content { flex: 1; display: flex; flex-direction: column; overflow: hidden; position: relative; margin-top: 60px; }
        .view-section { display: none; flex: 1; overflow-y: auto; padding: 20px 20px 100px 20px; max-width: 800px; width: 100%; margin: 0 auto; scroll-behavior: smooth; }
        .view-section.active-view { display: flex; flex-direction: column; }
        .welcome-section { display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center; margin: auto 0; width: 100%; padding: 25px 20px; background: linear-gradient(180deg, rgba(240,244,241,0.6) 0%, rgba(255,255,255,1) 100%); border-radius: 24px; border: 1px solid #e2ece4; }
        .tibyan-logo-icon { width: 85px; height: 85px; display: flex; align-items: center; justify-content: center; margin-bottom: 12px; }
        .tibyan-logo-icon img { width: 100%; height: 100%; object-fit: contain; mix-blend-mode: multiply; }
        .welcome-title { font-size: 32px; color: #1e3d2f; font-weight: bold; margin-bottom: 25px; line-height: 1.3; }
        .suggestions { width: 100%; display: flex; flex-direction: column; align-items: center; gap: 10px; max-width: 550px; margin: 0 auto; }
        .suggestions-row { display: flex; justify-content: center; gap: 10px; width: 100%; }
        .suggestion-chip { background: #fff; border: 1px solid #d0ded4; border-radius: 30px; padding: 12px 18px; font-size: 15px; color: #1e3d2f; cursor: pointer; text-align: center; box-shadow: 0 2px 5px rgba(30,61,47,0.03); transition: 0.2s; flex: 1; }
        .suggestion-chip:hover { border-color: #1e3d2f; background: #f0f4f1; }
        #chat-history { width: 100%; display: flex; flex-direction: column; gap: 18px; padding-bottom: 40px; }
        .message-wrapper { display: flex; flex-direction: column; width: 100%; margin-bottom: 12px; position: relative; }
        .message { padding: 16px 20px; border-radius: 14px; max-width: 85%; line-height: 1.6; font-size: 17px; text-align: left; }
        .user-msg { background: #f0f4f1; color: #1e3d2f; align-self: flex-end; margin-left: auto; white-space: pre-wrap; }
        .ai-msg { background: #ffffff; border: 1px solid #e0e0e0; color: #222; align-self: flex-start; width: 100%; max-width: 100%; }
        .ai-msg strong { font-weight: 800; color: #1e3d2f; font-size: 19px; display: block; margin-top: 16px; margin-bottom: 8px; border-left: 3px solid #1e3d2f; padding-left: 8px; }
        .library-grid { display: grid; grid-template-columns: 1fr; gap: 12px; }
        .library-card { background: #fff; border: 1px solid #e0e0e0; border-radius: 10px; padding: 16px 20px; font-size: 18px; font-weight: 500; color: #1e3d2f; cursor: pointer; display: flex; align-items: center; justify-content: space-between; }
        .profile-container { background: #fff; border: 1px solid #e0e0e0; border-radius: 12px; padding: 24px; max-width: 500px; margin: 10px auto; }
        .profile-pic-wrapper { display: flex; flex-direction: column; align-items: center; margin-bottom: 20px; }
        .profile-preview { width: 90px; height: 90px; border-radius: 50%; object-fit: cover; border: 2px solid #1e3d2f; background: #f0f4f1; display: flex; align-items: center; justify-content: center; font-size: 36px; color: #1e3d2f; overflow: hidden; }
        .profile-preview img { width: 100%; height: 100%; object-fit: cover; }
        .file-input-label { background: #f0f4f1; color: #1e3d2f; padding: 8px 16px; border-radius: 20px; font-size: 14px; cursor: pointer; font-weight: 500; border: 1px solid #d0ded4; }
        .form-group { margin-bottom: 16px; }
        .form-label { display: block; font-size: 15px; font-weight: 500; color: #333; margin-bottom: 6px; }
        .form-control { width: 100%; padding: 12px 16px; border: 1px solid #ddd; border-radius: 8px; font-size: 16px; outline: none; background: #f9f9f9; }
        .save-profile-btn { background: #1e3d2f; color: white; border: none; border-radius: 8px; padding: 12px; width: 100%; font-size: 16px; font-weight: bold; cursor: pointer; margin-top: 10px; }
        .input-area { display: flex; flex-direction: column; padding: 10px 16px calc(20px + env(safe-area-inset-bottom, 25px)) 16px; border-top: 1px solid #eaeaea; background: #fff; max-width: 800px; width: 100%; margin: 0 auto; flex-shrink: 0; gap: 8px; z-index: 20; position: relative; bottom: 45px; box-shadow: 0 -4px 10px rgba(0,0,0,0.03); }
        .input-top-row { display: flex; align-items: center; gap: 10px; width: 100%; }
        .text-input { flex: 1; border: 1px solid #e0e0e0; border-radius: 24px; padding: 12px 18px; font-size: 16px; outline: none; background: #f9f9f9; resize: none; max-height: 150px; }
        .action-icon-btn { background: none; border: none; cursor: pointer; font-size: 22px; color: #1e3d2f; display: flex; align-items: center; justify-content: center; padding: 8px; }
        .send-btn { background: #1e3d2f; border: none; border-radius: 50%; width: 48px; height: 48px; min-width: 48px; display: flex; align-items: center; justify-content: center; cursor: pointer; color: white; font-size: 26px; font-weight: bold; }
        .image-preview-bar { display: none; align-items: center; gap: 10px; padding: 6px 12px; background: #f0f4f1; border-radius: 8px; width: fit-content; }
        .image-preview-bar img { width: 40px; height: 40px; border-radius: 6px; object-fit: cover; }
        .remove-img-btn { background: none; border: none; color: #d9534f; font-weight: bold; cursor: pointer; font-size: 16px; }
    </style>
</head>
<body>
    <header>
        <div class="header-left">
            <button class="menu-btn" onclick="toggleSidebar()">☰</button>
            <img src="{{ url_for('static', filename='logo.png') }}" alt="Tibyan AI" class="logo-img">
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
            <li><a href="/logout" style="color: #d9534f;">🚪 Logout</a></li>
        </ul>
        <div class="chat-history-section">
            <div class="history-title">Recent Chats</div>
            <div id="sidebarHistoryList"><div style="font-size: 14px; color: #888;">No past chats yet.</div></div>
        </div>
    </div>

    <div class="main-content">
        <div id="home-view" class="view-section active-view">
            <div id="chat-box" style="width: 100%;">
                <div class="welcome-section" id="welcome-screen">
                    <div class="tibyan-logo-icon"><img src="{{ url_for('static', filename='logo.png') }}" alt="Tibyan Logo"></div>
                    <div class="welcome-title" id="welcomeTitle">What's next, {{ user.name }}?</div>
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
            <div style="font-size:28px; color:#1e3d2f; margin-bottom:20px; font-weight:bold;">Islamic Library 📚</div>
            <div class="library-grid">
                <div class="library-card" onclick="sendPrompt('Tell me about Qur\'an sciences.')">📖 Qur'an</div>
                <div class="library-card" onclick="sendPrompt('Explain Hadith collections.')">🏷️ Hadith</div>
                <div class="library-card" onclick="sendPrompt('Explain Fiqh according to Hanafi school.')">⚖️ Fiqh</div>
            </div>
        </div>

        <div id="saved-view" class="view-section">
            <div style="font-size:28px; color:#1e3d2f; margin-bottom:20px; font-weight:bold;">Saved Chats 📜</div>
            <div id="saved-chats-list"><p style="color: #666; font-size: 15px;">No saved responses yet.</p></div>
        </div>
        
        <div id="profile-view" class="view-section">
            <div style="font-size:28px; color:#1e3d2f; margin-bottom:15px; font-weight:bold;">Profile 👤</div>
            <div class="profile-container">
                <div class="profile-pic-wrapper">
                    <div class="profile-preview" id="profilePicPreview">{% if user.pic %}<img src="{{ user.pic }}" alt="Profile">{% else %}👤{% endif %}</div>
                    <label class="file-input-label" for="profilePicInput">Choose Profile Picture</label>
                    <input type="file" id="profilePicInput" accept="image/*" style="display:none;" onchange="previewProfileImage(event)">
                </div>
                <div class="form-group"><label class="form-label">Name</label><input type="text" id="profileName" class="form-control" value="{{ user.name }}"></div>
                <div class="form-group"><label class="form-label">Surname</label><input type="text" id="profileSurname" class="form-control" value="{{ user.surname or '' }}"></div>
                <div class="form-group"><label class="form-label">Email</label><input type="email" class="form-control" value="{{ user.email }}" disabled style="background:#eee;"></div>
                <div class="form-group"><label class="form-label">D.O.B</label><input type="date" id="profileDob" class="form-control" value="{{ user.dob or '' }}"></div>
                <button class="save-profile-btn" onclick="saveProfileData()">Save Profile</button>
            </div>
        </div>

        <div id="about-view" class="view-section"><div style="font-size:28px; color:#1e3d2f; margin-bottom:20px; font-weight:bold;">About ❕️</div><p>Tibyan AI authentic scholar assistant.</p></div>
    </div>

    <div class="input-area">
        <div class="image-preview-bar" id="imagePreviewBar">
            <img id="thumbPreview" src="" alt="preview">
            <span id="thumbName" style="font-size: 14px; color: #333;">Image attached</span>
            <button class="remove-img-btn" onclick="removeAttachedImage()">×</button>
        </div>
        <div class="input-top-row">
            <label class="action-icon-btn" title="Upload Image">📎<input type="file" id="chatImageInput" accept="image/*" style="display:none;" onchange="handleChatImageUpload(event)"></label>
            <textarea id="userInput" class="text-input" rows="1" placeholder="Ask Tibyan..." oninput="this.style.height='inherit';this.style.height=this.scrollHeight+'px';"></textarea>
            <button class="send-btn" id="sendBtn" onclick="submitQuery()" title="Send">↑</button>
        </div>
    </div>

    <script>
        let uploadedImageBase64 = "{{ user.pic or '' }}";
        let currentChatId = 'chat_' + Date.now();
        let currentChatTitle = "";
        let chatImageBase64 = null;

        function toggleSidebar() { document.getElementById('sidebar').classList.toggle('open'); document.getElementById('overlay').classList.toggle('active'); }
        function switchView(viewName) { document.querySelectorAll('.view-section').forEach(el => el.classList.remove('active-view')); document.getElementById(viewName + '-view').classList.add('active-view'); toggleSidebar(); }
        function startNewChat() { currentChatId = 'chat_' + Date.now(); currentChatTitle = ""; document.getElementById('chat-history').innerHTML = ''; const ws = document.getElementById('welcome-screen'); if(ws) ws.style.display = 'flex'; switchView('home'); }

        async function saveCurrentChat(title, historyHtml) {
            if(!currentChatTitle) currentChatTitle = title;
            await fetch('/save_chat', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ chat_id: currentChatId, title: currentChatTitle, html: historyHtml }) });
            loadSidebarHistory();
        }

        async function loadSidebarHistory(filterQuery = '') {
            const res = await fetch('/get_chats');
            const chats = await res.json();
            const listContainer = document.getElementById('sidebarHistoryList');
            let keys = Object.keys(chats).sort((a,b) => chats[b].time - chats[a].time);
            if(keys.length === 0) { listContainer.innerHTML = '<div style="font-size: 14px; color: #888;">No past chats yet.</div>'; return; }
            let html = '';
            keys.forEach(k => {
                let chat = chats[k];
                if(!filterQuery || chat.title.toLowerCase().includes(filterQuery.toLowerCase())) {
                    html += `<div class="history-item" onclick="loadSpecificChat('${k}')"><span>${chat.title}</span></div>`;
                }
            });
            listContainer.innerHTML = html;
        }

        async function loadSpecificChat(chatId) {
            const res = await fetch('/get_chats');
            const chats = await res.json();
            if(chats[chatId]) {
                currentChatId = chatId;
                currentChatTitle = chats[chatId].title;
                document.getElementById('chat-history').innerHTML = chats[chatId].html;
                const ws = document.getElementById('welcome-screen');
                if(ws) ws.style.display = 'none';
                switchView('home');
            }
        }

        async function submitQuery() {
            const inputField = document.getElementById('userInput');
            const query = inputField.value.trim();
            const currentImg = chatImageBase64;
            if(!query && !currentImg) return;
            document.querySelectorAll('.view-section').forEach(el => el.classList.remove('active-view'));
            document.getElementById('home-view').classList.add('active-view');
            const ws = document.getElementById('welcome-screen');
            if(ws) ws.style.display = 'none';
            const historyBox = document.getElementById('chat-history');
            let userHtml = `<div class="message-wrapper"><div class="message user-msg">`;
            if(currentImg) userHtml += `<img src="${currentImg}" style="max-width:150px; border-radius:8px; display:block; margin-bottom:8px;">`;
            if(query) userHtml += `<div>${query}</div>`;
            userHtml += `</div></div>`;
            historyBox.innerHTML += userHtml;
            inputField.value = '';
            inputField.style.height = 'inherit';
            removeAttachedImage();
            const uniqueId = 'msg-' + Date.now();
            historyBox.innerHTML += `<div class="message-wrapper"><div class="message ai-msg" id="${uniqueId}">Bismillah, analyzing...</div></div>`;
            window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' });
            try {
                const res = await fetch('/generate', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ prompt: query, image: currentImg }) });
                const data = await res.json();
                document.getElementById(uniqueId).innerHTML = marked.parse(data.response || "Error");
                window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' });
                saveCurrentChat(query.substring(0, 30) || "Image Query", historyBox.innerHTML);
            } catch(e) {
                document.getElementById(uniqueId).innerText = "Network error.";
            }
        }

        function sendPrompt(text) { document.getElementById('userInput').value = text; submitQuery(); }
        window.onload = function() { loadSidebarHistory(); };

        function previewProfileImage(event) {
            const file = event.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function(e) { uploadedImageBase64 = e.target.result; document.getElementById('profilePicPreview').innerHTML = `<img src="${uploadedImageBase64}" alt="Profile">`; }
                reader.readAsDataURL(file);
            }
        }

        async function saveProfileData() {
            const name = document.getElementById('profileName').value;
            const surname = document.getElementById('profileSurname').value;
            const dob = document.getElementById('profileDob').value;
            await fetch('/update_profile', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ name: name, surname: surname, dob: dob, pic: uploadedImageBase64 }) });
            document.getElementById('welcomeTitle').innerText = "What's next, " + name.trim() + "?";
            alert("Profile updated successfully!");
        }

        function handleChatImageUpload(event) {
            const file = event.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function(e) { chatImageBase64 = e.target.result; document.getElementById('thumbPreview').src = chatImageBase64; document.getElementById('imagePreviewBar').style.display = 'flex'; }
                reader.readAsDataURL(file);
            }
        }
        function removeAttachedImage() { chatImageBase64 = null; document.getElementById('imagePreviewBar').style.display = 'none'; document.getElementById('chatImageInput').value = ''; }
    </script>
</body>
</html>
"""

AUTH_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ title }} - Tibyan AI</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }
        body { background: #f0f4f1; display: flex; align-items: center; justify-content: center; min-height: 100vh; padding: 20px; }
        .auth-card { background: #fff; padding: 30px; border-radius: 16px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); width: 100%; max-width: 400px; border: 1px solid #d0ded4; }
        .auth-title { font-size: 26px; color: #1e3d2f; font-weight: bold; margin-bottom: 20px; text-align: center; }
        .form-group { margin-bottom: 16px; }
        .form-label { display: block; font-size: 14px; font-weight: 500; color: #333; margin-bottom: 6px; }
        .form-control { width: 100%; padding: 12px 16px; border: 1px solid #ddd; border-radius: 8px; font-size: 16px; outline: none; background: #f9f9f9; }
        .auth-btn { background: #1e3d2f; color: white; border: none; border-radius: 8px; padding: 12px; width: 100%; font-size: 16px; font-weight: bold; cursor: pointer; margin-top: 10px; }
        .auth-link { text-align: center; margin-top: 15px; font-size: 14px; color: #555; }
        .auth-link a { color: #1e3d2f; text-decoration: none; font-weight: bold; }
        .flash-msg { background: #ffe6e6; color: #d9534f; padding: 10px; border-radius: 6px; margin-bottom: 15px; font-size: 14px; text-align: center; }
    </style>
</head>
<body>
    <div class="auth-card">
        <div class="auth-title">{{ title }}</div>
        {% with messages = get_flashed_messages() %}
          {% if messages %}<div class="flash-msg">{{ messages[0] }}</div>{% endif %}
        {% endwith %}
        <form method="POST">
            {% if is_signup %}
            <div class="form-group"><label class="form-label">Name</label><input type="text" name="name" class="form-control" required></div>
            <div class="form-group"><label class="form-label">Surname</label><input type="text" name="surname" class="form-control"></div>
            {% endif %}
            <div class="form-group"><label class="form-label">Email</label><input type="email" name="email" class="form-control" required></div>
            <div class="form-group"><label class="form-label">Password</label><input type="password" name="password" class="form-control" required></div>
            {% if is_signup %}
            <div class="form-group"><label class="form-label">Confirm Password</label><input type="password" name="confirm_password" class="form-control" required></div>
            {% endif %}
            <button type="submit" class="auth-btn">{{ title }}</button>
        </form>
        <div class="auth-link">
            {% if is_signup %}Already have an account? <a href="{{ url_for('login') }}">Login</a>{% else %}Don't have an account? <a href="{{ url_for('signup') }}">Sign Up</a>{% endif %}
        </div>
    </div>
</body>
</html>
"""

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('home'))
        flash('Invalid email or password!')
    return render_template_string(AUTH_TEMPLATE, title='Login', is_signup=False)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form.get('name')
        surname = request.form.get('surname')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if password != confirm_password:
            flash('Passwords do not match!')
            return redirect(url_for('signup'))

        user_exists = User.query.filter_by(email=email).first()
        if user_exists:
            flash('Email address already registered!')
            return redirect(url_for('signup'))
            
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        new_user = User(name=name, surname=surname, email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        return redirect(url_for('home'))
    return render_template_string(AUTH_TEMPLATE, title='Sign Up', is_signup=True)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/')
@login_required
def home():
    return render_template_string(HTML_TEMPLATE, user=current_user)

@app.route('/generate', methods=['POST'])
@login_required
def generate():
    data = request.json or {}
    ai_response = call_groq_api(data.get('prompt', ''), data.get('image', None))
    return jsonify({'response': ai_response})

@app.route('/save_chat', methods=['POST'])
@login_required
def save_chat():
    data = request.json or {}
    c_id = data.get('chat_id')
    if not c_id: return jsonify({'status': 'error'}), 400
    chat = ChatHistory.query.filter_by(user_id=current_user.id, chat_id=c_id).first()
    if chat:
        chat.title = data.get('title')
        chat.html_content = data.get('html')
        chat.timestamp = time.time()
    else:
        new_chat = ChatHistory(user_id=current_user.id, chat_id=c_id, title=data.get('title'), html_content=data.get('html'), timestamp=time.time())
        db.session.add(new_chat)
    db.session.commit()
    return jsonify({'status': 'success'})

@app.route('/get_chats', methods=['GET'])
@login_required
def get_chats():
    chats = ChatHistory.query.filter_by(user_id=current_user.id).all()
    return jsonify({c.chat_id: {'title': c.title, 'html': c.html_content, 'time': c.timestamp} for c in chats})

@app.route('/update_profile', methods=['POST'])
@login_required
def update_profile():
    data = request.json or {}
    current_user.name = data.get('name', current_user.name)
    current_user.surname = data.get('surname', current_user.surname)
    current_user.dob = data.get('dob', current_user.dob)
    current_user.pic = data.get('pic', current_user.pic)
    db.session.commit()
    return jsonify({'status': 'success'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)


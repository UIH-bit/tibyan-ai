from flask import Flask, request, jsonify, render_template_string, url_for, redirect, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import os
import requests
import re

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

def call_groq_api(prompt_text, image_data=None):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    
    messages = [
        {
            "role": "system", 
            "content": "You are Tibyan AI, a knowledgeable and respectful Muslim scholar assistant adhering to Hanafi Fiqh (Deoband/Banuri Town manhaj). Use clear markdown headings with double asterisks like **Heading** for main sections."
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
            return f"Error: {response.text}"
    except Exception as e:
        return f"Exception: {str(e)}"

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
        
        .chat-context-menu { display: none; position: absolute; right: 10px; top: 50%; transform: translateY(-50%); background: #fff; border: 1px solid #ddd; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.15); z-index: 100; overflow: hidden; }
        .chat-context-menu.show { display: flex; gap: 5px; padding: 4px; }
        .ctx-btn { background: #f0f4f1; border: none; border-radius: 4px; padding: 6px 10px; font-size: 13px; font-weight: bold; color: #1e3d2f; cursor: pointer; }
        .ctx-btn:hover { background: #e2ece4; }
        .ctx-btn.delete { color: #d9534f; }
        
        .overlay { position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.4); display: none; z-index: 998; }
        .overlay.active { display: block; }

        .main-content { flex: 1; display: flex; flex-direction: column; overflow: hidden; position: relative; margin-top: 60px; }
        .view-section { display: none; flex: 1; overflow-y: auto; padding: 20px 20px 100px 20px; max-width: 800px; width: 100%; margin: 0 auto; scroll-behavior: smooth; }
        .view-section.active-view { display: flex; flex-direction: column; }

        .chat-container { justify-content: flex-start; }
        
        .welcome-section { display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center; margin: auto 0; width: 100%; padding: 25px 20px; background: linear-gradient(180deg, rgba(240,244,241,0.6) 0%, rgba(255,255,255,1) 100%); border-radius: 24px; border: 1px solid #e2ece4; }
        
        .tibyan-logo-icon { width: 85px; height: 85px; display: flex; align-items: center; justify-content: center; margin-bottom: 12px; background: transparent; }
        .tibyan-logo-icon img { width: 100%; height: 100%; object-fit: contain; mix-blend-mode: multiply; }
        
        .welcome-title { font-size: 32px; color: #1e3d2f; font-weight: bold; margin-bottom: 25px; line-height: 1.3; }
        
        .suggestions { width: 100%; display: flex; flex-direction: column; align-items: center; gap: 10px; max-width: 550px; margin: 0 auto; }
        .suggestions-row { display: flex; justify-content: center; gap: 10px; width: 100%; }
        .suggestion-chip { background: #fff; border: 1px solid #d0ded4; border-radius: 30px; padding: 12px 18px; font-size: 15px; color: #1e3d2f; cursor: pointer; text-align: center; box-shadow: 0 2px 5px rgba(30,61,47,0.03); transition: 0.2s; flex: 1; }
        .suggestion-chip:hover { border-color: #1e3d2f; background: #f0f4f1; }
        .suggestion-center { max-width: 320px; width: 100%; }

        #chat-history { width: 100%; display: flex; flex-direction: column; gap: 18px; padding-bottom: 40px; }
        .message-wrapper { display: flex; flex-direction: column; width: 100%; margin-bottom: 12px; position: relative; }
        .message { padding: 16px 20px; border-radius: 14px; max-width: 85%; line-height: 1.6; font-size: 17px; text-align: left; unicode-bidi: plaintext; }
        .user-msg { background: #f0f4f1; color: #1e3d2f; align-self: flex-end; margin-left: auto; text-align: left; white-space: pre-wrap; }
        
        .ai-msg { background: #ffffff; border: 1px solid #e0e0e0; color: #222; align-self: flex-start; width: 100%; max-width: 100%; }
        .ai-msg strong, .ai-msg b { font-weight: 800; color: #1e3d2f; font-size: 19px; display: block; margin-top: 16px; margin-bottom: 8px; letter-spacing: 0.3px; border-left: 3px solid #1e3d2f; padding-left: 8px; }
        .ai-msg p { margin-bottom: 10px; line-height: 1.7; }
        .ai-msg ul, .ai-msg ol { padding-left: 20px; margin-bottom: 10px; }
        .ai-msg li { margin-bottom: 6px; line-height: 1.6; }
        
        .ai-actions { display: flex; gap: 10px; margin-top: 8px; align-self: flex-start; padding-left: 4px; align-items: center; }
        .action-btn { background: #f9f9f9; border: 1px solid #ddd; border-radius: 8px; font-size: 14px; color: #444; cursor: pointer; padding: 6px 12px; display: flex; align-items: center; gap: 5px; transition: 0.2s; }
        .action-btn:hover { background: #f0f4f1; color: #1e3d2f; border-color: #1e3d2f; }
        .action-btn.active { background: #f0f4f1; color: #1e3d2f; border-color: #1e3d2f; font-weight: bold; }
        
        .dropdown-container { position: relative; display: inline-block; }
        .dropdown-menu { display: none; position: absolute; bottom: 100%; left: 0; background: #fff; border: 1px solid #ddd; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.15); z-index: 50; min-width: 120px; overflow: hidden; margin-bottom: 5px; }
        .dropdown-menu.show { display: block; }
        .dropdown-item { padding: 10px 16px; font-size: 14px; color: #333; cursor: pointer; display: block; text-align: left; transition: 0.2s; }
        .dropdown-item:hover { background: #f0f4f1; color: #1e3d2f; }

        .library-grid { display: grid; grid-template-columns: 1fr; gap: 12px; padding-bottom: 20px; }
        .library-card { background: #fff; border: 1px solid #e0e0e0; border-radius: 10px; padding: 16px 20px; font-size: 18px; font-weight: 500; color: #1e3d2f; cursor: pointer; box-shadow: 0 2px 4px rgba(0,0,0,0.02); transition: 0.2s; display: flex; align-items: center; justify-content: space-between; }
        .library-card:hover { background: #f0f4f1; border-color: #1e3d2f; }

        .profile-container { background: #fff; border: 1px solid #e0e0e0; border-radius: 12px; padding: 24px; max-width: 500px; margin: 10px auto; box-shadow: 0 2px 8px rgba(0,0,0,0.02); }
        .profile-pic-wrapper { display: flex; flex-direction: column; align-items: center; margin-bottom: 20px; }
        .profile-preview { width: 90px; height: 90px; border-radius: 50%; object-fit: cover; border: 2px solid #1e3d2f; background: #f0f4f1; display: flex; align-items: center; justify-content: center; font-size: 36px; color: #1e3d2f; margin-bottom: 10px; overflow: hidden; }
        .profile-preview img { width: 100%; height: 100%; object-fit: cover; }
        .file-input-label { background: #f0f4f1; color: #1e3d2f; padding: 8px 16px; border-radius: 20px; font-size: 14px; cursor: pointer; font-weight: 500; border: 1px solid #d0ded4; transition: 0.2s; }
        .file-input-label:hover { background: #e2ece4; }
        .form-group { margin-bottom: 16px; }
        .form-label { display: block; font-size: 15px; font-weight: 500; color: #333; margin-bottom: 6px; }
        .form-control { width: 100%; padding: 12px 16px; border: 1px solid #ddd; border-radius: 8px; font-size: 16px; outline: none; background: #f9f9f9; }
        .form-control:focus { border-color: #1e3d2f; background: #fff; }
        .save-profile-btn { background: #1e3d2f; color: white; border: none; border-radius: 8px; padding: 12px; width: 100%; font-size: 16px; font-weight: bold; cursor: pointer; transition: 0.2s; margin-top: 10px; }
        .save-profile-btn:hover { background: #152b21; }

        .input-area { display: flex; flex-direction: column; padding: 10px 16px calc(20px + env(safe-area-inset-bottom, 25px)) 16px; border-top: 1px solid #eaeaea; background: #fff; max-width: 800px; width: 100%; margin: 0 auto; flex-shrink: 0; gap: 8px; z-index: 20; position: relative; bottom: 45px; box-shadow: 0 -4px 10px rgba(0,0,0,0.03); }
        .input-top-row { display: flex; align-items: center; gap: 10px; width: 100%; }
        .text-input { flex: 1; border: 1px solid #e0e0e0; border-radius: 24px; padding: 12px 18px; font-size: 16px; outline: none; background: #f9f9f9; resize: none; max-height: 150px; overflow-y: auto; line-height: 1.5; text-align: left; unicode-bidi: plaintext; }
        
        .action-icon-btn { background: none; border: none; cursor: pointer; font-size: 22px; color: #1e3d2f; display: flex; align-items: center; justify-content: center; padding: 8px; transition: 0.2s; }
        .action-icon-btn:hover { opacity: 0.7; }
        
        .send-btn { background: #1e3d2f; border: none; border-radius: 50%; width: 48px; height: 48px; min-width: 48px; display: flex; align-items: center; justify-content: center; cursor: pointer; color: white; transition: 0.2s; box-shadow: 0 2px 6px rgba(0,0,0,0.15); font-size: 26px; font-weight: bold; }
        .send-btn:hover { background: #152b21; }

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
            <div id="sidebarHistoryList">
                <div style="font-size: 14px; color: #888;">No past chats yet.</div>
            </div>
        </div>
    </div>

    <div class="main-content">
        <div id="home-view" class="view-section active-view chat-container">
            <div id="chat-box" style="width: 100%;">
                <div class="welcome-section" id="welcome-screen">
                    <div class="tibyan-logo-icon">
                        <img src="{{ url_for('static', filename='logo.png') }}" alt="Tibyan Logo">
                    </div>
                    <div class="welcome-title" id="welcomeTitle">What's next, {{ user.name }}?</div>
                    <div class="suggestions">
                        <div class="suggestions-row">
                            <div class="suggestion-chip" onclick="sendPrompt('What does the Quran say about patience (Sabr)?')">What does the Quran say about patience (Sabr)?</div>
                            <div class="suggestion-chip" onclick="sendPrompt('Roza kaise toot jata hai')">Roza kaise toot jata hai</div>
                        </div>
                        <div class="suggestions-row">
                            <div class="suggestion-chip suggestion-center" onclick="sendPrompt('Hanafi fiqh ke mutabiq namaz ka tareeqa')">Hanafi fiqh ke mutabiq namaz ka tareeqa</div>
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

        <div id="saved-view" class="view-section">
            <div style="font-size:28px; color:#1e3d2f; margin-bottom:20px; font-weight:bold;">Saved Chats 📜</div>
            <div id="saved-chats-list"><p style="color: #666; font-size: 15px;">No saved responses yet.</p></div>
        </div>
        
        <div id="profile-view" class="view-section">
            <div style="font-size:28px; color:#1e3d2f; margin-bottom:15px; font-weight:bold;">Profile 👤</div>
            <div class="profile-container">
                <div class="profile-pic-wrapper">
                    <div class="profile-preview" id="profilePicPreview">
                        {% if user.pic %}<img src="{{ user.pic }}" alt="Profile">{% else %}👤{% endif %}
                    </div>
                    <label class="file-input-label" for="profilePicInput">Choose Profile Picture</label>
                    <input type="file" id="profilePicInput" accept="image/*" style="display:none;" onchange="previewProfileImage(event)">
                </div>
                <div class="form-group">
                    <label class="form-label">Name</label>
                    <input type="text" id="profileName" class="form-control" value="{{ user.name }}">
                </div>
                <div class="form-group">
                    <label class="form-label">Surname</label>
                    <input type="text" id="profileSurname" class="form-control" value="{{ user.surname or '' }}">
                </div>
                <div class="form-group">
                    <label class="form-label">Email</label>
                    <input type="email" class="form-control" value="{{ user.email }}" disabled style="background:#eee;">
                </div>
                <div class="form-group">
                    <label class="form-label">Date of Birth (D.O.B)</label>
                    <input type="date" id="profileDob" class="form-control" value="{{ user.dob or '' }}">
                </div>
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
            <label class="action-icon-btn" title="Upload Image">
                📎
                <input type="file" id="chatImageInput" accept="image/*" style="display:none;" onchange="handleChatImageUpload(event)">
            </label>
            <textarea id="userInput" class="text-input" rows="1" placeholder="Ask Tibyan..." oninput="this.style.height='inherit';this.style.height=this.scrollHeight+'px';"></textarea>
            <button class="send-btn" id="sendBtn" onclick="submitQuery()" title="Send">↑</button>
        </div>
    </div>

    <script>
        let uploadedImageBase64 = "{{ user.pic or '' }}";
        let currentChatId = 'chat_' + Date.now();
        let currentChatTitle = "";

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
            currentChatId = 'chat_' + Date.now();
            currentChatTitle = "";
            document.getElementById('chat-history').innerHTML = '';
            const ws = document.getElementById('welcome-screen');
            if(ws) ws.style.display = 'flex';
            switchView('home');
        }

        async function saveCurrentChat(title, historyHtml) {
            if(!currentChatTitle) {
                currentChatTitle = title;
            }
            await fetch('/save_chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ chat_id: currentChatId, title: currentChatTitle, html: historyHtml })
            });
            loadSidebarHistory();
        }

        async function loadSidebarHistory(filterQuery = '') {
            const res = await fetch('/get_chats');
            const chats = await res.json();
            const listContainer = document.getElementById('sidebarHistoryList');
            
            let keys = Object.keys(chats).sort((a,b) => chats[b].time - chats[a].time);
            
            if(keys.length === 0) {
                listContainer.innerHTML = '<div style="font-size: 14px; color: #888;">No past chats yet.</div>';
                return;
            }

            let html = '';
            keys.forEach(k => {
                let chat = chats[k];
                if(!filterQuery || chat.title.toLowerCase().includes(filterQuery.toLowerCase())) {
                    html += `
                        <div class="history-item" onclick="loadSpecificChat('${k}')" oncontextmenu="openChatContext('${k}', event)" ontouchstart="handleTouchStart(event, '${k}')" ontouchend="handleTouchEnd()">
                            <span class="chat-text-span">${chat.title}</span>
                            <div class="chat-context-menu" id="ctx-${k}">
                                <button class="ctx-btn" onclick="shareSpecificChat('${k}', event)">Share</button>
                                <button class="ctx-btn delete" onclick="deleteSpecificChat('${k}', event)">Delete</button>
                            </div>
                        </div>`;
                }
            });
            listContainer.innerHTML = html || '<div style="font-size: 14px; color: #888;">No matching chats.</div>';
        }

        let pressTimer = null;
        function handleTouchStart(e, chatId) {
            pressTimer = setTimeout(() => {
                e.preventDefault();
                openChatContext(chatId, e);
            }, 600);
        }
        function handleTouchEnd() {
            clearTimeout(pressTimer);
        }

        function openChatContext(chatId, event) {
            event.preventDefault();
            event.stopPropagation();
            closeAllContextMenus();
            const menu = document.getElementById('ctx-' + chatId);
            if(menu) menu.classList.add('show');
        }

        function closeAllContextMenus() {
            document.querySelectorAll('.chat-context-menu').forEach(m => m.classList.remove('show'));
        }

        async function deleteSpecificChat(chatId, event) {
            event.stopPropagation();
            await fetch('/delete_chat/' + chatId, { method: 'DELETE' });
            loadSidebarHistory();
            if(currentChatId === chatId) {
                startNewChat();
            }
        }

        async function shareSpecificChat(chatId, event) {
            event.stopPropagation();
            const res = await fetch('/get_chats');
            const chats = await res.json();
            if(chats[chatId]) {
                const chatText = chats[chatId].title;
                if(navigator.share) {
                    navigator.share({ title: 'Tibyan Chat', text: chatText }).catch(()=>{});
                } else {
                    navigator.clipboard.writeText(chatText);
                }
            }
            closeAllContextMenus();
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

        function filterChats(q) {
            loadSidebarHistory(q);
        }

        function likeMsg(btn, id) { btn.classList.toggle('active'); }
        function dislikeMsg(btn, id) { btn.classList.toggle('active'); }

        async function saveMsg(id) {
            const content = document.getElementById(id).innerHTML;
            await fetch('/save_message', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ id: id, html: content })
            });
            loadSavedMessagesView();
        }

        async function loadSavedMessagesView() {
            const res = await fetch('/get_saved_messages');
            const savedList = await res.json();
            const container = document.getElementById('saved-chats-list');
            if(savedList.length === 0) {
                container.innerHTML = '<p style="color: #666; font-size: 15px;">No saved responses yet.</p>';
                return;
            }
            let html = '';
            savedList.forEach((item, index) => {
                html += `<div style="background:#fff; border:1px solid #e0e0e0; border-radius:10px; padding:15px; margin-bottom:12px;">
                    <div style="font-size:14px; color:#888; margin-bottom:8px;">Saved Response #${index + 1}</div>
                    <div style="font-size:16px; color:#222; line-height:1.6;">${item.html}</div>
                </div>`;
            });
            container.innerHTML = html;
        }
        
        function copyMsg(id) {
            const text = document.getElementById(id).innerText;
            navigator.clipboard.writeText(text);
            closeAllDropdowns();
        }

        function shareMsg(id) {
            const text = document.getElementById(id).innerText;
            if (navigator.share) {
                navigator.share({ title: 'Tibyan AI Response', text: text }).catch(() => {});
            } else {
                copyMsg(id);
            }
            closeAllDropdowns();
        }

        function toggleDropdown(menuId, event) {
            event.stopPropagation();
            const menu = document.getElementById(menuId);
            const isOpen = menu.classList.contains('show');
            closeAllDropdowns();
            if (!isOpen) menu.classList.add('show');
        }

        function closeAllDropdowns() {
            document.querySelectorAll('.dropdown-menu').forEach(m => m.classList.remove('show'));
        }

        window.onclick = function() {
            closeAllDropdowns();
            closeAllContextMenus();
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
            const uniqueActionsId = 'actions-' + Date.now();
            const logoMenuId = 'menu-' + Date.now();
            
            historyBox.innerHTML += `
                <div class="message-wrapper">
                    <div class="message ai-msg" id="${uniqueId}">Bismillah, analyzing...</div>
                    <div class="ai-actions" id="${uniqueActionsId}" style="display:none;">
                        <button class="action-btn" onclick="likeMsg(this, '${uniqueId}')">👍 Like</button>
                        <button class="action-btn" onclick="dislikeMsg(this, '${uniqueId}')">👎 Dislike</button>
                        <button class="action-btn" onclick="saveMsg('${uniqueId}')">📜 Save</button>
                        <div class="dropdown-container">
                            <button class="action-btn" onclick="toggleDropdown('${logoMenuId}', event)">•••</button>
                            <div class="dropdown-menu" id="${logoMenuId}">
                                <div class="dropdown-item" onclick="copyMsg('${uniqueId}')">📋 Copy</div>
                                <div class="dropdown-item" onclick="shareMsg('${uniqueId}')">🔗 Share</div>
                            </div>
                        </div>
                    </div>
                </div>`;
            
            window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' });
            
            try {
                const res = await fetch('/generate', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ prompt: query, image: currentImg })
                });
                const data = await res.json();
                
                const rawMarkdown = data.response || "Error";
                document.getElementById(uniqueId).innerHTML = marked.parse(rawMarkdown);
                document.getElementById(uniqueActionsId).style.display = "flex";
                window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' });

                saveCurrentChat(query.substring(0, 30) || "Image Query", historyBox.innerHTML);
            } catch(e) {
                document.getElementById(uniqueId).innerText = "Network error.";
                document.getElementById(uniqueActionsId).style.display = "flex";
            }
        }
        function sendPrompt(text) {
            document.getElementById('userInput').value = text;
            submitQuery();
        }

        window.onload = function() {
            loadSidebarHistory();
            loadSavedMessagesView();
        };

        function previewProfileImage(event) {
            const file = event.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    uploadedImageBase64 = e.target.result;
                    document.getElementById('profilePicPreview').innerHTML = `<img src="${uploadedImageBase64}" alt="Profile">`;
                }
                reader.readAsDataURL(file);
            }
        }

        async function saveProfileData() {
            const name = document.getElementById('profileName').value;
            const surname = document.getElementById('profileSurname').value;
            const dob = document.getElementById('profileDob').value;
            
            const res = await fetch('/update_profile', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ name: name, surname: surname, dob: dob, pic: uploadedImageBase64 })
            });
            if(res.ok) {
                document.getElementById('welcomeTitle').innerText = "What's next, " + name.trim() + "?";
                alert("Profile updated successfully!");
            }
        }

        let chatImageBase64 = null;
        function handleChatImageUpload(event) {
            const file = event.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    chatImageBase64 = e.target.result;
                    document.getElementById('thumbPreview').src = chatImageBase64;
                    document.getElementById('imagePreviewBar').style.display = 'flex';
                }
                reader.readAsDataURL(file);
            }
        }

        function removeAttachedImage() {
            chatImageBase64 = null;
            document.getElementById('imagePreviewBar').style.display = 'none';
            document.getElementById('chatImageInput').value = '';
        }
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
        .input-wrapper { position: relative; display: flex; align-items: center; }
        .form-control { width: 100%; padding: 12px 16px; border: 1px solid #ddd; border-radius: 8px; font-size: 16px; outline: none; background: #f9f9f9; }
        .form-control:focus { border-color: #1e3d2f; background: #fff; }
        .eye-btn { position: absolute; right: 12px; background: none; border: none; cursor: pointer; font-size: 18px; color: #666; }
        .auth-btn { background: #1e3d2f; color: white; border: none; border-radius: 8px; padding: 12px; width: 100%; font-size: 16px; font-weight: bold; cursor: pointer; transition: 0.2s; margin-top: 10px; }
        .auth-btn:hover { background: #152b21; }
        .auth-link { text-align: center; margin-top: 15px; font-size: 14px; color: #555; }
        .auth-link a { color: #1e3d2f; text-decoration: none; font-weight: bold; }
        .flash-msg { background: #ffe6e6; color: #d9534f; padding: 10px; border-radius: 6px; margin-bottom: 15px; font-size: 14px; text-align: center; }
    </style>
</head>
<body>
    <div class="auth-card">
        <div class="auth-title">{{ title }}</div>
        {% with messages = get_flashed_messages() %}
          {% if messages %}
            <div class="flash-msg">{{ messages[0] }}</div>
          {% endif %}
        {% endwith %}
        <form method="POST">
            {% if is_signup %}
            <div class="form-group">
                <label class="form-label">Name</label>
                <input type="text" name="name" class="form-control" required placeholder="Name">
            </div>
            <div class="form-group">
                <label class="form-label">Surname</label>
                <input type="text" name="surname" class="form-control" placeholder="Surname">
            </div>
            {% endif %}
            <div class="form-group">
                <label class="form-label">Email Address</label>
                <input type="email" name="email" class="form-control" required placeholder="email@example.com">
            </div>
            <div class="form-group">
                <label class="form-label">Password</label>
                <div class="input-wrapper">
                    <input type="password" name="password" id="password" class="form-control" required placeholder="********">
                    <button type="button" class="eye-btn" onclick="togglePassword('password', this)">👁️</button>
                </div>
            </div>
            {% if is_signup %}
            <div class="form-group">
                <label class="form-label">Confirm Password</label>
                <div class="input-wrapper">
                    <input type="password" name="confirm_password" id="confirm_password" class="form-control" required placeholder="********">
                    <button type="button" class="eye-btn" onclick="togglePassword('confirm_password', this)">👁️</button>
                </div>
            </div>
            {% endif %}
            <button type="submit" class="auth-btn">{{ title }}</button>
        </form>
        <div class="auth-link">
            {% if is_signup %}
                Already have an account? <a href="{{ url_for('login') }}">Login</a>
            {% else %}
                Don't have an account? <a href="{{ url_for('signup') }}">Sign Up</a>
            {% endif %}
        </div>
    </div>
    <script>
        function togglePassword(fieldId, btn) {
            const field = document.getElementById(fieldId);
            if (field.type === "password") {
                field.type = "text";
                btn.style.opacity = "1";
            } else {
                field.type = "password";
                btn.style.opacity = "0.6";
            }
        }
    </script>
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

        # Password validation: must contain letters and numbers mixture
        if not re.search(r'[A-Za-z]', password) or not re.search(r'\d', password):
            flash('Password must contain a mix of letters and numbers!')
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
    data = request.json
    user_prompt = data.get('prompt', '')
    image_data = data.get('image', None)
    ai_response = call_groq_api(user_prompt, image_data)
    return jsonify({'response': ai_response})

@app.route('/save_chat', methods=['POST'])
@login_required
def save_chat():
    data = request.json
    c_id = data.get('chat_id')
    title = data.get('title')
    html_content = data.get('html')
    
    chat = ChatHistory.query.filter_by(user_id=current_user.id, chat_id=c_id).first()
    if chat:
        chat.title = title
        chat.html_content = html_content
        chat.timestamp = db.func.now()
    else:
        new_chat = ChatHistory(user_id=current_user.id, chat_id=c_id, title=title, html_content=html_content, timestamp=os.times()[4])
        db.session.add(new_chat)
    db.session.commit()
    return jsonify({'status': 'success'})

@app.route('/get_chats', methods=['GET'])
@login_required
def get_chats():
    chats = ChatHistory.query.filter_by(user_id=current_user.id).all()
    result = {}
    for c in chats:
        result[c.chat_id] = {'title': c.title, 'html': c.html_content, 'time': c.timestamp}
    return jsonify(result)

@app.route('/delete_chat/<chat_id>', methods=['DELETE'])
@login_required
def delete_chat(chat_id):
    chat = ChatHistory.query.filter_by(user_id=current_user.id, chat_id=chat_id).first()
    if chat:
        db.session.delete(chat)
        db.session.commit()
    return jsonify({'status': 'success'})

@app.route('/update_profile', methods=['POST'])
@login_required
def update_profile():
    data = request.json
    current_user.name = data.get('name', current_user.name)
    current_user.surname = data.get('surname', current_user.surname)
    current_user.dob = data.get('dob', current_user.dob)
    current_user.pic = data.get('pic', current_user.pic)
    db.session.commit()
    return jsonify({'status': 'success'})

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        # Migration check for existing databases to prevent server errors
        try:
            db.session.execute(db.text('ALTER TABLE user ADD COLUMN surname VARCHAR(100)'))
            db.session.commit()
        except Exception:
            db.session.rollback()
    app.run(host='0.0.0.0', port=5000)


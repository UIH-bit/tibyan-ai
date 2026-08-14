from flask import Flask, request, jsonify, render_template_string, url_for, redirect, flash, session
from datetime import timedelta
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_mail import Mail, Message
import os
import requests
import time
import random
import traceback
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.permanent_session_lifetime = timedelta(days=3650)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'tibyan_secure_secret_key_2026')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///database.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Flask-Mail Configuration
app.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
app.config['MAIL_PORT'] = int(os.environ.get('MAIL_PORT', 587))
app.config['MAIL_USE_TLS'] = os.environ.get('MAIL_USE_TLS', 'True') == 'True'
app.config['MAIL_USE_SSL'] = os.environ.get('MAIL_USE_SSL', 'False') == 'False'
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')

db = SQLAlchemy(app)
mail = Mail(app)

login_manager = LoginManager()
login_manager.login_message = None
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

@app.before_request
def make_session_permanent():
    session.permanent = True
    if not getattr(app, '_database_checked', False):
        db.create_all()
        app._database_checked = True

@app.errorhandler(Exception)
def handle_exception(e):
    tb = traceback.format_exc()
    error_page = f"""
    <div style="font-family: monospace; padding: 20px; background: #ffe6e6; color: #900; border: 2px solid red; margin: 20px; border-radius: 8px;">
        <h2>⚠️ Application Error Caught:</h2>
        <pre>{tb}</pre>
    </div>
    """
    return error_page, 500

def call_groq_api(prompt_text, image_data=None):
    if not api_key:
        return "Error: API Key is missing. Please set GROQ_API_KEY in your .env file."
        
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    
    system_instruction = (
        "You are 'Tibyan AI', an Islamic knowledge assistant following Hanafi Fiqh. "
        "CRITICAL RULE: NEVER output your internal thinking, reasoning, analysis, constraint checks, or drafting steps "
        "(e.g., 'Analyze User Input', 'Check Constraints', 'Draft Content', 'All constraints met. Proceed to output') in the final response. "
        "Your response must START DIRECTLY with the requested headings and contain NO PRE-TEXT or thoughts. "
        "Your entire output must strictly follow this exact format with content under each heading:\n\n"
        "Short Answer\n"
        "Explanation\n"
        "Evidence\n"
        "Quran\n"
        "Hadith\n"
        "Scholars\n"
        "References\n"
        "Related topics\n\n"
        "Rules:\n"
        "1. Direct Output Only: Provide the final answer straight away.\n"
        "2. Language Matching: Match the exact language and script of the user (e.g., Roman Urdu, English, Urdu).\n"
        "3. Vocabulary: Use authentic Islamic/Urdu vocabulary."
    )

    content_list = [{"type": "text", "text": prompt_text if prompt_text else "Please analyze this image."}]
    
    if image_data:
        if not image_data.startswith("data:image"):
            image_data = f"data:image/jpeg;base64,{image_data}"
        content_list.append({
            "type": "image_url",
            "image_url": {"url": image_data}
        })

    messages = [
        {
            "role": "system", 
            "content": system_instruction
        },
        {
            "role": "user",
            "content": content_list
        }
    ]
    
    payload = {
        "model": "qwen/qwen3.6-27b",
        "messages": messages,
        "temperature": 0.2
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=45)
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
        .header-right { display: flex; align-items: center; }
        .new-chat-icon-btn { background: none; border: none; font-size: 22px; cursor: pointer; color: #1e3d2f; display: flex; align-items: center; justify-content: center; padding: 6px 10px; border-radius: 50%; transition: 0.2s; }
        .new-chat-icon-btn:hover { background: #f0f4f1; }
        
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
        
        .history-item { padding: 12px 14px; font-size: 16px; font-weight: 700; color: #1e3d2f; background: #f9f9f9; border-radius: 8px; margin-bottom: 8px; cursor: pointer; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; border: 1px solid #eee; transition: 0.2s; position: relative; user-select: none; }
        .history-item:hover { background: #f0f4f1; border-color: #d0ded4; }
        
        .chat-context-menu { position: absolute; background: #fff; border: 1px solid #d0ded4; box-shadow: 0 4px 12px rgba(0,0,0,0.15); border-radius: 8px; z-index: 10005; display: none; width: 160px; overflow: hidden; }
        .chat-context-menu div { padding: 10px 14px; font-size: 14px; font-weight: 600; color: #333; cursor: pointer; transition: 0.2s; }
        .chat-context-menu div:hover { background: #f0f4f1; color: #1e3d2f; }
        .chat-context-menu div.delete-option { color: #d9534f; }
        .chat-context-menu div.delete-option:hover { background: #ffe6e6; }

        .overlay { position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.4); display: none; z-index: 998; }
        .overlay.active { display: block; }
        .main-content { flex: 1; display: flex; flex-direction: column; overflow-y: auto; position: relative; margin-top: 60px; scroll-behavior: smooth; }
        .view-section { display: none; flex: 1; padding: 20px 20px 120px 20px; max-width: 800px; width: 100%; margin: 0 auto; }
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
        
        .ai-actions-bar { display: flex; align-items: center; gap: 12px; margin-top: 10px; padding-left: 4px; }
        .action-btn { background: none; border: none; cursor: pointer; font-size: 16px; color: #555; display: flex; align-items: center; gap: 4px; padding: 4px 8px; border-radius: 6px; transition: 0.2s; }
        .action-btn:hover { background: #f0f4f1; color: #1e3d2f; }
        .action-btn.active { color: #1e3d2f; font-weight: bold; background: #f0f4f1; }

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
        
        .input-area { display: flex; flex-direction: column; padding: 10px 16px calc(20px + env(safe-area-inset-bottom, 25px)) 16px; border-top: 1px solid #eaeaea; background: #fff; max-width: 800px; width: 100%; margin: 0 auto; flex-shrink: 0; gap: 8px; z-index: 20; position: fixed; bottom: 0; left: 50%; transform: translateX(-50%); box-shadow: 0 -4px 10px rgba(0,0,0,0.03); }
        .input-top-row { display: flex; align-items: center; gap: 10px; width: 100%; }
        .text-input { flex: 1; border: 1px solid #e0e0e0; border-radius: 24px; padding: 12px 18px; font-size: 16px; outline: none; background: #f9f9f9; resize: none; max-height: 150px; }
        .action-icon-btn { background: none; border: none; cursor: pointer; font-size: 22px; color: #1e3d2f; display: flex; align-items: center; justify-content: center; padding: 8px; }
        .send-btn { background: #1e3d2f; border: none; border-radius: 50%; width: 48px; height: 48px; min-width: 48px; display: flex; align-items: center; justify-content: center; cursor: pointer; color: white; font-size: 26px; font-weight: bold; }
        
        #imagePreviewContainer { display: none; align-items: center; gap: 10px; padding: 6px 12px; background: #f0f4f1; border-radius: 8px; width: fit-content; margin-bottom: 4px; border: 1px solid #d0ded4; }
        #imagePreviewContainer img { width: 40px; height: 40px; object-fit: cover; border-radius: 4px; }
        .remove-img-btn { background: none; border: none; color: #d9534f; font-weight: bold; cursor: pointer; font-size: 16px; }
        .chat-img-thumb { max-width: 200px; max-height: 200px; border-radius: 8px; margin-bottom: 8px; display: block; border: 1px solid #ddd; }
    </style>
</head>
<body>
    <header>
        <div class="header-left">
            <button class="menu-btn" onclick="toggleSidebar()">☰</button>
            <img src="{{ url_for('static', filename='logo.png') }}" alt="Tibyan AI" class="logo-img">
        </div>
        <div class="header-right">
            <button class="new-chat-icon-btn" onclick="startNewChat()" title="New Chat">✏️</button>
        </div>
    </header>

    <div class="overlay" id="overlay" onclick="toggleSidebar(); hideContextMenu();"></div>
    
    <div class="chat-context-menu" id="chatContextMenu">
        <div onclick="shareChatLink()">🔗 Share Chat Link</div>
        <div class="delete-option" onclick="deleteSelectedChat()">🗑️ Delete</div>
    </div>

    <div class="sidebar" id="sidebar">
        <div class="sidebar-header">
            <span>Tibyan Menu</span>
            <button class="close-sidebar" onclick="toggleSidebar()">✕</button>
        </div>
        <div class="sidebar-search-box">
            <input type="text" id="chatSearchInput" class="sidebar-search" placeholder="Search Chats..." oninput="filterChats(this.value)">
        </div>
        <ul class="sidebar-menu">
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

    <div class="main-content" id="mainContainer">
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
        <div id="imagePreviewContainer">
            <img id="previewThumb" src="" alt="Preview">
            <span id="previewName" style="font-size:13px; color:#1e3d2f; font-weight:500;">Image attached</span>
            <button class="remove-img-btn" onclick="removeAttachedImage()">✕</button>
        </div>
        <div class="input-top-row">
            <label class="action-icon-btn" title="Attach Image" style="cursor:pointer;">
                📎
                <input type="file" id="chatImageInput" accept="image/*" style="display:none;" onchange="handleChatImageSelect(event)">
            </label>
            <textarea id="userInput" class="text-input" rows="1" placeholder="Ask Tibyan..." oninput="this.style.height='inherit';this.style.height=this.scrollHeight+'px';"></textarea>
            <button class="send-btn" id="sendBtn" onclick="submitQuery()" title="Send">↑</button>
        </div>
    </div>

    <script>
        let uploadedImageBase64 = "{{ user.pic or '' }}";
        let currentAttachedImage = null;
        let currentChatId = 'chat_' + Date.now();
        let currentChatTitle = "";
        let savedResponses = {};
        let activeContextMenuChatId = null;

        function toggleSidebar() { document.getElementById('sidebar').classList.toggle('open'); document.getElementById('overlay').classList.toggle('active'); }
        function switchView(viewName) { document.querySelectorAll('.view-section').forEach(el => el.classList.remove('active-view')); document.getElementById(viewName + '-view').classList.add('active-view'); }
        
        function startNewChat() { 
            currentChatId = 'chat_' + Date.now(); 
            currentChatTitle = ""; 
            document.getElementById('chat-history').innerHTML = ''; 
            const ws = document.getElementById('welcome-screen'); 
            if(ws) ws.style.display = 'flex'; 
            switchView('home'); 
        }

        function handleChatImageSelect(event) {
            const file = event.target.files[0];
            if(file) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    currentAttachedImage = e.target.result;
                    document.getElementById('previewThumb').src = currentAttachedImage;
                    document.getElementById('imagePreviewContainer').style.display = 'flex';
                };
                reader.readAsDataURL(file);
            }
        }

        function removeAttachedImage() {
            currentAttachedImage = null;
            document.getElementById('imagePreviewContainer').style.display = 'none';
            document.getElementById('chatImageInput').value = '';
        }

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
                    html += `<div class="history-item" data-chat-id="${k}" onclick="loadSpecificChat('${k}')"><span>${chat.title}</span></div>`;
                }
            });
            listContainer.innerHTML = html;
            attachLongPressEvents();
        }

        function attachLongPressEvents() {
            const items = document.querySelectorAll('.history-item');
            items.forEach(item => {
                let pressTimer;
                const chatId = item.getAttribute('data-chat-id');

                item.addEventListener('touchstart', (e) => {
                    pressTimer = setTimeout(() => { showContextMenu(e, chatId); }, 600);
                });
                item.addEventListener('touchend', () => { clearTimeout(pressTimer); });
                item.addEventListener('touchmove', () => { clearTimeout(pressTimer); });

                item.addEventListener('mousedown', (e) => {
                    if (e.button === 0) {
                        pressTimer = setTimeout(() => { showContextMenu(e, chatId); }, 600);
                    }
                });
                item.addEventListener('mouseup', () => { clearTimeout(pressTimer); });
                item.addEventListener('mouseleave', () => { clearTimeout(pressTimer); });
            });
        }

        function showContextMenu(e, chatId) {
            e.preventDefault();
            e.stopPropagation();
            activeContextMenuChatId = chatId;
            const menu = document.getElementById('chatContextMenu');
            const overlay = document.getElementById('overlay');
            
            let clientX = e.clientX || (e.touches && e.touches[0].clientX) || 100;
            let clientY = e.clientY || (e.touches && e.touches[0].clientY) || 100;

            menu.style.left = clientX + 'px';
            menu.style.top = clientY + 'px';
            menu.style.display = 'block';
            overlay.classList.add('active');
        }

        function hideContextMenu() {
            document.getElementById('chatContextMenu').style.display = 'none';
            activeContextMenuChatId = null;
        }

        async function shareChatLink() {
            if (!activeContextMenuChatId) return;
            const shareUrl = window.location.origin + "/?chat=" + activeContextMenuChatId;
            hideContextMenu();
            if (navigator.share) {
                try {
                    await navigator.share({ title: 'Tibyan AI Chat', url: shareUrl });
                } catch(err) {}
            } else {
                navigator.clipboard.writeText(shareUrl).then(() => {
                    alert("Chat link copied to clipboard!");
                });
            }
        }

        async function deleteSelectedChat() {
            if (!activeContextMenuChatId) return;
            const cId = activeContextMenuChatId;
            hideContextMenu();
            
            const res = await fetch('/delete_chat', { 
                method: 'POST', 
                headers: { 'Content-Type': 'application/json' }, 
                body: JSON.stringify({ chat_id: cId }) 
            });
            
            if (res.ok) {
                if (currentChatId === cId) {
                    startNewChat();
                }
                loadSidebarHistory();
            }
        }

        function filterChats(query) {
            loadSidebarHistory(query);
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

        function handleLike(btn) {
            const parent = btn.closest('.ai-actions-bar');
            const likeBtn = parent.querySelector('.like-btn');
            const dislikeBtn = parent.querySelector('.dislike-btn');
            likeBtn.classList.toggle('active');
            dislikeBtn.classList.remove('active');
        }

        function handleDislike(btn) {
            const parent = btn.closest('.ai-actions-bar');
            const likeBtn = parent.querySelector('.like-btn');
            const dislikeBtn = parent.querySelector('.dislike-btn');
            dislikeBtn.classList.toggle('active');
            likeBtn.classList.remove('active');
        }

        function handleSave(btn, msgId) {
            btn.classList.toggle('active');
            const contentBox = document.getElementById(msgId);
            if(btn.classList.contains('active')) {
                savedResponses[msgId] = contentBox.innerHTML;
            } else {
                delete savedResponses[msgId];
            }
            renderSavedList();
        }

        function renderSavedList() {
            const container = document.getElementById('saved-chats-list');
            const keys = Object.keys(savedResponses);
            if(keys.length === 0) {
                container.innerHTML = '<p style="color: #666; font-size: 15px;">No saved responses yet.</p>';
                return;
            }
            let html = '';
            keys.forEach((k, idx) => {
                html += `<div style="background:#fff; border:1px solid #e0e0e0; border-radius:10px; padding:16px; margin-bottom:12px;">
                    <div style="font-size:13px; color:#777; margin-bottom:8px; font-weight:bold;">Saved Response #${idx + 1}</div>
                    <div>${savedResponses[k]}</div>
                </div>`;
            });
            container.innerHTML = html;
        }

        function handleMore(btn, msgId) {
            const contentBox = document.getElementById(msgId);
            const textToCopy = contentBox.innerText;
            
            if (navigator.share) {
                navigator.share({
                    title: 'Tibyan AI Response',
                    text: textToCopy,
                }).catch(() => {});
            } else {
                navigator.clipboard.writeText(textToCopy).then(() => {
                    let originalHTML = btn.innerHTML;
                    btn.innerHTML = '✓ Copied';
                    setTimeout(() => { btn.innerHTML = originalHTML; }, 1500);
                });
            }
        }

        async function submitQuery() {
            const inputField = document.getElementById('userInput');
            const query = inputField.value.trim();
            const attachedImg = currentAttachedImage;

            if(!query && !attachedImg) return;

            document.querySelectorAll('.view-section').forEach(el => el.classList.remove('active-view'));
            document.getElementById('home-view').classList.add('active-view');
            const ws = document.getElementById('welcome-screen');
            if(ws) ws.style.display = 'none';
            const historyBox = document.getElementById('chat-history');
            
            let userWrapperId = 'user-msg-' + Date.now();
            let imgHtmlTag = attachedImg ? `<img src="${attachedImg}" class="chat-img-thumb">` : '';
            let userHtml = `<div class="message-wrapper" id="${userWrapperId}"><div class="message user-msg">${imgHtmlTag}<div>${query || "Analyze this image."}</div></div></div>`;
            
            historyBox.innerHTML += userHtml;
            inputField.value = '';
            inputField.style.height = 'inherit';
            removeAttachedImage();
            
            const userMsgElement = document.getElementById(userWrapperId);
            if(userMsgElement) {
                userMsgElement.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }

            const uniqueId = 'msg-' + Date.now();
            const wrapperId = 'wrapper-' + Date.now();
            
            historyBox.innerHTML += `
                <div class="message-wrapper" id="${wrapperId}">
                    <div class="message ai-msg" id="${uniqueId}">Bismillah, analyzing...</div>
                    <div class="ai-actions-bar">
                        <button class="action-btn like-btn" onclick="handleLike(this)">👍 Like</button>
                        <button class="action-btn dislike-btn" onclick="handleDislike(this)">👎 Dislike</button>
                        <button class="action-btn" onclick="handleSave(this, '${uniqueId}')">📜 Save</button>
                        <button class="action-btn" onclick="handleMore(this, '${uniqueId}')">•••</button>
                    </div>
                </div>`;
            
            try {
                const res = await fetch('/generate', { 
                    method: 'POST', 
                    headers: { 'Content-Type': 'application/json' }, 
                    body: JSON.stringify({ prompt: query, image: attachedImg }) 
                });
                const data = await res.json();
                document.getElementById(uniqueId).innerHTML = marked.parse(data.response || "Error");
                document.getElementById(uniqueId).scrollIntoView({ behavior: 'smooth', block: 'nearest' });
                saveCurrentChat((query || "Image Query").substring(0, 30), historyBox.innerHTML);
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
        .password-container { position: relative; width: 100%; }
        .form-control { width: 100%; padding: 12px 45px 12px 16px; border: 1px solid #ddd; border-radius: 8px; font-size: 16px; outline: none; background: #f9f9f9; }
        .toggle-password { position: absolute; right: 12px; top: 50%; transform: translateY(-50%); background: none; border: none; cursor: pointer; display: flex; align-items: center; justify-content: center; width: 24px; height: 24px; color: #666; }
        .toggle-password svg { width: 20px; height: 20px; fill: currentColor; }
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
            <div class="form-group"><label class="form-label">Name</label><input type="text" name="name" class="form-control" style="padding-right: 16px;" required></div>
            <div class="form-group"><label class="form-label">Surname</label><input type="text" name="surname" class="form-control" style="padding-right: 16px;"></div>
            {% endif %}
            
            <div class="form-group"><label class="form-label">Email</label><input type="email" name="email" class="form-control" style="padding-right: 16px;" required></div>
            
            {% if not is_forgot_request %}
            <div class="form-group">
                <label class="form-label">Password</label>
                <div class="password-container">
                    <input type="password" name="password" id="passwordField" class="form-control" required>
                    <button type="button" class="toggle-password" onclick="togglePasswordVisibility('passwordField', this)">
                        <svg class="eye-icon" viewBox="0 0 24 24"><path d="M12 4.5C7 4.5 2.73 7.61 1 12c1.73 4.39 6 7.5 11 7.5s9.27-3.11 11-7.5c-1.73-4.39-6-7.5-11-7.5zM12 17c-2.76 0-5-2.24-5-5s2.24-5 5-5 5 2.24 5 5-2.24 5-5 5zm0-8c-1.66 0-3 1.34-3 3s1.34 3 3 3 3-1.34 3-3-1.34-3-3-3z"/></svg>
                    </button>
                </div>
            </div>
            {% endif %}

            {% if is_signup %}
            <div class="form-group">
                <label class="form-label">Confirm Password</label>
                <div class="password-container">
                    <input type="password" name="confirm_password" id="confirmPasswordField" class="form-control" required>
                    <button type="button" class="toggle-password" onclick="togglePasswordVisibility('confirmPasswordField', this)">
                        <svg class="eye-icon" viewBox="0 0 24 24"><path d="M12 4.5C7 4.5 2.73 7.61 1 12c1.73 4.39 6 7.5 11 7.5s9.27-3.11 11-7.5c-1.73-4.39-6-7.5-11-7.5zM12 17c-2.76 0-5-2.24-5-5s2.24-5 5-5 5 2.24 5 5-2.24 5-5 5zm0-8c-1.66 0-3 1.34-3 3s1.34 3 3 3 3-1.34 3-3-1.34-3-3-3z"/></svg>
                    </button>
                </div>
            </div>
            {% endif %}

            <button type="submit" class="auth-btn">{{ btn_text }}</button>
        </form>
        
        <div class="auth-link">
            {% if is_signup %}
                Already have an account? <a href="{{ url_for('login') }}">Login</a>
            {% elif is_forgot_request %}
                Remember your password? <a href="{{ url_for('login') }}">Login</a>
            {% else %}
                <a href="{{ url_for('forgot_password') }}" style="display:block; margin-bottom:8px;">Forgot Password?</a>
                Don't have an account? <a href="{{ url_for('signup') }}">Sign Up</a>
            {% endif %}
        </div>
    </div>

    <script>
        const eyeOpenSvg = '<path d="M12 4.5C7 4.5 2.73 7.61 1 12c1.73 4.39 6 7.5 11 7.5s9.27-3.11 11-7.5c-1.73-4.39-6-7.5-11-7.5zM12 17c-2.76 0-5-2.24-5-5s2.24-5 5-5 5 2.24 5 5-2.24 5-5 5zm0-8c-1.66 0-3 1.34-3 3s1.34 3 3 3 3-1.34 3-3-1.34-3-3-3 z"/>';
        const eyeClosedSvg = '<path d="M12 7c2.76 0 5 2.24 5 5 0 .65-.13 1.26-.36 1.83l2.92 2.92c1.51-1.26 2.7-2.89 3.43-4.75-1.73-4.39-6-7.5-11-7.5-1.4 0-2.74.25-3.98.7l2.16 2.16C10.74 7.13 11.35 7 12 7zM2.81 2.81L1.39 4.22l3.41 3.41C3.17 9.07 1.95 10.4 1 12c1.73 4.39 6 7.5 11 7.5 1.55 0 3.03-.3 4.38-.84l4.4 4.4 1.41-1.41L2.81 2.81zM12 15c-1.66 0-3-1.34-3-3 0-.34.07-.66.19-.96l3.77 3.77c-.3.12-.62.19-.96.19 z"/>';

        function togglePasswordVisibility(fieldId, btn) {
            const field = document.getElementById(fieldId);
            if(!field) return;
            const svgEl = btn.querySelector('svg');
            if (field.type === "password") {
                field.type = "text";
                svgEl.innerHTML = eyeClosedSvg;
            } else {
                field.type = "password";
                svgEl.innerHTML = eyeOpenSvg;
            }
        }
    </script>
</body>
</html>
"""

OTP_VERIFY_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Verify OTP - Tibyan AI</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }
        body { background: #f0f4f1; display: flex; align-items: center; justify-content: center; min-height: 100vh; padding: 20px; }
        .auth-card { background: #fff; padding: 30px; border-radius: 16px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); width: 100%; max-width: 400px; border: 1px solid #d0ded4; }
        .auth-title { font-size: 26px; color: #1e3d2f; font-weight: bold; margin-bottom: 20px; text-align: center; }
        .form-group { margin-bottom: 16px; }
        .form-label { display: block; font-size: 14px; font-weight: 500; color: #333; margin-bottom: 6px; }
        .form-control { width: 100%; padding: 12px 16px; border: 1px solid #ddd; border-radius: 8px; font-size: 16px; outline: none; background: #f9f9f9; }
        .auth-btn { background: #1e3d2f; color: white; border: none; border-radius: 8px; padding: 12px; width: 100%; font-size: 16px; font-weight: bold; cursor: pointer; margin-top: 10px; }
        .flash-msg { background: #ffe6e6; color: #d9534f; padding: 10px; border-radius: 6px; margin-bottom: 15px; font-size: 14px; text-align: center; }
    </style>
</head>
<body>
    <div class="auth-card">
        <div class="auth-title">Reset Password</div>
        {% with messages = get_flashed_messages() %}
          {% if messages %}<div class="flash-msg">{{ messages[0] }}</div>{% endif %}
        {% endwith %}
        <form method="POST">
            <div class="form-group"><label class="form-label">Enter 6-Digit OTP</label><input type="text" name="otp" class="form-control" required></div>
            <div class="form-group"><label class="form-label">New Password</label><input type="password" name="new_password" class="form-control" required></div>
            <button type="submit" class="auth-btn">Update Password</button>
        </form>
    </div>
</body>
</html>
"""

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            login_user(user, remember=True)
            return redirect(url_for('home'))
        flash('Invalid email or password!')
    return render_template_string(AUTH_TEMPLATE, title='Login', is_signup=False, is_forgot_request=False, btn_text='Login')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form.get('name')
        surname = request.form.get('surname')
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if password != confirm_password:
            flash('Passwords do not match!')
            return redirect(url_for('signup'))

        user_exists = User.query.filter_by(email=email).first()
        if user_exists:
            flash('Email address already registered! Please login.')
            return redirect(url_for('login'))
            
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        new_user = User(name=name, surname=surname, email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user, remember=True)
        return redirect(url_for('home'))
    return render_template_string(AUTH_TEMPLATE, title='Sign Up', is_signup=True, is_forgot_request=False, btn_text='Sign Up')

@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        user = User.query.filter_by(email=email).first()
        if not user:
            flash('This email is not registered with us!')
            return redirect(url_for('forgot_password'))
        
        otp = str(random.randint(100000, 999999))
        session['reset_email'] = email
        session['reset_otp'] = otp
        
        try:
            msg = Message('Tibyan AI - Password Reset OTP',
                          sender=os.environ.get('MAIL_USERNAME'),
                          recipients=[email])
            msg.body = f"Assalamu Alaikum,\n\nYour OTP for resetting your Tibyan AI password is: {otp}\n\nValid for a single use."
            mail.send(msg)
            return redirect(url_for('verify_otp'))
        except Exception as e:
            flash(f'Failed to send email. Check configuration: {str(e)}')
            
    return render_template_string(AUTH_TEMPLATE, title='Forgot Password', is_signup=False, is_forgot_request=True, btn_text='Send OTP')

@app.route('/verify_otp', methods=['GET', 'POST'])
def verify_otp():
    if 'reset_email' not in session:
        return redirect(url_for('forgot_password'))
        
    if request.method == 'POST':
        entered_otp = request.form.get('otp', '').strip()
        new_password = request.form.get('new_password', '').strip()
        
        if entered_otp == session.get('reset_otp'):
            email = session.get('reset_email')
            user = User.query.filter_by(email=email).first()
            if user:
                user.password = generate_password_hash(new_password, method='pbkdf2:sha256')
                db.session.commit()
            
            session.pop('reset_email', None)
            session.pop('reset_otp', None)
            
            flash('Password updated successfully! Please login.')
            return redirect(url_for('login'))
        else:
            flash('Invalid OTP! Please try again.')
            
    return render_template_string(OTP_VERIFY_TEMPLATE)

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
    ai_response = call_groq_api(data.get('prompt', ''), data.get('image'))
    return jsonify({'response': ai_response})

@app.get('/get_chats')
@login_required
def get_chats():
    chats = ChatHistory.query.filter_by(user_id=current_user.id).all()
    chats_dict = {}
    for chat in chats:
        chats_dict[chat.chat_id] = {
            'title': chat.title,
            'html': chat.html_content,
            'time': chat.timestamp
        }
    return jsonify(chats_dict)

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

@app.route('/delete_chat', methods=['POST'])
@login_required
def delete_chat():
    data = request.json or {}
    c_id = data.get('chat_id')
    if not c_id: return jsonify({'status': 'error'}), 400
    chat = ChatHistory.query.filter_by(user_id=current_user.id, chat_id=c_id).first()
    if chat:
        db.session.delete(chat)
        db.session.commit()
    return jsonify({'status': 'success'})

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


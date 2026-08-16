import os
import requests
import time
import random
import logging
from datetime import timedelta
from functools import wraps
from dotenv import load_dotenv

from flask import Flask, request, jsonify, render_template_string, url_for, redirect, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_mail import Mail, Message
from authlib.integrations.flask_client import OAuth

# Load environment variables
load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.permanent_session_lifetime = timedelta(days=30)

# Secret Key Security Setup
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'tibyan_secure_fallback_secret_key_2026')

# PostgreSQL Fix for Render (postgres:// -> postgresql://)
db_url = os.environ.get('DATABASE_URL', 'sqlite:///database.db')
if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)
app.config['SQLALCHEMY_DATABASE_URI'] = db_url
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

# OAuth Setup
oauth = OAuth(app)
google = oauth.register(
    name='google',
    client_id=os.environ.get('GOOGLE_CLIENT_ID', 'dummy_client_id'),
    client_secret=os.environ.get('GOOGLE_CLIENT_SECRET', 'dummy_client_secret'),
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid email profile'}
)

login_manager = LoginManager()
login_manager.login_message = None
login_manager.init_app(app)
login_manager.login_view = 'login'

api_key = os.environ.get("GROQ_API_KEY") or os.environ.get("GEMINI_API_KEY")

# --- DATABASE MODELS ---
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    surname = db.Column(db.String(100), nullable=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=True)
    dob = db.Column(db.String(20), nullable=True)
    pic = db.Column(db.Text, nullable=True)
    is_admin = db.Column(db.Boolean, default=False)
    chats = db.relationship('ChatHistory', backref='user', cascade="all, delete-orphan", lazy=True)

class ChatHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    chat_id = db.Column(db.String(100), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    html_content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.Float, nullable=False)

class CustomKnowledge(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    updated_at = db.Column(db.Float, default=time.time)

# Auto Initialize DB Tables Safely
with app.app_context():
    try:
        db.create_all()
    except Exception as err:
        logger.error(f"Database Creation Error: {err}")

# --- DECORATORS & HOOKS ---
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash("Aapko is page par jane ki ijazat nahi hai.")
            return redirect(url_for('home'))
        return f(*args, **kwargs)
    return decorated_function

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

@app.before_request
def make_session_permanent():
    session.permanent = True
    if not getattr(app, '_admin_checked', False):
        try:
            admin_email = os.environ.get('ADMIN_EMAIL')
            if admin_email:
                first_admin = User.query.filter_by(email=admin_email).first()
                if first_admin:
                    first_admin.is_admin = True
                    db.session.commit()
            app._admin_checked = True
        except Exception:
            pass

def call_groq_api(prompt_text, image_data=None):
    if not api_key:
        return "Error: API Key is missing. Please set GROQ_API_KEY in Environment Variables."
        
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    
    custom_records = CustomKnowledge.query.all()
    knowledge_text = ""
    if custom_records:
        knowledge_text = "\n--- OFFICIAL KNOWLEDGE BASE DATA ---\n"
        for rec in custom_records:
            knowledge_text += f"Topic: {rec.title}\nContent: {rec.content}\n\n"
        knowledge_text += "--- END OF KNOWLEDGE BASE ---\n"

    system_instruction = (
        "You are 'Tibyan AI', an authentic Islamic Ilmi assistant following the Hanafi school of thought (Fiqh-e-Hanafi).\n"
        "STRICT MANDATORY RULES:\n"
        "1. KNOWLEDGE BASE PRIORITIZATION: If custom knowledge base data is provided below, strictly check it first to answer user questions.\n"
        "2. STRICT LANGUAGE & SCRIPT MATCHING: Always respond strictly in the EXACT same language, dialect, and script used by the user in their prompt.\n"
        "3. ABSOLUTELY NO INTERNAL THINKING: Do NOT output any internal thinking, reasoning steps, or analysis.\n"
        "4. FORMATTING: Provide clear, polite, and well-structured responses using Markdown headers (### Heading) where appropriate.\n"
        f"{knowledge_text}"
    )

    if image_data:
        selected_model = "llama-3.2-11b-vision-preview"
        if not image_data.startswith("data:image"):
            image_data = f"data:image/jpeg;base64,{image_data}"
        
        messages = [
            {"role": "system", "content": system_instruction},
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt_text if prompt_text else "Please analyze this image."},
                    {"type": "image_url", "image_url": {"url": image_data}}
                ]
            }
        ]
    else:
        selected_model = "llama-3.3-70b-versatile"
        messages = [
            {"role": "system", "content": system_instruction},
            {"role": "user", "content": prompt_text}
        ]
    
    payload = {
        "model": selected_model,
        "messages": messages,
        "temperature": 0.3,
        "max_completion_tokens": 2048,
        "top_p": 1
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=45)
        if response.status_code == 200:
            return response.json()['choices'][0]['message']['content']
        else:
            return f"API Error ({response.status_code}): {response.text}"
    except Exception as e:
        return f"API Connection Error: {str(e)}"

# --- TEMPLATES ---
ADMIN_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Spatial Admin Control Panel - Tibyan AI</title>
    <style>
        :root { --bg-color: #0d1310; --card-bg: rgba(30, 61, 47, 0.25); --border-color: rgba(208, 222, 212, 0.15); --accent-green: #2ecc71; --primary-green: #1e3d2f; --text-light: #f4f6f5; --text-muted: #a0b2a6; --danger-color: #e74c3c; }
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }
        body { background: var(--bg-color); color: var(--text-light); padding: 24px; min-height: 100vh; }
        .admin-wrapper { max-width: 1200px; margin: 0 auto; }
        .header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 30px; background: var(--card-bg); backdrop-filter: blur(12px); padding: 20px 24px; border-radius: 16px; border: 1px solid var(--border-color); }
        .header h2 { font-size: 22px; font-weight: 700; letter-spacing: -0.5px; }
        .stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 20px; margin-bottom: 30px; }
        .stat-card { background: var(--card-bg); backdrop-filter: blur(12px); padding: 20px; border-radius: 14px; border: 1px solid var(--border-color); }
        .stat-card h3 { font-size: 13px; text-transform: uppercase; letter-spacing: 0.8px; color: var(--text-muted); margin-bottom: 10px; }
        .stat-card p { font-size: 28px; font-weight: 800; color: var(--accent-green); }
        .section-title { font-size: 20px; font-weight: 700; margin: 30px 0 15px 0; color: var(--accent-green); }
        .table-canvas { background: var(--card-bg); backdrop-filter: blur(12px); border-radius: 16px; border: 1px solid var(--border-color); overflow-x: auto; width: 100%; margin-bottom: 30px; box-shadow: 0 10px 30px rgba(0,0,0,0.3); }
        table { width: 100%; min-width: 900px; border-collapse: collapse; text-align: left; }
        th { background: rgba(30, 61, 47, 0.6); padding: 16px 20px; font-size: 13px; text-transform: uppercase; color: var(--text-muted); white-space: nowrap; }
        td { padding: 14px 20px; border-bottom: 1px solid var(--border-color); font-size: 14px; white-space: nowrap; }
        tr:hover td { background: rgba(255, 255, 255, 0.02); }
        .input-inline { background: rgba(255,255,255,0.08); border: 1px solid var(--border-color); color: #fff; padding: 6px 10px; border-radius: 6px; font-size: 13px; outline: none; }
        .badge { padding: 6px 12px; border-radius: 20px; font-size: 12px; font-weight: 600; display: inline-block; }
        .badge-admin { background: rgba(46, 204, 113, 0.15); color: var(--accent-green); border: 1px solid var(--accent-green); }
        .badge-user { background: rgba(160, 178, 166, 0.15); color: var(--text-muted); border: 1px solid var(--text-muted); }
        .btn { padding: 8px 14px; border-radius: 8px; text-decoration: none; font-size: 13px; font-weight: 600; display: inline-block; transition: all 0.2s ease; border: none; cursor: pointer; }
        .btn-success { background: #27ae60; color: #fff; }
        .btn-toggle { background: var(--primary-green); color: #fff; border: 1px solid var(--border-color); }
        .btn-danger { background: rgba(231, 76, 60, 0.2); color: var(--danger-color); border: 1px solid var(--danger-color); }
        .btn-secondary { background: rgba(255, 255, 255, 0.1); color: #fff; }
        .form-card { background: var(--card-bg); backdrop-filter: blur(12px); border-radius: 16px; border: 1px solid var(--border-color); padding: 20px; margin-bottom: 25px; }
        .form-card input, .form-card textarea { width: 100%; background: rgba(255,255,255,0.05); border: 1px solid var(--border-color); color: #fff; padding: 12px; border-radius: 8px; margin-bottom: 12px; outline: none; }
        .form-card textarea { height: 100px; resize: vertical; }
    </style>
</head>
<body>
    <div class="admin-wrapper">
        <div class="header">
            <h2>Spatial Admin Control Panel</h2>
            <a href="/" class="btn btn-secondary">← Back to App</a>
        </div>
        <div class="stats-grid">
            <div class="stat-card"><h3>Total Users</h3><p>{{ total_users }}</p></div>
            <div class="stat-card"><h3>Active Admins</h3><p>{{ total_admins }}</p></div>
            <div class="stat-card"><h3>Knowledge Records</h3><p>{{ knowledge_items|length }}</p></div>
        </div>
        <div class="section-title">👤 User Data Management</div>
        <div class="table-canvas">
            <table>
                <thead>
                    <tr><th>ID</th><th>Name</th><th>Surname</th><th>Email</th><th>DOB</th><th>Role</th><th>Actions</th></tr>
                </thead>
                <tbody>
                    {% for u in users %}
                    <tr>
                        <form method="POST" action="/admin/edit_user/{{ u.id }}">
                            <td>#{{ u.id }}</td>
                            <td><input type="text" name="name" class="input-inline" value="{{ u.name }}" required></td>
                            <td><input type="text" name="surname" class="input-inline" value="{{ u.surname or '' }}"></td>
                            <td><input type="email" name="email" class="input-inline" value="{{ u.email }}" required></td>
                            <td><input type="date" name="dob" class="input-inline" value="{{ u.dob or '' }}"></td>
                            <td>{% if u.is_admin %}<span class="badge badge-admin">Admin</span>{% else %}<span class="badge badge-user">User</span>{% endif %}</td>
                            <td>
                                <button type="submit" class="btn btn-success">Save</button>
                                {% if u.id != current_user.id %}
                                <a href="/admin/toggle_admin/{{ u.id }}" class="btn btn-toggle">Role</a>
                                <a href="/admin/delete_user/{{ u.id }}" class="btn btn-danger" onclick="return confirm('Delete this user?')">Delete</a>
                                {% endif %}
                            </td>
                        </form>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
        <div class="section-title">🧠 AI Knowledge Base</div>
        <div class="form-card">
            <h4 style="margin-bottom: 10px; color: var(--accent-green);">+ Add New Knowledge Topic</h4>
            <form method="POST" action="/admin/add_knowledge">
                <input type="text" name="title" placeholder="Topic Title" required>
                <textarea name="content" placeholder="Enter full detail that AI should know..." required></textarea>
                <button type="submit" class="btn btn-success">+ Save to AI Data</button>
            </form>
        </div>
        <div class="table-canvas">
            <table>
                <thead>
                    <tr><th style="width: 20%;">Topic Title</th><th style="width: 60%;">Data Detail / Content</th><th style="width: 20%;">Actions</th></tr>
                </thead>
                <tbody>
                    {% for item in knowledge_items %}
                    <tr>
                        <form method="POST" action="/admin/edit_knowledge/{{ item.id }}">
                            <td><input type="text" name="title" class="input-inline" value="{{ item.title }}" style="width:100%;" required></td>
                            <td><textarea name="content" class="input-inline" style="width:100%; height:50px;" required>{{ item.content }}</textarea></td>
                            <td>
                                <button type="submit" class="btn btn-success">Update</button>
                                <a href="/admin/delete_knowledge/{{ item.id }}" class="btn btn-danger" onclick="return confirm('Delete this record?')">Delete</a>
                            </td>
                        </form>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </div>
</body>
</html>"""

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Tibyan AI</title>
    <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }
        body { background-color: #ffffff; color: #111; display: flex; flex-direction: column; height: 100vh; overflow: hidden; font-size: 17px; }
        header { display: flex; align-items: center; justify-content: space-between; padding: 12px 20px; border-bottom: 1px solid #eaeaea; background: #fff; z-index: 1000; position: fixed; top: 0; left: 0; width: 100%; }
        .header-left { display: flex; align-items: center; gap: 15px; }
        .menu-btn { background: none; border: none; font-size: 26px; cursor: pointer; color: #1e3d2f; padding: 4px 8px; }
        .logo-title { font-size: 22px; font-weight: bold; color: #1e3d2f; }
        .header-right { display: flex; align-items: center; }
        .new-chat-icon-btn { background: none; border: none; font-size: 22px; cursor: pointer; color: #1e3d2f; padding: 6px 10px; border-radius: 50%; }
        .sidebar { position: fixed; top: 0; left: -280px; width: 280px; height: 100%; background: #fff; box-shadow: 2px 0 10px rgba(0,0,0,0.1); transition: 0.3s ease; z-index: 9999; display: flex; flex-direction: column; }
        .sidebar.open { left: 0; }
        .sidebar-header { padding: 20px; font-size: 20px; font-weight: bold; color: #1e3d2f; border-bottom: 1px solid #eaeaea; display: flex; justify-content: space-between; align-items: center; }
        .close-sidebar { background: none; border: none; font-size: 20px; cursor: pointer; color: #555; }
        .sidebar-menu { list-style: none; padding: 10px 0; overflow-y: auto; flex: 1; border-bottom: 1px solid #eaeaea; }
        .sidebar-menu li { padding: 14px 20px; font-size: 17px; color: #333; cursor: pointer; display: flex; align-items: center; gap: 14px; border-bottom: 1px solid #f7f7f7; }
        .sidebar-menu li a { text-decoration: none; color: inherit; width: 100%; }
        .overlay { position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.4); display: none; z-index: 998; }
        .overlay.active { display: block; }
        .main-content { flex: 1; display: flex; flex-direction: column; overflow-y: auto; position: relative; margin-top: 60px; }
        .view-section { display: none; flex: 1; padding: 20px 20px 120px 20px; max-width: 800px; width: 100%; margin: 0 auto; }
        .view-section.active-view { display: flex; flex-direction: column; }
        .welcome-section { display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center; margin: auto 0; width: 100%; padding: 25px 20px; background: linear-gradient(180deg, rgba(240,244,241,0.6) 0%, rgba(255,255,255,1) 100%); border-radius: 24px; border: 1px solid #e2ece4; }
        .welcome-title { font-size: 28px; color: #1e3d2f; font-weight: bold; margin-bottom: 25px; }
        #chat-history { width: 100%; display: flex; flex-direction: column; gap: 18px; padding-bottom: 40px; }
        .message-wrapper { display: flex; flex-direction: column; width: 100%; margin-bottom: 12px; }
        .message { padding: 16px 20px; border-radius: 14px; max-width: 85%; line-height: 1.6; font-size: 17px; }
        .user-msg { background: #f0f4f1; color: #1e3d2f; align-self: flex-end; margin-left: auto; }
        .ai-msg { background: #ffffff; border: 1px solid #e0e0e0; color: #222; align-self: flex-start; width: 100%; }
        .input-area { display: flex; flex-direction: column; padding: 10px 16px; border-top: 1px solid #eaeaea; background: #fff; max-width: 800px; width: 100%; margin: 0 auto; position: fixed; bottom: 0; left: 50%; transform: translateX(-50%); }
        .input-top-row { display: flex; align-items: center; gap: 10px; width: 100%; }
        .text-input { flex: 1; border: 1px solid #e0e0e0; border-radius: 24px; padding: 12px 18px; font-size: 16px; outline: none; background: #f9f9f9; resize: none; }
        .send-btn { background: #1e3d2f; border: none; border-radius: 50%; width: 44px; height: 44px; display: flex; align-items: center; justify-content: center; cursor: pointer; color: white; font-size: 22px; }
    </style>
</head>
<body>
    <header>
        <div class="header-left">
            <button class="menu-btn" onclick="toggleSidebar()">☰</button>
            <div class="logo-title">Tibyan AI</div>
        </div>
        <div class="header-right">
            <button class="new-chat-icon-btn" onclick="startNewChat()">✏︎</button>
        </div>
    </header>

    <div class="overlay" id="overlay" onclick="toggleSidebar()"></div>

    <div class="sidebar" id="sidebar">
        <div class="sidebar-header">
            <span>Menu</span>
            <button class="close-sidebar" onclick="toggleSidebar()">✕</button>
        </div>
        <ul class="sidebar-menu">
            {% if user.is_admin %}
            <li><a href="/admin" style="color: #1e3d2f; font-weight: bold;">🛠️ Admin Panel</a></li>
            {% endif %}
            <li onclick="switchView('profile')">👤 Profile</li>
            <li><a href="/logout" style="color: #d9534f;">🚪 Logout</a></li>
        </ul>
    </div>

    <div class="main-content">
        <div id="home-view" class="view-section active-view">
            <div id="chat-box" style="width: 100%;">
                <div class="welcome-section" id="welcome-screen">
                    <div class="welcome-title">Assalamu Alaikum, {{ user.name }}!</div>
                    <p style="color:#555;">How can I assist you today?</p>
                </div>
                <div id="chat-history"></div>
            </div>
        </div>
        
        <div id="profile-view" class="view-section">
            <div style="font-size:24px; color:#1e3d2f; margin-bottom:15px; font-weight:bold;">Profile 👤</div>
            <p><strong>Name:</strong> {{ user.name }} {{ user.surname or '' }}</p>
            <p><strong>Email:</strong> {{ user.email }}</p>
        </div>
    </div>

    <div class="input-area">
        <div class="input-top-row">
            <textarea id="userInput" class="text-input" rows="1" placeholder="Ask Tibyan AI..."></textarea>
            <button class="send-btn" onclick="submitQuery()">↑</button>
        </div>
    </div>

    <script>
        function toggleSidebar() { document.getElementById('sidebar').classList.toggle('open'); document.getElementById('overlay').classList.toggle('active'); }
        function switchView(viewName) { document.querySelectorAll('.view-section').forEach(el => el.classList.remove('active-view')); document.getElementById(viewName + '-view').classList.add('active-view'); toggleSidebar(); }
        function startNewChat() { document.getElementById('chat-history').innerHTML = ''; document.getElementById('welcome-screen').style.display = 'flex'; }
        
        async function submitQuery() {
            const inputField = document.getElementById('userInput');
            const query = inputField.value.trim();
            if(!query) return;

            document.getElementById('welcome-screen').style.display = 'none';
            const historyBox = document.getElementById('chat-history');
            
            historyBox.innerHTML += `<div class="message-wrapper"><div class="message user-msg">${query}</div></div>`;
            inputField.value = '';

            const uniqueId = 'msg-' + Date.now();
            historyBox.innerHTML += `<div class="message-wrapper"><div class="message ai-msg" id="${uniqueId}">Generating answer...</div></div>`;
            
            try {
                const res = await fetch('/generate', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ prompt: query }) });
                const data = await res.json();
                document.getElementById(uniqueId).innerHTML = marked.parse(data.response || "Error");
            } catch(e) {
                document.getElementById(uniqueId).innerText = "Connection error.";
            }
        }
    </script>
</body>
</html>"""

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
            <div class="form-group"><label class="form-label">First Name</label><input type="text" name="name" class="form-control" required></div>
            <div class="form-group"><label class="form-label">Surname</label><input type="text" name="surname" class="form-control"></div>
            {% endif %}
            <div class="form-group"><label class="form-label">Email</label><input type="email" name="email" class="form-control" required></div>
            <div class="form-group"><label class="form-label">Password</label><input type="password" name="password" class="form-control" required></div>
            {% if is_signup %}
            <div class="form-group"><label class="form-label">Confirm Password</label><input type="password" name="confirm_password" class="form-control" required></div>
            {% endif %}
            <button type="submit" class="auth-btn">{{ btn_text }}</button>
        </form>
        <div class="auth-link">
            {% if is_signup %}
                Already have an account? <a href="{{ url_for('login') }}">Login</a>
            {% else %}
                Need a new account? <a href="{{ url_for('signup') }}">Sign Up</a>
            {% endif %}
        </div>
    </div>
</body>
</html>"""

# --- ROUTES ---
@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        user = User.query.filter_by(email=email).first()
        if user and user.password and check_password_hash(user.password, password):
            login_user(user, remember=True)
            return redirect(url_for('home'))
        flash('Invalid email or password!')
    return render_template_string(AUTH_TEMPLATE, title='Login', is_signup=False, btn_text='Login')

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
            flash('Email is already registered!')
            return redirect(url_for('login'))
            
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        first_user = User.query.first() is None
        new_user = User(name=name, surname=surname, email=email, password=hashed_password, is_admin=first_user)
        
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user, remember=True)
        return redirect(url_for('home'))
    return render_template_string(AUTH_TEMPLATE, title='Create Account', is_signup=True, btn_text='Sign Up')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/home')
@login_required
def home():
    return render_template_string(HTML_TEMPLATE, user=current_user)

@app.route('/generate', methods=['POST'])
@login_required
def generate():
    data = request.json or {}
    ai_response = call_groq_api(data.get('prompt', ''), data.get('image'))
    return jsonify({'response': ai_response})

@app.route('/admin')
@login_required
@admin_required
def admin_dashboard():
    users = User.query.order_by(User.id.desc()).all()
    total_users = User.query.count()
    total_admins = User.query.filter_by(is_admin=True).count()
    knowledge_items = CustomKnowledge.query.order_by(CustomKnowledge.id.desc()).all()
    return render_template_string(ADMIN_TEMPLATE, users=users, total_users=total_users, total_admins=total_admins, knowledge_items=knowledge_items)

@app.route('/admin/add_knowledge', methods=['POST'])
@login_required
@admin_required
def add_knowledge():
    title = request.form.get('title')
    content = request.form.get('content')
    if title and content:
        new_record = CustomKnowledge(title=title, content=content, updated_at=time.time())
        db.session.add(new_record)
        db.session.commit()
    return redirect(url_for('admin_dashboard'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)


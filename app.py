import os
import requests
import time
import random
import traceback
import hashlib
from datetime import timedelta
from dotenv import load_dotenv

from flask import Flask, request, jsonify, render_template_string, url_for, redirect, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_mail import Mail, Message
from authlib.integrations.flask_client import OAuth

load_dotenv()

app = Flask(__name__)
app.permanent_session_lifetime = timedelta(days=3650)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'tibyan_secure_secret_key_2026')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///database.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Flask-Mail Configuration Fixes
app.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
app.config['MAIL_PORT'] = int(os.environ.get('MAIL_PORT', 587))
app.config['MAIL_USE_TLS'] = os.environ.get('MAIL_USE_TLS', 'True').lower() == 'true'
app.config['MAIL_USE_SSL'] = os.environ.get('MAIL_USE_SSL', 'False').lower() == 'true'
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')

db = SQLAlchemy(app)
mail = Mail(app)

oauth = OAuth(app)
google = oauth.register(
    name='google',
    client_id=os.environ.get('GOOGLE_CLIENT_ID'),
    client_secret=os.environ.get('GOOGLE_CLIENT_SECRET'),
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid email profile'}
)

login_manager = LoginManager()
login_manager.login_message = None
login_manager.init_app(app)
login_manager.login_view = 'login'

api_key = os.environ.get("GROQ_API_KEY") or os.environ.get("GEMINI_API_KEY")

# HTML Templates Definitions
AUTH_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>{{ title }} - Tibyan AI</title>
    <style>
        body { font-family: Arial, sans-serif; background: #f4f7f6; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }
        .auth-card { background: white; padding: 30px; border-radius: 10px; box-shadow: 0 4px 10px rgba(0,0,0,0.1); width: 100%; max-width: 400px; }
        .auth-card h2 { text-align: center; margin-bottom: 20px; color: #1a5276; }
        .form-group { margin-bottom: 15px; }
        .form-group label { display: block; margin-bottom: 5px; font-weight: bold; }
        .form-group input { width: 100%; padding: 10px; border: 1px solid #ccc; border-radius: 5px; box-sizing: border-box; }
        .btn { width: 100%; padding: 10px; background: #1a5276; color: white; border: none; border-radius: 5px; cursor: pointer; font-size: 16px; margin-top: 10px; }
        .btn:hover { background: #154360; }
        .links { text-align: center; margin-top: 15px; font-size: 14px; }
        .links a { color: #1a5276; text-decoration: none; }
        .flash-msg { color: red; text-align: center; margin-bottom: 15px; }
    </style>
</head>
<body>
    <div class="auth-card">
        <h2>{{ title }}</h2>
        {% with messages = get_flashed_messages() %}
            {% if messages %}
                {% for message in messages %}
                    <div class="flash-msg">{{ message }}</div>
                {% endfor %}
            {% endif %}
        {% endwith %}
        
        <form method="POST">
            {% if is_signup %}
                <div class="form-group">
                    <label>First Name</label>
                    <input type="text" name="name" required>
                </div>
                <div class="form-group">
                    <label>Surname</label>
                    <input type="text" name="surname">
                </div>
            {% endif %}
            
            <div class="form-group">
                <label>Email</label>
                <input type="email" name="email" required>
            </div>
            
            {% if not is_forgot_request %}
                <div class="form-group">
                    <label>Password</label>
                    <input type="password" name="password" required>
                </div>
            {% endif %}
            
            {% if is_signup %}
                <div class="form-group">
                    <label>Confirm Password</label>
                    <input type="password" name="confirm_password" required>
                </div>
            {% endif %}
            
            <button type="submit" class="btn">{{ btn_text }}</button>
        </form>

        {% if not is_signup and not is_forgot_request %}
            <a href="{{ url_for('google_login') }}"><button class="btn" style="background: #db4437;">Login with Google</button></a>
        {% endif %}

        <div class="links">
            {% if is_signup %}
                Already have an account? <a href="{{ url_for('login') }}">Login</a>
            {% elif is_forgot_request %}
                Remember password? <a href="{{ url_for('login') }}">Login</a>
            {% else %}
                <a href="{{ url_for('signup') }}">Create Account</a> | <a href="{{ url_for('forgot_password') }}">Forgot Password?</a>
            {% endif %}
        </div>
    </div>
</body>
</html>
"""

OTP_VERIFY_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Verify OTP - Tibyan AI</title>
    <style>
        body { font-family: Arial, sans-serif; background: #f4f7f6; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }
        .auth-card { background: white; padding: 30px; border-radius: 10px; box-shadow: 0 4px 10px rgba(0,0,0,0.1); width: 100%; max-width: 400px; }
        .auth-card h2 { text-align: center; margin-bottom: 20px; color: #1a5276; }
        .form-group { margin-bottom: 15px; }
        .form-group label { display: block; margin-bottom: 5px; font-weight: bold; }
        .form-group input { width: 100%; padding: 10px; border: 1px solid #ccc; border-radius: 5px; box-sizing: border-box; }
        .btn { width: 100%; padding: 10px; background: #1a5276; color: white; border: none; border-radius: 5px; cursor: pointer; font-size: 16px; margin-top: 10px; }
        .flash-msg { color: red; text-align: center; margin-bottom: 15px; }
    </style>
</head>
<body>
    <div class="auth-card">
        <h2>Verify OTP</h2>
        {% with messages = get_flashed_messages() %}
            {% if messages %}
                {% for message in messages %}
                    <div class="flash-msg">{{ message }}</div>
                {% endfor %}
            {% endif %}
        {% endwith %}
        <form method="POST">
            <div class="form-group">
                <label>Enter 6-Digit OTP</label>
                <input type="text" name="otp" maxlength="6" required>
            </div>
            <div class="form-group">
                <label>New Password</label>
                <input type="password" name="new_password" required>
            </div>
            <button type="submit" class="btn">Reset Password</button>
        </form>
    </div>
</body>
</html>
"""

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Tibyan AI - Home</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; background: #eef2f5; display: flex; height: 100vh; }
        .sidebar { width: 250px; background: #1a5276; color: white; padding: 20px; box-sizing: border-box; }
        .main-content { flex: 1; padding: 30px; display: flex; flex-direction: column; justify-content: space-between; }
        .profile { display: flex; align-items: center; gap: 10px; margin-bottom: 20px; }
        .profile img { border-radius: 50%; width: 40px; height: 40px; }
        .chat-area { background: white; flex: 1; border-radius: 8px; padding: 20px; overflow-y: auto; box-shadow: 0 2px 5px rgba(0,0,0,0.05); }
        .input-area { display: flex; gap: 10px; margin-top: 20px; }
        .input-area input { flex: 1; padding: 12px; border: 1px solid #ccc; border-radius: 5px; }
        .input-area button { padding: 12px 20px; background: #1a5276; color: white; border: none; border-radius: 5px; cursor: pointer; }
        .logout-btn { color: #ff6b6b; text-decoration: none; font-weight: bold; }
    </style>
</head>
<body>
    <div class="sidebar">
        <div class="profile">
            <img src="{{ user.pic }}" alt="Avatar">
            <div>
                <strong>{{ user.name }}</strong><br>
                <a href="{{ url_for('logout') }}" class="logout-btn">Logout</a>
            </div>
        </div>
        <hr>
        <h3>Chat History</h3>
        <p style="font-size: 13px; color: #bdc3c7;">Your chats will appear here.</p>
    </div>
    <div class="main-content">
        <h2>Welcome to Tibyan AI</h2>
        <div class="chat-area" id="chatArea">
            <p><strong>Tibyan AI:</strong> Assalamu Alaikum! How can I help you today?</p>
        </div>
        <div class="input-area">
            <input type="text" id="userInput" placeholder="Ask a question...">
            <button onclick="sendMessage()">Send</button>
        </div>
    </div>

    <script>
        async function sendMessage() {
            const input = document.getElementById('userInput');
            const chatArea = document.getElementById('chatArea');
            const text = input.value.trim();
            if(!text) return;

            chatArea.innerHTML += `<p><strong>You:</strong> ${text}</p>`;
            input.value = '';

            const response = await fetch('/generate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ prompt: text })
            });

            const data = await response.json();
            chatArea.innerHTML += `<p><strong>Tibyan AI:</strong> ${data.response}</p>`;
            chatArea.scrollTop = chatArea.scrollHeight;
        }
    </script>
</body>
</html>
"""

def get_gravatar(email, size=200):
    if not email:
        return ""
    email_hash = hashlib.md5(email.strip().lower().encode('utf-8')).hexdigest()
    return f"https://www.gravatar.com/avatar/{email_hash}?s={size}&d=mp"

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    surname = db.Column(db.String(100), nullable=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=True)
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

@app.errorhandler(Exception)
def handle_exception(e):
    tb = traceback.format_exc()
    error_page = f"""
    <div style="font-family: monospace; padding: 20px; background: #ffe6e6; color: #900; border: 2px solid red; margin: 20px; border-radius: 8px;">
        <h2>⚠️ Application Error:</h2>
        <pre>{tb}</pre>
    </div>
    """
    return error_page, 500

def call_groq_api(prompt_text, image_data=None):
    if not api_key:
        return "Error: API Key is missing. Please set GROQ_API_KEY in .env file."
        
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    
    system_instruction = (
        "You are 'Tibyan AI', an authentic Islamic Ilmi assistant following the Hanafi school of thought (Fiqh-e-Hanafi).\n"
        "STRICT MANDATORY RULES:\n"
        "1. STRICT LANGUAGE & SCRIPT MATCHING: Always respond strictly in the EXACT same language, dialect, and script used by the user in their prompt.\n"
        "2. ABSOLUTELY NO INTERNAL THINKING: Do NOT output any internal thinking, reasoning steps, or analysis.\n"
        "3. FORMATTING: Provide clear, polite, and well-structured responses using Markdown headers (### Heading) where appropriate.\n"
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

# Direct Route Registrations & Handlers
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        user = User.query.filter_by(email=email).first()
        if user and user.password and check_password_hash(user.password, password):
            if not user.pic:
                user.pic = get_gravatar(user.email)
                db.session.commit()
            login_user(user, remember=True)
            return redirect(url_for('home'))
        flash('Invalid email or password!')
    return render_template_string(AUTH_TEMPLATE, title='Login', is_signup=False, is_forgot_request=False, btn_text='Login')

@app.route('/google-login')
def google_login():
    redirect_uri = url_for('google_authorize', _external=True)
    return google.authorize_redirect(redirect_uri)

@app.route('/google-authorize')
def google_authorize():
    token = google.authorize_access_token()
    resp = google.get('https://www.googleapis.com/oauth2/v3/userinfo')
    user_info = resp.json()
    
    email = user_info.get('email')
    name = user_info.get('given_name', user_info.get('name', 'User'))
    surname = user_info.get('family_name', '')
    picture = user_info.get('picture', '') or get_gravatar(email)

    user = User.query.filter_by(email=email).first()
    if not user:
        user = User(name=name, surname=surname, email=email, pic=picture, password=None)
        db.session.add(user)
        db.session.commit()
    elif not user.pic:
        user.pic = picture
        db.session.commit()
    
    login_user(user, remember=True)
    return redirect(url_for('home'))

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
            flash('Email is already registered! Please login.')
            return redirect(url_for('login'))
            
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        default_pic = get_gravatar(email)
        new_user = User(name=name, surname=surname, email=email, password=hashed_password, pic=default_pic)
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user, remember=True)
        return redirect(url_for('home'))
    return render_template_string(AUTH_TEMPLATE, title='Create Account', is_signup=True, is_forgot_request=False, btn_text='Sign Up')

@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        user = User.query.filter_by(email=email).first()
        if not user:
            flash('Email not found in our records!')
            return redirect(url_for('forgot_password'))
        
        otp = str(random.randint(100000, 999999))
        session['reset_email'] = email
        session['reset_otp'] = otp
        
        try:
            msg = Message('Tibyan AI - Password Reset OTP',
                          sender=os.environ.get('MAIL_USERNAME'),
                          recipients=[email])
            msg.body = f"Assalamu Alaikum,\n\nYour OTP code to reset your Tibyan AI password is: {otp}\n\nThis is for single-use only."
            mail.send(msg)
            return redirect(url_for('verify_otp'))
        except Exception as e:
            flash(f'Failed to send email: {str(e)}')
            
    return render_template_string(AUTH_TEMPLATE, title='Reset Password', is_signup=False, is_forgot_request=True, btn_text='Send OTP')

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
            
            flash('Password changed successfully! Please login.')
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
    if not current_user.pic:
        current_user.pic = get_gravatar(current_user.email)
        db.session.commit()
    return render_template_string(HTML_TEMPLATE, user=current_user, get_gravatar=get_gravatar)

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
    current_user.pic = data.get('pic', current_user.pic) or get_gravatar(current_user.email)
    db.session.commit()
    return jsonify({'status': 'success'})

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5000)


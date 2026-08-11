from flask import Flask, request, jsonify, render_template_string, redirect, url_for, flash
from datetime import timedelta
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import os
import requests
import re
import time
import traceback

app = Flask(__name__)
app.secret_key = 'Huzaifa@35789612'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=365)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tibyan.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
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
        return "Error: API Key is missing. Please set it."
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    messages = [
        {
            "role": "system",
            "content": "You are Tibyan AI, a knowledgeable Islamic assistant."
        }
    ]
    if image_data:
        messages.append({
            "role": "user",
            "content": [
                {"type": "text", "text": prompt_text},
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
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]
        else:
            return f"API Error ({response.status_code}): {response.text}"
    except Exception as e:
        return f"Exception occurred while contacting AI: {str(e)}"

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            session.permanent = True
            return redirect(url_for('home'))
        flash('Invalid email or password!')
    return render_template_string(AUTH_TEMPLATE if 'AUTH_TEMPLATE' in globals() else "<h1>Login</h1>", title='Login', is_signup=False)

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
        session.permanent = True
        return redirect(url_for('home'))
    return render_template_string(AUTH_TEMPLATE if 'AUTH_TEMPLATE' in globals() else "<h1>Signup</h1>", title='Sign Up', is_signup=True)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    session.clear()
    return redirect(url_for('login'))

@app.route('/')
@login_required
def home():
    return render_template_string(HTML_TEMPLATE if 'HTML_TEMPLATE' in globals() else "<h1>Home</h1>", user=current_user)

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

@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email')
        return "Password reset link has been sent to your email."
    return "Forgot Password Page"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

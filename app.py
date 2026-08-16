import os
import re
import time
import logging
from datetime import timedelta
from functools import wraps
from dotenv import load_dotenv

import requests
import markupsafe
from bleach import clean as sanitize_html

from flask import Flask, request, jsonify, render_template_string, url_for, redirect, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_mail import Mail, Message
from flask_wtf.csrf import CSRFProtect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from authlib.integrations.flask_client import OAuth
from marshmallow import Schema, fields, validate, ValidationError

load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("security_logger")

app = Flask(__name__)

# --- [A] SECRETS & CONFIGURATION ---
SECRET_KEY = os.environ.get('SECRET_KEY')
if not SECRET_KEY:
    raise RuntimeError("CRITICAL SECURITY RISK: SECRET_KEY environment variable is missing.")

app.config['SECRET_KEY'] = SECRET_KEY

# Fix for Render's PostgreSQL URL format (postgres:// -> postgresql://)
db_url = os.environ.get('DATABASE_URL', 'sqlite:///database.db')
if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = db_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# --- [D] COOKIE & SESSION SECURITY ---
app.permanent_session_lifetime = timedelta(hours=12)
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SECURE'] = os.environ.get('FLASK_ENV') == 'production' or os.environ.get('RENDER') is not None
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

# --- [F] CSRF PROTECTION ---
csrf = CSRFProtect(app)

# Flask-Mail Configuration
app.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
app.config['MAIL_PORT'] = int(os.environ.get('MAIL_PORT', 587))
app.config['MAIL_USE_TLS'] = os.environ.get('MAIL_USE_TLS', 'True') == 'True'
app.config['MAIL_USE_SSL'] = os.environ.get('MAIL_USE_SSL', 'False') == 'True'
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

# --- [B] RATE LIMITING SETUP ---
def get_rate_limit_key():
    if current_user and current_user.is_authenticated:
        return f"user_{current_user.id}"
    return get_remote_address()

limiter = Limiter(
    key_func=get_rate_limit_key,
    app=app,
    default_limits=["60 per minute"],
    storage_uri=os.environ.get("REDIS_URL", "memory://")
)

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

# --- [C] INPUT VALIDATION SCHEMAS (Marshmallow) ---
class LoginSchema(Schema):
    email = fields.Email(required=True, validate=validate.Length(max=120))
    password = fields.Str(required=True, validate=validate.Length(min=8, max=128))

class SignupSchema(Schema):
    name = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    surname = fields.Str(validate=validate.Length(max=100))
    email = fields.Email(required=True, validate=validate.Length(max=120))
    password = fields.Str(required=True, validate=validate.Length(min=8, max=128))
    confirm_password = fields.Str(required=True, validate=validate.Length(min=8, max=128))

class GenerateSchema(Schema):
    prompt = fields.Str(validate=validate.Length(max=4000))
    image = fields.Str(validate=validate.Length(max=10000000))

class SaveChatSchema(Schema):
    chat_id = fields.Str(required=True, validate=validate.Length(max=100))
    title = fields.Str(required=True, validate=validate.Length(max=200))
    html = fields.Str(required=True, validate=validate.Length(max=500000))

# --- [F] SECURITY HEADERS MIDDLEWARE ---
@app.after_request
def apply_security_headers(response):
    response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; style-src 'self' 'unsafe-inline';"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    return response

# --- ADMIN DECORATOR ---
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash("Unauthorized access.")
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

@app.before_request
def make_session_permanent():
    session.permanent = True
    if not getattr(app, '_database_checked', False):
        db.create_all()
        admin_email = os.environ.get('ADMIN_EMAIL')
        if admin_email:
            first_admin = User.query.filter_by(email=admin_email).first()
            if first_admin:
                first_admin.is_admin = True
                db.session.commit()
        app._database_checked = True

# --- [G] ERROR HANDLING FIXES ---
@app.errorhandler(Exception)
def handle_exception(e):
    logger.error(f"Internal Error: {str(e)}", exc_info=True)
    if request.path.startswith('/generate') or request.is_json:
        return jsonify({'error': 'An internal error occurred. Please try again later.'}), 500
    return "<h3>An unexpected error occurred. Please contact support.</h3>", 500

@app.errorhandler(429)
def ratelimit_handler(e):
    return jsonify({"error": "Rate limit exceeded", "retry_after": e.description}), 429

# --- [E] PROMPT INJECTION SANITIZER ---
def sanitize_prompt_input(text):
    if not text:
        return ""
    forbidden_patterns = [
        r"ignore\s+previous\s+instructions",
        r"system\s*:",
        r"assistant\s*:",
        r"you\s+are\s+now\s+a"
    ]
    for pattern in forbidden_patterns:
        if re.search(pattern, text, re.IGNORECASE):
            raise ValueError("Invalid prompt content detected.")
    return text

def call_groq_api(prompt_text, image_data=None):
    if not api_key:
        return "Error: API Service Configuration Missing."
        
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
            knowledge_text += f"Topic: {markupsafe.escape(rec.title)}\nContent: {markupsafe.escape(rec.content)}\n\n"
        knowledge_text += "--- END OF KNOWLEDGE BASE ---\n"

    system_instruction = (
        "You are 'Tibyan AI', an authentic Islamic Ilmi assistant following the Hanafi school of thought (Fiqh-e-Hanafi).\n"
        "STRICT MANDATORY RULES:\n"
        "1. KNOWLEDGE BASE PRIORITIZATION: Strictly check provided custom knowledge base data first.\n"
        "2. LANGUAGE MATCHING: Respond strictly in the exact same language/script used by the user.\n"
        "3. NO INTERNAL THINKING: Output direct answers only.\n"
        f"{knowledge_text}"
    )

    try:
        clean_prompt = sanitize_prompt_input(prompt_text)
    except ValueError:
        return "Security Alert: Input contained disallowed characters or prompt manipulation patterns."

    delimited_user_prompt = f"[USER_INPUT_START]\n{clean_prompt}\n[USER_INPUT_END]"

    if image_data:
        selected_model = "llama-3.2-11b-vision-preview"
        if not image_data.startswith("data:image"):
            image_data = f"data:image/jpeg;base64,{image_data}"
        
        messages = [
            {"role": "system", "content": system_instruction},
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": delimited_user_prompt},
                    {"type": "image_url", "image_url": {"url": image_data}}
                ]
            }
        ]
    else:
        selected_model = "llama-3.3-70b-versatile"
        messages = [
            {"role": "system", "content": system_instruction},
            {"role": "user", "content": delimited_user_prompt}
        ]
    
    payload = {
        "model": selected_model,
        "messages": messages,
        "temperature": 0.3,
        "max_tokens": 1024,
        "top_p": 1
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        if response.status_code == 200:
            return response.json()['choices'][0]['message']['content']
        else:
            logger.error(f"Groq API Error Status: {response.status_code}")
            return "Unable to process request at this time."
    except Exception as e:
        logger.error(f"Groq Connection Exception: {str(e)}")
        return "Service temporarily unavailable."

# --- ROUTES ---
@app.route('/login', methods=['GET', 'POST'])
@limiter.limit("5 per minute")
def login():
    if request.method == 'POST':
        try:
            data = LoginSchema().load(request.form.to_dict())
        except ValidationError:
            flash('Invalid input structure.')
            return redirect(url_for('login'))

        user = User.query.filter_by(email=data['email'].lower()).first()
        if user and user.password and check_password_hash(user.password, data['password']):
            login_user(user, remember=True)
            return redirect(url_for('generate'))
        flash('Invalid email or password!')
    return "Login Page" # Apne template ke sath replace karein

@app.route('/signup', methods=['GET', 'POST'])
@limiter.limit("5 per minute")
def signup():
    if request.method == 'POST':
        try:
            data = SignupSchema().load(request.form.to_dict())
        except ValidationError:
            flash('Invalid parameters submitted.')
            return redirect(url_for('signup'))

        if data['password'] != data['confirm_password']:
            flash('Passwords do not match!')
            return redirect(url_for('signup'))

        if User.query.filter_by(email=data['email'].lower()).first():
            flash('Email is already registered!')
            return redirect(url_for('login'))
            
        hashed_password = generate_password_hash(data['password'], method='pbkdf2:sha256')
        first_user = User.query.first() is None
        new_user = User(name=data['name'], surname=data.get('surname'), email=data['email'].lower(), password=hashed_password, is_admin=first_user)
        
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user, remember=True)
        return redirect(url_for('generate'))
    return "Signup Page" # Apne template ke sath replace karein

@app.route('/generate', methods=['POST'])
@login_required
@limiter.limit("10 per minute")
def generate():
    try:
        data = GenerateSchema().load(request.json or {})
    except ValidationError:
        return jsonify({'error': 'Invalid payload size or format'}), 400

    ai_response = call_groq_api(data.get('prompt', ''), data.get('image'))
    return jsonify({'response': ai_response})

@app.route('/save_chat', methods=['POST'])
@login_required
@limiter.limit("30 per minute")
def save_chat():
    try:
        data = SaveChatSchema().load(request.json or {})
    except ValidationError:
        return jsonify({'status': 'invalid input'}), 400

    clean_html = sanitize_html(data['html'], tags=['div', 'span', 'p', 'br', 'strong', 'em', 'img', 'h1', 'h2', 'h3'], attributes={'img': ['src', 'class']})

    chat = ChatHistory.query.filter_by(user_id=current_user.id, chat_id=data['chat_id']).first()
    if chat:
        chat.title = data['title']
        chat.html_content = clean_html
        chat.timestamp = time.time()
    else:
        new_chat = ChatHistory(user_id=current_user.id, chat_id=data['chat_id'], title=data['title'], html_content=clean_html, timestamp=time.time())
        db.session.add(new_chat)
    db.session.commit()
    return jsonify({'status': 'success'})

@app.route('/admin/toggle_admin/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def toggle_admin(user_id):
    user = db.session.get(User, user_id)
    if user and user.id != current_user.id:
        user.is_admin = not user.is_admin
        db.session.commit()
    return jsonify({'status': 'success'})

@app.route('/admin/delete_user/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def delete_user(user_id):
    user = db.session.get(User, user_id)
    if user and user.id != current_user.id:
        db.session.delete(user)
        db.session.commit()
    return jsonify({'status': 'success'})

# --- RENDER ENTRYPOINT ---
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)


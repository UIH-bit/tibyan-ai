import os
import re
import time
import hmac
import hashlib
import requests
import secrets
from datetime import timedelta
from dotenv import load_dotenv

from flask import Flask, request, jsonify, render_template_string, url_for, redirect, flash, session, abort
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.middleware.proxy_fix import ProxyFix
from flask_mail import Mail, Message
from flask_wtf.csrf import CSRFProtect, generate_csrf, CSRFError
from marshmallow import Schema, fields, validate, ValidationError
import bleach

load_dotenv()

app = Flask(__name__)
# Enable ProxyFix for proper IP & HTTPS detection behind reverse proxies
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_port=1)

app.permanent_session_lifetime = timedelta(days=7)

# [A] Secrets & Configuration Handling
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
if not app.config['SECRET_KEY'] or len(app.config['SECRET_KEY']) < 32:
    raise RuntimeError("CRITICAL: SECRET_KEY environment variable is missing or insufficiently complex (min 32 chars).")

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
if not app.config['SQLALCHEMY_DATABASE_URI']:
    raise RuntimeError("CRITICAL: DATABASE_URL environment variable is missing.")

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5MB Payload Limit

# [D] Secure Cookie Policy
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Strict'
app.config['REMEMBER_COOKIE_HTTPONLY'] = True
app.config['REMEMBER_COOKIE_SECURE'] = True
app.config['REMEMBER_COOKIE_SAMESITE'] = 'Strict'

# Flask-Mail Configuration
app.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER')
app.config['MAIL_PORT'] = int(os.environ.get('MAIL_PORT', 587))
app.config['MAIL_USE_TLS'] = os.environ.get('MAIL_USE_TLS', 'True').lower() == 'true'
app.config['MAIL_USE_SSL'] = os.environ.get('MAIL_USE_SSL', 'False').lower() == 'true'
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')

db = SQLAlchemy(app)
mail = Mail(app)
csrf = CSRFProtect(app)

login_manager = LoginManager()
login_manager.login_message = None
login_manager.init_app(app)
login_manager.login_view = 'login'

API_KEY = os.environ.get("GROQ_API_KEY")

# [B] Sliding-Window Rate Limiter Logic
class RateLimiter:
    def __init__(self):
        self.requests = {}

    def is_rate_limited(self, key, limit, window=60):
        now = time.time()
        request_times = self.requests.get(key, [])
        request_times = [t for t in request_times if now - t < window]
        if len(request_times) >= limit:
            self.requests[key] = request_times
            return True
        request_times.append(now)
        self.requests[key] = request_times
        return False

limiter = RateLimiter()

def enforce_rate_limit(limit_type):
    def decorator(f):
        def wrapped(*args, **kwargs):
            # Safe IP extraction behind proxy using ProxyFix
            ip = request.remote_addr or "127.0.0.1"
            if limit_type == 'public':
                key, max_req = f"pub_{ip}", 20
            elif limit_type == 'auth':
                key, max_req = f"auth_{ip}", 5
            elif limit_type == 'user':
                uid = current_user.id if current_user.is_authenticated else ip
                key, max_req = f"usr_{uid}", 60
            elif limit_type == 'llm':
                uid = current_user.id if current_user.is_authenticated else ip
                key, max_req = f"llm_{uid}", 10
            else:
                key, max_req = f"gen_{ip}", 30

            if limiter.is_rate_limited(key, limit=max_req, window=60):
                resp = jsonify({"error": "Too many requests. Please try again later."})
                resp.status_code = 429
                resp.headers['Retry-After'] = '60'
                return resp
            return f(*args, **kwargs)
        wrapped.__name__ = f.__name__
        return wrapped
    return decorator

# Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    surname = db.Column(db.String(100), nullable=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password = db.Column(db.String(200), nullable=False)
    dob = db.Column(db.String(20), nullable=True)
    pic = db.Column(db.Text, nullable=True)

class ChatHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    chat_id = db.Column(db.String(100), nullable=False, index=True)
    title = db.Column(db.String(200), nullable=False)
    html_content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.Float, nullable=False)

# [C] Input Schemas & Sanitization
class SignupSchema(Schema):
    name = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    surname = fields.Str(required=False, validate=validate.Length(max=100))
    email = fields.Email(required=True, validate=validate.Length(max=120))
    password = fields.Str(required=True, validate=validate.Length(min=8, max=128))

class PromptSchema(Schema):
    prompt = fields.Str(required=False, validate=validate.Length(max=1500))
    image = fields.Str(required=False, validate=validate.Length(max=4000000)) # Strict image bound

class ProfileUpdateSchema(Schema):
    name = fields.Str(required=False, validate=validate.Length(min=1, max=100))
    surname = fields.Str(required=False, validate=validate.Length(max=100))
    dob = fields.Str(required=False, validate=validate.Length(max=20))

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

with app.app_context():
    db.create_all()

# [F] Security Headers & HTTPS Enforcement
@app.before_request
def enforce_https():
    if not request.is_secure and app.env != 'development':
        return redirect(request.url.replace("http://", "https://"), code=301)

@app.after_request
def apply_security_headers(response):
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    response.headers['Content-Security-Policy'] = (
        "default-src 'self'; "
        "script-src 'self' https://cdn.jsdelivr.net; "
        "style-src 'self' https://cdn.jsdelivr.net; "
        "img-src 'self' data:; "
        "object-src 'none';"
    )
    response.headers['Permissions-Policy'] = 'camera=(), microphone=(), geolocation=()'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    return response

# [G] Safe Error Handlers
@app.errorhandler(CSRFError)
def handle_csrf_error(e):
    return jsonify({"error": "CSRF token validation failed."}), 400

@app.errorhandler(Exception)
def handle_exception(e):
    app.logger.error(f"Internal Exception Captured: {type(e).__name__}")
    return jsonify({"error": "An internal server error occurred."}), 500

# [C & E] Input Sanitization & HTML Cleaning
def sanitize_text(text):
    if not text:
        return ""
    # Strip HTML tags from standard text inputs
    cleaned = bleach.clean(str(text), tags=[], strip=True).strip()
    return cleaned[:1500]

def sanitize_html(raw_html):
    if not raw_html:
        return ""
    # Allowed tags for safe rendered chat history
    allowed_tags = ['p', 'b', 'i', 'strong', 'em', 'ul', 'ol', 'li', 'br', 'code', 'pre', 'h1', 'h2', 'h3']
    return bleach.clean(raw_html, tags=allowed_tags, strip=True)

INJECTION_PATTERNS = [
    r"ignore\s+previous\s+instructions",
    r"system:",
    r"assistant:",
    r"override\s+system\s+prompt",
    r"\[USER_INPUT_START\]",
    r"\[USER_INPUT_END\]"
]

def check_prompt_injection(text):
    for pattern in INJECTION_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            raise ValueError("Invalid input pattern detected.")

def generate_otp_hash(email, otp):
    secret = app.config['SECRET_KEY'].encode('utf-8')
    data = f"{email}:{otp}".encode('utf-8')
    return hmac.new(secret, data, hashlib.sha256).hexdigest()

def call_groq_api(prompt_text, image_data=None):
    if not API_KEY:
        return "Service processing is currently unavailable."
        
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        'Authorization': f'Bearer {API_KEY}',
        'Content-Type': 'application/json'
    }
    
    system_instruction = (
        "Aap 'Tibyan AI' hain, ek authentic Islamic Ilmi assistant jo Fiqh-e-Hanafi ki pehravani karte hain.\n"
        "STRICT MANDATORY RULES:\n"
        "1. Internal thinking, reasoning, ya analysis steps ki vazaahat bilkul na karein.\n"
        "2. LANGUAGE MATCHING: Jis zabaan me sawaal pucha jaye, usi me jawaab dein.\n"
        "3. Jawaab clear aur structured rakhein.\n"
    )

    clean_text = sanitize_text(prompt_text)
    check_prompt_injection(clean_text)
    
    delimited_input = f"[USER_INPUT_START]\n{clean_text}\n[USER_INPUT_END]"

    if image_data:
        selected_model = "llama-3.2-11b-vision-preview"
        if not re.match(r'^data:image/(jpeg|png|webp);base64,', image_data):
            return "Invalid image format."
        
        messages = [
            {"role": "system", "content": system_instruction},
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": delimited_input},
                    {"type": "image_url", "image_url": {"url": image_data}}
                ]
            }
        ]
    else:
        selected_model = "llama-3.3-70b-versatile"
        messages = [
            {"role": "system", "content": system_instruction},
            {"role": "user", "content": delimited_input}
        ]
    
    payload = {
        "model": selected_model,
        "messages": messages,
        "temperature": 0.4,
        "max_completion_tokens": 1024,
        "top_p": 1
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=20)
        if response.status_code == 200:
            content = response.json()['choices'][0]['message']['content']
            return bleach.clean(content, strip=True)
        return "Service response failed."
    except Exception:
        return "Network connection issue. Service unavailable."

# Routes

@app.route('/login', methods=['GET', 'POST'])
@enforce_rate_limit('auth')
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            session.clear()  # Session Fixation Defense
            login_user(user, remember=False)
            return redirect(url_for('home'))
        flash('Invalid email or password!')
    return render_template_string("<!-- AUTH TEMPLATE -->", title='Login', is_signup=False, is_forgot_request=False, btn_text='Login', csrf_token=generate_csrf())

@app.route('/signup', methods=['GET', 'POST'])
@enforce_rate_limit('auth')
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    if request.method == 'POST':
        try:
            data = SignupSchema().load(request.form.to_dict())
        except ValidationError:
            flash('Invalid input parameters.')
            return redirect(url_for('signup'))

        if data['password'] != request.form.get('confirm_password', ''):
            flash('Passwords do not match!')
            return redirect(url_for('signup'))

        if User.query.filter_by(email=data['email']).first():
            flash('Email is already registered!')
            return redirect(url_for('login'))
            
        hashed_password = generate_password_hash(data['password'], method='pbkdf2:sha256')
        new_user = User(name=sanitize_text(data['name']), surname=sanitize_text(data.get('surname', '')), email=data['email'], password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        session.clear()
        login_user(new_user, remember=False)
        return redirect(url_for('home'))
    return render_template_string("<!-- AUTH TEMPLATE -->", title='Create Account', is_signup=True, is_forgot_request=False, btn_text='Sign Up', csrf_token=generate_csrf())

@app.route('/forgot_password', methods=['GET', 'POST'])
@enforce_rate_limit('auth')
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        user = User.query.filter_by(email=email).first()
        if not user:
            flash('If the email exists, an OTP has been dispatched.')
            return redirect(url_for('forgot_password'))
        
        otp = f"{secrets.randbelow(900000) + 100000}"
        session['reset_email'] = email
        session['reset_otp_hash'] = generate_otp_hash(email, otp)
        session['reset_otp_expiry'] = time.time() + 600

        try:
            msg = Message('Password Reset OTP', sender=os.environ.get('MAIL_USERNAME'), recipients=[email])
            msg.body = f"Your OTP is: {otp}"
            mail.send(msg)
            return redirect(url_for('verify_otp'))
        except Exception:
            flash('Failed to dispatch OTP.')
            
    return render_template_string("<!-- AUTH TEMPLATE -->", title='Reset Password', is_signup=False, is_forgot_request=True, btn_text='Send OTP', csrf_token=generate_csrf())

@app.route('/verify_otp', methods=['GET', 'POST'])
@enforce_rate_limit('auth')
def verify_otp():
    if 'reset_email' not in session or 'reset_otp_hash' not in session:
        return redirect(url_for('forgot_password'))
        
    if request.method == 'POST':
        entered_otp = request.form.get('otp', '').strip()
        new_password = request.form.get('new_password', '').strip()
        email = session.get('reset_email')

        if time.time() > session.get('reset_otp_expiry', 0):
            session.clear()
            flash('OTP has expired!')
            return redirect(url_for('forgot_password'))

        computed_hash = generate_otp_hash(email, entered_otp)
        if hmac.compare_digest(computed_hash, session.get('reset_otp_hash', '')):
            if len(new_password) < 8:
                flash('Password must be at least 8 characters!')
                return render_template_string("<!-- OTP TEMPLATE -->", csrf_token=generate_csrf())

            user = User.query.filter_by(email=email).first()
            if user:
                user.password = generate_password_hash(new_password, method='pbkdf2:sha256')
                db.session.commit()
            
            session.clear()
            flash('Password changed successfully!')
            return redirect(url_for('login'))
        else:
            flash('Invalid OTP code!')
            
    return render_template_string("<!-- OTP TEMPLATE -->", csrf_token=generate_csrf())

@app.route('/logout')
@login_required
def logout():
    session.clear()
    logout_user()
    return redirect(url_for('login'))

@app.route('/')
@login_required
@enforce_rate_limit('user')
def home():
    return render_template_string("<!-- HOME TEMPLATE -->", user=current_user, csrf_token=generate_csrf())

@app.route('/generate', methods=['POST'])
@login_required
@enforce_rate_limit('llm')
def generate():
    try:
        data = PromptSchema().load(request.json or {})
        prompt = sanitize_text(data.get('prompt', ''))
        ai_response = call_groq_api(prompt, data.get('image'))
        return jsonify({'response': ai_response})
    except (ValidationError, ValueError):
        return jsonify({'error': 'Invalid request data.'}), 400

@app.get('/get_chats')
@login_required
@enforce_rate_limit('user')
def get_chats():
    chats = ChatHistory.query.filter_by(user_id=current_user.id).all()
    return jsonify({c.chat_id: {'title': c.title, 'html': c.html_content, 'time': c.timestamp} for c in chats})

@app.route('/save_chat', methods=['POST'])
@login_required
@enforce_rate_limit('user')
def save_chat():
    data = request.json or {}
    c_id = sanitize_text(data.get('chat_id'))
    if not c_id: return jsonify({'status': 'error', 'message': 'Invalid Chat ID'}), 400
    
    chat = ChatHistory.query.filter_by(user_id=current_user.id, chat_id=c_id).first()
    safe_title = sanitize_text(data.get('title', 'Untitled Chat'))
    safe_html = sanitize_html(data.get('html', ''))
    
    if chat:
        chat.title = safe_title
        chat.html_content = safe_html
        chat.timestamp = time.time()
    else:
        new_chat = ChatHistory(user_id=current_user.id, chat_id=c_id, title=safe_title, html_content=safe_html, timestamp=time.time())
        db.session.add(new_chat)
    db.session.commit()
    return jsonify({'status': 'success'})

@app.route('/delete_chat', methods=['POST'])
@login_required
@enforce_rate_limit('user')
def delete_chat():
    data = request.json or {}
    c_id = sanitize_text(data.get('chat_id'))
    if not c_id: return jsonify({'status': 'error', 'message': 'Invalid Chat ID'}), 400
    chat = ChatHistory.query.filter_by(user_id=current_user.id, chat_id=c_id).first()
    if chat:
        db.session.delete(chat)
        db.session.commit()
    return jsonify({'status': 'success'})

@app.route('/update_profile', methods=['POST'])
@login_required
@enforce_rate_limit('user')
def update_profile():
    try:
        data = ProfileUpdateSchema().load(request.json or {})
        if 'name' in data:
            current_user.name = sanitize_text(data['name'])
        if 'surname' in data:
            current_user.surname = sanitize_text(data['surname'])
        if 'dob' in data:
            current_user.dob = sanitize_text(data['dob'])
        db.session.commit()
        return jsonify({'status': 'success'})
    except ValidationError:
        return jsonify({'error': 'Invalid profile fields.'}), 400

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=False)


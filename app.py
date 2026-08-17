import os
import requests
import time
import random
import traceback
from datetime import timedelta
from functools import wraps
from dotenv import load_dotenv

from flask import Flask, request, jsonify, render_template, url_for, redirect, flash, session, abort
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_mail import Mail, Message
from authlib.integrations.flask_client import OAuth
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_wtf.csrf import CSRFProtect
from marshmallow import Schema, fields, validate, ValidationError

load_dotenv()

app = Flask(__name__)
app.permanent_session_lifetime = timedelta(days=1)

# SECRETS VALIDATION
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
if not app.config['SECRET_KEY']:
    raise ValueError("CRITICAL: SECRET_KEY environment variable is missing.")

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
if not app.config['SQLALCHEMY_DATABASE_URI']:
    raise ValueError("CRITICAL: DATABASE_URL environment variable is missing.")

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# COOKIE SECURITY HARDENING
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Strict'

# Flask-Mail Configuration
app.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
app.config['MAIL_PORT'] = int(os.environ.get('MAIL_PORT', 587))
app.config['MAIL_USE_TLS'] = os.environ.get('MAIL_USE_TLS', 'True') == 'True'
app.config['MAIL_USE_SSL'] = os.environ.get('MAIL_USE_SSL', 'False') == 'False'
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')

db = SQLAlchemy(app)
mail = Mail(app)
csrf = CSRFProtect(app)

# RATE LIMITING
limiter = Limiter(
    key_func=get_remote_address,
    app=app,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://"
)

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

# --- INPUT VALIDATION SCHEMAS ---
class SignupSchema(Schema):
    name = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    surname = fields.Str(allow_none=True, validate=validate.Length(max=100))
    email = fields.Email(required=True, validate=validate.Length(max=120))
    password = fields.Str(required=True, validate=validate.Length(min=8, max=200))
    confirm_password = fields.Str(required=True, validate=validate.Length(min=8, max=200))

class LoginSchema(Schema):
    email = fields.Email(required=True, validate=validate.Length(max=120))
    password = fields.Str(required=True, validate=validate.Length(max=200))

class PromptSchema(Schema):
    prompt = fields.Str(required=False, allow_none=True, validate=validate.Length(max=5000))
    image = fields.Str(required=False, allow_none=True)

class ProfileSchema(Schema):
    name = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    surname = fields.Str(allow_none=True, validate=validate.Length(max=100))
    dob = fields.Str(allow_none=True, validate=validate.Length(max=20))
    pic = fields.Str(allow_none=True)

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

# --- ADMIN DECORATOR ---
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
    if not getattr(app, '_database_checked', False):
        db.create_all()
        admin_email = os.environ.get('ADMIN_EMAIL')
        if admin_email:
            first_admin = User.query.filter_by(email=admin_email).first()
            if first_admin:
                first_admin.is_admin = True
                db.session.commit()
        app._database_checked = True

# SECURITY HEADERS & ERROR HANDLING
@app.after_request
def set_security_headers(response):
    response.headers['Content-Security-Policy'] = "default-src 'self' https://cdn.jsdelivr.net; img-src 'self' data: https:; style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net;"
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    response.headers['Permissions-Policy'] = 'camera=(), microphone=(), geolocation=()'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    return response

@app.errorhandler(Exception)
def handle_exception(e):
    app.logger.error(f"Unhandled Exception: {traceback.format_exc()}")
    return render_template('error.html'), 500

def call_groq_api(prompt_text, image_data=None):
    if not api_key:
        return "Error: API Key is missing. Please set GROQ_API_KEY in .env file."
        
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

    safe_prompt = f"[USER_INPUT_START]\n{prompt_text or ''}\n[USER_INPUT_END]"

    if image_data:
        selected_model = "llama-3.2-11b-vision-preview"
        if not image_data.startswith("data:image"):
            image_data = f"data:image/jpeg;base64,{image_data}"
        
        messages = [
            {"role": "system", "content": system_instruction},
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": safe_prompt},
                    {"type": "image_url", "image_url": {"url": image_data}}
                ]
            }
        ]
    else:
        selected_model = "llama-3.3-70b-versatile"
        messages = [
            {"role": "system", "content": system_instruction},
            {"role": "user", "content": safe_prompt}
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
            return "API Error encountered. Please try again later."
    except Exception as e:
        app.logger.error(f"API Connection Error: {str(e)}")
        return "API Connection Error."

# --- ROUTES ---
@app.route('/login', methods=['GET', 'POST'])
@limiter.limit("5 per minute")
def login():
    if request.method == 'POST':
        try:
            data = LoginSchema().load(request.form)
        except ValidationError:
            flash('Invalid input format.')
            return render_template('auth.html', title='Login', is_signup=False, is_forgot_request=False, btn_text='Login')

        email = data['email'].strip().lower()
        password = data['password']
        user = User.query.filter_by(email=email).first()
        if user and user.password and check_password_hash(user.password, password):
            login_user(user, remember=True)
            return redirect(url_for('home'))
        flash('Invalid email or password!')
    return render_template('auth.html', title='Login', is_signup=False, is_forgot_request=False, btn_text='Login')

@app.route('/google-login')
@limiter.limit("5 per minute")
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
    picture = user_info.get('picture', '')

    user = User.query.filter_by(email=email).first()
    if not user:
        user = User(name=name, surname=surname, email=email, pic=picture, password=None)
        db.session.add(user)
        db.session.commit()
    
    login_user(user, remember=True)
    return redirect(url_for('home'))

@app.route('/signup', methods=['GET', 'POST'])
@limiter.limit("5 per minute")
def signup():
    if request.method == 'POST':
        try:
            data = SignupSchema().load(request.form)
        except ValidationError:
            flash('Invalid input format or validation error.')
            return redirect(url_for('signup'))
        
        if data['password'] != data['confirm_password']:
            flash('Passwords do not match!')
            return redirect(url_for('signup'))

        email = data['email'].strip().lower()
        user_exists = User.query.filter_by(email=email).first()
        if user_exists:
            flash('Email is already registered! Please login.')
            return redirect(url_for('login'))
            
        hashed_password = generate_password_hash(data['password'], method='pbkdf2:sha256')
        first_user = User.query.first() is None
        new_user = User(name=data['name'], surname=data.get('surname'), email=email, password=hashed_password, is_admin=first_user)
        
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user, remember=True)
        return redirect(url_for('home'))
    return render_template('auth.html', title='Create Account', is_signup=True, is_forgot_request=False, btn_text='Sign Up')

@app.route('/forgot_password', methods=['GET', 'POST'])
@limiter.limit("5 per minute")
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
            flash('Failed to send email.')
            
    return render_template('auth.html', title='Reset Password', is_signup=False, is_forgot_request=True, btn_text='Send OTP')

@app.route('/verify_otp', methods=['GET', 'POST'])
@limiter.limit("5 per minute")
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
            flash('Invalid OTP!')
            
    return render_template('verify_otp.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    session.clear()
    return redirect(url_for('login'))

@app.route('/')
@login_required
@limiter.limit("60 per minute")
def home():
    return render_template('chat.html', user=current_user)

# --- ADMIN PANEL ROUTES ---
@app.route('/admin')
@login_required
@admin_required
@limiter.limit("60 per minute")
def admin_dashboard():
    users = User.query.order_by(User.id.desc()).all()
    total_users = User.query.count()
    total_admins = User.query.filter_by(is_admin=True).count()
    knowledge_items = CustomKnowledge.query.order_by(CustomKnowledge.id.desc()).all()
    return render_template('admin.html', users=users, total_users=total_users, total_admins=total_admins, knowledge_items=knowledge_items)

@app.route('/admin/edit_user/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def edit_user(user_id):
    user = db.session.get(User, user_id)
    if user:
        user.name = request.form.get('name', user.name)
        user.surname = request.form.get('surname', user.surname)
        user.email = request.form.get('email', user.email)
        user.dob = request.form.get('dob', user.dob)
        db.session.commit()
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/toggle_admin/<int:user_id>')
@login_required
@admin_required
def toggle_admin(user_id):
    user = db.session.get(User, user_id)
    if user and user.id != current_user.id:
        user.is_admin = not user.is_admin
        db.session.commit()
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/delete_user/<int:user_id>')
@login_required
@admin_required
def delete_user(user_id):
    user = db.session.get(User, user_id)
    if user and user.id != current_user.id:
        db.session.delete(user)
        db.session.commit()
    return redirect(url_for('admin_dashboard'))

# --- ADMIN KNOWLEDGE BASE ROUTES ---
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

@app.route('/admin/edit_knowledge/<int:item_id>', methods=['POST'])
@login_required
@admin_required
def edit_knowledge(item_id):
    record = db.session.get(CustomKnowledge, item_id)
    if record:
        record.title = request.form.get('title', record.title)
        record.content = request.form.get('content', record.content)
        record.updated_at = time.time()
        db.session.commit()
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/delete_knowledge/<int:item_id>')
@login_required
@admin_required
def delete_knowledge(item_id):
    record = db.session.get(CustomKnowledge, item_id)
    if record:
        db.session.delete(record)
        db.session.commit()
    return redirect(url_for('admin_dashboard'))

@app.route('/generate', methods=['POST'])
@login_required
@limiter.limit("10 per minute")
def generate():
    try:
        data = PromptSchema().load(request.json or {})
    except ValidationError:
        return jsonify({'response': 'Invalid input schema.'}), 400

    ai_response = call_groq_api(data.get('prompt', ''), data.get('image'))
    return jsonify({'response': ai_response})

@app.get('/get_chats')
@login_required
@limiter.limit("60 per minute")
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
@limiter.limit("60 per minute")
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
@limiter.limit("60 per minute")
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
@limiter.limit("60 per minute")
def update_profile():
    try:
        data = ProfileSchema().load(request.json or {})
    except ValidationError:
        return jsonify({'status': 'error'}), 400

    current_user.name = data.get('name', current_user.name)
    current_user.surname = data.get('surname', current_user.surname)
    current_user.dob = data.get('dob', current_user.dob)
    current_user.pic = data.get('pic', current_user.pic)
    db.session.commit()
    return jsonify({'status': 'success'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)


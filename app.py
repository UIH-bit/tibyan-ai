import os
import requests
import time
import logging
from datetime import timedelta
from functools import wraps
from dotenv import load_dotenv

from flask import Flask, request, jsonify, render_template_string, url_for, redirect, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_mail import Mail
from flask_wtf.csrf import CSRFProtect

# Load environment variables
load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.permanent_session_lifetime = timedelta(days=30)

is_production = os.environ.get('FLASK_ENV') == 'production'

app.config['SESSION_COOKIE_SECURE'] = is_production
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

SECRET_KEY = os.environ.get('SECRET_KEY')
if not SECRET_KEY:
    if is_production:
        raise RuntimeError("CRITICAL: SECRET_KEY environment variable is not set!")
    SECRET_KEY = os.urandom(32).hex()
app.config['SECRET_KEY'] = SECRET_KEY

csrf = CSRFProtect(app)

db_url = os.environ.get('DATABASE_URL', 'sqlite:///database.db')
if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)
app.config['SQLALCHEMY_DATABASE_URI'] = db_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
mail = Mail(app)

login_manager = LoginManager()
login_manager.login_message = None
login_manager.init_app(app)
login_manager.login_view = 'login'

@app.after_request
def set_security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    return response

# --- DATABASE MODELS ---
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    surname = db.Column(db.String(100), nullable=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password = db.Column(db.String(200), nullable=True)
    dob = db.Column(db.String(20), nullable=True)
    pic = db.Column(db.Text, nullable=True)
    is_admin = db.Column(db.Boolean, default=False)

class CustomKnowledge(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    updated_at = db.Column(db.Float, default=time.time)

with app.app_context():
    try:
        db.create_all()
    except Exception as err:
        logger.error(f"Database Creation Error: {err}")

# --- DECORATORS ---
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
    api_key = os.environ.get("GROQ_API_KEY") or os.environ.get("GEMINI_API_KEY")
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
        "1. KNOWLEDGE BASE PRIORITIZATION: Strictly check custom knowledge base data first.\n"
        "2. STRICT LANGUAGE MATCHING: Respond strictly in the EXACT same language/script used by the user.\n"
        "3. ABSOLUTELY NO INTERNAL THINKING: Do NOT output any internal thinking.\n"
        "4. FORMATTING: Provide clear Markdown headers (### Heading) where appropriate.\n"
        f"{knowledge_text}"
    )

    if image_data:
        selected_model = "llama-3.2-11b-vision-preview"
        if not image_data.startswith("data:image"):
            image_data = f"data:image/jpeg;base64,{image_data}"
        messages = [
            {"role": "system", "content": system_instruction},
            {"role": "user", "content": [{"type": "text", "text": prompt_text or "Please analyze this image."}, {"type": "image_url", "image_url": {"url": image_data}}]}
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
        return f"API Error ({response.status_code}): {response.text}"
    except Exception as e:
        return f"API Connection Error: {str(e)}"

# --- TEMPLATES ---
AUTH_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ title }}</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-900 text-white flex items-center justify-center min-h-screen">
    <div class="bg-gray-800 p-8 rounded-xl shadow-lg w-full max-w-md">
        <h2 class="text-2xl font-bold mb-6 text-center">{{ title }}</h2>
        {% with messages = get_flashed_messages() %}
          {% if messages %}
            <div class="bg-red-500 text-white p-3 rounded mb-4 text-sm">{{ messages[0] }}</div>
          {% endif %}
        {% endwith %}
        <form method="POST">
            <input type="hidden" name="csrf_token" value="{{ csrf_token() }}"/>
            {% if is_signup %}
            <div class="mb-4">
                <label class="block text-sm mb-2">First Name</label>
                <input type="text" name="name" required class="w-full p-2 rounded bg-gray-700 border border-gray-600 focus:outline-none">
            </div>
            <div class="mb-4">
                <label class="block text-sm mb-2">Surname</label>
                <input type="text" name="surname" class="w-full p-2 rounded bg-gray-700 border border-gray-600 focus:outline-none">
            </div>
            {% endif %}
            <div class="mb-4">
                <label class="block text-sm mb-2">Email</label>
                <input type="email" name="email" required class="w-full p-2 rounded bg-gray-700 border border-gray-600 focus:outline-none">
            </div>
            <div class="mb-4">
                <label class="block text-sm mb-2">Password</label>
                <input type="password" name="password" required class="w-full p-2 rounded bg-gray-700 border border-gray-600 focus:outline-none">
            </div>
            {% if is_signup %}
            <div class="mb-4">
                <label class="block text-sm mb-2">Confirm Password</label>
                <input type="password" name="confirm_password" required class="w-full p-2 rounded bg-gray-700 border border-gray-600 focus:outline-none">
            </div>
            {% endif %}
            <button type="submit" class="w-full bg-blue-600 hover:bg-blue-700 p-2 rounded font-semibold transition">{{ btn_text }}</button>
        </form>
        <p class="mt-4 text-center text-sm text-gray-400">
            {% if is_signup %}
            Already have an account? <a href="{{ url_for('login') }}" class="text-blue-400 hover:underline">Login</a>
            {% else %}
            Don't have an account? <a href="{{ url_for('signup') }}" class="text-blue-400 hover:underline">Sign up</a>
            {% endif %}
        </p>
    </div>
</body>
</html>
"""

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Tibyan AI</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
</head>
<body class="bg-gray-950 text-gray-100 flex h-screen overflow-hidden">
    <div class="flex-1 flex flex-col h-full">
        <header class="bg-gray-900 border-b border-gray-800 p-4 flex justify-between items-center">
            <h1 class="text-xl font-bold text-emerald-400">Tibyan AI</h1>
            <div class="flex items-center gap-4">
                <span class="text-sm text-gray-300">Salam, {{ user.name }}</span>
                {% if user.is_admin %}
                <a href="{{ url_for('admin_dashboard') }}" class="bg-amber-600 px-3 py-1 rounded text-sm hover:bg-amber-700">Admin Panel</a>
                {% endif %}
                <a href="{{ url_for('logout') }}" class="bg-red-600 px-3 py-1 rounded text-sm hover:bg-red-700">Logout</a>
            </div>
        </header>
        <div id="chat-container" class="flex-1 overflow-y-auto p-4 space-y-4 max-w-3xl w-full mx-auto"></div>
        <div class="p-4 bg-gray-900 border-t border-gray-800">
            <div class="max-w-3xl mx-auto flex gap-2">
                <input type="text" id="prompt-input" placeholder="Ask a question..." class="flex-1 bg-gray-800 border border-gray-700 rounded p-2 focus:outline-none">
                <button onclick="sendMessage()" class="bg-emerald-600 px-4 py-2 rounded hover:bg-emerald-700">Send</button>
            </div>
        </div>
    </div>
    <script>
        const csrfToken = "{{ csrf_token() }}";
        async function sendMessage() {
            const input = document.getElementById('prompt-input');
            const prompt = input.value.trim();
            if(!prompt) return;
            const container = document.getElementById('chat-container');
            container.innerHTML += `<div class="text-right"><span class="bg-blue-600 p-2 rounded inline-block">${prompt}</span></div>`;
            input.value = '';
            
            const res = await fetch('/generate', {
                method: 'POST',
                headers: {'Content-Type': 'application/json', 'X-CSRFToken': csrfToken},
                body: JSON.stringify({prompt})
            });
            const data = await res.json();
            container.innerHTML += `<div><span class="bg-gray-800 p-2 rounded inline-block">${marked.parse(data.response)}</span></div>`;
            container.scrollTop = container.scrollHeight;
        }
    </script>
</body>
</html>
"""

ADMIN_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Admin Dashboard</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-900 text-white p-8">
    <div class="max-w-5xl mx-auto">
        <div class="flex justify-between items-center mb-6">
            <h1 class="text-3xl font-bold">Admin Dashboard</h1>
            <a href="{{ url_for('home') }}" class="bg-gray-700 px-4 py-2 rounded hover:bg-gray-600">Back to Chat</a>
        </div>
        <div class="bg-gray-800 p-6 rounded-lg mb-6">
            <h2 class="text-xl font-semibold mb-4">Stats</h2>
            <p>Total Users: {{ total_users }} | Total Admins: {{ total_admins }}</p>
        </div>
        <div class="bg-gray-800 p-6 rounded-lg">
            <h2 class="text-xl font-semibold mb-4">Users List</h2>
            <table class="w-full text-left border-collapse">
                <thead><tr class="border-b border-gray-700"><th class="p-2">Name</th><th class="p-2">Email</th><th class="p-2">Admin</th><th class="p-2">Action</th></tr></thead>
                <tbody>
                    {% for u in users %}
                    <tr class="border-b border-gray-700">
                        <td class="p-2">{{ u.name }}</td>
                        <td class="p-2">{{ u.email }}</td>
                        <td class="p-2">{{ 'Yes' if u.is_admin else 'No' }}</td>
                        <td class="p-2">
                            {% if u.id != current_user.id %}
                            <a href="{{ url_for('toggle_admin', user_id=u.id) }}" class="text-blue-400 hover:underline mr-2">Toggle Admin</a>
                            <a href="{{ url_for('delete_user', user_id=u.id) }}" class="text-red-400 hover:underline">Delete</a>
                            {% endif %}
                        </td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </div>
</body>
</html>
"""

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

        if User.query.filter_by(email=email).first():
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

@app.route('/admin/toggle_admin/<int:user_id>')
@login_required
@admin_required
def toggle_admin(user_id):
    if user_id != current_user.id:
        user = db.session.get(User, user_id)
        if user:
            user.is_admin = not user.is_admin
            db.session.commit()
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/delete_user/<int:user_id>')
@login_required
@admin_required
def delete_user(user_id):
    if user_id != current_user.id:
        user = db.session.get(User, user_id)
        if user:
            db.session.delete(user)
            db.session.commit()
    return redirect(url_for('admin_dashboard'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)


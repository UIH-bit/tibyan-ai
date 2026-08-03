from flask import Flask, request, jsonify, render_template_string
import os
import requests

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Tibyan AI</title>
    <link rel="manifest" href="/manifest.json">
    <meta name="theme-color" content="#ffffff">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }
        body { background-color: #ffffff; color: #1f1f1f; display: flex; height: 100vh; overflow: hidden; }
        
        /* Auth Screen Overlay */
        #auth-screen { position: fixed; top: 0; left: 0; width: 100%; height: 100vh; background: #ffffff; z-index: 9999; display: flex; align-items: center; justify-content: center; padding: 20px; }
        .auth-card { width: 100%; max-width: 400px; background: #ffffff; border: 1px solid #e0e0e0; padding: 30px; border-radius: 20px; box-shadow: 0 4px 20px rgba(0,0,0,0.05); display: flex; flex-direction: column; gap: 16px; text-align: center; }
        .auth-card h2 { font-size: 24px; color: #1a73e8; display: flex; align-items: center; justify-content: center; gap: 8px; }
        .social-btn { display: flex; align-items: center; justify-content: center; gap: 10px; background: #ffffff; border: 1px solid #dadce0; padding: 12px; border-radius: 12px; font-size: 15px; cursor: pointer; color: #3c4043; width: 100%; }
        .auth-input { width: 100%; padding: 12px 16px; border: 1px solid #dadce0; border-radius: 12px; font-size: 14px; outline: none; }
        .auth-btn { background: #1a73e8; color: white; border: none; padding: 12px; border-radius: 12px; font-size: 15px; cursor: pointer; width: 100%; }
        
        /* Sidebar Drawer */
        .sidebar { width: 280px; background-color: #f9fbfd; border-right: 1px solid #e0e0e0; display: flex; flex-direction: column; height: 100vh; position: fixed; top: 0; left: -280px; transition: left 0.3s ease; z-index: 1000; }
        .sidebar.open { left: 0; }
        .sidebar-header { padding: 16px; border-bottom: 1px solid #f0f0f0; }
        .new-chat-btn { display: flex; align-items: center; gap: 8px; background: #ffffff; border: 1px solid #dadce0; color: #1a73e8; padding: 10px 14px; border-radius: 16px; font-size: 14px; cursor: pointer; width: 100%; justify-content: center; }
        .sidebar-menu { flex: 1; overflow-y: auto; padding: 12px; display: flex; flex-direction: column; gap: 4px; }
        .menu-item { display: flex; align-items: center; gap: 12px; padding: 10px 14px; border-radius: 10px; color: #3c4043; font-size: 14px; cursor: pointer; }
        .menu-item:hover { background: #f1f3f4; }
        .sidebar-footer { padding: 12px; border-top: 1px solid #f0f0f0; font-size: 13px; color: #5f6368; display: flex; justify-content: space-between; }

        /* Main UI */
        .main-wrapper { flex: 1; display: flex; flex-direction: column; height: 100vh; width: 100%; }
        header { display: flex; align-items: center; justify-content: space-between; padding: 14px 20px; background: #ffffff; border-bottom: 1px solid #f0f0f0; position: sticky; top: 0; z-index: 99; }
        .menu-toggle { background: transparent; border: none; font-size: 20px; cursor: pointer; color: #444746; padding: 6px; }
        
        .content-area { flex: 1; overflow-y: auto; padding: 24px; display: flex; flex-direction: column; align-items: center; padding-bottom: 140px; }
        .view { width: 100%; max-width: 800px; display: none; flex-direction: column; }
        .view.active { display: flex; }
        .home-center { text-align: center; margin: auto 0; width: 100%; }
        .greeting { font-size: 36px; color: #1f1f1f; margin-bottom: 10px; font-family: serif; }
        
        #chat-box { width: 100%; text-align: left; display: none; flex-direction: column; gap: 20px; }
        .msg-container { width: 100%; margin-bottom: 15px; display: flex; flex-direction: column; gap: 8px; }
        .msg { font-size: 15px; line-height: 1.6; white-space: pre-wrap; width: 100%; }
        .user-msg { background: #f0f4f9; color: #1f1f1f; padding: 12px 18px; border-radius: 18px 18px 4px 18px; align-self: flex-end; max-width: 85%; margin-left: auto; display: flex; flex-direction: column; gap: 8px; }
        .bot-msg { color: #202124; padding: 4px 0; align-self: flex-start; width: 100%; }
        .chat-img { max-width: 200px; max-height: 200px; border-radius: 10px; object-fit: cover; }
        
        /* Bottom Input Panel */
        .bottom-panel { position: fixed; bottom: 0; left: 0; width: 100%; background: #ffffff; padding: 12px 20px; display: flex; flex-direction: column; align-items: center; z-index: 98; border-top: 1px solid #f0f0f0; gap: 8px; }
        .image-preview-bar { display: none; width: 100%; max-width: 750px; align-items: center; gap: 10px; padding: 4px 8px; }
        .image-preview-bar img { width: 50px; height: 50px; border-radius: 8px; object-fit: cover; border: 1px solid #dadce0; }
        
        .input-box { display: flex; align-items: flex-end; background-color: #f0f4f9; border-radius: 28px; padding: 10px 16px; width: 100%; max-width: 750px; gap: 8px; }
        .input-box textarea { flex: 1; background: transparent; border: none; outline: none; color: #1f1f1f; font-size: 15px; resize: none; max-height: 120px; min-height: 24px; }
        .tool-btn { background: transparent; border: none; color: #444746; font-size: 18px; cursor: pointer; padding: 6px; display: flex; align-items: center; justify-content: center; }
        .send-btn { background: #1a73e8; border: none; color: #ffffff; width: 38px; height: 38px; border-radius: 50%; cursor: pointer; display: flex; align-items: center; justify-content: center; }

        .overlay { position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.3); display: none; z-index: 999; }
        .overlay.active { display: block; }
    </style>
</head>
<body>

    <div id="auth-screen">
        <div class="auth-card">
            <h2><i class="fa-solid fa-sparkles"></i> Tibyan AI</h2>
            <p id="auth-subtitle">Please sign in or create an account</p>
            <button class="social-btn" onclick="handleGoogleLogin()"><i class="fa-brands fa-google" style="color: #ea4335;"></i> Continue with Google</button>
            <div style="margin: 5px 0; color: #80868b; font-size: 13px;">or</div>
            <div style="display: flex; flex-direction: column; gap: 12px;">
                <input type="text" id="auth-username" class="auth-input" placeholder="Username">
                <input type="email" id="auth-email" class="auth-input" placeholder="Email Address">
                <input type="password" id="auth-password" class="auth-input" placeholder="Password">
                <button class="auth-btn" onclick="submitAuth()">Sign Up</button>
            </div>
            <div style="font-size: 13px; color: #1a73e8; cursor: pointer;" onclick="toggleAuthMode()">Already have an account? Login</div>
        </div>
    </div>

    <div class="overlay" id="overlay" onclick="toggleSidebar()"></div>
    <div class="sidebar" id="sidebar">
        <div class="sidebar-header">
            <button class="new-chat-btn" onclick="startNewChat();"><i class="fa-solid fa-plus"></i> New Chat</button>
        </div>
        <div class="sidebar-menu">
            <div class="menu-item" onclick="switchView('home')"><i class="fa-solid fa-house"></i> Home / Chat</div>
            <div class="menu-item" onclick="switchView('history')"><i class="fa-solid fa-clock-rotate-left"></i> History</div>
            <div class="menu-item" onclick="switchView('library')"><i class="fa-solid fa-book-open"></i> Library</div>
            <div class="menu-item" onclick="switchView('bookmarks')"><i class="fa-solid fa-bookmark"></i> Bookmarks</div>
            <div class="menu-item" onclick="switchView('settings')"><i class="fa-solid fa-gear"></i> Settings</div>
        </div>
        <div class="sidebar-footer">
            <span id="user-display-name">User</span>
            <span onclick="logout()" style="color: #ea4335; cursor: pointer;"><i class="fa-solid fa-right-from-bracket"></i> Logout</span>
        </div>
    </div>

    <div class="main-wrapper">
        <header>
            <div style="display: flex; align-items: center; gap: 12px;">
                <button class="menu-toggle" onclick="toggleSidebar()"><i class="fa-solid fa-bars"></i></button>
                <div style="font-size: 18px; font-weight: 600;"><i class="fa-solid fa-sparkles" style="color: #1a73e8;"></i> Tibyan AI</div>
            </div>
            <button onclick="startNewChat()" style="background: #f0f4f9; border: 1px solid #dadce0; color: #1a73e8; padding: 6px 12px; border-radius: 14px; font-size: 13px; cursor: pointer;"><i class="fa-solid fa-plus"></i> New Chat</button>
        </header>

        <div class="content-area">
            <div id="view-home" class="view active">
                <div id="home-welcome" class="home-center">
                    <div class="greeting">السلام عليكم</div>
                    <div style="font-size: 15px; color: #5f6368; margin-bottom: 30px;">Authentic Islamic Knowledge & Vision Assistant</div>
                </div>
                <div id="chat-box"></div>
            </div>
            <div id="view-history" class="view"><h2>Chat History</h2></div>
            <div id="view-library" class="view"><h2>Islamic Library</h2></div>
            <div id="view-bookmarks" class="view"><h2>Bookmarks</h2></div>
            <div id="view-settings" class="view"><h2>Settings</h2></div>
        </div>
    </div>

    <div class="bottom-panel">
        <div class="image-preview-bar" id="image-preview-bar">
            <img id="preview-img" src="" alt="Preview">
            <span id="preview-name" style="font-size: 13px; color: #5f6368; flex: 1; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;"></span>
            <button onclick="removeImage()" style="background: transparent; border: none; color: #ea4335; cursor: pointer; font-size: 16px;"><i class="fa-solid fa-xmark"></i></button>
        </div>

        <div class="input-box">
            <input type="file" id="image-input" accept="image/*" style="display: none;" onchange="handleImageSelect(event)">
            <button class="tool-btn" onclick="document.getElementById('image-input').click()" title="Upload Image"><i class="fa-solid fa-image"></i></button>
            <textarea id="user-input" placeholder="Ask about text, Quran, or upload an image..." rows="1" onkeydown="handleKey(event)"></textarea>
            <button class="send-btn" onclick="sendMessage()"><i class="fa-solid fa-arrow-up"></i></button>
        </div>
    </div>

    <script>
        let isLoginMode = false;
        let selectedBase64Image = null;

        window.addEventListener('DOMContentLoaded', () => { checkAuthStatus(); });

        function checkAuthStatus() {
            const user = localStorage.getItem('tibyan_logged_user');
            if (user) {
                document.getElementById('auth-screen').style.display = 'none';
                document.getElementById('user-display-name').innerText = user;
            } else {
                document.getElementById('auth-screen').style.display = 'flex';
            }
        }

        function toggleAuthMode() {
            isLoginMode = !isLoginMode;
            document.getElementById('auth-username').style.display = isLoginMode ? 'none' : 'block';
        }

        function handleGoogleLogin() {
            localStorage.setItem('tibyan_logged_user', 'Google User');
            checkAuthStatus();
        }

        function submitAuth() {
            const email = document.getElementById('auth-email').value.trim();
            if (email) {
                localStorage.setItem('tibyan_logged_user', email.split('@')[0]);
                checkAuthStatus();
            }
        }

        function logout() {
            localStorage.removeItem('tibyan_logged_user');
            checkAuthStatus();
        }

        function toggleSidebar() {
            document.getElementById('sidebar').classList.toggle('open');
            document.getElementById('overlay').classList.toggle('active');
        }

        function switchView(viewName) {
            document.querySelectorAll('.view').forEach(v => v.classList.remove('active'));
            document.getElementById('view-' + viewName).classList.add('active');
            document.getElementById('sidebar').classList.remove('open');
            document.getElementById('overlay').classList.remove('active');
        }

        function startNewChat() {
            document.getElementById('home-welcome').style.display = 'block';
            const chatBox = document.getElementById('chat-box');
            chatBox.style.display = 'none';
            chatBox.innerHTML = '';
            removeImage();
            switchView('home');
        }

        function handleImageSelect(event) {
            const file = event.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    selectedBase64Image = e.target.result;
                    document.getElementById('preview-img').src = selectedBase64Image;
                    document.getElementById('preview-name').innerText = file.name;
                    document.getElementById('image-preview-bar').style.display = 'flex';
                };
                reader.readAsDataURL(file);
            }
        }

        function removeImage() {
            selectedBase64Image = null;
            document.getElementById('image-input').value = '';
            document.getElementById('image-preview-bar').style.display = 'none';
            document.getElementById('preview-img').src = '';
            document.getElementById('preview-name').innerText = '';
        }

        function handleKey(e) { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendMessage(); } }

        async function sendMessage() {
            const input = document.getElementById('user-input');
            const message = input.value.trim();
            const currentImg = selectedBase64Image;

            if (!message && !currentImg) return;

            document.getElementById('sidebar').classList.remove('open');
            document.getElementById('overlay').classList.remove('active');
            document.getElementById('home-welcome').style.display = 'none';
            
            const chatBox = document.getElementById('chat-box');
            chatBox.style.display = 'flex';

            let userHtml = '<div class="msg-container"><div class="msg user-msg">';
            if (currentImg) {
                userHtml += `<img src="${currentImg}" class="chat-img">`;
            }
            if (message) {
                userHtml += `<span>${message}</span>`;
            }
            userHtml += '</div></div>';
            
            chatBox.innerHTML += userHtml;
            input.value = '';
            removeImage();

            chatBox.innerHTML += `<div class="msg-container" id="loading-msg"><div class="msg bot-msg"><i class="fa-solid fa-spinner fa-spin"></i> Thinking...</div></div>`;
            chatBox.scrollTop = chatBox.scrollHeight;

            try {
                const response = await fetch('/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ message: message, image: currentImg })
                });
                const data = await response.json();
                
                document.getElementById('loading-msg').remove();
                chatBox.innerHTML += `<div class="msg-container"><div class="msg bot-msg">${data.response}</div></div>`;
            } catch (err) {
                document.getElementById('loading-msg').remove();
                chatBox.innerHTML += `<div class="msg-container"><div class="msg bot-msg">Error fetching response.</div></div>`;
            }
            chatBox.scrollTop = chatBox.scrollHeight;
        }
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/manifest.json')
def manifest():
    return jsonify({
        "name": "Tibyan AI",
        "short_name": "Tibyan",
        "start_url": "/",
        "display": "standalone",
        "background_color": "#ffffff",
        "theme_color": "#1a73e8"
    })

@app.route('/chat', methods=['POST'])
def chat():
    user_msg = request.json.get('message', '')
    user_image = request.json.get('image', None)
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        return jsonify({"response": "Error: GROQ_API_KEY is missing in Render environment variables."})

    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    
    system_prompt = (
        "You are Tibyan AI, an authentic Islamic scholar and multi-modal assistant. "
        "Provide grounded answers with references to Quran, Hadith, and Fiqh. "
        "If an image is provided, analyze it accurately."
    )

    content_list = []
    if user_msg:
        content_list.append({"type": "text", "text": user_msg})
    else:
        content_list.append({"type": "text", "text": "Describe this image and provide relevant insights."})

        if user_image:
        content_list.append({"type": "image_url", "image_url": {"url": user_image}})
        model_name = "llama-3.3-70b-versatile"
    else:
        model_name = "llama-3.3-70b-versatile"


    data = {
        "model": model_name,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": content_list}
        ]
    }
    
    try:
        res = requests.post(url, json=data, headers=headers)
        res_json = res.json()
        if 'choices' in res_json:
            return jsonify({"response": res_json['choices'][0]['message']['content']})
        else:
            return jsonify({"response": f"API Error: {res_json.get('error', {}).get('message', 'Invalid Request')}"})
    except Exception as e:
        return jsonify({"response": f"Connection Error: {str(e)}"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)


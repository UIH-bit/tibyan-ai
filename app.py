from flask import Flask, request, jsonify, render_template_string
import os
import requests
import base64

app = Flask(__name__)

api_key = os.environ.get("GROQ_API_KEY") or os.environ.get("GEMINI_API_KEY")

def fetch_quran_api(query):
    try:
        url = f"https://api.quran.com/api/v4/search?q={query}&size=3"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            results = data.get('search', {}).get('results', [])
            verses_text = ""
            for res in results:
                verses_text += f"- Surah/Ayah Ref ({res.get('verse_key')}): {res.get('text')}\n"
            return verses_text
    except Exception as e:
        print("Quran API Error:", e)
    return None

def call_groq_api(prompt_text, image_base64=None):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    
    content_list = [{"type": "text", "text": prompt_text}]
    if image_base64:
        content_list.append({
            "type": "image_url",
            "image_url": {
                "url": f"data:image/jpeg;base64,{image_base64}"
            }
        })

    payload = {
        "model": "llama-3.2-11b-vision-preview",
        "messages": [
            {
                "role": "system", 
                "content": "You are Tibyan AI, an authentic and knowledgeable Islamic assistant. Answer queries accurately using the provided Quran data and image content if provided."
            },
            {
                "role": "user", 
                "content": content_list
            }
        ],
        "temperature": 0.7
    }
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=20)
        if response.status_code == 200:
            res_data = response.json()
            return res_data['choices'][0]['message']['content']
        else:
            return f"Groq API Error ({response.status_code}): {response.text}"
    except Exception as e:
        return f"Request Exception: {str(e)}"

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Tibyan AI - Authentic Islamic Knowledge</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }
        body { background-color: #ffffff; color: #111; display: flex; flex-direction: column; height: 100vh; overflow: hidden; }
        
        /* Header & Sidebar Styles */
        header { display: flex; align-items: center; justify-content: space-between; padding: 15px 20px; border-bottom: 1px solid #eaeaea; background: #fff; z-index: 10; }
        .header-left { display: flex; align-items: center; gap: 15px; }
        .menu-btn { background: none; border: none; font-size: 22px; cursor: pointer; color: #1e3d2f; }
        .logo { font-size: 20px; font-weight: bold; color: #1e3d2f; }
        
        /* Sidebar Drawer */
        .sidebar { position: fixed; top: 0; left: -260px; width: 260px; height: 100%; background: #fff; box-shadow: 2px 0 10px rgba(0,0,0,0.1); transition: 0.3s ease; z-index: 100; display: flex; flex-direction: column; }
        .sidebar.open { left: 0; }
        .sidebar-header { padding: 20px; font-size: 20px; font-weight: bold; color: #1e3d2f; border-bottom: 1px solid #eaeaea; display: flex; justify-content: space-between; align-items: center; }
        .close-sidebar { background: none; border: none; font-size: 20px; cursor: pointer; color: #555; }
        .sidebar-menu { list-style: none; padding: 20px 0; }
        .sidebar-menu li { padding: 15px 20px; font-size: 16px; color: #333; cursor: pointer; display: flex; align-items: center; gap: 15px; transition: 0.2s; }
        .sidebar-menu li:hover { background: #f0f4f1; color: #1e3d2f; font-weight: 500; }
        
        .overlay { position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.4); display: none; z-index: 90; }
        .overlay.active { display: block; }

        /* Main Content Views */
        .main-content { flex: 1; display: flex; flex-direction: column; overflow: hidden; position: relative; }
        .view-section { display: none; flex: 1; overflow-y: auto; padding: 20px; max-width: 800px; width: 100%; margin: 0 auto; }
        .view-section.active-view { display: flex; flex-direction: column; }

        /* Chat UI */
        .chat-container { justify-content: space-between; }
        .welcome-section { display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center; margin: auto 0; width: 100%; }
        .arabic-greeting { font-size: 36px; color: #1e3d2f; font-weight: bold; margin-bottom: 15px; font-family: serif; }
        .sub-text { font-size: 16px; color: #555; margin-bottom: 30px; }
        
        .suggestions { width: 100%; display: flex; flex-direction: column; align-items: center; gap: 12px; max-width: 500px; margin: 0 auto; }
        .suggestions-row { display: flex; justify-content: center; gap: 12px; width: 100%; }
        .suggestion-chip { background: #fff; border: 1px solid #e0e0e0; border-radius: 30px; padding: 12px 18px; font-size: 14px; color: #333; cursor: pointer; text-align: center; box-shadow: 0 2px 5px rgba(0,0,0,0.02); transition: 0.2s; flex: 1; }
        .suggestion-chip:hover { border-color: #1e3d2f; background: #f9fbf9; }
        .suggestion-center { max-width: 260px; width: 100%; }

        #chat-history { width: 100%; display: flex; flex-direction: column; gap: 15px; margin-bottom: 20px; }
        .message { padding: 14px 18px; border-radius: 12px; max-width: 85%; line-height: 1.6; font-size: 15px; white-space: pre-wrap; }
        .user-msg { background: #f0f4f1; color: #1e3d2f; align-self: flex-end; margin-left: auto; }
        .ai-msg { background: #ffffff; border: 1px solid #e0e0e0; color: #222; align-self: flex-start; }
        
        /* Input Area & Custom Send Button with Spinner */
        .input-area { display: flex; align-items: flex-end; padding: 12px 15px; border-top: 1px solid #eaeaea; background: #fff; gap: 10px; max-width: 800px; width: 100%; margin: 0 auto; }
        .text-input { flex: 1; border: 1px solid #e0e0e0; border-radius: 20px; padding: 10px 18px; font-size: 15px; outline: none; background: #f9f9f9; resize: none; }
        
        .upload-btn { background: none; border: none; font-size: 22px; cursor: pointer; color: #555; padding-bottom: 8px; }
        .upload-btn:hover { color: #1e3d2f; }

        /* Send Button like Gemini */
        .send-btn { 
            background: #1e3d2f; border: none; border-radius: 50%; width: 42px; height: 42px; min-width: 42px; 
            display: flex; align-items: center; justify-content: center; cursor: pointer; color: white; position: relative; 
        }
        .send-btn svg { width: 18px; height: 18px; fill: white; transition: transform 0.2s; }
        
        /* 360 Rotating Circle Effect on Load */
        .send-btn.loading::after {
            content: ''; position: absolute; top: -3px; left: -3px; right: -3px; bottom: -3px;
            border: 2px solid transparent; border-top-color: #4CAF50; border-radius: 50%;
            animation: spin 0.8s linear infinite;
        }
        @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }

        /* Preview Thumbnail */
        #imagePreviewContainer { display: none; padding: 5px 15px; align-items: center; gap: 10px; background: #f9f9f9; max-width: 800px; margin: 0 auto; border-top: 1px solid #eaeaea; }
        #imagePreviewContainer img { width: 45px; height: 45px; object-fit: cover; border-radius: 6px; border: 1px solid #ccc; }
        .remove-img { background: #ff4d4d; color: white; border: none; border-radius: 50%; width: 20px; height: 20px; font-size: 12px; cursor: pointer; display: flex; align-items: center; justify-content: center; }

        /* Dynamic Views Styling */
        .view-title { font-size: 24px; color: #1e3d2f; margin-bottom: 15px; font-weight: bold; }
        .view-body { font-size: 15px; color: #444; line-height: 1.6; }
    </style>
</head>
<body>
    <header>
        <div class="header-left">
            <button class="menu-btn" onclick="toggleSidebar()">☰</button>
            <div class="logo">Tibyan AI</div>
        </div>
    </header>

    <!-- Sidebar Drawer -->
    <div class="overlay" id="overlay" onclick="toggleSidebar()"></div>
    <div class="sidebar" id="sidebar">
        <div class="sidebar-header">
            <span>Tibyan Menu</span>
            <button class="close-sidebar" onclick="toggleSidebar()">✕</button>
        </div>
        <ul class="sidebar-menu">
            <li onclick="switchView('home')">🏡 Home</li>
            <li onclick="switchView('library')">📚 Library</li>
            <li onclick="switchView('saved')">📜 Saved</li>
            <li onclick="switchView('profile')">👤 Profile</li>
            <li onclick="switchView('about')">❕️ About</li>
        </ul>
    </div>

    <div class="main-content">
        <!-- HOME / CHAT VIEW -->
        <div id="home-view" class="view-section active-view chat-container">
            <div id="chat-box" style="width: 100%;">
                <div class="welcome-section" id="welcome-screen">
                    <div class="arabic-greeting">بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ</div>
                    <div class="sub-text">Ask authentic Islamic questions backed by Quran API</div>
                    
                    <div class="suggestions">
                        <div class="suggestions-row">
                            <div class="suggestion-chip" onclick="sendPrompt('What does the Quran say about patience (Sabr)?')">What does the Quran say about patience (Sabr)?</div>
                            <div class="suggestion-chip" onclick="sendPrompt('Authentic Hadiths on honesty')">Authentic Hadiths on honesty</div>
                        </div>
                        <div class="suggestion-chip suggestion-center" onclick="sendPrompt('Who is Adam alai issalam?')">Who is Adam alai issalam?</div>
                    </div>
                </div>
                <div id="chat-history"></div>
            </div>
        </div>

        <!-- LIBRARY VIEW -->
        <div id="library-view" class="view-section">
            <div class="view-title">Islamic Library 📚</div>
            <div class="view-body">
                <p>Access authentic references, verses categorized by topics, Surah indices, and verified scholarly notes directly backed by the Quran API.</p>
            </div>
        </div>

        <!-- SAVED VIEW -->
        <div id="saved-view" class="view-section">
            <div class="view-title">Saved Chats & Bookmarks 📜</div>
            <div class="view-body">
                <p>Your bookmarked conversations, important rulings, and favorite verse references will appear here.</p>
            </div>
        </div>

        <!-- PROFILE VIEW -->
        <div id="profile-view" class="view-section">
            <div class="view-title">User Profile 👤</div>
            <div class="view-body">
                <p><strong>Account Name:</strong> Tibyan User</p>
                <p><strong>Status:</strong> Active Developer Mode</p>
                <p><strong>Connected API:</strong> Groq High-Speed LPU</p>
            </div>
        </div>

        <!-- ABOUT VIEW -->
        <div id="about-view" class="view-section">
            <div class="view-title">About Tibyan AI ❕️</div>
            <div class="view-body">
                <p>Tibyan AI is an advanced, authentic Islamic knowledge assistant designed to provide accurate answers backed by Quranic database references and multimodal vision capabilities.</p>
            </div>
        </div>
    </div>

    <!-- Image Preview Bar -->
    <div id="imagePreviewContainer">
        <img id="previewImg" src="" alt="preview">
        <span id="fileName" style="font-size: 13px; color: #555; flex: 1;"></span>
        <button class="remove-img" onclick="clearImage()">✕</button>
    </div>

    <div class="input-area">
        <input type="file" id="imageInput" accept="image/*" style="display: none;" onchange="handleImageSelect(event)">
        <button class="upload-btn" onclick="document.getElementById('imageInput').click()" title="Upload Image">📎</button>
        <textarea id="userInput" class="text-input" rows="1" placeholder="Ask a question or upload an image..."></textarea>
        <button class="send-btn" id="sendBtn" onclick="submitQuery()">
            <svg viewBox="0 0 24 24"><path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"></path></svg>
        </button>
    </div>

    <script>
        let selectedBase64Image = null;

        function toggleSidebar() {
            document.getElementById('sidebar').classList.toggle('open');
            document.getElementById('overlay').classList.toggle('active');
        }

        function switchView(viewName) {
            document.querySelectorAll('.view-section').forEach(el => el.classList.remove('active-view'));
            document.getElementById(viewName + '-view').classList.add('active-view');
            toggleSidebar();
        }

        function handleImageSelect(event) {
            const file = event.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    selectedBase64Image = e.target.result.split(',')[1];
                    document.getElementById('previewImg').src = e.target.result;
                    document.getElementById('fileName').innerText = file.name;
                    document.getElementById('imagePreviewContainer').style.display = 'flex';
                };
                reader.readAsDataURL(file);
            }
        }

        function clearImage() {
            selectedBase64Image = null;
            document.getElementById('imageInput').value = '';
            document.getElementById('imagePreviewContainer').style.display = 'none';
        }

        async function submitQuery() {
            const inputField = document.getElementById('userInput');
            const query = inputField.value.trim();
            if (!query && !selectedBase64Image) return;

            // Switch to home view if currently on other tabs
            document.querySelectorAll('.view-section').forEach(el => el.classList.remove('active-view'));
            document.getElementById('home-view').classList.add('active-view');
            
            const welcomeScreen = document.getElementById('welcome-screen');
            if (welcomeScreen) {
                welcomeScreen.style.display = 'none';
            }

            const historyBox = document.getElementById('chat-history');
            let userHtml = `<div class="message user-msg">`;
            if (selectedBase64Image) {
                userHtml += `<img src="data:image/jpeg;base64,${selectedBase64Image}" style="max-width:150px; border-radius:8px; display:block; margin-bottom:8px;">`;
            }
            userHtml += `${query || 'Analysing uploaded image...'}</div>`;
            historyBox.innerHTML += userHtml;

            const currentImg = selectedBase64Image;
            inputField.value = '';
            clearImage();
            
            const sendBtn = document.getElementById('sendBtn');
            sendBtn.classList.add('loading');

            const loadingId = 'loading-' + Date.now();
            historyBox.innerHTML += `<div class="message ai-msg" id="${loadingId}">Analyzing with Quran & Vision database...</div>`;
            window.scrollTo(0, document.body.scrollHeight);

            try {
                const response = await fetch('/generate', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ prompt: query, image: currentImg })
                });
                const data = await response.json();
                const aiMsgBox = document.getElementById(loadingId);
                if (data.response) {
                    aiMsgBox.innerText = data.response;
                } else {
                    aiMsgBox.innerText = "Error: " + (data.error || "Something went wrong.");
                }
            } catch (err) {
                document.getElementById(loadingId).innerText = "Network error occurred.";
            } finally {
                sendBtn.classList.remove('loading');
            }
            window.scrollTo(0, document.body.scrollHeight);
        }

        function sendPrompt(text) {
            document.getElementById('userInput').value = text;
            submitQuery();
        }
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/generate', methods=['POST'])
def generate():
    data = request.json
    user_prompt = data.get('prompt', '')
    img_data = data.get('image', None)
    
    quran_data = fetch_quran_api(user_prompt) if user_prompt else ""
    context_data = f"\nQuran Data References:\n{quran_data}\n" if quran_data else ""
    
    ai_response = call_groq_api(f"{context_data}\nUser Question: {user_prompt}", image_base64=img_data)
    return jsonify({'response': ai_response})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

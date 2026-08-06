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
    
    # Updated vision model name
    model_name = "qwen/qwen3.6-27b" if image_base64 else "llama-3.3-70b-versatile"
    
    content_list = [{"type": "text", "text": prompt_text}]
    if image_base64:
        content_list.append({
            "type": "image_url",
            "image_url": {
                "url": f"data:image/jpeg;base64,{image_base64}"
            }
        })

    payload = {
        "model": model_name,
        "messages": [
            {
                "role": "system", 
                "content": (
                    "You are Tibyan AI, a knowledgeable, wise, and respectful Muslim scholar assistant. "
                    "Always begin your responses warmly with Islamic greetings (like Bismillah or Assalamu Alaikum). "
                    "Your responses on Islamic rulings, Fiqh, and fatawa must strictly align with the authentic methodologies, "
                    "teachings, and scholarly standards of prominent institutions like Darul Ifta Darul Uloom Deoband and "
                    "Jamia Uloom-ul-Islamia Banuri Town (Ahlus Sunnah wal Jama'ah / Hanafi Fiqh unless specified). "
                    "Speak with deep respect, empathy, and wisdom like a sincere practicing Muslim scholar. "
                    "When provided with an image, analyze its content and text accurately to provide context for your Islamic guidance."
                )
            },
            {
                "role": "user", 
                "content": content_list if image_base64 else prompt_text
            }
        ],
        "temperature": 0.7
    }
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=25)
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
        body { background-color: #ffffff; color: #111; display: flex; flex-direction: column; height: 100vh; overflow: hidden; font-size: 17px; }
        
        header { display: flex; align-items: center; justify-content: space-between; padding: 15px 20px; border-bottom: 1px solid #eaeaea; background: #fff; z-index: 10; flex-shrink: 0; }
        .header-left { display: flex; align-items: center; gap: 15px; }
        .menu-btn { background: none; border: none; font-size: 24px; cursor: pointer; color: #1e3d2f; }
        .logo { font-size: 22px; font-weight: bold; color: #1e3d2f; }
        
        .sidebar { position: fixed; top: 0; left: -260px; width: 260px; height: 100%; background: #fff; box-shadow: 2px 0 10px rgba(0,0,0,0.1); transition: 0.3s ease; z-index: 100; display: flex; flex-direction: column; }
        .sidebar.open { left: 0; }
        .sidebar-header { padding: 20px; font-size: 20px; font-weight: bold; color: #1e3d2f; border-bottom: 1px solid #eaeaea; display: flex; justify-content: space-between; align-items: center; }
        .close-sidebar { background: none; border: none; font-size: 20px; cursor: pointer; color: #555; }
        .sidebar-menu { list-style: none; padding: 20px 0; }
        .sidebar-menu li { padding: 16px 20px; font-size: 18px; color: #333; cursor: pointer; display: flex; align-items: center; gap: 16px; transition: 0.2s; }
        .sidebar-menu li:hover { background: #f0f4f1; color: #1e3d2f; font-weight: 500; }
        
        .overlay { position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.4); display: none; z-index: 90; }
        .overlay.active { display: block; }

        .main-content { flex: 1; display: flex; flex-direction: column; overflow: hidden; position: relative; }
        .view-section { display: none; flex: 1; overflow-y: auto; padding: 20px; max-width: 800px; width: 100%; margin: 0 auto; scroll-behavior: smooth; }
        .view-section.active-view { display: flex; flex-direction: column; }

        .chat-container { justify-content: space-between; }
        .welcome-section { display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center; margin: auto 0; width: 100%; padding: 20px 0; }
        .arabic-greeting { font-size: 40px; color: #1e3d2f; font-weight: bold; margin-bottom: 15px; font-family: serif; }
        .sub-text { font-size: 18px; color: #555; margin-bottom: 30px; line-height: 1.5; }
        
        .suggestions { width: 100%; display: flex; flex-direction: column; align-items: center; gap: 14px; max-width: 550px; margin: 0 auto; }
        .suggestions-row { display: flex; justify-content: center; gap: 14px; width: 100%; }
        .suggestion-chip { background: #fff; border: 1px solid #e0e0e0; border-radius: 30px; padding: 14px 20px; font-size: 16px; color: #333; cursor: pointer; text-align: center; box-shadow: 0 2px 5px rgba(0,0,0,0.02); transition: 0.2s; flex: 1; }
        .suggestion-chip:hover { border-color: #1e3d2f; background: #f9fbf9; }
        .suggestion-center { max-width: 280px; width: 100%; }

        #chat-history { width: 100%; display: flex; flex-direction: column; gap: 18px; padding-bottom: 20px; }
        .message-wrapper { display: flex; flex-direction: column; width: 100%; margin-bottom: 12px; }
        .message { padding: 16px 20px; border-radius: 14px; max-width: 85%; line-height: 1.6; font-size: 17px; white-space: pre-wrap; }
        .user-msg { background: #f0f4f1; color: #1e3d2f; align-self: flex-end; margin-left: auto; }
        .ai-msg { background: #ffffff; border: 1px solid #e0e0e0; color: #222; align-self: flex-start; }
        
        .ai-actions { display: flex; gap: 14px; margin-top: 8px; align-self: flex-start; padding-left: 6px; }
        .action-btn { background: none; border: none; font-size: 15px; color: #666; cursor: pointer; display: flex; align-items: center; gap: 5px; padding: 5px 10px; border-radius: 7px; transition: 0.2s; }
        .action-btn:hover { background: #f0f4f1; color: #1e3d2f; }
        .action-btn.saved-active { color: #1e3d2f; font-weight: bold; background: #e8f0eb; }

        .saved-item { background: #fff; border: 1px solid #e0e0e0; border-radius: 12px; padding: 18px; margin-bottom: 18px; box-shadow: 0 2px 5px rgba(0,0,0,0.02); }
        .saved-q { font-weight: bold; color: #1e3d2f; margin-bottom: 10px; font-size: 18px; }
        .saved-a { color: #333; font-size: 17px; line-height: 1.6; white-space: pre-wrap; }
        .unsave-btn { background: #ff4d4d; color: white; border: none; padding: 6px 12px; border-radius: 6px; font-size: 14px; cursor: pointer; margin-top: 12px; float: right; }

        .input-area { display: flex; align-items: flex-end; padding: 14px 18px; border-top: 1px solid #eaeaea; background: #fff; gap: 12px; max-width: 800px; width: 100%; margin: 0 auto; flex-shrink: 0; }
        .text-input { flex: 1; border: 1px solid #e0e0e0; border-radius: 24px; padding: 14px 20px; font-size: 17px; outline: none; background: #f9f9f9; resize: none; max-height: 180px; overflow-y: auto; line-height: 1.5; }
        
        .upload-btn { background: none; border: none; font-size: 26px; cursor: pointer; color: #555; padding-bottom: 10px; }
        .upload-btn:hover { color: #1e3d2f; }

        .send-btn { 
            background: #1e3d2f; border: none; border-radius: 50%; width: 48px; height: 48px; min-width: 48px; 
            display: flex; align-items: center; justify-content: center; cursor: pointer; color: white; position: relative; margin-bottom: 3px;
        }
        .send-btn svg { width: 20px; height: 20px; fill: white; transition: transform 0.2s; }
        
        .send-btn.loading::after {
            content: ''; position: absolute; top: -4px; left: -4px; right: -4px; bottom: -4px;
            border: 2.5px solid transparent; border-top-color: #4CAF50; border-radius: 50%;
            animation: spin 0.8s linear infinite;
        }
        @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }

        #imagePreviewContainer { display: none; padding: 6px 18px; align-items: center; gap: 12px; background: #f9f9f9; max-width: 800px; margin: 0 auto; border-top: 1px solid #eaeaea; flex-shrink: 0; }
        #imagePreviewContainer img { width: 55px; height: 55px; object-fit: cover; border-radius: 8px; border: 1px solid #ccc; }
        .remove-img { background: #ff4d4d; color: white; border: none; border-radius: 50%; width: 24px; height: 24px; font-size: 14px; cursor: pointer; display: flex; align-items: center; justify-content: center; }

        .view-title { font-size: 28px; color: #1e3d2f; margin-bottom: 20px; font-weight: bold; }
        .view-body { font-size: 17px; color: #444; line-height: 1.6; }
    </style>
</head>
<body>
    <header>
        <div class="header-left">
            <button class="menu-btn" onclick="toggleSidebar()">☰</button>
            <div class="logo">Tibyan AI</div>
        </div>
    </header>

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
        <div id="home-view" class="view-section active-view chat-container">
            <div id="chat-box" style="width: 100%;">
                <div class="welcome-section" id="welcome-screen">
                    <div class="arabic-greeting">بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ</div>
                    <div class="sub-text">Authentic Islamic Knowledge backed by Deoband & Banuri Town manhaj</div>
                    
                    <div class="suggestions">
                        <div class="suggestions-row">
                            <div class="suggestion-chip" onclick="sendPrompt('What does the Quran say about patience (Sabr)?')">What does the Quran say about patience (Sabr)?</div>
                            <div class="suggestion-chip" onclick="sendPrompt('Roza kaise toot jata hai')">Roza kaise toot jata hai</div>
                        </div>
                        <div class="suggestion-chip suggestion-center" onclick="sendPrompt('Who is Adam alai issalam?')">Who is Adam alai issalam?</div>
                    </div>
                </div>
                <div id="chat-history"></div>
            </div>
        </div>

        <div id="library-view" class="view-section">
            <div class="view-title">Islamic Library 📚</div>
            <div class="view-body">
                <p>Access authentic references, Quran API verses, and Fatawa methodologies inspired by Darul Uloom Deoband and Jamia Banuri Town.</p>
            </div>
        </div>

        <div id="saved-view" class="view-section">
            <div class="view-title">Saved Chats & Bookmarks 📜</div>
            <div class="view-body" id="saved-container">
                <p>No saved responses yet. Click 'Saved 📜' under any AI response to save it here permanently.</p>
            </div>
        </div>

        <div id="profile-view" class="view-section">
            <div class="view-title">User Profile 👤</div>
            <div class="view-body">
                <p><strong>Account Name:</strong> Tibyan User</p>
                <p><strong>Status:</strong> Active Developer Mode</p>
                <p><strong>Knowledge Base:</strong> Quran API + Deoband & Banuri Town Fiqh Standards</p>
            </div>
        </div>

        <div id="about-view" class="view-section">
            <div class="view-title">About Tibyan AI ❕️</div>
            <div class="view-body">
                <p>Tibyan AI provides authenticated answers adhering strictly to Quran, Sunnah, and the scholarly standards of Deoband and Banuri Town.</p>
            </div>
        </div>
    </div>

    <div id="imagePreviewContainer">
        <img id="previewImg" src="" alt="preview">
        <span id="fileName" style="font-size: 14px; color: #555; flex: 1;"></span>
        <button class="remove-img" onclick="clearImage()">✕</button>
    </div>

    <div class="input-area">
        <input type="file" id="imageInput" accept="image/*" style="display: none;" onchange="handleImageSelect(event)">
        <button class="upload-btn" onclick="document.getElementById('imageInput').click()" title="Upload Image">📎</button>
        <textarea id="userInput" class="text-input" rows="1" placeholder="Ask a question or upload an image..." oninput="autoExpand(this)"></textarea>
        <button class="send-btn" id="sendBtn" onclick="submitQuery()">
            <svg viewBox="0 0 24 24"><path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"></path></svg>
        </button>
    </div>

    <script>
        let selectedBase64Image = null;

        function autoExpand(field) {
            field.style.height = 'inherit';
            field.style.height = (field.scrollHeight) + 'px';
        }

        function toggleSidebar() {
            document.getElementById('sidebar').classList.toggle('open');
            document.getElementById('overlay').classList.toggle('active');
        }

        function switchView(viewName) {
            document.querySelectorAll('.view-section').forEach(el => el.classList.remove('active-view'));
            document.getElementById(viewName + '-view').classList.add('active-view');
            if (viewName === 'saved') {
                renderSavedChats();
            }
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

        function scrollToBottom() {
            const homeView = document.getElementById('home-view');
            homeView.scrollTop = homeView.scrollHeight;
        }

        async function submitQuery() {
            const inputField = document.getElementById('userInput');
            const query = inputField.value.trim();
            if (!query && !selectedBase64Image) return;

            document.querySelectorAll('.view-section').forEach(el => el.classList.remove('active-view'));
            document.getElementById('home-view').classList.add('active-view');
            
            const welcomeScreen = document.getElementById('welcome-screen');
            if (welcomeScreen) {
                welcomeScreen.style.display = 'none';
            }

            const historyBox = document.getElementById('chat-history');
            let userHtml = `<div class="message-wrapper"><div class="message user-msg">`;
            if (selectedBase64Image) {
                userHtml += `<img src="data:image/jpeg;base64,${selectedBase64Image}" style="max-width:180px; border-radius:8px; display:block; margin-bottom:8px;">`;
            }
            userHtml += `${query || 'Analysing uploaded image...'}</div></div>`;
            historyBox.innerHTML += userHtml;
            scrollToBottom();

            const currentQuery = query || 'Uploaded Image Query';
            const currentImg = selectedBase64Image;
            
            inputField.value = '';
            inputField.style.height = 'inherit';
            clearImage();
            
            const sendBtn = document.getElementById('sendBtn');
            sendBtn.classList.add('loading');

            const uniqueId = 'msg-' + Date.now();
            historyBox.innerHTML += `
                <div class="message-wrapper" id="wrapper-${uniqueId}">
                    <div class="message ai-msg" id="${uniqueId}">Bismillah, searching authentic Fatawa references...</div>
                </div>`;
            scrollToBottom();

            try {
                const response = await fetch('/generate', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ prompt: currentQuery, image: currentImg })
                });
                const data = await response.json();
                const aiMsgBox = document.getElementById(uniqueId);
                const wrapperBox = document.getElementById(`wrapper-${uniqueId}`);
                
                if (data.response) {
                    aiMsgBox.innerText = data.response;
                    
                    const actionsDiv = document.createElement('div');
                    actionsDiv.className = 'ai-actions';
                    actionsDiv.innerHTML = `
                        <button class="action-btn" onclick="handleLike(this)">👍 Like</button>
                        <button class="action-btn" onclick="handleDislike(this)">👎 Dislike</button>
                        <button class="action-btn" id="save-btn-${uniqueId}" onclick="toggleSave('${uniqueId}', \`${b16Encode(currentQuery)}\`, \`${b16Encode(data.response)}\`)">📜 Saved</button>
                        <button class="action-btn" onclick="shareContent(\`${b16Encode(data.response)}\`)">📤 Share</button>
                    `;
                    wrapperBox.appendChild(actionsDiv);
                } else {
                    aiMsgBox.innerText = "Error: " + (data.error || "Something went wrong.");
                }
            } catch (err) {
                document.getElementById(uniqueId).innerText = "Network error occurred.";
            } finally {
                sendBtn.classList.remove('loading');
            }
            scrollToBottom();
        }

        function b16Encode(str) {
            return btoa(encodeURIComponent(str));
        }
        function b16Decode(str) {
            return decodeURIComponent(atob(str));
        }

        function handleLike(btn) {
            btn.style.color = '#2e7d32';
            btn.style.fontWeight = 'bold';
            btn.innerText = '👍 Liked';
        }

        function handleDislike(btn) {
            btn.style.color = '#c62828';
            btn.style.fontWeight = 'bold';
            btn.innerText = '👎 Disliked';
        }

        function toggleSave(id, encQuery, encAns) {
            const queryText = b16Decode(encQuery);
            const ansText = b16Decode(encAns);
            let savedList = JSON.parse(localStorage.getItem('tibyan_saved') || '[]');
            
            const existingIndex = savedList.findIndex(item => item.query === queryText && item.answer === ansText);
            const btn = document.getElementById(`save-btn-${id}`);

            if (existingIndex > -1) {
                savedList.splice(existingIndex, 1);
                if(btn) {
                    btn.classList.remove('saved-active');
                    btn.innerHTML = '📜 Saved';
                }
            } else {
                savedList.push({ query: queryText, answer: ansText, date: new Date().toLocaleString() });
                if(btn) {
                    btn.classList.add('saved-active');
                    btn.innerHTML = '✅ Saved';
                }
            }
            localStorage.setItem('tibyan_saved', JSON.stringify(savedList));
        }

        function renderSavedChats() {
            const container = document.getElementById('saved-container');
            let savedList = JSON.parse(localStorage.getItem('tibyan_saved') || '[]');
            
            if (savedList.length === 0) {
                container.innerHTML = `<p>No saved responses yet. Click 'Saved 📜' under any AI response to save it here permanently.</p>`;
                return;
            }

            let html = '';
            savedList.forEach((item, index) => {
                html += `
                    <div class="saved-item">
                        <div class="saved-q">Q: ${item.query}</div>
                        <div class="saved-a">${item.answer}</div>
                        <button class="unsave-btn" onclick="removeSaved(${index})">Delete</button>
                        <div style="clear:both;"></div>
                    </div>
                `;
            });
            container.innerHTML = html;
        }

        function removeSaved(index) {
            let savedList = JSON.parse(localStorage.getItem('tibyan_saved') || '[]');
            savedList.splice(index, 1);
            localStorage.setItem('tibyan_saved', JSON.stringify(savedList));
            renderSavedChats();
        }

        function shareContent(encAns) {
            const ansText = b16Decode(encAns);
            if (navigator.share) {
                navigator.share({
                    title: 'Tibyan AI Response',
                    text: ansText
                }).catch(console.error);
            } else {
                navigator.clipboard.writeText(ansText);
                alert('Answer copied to clipboard!');
            }
        }

        function sendPrompt(text) {
            document.getElementById('userInput').value = text;
            autoExpand(document.getElementById('userInput'));
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
    context_data = f"\nQuran API References:\n{quran_data}\n" if quran_data else ""
    
    ai_response = call_groq_api(f"{context_data}\nUser Question: {user_prompt}", image_base64=img_data)
    return jsonify({'response': ai_response})

if __name__ == 'main':
    app.run(host='0.0.0.0', port=5000)

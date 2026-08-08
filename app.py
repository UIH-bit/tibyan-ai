from flask import Flask, request, jsonify, render_template_string
import os
import requests

app = Flask(__name__)
api_key = os.environ.get("GROQ_API_KEY") or os.environ.get("GEMINI_API_KEY")

def call_groq_api(prompt_text, image_data=None):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    
    messages = [
        {
            "role": "system", 
            "content": "You are Tibyan AI, a knowledgeable and respectful Muslim scholar assistant adhering to Hanafi Fiqh (Deoband/Banuri Town manhaj). Structure responses cleanly."
        }
    ]
    
    if image_data:
        messages.append({
            "role": "user",
            "content": [
                {"type": "text", "text": prompt_text if prompt_text else "Explain this image from an Islamic perspective."},
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
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        if response.status_code == 200:
            return response.json()['choices'][0]['message']['content']
        else:
            return f"Error: {response.text}"
    except Exception as e:
        return f"Exception: {str(e)}"

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Tibyan AI - Authentic Islamic Knowledge</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }
        body { background-color: #ffffff; color: #111; display: flex; flex-direction: column; height: 100vh; overflow: hidden; font-size: 17px; }
        header { display: flex; align-items: center; justify-content: space-between; padding: 12px 20px; border-bottom: 1px solid #eaeaea; background: #fff; z-index: 10; flex-shrink: 0; }
        .header-left { display: flex; align-items: center; gap: 15px; }
        .menu-btn { background: none; border: none; font-size: 24px; cursor: pointer; color: #1e3d2f; }
        .logo { font-size: 22px; font-weight: bold; color: #1e3d2f; }
        
        .sidebar { position: fixed; top: 0; left: -280px; width: 280px; height: 100%; background: #fff; box-shadow: 2px 0 10px rgba(0,0,0,0.1); transition: 0.3s ease; z-index: 100; display: flex; flex-direction: column; }
        .sidebar.open { left: 0; }
        .sidebar-header { padding: 20px; font-size: 20px; font-weight: bold; color: #1e3d2f; border-bottom: 1px solid #eaeaea; display: flex; justify-content: space-between; align-items: center; }
        .close-sidebar { background: none; border: none; font-size: 20px; cursor: pointer; color: #555; }
        .sidebar-search-box { padding: 12px 16px; border-bottom: 1px solid #eaeaea; }
        .sidebar-search { width: 100%; padding: 10px 14px; border: 1px solid #ddd; border-radius: 8px; font-size: 15px; outline: none; background: #f9f9f9; }
        .sidebar-menu { list-style: none; padding: 10px 0; overflow-y: auto; flex: 1; }
        .sidebar-menu li { padding: 14px 20px; font-size: 17px; color: #333; cursor: pointer; display: flex; align-items: center; gap: 14px; transition: 0.2s; border-bottom: 1px solid #f7f7f7; }
        .sidebar-menu li:hover { background: #f0f4f1; color: #1e3d2f; font-weight: 500; }
        
        .overlay { position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.4); display: none; z-index: 90; }
        .overlay.active { display: block; }

        .main-content { flex: 1; display: flex; flex-direction: column; overflow: hidden; position: relative; }
        .view-section { display: none; flex: 1; overflow-y: auto; padding: 20px 20px 80px 20px; max-width: 800px; width: 100%; margin: 0 auto; scroll-behavior: smooth; }
        .view-section.active-view { display: flex; flex-direction: column; }

        .chat-container { justify-content: flex-start; }
        .welcome-section { display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center; margin: auto 0; width: 100%; padding: 10px 0; }
        .arabic-greeting { font-size: 36px; color: #1e3d2f; font-weight: bold; margin-bottom: 12px; font-family: serif; }
        .sub-text { font-size: 16px; color: #555; margin-bottom: 25px; line-height: 1.5; padding: 0 10px; }
        
        .suggestions { width: 100%; display: flex; flex-direction: column; align-items: center; gap: 10px; max-width: 550px; margin: 0 auto; }
        .suggestions-row { display: flex; justify-content: center; gap: 10px; width: 100%; }
        .suggestion-chip { background: #fff; border: 1px solid #e0e0e0; border-radius: 30px; padding: 12px 18px; font-size: 15px; color: #333; cursor: pointer; text-align: center; box-shadow: 0 2px 5px rgba(0,0,0,0.02); transition: 0.2s; flex: 1; }
        .suggestion-chip:hover { border-color: #1e3d2f; background: #f9fbf9; }
        .suggestion-center { max-width: 320px; width: 100%; }

        #chat-history { width: 100%; display: flex; flex-direction: column; gap: 18px; padding-bottom: 40px; }
        .message-wrapper { display: flex; flex-direction: column; width: 100%; margin-bottom: 12px; position: relative; }
        .message { padding: 16px 20px; border-radius: 14px; max-width: 85%; line-height: 1.6; font-size: 17px; white-space: pre-wrap; direction: rtl; text-align: right; }
        .user-msg { background: #f0f4f1; color: #1e3d2f; align-self: flex-end; margin-left: auto; }
        .ai-msg { background: #ffffff; border: 1px solid #e0e0e0; color: #222; align-self: flex-start; width: 100%; max-width: 100%; }
        
        .ai-actions { display: flex; gap: 10px; margin-top: 8px; align-self: flex-start; padding-left: 4px; align-items: center; }
        .action-btn { background: #f9f9f9; border: 1px solid #ddd; border-radius: 8px; font-size: 14px; color: #444; cursor: pointer; padding: 6px 12px; display: flex; align-items: center; gap: 5px; transition: 0.2s; }
        .action-btn:hover { background: #f0f4f1; color: #1e3d2f; border-color: #1e3d2f; }
        
        .dropdown-container { position: relative; display: inline-block; }
        .dropdown-menu { display: none; position: absolute; bottom: 100%; left: 0; background: #fff; border: 1px solid #ddd; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.15); z-index: 50; min-width: 120px; overflow: hidden; margin-bottom: 5px; }
        .dropdown-menu.show { display: block; }
        .dropdown-item { padding: 10px 16px; font-size: 14px; color: #333; cursor: pointer; display: block; text-align: left; transition: 0.2s; }
        .dropdown-item:hover { background: #f0f4f1; color: #1e3d2f; }

        .library-grid { display: grid; grid-template-columns: 1fr; gap: 12px; padding-bottom: 20px; }
        .library-card { background: #fff; border: 1px solid #e0e0e0; border-radius: 10px; padding: 16px 20px; font-size: 18px; font-weight: 500; color: #1e3d2f; cursor: pointer; box-shadow: 0 2px 4px rgba(0,0,0,0.02); transition: 0.2s; display: flex; align-items: center; justify-content: space-between; }
        .library-card:hover { background: #f0f4f1; border-color: #1e3d2f; }

        .profile-container { background: #fff; border: 1px solid #e0e0e0; border-radius: 12px; padding: 24px; max-width: 500px; margin: 10px auto; box-shadow: 0 2px 8px rgba(0,0,0,0.02); }
        .profile-pic-wrapper { display: flex; flex-direction: column; align-items: center; margin-bottom: 20px; }
        .profile-preview { width: 90px; height: 90px; border-radius: 50%; object-fit: cover; border: 2px solid #1e3d2f; background: #f0f4f1; display: flex; align-items: center; justify-content: center; font-size: 36px; color: #1e3d2f; margin-bottom: 10px; overflow: hidden; }
        .profile-preview img { width: 100%; height: 100%; object-fit: cover; }
        .file-input-label { background: #f0f4f1; color: #1e3d2f; padding: 8px 16px; border-radius: 20px; font-size: 14px; cursor: pointer; font-weight: 500; border: 1px solid #d0ded4; transition: 0.2s; }
        .file-input-label:hover { background: #e2ece4; }
        .form-group { margin-bottom: 16px; }
        .form-label { display: block; font-size: 15px; font-weight: 500; color: #333; margin-bottom: 6px; }
        .form-control { width: 100%; padding: 12px 16px; border: 1px solid #ddd; border-radius: 8px; font-size: 16px; outline: none; background: #f9f9f9; }
        .form-control:focus { border-color: #1e3d2f; background: #fff; }
        .save-profile-btn { background: #1e3d2f; color: white; border: none; border-radius: 8px; padding: 12px; width: 100%; font-size: 16px; font-weight: bold; cursor: pointer; transition: 0.2s; margin-top: 10px; }
        .save-profile-btn:hover { background: #152b21; }

        .input-area { display: flex; flex-direction: column; padding: 10px 16px 20px 16px; border-top: 1px solid #eaeaea; background: #fff; max-width: 800px; width: 100%; margin: 0 auto; flex-shrink: 0; gap: 8px; z-index: 20; }
        .input-top-row { display: flex; align-items: flex-end; gap: 10px; width: 100%; }
        .text-input { flex: 1; border: 1px solid #e0e0e0; border-radius: 24px; padding: 12px 18px; font-size: 16px; outline: none; background: #f9f9f9; resize: none; max-height: 150px; overflow-y: auto; line-height: 1.5; direction: rtl; text-align: right; }
        
        .action-icon-btn { background: none; border: none; cursor: pointer; font-size: 22px; color: #1e3d2f; display: flex; align-items: center; justify-content: center; padding: 8px; transition: 0.2s; }
        .action-icon-btn:hover { opacity: 0.7; }
        
        .send-btn { background: #1e3d2f; border: none; border-radius: 50%; width: 46px; height: 46px; min-width: 46px; display: flex; align-items: center; justify-content: center; cursor: pointer; color: white; position: relative; margin-bottom: 2px; }
        .send-btn svg { width: 18px; height: 18px; fill: white; }

        .image-preview-bar { display: none; align-items: center; gap: 10px; padding: 6px 12px; background: #f0f4f1; border-radius: 8px; width: fit-content; }
        .image-preview-bar img { width: 40px; height: 40px; border-radius: 6px; object-fit: cover; }
        .remove-img-btn { background: none; border: none; color: #d9534f; font-weight: bold; cursor: pointer; font-size: 16px; }
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
        
        <div class="sidebar-search-box">
            <input type="text" id="chatSearchInput" class="sidebar-search" placeholder="Search Chats..." oninput="filterChats(this.value)">
        </div>

        <ul class="sidebar-menu">
            <li onclick="startNewChat()">➕️ New Chat</li>
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
                        <div class="suggestions-row">
                            <div class="suggestion-chip suggestion-center" onclick="sendPrompt('Hanafi fiqh ke mutabiq namaz ka tareeqa')">Hanafi fiqh ke mutabiq namaz ka tareeqa</div>
                        </div>
                    </div>
                </div>
                <div id="chat-history"></div>
            </div>
        </div>

        <div id="library-view" class="view-section">
            <div class="view-title" style="font-size:28px; color:#1e3d2f; margin-bottom:20px; font-weight:bold;">Islamic Library 📚</div>
            <div class="library-grid">
                <div class="library-card" onclick="sendPrompt('Tell me about Qur\'an sciences.')">📖 Qur'an</div>
                <div class="library-card" onclick="sendPrompt('Explain Tafsir methodologies.')">📜 Tafsir</div>
                <div class="library-card" onclick="sendPrompt('Explain Hadith collections.')">🏷️ Hadith</div>
                <div class="library-card" onclick="sendPrompt('Explain Fiqh according to Hanafi school.')">⚖️ Fiqh</div>
                <div class="library-card" onclick="sendPrompt('Principles of Usul al-Fiqh.')">📋 Usul al-Fiqh</div>
                <div class="library-card" onclick="sendPrompt('Explain Islamic Aqeedah.')">💡 Aqeedah</div>
                <div class="library-card" onclick="sendPrompt('Arabic Fatawa insights.')">📜 Arabic Fatwa</div>
                <div class="library-card" onclick="sendPrompt('Overview of Islamic History.')">🏛️ History</div>
                <div class="library-card" onclick="sendPrompt('Seerah of Prophet Muhammad (PBUH).')">⭐ Seerah</div>
                <div class="library-card" onclick="sendPrompt('Islamic Biographies.')">👥 Biography</div>
                <div class="library-card" onclick="sendPrompt('Islamic Finance and Banking.')">🪙 Islamic Finance</div>
                <div class="library-card" onclick="sendPrompt('Comparative religion.')">🌐 Comparative religion</div>
            </div>
        </div>

        <div id="saved-view" class="view-section"><div style="font-size:28px; color:#1e3d2f; margin-bottom:20px; font-weight:bold;">Saved Chats 📜</div><p>No saved responses yet.</p></div>
        
        <div id="profile-view" class="view-section">
            <div style="font-size:28px; color:#1e3d2f; margin-bottom:15px; font-weight:bold;">Profile 👤</div>
            <div class="profile-container">
                <div class="profile-pic-wrapper">
                    <div class="profile-preview" id="profilePicPreview">👤</div>
                    <label class="file-input-label" for="profilePicInput">Choose Profile Picture</label>
                    <input type="file" id="profilePicInput" accept="image/*" style="display:none;" onchange="previewProfileImage(event)">
                </div>
                <div class="form-group">
                    <label class="form-label">Enter Name</label>
                    <input type="text" id="profileName" class="form-control" placeholder="Aapka naam...">
                </div>
                <div class="form-group">
                    <label class="form-label">Date of Birth (D.O.B)</label>
                    <input type="date" id="profileDob" class="form-control">
                </div>
                <button class="save-profile-btn" onclick="saveProfileData()">Save Profile</button>
            </div>
        </div>

        <div id="about-view" class="view-section"><div style="font-size:28px; color:#1e3d2f; margin-bottom:20px; font-weight:bold;">About ❕️</div><p>Tibyan AI authentic scholar assistant.</p></div>
    </div>

    <div class="input-area">
        <div class="image-preview-bar" id="imagePreviewBar">
            <img id="thumbPreview" src="" alt="preview">
            <span id="thumbName" style="font-size: 14px; color: #333;">Image attached</span>
            <button class="remove-img-btn" onclick="removeAttachedImage()">×</button>
        </div>
        <div class="input-top-row">
            <label class="action-icon-btn" title="Upload Image" style="margin-bottom:6px;">
                📎
                <input type="file" id="chatImageInput" accept="image/*" style="display:none;" onchange="handleChatImageUpload(event)">
            </label>
            <textarea id="userInput" class="text-input" rows="1" placeholder="Ask a question or upload image..." oninput="this.style.height='inherit';this.style.height=this.scrollHeight+'px';"></textarea>
            <button class="send-btn" id="sendBtn" onclick="submitQuery()">
                <svg viewBox="0 0 24 24"><path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"></path></svg>
            </button>
        </div>
    </div>

    <script>
        let uploadedImageBase64 = "";
        let chatImageBase64 = null;

        function toggleSidebar() {
            document.getElementById('sidebar').classList.toggle('open');
            document.getElementById('overlay').classList.toggle('active');
        }
        function switchView(viewName) {
            document.querySelectorAll('.view-section').forEach(el => el.classList.remove('active-view'));
            document.getElementById(viewName + '-view').classList.add('active-view');
            toggleSidebar();
        }
        function startNewChat() {
            document.getElementById('chat-history').innerHTML = '';
            const ws = document.getElementById('welcome-screen');
            if(ws) ws.style.display = 'flex';
            switchView('home');
        }
        function filterChats(q) { console.log(q); }

        function previewProfileImage(event) {
            const file = event.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    uploadedImageBase64 = e.target.result;
                    document.getElementById('profilePicPreview').innerHTML = `<img src="${uploadedImageBase64}" alt="Profile">`;
                }
                reader.readAsDataURL(file);
            }
        }

        function saveProfileData() {
            const name = document.getElementById('profileName').value;
            const dob = document.getElementById('profileDob').value;
            const profileData = { name: name, dob: dob, pic: uploadedImageBase64 };
            localStorage.setItem('tibyan_user_profile', JSON.stringify(profileData));
            alert('Profile saved successfully! ✅');
        }

        function handleChatImageUpload(event) {
            const file = event.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    chatImageBase64 = e.target.result;
                    document.getElementById('thumbPreview').src = chatImageBase64;
                    document.getElementById('imagePreviewBar').style.display = 'flex';
                }
                reader.readAsDataURL(file);
            }
        }

        function removeAttachedImage() {
            chatImageBase64 = null;
            document.getElementById('imagePreviewBar').style.display = 'none';
            document.getElementById('chatImageInput').value = '';
        }

        window.onload = function() {
            const saved = localStorage.getItem('tibyan_user_profile');
            if (saved) {
                try {
                    const data = JSON.parse(saved);
                    if(data.name) document.getElementById('profileName').value = data.name;
                    if(data.dob) document.getElementById('profileDob').value = data.dob;
                    if(data.pic) {
                        uploadedImageBase64 = data.pic;
                        document.getElementById('profilePicPreview').innerHTML = `<img src="${uploadedImageBase64}" alt="Profile">`;
                    }
                } catch(e) {}
            }
        };

        function likeMsg(id) {}
        function dislikeMsg(id) {}
        function saveMsg(id) {}
        
        function copyMsg(id) {
            const text = document.getElementById(id).innerText;
            navigator.clipboard.writeText(text);
            closeAllDropdowns();
        }

        function shareMsg(id) {
            const text = document.getElementById(id).innerText;
            if (navigator.share) {
                navigator.share({ title: 'Tibyan AI Response', text: text }).catch(() => {});
            } else {
                copyMsg(id);
            }
            closeAllDropdowns();
        }

        function toggleDropdown(menuId, event) {
            event.stopPropagation();
            const menu = document.getElementById(menuId);
            const isOpen = menu.classList.contains('show');
            closeAllDropdowns();
            if (!isOpen) {
                menu.classList.add('show');
            }
        }

        function closeAllDropdowns() {
            document.querySelectorAll('.dropdown-menu').forEach(m => m.classList.remove('show'));
        }

        window.onclick = function() {
            closeAllDropdowns();
        }

        async function submitQuery() {
            const inputField = document.getElementById('userInput');
            const query = inputField.value.trim();
            const currentImg = chatImageBase64;
            
            if(!query && !currentImg) return;

            document.querySelectorAll('.view-section').forEach(el => el.classList.remove('active-view'));
            document.getElementById('home-view').classList.add('active-view');
            const ws = document.getElementById('welcome-screen');
            if(ws) ws.style.display = 'none';
            
            const historyBox = document.getElementById('chat-history');
            
            let userHtml = `<div class="message-wrapper"><div class="message user-msg">`;
            if(currentImg) {
                userHtml += `<img src="${currentImg}" style="max-width:150px; border-radius:8px; display:block; margin-bottom:8px; margin-left:auto;">`;
            }
            if(query) {
                userHtml += `<div>${query}</div>`;
            }
            userHtml += `</div></div>`;
            
            historyBox.innerHTML += userHtml;
            
            inputField.value = '';
            inputField.style.height = 'inherit';
            removeAttachedImage();
            
            const uniqueId = 'msg-' + Date.now();
            const uniqueActionsId = 'actions-' + Date.now();
            const menuId = 'menu-' + Date.now();
            
            historyBox.innerHTML += `
                <div class="message-wrapper">
                    <div class="message ai-msg" id="${uniqueId}">Bismillah, analyzing...</div>
                    <div class="ai-actions" id="${uniqueActionsId}" style="display:none;">
                        <button class="action-btn" onclick="likeMsg('${uniqueId}')">👍 Like</button>
                        <button class="action-btn" onclick="dislikeMsg('${uniqueId}')">👎 Dislike</button>
                        <button class="action-btn" onclick="saveMsg('${uniqueId}')">📜 Save</button>
                        <div class="dropdown-container">
                            <button class="action-btn" onclick="toggleDropdown('${menuId}', event)">•••</button>
                            <div class="dropdown-menu" id="${menuId}">
                                <div class="dropdown-item" onclick="copyMsg('${uniqueId}')">📋 Copy</div>
                                <div class="dropdown-item" onclick="shareMsg('${uniqueId}')">🔗 Share</div>
                            </div>
                        </div>
                    </div>
                </div>`;
            
            window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' });
            
            try {
                const res = await fetch('/generate', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ prompt: query, image: currentImg })
                });
                const data = await res.json();
                document.getElementById(uniqueId).innerText = data.response || "Error";
                document.getElementById(uniqueActionsId).style.display = "flex";
                window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' });
            } catch(e) {
                document.getElementById(uniqueId).innerText = "Network error.";
                document.getElementById(uniqueActionsId).style.display = "flex";
            }
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
    image_data = data.get('image', None)
    ai_response = call_groq_api(user_prompt, image_data)
    return jsonify({'response': ai_response})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

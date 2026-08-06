from flask import Flask, request, jsonify, render_template_string
import os
import requests

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
                    "You MUST structure every answer using the exact following sections with clear headings:\n\n"
                    "1. Short Answer\n"
                    "2. Explanation\n"
                    "3. Evidence\n"
                    "4. Quran\n"
                    "5. Hadith\n"
                    "6. Scholars\n"
                    "7. References\n"
                    "8. Related Topics\n\n"
                    "Speak with deep respect, empathy, and wisdom like a sincere practicing Muslim scholar."
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
        
        .sidebar { position: fixed; top: 0; left: -280px; width: 280px; height: 100%; background: #fff; box-shadow: 2px 0 10px rgba(0,0,0,0.1); transition: 0.3s ease; z-index: 100; display: flex; flex-direction: column; }
        .sidebar.open { left: 0; }
        .sidebar-header { padding: 20px; font-size: 20px; font-weight: bold; color: #1e3d2f; border-bottom: 1px solid #eaeaea; display: flex; justify-content: space-between; align-items: center; }
        .close-sidebar { background: none; border: none; font-size: 20px; cursor: pointer; color: #555; }
        
        .sidebar-menu { list-style: none; padding: 15px 0; overflow-y: auto; flex: 1; }
        .sidebar-menu li { padding: 14px 20px; font-size: 17px; color: #333; cursor: pointer; display: flex; align-items: center; gap: 14px; transition: 0.2s; border-bottom: 1px solid #f9f9f9; }
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

        .search-box-container { margin-bottom: 15px; display: flex; gap: 10px; }
        .search-input-field { flex: 1; padding: 10px 15px; border: 1px solid #ccc; border-radius: 8px; font-size: 16px; outline: none; }

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
            <li onclick="startNewChat()">New Chat ➕️</li>
            <li onclick="switchView('history')">History</li>
            <li onclick="switchView('search')">Search Chats</li>
            <li onclick="switchView('setting')">Setting</li>
            <li onclick="switchView('help')">Help</li>
        </ul>
    </div>

    <div class="main-content">
        <!-- Home / Chat View -->
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

        <!-- History View -->
        <div id="history-view" class="view-section">
            <div class="view-title">Chat History 📜</div>
            <div class="view-body" id="history-container">
                <p>No chat history available.</p>
            </div>
        </div>

        <!-- Search Chats View -->
        <div id="search-view" class="view-section">
            <div class="view-title">Search Chats 🔍</div>
            <div class="search-box-container">
                <input type="text" id="chatSearchInput" class="search-input-field" placeholder="Search your past queries and answers..." oninput="filterSearchChats(this.value)">
            </div>
            <div class="view-body" id="search-results-container">
                <p>Type above to search through your saved chats.</p>
            </div>
        </div>

        <!-- Setting View -->
        <div id="setting-view" class="view-section">
            <div class="view-title">Settings ⚙️</div>
            <div class="view-body">
                <p><strong>Response Format:</strong> Structured (Short Answer, Explanation, Evidence, Quran, Hadith, Scholars, References, Related Topics)</p>
                <p style="margin-top: 15px;"><strong>School of Thought:</strong> Hanafi / Deoband & Banuri Town</p>
                <p style="margin-top: 15px;"><button onclick="clearAllData()" style="background:#ff4d4d; color:white; border:none; padding:10px 15px; border-radius:6px; cursor:pointer;">Clear All Chat Data</button></p>
            </div>
        </div>

        <!-- Help View -->
        <div id="help-view" class="view-section">
            <div class="view-title">Help & Support 💡</div>
            <div class="view-body">
                <p><strong>How to use Tibyan AI:</strong></p>
                <p style="margin-top: 10px;">• Type any Islamic question in the box below or click on the suggestion chips.</p>
                <p style="margin-top: 5px;">• Upload any scanned Fatawa or image using the paperclip 📎 icon to get insights.</p>
                <p style="margin-top: 5px;">• Every answer follows a rigorous scholarly breakdown format including Quranic verses, Hadith evidence, and scholarly references.</p>
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
            if (viewName === 'history') {
                renderHistory();
            }
            toggleSidebar();
        }

        function startNewChat() {
            document.getElementById('chat-history').innerHTML = '';
            const welcomeScreen = document.getElementById('welcome-screen');
            if (welcomeScreen) {
                welcomeScreen.style.display = 'flex';
            }
            switchView('home');
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
                    <div class="message ai-msg" id="${uniqueId}">Bismillah, preparing structured scholarly response...</div>
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
                    
                    // Save to local storage history
                    saveChatHistory(currentQuery, data.response);

                    const actionsDiv = document.createElement('div');
                    actionsDiv.className = 'ai-actions';
                    actionsDiv.innerHTML = `
                        <button class="action-btn" onclick="handleLike(this)">👍 Like</button>
                        <button class="action-btn" onclick="handleDislike(this)">👎 Dislike</button>
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

        function saveChatHistory(query, answer) {
            let historyList = JSON.parse(localStorage.getItem('tibyan_history') || '[]');
            historyList.unshift({ query: query, answer: answer, date: new Date().toLocaleString() });
            localStorage.setItem('tibyan_history', JSON.stringify(historyList));
        }

        function renderHistory() {
            const container = document.getElementById('history-container');
            let historyList = JSON.parse(localStorage.getItem('tibyan_history') || '[]');
            
            if (historyList.length === 0) {
                container.innerHTML = `<p>No chat history found.</p>`;
                return;
            }

            let html = '';
            historyList.forEach((item) => {
                html += `
                    <div class="saved-item">
                        <div class="saved-q">Q: ${item.query}</div>
                        <div class="saved-a">${item.answer}</div>
                    </div>
                `;
            });
            container.innerHTML = html;
        }

        function filterSearchChats(keyword) {
            const container = document.getElementById('search-results-container');
            let historyList = JSON.parse(localStorage.getItem('tibyan_history') || '[]');
            
            if (!keyword.trim()) {
                container.innerHTML = `<p>Type above to search through your saved chats.</p>`;
                return;
            }

            const filtered = historyList.filter(item => 
                item.query.toLowerCase().includes(keyword.toLowerCase()) || 
                item.answer.toLowerCase().includes(keyword.toLowerCase())
            );

            if (filtered.length === 0) {
                container.innerHTML = `<p>No matching chats found.</p>`;
                return;
            }

            let html = '';
            filtered.forEach((item) => {
                html += `
                    <div class="saved-item">
                        <div class="saved-q">Q: ${item.query}</div>
                        <div class="saved-a">${item.answer}</div>
                    </div>
                `;
            });
            container.innerHTML = html;
        }

        function clearAllData() {
            if (confirm("Are you sure you want to clear all chat data?")) {
                localStorage.removeItem('tibyan_history');
                alert("All data cleared successfully.");
                renderHistory();
            }
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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

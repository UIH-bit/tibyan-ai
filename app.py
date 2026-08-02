from flask import Flask, request, jsonify, render_template_string
import os
import requests

app = Flask(__name__)

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Tibyan AI</title>
    
    <!-- PWA Manifest & Mobile App Meta Tags -->
    <link rel="manifest" href="/manifest.json">
    <meta name="theme-color" content="#1a73e8">
    <meta name="mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-capable" content="yes">

    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; }
        
        body { background-color: #ffffff; color: #1f1f1f; display: flex; flex-direction: column; height: 100vh; overflow: hidden; }
        
        header { display: flex; align-items: center; justify-content: space-between; padding: 14px 24px; background-color: #ffffff; border-bottom: 1px solid #f0f0f0; flex-shrink: 0; }
        .logo-text { font-size: 20px; font-weight: 600; color: #1f1f1f; display: flex; align-items: center; gap: 8px; }
        .logo-text i { color: #1a73e8; }
        
        .content-area { flex: 1; overflow-y: auto; padding: 24px; display: flex; flex-direction: column; align-items: center; padding-bottom: 140px; }
        
        .view { width: 100%; max-width: 800px; display: none; flex-direction: column; }
        .view.active { display: flex; }

        .home-center { text-align: center; margin: auto 0; width: 100%; }
        .greeting { font-size: 38px; color: #1f1f1f; margin-bottom: 10px; font-weight: 500; font-family: serif; }
        .sub-greeting { font-size: 16px; color: #5f6368; margin-bottom: 30px; }
        
        .suggestions { display: flex; flex-wrap: wrap; gap: 12px; justify-content: center; margin-bottom: 20px; }
        .chip { background: #f8f9fa; border: 1px solid #dadce0; color: #3c4043; padding: 10px 16px; border-radius: 16px; font-size: 14px; cursor: pointer; transition: 0.2s; font-weight: 400; }
        .chip:hover { background: #f1f3f4; border-color: #bdc1c6; }
        
        #chat-box { width: 100%; text-align: left; display: none; flex-direction: column; gap: 24px; }
        .msg-container { width: 100%; margin-bottom: 15px; border-bottom: 1px solid #f1f3f4; padding-bottom: 15px; }
        
        .msg { font-size: 16px; line-height: 1.7; white-space: pre-wrap; width: 100%; }
        .user-msg { color: #1f1f1f; font-weight: 600; background: #f8f9fa; padding: 14px 18px; border-radius: 16px; margin-bottom: 12px; border-left: 4px solid #1a73e8; }
        .bot-msg { color: #202124; margin-bottom: 12px; padding: 4px 0; }
        
        .action-bar { display: flex; gap: 15px; align-items: center; margin-top: 5px; }
        .action-btn { background: transparent; border: none; color: #5f6368; font-size: 14px; cursor: pointer; display: inline-flex; align-items: center; gap: 6px; padding: 6px 10px; border-radius: 8px; transition: 0.2s; }
        .action-btn:hover { background: #f1f3f4; color: #202124; }
        .action-btn.active-action { color: #1a73e8; font-weight: 500; }

        .lib-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(240px, 1fr)); gap: 16px; width: 100%; margin-top: 10px; }
        .lib-card { background: #f8f9fa; border: 1px solid #dadce0; padding: 20px; border-radius: 16px; cursor: pointer; transition: 0.2s; display: flex; flex-direction: column; gap: 8px; }
        .lib-card:hover { background: #f1f3f4; border-color: #bdc1c6; box-shadow: 0 2px 6px rgba(0,0,0,0.05); }
        .lib-card h3 { color: #1a73e8; font-size: 17px; font-weight: 500; display: flex; align-items: center; gap: 8px; }
        .lib-card p { color: #5f6368; font-size: 14px; line-height: 1.4; }

        .section-title { font-size: 24px; color: #1f1f1f; margin-bottom: 15px; font-weight: 500; width: 100%; display: flex; justify-content: space-between; align-items: center; }
        
        .profile-box { background: #f8f9fa; border: 1px solid #dadce0; padding: 30px; border-radius: 16px; text-align: center; width: 100%; max-width: 450px; margin: auto; }
        .profile-avatar { font-size: 60px; color: #1a73e8; margin-bottom: 15px; }

        .bottom-panel { position: fixed; bottom: 65px; left: 0; width: 100%; background: transparent; padding: 12px 20px; display: flex; justify-content: center; z-index: 100; pointer-events: none; }
        .input-box { pointer-events: auto; display: flex; align-items: flex-end; background-color: #f0f4f9; border: 1px solid transparent; border-radius: 28px; padding: 10px 16px; width: 100%; max-width: 750px; transition: 0.2s; box-shadow: 0 2px 10px rgba(0,0,0,0.06); gap: 8px; }
        .input-box:focus-within { background: #ffffff; border-color: #d3e3fd; box-shadow: 0 4px 14px rgba(26,115,232,0.1); }
        
        .input-box textarea { flex: 1; background: transparent; border: none; outline: none; color: #1f1f1f; font-size: 16px; resize: none; max-height: 150px; min-height: 24px; line-height: 1.5; padding-top: 2px; }
        .input-box textarea::placeholder { color: #757575; }
        
        .tool-btn { background: transparent; border: none; color: #444746; font-size: 18px; cursor: pointer; padding: 6px; border-radius: 50%; transition: 0.2s; display: flex; align-items: center; justify-content: center; width: 38px; height: 38px; flex-shrink: 0; }
        .tool-btn:hover { background: #e2e8f0; color: #1f1f1f; }
        
        .send-btn { background: #1a73e8; border: none; color: #ffffff; font-size: 15px; cursor: pointer; width: 38px; height: 38px; border-radius: 50% !important; display: flex; align-items: center; justify-content: center; transition: 0.2s; flex-shrink: 0; }
        .send-btn:hover { background: #1557b0; }

        nav { position: fixed; bottom: 0; left: 0; width: 100%; display: flex; justify-content: space-around; background-color: #ffffff; padding: 8px 0; border-top: 1px solid #f0f0f0; z-index: 101; height: 60px; }
        .nav-item { display: flex; flex-direction: column; align-items: center; color: #5f6368; font-size: 12px; text-decoration: none; gap: 3px; cursor: pointer; }
        .nav-item.active { color: #1a73e8; font-weight: 500; }
        .nav-item i { font-size: 18px; }
    </style>
</head>
<body>
    <header>
        <div class="logo-text"><i class="fa-solid fa-sparkles"></i> Tibyan AI</div>
        <div style="font-size: 14px; color: #5f6368; font-weight: 500;"><i class="fa-solid fa-shield-halved" style="color: #1a73e8;"></i> Verified Knowledge</div>
    </header>

    <div class="content-area">
        <div id="view-home" class="view active">
            <div id="home-welcome" class="home-center">
                <div class="greeting">السلام عليكم</div>
                <div class="sub-greeting">Authentic Islamic Knowledge, Powered by Advanced Context AI</div>
                <div class="suggestions">
                    <div class="chip" onclick="sendSuggestion('What breaks the fast in detail?')">What breaks the fast?</div>
                    <div class="chip" onclick="sendSuggestion('Explain the deep virtues of Ayat al-Kursi')">Virtues of Ayat al-Kursi</div>
                    <div class="chip" onclick="sendSuggestion('Step by step guide to Tahajjud prayer')">How to perform Tahajjud?</div>
                </div>
            </div>
            <div id="chat-box"></div>
        </div>

        <div id="view-library" class="view">
            <div class="section-title">Expanded Islamic Library</div>
            <div class="lib-grid">
                <div class="lib-card" onclick="sendSuggestion('Explain the 5 Pillars of Islam with comprehensive proofs')">
                    <h3><i class="fa-solid fa-book"></i> Pillars of Islam</h3>
                    <p>Detailed study of Shahada, Salah, Zakat, Sawm, and Hajj.</p>
                </div>
                <div class="lib-card" onclick="sendSuggestion('Share 5 essential Daily Duas with Arabic text and meanings')">
                    <h3><i class="fa-solid fa-hands-praying"></i> Daily Duas</h3>
                    <p>Essential supplications for morning, evening, and protection.</p>
                </div>
                <div class="lib-card" onclick="sendSuggestion('Explain 3 authentic Hadiths from 40 Hadith Nawawi')">
                    <h3><i class="fa-solid fa-scroll"></i> 40 Hadith Nawawi</h3>
                    <p>Core sayings of Prophet Muhammad (PBUH) on Islamic morals.</p>
                </div>
                <div class="lib-card" onclick="sendSuggestion('Explain the meaning and beauty of 5 Names of Allah (Asma-ul-Husna)')">
                    <h3><i class="fa-solid fa-star-and-crescent"></i> Asma-ul-Husna</h3>
                    <p>Discover the profound meanings of the Beautiful Names of Allah.</p>
                </div>
                <div class="lib-card" onclick="sendSuggestion('Summarize Surah Al-Baqarah core themes and lessons')">
                    <h3><i class="fa-solid fa-quran"></i> Quranic Surahs</h3>
                    <p>Explore context, themes, and deep tafseer insights.</p>
                </div>
                <div class="lib-card" onclick="sendSuggestion('What are the main rules of Islamic Fiqh regarding Taharah (Purification)?')">
                    <h3><i class="fa-solid fa-scale-balanced"></i> Islamic Fiqh</h3>
                    <p>Practical rulings on daily worship, Wudu, and Ghusl.</p>
                </div>
            </div>
        </div>

        <div id="view-saved" class="view">
            <div class="section-title">
                Saved Answers
                <button onclick="clearSaved()" style="background: transparent; border: none; color: #ea4335; font-size: 13px; cursor: pointer;"><i class="fa-solid fa-trash"></i> Clear All</button>
            </div>
            <div id="saved-container" style="display: flex; flex-direction: column; gap: 15px; width: 100%;">
                <div style="color: #5f6368; font-size: 15px; text-align: center; margin-top: 40px;">
                    No saved answers yet. Click "Save" under any response.
                </div>
            </div>
        </div>

        <div id="view-profile" class="view">
            <div class="section-title">User Profile</div>
            <div class="profile-box">
                <div class="profile-avatar"><i class="fa-solid fa-circle-user"></i></div>
                <h3 style="color: #202124; font-size: 20px; margin-bottom: 6px;">Islamic Seeker</h3>
                <p style="color: #5f6368; font-size: 14px; margin-bottom: 20px;">Connected to Tibyan AI Advanced Engine</p>
                <div style="background: #e8f0fe; color: #1967d2; padding: 12px; border-radius: 8px; font-size: 14px; font-weight: 500;">
                    Status: Active & Contextualized
                </div>
            </div>
        </div>
    </div>

    <!-- Gemini Style Input Bar -->
    <div class="bottom-panel" id="input-container-wrapper">
        <div class="input-box">
            <button class="tool-btn" title="Voice Input" onclick="toggleVoiceInput()"><i class="fa-solid fa-microphone" id="mic-icon"></i></button>
            <textarea id="user-input" placeholder="Ask anything about Quran, Hadith, Fiqh..." rows="1" oninput="autoResize(this)" onkeydown="handleKey(event)"></textarea>
            <button class="send-btn" onclick="sendMessage()"><i class="fa-solid fa-arrow-up"></i></button>
        </div>
    </div>

    <nav>
        <a class="nav-item active" onclick="switchTab('home', this)"><i class="fa-solid fa-house"></i>Chat</a>
        <a class="nav-item" onclick="switchTab('library', this)"><i class="fa-solid fa-book-open"></i>Library</a>
        <a class="nav-item" onclick="switchTab('saved', this)"><i class="fa-solid fa-bookmark"></i>Saved</a>
        <a class="nav-item" onclick="switchTab('profile', this)"><i class="fa-solid fa-user"></i>Profile</a>
    </nav>

    <script>
        let chatHistory = JSON.parse(localStorage.getItem('tibyan_chat_history')) || [];
        let savedItems = JSON.parse(localStorage.getItem('tibyan_saved_items')) || [];
        let recognition = null;
        let isListening = false;

        window.addEventListener('DOMContentLoaded', () => {
            renderChatHistory();
            updateSavedUI();
        });

        if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            recognition = new SpeechRecognition();
            recognition.continuous = false;
            recognition.interimResults = false;
            recognition.lang = 'en-US';

            recognition.onresult = function(event) {
                const speechToText = event.results[0][0].transcript;
                const input = document.getElementById('user-input');
                input.value = speechToText;
                autoResize(input);
                stopListeningVisual();
                sendMessage();
            };

            recognition.onerror = () => stopListeningVisual();
            recognition.onend = () => stopListeningVisual();
        }

        function toggleVoiceInput() {
            if (!recognition) {
                alert('Voice input is not supported on your browser.');
                return;
            }
            if (isListening) {
                recognition.stop();
                stopListeningVisual();
            } else {
                recognition.start();
                startListeningVisual();
            }
        }

        function startListeningVisual() {
            isListening = true;
            const micIcon = document.getElementById('mic-icon');
            micIcon.style.color = '#ea4335';
            micIcon.classList.add('fa-beat');
        }

        function stopListeningVisual() {
            isListening = false;
            const micIcon = document.getElementById('mic-icon');
            micIcon.style.color = '#444746';
            micIcon.classList.remove('fa-beat');
        }

        function autoResize(textarea) {
            textarea.style.height = 'auto';
            textarea.style.height = textarea.scrollHeight + 'px';
        }

        function switchTab(tabName, element) {
            document.querySelectorAll('.view').forEach(v => v.classList.remove('active'));
            document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
            
            document.getElementById('view-' + tabName).classList.add('active');
            element.classList.add('active');

            document.getElementById('input-container-wrapper').style.display = (tabName === 'home') ? 'flex' : 'none';
        }

        function sendSuggestion(text) {
            switchTab('home', document.querySelector('.nav-item'));
            const input = document.getElementById('user-input');
            input.value = text;
            autoResize(input);
            sendMessage();
        }

        function handleKey(e) {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendMessage();
            }
        }

        function toggleLike(btn) {
            btn.classList.toggle('active-action');
            const dislikeBtn = btn.parentElement.querySelector('.dislike-btn');
            if (dislikeBtn) dislikeBtn.classList.remove('active-action');
        }

        function toggleDislike(btn) {
            btn.classList.toggle('active-action');
            const likeBtn = btn.parentElement.querySelector('.like-btn');
            if (likeBtn) likeBtn.classList.remove('active-action');
        }

        function copyText(btn) {
            const text = btn.getAttribute('data-content');
            navigator.clipboard.writeText(text);
            const originalHTML = btn.innerHTML;
            btn.innerHTML = '<i class="fa-solid fa-check"></i> Copied';
            setTimeout(() => { btn.innerHTML = originalHTML; }, 2000);
        }

        function saveAnswer(btn) {
            const text = btn.getAttribute('data-content');
            if (btn.classList.contains('active-action')) return;
            
            btn.classList.add('active-action');
            btn.innerHTML = '<i class="fa-solid fa-bookmark"></i> Saved';
            
            if (!savedItems.includes(text)) {
                savedItems.push(text);
                localStorage.setItem('tibyan_saved_items', JSON.stringify(savedItems));
                updateSavedUI();
            }
        }

        function clearSaved() {
            if (confirm("Are you sure you want to clear all saved answers?")) {
                savedItems = [];
                localStorage.removeItem('tibyan_saved_items');
                updateSavedUI();
            }
        }

        function updateSavedUI() {
            const container = document.getElementById('saved-container');
            if (savedItems.length === 0) {
                container.innerHTML = '<div style="color: #5f6368; font-size: 15px; text-align: center; margin-top: 40px;">No saved answers yet. Click "Save" under any response.</div>';
                return;
            }
            container.innerHTML = '';
            savedItems.forEach((item, index) => {
                container.innerHTML += `
                    <div style="background: #f8f9fa; border: 1px solid #dadce0; padding: 20px; border-radius: 16px; font-size: 15px; line-height: 1.6; color: #202124;">
                        <div style="color: #1a73e8; font-weight: 500; margin-bottom: 8px;">Saved Answer #${index + 1}</div>
                        ${item}
                    </div>
                `;
            });
        }

        function renderChatHistory() {
            const homeWelcome = document.getElementById('home-welcome');
            const chatBox = document.getElementById('chat-box');
            
            if (chatHistory.length > 0) {
                homeWelcome.style.display = 'none';
                chatBox.style.display = 'flex';
                chatBox.innerHTML = '';

                chatHistory.forEach(chat => {
                    const tempDiv = document.createElement('div');
                    tempDiv.textContent = chat.bot;
                    const safeText = tempDiv.innerHTML;

                    const isAlreadySaved = savedItems.includes(chat.bot);
                    const saveBtnClass = isAlreadySaved ? 'action-btn active-action' : 'action-btn';
                    const saveBtnHtml = isAlreadySaved ? '<i class="fa-solid fa-bookmark"></i> Saved' : '<i class="fa-regular fa-bookmark"></i> Save';

                    chatBox.innerHTML += `
                        <div class="msg-container">
                            <div class="msg user-msg">You: ${chat.user}</div>
                            <div class="msg bot-msg">${chat.bot}</div>
                            <div class="action-bar">
                                <button class="action-btn like-btn" onclick="toggleLike(this)"><i class="fa-regular fa-thumbs-up"></i> Like</button>
                                <button class="action-btn dislike-btn" onclick="toggleDislike(this)"><i class="fa-regular fa-thumbs-down"></i> Dislike</button>
                                <button class="action-btn" data-content="${safeText.replace(/"/g, '&quot;')}" onclick="copyText(this)"><i class="fa-regular fa-copy"></i> Copy</button>
                                <button class="${saveBtnClass}" data-content="${safeText.replace(/"/g, '&quot;')}" onclick="saveAnswer(this)">${saveBtnHtml}</button>
                            </div>
                        </div>
                    `;
                });
            }
        }

        async function sendMessage() {
            const input = document.getElementById('user-input');
            const message = input.value.trim();
            if (!message) return;

            const homeWelcome = document.getElementById('home-welcome');
            const chatBox = document.getElementById('chat-box');
            
            if (homeWelcome) homeWelcome.style.display = 'none';
            chatBox.style.display = 'flex';

            chatBox.innerHTML += `<div class="msg-container"><div class="msg user-msg">You: ${message}</div></div>`;
            input.value = '';
            input.style.height = '24px';
            window.scrollTo(0, document.body.scrollHeight);

            try {
                const response = await fetch('/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ message: message })
                });
                const data = await response.json();
                
                const tempDiv = document.createElement('div');
                tempDiv.textContent = data.response;
                const safeText = tempDiv.innerHTML;

                chatHistory.push({ user: message, bot: data.response });
                localStorage.setItem('tibyan_chat_history', JSON.stringify(chatHistory));

                chatBox.innerHTML += `
                    <div class="msg-container">
                        <div class="msg bot-msg">${data.response}</div>
                        <div class="action-bar">
                            <button class="action-btn like-btn" onclick="toggleLike(this)"><i class="fa-regular fa-thumbs-up"></i> Like</button>
                            <button class="action-btn dislike-btn" onclick="toggleDislike(this)"><i class="fa-regular fa-thumbs-down"></i> Dislike</button>
                            <button class="action-btn" data-content="${safeText.replace(/"/g, '&quot;')}" onclick="copyText(this)"><i class="fa-regular fa-copy"></i> Copy</button>
                            <button class="action-btn" data-content="${safeText.replace(/"/g, '&quot;')}" onclick="saveAnswer(this)"><i class="fa-regular fa-bookmark"></i> Save</button>
                        </div>
                    </div>
                `;
                window.scrollTo(0, document.body.scrollHeight);
            } catch (err) {
                chatBox.innerHTML += `<div class="msg-container"><div class="msg bot-msg">Error: Unable to fetch response.</div></div>`;
            }
        }
    </script>
</body>
</html>
'''

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

# Manifest Route with SVG Icon Support (No Pillow needed)
@app.route('/manifest.json')
def manifest():
    return jsonify({
        "name": "Tibyan AI",
        "short_name": "Tibyan",
        "start_url": "/",
        "display": "standalone",
        "background_color": "#ffffff",
        "theme_color": "#1a73e8",
        "icons": [
            {
                "src": "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/svgs/solid/sparkles.svg",
                "sizes": "512x512",
                "type": "image/svg+xml",
                "purpose": "any maskable"
            }
        ]
    })

@app.route('/chat', methods=['POST'])
def chat():
    user_msg = request.json.get('message', '')
    api_key = os.environ.get("GROQ_API_KEY")
    
    if not api_key:
        return jsonify({"response": "Error: GROQ_API_KEY is missing."})

    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    system_prompt = (
        "You are Tibyan AI, a deeply knowledgeable, empathetic, and expert Islamic scholar assistant. "
        "Your goal is to fully understand the user's intent, context, and core question with high intelligence. "
        "Provide structured, comprehensive, and authentic answers strictly derived from the Holy Quran, authentic Hadiths "
        "(Sahih al-Bukhari, Sahih Muslim, etc.), and recognized mainstream Fiqh schools. "
        "Always cite relevant Quranic verses or Hadith references where appropriate. Maintain a respectful, wise, and scholarly tone."
    )

    data = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_msg}
        ]
    }
    try:
        res = requests.post(url, json=data, headers=headers)
        res_json = res.json()
        if 'choices' in res_json:
            bot_response = res_json['choices'][0]['message']['content']
            return jsonify({"response": bot_response})
        else:
            error_msg = res_json.get('error', {}).get('message', 'Invalid API Key')
            return jsonify({"response": f"API Error: {error_msg}"})
    except Exception as e:
        return jsonify({"response": f"Connection Error: {str(e)}"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

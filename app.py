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
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }
        body { background-color: #031e11; color: #ffffff; display: flex; flex-direction: column; height: 100vh; overflow: hidden; }
        header { display: flex; align-items: center; padding: 12px 20px; gap: 15px; background-color: #031e11; border-bottom: 1px solid #0d301e; flex-shrink: 0; }
        .logo-text { font-size: 18px; font-weight: bold; color: #d4af37; }
        
        .content-area { flex: 1; overflow-y: auto; padding: 20px; display: flex; flex-direction: column; align-items: center; padding-bottom: 90px; }
        
        .view { width: 100%; max-width: 600px; display: none; flex-direction: column; }
        .view.active { display: flex; }

        .home-center { text-align: center; margin: auto 0; width: 100%; }
        .greeting { font-size: 32px; color: #d4af37; margin-bottom: 8px; font-family: serif; }
        .sub-greeting { font-size: 14px; color: #a0b0a8; margin-bottom: 25px; }
        .suggestions { display: flex; flex-wrap: wrap; gap: 10px; justify-content: center; margin-bottom: 20px; }
        .chip { background: transparent; border: 1px solid #1a422d; color: #a0b0a8; padding: 10px 16px; border-radius: 12px; font-size: 13px; cursor: pointer; transition: 0.2s; }
        .chip:hover { border-color: #d4af37; color: #ffffff; }
        
        #chat-box { width: 100%; text-align: left; display: none; flex-direction: column; gap: 20px; }
        .msg-container { width: 100%; margin-bottom: 20px; position: relative; }
        .msg { font-size: 14px; line-height: 1.6; white-space: pre-wrap; width: 100%; }
        .user-msg { color: #d4af37; font-weight: 500; border-left: 3px solid #d4af37; padding-left: 10px; margin-bottom: 10px; }
        .bot-msg { color: #e0e0e0; margin-bottom: 8px; }
        
        .save-btn { background: transparent; border: none; color: #5a7566; font-size: 13px; cursor: pointer; display: inline-flex; align-items: center; gap: 5px; transition: 0.2s; }
        .save-btn:hover, .save-btn.saved { color: #d4af37; }

        .lib-card { background: #072e1b; border: 1px solid #1a422d; padding: 15px; border-radius: 12px; margin-bottom: 12px; cursor: pointer; transition: 0.2s; width: 100%; }
        .lib-card:hover { border-color: #d4af37; }
        .lib-card h3 { color: #d4af37; font-size: 16px; margin-bottom: 5px; }
        .lib-card p { color: #a0b0a8; font-size: 13px; }

        .section-title { font-size: 20px; color: #d4af37; margin-bottom: 15px; font-family: serif; width: 100%; }
        .profile-box { background: #072e1b; border: 1px solid #1a422d; padding: 20px; border-radius: 12px; text-align: center; width: 100%; }
        .profile-avatar { font-size: 50px; color: #d4af37; margin-bottom: 10px; }

        /* Bottom Fixed Controls */
        .bottom-panel { position: fixed; bottom: 50px; left: 0; width: 100%; background: #031e11; padding: 8px 15px; display: flex; justify-content: center; z-index: 100; border-top: 1px solid #0d301e; }
        .input-box { display: flex; align-items: center; background-color: #0d301e; border: 1px solid #1a422d; border-radius: 25px; padding: 8px 16px; width: 100%; max-width: 600px; }
        .input-box input { flex: 1; background: transparent; border: none; outline: none; color: #fff; font-size: 14px; }
        .input-box input::placeholder { color: #6b8275; }
        .send-btn { background: transparent; border: none; color: #d4af37; font-size: 18px; cursor: pointer; margin-left: 10px; }

        nav { position: fixed; bottom: 0; left: 0; width: 100%; display: flex; justify-content: space-around; background-color: #031e11; padding: 10px 0; border-top: 1px solid #0d301e; z-index: 101; height: 50px; }
        .nav-item { display: flex; flex-direction: column; align-items: center; color: #5a7566; font-size: 11px; text-decoration: none; gap: 2px; cursor: pointer; }
        .nav-item.active { color: #d4af37; }
        .nav-item i { font-size: 16px; }
    </style>
</head>
<body>
    <header>
        <div class="logo-text"><i class="fa-solid fa-moon"></i> Tibyan AI</div>
    </header>

    <div class="content-area">
        <div id="view-home" class="view active">
            <div id="home-welcome" class="home-center">
                <div class="greeting">السلام عليكم</div>
                <div class="sub-greeting">Authentic Islamic Knowledge, Powered by AI</div>
                <div class="suggestions">
                    <div class="chip" onclick="sendSuggestion('What breaks the fast?')">What breaks the fast?</div>
                    <div class="chip" onclick="sendSuggestion('Virtues of Ayat al-Kursi')">Virtues of Ayat al-Kursi</div>
                    <div class="chip" onclick="sendSuggestion('How to perform Tahajjud?')">How to perform Tahajjud?</div>
                </div>
            </div>
            <div id="chat-box"></div>
        </div>

        <div id="view-library" class="view">
            <div class="section-title">Islamic Library</div>
            <div class="lib-card" onclick="sendSuggestion('Explain the 5 Pillars of Islam')">
                <h3><i class="fa-solid fa-book"></i> The 5 Pillars of Islam</h3>
                <p>Learn about Shahada, Salah, Zakat, Sawm, and Hajj with proofs.</p>
            </div>
            <div class="lib-card" onclick="sendSuggestion('Summarize Surah Al-Baqarah main themes')">
                <h3><i class="fa-solid fa-quran"></i> Quranic Studies & Surahs</h3>
                <p>Explore verses, context of revelation, and tafseer.</p>
            </div>
            <div class="lib-card" onclick="sendSuggestion('Give me 3 authentic Hadiths on good character')">
                <h3><i class="fa-solid fa-scroll"></i> Hadith Collections</h3>
                <p>Sahih Bukhari, Sahih Muslim authentic sayings.</p>
            </div>
        </div>

        <div id="view-saved" class="view">
            <div class="section-title">Saved Answers</div>
            <div id="saved-container" style="display: flex; flex-direction: column; gap: 15px; width: 100%;">
                <div id="no-saved" style="color: #a0b0a8; font-size: 14px; text-align: center; margin-top: 40px;">
                    No saved answers yet. Click "Save Answer" under any response.
                </div>
            </div>
        </div>

        <div id="view-profile" class="view">
            <div class="section-title">User Profile</div>
            <div class="profile-box">
                <div class="profile-avatar"><i class="fa-solid fa-user-circle"></i></div>
                <h3 style="color: #d4af37; margin-bottom: 5px;">Islamic Seeker</h3>
                <p style="color: #a0b0a8; font-size: 13px; margin-bottom: 15px;">Connected to Tibyan AI Engine</p>
                <div style="background: #031e11; padding: 10px; border-radius: 8px; font-size: 13px; color: #fff;">
                    Status: <span style="color: #2ecc71;">Active & Verified</span>
                </div>
            </div>
        </div>
    </div>

    <div class="bottom-panel" id="input-container-wrapper">
        <div class="input-box">
            <input type="text" id="user-input" placeholder="Ask anything about Quran, Hadith, Fiqh..." onkeypress="handleKey(event)">
            <button class="send-btn" onclick="sendMessage()"><i class="fa-solid fa-paper-plane"></i></button>
        </div>
    </div>

    <nav>
        <a class="nav-item active" onclick="switchTab('home', this)"><i class="fa-solid fa-house"></i>Chat</a>
        <a class="nav-item" onclick="switchTab('library', this)"><i class="fa-solid fa-book-open"></i>Library</a>
        <a class="nav-item" onclick="switchTab('saved', this)"><i class="fa-solid fa-bookmark"></i>Saved</a>
        <a class="nav-item" onclick="switchTab('profile', this)"><i class="fa-solid fa-user"></i>Profile</a>
    </nav>

    <script>
        let savedItems = [];

        function switchTab(tabName, element) {
            document.querySelectorAll('.view').forEach(v => v.classList.remove('active'));
            document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
            
            document.getElementById('view-' + tabName).classList.add('active');
            element.classList.add('active');

            document.getElementById('input-container-wrapper').style.display = (tabName === 'home') ? 'flex' : 'none';
        }

        function sendSuggestion(text) {
            switchTab('home', document.querySelector('.nav-item'));
            document.getElementById('user-input').value = text;
            sendMessage();
        }

        function handleKey(e) {
            if (e.key === 'Enter') sendMessage();
        }

        function saveAnswer(btn, text) {
            if (btn.classList.contains('saved')) return;
            btn.classList.add('saved');
            btn.innerHTML = '<i class="fa-solid fa-bookmark"></i> Saved';
            
            savedItems.push(text);
            updateSavedUI();
        }

        function updateSavedUI() {
            const container = document.getElementById('saved-container');
            if (savedItems.length === 0) {
                container.innerHTML = '<div style="color: #a0b0a8; font-size: 14px; text-align: center; margin-top: 40px;">No saved answers yet.</div>';
                return;
            }
            container.innerHTML = '';
            savedItems.forEach((item, index) => {
                container.innerHTML += `
                    <div style="background: #072e1b; border: 1px solid #1a422d; padding: 15px; border-radius: 12px; font-size: 14px; line-height: 1.5; color: #e0e0e0;">
                        <div style="color: #d4af37; font-weight: bold; margin-bottom: 8px;">Saved Answer #${index + 1}</div>
                        ${item}
                    </div>
                `;
            });
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
            window.scrollTo(0, document.body.scrollHeight);

            try {
                const response = await fetch('/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ message: message })
                });
                const data = await response.json();
                
                const uniqueId = 'msg_' + Date.now();
                chatBox.innerHTML += `
                    <div class="msg-container">
                        <div class="msg bot-msg" id="${uniqueId}">${data.response}</div>
                        <button class="save-btn" onclick="saveAnswer(this, \`${data.response.replace(/`/g, '\\`')}\`)">
                            <i class="fa-regular fa-bookmark"></i> Save Answer
                        </button>
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
    data = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": "You are Tibyan AI, an expert and authentic Islamic scholar assistant. Provide well-structured answers based strictly on Quran, authentic Hadiths (Bukhari, Muslim, etc.), and recognized Fiqh, along with clear references."},
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

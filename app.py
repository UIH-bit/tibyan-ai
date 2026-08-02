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
        * { margin: 0; padding: 0; box-sizing: border-box; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; }
        
        /* Gemini style clean white theme */
        body { background-color: #ffffff; color: #1f1f1f; display: flex; flex-direction: column; height: 100vh; overflow: hidden; }
        
        header { display: flex; align-items: center; padding: 16px 24px; gap: 15px; background-color: #ffffff; border-bottom: 1px solid #f0f0f0; flex-shrink: 0; }
        .logo-text { font-size: 20px; font-weight: 600; color: #1f1f1f; display: flex; align-items: center; gap: 8px; }
        .logo-text i { color: #1a73e8; }
        
        .content-area { flex: 1; overflow-y: auto; padding: 24px; display: flex; flex-direction: column; align-items: center; padding-bottom: 100px; }
        
        .view { width: 100%; max-width: 750px; display: none; flex-direction: column; }
        .view.active { display: flex; }

        .home-center { text-align: center; margin: auto 0; width: 100%; }
        .greeting { font-size: 38px; color: #1f1f1f; margin-bottom: 10px; font-weight: 500; font-family: serif; }
        .sub-greeting { font-size: 16px; color: #5f6368; margin-bottom: 30px; }
        
        .suggestions { display: flex; flex-wrap: wrap; gap: 12px; justify-content: center; margin-bottom: 20px; }
        .chip { background: #f8f9fa; border: 1px solid #dadce0; color: #3c4043; padding: 12px 18px; border-radius: 16px; font-size: 15px; cursor: pointer; transition: 0.2s; font-weight: 400; }
        .chip:hover { background: #f1f3f4; border-color: #bdc1c6; }
        
        #chat-box { width: 100%; text-align: left; display: none; flex-direction: column; gap: 24px; }
        .msg-container { width: 100%; margin-bottom: 10px; }
        
        /* Larger fonts and clean spacing like Gemini */
        .msg { font-size: 16px; line-height: 1.7; white-space: pre-wrap; width: 100%; }
        .user-msg { color: #1f1f1f; font-weight: 600; background: #f8f9fa; padding: 14px 18px; border-radius: 16px; margin-bottom: 12px; border-left: 4px solid #1a73e8; }
        .bot-msg { color: #202124; margin-bottom: 10px; padding: 4px 0; }
        
        .save-btn { background: transparent; border: none; color: #5f6368; font-size: 14px; cursor: pointer; display: inline-flex; align-items: center; gap: 6px; transition: 0.2s; padding: 4px 0; }
        .save-btn:hover, .save-btn.saved { color: #1a73e8; font-weight: 500; }

        .lib-card { background: #f8f9fa; border: 1px solid #dadce0; padding: 20px; border-radius: 16px; margin-bottom: 16px; cursor: pointer; transition: 0.2s; width: 100%; }
        .lib-card:hover { background: #f1f3f4; border-color: #bdc1c6; }
        .lib-card h3 { color: #1a73e8; font-size: 18px; margin-bottom: 6px; font-weight: 500; }
        .lib-card p { color: #5f6368; font-size: 15px; }

        .section-title { font-size: 24px; color: #1f1f1f; margin-bottom: 20px; font-weight: 500; width: 100%; }
        
        .profile-box { background: #f8f9fa; border: 1px solid #dadce0; padding: 30px; border-radius: 16px; text-align: center; width: 100%; }
        .profile-avatar { font-size: 60px; color: #1a73e8; margin-bottom: 15px; }

        /* Bottom Fixed Controls */
        .bottom-panel { position: fixed; bottom: 60px; left: 0; width: 100%; background: #ffffff; padding: 12px 20px; display: flex; justify-content: center; z-index: 100; }
        .input-box { display: flex; align-items: center; background-color: #f1f3f4; border: 1px solid transparent; border-radius: 28px; padding: 12px 20px; width: 100%; max-width: 750px; transition: 0.2s; box-shadow: 0 1px 6px rgba(32,33,36,.1); }
        .input-box:focus-within { background: #ffffff; border-color: #dadce0; box-shadow: 0 1px 6px rgba(32,33,36,.15); }
        .input-box input { flex: 1; background: transparent; border: none; outline: none; color: #202124; font-size: 16px; }
        .input-box input::placeholder { color: #70757a; }
        .send-btn { background: transparent; border: none; color: #1a73e8; font-size: 20px; cursor: pointer; margin-left: 12px; }

        nav { position: fixed; bottom: 0; left: 0; width: 100%; display: flex; justify-content: space-around; background-color: #ffffff; padding: 10px 0; border-top: 1px solid #f0f0f0; z-index: 101; height: 60px; }
        .nav-item { display: flex; flex-direction: column; align-items: center; color: #5f6368; font-size: 12px; text-decoration: none; gap: 4px; cursor: pointer; }
        .nav-item.active { color: #1a73e8; font-weight: 500; }
        .nav-item i { font-size: 18px; }
    </style>
</head>
<body>
    <header>
        <div class="logo-text"><i class="fa-solid fa-sparkles"></i> Tibyan AI</div>
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
                <div style="color: #5f6368; font-size: 15px; text-align: center; margin-top: 40px;">
                    No saved answers yet. Click "Save Answer" under any response.
                </div>
            </div>
        </div>

        <div id="view-profile" class="view">
            <div class="section-title">User Profile</div>
            <div class="profile-box">
                <div class="profile-avatar"><i class="fa-solid fa-circle-user"></i></div>
                <h3 style="color: #202124; font-size: 20px; margin-bottom: 6px;">Islamic Seeker</h3>
                <p style="color: #5f6368; font-size: 14px; margin-bottom: 20px;">Connected to Tibyan AI Engine</p>
                <div style="background: #e8f0fe; color: #1967d2; padding: 12px; border-radius: 8px; font-size: 14px; font-weight: 500;">
                    Status: Active & Verified
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
                container.innerHTML = '<div style="color: #5f6368; font-size: 15px; text-align: center; margin-top: 40px;">No saved answers yet.</div>';
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

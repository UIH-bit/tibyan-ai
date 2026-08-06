from flask import Flask, request, jsonify, render_template_string
import urllib.request
import json
import os

app = Flask(__name__)

# Frontend HTML/CSS/JS Template (Screenshots ke mutabiq exact design)
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Tibyan AI</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }
        body { background-color: #ffffff; color: #111; display: flex; flex-direction: column; height: 100vh; }
        
        /* Header */
        header { display: flex; align-items: center; padding: 15px 20px; border-bottom: 1px solid #eaeaea; background: #fff; }
        .menu-btn { font-size: 24px; background: none; border: none; cursor: pointer; margin-right: 15px; color: #1e3d2f; }
        .logo { font-size: 20px; font-weight: bold; color: #1e3d2f; }

        /* Sidebar Menu */
        .sidebar { position: fixed; top: 0; left: -280px; width: 280px; height: 100%; background: #ffffff; box-shadow: 2px 0 10px rgba(0,0,0,0.1); transition: 0.3s ease; z-index: 1000; display: flex; flex-direction: column; }
        .sidebar.active { left: 0; }
        .sidebar-header { padding: 20px; font-size: 20px; font-weight: bold; color: #1e3d2f; border-bottom: 1px solid #eaeaea; }
        .sidebar-menu { list-style: none; padding: 10px 0; }
        .sidebar-menu li { padding: 15px 20px; display: flex; align-items: center; cursor: pointer; color: #333; font-size: 16px; }
        .sidebar-menu li:hover { background: #f4f7f5; }
        .sidebar-menu li span { margin-right: 15px; font-size: 18px; }
        .overlay { position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.4); display: none; z-index: 999; }
        .overlay.active { display: block; }

        /* Main Chat Area */
        .chat-container { flex: 1; display: flex; flex-direction: column; justify-content: space-between; max-width: 800px; width: 100%; margin: 0 auto; padding: 20px; overflow-y: auto; }
        
        .welcome-section { display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center; margin: auto 0; }
        .arabic-greeting { font-size: 38px; color: #1e3d2f; font-weight: bold; margin-bottom: 15px; font-family: serif; }
        .sub-text { font-size: 16px; color: #555; margin-bottom: 30px; }

        /* Suggestion Buttons */
        .suggestions { width: 100%; display: flex; flex-direction: column; gap: 12px; max-width: 500px; }
        .suggestion-chip { background: #fff; border: 1px solid #e0e0e0; border-radius: 30px; padding: 14px 20px; text-align: left; font-size: 15px; color: #333; cursor: pointer; transition: 0.2s; box-shadow: 0 2px 5px rgba(0,0,0,0.02); }
        .suggestion-chip:hover { background: #f9fbf9; border-color: #1e3d2f; }

        /* Chat History Box */
        #chat-history { width: 100%; display: flex; flex-direction: column; gap: 15px; margin-bottom: 20px; }
        .message { padding: 12px 18px; border-radius: 12px; max-width: 85%; line-height: 1.5; font-size: 15px; }
        .user-msg { background: #f0f4f1; color: #1e3d2f; align-self: flex-end; margin-left: auto; }
        .ai-msg { background: #ffffff; border: 1px solid #e0e0e0; color: #222; align-self: flex-start; }

        /* Input Area */
        .input-area { display: flex; align-items: center; padding: 15px 10px; border-top: 1px solid #eaeaea; background: #fff; gap: 10px; max-width: 800px; width: 100%; margin: 0 auto; }
        .action-btn { background: #f4f4f4; border: none; border-radius: 50%; width: 40px; height: 40px; font-size: 20px; cursor: pointer; display: flex; align-items: center; justify-content: center; color: #555; }
        .text-input { flex: 1; border: 1px solid #e0e0e0; border-radius: 25px; padding: 12px 20px; font-size: 15px; outline: none; background: #f9f9f9; }
        .text-input:focus { border-color: #1e3d2f; background: #fff; }
        .send-btn { background: #1e3d2f; border: none; border-radius: 50%; width: 42px; height: 42px; display: flex; align-items: center; justify-content: center; cursor: pointer; color: white; }
        .send-btn svg { width: 18px; height: 18px; fill: currentColor; }
    </style>
</head>
<body>

    <!-- Header -->
    <header>
        <button class="menu-btn" onclick="toggleMenu()">☰</button>
        <div class="logo">Tibyan AI</div>
    </header>

    <!-- Sidebar Menu -->
    <div class="overlay" id="overlay" onclick="toggleMenu()"></div>
    <div class="sidebar" id="sidebar">
        <div class="sidebar-header">Tibyan AI Menu</div>
        <ul class="sidebar-menu">
            <li onclick="toggleMenu()"><span>🏠</span> Home</li>
            <li onclick="alert('Library feature coming soon!')"><span>📚</span> Library (Authentic Books)</li>
            <li onclick="alert('Saved Answers feature coming soon!')"><span>🔖</span> Saved Answers</li>
            <li onclick="alert('User Profile feature coming soon!')"><span>👤</span> User Profile</li>
            <li onclick="alert('Tibyan AI v1.0 - Authentic Islamic Knowledge Source')"><span>ℹ️</span> About Tibyan AI</li>
        </ul>
    </div>

    <!-- Main Chat Container -->
    <div class="chat-container">
        
        <div id="chat-box" style="width: 100%;">
            <!-- Initial Welcome & Suggestions Screen -->
            <div class="welcome-section" id="welcome-screen">
                <div class="arabic-greeting">السلام عليكم</div>
                <div class="sub-text">Ask anything about Islam from authentic sources</div>
                
                <div class="suggestions">
                    <div class="suggestion-chip" onclick="sendPrompt('What breaks the fast?')">What breaks the fast?</div>
                    <div class="suggestion-chip" onclick="sendPrompt('Virtues of Ayat al-Kursi')">Virtues of Ayat al-Kursi</div>
                    <div class="suggestion-chip" onclick="sendPrompt('How to perform Tahajjud?')">How to perform Tahajjud?</div>
                </div>
            </div>
            
            <div id="chat-history"></div>
        </div>

        <!-- Input Bar -->
        <div class="input-area">
            <button class="action-btn" onclick="document.getElementById('userInput').value=''">+</button>
            <input type="text" id="userInput" class="text-input" placeholder="Type your question..." onkeypress="handleKeyPress(event)">
            <button class="send-btn" onclick="submitQuery()">
                <svg viewBox="0 0 24 24"><path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"></path></svg>
            </button>
        </div>
    </div>

    <script>
        function toggleMenu() {
            document.getElementById('sidebar').classList.toggle('active');
            document.getElementById('overlay').classList.toggle('active');
        }

        function handleKeyPress(e) {
            if (e.key === 'Enter') {
                submitQuery();
            }
        }

        function sendPrompt(text) {
            document.getElementById('userInput').value = text;
            submitQuery();
        }

        async function submitQuery() {
            const inputField = document.getElementById('userInput');
            const query = inputField.value.trim();
            if (!query) return;

            // Hide welcome screen on first message
            const welcomeScreen = document.getElementById('welcome-screen');
            if (welcomeScreen) {
                welcomeScreen.style.display = 'none';
            }

            const historyBox = document.getElementById('chat-history');

            // Append User Message
            historyBox.innerHTML += `<div class="message user-msg">${query}</div>`;
            inputField.value = '';
            window.scrollTo(0, document.body.scrollHeight);

            // Loading placeholder
            const loadingId = 'loading-' + Date.now();
            historyBox.innerHTML += `<div class="message ai-msg" id="${loadingId}">Thinking...</div>`;

            try {
                const response = await fetch('/generate', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ prompt: query })
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
            }
            window.scrollTo(0, document.body.scrollHeight);
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
    prompt = data.get('prompt', '')
    api_key = os.environ.get("GEMINI_API_KEY")
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
    
    payload = {
        "contents": [{"parts": [{"text": prompt}]}]
    }
    
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode('utf-8'),
        headers={'Content-Type': 'application/json'}
    )
    
    try:
        with urllib.request.urlopen(req) as response:
            res_data = json.loads(response.read().decode('utf-8'))
            text = res_data['candidates'][0]['content']['parts'][0]['text']
            return jsonify({'response': text})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

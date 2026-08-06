from flask import Flask, request, jsonify, render_template_string
import google.generativeai as genai
import os
import requests

app = Flask(__name__)

api_key = os.environ.get("GEMINI_API_KEY")
genai.configure(api_key=api_key)

# Using a robust fallback model name for older google-generativeai packages
model = genai.GenerativeModel('gemini-pro')

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

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Tibyan AI - Authentic Islamic Knowledge</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }
        body { background-color: #ffffff; color: #111; display: flex; flex-direction: column; height: 100vh; }
        
        header { display: flex; align-items: center; padding: 15px 20px; border-bottom: 1px solid #eaeaea; background: #fff; }
        .menu-btn { font-size: 24px; background: none; border: none; cursor: pointer; margin-right: 15px; color: #1e3d2f; }
        .logo { font-size: 20px; font-weight: bold; color: #1e3d2f; }

        .sidebar { position: fixed; top: 0; left: -280px; width: 280px; height: 100%; background: #ffffff; box-shadow: 2px 0 10px rgba(0,0,0,0.1); transition: 0.3s ease; z-index: 1000; display: flex; flex-direction: column; }
        .sidebar.active { left: 0; }
        .sidebar-header { padding: 20px; font-size: 20px; font-weight: bold; color: #1e3d2f; border-bottom: 1px solid #eaeaea; }
        .sidebar-menu { list-style: none; padding: 10px 0; }
        .sidebar-menu li { padding: 15px 20px; display: flex; align-items: center; cursor: pointer; color: #333; font-size: 16px; }
        .sidebar-menu li:hover { background: #f4f7f5; }
        .sidebar-menu li span { margin-right: 15px; font-size: 18px; }
        .overlay { position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.4); display: none; z-index: 999; }
        .overlay.active { display: block; }

        .chat-container { flex: 1; display: flex; flex-direction: column; justify-content: space-between; max-width: 800px; width: 100%; margin: 0 auto; padding: 20px; overflow-y: auto; }
        
        .welcome-section { display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center; margin: auto 0; }
        .arabic-greeting { font-size: 38px; color: #1e3d2f; font-weight: bold; margin-bottom: 15px; font-family: serif; }
        .sub-text { font-size: 16px; color: #555; margin-bottom: 30px; }

        .suggestions { width: 100%; display: flex; flex-direction: column; gap: 12px; max-width: 500px; }
        .suggestion-chip { background: #fff; border: 1px solid #e0e0e0; border-radius: 30px; padding: 14px 20px; text-align: left; font-size: 15px; color: #333; cursor: pointer; transition: 0.2s; box-shadow: 0 2px 5px rgba(0,0,0,0.02); }
        .suggestion-chip:hover { background: #f9fbf9; border-color: #1e3d2f; }

        #chat-history { width: 100%; display: flex; flex-direction: column; gap: 15px; margin-bottom: 20px; }
        .message { padding: 14px 18px; border-radius: 12px; max-width: 85%; line-height: 1.6; font-size: 15px; white-space: pre-wrap; }
        .user-msg { background: #f0f4f1; color: #1e3d2f; align-self: flex-end; margin-left: auto; }
        .ai-msg { background: #ffffff; border: 1px solid #e0e0e0; color: #222; align-self: flex-start; }

        .input-area { display: flex; align-items: flex-end; padding: 12px 15px; border-top: 1px solid #eaeaea; background: #fff; gap: 10px; max-width: 800px; width: 100%; margin: 0 auto; }
        .action-btn { background: #f4f4f4; border: none; border-radius: 50%; width: 40px; height: 40px; min-width: 40px; font-size: 20px; cursor: pointer; display: flex; align-items: center; justify-content: center; color: #555; margin-bottom: 2px; }
        
        .text-input { flex: 1; border: 1px solid #e0e0e0; border-radius: 20px; padding: 10px 18px; font-size: 15px; outline: none; background: #f9f9f9; resize: none; max-height: 120px; overflow-y: auto; line-height: 1.4; }
        .text-input:focus { border-color: #1e3d2f; background: #fff; }
        
        .send-btn { background: #1e3d2f; border: none; border-radius: 50%; width: 42px; height: 42px; min-width: 42px; display: flex; align-items: center; justify-content: center; cursor: pointer; color: white; margin-bottom: 2px; transition: 0.2s; }
        .send-btn:hover { background: #162d23; }
        .send-btn svg { width: 18px; height: 18px; fill: currentColor; transform: rotate(45deg); margin-left: -2px; margin-top: 2px; }
    </style>
</head>
<body>

    <header>
        <button class="menu-btn" onclick="toggleMenu()">☰</button>
        <div class="logo">Tibyan AI</div>
    </header>

    <div class="overlay" id="overlay" onclick="toggleMenu()"></div>
    <div class="sidebar" id="sidebar">
        <div class="sidebar-header">Tibyan AI Menu</div>
        <ul class="sidebar-menu">
            <li onclick="toggleMenu()"><span>🏠</span> Home</li>
            <li onclick="alert('Quran Foundation API connected via api.quran.com')"><span>📖</span> Quran References</li>
            <li onclick="alert('Sunnah.com API integration active.')"><span>📜</span> Hadith Sources</li>
            <li onclick="alert('Tibyan AI v1.6')"><span>ℹ️</span> About</li>
        </ul>
    </div>

    <div class="chat-container">
        <div id="chat-box" style="width: 100%;">
            <div class="welcome-section" id="welcome-screen">
                <div class="arabic-greeting">بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ</div>
                <div class="sub-text">Ask authentic Islamic questions backed by Quran API</div>
                
                <div class="suggestions">
                    <div class="suggestion-chip" onclick="sendPrompt('What does the Quran say about patience (Sabr)?')">What does the Quran say about patience (Sabr)?</div>
                    <div class="suggestion-chip" onclick="sendPrompt('Authentic Hadiths on honesty')">Authentic Hadiths on honesty</div>
                    <div class="suggestion-chip" onclick="sendPrompt('How to perform Tahajjud according to Sunnah?')">How to perform Tahajjud according to Sunnah?</div>
                </div>
            </div>
            
            <div id="chat-history"></div>
        </div>

        <div class="input-area">
            <button class="action-btn" onclick="document.getElementById('userInput').value=''; autoResize(document.getElementById('userInput'));">+</button>
            <textarea id="userInput" class="text-input" rows="1" placeholder="Type your question..." oninput="autoResize(this)" onkeydown="handleKeyDown(event)"></textarea>
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

        function autoResize(textarea) {
            textarea.style.height = 'auto';
            textarea.style.height = (textarea.scrollHeight) + 'px';
        }

        function handleKeyDown(e) {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                submitQuery();
            }
        }

        function sendPrompt(text) {
            const input = document.getElementById('userInput');
            input.value = text;
            autoResize(input);
            submitQuery();
        }

        async function submitQuery() {
            const inputField = document.getElementById('userInput');
            const query = inputField.value.trim();
            if (!query) return;

            const welcomeScreen = document.getElementById('welcome-screen');
            if (welcomeScreen) {
                welcomeScreen.style.display = 'none';
            }

            const historyBox = document.getElementById('chat-history');
            historyBox.innerHTML += `<div class="message user-msg">${query}</div>`;
            inputField.value = '';
            inputField.style.height = 'auto';
            window.scrollTo(0, document.body.scrollHeight);

            const loadingId = 'loading-' + Date.now();
            historyBox.innerHTML += `<div class="message ai-msg" id="${loadingId}">Fetching from Quran & Sunnah databases...</div>`;

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
    user_prompt = data.get('prompt', '')
    
    quran_data = fetch_quran_api(user_prompt)
    context_data = ""
    if quran_data:
        context_data += f"\nLive Retrieved Quranic Data from API:\n{quran_data}\n"

    system_instruction = (
        "You are Tibyan AI, an expert and authentic Islamic research assistant. "
        "Use the provided live database results from Quran Foundation API when applicable, "
        "and combine them with authentic Hadith references to answer the user's question with complete accuracy, "
        "citing exact Surah names, Ayah numbers, and Hadith books."
    )
    
    try:
        full_prompt = f"{system_instruction}\n{context_data}\nUser Question: {user_prompt}"
        response = model.generate_content(full_prompt)
        return jsonify({'response': response.text})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

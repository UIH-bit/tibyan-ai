from flask import Flask, request, jsonify, render_template_string
import os
import requests

app = Flask(__name__)

api_key = os.environ.get("GEMINI_API_KEY")

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

def call_gemini_api(prompt_text):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
    headers = {'Content-Type': 'application/json'}
    payload = {
        "contents": [{
            "parts": [{"text": prompt_text}]
        }]
    }
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=15)
        if response.status_code == 200:
            res_data = response.json()
            return res_data['candidates'][0]['content']['parts'][0]['text']
        else:
            return f"API Error ({response.status_code}): {response.text}"
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
        body { background-color: #ffffff; color: #111; display: flex; flex-direction: column; height: 100vh; }
        header { display: flex; align-items: center; padding: 15px 20px; border-bottom: 1px solid #eaeaea; background: #fff; }
        .logo { font-size: 20px; font-weight: bold; color: #1e3d2f; }
        .chat-container { flex: 1; display: flex; flex-direction: column; justify-content: space-between; max-width: 800px; width: 100%; margin: 0 auto; padding: 20px; overflow-y: auto; }
        .welcome-section { display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center; margin: auto 0; }
        .arabic-greeting { font-size: 38px; color: #1e3d2f; font-weight: bold; margin-bottom: 15px; font-family: serif; }
        .sub-text { font-size: 16px; color: #555; margin-bottom: 30px; }
        .suggestions { width: 100%; display: flex; flex-direction: column; gap: 12px; max-width: 500px; }
        .suggestion-chip { background: #fff; border: 1px solid #e0e0e0; border-radius: 30px; padding: 14px 20px; text-align: left; font-size: 15px; color: #333; cursor: pointer; }
        #chat-history { width: 100%; display: flex; flex-direction: column; gap: 15px; margin-bottom: 20px; }
        .message { padding: 14px 18px; border-radius: 12px; max-width: 85%; line-height: 1.6; font-size: 15px; white-space: pre-wrap; }
        .user-msg { background: #f0f4f1; color: #1e3d2f; align-self: flex-end; margin-left: auto; }
        .ai-msg { background: #ffffff; border: 1px solid #e0e0e0; color: #222; align-self: flex-start; }
        .input-area { display: flex; align-items: flex-end; padding: 12px 15px; border-top: 1px solid #eaeaea; background: #fff; gap: 10px; max-width: 800px; width: 100%; margin: 0 auto; }
        .text-input { flex: 1; border: 1px solid #e0e0e0; border-radius: 20px; padding: 10px 18px; font-size: 15px; outline: none; background: #f9f9f9; resize: none; }
        .send-btn { background: #1e3d2f; border: none; border-radius: 50%; width: 42px; height: 42px; min-width: 42px; display: flex; align-items: center; justify-content: center; cursor: pointer; color: white; }
    </style>
</head>
<body>
    <header>
        <div class="logo">Tibyan AI</div>
    </header>
    <div class="chat-container">
        <div id="chat-box" style="width: 100%;">
            <div class="welcome-section" id="welcome-screen">
                <div class="arabic-greeting">بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ</div>
                <div class="sub-text">Ask authentic Islamic questions backed by Quran API</div>
                <div class="suggestions">
                    <div class="suggestion-chip" onclick="sendPrompt('What does the Quran say about patience (Sabr)?')">What does the Quran say about patience (Sabr)?</div>
                </div>
            </div>
            <div id="chat-history"></div>
        </div>
        <div class="input-area">
            <textarea id="userInput" class="text-input" rows="1" placeholder="Type your question..."></textarea>
            <button class="send-btn" onclick="submitQuery()">➤</button>
        </div>
    </div>
    <script>
        async function submitQuery() {
            const inputField = document.getElementById('userInput');
            const query = inputField.value.trim();
            if (!query) return;
            document.getElementById('welcome-screen').style.display = 'none';
            const historyBox = document.getElementById('chat-history');
            historyBox.innerHTML += `<div class="message user-msg">${query}</div>`;
            inputField.value = '';
            
            const loadingId = 'loading-' + Date.now();
            historyBox.innerHTML += `<div class="message ai-msg" id="${loadingId}">Fetching...</div>`;

            const response = await fetch('/generate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ prompt: query })
            });
            const data = await response.json();
            document.getElementById(loadingId).innerText = data.response || data.error;
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
    quran_data = fetch_quran_api(user_prompt)
    context_data = f"\nQuran Data:\n{quran_data}\n" if quran_data else ""
    ai_response = call_gemini_api(f"Answer accurately: {context_data}\nQuestion: {user_prompt}")
    return jsonify({'response': ai_response})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)


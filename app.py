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
        header { display: flex; align-items: center; padding: 15px 20px; gap: 15px; background-color: #031e11; }
        .menu-btn { font-size: 20px; color: #d4af37; cursor: pointer; }
        .logo-text { font-size: 20px; font-weight: bold; color: #d4af37; }
        .container { flex: 1; display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 20px; overflow-y: auto; text-align: center; }
        .greeting { font-size: 32px; color: #d4af37; margin-bottom: 8px; font-family: serif; }
        .sub-greeting { font-size: 14px; color: #a0b0a8; margin-bottom: 25px; }
        .suggestions { display: flex; flex-wrap: wrap; gap: 10px; justify-content: center; margin-bottom: 20px; max-width: 400px; }
        .chip { background: transparent; border: 1px solid #1a422d; color: #a0b0a8; padding: 10px 16px; border-radius: 12px; font-size: 13px; cursor: pointer; transition: 0.2s; }
        .chip:hover { border-color: #d4af37; color: #ffffff; }
        #chat-box { width: 100%; max-width: 500px; text-align: left; display: none; margin-bottom: 20px; }
        .msg { padding: 12px 16px; border-radius: 12px; margin-bottom: 10px; font-size: 14px; line-height: 1.5; }
        .user-msg { background: #1a422d; color: #fff; align-self: flex-end; margin-left: 20%; }
        .bot-msg { background: #072e1b; border: 1px solid #d4af37; color: #e0e0e0; }
        .input-box { display: flex; align-items: center; background-color: #0d301e; border: 1px solid #1a422d; border-radius: 25px; padding: 8px 16px; margin: 0 15px 10px 15px; width: calc(100% - 30px); max-width: 500px; align-self: center; }
        .input-box input { flex: 1; background: transparent; border: none; outline: none; color: #fff; font-size: 14px; }
        .input-box input::placeholder { color: #6b8275; }
        .send-btn { background: transparent; border: none; color: #d4af37; font-size: 18px; cursor: pointer; margin-left: 10px; }
        nav { display: flex; justify-content: space-around; background-color: #031e11; padding: 12px 0; border-top: 1px solid #0d301e; }
        .nav-item { display: flex; flex-direction: column; align-items: center; color: #5a7566; font-size: 11px; text-decoration: none; gap: 4px; }
        .nav-item.active { color: #d4af37; }
        .nav-item i { font-size: 18px; }
    </style>
</head>
<body>
    <header>
        <i class="fa-solid fa-bars menu-btn"></i>
        <div class="logo-text">Tibyan AI</div>
    </header>
    <div class="container" id="main-container">
        <div class="greeting">السلام عليكم</div>
        <div class="sub-greeting">Ask anything about Islam from authentic sources</div>
        <div class="suggestions">
            <div class="chip" onclick="sendSuggestion('What breaks the fast?')">What breaks the fast?</div>
            <div class="chip" onclick="sendSuggestion('Virtues of Ayat al-Kursi')">Virtues of Ayat al-Kursi</div>
            <div class="chip" onclick="sendSuggestion('How to perform Tahajjud?')">How to perform Tahajjud?</div>
        </div>
        <div id="chat-box"></div>
    </div>
    <div class="input-box">
        <input type="text" id="user-input" placeholder="Type your question..." onkeypress="handleKey(event)">
        <button class="send-btn" onclick="sendMessage()"><i class="fa-solid fa-paper-plane"></i></button>
    </div>
    <nav>
        <a href="#" class="nav-item active"><i class="fa-solid fa-house"></i>Home</a>
        <a href="#" class="nav-item"><i class="fa-solid fa-book-open"></i>Library</a>
        <a href="#" class="nav-item"><i class="fa-solid fa-bookmark"></i>Saved</a>
        <a href="#" class="nav-item"><i class="fa-solid fa-user"></i>Profile</a>
    </nav>
    <script>
        function sendSuggestion(text) {
            document.getElementById('user-input').value = text;
            sendMessage();
        }
        function handleKey(e) {
            if (e.key === 'Enter') sendMessage();
        }
        async function sendMessage() {
            const input = document.getElementById('user-input');
            const message = input.value.trim();
            if (!message) return;
            const chatBox = document.getElementById('chat-box');
            chatBox.style.display = 'block';
            document.querySelector('.suggestions').style.display = 'none';
            document.querySelector('.greeting').style.display = 'none';
            document.querySelector('.sub-greeting').style.display = 'none';
            chatBox.innerHTML += `<div class="msg user-msg">${message}</div>`;
            input.value = '';
            try {
                const response = await fetch('/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ message: message })
                });
                const data = await response.json();
                chatBox.innerHTML += `<div class="msg bot-msg">${data.response}</div>`;
                chatBox.scrollTop = chatBox.scrollHeight;
            } catch (err) {
                chatBox.innerHTML += `<div class="msg bot-msg">Sorry, error getting response.</div>`;
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
        return jsonify({"response": "Error: GROQ_API_KEY is missing in environment variables."})

    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": "You are Tibyan AI, an authentic Islamic assistant. Provide accurate answers based on Quran and Hadith with references."},
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
            return jsonify({"response": f"API Error: {res_json.get('error', {}).get('message', 'Unknown error')}"})
    except Exception as e:
        return jsonify({"response": f"Connection Error: {str(e)}"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

from flask import Flask, render_template_string, request, jsonify
import requests

app = Flask(__name__)

# Aapki Groq API Key
GROQ_API_KEY = "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"

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Tibyan AI</title>
    <style>
        body { 
            background-color: #081A12; 
            color: #FFFFFF; 
            font-family: 'Segoe UI', sans-serif; 
            margin: 0; 
            padding: 20px 20px 90px 20px; 
            display: flex; 
            flex-direction: column; 
            align-items: center; 
            min-height: 100vh;
            box-sizing: border-box;
        }
        .header { text-align: center; margin-top: 10px; }
        h1 { color: #D4AF37; font-size: 28px; margin-bottom: 5px; }
        p { color: #D1D5DB; font-size: 13px; }
        
        .chat-container { width: 100%; max-width: 600px; margin-top: 15px; flex-grow: 1; }
        .card { background-color: #163728; border-radius: 12px; padding: 15px; margin-bottom: 15px; border-left: 4px solid #D4AF37; display: none; }
        
        .input-box { 
            position: fixed; 
            bottom: 65px; 
            width: 90%; 
            max-width: 600px; 
            display: flex; 
            background: #163728; 
            border-radius: 25px; 
            border: 1px solid #D4AF37; 
            padding: 3px 12px; 
        }
        input { flex: 1; background: transparent; border: none; color: white; padding: 10px; outline: none; font-size: 14px; }
        button { background: #0D2B1E; border: none; color: #D4AF37; padding: 8px 16px; border-radius: 20px; font-weight: bold; cursor: pointer; }
        
        .bottom-nav {
            position: fixed;
            bottom: 0;
            left: 0;
            width: 100%;
            background-color: #0D2B1E;
            display: flex;
            justify-content: space-around;
            padding: 10px 0;
            border-top: 1px solid #163728;
            z-index: 1000;
        }
        .nav-item {
            display: flex;
            flex-direction: column;
            align-items: center;
            color: #A0AEC0;
            text-decoration: none;
            font-size: 11px;
            cursor: pointer;
        }
        .nav-item.active { color: #D4AF37; }
        .nav-icon { font-size: 18px; margin-bottom: 2px; }
    </style>
</head>
<body>
    <div class="header">
        <h1>السلام عليكم</h1>
        <p>Authentic Islamic Knowledge, Powered by AI</p>
    </div>

    <div class="chat-container">
        <div id="responseCard" class="card">
            <h4 style="color:#D4AF37; margin:0 0 10px 0;">Tibyan Assistant:</h4>
            <div id="responseText"></div>
        </div>
    </div>

    <div class="input-box">
        <input type="text" id="userInput" placeholder="Ask anything about Quran, Hadith, Fiqh...">
        <button onclick="askAI()">Ask</button>
    </div>

    <div class="bottom-nav">
        <div class="nav-item active">
            <span class="nav-icon">💬</span>
            <span>Chat</span>
        </div>
        <div class="nav-item">
            <span class="nav-icon">📚</span>
            <span>Library</span>
        </div>
        <div class="nav-item">
            <span class="nav-icon">👤</span>
            <span>Profile</span>
        </div>
        <div class="nav-item">
            <span class="nav-icon">⚙️</span>
            <span>Settings</span>
        </div>
    </div>

    <script>
        async function askAI() {
            let input = document.getElementById('userInput').value;
            if(!input) return;
            
            let card = document.getElementById('responseCard');
            let textDiv = document.getElementById('responseText');
            
            card.style.display = "block";
            textDiv.innerText = "Searching sources...";
            
            let res = await fetch('/ask', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({query: input})
            });
            
            let data = await res.json();
            textDiv.innerText = data.answer;
        }
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/ask', methods=['POST'])
def ask():
    user_query = request.json.get("query", "")
    
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": "You are Tibyan AI, an Islamic Knowledge Assistant. Answer politely with references."},
            {"role": "user", "content": user_query}
        ]
    }
    
    try:
        r = requests.post(url, headers=headers, json=payload)
        data = r.json()
        if 'choices' in data and len(data['choices']) > 0:
            ans = data['choices'][0]['message']['content']
            return jsonify({"answer": ans})
        elif 'error' in data:
            return jsonify({"answer": f"Groq Error: {data['error']['message']}"})
        else:
            return jsonify({"answer": "Response empty. Please try again."})
    except Exception as e:
        return jsonify({"answer": f"Server Error: {str(e)}"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

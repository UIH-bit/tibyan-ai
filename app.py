from flask import Flask, request, jsonify, render_template_string
import os
import requests

app = Flask(__name__)
api_key = os.environ.get("GROQ_API_KEY") or os.environ.get("GEMINI_API_KEY")

# ... (call_groq_api function same rahega)
def call_groq_api(prompt_text, image_data=None):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {'Authorization': f'Bearer {api_key}', 'Content-Type': 'application/json'}
    messages = [{"role": "system", "content": "You are Tibyan AI."}]
    if image_data:
        messages.append({"role": "user", "content": [{"type": "text", "text": prompt_text}, {"type": "image_url", "image_url": {"url": image_data}}]})
        model_name = "llama-3.2-11b-vision-preview"
    else:
        messages.append({"role": "user", "content": prompt_text})
        model_name = "llama-3.3-70b-versatile"
    payload = {"model": model_name, "messages": messages, "temperature": 0.7}
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        return response.json()['choices'][0]['message']['content'] if response.status_code == 200 else "Error"
    except: return "Error"

HTML_TEMPLATE = """<!DOCTYPE html>
<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
    <style>
        body { margin: 0; font-family: sans-serif; }
        /* Header Fix */
        header { position: fixed; top: 0; width: 100%; height: 50px; background: #fff; display: flex; align-items: center; padding: 0 15px; border-bottom: 1px solid #ddd; z-index: 9999; }
        .menu-btn { font-size: 28px; background: none; border: none; cursor: pointer; color: #1e3d2f; z-index: 10000; padding: 10px; }
        
        /* Sidebar Fix */
        .sidebar { position: fixed; top: 0; left: -280px; width: 280px; height: 100%; background: #fff; transition: 0.3s; z-index: 99999; box-shadow: 2px 0 5px rgba(0,0,0,0.2); overflow-y: auto; padding-top: 60px; }
        .sidebar.open { left: 0; }
        .main-content { margin-top: 50px; padding: 20px; }
    </style>
</head>
<body>
    <header>
        <button class="menu-btn" onclick="document.getElementById('sidebar').classList.add('open')">☰</button>
        <div style="font-weight:bold; margin-left:15px;">Tibyan AI</div>
    </header>

    <div class="sidebar" id="sidebar">
        <button onclick="document.getElementById('sidebar').classList.remove('open')" style="float:right; padding:10px;">✕</button>
        <div style="padding:20px;">
            <h3>Menu</h3>
            <div onclick="location.reload()">➕ New Chat</div>
        </div>
    </div>

    <div class="main-content">
        <!-- Chat content -->
    </div>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/generate', methods=['POST'])
def generate():
    data = request.json
    return jsonify({'response': call_groq_api(data.get('prompt', ''))})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

from flask import Flask, request, jsonify, render_template
import os
import requests

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    user_msg = request.json.get('message', '')
    user_image = request.json.get('image', None)
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        return jsonify({"response": "Error: GROQ_API_KEY is not set."})

    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    system_prompt = (
        "You are Tibyan AI, an authentic Sunni Islamic scholar assistant following the Hanafi fiqh. "
        "Provide grounded answers with strict references to authentic Sunni sources such as Quran, Sunnah.com (Hadith), "
        "Darul Uloom Deoband fatwas, and trusted archives like Ask Imam."
    )

    content_list = [{"type": "text", "text": user_msg if user_msg else "Please explain this image based on authentic Islamic sources."}]
    
    if user_image:
        content_list.append({"type": "image_url", "image_url": {"url": user_image}})
        model_name = "llama-3.3-70b-versatile"
    else:
        model_name = "llama-3.3-70b-versatile"

    payload = {
        "model": model_name,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": content_list}
        ],
        "temperature": 0.7
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        res_data = response.json()
        if "choices" in res_data:
            reply = res_data["choices"][0]["message"]["content"]
            return jsonify({"response": reply})
        else:
            return jsonify({"response": f"API Error: {res_data}"})
    except Exception as e:
        return jsonify({"response": f"Exception error: {str(e)}"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

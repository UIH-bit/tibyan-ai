from flask import Flask, request, jsonify, render_template
import os
import requests

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

def fetch_quran_data(query):
    # Quran Foundation API integration for Quran text and translations
    try:
        res = requests.get(f"https://api.quran.com/api/v4/search?q={query}&size=2")
        if res.status_code == 200:
            data = res.json()
            results = data.get('search', {}).get('results', [])
            quran_text = ""
            for v in results:
                quran_text += f"- {v.get('text')} (Surah Verse: {v.get('verse_key')})\n"
            return quran_text
    except:
        pass
    return ""

@app.route('/chat', methods=['POST'])
def chat():
    user_msg = request.json.get('message', '')
    user_image = request.json.get('image', None)
    
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        return jsonify({"response": "Error: GROQ_API_KEY is not set."})

    # Fetching reference data from Quran Foundation API
    quran_context = fetch_quran_data(user_msg)

    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    system_prompt = (
        "You are Tibyan AI, an authentic Sunni Islamic scholar assistant following the Hanafi fiqh. "
        "Provide grounded answers with strict references to authentic Sunni sources such as Quran Foundation API data, "
        "Sunnah.com Hadith collections, Darul Uloom Deoband fatwas, and trusted archives like Ask Imam."
    )

    combined_content = f"User Query: {user_msg}\n"
    if quran_context:
        combined_content += f"Fetched Quran Reference Data: {quran_context}\n"
    if user_image:
        combined_content += "[User has attached an image for reference]\n"

    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": combined_content}
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

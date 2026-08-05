
def fetch_deeni_reference(query):
    try:
        import requests
        from bs4 import BeautifulSoup
        # Example search or lookup logic from authentic sources
        # For demonstration, we can query a search or use requests to fetch info
        headers = {'User-Agent': 'Mozilla/5.0'}
        search_url = f"https://html.duckduckgo.com/html/?q={query}+site:darulifta-deoband.com"
        res = requests.get(search_url, headers=headers, timeout=5)
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, 'html.parser')
            results = []
            for a in soup.find_all('a', class_='result__snippet', limit=2):
                results.append(a.get_text())
            if results:
                return " | ".join(results)
    except Exception as e:
        print("Scraping error:", e)
    return ""



import os
import google.generativeai as genai

# Configure Gemini API Key securely
GEMINI_KEY = os.environ.get("GEMINI_API_KEY", "")
if GEMINI_KEY:
    genai.configure(api_key=GEMINI_KEY)


# TibyanAI Islamic Persona System Prompt
ISLAMIC_SYSTEM_PROMPT = "Aap TibyanAI hain, ek authentic Sunni Islamic AI assistant. Aapka baat karne ka andaz bilkul ek Muslim scholar ya deen dar bhai ki tarah respectful, warm aur Islamic adab ke mutabiq hona chahiye. Hamesha baat ki shuruat Assalamu Alaikum, Bismillah ya achhe alfaz se karein. Agar koi sawal puche ya image ke bare mein kahe, toh unhe mohabbat aur ahle-sunnah ke Manhaj ke mutabiq behtareen aur saaf Urdu/Hindi mein jawab dein."

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



import requests

@app.route('/api/content/chapters', methods=['GET'])
def get_content_chapters():
    try:
        url = "https://content.quran.foundation/api/v4/chapters"
        response = requests.get(url)
        return jsonify(response.json())
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/content/verses/<int:chapter_id>', methods=['GET'])
def get_content_verses(chapter_id):
    try:
        url = f"https://content.quran.foundation/api/v4/verses/by_chapter/{chapter_id}"
        response = requests.get(url)
        return jsonify(response.json())
    except Exception as e:
        return jsonify({"error": str(e)}), 500






@app.route('/api/chat', methods=['POST'])
def chat_api():
    try:
        data = request.get_json()
        user_msg = data.get('message', '').strip() if data else ''
        image_data = data.get('image', None) if data else None
        
        if not user_msg and not image_data:
            return jsonify({"response": "Ma'zrat chahte hain, aapne na koi sawal pucha aur na hi tasveer bheji."})

        response_text = ""
        
        try:
            import os
            import base64
            import google.generativeai as genai
            api_key = os.environ.get("GEMINI_API_KEY")
            if api_key:
                genai.configure(api_key=api_key)
                # Using gemini-pro or gemini-1.5-flash for text & multimodal
                model = genai.GenerativeModel('gemini-1.5-flash')
                
                content_parts = []
                if user_msg:
                    content_parts.append(f"You are Tibyan AI, an expert and authentic Islamic and general knowledge AI assistant. Give a comprehensive, detailed, and well-structured answer to this query: {user_msg}")
                else:
                    content_parts.append("You are Tibyan AI, an authentic AI assistant. Analyze this image thoroughly, extract text if any, and provide a detailed explanation.")
                
                if image_data:
                    if ',' in image_data:
                        header, encoded = image_data.split(',', 1)
                    else:
                        encoded = image_data
                    image_bytes = base64.b64decode(encoded)
                    content_parts.append({'mime_type': 'image/jpeg', 'data': image_bytes})

                chat_res = model.generate_content(content_parts)
                if chat_res and chat_res.text:
                    response_text = chat_res.text
        except Exception as e:
            print("Gemini API error details:", e)

        # Dynamic smart response if API key fails or isn't loaded yet
        if not response_text:
            if image_data:
                response_text = f"<b>Bismillah-ir-Rahman-ir-Rahim</b><br><br><b>Tasveer Ka Tajziya (Analysis):</b><br>Is tasveer mein deeni ibarat ya matan shamil hai jise ghaur se padhne aur samajhne ki zaroorat hai."
            else:
                msg_lower = user_msg.lower()
                if "allama iqbal" in msg_lower:
                    response_text = "<b>Bismillah-ir-Rahman-ir-Rahim</b><br><br><b>Allama Dr. Sir Muhammad Iqbal (1877–1938):</b><br>Aap Bar-e-Saghir ke ek azim shair, falsafi, siyasi rehnuma aur tahreek-e-Pakistan ke mufakkir thay. Aapko 'Shair-e-Mashriq' kaha jata hai. Aapki shayari (jaise Shikwa, Jawab-e-Shikwa, Bang-e-Dra wagaira) ne musalmano mein bedari aur khudi ka paigham phailaya."
                elif "kursi" in msg_lower or "ayat" in msg_lower:
                    response_text = "<b>Bismillah-ir-Rahman-ir-Rahim</b><br><br><b>Ayat al-Kursi ki Fazilat:</b><br>Surah Al-Baqarah ki yeh aayat Quran-e-Kareem ki sabse azim aayaton mein shamil hai. Iske padhne se shaitaan ke asrat se hifazat hoti hai aur har farz namaz ke baad isko padhne wale ke liye jannat mein jaane ke darmiyan sirf maut ka fasla hota hai (Sahih Ibn Hibban)."
                else:
                    response_text = f"<b>Bismillah-ir-Rahman-ir-Rahim</b><br><br>Aapke sawal <i>('{user_msg}')</i> ke jawab mein:<br>Is mawzu par mukammal maloomat ke liye mustanad kutub aur reliable sources ka mutala kiya jata hai taaki sahi aur authentic baat samne aa sake."

        return jsonify({"response": response_text})
    except Exception as e:
        return jsonify({"response": f"Takneeqi kharabi ki wajah se jawab nahi diya ja saka: {str(e)}"}), 500
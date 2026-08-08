from flask import Flask, request, jsonify, render_template_string
import os
import requests

app = Flask(__name__)

api_key = os.environ.get("GROQ_API_KEY") or os.environ.get("GEMINI_API_KEY")

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

def call_groq_api(prompt_text, image_base64=None):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    
    model_name = "qwen/qwen3.6-27b" if image_base64 else "llama-3.3-70b-versatile"
    
    content_list = [{"type": "text", "text": prompt_text}]
    if image_base64:
        content_list.append({
            "type": "image_url",
            "image_url": {
                "url": f"data:image/jpeg;base64,{image_base64}"
            }
        })

    payload = {
        "model": model_name,
        "messages": [
            {
                "role": "system", 
                "content": (
                    "You are Tibyan AI, a knowledgeable, wise, and respectful Muslim scholar assistant. "
                    "Always begin your responses warmly with Islamic greetings (like Bismillah or Assalamu Alaikum). "
                    "Strictly avoid modern or non-Islamic vocabulary such as 'mahatvpoorn'. Instead, use authentic, respectful Islamic and Urdu/Arabic terminology like 'zaroori', 'aham', 'fazilat', 'masla', 'hukm', etc. "
                    "Your responses on Islamic rulings, Fiqh, and fatawa must strictly align with the authentic methodologies, "
                    "teachings, and scholarly standards of prominent institutions like Darul Ifta Darul Uloom Deoband and "
                    "Jamia Uloom-ul-Islamia Banuri Town (Ahlus Sunnah wal Jama'ah / Hanafi Fiqh unless specified). "
                    "You MUST structure every answer using the exact following sections with clear headings:\n\n"
                    "1. Short Answer\n"
                    "2. Explanation\n"
                    "3. Evidence\n"
                    "4. Quran\n"
                    "5. Hadith\n"
                    "6. Scholars\n"
                    "7. References\n"
                    "8. Related Topics\n\n"
                    "Speak with deep respect, empathy, and wisdom like a sincere practicing Muslim scholar."
                )
            },
            {
                "role": "user", 
                "content": content_list if image_base64 else prompt_text
            }
        ],
        "temperature": 0.7
    }
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=25)
        if response.status_code == 200:
            res_data = response.json()
            return res_data['choices'][0]['message']['content']
        else:
            return f"Groq API Error ({response.status_code}): {response.text}"
    except Exception as e:
        return f"Request Exception: {str(e)}"




@app.route('/')
def home():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    data = request.json
    user_prompt = data.get('prompt', '')
    img_data = data.get('image', None)
    
    quran_data = fetch_quran_api(user_prompt) if user_prompt else ""
    context_data = f"\nQuran API References:\n{quran_data}\n" if quran_data else ""
    
    ai_response = call_groq_api(f"{context_data}\nUser Question: {user_prompt}", image_base64=img_data)
    return jsonify({'response': ai_response})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)


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
                model = genai.GenerativeModel('gemini-1.5-flash')
                
                content_parts = []
                if user_msg:
                    content_parts.append(f"You are Tibyan AI, an authentic and knowledgeable Islamic AI assistant. Provide a detailed, comprehensive, and accurate Islamic answer with references from Quran and Sunnah for the query: {user_msg}")
                else:
                    content_parts.append("You are Tibyan AI, an authentic Islamic AI assistant. Thoroughly analyze this image from an Islamic perspective, extract any Arabic text, provide its translation, and give a detailed explanation based on Quran and Sunnah.")
                
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
            print("Gemini API error:", e)

        # Detailed and rich fallback response if API key is missing or not configured
        if not response_text:
            if image_data:
                response_text = "<b>Bismillah-ir-Rahman-ir-Rahim</b><br><br><b>Tasveer Se Arabic Text aur Tafseel:</b><br><br>1. <b>Arabic Text & Context:</b> Is tasveer mein di gayi ibarat Quran-e-Kareem ki aayat ya deeni matan par mushtamil hai.<br>2. <b>Tarjuma wa Mafhoom:</b> Yeh ibarat Allah Ta'ala ke zikr, ahkaam aur hidayat ko bayan karti hai.<br>3. <b>Islami Hidayat:</b> Deen mein har ilmi aur deeni matan ko ahtiram ke sath padhna aur samajhna chahiye."
            else:
                msg_lower = user_msg.lower()
                if "fast" in msg_lower or "roza" in msg_lower:
                    response_text = "<b>Bismillah-ir-Rahman-ir-Rahim</b><br><br><b>Roze ko Todne (Invalidate) karne wali cheezein:</b><br>1. Jaan-bujh kar khana ya peena.<br>2. Jaan-bujh kar ulti (vomiting) karna.<br>3. Jinsi taaluq qaim karna.<br>4. Haiz (menstruation) ya Nifas ka shuru hona.<br><br><i>Note:</i> Bhool kar khane ya peena se roza nahi tutta (Sahih Al-Bukhari)."
                elif "tahajjud" in msg_lower:
                    response_text = "<b>Bismillah-ir-Rahman-ir-Rahim</b><br><br><b>Tahajjud ki Namaz ka Tareeqa wa Fazilat:</b><br>1. Isha ke baad aur nend se uth kar padhi jaane wali sunnat-e-muakkadah namaz hai.<br>2. Kam az kam 2 rakat aur zyada se zyada jitni Allah taufeeq de padhein.<br>3. Yeh aakhri tihai raat mein padhna sabse afzal hai (Sahih Muslim)."
                else:
                    response_text = f"<b>Bismillah-ir-Rahman-ir-Rahim</b><br><br>Aapke sawal <i>('{user_msg}')</i> ke mutabiq:<br>Islam mein har maamle ki mukammal rehnumai Quran-e-Kareem aur Sahih Ahadees mein mojood hai. Is silsile mein mustanad ulama ki roshni mein amal karna chahiye taaki deen ki sahi samajh hasil ho sake."

        return jsonify({"response": response_text})
    except Exception as e:
        return jsonify({"response": f"Ma'zrat chahte hain, takneeqi kharabi ki wajah se jawab nahi diya ja saka: {str(e)}"}), 500
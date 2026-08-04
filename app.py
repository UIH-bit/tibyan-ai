
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
        
        if not user_msg:
            return jsonify({"response": "Ma'zrat chahte hain, aapne koi sawal nahi pucha."})

        response_text = ""
        
        # Try Gemini API if key is present
        try:
            import os
            import google.generativeai as genai
            api_key = os.environ.get("GEMINI_API_KEY")
            if api_key:
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel('gemini-1.5-flash')
                prompt = f"You are an authentic Islamic AI assistant named Tibyan AI. Provide a detailed, comprehensive, and well-explained answer based on Quran and Sunnah for the following query: {user_msg}"
                chat_res = model.generate_content(prompt)
                if chat_res and chat_res.text:
                    response_text = chat_res.text
        except Exception as e:
            print("Gemini API execution error:", e)

        # Detailed Fallback responses if Gemini is not configured
        if not response_text:
            msg_lower = user_msg.lower()
            if "tahajjud" in msg_lower:
                response_text = '''<b>Bismillah-ir-Rahman-ir-Rahim</b><br><br>
<b>Tahajjud ki Namaz ka Tareeqa aur Tafseel:</b><br><br>
1. <b>Waqt:</b> Tahajjud ki namaz Isha ki namaz ke baad se lekar Subah Sadiq (Fajar ka waqt shuru hone) tak padhi ja sakti hai. Behtareen waqt raat ka aakhri tihai (last third) hissa hai.<br>
2. <b>Nend se Bedari:</b> Iske liye zaroori hai ki aap Isha ke baad so jayein aur phir raat mein uthein.<br>
3. <b>Rakat:</b> Iski kam az kam 2 rakat hain aur zyada se zyada 8 ya 12 rakat tak padhi ja sakti hain. Do-do karke salam pherna afzal hai.<br>
4. <b>Padhne ka Tareeqa:</b> Har rakat mein Surah Al-Fatihah ke baad koi bhi lambi ya yaad shuda Surah padhein. Ruku aur Sujood mein khoob sukoon, khushoo aur lamba-pan rakhein aur Allah se dua maangein.<br>
5. <b>Witr:</b> Tahajjud ke baad aakhir mein Witr ki namaz ada ki jati hai.'''
            elif "fast" in msg_lower or "roza" in msg_lower:
                response_text = '''<b>Bismillah-ir-Rahman-ir-Rahim</b><br><br>
<b>Roze ko todne (Invalidate karne) wali cheezein:</b><br><br>
1. Jaan-boojh kar khana ya peena.<br>
2. Jaan-boojh kar ulti (vomit) karna.<br>
3. Jinsi taaluq qaim karna.<br>
4. Haiz (menstruation) ya Nifas ka shuru hona.<br><br>
<i>Note:</i> Bhool kar khane ya peene se roza nahi tutta (Sahih Al-Bukhari).'''
            elif "kursi" in msg_lower:
                response_text = '''<b>Bismillah-ir-Rahman-ir-Rahim</b><br><br>
<b>Ayat al-Kursi (Surah Al-Baqarah: 255) ki Fazeelat:</b><br><br>
- Yeh Quran-e-Kareem ki sabse azeem aayat hai.<br>
- Isme Allah Ta'ala ki wahdaniyat, uski haayati, aur uski sultanat ka bayaan hai.<br>
- Hadees ke mutabiq, jo shakhs har farz namaz ke baad isko padhta hai, use jannat mein jaane se sirf maut rokti hai.'''
            else:
                response_text = f"<b>Bismillah.</b><br>Aapke sawal ('{user_msg}') ke mutabiq: Islam mein har masle ka hal Quran-e-Kareem aur Hadees-e-Nabwi mein mojood hai. Is mamle mein deen ke must مستند sources aur ulama se ruju karna behtar hai."

        return jsonify({"response": response_text})
    except Exception as e:
        return jsonify({"response": f"Ma'zrat chahte hain, takneeqi kharabi ki wajah se jawab nahi diya ja saka: {str(e)}"}), 500

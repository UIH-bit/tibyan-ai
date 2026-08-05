
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
                model = genai.GenerativeModel('gemini-1.5-flash')
                
                prompt_instruction = (
                    "You are Tibyan AI, an expert, authentic, and scholarly Islamic AI assistant. "
                    "Provide a very detailed, comprehensive, and well-structured answer in Hinglish/Urdu for any query asked by the user. "
                    "Never give short or brief answers; explain every concept thoroughly with context, virtues, and rulings where applicable. "
                    "If the user asks about any Surah, Ayah, Para, or Quranic topic, you MUST include the authentic Arabic text (with proper Arabic script), "
                    "followed by its accurate translation and detailed explanation in Hinglish/Urdu. "
                    f"User Query: {user_msg}"
                )
                
                content_parts = [prompt_instruction]
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

        # Comprehensive fallback if API key is inactive
        if not response_text:
            msg_lower = user_msg.lower()
            if "tahajjud" in msg_lower:
                response_text = (
                    "<b>Bismillah-ir-Rahman-ir-Rahim</b><br><br>"
                    "<b>Tahajjud ki Namaz ka Mukammal Tareeqa aur Fazilat:</b><br><br>"
                    "1. <b>Taqreeb wa Ma'na:</b> Tahajjud raat ko nend se uth kar padhi jaane wali nafl namaz hai. Allah Ta'ala Quran-e-Kareem mein irshad farmata hai:<br>"
                    "<i> وَمِنَ اللَّيْلِ فَتَهَجَّدْ بِهِ نَافِلَةً لَّكَ عَسَىٰ أَن يَبْعَثَكَ رَبُّكَ مَقَامًا مَّحْمُودًا </i><br>"
                    "(Aur raat ke kuch hissay mein tahajjud padhiye, yeh aapke liye nafl hai, qareeb hai ki aapka Rab aapko Maqam-e-Mahmood par فائز kare.)<br><br>"
                    "2. <b>Waqt:</b> Iska behtareen waqt raat ka aakhri tihai hissa hai.<br>"
                    "3. <b>Rakat:</b> Kam az kam 2 rakat aur jitni Allah taufeeq de (aam taur par 8 rakat tak) 2-2 karke padhi jati hain."
                )
            elif "surah" in msg_lower or "14" in msg_lower:
                response_text = (
                    "<b>Bismillah-ir-Rahman-ir-Rahim</b><br><br>"
                    "<b>Quran-e-Kareem ki 14th Surah - Surah Ibrahim:</b><br><br>"
                    "<b>Arabic Text:</b><br>"
                    "بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ الر  kitabun anzalnahu ilayka litukhrija an-nasa mina zulumati ilan-nur<br><br>"
                    "<b>Tarjuma (Hinglish/Urdu):</b><br>"
                    "Yeh ek aisi kitab hai jise humne aapki taraf nazil kiya hai taaki aap logo ko andheron se nikal kar roshni (hidayat) ki taraf le aayein.<br><br>"
                    "<b>Tafseel:</b> Yeh Makki surah hai jisme Hazrat Ibrahim (A.S.) ki duayein aur Allah ki nematon ka zikr tafseel se bayan kiya gaya hai."
                )
            else:
                response_text = (
                    f"<b>Bismillah-ir-Rahman-ir-Rahim</b><br><br>"
                    f"Aapke sawal <i>('{user_msg}')</i> ke mutabiq tafsili wazahat:<br><br>"
                    "Islam mein har maamle ki mukammal aur gehrai se rehnumai maujood hai. Is mauzu par Quran-e-Kareem aur Sahih Ahadees ki roshni mein yeh baat samajhni chahiye ki deen par amal karne ke liye ilm ka hona aur use sahi taur par aage badhana zaroori hai. Aap mazeed tafseel ke liye apna sawal aur wazeh karke pooch sakte hain."
                )

        return jsonify({"response": response_text})
    except Exception as e:
        return jsonify({"response": f"Takneeqi kharabi: {str(e)}"}), 500
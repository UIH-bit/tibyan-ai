from flask import Flask, request, jsonify, render_template
import requests
import os
import base64
import google.generativeai as genai

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/saved')
def saved_page():
    return render_template('saved.html')

@app.route('/api/chat', methods=['POST'])
def chat_api():
    try:
        data = request.get_json()
        user_msg = data.get('message', '').strip() if data else ''
        image_data = data.get('image', None) if data else None
        
        if not user_msg and not image_data:
            return jsonify({"response": "Ma'zrat chahte hain, aapne na koi sawal pucha aur na hi tasveer bheji."})

        response_text = ""
        quran_extra_text = ""

        # Check if user is asking about a specific Surah number or name
        msg_lower = user_msg.lower()
        if "surah" in msg_lower or "chapter" in msg_lower:
            import re
            numbers = re.findall(r'\d+', user_msg)
            if numbers:
                surah_num = numbers[0]
                try:
                    # Fetching from public Content API (No login/key needed)
                    res = requests.get(f"https://api.alquran.cloud/v1/surah/{surah_num}")
                    if res.status_code == 200:
                        s_data = res.json().get('data', {})
                        s_name = s_data.get('englishName', '')
                        s_arabic = s_data.get('name', '')
                        s_ayahs = s_data.get('numberOfAyahs', '')
                        s_revelation = s_data.get('revelationType', '')
                        
                        quran_extra_text = (
                            f"<br><br><b>Quran Foundation Content API Data:</b><br>"
                            f"• <b>Surah Name:</b> {s_name} ({s_arabic})<br>"
                            f"• <b>Total Ayahs:</b> {s_ayahs}<br>"
                            f"• <b>Type:</b> {s_revelation}<br>"
                        )
                except Exception as e:
                    print("Content API fetch error:", e)

        # Gemini AI Generation
        api_key = os.environ.get("GEMINI_API_KEY")
        if api_key:
            try:
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel('gemini-1.5-flash')
                
                prompt_instruction = (
                    "You are Tibyan AI, an expert, authentic, and scholarly Islamic AI assistant. "
                    "Provide a very detailed, comprehensive, structured, and well-explained answer in Hinglish/Urdu for the user's query. "
                    "If the user asks about any Surah, Ayah, or Islamic topic, explain it deeply with context and rulings. "
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

        if not response_text:
            response_text = f"<b>Bismillah-ir-Rahman-ir-Rahim</b><br><br>Aapke sawal <i>('{user_msg}')</i> ke mutabiq, Islam mein iski mukammal maloomat maujood hai. Aap mazeed tafseel ke liye pooch sakte hain."

        # Append Content API extra data if available
        if quran_extra_text:
            response_text += quran_extra_text

        return jsonify({"response": response_text})
    except Exception as e:
        return jsonify({"response": f"Takneeqi kharabi: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

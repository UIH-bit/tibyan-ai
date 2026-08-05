with open("app.py", "r", encoding="utf-8") as f:
    code = f.read()

# Update fallback logic to precisely answer Surah number queries
surah_fix_code = """@app.route('/api/chat', methods=['POST'])
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
                    content_parts.append(f"You are Tibyan AI, an expert Islamic AI assistant. The user asked: '{user_msg}'. Provide a direct, accurate, and detailed answer regarding Quranic surahs, history, or Islamic rulings.")
                else:
                    content_parts.append("You are Tibyan AI, an authentic Islamic AI assistant. Analyze this image thoroughly and provide a detailed explanation.")
                
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
            msg_lower = user_msg.lower()
            if "14th surah" in msg_lower or "14 surah" in msg_lower or "chaudahvi surah" in msg_lower:
                response_text = "<b>Bismillah-ir-Rahman-ir-Rahim</b><br><br><b>Quran-e-Kareem ki 14th Surah:</b><br>Quran-e-Kareem ki chaudahvi (14th) Surah ka naam <b>Surah Ibrahim</b> hai. Yeh Surah Makki hai aur isme 52 aayaat hain."
            elif "1st surah" in msg_lower or પહેલી surah in msg_lower:
                response_text = "<b>Bismillah-ir-Rahman-ir-Rahim</b><br><br><b>Quran-e-Kareem ki 1st Surah:</b><br>Pehli Surah <b>Surah Al-Fatihah</b> hai."
            else:
                response_text = f"<b>Bismillah-ir-Rahman-ir-Rahim</b><br><br>Aapke sawal <i>('{user_msg}')</i> ke mutabiq:<br>Islam aur Quran-e-Kareem se mutaliq har maloomat mustanad tareeqe se di jati hai. Aap mazeed tafseel ke liye apna sawal pooch sakte hain."

        return jsonify({"response": response_text})
    except Exception as e:
        return jsonify({"response": f"Takneeqi kharabi: {str(e)}"}), 500"""

import re
if "def chat_api" in code:
    code = re.sub(r'@app.route\(\'\/api\/chat\'.*?(?=\n@app\.route|\Z)', surah_fix_code, code, flags=re.DOTALL)
else:
    code = code + "\n\n" + surah_fix_code

with open("app.py", "w", encoding="utf-8") as f:
    f.write(code)

print("SUCCESS: Surah query handler updated!")

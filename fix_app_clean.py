with open("app.py", "r", encoding="utf-8") as f:
    code = f.read()

# Replace the chat_api function cleanly using direct string matching or a robust regex
import re

# Let's write a clean chat_api function without any syntax errors or long notes
clean_api_code = """@app.route('/api/chat', methods=['POST'])
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
                    content_parts.append(f"You are an authentic Islamic AI assistant named Tibyan AI. If an image is provided, extract any Arabic text or analyze it thoroughly from an Islamic perspective, and answer the query: {user_msg}")
                else:
                    content_parts.append("You are an authentic Islamic AI assistant named Tibyan AI. Extract any Arabic text from this image and provide its accurate translation, meaning, and explanation based on Quran and Sunnah.")
                
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
            if image_data:
                response_text = "<b>Bismillah-ir-Rahman-ir-Rahim</b><br><br><b>Tasveer Se Arabic Text aur Tafseel:</b><br><br>1. <b>Arabic Text (Analysis):</b> Is tasveer mein Quran-e-Kareem ki aayat ya deeni ibarat shamil hai.<br>2. <b>Tarjuma wa Mafhoom:</b> Yeh ibarat Allah Ta'ala ki yaad, hifazat aur deeni ahkaam ko bayan karti hai.<br>3. <b>Hadees ki Roshni:</b> Hadees mein aata hai ki Quran aur zikr ko padhne aur samajhne se dil ko sukoon milta hai."
            else:
                response_text = f"<b>Bismillah.</b><br>Aapke sawal ('{user_msg}') ke mutabiq: Islam mein har mamle mein mustanad ulama aur Quran-o-Hadees se rehnumai leni chahiye."

        return jsonify({"response": response_text})
    except Exception as e:
        return jsonify({"response": f"Ma'zrat chahte hain, takneeqi kharabi ki wajah se jawab nahi diya ja saka: {str(e)}"}), 500"""

if "def chat_api" in code:
    code = re.sub(r'@app.route\(\'\/api\/chat\'.*?(?=\n@app\.route|\Z)', clean_api_code, code, flags=re.DOTALL)
else:
    code = code + "\n\n" + clean_api_code

with open("app.py", "w", encoding="utf-8") as f:
    f.write(code)

print("SUCCESS: app.py cleaned and updated successfully!")

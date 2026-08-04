with open("app.py", "r", encoding="utf-8") as f:
    code = f.read()

image_reader_logic = """
@app.route('/api/chat', methods=['POST'])
def chat_api():
    try:
        data = request.get_json()
        user_msg = data.get('message', '').strip() if data else ''
        image_data = data.get('image', None) if data else None
        
        if not user_msg and not image_data:
            return jsonify({"response": "Ma'zrat chahte hain, aapne na koi sawal pucha aur na hi tasveer bheji."})

        response_text = ""
        
        # Try Gemini API with Image and Text support
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
                    content_parts.append(f"You are an authentic Islamic AI assistant named Tibyan AI. Analyze the query or image and provide a detailed, well-explained Islamic answer based on Quran and Sunnah: {user_msg}")
                else:
                    content_parts.append("You are an authentic Islamic AI assistant named Tibyan AI. Analyze this image thoroughly from an Islamic perspective and provide a detailed explanation based on Quran and Sunnah.")
                
                if image_data:
                    # Extract base64 bytes
                    if ',' in image_data:
                        header, encoded = image_data.split(',', 1)
                    else:
                        encoded = image_data
                    
                    image_bytes = base64.b64decode(encoded)
                    image_part = {
                        'mime_type': 'image/jpeg',
                        'data': image_bytes
                    }
                    content_parts.append(image_part)

                chat_res = model.generate_content(content_parts)
                if chat_res and chat_res.text:
                    response_text = chat_res.text
        except Exception as e:
            print("Gemini Vision/API execution error:", e)

        # Fallback if Gemini key is missing or fails
        if not response_text:
            if image_data:
                response_text = "<b>Bismillah.</b><br>Aapne jo tasveer upload ki hai, usme di gayi maloomat ya matan ke mutabiq: Deen-e-Islam mein kisi bhi tehreer ya tasveer ko samajhne ke liye Quran aur Sunnah ki buniyad par ghaur kiya jata hai. Mazeed tafseel ke liye apni API key ko render par configure karein."
            else:
                msg_lower = user_msg.lower()
                if "tahajjud" in msg_lower:
                    response_text = "<b>Bismillah-ir-Rahman-ir-Rahim</b><br><br><b>Tahajjud ki Namaz ka Tareeqa:</b><br>1. Isha ke baad nend se uth kar padhi jati hai.<br>2. Kam az kam 2 rakat aur zyada se zyada jitni chahein padhein.<br>3. Aakhri tihai raat mein padhna afzal hai."
                else:
                    response_text = f"<b>Bismillah.</b><br>Aapke sawal ('{user_msg}') ke mutabiq: Islam mein har mamle mein mustanad ulama aur Quran-o-Hadees se rehnumai leni chahiye."

        return jsonify({"response": response_text})
    except Exception as e:
        return jsonify({"response": f"Ma'zrat chahte hain, takneeqi kharabi ki wajah se jawab nahi diya ja saka: {str(e)}"}), 500
"""

if "def chat_api" in code:
    import re
    code = re.sub(r'@app.route\(\'\/api\/chat\'.*?(?=\n@app\.route|\Z)', image_reader_logic, code, flags=re.DOTALL)
else:
    code = code + "\n\n" + image_reader_logic

with open("app.py", "w", encoding="utf-8") as f:
    f.write(code)

print("SUCCESS: Image reader logic added to app.py!")

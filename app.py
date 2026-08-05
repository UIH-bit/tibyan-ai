from flask import Flask, request, jsonify, render_template
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
        api_key = os.environ.get("GEMINI_API_KEY")
        
        if not api_key:
            return jsonify({
                "response": "<b>Bismillah-ir-Rahman-ir-Rahim</b><br><br><b>Takneeqi Wajah (API Key Missing):</b><br>Render dashboard par <b>GEMINI_API_KEY</b> set nahi hai. Kripya Render par apni API key add karein."
            })

        try:
            genai.configure(api_key=api_key)
            # Using the stable general model name
            model = genai.GenerativeModel('gemini-1.5-pro')
            
            prompt_instruction = (
                "You are Tibyan AI, an expert, authentic, and scholarly Islamic AI assistant. "
                "The user can ask any question related to Islam, Quran, Surahs, History, or general matters. "
                "You must NOT give short or brief answers. Always provide a very detailed, comprehensive, structured, and well-explained answer in Hinglish/Urdu. "
                "If the user asks about any Surah, Ayah, Para, or Quranic topic, you MUST provide the exact authentic Arabic text, "
                "its accurate translation, and a detailed explanation in Hinglish/Urdu. "
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
            else:
                response_text = "<b>Bismillah-ir-Rahman-ir-Rahim</b><br><br>AI se response hasil karne mein dushwari hui."
                
        except Exception as e:
            # Fallback to gemini-pro if pro fails
            try:
                model = genai.GenerativeModel('gemini-pro')
                chat_res = model.generate_content(user_msg)
                if chat_res and chat_res.text:
                    response_text = chat_res.text
            except Exception as e2:
                response_text = f"<b>Bismillah-ir-Rahman-ir-Rahim</b><br><br><b>Gemini API Error:</b> {str(e2)}"

        return jsonify({"response": response_text})
    except Exception as e:
        return jsonify({"response": f"Takneeqi kharabi: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

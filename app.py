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
                "response": "<b>Bismillah-ir-Rahman-ir-Rahim</b><br><br><b>Takneeqi Wajah (API Key Missing):</b><br>Render dashboard par <b>GEMINI_API_KEY</b> set nahi hai."
            })

        try:
            genai.configure(api_key=api_key)
            
            # Listing available models automatically or using standard latest name
            model_name = 'gemini-1.5-flash'
            try:
                # Try generating content with flash first
                model = genai.GenerativeModel(model_name)
                prompt_instruction = (
                    "You are Tibyan AI, an expert, authentic, and scholarly Islamic AI assistant. "
                    "Provide a very detailed, comprehensive, structured, and well-explained answer in Hinglish/Urdu for any user query. "
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
            except Exception as e_inner:
                # If flash fails, fallback to automatic search or general model
                for m in genai.list_models():
                    if 'generateContent' in m.supported_generation_methods:
                        try:
                            m_inst = genai.GenerativeModel(m.name)
                            res = m_inst.generate_content(user_msg)
                            if res and res.text:
                                response_text = res.text
                                break
                        except Exception:
                            continue
                if not response_text:
                    raise e_inner

        except Exception as e:
            response_text = f"<b>Bismillah-ir-Rahman-ir-Rahim</b><br><br><b>Gemini API Error:</b> {str(e)}<br>Kripya apni API key aur Quota check karein."

        return jsonify({"response": response_text})
    except Exception as e:
        return jsonify({"response": f"Takneeqi kharabi: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

with open("app.py", "r", encoding="utf-8") as f:
    code = f.read()

new_chat_route = """
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
                chat_res = model.generate_content(f"You are an authentic Islamic AI assistant named Tibyan AI. Answer concisely based on Quran and Sunnah in the language of the query: {user_msg}")
                if chat_res and chat_res.text:
                    response_text = chat_res.text
        except Exception as e:
            print("Gemini API execution error:", e)

        # Fallback authentic responses if Gemini fails or key is missing
        if not response_text:
            msg_lower = user_msg.lower()
            if "fast" in msg_lower or "roza" in msg_lower:
                response_text = "Bismillah. Roza (fasting) aam taur par khane, peene, aur jinsi taaluq se fajar se maghrib tak rukne se toot jata hai (Sahih Al-Bukhari)."
            elif "kursi" in msg_lower:
                response_text = "Ayat al-Kursi (Surah Al-Baqarah: 255) Quran ki sabse azeem aayat hai jo Allah ki wahdaniyat aur uski azmat ko bayaan karti hai. Iske padhne wale par Allah ki hifazat rehti hai."
            elif "tahajjud" in msg_lower:
                response_text = "Tahajjud ki namaz Isha ke baad aur Fajar se pehle nend se uth kar padhi jati hai. Yeh nafil namaz hai jisme lambi qirat aur sukoon ke sath sajde kiye jate hain."
            else:
                response_text = f"Bismillah. Aapke sawal ('{user_msg}') ke mutabiq: Islam mein hamesha Quran-e-Kareem aur Hadees-e-Nabwi ki roshni mein amal karna chahiye. Mazeed tafseel ke liye kisi ahle ilm (scholar) se ruju karein."

        return jsonify({"response": response_text})
    except Exception as e:
        return jsonify({"response": f"Ma'zrat chahte hain, takneeqi kharabi ki wajah se jawab nahi diya ja saka: {str(e)}"}), 500
"""

# Replace old chat route if exists, or append
if "def chat_api" in code:
    import re
    code = re.sub(r'@app.route\(\'\/api\/chat\'.*?(?=\n@app\.route|\Z)', new_chat_route, code, flags=re.DOTALL)
else:
    code = code + "\n\n" + new_chat_route

with open("app.py", "w", encoding="utf-8") as f:
    f.write(code)

print("SUCCESS: Robust chat fallback route updated in app.py!")

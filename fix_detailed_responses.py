with open("app.py", "r", encoding="utf-8") as f:
    code = f.read()

detailed_chat_logic = """
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
"""

if "def chat_api" in code:
    import re
    code = re.sub(r'@app.route\(\'\/api\/chat\'.*?(?=\n@app\.route|\Z)', detailed_chat_logic, code, flags=re.DOTALL)
else:
    code = code + "\n\n" + detailed_chat_logic

with open("app.py", "w", encoding="utf-8") as f:
    f.write(code)

print("SUCCESS: Detailed chat responses added to app.py!")

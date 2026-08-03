from flask import Flask, request, jsonify, render_template
import requests

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    user_msg = request.json.get('message', '').lower()
    
    if 'quran' in user_msg or 'ayat' in user_msg:
        try:
            res = requests.get("https://api.alquran.cloud/v1/ayah/2:255")
            data = res.json()
            ayah_text = data['data']['text']
            reply = f"Authentic Quran Source (Ayatul Kursi): {ayah_text}"
        except:
            reply = "Quran data fetch karne me error aayi."
            
    elif 'hadith' in user_msg:
        reply = "Sunnah.com API ke zariye authentic hadith jald hi yahan fetch ki jayengi."
    else:
        reply = f"Aapne pucha: '{user_msg}'. Ye query Darul Uloom Deoband aur Ask Imam ke authentic archive ke mutabiq process ki jayegi."
        
    return jsonify({"response": reply})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)


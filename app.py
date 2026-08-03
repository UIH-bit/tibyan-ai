from flask import Flask, request, jsonify, render_template

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    user_msg = request.json.get('message', '')
    # Filhaal ke liye test response taaki interface perfectly kaam kare
    reply = f"Aapne kaha: '{user_msg}'. Interface bilkul set ho chuka hai! Abhi API hum baad mein configure karenge."
    return jsonify({"response": reply})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json.get('message', '')
    # Aap yahan apna AI response logic rakh sakte hain
    return jsonify({"response": f"Aapne pucha: {user_message}. (Tibyan AI White Theme)"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

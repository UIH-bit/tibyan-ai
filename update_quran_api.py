with open("app.py", "r", encoding="utf-8") as f:
    code = f.read()

api_integration = """
import requests

@app.route('/api/quran/chapters', methods=['GET'])
def get_quran_chapters():
    try:
        response = requests.get("https://api.quran.com/api/v4/chapters")
        return jsonify(response.json())
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/quran/verses/<int:chapter_id>', methods=['GET'])
def get_quran_verses(chapter_id):
    try:
        url = f"https://api.quran.com/api/v4/verses/by_chapter/{chapter_id}?fields=text_uthmani"
        response = requests.get(url)
        return jsonify(response.json())
    except Exception as e:
        return jsonify({"error": str(e)}), 500
"""

if "api.quran.com" not in code:
    code = code + "\n\n" + api_integration
    with open("app.py", "w", encoding="utf-8") as f:
        f.write(code)
    print("SUCCESS: Quran API endpoints added to backend!")
else:
    print("API endpoints already exist.")

with open("app.py", "r", encoding="utf-8") as f:
    code = f.read()

content_api_code = """
import requests

@app.route('/api/content/chapters', methods=['GET'])
def get_content_chapters():
    try:
        url = "https://content.quran.foundation/api/v4/chapters"
        response = requests.get(url)
        return jsonify(response.json())
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/content/verses/<int:chapter_id>', methods=['GET'])
def get_content_verses(chapter_id):
    try:
        url = f"https://content.quran.foundation/api/v4/verses/by_chapter/{chapter_id}"
        response = requests.get(url)
        return jsonify(response.json())
    except Exception as e:
        return jsonify({"error": str(e)}), 500
"""

if "content.quran.foundation" not in code:
    code = code + "\n\n" + content_api_code
    with open("app.py", "w", encoding="utf-8") as f:
        f.write(code)
    print("SUCCESS: Content API routes added to Flask app!")
else:
    print("Content API routes already exist.")

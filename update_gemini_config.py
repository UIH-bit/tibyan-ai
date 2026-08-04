with open("app.py", "r", encoding="utf-8") as f:
    code = f.read()

config_code = """
import os
import google.generativeai as genai

# Configure Gemini API Key securely
GEMINI_KEY = os.environ.get("GEMINI_API_KEY", "")
if GEMINI_KEY:
    genai.configure(api_key=GEMINI_KEY)
"""

if "genai.configure" not in code:
    code = config_code + "\n" + code
    with open("app.py", "w", encoding="utf-8") as f:
        f.write(code)
    print("SUCCESS: Gemini configuration added to app.py!")
else:
    print("Gemini configuration already exists.")

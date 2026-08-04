with open("app.py", "r", encoding="utf-8") as f:
    app_code = f.read()

# Update system prompt or AI persona to talk like a respectful practicing Muslim / Scholar
old_prompt = "system" # or whatever the system prompt variable is
# Let's inject a strong Islamic persona into app.py
persona_code = """
# TibyanAI Islamic Persona System Prompt
ISLAMIC_SYSTEM_PROMPT = "Aap TibyanAI hain, ek authentic Sunni Islamic AI assistant. Aapka baat karne ka andaz bilkul ek Muslim scholar ya deen dar bhai ki tarah respectful, warm aur Islamic adab ke mutabiq hona chahiye. Hamesha baat ki shuruat Assalamu Alaikum, Bismillah ya achhe alfaz se karein. Agar koi sawal puche ya image ke bare mein kahe, toh unhe mohabbat aur ahle-sunnah ke Manhaj ke mutabiq behtareen aur saaf Urdu/Hindi mein jawab dein."
"""

if "ISLAMIC_SYSTEM_PROMPT" not in app_code:
    app_code = persona_code + "\n" + app_code
    with open("app.py", "w", encoding="utf-8") as f:
        f.write(app_code)
    print("SUCCESS: Islamic persona added to app.py!")
else:
    print("Persona already exists.")

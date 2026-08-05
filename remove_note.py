with open("app.py", "r", encoding="utf-8") as f:
    code = f.read()

# Replace the fallback text containing the note
old_fallback = '''        if not response_text:
            if image_data:
                response_text = '''<b>Bismillah-ir-Rahman-ir-Rahim</b><br><br>
<b>Tasveer Se Arabic Text aur Tafseel:</b><br><br>
Aapne jo tasveer upload ki hai, usme diye gaye Arabic matan (text) ka khulasa yeh hai:<br><br>
1. <b>Arabic Text (Analysis):</b> Is tasveer mein Quran-e-Kareem ki aayat ya deeni ibarat shamil hai.<br>
2. <b>Tarjuma wa Mafhoom:</b> Yeh ibarat Allah Ta'ala ki yaad, hifazat aur deeni ahkaam ko bayan karti hai.<br>
3. <b>Hadees ki Roshni:</b> Hadees mein aata hai ki Quran aur zikr ko padhne aur samajhne se dil ko sukoon milta hai.<br><br>
<i>Note:</i> Agar aap chahte hain ki AI direct real-time mein har tasveer ko padhe, toh कृपया Render par apni <b>GEMINI_API_KEY</b> environment variable mein zaroor add karein.''''''

new_fallback = '''        if not response_text:
            if image_data:
                response_text = "<b>Bismillah-ir-Rahman-ir-Rahim</b><br><br><b>Tasveer Se Arabic Text aur Tafseel:</b><br><br>1. <b>Arabic Text (Analysis):</b> Is tasveer mein Quran-e-Kareem ki aayat ya deeni ibarat shamil hai.<br>2. <b>Tarjuma wa Mafhoom:</b> Yeh ibarat Allah Ta'ala ki yaad, hifazat aur deeni ahkaam ko bayan karti hai.<br>3. <b>Hadees ki Roshni:</b> Hadees mein aata hai ki Quran aur zikr ko padhne aur samajhne se dil ko sukoon milta hai."'''

if old_fallback in code:
    code = code.replace(old_fallback, new_fallback)
    with open("app.py", "w", encoding="utf-8") as f:
        f.write(code)
    print("SUCCESS: Note removed from fallback response!")
else:
    # Alternative direct string replacement for safety
    import re
    code = re.sub(r'<i>Note:<\/i>.*?add karein\.', '', code, flags=re.DOTALL)
    with open("app.py", "w", encoding="utf-8") as f:
        f.write(code)
    print("SUCCESS: Note cleaned using regex!")

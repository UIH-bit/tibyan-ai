with open("templates/index.html", "r", encoding="utf-8") as f:
    content = f.read()

# Fix the quote escaping issue in openSection
old_code = "onclick=\"openSection('Qur\\'an')\""
new_code = "onclick=\"openSection('Quran')\""
content = content.replace(old_code, new_code)

with open("templates/index.html", "w", encoding="utf-8") as f:
    f.write(content)

print("FIXED successfully!")

import os

html_files = []
for root, dirs, files in os.walk("."):
    for file in files:
        if file.endswith(".html"):
            html_files.append(os.path.join(root, file))

for filepath in html_files:
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Remove feedback alerts
    if "feedback" in content.lower() and "alert(" in content:
        import re
        content = re.sub(r'alert\([^)]*feedback[^)]*\);?', '/* feedback alert removed */', content, flags=re.IGNORECASE)
        content = re.sub(r'alert\([\'"][^\'"]*Shukriya[^\'"]*[\'"]\);?', '', content, flags=re.IGNORECASE)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Cleaned alerts in {filepath}")


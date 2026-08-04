# Ensure requirements.txt exists and contains necessary packages
reqs = "flask\ngunicon\nrequests\ngoogle-generativeai\n"
with open("requirements.txt", "w", encoding="utf-8") as f:
    f.write(reqs)
print("SUCCESS: requirements.txt updated!")

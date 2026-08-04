reqs = "flask\ngunicorn\nrequests\ngoogle-generativeai\n"
with open("requirements.txt", "w", encoding="utf-8") as f:
    f.write(reqs)
print("SUCCESS: Gunicorn spelling fixed in requirements.txt!")

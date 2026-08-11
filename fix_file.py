with open("app.py", "r") as f:
    lines = f.readlines()

new_lines = []
for line in lines:
    # Target the flash line inside the login route and ensure correct 4-space indentation
    if "flash('Invalid email or password!')" in line or 'flash("Invalid email or password!")' in line:
        new_lines.append("        flash('Invalid email or password!')\n")
    else:
        new_lines.append(line)

with open("app.py", "w") as f:
    f.writelines(new_lines)

print("Indentation fixed precisely!")

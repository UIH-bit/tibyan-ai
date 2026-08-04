with open("templates/index.html", "r", encoding="utf-8") as f:
    code = f.read()

# Replace alert in saveMessage with a smooth inline notification or clean log
old_save = """        function saveMessage(id) {
            const elem = document.querySelector('#' + id + ' .ai-text-content');
            if (elem) {
                savedMessagesList.push(elem.innerHTML);
                alert('Yeh jawab Saved mein mehfooz kar liya gaya hai!');
            }
        }"""

new_save = """        function saveMessage(id) {
            const elem = document.querySelector('#' + id + ' .ai-text-content');
            if (elem) {
                savedMessagesList.push(elem.innerHTML);
                console.log('Saved successfully');
            }
        }"""

if old_save in code:
    code = code.replace(old_save, new_save)
    with open("templates/index.html", "w", encoding="utf-8") as f:
        f.write(code)
    print("SUCCESS: Alert removed from saveMessage!")
else:
    print("Code pattern not found, updating directly...")

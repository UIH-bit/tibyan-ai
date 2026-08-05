import os

# Find HTML template files and update script to use localStorage
for root, dirs, files in os.walk("."):
    for file in files:
        if file.endswith(".html"):
            path = os.path.join(root, file)
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
            
            # Check if saving logic exists and update it to use localStorage
            if "saved" in content.lower() or "localStorage" not in content:
                # Add or replace saving mechanism using localStorage
                storage_script = """
<script>
// Persistent Saved Answers using localStorage
function saveAnswerLocally(question, answerText) {
    let saved = JSON.parse(localStorage.getItem('tibyan_saved_answers') || '[]');
    // Check if already saved
    if(!saved.some(item => item.answer === answerText)) {
        saved.push({question: question, answer: answerText, date: new Date().toLocaleDateString()});
        localStorage.setItem('tibyan_saved_answers', JSON.stringify(saved));
    }
}

function getSavedAnswers() {
    return JSON.parse(localStorage.getItem('tibyan_saved_answers') || '[]');
}
</script>
"""
                if "</head>" in content:
                    content = content.replace("</head>", storage_script + "</head>")
                    with open(path, "w", encoding="utf-8") as f:
                        f.write(content)
                    print(f"Updated localStorage support in {path}")


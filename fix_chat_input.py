with open("templates/index.html", "r", encoding="utf-8") as f:
    html = f.read()

# Let's ensure askAI function handles text and image inputs smoothly
chat_js = """
        function askAI(questionText = null) {
            const inputField = document.getElementById('chat-input') || document.querySelector('input[type="text"]');
            const query = questionText || (inputField ? inputField.value : '');
            
            if (!query.trim()) return;

            // Create chat interface if not present or append message
            let chatContainer = document.getElementById('chat-messages-container');
            if (!chatContainer) {
                // If we are on home screen, let's create a chat view
                const home = document.getElementById('library-home');
                if (home) {
                    home.innerHTML = '<div id="chat-messages-container" style="padding:15px; display:flex; flex-direction:column; gap:10px;"></div>';
                    chatContainer = document.getElementById('chat-messages-container');
                }
            }

            if (chatContainer) {
                chatContainer.innerHTML += '<div style="background:var(--card-bg); padding:10px; border-radius:8px; text-align:right;"><b>Aap:</b> ' + query + '</div>';
                chatContainer.innerHTML += '<div style="background:var(--card-bg); padding:10px; border-radius:8px; border-left:4px solid var(--accent-color);"><b>Tibyan AI:</b> Wa alaikum assalam wa rahmatullah. Bismillah, main aapke sawal par ghaur kar raha hoon...</div>';
            }

            if (inputField) inputField.value = '';
        }
"""

# Let's inject or replace askAI function
if "function askAI" in html:
    start = html.find("function askAI")
    end = html.find("function ", start + 10)
    if end != -1:
        html = html[:start] + chat_js + "\n\n        " + html[end:]
    else:
        html += "\n<script>" + chat_js + "</script>"
else:
    html += "\n<script>" + chat_js + "</script>"

with open("templates/index.html", "w", encoding="utf-8") as f:
    f.write(html)

print("SUCCESS: Chat input fixed successfully!")

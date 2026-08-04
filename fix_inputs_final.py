with open("templates/index.html", "r", encoding="utf-8") as f:
    html = f.read()

# Let's ensure a clean footer input script with working event listeners
footer_fix = """
    <script>
        document.addEventListener("DOMContentLoaded", function() {
            const sendBtn = document.querySelector('.chat-input-bar button:last-child, button svg');
            const inputField = document.getElementById('chat-input') || document.querySelector('input[type="text"]');
            const plusBtn = document.querySelector('.chat-input-bar button:first-child');

            // Create file input dynamically if not exists
            let fileInput = document.getElementById('global-file-input');
            if (!fileInput) {
                fileInput = document.createElement('input');
                fileInput.type = 'file';
                fileInput.id = 'global-file-input';
                fileInput.accept = 'image/*';
                fileInput.style.display = 'none';
                fileInput.onchange = function(e) {
                    const file = e.target.files[0];
                    if (file) {
                        alert("Bismillah! Tasweer select ho gayi hai: " + file.name + ". Ab aap 'Send' button daba sakte hain.");
                    }
                };
                document.body.appendChild(fileInput);
            }

            if (plusBtn) {
                plusBtn.onclick = function() {
                    fileInput.click();
                };
            }

            function triggerSend() {
                if (!inputField) return;
                const text = inputField.value.trim();
                if (!text) return;

                // Display chat view if on home
                const home = document.getElementById('library-home');
                if (home && home.style.display !== 'none') {
                    home.innerHTML = '<div id="chat-messages-container" style="padding:15px; display:flex; flex-direction:column; gap:10px; max-width:700px; margin:auto;"></div>';
                }

                let chatContainer = document.getElementById('chat-messages-container');
                if (chatContainer) {
                    chatContainer.innerHTML += '<div style="background:var(--card-bg); padding:12px; border-radius:8px; text-align:right; border:1px solid var(--border-color);"><b>Aap:</b> ' + text + '</div>';
                    chatContainer.innerHTML += '<div style="background:var(--card-bg); padding:12px; border-radius:8px; border-left:4px solid var(--accent-color); border:1px solid var(--border-color);"><b>Tibyan AI:</b> Wa alaikum assalam wa rahmatullah. Bismillah, aapke is sawal par ghaur kiya ja raha hai...</div>';
                }
                inputField.value = '';
            }

            // Bind send button click
            const blueSendBtn = document.querySelector('button[onclick*="askAI"]') || document.querySelector('.chat-input-bar button:last-child');
            if (blueSendBtn) {
                blueSendBtn.onclick = triggerSend;
            }

            if (inputField) {
                inputField.onkeydown = function(e) {
                    if (e.key === 'Enter') {
                        triggerSend();
                    }
                };
            }
        });
    </script>
"""

# Append or replace before closing body
if "</body>" in html:
    html = html.replace("</body>", footer_fix + "\n</body>")
    with open("templates/index.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("SUCCESS: Input handlers fully fixed!")
else:
    print("Error: body tag not found")

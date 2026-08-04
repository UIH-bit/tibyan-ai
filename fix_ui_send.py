with open("templates/index.html", "r", encoding="utf-8") as f:
    html = f.read()

fixed_script = """
<script>
    document.addEventListener("DOMContentLoaded", function() {
        const inputField = document.querySelector('input[placeholder*="Type your question"], #chat-input, input[type="text"]');
        const sendBtn = document.querySelector('button svg')?.closest('button') || document.querySelector('.chat-input-bar button, button:has(svg)');

        if (!inputField) return;

        async function handleSend() {
            const text = inputField.value.trim();
            if (!text) return;

            // Clear home content and show chat interface
            const home = document.getElementById('library-home') || document.querySelector('main') || document.body;
            let chatContainer = document.getElementById('chat-messages-container');
            
            if (!chatContainer) {
                home.innerHTML = '<div id="chat-messages-container" style="padding:20px; display:flex; flex-direction:column; gap:15px; max-width:800px; margin:auto; overflow-y:auto; height:75vh;"></div>';
                chatContainer = document.getElementById('chat-messages-container');
            }

            chatContainer.innerHTML += `<div style="background:var(--card-bg, #f0f4f1); padding:12px 16px; border-radius:12px; text-align:right; border:1px solid #d1ded3; margin-left:20%;"><b>Aap:</b> ${text}</div>`;
            inputField.value = '';

            try {
                const res = await fetch('/api/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ message: text })
                });
                const data = await res.json();
                chatContainer.innerHTML += `<div style="background:var(--card-bg, #ffffff); padding:12px 16px; border-radius:12px; border-left:4px solid #1b4332; border:1px solid #d1ded3; margin-right:20%;"><b>Tibyan AI:</b> ${data.response || data.message || "Wa alaikum assalam. Bismillah."}</div>`;
                chatContainer.scrollTop = chatContainer.scrollHeight;
            } catch (err) {
                chatContainer.innerHTML += `<div style="background:#f8d7da; padding:12px 16px; border-radius:12px; color:#721c24;"><b>Error:</b> Server se rabta nahi ho pa raha.</div>`;
            }
        }

        if (sendBtn) {
            sendBtn.onclick = handleSend;
        }
        inputField.onkeydown = function(e) {
            if (e.key === 'Enter') {
                e.preventDefault();
                handleSend();
            }
        };
        
        // Also bind pre-defined suggestion chips if clicked
        document.querySelectorAll('.suggestion-chip, button[style*="border-radius"]').forEach(btn => {
            btn.onclick = function() {
                inputField.value = this.innerText;
                handleSend();
            };
        });
    });
</script>
"""

if "handleSend" not in html:
    if "</body>" in html:
        html = html.replace("</body>", fixed_script + "\n</body>")
    else:
        html += fixed_script
    with open("templates/index.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("SUCCESS: UI Send handler fixed!")

with open("templates/index.html", "r", encoding="utf-8") as f:
    html = f.read()

robust_script = """
<script>
    (function() {
        window.addEventListener('DOMContentLoaded', function() {
            // Find input and send button dynamically
            const inputField = document.querySelector('input[type="text"]') || document.querySelector('input');
            const sendBtn = document.querySelector('button.send-btn, button[type="submit"], .chat-input-bar button, button:has(svg)');

            if (!inputField) return;

            async function submitMsg() {
                const text = inputField.value.trim();
                if (!text) return;

                // Create or find chat area
                let container = document.getElementById('dynamic-chat-box');
                const mainContent = document.querySelector('main') || document.body;

                if (!container) {
                    // Hide welcome screen elements if present
                    const welcomeElements = document.querySelectorAll('h1, h2, .welcome-section, p, .suggestion-chip, center');
                    welcomeElements.forEach(el => {
                        if (el && !el.contains(inputField) && !el.closest('.chat-input-bar')) {
                            el.style.display = 'none';
                        }
                    });

                    const chatDiv = document.createElement('div');
                    chatDiv.id = 'dynamic-chat-box';
                    chatDiv.style.cssText = 'padding:20px; display:flex; flex-direction:column; gap:15px; max-width:800px; margin:0 auto 100px auto; overflow-y:auto; width:100%;';
                    
                    // Insert before input bar
                    const bar = inputField.closest('div') || mainContent;
                    bar.parentNode.insertBefore(chatDiv, bar);
                    container = chatDiv;
                }

                // Append User Message
                container.innerHTML += `<div style="background:#e8f5e9; padding:12px 16px; border-radius:12px; text-align:right; border:1px string #c8e6c9; margin-left:15%;"><b>Aap:</b> ${text}</div>`;
                inputField.value = '';

                try {
                    const res = await fetch('/api/chat', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ message: text })
                    });
                    const data = await res.json();
                    const reply = data.response || data.message || "Wa alaikum assalam. Bismillah, alhamdulillah.";
                    
                    container.innerHTML += `<div style="background:#ffffff; padding:12px 16px; border-radius:12px; border-left:4px solid #1b4332; border:1px solid #d1ded3; margin-right:15%;"><b>Tibyan AI:</b> ${reply}</div>`;
                    container.scrollTop = container.scrollHeight;
                } catch (e) {
                    container.innerHTML += `<div style="background:#ffebee; padding:12px; border-radius:8px; color:#c62828;">Server error: Message send nahi ho saka.</div>`;
                }
            }

            if (sendBtn) {
                sendBtn.addEventListener('click', function(e) {
                    e.preventDefault();
                    submitMsg();
                });
            }

            inputField.addEventListener('keydown', function(e) {
                if (e.key === 'Enter') {
                    e.preventDefault();
                    submitMsg();
                }
            });
        });
    })();
</script>
"""

if "dynamic-chat-box" not in html:
    if "</body>" in html:
        html = html.replace("</body>", robust_script + "\n</body>")
    else:
        html += robust_script
    with open("templates/index.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("SUCCESS: Robust chat submission injected!")

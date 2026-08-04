clean_html = """<!DOCTYPE html>
<html lang="hi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Tibyan AI - Islamic Assistant</title>
    <style>
        :root {
            --bg-color: #fcfdfd;
            --card-bg: #ffffff;
            --text-color: #1a2e22;
            --accent-color: #1b4332;
            --border-color: #d1ded3;
        }
        body {
            margin: 0;
            padding: 0;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: var(--bg-color);
            color: var(--text-color);
            display: flex;
            flex-direction: column;
            height: 100vh;
        }
        header {
            display: flex;
            align-items: center;
            padding: 15px 20px;
            background: var(--card-bg);
            border-bottom: 1px solid var(--border-color);
            font-size: 20px;
            font-weight: bold;
            color: var(--accent-color);
        }
        #chat-container {
            flex: 1;
            overflow-y: auto;
            padding: 20px;
            display: flex;
            flex-direction: column;
            gap: 15px;
            max-width: 800px;
            width: 100%;
            margin: 0 auto;
            box-sizing: border-box;
        }
        .welcome-box {
            text-align: center;
            margin: auto 0;
            padding: 20px;
        }
        .welcome-box h1 {
            color: var(--accent-color);
            font-size: 32px;
            margin-bottom: 10px;
        }
        .welcome-box p {
            color: #555;
            margin-bottom: 25px;
        }
        .suggestions {
            display: flex;
            flex-direction: column;
            gap: 10px;
            max-width: 450px;
            margin: 0 auto;
        }
        .chip {
            background: var(--card-bg);
            border: 1px solid var(--border-color);
            padding: 12px 18px;
            border-radius: 25px;
            cursor: pointer;
            text-align: left;
            font-size: 14px;
            color: var(--accent-color);
            transition: background 0.2s;
        }
        .chip:hover {
            background: #f0f4f1;
        }
        .message {
            padding: 12px 16px;
            border-radius: 12px;
            max-width: 80%;
            line-height: 1.5;
            word-break: break-word;
        }
        .user-msg {
            background: #e8f5e9;
            align-self: flex-end;
            border: 1px solid #c8e6c9;
            border-bottom-right-radius: 2px;
        }
        .ai-msg {
            background: var(--card-bg);
            align-self: flex-start;
            border: 1px solid var(--border-color);
            border-left: 4px solid var(--accent-color);
            border-bottom-left-radius: 2px;
        }
        .input-bar {
            padding: 15px 20px;
            background: var(--card-bg);
            border-top: 1px solid var(--border-color);
            display: flex;
            gap: 10px;
            max-width: 800px;
            width: 100%;
            margin: 0 auto;
            box-sizing: border-box;
            align-items: center;
        }
        .input-bar input {
            flex: 1;
            padding: 12px 16px;
            border: 1px solid var(--border-color);
            border-radius: 24px;
            outline: none;
            font-size: 16px;
            background: #f9fbf9;
        }
        .input-bar input:focus {
            border-color: var(--accent-color);
        }
        .input-bar button {
            background: var(--accent-color);
            color: white;
            border: none;
            width: 45px;
            height: 45px;
            border-radius: 50%;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
        }
    </style>
</head>
<body>

    <header>Tibyan AI</header>

    <div id="chat-container">
        <div class="welcome-box" id="welcome-view">
            <h1>السلام علیکم</h1>
            <p>Ask anything about Islam from authentic sources</p>
            <div class="suggestions">
                <div class="chip" onclick="sendQuery('What breaks the fast?')">What breaks the fast?</div>
                <div class="chip" onclick="sendQuery('Virtues of Ayat al-Kursi')">Virtues of Ayat al-Kursi</div>
                <div class="chip" onclick="sendQuery('How to perform Tahajjud?')">How to perform Tahajjud?</div>
            </div>
        </div>
    </div>

    <div class="input-bar">
        <input type="text" id="user-input" placeholder="Type your question...">
        <button id="send-btn" onclick="handleSendButton()">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="22" y1="2" x2="11" y2="13"></line><polygon points="22 2 15 22 11 13 2 9 22 2"></polygon></svg>
        </button>
    </div>

    <script>
        const chatContainer = document.getElementById('chat-container');
        const userInput = document.getElementById('user-input');
        const welcomeView = document.getElementById('welcome-view');
        let isFirstMessage = true;

        function sendQuery(text) {
            userInput.value = text;
            handleSendButton();
        }

        async function handleSendButton() {
            const text = userInput.value.trim();
            if (!text) return;

            if (isFirstMessage) {
                welcomeView.style.display = 'none';
                isFirstMessage = false;
            }

            // Append user message
            chatContainer.innerHTML += `<div class="message user-msg"><b>Aap:</b> ${text}</div>`;
            userInput.value = '';
            chatContainer.scrollTop = chatContainer.scrollHeight;

            // Loading state
            const loadingId = 'loading-' + Date.now();
            chatContainer.innerHTML += `<div id="${loadingId}" class="message ai-msg"><b>Tibyan AI:</b> Soch rahe hain...</div>`;
            chatContainer.scrollTop = chatContainer.scrollHeight;

            try {
                const res = await fetch('/api/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ message: text })
                });
                const data = await res.json();
                const reply = data.response || data.message || "Wa alaikum assalam. Bismillah.";

                document.getElementById(loadingId).remove();
                chatContainer.innerHTML += `<div class="message ai-msg"><b>Tibyan AI:</b> ${reply}</div>`;
                chatContainer.scrollTop = chatContainer.scrollHeight;
            } catch (err) {
                document.getElementById(loadingId).remove();
                chatContainer.innerHTML += `<div class="message ai-msg" style="border-left-color:red;"><b>Tibyan AI:</b> Ma'zur chahte hain, server se rabta nahi ho saka.</div>`;
                chatContainer.scrollTop = chatContainer.scrollHeight;
            }
        }

        userInput.addEventListener('keydown', function(e) {
            if (e.key === 'Enter') {
                e.preventDefault();
                handleSendButton();
            }
        });
    </script>
</body>
</html>
"""

with open("templates/index.html", "w", encoding="utf-8") as f:
    f.write(clean_html)
print("SUCCESS: Clean UI written!")

full_html = """<!DOCTYPE html>
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
            justify-content: space-between;
            padding: 12px 20px;
            background: var(--card-bg);
            border-bottom: 1px solid var(--border-color);
            font-size: 20px;
            font-weight: bold;
            color: var(--accent-color);
        }
        .menu-icon {
            cursor: pointer;
            font-size: 24px;
        }
        /* Sidebar Navigation */
        #sidebar {
            position: fixed;
            top: 0;
            left: -280px;
            width: 280px;
            height: 100%;
            background: var(--card-bg);
            box-shadow: 2px 0 10px rgba(0,0,0,0.1);
            transition: left 0.3s ease;
            z-index: 1000;
            display: flex;
            flex-direction: column;
            padding-top: 20px;
            border-right: 1px solid var(--border-color);
        }
        #sidebar.active {
            left: 0;
        }
        .sidebar-header {
            padding: 0 20px 20px 20px;
            font-size: 22px;
            font-weight: bold;
            color: var(--accent-color);
            border-bottom: 1px solid var(--border-color);
        }
        .sidebar-links {
            list-style: none;
            padding: 0;
            margin: 0;
        }
        .sidebar-links li a {
            display: block;
            padding: 15px 20px;
            color: var(--text-color);
            text-decoration: none;
            font-size: 16px;
            border-bottom: 1px solid #f0f4f1;
            transition: background 0.2s;
        }
        .sidebar-links li a:hover {
            background: #f0f4f1;
            color: var(--accent-color);
        }
        .overlay {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.3);
            display: none;
            z-index: 999;
        }
        .overlay.active {
            display: block;
        }
        #chat-container {
            flex: 1;
            overflow-y: auto;
            padding: 20px;
            display: flex;
            flex-direction: column;
            gap: 20px;
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
        .message-wrapper {
            display: flex;
            flex-direction: column;
            gap: 8px;
            max-width: 85%;
        }
        .user-wrapper {
            align-self: flex-end;
            align-items: flex-end;
        }
        .ai-wrapper {
            align-self: flex-start;
            align-items: flex-start;
        }
        .message {
            padding: 12px 16px;
            border-radius: 12px;
            line-height: 1.5;
            word-break: break-word;
        }
        .user-msg {
            background: #e8f5e9;
            border: 1px solid #c8e6c9;
            border-bottom-right-radius: 2px;
        }
        .ai-msg {
            background: var(--card-bg);
            border: 1px solid var(--border-color);
            border-left: 4px solid var(--accent-color);
            border-bottom-left-radius: 2px;
        }
        /* Action buttons below AI responses */
        .ai-actions {
            display: flex;
            gap: 12px;
            font-size: 13px;
            color: #555;
            padding-left: 5px;
        }
        .ai-actions button {
            background: none;
            border: none;
            cursor: pointer;
            color: #555;
            display: flex;
            align-items: center;
            gap: 4px;
            padding: 2px 6px;
            border-radius: 4px;
            transition: background 0.2s, color 0.2s;
        }
        .ai-actions button:hover {
            background: #f0f4f1;
            color: var(--accent-color);
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
        .plus-btn {
            background: none;
            border: 1px solid var(--border-color);
            width: 40px;
            height: 40px;
            border-radius: 50%;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 22px;
            color: var(--accent-color);
            transition: background 0.2s;
        }
        .plus-btn:hover {
            background: #f0f4f1;
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
        .input-bar button.send-btn {
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
        #file-input {
            display: none;
        }
    </style>
</head>
<body>

    <header>
        <div style="display:flex; align-items:center; gap:15px;">
            <span class="menu-icon" onclick="toggleSidebar()">☰</span>
            <span>Tibyan AI</span>
        </div>
    </header>

    <!-- Sidebar Navigation -->
    <div class="overlay" id="overlay" onclick="toggleSidebar()"></div>
    <div id="sidebar">
        <div class="sidebar-header">Tibyan AI Menu</div>
        <ul class="sidebar-links">
            <li><a href="#" onclick="toggleSidebar()">🏠 Home</a></li>
            <li><a href="#" onclick="alert('Library section loaded'); toggleSidebar();">📚 Library</a></li>
            <li><a href="#" onclick="alert('Saved items section'); toggleSidebar();">🔖 Saved</a></li>
            <li><a href="#" onclick="alert('User Profile'); toggleSidebar();">👤 Profile</a></li>
            <li><a href="#" onclick="alert('Tibyan AI v4.0 - Authentic Islamic Assistant'); toggleSidebar();">ℹ️ About</a></li>
        </ul>
    </div>

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
        <input type="file" id="file-input" accept="image/*" onchange="handleImageUpload(event)">
        <button class="plus-btn" onclick="document.getElementById('file-input').click()" title="Upload Image">+</button>
        <input type="text" id="user-input" placeholder="Type your question...">
        <button class="send-btn" onclick="handleSendButton()">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="22" y1="2" x2="11" y2="13"></line><polygon points="22 2 15 22 11 13 2 9 22 2"></polygon></svg>
        </button>
    </div>

    <script>
        const chatContainer = document.getElementById('chat-container');
        const userInput = document.getElementById('user-input');
        const welcomeView = document.getElementById('welcome-view');
        const sidebar = document.getElementById('sidebar');
        const overlay = document.getElementById('overlay');
        let isFirstMessage = true;
        let uploadedImagePreview = null;

        function toggleSidebar() {
            sidebar.classList.toggle('active');
            overlay.classList.toggle('active');
        }

        function handleImageUpload(event) {
            const file = event.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    uploadedImagePreview = e.target.result;
                    userInput.placeholder = "Image attached. Type your question about it...";
                    userInput.style.borderColor = "#1b4332";
                };
                reader.readAsDataURL(file);
            }
        }

        function sendQuery(text) {
            userInput.value = text;
            handleSendButton();
        }

        async function handleSendButton() {
            const text = userInput.value.trim();
            if (!text && !uploadedImagePreview) return;

            if (isFirstMessage) {
                welcomeView.style.display = 'none';
                isFirstMessage = false;
            }

            // Append User Message Wrapper
            let userHtml = `<div class="message-wrapper user-wrapper">`;
            if (uploadedImagePreview) {
                userHtml += `<img src="${uploadedImagePreview}" style="max-width:200px; border-radius:8px; border:1px solid #d1ded3;">`;
            }
            userHtml += `<div class="message user-msg"><b>Aap:</b> ${text || "Is tasveer ke mutabiq رہنمائی farmaein."}</div></div>`;
            
            chatContainer.innerHTML += userHtml;
            const currentImg = uploadedImagePreview;
            
            // Reset input
            userInput.value = '';
            userInput.placeholder = "Type your question...";
            uploadedImagePreview = null;
            document.getElementById('file-input').value = '';
            chatContainer.scrollTop = chatContainer.scrollHeight;

            // Loading state
            const loadingId = 'loading-' + Date.now();
            chatContainer.innerHTML += `<div class="message-wrapper ai-wrapper" id="${loadingId}"><div class="message ai-msg"><b>Tibyan AI:</b> Soch rahe hain...</div></div>`;
            chatContainer.scrollTop = chatContainer.scrollHeight;

            try {
                const res = await fetch('/api/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ message: text, image: currentImg })
                });
                const data = await res.json();
                const reply = data.response || "Wa alaikum assalam. Bismillah.";

                document.getElementById(loadingId).remove();

                // Append AI Response with Like, Dislike, Saved, Share buttons
                const aiWrapperId = 'ai-res-' + Date.now();
                const aiHtml = `
                <div class="message-wrapper ai-wrapper" id="${aiWrapperId}">
                    <div class="message ai-msg"><b>Tibyan AI:</b> <span class="ai-text-content">${reply}</span></div>
                    <div class="ai-actions">
                        <button onclick="likeMessage('${aiWrapperId}')">👍 Like</button>
                        <button onclick="dislikeMessage('${aiWrapperId}')">👎 Dislike</button>
                        <button onclick="saveMessage('${aiWrapperId}')">🔖 Saved</button>
                        <button onclick="shareMessage('${aiWrapperId}')">🔗 Share</button>
                    </div>
                </div>`;

                chatContainer.innerHTML += aiHtml;
                chatContainer.scrollTop = chatContainer.scrollHeight;
            } catch (err) {
                document.getElementById(loadingId).remove();
                chatContainer.innerHTML += `<div class="message-wrapper ai-wrapper"><div class="message ai-msg" style="border-left-color:red;"><b>Tibyan AI:</b> Ma'zrat chahte hain, server se rabta nahi ho saka.</div></div>`;
                chatContainer.scrollTop = chatContainer.scrollHeight;
            }
        }

        function likeMessage(id) {
            alert('Shukriya! Aapka feedback record kar liya gaya hai.');
        }
        function dislikeMessage(id) {
            alert('Shukriya! Hum isme behtari karenge.');
        }
        function saveMessage(id) {
            alert('Yeh jawab Saved mein mehfooz kar liya gaya hai!');
        }
        function shareMessage(id) {
            const textElem = document.querySelector('#' + id + ' .ai-text-content');
            if (navigator.share && textElem) {
                navigator.share({ title: 'Tibyan AI Answer', text: textElem.innerText });
            } else {
                alert('Jawab copy kar liya gaya hai!');
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
    f.write(full_html)
print("SUCCESS: Full UI with Image Upload, Menu, and Action buttons written!")

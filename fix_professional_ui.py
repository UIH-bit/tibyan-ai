professional_html = """<!DOCTYPE html>
<html lang="hi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Tibyan AI - Authentic Islamic Assistant</title>
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
        /* Main View Container */
        .view-section {
            flex: 1;
            overflow-y: auto;
            padding: 20px;
            display: flex;
            flex-direction: column;
            max-width: 800px;
            width: 100%;
            margin: 0 auto;
            box-sizing: border-box;
        }
        .hidden {
            display: none !important;
        }
        /* Chat View */
        #chat-container {
            display: flex;
            flex-direction: column;
            gap: 20px;
            flex: 1;
            overflow-y: auto;
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
            padding: 14px 18px;
            border-radius: 12px;
            line-height: 1.6;
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
        .ai-actions {
            display: flex;
            gap: 15px;
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
            gap: 5px;
            padding: 4px 8px;
            border-radius: 6px;
            transition: background 0.2s, color 0.2s;
        }
        .ai-actions button:hover {
            background: #f0f4f1;
            color: var(--accent-color);
        }
        /* Input Bar */
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
        .input-bar input[type="text"] {
            flex: 1;
            padding: 12px 16px;
            border: 1px solid var(--border-color);
            border-radius: 24px;
            outline: none;
            font-size: 16px;
            background: #f9fbf9;
        }
        .input-bar input[type="text"]:focus {
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
        /* Custom Section Pages style */
        .page-card {
            background: var(--card-bg);
            border: 1px solid var(--border-color);
            padding: 20px;
            border-radius: 12px;
            margin-bottom: 15px;
        }
        .page-card h2 {
            color: var(--accent-color);
            margin-top: 0;
        }
    </style>
</head>
<body>

    <header>
        <div style="display:flex; align-items:center; gap:15px;">
            <span class="menu-icon" onclick="toggleSidebar()">☰</span>
            <span id="header-title">Tibyan AI</span>
        </div>
    </header>

    <!-- Sidebar Navigation -->
    <div class="overlay" id="overlay" onclick="toggleSidebar()"></div>
    <div id="sidebar">
        <div class="sidebar-header">Tibyan AI Menu</div>
        <ul class="sidebar-links">
            <li><a href="#" onclick="switchView('chat')">🏠 Home</a></li>
            <li><a href="#" onclick="switchView('library')">📚 Library (Authentic Books)</a></li>
            <li><a href="#" onclick="switchView('saved')">🔖 Saved Answers</a></li>
            <li><a href="#" onclick="switchView('profile')">👤 User Profile</a></li>
            <li><a href="#" onclick="switchView('about')">ℹ️ About Tibyan AI</a></li>
        </ul>
    </div>

    <!-- 1. CHAT VIEW -->
    <div id="chat-view" class="view-section">
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
    </div>

    <!-- 2. LIBRARY VIEW -->
    <div id="library-view" class="view-section hidden">
        <h2>Islamic Library</h2>
        <p>Access authentic Islamic reference books and collections:</p>
        <div class="page-card">
            <h3>Sahih Al-Bukhari</h3>
            <p>The most authentic collection of Hadith compiled by Imam Bukhari.</p>
        </div>
        <div class="page-card">
            <h3>Sahih Muslim</h3>
            <p>Another major canonical collection of prophetic traditions.</p>
        </div>
        <div class="page-card">
            <h3>Quran-e-Kareem</h3>
            <p>Complete Arabic text with translation and Tafseer.</p>
        </div>
    </div>

    <!-- 3. SAVED VIEW -->
    <div id="saved-view" class="view-section hidden">
        <h2>Saved Answers</h2>
        <p>Aapke mehfooz kiye gaye jawabat yahan show honge.</p>
        <div id="saved-list-container">
            <div class="page-card">
                <p>Abhi tak koi jawab saved nahi hai. Kisi bhi jawab ke neeche <b>Saved</b> button par click karein.</p>
            </div>
        </div>
    </div>

    <!-- 4. PROFILE VIEW -->
    <div id="profile-view" class="view-section hidden">
        <h2>User Profile</h2>
        <div class="page-card">
            <p><b>Naam:</b> Deen Ka Talib Ilm</p>
            <p><b>Status:</b> Active Member</p>
            <p><b>App Version:</b> Tibyan AI v4.2 (Render Live)</p>
        </div>
    </div>

    <!-- 5. ABOUT VIEW -->
    <div id="about-view" class="view-section hidden">
        <h2>About Tibyan AI</h2>
        <div class="page-card">
            <p><b>Tibyan AI</b> ek authentic Islamic artificial intelligence assistant hai jo Quran, Sunnah aur mustanad ulema ki roshni mein aapke sawalon ke tafsili aur behtareen jawaab faraham karta hai.</p>
            <p>Developed with ❤️ for the Ummah.</p>
        </div>
    </div>

    <!-- Input Bar (Visible only on Chat View) -->
    <div class="input-bar" id="bottom-input-bar">
        <input type="file" id="file-input" accept="image/*" onchange="handleImageUpload(event)">
        <button class="plus-btn" onclick="document.getElementById('file-input').click()" title="Upload Image">+</button>
        <input type="text" id="user-input" placeholder="Type your question...">
        <button class="send-btn" onclick="handleSendButton()">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="22" y1="2" x2="11" y2="13"></line><polygon points="22 2 15 22 11 13 2 9 22 2"></polygon></svg>
        </button>
    </div>

    <script>
        const sidebar = document.getElementById('sidebar');
        const overlay = document.getElementById('overlay');
        const headerTitle = document.getElementById('header-title');
        
        const chatView = document.getElementById('chat-view');
        const libraryView = document.getElementById('library-view');
        const savedView = document.getElementById('saved-view');
        const profileView = document.getElementById('profile-view');
        const aboutView = document.getElementById('about-view');
        const bottomInputBar = document.getElementById('bottom-input-bar');

        const chatContainer = document.getElementById('chat-container');
        const userInput = document.getElementById('user-input');
        const welcomeView = document.getElementById('welcome-view');
        let isFirstMessage = true;
        let uploadedImagePreview = null;
        let savedMessagesList = [];

        function toggleSidebar() {
            sidebar.classList.toggle('active');
            overlay.classList.toggle('active');
        }

        function switchView(viewName) {
            toggleSidebar();
            chatView.classList.add('hidden');
            libraryView.classList.add('hidden');
            savedView.classList.add('hidden');
            profileView.classList.add('hidden');
            aboutView.classList.add('hidden');
            bottomInputBar.style.display = 'flex';

            if (viewName === 'chat') {
                chatView.classList.remove('hidden');
                headerTitle.innerText = "Tibyan AI";
            } else if (viewName === 'library') {
                libraryView.classList.remove('hidden');
                headerTitle.innerText = "Islamic Library";
                bottomInputBar.style.display = 'none';
            } else if (viewName === 'saved') {
                savedView.classList.remove('hidden');
                headerTitle.innerText = "Saved Answers";
                bottomInputBar.style.display = 'none';
                renderSavedList();
            } else if (viewName === 'profile') {
                profileView.classList.remove('hidden');
                headerTitle.innerText = "User Profile";
                bottomInputBar.style.display = 'none';
            } else if (viewName === 'about') {
                aboutView.classList.remove('hidden');
                headerTitle.innerText = "About Tibyan AI";
                bottomInputBar.style.display = 'none';
            }
        }

        function handleImageUpload(event) {
            const file = event.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    uploadedImagePreview = e.target.result;
                    userInput.placeholder = "Image attached. Type your question about it...";
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

            let userHtml = `<div class="message-wrapper user-wrapper">`;
            if (uploadedImagePreview) {
                userHtml += `<img src="${uploadedImagePreview}" style="max-width:200px; border-radius:8px; border:1px solid #d1ded3;">`;
            }
            userHtml += `<div class="message user-msg"><b>Aap:</b> ${text || "Is tasveer ke mutabiq رہنمائی farmaein."}</div></div>`;
            
            chatContainer.innerHTML += userHtml;
            const currentImg = uploadedImagePreview;
            
            userInput.value = '';
            userInput.placeholder = "Type your question...";
            uploadedImagePreview = null;
            document.getElementById('file-input').value = '';
            chatContainer.scrollTop = chatContainer.scrollHeight;

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
                const reply = data.response || "Bismillah. Al-hamdulillah.";

                document.getElementById(loadingId).remove();

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
            const elem = document.querySelector('#' + id + ' .ai-text-content');
            if (elem) {
                savedMessagesList.push(elem.innerHTML);
                alert('Yeh jawab Saved mein mehfooz kar liya gaya hai!');
            }
        }
        function renderSavedList() {
            const container = document.getElementById('saved-list-container');
            if (savedMessagesList.length === 0) {
                container.innerHTML = `<div class="page-card"><p>Abhi tak koi jawab saved nahi hai. Kisi bhi jawab ke neeche <b>Saved</b> button par click karein.</p></div>`;
            } else {
                let html = '';
                savedMessagesList.forEach((ans, idx) => {
                    html += `<div class="page-card"><h3>Saved Item #${idx + 1}</h3><p>${ans}</p></div>`;
                });
                container.innerHTML = html;
            }
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
    f.write(professional_html)
print("SUCCESS: Professional Multi-view UI written!")

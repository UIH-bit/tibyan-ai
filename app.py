from flask import Flask, request, jsonify, render_template_string
import os
import requests

app = Flask(__name__)

api_key = os.environ.get("GROQ_API_KEY") or os.environ.get("GEMINI_API_KEY")

def fetch_quran_api(query):
    try:
        url = f"https://api.quran.com/api/v4/search?q={query}&size=3"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            results = data.get('search', {}).get('results', [])
            verses_text = ""
            for res in results:
                verses_text += f"- Surah/Ayah Ref ({res.get('verse_key')}): {res.get('text')}\n"
            return verses_text
    except Exception as e:
        print("Quran API Error:", e)
    return None

def call_groq_api(prompt_text, image_base64=None):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    
    model_name = "qwen/qwen3.6-27b" if image_base64 else "llama-3.3-70b-versatile"
    
    content_list = [{"type": "text", "text": prompt_text}]
    if image_base64:
        content_list.append({
            "type": "image_url",
            "image_url": {
                "url": f"data:image/jpeg;base64,{image_base64}"
            }
        })

    payload = {
        "model": model_name,
        "messages": [
            {
                "role": "system", 
                "content": (
                    "You are Tibyan AI, a knowledgeable, wise, and respectful Muslim scholar assistant. "
                    "Always begin your responses warmly with Islamic greetings (like Bismillah or Assalamu Alaikum). "
                    "Strictly avoid modern or non-Islamic vocabulary such as 'mahatvpoorn'. Instead, use authentic, respectful Islamic and Urdu/Arabic terminology like 'zaroori', 'aham', 'fazilat', 'masla', 'hukm', etc. "
                    "Your responses on Islamic rulings, Fiqh, and fatawa must strictly align with the authentic methodologies, "
                    "teachings, and scholarly standards of prominent institutions like Darul Ifta Darul Uloom Deoband and "
                    "Jamia Uloom-ul-Islamia Banuri Town (Ahlus Sunnah wal Jama'ah / Hanafi Fiqh unless specified). "
                    "You MUST structure every answer using the exact following sections with clear headings:\n\n"
                    "1. Short Answer\n"
                    "2. Explanation\n"
                    "3. Evidence\n"
                    "4. Quran\n"
                    "5. Hadith\n"
                    "6. Scholars\n"
                    "7. References\n"
                    "8. Related Topics\n\n"
                    "Speak with deep respect, empathy, and wisdom like a sincere practicing Muslim scholar."
                )
            },
            {
                "role": "user", 
                "content": content_list if image_base64 else prompt_text
            }
        ],
        "temperature": 0.7
    }
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=25)
        if response.status_code == 200:
            res_data = response.json()
            return res_data['choices'][0]['message']['content']
        else:
            return f"Groq API Error ({response.status_code}): {response.text}"
    except Exception as e:
        return f"Request Exception: {str(e)}"


HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Tibyan AI - Professional Scholar Assistant</title>
    <style>
        :root {
            --primary: #1b4332;
            --secondary: #2d6a4f;
            --bg: #f8f9fa;
            --card-bg: #ffffff;
            --text: #212529;
            --border: #dee2e6;
        }
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: var(--bg); color: var(--text); margin: 0; padding: 0; }
        .container { max-width: 800px; margin: 0 auto; padding: 20px; }
        .card { background: var(--card-bg); border-radius: 12px; padding: 20px; box-shadow: 0 4px 12px rgba(0,0,0,0.05); margin-bottom: 20px; border-left: 5px solid var(--primary); }
        .search-input { width: 100%; padding: 12px; border: 1px solid var(--border); border-radius: 8px; font-size: 14px; margin-bottom: 15px; box-sizing: border-box; }
        .profile-header { display: flex; align-items: center; gap: 20px; margin-bottom: 15px; }
        .profile-img-preview { width: 70px; height: 70px; border-radius: 50%; object-fit: cover; background: #e9f5ed; display: flex; align-items: center; justify-content: center; font-size: 30px; border: 2px solid var(--primary); }
        .form-group { margin-bottom: 12px; }
        .form-group label { display: block; font-weight: 600; font-size: 13px; margin-bottom: 5px; color: var(--primary); }
        .form-control { width: 100%; padding: 10px; border: 1px solid var(--border); border-radius: 6px; font-size: 14px; box-sizing: border-box; }
        .faq-category h3 { color: var(--primary); border-bottom: 2px solid #e9f5ed; padding-bottom: 5px; font-size: 16px; margin-top: 20px; }
        .faq-item { background: #fafafa; border: 1px solid var(--border); padding: 12px; border-radius: 6px; margin-bottom: 10px; }
        .quick-tips { background: #fff8e1; border-left: 4px solid #ffc107; padding: 12px; border-radius: 6px; font-size: 14px; margin-bottom: 15px; }
        .contact-btn { display: inline-block; background: var(--primary); color: white; padding: 10px 20px; border-radius: 6px; text-decoration: none; font-weight: 500; margin-top: 10px; }
    </style>
</head>
<body>
    <div class="container">
        
        <!-- Profile Board -->
        <div class="card">
            <h2 style="margin-top:0; color: var(--primary);">Scholar Profile 👤</h2>
            <div class="profile-header">
                <div id="avatarContainer" class="profile-img-preview">🕌</div>
                <div>
                    <h3 id="displayName" style="margin:0;">Tibyan User</h3>
                    <p id="displayBio" style="margin:4px 0 0; color: #6c757d; font-size: 13px;">Seeking authentic Islamic knowledge.</p>
                </div>
            </div>
            <div class="form-group">
                <label>Your Name:</label>
                <input type="text" id="profileNameInput" class="form-control" value="Tibyan User" oninput="updateProfile()">
            </div>
            <div class="form-group">
                <label>Bio / Status:</label>
                <input type="text" id="profileBioInput" class="form-control" value="Seeking authentic Islamic knowledge." oninput="updateProfile()">
            </div>
            <div class="form-group">
                <label>Profile Image URL:</label>
                <input type="text" id="profileImgInput" class="form-control" placeholder="Paste image link here..." oninput="updateProfile()">
            </div>
        </div>

        <!-- Chat History with Search & Top Sorting -->
        <div class="card">
            <h2 style="margin-top:0; color: var(--primary);">Chat History 📜</h2>
            <input type="text" id="chatSearchInput" class="search-input" placeholder="Search previous chats... (Matching items move to top)" onkeyup="filterAndSortChats()">
            
            <div id="chatListContainer">
                <div class="chat-item-box faq-item" data-keywords="roza sawm fasting islam pillars">
                    <strong>Q: Roza</strong>
                    <p style="margin: 5px 0 0; font-size: 13px;">Roza, or Sawm, is one of the five fundamental pillars of Islam...</p>
                </div>
                <div class="chat-item-box faq-item" data-keywords="samas hindi grammar dvandva">
                    <strong>Q: Dvandva Samas</strong>
                    <p style="margin: 5px 0 0; font-size: 13px;">Hindi grammar explanation regarding Dvandva Samas...</p>
                </div>
                <div class="chat-item-box faq-item" data-keywords="zakat charity wealth islam">
                    <strong>Q: Zakat Calculation</strong>
                    <p style="margin: 5px 0 0; font-size: 13px;">Details regarding rules of Zakat and Nisab threshold...</p>
                </div>
            </div>
        </div>

        <!-- Help & Support with Email -->
        <div class="card">
            <h2 style="margin-top:0; color: var(--primary);">Help & Support 💡</h2>
            
            <div class="quick-tips">
                <strong>Pro Tip:</strong> Use exact keywords in the search bar above to instantly filter and lift your required chats to the very top.
            </div>

            <div class="faq-category">
                <h3>🚀 Getting Started</h3>
                <div class="faq-item">
                    <strong>How to ask queries?</strong>
                    <p style="margin:4px 0 0; font-size:13px;">Type any question into the input console to fetch verified scholarly content.</p>
                </div>
            </div>

            <div class="faq-category">
                <h3>📁 Uploading Fatawa</h3>
                <div class="faq-item">
                    <strong>How to scan documents?</strong>
                    <p style="margin:4px 0 0; font-size:13px;">Tap the '+' icon to upload scanned images/Fatawa for instant breakdown.</p>
                </div>
            </div>

            <div class="faq-category">
                <h3>📚 References</h3>
                <div class="faq-item">
                    <strong>Are citations provided?</strong>
                    <p style="margin:4px 0 0; font-size:13px;">Yes, structural responses include Quranic verses and Hadith references.</p>
                </div>
            </div>

            <div style="margin-top: 20px; padding-top: 15px; border-top: 1px solid var(--border); text-align: center;">
                <p style="margin: 0 0 10px; font-size: 14px; color: #555;">Need direct assistance or technical support?</p>
                <a href="mailto:uih0209@gmail.com" class="contact-btn">✉️ Email Support: uih0209@gmail.com</a>
            </div>
        </div>

    </div>

    <script>
        function updateProfile() {
            const name = document.getElementById('profileNameInput').value;
            const bio = document.getElementById('profileBioInput').value;
            const imgUrl = document.getElementById('profileImgInput').value;
            
            document.getElementById('displayName').innerText = name || "Tibyan User";
            document.getElementById('displayBio').innerText = bio || "";
            
            const avatarContainer = document.getElementById('avatarContainer');
            if (imgUrl.trim() !== "") {
                avatarContainer.innerHTML = `<img src="${imgUrl}" style="width:100%; height:100%; border-radius:50%; object-fit:cover;" onerror="this.onerror=null;this.parentNode.innerHTML='🕌';">`;
            } else {
                avatarContainer.innerHTML = "🕌";
            }
        }

        function filterAndSortChats() {
            const query = document.getElementById('chatSearchInput').value.toLowerCase();
            const container = document.getElementById('chatListContainer');
            const items = Array.from(container.getElementsByClassName('chat-item-box'));

            items.sort((a, b) => {
                const textA = (a.getAttribute('data-keywords') + " " + a.innerText).toLowerCase();
                const textB = (b.getAttribute('data-keywords') + " " + b.innerText).toLowerCase();
                const matchA = textA.includes(query) ? 1 : 0;
                const matchB = textB.includes(query) ? 1 : 0;
                return matchB - matchA;
            });

            items.forEach(item => {
                const fullText = (item.innerText + " " + item.getAttribute('data-keywords')).toLowerCase();
                if (query === "" || fullText.includes(query)) {
                    item.style.display = "block";
                    container.appendChild(item);
                } else {
                    item.style.display = "none";
                }
            });
        }
    </script>
</body>
</html>
'''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Tibyan AI - Authentic Islamic Knowledge</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }
        body { background-color: #ffffff; color: #111; display: flex; flex-direction: column; height: 100vh; overflow: hidden; font-size: 17px; }
        
        header { display: flex; align-items: center; justify-content: space-between; padding: 15px 20px; border-bottom: 1px solid #eaeaea; background: #fff; z-index: 10; flex-shrink: 0; }
        .header-left { display: flex; align-items: center; gap: 15px; }
        .menu-btn { background: none; border: none; font-size: 24px; cursor: pointer; color: #1e3d2f; }
        .logo { font-size: 22px; font-weight: bold; color: #1e3d2f; }
        
        .sidebar { position: fixed; top: 0; left: -280px; width: 280px; height: 100%; background: #fff; box-shadow: 2px 0 10px rgba(0,0,0,0.1); transition: 0.3s ease; z-index: 100; display: flex; flex-direction: column; }
        .sidebar.open { left: 0; }
        .sidebar-header { padding: 20px; font-size: 20px; font-weight: bold; color: #1e3d2f; border-bottom: 1px solid #eaeaea; display: flex; justify-content: space-between; align-items: center; }
        .close-sidebar { background: none; border: none; font-size: 20px; cursor: pointer; color: #555; }
        
        .sidebar-menu { list-style: none; padding: 15px 0; overflow-y: auto; flex: 1; }
        .sidebar-menu li { padding: 14px 20px; font-size: 17px; color: #333; cursor: pointer; display: flex; align-items: center; gap: 14px; transition: 0.2s; border-bottom: 1px solid #f9f9f9; }
        .sidebar-menu li:hover { background: #f0f4f1; color: #1e3d2f; font-weight: 500; }
        
        .overlay { position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.4); display: none; z-index: 90; }
        .overlay.active { display: block; }

        .main-content { flex: 1; display: flex; flex-direction: column; overflow: hidden; position: relative; }
        .view-section { display: none; flex: 1; overflow-y: auto; padding: 20px 20px 100px 20px; max-width: 800px; width: 100%; margin: 0 auto; scroll-behavior: smooth; }
        .view-section.active-view { display: flex; flex-direction: column; }

        .chat-container { justify-content: space-between; }
        .welcome-section { display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center; margin: auto 0; width: 100%; padding: 20px 0; }
        .arabic-greeting { font-size: 40px; color: #1e3d2f; font-weight: bold; margin-bottom: 15px; font-family: serif; }
        .sub-text { font-size: 18px; color: #555; margin-bottom: 30px; line-height: 1.5; }
        
        .suggestions { width: 100%; display: flex; flex-direction: column; align-items: center; gap: 14px; max-width: 550px; margin: 0 auto; }
        .suggestions-row { display: flex; justify-content: center; gap: 14px; width: 100%; }
        .suggestion-chip { background: #fff; border: 1px solid #e0e0e0; border-radius: 30px; padding: 14px 20px; font-size: 16px; color: #333; cursor: pointer; text-align: center; box-shadow: 0 2px 5px rgba(0,0,0,0.02); transition: 0.2s; flex: 1; }
        .suggestion-chip:hover { border-color: #1e3d2f; background: #f9fbf9; }
        .suggestion-center { max-width: 280px; width: 100%; }

        #chat-history { width: 100%; display: flex; flex-direction: column; gap: 18px; padding-bottom: 30px; }
        .message-wrapper { display: flex; flex-direction: column; width: 100%; margin-bottom: 12px; }
        .message { padding: 16px 20px; border-radius: 14px; max-width: 85%; line-height: 1.6; font-size: 17px; white-space: pre-wrap; }
        .user-msg { background: #f0f4f1; color: #1e3d2f; align-self: flex-end; margin-left: auto; }
        .ai-msg { background: #ffffff; border: 1px solid #e0e0e0; color: #222; align-self: flex-start; }
        
        .ai-actions { display: flex; gap: 10px; margin-top: 8px; align-self: flex-start; padding-left: 6px; align-items: center; position: relative; }
        .action-btn { background: none; border: none; font-size: 15px; color: #666; cursor: pointer; display: flex; align-items: center; gap: 5px; padding: 6px 10px; border-radius: 7px; transition: 0.2s; }
        .action-btn:hover { background: #f0f4f1; color: #1e3d2f; }
        .action-btn.saved-active { color: #1e3d2f; font-weight: bold; background: #e8f0eb; }

        /* Popover Menu for More Options (•••) */
        .more-menu-container { position: relative; display: inline-block; }
        .more-dropdown { display: none; position: absolute; bottom: 100%; left: 0; background: #fff; border: 1px solid #ccc; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.15); z-index: 50; min-width: 130px; overflow: hidden; margin-bottom: 5px; }
        .more-dropdown.show { display: block; }
        .more-dropdown button { width: 100%; text-align: left; background: none; border: none; padding: 10px 15px; font-size: 15px; cursor: pointer; color: #333; }
        .more-dropdown button:hover { background: #f0f4f1; color: #1e3d2f; }

        .search-box-container { margin-bottom: 15px; display: flex; gap: 10px; }
        .search-input-field { flex: 1; padding: 10px 15px; border: 1px solid #ccc; border-radius: 8px; font-size: 16px; outline: none; }

        .saved-item { background: #fff; border: 1px solid #e0e0e0; border-radius: 12px; padding: 18px; margin-bottom: 18px; box-shadow: 0 2px 5px rgba(0,0,0,0.02); }
        .saved-q { font-weight: bold; color: #1e3d2f; margin-bottom: 10px; font-size: 18px; }
        .saved-a { color: #333; font-size: 17px; line-height: 1.6; white-space: pre-wrap; }
        .unsave-btn { background: #ff4d4d; color: white; border: none; padding: 6px 12px; border-radius: 6px; font-size: 14px; cursor: pointer; margin-top: 12px; float: right; }

        /* Input Area lifted up to avoid mobile navigation bar overlay */
        .input-area { display: flex; align-items: flex-end; padding: 14px 18px 22px 18px; border-top: 1px solid #eaeaea; background: #fff; gap: 12px; max-width: 800px; width: 100%; margin: 0 auto; flex-shrink: 0; position: sticky; bottom: 0; z-index: 20; box-shadow: 0 -2px 10px rgba(0,0,0,0.03); }
        .text-input { flex: 1; border: 1px solid #e0e0e0; border-radius: 24px; padding: 14px 20px; font-size: 17px; outline: none; background: #f9f9f9; resize: none; max-height: 180px; overflow-y: auto; line-height: 1.5; }
        
        .upload-btn { background: none; border: none; font-size: 26px; cursor: pointer; color: #555; padding-bottom: 8px; display: flex; align-items: center; justify-content: center; width: 36px; height: 36px; border-radius: 50%; transition: 0.2s; }
        .upload-btn:hover { background: #f0f4f1; color: #1e3d2f; }

        .send-btn { 
            background: #1e3d2f; border: none; border-radius: 50%; width: 48px; height: 48px; min-width: 48px; 
            display: flex; align-items: center; justify-content: center; cursor: pointer; color: white; position: relative; margin-bottom: 3px;
        }
        .send-btn svg { width: 20px; height: 20px; fill: white; transition: transform 0.2s; }
        
        .send-btn.loading::after {
            content: ''; position: absolute; top: -4px; left: -4px; right: -4px; bottom: -4px;
            border: 2.5px solid transparent; border-top-color: #4CAF50; border-radius: 50%;
            animation: spin 0.8s linear infinite;
        }
        @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }

        #imagePreviewContainer { display: none; padding: 6px 18px; align-items: center; gap: 12px; background: #f9f9f9; max-width: 800px; margin: 0 auto; border-top: 1px solid #eaeaea; flex-shrink: 0; }
        #imagePreviewContainer img { width: 55px; height: 55px; object-fit: cover; border-radius: 8px; border: 1px solid #ccc; }
        .remove-img { background: #ff4d4d; color: white; border: none; border-radius: 50%; width: 24px; height: 24px; font-size: 14px; cursor: pointer; display: flex; align-items: center; justify-content: center; }

        .view-title { font-size: 28px; color: #1e3d2f; margin-bottom: 20px; font-weight: bold; }
        .view-body { font-size: 17px; color: #444; line-height: 1.6; }
    </style>
</head>
<body>
    <header>
        <div class="header-left">
            <button class="menu-btn" onclick="toggleSidebar()">☰</button>
            <div class="logo">Tibyan AI</div>
        </div>
    </header>

    <div class="overlay" id="overlay" onclick="toggleSidebar()"></div>
    <div class="sidebar" id="sidebar">
        <div class="sidebar-header">
            <span>Tibyan Menu</span>
            <button class="close-sidebar" onclick="toggleSidebar()">✕</button>
        </div>
        <ul class="sidebar-menu">
            <li onclick="startNewChat()">New Chat ➕️</li>
            <li onclick="switchView('home')">Home 🏡</li>
            <li onclick="switchView('saved')">Saved 📜</li>
            <li onclick="switchView('profile')">Profile 👤</li>
            <li onclick="switchView('history')">History</li>
            <li onclick="switchView('search')">Search Chats</li>
            <li onclick="switchView('setting')">Setting</li>
            <li onclick="switchView('help')">Help</li>
        </ul>
    </div>

    <div class="main-content">
        <!-- Home / Chat View -->
        <div id="home-view" class="view-section active-view chat-container">
            <div id="chat-box" style="width: 100%;">
                <div class="welcome-section" id="welcome-screen">
                    <div class="arabic-greeting">بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ</div>
                    <div class="sub-text">Authentic Islamic Knowledge backed by Deoband & Banuri Town manhaj</div>
                    
                    <div class="suggestions">
                        <div class="suggestions-row">
                            <div class="suggestion-chip" onclick="sendPrompt('What does the Quran say about patience (Sabr)?')">What does the Quran say about patience (Sabr)?</div>
                            <div class="suggestion-chip" onclick="sendPrompt('Roza kaise toot jata hai')">Roza kaise toot jata hai</div>
                        </div>
                        <div class="suggestion-chip suggestion-center" onclick="sendPrompt('Who is Adam alai issalam?')">Who is Adam alai issalam?</div>
                    </div>
                </div>
                <div id="chat-history"></div>
            </div>
        </div>

        <!-- Saved View -->
        <div id="saved-view" class="view-section">
            <div class="view-title">Saved Chats 📜</div>
            <div class="view-body" id="saved-container">
                <p>No saved responses yet. Click 'Saved 📜' under any AI response to bookmark it here.</p>
            </div>
        </div>

        <!-- Profile View -->
        <div id="profile-view" class="view-section">
            <div class="view-title">Profile 👤</div>
            <div class="view-body">
                <p><strong>Account Name:</strong> Tibyan User</p>
                <p style="margin-top: 10px;"><strong>Manhaj:</strong> Ahlus Sunnah wal Jama'ah (Deoband & Banuri Town)</p>
                <p style="margin-top: 10px;"><strong>Status:</strong> Active Scholar Assistant</p>
            </div>
        </div>

        <!-- History View -->
        <div id="history-view" class="view-section">
            <div class="view-title">Chat History 📜</div>
            <div class="view-body" id="history-container">
                <p>No chat history available.</p>
            </div>
        </div>

        <!-- Search Chats View -->
        <div id="search-view" class="view-section">
            <div class="view-title">Search Chats 🔍</div>
            <div class="search-box-container">
                <input type="text" id="chatSearchInput" class="search-input-field" placeholder="Search your past queries and answers..." oninput="filterSearchChats(this.value)">
            </div>
            <div class="view-body" id="search-results-container">
                <p>Type above to search through your saved chats.</p>
            </div>
        </div>

        <!-- Setting View -->
        <div id="setting-view" class="view-section">
            <div class="view-title">Settings ⚙️</div>
            <div class="view-body">
                <p><strong>Response Format:</strong> Structured (Short Answer, Explanation, Evidence, Quran, Hadith, Scholars, References, Related Topics)</p>
                <p style="margin-top: 15px;"><strong>School of Thought:</strong> Hanafi / Deoband & Banuri Town</p>
                <p style="margin-top: 15px;"><button onclick="clearAllData()" style="background:#ff4d4d; color:white; border:none; padding:10px 15px; border-radius:6px; cursor:pointer;">Clear All Chat Data</button></p>
            </div>
        </div>

        <!-- Help View -->
        <div id="help-view" class="view-section">
            <div class="view-title">Help & Support 💡</div>
            <div class="view-body">
                <p><strong>How to use Tibyan AI:</strong></p>
                <p style="margin-top: 10px;">• Type any Islamic question in the box below or click on the suggestion chips.</p>
                <p style="margin-top: 5px;">• Upload any scanned Fatawa or image using the '+' icon to get insights.</p>
                <p style="margin-top: 5px;">• Every answer follows a rigorous scholarly breakdown format including Quranic verses, Hadith evidence, and scholarly references.</p>
            </div>
        </div>
    </div>

    <div id="imagePreviewContainer">
        <img id="previewImg" src="" alt="preview">
        <span id="fileName" style="font-size: 14px; color: #555; flex: 1;"></span>
        <button class="remove-img" onclick="clearImage()">✕</button>
    </div>

    <div class="input-area">
        <input type="file" id="imageInput" accept="image/*" style="display: none;" onchange="handleImageSelect(event)">
        <button class="upload-btn" onclick="document.getElementById('imageInput').click()" title="Upload Image">+</button>
        <textarea id="userInput" class="text-input" rows="1" placeholder="Ask a question or upload an image..." oninput="autoExpand(this)"></textarea>
        <button class="send-btn" id="sendBtn" onclick="submitQuery()">
            <svg viewBox="0 0 24 24"><path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"></path></svg>
        </button>
    </div>

    <script>
        let selectedBase64Image = null;

        function autoExpand(field) {
            field.style.height = 'inherit';
            field.style.height = (field.scrollHeight) + 'px';
        }

        function toggleSidebar() {
            document.getElementById('sidebar').classList.toggle('open');
            document.getElementById('overlay').classList.toggle('active');
        }

        function switchView(viewName) {
            document.querySelectorAll('.view-section').forEach(el => el.classList.remove('active-view'));
            document.getElementById(viewName + '-view').classList.add('active-view');
            if (viewName === 'history') {
                renderHistory();
            } else if (viewName === 'saved') {
                renderSavedChats();
            }
            toggleSidebar();
        }

        function startNewChat() {
            document.getElementById('chat-history').innerHTML = '';
            const welcomeScreen = document.getElementById('welcome-screen');
            if (welcomeScreen) {
                welcomeScreen.style.display = 'flex';
            }
            switchView('home');
            toggleSidebar();
        }

        function handleImageSelect(event) {
            const file = event.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    selectedBase64Image = e.target.result.split(',')[1];
                    document.getElementById('previewImg').src = e.target.result;
                    document.getElementById('fileName').innerText = file.name;
                    document.getElementById('imagePreviewContainer').style.display = 'flex';
                };
                reader.readAsDataURL(file);
            }
        }

        function clearImage() {
            selectedBase64Image = null;
            document.getElementById('imageInput').value = '';
            document.getElementById('imagePreviewContainer').style.display = 'none';
        }

        function scrollToBottom() {
            const homeView = document.getElementById('home-view');
            homeView.scrollTop = homeView.scrollHeight;
        }

        async function submitQuery() {
            const inputField = document.getElementById('userInput');
            const query = inputField.value.trim();
            if (!query && !selectedBase64Image) return;

            document.querySelectorAll('.view-section').forEach(el => el.classList.remove('active-view'));
            document.getElementById('home-view').classList.add('active-view');
            
            const welcomeScreen = document.getElementById('welcome-screen');
            if (welcomeScreen) {
                welcomeScreen.style.display = 'none';
            }

            const historyBox = document.getElementById('chat-history');
            let userHtml = `<div class="message-wrapper"><div class="message user-msg">`;
            if (selectedBase64Image) {
                userHtml += `<img src="data:image/jpeg;base64,${selectedBase64Image}" style="max-width:180px; border-radius:8px; display:block; margin-bottom:8px;">`;
            }
            userHtml += `${query || 'Analysing uploaded image...'}</div></div>`;
            historyBox.innerHTML += userHtml;
            scrollToBottom();

            const currentQuery = query || 'Uploaded Image Query';
            const currentImg = selectedBase64Image;
            
            inputField.value = '';
            inputField.style.height = 'inherit';
            clearImage();
            
            const sendBtn = document.getElementById('sendBtn');
            sendBtn.classList.add('loading');

            const uniqueId = 'msg-' + Date.now();
            historyBox.innerHTML += `
                <div class="message-wrapper" id="wrapper-${uniqueId}">
                    <div class="message ai-msg" id="${uniqueId}">Bismillah, preparing structured scholarly response...</div>
                </div>`;
            scrollToBottom();

            try {
                const response = await fetch('/generate', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ prompt: currentQuery, image: currentImg })
                });
                const data = await response.json();
                const aiMsgBox = document.getElementById(uniqueId);
                const wrapperBox = document.getElementById(`wrapper-${uniqueId}`);
                
                if (data.response) {
                    aiMsgBox.innerText = data.response;
                    
                    saveChatHistory(currentQuery, data.response);

                    const actionsDiv = document.createElement('div');
                    actionsDiv.className = 'ai-actions';
                    actionsDiv.innerHTML = `
                        <button class="action-btn" onclick="handleLike(this)">👍 Like</button>
                        <button class="action-btn" onclick="handleDislike(this)">👎 Dislike</button>
                        <button class="action-btn" id="save-btn-${uniqueId}" onclick="toggleSave('${uniqueId}', \`${b16Encode(currentQuery)}\`, \`${b16Encode(data.response)}\`)">📜 Save</button>
                        <div class="more-menu-container">
                            <button class="action-btn" onclick="toggleMoreMenu(event, '${uniqueId}')">•••</button>
                            <div class="more-dropdown" id="dropdown-${uniqueId}">
                                <button onclick="copyContent(\`${b16Encode(data.response)}\`, '${uniqueId}')">📋 Copy</button>
                                <button onclick="shareContent(\`${b16Encode(data.response)}\`, '${uniqueId}')">📤 Share</button>
                            </div>
                        </div>
                    `;
                    wrapperBox.appendChild(actionsDiv);
                } else {
                    aiMsgBox.innerText = "Error: " + (data.error || "Something went wrong.");
                }
            } catch (err) {
                document.getElementById(uniqueId).innerText = "Network error occurred.";
            } finally {
                sendBtn.classList.remove('loading');
            }
            scrollToBottom();
        }

        function b16Encode(str) {
            return btoa(encodeURIComponent(str));
        }
        function b16Decode(str) {
            return decodeURIComponent(atob(str));
        }

        function handleLike(btn) {
            btn.style.color = '#2e7d32';
            btn.style.fontWeight = 'bold';
            btn.innerText = '👍 Liked';
        }

        function handleDislike(btn) {
            btn.style.color = '#c62828';
            btn.style.fontWeight = 'bold';
            btn.innerText = '👎 Disliked';
        }

        function toggleMoreMenu(event, id) {
            event.stopPropagation();
            // Close any other open dropdowns
            document.querySelectorAll('.more-dropdown').forEach(el => {
                if(el.id !== `dropdown-${id}`) el.classList.remove('show');
            });
            const dropdown = document.getElementById(`dropdown-${id}`);
            dropdown.classList.toggle('show');
        }

        // Close dropdown when clicking outside
        window.onclick = function(event) {
            if (!event.target.matches('.action-btn')) {
                document.querySelectorAll('.more-dropdown').forEach(el => el.classList.remove('show'));
            }
        }

        function toggleSave(id, encQuery, encAns) {
            const queryText = b16Decode(encQuery);
            const ansText = b16Decode(encAns);
            let savedList = JSON.parse(localStorage.getItem('tibyan_saved') || '[]');
            
            const existingIndex = savedList.findIndex(item => item.query === queryText && item.answer === ansText);
            const btn = document.getElementById(`save-btn-${id}`);

            if (existingIndex > -1) {
                savedList.splice(existingIndex, 1);
                if(btn) {
                    btn.classList.remove('saved-active');
                    btn.innerHTML = '📜 Save';
                }
            } else {
                savedList.push({ query: queryText, answer: ansText, date: new Date().toLocaleString() });
                if(btn) {
                    btn.classList.add('saved-active');
                    btn.innerHTML = '✅ Saved';
                }
            }
            localStorage.setItem('tibyan_saved', JSON.stringify(savedList));
        }

        function renderSavedChats() {
            const container = document.getElementById('saved-container');
            let savedList = JSON.parse(localStorage.getItem('tibyan_saved') || '[]');
            
            if (savedList.length === 0) {
                container.innerHTML = `<p>No saved responses yet. Click 'Save 📜' under any AI response to bookmark it here.</p>`;
                return;
            }

            let html = '';
            savedList.forEach((item, index) => {
                html += `
                    <div class="saved-item">
                        <div class="saved-q">Q: ${item.query}</div>
                        <div class="saved-a">${item.answer}</div>
                        <button class="unsave-btn" onclick="removeSaved(${index})">Delete</button>
                        <div style="clear:both;"></div>
                    </div>
                `;
            });
            container.innerHTML = html;
        }

        function removeSaved(index) {
            let savedList = JSON.parse(localStorage.getItem('tibyan_saved') || '[]');
            savedList.splice(index, 1);
            localStorage.setItem('tibyan_saved', JSON.stringify(savedList));
            renderSavedChats();
        }

        function saveChatHistory(query, answer) {
            let historyList = JSON.parse(localStorage.getItem('tibyan_history') || '[]');
            historyList.unshift({ query: query, answer: answer, date: new Date().toLocaleString() });
            localStorage.setItem('tibyan_history', JSON.stringify(historyList));
        }

        function renderHistory() {
            const container = document.getElementById('history-container');
            let historyList = JSON.parse(localStorage.getItem('tibyan_history') || '[]');
            
            if (historyList.length === 0) {
                container.innerHTML = `<p>No chat history found.</p>`;
                return;
            }

            let html = '';
            historyList.forEach((item) => {
                html += `
                    <div class="saved-item">
                        <div class="saved-q">Q: ${item.query}</div>
                        <div class="saved-a">${item.answer}</div>
                    </div>
                `;
            });
            container.innerHTML = html;
        }

        function filterSearchChats(keyword) {
            const container = document.getElementById('search-results-container');
            let historyList = JSON.parse(localStorage.getItem('tibyan_history') || '[]');
            
            if (!keyword.trim()) {
                container.innerHTML = `<p>Type above to search through your saved chats.</p>`;
                return;
            }

            const filtered = historyList.filter(item => 
                item.query.toLowerCase().includes(keyword.toLowerCase()) || 
                item.answer.toLowerCase().includes(keyword.toLowerCase())
            );

            if (filtered.length === 0) {
                container.innerHTML = `<p>No matching chats found.</p>`;
                return;
            }

            let html = '';
            filtered.forEach((item) => {
                html += `
                    <div class="saved-item">
                        <div class="saved-q">Q: ${item.query}</div>
                        <div class="saved-a">${item.answer}</div>
                    </div>
                `;
            });
            container.innerHTML = html;
        }

        function clearAllData() {
            if (confirm("Are you sure you want to clear all chat data?")) {
                localStorage.removeItem('tibyan_history');
                localStorage.removeItem('tibyan_saved');
                alert("All data cleared successfully.");
                renderHistory();
            }
        }

        function copyContent(encAns, id) {
            const ansText = b16Decode(encAns);
            navigator.clipboard.writeText(ansText);
            alert('Answer copied to clipboard!');
            document.getElementById(`dropdown-${id}`).classList.remove('show');
        }

        function shareContent(encAns, id) {
            const ansText = b16Decode(encAns);
            if (navigator.share) {
                navigator.share({
                    title: 'Tibyan AI Response',
                    text: ansText
                }).catch(console.error);
            } else {
                navigator.clipboard.writeText(ansText);
                alert('Answer copied to clipboard!');
            }
            document.getElementById(`dropdown-${id}`).classList.remove('show');
        }

        function sendPrompt(text) {
            document.getElementById('userInput').value = text;
            autoExpand(document.getElementById('userInput'));
            submitQuery();
        }
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/generate', methods=['POST'])
def generate():
    data = request.json
    user_prompt = data.get('prompt', '')
    img_data = data.get('image', None)
    
    quran_data = fetch_quran_api(user_prompt) if user_prompt else ""
    context_data = f"\nQuran API References:\n{quran_data}\n" if quran_data else ""
    
    ai_response = call_groq_api(f"{context_data}\nUser Question: {user_prompt}", image_base64=img_data)
    return jsonify({'response': ai_response})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)


@app.route('/api/chat', methods=['POST'])
def chat_api():
    try:
        data = request.get_json()
        user_msg = data.get('message', '').strip() if data else ''
        image_data = data.get('image', None) if data else None
        
        if not user_msg and not image_data:
            return jsonify({"response": "Ma'zrat chahte hain, aapne na koi sawal pucha aur na hi tasveer bheji."})

        response_text = ""
        
        try:
            import os
            import base64
            import google.generativeai as genai
            api_key = os.environ.get("GEMINI_API_KEY")
            if api_key:
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel('gemini-1.5-flash')
                
                content_parts = []
                if user_msg:
                    content_parts.append(f"You are Tibyan AI, an authentic and knowledgeable Islamic AI assistant. Provide a detailed, comprehensive, and accurate Islamic answer with references from Quran and Sunnah for the query: {user_msg}")
                else:
                    content_parts.append("You are Tibyan AI, an authentic Islamic AI assistant. Thoroughly analyze this image from an Islamic perspective, extract any Arabic text, provide its translation, and give a detailed explanation based on Quran and Sunnah.")
                
                if image_data:
                    if ',' in image_data:
                        header, encoded = image_data.split(',', 1)
                    else:
                        encoded = image_data
                    image_bytes = base64.b64decode(encoded)
                    content_parts.append({'mime_type': 'image/jpeg', 'data': image_bytes})

                chat_res = model.generate_content(content_parts)
                if chat_res and chat_res.text:
                    response_text = chat_res.text
        except Exception as e:
            print("Gemini API error:", e)

        # Detailed and rich fallback response if API key is missing or not configured
        if not response_text:
            if image_data:
                response_text = "<b>Bismillah-ir-Rahman-ir-Rahim</b><br><br><b>Tasveer Se Arabic Text aur Tafseel:</b><br><br>1. <b>Arabic Text & Context:</b> Is tasveer mein di gayi ibarat Quran-e-Kareem ki aayat ya deeni matan par mushtamil hai.<br>2. <b>Tarjuma wa Mafhoom:</b> Yeh ibarat Allah Ta'ala ke zikr, ahkaam aur hidayat ko bayan karti hai.<br>3. <b>Islami Hidayat:</b> Deen mein har ilmi aur deeni matan ko ahtiram ke sath padhna aur samajhna chahiye."
            else:
                msg_lower = user_msg.lower()
                if "fast" in msg_lower or "roza" in msg_lower:
                    response_text = "<b>Bismillah-ir-Rahman-ir-Rahim</b><br><br><b>Roze ko Todne (Invalidate) karne wali cheezein:</b><br>1. Jaan-bujh kar khana ya peena.<br>2. Jaan-bujh kar ulti (vomiting) karna.<br>3. Jinsi taaluq qaim karna.<br>4. Haiz (menstruation) ya Nifas ka shuru hona.<br><br><i>Note:</i> Bhool kar khane ya peena se roza nahi tutta (Sahih Al-Bukhari)."
                elif "tahajjud" in msg_lower:
                    response_text = "<b>Bismillah-ir-Rahman-ir-Rahim</b><br><br><b>Tahajjud ki Namaz ka Tareeqa wa Fazilat:</b><br>1. Isha ke baad aur nend se uth kar padhi jaane wali sunnat-e-muakkadah namaz hai.<br>2. Kam az kam 2 rakat aur zyada se zyada jitni Allah taufeeq de padhein.<br>3. Yeh aakhri tihai raat mein padhna sabse afzal hai (Sahih Muslim)."
                else:
                    response_text = f"<b>Bismillah-ir-Rahman-ir-Rahim</b><br><br>Aapke sawal <i>('{user_msg}')</i> ke mutabiq:<br>Islam mein har maamle ki mukammal rehnumai Quran-e-Kareem aur Sahih Ahadees mein mojood hai. Is silsile mein mustanad ulama ki roshni mein amal karna chahiye taaki deen ki sahi samajh hasil ho sake."

        return jsonify({"response": response_text})
    except Exception as e:
        return jsonify({"response": f"Ma'zrat chahte hain, takneeqi kharabi ki wajah se jawab nahi diya ja saka: {str(e)}"}), 500